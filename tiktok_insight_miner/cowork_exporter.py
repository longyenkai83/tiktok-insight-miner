"""Cowork Exporter — generate insight pack cho handoff sang Nhi Hien CoWork.

Input:
  - selected_angles.json (output Bước 3 - selection.py)
  - niche_configs/<niche>.json (có taxonomy + freedom_layer mapping v1.4+)

Output:
  - _master/insights-pack-for-cowork.md (file Hiền paste vào CoWork)

Logic:
  1. Load 2 file input
  2. Dedupe selected_angles theo quote (file có thể có duplicates)
  3. Build mapping problem_code → metadata (freedom_layer, mode, combo, emotions, desires)
  4. Render markdown theo schema chuẩn (xem docs/MAPPING_FREEDOM_LAYER.md)
  5. Write _master/insights-pack-for-cowork.md

KHÔNG gọi Claude. Pure mapping + format.

Spec format: docs/HANDOFF_DIAGRAM.md mục 6.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# --- Constants ---

LAYER_NAMES: dict[int, str] = {
    1: "Đời sống",
    2: "Công việc",
    3: "Tâm trí",
    4: "Dòng tiền",
}

MODE_NAMES: dict[str, str] = {
    "A": "Framework",
    "B": "Storytelling",
}

COMBO_NAMES: dict[int, str] = {
    1: "Phòng Thiền + Microphone",
    2: "Vườn + Macbook",
    3: "Hồ Sen + iPad/Sổ tay",
}


# --- Mapping & dedup helpers ---

def load_problem_mapping(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build dict {problem_code: main_problem_dict} từ niche config."""
    mapping: dict[str, dict[str, Any]] = {}
    for prob in config.get("main_problems", []):
        code = prob.get("code")
        if code:
            mapping[code] = prob
    return mapping


