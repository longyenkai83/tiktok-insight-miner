"""Independent Pattern Engine: closed evidence graph, deterministic aggregation."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from pydantic import ValidationError

from .customer_context_models import ContextsEnvelope
from .pattern_models import (
    ContextVariant, CounterEvidence, EvidenceRef, LanguagePhrase, Pattern,
    PatternsEnvelope, Relation, Support, Variation, artifact_hash,
)
from .signal_models import SignalsEnvelope, ValidationIssue, normalize_whitespace, validate_source_span


LIMITATIONS = [
    "Candidate patterns, not Verified Insights or validated demand; frequency is sample support only.",
    "Semantic relations are DERIVED judgments; exact provenance does not prove semantic correctness.",
    "Singletons are retained as candidates, not evidence of recurrence.",
    "Authors are distinct supplied platform/author identifiers, not verified people; aliases can collide.",
    "Dedup uses source_record_id; reposts with different IDs cannot be reliably identified.",
    "Missing context is unknown; context variants are not final segments.",
    "Counter-evidence search is limited to accepted input claims; absent findings do not prove absence.",
    "Labels are representative source wording, not a synthesis of all members; inspect variations.",
]


def issue(code: str, detail: str, cid: str | None = None) -> ValidationIssue:
    return ValidationIssue(code=code, detail=detail, comment_id=cid)


def catalog_for(signals: SignalsEnvelope, contexts: ContextsEnvelope | None):
    """Recheck both schemas and compatible snapshots, retaining upstream failures."""
    signals = SignalsEnvelope.model_validate(signals.model_dump())
    contexts = ContextsEnvelope.model_validate(contexts.model_dump()) if contexts else None
    if contexts and contexts.input_signals_hash != artifact_hash(signals):
        raise ValueError("context input_signals_hash does not match supplied signals")
    catalog, sources, context_refs = {}, {}, defaultdict(list)
    def upstream_issue(value, phase):
        field = getattr(value, "field", None)
        scope = f"{phase}" + (f" field={field}" if field else "")
        return ValidationIssue(code=value.code, comment_id=value.comment_id,
            item_index=value.item_index, detail=f"{scope}: {value.detail}")

    issues = [upstream_issue(i, "Phase 1") for i in signals.issues]

    def add(source, claim, origin, path, upstream_id):
        validate_source_span(source, claim.source_record_id, claim.source_snapshot_hash,
                             claim.start, claim.end, claim.evidence_quote)
        key = "E-" + hashlib.sha256(
            f"{origin}\0{source.source_record_id}\0{upstream_id}".encode()).hexdigest()
        if key in catalog:
            raise ValueError("duplicate upstream claim identity")
        ref = EvidenceRef(evidence_id=key, origin=origin, upstream_claim_id=upstream_id,
            comment_id=source.comment_id, source_record_id=source.source_record_id,
            source_hash=source.snapshot_hash, start=claim.start, end=claim.end,
            evidence_quote=claim.evidence_quote, signal_path=path, truth_type=claim.truth_type)
        catalog[key] = ref
        return ref

    for record in signals.records:
        sources[record.comment_id] = record.source
        issues.extend(upstream_issue(i, "Phase 1") for i in record.issues)
        for claim in record.signals:
            # Phase 1 repeated_expressions is not reinterpreted or rewritten.
            # Its literal spans can contribute to the Phase 3 exact language bank.
            add(record.source, claim, "signal", f"{claim.category}.{claim.subcategory}", claim.signal_id)
    if contexts:
        issues.extend(upstream_issue(i, "Phase 2") for i in contexts.validation_issues)
        for record in contexts.records:
            if record.comment_id not in sources:
                issues.append(issue("orphan_context", "Context has no matching signal record; ignored", record.comment_id))
                continue
            if record.source_hash != sources[record.comment_id].snapshot_hash:
                raise ValueError("joined source hash mismatch")
            issues.extend(upstream_issue(i, "Phase 2") for i in record.validation_issues)
            for claim in record.customer_identity.all_claims():
                ref = add(record.source, claim, "context", f"context.{claim.field}", claim.claim_id)
                context_refs[record.comment_id].append(ref)
    # Exact duplicates of envelope/record issues are not multiple rejections.
    dedup = {i.model_dump_json(): i for i in issues}
    return dict(sorted(catalog.items())), sources, context_refs, list(dedup.values())


def grouping_key(ref: EvidenceRef) -> str:
    category = ref.signal_path.split(".")[0]
    # Context fields differ semantically; language subtypes can share literal phrases.
    return ref.signal_path if category == "context" else category


def validate_relations(catalog: dict[str, EvidenceRef], items):
    accepted, issues, pairs = [], [], defaultdict(list)
    if not isinstance(items, list):
        return [], [issue("invalid_relations", "Expected relations array")]
    for index, item in enumerate(items):
        try:
            relation = Relation.model_validate(item)
            if relation.left not in catalog or relation.right not in catalog:
                issues.append(issue("unknown_member", f"Relation index {index} rejected"))
                continue
            if relation.left == relation.right:
                issues.append(issue("self_relation", f"Relation index {index} rejected"))
                continue
            left, right = sorted([relation.left, relation.right])
            relation = relation.model_copy(update={"left": left, "right": right})
            if relation.kind != "contradiction" and grouping_key(catalog[left]) != grouping_key(catalog[right]):
                issues.append(issue("incompatible_relation", f"Relation index {index} crosses category/field"))
                continue
            pairs[(left, right)].append(relation)
        except (ValidationError, TypeError):
            issues.append(issue("invalid_relation", f"Relation index {index} rejected"))
    for pair in sorted(pairs):
        values = pairs[pair]
        if len(values) != 1:
            kinds = {value.kind for value in values}
            if "contradiction" in kinds and len(kinds) > 1:
                # Do not merge conflicting evidence or silently hide the counter-ref.
                accepted.append(next(v for v in values if v.kind == "contradiction"))
                issues.append(issue("conflicting_relation", "Merge rejected; possible counter-evidence retained for review"))
            else:
                issues.append(issue("duplicate_relation", "Repeated pair rejected in full"))
        else:
            accepted.append(values[0])
    return accepted, issues


def support_for(refs, sources) -> Support:
    # One source comment can supply many signals; count its metadata only once.
    records = {sources[r.comment_id].source_record_id: sources[r.comment_id] for r in refs}
    rows = list(records.values())
    authors = {(s.platform or "", s.author) for s in rows if s.author}
    videos = {(s.platform or "", s.video_url) for s in rows if s.video_url}
    missing_authors = sum(not s.author for s in rows)
    missing_videos = sum(not s.video_url for s in rows)
    missing_likes = sum(s.likes is None for s in rows)
    missing_replies = sum(s.reply_count is None for s in rows)
    likes = sum(s.likes for s in rows if s.likes is not None)
    replies = sum(s.reply_count for s in rows if s.reply_count is not None)
    return Support(comment_count=len(rows), unique_authors=None if missing_authors else len(authors),
        known_author_count=len(authors), unknown_author_comments=missing_authors,
        source_count=None if missing_videos else len(videos), known_source_count=len(videos),
        unknown_source_comments=missing_videos, total_likes=None if missing_likes else likes,
        known_likes_sum=likes, unknown_likes_comments=missing_likes,
        total_replies=None if missing_replies else replies, known_replies_sum=replies,
        unknown_replies_comments=missing_replies)


def compile_patterns(catalog, sources, contexts, relations, searched):
    edges = {(r.left, r.right): r.kind for r in relations}

    def compatible(a, b):
        pair = tuple(sorted([a, b]))
        relation = edges.get(pair)
        if relation == "contradiction":
            return False
        ra, rb = catalog[a], catalog[b]
        return grouping_key(ra) == grouping_key(rb) and (
            relation in ("same_meaning", "variation") or
            normalize_whitespace(ra.evidence_quote) == normalize_whitespace(rb.evidence_quote))

    # Stable greedy complete-link: no transitive A-B-C chaining without A-C support.
    groups = []
    for eid in sorted(catalog):
        for group in groups:
            if all(compatible(eid, other) for other in group):
                group.append(eid)
                break
        else:
            groups.append([eid])
    patterns = []
    for group in groups:
        refs = [catalog[eid] for eid in group]
        subcategories = sorted({
            "exact_phrases" if r.signal_path == "language.repeated_expressions"
            else r.signal_path.split(".")[1] for r in refs})
        # Extractive labeling prevents a generated label from adding customer facts.
        label = min((r.evidence_quote for r in refs), key=lambda s: (len(s), s))
        variants = defaultdict(list)
        for ref in refs:
            variants[ref.evidence_quote].append(ref)
        context_groups = defaultdict(dict)
        missing = []
        for cid in sorted({r.comment_id for r in refs}):
            if not contexts.get(cid):
                missing.append(cid)
            for ref in contexts.get(cid, []):
                context_groups[(ref.signal_path.split(".")[1], ref.evidence_quote)][ref.evidence_id] = ref
        distribution = [ContextVariant(field=field, label=quote,
            evidence_refs=list(values.values()), support=support_for(values.values(), sources))
            for (field, quote), values in sorted(context_groups.items())]
        counters = []
        for relation in relations:
            if relation.kind != "contradiction":
                continue
            a, b = relation.left, relation.right
            if a in group and b not in group:
                counters.append(CounterEvidence(supporting_ref=catalog[a], counter_ref=catalog[b]))
            elif b in group and a not in group:
                counters.append(CounterEvidence(supporting_ref=catalog[b], counter_ref=catalog[a]))
        pid = "PAT-" + hashlib.sha256("\0".join(group).encode()).hexdigest()
        patterns.append(Pattern(pattern_id=pid, pattern_type=refs[0].signal_path.split(".")[0],
            subcategory=subcategories[0] if len(subcategories) == 1 else "mixed",
            label=label, normalized_meaning=normalize_whitespace(label),
            support=support_for(refs, sources), evidence_refs=refs,
            context_distribution=distribution, missing_context_comments=missing,
            variations=[Variation(label=quote, evidence_refs=values)
                        for quote, values in sorted(variants.items())] if len(variants) > 1 else [],
            contradictions=counters, contradiction_search="CHECKED_WITHIN_INPUT" if searched else "NOT_CHECKED"))
    phrases = defaultdict(list)
    for ref in catalog.values():
        if ref.signal_path.startswith("language."):
            phrases[ref.evidence_quote].append(ref)
    bank = [LanguagePhrase(phrase=phrase, evidence_refs=refs, support=support_for(refs, sources))
            for phrase, refs in sorted(phrases.items())]
    return sorted(patterns, key=lambda p: (-p.support.comment_count, p.pattern_id)), bank


def build_patterns(signals: SignalsEnvelope, contexts: ContextsEnvelope | None = None,
                   *, provider=None) -> PatternsEnvelope:
    """Offline exact baseline unless a semantic provider is explicitly supplied."""
    catalog, sources, context_refs, issues = catalog_for(signals, contexts)
    relations = []
    status = "not_requested"
    if provider is not None and catalog:
        payload = [{**ref.model_dump(), "source_text": sources[ref.comment_id].text,
            "context_quotes": [{"field": c.signal_path, "quote": c.evidence_quote}
                               for c in context_refs.get(ref.comment_id, [])]}
                   for ref in catalog.values()]
        try:
            result = provider.compare(payload)
            if not isinstance(result, dict) or set(result) != {"relations"}:
                raise ValueError("invalid relation envelope")
            relations, rejected = validate_relations(catalog, result["relations"])
            issues.extend(rejected)
            status = "error" if rejected else "complete"
        except Exception as exc:
            # Preserve exact baseline and make failure visible; never log private API bodies.
            issues.append(issue("semantic_provider_error", f"Semantic comparison failed: {type(exc).__name__}"))
            status = "error"
    elif provider is not None:
        status = "complete"  # Empty corpus, no network request needed.
    patterns, language = compile_patterns(catalog, sources, context_refs, relations, status == "complete")
    return PatternsEnvelope(similarity_provider=provider.name if provider else "exact_only.1",
        semantic_status=status, input_signals_hash=artifact_hash(signals),
        input_contexts_hash=artifact_hash(contexts) if contexts else None,
        input_signals=signals, input_contexts=contexts, relations=relations, patterns=patterns,
        language_bank=language, validation_issues=issues, limitations=LIMITATIONS)


def save_patterns_json(result: PatternsEnvelope, path: Path) -> None:
    checked = PatternsEnvelope.model_validate(result.model_dump())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(checked.model_dump_json(indent=2), encoding="utf-8")


def load_patterns_json(path: Path) -> PatternsEnvelope:
    return PatternsEnvelope.model_validate_json(path.read_text(encoding="utf-8"))
