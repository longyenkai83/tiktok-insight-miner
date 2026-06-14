"""Production — biến selected_angles.json thành file thực thi `4-thực-thi/angle-XX-*.md`.

Workflow:
  1. Load selected_angles.json (output Bước 3) + niche_config.json (Bước 1)
  2. Với mỗi angle:
     - Path A: Gọi Claude (Opus 4.7 mặc định) sinh ProductionBrief structured
     - Path B: Fallback rule-based template nếu không có API key / lỗi API
  3. Render markdown 10 sections (Metadata → Insight → Big idea → Hook → Script → B-roll → Caption → CTA → Checklist → Post-mortem)
  4. Ghi `4-thực-thi/angle-{idx:02d}-{problem_lower}-{slug}.md`

Default: skip nếu file đã tồn tại (idempotent). Pass --overwrite để re-gen.
"""

from __future__ import annotations

import json
import logging
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from tiktok_insight_miner.insight_bank import load_niche_config

logger = logging.getLogger(__name__)


# --- Pydantic schemas (Claude structured output) ---

class HookOptions(BaseModel):
    """5 hook variants — Claude trả về 5 cái strict, không phải list mơ hồ."""

    emotion_1: str = Field(description="Hook chạm cảm xúc thứ 1, 1-2 câu, max 150 ký tự")
    emotion_2: str = Field(description="Hook chạm cảm xúc thứ 2, góc khác emotion_1")
    myth_bust: str = Field(description="Hook phản biện 1 niềm tin sai phổ biến")
    question: str = Field(description="Hook dạng câu hỏi mở, kéo người xem xuống")
    caption: str = Field(description="Hook dạng câu nói ngắn, dễ làm caption (max 80 ký tự)")


class Script60s(BaseModel):
    """Script 60 giây cấu trúc 5 đoạn theo timing chuẩn."""

    s00_03_hook: str = Field(description="0-3s: Hook bắt attention")
    s03_15_pain: str = Field(description="3-15s: Chạm nỗi đau, validate cảm xúc người xem")
    s15_35_insight: str = Field(description="15-35s: Insight / root cause / framework")
    s35_50_action: str = Field(description="35-50s: 1 action nhỏ người xem có thể làm hôm nay")
    s50_60_cta: str = Field(description="50-60s: Call to action cụ thể")


class ProductionBrief(BaseModel):
    """Full brief sản xuất 1 video TikTok 60s từ 1 insight."""

    short_title: str = Field(description="Tiêu đề video 5-10 từ tiếng Việt")
    big_idea: str = Field(description="1 ý tưởng trung tâm — 1-2 câu, là 'soul' của video")
    hook_options: HookOptions
    script_60s: Script60s

    broll_main_shots: list[str] = Field(
        description="3-5 cảnh quay chính, mỗi item 1 dòng cụ thể"
    )
    text_overlays: list[str] = Field(
        description="3-5 text overlay xuất hiện trên màn hình (đồng bộ với script)"
    )
    setting: str = Field(description="Bối cảnh quay (vd: bàn làm việc tại nhà, cafe sáng)")
    props: list[str] = Field(description="Đạo cụ cần chuẩn bị (vd: laptop, sổ tay, ly cafe)")
    pacing_notes: str = Field(description="Note nhịp dựng — vd 'cut nhanh 3 lần ở 0-3s'")

    caption: str = Field(
        description="Caption FB/TikTok có chiều sâu (200-400 ký tự), không quá bán hàng"
    )

    cta_soft: str = Field(description="CTA mềm — gợi mở, không hô hào")
    cta_comment_keyword: str = Field(
        description="CTA dạng comment keyword (vd: 'Comment BÌNH YÊN để mình DM')"
    )
    cta_save_share: str = Field(description="CTA dạng lưu bài / chia sẻ với ai")

    shoot_checklist: list[str] = Field(
        description="5-8 việc cần check khi quay (props, ánh sáng, câu cần nhấn, biểu cảm)"
    )


