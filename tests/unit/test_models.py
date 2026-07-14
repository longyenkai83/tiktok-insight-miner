"""Unit tests cho Pydantic schema mapping (Spec 1 của T4).

Kiểm chứng 3 class methods map dữ liệu từ 3 nguồn scraper sang Comment:
- from_apify_item (TikTok)
- from_apify_facebook_item (FB post)
- from_apify_facebook_group_comment (FB Group)

Cũng test ClassifiedComment mapping từ Comment + classification.
"""

from __future__ import annotations

import pytest

from tiktok_insight_miner.models import ClassifiedComment, Comment


# --- from_apify_item (TikTok) ---

def test_from_apify_item_full_payload():
    item = {
        "cid": "abc123",
        "text": "Video hay quá chị",
        "uniqueId": "user_x",
        "diggCount": 42,
        "replyCommentTotal": 5,
        "createTimeISO": "2026-01-15T10:30:00Z",
        "videoWebUrl": "https://tiktok.com/@u/video/1",
    }
    c = Comment.from_apify_item(item)
    assert c.id == "abc123"
    assert c.text == "Video hay quá chị"
    assert c.author == "user_x"
    assert c.likes == 42
    assert c.reply_count == 5
    assert c.created_at == "2026-01-15T10:30:00Z"
    assert c.video_url == "https://tiktok.com/@u/video/1"
    assert c.raw == item


def test_from_apify_item_fallback_id_field():
    """Actor version cũ dùng `id` thay vì `cid` — cả 2 phải work."""
    item = {"id": "xyz789", "text": "hello"}
    c = Comment.from_apify_item(item)
    assert c.id == "xyz789"


def test_from_apify_item_missing_optional_fields_no_crash():
    """Thiếu field optional → default value, không raise."""
    c = Comment.from_apify_item({"cid": "1", "text": "hi"})
    assert c.id == "1"
    assert c.text == "hi"
    assert c.likes == 0
    assert c.reply_count == 0
    assert c.author == ""
    assert c.video_url == ""


def test_from_apify_item_none_values_coerced():
    """Actor đôi khi trả None cho likes → phải coerce về 0, không crash."""
    item = {"cid": "1", "text": "x", "diggCount": None, "replyCommentTotal": None}
    c = Comment.from_apify_item(item)
    assert c.likes == 0
    assert c.reply_count == 0


def test_from_apify_item_empty_dict_defaults():
    """Edge: item rỗng hoàn toàn → id/text = '', không raise."""
    c = Comment.from_apify_item({})
    assert c.id == ""
    assert c.text == ""


# --- from_apify_facebook_item (FB post) ---

def test_from_apify_facebook_item_full():
    item = {
        "commentId": "fb_1",
        "text": "Bài viết ý nghĩa",
        "profileName": "Nguyễn Văn A",
        "likesCount": 15,
        "date": "2026-02-10T08:00:00Z",
        "facebookUrl": "https://facebook.com/post/1",
        "threadingDepth": 0,
    }
    c = Comment.from_apify_facebook_item(item)
    assert c.id == "fb_1"
    assert c.text == "Bài viết ý nghĩa"
    assert c.author == "Nguyễn Văn A"
    assert c.likes == 15
    assert c.reply_count == 0  # FB actor không trả reply_count per comment
    assert c.created_at == "2026-02-10T08:00:00Z"
    assert c.video_url == "https://facebook.com/post/1"
    assert c.raw["_platform"] == "facebook"
    assert c.raw["_thread_depth"] == 0


def test_from_apify_facebook_item_id_fallback_chain():
    """commentId > id > feedbackId > facebookId fallback."""
    assert Comment.from_apify_facebook_item({"id": "x", "text": ""}).id == "x"
    assert Comment.from_apify_facebook_item({"feedbackId": "y", "text": ""}).id == "y"
    assert Comment.from_apify_facebook_item({"facebookId": "z", "text": ""}).id == "z"


