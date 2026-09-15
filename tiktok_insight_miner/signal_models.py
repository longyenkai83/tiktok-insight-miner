"""Phase 1 models, deliberately independent of legacy classification."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TAXONOMY = {
    "jobs": ("functional", "social", "emotional", "supporting"),
    "pains": ("negative_outcomes", "obstacles", "risks_fears", "costs", "frustrations"),
    "gains": ("required", "expected", "desired", "unexpected"),
    "behavior": ("trigger", "current_solution", "alternatives", "workarounds",
                 "decision_criteria", "objections"),
    "language": ("exact_phrases", "emotional_wording", "repeated_expressions"),
}
Category = Literal["jobs", "pains", "gains", "behavior", "language"]
TruthType = Literal["OBSERVED", "DERIVED"]


def normalize_whitespace(text: str) -> str:
    """No case folding, punctuation changes, accent removal or paraphrasing."""
    return " ".join(text.split())


def quote_span(text: str, quote: str) -> tuple[int, int] | None:
    """Find a whitespace-normalized quote and return original Unicode offsets."""
    parts = re.findall(r"\S+", quote)
    if not parts:
        return None
    match = re.search(r"\s+".join(re.escape(p) for p in parts), text)
    return match.span() if match else None


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CandidateSignal(StrictModel):
    """Transport schema; application validation still checks each item separately."""
    category: Category
    subcategory: str
    truth_type: TruthType
    evidence_quote: str
    confidence: Literal["high", "medium", "low"]

    @model_validator(mode="after")
    def valid_claim(self) -> CandidateSignal:
        if self.subcategory not in TAXONOMY[self.category]:
            raise ValueError("unknown subcategory")
        if not normalize_whitespace(self.evidence_quote):
            raise ValueError("empty quote")
        if self.category == "language" and self.truth_type != "OBSERVED":
            raise ValueError("literal language must be OBSERVED")
        return self


class CandidateComment(StrictModel):
    comment_id: str
    signals: list[CandidateSignal]


class CandidateBatch(StrictModel):
    results: list[CandidateComment]


class Signal(CandidateSignal):
    claim: str
    signal_id: str
    source_record_id: str
    source_snapshot_hash: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)

    @model_validator(mode="after")
    def valid_saved_claim(self) -> Signal:
        # Keep reading Phase 1 artifacts whose semantic claim normalized whitespace.
        # New claims are constructed from the exact validated span in code.
        if normalize_whitespace(self.claim) != normalize_whitespace(self.evidence_quote):
            raise ValueError("claim must retain the quoted wording; no added facts")
        return self


class SignalSource(StrictModel):
    comment_id: str
    text: str
    author: str | None = None
    likes: int | None = Field(default=None, ge=0)
    reply_count: int | None = Field(default=None, ge=0)
    created_at: str | None = None
    video_url: str | None = None
    platform: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    metric_notes: dict[str, str] = Field(default_factory=dict)
    source_record_id: str
    snapshot_hash: str

    def expected_hash(self) -> str:
        import json
        data = self.model_dump(exclude={"source_record_id", "snapshot_hash"})
        return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

    @model_validator(mode="after")
    def check_hash(self) -> SignalSource:
        if self.snapshot_hash != self.expected_hash():
            raise ValueError("source snapshot hash mismatch")
        identity = f"{self.platform or ''}\0{self.video_url or ''}\0{self.comment_id}"
        expected_id = "source-" + hashlib.sha256(identity.encode()).hexdigest()
        if self.source_record_id != expected_id:
            raise ValueError("source ID mismatch")
        return self


class ValidationIssue(StrictModel):
    code: str
    comment_id: str | None = None
    item_index: int | None = None
    detail: str


class CommentSignals(StrictModel):
    comment_id: str
    source: SignalSource
    signals: list[Signal] = Field(default_factory=list)
    extraction_status: Literal["ok", "no_signal", "partial", "error"]
    issues: list[ValidationIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_grounding(self) -> CommentSignals:
        if self.comment_id != self.source.comment_id:
            raise ValueError("comment/source ID mismatch")
        ids = [s.signal_id for s in self.signals]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate signal IDs")
        for signal in self.signals:
            if (signal.source_record_id != self.source.source_record_id
                    or signal.source_snapshot_hash != self.source.snapshot_hash):
                raise ValueError("broken source reference")
            if not (0 <= signal.start < signal.end <= len(self.source.text)):
                raise ValueError("invalid source span")
            if self.source.text[signal.start:signal.end] != signal.evidence_quote:
                raise ValueError("quote does not match source span")
            if signal.category == "language" and signal.claim != signal.evidence_quote:
                raise ValueError("language phrase must be literal")
        if self.extraction_status == "ok" and (not self.signals or self.issues):
            raise ValueError("ok requires signals and no issues")
        if self.extraction_status == "no_signal" and (self.signals or self.issues):
            raise ValueError("no_signal requires valid empty extraction")
        if self.extraction_status in ("partial", "error") and not self.issues:
            raise ValueError("incomplete extraction requires issues")
        if self.extraction_status == "error" and self.signals:
            raise ValueError("error cannot contain accepted signals")
        return self


class SignalsEnvelope(StrictModel):
    schema_version: Literal["v2.signals.1"] = "v2.signals.1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model: str
    prompt_version: Literal["phase1.extractive.1", "phase1.extractive.2"] = "phase1.extractive.2"
    derivation_method: Literal["source_span_categorization"] = "source_span_categorization"
    records: list[CommentSignals] = Field(default_factory=list)
    issues: list[ValidationIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_records(self) -> SignalsEnvelope:
        ids = [r.comment_id for r in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate source comment IDs")
        return self
