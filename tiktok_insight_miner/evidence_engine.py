"""Construct all downstream evidence from validated Phase 3 members in code."""
from .customer_context_models import CONTEXT_FIELDS
from .evidence_models import CustomerProfileLinks, EvidenceBundle, InsightScope
from .pattern_engine import support_for
from .pattern_models import ContextVariant, PatternsEnvelope


def checked_patterns(patterns: PatternsEnvelope) -> PatternsEnvelope:
    return PatternsEnvelope.model_validate(patterns.model_dump())


def build_evidence(patterns: PatternsEnvelope, pattern_ids: list[str]) -> EvidenceBundle:
    """Public boundary revalidates source snapshots before resolving IDs."""
    return evidence_from_checked(checked_patterns(patterns), pattern_ids)


def evidence_from_checked(patterns: PatternsEnvelope, pattern_ids: list[str]) -> EvidenceBundle:
    index = {p.pattern_id: p for p in patterns.patterns}
    if not pattern_ids or len(set(pattern_ids)) != len(pattern_ids):
        raise ValueError("empty or duplicate support pattern IDs")
    if any(pid not in index for pid in pattern_ids):
        raise ValueError("unknown support pattern ID")
    selected = [index[pid] for pid in sorted(pattern_ids)]
    refs = {r.evidence_id: r for p in selected for r in p.evidence_refs}
    if not refs:
        raise ValueError("no evidence refs")
    refs = [refs[key] for key in sorted(refs)]
    sources = {r.comment_id: r.source for r in patterns.input_signals.records}
    shared = set.intersection(*({r.comment_id for r in p.evidence_refs} for p in selected))
    comments = {r.comment_id for r in refs}
    links = CustomerProfileLinks()
    for p in selected:
        getattr(links, p.pattern_type).append(p.pattern_id)
    contextual = {}
    for p in selected:
        for variant in p.context_distribution:
            key = (variant.field, variant.label)
            bucket = contextual.setdefault(key, {})
            bucket.update({r.evidence_id: r for r in variant.evidence_refs})
    scope_fields = {field: [] for field in CONTEXT_FIELDS}
    has_context = set()
    for (field, label), values in sorted(contextual.items()):
        crefs = [values[k] for k in sorted(values)]
        has_context.update(r.comment_id for r in crefs)
        scope_fields[field].append(ContextVariant(field=field, label=label,
            evidence_refs=crefs, support=support_for(crefs, sources)))
    scope = InsightScope(source_comment_ids=sorted(comments), shared_comment_ids=sorted(shared),
        relationship_scope="within_comments" if shared else "across_corpus",
        missing_context_comments=sorted(comments - has_context), **scope_fields)
    variants = {v.model_dump_json(): v for p in selected for v in p.variations}
    counters = {c.model_dump_json(): c for p in selected for c in p.contradictions}
    limitations = [
        "Scope is the cited source comments, not a population or market estimate.",
        "Customer speech includes self-reported experience, not independently observed behavior or payment.",
        "Machine semantic review is fallible; pending human review, not human/market/purchase validation.",
        "Upstream patterns, context assignments and possible counter-relations remain candidates.",
        "A selected pattern's members need not express every part of a cross-pattern statement.",
    ]
    if len(selected) > 1:
        limitations.append("Shared comments are explicit; do not infer within-person causality from separate speakers.")
    if not shared:
        limitations.append("No comment supports all selected patterns together; only a corpus-level comparison is possible.")
    if len(comments) == 1:
        limitations.append("Single-comment scope; no evidence of recurrence across people.")
    if counters:
        limitations.append("Possible counter-evidence is preserved; conflicting situations may explain the difference.")
    if patterns.validation_issues:
        limitations.append("Input contains extraction/validation issues; accepted refs do not erase upstream failures.")
    limitations.extend(patterns.limitations)
    return EvidenceBundle(customer_profile_links=links, scope=scope,
        evidence_summary=support_for(refs, sources), evidence_refs=refs,
        variations=[variants[k] for k in sorted(variants)],
        contradictions=[counters[k] for k in sorted(counters)],
        evidence_kind=["customer_speech"], limitations=list(dict.fromkeys(limitations)))