# --- Fallback template (no API needed) ---

def _fallback_brief(angle: dict[str, Any], problem_def: dict[str, Any] | None) -> ProductionBrief:
    """Generate production brief bằng rule-based template — quality thấp hơn Claude.

    Đánh dấu rõ là fallback để user biết cần edit tay.
    """
    quote = angle.get("quote", "")
    summary = angle.get("summary", "(chưa có summary)")
    bucket = angle.get("bucket", "pain")
    problem_name = problem_def.get("name_vi", angle.get("problem_code", "?")) if problem_def else "?"

    short_title = f"[FALLBACK] {summary[:60]}"

    # Hook patterns theo bucket
    if bucket == "pain":
        emotion_1 = f"Bạn cũng từng cảm thấy: {summary.lower()}? Bạn không một mình."
        emotion_2 = f"Có 1 thứ mà phụ nữ kinh doanh ít ai dám nói thành lời..."
    elif bucket == "desire":
        emotion_1 = f"Bạn đang ước: {summary.lower()}. 3 bước để chạm đến nó."
        emotion_2 = f"Cảm giác khi bạn cuối cùng đạt được nó là gì?"
    elif bucket == "question":
        emotion_1 = f"Câu hỏi này em đã được hỏi rất nhiều lần."
        emotion_2 = f"Có 1 câu hỏi mà chị em hay hỏi em — và em sẽ trả lời thẳng hôm nay."
    else:  # objection
        emotion_1 = f"Có người sẽ nói: \"{quote[:60]}\". Em không đồng ý — đây là vì sao."
        emotion_2 = f"Nghe có vẻ đúng, nhưng nếu nhìn kỹ hơn..."

    big_idea = f"[FALLBACK — cần edit] Big idea từ insight: {summary}"

    hooks = HookOptions(
        emotion_1=emotion_1,
        emotion_2=emotion_2,
        myth_bust=f"Mọi người nghĩ X về '{problem_name.lower()}', nhưng thực ra Y.",
        question=f"Bạn đã bao giờ tự hỏi: {summary.lower()}?",
        caption=summary[:80],
    )

    script = Script60s(
        s00_03_hook=emotion_1,
        s03_15_pain=f"Em đã đọc 1 comment trên TikTok: \"{quote[:200]}\". Cảm giác này chắc nhiều chị em hiểu.",
        s15_35_insight=f"[FALLBACK — viết tay] Lý do thật sự là... [insert root cause based on '{problem_name}']",
        s35_50_action="[FALLBACK — viết tay] 1 việc bạn có thể làm ngay hôm nay là...",
        s50_60_cta="Nếu bạn cũng đang trải qua điều này, comment cho em biết bạn nghĩ gì nhé.",
    )

    return ProductionBrief(
        short_title=short_title,
        big_idea=big_idea,
        hook_options=hooks,
        script_60s=script,
        broll_main_shots=[
            "[FALLBACK] Cảnh quay chính 1 — close-up khuôn mặt, mắt nhìn camera",
            "[FALLBACK] Cảnh quay chính 2 — wide shot bàn làm việc",
            "[FALLBACK] Cảnh quay chính 3 — text overlay quote gốc",
        ],
        text_overlays=[
            f"\"{quote[:80]}\"",
            f"— @{angle.get('author', 'audience')} ({angle.get('likes', 0)} likes)",
            "Bạn cũng vậy?",
        ],
        setting="[FALLBACK] Bàn làm việc tại nhà, ánh sáng tự nhiên buổi sáng",
        props=["[FALLBACK] Laptop / sổ tay / ly cafe"],
        pacing_notes="[FALLBACK] Cut chậm, giữ nhịp ấm. Pause 1s trước khi nói insight chính.",
        caption=f"[FALLBACK — edit lại] {summary}\n\n— Quote gốc từ comment của @{angle.get('author', '?')}",
        cta_soft="Bạn có đang trải qua điều này không?",
        cta_comment_keyword="Comment 'EM' để em DM bạn cách bắt đầu.",
        cta_save_share="Lưu bài này để đọc lại khi cần.",
        shoot_checklist=[
            "[FALLBACK] Check ánh sáng đủ sáng khuôn mặt",
            "[FALLBACK] Mic không nhiễu",
            "[FALLBACK] Nhấn câu hook trong 3s đầu",
            "[FALLBACK] Biểu cảm chân thật, không gồng",
            "[FALLBACK] Quay 2 take khác nhau để có lựa chọn",
        ],
    )


