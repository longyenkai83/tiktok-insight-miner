"""Insight Bank — biến classified.json + niche_config.json thành 3 file output:

  1-liệt-kê.csv     (Liệt kê — Excel-friendly, mọi insight actionable)
  2-sắp-xếp.md      (Sắp xếp — group theo 9 nhóm, sort theo demand_score)
  3-lựa-chọn.md     (Lựa chọn — top 30 candidates, checkbox để anh tick)

KHÔNG hardcode taxonomy: mọi main_problem/keywords/scoring đều đọc từ niche_config.json.
KHÔNG gọi Claude — toàn bộ là rule-based để cheap, deterministic, dễ debug.

Bước 4-thực-thi/ sẽ làm ở module riêng (production.py).
"""

from __future__ import annotations

import csv
import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from tiktok_insight_miner.classifier import load_classified_json
from tiktok_insight_miner.models import ClassifiedComment

logger = logging.getLogger(__name__)

# Buckets nào được giữ lại làm insight actionable
ACTIONABLE_BUCKETS = ("pain", "desire", "question", "objection")

# Sentinel khi không match nhóm nào trong config
UNCLASSIFIED_PROBLEM = "UNCLASSIFIED"


# --- Config loader ---

def load_niche_config(path: Path) -> dict[str, Any]:
    """Load niche config JSON, validate cấu trúc tối thiểu."""
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required_top = ("niche_slug", "main_problems", "scoring_rules", "output_files")
    missing = [k for k in required_top if k not in cfg]
    if missing:
        raise ValueError(f"Niche config thiếu key: {missing}")

    if not isinstance(cfg["main_problems"], list) or not cfg["main_problems"]:
        raise ValueError("main_problems phải là list non-empty")

    return cfg


# --- Heuristics: problem matching ---

def _normalize(text: str) -> str:
    """Lowercase + strip dấu cách thừa. Không bỏ dấu tiếng Việt (keyword config có dấu)."""
    return re.sub(r"\s+", " ", text.lower()).strip()


class ProblemClassifier:
    """Match insight (text + summary) vào 1 trong 9 problem dựa trên keyword overlap.

    Tie-break: problem nào có problem_priority_bonus cao hơn thắng.
    Nếu 0 keyword match → trả UNCLASSIFIED.
    """

    def __init__(self, problems: list[dict], priority_bonus: dict[str, int]):
        self.problems = problems
        self.priority_bonus = priority_bonus
        # Pre-lowercase keywords mỗi problem
        self._keywords_by_code = {
            p["code"]: [_normalize(kw) for kw in p.get("keywords", [])]
            for p in problems
        }

    def classify(self, text: str, summary: str) -> tuple[str, int]:
        """Trả (problem_code, num_keyword_hits)."""
        blob = _normalize(f"{text} {summary}")
        hits_per_problem: dict[str, int] = {}
        for code, kws in self._keywords_by_code.items():
            hits = sum(1 for kw in kws if kw in blob)
            if hits > 0:
                hits_per_problem[code] = hits

        if not hits_per_problem:
            return UNCLASSIFIED_PROBLEM, 0

        # Sort: hits desc, then priority_bonus desc
        best = max(
            hits_per_problem.items(),
            key=lambda kv: (kv[1], self.priority_bonus.get(kv[0], 0)),
        )
        return best[0], best[1]


# --- Heuristics: intent detection ---

# (intent_code, list of patterns — substring match trong text đã lowercase)
INTENT_PATTERNS: list[tuple[str, list[str]]] = [
    ("TAG_FRIEND", ["@"]),
    ("SEEK_HOWTO", [
        "làm sao", "làm thế nào", "cách nào", "cách làm", "công thức",
        "bước nào", "bắt đầu từ đâu", "xin chỉ", "chỉ em với", "chỉ mình với",
        "how to", "hướng dẫn", "có ai biết",
    ]),
    ("SEEK_RECOMMENDATION", [
        "có khóa nào", "có sách nào", "cuốn sách nào", "tool gì", "tool nào",
        "app nào", "ai biết khóa", "có ai khóa", "review giúp", "khóa học nào",
        "sản phẩm nào", "shop nào", "page nào",
    ]),
    ("SEEK_VALIDATION", [
        "có ai như mình", "có ai giống", "mình cũng vậy", "em cũng vậy",
        "ai cũng", "có phải mình", "có ai cùng", "chỉ mình mình",
        "không một mình", "mọi người có",
    ]),
    ("DISAGREE", [
        "không đúng", "không phải vậy", "sai rồi", "theo em thì",
        "thực ra", "thật ra không", "không phải đâu", "mình không nghĩ vậy",
        "không hẳn", "ngược lại",
    ]),
    ("SHARE_EXPERIENCE", [
        "mình từng", "em từng", "tôi từng", "trước đây mình", "trước đây em",
        "mình đã", "em đã trải qua", "mình đang", "câu chuyện của em",
        "mình kể", "5 năm trước", "10 năm trước",
    ]),
    ("PRAISE_KOL", [
        "chị nói hay", "chị nói chuẩn", "video hay quá", "yêu chị",
        "chị xinh", "thích chị", "follow chị", "biết ơn chị",
    ]),
]


