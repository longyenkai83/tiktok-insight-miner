"""Strategy Analyst — Stage 5 pipeline (Option 2 trong roadmap).

Sau khi brief generation (suggester) xong, module này tổng hợp:
- PHẦN B — Customer Profile Canvas mini (Pains/Gains/Jobs × 4 bước Liệt kê→Sắp xếp→Lựa chọn→Thực thi)
- PHẦN C — Chấm điểm brief vừa generate theo lăng kính niche persona
- PHẦN D — Synthesis (3 phát hiện + 3 product offer + content roadmap + cờ đỏ)

Output: 1 file markdown `phan-tich-toan-dien.md` đầy đủ A+B+C+D.

Cost: ~$0.05-0.08/run (Opus 4.7 với adaptive thinking, max_tokens 16000).
Latency: ~30-60s.

Reference framework: docs/psychology/insight-mining-framework.md +
sample-brief-fanpage-2745-v1.md + customer-profile-canvas-2745.md
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import anthropic

from tiktok_insight_miner.models import ClassifiedComment
from tiktok_insight_miner.suggester import (
    PRAISE_MIN_LIKES,
    _format_insights_input,
    _format_lexicon,
    _format_persona_block,
    _is_mature_persona,
    extract_lexicon,
    load_meta_pains,
    load_niche_persona,
    select_top_insights,
)

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Bạn là chuyên gia chiến lược content + product cho phụ nữ kinh doanh Việt Nam, đã làm 10+ năm marketing thực chiến.

Bạn nhận được:
1. **TOP INSIGHTS** — top comments đã phân loại 7 bucket
2. **BRIEF** — 10 content angle vừa generated ở stage trước (PHẦN A)
3. **NICHE PERSONA** — audience profile từ niche config
4. **META-PAINS** — 5+ pain ẨN audience không nói công khai (face culture)
5. **LEXICON** — vocabulary thật của audience

Nhiệm vụ: Generate **báo cáo strategy 3 phần B + C + D** dạng Markdown chuẩn. Output PHẢI là pure markdown, có nhiều bảng, tone peer-level (chị/em/mình), KHÔNG hyperbole.

═══════════════════════════════════════════════════
TEMPLATE OUTPUT (theo đúng format này — header H1 = "# Phân tích toàn diện —")
═══════════════════════════════════════════════════

# Phân tích toàn diện — [Niche name] ([N] cmt, [date])

> **Source**: report.md + brief.md
> **Generated**: [timestamp]
> **Framework**: Customer Profile Canvas (Strategyzer) + Persona v1.1

---

# PHẦN B — Customer Profile Canvas mini

## B.1 PAINS — Liệt kê → Sắp xếp → Lựa chọn → Thực thi

### B.1.1 Liệt kê (12-15 pains từ raw + meta)
Bảng: # | Pain | Source signal | Demand intensity (🔴 Extreme / 🟠 Cao / 🟡 TB / 🟢 Thấp)

### B.1.2 Sắp xếp theo Strategyzer (6 loại)
Bảng: Loại (Macro/Functional/Emotional/Social/Operational/Hidden-Meta) | Pains | Notes

### B.1.3 Lựa chọn top 5-7 priority
Bảng: Rank (🥇🥈🥉) | Pain | Lý do priority

### B.1.4 Thực thi — Pain Reliever per top
Bảng: Rank | Pain | Pain Reliever cụ thể | Format gợi ý

## B.2 GAINS — Liệt kê → Sắp xếp → Lựa chọn → Thực thi

### B.2.1 Liệt kê (10-12 gains)
### B.2.2 Sắp xếp theo Strategyzer scale (Required/Expected/Desired/Unexpected)
### B.2.3 Lựa chọn top 5
### B.2.4 Thực thi — Gain Creator per top

## B.3 JOBS — Liệt kê → Sắp xếp → Lựa chọn → Thực thi

### B.3.1 Liệt kê (8-10 jobs)
### B.3.2 Sắp xếp theo importance + journey stage (Pre-start/Starting/Growing/Scaling)
### B.3.3 Lựa chọn top 5
### B.3.4 Thực thi — JTBD framing per top
Format JTBD: "Khi tôi [situation], tôi muốn [motivation], để [outcome]"

---

# PHẦN C — Chấm điểm Brief A vừa generated

## C.1 Bảng chấm 10 angle (brief vừa tạo)
Bảng đa cột: # | Angle title | Likes target | Cluster | Score 27-45 Fanpage (1-10) | Vấn đề chính (nếu có)

## C.2 Top 3 angle xuất sắc nhất
Bullet list — angle nào + tại sao xuất sắc

## C.3 Top 3 angle yếu cần fix
Bullet list — angle nào + vấn đề + cách fix

## C.4 Tổng score brief: X.X/10
1 dòng đánh giá tổng + so với target (target: 9.0+ cho niche mature)

---

# PHẦN D — Synthesis chiến lược

## D.1 3 phát hiện chiến lược
Mỗi phát hiện: title + 2-3 dòng giải thích + tác động

## D.2 3 Product Offer candidates
Bảng: Product name | Pain solved | Gain delivered | Price range (VND) | Effort build

## D.3 Content roadmap mini — 10 video / 30 ngày
Bảng: Ngày (D01-D30) | Angle (lấy từ Brief A) | Type | Mục đích

## D.4 3-5 Cờ đỏ + Recommendations
Mỗi cờ đỏ: mức (🔴/🟠/🟡) + mô tả + action

## D.5 Tóm tắt 1 dòng
1 câu chốt toàn báo cáo

═══════════════════════════════════════════════════
QUY TẮC OUTPUT CỨNG
═══════════════════════════════════════════════════

1. PURE MARKDOWN, không có meta-text như "Here is the analysis..." hay "I'll generate..."
2. Bảng có alignment đúng (| --- | ---: | ---: |)
3. KHÔNG hyperbole ("đổi đời", "thay đổi tất cả")
4. KHÔNG clickbait ("không phải bạn dở đâu")
5. Mỗi pain/gain/job ground vào DATA THẬT (quote nguyên văn + likes) HOẶC meta-pattern
6. Product offer price phải hợp lý cho audience (vd phụ nữ KD 27-45: entry 199-499k, mid 590-1.5tr, high 1.5-5tr)
7. Content roadmap PHẢI map angle từ Brief A đã cho — KHÔNG bịa angle mới
8. Score brief HONEST — nếu yếu thì 6/10, không inflation 9/10
9. Tone peer-level — "chị/em/mình", KHÔNG "bạn xứng đáng" / "kính thưa"
10. Vietnamese throughout (trừ tên model + framework academic)

═══════════════════════════════════════════════════
PERSONA-AWARE OVERRIDE
═══════════════════════════════════════════════════

Nếu NICHE PERSONA có maturity ≥27 (mature audience):
- Chấm điểm khắt khe hơn với clickbait, slang, infantile tone
- Score 27-45 Fanpage là benchmark chính
- Product offer price ≥299k (audience có khả năng chi trả)

Nếu KHÔNG có persona (Gen Z hoặc niche unknown):
- Tone flexible hơn, có thể có emoji nhẹ
- Price entry có thể thấp hơn (99-199k)
"""