def dedupe_by_quote(angles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Loại bỏ angle trùng quote (file selected_angles có thể có dupes do append nhiều run)."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for a in angles:
        q = (a.get("quote") or "").strip()
        if not q or q in seen:
            continue
        seen.add(q)
        unique.append(a)
    return unique


def compute_data_quality_notes(angles: list[dict[str, Any]]) -> list[str]:
    """Auto-detect data quality issues — flag cho CoWork biết tin field nào."""
    notes: list[str] = []
    total = len(angles)
    if total == 0:
        return ["Batch rỗng — không có insight nào để export."]

    no_likes = sum(1 for a in angles if (a.get("likes") or 0) == 0)
    no_url = sum(1 for a in angles if not (a.get("video_url") or ""))
    no_author = sum(1 for a in angles if (a.get("author") or "") in ("", "unknown"))
    missing_bucket = sum(1 for a in angles if not (a.get("bucket") or "").strip())

    if no_likes == total and no_url == total:
        notes.append(
            f"Toàn bộ {total} insight từ manual import (paste text), không có likes/replies/video_url. "
            f"Demand score thấp + chênh nhau ít → tin distribution `problem_code`, KHÔNG tin engagement signal."
        )
    elif no_likes > total * 0.5:
        notes.append(
            f"{no_likes}/{total} insight thiếu engagement (likes=0). Có thể là mix manual import + scrape."
        )

    if no_author == total:
        notes.append(f"Author='unknown' ở toàn bộ {total} record — không trace được người comment.")

    if missing_bucket > 0:
        notes.append(
            f"{missing_bucket}/{total} record thiếu field `bucket` (pipeline classifier miss). "
            f"Cần infer pain/desire/question từ context khi viết."
        )

    return notes


# --- Format helpers ---

def short_title(angle: dict[str, Any]) -> str:
    """Tên ngắn cho heading — từ summary, cắt 60 ký tự."""
    s = (angle.get("summary") or "").strip()
    if not s:
        return f"({angle.get('problem_code', 'UNKNOWN')})"
    if len(s) > 60:
        return s[:57].rstrip() + "..."
    return s


def format_layer_hint(prob_meta: dict[str, Any]) -> str:
    """'3 Tâm trí · phụ: 2 Công việc' / '4 Dòng tiền' / 'unknown' (cho UNCLASSIFIED)."""
    primary = prob_meta.get("freedom_layer")
    secondary = prob_meta.get("freedom_layer_secondary")
    if primary is None:
        return "unknown (UNCLASSIFIED — Hiền tự gán)"
    p_str = f"**{primary}** {LAYER_NAMES.get(primary, '?')}"
    if secondary:
        s_str = f"{secondary} {LAYER_NAMES.get(secondary, '?')}"
        return f"{p_str} · phụ: {s_str}"
    return p_str


def format_mode_hint(prob_meta: dict[str, Any]) -> str:
    """'B Storytelling' / 'A Framework' / '— (Hiền tự chọn)' cho UNCLASSIFIED."""
    mode = prob_meta.get("suggested_mode")
    if not mode:
        return "— (Hiền tự chọn)"
    return f"**{mode}** {MODE_NAMES.get(mode, '?')}"


def format_combo_hint(prob_meta: dict[str, Any]) -> str:
    """'1 Phòng Thiền + Microphone' / '—'."""
    combo = prob_meta.get("combo_visual_hint")
    if not combo:
        return "— (Hiền tự chọn)"
    return f"**{combo}** {COMBO_NAMES.get(combo, '?')}"


def format_bullets(items: list[str]) -> str:
    """Render list str thành markdown bullets."""
    if not items:
        return "- (không có data trong niche taxonomy)"
    return "\n".join(f"- {x}" for x in items)


def format_insight_block(
    idx: int,
    angle: dict[str, Any],
    mapping: dict[str, dict[str, Any]],
) -> str:
    """Render 1 insight thành block markdown đầy đủ."""
    code = angle.get("problem_code", "UNKNOWN")
    prob_meta = mapping.get(code, {})
    name_vi = prob_meta.get("name_vi", "(không có trong taxonomy)")

    quote = (angle.get("quote") or "").strip()
    summary = (angle.get("summary") or "").strip()
    bucket = (angle.get("bucket") or "").strip() or "(thiếu — infer từ context)"
    intent = (angle.get("intent") or "").strip() or "—"
    opportunity = (angle.get("opportunity") or "").strip() or "—"
    score = angle.get("score", "—")
    angle_id = angle.get("id", "—")
    author = (angle.get("author") or "").strip() or "unknown"
    video_url = (angle.get("video_url") or "").strip() or "(không có)"
    source_run = (angle.get("source_run") or "").strip() or "—"

    title = short_title(angle)
    emotions = prob_meta.get("common_emotions", [])
    desires = prob_meta.get("hidden_desires", [])

    return (
        f"## Insight #{idx} — {title} [`{angle_id}` · Score {score}]\n"
        f"\n"
        f"**Quote audience (full)**:\n"
        f"> {quote}\n"
        f"\n"
        f"**Insight 1 câu**: {summary or '(không có summary)'}\n"
        f"\n"
        f"**Phân loại miner**:\n"
        f"- Nhóm vấn đề: `{code}` ({name_vi})\n"
        f"- Bucket: `{bucket}` · Intent: `{intent}` · Opportunity: `{opportunity}`\n"
        f"- Score: {score}\n"
        f"\n"
        f"**Hint cho CoWork** (mapping từ niche config, Hiền chốt cuối):\n"
        f"- **Lớp tự do**: {format_layer_hint(prob_meta)}\n"
        f"- **Mode đề xuất**: {format_mode_hint(prob_meta)}\n"
        f"- **Combo visual**: {format_combo_hint(prob_meta)}\n"
        f"- **Audience temperature**: Lạnh (default 30 bài đầu)\n"
        f"\n"
        f"**Cảm xúc audience đang sống** (từ niche taxonomy):\n"
        f"{format_bullets(emotions)}\n"
        f"\n"
        f"**Mong muốn ẩn**:\n"
        f"{format_bullets(desires)}\n"
        f"\n"
        f"**Trace gốc**:\n"
        f"- ID: `{angle_id}` · Author: {author} · Source run: `{source_run}`\n"
        f"- Video URL: {video_url}\n"
        f"\n"
        f"---\n"
    )


def format_distribution_table(
    angles: list[dict[str, Any]],
    mapping: dict[str, dict[str, Any]],
) -> str:
    """Render distribution table cuối file."""
    counter = Counter(a.get("problem_code", "UNKNOWN") for a in angles)
    sorted_codes = sorted(counter.items(), key=lambda kv: -kv[1])

    L = [
        "| Nhóm | Số insight | Lớp | Mode | Combo |",
        "|---|:---:|:---:|:---:|:---:|",
    ]
    for code, cnt in sorted_codes:
        prob_meta = mapping.get(code, {})
        layer = prob_meta.get("freedom_layer") or "—"
        mode = prob_meta.get("suggested_mode") or "—"
        combo = prob_meta.get("combo_visual_hint") or "—"
        L.append(f"| `{code}` | {cnt} | {layer} | {mode} | {combo} |")
    L.append(f"| **Tổng** | **{len(angles)}** | | | |")
    return "\n".join(L)


def render_pack(
    angles: list[dict[str, Any]],
    mapping: dict[str, dict[str, Any]],
    niche_slug: str,
    source_path: Path,
) -> str:
    """Render full markdown content cho insight pack."""
    quality_notes = compute_data_quality_notes(angles)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    L: list[str] = []
    L.append(f"# Insight Pack for Nhi Hien CoWork — `{niche_slug}`")
    L.append("")
    L.append(f"> **Phiên bản**: auto-generated {ts}")
    L.append(f"> **Mục đích**: mỗi insight là 1 input cho Content Proposal Protocol bên CoWork")
    L.append(f"> **Nguồn dữ liệu**: `{source_path.as_posix()}`")
    L.append(f"> **Tổng insight unique**: {len(angles)}")
    L.append(f"> **Module**: `tim export-for-cowork`")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Cách CoWork dùng file này")
    L.append("")
    L.append("1. Copy file này sang `D:\\Nhi Hien CoWork\\WORK AREAS\\Marketing\\<project>\\inputs\\insights-pack_v1.md`")
    L.append("2. Mỗi insight bên dưới là **1 input riêng** cho Content Proposal Protocol")
    L.append("3. Hiền chọn 1 insight → trigger Claude CoWork đẻ 3-5 concept chấm điểm 5 trục → chọn 1 concept")
    L.append("4. Claude CoWork viết bài theo flow 7 bước (đọc `00_README.md` ABOUT ME)")
    L.append("")
    L.append("---")
    L.append("")

    if quality_notes:
        L.append("## Notes về batch dữ liệu hiện tại")
        L.append("")
        for note in quality_notes:
            L.append(f"- {note}")
        L.append("")
        L.append("---")
        L.append("")

    for idx, angle in enumerate(angles, start=1):
        L.append(format_insight_block(idx, angle, mapping))

    L.append("")
    L.append(f"## Distribution toàn bộ batch ({len(angles)} insight)")
    L.append("")
    L.append(format_distribution_table(angles, mapping))
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"**Generated by**: `tim export-for-cowork` ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    L.append(f"**Source**: `{source_path.as_posix()}`")
    L.append("")

    return "\n".join(L)


# --- Entry point ---

def snapshot_to_drive(
    source: Path,
    snapshot_root: Path,
    niche_slug: str,
) -> Path | None:
    """Copy source file sang snapshot_root/<niche-slug>/insights-pack_v<N>.md với versioning.

    Mode LOCAL (PC anh): snapshot_root là Drive Desktop folder local.

    Logic versioning:
    - Lần 1: insights-pack_v1.md
    - Lần 2: insights-pack_v2.md (không ghi đè v1)

    Returns:
        Path file mới sau snapshot, hoặc None nếu snapshot_root không tồn tại
    """
    if not snapshot_root.exists():
        logger.warning(
            "Snapshot dir không tồn tại: %s — skip snapshot. "
            "Local mode cần Drive Desktop sync folder này về local. "
            "Hoặc dùng API mode (set GDRIVE_SERVICE_ACCOUNT_JSON + INSIGHTS_PACK_DRIVE_FOLDER_ID).",
            snapshot_root,
        )
        return None

    niche_dir = snapshot_root / niche_slug
    niche_dir.mkdir(parents=True, exist_ok=True)

    # Find next version (scan files insights-pack_v<N>.md hiện có)
    max_v = 0
    for f in niche_dir.glob("insights-pack_v*.md"):
        m = re.match(r"insights-pack_v(\d+)\.md$", f.name)
        if m:
            v = int(m.group(1))
            if v > max_v:
                max_v = v
    next_v = max_v + 1

    dest = niche_dir / f"insights-pack_v{next_v}.md"
    shutil.copy2(source, dest)
    logger.info("Snapshot to Drive (local mode): %s", dest)
    return dest


def snapshot_to_drive_api(
    source: Path,
    root_folder_id: str,
    niche_slug: str,
    service_account_json: str,
) -> dict[str, Any] | None:
    """Upload file lên Drive thông qua API với versioning.

    Mode API (server cloud): không cần Drive Desktop sync local — upload thẳng cloud.

    Args:
        source: file gốc ở miner _master/insights-pack-for-cowork.md
        root_folder_id: Drive folder ID (vd "1S27BXGisZTNZ63EgrINDxhMTVvmrue8W" cho insights-packs/)
        niche_slug: tên niche → tạo subfolder cùng tên trên Drive
        service_account_json: nội dung JSON file service account (string)

    Returns:
        dict {file_id, file_name, web_link, version} hoặc None nếu fail
    """
    try:
        # Lazy import — chỉ load khi cần (giảm startup time)
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
    except ImportError as e:
        logger.error(
            "Drive API libs chưa cài. Run: pip install google-api-python-client google-auth. Error: %s",
            e,
        )
        return None

    if not source.exists():
        logger.error("Source file không tồn tại: %s", source)
        return None

    try:
        credentials_info = json.loads(service_account_json)
    except json.JSONDecodeError as e:
        logger.error("GDRIVE_SERVICE_ACCOUNT_JSON không phải JSON hợp lệ: %s", e)
        return None

    try:
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    except Exception as e:
        logger.error("Không tạo được Drive API client: %s", e)
        return None

    try:
        # 1. Find or create subfolder for niche
        niche_folder_id = _drive_find_or_create_folder(service, niche_slug, root_folder_id)
        if not niche_folder_id:
            return None

        # 2. Find next version number
        next_v = _drive_find_next_version(service, niche_folder_id)

        # 3. Upload file
        file_name = f"insights-pack_v{next_v}.md"
        file_metadata = {
            "name": file_name,
            "parents": [niche_folder_id],
        }
        media = MediaFileUpload(str(source), mimetype="text/markdown", resumable=False)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name, webViewLink",
        ).execute()

        logger.info(
            "Snapshot to Drive (API mode): %s (id=%s) → %s",
            file_name, uploaded.get("id"), uploaded.get("webViewLink"),
        )
        return {
            "file_id": uploaded.get("id"),
            "file_name": uploaded.get("name"),
            "web_link": uploaded.get("webViewLink"),
            "version": next_v,
        }
    except HttpError as e:
        logger.error("Drive API HTTP error: %s", e)
        return None
    except Exception as e:
        logger.error("Drive API upload failed: %s", e)
        return None


