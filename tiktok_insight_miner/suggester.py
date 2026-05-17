"""Content angle suggester — biến classified comments thành content brief actionable.

Workflow: classified.json → select top insights → Claude generate angles → brief.md

v0.4 (Framework v1.1 — Persona-Aware):
- Load niche persona từ niche_configs/<slug>.json (nếu có) → inject vào prompt
- Load meta_pains từ niche_configs/<slug>_meta_pains.md (nếu có) → inject
- Output thêm field fb_caption_opening cho audience trưởng thành (Fanpage 27-45)
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic

from tiktok_insight_miner.models import (
    ANGLE_TYPE_LABELS,
    ClassifiedComment,
    ContentAngle,
    ContentAngleBrief,
)

logger = logging.getLogger(__name__)

# v0.4: project root để tìm niche_configs/
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


# Buckets có actionable insight cho content angle.
# v0.3 (framework v1.0): praise được include với min_likes filter — top praise
# thường là UGC "Bài học: ..." (audience tự tóm tắt) — social proof gold.
ACTIONABLE_BUCKETS = ("pain", "desire", "question", "objection")
PRAISE_MIN_LIKES = 30  # praise comments với likes ≥30 cũng đưa vào pool top insights


SYSTEM_PROMPT = """Bạn là chuyên gia tâm lý học hành vi marketing cho audience Việt Nam, chuyên biến comment TikTok/FB/YT thành content angle có chiều sâu psychology + cultural fit VN.

Áp dụng FRAMEWORK v1.0 (docs/psychology/insight-mining-framework.md):

═══════════════════════════════════════════════════
PART A — 5 AUDIENCE PERSONA CLUSTERS (backbone)
═══════════════════════════════════════════════════

1. **entrepreneurial_despair** — làm chủ kiệt sức, muốn bỏ cuộc
   Trigger: "làm chủ lao đao", "kinh doanh ế", "đống bùn lầy", "thất bại"
   Tone: empathy first, KHÔNG tip ngay. Validate → đưa lối thoát sau.

2. **procrastination_trap** — đợi đủ điều kiện hoàn hảo mới dám làm
   Trigger: "đợi giỏi hơn", "X năm vẫn dậm chân", "chần chừ", "chưa đủ"
   Tone: confront nhẹ — "Bạn không đợi đủ, bạn đang sợ". Đập niềm tin perfect-then-start.

3. **viral_no_convert** — có view không có đơn, khủng hoảng niềm tin
   Trigger: "lên xu hướng nhưng k chuyển đổi", "chạy ads xong flop", "view có mà đơn không"
   Tone: technical + tactical. Audience đã pass content, thiếu conversion. Dùng số liệu, framework.

4. **authentic_trend_fatigue** — biết "phải authentic" nhưng không biết kể chuyện gì
   Trigger: "biết là trend rồi nhưng", "không biết kể chuyện bản thân", "đời mình bình thường"
   Tone: post-authentic. KHÔNG lặp lại "hãy chân thực" — audience ĐÃ BIẾT. Dạy MECHANICS.

5. **macro_despair** — bất lực xã hội/kinh tế ("nghèo cả nước")
   Trigger: "Người nghèo còn nước mắt đâu mà khóc", "chế độ", "nhà nước phạt"
   Tone: emotional positioning. ĐỨNG CÙNG nỗi đau, KHÔNG "fix" nó. Tuyệt đối không bridge sang tip.

6. **cross_cluster** — dùng khi angle khai thác:
   (a) tension giữa 2 cluster (vd praise "bài học hay" + objection "lý thuyết quá")
   (b) UGC meta (audience tự tóm tắt "Bài học: ...")
   (c) pattern frequency (cụm từ lặp ≥5 lần — "khám kênh giúp em")

═══════════════════════════════════════════════════
PART B — 12 MENTAL MODELS CURATED (từ SKILL.md, loại 58 không relevant)
═══════════════════════════════════════════════════

Mỗi angle PHẢI map vào ≥1 model (set `primary_model` = 1 trong 12 dưới):