# --- Claude path ---

SYSTEM_PROMPT_TEMPLATE = """Bạn là content strategist sản xuất video TikTok 60s cho phụ nữ Việt Nam {age_range} làm kinh doanh.

NICHE & PERSONA:
{persona_summary}

POSITIONING TONE:
- {tone}
- Anti-patterns CẦN TRÁNH:
{anti_patterns}

VẤN ĐỀ TRỌNG TÂM (problem này):
- Tên: {problem_name}
- Mô tả: {problem_description}
- Cảm xúc thường gặp: {common_emotions}
- Mong muốn ẩn (hidden desire): {hidden_desires}

NHIỆM VỤ:
Từ 1 insight comment thật, tạo full production brief cho 1 video TikTok 60s — script đủ dùng, không cần edit nhiều.

QUY TẮC:
1. Quote gốc PHẢI được reference trong script hoặc text overlay (proof of demand thật)
2. Tone "chị/em/mình" — peer-level, KHÔNG "quý khách / kính thưa"
3. Hook trong 3s đầu PHẢI cụ thể, KHÔNG generic ("bạn ơi cố lên")
4. Script đủ chi tiết để creator đọc thẳng vào camera, KHÔNG cần improvise
5. CTA cụ thể, không "like share follow"
6. Insight ở 15-35s phải là góc nhìn THẬT — không guru, không cliché, không hứa giàu nhanh
7. Trả về theo schema JSON đã định.
"""


def _build_system_prompt(config: dict[str, Any], problem_def: dict[str, Any] | None) -> str:
    """Inject persona + positioning + problem context vào system prompt."""
    persona = config.get("persona", {})
    positioning = config.get("positioning", {})

    age_range = persona.get("age_range", [27, 45])
    age_str = f"{age_range[0]}-{age_range[1]} tuổi"

    persona_summary = persona.get("summary", "(chưa định nghĩa persona)")

    tone = positioning.get("tone", "peer-level, ấm")
    anti_patterns_list = positioning.get("anti_pattern", [])
    anti_patterns = "\n".join(f"  • {a}" for a in anti_patterns_list) or "  • (không có)"

    if problem_def:
        problem_name = problem_def.get("name_vi", "?")
        problem_description = problem_def.get("description", "")
        common_emotions = ", ".join(problem_def.get("common_emotions", [])) or "(không có)"
        hidden_desires = "; ".join(problem_def.get("hidden_desires", [])) or "(không có)"
    else:
        problem_name = "(unclassified)"
        problem_description = ""
        common_emotions = "(không xác định)"
        hidden_desires = "(không xác định)"

    return SYSTEM_PROMPT_TEMPLATE.format(
        age_range=age_str,
        persona_summary=persona_summary,
        tone=tone,
        anti_patterns=anti_patterns,
        problem_name=problem_name,
        problem_description=problem_description,
        common_emotions=common_emotions,
        hidden_desires=hidden_desires,
    )


def _build_user_prompt(angle: dict[str, Any]) -> str:
    """Format insight để Claude generate brief."""
    return f"""INSIGHT GỐC (từ comment TikTok thật):

Quote nguyên văn: "{angle.get('quote', '')}"
Author: @{angle.get('author', '?')}
Likes: {angle.get('likes', 0)} · Replies: {angle.get('replies', 0)}
Bucket: {angle.get('bucket', '?')}
Intent: {angle.get('intent', '?')}
Opportunity type: {angle.get('opportunity', '?')}
Summary 1 câu: {angle.get('summary', '(không có)')}
Video gốc: {angle.get('video_url', '(không có)')}

Tạo full production brief cho 1 video TikTok 60s từ insight này, theo schema JSON đã cung cấp.
"""


