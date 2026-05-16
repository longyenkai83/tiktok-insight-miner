"""Classify comments bằng Claude — batch + prompt caching + structured outputs."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import anthropic

from tiktok_insight_miner.models import (
    BatchClassificationResult,
    ClassifiedComment,
    Comment,
)

logger = logging.getLogger(__name__)

# System prompt — frozen, được cache với cache_control ephemeral.
# Không interpolate timestamp/ID/dynamic content vào đây để không break cache.
SYSTEM_PROMPT = """Bạn là chuyên gia phân tích insight từ comment social media (chủ yếu TikTok tiếng Việt).

Nhiệm vụ: Đọc danh sách comment, phân loại mỗi comment vào ĐÚNG 1 trong 7 bucket sau:

**pain** — Vấn đề, khó khăn, frustration, complaint user đang gặp.
  Ví dụ: "shop giao chậm quá", "dùng cái này 1 tuần là hỏng", "đau lưng vì ngồi sai tư thế"

**desire** — Mong muốn, ước, aspiration, "giá mà có...".
  Ví dụ: "ước gì có version màu hồng", "thèm về quê quá", "mong shop làm size lớn hơn"

**question** — Câu hỏi cần được giải đáp (về sản phẩm, cách dùng, giá, where to buy...).
  Ví dụ: "shop ơi giá bao nhiêu?", "mua ở đâu vậy ạ?", "dùng cho da dầu được không?"

**objection** — Phản đối, nghi ngờ, lý do KHÔNG mua/dùng/tin.
  Ví dụ: "đắt thế ai mua", "trông fake quá", "nghe quảng cáo mãi rồi không tin nữa"

**praise** — Khen ngợi, ca ngợi, positive feedback, biểu cảm yêu thích cụ thể.
  Ví dụ: "video hay quá ạ", "shop tâm huyết thật", "ưng quá đặt liền"

**mention** — Comment chủ yếu là tag/mention người khác (@username) để chia sẻ video, không có nội dung khác đáng kể.
  Ví dụ: "@ngoclan2k coi nè", "@a @b @c", "@Hoàng Cường 😳", "tag bạn vào xem"
  Đây là social signal mạnh (sharing intent) nhưng không có content insight.

**other** — Spam, emoji-only, off-topic, chào hỏi suông, không có insight rõ ràng và KHÔNG phải mention.
  Ví dụ: "❤️❤️❤️", "first", "ai đến từ x cho mình xin like", "[Sticker]"

Quy tắc phân loại:
1. Mỗi comment chỉ chọn 1 bucket — bucket phù hợp NHẤT
2. Nếu comment vừa khen vừa hỏi → ưu tiên `question` (vì có actionable insight)
3. Comment "đẹp quá" / "hay" / "nice" → `praise`, không phải `other`
4. Comment chỉ chứa emoji hoặc dưới 3 từ vô nghĩa → `other`
5. Sarcasm/mỉa mai khen → `objection` (negative intent)
6. Comment có @username + nội dung thực → phân theo nội dung (vd "@a sản phẩm này hiệu quả không?" → question)
7. Comment chỉ có @username (1 hoặc nhiều) + emoji/chào ngắn → `mention`

Cho mỗi comment, trả về:
- `comment_id`: id của comment (giữ nguyên từ input)
- `bucket`: 1 trong 7 giá trị trên
- `summary`: 1 câu tiếng Việt, max 15 từ, tóm tắt insight cốt lõi (KHÔNG copy nguyên văn comment)
- `confidence`: float 0.0-1.0, mức độ tự tin về phân loại

