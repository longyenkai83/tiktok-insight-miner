"""Only explicitly synthetic human-approved fixtures; no real approvals or live API."""
import json
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from tests.unit.test_governance import sample, action
from tests.unit.test_insight_engine import FakeProvider, candidate
from tiktok_insight_miner.content_route_engine import (AnthropicContent, build_content_tree,
    checked_tree, extend_content_tree, new_content_tree)
from tiktok_insight_miner.content_route_models import ContentTree
from tiktok_insight_miner.content_selection import (SelectionAction, SelectionLedger, SelectedAnglesEnvelope,
    apply_selection, prepare_selection, select_angle, require_selected, save_tree, load_tree,
    prepare_selection_file, select_angle_file, load_selection, export_selection_file)
from tiktok_insight_miner.governance_engine import prepare_review, record_review, apply_reviews
from tiktok_insight_miner.governance_store import atomic_json
from tiktok_insight_miner.insight_engine import build_insights
from tiktok_insight_miner.pattern_engine import build_patterns
from tiktok_insight_miner.pattern_models import artifact_hash
from tiktok_insight_miner.signal_extractor import source_from_comment, validate_batch
from tiktok_insight_miner.signal_models import SignalsEnvelope


def verified_fixture():
    q = prepare_review(sample())
    q = record_review(q, action(q))
    return apply_reviews(q), q


def text(value):
    return dict(text=value, claim_kind="general_explanatory", needs_external_evidence=True)


class ContentProvider:
    name = "synthetic-content-provider"
    def generate(self, stage, payload, schema):
        parent = payload["parent"]
        result = []
        for n in range(min(payload["requested_count"], 2)):
            if stage == "opportunities":
                result.append(dict(local_id=f"o{n}", verified_insight_id=parent["verified_insight_id"],
                    statement=text(["Discuss the tension between rent and retained income.",
                                    "Explore stability as a lens for thinking about tradeoffs."][n]),
                    purpose="decision_support", customer_value=text("Clarify a useful decision question.")))
            elif stage == "topics":
                result.append(dict(local_id=f"t{n}", content_opportunity_id=parent["content_opportunity_id"],
                    title=text(["Understanding rent pressure", "Considering stability"][n]),
                    description=text(["Cost pressure and retained income as a subject area.",
                                      "Planning choices through the lens of stability."][n]),
                    customer_value=text("Explore the choices without claiming a proven solution.")))
            else:
                result.append(dict(local_id=f"a{n}", topic_id=parent["topic_id"],
                    title=text(["Looking beyond the rent bill", "Making room for stability"][n]),
                    angle_type=["comparison", "question_answer"][n],
                    core_argument=text(["Compare the rent burden with what remains from income.",
                                        "Ask which decisions could help frame a discussion of stability."][n]),
                    belief_before=text(["Focus on the rent bill in isolation.", "Treat uncertainty as something to ignore."][n]),
                    belief_after=text(["Consider retained income alongside rent.", "Make uncertainty a visible decision question."][n]),
                    opening_direction=text("Begin with a clearly hypothetical decision question."),
                    customer_value=text("A proposed way to think through the tension."), value_scene={}))
        return {"candidates": result}


def tree_fixture():
    v, q = verified_fixture()
    return build_content_tree(v, q, project_id="synthetic", run_id="test-run",
                              opportunities=2, topics=2, angles=2, provider=ContentProvider()), q


def choose(ledger, decision="selected", **changes):
    tree = ledger.trees[-1]
    a = tree.angles[0]
    return SelectionAction(**dict(request_id="synthetic-choice", tree_hash=artifact_hash(tree),
        angle_id=a.angle_id, angle_hash=artifact_hash(a), decision=decision,
        reviewer_id="synthetic-human", human_attested=True, rationale="Synthetic lens reviewed", **changes))


def test_non_verified_or_stale_input_fails_before_ai():
    source = sample()
    q = prepare_review(source)
    with pytest.raises(ValueError): new_content_tree(source, q, project_id="p", run_id="r")
    v, q = verified_fixture()
    revoked = record_review(q, action(q, "rejected", request_id="revoke"))
    provider = Mock()
    with pytest.raises(ValueError, match="stale"):
        build_content_tree(v, revoked, project_id="p", run_id="r", provider=provider)
    provider.generate.assert_not_called()