def _drive_find_or_create_folder(service: Any, name: str, parent_id: str) -> str | None:
    """Tìm subfolder cùng tên trong parent. Nếu chưa có → tạo mới. Return folder ID."""
    try:
        # Search existing folder
        query = (
            f"name='{name}' and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"'{parent_id}' in parents and "
            f"trashed=false"
        )
        results = service.files().list(q=query, fields="files(id, name)", pageSize=1).execute()
        files = results.get("files", [])
        if files:
            return files[0]["id"]

        # Create new folder
        folder_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        folder = service.files().create(body=folder_metadata, fields="id").execute()
        logger.info("Created Drive subfolder: %s (id=%s)", name, folder.get("id"))
        return folder.get("id")
    except Exception as e:
        logger.error("_drive_find_or_create_folder failed: %s", e)
        return None


def _drive_find_next_version(service: Any, folder_id: str) -> int:
    """Scan files insights-pack_v<N>.md trong folder, return next version (max + 1)."""
    try:
        query = (
            f"'{folder_id}' in parents and "
            f"name contains 'insights-pack_v' and "
            f"trashed=false"
        )
        results = service.files().list(q=query, fields="files(name)", pageSize=1000).execute()
        files = results.get("files", [])
        max_v = 0
        for f in files:
            m = re.match(r"insights-pack_v(\d+)\.md$", f.get("name", ""))
            if m:
                v = int(m.group(1))
                if v > max_v:
                    max_v = v
        return max_v + 1
    except Exception as e:
        logger.warning("_drive_find_next_version failed (default v1): %s", e)
        return 1


