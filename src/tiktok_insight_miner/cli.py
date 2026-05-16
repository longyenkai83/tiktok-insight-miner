"""CLI entry point — argparse với subcommands init / scrape / classify / report / suggest / run."""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from tiktok_insight_miner.classifier import (
    classify_comments,
    load_classified_json,
    save_classified_json,
)
from tiktok_insight_miner.comment_importer import import_comments
from tiktok_insight_miner.content_calendar import build_calendar
from tiktok_insight_miner.cowork_exporter import export_for_cowork
from tiktok_insight_miner.insight_bank import build_insight_bank
from tiktok_insight_miner.production import run_production
from tiktok_insight_miner.reporter import generate_report
from tiktok_insight_miner.selection import run_selection
from tiktok_insight_miner.scraper import (
    load_comments_json,
    save_comments_json,
    scrape_tiktok_comments,
)
from tiktok_insight_miner.suggester import generate_brief


def _read_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = []
    if args.urls:
        urls.extend(args.urls)
    if args.urls_file:
        path = Path(args.urls_file)
        if not path.exists():
            sys.exit(f"URLs file không tồn tại: {path}")
        urls.extend(
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        )
    if not urls:
        sys.exit("Cần --urls hoặc --urls-file")
    return urls


def cmd_scrape(args: argparse.Namespace) -> None:
    urls = _read_urls(args)
    comments = scrape_tiktok_comments(urls, max_comments_per_video=args.max_comments)
    save_comments_json(comments, Path(args.output))
    print(f"✓ Scraped {len(comments)} comments → {args.output}")


def cmd_classify(args: argparse.Namespace) -> None:
    comments = load_comments_json(Path(args.input))
    print(f"Loaded {len(comments)} comments từ {args.input}")
    classified = classify_comments(
        comments,
        model=args.model,
        batch_size=args.batch_size,
    )
    save_classified_json(classified, Path(args.output))
    print(f"✓ Classified {len(classified)} comments → {args.output}")


def cmd_report(args: argparse.Namespace) -> None:
    classified = load_classified_json(Path(args.input))
    print(f"Loaded {len(classified)} classified comments từ {args.input}")
    generate_report(classified, Path(args.output), top_n=args.top_n)
    print(f"✓ Report → {args.output}")


_NICHE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")

_URLS_TEMPLATE = """\
# Niche: {niche}
# Run date: {run_date}
# Mỗi dòng 1 URL TikTok video. Dòng bắt đầu bằng # bị bỏ qua.
# Ví dụ:
# https://www.tiktok.com/@user1/video/1234567890
# https://www.tiktok.com/@user2/video/9876543210
"""

_NOTES_TEMPLATE = """\
# Notes — {niche} — {run_date}

> Sau khi đọc `report.md` + `brief.md`, viết vào đây 3-5 insight đáng nhớ nhất.
> 6 tháng sau chỉ cần đọc file này là nhớ ngay (không phải mở lại report đầy đủ).

## 🎯 Top insight (3-5 bullet)

1. _(fill sau khi đọc report)_

## 💡 Top angle nên test (từ brief.md)

1. _(angle # mấy, lý do chọn)_

## 🤔 Câu hỏi mở / cần research thêm

- _(điều gì chưa rõ, cần chạy lại với niche khác / video khác)_

## 🔗 Cross-niche connection

- _(insight này liên quan đến niche nào em đã làm trước? pattern chung?)_
"""

_INDEX_HEADER = """\
# 📚 Insight Index

| Niche | Run date | Videos | Comments | Top insight | Brief? |
|---|---|---|---|---|---|
"""


