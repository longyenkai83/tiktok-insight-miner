"""Append-only human product decisions, current-tree binding and atomic local storage."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import Field, StrictBool, field_validator, model_validator

from .governance_engine import value_hash
from .governance_store import atomic_json, file_lock
from .pattern_models import artifact_hash
from .product_engine import checked_discovery
from .product_models import ProductDiscovery
from .signal_models import StrictModel


class ProductAction(StrictModel):
    request_id: str = Field(min_length=1, max_length=100)
    tree_hash: str
    product_opportunity_id: str
    opportunity_hash: str
    decision: Literal['explore', 'reject', 'defer']
    reviewer_id: str = Field(min_length=1, max_length=120)
    human_attested: Literal[True]
    rationale: str = Field(min_length=1, max_length=8000)
    assumption_to_test_first: str | None = None
    assumption_importance: Literal['high', 'medium', 'low', 'unknown'] = 'unknown'
    riskiest_assumption: StrictBool = False

    @field_validator('request_id', 'reviewer_id', 'rationale')
    @classmethod
    def nonblank(cls, value):
        if not value.strip(): raise ValueError('blank_human_decision')
        return value

    @model_validator(mode='after')
    def choice_fields(self):
        if self.decision != 'explore' and (self.assumption_to_test_first or self.assumption_importance != 'unknown' or self.riskiest_assumption):
            raise ValueError('only_explore_may_choose_test')
        if not self.assumption_to_test_first and (self.assumption_importance != 'unknown' or self.riskiest_assumption):
            raise ValueError('assumption_required_for_importance')
        return self


class ProductEvent(StrictModel):
    event_id: str
    previous_event_id: str | None
    sequence: int
    action: ProductAction
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def event_hash(event):
    return 'PDEC-'+value_hash(event.model_dump(mode='json', exclude={'event_id'}))


def validate_action(action, tree):
    if action.tree_hash != artifact_hash(tree): raise ValueError('stale_product_tree')
    opp = next((o for o in tree.opportunities if o.product_opportunity_id == action.product_opportunity_id), None)
    if opp is None or artifact_hash(opp) != action.opportunity_hash: raise ValueError('unknown_or_changed_opportunity')
    if action.assumption_to_test_first is not None and not any(
        a.assumption_id == action.assumption_to_test_first and a.product_opportunity_id == action.product_opportunity_id for a in tree.assumptions):
        raise ValueError('unknown_or_foreign_assumption')


class ProductLedger(StrictModel):
    schema_version: Literal['v2.product-decisions.1'] = 'v2.product-decisions.1'
    revisions: list[ProductDiscovery] = Field(min_length=1)
    events: list[ProductEvent] = Field(default_factory=list)

    @model_validator(mode='after')
    def history(self):
        hashes = [artifact_hash(t) for t in self.revisions]
        if len(hashes) != len(set(hashes)): raise ValueError('duplicate_product_revision')
        previous, requests, position = None, set(), 0
        for n, e in enumerate(self.events, 1):
            if e.action.tree_hash not in hashes: raise ValueError('unknown_product_revision')
            at = hashes.index(e.action.tree_hash)
            if at < position: raise ValueError('historical_revision_reactivated')
            position = at
            validate_action(e.action, self.revisions[at])
            if e.sequence != n or e.previous_event_id != previous or e.event_id != event_hash(e):
                raise ValueError('broken_product_history')
            if e.reviewed_at.tzinfo is None or e.action.request_id in requests:
                raise ValueError('invalid_product_event')
            requests.add(e.action.request_id); previous = e.event_id
        return self


class SelectedProduct(StrictModel):
    product_opportunity_id: str
    opportunity_hash: str
    decision_event_id: str
    reviewer_id: str
    reviewed_at: datetime
    assumption_to_test_first: str | None
    assumption_importance: Literal['high', 'medium', 'low', 'unknown']
    riskiest_assumption: StrictBool
    # Human choice to test, not AI ranking or investment authorization.
    status: Literal['explore_for_testing'] = 'explore_for_testing'
    truth_type: Literal['PROPOSED'] = 'PROPOSED'
    validated_product: Literal[False] = False


def projection(ledger):
    h = artifact_hash(ledger.revisions[-1]); latest = {}
    for e in ledger.events:
        if e.action.tree_hash == h: latest[e.action.product_opportunity_id] = e
    return [SelectedProduct(product_opportunity_id=a.product_opportunity_id, opportunity_hash=a.opportunity_hash,
        decision_event_id=e.event_id, reviewer_id=a.reviewer_id, reviewed_at=e.reviewed_at,
        assumption_to_test_first=a.assumption_to_test_first, assumption_importance=a.assumption_importance,
        riskiest_assumption=a.riskiest_assumption)
        for e in latest.values() if (a := e.action).decision == 'explore']


class SelectedProducts(StrictModel):
    schema_version: Literal['v2.selected-product-opportunities.1'] = 'v2.selected-product-opportunities.1'
    decision_history: ProductLedger
    input_decisions_hash: str
    selected_opportunities: list[SelectedProduct]

    @model_validator(mode='after')
    def replay(self):
        if self.input_decisions_hash != artifact_hash(self.decision_history) or self.selected_opportunities != projection(self.decision_history):
            raise ValueError('selected_product_replay_mismatch')
        return self


def prepare_products(tree, reviews, previous=None):
    tree = checked_discovery(tree, reviews)
    if previous is None: return ProductLedger(revisions=[tree])
    previous = ProductLedger.model_validate(previous.model_dump())
    h = artifact_hash(tree)
    if h == artifact_hash(previous.revisions[-1]): return previous
    if h in {artifact_hash(t) for t in previous.revisions}: raise ValueError('historical_revision_reactivated')
    return ProductLedger(revisions=[*previous.revisions, tree], events=previous.events)


def current_ledger(ledger, tree, reviews):
    tree = checked_discovery(tree, reviews)
    ledger = ProductLedger.model_validate(ledger.model_dump())
    if artifact_hash(tree) != artifact_hash(ledger.revisions[-1]): raise ValueError('stale_product_tree')
    return ledger


def decide_product(ledger, tree, reviews, action):
    ledger = current_ledger(ledger, tree, reviews)
    action = ProductAction.model_validate(action.model_dump())
    validate_action(action, tree)
    previous = next((e for e in ledger.events if e.action.request_id == action.request_id), None)
    if previous:
        if previous.action == action: return ledger
        raise ValueError('request_id_reused')
    e = ProductEvent(event_id='pending', previous_event_id=ledger.events[-1].event_id if ledger.events else None,
        sequence=len(ledger.events)+1, action=action)
    e.event_id = event_hash(e)
    return ProductLedger(revisions=ledger.revisions, events=[*ledger.events, e])


def apply_products(ledger, tree, reviews):
    ledger = current_ledger(ledger, tree, reviews)
    return SelectedProducts(decision_history=ledger, input_decisions_hash=artifact_hash(ledger), selected_opportunities=projection(ledger))


def require_products(artifact, ledger, tree, reviews):
    if not isinstance(artifact, SelectedProducts): raise ValueError('typed_selected_products_required')
    artifact = SelectedProducts.model_validate(artifact.model_dump())
    expected = apply_products(ledger, tree, reviews)
    if expected != artifact: raise ValueError('stale_selected_products')
    return artifact.selected_opportunities


def load_discovery(path):
    return ProductDiscovery.model_validate_json(Path(path).read_text(encoding='utf-8'))


def load_product_ledger(path):
    return ProductLedger.model_validate_json(Path(path).read_text(encoding='utf-8'))


def save_discovery(tree, path, reviews, *, expected_hash=None):
    tree = checked_discovery(tree, reviews); path = Path(path)
    with file_lock(path):
        if path.exists():
            old = load_discovery(path)
            if artifact_hash(old) != expected_hash: raise ValueError('product_tree_changed_reload')
            if (old.project_id, old.run_id, old.verified_input) != (tree.project_id, tree.run_id, tree.verified_input) or tree.generations[:len(old.generations)] != old.generations:
                raise ValueError('product_history_is_append_only')
        elif expected_hash is not None: raise ValueError('expected_product_tree_missing')
        atomic_json(path, tree)


def prepare_product_file(tree, reviews, path):
    path = Path(path)
    with file_lock(path):
        old = load_product_ledger(path) if path.exists() else None
        new = prepare_products(tree, reviews, old)
        if new != old: atomic_json(path, new)
        return new


def decide_product_file(path, tree, reviews, action, *, expected_history_hash):
    with file_lock(path):
        old = load_product_ledger(path)
        if artifact_hash(old) != expected_history_hash and not any(e.action.request_id == action.request_id for e in old.events):
            raise ValueError('product_decisions_changed_reload')
        new = decide_product(old, tree, reviews, action)
        if new.events[:len(old.events)] != old.events: raise ValueError('product_history_is_append_only')
        if new != old: atomic_json(path, new)
        return new


def export_products(path, output, tree, reviews):
    if Path(path).resolve() == Path(output).resolve(): raise ValueError('cannot_overwrite_decision_history')
    with file_lock(path):
        result = apply_products(load_product_ledger(path), tree, reviews)
        with file_lock(output):
            if Path(output).exists(): SelectedProducts.model_validate_json(Path(output).read_text(encoding='utf-8'))
            atomic_json(output, result)
        return result
