"""Content Calendar — generate strategic outline calendar (30/60/90 days) cho 1 brand.

Workflow:
  strategy_config + insight_pool (selected_angles.json hoặc classified.json)
    → load + filter (constraints)
    → group by problem_code
    → cho mỗi week: build format pattern, match insight per slot
    → render .md (human) + .json (machine)

Module GENERIC — KHÔNG hardcode brand-specific text. Mọi giọng/text riêng đến từ:
- strategy config (big idea, sub-pillars, constraints)
- niche config (problem definitions, persona)
- brand profile (voice context — chỉ load path, không embed string)

Production-level full text generation = production.py downstream.
"""

from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# --- Constants — generic templates (KHÔNG hardcode brand) ---

FORMAT_TYPES = ("reel_60s", "short_fb_post", "long_fb_post", "educational", "soft_cta")

# Hook pattern picked from docs/writing_methods/hook_methods.md, generic per format
HOOK_PATTERN_BY_FORMAT = {
    "reel_60s":      "Hard Truth",
    "short_fb_post": "Specific Pain",
    "long_fb_post":  "Story-Opening",
    "educational":   "Counter-Belief",
    "soft_cta":      "Inner Question",
}

# Measurement focus per format (theo docs/writing_methods/persuasion_methods.md)
MEASUREMENT_FOCUS_BY_FORMAT = {
    "reel_60s":      "comment + save",
    "short_fb_post": "comment",
    "long_fb_post":  "comment + save + share",
    "educational":   "save + comment",
    "soft_cta":      "comment + inbox",
}


# --- Loaders ---

def load_strategy(path: Path) -> dict[str, Any]:
    """Load + validate strategy config."""
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = (
        "strategy_id", "brand_profile", "niche_config", "period_days",
        "core_big_idea", "weeks", "format_ratio",
        "format_distribution_per_week", "constraints",
    )
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError(f"Strategy config thiếu key: {missing}")

    # Verify format_ratio sums to period_days
    total = sum(cfg["format_ratio"].values())
    if total != cfg["period_days"]:
        raise ValueError(
            f"format_ratio sum ({total}) != period_days ({cfg['period_days']})"
        )

    return cfg


def load_brand_profile(profile_dir: Path) -> dict[str, Any]:
    """Lightweight: chỉ verify exists + return path. KHÔNG load nội dung text vào module."""
    return {
        "path": str(profile_dir),
        "exists": profile_dir.exists(),
        "files_present": (
            sorted(p.name for p in profile_dir.glob("*.md")) if profile_dir.exists() else []
        ),
    }


def detect_input_format(data: list) -> str:
    """Auto-detect: 'selected_angles' hay 'classified' hay 'unknown'."""
    if not data or not isinstance(data, list):
        return "unknown"
    first = data[0]
    if not isinstance(first, dict):
        return "unknown"
    if "quote" in first and "problem_code" in first:
        return "selected_angles"
    if "comment" in first and "bucket" in first:
        return "classified"
    return "unknown"