def cmd_init(args: argparse.Namespace) -> None:
    niche = args.niche.strip().lower()
    if not _NICHE_SLUG_RE.match(niche):
        sys.exit(
            f"Niche slug không hợp lệ: '{niche}'. "
            "Dùng kebab-case (a-z, 0-9, dấu -). Ví dụ: skincare-acne, food-banh-mi"
        )

    run_date = args.date or date.today().isoformat()
    output_root = Path(args.output_root)
    niche_dir = output_root / niche / run_date

    if niche_dir.exists() and any(niche_dir.iterdir()):
        sys.exit(
            f"Folder '{niche_dir}' đã tồn tại và không trống. "
            "Dùng --date YYYY-MM-DD để chọn date khác, hoặc xóa folder cũ trước."
        )

    niche_dir.mkdir(parents=True, exist_ok=True)

    urls_path = niche_dir / "urls.txt"
    notes_path = niche_dir / "notes.md"
    urls_path.write_text(
        _URLS_TEMPLATE.format(niche=niche, run_date=run_date),
        encoding="utf-8",
    )
    notes_path.write_text(
        _NOTES_TEMPLATE.format(niche=niche, run_date=run_date),
        encoding="utf-8",
    )

    # Update master index (tạo nếu chưa có)
    index_path = output_root / "_index.md"
    rel_link = f"{niche}/{run_date}/"
    new_row = f"| [{niche}]({rel_link}) | {run_date} | TBD | TBD | _(fill sau)_ | ⏳ |\n"
    if index_path.exists():
        existing = index_path.read_text(encoding="utf-8")
        if rel_link not in existing:
            index_path.write_text(existing.rstrip() + "\n" + new_row, encoding="utf-8")
    else:
        index_path.write_text(_INDEX_HEADER + new_row, encoding="utf-8")

    print(f"✓ Created: {niche_dir}")
    print(f"  - {urls_path.name} (paste TikTok URLs vào đây)")
    print(f"  - {notes_path.name} (viết tay sau khi đọc report)")
    print(f"✓ Updated: {index_path}")
    print()
    print("📋 Next steps:")
    print(f"  1. Edit {urls_path} — paste URLs (mỗi dòng 1 cái)")
    print(f"  2. Chạy lệnh sau (đã fill sẵn paths):")
    print()
    # Lệnh template — dùng forward slash để paste vào PowerShell vẫn work
    cmd = (
        f'python -m tiktok_insight_miner run '
        f'--urls-file "{urls_path}" '
        f'--max-comments 100 '
        f'--with-angles '
        f'-o "{niche_dir}"'
    )
    print(f"     {cmd}")
    print()
    print(f"  3. Đọc {niche_dir / 'report.md'} + {niche_dir / 'brief.md'}")
    print(f"  4. Update {notes_path} với insight quan trọng")
    print(f"  5. Update top insight cell trong {index_path}")


def cmd_suggest(args: argparse.Namespace) -> None:
    classified = load_classified_json(Path(args.input))
    print(f"Loaded {len(classified)} classified comments từ {args.input}")
    angles = generate_brief(
        classified,
        Path(args.output),
        num_angles=args.num,
        top_n_per_bucket=args.top_per_bucket,
        model=args.model,
    )
    if angles:
        print(f"✓ {len(angles)} content angles → {args.output}")
    else:
        sys.exit("❌ Không generate được angle nào (kiểm tra log).")


def cmd_import_comments(args: argparse.Namespace) -> None:
    """Import comment thủ công từ CSV/XLSX → raw_comments.json (cho FB / YT / nguồn khác)."""
    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"❌ File input không tồn tại: {input_path}")

    output_root = Path(
        args.output_root or os.environ.get("DEFAULT_OUTPUT_DIR", "./output")
    )

    print(f"Reading: {input_path}")
    print(f"Niche:   {args.niche}")
    if args.source:
        print(f"Source:  {args.source} (override default 'manual')")
    print()

    try:
        stats = import_comments(
            input_path=input_path,
            niche_slug=args.niche,
            output_root=output_root,
            source_override=args.source,
            run_date=args.date,
        )
    except (ValueError, FileNotFoundError, ImportError) as e:
        sys.exit(f"❌ Lỗi import: {e}")

    print(f"📊 Kết quả:")
    print(f"   Số dòng đọc:        {stats['total_rows']}")
    print(f"   Comment hợp lệ:     {stats['kept']}")
    print(f"   Bỏ qua (rỗng):      {stats['skipped_empty']}")
    print(f"   Bỏ qua (<5 ký tự):  {stats['skipped_short']}")
    print(f"   Cột text:           '{stats['text_column']}'")
    print()
    print(f"✓ Output: {stats['output_path']}")
    print()
    print("👉 Bước tiếp: classify file này:")
    print(
        f"     python -m tiktok_insight_miner classify "
        f"-i \"{stats['output_path']}\" -o \"{stats['output_path'].parent / 'classified.json'}\""
    )