def _format_brief_for_analysis(brief_md_path: Path) -> str:
    """Read brief.md → trả raw text để inject vào prompt."""
    if not brief_md_path.exists():
        return "_(Brief file không tồn tại — chấm điểm phần C có thể skip)_"
    return brief_md_path.read_text(encoding="utf-8")


def generate_strategy_analysis(
    classified: list[ClassifiedComment],
    brief_md_path: Path,
    output_path: Path,
    niche_slug: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    """Stage 5: generate Customer Profile Canvas + Chấm brief + Synthesis.

    Args:
        classified: list ClassifiedComment từ stage 2
        brief_md_path: path tới brief.md vừa generate ở stage 4
        output_path: nơi lưu phan-tich-toan-dien.md
        niche_slug: để load persona + meta_pains
        model: override (default Opus 4.7 — task strategy cần reasoning sâu)
        api_key: override key

    Returns:
        Markdown content của phân tích.
    """
    # v0.4: Suggester + Strategy Analyst đều cần Opus depth
    model = model or os.environ.get("STRATEGY_MODEL") or "claude-opus-4-7"

    # Load top insights (include praise high-likes)
    top_insights = select_top_insights(classified, top_n_per_bucket=5)
    if not top_insights:
        raise RuntimeError("Không có insight nào để phân tích.")

    # Auto-detect niche từ output path nếu không pass
    if niche_slug is None:
        try:
            candidate = output_path.parent.parent.name
            if candidate and candidate not in ("output", ".", "..", ""):
                niche_slug = candidate
        except (AttributeError, IndexError):
            pass

    # Load persona + meta_pains nếu có
    persona_config = None
    persona_block_text = ""
    meta_pains_text = ""
    is_mature = False
    if niche_slug:
        persona_config = load_niche_persona(niche_slug)
        if persona_config:
            persona_block_text = _format_persona_block(persona_config)
            is_mature = _is_mature_persona(persona_config)
        meta_pains_raw = load_meta_pains(niche_slug)
        if meta_pains_raw:
            meta_pains_text = meta_pains_raw

    # Read brief vừa generate
    brief_text = _format_brief_for_analysis(brief_md_path)

    # Extract lexicon cho context
    lexicon = extract_lexicon(classified)

    logger.info(
        "Stage 5 Strategy Analysis: niche=%s, mature=%s, model=%s, brief=%d chars",
        niche_slug, is_mature, model, len(brief_text),
    )

    insights_text = _format_insights_input(top_insights)
    lexicon_text = _format_lexicon(lexicon)

    # Build dynamic system prompt — inject persona + meta_pains nếu có
    system_text = SYSTEM_PROMPT
    if persona_block_text:
        system_text += (
            "\n\n═══════════════════════════════════════════════════\n"
            "PART G — NICHE-SPECIFIC PERSONA (Persona-Aware Layer)\n"
            "═══════════════════════════════════════════════════\n\n"
            f"{persona_block_text}"
        )
    if meta_pains_text:
        system_text += (
            "\n\n═══════════════════════════════════════════════════\n"
            "PART H — META-PAINS (pain ẨN — dùng làm source cho B.1)\n"
            "═══════════════════════════════════════════════════\n\n"
            f"{meta_pains_text}"
        )

    user_prompt = (
        f"Generate báo cáo strategy 3 phần B + C + D theo template.\n\n"
        f"═══ NICHE ═══\n{niche_slug or '(unknown)'}\n\n"
        f"═══ TOP INSIGHTS ({len(top_insights)} items) ═══\n{insights_text}\n\n"
        f"═══ LEXICON (vocab audience) ═══\n{lexicon_text}\n\n"
        f"═══ BRIEF A vừa generate (10 angle) ═══\n{brief_text}\n\n"
        f"═══ YÊU CẦU ═══\n"
        f"Output pure markdown 3 phần B + C + D theo TEMPLATE OUTPUT trong system prompt.\n"
        f"PHẦN C — chấm 10 angle trong BRIEF A trên (KHÔNG bịa angle mới).\n"
        f"PHẦN D — content roadmap MAP angle từ BRIEF A (không thêm angle ngoài).\n"
        f"Score brief honest — nếu mediocre 6.5/10 thì nói 6.5, không inflate."
    )

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    request_kwargs: dict = {
        "model": model,
        "max_tokens": 16000,
        "system": system_text,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    # Bug 1 fix: match cả 4-6, 4-7, 4-8, 4-9...
    # messages.create() KHÔNG output_format → có thể thêm output_config={"effort":...}
    # an toàn nếu cần. Tạm giữ chỉ thinking adaptive (effort default high).
    if model.startswith("claude-opus-4"):
        request_kwargs["thinking"] = {"type": "adaptive"}

    response = client.messages.create(**request_kwargs)

    usage = response.usage
    logger.info(
        "Stage 5 usage: input=%d, output=%d (cache_read=%d)",
        usage.input_tokens,
        usage.output_tokens,
        getattr(usage, "cache_read_input_tokens", 0) or 0,
    )

    # Extract markdown text từ response
    md_parts: list[str] = []
    for block in response.content:
        if hasattr(block, "text"):
            md_parts.append(block.text)
    md_content = "\n".join(md_parts).strip()

    if not md_content:
        raise RuntimeError(
            f"Strategy Analyst trả về empty content. stop_reason={response.stop_reason}"
        )

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content, encoding="utf-8")
    logger.info("Strategy analysis saved → %s (%d chars)", output_path, len(md_content))

    return md_content
