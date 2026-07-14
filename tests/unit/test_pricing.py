"""Unit tests cho pricing.estimate_cost + estimate_claude_token_cost (Spec 4).

Verify:
- estimate_cost đúng cho 4 mode (scrape TikTok, scrape_fb, scrape_fb_group, paste)
- Toggle with_brief + with_strategy đúng
- Strategy chỉ tính khi with_brief=True (guard)
- estimate_claude_token_cost đúng cho Haiku vs Opus, future-proof cho 4-8, 4-9
"""

from __future__ import annotations

import pytest

from tiktok_insight_miner.pricing import estimate_cost, estimate_claude_token_cost


# --- estimate_cost: mode Apify ---

def test_estimate_cost_paste_mode_no_apify():
    """paste mode → apify = 0, chỉ Haiku classify."""
    cost = estimate_cost(num_comments=100, with_brief=False, mode="paste")
    # 100 * 0.0003 = 0.03
    assert cost == pytest.approx(0.03, abs=1e-6)


def test_estimate_cost_scrape_tiktok():
    """TikTok: $0.001/cmt Apify + $0.0003/cmt Haiku."""
    cost = estimate_cost(num_comments=100, with_brief=False, mode="scrape")
    # 100 * 0.001 + 100 * 0.0003 = 0.13
    assert cost == pytest.approx(0.13, abs=1e-6)


def test_estimate_cost_scrape_fb():
    """FB post: $0.0014/cmt Apify + $0.0003/cmt Haiku."""
    cost = estimate_cost(num_comments=100, with_brief=False, mode="scrape_fb")
    # 100 * 0.0014 + 100 * 0.0003 = 0.17
    assert cost == pytest.approx(0.17, abs=1e-6)


def test_estimate_cost_scrape_fb_group():
    """FB Group approx: $0.001/cmt Apify + $0.0003/cmt Haiku."""
    cost = estimate_cost(num_comments=100, with_brief=False, mode="scrape_fb_group")
    assert cost == pytest.approx(0.13, abs=1e-6)


def test_estimate_cost_unknown_mode_falls_to_paste():
    """Mode string không recognize → apify = 0 (fallback paste)."""
    cost = estimate_cost(num_comments=100, with_brief=False, mode="nonsense")
    assert cost == pytest.approx(0.03, abs=1e-6)


# --- estimate_cost: brief + strategy toggle ---

def test_estimate_cost_with_brief_adds_flat_002():
    """with_brief=True → +$0.02 flat."""
    cost_no_brief = estimate_cost(100, with_brief=False, mode="paste")
    cost_with_brief = estimate_cost(100, with_brief=True, mode="paste")
    assert cost_with_brief - cost_no_brief == pytest.approx(0.02, abs=1e-6)


def test_estimate_cost_with_strategy_adds_flat_007():
    """with_brief=True + with_strategy=True → +$0.07 strategy."""
    cost_brief_only = estimate_cost(100, with_brief=True, mode="paste", with_strategy=False)
    cost_full = estimate_cost(100, with_brief=True, mode="paste", with_strategy=True)
    assert cost_full - cost_brief_only == pytest.approx(0.07, abs=1e-6)


def test_estimate_cost_strategy_ignored_without_brief():
    """with_strategy=True nhưng with_brief=False → strategy KHÔNG cộng."""
    cost = estimate_cost(100, with_brief=False, mode="paste", with_strategy=True)
    # Chỉ Haiku 100 * 0.0003 = 0.03
    assert cost == pytest.approx(0.03, abs=1e-6)


def test_estimate_cost_zero_comments():
    """0 comment → chỉ có flat cost brief/strategy nếu tick."""
    assert estimate_cost(0, with_brief=False, mode="paste") == 0.0
    assert estimate_cost(0, with_brief=True, mode="paste") == pytest.approx(0.02)
    assert estimate_cost(0, with_brief=True, mode="paste", with_strategy=True) == pytest.approx(0.09)


def test_estimate_cost_scale_linear_with_comments():
    """Cost scale linear với num_comments (test 1000 comments)."""
    small = estimate_cost(10, with_brief=False, mode="scrape")
    large = estimate_cost(1000, with_brief=False, mode="scrape")
    # 1000/10 = 100x
    assert large / small == pytest.approx(100.0, rel=1e-6)


# --- estimate_claude_token_cost ---

def test_claude_cost_haiku_45():
    """Haiku 4-5: $1/M input, $5/M output."""
    cost = estimate_claude_token_cost(
        input_tokens=1_000_000, output_tokens=0, model="claude-haiku-4-5",
    )
    assert cost == pytest.approx(1.0, abs=1e-6)

    cost_out = estimate_claude_token_cost(
        input_tokens=0, output_tokens=1_000_000, model="claude-haiku-4-5",
    )
    assert cost_out == pytest.approx(5.0, abs=1e-6)


def test_claude_cost_opus_47():
    """Opus 4-7: $15/M input, $75/M output."""
    cost = estimate_claude_token_cost(
        input_tokens=1_000_000, output_tokens=0, model="claude-opus-4-7",
    )
    assert cost == pytest.approx(15.0, abs=1e-6)

    cost_out = estimate_claude_token_cost(
        input_tokens=0, output_tokens=1_000_000, model="claude-opus-4-7",
    )
    assert cost_out == pytest.approx(75.0, abs=1e-6)


def test_claude_cost_opus_48_future_proof():
    """Opus 4-8 (release tương lai) phải match cùng price bracket."""
    cost = estimate_claude_token_cost(
        input_tokens=100_000, output_tokens=50_000, model="claude-opus-4-8",
    )
    # 100000/1M * 15 + 50000/1M * 75 = 1.5 + 3.75 = 5.25
    assert cost == pytest.approx(5.25, abs=1e-6)


def test_claude_cost_haiku_46_future_proof():
    """Haiku 4-6 (release tương lai) phải match Haiku bracket."""
    cost = estimate_claude_token_cost(100_000, 50_000, "claude-haiku-4-6")
    # 0.1 + 0.25 = 0.35
    assert cost == pytest.approx(0.35, abs=1e-6)


def test_claude_cost_unknown_model_returns_zero():
    """Model không recognize → 0.0 (không raise, để không crash pipeline)."""
    assert estimate_claude_token_cost(1000, 1000, "gpt-5") == 0.0
    assert estimate_claude_token_cost(1000, 1000, "") == 0.0


def test_claude_cost_zero_tokens():
    """0 tokens → 0.0."""
    assert estimate_claude_token_cost(0, 0, "claude-opus-4-7") == 0.0


def test_claude_cost_combined_input_output():
    """Cả input + output tính chính xác."""
    cost = estimate_claude_token_cost(
        input_tokens=10_000, output_tokens=5_000, model="claude-opus-4-7",
    )
    # 10000/1M * 15 + 5000/1M * 75 = 0.15 + 0.375 = 0.525
    assert cost == pytest.approx(0.525, abs=1e-6)