def test_complete_hierarchy_is_proposed_and_keeps_customer_truth_separate():
    tree, q = tree_fixture()
    assert (len(tree.content_opportunities), len(tree.topics), len(tree.angles)) == (2, 4, 8)
    for obj in [*tree.content_opportunities, *tree.topics, *tree.angles]:
        assert obj.truth_type == "PROPOSED" and obj.status == "generated"
        assert obj.customer_truth.truth_type == "DERIVED"
        assert obj.verified_insight_id == tree.verified_input.verified_insights[0].verified_insight_id
        assert obj.evidence_refs == tree.verified_input.verified_insights[0].evidence_refs
        assert obj.created_at.tzinfo is not None and obj.project_id == "synthetic"
    assert tree.angles[0].schema_version == "v2.angles.1"
    assert tree.topics[0].schema_version == "v2.topics.1"
    assert tree.content_opportunities[0].schema_version == "v2.content-opportunities.1"
    assert tree.angles[0].core_argument.needs_external_evidence
    assert not tree.validation_issues


@pytest.mark.parametrize("mode,code", [("unknown", "unknown_upstream_id"), ("extra_evidence", "invalid_candidate_schema"),
    ("script", "invalid_candidate_schema"), ("product", "invalid_candidate_schema"),
    ("truth", "invalid_candidate_schema"), ("language", "invalid_candidate_schema"),
    ("statistics", "unsupported_statistics"), ("research", "fake_research_or_case"),
    ("quote", "fabricated_quote"), ("demographic", "demographic_outside_scope"),
    ("external_false", "invalid_candidate_schema")])
def test_bad_angle_transport_rejected(mode, code):
    tree, q = tree_fixture()
    provider = ContentProvider()
    generate = provider.generate
    def bad(stage, payload, schema):
        raw = generate(stage, payload, schema)
        item = raw["candidates"][0]
        if mode == "unknown": item["topic_id"] = "unknown"
        if mode == "extra_evidence": item["evidence_refs"] = ["invented"]
        if mode == "script": item["final_script"] = "full article"
        if mode == "product": item["product_opportunity"] = "new product"
        if mode == "truth": item["truth_type"] = "OBSERVED"
        if mode == "language": item["language_bank"] = ["generated hook phrase"]
        if mode == "statistics": item["core_argument"] = text("85% of customers want stable income")
        if mode == "research": item["core_argument"] = text("McKinsey says rent determines success")
        if mode == "quote": item["title"] = text('Customers say "rent is impossible"')
        if mode == "demographic": item["title"] = text("Women need income stability")
        if mode == "external_false": item["core_argument"]["needs_external_evidence"] = False
        return {"candidates": [item]}
    provider.generate = bad
    updated = extend_content_tree(tree, q, stage="angles", parent_id=tree.topics[0].topic_id, provider=provider)
    assert len(updated.angles) == len(tree.angles)
    assert updated.validation_issues[-1].code == code


def test_unknown_parent_rejected_without_provider_call():
    tree, q = tree_fixture()
    provider = Mock()
    with pytest.raises(ValueError, match="unknown parent"):
        extend_content_tree(tree, q, stage="topics", parent_id="unknown", provider=provider)
    provider.generate.assert_not_called()


def test_duplicate_arguments_deduped_even_with_different_headlines():
    tree, q = tree_fixture()
    provider = ContentProvider()
    original = provider.generate
    def renamed(stage, payload, schema):
        r = original(stage, payload, schema)
        r["candidates"][0]["title"] = text("A newly renamed headline")
        return r
    provider.generate = renamed
    updated = extend_content_tree(tree, q, stage="angles", parent_id=tree.topics[0].topic_id, count=10, provider=provider)
    assert len(updated.angles) == 8
    assert [i.code for i in updated.validation_issues] == ["duplicate_proposal", "duplicate_proposal"]
    assert updated.batches[-1].requested_count == 10  # Not a mandatory output quota.


