"""Product research proposals: customer evidence is immutable; no demand validation."""
from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .evidence_models import EvidenceBundle
from .governance_models import VerifiedInsight, VerifiedInsightsEnvelope
from .pattern_models import EvidenceRef
from .signal_models import StrictModel

Text = Annotated[str, Field(min_length=1, max_length=700)]
LocalID = Annotated[str, Field(min_length=1, max_length=80)]
ProductType = Literal['tool', 'checklist', 'worksheet', 'template', 'calculator', 'diagnostic',
    'scorecard', 'guide', 'report', 'lead_magnet', 'course', 'workshop', 'service', 'feature',
    'automation', 'free_resource', 'paid_product', 'commercial_offer', 'other']
Risk = Literal['DESIRABILITY', 'FEASIBILITY', 'VIABILITY', 'SURVIVABILITY']


class Proposal(StrictModel):
    text: Text
    truth_type: Literal['PROPOSED'] = 'PROPOSED'


class ProgressCandidate(StrictModel):
    struggle_ref: str
    job_ref: str
    gain_ref: str | None = None
    desired_progress: Proposal
    need_moment_ref: str | None = None


class ServiceCandidate(StrictModel):
    local_id: LocalID
    description: Proposal
    target_refs: list[str] = Field(min_length=1, max_length=20)


class FitCandidate(StrictModel):
    local_id: LocalID
    service_id: str
    target_ref: str
    mechanism: Proposal


class MapCandidate(StrictModel):
    products_services: list[ServiceCandidate] = Field(min_length=1, max_length=10)
    pain_relievers: list[FitCandidate] = Field(default_factory=list, max_length=20)
    gain_creators: list[FitCandidate] = Field(default_factory=list, max_length=20)


class AssumptionCandidate(StrictModel):
    local_id: LocalID
    risk_category: Risk
    observable_behavior: Text
    offered_value: Text
    observation_method: Text
    truth_type: Literal['HYPOTHESIS'] = 'HYPOTHESIS'
    # Human assessment belongs to decision history, not model transport.


class TestThreshold(StrictModel):
    label: Literal['PROPOSED_TEST_THRESHOLD']
    metric: Text
    value: float = Field(allow_inf_nan=False)
    unit: Text
    operator: Literal['>=', '<=', '>', '<', '==']


class ExperimentCandidate(StrictModel):
    local_id: LocalID
    assumption_id: str
    target_evidence_level: int = Field(ge=1, le=5, strict=True)
    experiment_type: Literal['interview', 'prototype_reaction', 'behavior_test', 'commitment_test', 'market_test']
    procedure: Text
    measurement: Text
    success_condition: Text
    failure_condition: Text
    evidence_to_collect: Text
    threshold: TestThreshold | None = None
    truth_type: Literal['PROPOSED'] = 'PROPOSED'


class ProductCandidate(StrictModel):
    local_id: LocalID
    verified_insight_id: str
    opportunity_statement: Proposal
    opportunity_type: ProductType | None = None
    mechanism: Proposal
    delivery_mode: Literal['self_service', 'human_service', 'done_with_you', 'done_for_you', 'other']
    commercial_model: Literal['free', 'paid', 'undecided'] = 'undecided'
    progress: ProgressCandidate
    value_map: MapCandidate
    assumptions: list[AssumptionCandidate] = Field(min_length=1, max_length=12)
    experiments: list[ExperimentCandidate] = Field(min_length=1, max_length=12)


class ProductBatch(StrictModel):
    candidates: list[ProductCandidate] = Field(max_length=20)


class ProductValidation(StrictModel):
    customer_need_human_verified: Literal[True] = True
    product_demand_validated: Literal[False] = False
    market_validated: Literal[False] = False
    purchase_validated: Literal[False] = False
    validated_product: Literal[False] = False


class CustomerProgress(StrictModel):
    current_struggle: EvidenceRef
    job: EvidenceRef
    supported_gain: EvidenceRef | None
    desired_progress: Proposal
    need_moment: EvidenceRef | None


