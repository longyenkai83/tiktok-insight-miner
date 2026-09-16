"""Trusted local human correction API; never exposed to a generation provider.

One atomic selection-ledger append contains the new tree, audit and selection.
The audit lives in GenerationBatch.payload (already an open transport container),
not in the portable Phase8 packet. Local attestation is not user authentication.
"""
from datetime import datetime, timezone
from typing import Literal

from pydantic import Field

from .content_route_models import AngleProposal, ContentTree, GenerationBatch
from .governance_engine import value_hash
from .pattern_models import artifact_hash
from .signal_models import StrictModel

PRODUCER = 'human-owner-correction.v1'


class OwnerCorrection(StrictModel):
    request_id: str = Field(min_length=1)
    expected_selection_hash: str
    previous_angle_id: str
    previous_angle_hash: str
    reviewer_id: str = Field(min_length=1)
    actor_kind: Literal['human']
    human_attested: Literal[True]
    correction_rationale: str = Field(min_length=1, max_length=8000)
    content_objective: str = Field(default='', max_length=600)
    corrected: AngleProposal


def supersessions(tree):
    return {b.payload['owner_correction']['previous_angle_id']:
            b.payload['owner_correction']['new_angle_id']
            for b in tree.batches if b.producer == PRODUCER}


def audit_id(record):
    return 'COR-' + value_hash({k: v for k, v in record.items() if k != 'correction_event_id'})


def validate_batch_audit(batch, angles, project_id, run_id):
    """Called by deterministic tree replay AFTER compiling the one new angle."""
    record = batch.payload.get('owner_correction')
    if not isinstance(record, dict):
        raise ValueError('owner_correction_audit_missing')
    request = OwnerCorrection.model_validate(record['request'])
    old = angles.get(request.previous_angle_id)
    new = angles.get(record['new_angle_id'])
    if old is None or new is None:
        raise ValueError('owner_correction_angle_missing')
    if (request.previous_angle_hash != artifact_hash(old)
            or request.corrected.model_dump(mode='json') != batch.payload['candidates'][0]
            or request.corrected.topic_id != old.topic_id
            or new.generation_id != batch.generation_id
            or old.core_argument == new.core_argument):
        raise ValueError('owner_correction_request_mismatch')
    expected = make_audit(request, old, new, batch, record['previous_selection_event_id'])
    if record != expected or new.project_id != project_id or new.run_id != run_id:
        raise ValueError('owner_correction_audit_mismatch')
    if not request.reviewer_id.strip() or not request.correction_rationale.strip():
        raise ValueError('owner_correction_human_details_required')


def make_audit(request, old, new, batch, previous_selection_event_id):
    record = dict(request=request.model_dump(mode='json'), previous_angle_id=old.angle_id,
        new_angle_id=new.angle_id, supersedes=old.angle_id, superseded_by=new.angle_id,
        project_id=old.project_id, run_id=old.run_id, reviewer_id=request.reviewer_id,
        reviewed_at=batch.created_at.isoformat(), correction_rationale=request.correction_rationale,
        previous_core_argument=old.core_argument.model_dump(mode='json'),
        corrected_core_argument=new.core_argument.model_dump(mode='json'),
        previous_angle_hash=artifact_hash(old), new_angle_hash=artifact_hash(new),
        previous_selection_event_id=previous_selection_event_id,
        previous_selection_hash=request.expected_selection_hash,
        truth_type='PROPOSED', human_attested=True)
    record['correction_event_id'] = audit_id(record)
    return record


def correct_angle(ledger, reviews, raw):
    from .content_route_engine import compile_tree, checked_tree
    from .content_selection import (SelectionLedger, SelectionAction, apply_selection,
                                    prepare_selection, select_angle)
    request = OwnerCorrection.model_validate(raw)
    ledger = SelectionLedger.model_validate(ledger.model_dump())
    for b in ledger.trees[-1].batches:
        if b.producer == PRODUCER and b.payload['owner_correction']['request']['request_id'] == request.request_id:
            if b.payload['owner_correction']['request'] != request.model_dump(mode='json'):
                raise ValueError('correction_request_id_already_used')
            checked_tree(ledger.trees[-1], reviews)
            return ledger  # Exact retry is read-only, never reselects an old revision.
    if artifact_hash(ledger) != request.expected_selection_hash:
        raise ValueError('stale_owner_correction')
    tree = checked_tree(ledger.trees[-1], reviews)
    selected = next((s for s in apply_selection(ledger, reviews).selected_angles
                     if s.angle_id == request.previous_angle_id), None)
    old = next((a for a in tree.angles if a.angle_id == request.previous_angle_id), None)
    if selected is None or old is None or artifact_hash(old) != request.previous_angle_hash:
        raise ValueError('correction_requires_current_selected_angle')
    if request.corrected.topic_id != old.topic_id:
        raise ValueError('correction_cannot_change_upstream_topic')
    if request.corrected.core_argument == old.core_argument:
        raise ValueError('correction_requires_changed_argument')
    generation = 'GEN-' + value_hash(request.model_dump(mode='json'))
    # Compile using the ordinary proposal/evidence guards before adding audit metadata.
    batch = GenerationBatch(generation_id=generation, stage='angles', parent_id=old.topic_id,
        producer=PRODUCER, requested_count=1, created_at=datetime.now(timezone.utc),
        content_objective=request.content_objective,
        payload={'candidates': [request.corrected.model_dump(mode='json')]})
    provisional = batch.model_copy(update={'producer': 'owner-correction-validation'})
    outputs = compile_tree(tree.project_id, tree.run_id, tree.verified_input, [*tree.batches, provisional])
    new_id = 'ANG-' + value_hash({'generation': generation, 'parent': old.topic_id,
                                 'local': request.corrected.local_id})
    new = next((a for a in outputs[2] if a.angle_id == new_id), None)
    if new is None:
        raise ValueError('corrected_angle_failed_proposal_guards')
    new = new.model_copy(update={'producer': PRODUCER})
    batch.payload['owner_correction'] = make_audit(request, old, new, batch, selected.selection_event_id)
    outputs = compile_tree(tree.project_id, tree.run_id, tree.verified_input, [*tree.batches, batch])
    revised = ContentTree(project_id=tree.project_id, run_id=tree.run_id,
        verified_input=tree.verified_input, input_verified_hash=tree.input_verified_hash,
        batches=[*tree.batches, batch], content_opportunities=outputs[0], topics=outputs[1],
        angles=outputs[2], validation_issues=outputs[3])
    current = prepare_selection(revised, reviews, ledger)
    return select_angle(current, reviews, SelectionAction(request_id='correction:'+request.request_id,
        tree_hash=artifact_hash(revised), angle_id=new_id, angle_hash=artifact_hash(new),
        decision='selected', reviewer_id=request.reviewer_id, human_attested=True,
        rationale=request.correction_rationale))


def correct_angle_file(path, reviews, raw):
    from .content_selection import load_selection
    from .governance_store import file_lock, atomic_json
    with file_lock(path):
        old = load_selection(path)
        new = correct_angle(old, reviews, raw)
        if new.trees[:len(old.trees)] != old.trees or new.events[:len(old.events)] != old.events:
            raise ValueError('correction_history_must_be_append_only')
        if new != old:
            atomic_json(path, new)
        return new
