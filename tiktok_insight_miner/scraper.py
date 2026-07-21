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


def discover_tiktok_videos(
    keywords: list[str] | None = None,
    profiles: list[str] | None = None,
    hashtags: list[str] | None = None,
    limit_per_query: int = 30,
    min_views: int = 0,
    min_comments: int = 1,
    newest_days: int | None = None,
    apify_token: str | None = None,
    actor_id: str | None = None,
) -> list[dict[str, Any]]:
    """Tự tìm video TikTok theo từ khóa / hashtag / kênh (@đối thủ) qua Apify.

    Dùng actor `clockworks/tiktok-scraper` (KHÁC comments-scraper). Fields đã
    verify từ raw response: webVideoUrl, text, playCount, commentCount,
    diggCount, createTimeISO, authorMeta.name, hashtags.

    Mục tiêu: bỏ khâu tự lên TikTok tìm video thủ công. Kết quả đã lọc rác
    (bỏ video 0 comment / view thấp) + sort theo view giảm dần → chỉ giữ
    video đáng mine comment.

    Args:
        keywords: List từ khóa search (vd ["kinh doanh 2026"])
        profiles: List username (không cần @, vd ["cafef_official"]) — quét kênh đối thủ
        hashtags: List hashtag (không cần #, vd ["khoinghiep"])
        limit_per_query: Số video tối đa lấy mỗi query (default 30)
        min_views: Bỏ video dưới ngưỡng view này (default 0 = không lọc)
        min_comments: Bỏ video dưới ngưỡng comment (default 1 — video 0 cmt mine vô ích)
        newest_days: Chỉ giữ video đăng trong N ngày gần đây (None = không lọc).
            Lọc client-side dựa trên createTimeISO.
        apify_token: Override APIFY_TOKEN env var
        actor_id: Override actor (default clockworks/tiktok-scraper)

    Returns:
        List dict video, mỗi dict: {url, text, views, comments, likes,
        date, author, hashtags}. Sort view giảm dần.
    """
    token = apify_token or os.environ.get("APIFY_TOKEN")
    if not token:
        raise ValueError("Cần APIFY_TOKEN trong env hoặc truyền apify_token")

    if not any([keywords, profiles, hashtags]):
        raise ValueError("Cần ít nhất 1 trong: keywords / profiles / hashtags")

    actor = actor_id or os.environ.get(
        "APIFY_DISCOVER_ACTOR_ID", "clockworks/tiktok-scraper"
    )

    client = ApifyClient(token)

    actor_input: dict[str, Any] = {
        "resultsPerPage": limit_per_query,
        "maxItems": limit_per_query * max(
            len(keywords or []) + len(profiles or []) + len(hashtags or []), 1
        ),
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
    }
    if keywords:
        actor_input["searchQueries"] = keywords
    if profiles:
        # actor nhận profiles không có @
        actor_input["profiles"] = [p.lstrip("@") for p in profiles]
    if hashtags:
        actor_input["hashtags"] = [h.lstrip("#") for h in hashtags]

    logger.info(
        "Apify discover: actor=%s, keywords=%s, profiles=%s, hashtags=%s, limit=%d",
        actor, keywords, profiles, hashtags, limit_per_query,
    )

    run = client.actor(actor).call(run_input=actor_input)
    if not run:
        raise RuntimeError("Apify discover run trả về None")

    dataset_id = _extract_dataset_id(run)
    if not dataset_id:
        raise RuntimeError(
            f"Apify discover run không có defaultDatasetId. "
            f"Run type: {type(run).__name__}"
        )

    videos: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    total = 0
    for item in client.dataset(dataset_id).iterate_items():
        total += 1
        url = item.get("webVideoUrl")
        if not url or url in seen_urls:
            continue
        views = item.get("playCount") or 0
        comments = item.get("commentCount") or 0
        date_iso = (item.get("createTimeISO") or "")[:10]

        if views < min_views:
            continue
        if comments < min_comments:
            continue
        if newest_days is not None and date_iso:
            # so sánh chuỗi ISO đơn giản không đủ tin cậy tuyệt đối,
            # nhưng đủ để lọc bài quá cũ theo ngày.
            from datetime import date as _date, timedelta as _td
            try:
                created = _date.fromisoformat(date_iso)
                # today lấy từ createTime max để tránh phụ thuộc clock — dùng cutoff đơn giản
                cutoff = _date.today() - _td(days=newest_days)
                if created < cutoff:
                    continue
            except ValueError:
                pass

        seen_urls.add(url)
        videos.append({
            "url": url,
            "text": (item.get("text") or "").strip(),
            "views": views,
            "comments": comments,
            "likes": item.get("diggCount") or 0,
            "date": date_iso,
            "author": (item.get("authorMeta") or {}).get("name"),
            "hashtags": [h.get("name") for h in (item.get("hashtags") or []) if h.get("name")],
        })

    videos.sort(key=lambda v: v["views"], reverse=True)
    logger.info(
        "Discover: %d video thô → %d video sau lọc (min_views=%d, min_comments=%d)",
        total, len(videos), min_views, min_comments,
    )
    return videos


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