def export_for_cowork(
    selected_path: Path,
    config_path: Path,
    output_path: Path | None = None,
    snapshot_dir: Path | None = None,
    drive_folder_id: str | None = None,
    gdrive_service_account_json: str | None = None,
) -> dict[str, Any]:
    """All-in-one: load → dedupe → render → write [→ snapshot to Drive].

    2 snapshot modes (xài mode nào tuỳ env):
    - LOCAL mode: pass snapshot_dir (folder Drive Desktop sync local). Dùng cho PC anh.
    - API mode: pass drive_folder_id + gdrive_service_account_json. Dùng cho server cloud.

    Args:
        selected_path: Path tới _master/selected_angles.json
        config_path: Path tới niche_configs/<niche>.json
        output_path: Override output (default = selected_path.parent / 'insights-pack-for-cowork.md')
        snapshot_dir: LOCAL mode — folder Drive sync local.
        drive_folder_id: API mode — Drive folder ID (vd "1S27BXG...")
        gdrive_service_account_json: API mode — nội dung JSON service account.

    Returns:
        dict keys: input_count, unique_count, duplicates_removed, distribution,
                   output_path, niche_slug, data_quality_notes,
                   snapshot_path (LOCAL mode), snapshot_drive_info (API mode)
    """
    if not selected_path.exists():
        raise FileNotFoundError(f"selected_angles.json không tồn tại: {selected_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"Niche config không tồn tại: {config_path}")

    angles_raw: list[dict[str, Any]] = json.loads(selected_path.read_text(encoding="utf-8"))
    config: dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))

    niche_slug = config.get("niche_slug", "unknown-niche")

    angles = dedupe_by_quote(angles_raw)

    # Sort theo score desc, sau đó theo problem_code (để gom nhóm)
    angles.sort(
        key=lambda a: (-(a.get("score") or 0), a.get("problem_code") or ""),
    )

    mapping = load_problem_mapping(config)

    content = render_pack(angles, mapping, niche_slug, selected_path)

    if output_path is None:
        output_path = selected_path.parent / "insights-pack-for-cowork.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    distribution = Counter(a.get("problem_code") for a in angles)

    logger.info(
        "Exported %d unique insights to %s (input had %d, deduped to %d)",
        len(angles), output_path, len(angles_raw), len(angles),
    )

    snapshot_path: Path | None = None
    snapshot_drive_info: dict[str, Any] | None = None

    # Priority: API mode > LOCAL mode (chọn cái nào có đủ config)
    if drive_folder_id and gdrive_service_account_json:
        snapshot_drive_info = snapshot_to_drive_api(
            output_path,
            drive_folder_id,
            niche_slug,
            gdrive_service_account_json,
        )
    elif snapshot_dir is not None:
        snapshot_path = snapshot_to_drive(output_path, snapshot_dir, niche_slug)

    return {
        "input_count": len(angles_raw),
        "unique_count": len(angles),
        "duplicates_removed": len(angles_raw) - len(angles),
        "distribution": dict(distribution),
        "output_path": output_path,
        "niche_slug": niche_slug,
        "data_quality_notes": compute_data_quality_notes(angles),
        "snapshot_path": snapshot_path,
        "snapshot_drive_info": snapshot_drive_info,
    }
