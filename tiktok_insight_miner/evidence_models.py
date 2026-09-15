"""Platform-neutral evidence views; text self-reports never prove payment."""
from enum import Enum
from typing import Literal

from pydantic import Field

from .pattern_models import ContextVariant, CounterEvidence, EvidenceRef, Support, Variation
from .signal_models import StrictModel


class EvidenceKind(str, Enum):
    CUSTOMER_SPEECH = "customer_speech"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    COMMITMENT = "commitment"
    PAYMENT = "payment"
    MARKET_BEHAVIOR = "market_behavior"


class Verification(StrictModel):
    source_grounded: Literal[True] = True
    evidence_backed: Literal[True] = True
    human_verified: Literal[False] = False
    market_validated: Literal[False] = False
    purchase_validated: Literal[False] = False


class CustomerProfileLinks(StrictModel):
    jobs: list[str] = Field(default_factory=list)
    pains: list[str] = Field(default_factory=list)
    gains: list[str] = Field(default_factory=list)
    behavior: list[str] = Field(default_factory=list)
    language: list[str] = Field(default_factory=list)
    context: list[str] = Field(default_factory=list)


class InsightScope(StrictModel):
    population: Literal["cited_source_comments_only"] = "cited_source_comments_only"
    relationship_scope: Literal["within_comments", "across_corpus"]
    source_comment_ids: list[str]
    shared_comment_ids: list[str]
    audience_segment: list[ContextVariant] = Field(default_factory=list)
    context: list[ContextVariant] = Field(default_factory=list)
    situation: list[ContextVariant] = Field(default_factory=list)
    life_or_business_stage: list[ContextVariant] = Field(default_factory=list)
    user_buyer_distinction: list[ContextVariant] = Field(default_factory=list)
    missing_context_comments: list[str]


class EvidenceBundle(StrictModel):
    customer_profile_links: CustomerProfileLinks
    scope: InsightScope
    evidence_summary: Support
    evidence_refs: list[EvidenceRef]
    variations: list[Variation]
    contradictions: list[CounterEvidence]
    # Future kinds are vocabulary only; current input schema has text evidence only.
    evidence_kind: list[Literal["customer_speech"]]
    limitations: list[str]
