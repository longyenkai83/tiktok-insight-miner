"""Strict candidate transport and replayable, human-unverified Insight artifact."""
from datetime import datetime, timezone
from typing import Literal

from pydantic import Field, StrictBool, model_validator

from .evidence_models import EvidenceBundle, Verification
from .pattern_models import PatternsEnvelope, artifact_hash
from .signal_models import StrictModel, ValidationIssue

RelationshipType = Literal["single_pattern", "job_pain", "pain_behavior", "pain_gain",
    "situation_pain", "stage_decision", "current_solution_frustration", "language_behavior",
    "pattern_relationship"]


class InsightCandidate(StrictModel):
    insight_candidate_id: str = Field(min_length=1, max_length=100)
    support_pattern_ids: list[str] = Field(min_length=1)
    relationship_type: RelationshipType
    concise_statement: str = Field(min_length=1, max_length=1600)


class CandidateBatch(StrictModel):
    candidates: list[InsightCandidate]


class PartSupport(StrictModel):
    part_id: str
    support_pattern_ids: list[str] = Field(min_length=1)


class SemanticVerdict(StrictModel):
    insight_candidate_id: str
    supported: bool
    adds_understanding: bool
    scope_preserved: bool
    no_unsupported_causality: bool
    no_demographic_leak: bool
    no_solution_leak: bool
    no_market_generalization: bool
    support_pattern_ids: list[str]
    part_support: list[PartSupport]
    reason_code: Literal["supported", "overclaim", "shallow", "false_causality",
                         "context_leak", "solution_leak", "unsupported_demographic"]


class VerdictBatch(StrictModel):
    reviews: list[SemanticVerdict]


class SemanticReview(SemanticVerdict):
    candidate_hash: str


class InsightStatement(StrictModel):
    text: str
    truth_type: Literal["DERIVED"] = "DERIVED"


class StatementSupport(StrictModel):
    start: int
    end: int
    support_pattern_ids: list[str]


class Insight(EvidenceBundle):
    insight_id: str
    statement: InsightStatement
    statement_support: list[StatementSupport]
    relationship_type: RelationshipType
    support_pattern_ids: list[str]
    verification: Verification
    status: Literal["pending_human_review"] = "pending_human_review"
    semantic_review: SemanticReview
    validation_issues: list[ValidationIssue]


class CandidateOutcome(StrictModel):
    item_index: int
    candidate: InsightCandidate | None
    semantic_review: SemanticReview | None = None
    status: Literal["machine_accepted", "rejected", "deduplicated"]
    machine_review_passed: StrictBool = False
    insight_id: str | None = None
    duplicate_of: str | None = None
    validation_issues: list[ValidationIssue] = Field(default_factory=list)


class InsightsEnvelope(StrictModel):
    schema_version: Literal["v2.insights.2"] = "v2.insights.2"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    method: Literal["closed_patterns_semantic_review.1"] = "closed_patterns_semantic_review.1"
    producer: str
    input_patterns_hash: str
    input_patterns: PatternsEnvelope
    synthesis_status: Literal["complete", "error"]
    insights: list[Insight]
    outcomes: list[CandidateOutcome]
    upstream_issues: list[ValidationIssue]
    validation_issues: list[ValidationIssue]

    @model_validator(mode="before")
    @classmethod
    def check_schema_version(cls, data):
        if isinstance(data, dict) and data.get("schema_version", "v2.insights.2") != "v2.insights.2":
            raise ValueError("Unsupported insight schema version; expected v2.insights.2. "
                             "Rebuild from original patterns and saved model transports; "
                             "v2.insights.1 is not implicitly migrated.")
        return data

    @model_validator(mode="after")
    def validate_artifact(self):
        from collections import Counter
        from .insight_engine import assemble_insight
        from .insight_validator import candidate_issues, review_issues, dedupe_key
        if self.input_patterns_hash != artifact_hash(self.input_patterns):
            raise ValueError("patterns artifact hash mismatch")
        if self.upstream_issues != self.input_patterns.validation_issues:
            raise ValueError("upstream issues must be preserved")
        replayed, seen = [], {}
        ids = [o.item_index for o in self.outcomes]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate outcome index")
        candidate_counts = Counter(o.candidate.insight_candidate_id for o in self.outcomes if o.candidate)
        for outcome in self.outcomes:
            candidate = outcome.candidate
            review_passed = candidate is not None and not review_issues(candidate, outcome.semantic_review)
            if outcome.machine_review_passed != review_passed:
                raise ValueError("machine_review_passed does not match bound semantic review")
            if outcome.status == "rejected":
                if not outcome.validation_issues or outcome.insight_id or outcome.duplicate_of:
                    raise ValueError("invalid rejection outcome")
                continue
            if candidate is None or outcome.validation_issues or candidate_issues(candidate, self.input_patterns):
                raise ValueError("invalid accepted/deduplicated candidate")
            if candidate_counts[candidate.insight_candidate_id] != 1:
                raise ValueError("duplicate candidate ID cannot be accepted")
            if review_issues(candidate, outcome.semantic_review):
                raise ValueError("missing or invalid semantic review")
            key = dedupe_key(candidate)
            if outcome.status == "deduplicated":
                if key not in seen or outcome.duplicate_of != seen[key] or outcome.insight_id:
                    raise ValueError("invalid dedupe reference")
                continue
            if key in seen or outcome.duplicate_of:
                raise ValueError("duplicate insight not deduplicated")
            expected = assemble_insight(self.input_patterns, candidate, outcome.semantic_review)
            if outcome.insight_id != expected.insight_id:
                raise ValueError("insight ID mismatch")
            seen[key] = expected.insight_id
            replayed.append(expected)
        if replayed != self.insights:
            raise ValueError("insight provenance, scope, metrics, statement or verification mismatch")
        if self.synthesis_status == "error" and not self.validation_issues:
            raise ValueError("synthesis error requires issue")
        return self
