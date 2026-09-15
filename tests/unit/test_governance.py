"""Synthetic human workflow tests; never record decisions on customer samples."""
import json
from datetime import timedelta
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from tests.unit.test_insight_engine import FakeProvider, candidate, patterns_fixture
from tiktok_insight_miner.governance_engine import (apply_reviews, checked_queue, prepare_review,
    record_review, require_verified, review_rows)
from tiktok_insight_miner.governance_models import (PriorityDecision, ReviewAction,
    ReviewQueue, VerifiedInsightsEnvelope)
from tiktok_insight_miner.governance_store import (atomic_json, apply_review_file, file_lock,
    load_reviews, load_verified, prepare_review_file, record_review_file, _save_append_only)
from tiktok_insight_miner.governance_ui import candidate_view, render_preview, review_workspace
from tiktok_insight_miner.insight_engine import build_insights, save_insights_json
from tiktok_insight_miner.pattern_models import artifact_hash


def sample():
    p = patterns_fixture(with_context=True)
    return build_insights(p, provider=FakeProvider([candidate(p)]))


def action(queue, decision="approved", **changes):
    c = queue.snapshots[-1].insights[0]
    data = dict(request_id="request-1", candidate_insight_id=c.insight_id,
        candidate_hash=artifact_hash(c), decision=decision, reviewer_id="synthetic-reviewer",
        human_attested=True, rationale="Faithful within this synthetic corpus.")
    if decision == "edited_and_approved":
        data["edited_statement"] = "The cited speaker wants steady income while describing rent pressure."
    return ReviewAction(**{**data, **changes})


def test_prepare_and_apply_never_approve_or_assign_priority():
    source = sample()
    before = source.model_dump_json()
    q = prepare_review(source)
    assert not q.events and not apply_reviews(q).verified_insights
    assert review_rows(q)[0]["decision"] == "pending"
    assert review_rows(q)[0]["priority"].priority_status == "unassessed"
    assert prepare_review(source, q) == q
    assert source.model_dump_json() == before


@pytest.mark.parametrize("decision", ["approved", "edited_and_approved", "rejected", "deferred"])
def test_each_explicit_human_decision(decision):
    q = prepare_review(sample())
    original = q.model_dump_json()
    a = action(q, decision)
    reviewed = record_review(q, a)
    v = apply_reviews(reviewed)
    assert q.model_dump_json() == original
    event = reviewed.events[0]
    assert event.original_statement == q.snapshots[-1].insights[0].statement.text
    assert event.action.reviewer_id == "synthetic-reviewer"
    if decision in ("rejected", "deferred"):
        assert not v.verified_insights and event.approved_statement is None
    else:
        i = v.verified_insights[0]
        assert i.verification.human_verified
        assert not i.verification.market_validated and not i.verification.purchase_validated
        assert i.verification.machine_review_scope == "source_candidate_only"
        assert i.statement.truth_type == "DERIVED"
        assert i.statement.text == (a.edited_statement or event.original_statement)
        assert i.statement.statement_origin == ("human_edited" if a.edited_statement else "machine_approved")
        c = q.snapshots[-1].insights[0]
        for field in ("evidence_refs", "scope", "contradictions", "variations", "limitations", "support_pattern_ids"):
            assert getattr(i, field) == getattr(c, field)
        assert require_verified(v, reviewed) == v.verified_insights


@pytest.mark.parametrize("text,code", [
    ("80% of customers struggle with rent", "unsupported_numeric_claim"),
    ("We should build a rent calculator", "solution_leak"),
    ("Create a content script about rent", "solution_leak"),
    ("Women need income stability despite rent pressure", "unsupported_demographic"),
    ('Customers say "rent is unaffordable"', "quote_in_statement"),
    ("Most customers will pay to eliminate pressure", "market_generalization"),
])
def test_human_edit_integrity_guards(text, code):
    q = prepare_review(sample())
    with pytest.raises(ValueError, match=code):
        record_review(q, action(q, "edited_and_approved", edited_statement=text))
    assert not q.events


