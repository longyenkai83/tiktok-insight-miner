"""Post-run hooks: resolve folder conflicts, update master index, write LATEST.md.

Dùng bởi webapp.py sau mỗi pipeline thành công, và bởi daily_digest.py.
Tách module riêng để CLI có thể opt-in (không bắt buộc).
"""

from __future__ import annotations

import csv
import logging
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from tiktok_insight_miner.classifier import load_classified_json
from tiktok_insight_miner.models import BUCKET_LABELS, BUCKET_ORDER, ClassifiedComment

logger = logging.getLogger(__name__)

INDEX_FILENAME = "_index.md"
LATEST_FILENAME = "LATEST.md"

INDEX_HEADER = """\
# 📚 Insight Index

> Tự động cập nhật mỗi khi pipeline chạy xong (webapp + CLI).
> Sort: mới nhất trên cùng.

| Run date | Niche | User | Videos | Comments | Top buckets | Folder |
|---|---|---|---:|---:|---|---|
"""


def resolve_output_dir(output_root: Path, niche: str, run_date: str, user: str) -> Path:
    """Trả về folder unique cho run.

    Convention:
    - Default: output/<niche>/<date>/
    - Nếu đã tồn tại + có file: output/<niche>/<date>__<user>/
    - Nếu vẫn conflict: thêm timestamp HHMMSS

    KHÔNG bao giờ ghi đè data của nhân viên khác.
    """
    base = output_root / niche / run_date
    if not base.exists() or not any(base.iterdir()):
        return base

    safe_user = re.sub(r"[^a-z0-9_-]", "-", user.lower()) or "anon"
    with_user = output_root / niche / f"{run_date}__{safe_user}"
    if not with_user.exists() or not any(with_user.iterdir()):
        return with_user

    ts = datetime.now().strftime("%H%M%S")
    return output_root / niche / f"{run_date}__{safe_user}_{ts}"


def _bucket_distribution(classified: list[ClassifiedComment]) -> dict[str, int]:
    """Đếm comment theo bucket, giữ thứ tự BUCKET_ORDER."""
    counter = Counter(c.bucket for c in classified)
    return {b: counter.get(b, 0) for b in BUCKET_ORDER}


def _format_top_buckets(distribution: dict[str, int], top: int = 3) -> str:
    """Format top N bucket non-zero thành string ngắn cho table.

    Vd: 'pain 89 · desire 67 · question 54'
    """
    nonzero = [(b, n) for b, n in distribution.items() if n > 0]
    nonzero.sort(key=lambda x: x[1], reverse=True)
    return " · ".join(f"{b} {n}" for b, n in nonzero[:top]) or "—"


def _index_link(output_root: Path, output_dir: Path) -> str:
    """Path tương đối từ _index.md đến output_dir, dùng forward slash."""
    rel = output_dir.relative_to(output_root)
    return str(rel).replace("\\", "/") + "/"


def update_index(
    output_root: Path,
    output_dir: Path,
    niche: str,
    user: str,
    num_videos: int,
    num_comments: int,
    distribution: dict[str, int],
    with_brief: bool,
) -> Path:
    """Append/prepend row vào _index.md. Tạo file nếu chưa có.

    Idempotent theo (folder link): nếu folder đã có row → update in place.
    """
    index_path = output_root / INDEX_FILENAME
    run_date = date.today().isoformat()
    folder_link = _index_link(output_root, output_dir)
    top_b = _format_top_buckets(distribution)
    brief_mark = "✅" if with_brief else "—"

    new_row = (
        f"| {run_date} | {niche} | {user} | {num_videos} | {num_comments} "
        f"| {top_b} | [📂]({folder_link}) {brief_mark} |"
    )

    if not index_path.exists():
        index_path.write_text(INDEX_HEADER + new_row + "\n", encoding="utf-8")
        logger.info("Created %s", index_path)
        return index_path

    existing_text = index_path.read_text(encoding="utf-8")

    # Migration: nếu file cũ dùng schema khác (vd từ cmd_init), archive + tạo mới
    new_header_marker = "| Run date | Niche | User | Videos | Comments |"
    if new_header_marker not in existing_text:
        legacy_path = index_path.with_name("_index.legacy.md")
        legacy_path.write_text(existing_text, encoding="utf-8")
        index_path.write_text(INDEX_HEADER + new_row + "\n", encoding="utf-8")
        logger.info("Migrated old _index.md → _index.legacy.md, created fresh index")
        return index_path

    existing = existing_text.splitlines()

    # Tìm row cũ cho folder này (idempotent update)
    folder_marker = f"]({folder_link})"
    new_lines: list[str] = []
    replaced = False
    for line in existing:
        if folder_marker in line and line.startswith("|") and run_date in line:
            new_lines.append(new_row)
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        # Insert sau header table (sau dòng `|---|...|`)
        insert_idx = None
        for i, line in enumerate(new_lines):
            if line.startswith("|---"):
                insert_idx = i + 1
                break
        if insert_idx is None:
            new_lines.append(new_row)
        else:
            new_lines.insert(insert_idx, new_row)

    index_path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
    logger.info("Updated %s (%s row)", index_path, "replaced" if replaced else "added new")
    return index_path