def detect_intent(text: str) -> str:
    """Trả intent_code đầu tiên match. Mặc định 'VENT' (trút bầu tâm sự)."""
    blob = text.lower()
    for code, patterns in INTENT_PATTERNS:
        if any(p in blob for p in patterns):
            return code
    return "VENT"


# --- Heuristics: opportunity label ---

def derive_opportunity(bucket: str, intent: str, likes: int, text_len: int) -> str:
    """Map (bucket, intent, signals) → 1 trong 6 opportunity label.

    Rule đơn giản, dễ tune. Không cần Claude.
    """
    # Quote ngắn + likes cao → hook quote
    if likes >= 10 and text_len <= 80:
        return "HOOK_QUOTE"

    if bucket == "question":
        return "FAQ_ANSWER"

    if bucket == "objection":
        return "MYTH_BUST"

    if intent == "SHARE_EXPERIENCE":
        return "SOCIAL_PROOF"

    if intent == "SEEK_HOWTO":
        return "FRAMEWORK"

    if bucket == "pain":
        return "PAIN_SOLUTION"

    if bucket == "desire":
        return "FRAMEWORK"  # desire thường cần explain "3 bước để..."

    return "PAIN_SOLUTION"  # fallback


# --- Scoring ---

class DemandScorer:
    """Apply scoring formula từ niche_config.scoring_rules."""

    def __init__(self, scoring_rules: dict):
        weights = scoring_rules.get("weights", {})
        self.w_likes = float(weights.get("w_likes", 1.0))
        self.w_replies = float(weights.get("w_replies", 3.0))
        self.bucket_bonus = scoring_rules.get("bucket_bonus", {})
        self.problem_bonus = scoring_rules.get("problem_priority_bonus", {})
        self.intent_bonus = scoring_rules.get("intent_bonus", {})

    def score(
        self, likes: int, replies: int, bucket: str, problem_code: str, intent: str,
    ) -> int:
        base = likes * self.w_likes + replies * self.w_replies
        base += self.bucket_bonus.get(bucket, 0)
        base += self.problem_bonus.get(problem_code, self.problem_bonus.get("_unmatched", 0))
        base += self.intent_bonus.get(intent, 0)
        return int(round(base))


# --- Record builder ---

def _truncate(s: str, n: int = 280) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def build_records(
    classified: list[ClassifiedComment],
    config: dict,
) -> tuple[list[dict], dict[str, int]]:
    """Process classified comments → list of dict records (1 record / insight giữ lại).

    Trả về (records, stats) — stats có keys: total, kept, skipped_bucket, skipped_short.
    Records đã sort theo demand_score desc.
    """
    problems = config["main_problems"]
    priority_bonus = config["scoring_rules"].get("problem_priority_bonus", {})
    classifier = ProblemClassifier(problems, priority_bonus)
    scorer = DemandScorer(config["scoring_rules"])

    stats = {"total": len(classified), "kept": 0, "skipped_bucket": 0, "skipped_short": 0}
    records: list[dict] = []

    # Counter để gán id sequential theo bucket
    bucket_idx: dict[str, int] = defaultdict(int)

    for c in classified:
        if c.bucket not in ACTIONABLE_BUCKETS:
            stats["skipped_bucket"] += 1
            continue

        text = (c.comment.text or "").strip()
        if len(text) < 5:
            stats["skipped_short"] += 1
            continue

        problem_code, _hits = classifier.classify(text, c.summary or "")
        intent = detect_intent(text)
        opportunity = derive_opportunity(c.bucket, intent, c.comment.likes, len(text))
        score = scorer.score(
            likes=c.comment.likes,
            replies=c.comment.reply_count,
            bucket=c.bucket,
            problem_code=problem_code,
            intent=intent,
        )

        bucket_idx[c.bucket] += 1
        rec_id = f"{c.bucket[0].upper()}{bucket_idx[c.bucket]:03d}"

        records.append({
            "id": rec_id,
            "problem_code": problem_code,
            "bucket": c.bucket,
            "intent_label": intent,
            "opportunity_label": opportunity,
            "demand_score": score,
            "likes": c.comment.likes,
            "replies": c.comment.reply_count,
            "author": c.comment.author or "anon",
            "quote": text,
            "summary": c.summary or "",
            "video_url": c.comment.video_url or "",
            "status": "todo",
        })

    records.sort(key=lambda r: r["demand_score"], reverse=True)
    stats["kept"] = len(records)
    return records, stats