def cmd_production(args: argparse.Namespace) -> None:
    """Generate file `4-thực-thi/angle-XX-*.md` từ selected_angles.json."""
    angles_path = Path(args.input)
    config_path = Path(args.config)
    if not angles_path.exists():
        sys.exit(f"❌ selected_angles.json không tồn tại: {angles_path}")
    if not config_path.exists():
        sys.exit(f"❌ Niche config không tồn tại: {config_path}")

    use_claude = not args.no_claude

    print(f"Loading angles: {angles_path}")
    print(f"Loading config: {config_path}")
    print(f"Mode: {'Claude (' + (args.model or 'default model') + ')' if use_claude else 'Fallback template'}")
    if args.limit:
        print(f"Limit: chỉ generate {args.limit} angle đầu")
    if args.overwrite:
        print("Overwrite: ON — ghi đè file đã tồn tại")
    print()

    stats = run_production(
        angles_json=angles_path,
        config_path=config_path,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        use_claude=use_claude,
        model=args.model,
        limit=args.limit,
        overwrite=args.overwrite,
    )

    print()
    print(f"📊 Tổng angle đọc:        {stats['total_angles']}")
    print(f"   Claude generate:       {stats['generated_claude']}")
    print(f"   Fallback template:     {stats['generated_fallback']}")
    print(f"   Skip (đã có file):     {stats['skipped_existing']}")
    print(f"   Failed:                {stats['failed']}")
    print()
    print(f"📂 Output folder: {stats['output_dir']}")
    print(f"   {len(stats['files'])} file:")
    for f in stats["files"][:10]:
        print(f"     - {f.name}")
    if len(stats["files"]) > 10:
        print(f"     ... ({len(stats['files']) - 10} file khác)")


def cmd_calendar(args: argparse.Namespace) -> None:
    """Generate content calendar (.md + .json) từ strategy config + insight pool."""
    strategy_path = Path(args.strategy)
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not strategy_path.exists():
        sys.exit(f"❌ Strategy config không tồn tại: {strategy_path}")
    if not input_path.exists():
        sys.exit(f"❌ Insight pool input không tồn tại: {input_path}")

    print(f"Loading strategy: {strategy_path}")
    print(f"Loading insight pool: {input_path}")
    print()

    try:
        result = build_calendar(strategy_path, input_path, output_dir)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"❌ Lỗi build calendar: {e}")

    print(f"📊 Strategy:  {result['strategy_id']}")
    print(f"   Source:    {result['source_format']} ({result['pool_kept']}/{result['pool_size']} insights after constraints filter)")
    print(f"   Days:      {result['days_count']}")
    print(f"   Unique insights used: {result['unique_insights']}")
    if result['unique_insights'] < result['days_count']:
        avg = result['days_count'] / max(result['unique_insights'], 1)
        print(f"   ⚠️  Pool nhỏ — avg reuse: {avg:.1f}x per insight")
    print()
    print(f"   Format distribution:")
    for fmt, cnt in result['format_counts'].items():
        print(f"     {fmt}: {cnt}")
    print()
    print(f"   Problem distribution:")
    for prob, cnt in sorted(result['problem_counts'].items(), key=lambda x: -x[1]):
        print(f"     {prob}: {cnt}")
    print()
    print("✓ Output:")
    print(f"   📋 {result['md_path']}")
    print(f"   📄 {result['json_path']}")
    if result['backup_path']:
        print(f"   💾 Backed up old .md → {result['backup_path']}")
    print()
    print("👉 Bước tiếp: anh đọc calendar → quyết lịch quay → Day 1.")