def scrape_facebook_group_comments(
    group_urls: list[str],
    max_posts_per_group: int = 30,
    apify_token: str | None = None,
    actor_id: str | None = None,
) -> list[Comment]:
    """Scrape top comments từ posts của Facebook PUBLIC group.

    Dùng actor `apify/facebook-groups-scraper`:
    - **CHỈ public group** (private group cần FB login, vi phạm TOS — em không build)
    - Không cần FB cookie / session
    - Output: mỗi post có `topComments` array — flatten ra list Comment
    - Cost: $0.005/post (không phải per comment) — 30 posts = $0.15

    LIMITATION quan trọng:
    - Actor trả về TOP comments mỗi post (không phải FULL comments)
    - Không control được max_comments_per_post — trả theo limit Facebook
    - Engagement metrics có thể không đầy đủ

    Args:
        group_urls: List FB group URLs (vd https://facebook.com/groups/<name>)
        max_posts_per_group: Số posts tối đa quét mỗi group (default 30)
        apify_token: Override APIFY_TOKEN env var
        actor_id: Override actor (default apify/facebook-groups-scraper)

    Returns:
        List Comment đã flatten + chuẩn hoá (compat với pipeline downstream).
    """
    token = apify_token or os.environ.get("APIFY_TOKEN")
    if not token:
        raise ValueError("Cần APIFY_TOKEN trong env hoặc truyền apify_token")

    actor = actor_id or os.environ.get(
        "APIFY_FB_GROUP_ACTOR_ID", "apify/facebook-groups-scraper"
    )

    client = ApifyClient(token)

    actor_input: dict = {
        "startUrls": [{"url": url} for url in group_urls],
        "resultsLimit": max_posts_per_group * len(group_urls),
    }

    logger.info(
        "Apify FB Group run: actor=%s, groups=%d, max_posts_per_group=%d",
        actor, len(group_urls), max_posts_per_group,
    )

    run = client.actor(actor).call(run_input=actor_input)
    if not run:
        raise RuntimeError("Apify FB Group run trả về None")

    dataset_id = _extract_dataset_id(run)
    if not dataset_id:
        raise RuntimeError(
            f"Apify FB Group run không có defaultDatasetId. "
            f"Run type: {type(run).__name__}"
        )

    comments: list[Comment] = []
    post_count = 0
    for post in client.dataset(dataset_id).iterate_items():
        post_count += 1
        top_comments = post.get("topComments") or []
        for cmt in top_comments:
            try:
                comments.append(
                    Comment.from_apify_facebook_group_comment(cmt, post=post)
                )
            except Exception as e:
                logger.warning("Skip FB Group cmt lỗi mapping: %s | cmt=%s", e, cmt)

    logger.info(
        "Scraped %d top comments từ %d posts (%d groups)",
        len(comments), post_count, len(group_urls),
    )
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