def _generate_with_claude(
    angle: dict[str, Any],
    config: dict[str, Any],
    problem_def: dict[str, Any] | None,
    model: str | None = None,
) -> ProductionBrief:
    """Gọi Claude → ProductionBrief. Raise exception nếu fail (caller xử lý fallback)."""
    import anthropic  # lazy import — fallback path không cần anthropic

    model = model or os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7")
    system = _build_system_prompt(config, problem_def)
    user = _build_user_prompt(angle)

    client = anthropic.Anthropic()
    request_kwargs: dict = {
        "model": model,
        "max_tokens": 12000,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "output_format": ProductionBrief,
    }
    # Bug 1 fix: match cả 4-6, 4-7, 4-8, 4-9...
    # Bug 4 fix: BỎ output_config={"effort": "high"} — effort default = "high"
    # (per claude-api skill); kèm output_format trên messages.parse() conflict → fallback
    if model.startswith("claude-opus-4"):
        request_kwargs["thinking"] = {"type": "adaptive"}

    response = client.messages.parse(**request_kwargs)

    if response.parsed_output is None:
        raise RuntimeError(f"Claude refused. stop_reason={response.stop_reason}")

    usage = response.usage
    logger.info(
        "Production brief usage: input=%d, output=%d (cache_read=%d)",
        usage.input_tokens,
        usage.output_tokens,
        getattr(usage, "cache_read_input_tokens", 0) or 0,
    )

    return response.parsed_output


# --- Filename slug ---

def _strip_accent(text: str) -> str:
    """Bỏ dấu tiếng Việt: 'tiền bạc' → 'tien bac'."""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn").replace("đ", "d").replace("Đ", "D")


