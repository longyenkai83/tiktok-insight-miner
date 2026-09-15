"""Synthetic fixtures and offline API doubles only. No customer data/network."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import anthropic
import httpx
import pytest
from pydantic import ValidationError

from tiktok_insight_miner.models import Comment
from tiktok_insight_miner.signal_extractor import (
    DEFAULT_MODEL, SYSTEM_PROMPT, extract_signals, load_raw_sources,
    load_signals_json, resolve_model, save_signals_json, source_from_comment, validate_batch,
)
from tiktok_insight_miner.signal_models import CandidateSignal, SignalsEnvelope, TAXONOMY


def claim(text, category="pains", subcategory="costs", **kwargs):
    return dict(category=category, subcategory=subcategory, claim=text,
                truth_type="OBSERVED", evidence_quote=text, confidence="high", **kwargs)


def payload(cid, signals):
    return {"results": [{"comment_id": cid, "signals": signals}]}


def source(text="Phí giao hàng quá cao", cid="c1", **kwargs):
    return source_from_comment(dict(id=cid, text=text, **kwargs))


def response(data, stop="end_turn"):
    return SimpleNamespace(stop_reason=stop,
        content=[SimpleNamespace(type="text", text=json.dumps(data, ensure_ascii=False))],
        usage=SimpleNamespace(input_tokens=10, output_tokens=20, cache_read_input_tokens=8))


def api(*responses):
    client = Mock()
    client.messages.create.side_effect = list(responses)
    return client


def test_multisignal_and_fixture_categories():
    fixtures = load_raw_sources(Path(__file__).parents[1] / "fixtures/signal_comments.json")
    by_id = {s.comment_id: s for s in fixtures}
    rows = [
        {"comment_id": "pain", "signals": [claim("Phí giao hàng quá cao"),
            claim("tôi không mua nữa", "behavior", "objections"),
            claim("Phí giao hàng quá cao", "language", "exact_phrases")]},
        {"comment_id": "gain", "signals": [claim(by_id["gain"].text, "gains", "desired")]},
        {"comment_id": "functional", "signals": [claim(by_id["functional"].text, "jobs", "functional")]},
        {"comment_id": "emotional", "signals": [claim(by_id["emotional"].text, "jobs", "emotional")]},
        {"comment_id": "solution", "signals": [claim(by_id["solution"].text, "behavior", "workarounds"),
            claim(by_id["solution"].text, "behavior", "current_solution")]},
    ] + [{"comment_id": cid, "signals": []} for cid in ("joke", "tag", "noise", "ambiguous")]
    result = extract_signals(fixtures, client=api(response({"results": rows})))
    assert len(result.records[0].signals) == 3
    assert {s.category for r in result.records for s in r.signals} == set(TAXONOMY)
    assert all(r.extraction_status == "no_signal" for r in result.records[-4:])
    assert result.records[0].signals[-1].claim == "Phí giao hàng quá cao"
    assert len(result.records) == len(fixtures)


def test_invalid_quote_keeps_good_claim(caplog):
    s = source()
    result, _ = validate_batch([s], payload("c1", [claim("bịa hoàn toàn"), claim(s.text)]))
    assert result[0].extraction_status == "partial"
    assert [c.claim for c in result[0].signals] == [s.text]
    assert result[0].issues[0].code == "ungrounded_quote"
    assert "ungrounded_quote" in caplog.text
    assert "bịa hoàn toàn" not in caplog.text


@pytest.mark.parametrize("bad", [
    {"truth_type": "HYPOTHESIS"}, {"truth_type": "PROPOSED"},
    {"claim": "Khách hàng nữ 35 tuổi"}, {"demographics": "35 tuổi"},
    {"category": "audience_segment"}, {"subcategory": "economic_buyer"},
    {"confidence": "certain"}, {"claim": ""},
])
def test_bad_claim_schema_and_invented_demographics_rejected(bad):
    s = source()
    invalid = {**claim(s.text), **bad}
    with pytest.raises(ValidationError):
        CandidateSignal.model_validate(invalid)
    rows, _ = validate_batch([s], payload("c1", [invalid, claim(s.text)]))
    assert rows[0].extraction_status == "partial"
    assert len(rows[0].signals) == 1


def test_malformed_claim_does_not_kill_batch():
    s = source()
    rows, _ = validate_batch([s], payload("c1", [None, {}, "bad", claim(s.text)]))
    assert len(rows[0].signals) == 1
    assert len(rows[0].issues) == 3


def test_unknown_missing_and_duplicate_ids():
    sources = [source(cid="a"), source(cid="b"), source(cid="c")]
    rows, issues = validate_batch(sources, {"results": [
        {"comment_id": "a", "signals": []}, {"comment_id": "a", "signals": []},
        {"comment_id": "c", "signals": []}, {"comment_id": "unknown", "signals": []}]})
    assert issues[0].code == "unknown_comment_id"
    assert [r.comment_id for r in rows] == ["a", "b", "c"]
    assert rows[0].issues[0].code == "duplicate_comment_id"
    assert rows[1].issues[0].code == "missing_comment_id"
    assert rows[2].extraction_status == "no_signal"


def test_duplicate_input_rejected_before_api():
    client = api()
    with pytest.raises(ValueError, match="Duplicate input"):
        extract_signals([source(), source()], client=client)
    client.messages.create.assert_not_called()


def test_context_fields_not_accepted():
    data = payload("c1", [])
    data["results"][0]["audience_segment"] = "invented"
    rows, _ = validate_batch([source()], data)
    assert rows[0].extraction_status == "error"
    assert rows[0].issues[0].code == "invalid_result_fields"


def test_unicode_whitespace_spans_keep_original_and_derived():
    s = source("🙂 Phí\t giao\n hàng quá cao")
    item = {**claim("Phí giao hàng quá cao"), "truth_type": "DERIVED"}
    rows, _ = validate_batch([s], payload("c1", [item]))
    signal = rows[0].signals[0]
    assert signal.evidence_quote == "Phí\t giao\n hàng quá cao"
    assert s.text[signal.start:signal.end] == signal.evidence_quote
    assert signal.start == 2
    assert signal.truth_type == "DERIVED"


@pytest.mark.parametrize("phrase", ["phi giao hang qua cao", "phí giao hàng quá cao", "Phí-giao-hàng"])
def test_no_unsafe_quote_normalization(phrase):
    rows, _ = validate_batch([source()], payload("c1", [claim(phrase)]))
    assert not rows[0].signals
    assert rows[0].extraction_status == "partial"


def test_language_literal_and_repetition():
    s = source("khó\tquá")
    rows, _ = validate_batch([s], payload("c1", [claim("khó quá", "language", "exact_phrases")]))
    assert rows[0].issues[0].code == "nonliteral_language"
    rows, _ = validate_batch([s], payload("c1", [claim(s.text, "language", "repeated_expressions")]))
    assert rows[0].issues[0].code == "not_repeated_in_source"
    repeated = source("khó quá, khó quá")
    rows, _ = validate_batch([repeated], payload("c1", [claim("khó quá", "language", "repeated_expressions")]))
    assert rows[0].extraction_status == "ok"


def test_metrics_unknown_and_provenance():
    s = source(author="anonymous", created_at="2026-01-01", video_url="https://example.invalid/video")
    assert s.likes is None and s.reply_count is None
    s = source(raw={"platform": "facebook_inbox"}, likes=0, reply_count=0)
    assert s.likes is None and s.reply_count is None
    s = source(raw={"_platform": "facebook", "likesCount": 0}, likes=0, reply_count=0)
    assert s.likes == 0 and s.reply_count is None
    assert source(likes=0).likes is None  # serialized legacy fallback cannot prove measured zero
    assert source(likes=10).likes == 10
    assert source(raw={"cid": "c1"}, likes=0).likes is None
    assert source(raw={"cid": "c1", "diggCount": 0}).likes == 0
    s = source(raw={"imported_from": "manual_csv", "original_row": {"likes": "", "replies": "2"}}, likes=0)
    assert s.likes is None and s.reply_count == 2
    assert source_from_comment(Comment(id="x", text="hello")).likes is None


def test_serialization_and_tampered_quote_detection(tmp_path):
    s = source()
    result = extract_signals([s], client=api(response(payload("c1", [claim(s.text)]))))
    path = tmp_path / "signals.json"
    save_signals_json(result, path)
    assert load_signals_json(path) == result
    data = json.loads(path.read_text(encoding="utf-8"))
    data["records"][0]["signals"][0]["evidence_quote"] = "invented"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_signals_json(path)
    data = result.model_dump()
    data["records"][0]["source"]["likes"] = 999
    with pytest.raises(ValidationError):
        SignalsEnvelope.model_validate(data)


def test_model_precedence(monkeypatch):
    monkeypatch.delenv("SIGNAL_MODEL", raising=False)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    assert resolve_model() == DEFAULT_MODEL
    monkeypatch.setenv("ANTHROPIC_MODEL", "legacy")
    assert resolve_model() == "legacy"
    monkeypatch.setenv("SIGNAL_MODEL", "signals")
    assert resolve_model() == "signals"
    assert resolve_model("explicit") == "explicit"


def test_request_batching_cache_no_truncation_and_no_metadata(caplog):
    a, b = source("a" * 1200, cid="a", author="private"), source("b", cid="b")
    client = api(response(payload("a", [])), response(payload("b", [])))
    with caplog.at_level("INFO"):
        result = extract_signals([a, b], batch_size=1, client=client)
    assert len(result.records) == 2
    sent = client.messages.create.call_args_list[0].kwargs
    assert json.loads(sent["messages"][0]["content"])[0]["text"] == a.text
    assert "private" not in sent["messages"][0]["content"]
    assert sent["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert sent["output_config"]["format"]["type"] == "json_schema"
    assert "cache_read=8" in caplog.text
    assert "Do not invent" in SYSTEM_PROMPT


def test_batch_failure_preserves_next_batch():
    client = api(response({}, stop="max_tokens"), response(payload("b", [])))
    result = extract_signals([source(cid="a"), source(cid="b")], batch_size=1, client=client)
    assert [r.extraction_status for r in result.records] == ["error", "no_signal"]


def test_auth_failure_no_more_network_and_no_secret_logging(caplog):
    error = anthropic.AuthenticationError("SECRET", response=httpx.Response(401,
        request=httpx.Request("POST", "https://example.invalid")), body=None)
    client = api(error)
    result = extract_signals([source(cid="a"), source(cid="b")], batch_size=1, client=client)
    assert all(r.extraction_status == "error" for r in result.records)
    assert client.messages.create.call_count == 1
    assert "SECRET" not in caplog.text


@pytest.mark.parametrize("size", [0, -1, True, 1.5])
def test_invalid_batch_size(size):
    with pytest.raises(ValueError):
        extract_signals([], batch_size=size, client=api())


def test_empty_input_does_not_create_client(monkeypatch):
    ctor = Mock(side_effect=AssertionError("no API"))
    monkeypatch.setattr("tiktok_insight_miner.signal_extractor.anthropic.Anthropic", ctor)
    assert extract_signals([]).records == []


def test_cli_raw_to_signals_and_default_legacy_path(tmp_path, monkeypatch):
    from tiktok_insight_miner.cli import build_parser, cmd_classify, cmd_run
    import tiktok_insight_miner.signal_extractor as module
    path = tmp_path / "raw_comments.json"
    path.write_text(json.dumps([{"id": "c1", "text": "too ambiguous"}]), encoding="utf-8")
    client = api(response(payload("c1", [])))
    monkeypatch.setattr(module.anthropic, "Anthropic", lambda **kwargs: client)
    parser = build_parser()
    args = parser.parse_args(["extract-signals", "-i", str(path)])
    args.func(args)
    assert load_signals_json(tmp_path / "signals.json").records[0].extraction_status == "no_signal"
    assert parser.parse_args(["run", "--urls", "https://example.invalid"]).func == cmd_run
    assert parser.parse_args(["classify", "-i", str(path), "-o", "classified.json"]).func == cmd_classify
    bad = parser.parse_args(["extract-signals", "-i", str(path), "-o", str(path)])
    with pytest.raises(SystemExit):
        bad.func(bad)


def test_raw_loader_rejects_classified(tmp_path):
    path = tmp_path / "classified.json"
    path.write_text(json.dumps([{"comment": {"id": "c1", "text": "x"}, "bucket": "pain"}]))
    with pytest.raises(ValueError, match="raw Comment"):
        load_raw_sources(path)


def test_invalid_json_response_recovers_next_batch():
    bad = response({})
    bad.content[0].text = '{"results": ['
    result = extract_signals([source(cid="a"), source(cid="b")], batch_size=1,
        client=api(bad, response(payload("b", []))))
    assert [r.extraction_status for r in result.records] == ["error", "no_signal"]


def test_cli_partial_artifact_exit_two(tmp_path, monkeypatch):
    from tiktok_insight_miner.cli import build_parser
    path = tmp_path / "raw_comments.json"
    path.write_text(json.dumps([{"id": "c1", "text": "test"}]), encoding="utf-8")
    client = api(response(payload("c1", [claim("invented")])) )
    monkeypatch.setattr("tiktok_insight_miner.signal_extractor.anthropic.Anthropic", lambda **kw: client)
    args = build_parser().parse_args(["extract-signals", "-i", str(path)])
    with pytest.raises(SystemExit) as exc:
        args.func(args)
    assert exc.value.code == 2
    assert load_signals_json(tmp_path / "signals.json").records[0].extraction_status == "partial"


def test_extra_source_metadata_and_invalid_raw_shape():
    s = source(source_url="https://example.invalid/comment", raw={"custom": "preserved"})
    assert s.metadata["source_fields"]["source_url"] == "https://example.invalid/comment"
    assert s.metadata["raw"] == {"custom": "preserved"}
    with pytest.raises(ValueError):
        source(raw=[])


def test_duplicate_signal_is_not_counted_twice():
    s = source()
    records, _ = validate_batch([s], payload("c1", [claim(s.text), claim(s.text)]))
    assert len(records[0].signals) == 1
    assert records[0].issues[0].code == "duplicate_signal"
