"""Apify scraper wrapper cho clockworks/tiktok-comments-scraper."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from apify_client import ApifyClient

from tiktok_insight_miner.models import Comment

logger = logging.getLogger(__name__)


def _extract_dataset_id(run: Any) -> str | None:
    """Extract defaultDatasetId từ Apify run response — support cả dict (SDK cũ)
    và Run Pydantic object (apify-client v2+).

    SDK update breaking change:
    - v1.x: client.actor().call() trả dict → run.get("defaultDatasetId")
    - v2.x: trả Run Pydantic → run.default_dataset_id (snake_case attribute)
    """
    # Try Pydantic attribute (SDK mới)
    dataset_id = getattr(run, "default_dataset_id", None)
    if dataset_id:
        return str(dataset_id)
    # Try camelCase attribute (variant)
    dataset_id = getattr(run, "defaultDatasetId", None)
    if dataset_id:
        return str(dataset_id)
    # Try dict access (SDK cũ)
    if hasattr(run, "get"):
        try:
            dataset_id = run.get("defaultDatasetId")
            if dataset_id:
                return str(dataset_id)
        except (AttributeError, TypeError):
            pass
    # Last resort: cast Pydantic → dict
    if hasattr(run, "model_dump"):
        try:
            d = run.model_dump()
            return d.get("defaultDatasetId") or d.get("default_dataset_id")
        except Exception:
            pass
    return None


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

    dataset_id = _extract_dataset_id(run)
    if not dataset_id:
        raise RuntimeError(
            f"Apify run không có defaultDatasetId. Run type: {type(run).__name__}, "
            f"attrs: {[a for a in dir(run) if not a.startswith('_')][:10]}"
        )

    comments: list[Comment] = []
    for item in client.dataset(dataset_id).iterate_items():
        try:
            comments.append(Comment.from_apify_item(item))
        except Exception as e:
            logger.warning("Skip item lỗi mapping: %s | item=%s", e, item)

    logger.info("Scraped %d comments từ %d videos", len(comments), len(video_urls))
    return comments


def scrape_facebook_comments(
    post_urls: list[str],
    max_comments_per_post: int = 100,
    include_nested_replies: bool = True,
    view_option: str = "RANKED_THREADED",
    only_newer_than: str | None = None,
    apify_token: str | None = None,
    actor_id: str | None = None,
) -> list[Comment]:
    """Scrape comments từ list Facebook post URLs qua Apify.

    Dùng actor `apify/facebook-comments-scraper` (official Apify):
    - Cost: $1.40 / 1000 comments ($0.0014/cmt)
    - Không cần Facebook login/cookie (chỉ public post)
    - Support nested replies tối đa 3 cấp
    - Sort options: RANKED_THREADED (default) / RECENT_ACTIVITY / RANKED_UNFILTERED

    Args:
        post_urls: List Facebook post URLs (public). Có thể là post của
            Fanpage hoặc user public.
        max_comments_per_post: Số comment tối đa mỗi post (default 100)
        include_nested_replies: True = lấy luôn replies (3 cấp)
        view_option: Cách sort comment ("RANKED_THREADED" / "RECENT_ACTIVITY"
            / "RANKED_UNFILTERED")
        only_newer_than: Filter ngày (vd "2026-01-01" — chỉ comment sau ngày này)
        apify_token: Override APIFY_TOKEN env var
        actor_id: Override actor (default apify/facebook-comments-scraper)

    Returns:
        List Comment đã chuẩn hoá (compat với pipeline classify/report/brief).
    """
    token = apify_token or os.environ.get("APIFY_TOKEN")
    if not token:
        raise ValueError("Cần APIFY_TOKEN trong env hoặc truyền apify_token")

    actor = actor_id or os.environ.get(
        "APIFY_FB_ACTOR_ID", "apify/facebook-comments-scraper"
    )

    client = ApifyClient(token)

    actor_input: dict = {
        "startUrls": [{"url": url} for url in post_urls],
        "resultsLimit": max_comments_per_post * len(post_urls),
        "includeNestedComments": include_nested_replies,
        "viewOption": view_option,
    }
    if only_newer_than:
        actor_input["onlyCommentsNewerThan"] = only_newer_than

    logger.info(
        "Apify FB run: actor=%s, posts=%d, max_per_post=%d, nested=%s",
        actor, len(post_urls), max_comments_per_post, include_nested_replies,
    )

    run = client.actor(actor).call(run_input=actor_input)
    if not run:
        raise RuntimeError("Apify FB run trả về None")

    dataset_id = _extract_dataset_id(run)
    if not dataset_id:
        raise RuntimeError(
            f"Apify FB run không có defaultDatasetId. Run type: {type(run).__name__}"
        )

    comments: list[Comment] = []
    for item in client.dataset(dataset_id).iterate_items():
        try:
            comments.append(Comment.from_apify_facebook_item(item))
        except Exception as e:
            logger.warning("Skip FB item lỗi mapping: %s | item=%s", e, item)

    logger.info("Scraped %d FB comments từ %d posts", len(comments), len(post_urls))
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