def load_insight_pool(input_path: Path, niche_config: dict) -> tuple[list[dict], str]:
    """Load insight pool from selected_angles.json (preferred) hoặc classified.json (fallback).

    Returns (normalized_pool, source_format). Each item normalized to:
      {quote, summary, problem_code, score, intent, bucket, source_run}
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fmt = detect_input_format(data)

    if fmt == "selected_angles":
        pool = [
            {
                "quote":        a.get("quote", ""),
                "summary":      a.get("summary", ""),
                "problem_code": a.get("problem_code", "UNCLASSIFIED"),
                "score":        int(a.get("score", 0) or 0),
                "intent":       a.get("intent", ""),
                "bucket":       a.get("bucket", ""),
                "source_run":   a.get("source_run", ""),
                "author":       a.get("author", ""),
                "video_url":    a.get("video_url", ""),
            }
            for a in data
        ]
        return pool, "selected_angles"

    elif fmt == "classified":
        # Lazy import — chỉ cần khi fallback
        from tiktok_insight_miner.classifier import load_classified_json
        from tiktok_insight_miner.insight_bank import build_records

        classified = load_classified_json(input_path)
        records, _stats = build_records(classified, niche_config)
        pool = [
            {
                "quote":        r["quote"],
                "summary":      r["summary"],
                "problem_code": r["problem_code"],
                "score":        int(r["demand_score"]),
                "intent":       r["intent_label"],
                "bucket":       r["bucket"],
                "source_run":   "classified-loaded",
                "author":       r.get("author", ""),
                "video_url":    r.get("video_url", ""),
            }
            for r in records
        ]
        return pool, "classified"

    else:
        raise ValueError(
            f"Không detect được format input — file phải có 'quote'+'problem_code' "
            f"(selected_angles) hoặc 'comment'+'bucket' (classified)"
        )


def load_niche_config(path: Path) -> dict:
    """Reuse loader from insight_bank if path resolvable, else lightweight load."""
    try:
        from tiktok_insight_miner.insight_bank import load_niche_config as _load
        return _load(path)
    except Exception:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


# --- Filtering & grouping ---

def filter_pool_by_constraints(pool: list[dict], constraints: dict) -> list[dict]:
    """Apply banned_problem_groups."""
    banned = set(constraints.get("banned_problem_groups", []))
    if not banned:
        return pool
    return [p for p in pool if p.get("problem_code") not in banned]


def group_pool_by_problem(pool: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for p in pool:
        grouped[p.get("problem_code", "UNCLASSIFIED")].append(p)
    # Sort each group by score desc
    for code in grouped:
        grouped[code].sort(key=lambda x: x.get("score", 0), reverse=True)
    return dict(grouped)


# --- Format distribution per week ---

def get_week_distribution(strategy: dict, week_no: int) -> dict[str, int]:
    """Get format counts cho 1 week (override > default)."""
    dists = strategy["format_distribution_per_week"]
    override_key = f"week_{week_no}_override"
    if override_key in dists:
        return {k: v for k, v in dists[override_key].items() if not k.startswith("_")}
    return {k: v for k, v in dists["default"].items() if not k.startswith("_")}


def build_week_format_pattern(distribution: dict[str, int]) -> list[str]:
    """Generate ordered list of formats cho 1 week.

    Order convention (deterministic, brand-agnostic):
    - Body: round-robin (reel → short_fb → educational) — variety trong tuần
    - Long FB: cuối tuần (D7, D14, D21, D28)
    - Soft CTA: cuối cùng (D29, D30 ở week 4)
    """
    n_reel  = distribution.get("reel_60s", 0)
    n_short = distribution.get("short_fb_post", 0)
    n_edu   = distribution.get("educational", 0)
    n_long  = distribution.get("long_fb_post", 0)
    n_soft  = distribution.get("soft_cta", 0)

    # Body: round-robin reel/short_fb/edu
    body: list[str] = []
    pools = [
        ["reel_60s"] * n_reel,
        ["short_fb_post"] * n_short,
        ["educational"] * n_edu,
    ]
    while any(pools):
        for i in range(len(pools)):
            if pools[i]:
                body.append(pools[i].pop(0))

    # Append long_fb (end of week) + soft_cta (very end)
    return body + ["long_fb_post"] * n_long + ["soft_cta"] * n_soft


# --- Insight matching ---

def match_insights_to_slots(
    pattern: list[str],
    week: dict,
    pool_by_problem: dict[str, list[dict]],
    used_count: dict[str, int],
) -> list[dict]:
    """Pair each format slot với 1 insight.

    Strategy:
    - Cycle through primary_problems → secondary_problems → all problems
    - Pick least-used insight first (spread reuse)
    - If pool empty, return None (will show 'chưa có insight match')

    Modifies used_count in-place (quote → use count).
    """
    primary = week.get("primary_problems", [])
    secondary = week.get("secondary_problems", [])
    fallback_problems = primary + secondary

    matches: list[dict] = []
    problem_idx = 0

    for fmt in pattern:
        # Pick problem (round-robin through primary + secondary)
        chosen_insight = None
        chosen_problem = None

        # Try problems in order, find one with available insight
        for offset in range(len(fallback_problems)):
            problem = fallback_problems[(problem_idx + offset) % len(fallback_problems)]
            candidates = pool_by_problem.get(problem, [])
            if not candidates:
                continue

            # Sort: least-used first, then highest score
            candidates_ranked = sorted(
                candidates,
                key=lambda c: (used_count.get(c["quote"], 0), -c.get("score", 0)),
            )
            chosen_insight = candidates_ranked[0]
            chosen_problem = problem
            break

        # Fallback: try ANY problem in pool (still respect banned filter — already applied earlier)
        if chosen_insight is None:
            all_candidates: list[dict] = []
            for problem_pool in pool_by_problem.values():
                all_candidates.extend(problem_pool)
            if all_candidates:
                all_candidates.sort(
                    key=lambda c: (used_count.get(c["quote"], 0), -c.get("score", 0)),
                )
                chosen_insight = all_candidates[0]
                chosen_problem = chosen_insight.get("problem_code", "UNCLASSIFIED")

        if chosen_insight is not None:
            used_count[chosen_insight["quote"]] = used_count.get(chosen_insight["quote"], 0) + 1

        matches.append({
            "format": fmt,
            "insight": chosen_insight,
            "problem_used": chosen_problem or "UNCLASSIFIED",
        })

        problem_idx += 1

    return matches


# --- Generic templates (KHÔNG hardcode brand-specific text) ---

def _truncate(s: str, n: int) -> str:
    if not s:
        return ""
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def generate_working_title(week: dict, insight: dict | None, fmt: str) -> str:
    """Generic title — pillar/sub_big_idea + insight summary."""
    if not insight:
        return f"[{week['pillar']}] (chưa có insight match)"

    summary = insight.get("summary", "") or insight.get("quote", "")[:60]
    if fmt == "long_fb_post":
        return f"{week['sub_big_idea']}"
    if fmt == "soft_cta":
        return f"Mở cuộc trò chuyện: {_truncate(summary, 60)}"
    if fmt == "educational":
        return f"3 góc nhìn về: {_truncate(summary, 60)}"
    return _truncate(summary, 80)


def generate_hook_direction(insight: dict | None, fmt: str) -> str:
    """Pick hook pattern + cite quote anchor."""
    pattern = HOOK_PATTERN_BY_FORMAT.get(fmt, "Hard Truth")
    if not insight:
        return f"{pattern}: (chưa có quote)"
    quote = insight.get("quote", "")
    return f'{pattern}: "{_truncate(quote, 100)}"'


def generate_big_idea(week: dict, insight: dict | None) -> str:
    """Combine sub_big_idea (week) + insight summary."""
    sub = week.get("sub_big_idea", "")
    if not insight:
        return sub
    summary = insight.get("summary", "")
    return f"{sub} — {_truncate(summary, 80)}"


def generate_main_point(insight: dict | None, problem_def: dict | None) -> str:
    """Generic: insight summary + 1 frame (no brand-specific phrase)."""
    if not insight:
        return "Chưa có insight cụ thể — cần tick thêm trong 3-lựa-chọn.md hoặc fallback từ classified.json."
    summary = insight.get("summary", "")
    problem_name = problem_def.get("name_vi", insight.get("problem_code", "?")) if problem_def else "?"
    return f"Insight: {summary}. Khung: dạng {problem_name}. Action gợi ý: 1 việc nhỏ liên quan có thể làm hôm nay."


def generate_cta(insight: dict | None, fmt: str) -> str:
    """Generic CTA template — question form, no brand signature."""
    if fmt == "soft_cta":
        return "Bài này có chạm bạn không? Comment 1 từ — mình muốn biết bạn đang ở đó."
    if fmt == "educational":
        return "Bạn áp dụng được cái nào trong này? Comment số."
    if not insight:
        return "Comment để mình biết bạn nghĩ gì."
    summary = insight.get("summary", "")
    return f"Với bạn — {_truncate(summary, 60)}? Comment để mình biết."


def generate_angle_label(week: dict, insight: dict | None) -> str:
    """Short angle label combining pillar focus + insight summary."""
    sub = week.get("sub_big_idea", "")
    if not insight:
        return sub
    return f"{sub} · {_truncate(insight.get('summary', ''), 50)}"


# --- Day entry builder ---

def build_day_entry(
    day_num: int,
    week: dict,
    slot_match: dict,
    awareness_stage: str,
    niche_config: dict,
) -> dict:
    """Build 1 day entry với 14 fields theo spec."""
    insight = slot_match["insight"]
    fmt = slot_match["format"]
    problem_code = slot_match["problem_used"]

    problem_def = next(
        (p for p in niche_config.get("main_problems", []) if p["code"] == problem_code),
        None,
    )

    return {
        "day": day_num,
        "awareness_stage": awareness_stage,
        "content_pillar": week["pillar"],
        "problem_group": problem_code,
        "insight_source": {
            "quote":      insight.get("quote", "") if insight else "",
            "summary":    insight.get("summary", "") if insight else "",
            "score":      insight.get("score") if insight else None,
            "round":      insight.get("source_run") if insight else None,
            "intent":     insight.get("intent") if insight else None,
            "bucket":     insight.get("bucket") if insight else None,
        },
        "angle":              generate_angle_label(week, insight),
        "format":             fmt,
        "working_title":      generate_working_title(week, insight, fmt),
        "hook_direction":     generate_hook_direction(insight, fmt),
        "big_idea":           generate_big_idea(week, insight),
        "main_point":         generate_main_point(insight, problem_def),
        "cta":                generate_cta(insight, fmt),
        "measurement_focus":  MEASUREMENT_FOCUS_BY_FORMAT.get(fmt, "comment"),
        "production_status":  "idea",
    }


# --- Writers ---

def render_day_md(day: dict) -> list[str]:
    L = [f"### D{day['day']} — {day['format']}"]
    L.append(f"- **Awareness**: `{day['awareness_stage']}`")
    L.append(f"- **Pillar**: {day['content_pillar']}")
    L.append(f"- **Problem group**: `{day['problem_group']}`")
    quote = day["insight_source"].get("quote", "")
    if quote:
        L.append(f'- **Insight source**: "{_truncate(quote, 120)}"')
        meta = day["insight_source"]
        meta_parts = []
        if meta.get("score") is not None:
            meta_parts.append(f"score={meta['score']}")
        if meta.get("round"):
            meta_parts.append(f"from={meta['round']}")
        if meta.get("intent"):
            meta_parts.append(f"intent={meta['intent']}")
        if meta_parts:
            L.append(f"  · _{' · '.join(meta_parts)}_")
    else:
        L.append("- **Insight source**: _(chưa có)_")
    L.append(f"- **Angle**: {day['angle']}")
    L.append(f"- **Working title**: {day['working_title']}")
    L.append(f"- **Hook direction**: {day['hook_direction']}")
    L.append(f"- **Big idea**: {day['big_idea']}")
    L.append(f"- **Main point**: {day['main_point']}")
    L.append(f"- **CTA**: {day['cta']}")
    L.append(f"- **Measurement focus**: {day['measurement_focus']}")
    L.append(f"- **Production status**: `{day['production_status']}`")
    return L


def write_calendar_md(
    days: list[dict],
    strategy: dict,
    brand_context: dict,
    pool_meta: dict,
    output_path: Path,
) -> None:
    L: list[str] = []
    L.append(f"# 📅 Content Calendar — {strategy.get('strategy_name', strategy['strategy_id'])}")
    L.append("")
    L.append(f"> **Generated by**: `tim calendar` module (v1) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L.append(f"> **Strategy**: `{strategy['strategy_id']}`")
    L.append(f"> **Brand profile**: `{strategy['brand_profile']}` (exists={brand_context.get('exists', False)})")
    L.append(f"> **Niche config**: `{strategy['niche_config']}`")
    L.append(f"> **Insight source**: `{pool_meta['source_format']}` — {pool_meta['pool_size']} insights (after filter banned: {pool_meta['kept_after_filter']})")
    L.append("")
    L.append(f"## 🎯 Big idea cốt lõi {strategy['period_days']} ngày")
    L.append("")
    L.append(f"> {strategy['core_big_idea']}")
    L.append("")
    L.append("---")
    L.append("")

    # Days grouped by week
    days_by_week: dict[int, list[dict]] = defaultdict(list)
    for d in days:
        # Find week_no from days range
        for w in strategy["weeks"]:
            if w["days"][0] <= d["day"] <= w["days"][1]:
                days_by_week[w["week_no"]].append(d)
                break

    for week in strategy["weeks"]:
        wn = week["week_no"]
        L.append(f"## Tuần {wn} — {week['pillar']} (D{week['days'][0]}–D{week['days'][1]})")
        L.append("")
        L.append(f"> **Mục tiêu**: {week['goal']}")
        L.append(f"> **Sub big idea**: {week['sub_big_idea']}")
        L.append(f"> **Awareness**: `{week.get('default_awareness', 'AWARE')}`")
        L.append(f"> **Primary problems**: {', '.join(week['primary_problems'])}")
        if week.get("secondary_problems"):
            L.append(f"> **Secondary problems**: {', '.join(week['secondary_problems'])}")
        L.append("")

        for d in sorted(days_by_week[wn], key=lambda x: x["day"]):
            L.extend(render_day_md(d))
            L.append("")

        L.append("---")
        L.append("")

    # Stats
    L.append("## 📊 Stats")
    L.append("")
    fmt_counts = Counter(d["format"] for d in days)
    L.append("**Format distribution**:")
    L.append("")
    L.append("| Format | Count | Spec | Match |")
    L.append("|---|---:|---:|---|")
    for fmt in FORMAT_TYPES:
        actual = fmt_counts.get(fmt, 0)
        spec = strategy["format_ratio"].get(fmt, 0)
        ok = "✅" if actual == spec else "❌"
        L.append(f"| {fmt} | {actual} | {spec} | {ok} |")
    L.append("")

    problem_counts = Counter(d["problem_group"] for d in days)
    L.append("**Problem distribution**:")
    L.append("")
    L.append("| Problem group | Count |")
    L.append("|---|---:|")
    for prob, cnt in sorted(problem_counts.items(), key=lambda x: -x[1]):
        L.append(f"| `{prob}` | {cnt} |")
    L.append("")

    # Insight reuse
    quote_counts = Counter(
        d["insight_source"]["quote"] for d in days if d["insight_source"]["quote"]
    )
    n_unique = len(quote_counts)
    L.append("**Insight reuse**:")
    L.append("")
    L.append(f"- Total unique quotes: **{n_unique}** / {len(days)} days")
    if n_unique > 0:
        avg = len(days) / n_unique
        L.append(f"- Average reuse per quote: **{avg:.1f}x**")
    if n_unique < len(days):
        L.append("")
        L.append("> ⚠️ **Pool nhỏ — diversity thấp**. Để tăng diversity:")
        L.append("> - Tick thêm angles trong `3-lựa-chọn.md` (round 1/2/3) → re-run `tim select`")
        L.append("> - HOẶC pass `classified.json` thay vì `selected_angles.json` qua `-i`")
    L.append("")

    # Constraints check
    L.append("## ✅ Constraints check")
    L.append("")
    banned = strategy["constraints"].get("banned_problem_groups", [])
    if banned:
        violations = sum(1 for d in days if d["problem_group"] in banned)
        L.append(f"- Banned problem groups: `{', '.join(banned)}` — violations: **{violations}** {'✅' if violations == 0 else '❌'}")
    L.append("")

    output_path.write_text("\n".join(L), encoding="utf-8")
    logger.info("Wrote %s", output_path)


def write_calendar_json(
    days: list[dict],
    strategy: dict,
    pool_meta: dict,
    output_path: Path,
) -> None:
    fmt_counts = Counter(d["format"] for d in days)
    problem_counts = Counter(d["problem_group"] for d in days)
    quote_counts = Counter(
        d["insight_source"]["quote"] for d in days if d["insight_source"]["quote"]
    )

    output = {
        "strategy_id":       strategy["strategy_id"],
        "strategy_name":     strategy.get("strategy_name", ""),
        "brand_profile":     strategy["brand_profile"],
        "niche_config":      strategy["niche_config"],
        "generated_at":      datetime.now().isoformat(timespec="seconds"),
        "period_days":       strategy["period_days"],
        "core_big_idea":     strategy["core_big_idea"],
        "input_format":      pool_meta["source_format"],
        "pool_size_total":   pool_meta["pool_size"],
        "pool_size_kept":    pool_meta["kept_after_filter"],
        "days":              days,
        "stats": {
            "total_days":        len(days),
            "format_counts":     dict(fmt_counts),
            "problem_counts":    dict(problem_counts),
            "unique_insights":   len(quote_counts),
            "average_reuse":     round(len(days) / max(len(quote_counts), 1), 2),
        },
    }
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Wrote %s", output_path)


# --- Backup helper ---

def backup_existing_md(md_path: Path) -> Path | None:
    """Rename existing .md to *-MANUAL-BACKUP.md before overwrite. Idempotent."""
    if not md_path.exists():
        return None
    backup_path = md_path.parent / f"{md_path.stem}-MANUAL-BACKUP.md"
    if backup_path.exists():
        # Already backed up before — don't overwrite backup
        logger.info("Backup already exists at %s — current .md will be overwritten", backup_path)
        return backup_path
    md_path.rename(backup_path)
    logger.info("Backed up %s → %s", md_path.name, backup_path.name)
    return backup_path


# --- Path resolution ---

def resolve_project_root(strategy_path: Path) -> Path:
    """Strategy file is in <root>/strategy_configs/. Return <root>."""
    parent = strategy_path.parent
    if parent.name == "strategy_configs":
        return parent.parent
    return Path.cwd()


# --- Entry point ---

def build_calendar(
    strategy_path: Path,
    input_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """All-in-one: load → match → render. Returns stats."""
    strategy = load_strategy(strategy_path)
    project_root = resolve_project_root(strategy_path)

    # Resolve dependent paths
    niche_path = project_root / strategy["niche_config"]
    brand_dir = project_root / strategy["brand_profile"]

    if not niche_path.exists():
        raise FileNotFoundError(f"niche_config không tồn tại: {niche_path}")

    niche_config = load_niche_config(niche_path)
    brand_context = load_brand_profile(brand_dir)

    # Load pool
    pool_total, source_format = load_insight_pool(input_path, niche_config)
    pool_kept = filter_pool_by_constraints(pool_total, strategy["constraints"])
    pool_by_problem = group_pool_by_problem(pool_kept)

    pool_meta = {
        "source_format":     source_format,
        "pool_size":         len(pool_total),
        "kept_after_filter": len(pool_kept),
        "banned_filtered":   len(pool_total) - len(pool_kept),
    }

    # Generate days week by week
    days: list[dict] = []
    used_count: dict[str, int] = {}

    for week in strategy["weeks"]:
        wn = week["week_no"]
        n_days = week["days"][1] - week["days"][0] + 1
        dist = get_week_distribution(strategy, wn)
        n_dist = sum(dist.values())
        if n_dist != n_days:
            raise ValueError(
                f"Week {wn}: distribution sum ({n_dist}) != days ({n_days})"
            )

        pattern = build_week_format_pattern(dist)
        matches = match_insights_to_slots(pattern, week, pool_by_problem, used_count)

        awareness = week.get("default_awareness", "AWARE")
        for i, match in enumerate(matches):
            day_num = week["days"][0] + i
            entry = build_day_entry(day_num, week, match, awareness, niche_config)
            days.append(entry)

    # Resolve output paths
    base = strategy.get(
        "output_filename_base",
        f"content-calendar-{strategy['period_days']}-days-{strategy['strategy_id']}",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{base}.md"
    json_path = output_dir / f"{base}.json"

    # Backup existing .md before overwrite
    backup_path = backup_existing_md(md_path)

    # Write
    write_calendar_md(days, strategy, brand_context, pool_meta, md_path)
    write_calendar_json(days, strategy, pool_meta, json_path)

    # Stats
    fmt_counts = Counter(d["format"] for d in days)
    problem_counts = Counter(d["problem_group"] for d in days)
    quote_counts = Counter(
        d["insight_source"]["quote"] for d in days if d["insight_source"]["quote"]
    )

    return {
        "strategy_id":      strategy["strategy_id"],
        "md_path":          md_path,
        "json_path":        json_path,
        "backup_path":      backup_path,
        "days_count":       len(days),
        "format_counts":    dict(fmt_counts),
        "problem_counts":   dict(problem_counts),
        "unique_insights":  len(quote_counts),
        "pool_size":        pool_meta["pool_size"],
        "pool_kept":        pool_meta["kept_after_filter"],
        "source_format":    source_format,
    }
