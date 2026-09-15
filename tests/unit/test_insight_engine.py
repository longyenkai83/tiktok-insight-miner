"""Synthetic/offline tests for Phase 4; no real customer data or API dependency."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from tiktok_insight_miner.customer_context_extractor import validate_context_batch
from tiktok_insight_miner.customer_context_models import ContextsEnvelope
from tiktok_insight_miner.evidence_engine import build_evidence
from tiktok_insight_miner.evidence_models import EvidenceKind
from tiktok_insight_miner.insight_engine import AnthropicInsights, build_insights, load_insights_json, save_insights_json
from tiktok_insight_miner.insight_models import InsightsEnvelope, InsightCandidate
from tiktok_insight_miner.insight_validator import statement_parts
from tiktok_insight_miner.pattern_engine import build_patterns, save_patterns_json
from tiktok_insight_miner.pattern_models import artifact_hash
from tiktok_insight_miner.signal_extractor import source_from_comment, validate_batch
from tiktok_insight_miner.signal_models import SignalsEnvelope


def patterns_fixture(with_context=False):
    source = source_from_comment({"id": "c1", "text": "I want stable income but rent consumes my profit.", "author": "a"})
    rows, _ = validate_batch([source], {"results": [{"comment_id": "c1", "signals": [
        {"category": "jobs", "subcategory": "functional", "evidence_quote": "I want stable income",
         "truth_type": "OBSERVED", "confidence": "high"},
        {"category": "pains", "subcategory": "costs", "evidence_quote": "rent consumes my profit",
         "truth_type": "DERIVED", "confidence": "high"}]}]})
    signals = SignalsEnvelope(model="synthetic", records=rows)
    contexts = None
    if with_context:
        cr, _ = validate_context_batch(rows, {"results": [{"comment_id": "c1", "contexts": [
            {"field": "situation", "evidence_quote": "rent consumes my profit", "truth_type": "OBSERVED", "confidence": "high"}]}]})
        contexts = ContextsEnvelope(model="synthetic", input_signals_hash=artifact_hash(signals), records=cr)
    return build_patterns(signals, contexts)


def candidate(patterns, text="The wish for income stability coexists with pressure on the profit retained after rent.", **changes):
    return {"insight_candidate_id": "i1", "support_pattern_ids": [p.pattern_id for p in patterns.patterns if p.pattern_type in ("jobs", "pains")],
            "relationship_type": "job_pain", "concise_statement": text, **changes}


class FakeProvider:
    name = "offline-fixture"
    def __init__(self, candidates, verdict_changes=None):
        self.candidates = candidates
        self.verdict_changes = verdict_changes or {}
    def propose(self, catalog): return {"candidates": self.candidates}
    def review(self, items):
        return {"reviews": [{"insight_candidate_id": item["candidate"]["insight_candidate_id"],
            "support_pattern_ids": item["candidate"]["support_pattern_ids"], "supported": True,
            "adds_understanding": True, "scope_preserved": True, "no_unsupported_causality": True,
            "no_demographic_leak": True, "no_solution_leak": True, "no_market_generalization": True,
            "part_support": [{"part_id": p["part_id"], "support_pattern_ids": item["candidate"]["support_pattern_ids"]}
                             for p in statement_parts(InsightCandidate.model_validate(item["candidate"]))],
            "reason_code": "supported", **self.verdict_changes} for item in items]}


def test_cross_pattern_insight_valid_and_traceable():
    p = patterns_fixture()
    before = p.model_dump()
    result = build_insights(p, provider=FakeProvider([candidate(p)]))
    insight = result.insights[0]
    assert insight.statement.truth_type == "DERIVED"
    assert insight.relationship_type == "job_pain"
    assert len(insight.customer_profile_links.jobs) == len(insight.customer_profile_links.pains) == 1
    assert insight.evidence_summary.comment_count == 1
    assert insight.scope.shared_comment_ids == ["c1"]
    for ref in insight.evidence_refs:
        source = p.input_signals.records[0].source
        assert ref.source_hash == source.snapshot_hash
        assert ref.evidence_quote == source.text[ref.start:ref.end]
    assert p.model_dump() == before


def test_single_pattern_relationship_not_renamed_label():
    p = patterns_fixture()
    pain = next(x for x in p.patterns if x.pattern_type == "pains")
    c = candidate(p, "The retained profit is described in tension with the rent burden.",
                  support_pattern_ids=[pain.pattern_id], relationship_type="single_pattern")
    r = build_insights(p, provider=FakeProvider([c]))
    assert len(r.insights) == 1
    assert r.insights[0].customer_profile_links.jobs == []


@pytest.mark.parametrize("changes,code", [
    ({"support_pattern_ids": ["invented"]}, "unknown_pattern_id"),
    ({"support_pattern_ids": []}, "invalid_candidate"),
    ({"relationship_type": "stage_decision"}, "impossible_relationship"),
    ({"relationship_type": "single_pattern"}, "impossible_relationship"),
    ({"truth_type": "HYPOTHESIS"}, "invalid_candidate"),
    ({"truth_type": "PROPOSED"}, "invalid_candidate"),
    ({"new_quote": "invented"}, "invalid_candidate"),
    ({"comment_id": "invented"}, "invalid_candidate"),
    ({"human_verified": True}, "invalid_candidate"),
])
def test_bad_transport_rejected(changes, code):
    p = patterns_fixture()
    r = build_insights(p, provider=FakeProvider([candidate(p, **changes)]))
    assert not r.insights and any(i.code == code for i in r.outcomes[0].validation_issues)


@pytest.mark.parametrize("text,code", [
    ("85% of customers cannot afford rent", "unsupported_numeric_claim"),
    ("Rent consumes ninety percent of income", "unsupported_numeric_claim"),
    ("Most customers will pay to eliminate rent pressure", "market_generalization"),
    ("Women need income stability despite rent pressure", "unsupported_demographic"),
    ("Customers in New York struggle with rent", "unsupported_demographic"),
    ("Sinh viên cần ổn định thu nhập", "unsupported_demographic"),
    ("Nhóm đã có con chuyển sang ưu tiên gia đình", "unsupported_demographic"),
    ("We should build a rent calculator", "solution_leak"),
    ("Đề xuất một sản phẩm giúp ổn định thu nhập", "solution_leak"),
    ("Create a content script about rent pressure", "solution_leak"),
    ('Customers say "rent is unaffordable"', "quote_in_statement"),
    ("Customers say 'rent is unaffordable'", "quote_in_statement"),
    ("rent consumes my profit", "shallow_statement"),
])
def test_code_level_semantic_safety_guards(text, code):
    p = patterns_fixture()
    provider = FakeProvider([candidate(p, text)])
    provider.review = Mock(side_effect=AssertionError("invalid candidate must not reach review"))
    r = build_insights(p, provider=provider)
    assert not r.insights
    assert any(i.code == code for i in r.outcomes[0].validation_issues)
    provider.review.assert_not_called()


@pytest.mark.parametrize("flag,reason", [
    ("supported", "overclaim"), ("adds_understanding", "shallow"),
    ("scope_preserved", "context_leak"), ("no_unsupported_causality", "false_causality"),
    ("no_solution_leak", "solution_leak"), ("no_demographic_leak", "unsupported_demographic"),
    ("no_market_generalization", "overclaim"),
])
def test_separate_semantic_review_fails_closed(flag, reason):
    p = patterns_fixture()
    r = build_insights(p, provider=FakeProvider([candidate(p)], {flag: False, "reason_code": reason}))
    assert not r.insights
    assert r.outcomes[0].validation_issues[0].code == "semantic_" + reason


def test_scope_preserved_unknown_metrics_not_zero():
    p = patterns_fixture(with_context=True)
    i = build_insights(p, provider=FakeProvider([candidate(p)])).insights[0]
    assert i.scope.situation[0].label == "rent consumes my profit"
    assert not i.scope.audience_segment
    assert i.evidence_summary.total_likes is None and i.evidence_summary.total_replies is None
    assert i.evidence_summary.unknown_likes_comments == 1


def test_verification_and_evidence_kind_do_not_promote_speech():
    p = patterns_fixture()
    i = build_insights(p, provider=FakeProvider([candidate(p)])).insights[0]
    assert i.verification.source_grounded and i.verification.evidence_support_present
    assert not i.verification.human_verified and not i.verification.market_validated and not i.verification.purchase_validated
    assert i.status == "pending_human_review" and i.evidence_kind == ["customer_speech"]
    assert {k.value for k in EvidenceKind} == {"customer_speech", "customer_behavior", "commitment", "payment", "market_behavior"}


def test_text_about_payment_remains_speech():
    source = source_from_comment({"id": "paid", "text": "I paid for a service"})
    rows, _ = validate_batch([source], {"results": [{"comment_id": "paid", "signals": [{
        "category": "behavior", "subcategory": "current_solution", "evidence_quote": source.text,
        "truth_type": "OBSERVED", "confidence": "high"}]}]})
    p = build_patterns(SignalsEnvelope(model="synthetic", records=rows))
    evidence = build_evidence(p, [p.patterns[0].pattern_id])
    assert evidence.evidence_kind == ["customer_speech"]


def test_same_keywords_do_not_dedupe_but_near_identical_format_does():
    p = patterns_fixture()
    a = candidate(p)
    b = candidate(p, a["concise_statement"].upper().replace(".", "!"), insight_candidate_id="i2")
    c = candidate(p, "Rent pressure is present alongside a stated wish for income stability.", insight_candidate_id="i3")
    r = build_insights(p, provider=FakeProvider([a, b, c]))
    assert len(r.insights) == 2
    assert [o.status for o in r.outcomes] == ["machine_accepted", "deduplicated", "machine_accepted"]
    assert r.outcomes[1].duplicate_of == r.insights[0].insight_id


def test_duplicate_candidate_and_pattern_ids():
    p = patterns_fixture()
    c = candidate(p)
    r = build_insights(p, provider=FakeProvider([c, c]))
    assert not r.insights and all(o.validation_issues[0].code == "duplicate_candidate_id" for o in r.outcomes)
    c["support_pattern_ids"].append(c["support_pattern_ids"][0])
    r = build_insights(p, provider=FakeProvider([c]))
    assert r.outcomes[0].validation_issues[0].code == "duplicate_pattern_id"


@pytest.mark.parametrize("change", ["quote", "metric", "source", "statement", "truth", "human", "market", "purchase", "kind", "scope", "links", "review"])
def test_serialized_tampering_rejected(change):
    p = patterns_fixture(with_context=True)
    data = build_insights(p, provider=FakeProvider([candidate(p)])).model_dump(mode="json")
    i = data["insights"][0]
    if change == "quote": i["evidence_refs"][0]["evidence_quote"] = "invented"
    if change == "metric": i["evidence_summary"]["comment_count"] = 200
    if change == "source": data["input_patterns"]["input_signals"]["records"][0]["source"]["text"] = "changed"
    if change == "statement": i["statement"]["text"] = "Customers will buy"
    if change == "truth": i["statement"]["truth_type"] = "HYPOTHESIS"
    if change == "human": i["verification"]["human_verified"] = True
    if change == "market": i["verification"]["market_validated"] = True
    if change == "purchase": i["verification"]["purchase_validated"] = True
    if change == "kind": i["evidence_kind"] = ["payment"]
    if change == "scope": i["scope"]["source_comment_ids"].append("invented")
    if change == "links": i["customer_profile_links"]["jobs"].append("invented")
    if change == "review": data["outcomes"][0]["semantic_review"]["candidate_hash"] = "stale"
    with pytest.raises(ValidationError): InsightsEnvelope.model_validate(data)


def test_serialization_roundtrip(tmp_path):
    p = patterns_fixture()
    r = build_insights(p, provider=FakeProvider([candidate(p)]))
    path = tmp_path / "insights.json"
    save_insights_json(r, path)
    assert load_insights_json(path) == r
    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == "v2.insights.2"


def test_broken_pattern_provenance_rejected_before_provider():
    p = patterns_fixture()
    p.patterns[0].evidence_refs[0].source_hash = "wrong"
    provider = Mock()
    with pytest.raises(ValidationError): build_insights(p, provider=provider)
    provider.propose.assert_not_called()


@pytest.mark.parametrize("mode,code", [("missing", "missing_semantic_review"), ("duplicate", "duplicate_review_id"),
                                     ("unknown", "missing_semantic_review"), ("support", "invalid_review_support")])
def test_review_id_or_support_mismatch(mode, code):
    p = patterns_fixture()
    provider = FakeProvider([candidate(p)])
    original = provider.review
    def response(items):
        payload = original(items)
        if mode == "missing": payload["reviews"] = []
        if mode == "duplicate": payload["reviews"] *= 2
        if mode == "unknown": payload["reviews"][0]["insight_candidate_id"] = "other"
        if mode == "support": payload["reviews"][0]["support_pattern_ids"] = ["invented"]
        return payload
    provider.review = response
    r = build_insights(p, provider=provider)
    assert not r.insights and r.outcomes[0].validation_issues[0].code == code


def test_empty_input_and_valid_zero_candidates_do_not_fail():
    p = build_patterns(SignalsEnvelope(model="synthetic", records=[]))
    provider = Mock(); provider.name = "offline"
    r = build_insights(p, provider=provider)
    provider.propose.assert_not_called()
    assert r.synthesis_status == "complete" and not r.insights
    p = patterns_fixture()
    assert not build_insights(p, provider=FakeProvider([])).outcomes


@pytest.mark.parametrize("where", ["propose", "review"])
def test_api_errors_visible_without_private_exception_body(where):
    p = patterns_fixture()
    provider = FakeProvider([candidate(p)])
    setattr(provider, where, Mock(side_effect=RuntimeError("private api secret")))
    r = build_insights(p, provider=provider)
    assert not r.insights and r.synthesis_status == "error"
    assert "private api secret" not in r.model_dump_json()


def test_cli_independent_and_overwrite_guard(tmp_path, monkeypatch, capsys):
    from tiktok_insight_miner.cli import main
    p = patterns_fixture()
    source = tmp_path / "patterns.json"
    save_patterns_json(p, source)
    monkeypatch.setattr(AnthropicInsights, "propose", lambda self, catalog: {"candidates": []})
    monkeypatch.setattr("sys.argv", ["tim", "build-insights", "--patterns", str(source)])
    main()
    assert "Insight candidates: machine_accepted=0; pending_human_review=0" in capsys.readouterr().out
    assert load_insights_json(tmp_path / "insights.json").synthesis_status == "complete"
    monkeypatch.setattr("sys.argv", ["tim", "build-insights", "--patterns", str(source), "-o", str(source)])
    with pytest.raises(SystemExit, match="overwrite"): main()


def test_closed_short_id_transport_unknown_is_not_repaired():
    p = patterns_fixture()
    client = Mock()
    raw = candidate(p, support_pattern_ids=["p999"])
    client.messages.create.return_value = SimpleNamespace(stop_reason="end_turn",
        content=[SimpleNamespace(type="text", text=json.dumps({"candidates": [raw]}))],
        usage=SimpleNamespace(cache_read_input_tokens=0))
    r = build_insights(p, provider=AnthropicInsights(client=client))
    assert not r.insights and r.outcomes[0].validation_issues[0].code == "unknown_pattern_id"


def rich_patterns():
    sources = [source_from_comment({"id": f"c{i}", "text": text, "author": "same-author"}) for i, text in enumerate([
        "Starting: rent is painful", "Operating: rent hurts profit", "Operating: rent is manageable"])]
    rows, _ = validate_batch(sources, {"results": [{"comment_id": s.comment_id, "signals": [{
        "category": "pains", "subcategory": "costs", "evidence_quote": s.text,
        "truth_type": "OBSERVED", "confidence": "high"}]} for s in sources]})
    signals = SignalsEnvelope(model="synthetic", records=rows)
    context_rows, _ = validate_context_batch(rows, {"results": [{"comment_id": s.comment_id, "contexts": [{
        "field": "life_or_business_stage", "evidence_quote": s.text.split(':')[0],
        "truth_type": "OBSERVED", "confidence": "high"}]} for s in sources]})
    contexts = ContextsEnvelope(model="synthetic", input_signals_hash=artifact_hash(signals), records=context_rows)
    provider = Mock(); provider.name = "fixture"
    def compare(catalog):
        ids = {c["comment_id"]: c["evidence_id"] for c in catalog if c["origin"] == "signal"}
        return {"relations": [dict(left=ids[a], right=ids[b], kind=kind) for a, b, kind in [
            ("c0", "c1", "variation"), ("c0", "c2", "contradiction"), ("c1", "c2", "contradiction")]]}
    provider.compare.side_effect = compare
    return build_patterns(signals, contexts, provider=provider)


def test_contradictions_variants_narrow_context_and_support_preserved():
    p = rich_patterns()
    pattern = next(x for x in p.patterns if x.pattern_type == "pains" and x.support.comment_count == 2)
    c = candidate(p, "Rent pressure is expressed in both starting and operating situations.",
                  support_pattern_ids=[pattern.pattern_id], relationship_type="single_pattern")
    i = build_insights(p, provider=FakeProvider([c])).insights[0]
    assert len(i.contradictions) == 2 and all(c.counter_ref.comment_id == "c2" for c in i.contradictions)
    assert i.evidence_summary.comment_count == 2 and i.evidence_summary.unique_authors == 1
    assert len(i.variations) == 2
    assert {v.label for v in i.scope.life_or_business_stage} == {"Starting", "Operating"}
    assert i.scope.source_comment_ids == ["c0", "c1"]


def test_cross_corpus_is_not_within_person_cooccurrence():
    p = rich_patterns()
    pain_ids = [x.pattern_id for x in p.patterns if x.pattern_type == "pains"]
    c = candidate(p, "The corpus contains differing experiences of rent pressure.",
                  support_pattern_ids=pain_ids, relationship_type="pattern_relationship")
    i = build_insights(p, provider=FakeProvider([c])).insights[0]
    assert i.scope.relationship_scope == "across_corpus" and i.scope.shared_comment_ids == []
    assert i.evidence_summary.comment_count == 3
    assert any("No comment supports all" in text for text in i.limitations)


def test_known_zero_metrics_remain_measured_zero():
    s = source_from_comment({"id": "zero", "text": "Rent is difficult"})
    s.likes = 0; s.reply_count = 0; s.snapshot_hash = s.expected_hash()
    rows, _ = validate_batch([s], {"results": [{"comment_id": "zero", "signals": [{
        "category": "pains", "subcategory": "costs", "evidence_quote": s.text,
        "truth_type": "OBSERVED", "confidence": "high"}]}]})
    p = build_patterns(SignalsEnvelope(model="synthetic", records=rows))
    e = build_evidence(p, [p.patterns[0].pattern_id])
    assert e.evidence_summary.total_likes == e.evidence_summary.total_replies == 0


def test_cli_rejection_exit_two_preserves_artifact(tmp_path, monkeypatch):
    from tiktok_insight_miner.cli import main
    p = patterns_fixture()
    path = tmp_path / "patterns.json"
    save_patterns_json(p, path)
    monkeypatch.setattr(AnthropicInsights, "propose", lambda self, catalog: {"candidates": [candidate(p, "Most customers will pay")]})
    monkeypatch.setattr("sys.argv", ["tim", "build-insights", "--patterns", str(path)])
    with pytest.raises(SystemExit) as exc: main()
    assert exc.value.code == 2
    assert load_insights_json(tmp_path / "insights.json").outcomes[0].status == "rejected"


def test_review_transport_maps_short_pattern_ids_without_mutating_input():
    p = patterns_fixture()
    from tiktok_insight_miner.insight_engine import pattern_catalog
    c = candidate(p)
    data = [{"candidate": c, "evidence": pattern_catalog(p), "scope": {}}]
    before = json.dumps(data)
    client = Mock()
    response = FakeProvider([]).review([{"candidate": {**c, "support_pattern_ids": ["p000", "p001"]}}])
    client.messages.create.return_value = SimpleNamespace(stop_reason="end_turn",
        content=[SimpleNamespace(type="text", text=json.dumps(response))], usage=SimpleNamespace(cache_read_input_tokens=0))
    result = AnthropicInsights(client=client).review(data)
    assert set(result["reviews"][0]["support_pattern_ids"]) == set(c["support_pattern_ids"])
    assert json.dumps(data) == before


def test_api_truncation_and_payload_limit_never_succeed():
    p = patterns_fixture()
    client = Mock()
    client.messages.create.return_value = SimpleNamespace(stop_reason="max_tokens", content=[], usage=SimpleNamespace(cache_read_input_tokens=0))
    r = build_insights(p, provider=AnthropicInsights(client=client))
    assert r.synthesis_status == "error" and not r.insights
    client.reset_mock()
    with pytest.raises(ValueError, match="limit 200"): AnthropicInsights(client=client).propose([{}] * 201)
    client.messages.create.assert_not_called()


def test_mixed_invalid_and_valid_candidate_keeps_valid_result():
    p = patterns_fixture()
    c = candidate(p)
    r = build_insights(p, provider=FakeProvider([{"invented": "data"}, c]))
    assert len(r.insights) == 1 and [o.status for o in r.outcomes] == ["rejected", "machine_accepted"]


def test_vietnamese_lowercase_letters_are_not_mistaken_for_proper_names():
    p = patterns_fixture()
    c = candidate(p, "Nhu cầu ổn định thu nhập được đặt cạnh áp lực tiền thuê.")
    assert len(build_insights(p, provider=FakeProvider([c])).insights) == 1


def test_statement_parts_trace_to_patterns_and_exact_output_spans():
    p = patterns_fixture()
    c = candidate(p, "Income stability is desired; rent pressure limits retained profit.")
    i = build_insights(p, provider=FakeProvider([c])).insights[0]
    assert len(i.statement_support) == 2
    assert all(set(part.support_pattern_ids).issubset(i.support_pattern_ids) for part in i.statement_support)
    assert ''.join(i.statement.text[part.start:part.end] for part in i.statement_support) == c["concise_statement"]


@pytest.mark.parametrize("mode", ["missing", "unknown_part", "unknown_pattern", "duplicate"])
def test_invalid_statement_part_support_rejected(mode):
    p = patterns_fixture()
    provider = FakeProvider([candidate(p)])
    original = provider.review
    def review(items):
        response = original(items)
        v = response["reviews"][0]
        if mode == "missing": v["part_support"] = []
        if mode == "unknown_part": v["part_support"][0]["part_id"] = "invented"
        if mode == "unknown_pattern": v["part_support"][0]["support_pattern_ids"] = ["invented"]
        if mode == "duplicate": v["part_support"] *= 2
        return response
    provider.review = review
    r = build_insights(p, provider=provider)
    assert not r.insights and r.outcomes[0].validation_issues[0].code == "invalid_part_support"


@pytest.mark.parametrize("mode", ["pass", "fail", "missing", "stale", "bad_support", "bad_part", "precheck", "dedupe"])
def test_machine_review_state_matches_usable_review(mode):
    p = patterns_fixture()
    c = candidate(p)
    provider = FakeProvider([c])
    if mode == "fail": provider.verdict_changes = {"supported": False, "reason_code": "overclaim"}
    if mode == "missing": provider.review = lambda items: {"reviews": []}
    if mode == "stale": provider.verdict_changes = {"insight_candidate_id": "unknown"}
    if mode == "bad_support": provider.verdict_changes = {"support_pattern_ids": ["unknown"]}
    if mode == "bad_part": provider.verdict_changes = {"part_support": []}
    if mode == "precheck": c["support_pattern_ids"] = ["unknown"]
    if mode == "dedupe": provider.candidates.append({**c, "insight_candidate_id": "i2"})
    r = build_insights(p, provider=provider)
    passed = mode in ("pass", "dedupe")
    assert all(o.machine_review_passed is passed for o in r.outcomes)
    assert all(i.verification.machine_review_passed and i.status == "pending_human_review" for i in r.insights)
    assert InsightsEnvelope.model_validate_json(r.model_dump_json()) == r
    data = r.model_dump(mode="json")
    data["outcomes"][0]["machine_review_passed"] = not passed
    with pytest.raises(ValidationError, match="machine_review_passed"):
        InsightsEnvelope.model_validate(data)


@pytest.mark.parametrize("change", ["no_refs", "source_false", "support_false", "machine_false", "legacy_field", "approved", "edited_and_approved", "rejected", "old_accepted"])
def test_candidate_support_and_pending_state_cannot_be_forged(change):
    p = patterns_fixture()
    data = build_insights(p, provider=FakeProvider([candidate(p)])).model_dump(mode="json")
    i = data["insights"][0]
    if change == "no_refs": i["evidence_refs"] = []
    if change == "source_false": i["verification"]["source_grounded"] = False
    if change == "support_false": i["verification"]["evidence_support_present"] = False
    if change == "machine_false": i["verification"]["machine_review_passed"] = False
    if change == "legacy_field": i["verification"]["evidence_backed"] = True
    if change in ("approved", "edited_and_approved", "rejected"): i["status"] = change
    if change == "old_accepted": data["outcomes"][0]["status"] = "accepted"
    with pytest.raises(ValidationError): InsightsEnvelope.model_validate(data)


def test_attached_evidence_does_not_certify_semantic_truth():
    p = patterns_fixture()
    # Deliberately fallible reviewer: plausible structural support cannot verify psychology.
    c = candidate(p, "The rent burden conceals a private fear of failure.")
    r = build_insights(p, provider=FakeProvider([c]))
    i = r.insights[0]
    assert i.evidence_refs and i.verification.evidence_support_present
    assert i.verification.machine_review_passed
    assert not any((i.verification.human_verified, i.verification.market_validated, i.verification.purchase_validated))
    assert i.status == "pending_human_review"


@pytest.mark.parametrize("version", ["v2.insights.1", "v2.insights.99"])
def test_old_or_unknown_insight_schema_has_clear_version_error(version, tmp_path):
    p = patterns_fixture()
    data = build_insights(p, provider=FakeProvider([candidate(p)])).model_dump(mode="json")
    data["schema_version"] = version
    for i in data["insights"]:
        i["verification"].pop("evidence_support_present")
        i["verification"].pop("machine_review_passed")
        i["verification"]["evidence_backed"] = True
    data["outcomes"][0]["status"] = "accepted"
    data["outcomes"][0].pop("machine_review_passed")
    path = tmp_path / "old-insights.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValidationError, match="Unsupported insight schema version; expected v2.insights.2"):
        load_insights_json(path)
    assert path.read_bytes() == before
