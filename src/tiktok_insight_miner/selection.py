"""Selection — parse `3-lựa-chọn.md` (đã tick) → output 2 file vào `_master/`:

  _master/content-pipeline.md     (Markdown table cho anh browse + track status)
  _master/selected_angles.json    (JSON cho production.py — Bước 4 — đọc dễ)

Workflow:
  1. Anh / nhân viên mở `3-lựa-chọn.md` trong VS Code, tick `[x]` vào angle muốn quay
  2. Chạy `tim select -i .../3-lựa-chọn.md`
  3. Module này:
     - Parse các dòng `- [x]` hoặc `- [X]`
     - Cross-ref `1-liệt-kê.csv` ở sibling folder để lấy full quote/summary/video_url
     - Append vào `_master/content-pipeline.md` (giữ status cũ nếu quote trùng)
     - Ghi `_master/selected_angles.json` cho stage thực thi

KHÔNG gọi Claude. KHÔNG modify file input.
"""

from __future__ import annotations

import csv
import json
import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Format dòng checkbox được sinh bởi insight_bank.py:
#   - [x] `[SCORE 226]` `[Q001 TIEN_BAC_BINH_YEN]` `[FAQ_ANSWER]` "quote..." — @author (209 likes)
CHECKBOX_RE = re.compile(
    r"^\s*-\s*\[\s*[xX]\s*\]\s*"           # - [x] / - [X]
    r"`\[SCORE\s+(?P<score>\d+)\]`\s*"
    r"`\[(?P<id>\S+)\s+(?P<problem>[A-Z_]+)\]`\s*"
    r"`\[(?P<opportunity>[A-Z_]+)\]`\s*"
    r"\"(?P<quote>.+?)\"\s*"
    r"—\s*@(?P<author>\S+)\s*"
    r"\((?P<likes>\d+)\s*likes?\)",
    re.MULTILINE,
)

# Pattern continuation lines (indent 2 space):
#   - 💡 summary text
#   - 📂 nhóm: **Tên** · 🎯 intent: `VENT`
SUMMARY_LINE_RE = re.compile(r"^\s+-\s+💡\s+(.+?)\s*$")
INTENT_LINE_RE = re.compile(r"intent:\s*`([A-Z_]+)`")


# --- Parse 3-lựa-chọn.md ---

def parse_selected_md(md_path: Path) -> list[dict[str, Any]]:
    """Parse file 3-lựa-chọn.md, trả về list các angle đã tick.

    Mỗi item là dict với keys: id, score, problem_code, opportunity, quote_md (truncated),
    author, likes, summary_md, intent.

    `_md` suffix nghĩa là lấy từ markdown file (có thể truncated).
    Sẽ enrich bằng CSV ở bước sau để có quote/summary đầy đủ.
    """
    if not md_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {md_path}")

    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    selected: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = CHECKBOX_RE.match(line)
        if not m:
            i += 1
            continue

        item = {
            "id": m.group("id"),
            "score": int(m.group("score")),
            "problem_code": m.group("problem"),
            "opportunity": m.group("opportunity"),
            "quote_md": m.group("quote"),
            "author": m.group("author"),
            "likes": int(m.group("likes")),
            "summary_md": "",
            "intent": "",
            "selected_order": len(selected) + 1,
        }

        # Đọc tiếp 1-3 dòng continuation để lấy summary + intent
        j = i + 1
        while j < len(lines) and j < i + 4:
            cont = lines[j]
            sm = SUMMARY_LINE_RE.match(cont)
            if sm:
                item["summary_md"] = sm.group(1).strip()
            im = INTENT_LINE_RE.search(cont)
            if im:
                item["intent"] = im.group(1)
            # Dừng khi gặp dòng không indent
            if not cont.startswith(" ") and cont.strip():
                break
            j += 1

        selected.append(item)
        i = j

    return selected


# --- Enrich từ 1-liệt-kê.csv ---

def find_sibling_csv(md_path: Path) -> Path | None:
    """Tìm 1-liệt-kê.csv trong cùng folder với 3-lựa-chọn.md."""
    candidate = md_path.parent / "1-liệt-kê.csv"
    return candidate if candidate.exists() else None


def load_csv_index(csv_path: Path) -> dict[str, dict[str, str]]:
    """Load CSV → dict {id: row}."""
    index: dict[str, dict[str, str]] = {}
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_id = row.get("id", "").strip()
            if row_id:
                index[row_id] = row
    return index