def _slugify(text: str, max_len: int = 50) -> str:
    """Tiếng Việt → kebab-case ASCII slug."""
    text = _strip_accent(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    text = re.sub(r"-+", "-", text)
    return text[:max_len].rstrip("-") or "untitled"


def angle_filename(idx: int, angle: dict[str, Any]) -> str:
    """`angle-01-tien-bac-binh-yen-khong-tran-trong-khi-du.md`"""
    problem_lower = angle.get("problem_code", "unclassified").lower().replace("_", "-")
    summary_slug = _slugify(angle.get("summary", "") or angle.get("quote", "")[:50], max_len=40)
    return f"angle-{idx:02d}-{problem_lower}-{summary_slug}.md"


# --- Markdown renderer ---

def _render_metadata_section(angle: dict[str, Any]) -> list[str]:
    return [
        "## 1. Metadata",
        "",
        f"- **Status**: `{angle.get('status', 'todo')}`",
        f"- **Score**: {angle.get('score', 0)}",
        f"- **Problem code**: `{angle.get('problem_code', '?')}`",
        f"- **Bucket**: {angle.get('bucket', '?')}",
        f"- **Intent**: {angle.get('intent', '?')}",
        f"- **Opportunity**: {angle.get('opportunity', '?')}",
        f"- **Source run**: {angle.get('source_run', '?')}",
        f"- **Author**: @{angle.get('author', '?')} ({angle.get('likes', 0)} likes · {angle.get('replies', 0)} replies)",
        f"- **Source quote**:",
        f"  > \"{angle.get('quote', '')}\"",
        f"- **Video URL**: {angle.get('video_url', '(không có)')}",
        "",
    ]


def _render_insight_section(angle: dict[str, Any], problem_def: dict[str, Any] | None) -> list[str]:
    L = ["## 2. Insight gốc", ""]
    L.append(f"- **Quote thật**: \"{angle.get('quote', '')}\"")
    L.append(f"- **Summary**: {angle.get('summary', '(không có)')}")
    if problem_def:
        L.append(f"- **Vấn đề chính**: {problem_def.get('name_vi', '?')} — {problem_def.get('description', '')}")
        emotions = problem_def.get("common_emotions", [])
        desires = problem_def.get("hidden_desires", [])
        if emotions:
            L.append(f"- **Cảm xúc chính**: {', '.join(emotions)}")
        if desires:
            L.append(f"- **Mong muốn ẩn**:")
            for d in desires:
                L.append(f"  - {d}")
    else:
        L.append("- **Vấn đề chính**: _(unclassified — chưa có problem_def trong config)_")
    L.append("")
    return L


def render_angle_md(
    idx: int,
    angle: dict[str, Any],
    brief: ProductionBrief,
    problem_def: dict[str, Any] | None,
    is_fallback: bool = False,
) -> str:
    """Render full markdown 10 sections."""
    L: list[str] = []
    L.append(f"# Angle {idx:02d} — {brief.short_title}")
    L.append("")
    if is_fallback:
        L.append("> ⚠️ **FALLBACK BRIEF** — generate bằng template rule-based (không có Claude).")
        L.append("> Quality thấp hơn Claude. Cần edit tay các phần đánh dấu `[FALLBACK]`.")
        L.append("")
    L.append(f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    L.append("")

    L.extend(_render_metadata_section(angle))
    L.extend(_render_insight_section(angle, problem_def))

    L.append("## 3. Big idea")
    L.append("")
    L.append(brief.big_idea)
    L.append("")

    L.append("## 4. Hook options (5 variants)")
    L.append("")
    L.append(f"**🔥 Cảm xúc 1**: {brief.hook_options.emotion_1}")
    L.append("")
    L.append(f"**🔥 Cảm xúc 2**: {brief.hook_options.emotion_2}")
    L.append("")
    L.append(f"**💥 Phản biện niềm tin sai**: {brief.hook_options.myth_bust}")
    L.append("")
    L.append(f"**❓ Câu hỏi mở**: {brief.hook_options.question}")
    L.append("")
    L.append(f"**📝 Câu nói ngắn (caption-style)**: {brief.hook_options.caption}")
    L.append("")

    L.append("## 5. Script 60 giây")
    L.append("")
    L.append(f"**0–3s · Hook**")
    L.append(f"> {brief.script_60s.s00_03_hook}")
    L.append("")
    L.append(f"**3–15s · Chạm nỗi đau**")
    L.append(f"> {brief.script_60s.s03_15_pain}")
    L.append("")
    L.append(f"**15–35s · Insight / root cause**")
    L.append(f"> {brief.script_60s.s15_35_insight}")
    L.append("")
    L.append(f"**35–50s · Hành động nhỏ**")
    L.append(f"> {brief.script_60s.s35_50_action}")
    L.append("")
    L.append(f"**50–60s · CTA**")
    L.append(f"> {brief.script_60s.s50_60_cta}")
    L.append("")

    L.append("## 6. B-roll / Visual suggestions")
    L.append("")
    L.append("**Cảnh quay chính:**")
    for shot in brief.broll_main_shots:
        L.append(f"- {shot}")
    L.append("")
    L.append("**Text overlay:**")
    for overlay in brief.text_overlays:
        L.append(f"- {overlay}")
    L.append("")
    L.append(f"**Bối cảnh quay**: {brief.setting}")
    L.append("")
    L.append("**Props:**")
    for prop in brief.props:
        L.append(f"- {prop}")
    L.append("")
    L.append(f"**Nhịp dựng**: {brief.pacing_notes}")
    L.append("")

    L.append("## 7. Caption")
    L.append("")
    L.append(brief.caption)
    L.append("")

    L.append("## 8. CTA (3 lựa chọn)")
    L.append("")
    L.append(f"- **Mềm**: {brief.cta_soft}")
    L.append(f"- **Comment keyword**: {brief.cta_comment_keyword}")
    L.append(f"- **Lưu / chia sẻ**: {brief.cta_save_share}")
    L.append("")

    L.append("## 9. Checklist quay")
    L.append("")
    for item in brief.shoot_checklist:
        L.append(f"- [ ] {item}")
    L.append("")

    L.append("## 10. Post-mortem (fill sau khi đăng)")
    L.append("")
    L.append("- **Ngày đăng**: ")
    L.append("- **Nền tảng**: TikTok / Facebook / Instagram")
    L.append("- **View**: ")
    L.append("- **Like**: ")
    L.append("- **Comment**: ")
    L.append("- **Share**: ")
    L.append("- **Save**: ")
    L.append("- **Bài học rút ra**: ")
    L.append("")

    return "\n".join(L)


# --- Path resolution ---

def resolve_output_dir(angles_json_path: Path) -> Path:
    """`output/<niche>/_master/selected_angles.json` → `output/<niche>/4-thực-thi/`"""
    niche_root = angles_json_path.parent.parent
    return niche_root / "4-thực-thi"


# --- Entry point ---

def run_production(
    angles_json: Path,
    config_path: Path,
    output_dir: Path | None = None,
    use_claude: bool = True,
    model: str | None = None,
    limit: int | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """All-in-one: load + per-angle generate + write.

    Args:
        angles_json: Path tới selected_angles.json
        config_path: Path tới niche_config.json
        output_dir: Override `4-thực-thi/` location
        use_claude: False → dùng fallback template, True → thử Claude (fallback nếu lỗi)
        model: Override Claude model
        limit: Chỉ generate N angle đầu (cho test)
        overwrite: True → re-gen file đã tồn tại

    Returns dict stats + paths.
    """
    config = load_niche_config(config_path)
    angles = json.loads(angles_json.read_text(encoding="utf-8"))

    if limit:
        angles = angles[:limit]

    if output_dir is None:
        output_dir = resolve_output_dir(angles_json)
    output_dir.mkdir(parents=True, exist_ok=True)

    problem_index = {p["code"]: p for p in config.get("main_problems", [])}

    stats = {
        "total_angles": len(angles),
        "generated_claude": 0,
        "generated_fallback": 0,
        "skipped_existing": 0,
        "failed": 0,
        "files": [],
    }

    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if use_claude and not has_api_key:
        logger.warning("ANTHROPIC_API_KEY không có — auto chuyển sang fallback")
        use_claude = False

    for idx, angle in enumerate(angles, 1):
        filename = angle_filename(idx, angle)
        out_path = output_dir / filename

        if out_path.exists() and not overwrite:
            print(f"  [{idx}/{len(angles)}] SKIP (đã có): {filename}")
            stats["skipped_existing"] += 1
            stats["files"].append(out_path)
            continue

        problem_def = problem_index.get(angle.get("problem_code"))
        is_fallback = not use_claude

        # Try Claude first if enabled
        if use_claude:
            try:
                print(
                    f"  [{idx}/{len(angles)}] Claude generating: "
                    f"{angle.get('problem_code', '?')} — \"{angle.get('quote', '')[:50]}...\""
                )
                brief = _generate_with_claude(angle, config, problem_def, model=model)
                stats["generated_claude"] += 1
            except Exception as e:
                logger.warning("Angle %d: Claude lỗi (%s) — fallback", idx, e)
                brief = _fallback_brief(angle, problem_def)
                is_fallback = True
                stats["generated_fallback"] += 1
        else:
            print(f"  [{idx}/{len(angles)}] Fallback template: {filename}")
            brief = _fallback_brief(angle, problem_def)
            stats["generated_fallback"] += 1

        try:
            md = render_angle_md(idx, angle, brief, problem_def, is_fallback=is_fallback)
            out_path.write_text(md, encoding="utf-8")
            stats["files"].append(out_path)
            logger.info("Wrote %s", out_path)
        except Exception as e:
            logger.error("Render/write angle %d lỗi: %s", idx, e)
            stats["failed"] += 1

    stats["output_dir"] = output_dir
    return stats