class ProductOpportunity(EvidenceBundle):
    schema_version: Literal['v2.product-opportunities.1'] = 'v2.product-opportunities.1'
    product_opportunity_id: str
    verified_insight_id: str
    priority_need: VerifiedInsight
    verified_insight_hash: str
    project_id: str
    run_id: str
    generation_id: str
    producer: str
    created_at: datetime
    opportunity_statement: Proposal
    opportunity_type: ProductType | None
    mechanism: Proposal
    delivery_mode: str
    commercial_model: str
    customer_progress: CustomerProgress
    customer_need_evidence_level: Literal[1] = 1
    solution_evidence_level: Literal[0] = 0
    truth_type: Literal['PROPOSED'] = 'PROPOSED'
    status: Literal['proposed'] = 'proposed'
    validation: ProductValidation = Field(default_factory=ProductValidation)


class Service(StrictModel):
    value_map_item_id: str
    description: Proposal
    target_customer_profile_refs: list[EvidenceRef]
    truth_type: Literal['PROPOSED'] = 'PROPOSED'


class FitLink(StrictModel):
    value_map_item_id: str
    product_service_id: str
    target_customer_profile_ref: EvidenceRef
    relationship: Literal['relieves', 'creates']
    mechanism: Proposal
    truth_type: Literal['PROPOSED'] = 'PROPOSED'


class ValueMap(StrictModel):
    schema_version: Literal['v2.value-maps.1'] = 'v2.value-maps.1'
    value_map_id: str
    product_opportunity_id: str
    products_services: list[Service]
    pain_relievers: list[FitLink]
    gain_creators: list[FitLink]
    truth_type: Literal['PROPOSED'] = 'PROPOSED'


class Assumption(StrictModel):
    schema_version: Literal['v2.product-assumptions.1'] = 'v2.product-assumptions.1'
    assumption_id: str
    product_opportunity_id: str
    risk_category: Risk
    observable_behavior: Text
    offered_value: Text
    observation_method: Text
    # Population/context are taken only from the parent priority_need, never invented.
    subject_scope_ref: str
    truth_type: Literal['HYPOTHESIS'] = 'HYPOTHESIS'
    importance: Literal['unknown'] = 'unknown'
    evidence_strength: Literal[0] = 0
    riskiest_assumption: Literal[False] = False


class ExperimentPlan(StrictModel):
    schema_version: Literal['v2.experiment-plans.1'] = 'v2.experiment-plans.1'
    experiment_id: str
    product_opportunity_id: str
    assumption_id: str
    plan: ExperimentCandidate
    current_evidence_level: Literal[0] = 0
    truth_type: Literal['PROPOSED'] = 'PROPOSED'
    status: Literal['plan_only'] = 'plan_only'
    caution: str | None


class Generation(StrictModel):
    generation_id: str
    verified_insight_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    producer: str
    requested_count: int = Field(ge=1, le=20)
    payload: dict
    error: Literal['generation_error'] | None = None


class ProductIssue(StrictModel):
    generation_id: str
    item_index: int | None = None
    code: str


class ProductDiscovery(StrictModel):
    schema_version: Literal['v2.product-discovery.1'] = 'v2.product-discovery.1'
    project_id: Text
    run_id: Text
    verified_input: VerifiedInsightsEnvelope
    input_verified_hash: str
    generations: list[Generation] = Field(default_factory=list)
    opportunities: list[ProductOpportunity] = Field(default_factory=list)
    value_maps: list[ValueMap] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)
    experiment_plans: list[ExperimentPlan] = Field(default_factory=list)
    validation_issues: list[ProductIssue] = Field(default_factory=list)

    @model_validator(mode='after')
    def replay(self):
        from .product_engine import priority_inputs, compile_discovery
        from .pattern_models import artifact_hash
        priority_inputs(self.verified_input, self.verified_input.review_history)
        if artifact_hash(self.verified_input) != self.input_verified_hash:
            raise ValueError('verified_input_hash_mismatch')
        expected = compile_discovery(self.project_id, self.run_id, self.verified_input, self.generations)
        if expected != (self.opportunities, self.value_maps, self.assumptions, self.experiment_plans, self.validation_issues):
            raise ValueError('product_provenance_replay_mismatch')
        return self