def test_human_semantics_not_vetoed_by_ai_or_shallow_label_guard(monkeypatch):
    q = prepare_review(sample())
    monkeypatch.setattr("tiktok_insight_miner.insight_engine.AnthropicInsights.review", Mock(side_effect=AssertionError("AI review forbidden")))
    text = q.snapshots[-1].input_patterns.patterns[0].label
    reviewed = record_review(q, action(q, "edited_and_approved", edited_statement=text))
    assert apply_reviews(reviewed).verified_insights[0].statement.text == text


@pytest.mark.parametrize("extra", ["evidence_refs", "source_hash", "scope", "support_pattern_ids", "human_verified"])
def test_review_action_cannot_edit_evidence(extra):
    q = prepare_review(sample())
    data = action(q).model_dump()
    data[extra] = "invented"
    with pytest.raises(ValidationError): ReviewAction.model_validate(data)


@pytest.mark.parametrize("field,value", [("human_attested", False), ("reviewer_id", " "),
    ("rationale", ""), ("decision", "verified"), ("edited_statement", "unauthorized edit")])
def test_review_requires_explicit_valid_human_action(field, value):
    q = prepare_review(sample())
    data = action(q).model_dump()
    data[field] = value
    with pytest.raises(ValidationError): ReviewAction.model_validate(data)


def test_priority_need_is_human_assessment_only():
    q = prepare_review(sample())
    assert not review_rows(q, "Priority Needs")
    priority = PriorityDecision(priority_status="priority_need", important="high", urgent="unknown")
    reviewed = record_review(q, action(q, priority=priority))
    i = apply_reviews(reviewed).verified_insights[0]
    assert i.priority == priority and i.priority.frequent == "unknown"
    assert len(review_rows(reviewed, "Priority Needs")) == 1
    for decision in ("rejected", "deferred"):
        with pytest.raises(ValidationError): action(q, decision, priority=priority)


def test_reapplication_retry_and_revision_history_are_idempotent():
    q = prepare_review(sample())
    a = action(q)
    first = record_review(q, a)
    assert record_review(first, a) == first
    v1 = apply_reviews(first)
    assert apply_reviews(first).model_dump_json() == v1.model_dump_json()
    second = record_review(first, action(first, "edited_and_approved", request_id="request-2"))
    assert second.events[:1] == first.events
    v2 = apply_reviews(second).verified_insights[0]
    assert v2.revision == 2 and v2.supersedes == v1.verified_insights[0].verified_insight_id
    assert second.events[1].previous_event_id == first.events[0].review_event_id
    rejected = record_review(second, action(second, "rejected", request_id="request-3"))
    assert len(rejected.events) == 3 and not apply_reviews(rejected).verified_insights
    with pytest.raises(ValueError, match="stale verified"):
        require_verified(v1, rejected)


def test_changed_upstream_snapshot_cannot_inherit_approval():
    source = sample()
    q = prepare_review(source)
    reviewed = record_review(q, action(q))
    # Even a changed analysis version with unchanged candidate text needs fresh review.
    changed = source.model_copy(deep=True)
    changed.generated_at += timedelta(seconds=1)
    next_q = prepare_review(changed, reviewed)
    assert len(next_q.snapshots) == 2 and next_q.events == reviewed.events
    assert review_rows(next_q)[0]["decision"] == "pending"
    assert not apply_reviews(next_q).verified_insights
    with pytest.raises(ValueError, match="historical analysis"):
        prepare_review(source, next_q)
    with pytest.raises(ValueError, match="request ID"):
        record_review(next_q, action(next_q))


def test_changed_candidate_hash_rejects_stale_review():
    q = prepare_review(sample())
    with pytest.raises(ValueError, match="stale candidate"):
        record_review(q, action(q, candidate_hash="stale"))


def test_changed_statement_returns_to_pending_without_old_approval():
    q = prepare_review(sample())
    reviewed = record_review(q, action(q))
    p = patterns_fixture(with_context=True)
    changed = build_insights(p, provider=FakeProvider([candidate(p,
        "Rent pressure accompanies the wish for a more stable income.")]))
    updated = prepare_review(changed, reviewed)
    assert updated.events == reviewed.events
    assert not apply_reviews(updated).verified_insights
    assert review_rows(updated)[0]["decision"] == "pending"