def test_from_apify_facebook_item_nested_reply():
    """Nested reply (threadingDepth > 0) vẫn map OK, marker giữ trong raw."""
    item = {"commentId": "r1", "text": "reply", "threadingDepth": 2}
    c = Comment.from_apify_facebook_item(item)
    assert c.raw["_thread_depth"] == 2


def test_from_apify_facebook_item_missing_fields():
    c = Comment.from_apify_facebook_item({"commentId": "1"})
    assert c.id == "1"
    assert c.text == ""
    assert c.likes == 0
    assert c.raw["_platform"] == "facebook"


# --- from_apify_facebook_group_comment (FB Group) ---

def test_from_apify_facebook_group_comment_full():
    comment = {
        "id": "gc_1",
        "text": "Nhóm này hay",
        "profileName": "Chị B",
        "likesCount": 8,
        "date": "2026-03-01T12:00:00Z",
        "commentUrl": "https://facebook.com/groups/x/posts/1?comment=gc_1",
        "threadingDepth": 0,
    }
    post = {"postId": "post_1", "url": "https://facebook.com/groups/x/posts/1"}
    c = Comment.from_apify_facebook_group_comment(comment, post=post)
    assert c.id == "gc_1"
    assert c.text == "Nhóm này hay"
    assert c.author == "Chị B"
    assert c.likes == 8
    assert c.reply_count == 0
    assert c.video_url == comment["commentUrl"]
    assert c.raw["_platform"] == "facebook_group"
    assert c.raw["_post_id"] == "post_1"
    assert c.raw["_post_url"] == post["url"]


def test_from_apify_facebook_group_comment_no_post_arg():
    """post=None → post trace fields = empty, không raise."""
    comment = {"id": "gc_2", "text": "test"}
    c = Comment.from_apify_facebook_group_comment(comment, post=None)
    assert c.raw["_post_id"] == ""
    assert c.raw["_post_url"] == ""
    assert c.raw["_platform"] == "facebook_group"


def test_from_apify_facebook_group_comment_id_from_url_fallback():
    """Không có id/feedbackId → lấy từ commentUrl."""
    comment = {"commentUrl": "https://fb.com/x/posts/1?c=derived_id", "text": ""}
    c = Comment.from_apify_facebook_group_comment(comment)
    assert c.id  # phải có gì đó, không empty
    assert c.raw["_platform"] == "facebook_group"


# --- ClassifiedComment ---

def test_classified_comment_valid():
    comment = Comment(id="1", text="hi", likes=10)
    cc = ClassifiedComment(
        comment=comment,
        bucket="pain",
        summary="Người dùng than thở",
        confidence=0.85,
    )
    assert cc.bucket == "pain"
    assert cc.confidence == 0.85
    assert cc.comment.id == "1"


def test_classified_comment_invalid_bucket_raises():
    """Pydantic Literal validation phải bắt bucket lạ."""
    comment = Comment(id="1", text="hi")
    with pytest.raises(Exception):  # ValidationError
        ClassifiedComment(
            comment=comment,
            bucket="invalid_bucket",  # type: ignore[arg-type]
            summary="x",
            confidence=0.5,
        )


def test_classified_comment_confidence_range():
    """Confidence range validation (theoretically 0-1) — model hiện KHÔNG constrain
    ở ClassifiedComment (chỉ ClassificationResult). Test document behavior thực tế."""
    comment = Comment(id="1", text="hi")
    # Không raise vì ClassifiedComment.confidence là float không constrain range
    cc = ClassifiedComment(comment=comment, bucket="pain", summary="x", confidence=1.5)
    assert cc.confidence == 1.5


@pytest.mark.parametrize("bucket", [
    "pain", "desire", "question", "objection", "praise", "mention", "other",
])
def test_all_7_buckets_valid(bucket):
    """Tất cả 7 bucket phải được chấp nhận."""
    comment = Comment(id="1", text="x")
    cc = ClassifiedComment(
        comment=comment, bucket=bucket, summary="s", confidence=0.5,
    )
    assert cc.bucket == bucket
