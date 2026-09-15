"""Synthetic-only contract producer; no customer data or real human decisions."""
from datetime import datetime, timezone
from unittest.mock import Mock
from tests.unit.test_content_route import ContentProvider, text
from tests.unit.test_governance import action
from tests.unit.test_insight_engine import FakeProvider, candidate
from tiktok_insight_miner.content_route_engine import build_content_tree
from tiktok_insight_miner.content_selection import SelectionAction, prepare_selection, select_angle, apply_selection
from tiktok_insight_miner.governance_engine import prepare_review, record_review, apply_reviews
from tiktok_insight_miner.insight_engine import build_insights
from tiktok_insight_miner.pattern_engine import build_patterns
from tiktok_insight_miner.pattern_models import artifact_hash
from tiktok_insight_miner.signal_extractor import source_from_comment, validate_batch
from tiktok_insight_miner.signal_models import SignalsEnvelope
from tiktok_insight_miner.content_packet_builder import build_packet


def synthetic_state():
    sources=[source_from_comment(dict(id=f'SYNTHETIC-{i}',platform='synthetic_fixture',
        text='SYNTHETIC TEST ONLY. I want stable income; '+pain+'; rent feels like a weight.'))
        for i,pain in enumerate(['rent consumes my profit','rent is manageable'])]
    rows,_=validate_batch(sources,dict(results=[dict(comment_id=s.comment_id,signals=[
        dict(category=cat,subcategory=sub,evidence_quote=quote,truth_type='OBSERVED',confidence='high')
        for cat,sub,quote in [('jobs','functional','I want stable income'),('pains','costs',s.text.split('; ')[1]),
                             ('language','emotional_wording','rent feels like a weight')]]) for s in sources]))
    relation_provider=Mock(); relation_provider.name='synthetic-relations'
    def compare(catalog):
        pains=[r for r in catalog if r['signal_path'].startswith('pains.')]
        return dict(relations=[dict(left=pains[0]['evidence_id'],right=pains[1]['evidence_id'],kind='contradiction')])
    relation_provider.compare.side_effect=compare
    patterns=build_patterns(SignalsEnvelope(model='synthetic-fixture',records=rows),provider=relation_provider)
    ids=[p.pattern_id for p in patterns.patterns if p.pattern_type!='pains' or p.evidence_refs[0].comment_id=='SYNTHETIC-0']
    insights=build_insights(patterns,provider=FakeProvider([candidate(patterns,support_pattern_ids=ids,relationship_type='pattern_relationship')]))
    reviews=prepare_review(insights); reviews=record_review(reviews,action(reviews))
    verified=apply_reviews(reviews)
    provider=ContentProvider(); original=provider.generate
    def generate(stage,payload,schema):
        result=original(stage,payload,schema)
        if stage=='angles':
            pain=next(r['evidence_id'] for r in payload['parent']['evidence_refs'] if r['signal_path'].startswith('pains.'))
            for c in result['candidates']:
                c['value_scene']=dict(current_struggle=dict(evidence_id=pain),
                    desired_future=dict(proposed=text('Imagine a more manageable future as illustrative framing.')))
        return result
    provider.generate=generate
    tree=build_content_tree(verified,reviews,project_id='SYNTHETIC-CONTRACT-FIXTURE',run_id='synthetic-packet-test',
        opportunities=1,topics=1,angles=2,provider=provider)
    assert not tree.validation_issues
    angle=tree.angles[0]; ledger=prepare_selection(tree,reviews)
    choice=SelectionAction(request_id='SYNTHETIC-SELECTION',tree_hash=artifact_hash(tree),angle_id=angle.angle_id,
        angle_hash=artifact_hash(angle),decision='selected',reviewer_id='SYNTHETIC-HUMAN-NOT-REAL',human_attested=True,
        rationale='Synthetic fixture for offline contract tests only.')
    ledger=select_angle(ledger,reviews,choice)
    return dict(verified=verified,tree=tree,selected=apply_selection(ledger,reviews),reviews=reviews,ledger=ledger)


def synthetic_packet(state=None):
    state=state or synthetic_state()
    return build_packet(**state,angle_id=state['selected'].selected_angles[0].angle_id,
                        created_at=datetime(2026,9,15,0,0,tzinfo=timezone.utc))
