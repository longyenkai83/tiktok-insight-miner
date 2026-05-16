"""Daily digest script — gộp tất cả run trong ngày thành 1 file markdown.

Usage:
    python daily_digest.py              # Hôm nay
    python daily_digest.py 2026-05-07   # Ngày cụ thể
    python daily_digest.py --watch      # Chạy lúc 18h mỗi ngày (foreground loop)

Output: output/_daily/<YYYY-MM-DD>.md

Khi nào dùng:
- Cuối ngày: chạy 1 lần để có snapshot toàn bộ run của nhân viên
- Schedule qua Windows Task Scheduler 18h mỗi ngày
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

from tiktok_insight_miner.postrun import build_daily_digest

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = PROJECT_ROOT / "output"

# Force UTF-8 trên Windows (PowerShell/cmd mặc định cp1252 không in được Unicode)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def run_once(target_date: str | None) -> None:
    digest = build_daily_digest(PROJECT_ROOT, OUTPUT_ROOT, target_date=target_date)
    if digest:
        print(f"✓ Daily digest → {digest}")
    else:
        target = target_date or date.today().isoformat()
        print(f"⚠️  Không có run nào ngày {target}")
        sys.exit(0)


def watch_loop(hour: int = 18) -> None:
    """Background loop — sleep đến HH:00 mỗi ngày rồi gen digest hôm đó."""
    print(f"📅 Watch mode — sẽ gen digest mỗi ngày lúc {hour:02d}:00")
    while True:
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        sleep_s = (next_run - now).total_seconds()
        print(f"  Next run: {next_run:%Y-%m-%d %H:%M:%S} (sau {sleep_s/3600:.1f}h)")
        time.sleep(sleep_s)
        try:
            run_once(target_date=None)
        except Exception as e:
            print(f"❌ Digest error: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gộp run trong ngày thành digest markdown.",
    )
    parser.add_argument(
        "date_arg",
        nargs="?",
        default=None,
        help="Date YYYY-MM-DD (default = hôm nay)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Chạy daemon, gen digest tự động lúc 18h mỗi ngày",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=18,
        help="Giờ chạy auto trong watch mode (default 18)",
    )
    args = parser.parse_args()

    if args.watch:
        watch_loop(hour=args.hour)
    else:
        run_once(target_date=args.date_arg)


if __name__ == "__main__":
    main()