def cmd_select(args: argparse.Namespace) -> None:
    """Parse 3-lựa-chọn.md đã tick → append vào _master/content-pipeline.md + selected_angles.json."""
    md_path = Path(args.input)
    if not md_path.exists():
        sys.exit(f"❌ File không tồn tại: {md_path}")

    print(f"Reading: {md_path}")
    result = run_selection(
        md_path,
        niche_slug=args.niche,
        output_root=Path(args.output_root) if args.output_root else None,
    )

    if result["selected_count"] == 0:
        print()
        print("ℹ️  Chưa có insight nào được chọn.")
        print(f"   Hãy mở file `{md_path}`, tick `[x]` các angle muốn quay,")
        print("   rồi chạy lại lệnh này.")
        print()
        print("   (KHÔNG tạo content-pipeline rỗng để tránh nhiễu.)")
        return

    print()
    print(f"📊 Niche:       {result['niche']}")
    print(f"   Source run:  {result['source_run']}")
    print(f"   Đã tick:     {result['selected_count']} angle")
    print(f"   Mới thêm:    {result['added']} (đã loại trùng quote)")
    print(f"   Giữ từ pipeline cũ: {result['kept_existing']}")
    print(f"   Tổng pipeline: {result['total']}")
    print()
    print("✓ Output files:")
    print(f"   📋 {result['pipeline_path']}")
    print(f"   📄 {result['json_path']}")
    print()
    print("👉 Bước tiếp: chạy `tim production` để generate script đầy đủ cho mỗi angle.")
    print("   (production.py — chưa làm trong MVP)")


def cmd_bank(args: argparse.Namespace) -> None:
    """Build insight bank: 1-liệt-kê.csv + 2-sắp-xếp.md + 3-lựa-chọn.md."""
    classified_path = Path(args.input)
    config_path = Path(args.config)
    output_dir = Path(args.output_dir) if args.output_dir else None

    if not classified_path.exists():
        sys.exit(f"❌ classified.json không tồn tại: {classified_path}")
    if not config_path.exists():
        sys.exit(f"❌ Niche config không tồn tại: {config_path}")

    print(f"Loading config: {config_path}")
    print(f"Loading classified: {classified_path}")

    stats = build_insight_bank(classified_path, config_path, output_dir=output_dir)

    print()
    print(f"📊 Niche: {stats['niche_slug']}")
    print(f"   Total insights đọc:   {stats['total']}")
    print(f"   Giữ lại (actionable): {stats['kept']}")
    print(f"   Loại do bucket:       {stats['skipped_bucket']} (praise/mention/other)")
    print(f"   Loại do quote ngắn:   {stats['skipped_short']} (<5 ký tự)")
    print()
    print("✓ Output files:")
    print(f"   1️⃣  Liệt kê:   {stats['csv_path']}")
    print(f"   2️⃣  Sắp xếp:   {stats['sap_xep_path']}")
    print(f"   3️⃣  Lựa chọn:  {stats['lua_chon_path']}")
    print()
    print("👉 Mở `3-lựa-chọn.md`, tick checkbox top 5-10 angle muốn quay tuần này.")


