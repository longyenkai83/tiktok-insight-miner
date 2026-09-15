"""Code-level structural/lexical gates plus bound semantic-review checks.

Lexical guards are deliberately conservative, not a proof of semantic entailment.
"""
import re
import unicodedata

from .insight_models import InsightCandidate, SemanticReview
from .pattern_models import PatternsEnvelope, artifact_hash
from .signal_models import ValidationIssue


def normalize(text: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def problem(code: str, detail: str) -> ValidationIssue:
    return ValidationIssue(code=code, detail=detail)


def dedupe_key(candidate: InsightCandidate):
    # Do not merge different support/scope or keyword-overlap/reordered statements.
    return (tuple(sorted(candidate.support_pattern_ids)), candidate.relationship_type,
            normalize(candidate.concise_statement))


def statement_parts(candidate: InsightCandidate):
    text = candidate.concise_statement.strip()
    parts = []
    for match in re.finditer(r"[^.;!?]+[.;!?]*", text):
        if match.group().strip():
            parts.append({"part_id": f"part{len(parts)}", "start": match.start(),
                          "end": match.end(), "text": match.group()})
    return parts


def candidate_issues(candidate: InsightCandidate, patterns: PatternsEnvelope):
    issues = []
    index = {p.pattern_id: p for p in patterns.patterns}
    ids = candidate.support_pattern_ids
    if len(ids) != len(set(ids)):
        issues.append(problem("duplicate_pattern_id", "Repeated support ID"))
    if any(pid not in index for pid in ids):
        return issues + [problem("unknown_pattern_id", "Support ID not in supplied catalog")]
    selected = [index[pid] for pid in ids]
    if not selected or any(not p.evidence_refs for p in selected):
        return issues + [problem("orphan_insight", "No grounded support")]
    categories = {p.pattern_type for p in selected}
    paths = {r.signal_path for p in selected for r in p.evidence_refs}
    required = {"job_pain": {"jobs", "pains"}, "pain_behavior": {"pains", "behavior"},
        "pain_gain": {"pains", "gains"}, "situation_pain": {"context", "pains"},
        "stage_decision": {"context", "behavior"}, "current_solution_frustration": {"behavior", "pains"},
        "language_behavior": {"language", "behavior"}}
    rel = candidate.relationship_type
    incompatible = not required.get(rel, set()).issubset(categories)
    if rel == "single_pattern" and len(ids) != 1:
        incompatible = True
    if rel == "stage_decision" and not {"context.life_or_business_stage", "behavior.decision_criteria"}.issubset(paths):
        incompatible = True
    if rel == "situation_pain" and "context.situation" not in paths:
        incompatible = True
    if rel == "current_solution_frustration" and not {"behavior.current_solution", "pains.frustrations"}.issubset(paths):
        incompatible = True
    if incompatible:
        issues.append(problem("impossible_relationship", "Relationship lacks required upstream category/path"))
    text = unicodedata.normalize("NFKC", candidate.concise_statement).casefold()
    if not normalize(text):
        issues.append(problem("empty_statement", "Statement has no words"))
    # Numeric assertions belong in deterministic evidence_summary, not model prose.
    if re.search(r"\d|[%‰]|\b(percent|percentage|million|billion|hundred|twenty|thirty)\b|phần trăm|triệu|tỷ lệ", text):
        issues.append(problem("unsupported_numeric_claim", "Generated numeric assertions are not supported by this transport"))
    if re.search(r"\b(always|everyone|everybody|most customers|all customers|the market wants|will pay|proves|majority)\b|khách hàng luôn|mọi khách hàng|tất cả khách|đa số|phần lớn|thị trường muốn|sẽ trả tiền|chứng minh", text):
        issues.append(problem("market_generalization", "Population/demand or certainty claim is not allowed"))
    if re.search(r"\b(should (build|create|sell|launch)|we (should|can|must)|recommend|let's|lead magnet|value map|pain reliever|gain creator)\b|đề xuất|nên (tạo|xây|bán|ra mắt)|hãy (tạo|xây|bán)|cần (tạo|xây dựng|bán)|giải pháp là|cơ hội (sản phẩm|nội dung)", text):
        issues.append(problem("solution_leak", "Downstream recommendation/generation is forbidden"))
    evidence_text = " ".join(r.evidence_quote for p in selected for r in p.evidence_refs).casefold()
    for word in ("checklist", "calculator", "template", "offer", "hook", "script", "campaign",
                 "product", "tool", "content", "sản phẩm", "công cụ", "bài viết", "kịch bản", "chiến dịch"):
        if re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text) and word not in evidence_text:
            issues.append(problem("solution_leak", "Unprovided product/content term in candidate"))
            break
    contexts = " ".join(v.label for p in selected for v in p.context_distribution).casefold()
    for term in ("women", "men", "female", "male", "teenagers", "elderly", "parents", "mothers", "fathers",
                 "low-income", "high-income", "wealthy", "unemployed", "students", "phụ nữ", "đàn ông", "sinh viên", "học sinh",
                 "người già", "thu nhập thấp", "thu nhập cao", "giàu có", "thất nghiệp", "các bà mẹ", "nhân viên văn phòng",
                 "đã có con", "có con nhỏ", "phụ huynh", "mẹ bỉm", "độc thân", "trung niên", "giới trẻ", "người trẻ"):
        if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) and term not in contexts:
            issues.append(problem("unsupported_demographic", "Demographic claim absent from cited context"))
            break
    # New proper-name sequences (e.g. locations) cannot be filled from model knowledge.
    words = list(re.finditer(r"\b[^\W\d_]+\b", candidate.concise_statement))
    for first, second in zip(words, words[1:]):
        gap = candidate.concise_statement[first.end():second.start()]
        # Unicode ranges mix upper/lower Vietnamese letters; test casing explicitly.
        if gap.isspace() and first.group().istitle() and second.group().istitle():
            name = candidate.concise_statement[first.start():second.end()]
            if name.casefold() not in contexts:
                issues.append(problem("unsupported_demographic", "Unprovided named identity/location"))
    if any(mark in text for mark in ('"', '“', '”', '«', '»')) or re.search(r"(?<!\w)'[^'\n]+'(?!\w)", text):
        issues.append(problem("quote_in_statement", "Model transport must not generate quotes"))
    normalized = normalize(text)
    if normalized in {normalize(p.label) for p in selected} | {normalize(r.evidence_quote) for p in selected for r in p.evidence_refs}:
        issues.append(problem("shallow_statement", "Statement only renames/copies source or pattern label"))
    return issues