def test_literal_language_and_value_scene_roles():
    source = source_from_comment({"id": "synthetic", "text": "I want stable income but rent consumes my profit; rent feels like a weight."})
    records, _ = validate_batch([source], {"results": [{"comment_id": "synthetic", "signals": [
        dict(category=cat, subcategory=sub, evidence_quote=quote, truth_type="OBSERVED", confidence="high")
        for cat, sub, quote in [("jobs", "functional", "I want stable income"),
            ("pains", "costs", "rent consumes my profit"), ("language", "emotional_wording", "rent feels like a weight")]]}]})
    p = build_patterns(SignalsEnvelope(model="synthetic", records=records))
    c = candidate(p, support_pattern_ids=[p2.pattern_id for p2 in p.patterns], relationship_type="pattern_relationship")
    raw = build_insights(p, provider=FakeProvider([c]))
    q = prepare_review(raw); q = record_review(q, action(q)); v = apply_reviews(q)
    tree = build_content_tree(v, q, project_id="p", run_id="r", provider=ContentProvider())
    assert tree.angles[0].language_bank[0].evidence_quote == "rent feels like a weight"
    pain = next(r for r in v.verified_insights[0].evidence_refs if r.signal_path.startswith("pains."))
    provider = ContentProvider()
    original = provider.generate
    def scene(stage, payload, schema):
        r = original(stage, payload, schema); item = r["candidates"][0]
        item["core_argument"] = text("Contrast the language of burden with the wish for steadiness.")
        item["value_scene"] = {"current_struggle": {"evidence_id": pain.evidence_id},
            "desired_future": {"proposed": text("Imagine a more manageable future, as hypothetical framing.")}}
        return {"candidates": [item]}
    provider.generate = scene
    updated = extend_content_tree(tree, q, stage="angles", parent_id=tree.topics[0].topic_id, provider=provider)
    a = updated.angles[-1]
    assert a.value_scene.current_struggle.text == pain.evidence_quote
    assert a.value_scene.desired_future.kind == "proposed_framing"
    assert a.value_scene.desired_future.framing.truth_type == "PROPOSED"
    def invalid(stage, payload, schema):
        r = scene(stage, payload, schema)
        r["candidates"][0]["value_scene"]["desired_future"] = {"evidence_id": pain.evidence_id}
        return r
    provider.generate = invalid
    rejected = extend_content_tree(tree, q, stage="angles", parent_id=tree.topics[0].topic_id, provider=provider)
    assert rejected.validation_issues[-1].code == "unsupported_scene_role"


@pytest.mark.parametrize("change", ["truth", "evidence", "language", "customer_truth", "contradictions", "scene"])
def test_tree_tampering_cannot_create_evidence_or_truth(change):
    tree, _ = tree_fixture()
    data = tree.model_dump(mode="json")
    a = data["angles"][0]
    if change == "truth": a["truth_type"] = "DERIVED"
    if change == "evidence": a["evidence_refs"][0]["source_hash"] = "invented"
    if change == "language": a["language_bank"] = a["evidence_refs"]
    if change == "customer_truth": a["customer_truth"]["text"] = "Invented desire"
    if change == "contradictions": a["contradictions"] = [{"made_up": "data"}]
    if change == "scene": a["value_scene"]["desired_future"] = {"kind": "source_wording", "text": "made up"}
    with pytest.raises(ValidationError): ContentTree.model_validate(data)


@pytest.mark.parametrize("decision,count", [("selected", 1), ("rejected", 0), ("deferred", 0)])
def test_human_selection_required(decision, count):
    tree, q = tree_fixture()
    ledger = prepare_selection(tree, q)
    assert not ledger.events and not apply_selection(ledger, q).selected_angles
    a = choose(ledger, decision)
    decided = select_angle(ledger, q, a)
    assert not ledger.events
    assert select_angle(decided, q, a) == decided
    result = apply_selection(decided, q)
    assert len(result.selected_angles) == count
    assert require_selected(result, decided, q) == result.selected_angles
    assert SelectedAnglesEnvelope.model_validate_json(result.model_dump_json()) == result


