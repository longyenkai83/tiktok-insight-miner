"""Content angle suggester — biến classified comments thành content brief actionable.

Workflow: classified.json → select top insights → Claude generate angles → brief.md
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path

import anthropic

from tiktok_insight_miner.models import (
    ANGLE_TYPE_LABELS,
    ClassifiedComment,
    ContentAngle,
    ContentAngleBrief,
)

logger = logging.getLogger(__name__)


# Buckets có actionable insight cho content angle (loại praise, mention, other ra)
ACTIONABLE_BUCKETS = ("pain", "desire", "question", "objection")


SYSTEM_PROMPT = """Bạn là content strategist chuyên ý tưởng video TikTok ngắn (<60s) cho audience Việt Nam.

Input: Danh sách insight từ comment audience đã được phân loại (pain, desire, question, objection) cùng quote nguyên văn + số likes làm proof of demand.

Nhiệm vụ: Generate N content angle hoàn chỉnh — mỗi angle là 1 video idea sẵn sàng quay.

Quy tắc:

1. **Ground vào insight thực** (quan trọng nhất): Mỗi angle PHẢI link rõ tới 1 comment cụ thể từ input. KHÔNG bịa pain/desire/question. `target_insight` = quote nguyên văn comment + `target_likes` = likes của nó.

2. **Diverse angle types**: Mix 6 loại:
   - `pain_solution`: Giải pháp cho pain
   - `desire_fulfillment`: Cách đạt được desire
   - `question_answer`: Trả lời câu hỏi cụ thể (nhất là FAQ likes cao)
   - `myth_busting`: Counter objection bằng evidence/demo
   - `social_proof`: Testimonial/trước-sau từ user
   - `how_to`: Tutorial step-by-step

3. **Hook style TikTok (3s đầu)**: 1-2 câu, max 150 ký tự. Dùng pattern viral:
   - Question hook: "Bạn có biết...?"
   - Shocking stat: "1 trong 3 phụ nữ sau sinh bị..."
   - Contrarian: "Mọi người nghĩ X, nhưng thực ra Y"
   - Direct address: "Nếu bạn cũng từng thấy..."
   - Cliffhanger: "Đến phút 0:30 mới bất ngờ..."

4. **Script outline ngắn**: 3-5 bullet, mỗi bullet 1 dòng beat (vd: "0:00-0:03 Hook", "0:04-0:15 Demo bước 1", ...). KHÔNG viết script đầy đủ — chỉ outline.

5. **CTA actionable cụ thể**: "Comment 'kegel' để DM bài tập" tốt hơn "Like + share".

6. **Vietnamese tone**: peer-level, conversational. KHÔNG "quý khách / kính thưa". Dùng "mình / bạn / các bạn".

7. **Confidence**: 0.9+ nếu link 1-1 với insight + likes cao; 0.5-0.7 nếu phải kết hợp nhiều insight; <0.5 nếu suy diễn xa từ data → đừng generate angle này.

8. **Ưu tiên insight có likes cao** — proof of demand mạnh hơn.