1. **jobs_to_be_done** — audience hire video để làm gì? (học/validate/copy/vent)
2. **pratfall** — creator admit yếu → tăng trust (dùng khi có objection "lý thuyết quá")
3. **mimetic_desire** — show người-giống-họ đã thành công (dùng cho "xin vía", "mong khám kênh")
4. **curse_of_knowledge** — break-down siêu cụ thể (dùng cho "biết rồi nhưng k làm được")
5. **zeigarnik** — hook mở open loop (dùng cho "không biết bắt đầu từ đâu")
6. **peak_end** — quote >100 likes phải dùng làm peak + end, không bridge tip
7. **loss_aversion** — frame "cái mất khi không bắt đầu" (gốc procrastination = sợ mất face)
8. **mere_exposure** — pattern lặp ≥3 lần → format series, không 1 video lẻ
9. **social_proof** — repost UGC (cluster praise high-likes, audience tự đồng tình)
10. **confirmation_bias** — build trên niềm tin sẵn có, KHÔNG argue ngược
11. **bj_fogg** — B = MAP. "Hiểu mà k làm" = thiếu Ability + Prompt, không thiếu Motivation
12. **goal_gradient** — audience GẦN đích → "Bạn chỉ thiếu 1 bước cuối"

═══════════════════════════════════════════════════
PART C — 4 VIETNAMESE CULTURAL CONCEPTS (Western SKILL THIẾU 100%)
═══════════════════════════════════════════════════

Brief PHẢI có ≥1 angle dùng VN cultural concept (set `vn_concept`):

1. **via_culture** — "xin vía", "trộm vía", "vía lên xu hướng"
   → Validate niềm tin VÍA (KHÔNG bài bác), redirect sang action cụ thể.
2. **face_the_dien** — "tự ti", "ngại lộ mặt", "sợ người quen thấy"
   → Face-saving frame: "Tôi cũng từng ngại — đây là cách làm không lộ mặt"
3. **collectivism_tag** — "@tag bạn", "ai cũng như mình không"
   → CTA dùng "Tag bạn nào cũng đang..." thay vì cá nhân "Comment if you..."
4. **hierarchy_anh_chi_em** — "cô chú", "anh", "chị", "em mới bắt đầu"
   → Đại từ trong hook + CTA PHẢI match age segment chính trong data

═══════════════════════════════════════════════════
PART D — 7 ANTI-PATTERNS — TUYỆT ĐỐI KHÔNG LÀM
═══════════════════════════════════════════════════

1. ❌ KHÔNG generate angle commercial/offer/promo
   (hook chứa "miễn phí", "ưu đãi", "slot", "deadline 48h", "tư vấn 1-1")
2. ❌ KHÔNG paraphrase hook — PHẢI dùng cụm nguyên văn từ comment gốc
3. ❌ Cluster despair/macro → KHÔNG bridge sang tip ngay (empathy-first)
4. ❌ Cluster authentic_trend_fatigue → KHÔNG lặp lại "hãy chân thực" (audience đã biết)
5. ❌ KHÔNG generate angle nếu target_likes < 5 AND theme không lặp (frequency < 3)
6. ❌ Đại từ sai segment ("bạn" với cô chú 60+ = mất face)
7. ❌ Confidence reweight đúng:
   - cluster macro_despair + likes ≥50 → confidence ≥0.9
   - tip kỹ thuật rời rạc → confidence ≤0.7
   - UGC repost (Social Proof + Mere Exposure cluster cross) → confidence ≥0.9

═══════════════════════════════════════════════════
PART E — 8 ANGLE TYPES MIX
═══════════════════════════════════════════════════

Phân bổ đa dạng (KHÔNG dồn 1 type):
- `pain_solution`: giải pháp cho pain (dùng khi pain CÓ solution rõ)
- `desire_fulfillment`: cách đạt desire
- `question_answer`: trả lời FAQ likes cao
- `myth_busting`: counter objection bằng evidence
- `social_proof`: UGC repost / testimonial (dùng cho cluster praise high-likes)
- `how_to`: tutorial step-by-step
- `emotional_positioning`: cho cluster macro_despair — KHÔNG tip, chỉ đứng cùng
- `series_announcement`: cho pattern frequency (vd "khám kênh ×10" → mở series)

