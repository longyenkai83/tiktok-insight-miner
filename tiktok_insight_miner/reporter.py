"""Generate markdown report từ classified comments."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from tiktok_insight_miner.models import (
    BUCKET_LABELS,
    BUCKET_ORDER,
    Bucket,
    ClassifiedComment,
    Insights,
)

logger = logging.getLogger(__name__)


def aggregate(classified: list[ClassifiedComment]) -> Insights:
    """Group classified comments by bucket."""
    by_bucket: dict[Bucket, list[ClassifiedComment]] = defaultdict(list)
    videos = set()
    for c in classified:
        by_bucket[c.bucket].append(c)
        if c.comment.video_url:
            videos.add(c.comment.video_url)

    return Insights(
        total_comments=len(classified),
        videos_analyzed=sorted(videos),
        by_bucket=dict(by_bucket),
    )


# Nhãn nguồn: raw["platform"] do fb_page_source / comment_importer gắn.
# TikTok scraper không gắn → mặc định "tiktok".
PLATFORM_LABELS = {
    "tiktok": "TikTok",
    "facebook_page": "FB comment",
    "facebook_inbox": "FB inbox",
    "manual": "Nhập tay",
}


def _platform(c: ClassifiedComment) -> str:
    return (c.comment.raw or {}).get("platform") or "tiktok"


def _platforms_present(classified: list[ClassifiedComment]) -> list[str]:
    """Các nguồn có mặt, theo thứ tự PLATFORM_LABELS rồi tới nguồn lạ."""
    seen = {_platform(c) for c in classified}
    known = [p for p in PLATFORM_LABELS if p in seen]
    return known + sorted(seen - set(PLATFORM_LABELS))


def _format_quote(c: ClassifiedComment, show_platform: bool = False) -> str:
    """Format 1 quote line cho report."""
    text = c.comment.text.replace("\n", " ").strip()
    author = c.comment.author or "anon"
    likes = c.comment.likes
    parts = [f'> "{text}"', f"— @{author} ({likes} likes)"]
    if show_platform:
        parts.append(f"`[{PLATFORM_LABELS.get(_platform(c), _platform(c))}]`")
    if c.summary:
        parts.append(f"  *Insight: {c.summary}*")
    return " ".join(parts)


def render_markdown(
    insights: Insights,
    top_n: int = 10,
    classified: list[ClassifiedComment] | None = None,
) -> str:
    """Render Insights thành markdown report.

    Args:
        insights: Aggregate result
        top_n: Số top quote hiển thị mỗi bucket (sort theo likes)
        classified: list gốc — chỉ dùng để nhận diện nguồn (tiktok / fb / inbox).
            Không truyền thì coi như 1 nguồn, report y như cũ.
    """
    total = insights.total_comments
    all_items = classified if classified is not None else [
        c for items in insights.by_bucket.values() for c in items
    ]
    platforms = _platforms_present(all_items)
    multi_source = len(platforms) > 1

    lines: list[str] = []
    if multi_source:
        lines.append("# Comment Insights — nhiều nguồn\n")
    elif platforms and platforms[0] != "tiktok":
        lines.append(f"# Comment Insights — {PLATFORM_LABELS.get(platforms[0], platforms[0])}\n")
    else:
        lines.append("# TikTok Comment Insights\n")
    lines.append(f"**Videos analyzed**: {len(insights.videos_analyzed)}  ")
    lines.append(f"**Total comments**: {total}  ")
    lines.append(f"**Generated**: {insights.generated_at.strftime('%Y-%m-%d %H:%M')}\n")

    if insights.videos_analyzed:
        lines.append("**Source URLs**:")
        for url in insights.videos_analyzed:
            lines.append(f"- {url}")
        lines.append("")

    # Distribution table
    lines.append("## 📊 Distribution\n")
    lines.append("| Bucket | Count | % |")
    lines.append("|---|---:|---:|")
    for bucket in BUCKET_ORDER:
        count = len(insights.by_bucket.get(bucket, []))
        pct = (count / total * 100) if total else 0
        label = BUCKET_LABELS[bucket]
        lines.append(f"| {label} | {count} | {pct:.1f}% |")
    lines.append("")

    # Nguồn × nhóm — chỉ khi có từ 2 nguồn trở lên
    if multi_source:
        lines.append("## 🔀 Theo nguồn\n")
        lines.append(
            "> Thị trường (TikTok) và khách của mình (FB) trả lời 2 câu hỏi khác nhau "
            "— đọc tách, đừng cộng dồn.\n"
        )
        header = "| Nguồn | Tổng | " + " | ".join(BUCKET_LABELS[b] for b in BUCKET_ORDER) + " |"
        lines.append(header)
        lines.append("|---|---:|" + "---:|" * len(BUCKET_ORDER))
        for plat in platforms:
            cua_nguon = [c for c in all_items if _platform(c) == plat]
            n = len(cua_nguon)
            cells = []
            for b in BUCKET_ORDER:
                k = sum(1 for c in cua_nguon if c.bucket == b)
                cells.append(f"{k} ({k / n * 100:.0f}%)" if n else "0")
            lines.append(
                f"| {PLATFORM_LABELS.get(plat, plat)} | {n} | " + " | ".join(cells) + " |"
            )
        lines.append("")

    # Per-bucket sections
    for bucket in BUCKET_ORDER:
        items = insights.by_bucket.get(bucket, [])
        if not items:
            continue

        label = BUCKET_LABELS[bucket]
        lines.append(f"## {label} ({len(items)})\n")

        # Sort by likes desc, then confidence desc
        sorted_items = sorted(
            items,
            key=lambda x: (x.comment.likes, x.confidence),
            reverse=True,
        )

        lines.append(f"**Top {min(top_n, len(sorted_items))} quotes:**\n")
        for i, c in enumerate(sorted_items[:top_n], 1):
            lines.append(f"{i}. {_format_quote(c, show_platform=multi_source)}")
        lines.append("")

        # Summary themes — group by summary, dedupe
        summaries = [c.summary for c in items if c.summary]
        if len(summaries) > top_n:
            unique_summaries = list(dict.fromkeys(summaries))  # preserve order, dedupe
            if len(unique_summaries) < len(summaries):
                lines.append(f"**Common themes ({len(unique_summaries)} distinct):**\n")
                for s in unique_summaries[:15]:
                    count = summaries.count(s)
                    lines.append(f"- ({count}×) {s}")
                lines.append("")

    return "\n".join(lines)


def save_report(report: str, output_path: Path) -> None:
    """Save markdown report ra file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    logger.info("Lưu report → %s", output_path)


def generate_report(
    classified: list[ClassifiedComment],
    output_path: Path,
    top_n: int = 10,
) -> None:
    """All-in-one: aggregate + render + save."""
    insights = aggregate(classified)
    report = render_markdown(insights, top_n=top_n, classified=classified)
    save_report(report, output_path)
