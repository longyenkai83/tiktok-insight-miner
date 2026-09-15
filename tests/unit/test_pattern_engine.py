"""Offline Pattern Engine tests. All customer examples here are synthetic."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from tiktok_insight_miner.customer_context_extractor import validate_context_batch
from tiktok_insight_miner.customer_context_models import ContextsEnvelope
from tiktok_insight_miner.pattern_engine import (
    build_patterns, catalog_for, load_patterns_json, save_patterns_json,
)
from tiktok_insight_miner.pattern_models import PatternsEnvelope, Relation, artifact_hash
from tiktok_insight_miner.pattern_similarity import AnthropicRelations
from tiktok_insight_miner.signal_extractor import source_from_comment, validate_batch, save_signals_json
from tiktok_insight_miner.signal_models import SignalsEnvelope


def inputs(texts, categories=None, authors=None):
    sources = [source_from_comment({"id": f"c{i}", "text": text,
        "author": authors[i] if authors else "same-author"}) for i, text in enumerate(texts)]
    rows = []
    for i, text in enumerate(texts):
        category, subcategory = categories[i] if categories else ("pains", "costs")
        rows.append({"comment_id": f"c{i}", "signals": [{"category": category,
            "subcategory": subcategory, "evidence_quote": text,
            "truth_type": "OBSERVED", "confidence": "high"}]})
    records, issues = validate_batch(sources, {"results": rows})
    assert not issues
    return SignalsEnvelope(model="synthetic", records=records)


def contexts_for(signals, assignments):
    payload = {"results": [{"comment_id": r.comment_id, "contexts": [
        {"field": field, "evidence_quote": quote, "truth_type": "OBSERVED", "confidence": "high"}
        for field, quote in assignments.get(r.comment_id, [])]} for r in signals.records]}
    records, issues = validate_context_batch(signals.records, payload)
    assert not issues
    return ContextsEnvelope(model="synthetic", input_signals_hash=artifact_hash(signals), records=records)


class FakeRelations:
    name = "synthetic-semantic-fixture"

    def __init__(self, pairs):
        self.pairs = pairs

    def compare(self, catalog):
        ids = {c["comment_id"]: c["evidence_id"] for c in catalog if c["origin"] == "signal"}
        return {"relations": [{"left": ids[a], "right": ids[b], "kind": kind}
                              for a, b, kind in self.pairs]}


def test_semantically_similar_pains_cluster_distinct_problem_separate():
    s = inputs(["Rent consumes my profit", "I work just to pay the landlord", "My supplier is unreliable"])
    result = build_patterns(s, provider=FakeRelations([("c0", "c1", "same_meaning")]))
    assert [p.support.comment_count for p in result.patterns] == [2, 1]
    assert len(result.patterns[0].variations) == 2
    assert result.patterns[0].truth_type == "DERIVED"


def test_no_chain_overmerge():
    s = inputs(["Rent pressure", "Store cost pressure", "Inventory spoilage"])
    r = build_patterns(s, provider=FakeRelations([("c0", "c1", "variation"), ("c1", "c2", "variation")]))
    assert max(p.support.comment_count for p in r.patterns) == 2


def test_cross_comment_language_bank_preserves_phrase_and_counts():
    s = inputs(["working for the landlord"] * 3,
        categories=[("language", "exact_phrases")] * 3, authors=["a", "a", "b"])
    before = s.model_dump()
    r = build_patterns(s)
    phrase = r.language_bank[0]
    assert phrase.phrase == "working for the landlord"
    assert phrase.support.comment_count == 3 and phrase.support.unique_authors == 2
    assert r.patterns[0].support.comment_count == 3
    assert s.model_dump() == before  # no Phase 1 repeated_expressions rewrite


def test_missing_context_still_clusters():
    s = inputs(["rent too high", "rent too high"])
    r = build_patterns(s)
    assert len(r.patterns) == 1
    assert r.patterns[0].missing_context_comments == ["c0", "c1"]


def test_context_variants_preserved_not_forced_into_segment():
    s = inputs(["Opening soon; rent is high", "Five years running; rent is high"])
    c = contexts_for(s, {"c0": [("life_or_business_stage", "Opening soon")],
                         "c1": [("life_or_business_stage", "Five years running")]})
    r = build_patterns(s, c, provider=FakeRelations([("c0", "c1", "same_meaning")]))
    pain = next(p for p in r.patterns if p.pattern_type == "pains")
    assert {v.label for v in pain.context_distribution} == {"Opening soon", "Five years running"}
    assert all(v.support.comment_count == 1 for v in pain.context_distribution)
    assert not pain.missing_context_comments


def test_counter_evidence_cross_category_preserved_and_not_support():
    s = inputs(["Rent makes profit impossible", "Rent is manageable with my sales volume"],
               categories=[("pains", "costs"), ("gains", "expected")])
    r = build_patterns(s, provider=FakeRelations([("c0", "c1", "contradiction")]))
    assert len(r.patterns) == 2
    assert all(p.support.comment_count == 1 for p in r.patterns)
    assert all(len(p.contradictions) == 1 for p in r.patterns)
    assert all(p.contradiction_search == "CHECKED_WITHIN_INPUT" for p in r.patterns)
    assert all(p.contradictions[0].counter_ref.comment_id != p.evidence_refs[0].comment_id for p in r.patterns)


def test_distinct_mechanisms_remain_variations():
    s = inputs(["Nobody knows my shop", "Only referrals bring customers", "Ads fail to bring customers"])
    pairs = [("c0", "c1", "variation"), ("c0", "c2", "variation"), ("c1", "c2", "variation")]
    p = build_patterns(s, provider=FakeRelations(pairs)).patterns[0]
    assert p.support.comment_count == 3
    assert {v.label for v in p.variations} == {r.source.text for r in s.records}


def test_all_refs_resolve_to_original_claims_and_spans():
    s = inputs(["rent high", "rent high"])
    c = contexts_for(s, {"c0": [("situation", "rent high")]})
    result = build_patterns(s, c)
    for p in result.patterns:
        for ref in p.evidence_refs:
            src = next(r.source for r in s.records if r.comment_id == ref.comment_id)
            assert ref.source_hash == src.snapshot_hash
            assert ref.evidence_quote == src.text[ref.start:ref.end]
    assert result.input_signals_hash == c.input_signals_hash


@pytest.mark.parametrize("mutation", ["member", "quote", "count", "label", "truth", "status", "extra"])
def test_persisted_fabrication_rejected(mutation):
    data = build_patterns(inputs(["rent high"])).model_dump(mode="json")
    p = data["patterns"][0]
    if mutation == "member": p["evidence_refs"][0]["upstream_claim_id"] = "invented"
    if mutation == "quote": p["evidence_refs"][0]["evidence_quote"] = "invented customer truth"
    if mutation == "count": p["support"]["comment_count"] = 100
    if mutation == "label": p["label"] = "Customers will buy a product"
    if mutation == "truth": p["truth_type"] = "OBSERVED"
    if mutation == "status": p["pattern_status"] = "verified"
    if mutation == "extra": p["product_opportunity"] = "invented"
    with pytest.raises(ValidationError): PatternsEnvelope.model_validate(data)


@pytest.mark.parametrize("kind", ["unknown", "duplicate", "self", "truth", "cross_category", "extra"])
def test_bad_semantic_relations_rejected_without_invented_members(kind):
    s = inputs(["rent high", "want free time"], categories=[("pains", "costs"), ("gains", "desired")])
    catalog, *_ = catalog_for(s, None)
    a, b = list(catalog)
    rel = {"left": a, "right": b, "kind": "same_meaning"}
    if kind == "unknown": rel["right"] = "invented"
    if kind == "self": rel["right"] = a
    if kind == "truth": rel["truth_type"] = "HYPOTHESIS"
    if kind == "extra": rel["new_member"] = "made up"
    if kind == "duplicate": rel["kind"] = "contradiction"
    provider = Mock(name="test"); provider.name = "test"
    provider.compare.return_value = {"relations": [rel, rel] if kind == "duplicate" else [rel]}
    r = build_patterns(s, provider=provider)
    assert r.semantic_status == "error" and r.validation_issues
    assert not r.relations and len(r.patterns) == 2


@pytest.mark.parametrize("truth", ["HYPOTHESIS", "PROPOSED"])
def test_no_generated_hypothesis_or_proposal(truth):
    with pytest.raises(ValidationError):
        Relation(left="a", right="b", kind="same_meaning", truth_type=truth)


def test_unknown_engagement_author_and_video_not_measured_zero():
    r = build_patterns(inputs(["rent high"], authors=[""]))
    m = r.patterns[0].support
    assert m.total_likes is None and m.total_replies is None
    assert m.unique_authors is None and m.source_count is None
    assert m.unknown_likes_comments == m.unknown_author_comments == 1


def test_known_zero_and_partial_metric_coverage():
    s = inputs(["rent high", "rent high"])
    source = s.records[0].source
    source.likes = 0; source.reply_count = 2
    source.snapshot_hash = source.expected_hash()
    s.records[0].signals[0].source_snapshot_hash = source.snapshot_hash
    p = build_patterns(s).patterns[0]
    assert p.support.total_likes is None
    assert p.support.known_likes_sum == 0 and p.support.unknown_likes_comments == 1
    assert p.support.known_replies_sum == 2


def test_multisignal_comment_not_double_counted():
    s = inputs(["rent high"])
    extra = s.records[0].signals[0].model_copy(update={"subcategory": "frustrations", "signal_id": "other-signal"})
    s.records[0].signals.append(extra)
    p = build_patterns(s).patterns[0]
    assert len(p.evidence_refs) == 2 and p.support.comment_count == 1
    assert p.subcategory == "mixed"


def test_serialization_revalidates_input_hash_and_membership(tmp_path):
    r = build_patterns(inputs(["rent high", "rent high"]))
    path = tmp_path / "patterns.json"
    save_patterns_json(r, path)
    assert load_patterns_json(path) == r
    data = json.loads(path.read_text())
    data["input_signals"]["records"][0]["source"]["text"] = "changed"
    path.write_text(json.dumps(data))
    with pytest.raises(ValidationError): load_patterns_json(path)


def test_input_compatibility_missing_context_record_and_hash_mismatch():
    s = inputs(["rent high", "rent high"])
    c = contexts_for(s, {})
    c.records.pop()
    before_s, before_c = s.model_dump(), c.model_dump()
    assert build_patterns(s, c).patterns[0].support.comment_count == 2
    assert (s.model_dump(), c.model_dump()) == (before_s, before_c)
    c.input_signals_hash = "wrong"
    with pytest.raises(ValueError, match="input_signals_hash"): build_patterns(s, c)


def test_orphan_context_cannot_form_pattern():
    s = inputs(["rent high"])
    other = inputs(["other", "orphan situation"])
    c = contexts_for(other, {"c1": [("situation", "orphan situation")]})
    c.records = [c.records[1]]
    c.input_signals_hash = artifact_hash(s)
    r = build_patterns(s, c)
    assert len(r.patterns) == 1
    assert any(i.code == "orphan_context" for i in r.validation_issues)


def test_joined_source_hash_mismatch_rejected():
    s = inputs(["rent high"])
    c = contexts_for(inputs(["different text"]), {})
    c.input_signals_hash = artifact_hash(s)
    with pytest.raises(ValueError, match="source hash"): build_patterns(s, c)


def test_empty_no_signal_and_no_context_preserved():
    s = inputs(["unrelated"])
    s.records[0].signals = []; s.records[0].extraction_status = "no_signal"
    c = contexts_for(s, {})
    provider = Mock(); provider.name = "test"
    r = build_patterns(s, c, provider=provider)
    provider.compare.assert_not_called()
    assert not r.patterns and r.input_signals.records[0].extraction_status == "no_signal"


def test_provider_failure_visible_with_exact_baseline():
    provider = Mock(); provider.name = "test"; provider.compare.side_effect = RuntimeError("private secret")
    r = build_patterns(inputs(["rent high", "rent high"]), provider=provider)
    assert len(r.patterns) == 1 and r.semantic_status == "error"
    assert "private secret" not in r.validation_issues[0].detail
    assert r.patterns[0].contradiction_search == "NOT_CHECKED"


def test_provider_uses_existing_sdk_closed_transport_offline():
    client = Mock()
    client.messages.create.return_value = SimpleNamespace(stop_reason="end_turn",
        content=[SimpleNamespace(type="text", text='{"relations": []}')], usage=SimpleNamespace(cache_read_input_tokens=0))
    provider = AnthropicRelations(model="synthetic", client=client)
    r = build_patterns(inputs(["rent high", "rent consumes profit"]), provider=provider)
    assert r.semantic_status == "complete"
    args = client.messages.create.call_args.kwargs
    assert args["model"] == "synthetic"
    assert "metadata" not in json.loads(args["messages"][0]["content"])[0]


def test_provider_does_not_truncate_oversized_catalog():
    client = Mock()
    with pytest.raises(ValueError, match="limit 200"):
        AnthropicRelations(client=client).compare([{}] * 201)
    client.messages.create.assert_not_called()


def test_cli_independent_exact_mode_and_overwrite_guard(tmp_path, monkeypatch):
    from tiktok_insight_miner.cli import main
    path = tmp_path / "signals.json"
    save_signals_json(inputs(["rent high"]), path)
    monkeypatch.setattr("sys.argv", ["tim", "build-patterns", "--signals", str(path), "--exact-only"])
    main()
    assert load_patterns_json(tmp_path / "patterns.json").semantic_status == "not_requested"
    monkeypatch.setattr("sys.argv", ["tim", "build-patterns", "--signals", str(path), "-o", str(path), "--exact-only"])
    with pytest.raises(SystemExit, match="overwrite"): main()


def test_semantic_results_are_deterministic_given_saved_relations():
    s = inputs(["rent high", "landlord takes all profit"])
    provider = FakeRelations([("c0", "c1", "same_meaning")])
    one, two = build_patterns(s, provider=provider), build_patterns(s, provider=provider)
    assert one.patterns == two.patterns and one.relations == two.relations


@pytest.mark.parametrize("right,expected", [("e001", "complete"), ("e999", "error")])
def test_short_transport_ids_resolve_only_through_exact_mapping(right, expected):
    client = Mock()
    first = SimpleNamespace(stop_reason="end_turn", content=[
        SimpleNamespace(type="text", text=json.dumps({"relations": [
            {"left": "e000", "right": right, "kind": "same_meaning"}]}))],
        usage=SimpleNamespace(cache_read_input_tokens=0))
    client.messages.create.side_effect = [first, SimpleNamespace(stop_reason="end_turn",
        content=[SimpleNamespace(type="text", text='{"relations": []}')],
        usage=SimpleNamespace(cache_read_input_tokens=0))]
    s = inputs(["rent high", "rent consumes profit"])
    result = build_patterns(s, provider=AnthropicRelations(client=client))
    assert result.semantic_status == expected
    if expected == "complete":
        assert result.patterns[0].support.comment_count == 2
        assert all(r.left.startswith("E-") for r in result.relations)
    else:
        assert any(i.code == "unknown_member" for i in result.validation_issues)


def test_truncated_api_response_never_succeeds():
    client = Mock()
    client.messages.create.return_value = SimpleNamespace(stop_reason="max_tokens",
        content=[], usage=SimpleNamespace(cache_read_input_tokens=0))
    r = build_patterns(inputs(["rent high", "rent consumes profit"]), provider=AnthropicRelations(client=client))
    assert r.semantic_status == "error"
    assert r.validation_issues[0].code == "semantic_provider_error"


def test_no_content_product_priority_fields_or_verified_states():
    r = build_patterns(inputs(["rent high", "rent high"]))
    forbidden = {"insights", "product_opportunities", "content_opportunities", "topics", "angles", "priority_score"}
    assert not forbidden.intersection(r.model_dump())
    assert all(p.pattern_status == "candidate" and p.truth_type == "DERIVED" for p in r.patterns)
    assert all(not forbidden.intersection(p.model_dump()) for p in r.patterns)


def test_language_inside_comment_repetition_is_not_corpus_repetition():
    source = source_from_comment({"id": "c0", "text": "too much, too much"})
    records, _ = validate_batch([source], {"results": [{"comment_id": "c0", "signals": [{
        "category": "language", "subcategory": "repeated_expressions", "evidence_quote": "too much",
        "truth_type": "OBSERVED", "confidence": "high"}]}]})
    s = SignalsEnvelope(model="synthetic", records=records)
    r = build_patterns(s)
    assert r.language_bank[0].support.comment_count == 1
    assert r.patterns[0].subcategory == "exact_phrases"
    assert s.records[0].signals[0].subcategory == "repeated_expressions"


def test_cli_marks_semantic_failure_incomplete(tmp_path, monkeypatch):
    from tiktok_insight_miner.cli import main
    source = tmp_path / "signals.json"
    save_signals_json(inputs(["rent high"]), source)
    monkeypatch.setattr(AnthropicRelations, "compare", Mock(side_effect=RuntimeError("offline")))
    monkeypatch.setattr("sys.argv", ["tim", "build-patterns", "--signals", str(source)])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert load_patterns_json(tmp_path / "patterns.json").semantic_status == "error"


def test_context_fields_cannot_be_semantically_merged():
    s = inputs(["Opening soon"])
    c = contexts_for(s, {"c0": [("situation", "Opening soon"), ("life_or_business_stage", "Opening soon")]})
    catalog, *_ = catalog_for(s, c)
    context_ids = [ref.evidence_id for ref in catalog.values() if ref.origin == "context"]
    provider = Mock(); provider.name = "test"
    provider.compare.return_value = {"relations": [dict(left=context_ids[0], right=context_ids[1], kind="same_meaning")]}
    r = build_patterns(s, c, provider=provider)
    assert sum(p.pattern_type == "context" for p in r.patterns) == 2
    assert any(i.code == "incompatible_relation" for i in r.validation_issues)


def test_distinct_comment_and_author_counts_with_known_metrics():
    s = inputs(["rent high", "rent high"])
    for r in s.records:
        r.source.likes = 3; r.source.reply_count = 0
        r.source.snapshot_hash = r.source.expected_hash()
        r.signals[0].source_snapshot_hash = r.source.snapshot_hash
    p = build_patterns(s).patterns[0]
    assert p.support.comment_count == 2 and p.support.unique_authors == 1
    assert p.support.total_likes == 6 and p.support.total_replies == 0


def test_semantic_passes_are_category_bounded_and_counter_search_is_global():
    s = inputs(["rent high", "rent consumes profit", "I want more free time"],
        categories=[("pains", "costs"), ("pains", "costs"), ("gains", "desired")])
    client = Mock()
    client.messages.create.return_value = SimpleNamespace(stop_reason="end_turn",
        content=[SimpleNamespace(type="text", text='{"relations": []}')],
        usage=SimpleNamespace(cache_read_input_tokens=0))
    build_patterns(s, provider=AnthropicRelations(client=client))
    calls = client.messages.create.call_args_list
    assert len(calls) == 2
    first = json.loads(calls[0].kwargs["messages"][0]["content"])
    last = json.loads(calls[1].kwargs["messages"][0]["content"])
    assert len(first) == 2 and {c["grouping_key"] for c in first} == {"pains"}
    assert len(last) == 3
    assert calls[1].kwargs["output_config"]["format"]["schema"]["$defs"]["Relation"]["properties"]["kind"]["enum"] == ["contradiction"]


def test_rejections_in_different_phases_are_not_deduplicated_together():
    from tiktok_insight_miner.signal_models import ValidationIssue
    from tiktok_insight_miner.customer_context_models import ContextIssue
    s = inputs(["rent high"])
    s.records[0].extraction_status = "partial"
    s.records[0].issues = [ValidationIssue(code="ungrounded_quote", comment_id="c0", item_index=1, detail="bad quote")]
    c = contexts_for(s, {})
    c.records[0].extraction_status = "partial"
    c.records[0].validation_issues = [ContextIssue(code="ungrounded_quote", comment_id="c0", item_index=1, detail="bad quote", field="situation")]
    r = build_patterns(s, c)
    assert len(r.validation_issues) == 2
    assert {i.detail.split(':')[0] for i in r.validation_issues} == {"Phase 1", "Phase 2 field=situation"}
    data = r.model_dump()
    data["validation_issues"] = []
    with pytest.raises(ValidationError, match="upstream validation issues"):
        PatternsEnvelope.model_validate(data)


def test_conflicting_merge_and_counter_relation_keeps_counter_visible():
    s = inputs(["Rent is painful", "Rent is manageable"])
    r = build_patterns(s, provider=FakeRelations([
        ("c0", "c1", "same_meaning"), ("c0", "c1", "contradiction")]))
    assert len(r.patterns) == 2 and all(p.contradictions for p in r.patterns)
    assert r.semantic_status == "error"
    assert any(i.code == "conflicting_relation" for i in r.validation_issues)
