"""Offline regression for the unchanged legacy classifier execution path."""
from types import SimpleNamespace
from unittest.mock import Mock

from tiktok_insight_miner.classifier import classify_comments, load_classified_json, save_classified_json
from tiktok_insight_miner.models import BatchClassificationResult, Comment


def test_legacy_classify_roundtrip(monkeypatch, tmp_path):
    client = Mock()
    client.messages.parse.return_value = SimpleNamespace(
        usage=SimpleNamespace(input_tokens=10, output_tokens=10),
        parsed_output=BatchClassificationResult.model_validate({"classifications": [
            {"comment_id": "legacy", "bucket": "pain", "summary": "Giao hàng chậm", "confidence": .9}
        ]}),
    )
    monkeypatch.setattr("tiktok_insight_miner.classifier.anthropic.Anthropic", lambda: client)
    comment = Comment(id="legacy", text="Giao hàng chậm")
    result = classify_comments([comment], model="legacy-model")
    assert result[0].comment == comment
    assert result[0].bucket == "pain"
    assert client.messages.parse.call_args.kwargs["model"] == "legacy-model"
    path = tmp_path / "classified.json"
    save_classified_json(result, path)
    assert load_classified_json(path) == result
