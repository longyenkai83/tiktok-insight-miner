"""Pydantic models cho Comment, Classification, Insight."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Bucket = Literal["pain", "desire", "question", "objection", "praise", "mention", "other"]

BUCKET_LABELS: dict[Bucket, str] = {
    "pain": "😣 Pain",
    "desire": "💭 Desire",
    "question": "❓ Question",
    "objection": "🚫 Objection",
    "praise": "👍 Praise",
    "mention": "🏷️ Mention",
    "other": "📦 Other",
}

BUCKET_ORDER: list[Bucket] = [
    "pain", "desire", "question", "objection", "praise", "mention", "other",
]


class Comment(BaseModel):
    """Comment thô từ Apify scraper, đã chuẩn hoá field."""

    id: str
    text: str
    author: str = ""
    likes: int = 0
    reply_count: int = 0
    created_at: str = ""
    video_url: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_apify_item(cls, item: dict[str, Any]) -> Comment:
        """Map item từ clockworks/tiktok-comments-scraper sang Comment.

        Field names có thể đổi theo phiên bản actor — dùng .get() resilient
        và lưu raw để debug nếu thiếu field.
        """
        return cls(
            id=str(item.get("cid") or item.get("id") or ""),
            text=item.get("text", "") or "",
            author=item.get("uniqueId") or item.get("uid") or "",
            likes=int(item.get("diggCount", 0) or 0),
            reply_count=int(item.get("replyCommentTotal", 0) or 0),
            created_at=str(item.get("createTimeISO") or item.get("createTime") or ""),
            video_url=item.get("videoWebUrl") or item.get("videoUrl") or "",
            raw=item,
        )


class ClassificationResult(BaseModel):
    """Kết quả classify cho 1 comment — schema cho Claude trả về."""

    comment_id: str
    bucket: Bucket
    summary: str = Field(description="1 câu ngắn (max 15 từ) tóm tắt insight, tiếng Việt")
    confidence: float = Field(ge=0.0, le=1.0)


class BatchClassificationResult(BaseModel):
    """Wrapper cho batch — Claude trả về list các classification."""

    classifications: list[ClassificationResult]


class ClassifiedComment(BaseModel):
    """Comment + classification gộp lại để serialize."""

    comment: Comment
    bucket: Bucket
    summary: str
    confidence: float


class Insights(BaseModel):
    """Aggregate kết quả cho report."""

    total_comments: int
    videos_analyzed: list[str]
    by_bucket: dict[Bucket, list[ClassifiedComment]]
    generated_at: datetime = Field(default_factory=datetime.now)


# --- Content Angle Suggester (v0.2) ---

AngleType = Literal[
    "pain_solution",
    "desire_fulfillment",
    "question_answer",
    "myth_busting",
    "social_proof",
    "how_to",
]

ANGLE_TYPE_LABELS: dict[AngleType, str] = {
    "pain_solution": "💊 Pain Solution",
    "desire_fulfillment": "🎯 Desire Fulfillment",
    "question_answer": "❓ Q&A",
    "myth_busting": "💥 Myth Busting",
    "social_proof": "👥 Social Proof",
    "how_to": "📚 How-to",
}


class ContentAngle(BaseModel):
    """1 ý tưởng video TikTok ground vào insight thực."""

    title: str = Field(description="Tiêu đề video, 5-15 từ tiếng Việt")
    angle_type: AngleType
    target_insight: str = Field(
        description="Quote nguyên văn của comment dẫn ra angle này (proof of demand)"
    )
    target_likes: int = Field(
        ge=0, description="Số likes của comment gốc — signal demand strength"
    )
    hook: str = Field(
        description="1-2 câu mở video bắt attention trong 3s đầu, max 150 ký tự"
    )
    script_outline: list[str] = Field(
        description="3-5 bullet beat-by-beat của video, mỗi bullet 1 dòng ngắn"
    )
    cta: str = Field(
        description="Call to action cụ thể (vd: 'Comment X để nhận Y')"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Mức độ angle này grounded vào data thực vs suy diễn",
    )


class ContentAngleBrief(BaseModel):
    """Wrapper cho output của suggester."""

    angles: list[ContentAngle]
