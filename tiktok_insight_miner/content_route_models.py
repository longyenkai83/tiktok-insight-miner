"""Separable content types; all generated text is a proposal, never customer truth."""
from datetime import datetime, timezone
from typing import Literal

from pydantic import Field, model_validator

from .evidence_models import EvidenceBundle
from .governance_models import VerifiedInsightsEnvelope, VerifiedStatement
from .pattern_models import EvidenceRef
from .signal_models import StrictModel

Purpose = Literal["educate", "diagnose", "reframe", "answer_question", "handle_objection",
    "show_process", "show_mistake", "show_tradeoff", "decision_support", "story", "social_proof", "other"]
AngleType = Literal["contrarian", "diagnostic", "how_to", "mistake", "myth_busting", "question_answer",
    "decision_framework", "story", "comparison", "checklist", "warning", "case_lens", "other"]


class ProposedText(StrictModel):
    text: str = Field(min_length=1, max_length=600)
    claim_kind: Literal["general_explanatory", "creative_framing"]
    truth_type: Literal["PROPOSED"] = "PROPOSED"
    # Conservative: even creative framing must be checked for incidental external claims.
    needs_external_evidence: Literal[True] = True


class SceneChoice(StrictModel):
    evidence_id: str | None = None
    proposed: ProposedText | None = None

    @model_validator(mode="after")
    def one_kind(self):
        if (self.evidence_id is None) == (self.proposed is None):
            raise ValueError("Value Scene requires either a closed evidence ID or proposed framing")
        return self


class SceneProposal(StrictModel):
    need_moment: SceneChoice | None = None
    current_struggle: SceneChoice | None = None
    desired_future: SceneChoice | None = None


class OpportunityProposal(StrictModel):
    local_id: str = Field(min_length=1, max_length=80)
    verified_insight_id: str
    statement: ProposedText
    purpose: Purpose
    customer_value: ProposedText


class TopicProposal(StrictModel):
    local_id: str = Field(min_length=1, max_length=80)
    content_opportunity_id: str
    title: ProposedText
    description: ProposedText
    customer_value: ProposedText


class AngleProposal(StrictModel):
    local_id: str = Field(min_length=1, max_length=80)
    topic_id: str
    title: ProposedText
    angle_type: AngleType
    core_argument: ProposedText
    belief_before: ProposedText
    belief_after: ProposedText
    opening_direction: ProposedText
    customer_value: ProposedText
    value_scene: SceneProposal = Field(default_factory=SceneProposal)


class OpportunityBatch(StrictModel):
    candidates: list[OpportunityProposal]


class TopicBatch(StrictModel):
    candidates: list[TopicProposal]


class AngleBatch(StrictModel):
    candidates: list[AngleProposal]


class Constraints(StrictModel):
    no_fake_statistics: Literal[True] = True
    no_fake_case_studies: Literal[True] = True
    no_fake_customers: Literal[True] = True
    no_fake_quotes: Literal[True] = True
    no_fake_demographics: Literal[True] = True
    no_fake_research: Literal[True] = True
    no_final_script: Literal[True] = True
    no_product_discovery: Literal[True] = True


class GroundedScene(StrictModel):
    kind: Literal["source_wording"] = "source_wording"
    text: str
    truth_type: Literal["OBSERVED", "DERIVED"]
    evidence_ref: EvidenceRef


class ProposedScene(StrictModel):
    kind: Literal["proposed_framing"] = "proposed_framing"
    framing: ProposedText


class ValueScene(StrictModel):
    truth_type: Literal["PROPOSED"] = "PROPOSED"
    need_moment: GroundedScene | ProposedScene | None = None
    current_struggle: GroundedScene | ProposedScene | None = None
    desired_future: GroundedScene | ProposedScene | None = None


class ContentBase(EvidenceBundle):
    project_id: str
    run_id: str
    verified_insight_id: str
    verified_insight_hash: str
    customer_truth: VerifiedStatement
    support_pattern_ids: list[str]
    truth_type: Literal["PROPOSED"] = "PROPOSED"
    status: Literal["generated"] = "generated"
    created_at: datetime
    generation_id: str
    producer: str
    constraints: Constraints = Field(default_factory=Constraints)


class ContentOpportunity(ContentBase):
    schema_version: Literal["v2.content-opportunities.1"] = "v2.content-opportunities.1"
    content_opportunity_id: str
    statement: ProposedText
    purpose: Purpose
    customer_value: ProposedText


class Topic(ContentBase):
    schema_version: Literal["v2.topics.1"] = "v2.topics.1"
    topic_id: str
    content_opportunity_id: str
    title: ProposedText
    description: ProposedText
    customer_value: ProposedText


class Angle(ContentBase):
    schema_version: Literal["v2.angles.1"] = "v2.angles.1"
    angle_id: str
    topic_id: str
    content_opportunity_id: str
    title: ProposedText
    angle_type: AngleType
    core_argument: ProposedText
    belief_before: ProposedText
    belief_after: ProposedText
    opening_direction: ProposedText
    customer_value: ProposedText
    value_scene: ValueScene
    language_bank: list[EvidenceRef]


class GenerationBatch(StrictModel):
    generation_id: str
    stage: Literal["opportunities", "topics", "angles"]
    parent_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    producer: str
    requested_count: int = Field(ge=1, le=50)
    content_objective: str = Field(default="", max_length=600)
    angle_type_preference: AngleType | None = None
    payload: dict
    error_code: Literal["generation_error"] | None = None


class RouteIssue(StrictModel):
    generation_id: str
    item_index: int | None = None
    code: str


class ContentTree(StrictModel):
    schema_version: Literal["v2.content-tree.1"] = "v2.content-tree.1"
    project_id: str = Field(min_length=1, max_length=100)
    run_id: str = Field(min_length=1, max_length=100)
    verified_input: VerifiedInsightsEnvelope
    input_verified_hash: str
    batches: list[GenerationBatch] = Field(default_factory=list)
    content_opportunities: list[ContentOpportunity] = Field(default_factory=list)
    topics: list[Topic] = Field(default_factory=list)
    angles: list[Angle] = Field(default_factory=list)
    validation_issues: list[RouteIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def replay(self):
        from .content_route_engine import compile_tree
        from .governance_engine import require_verified
        from .pattern_models import artifact_hash
        require_verified(self.verified_input, self.verified_input.review_history)
        if artifact_hash(self.verified_input) != self.input_verified_hash:
            raise ValueError("verified input hash mismatch")
        expected = compile_tree(self.project_id, self.run_id, self.verified_input, self.batches)
        actual = (self.content_opportunities, self.topics, self.angles, self.validation_issues)
        if actual != expected:
            raise ValueError("content tree provenance/proposal/evidence replay mismatch")
        return self