Trả về theo schema JSON đã cung cấp."""


def select_top_insights(
    classified: list[ClassifiedComment],
    top_n_per_bucket: int = 5,
) -> list[ClassifiedComment]:
    """Lấy top N comments mỗi bucket actionable, sort theo likes desc.

    Trả về list flatten đã sort theo (bucket, -likes).
    """
    buckets: dict[str, list[ClassifiedComment]] = {b: [] for b in ACTIONABLE_BUCKETS}
    for c in classified:
        if c.bucket in buckets:
            buckets[c.bucket].append(c)

    selected: list[ClassifiedComment] = []
    for bucket in ACTIONABLE_BUCKETS:
        items = sorted(buckets[bucket], key=lambda x: x.comment.likes, reverse=True)
        selected.extend(items[:top_n_per_bucket])

    return selected


def _format_insights_input(top_insights: list[ClassifiedComment]) -> str:
    """Format top insights thành input cho Claude."""
    lines = ["Insight từ comment audience (đã phân loại):\n"]
    for c in top_insights:
        text = c.comment.text.strip().replace("\n", " ")
        if len(text) > 300:
            text = text[:300] + "..."
        lines.append(
            f'[{c.bucket}] (likes={c.comment.likes}) "{text}"'
            f"\n  → insight: {c.summary}"
        )
    return "\n\n".join(lines)


def generate_angles(
    classified: list[ClassifiedComment],
    num_angles: int = 10,
    top_n_per_bucket: int = 5,
    model: str | None = None,
    api_key: str | None = None,
) -> list[ContentAngle]:
    """Generate content angles từ classified comments.

    Args:
        classified: Output từ classify stage
        num_angles: Số angle muốn generate (default 10)
        top_n_per_bucket: Top N comments mỗi bucket dùng làm input (default 5)
        model: Override model (default Opus 4.7)
        api_key: Override ANTHROPIC_API_KEY
    """
    model = model or os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7")

    top_insights = select_top_insights(classified, top_n_per_bucket=top_n_per_bucket)
    if not top_insights:
        logger.warning(
            "Không có comment nào trong actionable buckets (pain/desire/question/objection). "
            "Không thể generate angle."
        )
        return []

    logger.info(
        "Generating %d angles từ %d top insights, model=%s",
        num_angles, len(top_insights), model,
    )

    insights_text = _format_insights_input(top_insights)
    user_prompt = (
        f"Generate ĐÚNG {num_angles} content angle dựa trên các insight sau.\n\n"
        f"{insights_text}\n\n"
        f"Lưu ý: Mỗi angle PHẢI có target_insight là quote nguyên văn từ 1 comment ở trên, "
        f"target_likes là số likes tương ứng. Không bịa."
    )

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    # Opus 4.7 hỗ trợ adaptive thinking + effort cho creative task
    request_kwargs: dict = {
        "model": model,
        "max_tokens": 16000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
        "output_format": ContentAngleBrief,
    }
    if model.startswith("claude-opus-4-7") or model.startswith("claude-opus-4-6"):
        request_kwargs["thinking"] = {"type": "adaptive"}
        request_kwargs["output_config"] = {"effort": "high"}

    response = client.messages.parse(**request_kwargs)

    usage = response.usage
    logger.info(
        "Suggester usage: input=%d, output=%d (cache_read=%d)",
        usage.input_tokens,
        usage.output_tokens,
        getattr(usage, "cache_read_input_tokens", 0) or 0,
    )

    if response.parsed_output is None:
        raise RuntimeError(
            f"Claude refused or failed to parse. stop_reason={response.stop_reason}"
        )

    angles = response.parsed_output.angles
    logger.info("Generated %d angles", len(angles))
    return angles


def render_brief_markdown(
    angles: list[ContentAngle],
    source_info: dict | None = None,
) -> str:
    """Render content brief thành markdown.

    Args:
        angles: List ContentAngle từ Claude
        source_info: Optional metadata (videos, total_comments, etc.)
    """
    lines: list[str] = []
    lines.append("# 🎬 Content Angle Brief\n")

    if source_info:
        if "videos" in source_info:
            lines.append(f"**Source videos**: {len(source_info['videos'])}  ")
        if "total_comments" in source_info:
            lines.append(f"**Comments analyzed**: {source_info['total_comments']}  ")
        if "model" in source_info:
            lines.append(f"**Model**: {source_info['model']}  ")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Total angles**: {len(angles)}\n")

    if source_info and "videos" in source_info:
        lines.append("**Source URLs**:")
        for url in source_info["videos"]:
            lines.append(f"- {url}")
        lines.append("")

    # Sort: confidence desc, then target_likes desc
    sorted_angles = sorted(
        angles,
        key=lambda a: (a.confidence, a.target_likes),
        reverse=True,
    )

    lines.append("---\n")

    for i, angle in enumerate(sorted_angles, 1):
        type_label = ANGLE_TYPE_LABELS.get(angle.angle_type, angle.angle_type)
        lines.append(f"## {i}. {angle.title}\n")
        lines.append(
            f"**Type**: {type_label}  "
            f"·  **Confidence**: {angle.confidence:.2f}  "
            f"·  **Demand**: {angle.target_likes} likes\n"
        )
        lines.append(f"**Target insight**:")
        lines.append(f"> \"{angle.target_insight.strip()}\"\n")
        lines.append(f"**🎣 Hook (3s đầu):**")
        lines.append(f"> {angle.hook.strip()}\n")
        lines.append(f"**📝 Script outline:**")
        for j, beat in enumerate(angle.script_outline, 1):
            lines.append(f"{j}. {beat.strip()}")
        lines.append(f"\n**🔔 CTA:** {angle.cta.strip()}\n")
        lines.append("---\n")

    return "\n".join(lines)


def save_angles_json(angles: list[ContentAngle], output_path: Path) -> None:
    """Save angles thành JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = [a.model_dump() for a in angles]
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Lưu %d angles → %s", len(angles), output_path)


def save_brief(brief_md: str, output_path: Path) -> None:
    """Save brief markdown."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(brief_md, encoding="utf-8")
    logger.info("Lưu brief → %s", output_path)


def generate_brief(
    classified: list[ClassifiedComment],
    output_path: Path,
    num_angles: int = 10,
    top_n_per_bucket: int = 5,
    model: str | None = None,
    source_videos: list[str] | None = None,
) -> list[ContentAngle]:
    """All-in-one: generate angles + render + save brief markdown."""
    angles = generate_angles(
        classified,
        num_angles=num_angles,
        top_n_per_bucket=top_n_per_bucket,
        model=model,
    )

    if not angles:
        return []

    source_info: dict = {
        "total_comments": len(classified),
        "model": model or os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7"),
    }
    if source_videos is None:
        source_videos = sorted({c.comment.video_url for c in classified if c.comment.video_url})
    if source_videos:
        source_info["videos"] = source_videos

    brief_md = render_brief_markdown(angles, source_info=source_info)
    save_brief(brief_md, output_path)

    # Save angles JSON song song để debug/reuse
    json_path = output_path.with_suffix(".json")
    save_angles_json(angles, json_path)

    return angles