def review_issues(candidate: InsightCandidate, review: SemanticReview | None):
    if review is None:
        return [problem("missing_semantic_review", "A separate semantic review is required")]
    if review.insight_candidate_id != candidate.insight_candidate_id or review.candidate_hash != artifact_hash(candidate):
        return [problem("stale_semantic_review", "Review not bound to this exact candidate")]
    if sorted(review.support_pattern_ids) != sorted(candidate.support_pattern_ids):
        return [problem("invalid_review_support", "Reviewer changed or omitted support pattern IDs")]
    expected_parts = {p["part_id"] for p in statement_parts(candidate)}
    got_parts = [p.part_id for p in review.part_support]
    if set(got_parts) != expected_parts or len(got_parts) != len(expected_parts):
        return [problem("invalid_part_support", "Each statement part requires exactly one support mapping")]
    covered = set()
    for part in review.part_support:
        if not set(part.support_pattern_ids).issubset(candidate.support_pattern_ids) or len(part.support_pattern_ids) != len(set(part.support_pattern_ids)):
            return [problem("invalid_part_support", "Statement part references unprovided support")]
        covered.update(part.support_pattern_ids)
    if covered != set(candidate.support_pattern_ids):
        return [problem("invalid_part_support", "Every selected pattern must support a statement part")]
    checks = (review.supported, review.adds_understanding, review.scope_preserved,
              review.no_unsupported_causality, review.no_demographic_leak,
              review.no_solution_leak, review.no_market_generalization)
    if not all(checks) or review.reason_code != "supported":
        return [problem("semantic_" + review.reason_code, "Candidate did not pass all semantic review checks")]
    return []
