"""Unit tests cho scraper._extract_dataset_id (Spec 2 của T4).

Apify SDK v1/v2 breaking change:
- v1.x: client.actor().call() trả dict → run.get("defaultDatasetId")
- v2.x: trả Run Pydantic object → run.default_dataset_id (snake_case)

Helper `_extract_dataset_id()` phải support cả 3 shape + không raise ngầm.
Không gọi Apify thật.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from tiktok_insight_miner.scraper import _extract_dataset_id


def test_extract_from_dict_v1_sdk():
    """SDK v1: dict với camelCase key."""
    run = {"defaultDatasetId": "dataset_v1"}
    assert _extract_dataset_id(run) == "dataset_v1"


def test_extract_from_pydantic_snake_case_v2_sdk():
    """SDK v2: Pydantic object với snake_case attribute."""
    run = MagicMock(spec=["default_dataset_id"])
    run.default_dataset_id = "dataset_v2"
    assert _extract_dataset_id(run) == "dataset_v2"


def test_extract_from_pydantic_camel_case_variant():
    """Variant: Pydantic có attr camelCase (edge case).

    MagicMock spec chỉ expose default_dataset_id (None) + defaultDatasetId.
    """
    run = MagicMock(spec=["default_dataset_id", "defaultDatasetId"])
    run.default_dataset_id = None
    run.defaultDatasetId = "dataset_camel"
    assert _extract_dataset_id(run) == "dataset_camel"


def test_extract_from_model_dump_fallback():
    """Last resort: cast Pydantic → dict qua model_dump().

    MagicMock có model_dump() trả dict chứa defaultDatasetId.
    Snake_case và camelCase attr đều None để buộc fallback path.
    """
    run = MagicMock(spec=["default_dataset_id", "defaultDatasetId", "model_dump"])
    run.default_dataset_id = None
    run.defaultDatasetId = None
    run.model_dump.return_value = {"defaultDatasetId": "dataset_dumped"}
    assert _extract_dataset_id(run) == "dataset_dumped"


def test_extract_from_model_dump_snake_case_key():
    """model_dump trả snake_case key cũng phải bắt được."""
    run = MagicMock(spec=["default_dataset_id", "defaultDatasetId", "model_dump"])
    run.default_dataset_id = None
    run.defaultDatasetId = None
    run.model_dump.return_value = {"default_dataset_id": "dataset_snake_dump"}
    assert _extract_dataset_id(run) == "dataset_snake_dump"


def test_extract_returns_none_when_nothing_found():
    """Không có defaultDatasetId ở đâu → return None (không raise)."""
    run = MagicMock(spec=["default_dataset_id", "defaultDatasetId"])
    run.default_dataset_id = None
    run.defaultDatasetId = None
    assert _extract_dataset_id(run) is None


def test_extract_from_empty_dict_returns_none():
    """Empty dict không có key → None, không raise KeyError."""
    assert _extract_dataset_id({}) is None


def test_extract_prefers_snake_case_over_camel():
    """Nếu cả 2 attr có → ưu tiên snake_case (SDK v2 chuẩn)."""
    run = MagicMock(spec=["default_dataset_id", "defaultDatasetId"])
    run.default_dataset_id = "snake_wins"
    run.defaultDatasetId = "camel_lose"
    assert _extract_dataset_id(run) == "snake_wins"


def test_extract_model_dump_raises_swallowed():
    """model_dump() raise → catch, không propagate lên caller (return None)."""
    run = MagicMock(spec=["default_dataset_id", "defaultDatasetId", "model_dump"])
    run.default_dataset_id = None
    run.defaultDatasetId = None
    run.model_dump.side_effect = RuntimeError("oops")
    # Không raise — chỉ return None
    assert _extract_dataset_id(run) is None


def test_extract_dict_with_get_method_but_no_key():
    """Dict-like có .get() nhưng thiếu key → None."""
    assert _extract_dataset_id({"otherField": "x"}) is None
