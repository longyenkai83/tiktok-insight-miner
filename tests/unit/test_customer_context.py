"""Offline Phase 2 behavior and compatibility tests; all examples are synthetic."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import anthropic
import httpx
import pytest
from pydantic import ValidationError

from tiktok_insight_miner.customer_context_models import (
    CONTEXT_FIELDS, ContextCandidate, ContextCandidateBatch, ContextsEnvelope, CustomerIdentity,
)
from tiktok_insight_miner.customer_context_extractor import (
    SYSTEM_PROMPT, extract_customer_context, load_contexts_json, resolve_context_model,
    save_contexts_json, validate_context_batch,
)
from tiktok_insight_miner.signal_extractor import load_signals_json, save_signals_json, source_from_comment
from tiktok_insight_miner.signal_models import CommentSignals, SignalsEnvelope


def upstream(text="Tôi mở quán được 2 năm rồi, giờ tiền thuê tăng quá.", cid="c1"):
    source = source_from_comment({"id": cid, "text": text, "author": "private-author"})
    return CommentSignals(comment_id=cid, source=source, extraction_status="no_signal")


def candidate(field="situation", text="giờ tiền thuê tăng quá", **kw):
    return {"field": field, "evidence_quote": text, "truth_type": "OBSERVED", "confidence": "high", **kw}


def payload(cid="c1", contexts=None):
    return {"results": [{"comment_id": cid, "contexts": contexts or []}]}


def response(data, stop="end_turn"):
    return SimpleNamespace(stop_reason=stop,
        content=[SimpleNamespace(type="text", text=json.dumps(data, ensure_ascii=False))],
        usage=SimpleNamespace(input_tokens=12, output_tokens=30, cache_read_input_tokens=4))


def client_for(*responses):
    client = Mock()
    client.messages.create.side_effect = list(responses)
    return client


@pytest.mark.parametrize("field,text", [
    ("audience_segment", "Tôi đang vận hành quán cà phê"),
    ("context", "Chỗ tôi làm bị mất điện"),
    ("situation", "Hôm nay tiền thuê tăng"),
    ("life_or_business_stage", "Tôi mới mở quán được hai tháng"),
    ("user_buyer_distinction", "Tôi mua cho con dùng"),
])
def test_each_locked_field(field, text):
    original = upstream(text)
    records, issues = validate_context_batch([original], payload(contexts=[candidate(field, text)]))
    assert not issues
    r = records[0]
    c = getattr(r.customer_identity, field)[0]
    assert c.claim == c.evidence_quote == text
    assert r.source.text[c.start:c.end] == c.claim
    assert r.source_hash == c.source_snapshot_hash == original.source.snapshot_hash
    assert c.comment_id == original.comment_id
    assert r.extraction_status == "ok"
    assert len(r.customer_identity.model_dump()) == 5


def test_multiple_fields_and_one_bad_claim_keeps_valid_ones(caplog):
    original = upstream()
    records, _ = validate_context_batch([original], payload(contexts=[
        candidate("audience_segment", "Tôi mở quán"),
        candidate("life_or_business_stage", "mở quán được 2 năm", truth_type="DERIVED"),
        candidate("situation", "giờ tiền thuê tăng quá"),
        candidate("context", "tôi sống ở Hà Nội"),
    ]))
    assert records[0].extraction_status == "partial"
    assert len(records[0].customer_identity.all_claims()) == 3
    issue = records[0].validation_issues[0]
    assert issue.code == "ungrounded_quote" and issue.field == "context"
    assert "Hà Nội" not in caplog.text


@pytest.mark.parametrize("text", ["@bạn 😂", "Cũng tùy thôi", "Ừ", ""])
def test_zero_ambiguous_context(text):
    r = extract_customer_context(SignalsEnvelope(model="synthetic", records=[upstream(text)]),
        client=client_for(response(payload()))).records[0]
    assert r.extraction_status == "no_context"
    assert not r.customer_identity.all_claims()
    assert r.customer_identity.user_buyer_distinction == []


@pytest.mark.parametrize("bad", [
    {"truth_type": "HYPOTHESIS"}, {"truth_type": "PROPOSED"}, {"truth_type": "observed"},
    {"claim": "Phụ nữ 35 tuổi ở Hà Nội"}, {"gender": "female"}, {"age": 35},
    {"evidence_quote": ""}, {"confidence": 0.9},
])
def test_invalid_demographics_truth_or_schema_rejected(bad):
    item = candidate(**bad)
    with pytest.raises(ValidationError):
        ContextCandidate.model_validate(item)
    records, _ = validate_context_batch([upstream()], payload(contexts=[item, candidate()]))
    assert records[0].extraction_status == "partial"
    assert len(records[0].customer_identity.all_claims()) == 1


@pytest.mark.parametrize("field", ["economic_buyer", "decision_committee", "channel_partner",
                                   "recommender", "saboteur", "stakeholder_graph"])
def test_no_b2b_fields(field):
    assert set(CustomerIdentity.model_fields) == set(CONTEXT_FIELDS)
    with pytest.raises(ValidationError):
        CustomerIdentity.model_validate({field: []})
    records, _ = validate_context_batch([upstream()], payload(contexts=[candidate(field)]))
    assert not records[0].customer_identity.all_claims()
    assert records[0].validation_issues[0].field is None


def test_unknown_missing_duplicate_ids():
    records, issues = validate_context_batch([upstream(cid="a"), upstream(cid="b"), upstream(cid="c")],
        {"results": [
            {"comment_id": "a", "contexts": []}, {"comment_id": "a", "contexts": []},
            {"comment_id": "c", "contexts": []}, {"comment_id": "unknown", "contexts": []}]})
    assert issues[0].code == "unknown_comment_id"
    assert records[0].validation_issues[0].code == "duplicate_comment_id"
    assert records[1].validation_issues[0].code == "missing_comment_id"
    assert records[2].extraction_status == "no_context"
    assert [r.comment_id for r in records] == ["a", "b", "c"]


def test_malformed_and_duplicate_items_not_silently_accepted():
    r = validate_context_batch([upstream()], payload(contexts=[None, {}, candidate(), candidate()]))[0][0]
    assert len(r.customer_identity.all_claims()) == 1
    assert [i.code for i in r.validation_issues] == ["invalid_context_claim", "invalid_context_claim", "duplicate_context_claim"]


def test_source_whitespace_offsets_and_no_model_claim():
    r = upstream("🙂 tôi\t mới\n mở quán")
    result = validate_context_batch([r], payload(contexts=[candidate("life_or_business_stage", "tôi mới mở quán")]))[0][0]
    c = result.customer_identity.life_or_business_stage[0]
    assert c.start == 2
    assert c.claim == c.evidence_quote == "tôi\t mới\n mở quán"
    schema = ContextCandidateBatch.model_json_schema()["$defs"]["ContextCandidate"]
    assert "claim" not in schema["properties"]


@pytest.mark.parametrize("quote", ["toi mo quan", "TÔI MỞ QUÁN", "Tôi-mở-quán", "Tôi là bác sĩ"])
def test_invented_quote_and_unsafe_normalization(quote):
    r = validate_context_batch([upstream()], payload(contexts=[candidate("audience_segment", quote)]))[0][0]
    assert not r.customer_identity.all_claims()
    assert r.validation_issues[0].code == "ungrounded_quote"


def test_serialization_and_tamper_checks(tmp_path):
    signals = SignalsEnvelope(model="test", records=[upstream()])
    out = extract_customer_context(signals, client=client_for(response(payload(contexts=[candidate()]))))
    path = tmp_path / "contexts.json"
    save_contexts_json(out, path)
    assert load_contexts_json(path) == out
    data = out.model_dump()
    data["records"][0]["customer_identity"]["situation"][0]["claim"] = "invented"
    with pytest.raises(ValidationError):
        ContextsEnvelope.model_validate(data)
    for key,value in [("source_hash", "tampered"), ("comment_id", "wrong")]:
        data = out.model_dump()
        data["records"][0][key] = value
        with pytest.raises(ValidationError):
            ContextsEnvelope.model_validate(data)
    data=out.model_dump()
    data["records"][0]["customer_identity"]["context"] = data["records"][0]["customer_identity"]["situation"]
    with pytest.raises(ValidationError):
        ContextsEnvelope.model_validate(data)


def test_phase1_compatibility_no_mutation_and_corruption_rejected(tmp_path):
    signals = SignalsEnvelope(model="test", records=[upstream()])
    path = tmp_path / "signals.json"
    save_signals_json(signals, path)
    old_bytes = path.read_bytes()
    old_dump = signals.model_dump_json()
    context = extract_customer_context(load_signals_json(path), client=client_for(response(payload())))
    assert context.input_schema_version == "v2.signals.1"
    assert path.read_bytes() == old_bytes and signals.model_dump_json() == old_dump
    signals.records[0].source.text = "tampered"
    client = client_for()
    with pytest.raises(ValidationError):
        extract_customer_context(signals, client=client)
    client.messages.create.assert_not_called()


def test_upstream_partial_status_preserved():
    from tiktok_insight_miner.signal_models import ValidationIssue
    r = upstream()
    r.extraction_status = "partial"
    r.issues = [ValidationIssue(code="invalid_claim", detail="invalid_claim", item_index=0)]
    result = extract_customer_context(SignalsEnvelope(model="test", records=[r]), client=client_for(response(payload())))
    assert result.records[0].upstream_status == "partial"
    assert result.records[0].upstream_issues == r.issues
    assert result.records[0].extraction_status == "no_context"


def test_batching_prompt_input_and_model_resolution(monkeypatch, caplog):
    monkeypatch.delenv("CONTEXT_MODEL", raising=False)
    monkeypatch.setenv("ANTHROPIC_MODEL", "common")
    assert resolve_context_model() == "common"
    monkeypatch.setenv("CONTEXT_MODEL", "context")
    assert resolve_context_model() == "context"
    assert resolve_context_model("explicit") == "explicit"
    client=client_for(response(payload("a")), response(payload("b")))
    with caplog.at_level("INFO"):
        result=extract_customer_context(SignalsEnvelope(model="signal", records=[upstream(cid="a"), upstream(cid="b")]),
            batch_size=1, client=client)
    assert len(result.records)==2
    sent=client.messages.create.call_args.kwargs
    assert sent["model"]=="context"
    assert "private-author" not in sent["messages"][0]["content"]
    assert sent["system"][0]["cache_control"]=={"type":"ephemeral"}
    assert "cache_read=4" in caplog.text
    assert "video topic" in SYSTEM_PROMPT and "Do not invent age" in SYSTEM_PROMPT


def test_api_auth_and_truncated_errors():
    signals=SignalsEnvelope(model="test", records=[upstream(cid="a"), upstream(cid="b")])
    error=anthropic.AuthenticationError("secret", response=httpx.Response(401,
        request=httpx.Request("POST", "https://example.invalid")), body=None)
    client=client_for(error)
    result=extract_customer_context(signals,batch_size=1,client=client)
    assert all(r.extraction_status=="error" for r in result.records)
    assert client.messages.create.call_count==1
    result=extract_customer_context(signals,batch_size=1,client=client_for(response({},"max_tokens"),response(payload("b"))))
    assert [r.extraction_status for r in result.records]==["error","no_context"]


@pytest.mark.parametrize("batch_size", [0,-1,True,1.5])
def test_invalid_batch_size(batch_size):
    with pytest.raises(ValueError):
        extract_customer_context(SignalsEnvelope(model="test"),batch_size=batch_size,client=client_for())


def test_empty_input_no_network():
    client=client_for()
    assert not extract_customer_context(SignalsEnvelope(model="test"),client=client).records
    client.messages.create.assert_not_called()


def test_cli_end_to_end_and_partial_exit(tmp_path, monkeypatch):
    from tiktok_insight_miner.cli import build_parser, cmd_run, cmd_extract_signals
    path=tmp_path/'signals.json'
    save_signals_json(SignalsEnvelope(model="test",records=[upstream()]),path)
    client=client_for(response(payload()), response(payload(contexts=[candidate(text="invented")])) )
    monkeypatch.setattr('tiktok_insight_miner.customer_context_extractor.anthropic.Anthropic',lambda **kw:client)
    parser=build_parser()
    args=parser.parse_args(['extract-context','-i',str(path)])
    args.func(args)
    assert load_contexts_json(tmp_path/'contexts.json').records[0].extraction_status=='no_context'
    with pytest.raises(SystemExit) as error:
        args.func(args)
    assert error.value.code==2
    bad=parser.parse_args(['extract-context','-i',str(path),'-o',str(path)])
    with pytest.raises(SystemExit):
        bad.func(bad)
    assert parser.parse_args(['extract-signals','-i','raw.json']).func==cmd_extract_signals
    assert parser.parse_args(['run','--urls','https://example.invalid']).func==cmd_run


@pytest.mark.parametrize('key,value', [('start',0),('end',999),('source_record_id','wrong'),
                                      ('source_snapshot_hash','wrong'),('comment_id','wrong')])
def test_persisted_context_provenance_cannot_be_tampered(key,value):
    result=extract_customer_context(SignalsEnvelope(model='test',records=[upstream()]),
        client=client_for(response(payload(contexts=[candidate()]))))
    data=result.model_dump()
    data['records'][0]['customer_identity']['situation'][0][key]=value
    with pytest.raises(ValidationError):
        ContextsEnvelope.model_validate(data)


def test_malformed_json_recovery():
    broken=response({})
    broken.content[0].text='{"results": ['
    result=extract_customer_context(SignalsEnvelope(model='test',records=[upstream(cid='a'),upstream(cid='b')]),
        batch_size=1,client=client_for(broken,response(payload('b'))))
    assert [r.extraction_status for r in result.records]==['error','no_context']