def enrich_from_csv(
    selected: list[dict[str, Any]], csv_index: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    """Cross-ref ID → lấy full quote/summary/video_url. Fall back vào _md fields nếu không match."""
    enriched: list[dict[str, Any]] = []
    for item in selected:
        csv_row = csv_index.get(item["id"])
        if csv_row:
            item["quote"] = csv_row.get("quote") or item["quote_md"]
            item["summary"] = csv_row.get("summary") or item.get("summary_md", "")
            item["video_url"] = csv_row.get("video_url", "")
            item["bucket"] = csv_row.get("bucket", "")
            item["replies"] = int(csv_row.get("replies") or 0)
            # Trust CSV intent over md regex (md format có thể đổi)
            item["intent"] = csv_row.get("intent_label") or item.get("intent", "")
        else:
            logger.warning("ID %s không tìm thấy trong CSV — dùng dữ liệu từ md", item["id"])
            item["quote"] = item["quote_md"]
            item["summary"] = item.get("summary_md", "")
            item["video_url"] = ""
            item["bucket"] = ""
            item["replies"] = 0
        enriched.append(item)
    return enriched


# --- Path resolution ---

def resolve_niche_root(md_path: Path) -> Path:
    """Từ output/<niche>/<date>/3-lựa-chọn.md → trả về output/<niche>/."""
    return md_path.parent.parent


def get_source_run(md_path: Path) -> str:
    """Tên folder cha của 3-lựa-chọn.md = source run identifier (vd '2026-05-06')."""
    return md_path.parent.name


# --- Pipeline merging ---

PIPELINE_TABLE_HEADER = "| ID | Status | Score | Problem | Quote | Author | Source Run | Next Step |"
PIPELINE_TABLE_DIVIDER = "|---|---|---:|---|---|---|---|---|"

DEFAULT_STATUS = "todo"
DEFAULT_NEXT_STEP = "generate_production_brief"


def _truncate_for_table(s: str, n: int = 100) -> str:
    """Truncate quote cho cell table — escape `|` để không phá format."""
    s = re.sub(r"\s+", " ", s).strip().replace("|", "\\|")
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def parse_existing_pipeline(pipeline_path: Path) -> dict[str, dict[str, str]]:
    """Parse content-pipeline.md cũ (nếu có) → dict {full_quote: row_dict}.

    Chỉ parse phần table, bỏ qua header/stats. Dùng quote (đã unescape) làm key dedup.
    """
    if not pipeline_path.exists():
        return {}

    rows_by_quote: dict[str, dict[str, str]] = {}
    in_table = False
    seen_divider = False

    for line in pipeline_path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if line.startswith("|---"):
            seen_divider = True
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            in_table = False
            continue
        if not seen_divider:
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 8:
            continue

        row = {
            "id": cells[0],
            "status": cells[1],
            "score": cells[2],
            "problem": cells[3],
            "quote": cells[4].replace("\\|", "|"),  # unescape
            "author": cells[5],
            "source_run": cells[6],
            "next_step": cells[7],
        }
        rows_by_quote[row["quote"]] = row

    return rows_by_quote


def merge_pipeline(
    existing: dict[str, dict[str, str]],
    new_items: list[dict[str, Any]],
    source_run: str,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    """Merge new items vào existing rows.

    Rule:
    - Dedup theo quote (full text, đã enrich từ CSV)
    - Quote đã tồn tại → giữ status + next_step cũ
    - Quote mới → thêm với status='todo', next_step='generate_production_brief'

    Trả (merged_rows, stats) — stats có keys: added, kept_existing, total.
    """
    stats = {"added": 0, "kept_existing": len(existing), "total": 0}
    merged: dict[str, dict[str, str]] = dict(existing)  # copy

    for item in new_items:
        full_quote = item["quote"]
        quote_truncated = _truncate_for_table(full_quote)

        if quote_truncated in merged:
            # Đã có → giữ row cũ (status có thể đã đổi tay)
            continue

        merged[quote_truncated] = {
            "id": item["id"],
            "status": DEFAULT_STATUS,
            "score": str(item["score"]),
            "problem": item["problem_code"],
            "quote": quote_truncated,
            "author": f"@{item['author']}",
            "source_run": source_run,
            "next_step": DEFAULT_NEXT_STEP,
        }
        stats["added"] += 1

    # Sort: theo source_run desc, then score desc
    rows = list(merged.values())
    rows.sort(
        key=lambda r: (r["source_run"], int(r["score"]) if r["score"].isdigit() else 0),
        reverse=True,
    )
    stats["total"] = len(rows)
    return rows, stats


def write_pipeline_md(
    rows: list[dict[str, str]],
    pipeline_path: Path,
    niche_slug: str,
) -> None:
    """Render content-pipeline.md."""
    status_counts = Counter(r["status"] for r in rows)

    L: list[str] = []
    L.append(f"# 🎬 Content Production Pipeline — `{niche_slug}`")
    L.append("")
    L.append(f"> Aggregated từ các `3-lựa-chọn.md` đã tick across nhiều run.")
    L.append(f"> **Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L.append("")
    L.append("## Stats")
    L.append("")
    L.append(f"- **Total angles**: {len(rows)}")
    L.append(
        f"- **Status**: todo ({status_counts.get('todo', 0)}) · "
        f"doing ({status_counts.get('doing', 0)}) · "
        f"done ({status_counts.get('done', 0)}) · "
        f"skip ({status_counts.get('skip', 0)})"
    )
    L.append("")
    L.append("> 💡 **Edit status thủ công**: mở file này, đổi cột `Status` thành `doing/done/skip`.")
    L.append("> Chạy `tim select` lại sẽ KHÔNG ghi đè status đã đổi.")
    L.append("")
    L.append("## Pipeline")
    L.append("")
    L.append(PIPELINE_TABLE_HEADER)
    L.append(PIPELINE_TABLE_DIVIDER)
    for r in rows:
        L.append(
            f"| {r['id']} | {r['status']} | {r['score']} | {r['problem']} | "
            f"{r['quote']} | {r['author']} | {r['source_run']} | {r['next_step']} |"
        )

    pipeline_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_path.write_text("\n".join(L) + "\n", encoding="utf-8")
    logger.info("Wrote %s (%d rows)", pipeline_path, len(rows))


def write_selected_angles_json(
    new_items: list[dict[str, Any]],
    json_path: Path,
    source_run: str,
) -> None:
    """Ghi selected_angles.json — full data cho stage Bước 4 production.py.

    Append mode: nếu file tồn tại, merge theo quote (dedup).
    """
    existing: list[dict[str, Any]] = []
    if json_path.exists():
        try:
            existing = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("selected_angles.json corrupted — overwrite")

    existing_quotes = {item.get("quote") for item in existing}

    selected_at = datetime.now().isoformat(timespec="seconds")
    for item in new_items:
        if item["quote"] in existing_quotes:
            continue
        # Strip _md duplicate fields, keep clean output
        clean = {
            "id": item["id"],
            "source_run": source_run,
            "selected_at": selected_at,
            "status": DEFAULT_STATUS,
            "next_step": DEFAULT_NEXT_STEP,
            "score": item["score"],
            "problem_code": item["problem_code"],
            "opportunity": item["opportunity"],
            "intent": item["intent"],
            "bucket": item.get("bucket", ""),
            "quote": item["quote"],
            "summary": item["summary"],
            "author": item["author"],
            "likes": item["likes"],
            "replies": item.get("replies", 0),
            "video_url": item.get("video_url", ""),
        }
        existing.append(clean)

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Wrote %s (%d total angles)", json_path, len(existing))


# --- Entry point ---

def run_selection(
    md_path: Path,
    niche_slug: str | None = None,
    output_root: Path | None = None,
) -> dict[str, Any]:
    """All-in-one: parse → enrich → merge → write 2 files.

    Args:
        md_path: Path tới 3-lựa-chọn.md
        niche_slug: Override niche slug (mặc định = tên folder cha của niche root)
        output_root: Override _master folder (mặc định = niche_root/_master)

    Returns dict với keys: selected_count, added, kept_existing, total,
        pipeline_path, json_path (None nếu không có insight được tick).
    """
    selected = parse_selected_md(md_path)

    if not selected:
        return {
            "selected_count": 0,
            "added": 0,
            "kept_existing": 0,
            "total": 0,
            "pipeline_path": None,
            "json_path": None,
        }

    # Enrich từ CSV nếu có
    csv_path = find_sibling_csv(md_path)
    if csv_path:
        csv_index = load_csv_index(csv_path)
        selected = enrich_from_csv(selected, csv_index)
    else:
        logger.warning(
            "Không tìm thấy 1-liệt-kê.csv ở %s — quote sẽ bị truncated, video_url sẽ trống",
            md_path.parent,
        )
        for item in selected:
            item["quote"] = item["quote_md"]
            item["summary"] = item.get("summary_md", "")
            item["video_url"] = ""
            item["bucket"] = ""
            item["replies"] = 0

    niche_root = resolve_niche_root(md_path)
    source_run = get_source_run(md_path)
    inferred_niche = niche_slug or niche_root.name

    master_dir = (output_root or niche_root) / "_master"
    pipeline_path = master_dir / "content-pipeline.md"
    json_path = master_dir / "selected_angles.json"

    existing_rows = parse_existing_pipeline(pipeline_path)
    merged_rows, merge_stats = merge_pipeline(existing_rows, selected, source_run)

    write_pipeline_md(merged_rows, pipeline_path, inferred_niche)
    write_selected_angles_json(selected, json_path, source_run)

    return {
        "selected_count": len(selected),
        "added": merge_stats["added"],
        "kept_existing": merge_stats["kept_existing"],
        "total": merge_stats["total"],
        "pipeline_path": pipeline_path,
        "json_path": json_path,
        "niche": inferred_niche,
        "source_run": source_run,
    }
