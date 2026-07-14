"""Cost estimator — Apify + Claude API cost cho pipeline.

Extracted từ webapp.py để test được không cần load Streamlit runtime.
"""

from __future__ import annotations


def estimate_cost(
    num_comments: int,
    with_brief: bool,
    mode: str = "scrape",
    with_strategy: bool = False,
) -> float:
    """Rough estimate USD: Apify + Haiku classify + Opus brief + Opus strategy.

    Apify cost theo mode:
    - "scrape" (TikTok): $0.001/cmt
    - "scrape_fb" (Facebook post): $0.0014/cmt
    - "scrape_fb_group" (FB Group): approx $0.001/cmt (charge per post ceiling)
    - "paste" (manual): $0 (no Apify)

    Claude cost:
    - Haiku classify: $0.0003/cmt
    - Opus brief (Stage 4): $0.02 flat
    - Opus strategy (Stage 5): $0.07 flat (chỉ khi with_brief=True)
    """
    if mode == "scrape":
        apify = num_comments * 0.001
    elif mode == "scrape_fb":
        apify = num_comments * 0.0014
    elif mode == "scrape_fb_group":
        apify = num_comments * 0.001
    else:  # paste hoặc unknown mode
        apify = 0.0

    brief = 0.02 if with_brief else 0.0
    strategy = 0.07 if (with_brief and with_strategy) else 0.0

    return apify + num_comments * 0.0003 + brief + strategy


def estimate_claude_token_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
) -> float:
    """Estimate USD cost cho 1 Claude API call theo token count + model.

    Pricing snapshot 2026-07 (verify tại anthropic.com/pricing):
    - claude-haiku-4-5: $1/M input, $5/M output
    - claude-opus-4-7 / claude-opus-4-8: $15/M input, $75/M output

    Trả 0.0 nếu model không recognized (không raise — avoid crash on new model).
    """
    if model.startswith("claude-haiku-4"):
        in_per_m = 1.0
        out_per_m = 5.0
    elif model.startswith("claude-opus-4"):
        in_per_m = 15.0
        out_per_m = 75.0
    else:
        return 0.0

    return (input_tokens / 1_000_000) * in_per_m + (output_tokens / 1_000_000) * out_per_m