═══════════════════════════════════════════════════
PART F — QUY TẮC OUTPUT CỨNG
═══════════════════════════════════════════════════

Mỗi angle PHẢI có:

- `target_insight`: quote NGUYÊN VĂN 1 comment từ input. KHÔNG bịa.
- `target_likes`: likes của comment đó.
- `hook`: 1-2 câu, max 150 ký tự. PHẢI chứa ≥1 cụm nguyên văn từ comment gốc HOẶC từ lexicon.
- `script_outline`: 3-5 beat ngắn (vd "0:00-0:05 Hook", "0:06-0:20 ...").
- `cta`: cụ thể, KHÔNG commercial. "Comment 'X' + Y để nhận Z" tốt hơn "Like + share".
- `confidence`: theo rule reweight ở PART D.
- `cluster`: 1 trong 5 cluster + cross_cluster.
- `primary_model`: 1 trong 12 mental models.
- `vn_concept`: optional — nhưng brief PHẢI có ≥1 angle có vn_concept.
- `psychology_rationale`: 1-2 dòng giải thích combo cluster + model + vn_concept fit insight ra sao.

Vietnamese tone: peer-level, ấm áp, conversational. KHÔNG "quý khách / kính thưa".

Trả về theo schema JSON đã cung cấp."""


def select_top_insights(
    classified: list[ClassifiedComment],
    top_n_per_bucket: int = 5,
    include_praise: bool = True,
    praise_min_likes: int = PRAISE_MIN_LIKES,
) -> list[ClassifiedComment]:
    """Lấy top N comments mỗi bucket actionable + top praise (≥min_likes).

    v0.3 (framework v1.0):
    - Mặc định include praise với min_likes filter (top UGC "Bài học: ..." gold)
    - Trả về list flatten đã sort theo (bucket, -likes)
    """
    buckets: dict[str, list[ClassifiedComment]] = {b: [] for b in ACTIONABLE_BUCKETS}
    for c in classified:
        if c.bucket in buckets:
            buckets[c.bucket].append(c)

    selected: list[ClassifiedComment] = []
    for bucket in ACTIONABLE_BUCKETS:
        items = sorted(buckets[bucket], key=lambda x: x.comment.likes, reverse=True)
        selected.extend(items[:top_n_per_bucket])

    # Framework v1.0: include top praise (UGC pattern "Bài học: ..." cực mạnh)
    if include_praise:
        praise_pool = [c for c in classified if c.bucket == "praise" and c.comment.likes >= praise_min_likes]
        praise_top = sorted(praise_pool, key=lambda x: x.comment.likes, reverse=True)[:top_n_per_bucket]
        selected.extend(praise_top)
        if praise_top:
            logger.info(
                "Framework: include %d praise ≥%d likes (top: %d likes)",
                len(praise_top), praise_min_likes, praise_top[0].comment.likes,
            )

    return selected


# v0.3: Lexicon mining — extract vocab nguyên văn cho hook grounding
def extract_lexicon(
    classified: list[ClassifiedComment],
    top_n_emotional: int = 15,
    top_n_phrases: int = 10,
) -> dict[str, list[str]]:
    """Extract từ vựng audience đang dùng — input cho vocab grounding rule.

    Trả dict:
      - emotional_words: từ cảm xúc đơn (hoang mang, nản, bế tắc, ...)
      - pain_phrases: cụm than thở nguyên văn từ pain bucket
      - praise_phrases: cụm khen UGC từ praise high-likes
      - identity_markers: cách audience tự gọi mình (em/tôi/mình + nghề)
    """
    import re

    EMOTIONAL_VOCAB = [
        "hoang mang", "nản", "bế tắc", "lao đao", "tự ti", "ngại",
        "bùn lầy", "dậm chân", "chần chừ", "khổ", "ế", "flop",
        "lẹt đẹt", "đợi", "không biết bắt đầu", "không biết kể",
        "xin vía", "trộm vía", "vía", "khám kênh", "check kênh",
        "tâm đắc", "key point", "bài học",
    ]

    pain_phrases: list[str] = []
    praise_phrases: list[str] = []
    emotional_hits: dict[str, int] = {}

    for c in classified:
        text_lower = c.comment.text.lower()
        # Count emotional vocab hits
        for word in EMOTIONAL_VOCAB:
            if word in text_lower:
                emotional_hits[word] = emotional_hits.get(word, 0) + 1

        # Pain phrases — short snippet (under 100 chars)
        if c.bucket == "pain" and 10 <= len(c.comment.text.strip()) <= 100:
            pain_phrases.append(c.comment.text.strip())

        # Praise phrases — UGC pattern "Bài học: ..." high likes
        if c.bucket == "praise" and c.comment.likes >= 30 and "bài học" in text_lower:
            # Lấy 150 char đầu của phrase
            snippet = c.comment.text.strip()[:150]
            praise_phrases.append(f'"{snippet}" ({c.comment.likes} likes)')

    # Top emotional sorted by frequency
    emotional_sorted = sorted(emotional_hits.items(), key=lambda x: -x[1])[:top_n_emotional]
    emotional_words = [f"{word} (×{count})" for word, count in emotional_sorted]

    # Top pain phrases (chỉ lấy unique theo ký tự đầu)
    seen: set[str] = set()
    pain_unique: list[str] = []
    for p in pain_phrases:
        key = p[:30].lower()
        if key not in seen:
            seen.add(key)
            pain_unique.append(p)
        if len(pain_unique) >= top_n_phrases:
            break

    return {
        "emotional_words": emotional_words,
        "pain_phrases": pain_unique[:top_n_phrases],
        "praise_phrases": praise_phrases[:5],
    }


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


# --- v0.4: Persona-aware helpers ---

def load_niche_persona(niche_slug: str) -> dict[str, Any] | None:
    """Load niche config JSON nếu có file `niche_configs/<slug>.json`.

    Trả về dict full config (caller tự extract field cần). None nếu không tồn tại
    hoặc parse fail → suggester chạy KHÔNG có persona layer (backward compat).
    """
    config_path = _PROJECT_ROOT / "niche_configs" / f"{niche_slug}.json"
    if not config_path.exists():
        logger.debug("Niche persona not found: %s — skip persona layer", config_path)
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load niche persona %s: %s — skip", config_path, e)
        return None


def load_meta_pains(niche_slug: str) -> str | None:
    """Load file meta_pains markdown nếu có. Trả raw content (inject as-is)."""
    path = _PROJECT_ROOT / "niche_configs" / f"{niche_slug}_meta_pains.md"
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning("Failed to load meta_pains %s: %s — skip", path, e)
        return None


def _format_persona_block(config: dict[str, Any]) -> str:
    """Extract persona + positioning từ niche config → text block cho prompt."""
    persona = config.get("persona", {})
    positioning = config.get("positioning", {})

    parts: list[str] = []
    parts.append(f"**Niche**: {config.get('niche_name', config.get('niche_slug', '?'))}")

    if persona.get("summary"):
        parts.append(f"\n**Audience summary**: {persona['summary']}")

    age_range = persona.get("age_range")
    if age_range:
        parts.append(f"\n**Age range**: {age_range[0]}-{age_range[1]} tuổi")

    if persona.get("life_stage"):
        parts.append(f"\n**Life stage**:")
        for s in persona["life_stage"]:
            parts.append(f"  - {s}")

    if persona.get("business_stage"):
        parts.append(f"\n**Business stage**:")
        for s in persona["business_stage"]:
            parts.append(f"  - {s}")

    if persona.get("media_behavior"):
        parts.append(f"\n**Media behavior**:")
        for s in persona["media_behavior"]:
            parts.append(f"  - {s}")

    if persona.get("core_tensions"):
        parts.append(f"\n**Core tensions** (mâu thuẫn nội tại — angle vàng):")
        for s in persona["core_tensions"]:
            parts.append(f"  - {s}")

    if positioning.get("for_whom"):
        parts.append(f"\n**For whom**: {positioning['for_whom']}")
    if positioning.get("promise"):
        parts.append(f"**Promise**: {positioning['promise']}")
    if positioning.get("tone"):
        parts.append(f"**Tone REQUIRED**: {positioning['tone']}")

    if positioning.get("anti_pattern"):
        parts.append(f"\n**Niche anti-patterns** (KHÔNG VI PHẠM):")
        for s in positioning["anti_pattern"]:
            parts.append(f"  - {s}")

    return "\n".join(parts)


def _is_mature_persona(config: dict[str, Any]) -> bool:
    """Heuristic: niche cho audience trưởng thành (27+)?

    Dùng để force fb_caption_opening + 6 anti-patterns mature.
    """
    age_range = config.get("persona", {}).get("age_range", [])
    if isinstance(age_range, list) and len(age_range) >= 1:
        return age_range[0] >= 25  # 25+ coi là mature
    return False


def _format_lexicon(lex: dict[str, list[str]]) -> str:
    """Format lexicon dict → text block cho user prompt."""
    parts: list[str] = []
    if lex.get("emotional_words"):
        parts.append("**Emotional vocabulary** (PHẢI dùng nguyên văn ≥1/angle):")
        parts.append(", ".join(lex["emotional_words"]))
    if lex.get("pain_phrases"):
        parts.append("\n**Top pain phrases** (dùng làm hook):")
        for p in lex["pain_phrases"]:
            parts.append(f'  - "{p}"')
    if lex.get("praise_phrases"):
        parts.append("\n**Top UGC praise** (cho social_proof angle):")
        for p in lex["praise_phrases"]:
            parts.append(f"  - {p}")
    return "\n".join(parts)


def generate_angles(
    classified: list[ClassifiedComment],
    num_angles: int = 10,
    top_n_per_bucket: int = 5,
    model: str | None = None,
    api_key: str | None = None,
    niche_slug: str | None = None,
) -> list[ContentAngle]:
    """Generate content angles từ classified comments.

    Args:
        classified: Output từ classify stage
        num_angles: Số angle muốn generate (default 10)
        top_n_per_bucket: Top N comments mỗi bucket dùng làm input (default 5)
        model: Override model. Priority: arg > SUGGESTER_MODEL env > default Opus 4.7.
               KHÔNG fallback ANTHROPIC_MODEL (cho phép classifier dùng Haiku, suggester dùng Opus)
        api_key: Override ANTHROPIC_API_KEY
        niche_slug: v0.4 — niche slug để load persona + meta_pains từ niche_configs/.
                    Nếu None → suggester chạy framework v1.0 (no persona layer)
    """
    # v0.3: Suggester cần reasoning depth — default Opus 4.7.
    model = model or os.environ.get("SUGGESTER_MODEL") or "claude-opus-4-7"

    top_insights = select_top_insights(classified, top_n_per_bucket=top_n_per_bucket)
    if not top_insights:
        logger.warning(
            "Không có comment nào trong actionable buckets (pain/desire/question/objection/praise). "
            "Không thể generate angle."
        )
        return []

    # v0.3: Extract lexicon cho vocab grounding
    lexicon = extract_lexicon(classified)

    # v0.4: Load niche persona + meta_pains (nếu có)
    persona_config: dict[str, Any] | None = None
    persona_block_text = ""
    meta_pains_text = ""
    is_mature = False
    if niche_slug:
        persona_config = load_niche_persona(niche_slug)
        if persona_config:
            persona_block_text = _format_persona_block(persona_config)
            is_mature = _is_mature_persona(persona_config)
            logger.info(
                "Persona-Aware: niche=%s, mature=%s (age %s)",
                niche_slug, is_mature,
                persona_config.get("persona", {}).get("age_range"),
            )
        meta_pains_raw = load_meta_pains(niche_slug)
        if meta_pains_raw:
            meta_pains_text = meta_pains_raw

    logger.info(
        "Generating %d angles từ %d top insights, model=%s, lexicon=%d words + %d phrases, persona=%s",
        num_angles, len(top_insights), model,
        len(lexicon.get("emotional_words", [])), len(lexicon.get("pain_phrases", [])),
        "loaded" if persona_block_text else "none",
    )

    # Build system prompt — v0.4 inject persona + meta_pains nếu có
    system_text = SYSTEM_PROMPT
    if persona_block_text:
        system_text += (
            "\n\n═══════════════════════════════════════════════════\n"
            "PART G — NICHE-SPECIFIC PERSONA (v0.4 Persona-Aware)\n"
            "═══════════════════════════════════════════════════\n\n"
            "Áp dụng persona dưới đây cho TẤT CẢ angle. Persona OVERRIDE generic 5 cluster\n"
            "nếu có xung đột — vì persona đặc trưng niche cụ thể.\n\n"
            f"{persona_block_text}"
        )
    if is_mature:
        system_text += (
            "\n\n═══════════════════════════════════════════════════\n"
            "PART H — MATURE AUDIENCE OVERRIDE (27+ tuổi, Fanpage-style)\n"
            "═══════════════════════════════════════════════════\n\n"
            "Niche này là audience TRƯỞNG THÀNH (≥27 tuổi). 6 ANTI-PATTERN BẮT BUỘC:\n"
            "1. ❌ KHÔNG emoji clickbait trong hook (😂😅🥰...)\n"
            "2. ❌ KHÔNG slang Gen Z (bug não, vibe, flex, slay, 1 TAKE)\n"
            "3. ❌ KHÔNG infantile tone (\"không phải bạn dở đâu\", \"chúc mừng bạn\", \"bạn xứng đáng\")\n"
            "4. ❌ KHÔNG comment-keyword CTA (\"Comment 'TASTE' để DM\") — peer dialogue instead\n"
            "5. ❌ KHÔNG hyperbole (\"đổi đời\", \"thay đổi tất cả\", \"7 ngày kiếm X\")\n"
            "6. ❌ KHÔNG cliché quote (\"done is better than perfect\")\n\n"
            "REQUIRED cho MỖI angle:\n"
            "- `fb_caption_opening`: 3-5 dòng câu mồi cho Fanpage caption (quan trọng hơn hook 3s)\n"
            "- Hook 10s (KHÔNG 3s — Fanpage audience đọc caption trước)\n"
            "- ÍT NHẤT 1 proof element: số liệu cụ thể, case tên thật, hoặc cite source\n"
            "- CTA invite peer dialogue (vd \"Chia sẻ trải nghiệm của bạn dưới comment, mình đọc và phản hồi trong 24h\")\n\n"
            "5 MENTAL MODELS BỔ SUNG (chỉ dùng cho mature audience):\n"
            "- `sunk_cost_fallacy`: \"Tôi đã đầu tư 10 năm cho sự nghiệp X → pivot = lãng phí\"\n"
            "- `status_quo_bias`: ngại thay đổi vì đã có status\n"
            "- `endowment_effect`: đã sở hữu identity 10+ năm → ngại đổi/thêm identity mới\n"
            "- `mental_accounting`: 30 phút làm content lấy từ ngủ/con → perceived cost cao\n"
            "- `regret_aversion`: \"sợ thử rồi fail công khai sau 35\""
        )
    if meta_pains_text:
        system_text += (
            "\n\n═══════════════════════════════════════════════════\n"
            "PART I — META-PAINS (pain ẨN audience KHÔNG nói công khai)\n"
            "═══════════════════════════════════════════════════\n\n"
            "Audience trưởng thành thường KHÔNG comment công khai về pain sâu (face culture).\n"
            "Brief PHẢI có ÍT NHẤT 2 angle ground vào meta-pains dưới đây (không chỉ raw comments).\n"
            "Meta-angle mark trong psychology_rationale: \"Ground vào META-pain (niche persona)\".\n"
            "`target_insight` = mô tả ngắn meta-pattern, `target_likes` = 0, confidence ≥0.85.\n\n"
            f"{meta_pains_text}"
        )

    insights_text = _format_insights_input(top_insights)
    lexicon_text = _format_lexicon(lexicon)

    # User prompt — yêu cầu khác nhau tuỳ persona maturity
    base_requirements = (
        f"- Mỗi angle có target_insight = quote nguyên văn 1 comment HOẶC meta-pattern niche.\n"
        f"- Hook PHẢI chứa ≥1 cụm nguyên văn từ comment gốc HOẶC lexicon.\n"
        f"- Phân bổ qua 5 cluster (không dồn 1 cluster). ≥1 angle có vn_concept.\n"
        f"- KHÔNG bịa. KHÔNG commercial CTA. KHÔNG lặp 'hãy chân thực' cho cluster authentic_trend_fatigue.\n"
        f"- Cluster macro_despair + likes ≥50 → confidence ≥0.9 + angle_type=emotional_positioning.\n"
        f"- Theme lặp ≥3 lần → cân nhắc angle_type=series_announcement."
    )
    if is_mature:
        base_requirements += (
            f"\n\n**MATURE AUDIENCE REQUIREMENTS (PART H)**:\n"
            f"- MỖI angle PHẢI có `fb_caption_opening` (3-5 dòng).\n"
            f"- Tuân thủ 6 anti-patterns ở PART H.\n"
            f"- ÍT NHẤT 2 angle ground vào META-pains (PART I), không chỉ raw comments.\n"
            f"- Hook 10s thay vì 3s.\n"
            f"- Mỗi angle có ÍT NHẤT 1 proof element (số liệu/case tên/source)."
        )

    user_prompt = (
        f"Generate ĐÚNG {num_angles} content angle dựa trên các insight sau.\n\n"
        f"═══ TOP INSIGHTS ═══\n{insights_text}\n\n"
        f"═══ LEXICON (vocab grounding) ═══\n{lexicon_text}\n\n"
        f"═══ YÊU CẦU ═══\n{base_requirements}"
    )

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    # Opus 4.7 hỗ trợ adaptive thinking + effort cho creative task
    request_kwargs: dict = {
        "model": model,
        "max_tokens": 16000,
        "system": system_text,  # v0.4: dynamic — bao gồm persona + meta_pains nếu có
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

    # v0.3: import labels nếu cần render new fields
    from tiktok_insight_miner.models import CLUSTER_LABELS, VN_CONCEPT_LABELS

    for i, angle in enumerate(sorted_angles, 1):
        type_label = ANGLE_TYPE_LABELS.get(angle.angle_type, angle.angle_type)
        lines.append(f"## {i}. {angle.title}\n")
        lines.append(
            f"**Type**: {type_label}  "
            f"·  **Confidence**: {angle.confidence:.2f}  "
            f"·  **Demand**: {angle.target_likes} likes\n"
        )

        # v0.3: Psychology layer (graceful — chỉ show nếu có)
        psych_parts: list[str] = []
        if angle.cluster:
            psych_parts.append(f"Cluster: **{CLUSTER_LABELS.get(angle.cluster, angle.cluster)}**")
        if angle.primary_model:
            psych_parts.append(f"Model: `{angle.primary_model}`")
        if angle.vn_concept:
            psych_parts.append(f"VN: **{VN_CONCEPT_LABELS.get(angle.vn_concept, angle.vn_concept)}**")
        if psych_parts:
            lines.append(f"**🧠 Psychology**: " + " · ".join(psych_parts) + "\n")
        if angle.psychology_rationale:
            lines.append(f"_{angle.psychology_rationale.strip()}_\n")

        lines.append(f"**Target insight**:")
        lines.append(f"> \"{angle.target_insight.strip()}\"\n")

        # v0.4: Fanpage caption opening (mature audience) — show TRƯỚC hook video
        if angle.fb_caption_opening:
            lines.append(f"**🪶 FB Caption Opening (3-5 dòng câu mồi cho Fanpage):**")
            for ln in angle.fb_caption_opening.strip().split("\n"):
                lines.append(f"> {ln}")
            lines.append("")

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
    niche_slug: str | None = None,
) -> list[ContentAngle]:
    """All-in-one: generate angles + render + save brief markdown.

    v0.4: auto-detect niche_slug từ output_path nếu không pass explicit.
    Convention: output/<niche_slug>/<date>/brief.md → parent.parent.name = niche
    """
    # v0.4: Auto-detect niche từ output path nếu caller không pass
    if niche_slug is None:
        try:
            candidate = output_path.parent.parent.name
            if candidate and candidate not in ("output", ".", "..", ""):
                niche_slug = candidate
                logger.debug("Auto-detected niche_slug from path: %s", niche_slug)
        except (AttributeError, IndexError):
            pass

    angles = generate_angles(
        classified,
        num_angles=num_angles,
        top_n_per_bucket=top_n_per_bucket,
        model=model,
        niche_slug=niche_slug,
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