def test_selection_history_revocation_and_stale_projection():
    tree, q = tree_fixture()
    ledger = prepare_selection(tree, q)
    first = select_angle(ledger, q, choose(ledger))
    exported = apply_selection(first, q)
    a = choose(first, "rejected").model_copy(update={"request_id": "second"})
    revoked = select_angle(first, q, a)
    assert revoked.events[:1] == first.events and not apply_selection(revoked, q).selected_angles
    with pytest.raises(ValueError, match="stale"): require_selected(exported, revoked, q)
    bad = revoked.model_dump(mode="json"); bad["events"][0]["action"]["reviewer_id"] = "forged"
    with pytest.raises(ValidationError): SelectionLedger.model_validate(bad)


def test_ledger_change_blocks_generation_selection_and_export():
    tree, q = tree_fixture()
    revoked = record_review(q, action(q, "rejected", request_id="later"))
    ledger = prepare_selection(tree, q)
    for call in (lambda: checked_tree(tree, revoked), lambda: select_angle(ledger, revoked, choose(ledger)),
                 lambda: apply_selection(ledger, revoked)):
        with pytest.raises(ValueError, match="stale"): call()


def test_files_are_atomic_versioned_and_do_not_autoselect(tmp_path):
    tree, q = tree_fixture()
    p = tmp_path / "tree.json"; history = tmp_path / "selections.json"; output = tmp_path / "selected.json"
    save_tree(tree, p, q)
    assert load_tree(p) == tree
    with pytest.raises(ValueError, match="changed"): save_tree(tree, p, q)
    ledger = prepare_selection_file(tree, q, history)
    assert prepare_selection_file(tree, q, history) == ledger
    selected = select_angle_file(history, q, choose(ledger), expected_history_hash=artifact_hash(ledger))
    assert load_selection(history) == selected
    result = export_selection_file(history, output, q)
    before = output.read_bytes(); export_selection_file(history, output, q)
    assert output.read_bytes() == before and len(result.selected_angles) == 1


def test_cli_offline_workflow(tmp_path, monkeypatch):
    from tiktok_insight_miner.cli import main
    v, q = verified_fixture()
    vp, qp, tp, sp, op = [tmp_path / n for n in ("verified.json", "reviews.json", "tree.json", "selections.json", "selected.json")]
    atomic_json(vp, v); atomic_json(qp, q)
    monkeypatch.setattr(AnthropicContent, "generate", ContentProvider.generate)
    def run(args):
        monkeypatch.setattr("sys.argv", ["tim", *args]); main()
    run(["build-content-tree", "--verified-insights", str(vp), "--reviews", str(qp), "--project-id", "p", "--run-id", "r", "-o", str(tp)])
    base = ["--tree", str(tp), "--reviews", str(qp), "--selections", str(sp)]
    run(["prepare-content-selection", *base])
    ledger = load_selection(sp); a = choose(ledger)
    assert not ledger.events
    run(["select-content-angle", *base, "--angle-id", a.angle_id, "--angle-hash", a.angle_hash,
         "--tree-hash", a.tree_hash, "--request-id", "cli-choice", "--reviewer", "synthetic-human",
         "--confirm-human", "--decision", "selected"])
    run(["export-content-selection", *base, "-o", str(op)])
    assert len(SelectedAnglesEnvelope.model_validate_json(op.read_text(encoding="utf-8")).selected_angles) == 1


