"""Human decisions are corpus-scoped; JSON history is the authoritative ledger."""
from datetime import datetime, timezone
from typing import Literal

from pydantic import Field, field_validator, model_validator

from .evidence_models import EvidenceBundle
from .insight_models import InsightsEnvelope
from .signal_models import StrictModel

Decision = Literal["approved", "edited_and_approved", "rejected", "deferred"]
Assessment = Literal["high", "medium", "low", "unknown"]


class PriorityDecision(StrictModel):
    priority_status: Literal["unassessed", "monitor", "priority_need"] = "unassessed"
    assessment_origin: Literal["human_assessment"] = "human_assessment"
    important: Assessment = "unknown"
    urgent: Assessment = "unknown"
    frequent: Assessment = "unknown"
    expensive: Assessment = "unknown"
    emotional_intensity: Assessment = "unknown"
    note: str = Field(default="", max_length=8000)


class ReviewAction(StrictModel):
    request_id: str = Field(min_length=1, max_length=100)
    candidate_insight_id: str
    candidate_hash: str
    decision: Decision
    reviewer_id: str = Field(min_length=1, max_length=120)
    human_attested: Literal[True]
    edited_statement: str | None = Field(default=None, min_length=1, max_length=1600)
    rationale: str = Field(min_length=1, max_length=8000)
    priority: PriorityDecision = Field(default_factory=PriorityDecision)

    @field_validator("reviewer_id", "rationale", "request_id", "edited_statement")
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("review identity, rationale and statement must not be blank")
        return value

    @model_validator(mode="after")
    def decision_fields(self):
        if (self.decision == "edited_and_approved") != (self.edited_statement is not None):
            raise ValueError("edited_statement required only for edited_and_approved")
        if self.decision in ("rejected", "deferred") and self.priority != PriorityDecision():
            raise ValueError("priority assessment requires an approved insight")
        return self


class ReviewEvent(StrictModel):
    review_event_id: str
    sequence: int = Field(ge=1)
    previous_event_id: str | None
    source_schema_version: Literal["v2.insights.2"] = "v2.insights.2"
    source_insights_hash: str
    action: ReviewAction
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    original_statement: str
    approved_statement: str | None

    @field_validator("reviewed_at")
    @classmethod
    def aware_time(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("review timestamp requires timezone")
        return value


class ReviewQueue(StrictModel):
    schema_version: Literal["v2.insight-reviews.1"] = "v2.insight-reviews.1"
    # Ordered, immutable snapshots; last snapshot is the active analysis revision.
    snapshots: list[InsightsEnvelope] = Field(min_length=1)
    events: list[ReviewEvent] = Field(default_factory=list)

    @model_validator(mode="after")
    def audit_history(self):
        from .governance_engine import validate_history
        validate_history(self)
        return self


class VerifiedStatement(StrictModel):
    text: str
    truth_type: Literal["DERIVED"] = "DERIVED"
    statement_origin: Literal["machine_approved", "human_edited"]


class HumanVerification(StrictModel):
    source_grounded: Literal[True] = True
    evidence_support_present: Literal[True] = True
    machine_review_passed: Literal[True] = True
    # In particular, an edited statement was NOT reviewed by the original machine pass.
    machine_review_scope: Literal["source_candidate_only"] = "source_candidate_only"
    human_verified: Literal[True] = True
    market_validated: Literal[False] = False
    purchase_validated: Literal[False] = False


class HumanReview(StrictModel):
    review_event_id: str
    reviewer_id: str
    reviewed_at: datetime
    decision: Literal["approved", "edited_and_approved"]
    rationale: str


class VerifiedInsight(EvidenceBundle):
    verified_insight_id: str
    source_candidate_id: str
    source_candidate_hash: str
    source_insights_hash: str
    revision: int = Field(ge=1)
    supersedes: str | None
    statement: VerifiedStatement
    support_pattern_ids: list[str]
    relationship_type: str
    verification: HumanVerification = Field(default_factory=HumanVerification)
    human_review: HumanReview
    priority: PriorityDecision
    status: Literal["verified"] = "verified"


class VerifiedInsightsEnvelope(StrictModel):
    schema_version: Literal["v2.verified-insights.1"] = "v2.verified-insights.1"
    input_reviews_hash: str
    review_history: ReviewQueue
    verified_insights: list[VerifiedInsight]

    @model_validator(mode="after")
    def verified_projection(self):
        from .governance_engine import project_verified
        from .pattern_models import artifact_hash
        if self.input_reviews_hash != artifact_hash(self.review_history):
            raise ValueError("review history hash mismatch")
        if self.verified_insights != project_verified(self.review_history):
            raise ValueError("verified output must match explicit human decisions and immutable evidence")
        return self