Trả về theo schema JSON đã cung cấp."""


def _build_user_message(batch: list[Comment]) -> str:
    """Format batch comments thành text cho user message."""
    lines = ["Phân loại các comment sau:\n"]
    for c in batch:
        # Truncate nếu quá dài (rare) — log warning nếu xảy ra
        text = c.text.strip()
        if len(text) > 500:
            logger.warning("Comment id=%s dài %d ký tự, truncate xuống 500", c.id, len(text))
            text = text[:500] + "..."
        lines.append(f"[id={c.id}] {text}")
    return "\n".join(lines)


def classify_batch(
    client: anthropic.Anthropic,
    batch: list[Comment],
    model: str,
) -> list[ClassifiedComment]:
    """Classify 1 batch comments. Trả về list ClassifiedComment đã merge."""
    response = client.messages.parse(
        model=model,
        max_tokens=8000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": _build_user_message(batch)}],
        output_format=BatchClassificationResult,
    )

    # Log cache stats để verify caching đang work
    usage = response.usage
    logger.debug(
        "Batch usage: input=%d, cache_read=%d, cache_write=%d, output=%d",
        usage.input_tokens,
        getattr(usage, "cache_read_input_tokens", 0) or 0,
        getattr(usage, "cache_creation_input_tokens", 0) or 0,
        usage.output_tokens,
    )

    if response.parsed_output is None:
        raise RuntimeError(
            f"Claude refused or failed to parse. stop_reason={response.stop_reason}"
        )

    # Index comments by id để merge
    comment_by_id = {c.id: c for c in batch}
    out: list[ClassifiedComment] = []
    for cls in response.parsed_output.classifications:
        original = comment_by_id.get(cls.comment_id)
        if original is None:
            logger.warning("Classifier trả về comment_id không tồn tại: %s", cls.comment_id)
            continue
        out.append(
            ClassifiedComment(
                comment=original,
                bucket=cls.bucket,
                summary=cls.summary,
                confidence=cls.confidence,
            )
        )

    # Detect missing classifications
    classified_ids = {c.comment.id for c in out}
    missing = [c.id for c in batch if c.id not in classified_ids]
    if missing:
        logger.warning("Classifier bỏ sót %d comments: %s", len(missing), missing[:5])

    return out


def classify_comments(
    comments: list[Comment],
    model: str | None = None,
    batch_size: int | None = None,
    api_key: str | None = None,
) -> list[ClassifiedComment]:
    """Classify toàn bộ comments theo batch.

    Args:
        comments: List Comment đã scrape
        model: Anthropic model id (default từ ANTHROPIC_MODEL env hoặc claude-opus-4-7)
        batch_size: Số comments per API call (default từ CLASSIFY_BATCH_SIZE env hoặc 20)
        api_key: Override ANTHROPIC_API_KEY

    Returns:
        List ClassifiedComment
    """
    model = model or os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7")
    batch_size = batch_size or int(os.environ.get("CLASSIFY_BATCH_SIZE", "20"))

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    logger.info(
        "Classify %d comments với model=%s, batch_size=%d",
        len(comments), model, batch_size,
    )

    results: list[ClassifiedComment] = []
    total_batches = (len(comments) + batch_size - 1) // batch_size
    consecutive_failures = 0
    for i in range(0, len(comments), batch_size):
        batch = comments[i : i + batch_size]
        batch_num = i // batch_size + 1
        logger.info("Batch %d/%d (%d comments)...", batch_num, total_batches, len(batch))
        try:
            results.extend(classify_batch(client, batch, model))
            consecutive_failures = 0
        except anthropic.AuthenticationError as e:
            # 401 invalid key — fail fast, không retry, không silent
            raise RuntimeError(
                f"Anthropic API key invalid (401). Check ANTHROPIC_API_KEY trong .env. "
                f"Original: {e}"
            ) from e
        except anthropic.APIError as e:
            logger.error("Batch %d lỗi API: %s — skip batch", batch_num, e)
            consecutive_failures += 1
            # Nếu 3 batches liên tiếp fail → fail toàn bộ, không silent return empty
            if consecutive_failures >= 3:
                raise RuntimeError(
                    f"3 batches liên tiếp fail. Có thể quota/rate-limit/network issue. "
                    f"Last error: {e}"
                ) from e
            continue

    logger.info("Hoàn tất: %d/%d comments classified", len(results), len(comments))
    if not results:
        raise RuntimeError(
            f"Không classify được comment nào trong {total_batches} batches. "
            "Check API key, quota, hoặc log để biết chi tiết."
        )
    return results


def save_classified_json(classified: list[ClassifiedComment], output_path: Path) -> None:
    """Save classified comments thành JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = [c.model_dump() for c in classified]
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    logger.info("Lưu %d classified comments → %s", len(classified), output_path)


def load_classified_json(input_path: Path) -> list[ClassifiedComment]:
    """Load classified comments từ JSON."""
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    return [ClassifiedComment.model_validate(item) for item in raw]