def cmd_export_for_cowork(args: argparse.Namespace) -> None:
    """Generate insight pack markdown cho handoff sang CoWork [+ snapshot to Drive]."""
    selected_path = Path(args.input)
    config_path = Path(args.config)
    output_path = Path(args.output) if args.output else None

    # Resolve snapshot mode: API > LOCAL > None
    drive_folder_id = (
        args.snapshot_drive_folder_id
        or os.environ.get("INSIGHTS_PACK_DRIVE_FOLDER_ID", "").strip()
        or None
    )
    gdrive_json = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON", "").strip() or None

    snapshot_dir_str = args.snapshot_to or os.environ.get("INSIGHTS_PACK_DRIVE_DIR", "").strip()
    snapshot_dir = Path(snapshot_dir_str) if snapshot_dir_str else None

    if not selected_path.exists():
        sys.exit(f"❌ selected_angles.json không tồn tại: {selected_path}")
    if not config_path.exists():
        sys.exit(f"❌ Niche config không tồn tại: {config_path}")

    print(f"Loading selected_angles: {selected_path}")
    print(f"Loading niche config:    {config_path}")
    if drive_folder_id and gdrive_json:
        print(f"Snapshot mode:           API (folder_id={drive_folder_id})")
    elif snapshot_dir:
        print(f"Snapshot mode:           LOCAL ({snapshot_dir})")
    else:
        print(f"Snapshot mode:           OFF (no snapshot)")
    print()

    try:
        result = export_for_cowork(
            selected_path, config_path, output_path,
            snapshot_dir=snapshot_dir,
            drive_folder_id=drive_folder_id,
            gdrive_service_account_json=gdrive_json,
        )
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"❌ Lỗi export: {e}")

    print(f"📊 Niche:                 {result['niche_slug']}")
    print(f"   Input records:         {result['input_count']}")
    print(f"   Unique insights:       {result['unique_count']}")
    print(f"   Duplicates removed:    {result['duplicates_removed']}")
    print()
    print(f"   Distribution by nhóm:")
    for code, cnt in sorted(result['distribution'].items(), key=lambda kv: -kv[1]):
        print(f"     {code}: {cnt}")
    print()
    if result['data_quality_notes']:
        print(f"   Data quality notes:")
        for note in result['data_quality_notes']:
            print(f"     - {note}")
        print()
    print(f"✓ Output (miner):  {result['output_path']}")
    if result.get('snapshot_drive_info'):
        info = result['snapshot_drive_info']
        print(f"✓ Snapshot (Drive API): {info['file_name']} (v{info['version']})")
        print(f"   Drive link:    {info['web_link']}")
        print()
        print(f"👉 File đã lên cloud. CoWork pull được ngay qua MCP Drive.")
    elif result.get('snapshot_path'):
        print(f"✓ Snapshot (Drive local): {result['snapshot_path']}")
        print()
        print(f"👉 Drive Desktop sync sẽ tự đẩy lên cloud. CoWork pull được sau vài giây.")
    elif snapshot_dir or drive_folder_id:
        print(f"⚠️  Snapshot skip — check log để biết lý do (folder không tồn tại / API auth fail / etc.)")
    else:
        print(f"👉 Bước tiếp: copy file này sang CoWork (manual) hoặc setup env var snapshot.")