def _peek_top_angle(brief_md_path: Path) -> str | None:
    """Đọc nhanh angle #1 từ brief.md (dòng heading H2 đầu tiên, bỏ ## ).

    Best-effort, fail silently nếu file format đổi.
    """
    if not brief_md_path or not brief_md_path.exists():
        return None
    try:
        for line in brief_md_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("## ") and not line.startswith("## 📋"):
                return line.lstrip("#").strip()
    except OSError:
        return None
    return None


def write_latest(
    project_root: Path,
    output_dir: Path,
    niche: str,
    user: str,
    num_videos: int,
    num_comments: int,
    distribution: dict[str, int],
    with_brief: bool,
    duration_s: float,
    cost_est_usd: float,
    brief_path: Path | None = None,
) -> Path:
    """Ghi LATEST.md ở project root — anh mở file này thấy ngay run mới nhất.

    Notification kiểu file-based: không cần dashboard, không cần check folder.
    """
    latest_path = project_root / LATEST_FILENAME
    now = datetime.now()
    rel_dir = output_dir.relative_to(project_root) if output_dir.is_relative_to(project_root) else output_dir
    rel_dir_str = str(rel_dir).replace("\\", "/")

    top_buckets = _format_top_buckets(distribution, top=5)
    top_angle = _peek_top_angle(brief_path) if with_brief else None

    lines = [
        "# 🆕 Latest run",
        "",
        f"> Cập nhật lúc: **{now.strftime('%Y-%m-%d %H:%M:%S')}**",
        "",
        "## Tóm tắt",
        "",
        f"- **Nhân viên**: `{user}`",
        f"- **Niche**: `{niche}`",
        f"- **Quy mô**: {num_videos} video · {num_comments} comments",
        f"- **Thời gian**: {duration_s:.0f}s · **Cost ước tính**: ${cost_est_usd:.2f}",
        f"- **Folder**: [{rel_dir_str}/]({rel_dir_str}/)",
        "",
        "## Phân bố",
        "",
        f"`{top_buckets}`",
        "",
        "## File chính",
        "",
        f"- 📊 [report.md]({rel_dir_str}/report.md) — insight summary",
    ]
    if with_brief:
        lines.append(f"- 🎬 [brief.md]({rel_dir_str}/brief.md) — content angles")
        if top_angle:
            lines.extend(["", "## 🎬 Top angle #1", "", f"> {top_angle}"])
    lines.extend([
        "",
        "---",
        "",
        f"_Xem [output/_index.md](output/{INDEX_FILENAME}) để duyệt tất cả runs._",
        "",
    ])

    latest_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", latest_path)
    return latest_path


def post_run_hook(
    project_root: Path,
    output_root: Path,
    output_dir: Path,
    classified_path: Path,
    niche: str,
    user: str,
    num_videos: int,
    with_brief: bool,
    duration_s: float,
    cost_est_usd: float,
    brief_path: Path | None = None,
) -> dict[str, Path]:
    """Chạy tất cả post-run side effects. Best-effort, log + tiếp tục nếu lỗi.

    Trả về dict {index_path, latest_path} để caller có thể hiển thị.
    """
    result: dict[str, Path] = {}
    try:
        classified = load_classified_json(classified_path)
        distribution = _bucket_distribution(classified)
        num_comments = len(classified)
    except Exception as e:
        logger.warning("post_run_hook: cannot read classified.json (%s) — skip", e)
        return result

    try:
        result["index_path"] = update_index(
            output_root=output_root,
            output_dir=output_dir,
            niche=niche,
            user=user,
            num_videos=num_videos,
            num_comments=num_comments,
            distribution=distribution,
            with_brief=with_brief,
        )
    except Exception as e:
        logger.warning("update_index failed: %s", e)

    try:
        result["latest_path"] = write_latest(
            project_root=project_root,
            output_dir=output_dir,
            niche=niche,
            user=user,
            num_videos=num_videos,
            num_comments=num_comments,
            distribution=distribution,
            with_brief=with_brief,
            duration_s=duration_s,
            cost_est_usd=cost_est_usd,
            brief_path=brief_path,
        )
    except Exception as e:
        logger.warning("write_latest failed: %s", e)

    return result