def test_streamlit_content_generation_and_selection(tmp_path):
    from streamlit.testing.v1 import AppTest
    from tiktok_insight_miner.governance_ui import review_workspace
    v, q = verified_fixture()
    source = review_workspace(tmp_path, "customer-intelligence")
    atomic_json(source / "insight_reviews.json", q)
    atomic_json(source / "verified_insights.json", v)
    script = ("from pathlib import Path\n"
              "from tests.unit.test_content_route import ContentProvider\n"
              "from tiktok_insight_miner.content_route_ui import render_content_route\n"
              f"render_content_route(Path({str(tmp_path)!r}), 'synthetic-reviewer', provider=ContentProvider())\n")
    app = AppTest.from_string(script, default_timeout=60).run()
    def labeled(elements, label): return next(e for e in elements if e.label == label)
    for label in ["Tạo Content Opportunities", "Mở rộng Topics", "Bung 10 góc"]:
        assert not app.exception and not app.error
        labeled(app.button, label).click().run()
    assert not app.exception and not app.error
    folder = tmp_path / "v2-content-route" / "customer-intelligence" / "content-research"
    ledger = load_selection(folder / "content_selections.json")
    assert not ledger.events and len(ledger.trees[-1].angles) == 2
    labeled(app.selectbox, "Quyết định góc").select("selected")
    labeled(app.checkbox, "Đây là lựa chọn của tôi sau khi xem góc và bằng chứng.").check()
    labeled(app.button, "Lưu lựa chọn góc").click().run()
    assert not app.exception and not app.error
    ledger = load_selection(folder / "content_selections.json")
    assert len(apply_selection(ledger, q).selected_angles) == 1
    app = AppTest.from_string(script, default_timeout=60).run()
    assert not app.exception and not app.error
    assert len(load_selection(folder / "content_selections.json").events) == 1


def test_failed_generation_keeps_history_without_private_exception():
    v, q = verified_fixture()
    tree = new_content_tree(v, q, project_id="p", run_id="r")
    provider = Mock(); provider.name = "synthetic"
    provider.generate.side_effect = RuntimeError("private-secret-body")
    updated = extend_content_tree(tree, q, stage="opportunities",
        parent_id=v.verified_insights[0].verified_insight_id, provider=provider)
    assert not updated.content_opportunities
    assert updated.validation_issues[0].code == "generation_error"
    assert "private-secret-body" not in updated.model_dump_json()


def test_invalid_human_selection_and_stale_writer(tmp_path):
    tree, q = tree_fixture()
    path = tmp_path / "selection.json"
    ledger = prepare_selection_file(tree, q, path)
    a = choose(ledger)
    bad = a.model_dump(); bad["human_attested"] = False
    with pytest.raises(ValidationError): SelectionAction.model_validate(bad)
    bad = a.model_dump(); bad["angle_hash"] = "forged"
    with pytest.raises(ValueError): select_angle(ledger, q, SelectionAction.model_validate(bad))
    selected = select_angle_file(path, q, a, expected_history_hash=artifact_hash(ledger))
    other = a.model_copy(update={"request_id": "another"})
    with pytest.raises(ValueError, match="history changed"):
        select_angle_file(path, q, other, expected_history_hash=artifact_hash(ledger))
    assert load_selection(path) == selected


def test_no_verified_records_means_no_generation():
    q = prepare_review(sample()); v = apply_reviews(q)
    provider = Mock(); provider.name = "unused"
    tree = build_content_tree(v, q, project_id="p", run_id="r", provider=provider)
    assert not tree.angles and not tree.content_opportunities
    provider.generate.assert_not_called()


@pytest.mark.parametrize("mode,code", [("unknown_insight", "unknown_upstream_id"),
                                      ("duplicate_id", "duplicate_local_id")])
def test_opportunity_transport_closed_ids(mode, code):
    v, q = verified_fixture()
    tree = new_content_tree(v, q, project_id="p", run_id="r")
    provider = ContentProvider(); original = provider.generate
    def invalid(stage, payload, schema):
        result = original(stage, payload, schema)
        for item in result["candidates"]:
            if mode == "unknown_insight": item["verified_insight_id"] = "unknown"
            else: item["local_id"] = "duplicate"
        return result
    provider.generate = invalid
    result = extend_content_tree(tree, q, stage="opportunities", count=2,
        parent_id=v.verified_insights[0].verified_insight_id, provider=provider)
    assert not result.content_opportunities
    assert [i.code for i in result.validation_issues] == [code, code]


def test_changed_tree_requires_fresh_human_selection():
    tree, q = tree_fixture()
    old = prepare_selection(tree, q)
    old = select_angle(old, q, choose(old))
    updated = extend_content_tree(tree, q, stage="angles", parent_id=tree.topics[0].topic_id,
                                  provider=ContentProvider())
    new = prepare_selection(updated, q, old)
    assert new.events == old.events and len(new.trees) == 2
    assert not apply_selection(new, q).selected_angles
    with pytest.raises(ValueError): select_angle(new, q, choose(old))
