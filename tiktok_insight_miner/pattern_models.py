"""Closed, replayable Phase 3 contract. Patterns never assert verified truth."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Literal

from pydantic import Field, model_validator

from .customer_context_models import ContextsEnvelope, ContextField
from .signal_models import SignalsEnvelope, StrictModel, TruthType, ValidationIssue


def artifact_hash(model: StrictModel) -> str:
    return hashlib.sha256(json.dumps(model.model_dump(mode="json"),
        ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class EvidenceRef(StrictModel):
    evidence_id: str
    origin: Literal["signal", "context"]
    upstream_claim_id: str
    comment_id: str
    source_record_id: str
    source_hash: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    evidence_quote: str
    signal_path: str
    truth_type: TruthType


class Relation(StrictModel):
    left: str
    right: str
    kind: Literal["same_meaning", "variation", "contradiction"]
    truth_type: Literal["DERIVED"] = "DERIVED"


class RelationBatch(StrictModel):
    relations: list[Relation]


class Support(StrictModel):
    comment_count: int = Field(ge=0)
    unique_authors: int | None = Field(default=None, ge=0)
    known_author_count: int = Field(ge=0)
    unknown_author_comments: int = Field(ge=0)
    source_count: int | None = Field(default=None, ge=0)
    known_source_count: int = Field(ge=0)
    unknown_source_comments: int = Field(ge=0)
    total_likes: int | None = Field(default=None, ge=0)
    known_likes_sum: int = Field(ge=0)
    unknown_likes_comments: int = Field(ge=0)
    total_replies: int | None = Field(default=None, ge=0)
    known_replies_sum: int = Field(ge=0)
    unknown_replies_comments: int = Field(ge=0)


class Variation(StrictModel):
    label: str
    truth_type: Literal["DERIVED"] = "DERIVED"
    evidence_refs: list[EvidenceRef]


class ContextVariant(Variation):
    field: ContextField
    support: Support


class CounterEvidence(StrictModel):
    supporting_ref: EvidenceRef
    counter_ref: EvidenceRef
    truth_type: Literal["DERIVED"] = "DERIVED"
    status: Literal["possible_contradiction"] = "possible_contradiction"


class LanguagePhrase(StrictModel):
    phrase: str
    evidence_refs: list[EvidenceRef]
    support: Support


class Pattern(StrictModel):
    pattern_id: str
    pattern_type: Literal["jobs", "pains", "gains", "behavior", "language", "context"]
    subcategory: str
    label: str
    normalized_meaning: str
    truth_type: Literal["DERIVED"] = "DERIVED"
    support: Support
    evidence_refs: list[EvidenceRef]
    context_distribution: list[ContextVariant]
    missing_context_comments: list[str]
    variations: list[Variation]
    contradictions: list[CounterEvidence]
    contradiction_search: Literal["NOT_CHECKED", "CHECKED_WITHIN_INPUT"]
    pattern_status: Literal["candidate"] = "candidate"
    validation_issues: list[ValidationIssue] = Field(default_factory=list)


class PatternsEnvelope(StrictModel):
    schema_version: Literal["v2.patterns.1"] = "v2.patterns.1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    method: Literal["closed_relations_complete_link.1"] = "closed_relations_complete_link.1"
    label_method: Literal["extractive_representative.1"] = "extractive_representative.1"
    similarity_provider: str
    semantic_status: Literal["complete", "not_requested", "error"]
    input_signals_hash: str
    input_contexts_hash: str | None
    # Self-contained snapshots permit source AND upstream-membership checks on load.
    input_signals: SignalsEnvelope
    input_contexts: ContextsEnvelope | None
    relations: list[Relation]
    patterns: list[Pattern]
    language_bank: list[LanguagePhrase]
    validation_issues: list[ValidationIssue]
    limitations: list[str]

    @model_validator(mode="after")
    def replay(self) -> PatternsEnvelope:
        from .pattern_engine import catalog_for, compile_patterns, validate_relations
        if artifact_hash(self.input_signals) != self.input_signals_hash:
            raise ValueError("signals artifact hash mismatch")
        expected = artifact_hash(self.input_contexts) if self.input_contexts else None
        if expected != self.input_contexts_hash:
            raise ValueError("contexts artifact hash mismatch")
        catalog, sources, contexts, upstream_issues = catalog_for(self.input_signals, self.input_contexts)
        if any(i not in self.validation_issues for i in upstream_issues):
            raise ValueError("upstream validation issues must be preserved")
        if self.semantic_status == "not_requested" and self.relations:
            raise ValueError("exact-only cannot contain semantic relations")
        if self.semantic_status == "error" and not self.validation_issues:
            raise ValueError("semantic error requires issues")
        accepted, issues = validate_relations(catalog, [r.model_dump() for r in self.relations])
        if issues or accepted != self.relations:
            raise ValueError("invalid persisted relations")
        patterns, language = compile_patterns(catalog, sources, contexts, accepted,
            self.semantic_status == "complete")
        if self.patterns != patterns or self.language_bank != language:
            raise ValueError("pattern membership, provenance or deterministic output mismatch")
        return self