@pytest.mark.parametrize("decision_label,expected", [("Approve", "approved"), ("Edit + Approve", "edited_and_approved"),
                                                    ("Reject", "rejected"), ("Defer", "deferred")])
def test_streamlit_human_action_flow(tmp_path, decision_label, expected):
    from streamlit.testing.v1 import AppTest
    folder = review_workspace(tmp_path, "customer-intelligence")
    path = folder / "insight_reviews.json"
    prepare_review_file(sample(), path)
    script = ("from pathlib import Path\nfrom tiktok_insight_miner.governance_ui import render_human_review\n"
              f"render_human_review(Path({str(tmp_path)!r}), 'synthetic-reviewer')\n")
    app = AppTest.from_string(script, default_timeout=20).run()
    assert not app.exception
    def labeled(elements, label): return next(e for e in elements if e.label == label)
    # Rendering, expanding evidence and selecting an action never itself writes a decision.
    labeled(app.selectbox, "Hành động").select(decision_label)
    labeled(app.text_area, "Lý do / ghi chú (bắt buộc)").input("Checked synthetic evidence.")
    if expected == "edited_and_approved":
        labeled(app.text_area, "Statement mới (chỉ dùng cho Edit + Approve)").input(
            "The cited speaker wants stable income while rent reduces retained profit.")
    labeled(app.checkbox, "Tôi là người đưa ra quyết định này và đã xem bằng chứng.").check()
    labeled(app.button, "Ghi quyết định của tôi").click().run()
    assert not app.exception
    q = load_reviews(path)
    assert len(q.events) == 1 and q.events[0].action.decision == expected
    # A fresh session also proves the decision is durable, not just session_state.
    app = AppTest.from_string(script, default_timeout=20).run()
    assert not app.exception
    labeled(app.button, "Cập nhật verified_insights.json từ lịch sử").click().run()
    assert not app.exception
    verified = load_verified(folder / "verified_insights.json")
    assert len(verified.verified_insights) == int(expected in ("approved", "edited_and_approved"))


@pytest.mark.parametrize("change", ["event_text", "event_order", "source", "reviewer", "evidence", "priority", "human", "market", "purchase", "truth"])
def test_persisted_ledger_and_verified_tampering_rejected(change):
    q = prepare_review(sample())
    data = apply_reviews(record_review(q, action(q))).model_dump(mode="json")
    e = data["review_history"]["events"][0]
    i = data["verified_insights"][0]
    if change == "event_text": e["approved_statement"] = "invented"
    if change == "event_order": e["sequence"] = 5
    if change == "source": data["review_history"]["snapshots"][0]["input_patterns"]["input_signals"]["records"][0]["source"]["text"] = "invented"
    if change == "reviewer": e["action"]["reviewer_id"] = "other"
    if change == "evidence": i["evidence_refs"][0]["source_hash"] = "invented"
    if change == "priority": i["priority"]["priority_status"] = "priority_need"
    if change == "human": i["verification"]["human_verified"] = False
    if change == "market": i["verification"]["market_validated"] = True
    if change == "purchase": i["verification"]["purchase_validated"] = True
    if change == "truth": i["statement"]["truth_type"] = "OBSERVED"
    with pytest.raises(ValidationError): VerifiedInsightsEnvelope.model_validate(data)


def test_downstream_rejects_machine_or_standalone_boolean():
    source = sample()
    q = prepare_review(source)
    for value in (source, source.insights[0], {"human_verified": True}):
        with pytest.raises(ValueError, match="downstream requires"): require_verified(value, q)