# --- Writers ---

def _slugify_anchor(s: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", s.lower())
    return re.sub(r"-+", "-", s).strip("-")


def write_csv(records: list[dict], path: Path, columns: list[str]) -> None:
    """Ghi 1-liệt-kê.csv. utf-8-sig để Excel mở đúng tiếng Việt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    logger.info("Wrote %s (%d rows)", path, len(records))


def write_sap_xep_md(
    records: list[dict],
    config: dict,
    path: Path,
    top_n_overall: int = 10,
) -> None:
    """Ghi 2-sắp-xếp.md."""
    problems = config["main_problems"]
    problem_meta = {p["code"]: p for p in problems}

    # Group records by problem
    by_problem: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_problem[r["problem_code"]].append(r)
    for code in by_problem:
        by_problem[code].sort(key=lambda r: r["demand_score"], reverse=True)

    L: list[str] = []
    L.append(f"# 🗂 Sắp xếp insight — {config.get('niche_name', config['niche_slug'])}")
    L.append("")
    L.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append(f"**Total insights kept**: {len(records)}")
    L.append(f"**Niche config**: `{config['niche_slug']}` (v{config.get('$schema_version', '?')})")
    L.append("")
    L.append("> 4 bước: **Liệt kê** → **Sắp xếp** ✅ (file này) → **Lựa chọn** → **Thực thi**")
    L.append("")

    # --- Tổng quan theo nhóm ---
    L.append("## 📊 Tổng quan 9 nhóm")
    L.append("")
    L.append("| # | Nhóm | Insights | Σ demand_score | Top likes |")
    L.append("|---:|---|---:|---:|---:|")

    # Sort nhóm theo total demand_score desc
    problem_totals = []
    for p in problems:
        items = by_problem.get(p["code"], [])
        total_score = sum(r["demand_score"] for r in items)
        top_likes = items[0]["likes"] if items else 0
        problem_totals.append((p["code"], p["name_vi"], len(items), total_score, top_likes))
    problem_totals.sort(key=lambda x: x[3], reverse=True)

    for idx, (code, name, n, total, top_likes) in enumerate(problem_totals, 1):
        L.append(f"| {idx} | **{name}** (`{code}`) | {n} | {total} | {top_likes} |")

    # Unclassified (nếu có)
    unclassified = by_problem.get(UNCLASSIFIED_PROBLEM, [])
    if unclassified:
        total_un = sum(r["demand_score"] for r in unclassified)
        L.append(f"| — | _UNCLASSIFIED_ | {len(unclassified)} | {total_un} | — |")
        L.append("")
        L.append(
            f"> ⚠️ Có **{len(unclassified)} insight** không match keyword nào trong 9 nhóm. "
            "Có thể cần bổ sung keyword vào niche_config.json — xem section cuối."
        )
    L.append("")

    # --- Top 10 cross-niche ---
    L.append(f"## 🔥 Top {top_n_overall} cross-niche (sort thuần demand_score)")
    L.append("")
    for i, r in enumerate(records[:top_n_overall], 1):
        problem_name = problem_meta.get(r["problem_code"], {}).get("name_vi", r["problem_code"])
        L.append(
            f"**{i}.** `[SCORE {r['demand_score']}]` `[{r['bucket']}]` `[{r['intent_label']}]` "
            f"`[{r['opportunity_label']}]` · **{problem_name}** · @{r['author']} ({r['likes']} likes)"
        )
        L.append(f"> \"{_truncate(r['quote'], 220)}\"")
        if r["summary"]:
            L.append(f"💡 {r['summary']}")
        L.append("")

    # --- Chi tiết từng nhóm ---
    L.append("---")
    L.append("")
    L.append("## 📁 Chi tiết từng nhóm")
    L.append("")

    for code, name, n, total, top_likes in problem_totals:
        items = by_problem.get(code, [])
        if not items:
            continue
        problem_def = problem_meta[code]
        L.append(f"### {name} (`{code}`) — {n} insights · Σ {total} score")
        L.append("")
        L.append(f"_{problem_def.get('description', '')}_")
        L.append("")
        for r in items:
            L.append(
                f"- `[SCORE {r['demand_score']}]` `[{r['bucket']}]` `[{r['intent_label']}]` "
                f"`[{r['opportunity_label']}]` · @{r['author']} ({r['likes']} likes, {r['replies']} replies)"
            )
            L.append(f"  > \"{_truncate(r['quote'], 200)}\"")
            if r["summary"]:
                L.append(f"  💡 {r['summary']}")
            L.append("")

    # Unclassified detail
    if unclassified:
        L.append("### ⚠️ Unclassified — chưa match keyword nào")
        L.append("")
        L.append("> Insight ở đây gợi ý keyword bổ sung cho niche_config.json")
        L.append("")
        for r in unclassified[:20]:  # Tối đa 20 cho gọn
            L.append(
                f"- `[SCORE {r['demand_score']}]` `[{r['bucket']}]` @{r['author']} ({r['likes']} likes)"
            )
            L.append(f"  > \"{_truncate(r['quote'], 200)}\"")
        if len(unclassified) > 20:
            L.append(f"\n_(còn {len(unclassified) - 20} insight unclassified khác)_")
        L.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L), encoding="utf-8")
    logger.info("Wrote %s", path)


def write_lua_chon_md(
    records: list[dict],
    config: dict,
    path: Path,
) -> None:
    """Ghi 3-lựa-chọn.md với checkbox top-N candidates."""
    output_cfg = config["output_files"]["step_3_lua_chon"]
    max_n = int(output_cfg.get("max_candidates", 30))
    threshold = int(config["scoring_rules"]["thresholds"].get("auto_promote_to_top", 20))

    # Filter theo threshold trước, fallback nếu không đủ thì lấy top-N theo score
    qualified = [r for r in records if r["demand_score"] >= threshold]
    if len(qualified) < max_n:
        # Bổ sung từ records còn lại (đã sort score desc)
        qualified_ids = {r["id"] for r in qualified}
        for r in records:
            if r["id"] in qualified_ids:
                continue
            qualified.append(r)
            if len(qualified) >= max_n:
                break

    candidates = qualified[:max_n]

    problem_meta = {p["code"]: p for p in config["main_problems"]}

    L: list[str] = []
    L.append(f"# ✅ Lựa chọn — Top {len(candidates)} candidates")
    L.append("")
    L.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append(f"**Niche**: `{config['niche_slug']}` · **Threshold**: score ≥ {threshold}")
    L.append("")
    L.append("> 4 bước: Liệt kê → Sắp xếp → **Lựa chọn** ✅ (file này) → Thực thi")
    L.append(">")
    L.append("> **Cách dùng**: Tick `[x]` các angle anh muốn quay tuần này (5-10 cái).")
    L.append("> Sau đó (Bước 3 — selection.py — chưa làm) sẽ parse file này → generate `4-thực-thi/`.")
    L.append("")
    L.append("---")
    L.append("")

    for r in candidates:
        problem_name = problem_meta.get(r["problem_code"], {}).get("name_vi", r["problem_code"])
        # Format: - [ ] [SCORE xx] [Pxx PROBLEM_CODE] "quote ngắn" — @author
        L.append(
            f"- [ ] `[SCORE {r['demand_score']}]` `[{r['id']} {r['problem_code']}]` "
            f"`[{r['opportunity_label']}]` "
            f"\"{_truncate(r['quote'], 140)}\" — @{r['author']} ({r['likes']} likes)"
        )
        if r["summary"]:
            L.append(f"  - 💡 {r['summary']}")
        L.append(f"  - 📂 nhóm: **{problem_name}** · 🎯 intent: `{r['intent_label']}`")
        L.append("")

    if not candidates:
        L.append("_(Không có candidate nào — kiểm tra threshold trong niche_config.json)_")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L), encoding="utf-8")
    logger.info("Wrote %s", path)


# --- Entry point ---

def build_insight_bank(
    classified_path: Path,
    config_path: Path,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """All-in-one: load + process + write 3 files. Trả stats + paths."""
    config = load_niche_config(config_path)
    classified = load_classified_json(classified_path)

    if output_dir is None:
        output_dir = classified_path.parent

    records, stats = build_records(classified, config)

    # Get column list từ config
    csv_cfg = config["output_files"]["step_1_liet_ke"]
    csv_columns = csv_cfg["columns"]

    csv_path = output_dir / csv_cfg["path"]
    sap_xep_path = output_dir / config["output_files"]["step_2_sap_xep"]["path"]
    lua_chon_path = output_dir / config["output_files"]["step_3_lua_chon"]["path"]

    write_csv(records, csv_path, csv_columns)
    write_sap_xep_md(records, config, sap_xep_path)
    write_lua_chon_md(records, config, lua_chon_path)

    return {
        **stats,
        "csv_path": csv_path,
        "sap_xep_path": sap_xep_path,
        "lua_chon_path": lua_chon_path,
        "config_path": config_path,
        "classified_path": classified_path,
        "niche_slug": config["niche_slug"],
    }
