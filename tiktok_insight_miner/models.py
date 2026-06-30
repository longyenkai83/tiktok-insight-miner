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

    @classmethod
    def from_apify_facebook_group_comment(
        cls, comment: dict[str, Any], post: dict[str, Any] | None = None,
    ) -> Comment:
        """Map 1 topComment trong post của apify/facebook-groups-scraper.

        Output schema khác facebook-comments-scraper:
        - Group scraper trả về posts, mỗi post có topComments array (limited)
        - Mỗi comment trong topComments có: commentUrl, id, feedbackId, date,
          text, profileUrl, profilePicture, profileId, profileName, likesCount,
          threadingDepth

        post (optional): pass thêm để giữ trace gốc về post (URL, postId, ...)
        """
        post = post or {}
        return cls(
            id=str(
                comment.get("id")
                or comment.get("feedbackId")
                or comment.get("commentUrl", "").split("/")[-1]
                or ""
            ),
            text=comment.get("text", "") or "",
            author=comment.get("profileName", "") or "",
            likes=int(comment.get("likesCount", 0) or 0),
            reply_count=0,  # group scraper không trả per-comment reply count
            created_at=str(comment.get("date") or ""),
            video_url=(
                comment.get("commentUrl")
                or post.get("url")
                or post.get("postUrl")
                or ""
            ),
            raw={
                **comment,
                "_platform": "facebook_group",
                "_thread_depth": comment.get("threadingDepth", 0),
                "_post_url": post.get("url") or post.get("postUrl") or "",
                "_post_id": post.get("postId") or post.get("id") or "",
            },
        )

    @classmethod
    def from_apify_facebook_item(cls, item: dict[str, Any]) -> Comment:
        """Map item từ apify/facebook-comments-scraper sang Comment.

        FB output schema khác TikTok:
        - commentId / id / feedbackId → id
        - text → text
        - profileName → author
        - likesCount → likes
        - date (ISO) → created_at
        - facebookUrl (link post gốc) → video_url (giữ trace gốc về post)
        - threadingDepth (0 = top-level, >0 = nested reply) → ghi vào raw

        Note: FB scraper KHÔNG cung cấp reply count cho mỗi comment (chỉ
        cho biết comment này nested ở depth nào). reply_count = 0 default.
        """
        return cls(
            id=str(
                item.get("commentId")
                or item.get("id")
                or item.get("feedbackId")
                or item.get("facebookId")
                or ""
            ),
            text=item.get("text", "") or "",
            author=item.get("profileName", "") or "",
            likes=int(item.get("likesCount", 0) or 0),
            reply_count=0,  # FB actor không trả reply_count per comment
            created_at=str(item.get("date") or ""),
            video_url=item.get("facebookUrl") or item.get("postUrl") or "",
            raw={
                **item,
                "_platform": "facebook",  # đánh dấu nguồn để trace
                "_thread_depth": item.get("threadingDepth", 0),
            },
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
    # v0.3 — added by framework v1.0
    "emotional_positioning",
    "series_announcement",
]

ANGLE_TYPE_LABELS: dict[AngleType, str] = {
    "pain_solution": "💊 Pain Solution",
    "desire_fulfillment": "🎯 Desire Fulfillment",
    "question_answer": "❓ Q&A",
    "myth_busting": "💥 Myth Busting",
    "social_proof": "👥 Social Proof",
    "how_to": "📚 How-to",
    "emotional_positioning": "💔 Emotional Positioning",
    "series_announcement": "📣 Series Announcement",
}

# v0.3 — Framework v1.0: 5 audience cluster + cross
AudienceCluster = Literal[
    "entrepreneurial_despair",
    "procrastination_trap",
    "viral_no_convert",
    "authentic_trend_fatigue",
    "macro_despair",
    "cross_cluster",
]