def test_atomic_store_roundtrip_and_stale_writer(tmp_path):
    p = tmp_path / "insight_reviews.json"
    q = prepare_review_file(sample(), p)
    old_hash = artifact_hash(q)
    a = action(q)
    first = record_review_file(p, a, expected_history_hash=old_hash)
    assert record_review_file(p, a, expected_history_hash=old_hash) == first
    with pytest.raises(ValueError, match="history changed"):
        record_review_file(p, action(q, request_id="other"), expected_history_hash=old_hash)
    assert load_reviews(p) == first
    output = tmp_path / "verified_insights.json"
    result = apply_review_file(p, output)
    assert load_verified(output) == result
    before = output.read_bytes()
    apply_review_file(p, output)
    assert output.read_bytes() == before
    with pytest.raises(ValueError, match="append-only"): _save_append_only(p, q, first)
    assert load_reviews(p) == first


def test_interrupted_atomic_write_keeps_history_and_cleans_temp(tmp_path, monkeypatch):
    p = tmp_path / "reviews.json"
    q = prepare_review_file(sample(), p)
    before = p.read_bytes()
    monkeypatch.setattr("tiktok_insight_miner.governance_store.os.replace", Mock(side_effect=OSError("interrupted")))
    with pytest.raises(OSError): record_review_file(p, action(q), expected_history_hash=artifact_hash(q))
    assert p.read_bytes() == before
    assert not list(tmp_path.glob(".review-*.tmp"))


def test_os_lock_blocks_concurrent_writer(tmp_path):
    p = tmp_path / "reviews.json"
    with file_lock(p):
        with pytest.raises(ValueError, match="busy"):
            with file_lock(p): pass


def test_no_overwrite_of_original_source_or_history(tmp_path):
    source = sample()
    source_path, reviews_path = tmp_path / "insights.json", tmp_path / "reviews.json"
    save_insights_json(source, source_path)
    prepare_review_file(source, reviews_path)
    before = source_path.read_bytes()
    with pytest.raises(ValidationError): apply_review_file(reviews_path, source_path)
    assert source_path.read_bytes() == before
    with pytest.raises(ValueError, match="overwrite"): apply_review_file(reviews_path, reviews_path)


def test_cli_prepare_record_apply(tmp_path, monkeypatch, capsys):
    from tiktok_insight_miner.cli import main
    source_path, reviews_path, output = [tmp_path / f for f in ("insights.json", "reviews.json", "verified.json")]
    save_insights_json(sample(), source_path)
    def run(args):
        monkeypatch.setattr("sys.argv", ["tim", *args])
        main()
    run(["prepare-insight-review", "--insights", str(source_path), "-o", str(reviews_path)])
    q = load_reviews(reviews_path)
    assert not q.events
    run(["apply-insight-review", "--reviews", str(reviews_path), "-o", str(output)])
    assert not load_verified(output).verified_insights
    a = action(q)
    run(["record-insight-review", "--reviews", str(reviews_path), "--candidate-id", a.candidate_insight_id,
         "--candidate-hash", a.candidate_hash, "--reviewer", "synthetic-reviewer", "--confirm-human",
         "--request-id", "cli-1", "--decision", "approved", "--rationale", "Reviewed synthetic corpus"])
    run(["apply-insight-review", "--reviews", str(reviews_path), "-o", str(output)])
    assert len(load_verified(output).verified_insights) == 1


def test_ui_helpers_filters_preview_and_safe_workspace(tmp_path):
    q = prepare_review(sample())
    c = q.snapshots[-1].insights[0]
    view = candidate_view(q, c)
    assert view["representative_quotes"] and view["context_count"]
    assert view["representative_quotes"][0]["quote"] in view["representative_quotes"][0]["source_text"]
    preview = render_preview(q)
    assert "TẠI SAO MÁY NÓI VẬY?" in preview and "Decision: pending" in preview
    for decision, label in [("approved", "Approved"), ("rejected", "Rejected"), ("deferred", "Deferred")]:
        r = record_review(q, action(q, decision))
        assert len(review_rows(r, label)) == 1 and not review_rows(r, "Pending")
    assert review_workspace(tmp_path, "research-1").parent == tmp_path / "v2-human-review"
    for invalid in ("../secret", "C:/temp", "../", "", "a/b"):
        with pytest.raises(ValueError): review_workspace(tmp_path, invalid)
