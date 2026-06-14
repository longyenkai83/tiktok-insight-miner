"""CoWork Brief Pack — Stage C Refinement Layer.

Transform RAW data (report + brief + strategy ở Drive) thành DATA TINH
(1 file md ~3-5KB) sẵn sàng paste vào CoWork workspace để Hiền viết bài.

Workflow:
  1. parse_brief_angles(brief.md) → 10 angles dict
  2. User tick chọn 3-5 angle trong webapp
  3. load_voice_profile() từ profiles/<persona>/
  4. generate_cowork_pack() render markdown
  5. save_cowork_pack() write file + return content

KHÔNG gọi Claude. Pure parse + render. Cost zero, latency <1s.

Reference: docs/psychology/customer-profile-canvas-2745.md (Stage C design)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Project root để load profiles
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

ANTI_PATTERNS_MATURE = [
    "KHÔNG emoji clickbait trong hook (😂😅🥰)",
    "KHÔNG slang Gen Z (bug não, 1 take, vibe, flex, slay)",
    "KHÔNG infantile tone ('không phải bạn dở đâu', 'chúc mừng bạn', 'bạn xứng đáng')",
    "KHÔNG comment-keyword CTA ('Comment X để DM Y') — peer dialogue thay vào",
    "KHÔNG hyperbole ('đổi đời', 'thay đổi tất cả', '7 ngày kiếm X')",
    "KHÔNG cliché quote ('done is better than perfect')",
]


def parse_brief_angles(brief_md_path: Path) -> list[dict]:
    """Parse brief.md → list of angle dicts.

    Brief format chuẩn (suggester output):
      ## N. <title>
      **Type**: ... · **Confidence**: 0.XX · **Demand**: NNN likes
      **🧠 Psychology**: Cluster: ... · Model: ...
      **Target insight**: > "..."
      **🪶 FB Caption Opening**: ...
      **🎣 Hook**: > ...
      **📝 Script outline**: ...
      **🔔 CTA**: ...

    Trả về list dict với keys: idx, title, type, confidence, demand_likes,
    cluster, model, vn_concept, target_insight, hook, cta, raw_block.
    """
    if not brief_md_path.exists():
        return []

    content = brief_md_path.read_text(encoding="utf-8")

    # Split theo H2 heading "## N. <title>"
    angle_pattern = re.compile(r"^## (\d+)\. (.+?)$", re.MULTILINE)
    matches = list(angle_pattern.finditer(content))

    angles: list[dict] = []
    for i, m in enumerate(matches):
        idx = int(m.group(1))
        title = m.group(2).strip()
        # Block = từ heading này tới heading tiếp theo (hoặc EOF)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block = content[start:end].strip()

        # Extract metadata fields
        type_m = re.search(r"\*\*Type\*\*:\s*(.+?)\s*·", block)
        conf_m = re.search(r"\*\*Confidence\*\*:\s*([\d.]+)", block)
        demand_m = re.search(r"\*\*Demand\*\*:\s*(\d+)\s*likes?", block)
        cluster_m = re.search(r"Cluster:\s*\*\*([^*]+)\*\*", block)
        model_m = re.search(r"Model:\s*`([^`]+)`", block)
        vn_m = re.search(r"VN:\s*\*\*([^*]+)\*\*", block)
        insight_m = re.search(r'\*\*Target insight\*\*:\s*\n>\s*"([^"]+)"', block, re.DOTALL)
        # Hook có thể trên nhiều dòng
        hook_m = re.search(r"\*\*🎣 Hook[^*]*\*\*:?\s*\n>\s*(.+?)(?=\n\n|\*\*)", block, re.DOTALL)
        # Bug 6 fix: dấu ":" có thể nằm SAU `**` close (vd "**🔔 CTA (peer)**:"),
        # không phải bên trong. Cho phép optional ":" + optional "> " (blockquote) sau **.
        cta_m = re.search(
            r"\*\*🔔 CTA[^*]*\*\*:?\s*(?:>\s*)?(.+?)(?=\n\n|\n---|\Z)",
            block, re.DOTALL,
        )

        angles.append({
            "idx": idx,
            "title": title,
            "type": type_m.group(1).strip() if type_m else "?",
            "confidence": float(conf_m.group(1)) if conf_m else 0.0,
            "demand_likes": int(demand_m.group(1)) if demand_m else 0,
            "cluster": cluster_m.group(1).strip() if cluster_m else "",
            "model": model_m.group(1).strip() if model_m else "",
            "vn_concept": vn_m.group(1).strip() if vn_m else "",
            "target_insight": insight_m.group(1).strip()[:200] if insight_m else "",
            "hook": hook_m.group(1).strip()[:300] if hook_m else "",
            "cta": cta_m.group(1).strip()[:200] if cta_m else "",
            "raw_block": block,  # giữ raw để có thể paste full
        })
    return angles


def load_voice_profile(persona_slug: str = "chi-hien") -> dict[str, str]:
    """Load voice profile từ profiles/<slug>/.

    Trả dict {about, voice, write_rules} — empty string nếu file không tồn tại.
    """
    profile_dir = _PROJECT_ROOT / "profiles" / persona_slug
    result = {"about": "", "voice": "", "write_rules": ""}
    if not profile_dir.exists():
        logger.debug("Voice profile not found: %s", profile_dir)
        return result

    file_map = {
        "about": profile_dir / "about.md",
        "voice": profile_dir / "voice_profile.md",
        "write_rules": profile_dir / "write_rules.md",
    }
    for key, path in file_map.items():
        if path.exists():
            try:
                result[key] = path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning("Failed to read %s: %s", path, e)
    return result


def extract_vocab_from_brief(angles: list[dict], top_n: int = 5) -> list[str]:
    """Extract top N từ vocab grounding từ hook nguyên văn của angles.

    Heuristic: tìm cụm trong quotes hoặc emphasized text trong hook.
    Trả về list cụm từ ngắn (≤30 ký tự).
    """
    vocab: list[str] = []
    seen: set[str] = set()
    for a in angles:
        hook = a.get("hook", "")
        # Lấy cụm trong "..." quote nếu có
        quotes = re.findall(r"'([^']{5,30})'", hook) + re.findall(r'"([^"]{5,30})"', hook)
        for q in quotes:
            q_clean = q.strip().lower()
            if q_clean and q_clean not in seen:
                seen.add(q_clean)
                vocab.append(q.strip())
                if len(vocab) >= top_n:
                    return vocab
    return vocab


def generate_cowork_pack(
    selected_angles: list[dict],
    niche_name: str,
    niche_slug: str,
    run_id: str,
    drive_folder_url: str = "",
    platform: str = "Fanpage",
    voice_profile_slug: str = "chi-hien",
    total_comments: int = 0,
) -> str:
    """Render CoWork Brief Pack markdown.

    Args:
        selected_angles: 3-5 angles dict (đã user-selected từ brief)
        niche_name: tên hiển thị niche
        niche_slug: kebab-case
        run_id: vd "2026-05-17_18-20_tuan"
        drive_folder_url: link Drive folder của run (optional)
        platform: "Fanpage" / "TikTok" / "Fanpage + TikTok"
        voice_profile_slug: persona dùng — default chi-hien
        total_comments: tổng cmt nguồn

    Returns: markdown content string (3-5 KB).
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    voice = load_voice_profile(voice_profile_slug)

    L: list[str] = []

    # 1. METADATA
    L.append(f"# CoWork Brief Pack — {run_id}")
    L.append("")
    L.append(f"> **Generated**: {ts}")
    L.append(f"> **Niche**: {niche_name} (`{niche_slug}`)")
    L.append(f"> **Source**: {total_comments} cmt" + (f" · [Drive folder]({drive_folder_url})" if drive_folder_url else ""))
    L.append(f"> **Target platform**: {platform}")
    L.append(f"> **Voice profile**: {voice_profile_slug}")
    L.append(f"> **Số angles đã chọn**: {len(selected_angles)}")
    L.append("")
    L.append("---")
    L.append("")

    # 2. VOICE PROFILE QUICK REF
    L.append("## 🎙 VOICE PROFILE QUICK REFERENCE")
    L.append("")
    if voice.get("voice"):
        # Lấy 1500 chars đầu của voice profile (đủ context, không quá dài)
        voice_excerpt = voice["voice"].strip()
        if len(voice_excerpt) > 1500:
            voice_excerpt = voice_excerpt[:1500].rstrip() + "\n\n_(xem full ở profiles/" + voice_profile_slug + "/voice_profile.md)_"
        L.append(voice_excerpt)
    else:
        L.append("_(Voice profile chưa được setup cho persona này)_")
    L.append("")
    L.append("---")
    L.append("")

    # 3. SELECTED ANGLES
    L.append(f"## 🎯 TOP {len(selected_angles)} ANGLES ĐÃ CHỌN")
    L.append("")
    L.append("_(Cherry-picked từ brief 10 angles — chỉ giữ những angle Hiền viết tuần này)_")
    L.append("")

    for i, angle in enumerate(selected_angles, 1):
        L.append(f"### Angle {i} — {angle.get('title', '?')}")
        L.append("")
        L.append(f"- **Type**: {angle.get('type', '?')}")
        L.append(f"- **Demand**: {angle.get('demand_likes', 0)} likes · Confidence: {angle.get('confidence', 0):.2f}")
        if angle.get("cluster"):
            L.append(f"- **Cluster**: {angle['cluster']}")
        if angle.get("model"):
            L.append(f"- **Mental model**: `{angle['model']}`")
        if angle.get("vn_concept"):
            L.append(f"- **VN concept**: **{angle['vn_concept']}**")
        L.append("")
        if angle.get("target_insight"):
            L.append(f"**Target insight (quote nguyên văn audience)**:")
            L.append(f'> "{angle["target_insight"]}"')
            L.append("")
        if angle.get("hook"):
            L.append(f"**Hook gợi ý**:")
            L.append(f"> {angle['hook']}")
            L.append("")
        if angle.get("cta"):
            L.append(f"**CTA**: {angle['cta']}")
            L.append("")
        L.append("---")
        L.append("")

    # 4. VOCAB GROUNDING
    vocab = extract_vocab_from_brief(selected_angles, top_n=5)
    if vocab:
        L.append("## 📝 VOCAB GROUNDING (BẮT BUỘC dùng nguyên văn ≥1 cụm/bài)")
        L.append("")
        for v in vocab:
            L.append(f'- "{v}"')
        L.append("")
        L.append("---")
        L.append("")

    # 5. ANTI-PATTERN CHECKLIST
    L.append("## ⛔ ANTI-PATTERN CHECKLIST (check trước khi đăng)")
    L.append("")
    for ap in ANTI_PATTERNS_MATURE:
        L.append(f"- [ ] {ap}")
    L.append("")
    L.append("---")
    L.append("")

    # 6. PUBLISH TARGET
    L.append("## 📅 PUBLISH TARGET")
    L.append("")
    if "Fanpage" in platform:
        L.append("- **Fanpage**: caption 800-1200 từ + media (ảnh/video 60-90s)")
        L.append("  - FB Caption Opening: 3-5 dòng mồi (quan trọng hơn hook 3s video)")
    if "TikTok" in platform:
        L.append("- **TikTok**: video 60-90s + caption ngắn 50-150 từ")
        L.append("  - Hook 3s đầu: critical (FYP scroll)")
    L.append("")
    L.append("---")
    L.append("")

    # 7. OUTPUT TEMPLATE (cuối — paste vào CoWork)
    L.append("## 🚀 OUTPUT TEMPLATE (paste cuối brief khi gửi CoWork)")
    L.append("")
    L.append("```")
    L.append("CoWork: dùng VOICE PROFILE + ANGLE [chọn số] + VOCAB GROUNDING.")
    L.append(f"Generate bài viết cho {platform}.")
    L.append("Tuân thủ ANTI-PATTERN CHECKLIST.")
    L.append("")
    L.append("Output JSON:")
    L.append("{")
    L.append('  "title": "...",')
    L.append('  "fb_caption_opening": "5 dòng mồi" (nếu Fanpage),')
    L.append('  "hook_3s_or_10s": "...",')
    L.append('  "body": "...",')
    L.append('  "cta": "peer dialogue, KHÔNG comment-keyword",')
    L.append('  "hashtags": [...],')
    L.append('  "anti_pattern_check": ["passed", "passed", ...]')
    L.append("}")
    L.append("```")
    L.append("")

    # 8. Footer
    L.append("---")
    L.append("")
    L.append(f"**Pack ID**: `cowork-pack_{run_id}` · Generated by Insight Miner Stage C (Refinement)")
    L.append(f"**Trace**: Drive folder → brief.md ({len(selected_angles)}/10 angles chọn) → CoWork Pack này")
    L.append("")

    return "\n".join(L)


def save_cowork_pack(content: str, output_path: Path) -> Path:
    """Save markdown content to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    logger.info("CoWork pack saved → %s (%d chars)", output_path, len(content))
    return output_path
