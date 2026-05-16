"""Apify scraper wrapper cho clockworks/tiktok-comments-scraper."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from apify_client import ApifyClient

from tiktok_insight_miner.models import Comment

logger = logging.getLogger(__name__)


def scrape_tiktok_comments(
    video_urls: list[str],
    max_comments_per_video: int = 100,
    apify_token: str | None = None,
    actor_id: str | None = None,
) -> list[Comment]:
    """Scrape comments từ list TikTok video URLs qua Apify.

    Args:
        video_urls: List TikTok video URLs
        max_comments_per_video: Số comment tối đa mỗi video
        apify_token: Override APIFY_TOKEN env var
        actor_id: Override actor (default clockworks/tiktok-comments-scraper)

    Returns:
        List Comment đã chuẩn hoá
    """
    token = apify_token or os.environ.get("APIFY_TOKEN")
    if not token:
        raise ValueError("Cần APIFY_TOKEN trong env hoặc truyền apify_token")

    actor = actor_id or os.environ.get("APIFY_ACTOR_ID", "clockworks/tiktok-comments-scraper")

    client = ApifyClient(token)

    actor_input = {
        "postURLs": video_urls,
        "commentsPerPost": max_comments_per_video,
        "maxRepliesPerComment": 0,
    }

    logger.info(
        "Apify run: actor=%s, videos=%d, max_per_video=%d",
        actor, len(video_urls), max_comments_per_video,
    )

    run = client.actor(actor).call(run_input=actor_input)
    if not run:
        raise RuntimeError("Apify run trả về None")

    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        raise RuntimeError(f"Apify run không có defaultDatasetId: {run}")

    comments: list[Comment] = []
    for item in client.dataset(dataset_id).iterate_items():
        try:
            comments.append(Comment.from_apify_item(item))
        except Exception as e:
            logger.warning("Skip item lỗi mapping: %s | item=%s", e, item)

    logger.info("Scraped %d comments từ %d videos", len(comments), len(video_urls))
    return comments


def save_comments_json(comments: list[Comment], output_path: Path) -> None:
    """Save list comments thành JSON file (UTF-8, indent đẹp)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = [c.model_dump() for c in comments]
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Lưu %d comments → %s", len(comments), output_path)


def load_comments_json(input_path: Path) -> list[Comment]:
    """Load list comments từ JSON file."""
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    return [Comment.model_validate(item) for item in raw]
