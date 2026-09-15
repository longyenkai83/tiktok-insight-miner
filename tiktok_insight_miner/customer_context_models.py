"""Per-comment B2C context candidates, not corpus segments or verified insights."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, get_args

from pydantic import Field, model_validator

from tiktok_insight_miner.signal_models import (
    SignalSource, StrictModel, TruthType, ValidationIssue, normalize_whitespace,
    validate_source_span,
)

ContextField = Literal["audience_segment", "context", "situation",
                       "life_or_business_stage", "user_buyer_distinction"]
CONTEXT_FIELDS = get_args(ContextField)


class ContextCandidate(StrictModel):
    field: ContextField
    evidence_quote: str
    truth_type: TruthType
    confidence: Literal["high", "medium", "low"]

    @model_validator(mode="after")
    def nonempty_quote(self) -> ContextCandidate:
        if not normalize_whitespace(self.evidence_quote):
            raise ValueError("empty context evidence")
        return self


class ContextCandidateRecord(StrictModel):
    comment_id: str
    contexts: list[ContextCandidate]


class ContextCandidateBatch(StrictModel):
    results: list[ContextCandidateRecord]


class ContextClaim(ContextCandidate):
    claim_id: str
    claim: str
    comment_id: str
    source_record_id: str
    source_snapshot_hash: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)

    @model_validator(mode="after")
    def exact_claim(self) -> ContextClaim:
        if self.claim != self.evidence_quote:
            raise ValueError("context claim must equal exact evidence wording")
        return self


class CustomerIdentity(StrictModel):
    audience_segment: list[ContextClaim] = Field(default_factory=list)
    context: list[ContextClaim] = Field(default_factory=list)
    situation: list[ContextClaim] = Field(default_factory=list)
    life_or_business_stage: list[ContextClaim] = Field(default_factory=list)
    user_buyer_distinction: list[ContextClaim] = Field(default_factory=list)

    def all_claims(self) -> list[ContextClaim]:
        return [claim for name in CONTEXT_FIELDS for claim in getattr(self, name)]

    @model_validator(mode="after")
    def field_consistency(self) -> CustomerIdentity:
        for name in CONTEXT_FIELDS:
            if any(claim.field != name for claim in getattr(self, name)):
                raise ValueError("claim stored in wrong identity field")
        return self


class ContextIssue(ValidationIssue):
    # None when the model did not provide a recognized field (or a record/batch error).
    field: ContextField | None = None


class CommentContext(StrictModel):
    comment_id: str
    source: SignalSource
    source_hash: str
    upstream_status: Literal["ok", "no_signal", "partial", "error"]
    upstream_issues: list[ValidationIssue] = Field(default_factory=list)
    customer_identity: CustomerIdentity = Field(default_factory=CustomerIdentity)
    extraction_status: Literal["ok", "no_context", "partial", "error"]
    validation_issues: list[ContextIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_grounding(self) -> CommentContext:
        if self.comment_id != self.source.comment_id or self.source_hash != self.source.snapshot_hash:
            raise ValueError("context/source identity mismatch")
        claims = self.customer_identity.all_claims()
        ids = [c.claim_id for c in claims]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate context claim IDs")
        for claim in claims:
            if claim.comment_id != self.comment_id:
                raise ValueError("claim/comment ID mismatch")
            validate_source_span(self.source, claim.source_record_id, claim.source_snapshot_hash,
                                 claim.start, claim.end, claim.evidence_quote)
        if self.extraction_status == "ok" and (not claims or self.validation_issues):
            raise ValueError("ok requires claims without issues")
        if self.extraction_status == "no_context" and (claims or self.validation_issues):
            raise ValueError("no_context requires valid empty extraction")
        if self.extraction_status in ("partial", "error") and not self.validation_issues:
            raise ValueError("incomplete extraction requires issues")
        if self.extraction_status == "error" and claims:
            raise ValueError("error cannot contain accepted context claims")
        return self


class ContextsEnvelope(StrictModel):
    schema_version: Literal["v2.contexts.1"] = "v2.contexts.1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model: str
    prompt_version: Literal["phase2.context.1"] = "phase2.context.1"
    derivation_method: Literal["source_span_context_assignment"] = "source_span_context_assignment"
    input_schema_version: Literal["v2.signals.1"] = "v2.signals.1"
    input_signals_hash: str
    upstream_issues: list[ValidationIssue] = Field(default_factory=list)
    records: list[CommentContext] = Field(default_factory=list)
    validation_issues: list[ContextIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_comments(self) -> ContextsEnvelope:
        ids = [r.comment_id for r in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate context comment IDs")
        return self