def cmd_run(args: argparse.Namespace) -> None:
    """All-in-one: scrape → classify → report."""
    urls = _read_urls(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_path = output_dir / "raw_comments.json"
    classified_path = output_dir / "classified.json"
    report_path = output_dir / "report.md"
    brief_path = output_dir / "brief.md"

    total_stages = 4 if args.with_angles else 3

    # Stage 1: scrape
    print(f"\n[1/{total_stages}] Scraping {len(urls)} videos...")
    comments = scrape_tiktok_comments(urls, max_comments_per_video=args.max_comments)
    save_comments_json(comments, raw_path)
    print(f"✓ {len(comments)} comments → {raw_path}")

    if not comments:
        sys.exit("Không scrape được comment nào, dừng.")

    # Stage 2: classify
    print(f"\n[2/{total_stages}] Classifying...")
    classified = classify_comments(
        comments,
        model=args.model,
        batch_size=args.batch_size,
    )
    save_classified_json(classified, classified_path)
    print(f"✓ {len(classified)} classified → {classified_path}")

    if not classified:
        sys.exit("Không classify được comment nào, dừng.")

    # Stage 3: report
    print(f"\n[3/{total_stages}] Generating report...")
    generate_report(classified, report_path, top_n=args.top_n)
    print(f"✓ Report → {report_path}")

    # Stage 4 (optional): content angle brief
    if args.with_angles:
        print(f"\n[4/{total_stages}] Generating content angle brief...")
        suggester_model = args.suggester_model or args.model
        angles = generate_brief(
            classified,
            brief_path,
            num_angles=args.num_angles,
            model=suggester_model,
        )
        if angles:
            print(f"✓ {len(angles)} angles → {brief_path}")
        else:
            print("⚠️ Không generate được angle (xem log)")

    print(f"\n🎉 Done. Mở {report_path} để xem insight.")
    if args.with_angles:
        print(f"   Brief: {brief_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tim",
        description="TikTok Insight Miner — quét comment, phân loại bằng Claude, xuất báo cáo markdown.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Bật debug log",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- init (scaffold niche folder) ---
    p_init = sub.add_parser(
        "init",
        help="Scaffold folder mới cho 1 niche/run (output/<niche>/<date>/) + update index",
    )
    p_init.add_argument(
        "niche",
        type=str,
        help="Niche slug, kebab-case (vd: skincare-acne, food-banh-mi-saigon)",
    )
    p_init.add_argument(
        "--date", type=str, default=None,
        help="Date của run (YYYY-MM-DD, default = hôm nay)",
    )
    p_init.add_argument(
        "--output-root", type=str,
        default=os.environ.get("DEFAULT_OUTPUT_DIR", "./output"),
        help="Root folder chứa niches (default ./output)",
    )
    p_init.set_defaults(func=cmd_init)

    # --- shared args helper ---
    def add_url_args(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--urls", action="append", default=[],
            help="TikTok video URL (lặp nhiều lần được)",
        )
        p.add_argument(
            "--urls-file", type=str, help="File text mỗi dòng 1 URL (# = comment)",
        )
        p.add_argument(
            "--max-comments", type=int, default=100,
            help="Số comment tối đa mỗi video (default 100)",
        )

    def add_classify_args(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--model", type=str, default=None,
            help="Override ANTHROPIC_MODEL (default claude-opus-4-7)",
        )
        p.add_argument(
            "--batch-size", type=int, default=None,
            help="Comments per API call (default 20)",
        )

    # --- scrape ---
    p_scrape = sub.add_parser("scrape", help="Scrape comments từ TikTok videos")
    add_url_args(p_scrape)
    p_scrape.add_argument(
        "-o", "--output", type=str, required=True,
        help="Output JSON file path",
    )
    p_scrape.set_defaults(func=cmd_scrape)

    # --- classify ---
    p_classify = sub.add_parser("classify", help="Classify comments bằng Claude")
    p_classify.add_argument(
        "-i", "--input", type=str, required=True, help="Input JSON từ scrape",
    )
    p_classify.add_argument(
        "-o", "--output", type=str, required=True, help="Output JSON",
    )
    add_classify_args(p_classify)
    p_classify.set_defaults(func=cmd_classify)

    # --- report ---
    p_report = sub.add_parser("report", help="Generate markdown report")
    p_report.add_argument(
        "-i", "--input", type=str, required=True, help="Input JSON từ classify",
    )
    p_report.add_argument(
        "-o", "--output", type=str, required=True, help="Output markdown file",
    )
    p_report.add_argument(
        "--top-n", type=int, default=10,
        help="Top N quotes hiển thị mỗi bucket (default 10)",
    )
    p_report.set_defaults(func=cmd_report)

    # --- suggest (content angle brief) ---
    p_suggest = sub.add_parser(
        "suggest",
        help="Generate content angle brief từ classified comments (v0.2)",
    )
    p_suggest.add_argument(
        "-i", "--input", type=str, required=True, help="Input JSON từ classify",
    )
    p_suggest.add_argument(
        "-o", "--output", type=str, required=True,
        help="Output markdown file (kèm theo .json sẽ được tạo song song)",
    )
    p_suggest.add_argument(
        "--num", type=int, default=10,
        help="Số angle cần generate (default 10)",
    )
    p_suggest.add_argument(
        "--top-per-bucket", type=int, default=5,
        help="Top N comments mỗi bucket actionable làm input cho Claude (default 5)",
    )
    p_suggest.add_argument(
        "--model", type=str, default=None,
        help="Override model cho suggester (default Opus 4.7 — task creative cần intelligence)",
    )
    p_suggest.set_defaults(func=cmd_suggest)

    # --- bank (build insight bank theo niche config) ---
    p_bank = sub.add_parser(
        "bank",
        help="Build insight bank: 1-liệt-kê.csv + 2-sắp-xếp.md + 3-lựa-chọn.md (theo niche_config)",
    )
    p_bank.add_argument(
        "-i", "--input", type=str, required=True,
        help="Input classified.json từ stage classify",
    )
    p_bank.add_argument(
        "--config", type=str, required=True,
        help="Path tới niche_configs/<niche>.json",
    )
    p_bank.add_argument(
        "-o", "--output-dir", type=str, default=None,
        help="Folder output (default = folder của classified.json)",
    )
    p_bank.set_defaults(func=cmd_bank)

    # --- select (parse 3-lựa-chọn.md đã tick → content-pipeline.md) ---
    p_select = sub.add_parser(
        "select",
        help="Parse 3-lựa-chọn.md đã tick → append vào _master/content-pipeline.md",
    )
    p_select.add_argument(
        "-i", "--input", type=str, required=True,
        help="Path tới 3-lựa-chọn.md đã tick `[x]`",
    )
    p_select.add_argument(
        "--niche", type=str, default=None,
        help="Override niche slug (default = tên folder cha của niche root)",
    )
    p_select.add_argument(
        "--output-root", type=str, default=None,
        help="Override folder chứa _master/ (default = niche root)",
    )
    p_select.set_defaults(func=cmd_select)

    # --- calendar (generate content calendar from strategy config) ---
    p_cal = sub.add_parser(
        "calendar",
        help="Generate content calendar (.md + .json) từ strategy config + insight pool",
    )
    p_cal.add_argument(
        "-i", "--input", type=str, required=True,
        help="Path tới selected_angles.json (ưu tiên) hoặc classified.json (fallback)",
    )
    p_cal.add_argument(
        "--strategy", type=str, required=True,
        help="Path tới strategy_configs/<strategy>.json",
    )
    p_cal.add_argument(
        "-o", "--output-dir", type=str, required=True,
        help="Folder output cho .md + .json (vd output/<niche>/_master/)",
    )
    p_cal.set_defaults(func=cmd_calendar)

    # --- production (generate 4-thực-thi/angle-XX-*.md) ---
    p_prod = sub.add_parser(
        "production",
        help="Generate file thực thi đầy đủ (hook + script 60s + B-roll + caption + checklist) từ selected_angles.json",
    )
    p_prod.add_argument(
        "-i", "--input", type=str, required=True,
        help="Path tới _master/selected_angles.json (output Bước 3)",
    )
    p_prod.add_argument(
        "--config", type=str, required=True,
        help="Path tới niche_configs/<niche>.json",
    )
    p_prod.add_argument(
        "-o", "--output-dir", type=str, default=None,
        help="Override folder 4-thực-thi/ (default = niche_root/4-thực-thi/)",
    )
    p_prod.add_argument(
        "--no-claude", action="store_true",
        help="Bỏ qua Claude, dùng fallback template (rule-based, không tốn API)",
    )
    p_prod.add_argument(
        "--model", type=str, default=None,
        help="Override Claude model (default = ANTHROPIC_MODEL trong .env, fallback claude-opus-4-7)",
    )
    p_prod.add_argument(
        "--limit", type=int, default=None,
        help="Chỉ generate N angle đầu (cho test, tiết kiệm cost)",
    )
    p_prod.add_argument(
        "--overwrite", action="store_true",
        help="Ghi đè file đã tồn tại (default skip)",
    )
    p_prod.set_defaults(func=cmd_production)

    # --- export-for-cowork (handoff sang Nhi Hien CoWork) ---
    p_export = sub.add_parser(
        "export-for-cowork",
        help="Generate insight pack markdown cho handoff sang Nhi Hien CoWork (từ selected_angles.json + niche_config)",
    )
    p_export.add_argument(
        "-i", "--input", type=str, required=True,
        help="Path tới _master/selected_angles.json (output Bước 3)",
    )
    p_export.add_argument(
        "--config", type=str, required=True,
        help="Path tới niche_configs/<niche>.json (cần có freedom_layer mapping v1.4+)",
    )
    p_export.add_argument(
        "-o", "--output", type=str, default=None,
        help="Override output path (default = _master/insights-pack-for-cowork.md)",
    )
    p_export.add_argument(
        "--snapshot-to", type=str, default=None,
        help="LOCAL mode — folder Drive Desktop sync local. "
             "Override env var INSIGHTS_PACK_DRIVE_DIR.",
    )
    p_export.add_argument(
        "--snapshot-drive-folder-id", type=str, default=None,
        help="API mode — Drive folder ID (vd '1S27BXG...'). "
             "Cần kèm env var GDRIVE_SERVICE_ACCOUNT_JSON. "
             "Override env var INSIGHTS_PACK_DRIVE_FOLDER_ID.",
    )
    p_export.set_defaults(func=cmd_export_for_cowork)

    # --- import-comments (manual import từ CSV/XLSX) ---
    p_import = sub.add_parser(
        "import-comments",
        help="Import comment thủ công từ CSV/XLSX (FB / YouTube / nguồn khác) → raw_comments.json",
    )
    p_import.add_argument(
        "-i", "--input", type=str, required=True,
        help="Path tới file .csv hoặc .xlsx (cột bắt buộc: 'comment' hoặc 'text')",
    )
    p_import.add_argument(
        "--niche", type=str, required=True,
        help="Niche slug (vd kinh-doanh-27-45) — dùng để tạo folder output",
    )
    p_import.add_argument(
        "--source", type=str, default=None,
        help="Override platform khi cột empty (vd: facebook, youtube, group). Default 'manual'.",
    )
    p_import.add_argument(
        "--date", type=str, default=None,
        help="Date của run (YYYY-MM-DD, default = hôm nay)",
    )
    p_import.add_argument(
        "--output-root", type=str, default=None,
        help="Override root folder (default = $DEFAULT_OUTPUT_DIR hoặc ./output)",
    )
    p_import.set_defaults(func=cmd_import_comments)

    # --- run (all-in-one) ---
    p_run = sub.add_parser("run", help="Scrape + classify + report [+ brief] (all-in-one)")
    add_url_args(p_run)
    add_classify_args(p_run)
    p_run.add_argument(
        "-o", "--output-dir", type=str,
        default=os.environ.get("DEFAULT_OUTPUT_DIR", "./output"),
        help="Output folder (default ./output)",
    )
    p_run.add_argument(
        "--top-n", type=int, default=10,
        help="Top N quotes mỗi bucket trong report (default 10)",
    )
    p_run.add_argument(
        "--with-angles", action="store_true",
        help="Chain stage 4: generate content angle brief sau report",
    )
    p_run.add_argument(
        "--num-angles", type=int, default=10,
        help="Số angle (chỉ dùng khi --with-angles, default 10)",
    )
    p_run.add_argument(
        "--suggester-model", type=str, default=None,
        help="Override model riêng cho suggester (default = --model hoặc Opus 4.7)",
    )
    p_run.set_defaults(func=cmd_run)

    return parser


def main() -> None:
    # Force UTF-8 output trên Windows (PowerShell/cmd mặc định cp1252 không encode được tiếng Việt)
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    load_dotenv()  # đọc .env nếu có
    parser = build_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    args.func(args)


if __name__ == "__main__":
    main()
