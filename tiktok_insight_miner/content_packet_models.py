"""Portable, strict packet contract. No Writer output or product objects in this schema."""
from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from .content_route_models import AngleType, ProposedText, Purpose, ValueScene
from .content_selection import SelectedAngle
from .governance_models import VerifiedInsight
from .pattern_models import EvidenceRef
from .signal_models import SignalSource, StrictModel


class PacketProject(StrictModel):
    project_id: str
    project_goal: Literal['CONTENT', 'BOTH'] = 'CONTENT'
    research_run_id: str
    # Taken only from source platform metadata; unknown is not guessed.
    source_route_context: list[str]


class LanguageBank(StrictModel):
    exact_phrases: list[EvidenceRef]
    emotional_wording: list[EvidenceRef]
    repeated_expressions: list[EvidenceRef]
    repetition_scope: Literal['within_source_comment_not_corpus_frequency'] = 'within_source_comment_not_corpus_frequency'


class CustomerTruthZone(StrictModel):
    zone: Literal['A_CUSTOMER_TRUTH'] = 'A_CUSTOMER_TRUTH'
    immutable: Literal[True] = True
    verified_insight: VerifiedInsight
    language_bank: LanguageBank
    representative_quotes: list[EvidenceRef]
    source_snapshots: list[SignalSource]


class PacketOpportunity(StrictModel):
    content_opportunity_id: str
    statement: ProposedText
    purpose: Purpose
    customer_value: ProposedText
    truth_type: Literal['PROPOSED'] = 'PROPOSED'


class PacketTopic(StrictModel):
    topic_id: str
    title: ProposedText
    description: ProposedText
    customer_value: ProposedText
    truth_type: Literal['PROPOSED'] = 'PROPOSED'


class PacketAngle(StrictModel):
    angle_id: str
    title: ProposedText
    angle_type: AngleType
    core_argument: ProposedText
    belief_before: ProposedText
    belief_after: ProposedText
    opening_direction: ProposedText
    customer_value: ProposedText
    truth_type: Literal['PROPOSED'] = 'PROPOSED'


class StrategyZone(StrictModel):
    zone: Literal['B_SELECTED_STRATEGY'] = 'B_SELECTED_STRATEGY'
    truth_type: Literal['PROPOSED'] = 'PROPOSED'
    opportunity: PacketOpportunity
    topic: PacketTopic
    angle: PacketAngle
    value_scene: ValueScene
    content_objective: ProposedText | None


class WriterMay(StrictModel):
    create_hooks: Literal[True] = True
    create_titles: Literal[True] = True
    create_structure: Literal[True] = True
    create_analogies: Literal[True] = True
    create_metaphors: Literal[True] = True
    create_clearly_labeled_illustrative_examples: Literal[True] = True
    choose_storytelling_format: Literal[True] = True
    adapt_brand_voice: Literal[True] = True
    improve_clarity: Literal[True] = True
    generate_cta: Literal[True] = True


class CreativeConstraints(StrictModel):
    no_fake_statistics: Literal[True] = True
    no_fake_case_studies: Literal[True] = True
    no_fake_customers: Literal[True] = True
    no_fake_quotes: Literal[True] = True
    no_fake_demographics: Literal[True] = True
    no_fake_research: Literal[True] = True
    preserve_customer_language: Literal[True] = True
    do_not_change_customer_truth: Literal[True] = True
    external_claims_require_evidence: Literal[True] = True
    no_evidence_level_upgrade: Literal[True] = True
    no_market_validation_claim: Literal[True] = True
    no_purchase_validation_claim: Literal[True] = True
    preserve_contradictions_and_limitations: Literal[True] = True


class ExecutionZone(StrictModel):
    zone: Literal['C_CREATIVE_EXECUTION'] = 'C_CREATIVE_EXECUTION'
    status: Literal['not_generated'] = 'not_generated'
    writer_may: WriterMay = Field(default_factory=WriterMay)
    constraints: CreativeConstraints = Field(default_factory=CreativeConstraints)


class ExternalRequirement(StrictModel):
    strategy_field: str
    claim_needed: str
    purpose: Literal['verify_proposed_framing_before_publication'] = 'verify_proposed_framing_before_publication'
    status: Literal['required_before_publish'] = 'required_before_publish'


class PacketLineage(StrictModel):
    verified_insight_id: str
    source_candidate_id: str
    pattern_ids: list[str]
    comment_ids: list[str]
    source_hashes: list[str]
    content_opportunity_id: str
    topic_id: str
    angle_id: str
    governance_hash: str
    verified_artifact_hash: str
    selection_hash: str
    selected_artifact_hash: str
    content_tree_hash: str
    verified_insight_hash: str
    opportunity_hash: str
    topic_hash: str
    angle_hash: str


class ContentIntelligencePacket(StrictModel):
    schema_version: Literal['v2.content-intelligence-packet.1']
    packet_id: str = Field(pattern=r'^CIP-[0-9a-f]{64}$')
    packet_revision: int = Field(ge=1, strict=True)
    supersedes_packet_id: str | None = Field(default=None, pattern=r'^CIP-[0-9a-f]{64}$')
    created_at: datetime
    producer: Literal['customer-intelligence:content-packet.1'] = 'customer-intelligence:content-packet.1'
    project: PacketProject
    customer_truth: CustomerTruthZone
    content_strategy: StrategyZone
    creative_execution: ExecutionZone = Field(default_factory=ExecutionZone)
    external_evidence_requirements: list[ExternalRequirement]
    selection: SelectedAngle
    lineage: PacketLineage

    @model_validator(mode='after')
    def snapshot_integrity(self):
        from .content_packet_validator import validate_snapshot
        validate_snapshot(self)
        return self
