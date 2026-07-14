"""Unit tests cho cowork_pack.parse_brief_angles (Spec 3 của T4).

Regex phải bắt CTA + Hook đúng cho:
- Format chuẩn suggester: `**🔔 CTA:** text` (dấu : trong **)
- Format mature/peer: `**🔔 CTA (peer)**: text` (dấu : sau ** close) — Bug 6 fixed
- CTA multi-line (kết thúc bởi \\n\\n hoặc ---)
- Hook multi-line trong blockquote
- File không tồn tại → return []
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tiktok_insight_miner.cowork_pack import parse_brief_angles


BRIEF_STANDARD = """# 🎬 Content Angle Brief

**Total angles**: 2

---

## 1. Angle tiêu đề đầu tiên

**Type**: 🎯 Desire Fulfillment  ·  **Confidence**: 0.85  ·  **Demand**: 42 likes

**🧠 Psychology**: Cluster: **Procrastination Trap** · Model: `bj_fogg`

**Target insight**:
> "quote nguyên văn của comment gốc"

**🎣 Hook (3s đầu):**
> Đây là hook 1 dòng chào audience đầu tiên.

**📝 Script outline:**
1. beat 1
2. beat 2

**🔔 CTA:** Comment X để nhận Y trong 24h.

---

## 2. Angle thứ hai với CTA format khác

**Type**: 💊 Pain Solution  ·  **Confidence**: 0.90  ·  **Demand**: 100 likes

**🧠 Psychology**: Cluster: **Macro Despair** · Model: `peak_end` · VN: **Face / Thể diện**

**Target insight**:
> "quote thứ hai"

**🎣 Hook (10s đầu):**
> Hook thứ hai có thể dài hơn
> và trên nhiều dòng blockquote.

**📝 Script outline:**
1. beat A

**🔔 CTA (peer)**: > Comment 'giờ rảnh của chị' để mình phản hồi.

---
"""


BRIEF_EMPTY = """# Empty Brief

No angles here.
"""


@pytest.fixture
def brief_standard_path(tmp_path: Path) -> Path:
    p = tmp_path / "brief.md"
    p.write_text(BRIEF_STANDARD, encoding="utf-8")
    return p


@pytest.fixture
def brief_empty_path(tmp_path: Path) -> Path:
    p = tmp_path / "brief_empty.md"
    p.write_text(BRIEF_EMPTY, encoding="utf-8")
    return p


def test_parse_returns_list_of_dicts(brief_standard_path):
    angles = parse_brief_angles(brief_standard_path)
    assert isinstance(angles, list)
    assert len(angles) == 2
    assert all(isinstance(a, dict) for a in angles)


def test_parse_extracts_titles_and_indices(brief_standard_path):
    angles = parse_brief_angles(brief_standard_path)
    assert angles[0]["idx"] == 1
    assert angles[0]["title"] == "Angle tiêu đề đầu tiên"
    assert angles[1]["idx"] == 2
    assert "CTA format khác" in angles[1]["title"]


def test_parse_extracts_type_confidence_demand(brief_standard_path):
    angles = parse_brief_angles(brief_standard_path)
    assert "Desire Fulfillment" in angles[0]["type"]
    assert angles[0]["confidence"] == 0.85
    assert angles[0]["demand_likes"] == 42
    assert angles[1]["confidence"] == 0.90
    assert angles[1]["demand_likes"] == 100


def test_parse_extracts_psychology_layer(brief_standard_path):
    angles = parse_brief_angles(brief_standard_path)
    assert angles[0]["cluster"] == "Procrastination Trap"
    assert angles[0]["model"] == "bj_fogg"
    assert angles[1]["cluster"] == "Macro Despair"
    assert angles[1]["vn_concept"] == "Face / Thể diện"


def test_parse_extracts_hook_single_line(brief_standard_path):
    """Hook 1 dòng blockquote — regex phải bắt content sau `> `."""
    angles = parse_brief_angles(brief_standard_path)
    hook_1 = angles[0]["hook"]
    assert "hook 1 dòng chào audience" in hook_1


def test_parse_extracts_cta_dot_inside_stars(brief_standard_path):
    """Format chuẩn `**🔔 CTA:** text` — dấu : NẰM TRONG **."""
    angles = parse_brief_angles(brief_standard_path)
    cta_1 = angles[0]["cta"]
    assert "Comment X để nhận Y" in cta_1


def test_parse_extracts_cta_dot_after_stars_bug6_fix(brief_standard_path):
    """BUG 6 REGRESSION TEST: format `**🔔 CTA (peer)**: text`
    — dấu : NẰM SAU ** close. Regex trước bị bug capture nhầm.
    """
    angles = parse_brief_angles(brief_standard_path)
    cta_2 = angles[1]["cta"]
    # CTA phải chứa content thật, KHÔNG start với ":" hoặc ">"
    assert "Comment" in cta_2 or "phản hồi" in cta_2
    # Không được chứa prefix ":" hoặc "> " sót lại
    assert not cta_2.startswith(":")
    assert not cta_2.startswith(">")


def test_parse_extracts_target_insight_quoted(brief_standard_path):
    angles = parse_brief_angles(brief_standard_path)
    assert angles[0]["target_insight"] == "quote nguyên văn của comment gốc"
    assert angles[1]["target_insight"] == "quote thứ hai"


def test_parse_preserves_raw_block(brief_standard_path):
    """raw_block phải giữ full text của angle để có thể paste lại."""
    angles = parse_brief_angles(brief_standard_path)
    assert "## 1. Angle tiêu đề đầu tiên" in angles[0]["raw_block"]
    assert "Script outline" in angles[0]["raw_block"]


def test_parse_empty_brief_returns_empty_list(brief_empty_path):
    """Brief không có angle nào (không có `## N.` heading) → []."""
    angles = parse_brief_angles(brief_empty_path)
    assert angles == []


def test_parse_nonexistent_file_returns_empty(tmp_path):
    """File không tồn tại → return [] (không raise)."""
    assert parse_brief_angles(tmp_path / "nope.md") == []


def test_parse_missing_optional_fields_default_values(tmp_path):
    """Angle thiếu field optional (vd không có Psychology) → default: '' hoặc 0.0."""
    minimal = """## 1. Just a title

Some text without expected fields.
"""
    p = tmp_path / "min.md"
    p.write_text(minimal, encoding="utf-8")
    angles = parse_brief_angles(p)
    assert len(angles) == 1
    assert angles[0]["title"] == "Just a title"
    assert angles[0]["confidence"] == 0.0
    assert angles[0]["demand_likes"] == 0
    assert angles[0]["type"] == "?"
    assert angles[0]["cluster"] == ""
    assert angles[0]["hook"] == ""
    assert angles[0]["cta"] == ""