# --- Daily digest support ---

def read_usage_log(log_path: Path) -> list[dict[str, str]]:
    """Đọc usage_log.csv. Trả về [] nếu file không tồn tại."""
    if not log_path.exists():
        return []
    rows: list[dict[str, str]] = []
    # File ghi với utf-8-sig (BOM), đọc cũng phải tương thích
    with open(log_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def filter_runs_by_date(rows: list[dict[str, str]], target_date: str) -> list[dict[str, str]]:
    """Lọc rows có timestamp khớp YYYY-MM-DD."""
    return [r for r in rows if r.get("timestamp", "").startswith(target_date)]


def build_daily_digest(
    project_root: Path,
    output_root: Path,
    target_date: str | None = None,
) -> Path | None:
    """Gộp tất cả run trong ngày thành 1 file output/_daily/<date>.md.

    Trả về path file hoặc None nếu không có run nào hôm đó.
    """
    target = target_date or date.today().isoformat()
    log_path = project_root / "usage_log.csv"
    rows = read_usage_log(log_path)
    today_rows = filter_runs_by_date(rows, target)

    if not today_rows:
        logger.info("Daily digest: không có run nào ngày %s", target)
        return None

    daily_dir = output_root / "_daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    digest_path = daily_dir / f"{target}.md"

    # Stats
    total_runs = len(today_rows)
    success_runs = [r for r in today_rows if r.get("status") == "success"]
    error_runs = [r for r in today_rows if r.get("status") != "success"]
    total_cost = sum(float(r.get("cost_est_usd") or 0) for r in success_runs)
    total_comments = sum(int(r.get("num_comments") or 0) for r in success_runs)
    users = sorted({r.get("user", "?") for r in today_rows})
    niches = sorted({r.get("niche", "?") for r in today_rows})

    lines = [
        f"# 📅 Daily digest — {target}",
        "",
        "## Tổng quan",
        "",
        f"- **Số run**: {total_runs} ({len(success_runs)} ✅ · {len(error_runs)} ❌)",
        f"- **Tổng comments xử lý**: {total_comments:,}",
        f"- **Tổng cost ước tính**: ${total_cost:.2f}",
        f"- **Nhân viên active**: {', '.join(users)}",
        f"- **Niches**: {', '.join(niches)}",
        "",
        "## Chi tiết runs",
        "",
        "| Time | User | Niche | Videos | Comments | Brief | Duration | Cost | Status |",
        "|---|---|---|---:|---:|---|---:|---:|---|",
    ]

    for r in sorted(today_rows, key=lambda x: x.get("timestamp", ""), reverse=True):
        ts = r.get("timestamp", "")[11:16]  # HH:MM
        user = r.get("user", "?")
        niche = r.get("niche", "?")
        urls_n = r.get("num_urls", "?")
        comments_n = r.get("num_comments", "?")
        with_brief = "✅" if str(r.get("with_brief", "")).lower() == "true" else "—"
        dur = r.get("duration_s", "?")
        cost = r.get("cost_est_usd", "?")
        status = "✅" if r.get("status") == "success" else "❌"
        lines.append(
            f"| {ts} | {user} | {niche} | {urls_n} | {comments_n} | "
            f"{with_brief} | {dur}s | ${cost} | {status} |"
        )

    lines.extend([
        "",
        "## Successful runs — quick links",
        "",
    ])
    if success_runs:
        for r in success_runs:
            niche = r.get("niche", "?")
            lines.append(f"- `{niche}` ({r.get('num_comments', '?')} cmt · ${r.get('cost_est_usd', '?')})")
    else:
        lines.append("_(không có)_")

    if error_runs:
        lines.extend(["", "## ❌ Errors cần xem", ""])
        for r in error_runs:
            ts = r.get("timestamp", "")[11:16]
            lines.append(
                f"- `{ts}` **{r.get('user', '?')}** chạy `{r.get('niche', '?')}` — fail sau {r.get('duration_s', '?')}s"
            )

    lines.append("")
    digest_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Daily digest → %s", digest_path)
    return digest_path