CLUSTER_LABELS: dict[AudienceCluster, str] = {
    "entrepreneurial_despair": "Entrepreneurial Despair",
    "procrastination_trap": "Procrastination Trap",
    "viral_no_convert": "Viral-No-Convert",
    "authentic_trend_fatigue": "Authentic Trend Fatigue",
    "macro_despair": "Macro Despair",
    "cross_cluster": "Cross-Cluster (tension / UGC / pattern)",
}

# v0.3 — Framework v1.0: VN cultural concepts (Western mental models KHÔNG có)
VnCulturalConcept = Literal[
    "via_culture",
    "face_the_dien",
    "collectivism_tag",
    "hierarchy_anh_chi_em",
]

VN_CONCEPT_LABELS: dict[VnCulturalConcept, str] = {
    "via_culture": "Vía Culture / Magical Thinking",
    "face_the_dien": "Face / Thể diện",
    "collectivism_tag": "Collectivism / Tag Culture",
    "hierarchy_anh_chi_em": "Hierarchy (Anh-Chị-Em-Cô-Chú)",
}


class ContentAngle(BaseModel):
    """1 ý tưởng video TikTok ground vào insight thực.

    v0.3: thêm 4 optional fields cho framework psychology v1.0
    (cluster, primary_model, vn_concept, psychology_rationale).
    Backward compat: brief cũ không có 4 field này vẫn load được.
    """

    title: str = Field(description="Tiêu đề video, 5-15 từ tiếng Việt")
    angle_type: AngleType
    target_insight: str = Field(
        description="Quote nguyên văn của comment dẫn ra angle này (proof of demand)"
    )
    target_likes: int = Field(
        ge=0, description="Số likes của comment gốc — signal demand strength"
    )
    hook: str = Field(
        description=(
            "1-2 câu mở video bắt attention trong 3s đầu, max 150 ký tự. "
            "BẮT BUỘC chứa ≥1 cụm nguyên văn từ comment gốc (vocab grounding)."
        )
    )
    script_outline: list[str] = Field(
        description="3-5 bullet beat-by-beat của video, mỗi bullet 1 dòng ngắn"
    )
    cta: str = Field(
        description="Call to action cụ thể (vd: 'Comment X để nhận Y'). KHÔNG commercial/offer/promo."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description=(
            "Mức độ angle grounded vào data thực vs suy diễn. "
            "Reweight rule: cluster macro_despair + likes ≥50 → ≥0.9. "
            "Tip kỹ thuật rời rạc → ≤0.7."
        ),
    )
    # --- v0.3 framework fields (optional cho backward compat) ---
    cluster: AudienceCluster | None = Field(
        default=None,
        description="1 trong 5 audience cluster của framework v1.0",
    )
    primary_model: str | None = Field(
        default=None,
        description=(
            "1 mental model chính từ 12 curated: jobs_to_be_done, pratfall, "
            "mimetic_desire, curse_of_knowledge, zeigarnik, peak_end, "
            "loss_aversion, mere_exposure, social_proof, confirmation_bias, "
            "bj_fogg, goal_gradient"
        ),
    )
    vn_concept: VnCulturalConcept | None = Field(
        default=None,
        description="VN cultural concept dùng (optional, nhưng brief PHẢI có ≥1 angle dùng)",
    )
    psychology_rationale: str | None = Field(
        default=None,
        description="1-2 dòng giải thích combo cluster + model + vn_concept fit insight ra sao",
    )
    # --- v0.4 (Framework v1.1 — Persona-Aware) ---
    fb_caption_opening: str | None = Field(
        default=None,
        description=(
            "3-5 dòng câu mồi cho Fanpage caption — quan trọng hơn hook 3s với "
            "audience trưởng thành (27-45) đọc post trước khi xem video. "
            "Optional: chỉ generate khi niche persona có platform=fanpage hoặc maturity=high."
        ),
    )


class ContentAngleBrief(BaseModel):
    """Wrapper cho output của suggester."""

    angles: list[ContentAngle]
