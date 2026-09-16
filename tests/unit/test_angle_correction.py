"""Synthetic human authority only; no model/network or real customer data."""
import json
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest

from tests.fixtures.content_packet_fixture import synthetic_state, synthetic_packet
from tiktok_insight_miner.angle_correction import correct_angle, correct_angle_file, PRODUCER
from tiktok_insight_miner.content_selection import (apply_selection, select_angle, SelectionAction,
    load_selection, prepare_selection)
from tiktok_insight_miner.content_route_models import ContentTree
from tiktok_insight_miner.content_route_engine import extend_content_tree
from tiktok_insight_miner.content_packet_builder import build_packet
from tiktok_insight_miner.content_packet_validator import validate_current, validate_revision
from tiktok_insight_miner.pattern_models import artifact_hash
from tiktok_insight_miner.governance_store import atomic_json


def request(state):
    old = state['tree'].angles[0]
    fields = ('topic_id', 'title', 'angle_type', 'core_argument', 'belief_before',
              'belief_after', 'opening_direction', 'customer_value')
    proposal = {k: old.model_dump(mode='json')[k] for k in fields}
    proposal.update(local_id='owner-corrected', value_scene={})
    proposal['core_argument']['text'] = 'Consider revenue and all relevant costs before interpreting the remaining amount.'
    return dict(request_id='SYNTHETIC-correction', expected_selection_hash=artifact_hash(state['ledger']),
        previous_angle_id=old.angle_id, previous_angle_hash=artifact_hash(old),
        reviewer_id='SYNTHETIC TEST owner', actor_kind='human', human_attested=True,
        correction_rationale='SYNTHETIC owner changes explanatory frame', corrected=proposal)


def revised(state, raw):
    ledger = correct_angle(state['ledger'], state['reviews'], raw)
    return {**state, 'tree': ledger.trees[-1], 'ledger': ledger,
            'selected': apply_selection(ledger, state['reviews'])}


def test_owner_revision_packet_and_immutable_history(tmp_path):
    state = synthetic_state(); raw = request(state)
    old_packet = synthetic_packet(state); before = state['tree'].model_dump_json()
    new = revised(state, raw); angle = new['selected'].selected_angles[0]
    assert state['tree'].model_dump_json() == before
    assert new['tree'].angles[:-1] == state['tree'].angles
    assert new['ledger'].events[:-1] == state['ledger'].events
    assert angle.angle_id != raw['previous_angle_id']
    assert len(new['selected'].selected_angles) == 1
    audit = new['tree'].batches[-1].payload['owner_correction']
    assert audit['supersedes'] == raw['previous_angle_id']
    assert audit['superseded_by'] == angle.angle_id
    assert audit['human_attested'] and audit['truth_type'] == 'PROPOSED'
    packet = build_packet(**new, angle_id=angle.angle_id, previous=old_packet)
    assert validate_revision(packet, old_packet) == packet
    assert packet.customer_truth == old_packet.customer_truth
    assert packet.supersedes_packet_id == old_packet.packet_id
    assert packet.content_strategy.angle.core_argument.text == raw['corrected']['core_argument']['text']
    with pytest.raises(ValueError): validate_current(old_packet, **new)
    with pytest.raises(ValueError):
        select_angle(new['ledger'], state['reviews'], SelectionAction(
            request_id='revive', tree_hash=artifact_hash(new['tree']), angle_id=raw['previous_angle_id'],
            angle_hash=raw['previous_angle_hash'], reviewer_id='SYNTHETIC TEST', human_attested=True, decision='selected'))
    schema = json.loads((Path(__file__).parents[2]/'contracts/content-intelligence-packet.schema.json').read_text())
    jsonschema.validate(packet.model_dump(mode='json'), schema)
    path = tmp_path/'selection.json'; atomic_json(path, state['ledger'])
    saved = correct_angle_file(path, state['reviews'], raw)
    assert saved == correct_angle_file(path, state['reviews'], raw) == load_selection(path)


@pytest.mark.parametrize('field,value', [('actor_kind','model'), ('human_attested',False),
    ('expected_selection_hash','stale'), ('previous_angle_hash','changed'), ('reviewer_id',' ')])
def test_no_model_authority_or_stale_edit(field,value):
    s = synthetic_state(); raw = request(s); raw[field] = value
    with pytest.raises(ValueError): correct_angle(s['ledger'], s['reviews'], raw)


def test_audit_tamper_and_model_transport_rejected():
    s=synthetic_state(); n=revised(s,request(s)); data=n['tree'].model_dump(mode='json')
    data['batches'][-1]['payload']['owner_correction']['corrected_core_argument']['text']='tampered'
    with pytest.raises(ValueError): ContentTree.model_validate(data)
    class Model:
        name=PRODUCER
        def generate(self,*args): raise AssertionError('Must not call model')
    with pytest.raises(ValueError,match='model_cannot'):
        extend_content_tree(s['tree'],s['reviews'],stage='angles',parent_id=s['tree'].topics[0].topic_id,provider=Model())
    dropped=s['tree'].model_copy(update={'run_id':'other'})
    with pytest.raises(ValueError): prepare_selection(dropped,s['reviews'],n['ledger'])
