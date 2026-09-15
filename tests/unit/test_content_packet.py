"""Offline portable-contract tests with clearly synthetic human decisions."""
import json
from pathlib import Path
import jsonschema
import pytest
from tests.fixtures.content_packet_fixture import synthetic_packet, synthetic_state
from tests.unit.test_governance import action
from tiktok_insight_miner.content_packet_builder import build_packet, packet_identity
from tiktok_insight_miner.content_packet_models import ContentIntelligencePacket
from tiktok_insight_miner.content_packet_store import load_packet, save_packet, packet_preview
from tiktok_insight_miner.content_packet_validator import validate_current, validate_revision
from tiktok_insight_miner.content_selection import SelectionAction, apply_selection, select_angle
from tiktok_insight_miner.governance_engine import record_review
from tiktok_insight_miner.governance_store import atomic_json
from tiktok_insight_miner.pattern_models import artifact_hash

ROOT=Path(__file__).resolve().parents[2]


@pytest.fixture
def state(): return synthetic_state()


def test_portable_zones_exact_customer_truth(state):
    packet=synthetic_packet(state)
    assert validate_current(packet,**state)==packet
    assert packet.customer_truth.verified_insight==state['verified'].verified_insights[0]
    assert packet.content_strategy.angle.truth_type=='PROPOSED'
    assert packet.creative_execution.status=='not_generated'
    assert packet.customer_truth.verified_insight.contradictions
    assert packet.customer_truth.verified_insight.limitations==state['verified'].verified_insights[0].limitations
    assert packet.customer_truth.language_bank.emotional_wording and packet.customer_truth.source_snapshots
    assert packet.external_evidence_requirements
    assert all(r.status=='required_before_publish' for r in packet.external_evidence_requirements)
    scene=packet.content_strategy.value_scene
    assert scene.current_struggle.kind=='source_wording' and scene.desired_future.kind=='proposed_framing'
    assert scene.desired_future.framing.truth_type=='PROPOSED'
    assert ContentIntelligencePacket.model_validate_json(packet.model_dump_json())==packet
    assert 'ZONE A' in packet_preview(packet) and 'External evidence still required' in packet_preview(packet)


@pytest.mark.parametrize('change', ['machine','unselected','rejected','deferred','stale_review','stale_selection','stale_tree','mismatch_verified'])
def test_current_gates(change,state):
    from tests.unit.test_governance import sample
    packet=synthetic_packet(state); changed=dict(state)
    if change=='machine': changed['verified']=sample()
    if change=='unselected':
        with pytest.raises(ValueError): build_packet(**state,angle_id=state['tree'].angles[1].angle_id)
        return
    if change in ('rejected','deferred','stale_selection'):
        a=state['ledger'].events[0].action.model_copy(update=dict(request_id='later',decision='rejected' if change=='stale_selection' else change))
        changed['ledger']=select_angle(state['ledger'],state['reviews'],a)
        if change!='stale_selection': changed['selected']=apply_selection(changed['ledger'],state['reviews'])
    if change=='stale_review': changed['reviews']=record_review(state['reviews'],action(state['reviews'],'rejected',request_id='revoke'))
    if change=='mismatch_verified': changed['verified']=synthetic_state()['verified']
    if change=='stale_tree':
        from tiktok_insight_miner.content_route_engine import extend_content_tree
        from tests.unit.test_content_route import ContentProvider
        changed['tree']=extend_content_tree(state['tree'],state['reviews'],stage='angles',parent_id=state['tree'].topics[0].topic_id,provider=ContentProvider())
    with pytest.raises(ValueError): validate_current(packet,**changed)


@pytest.mark.parametrize('change', ['truth','quote','source_ref','language','hook','contradiction','limitations',
    'market','purchase','angle_truth','governance_hash','selection_hash','angle_lineage','external','scene',
    'product','writer_permissions','revision','source_text'])
def test_tampered_packet_rejected(change,state):
    packet=synthetic_packet(state); data=packet.model_dump(mode='json'); vi=data['customer_truth']['verified_insight']
    if change=='truth': vi['statement']['text']='Invented customer truth'
    if change=='quote': vi['evidence_refs'][0]['evidence_quote']='Invented quote'
    if change=='source_ref': vi['evidence_refs'][0]['source_hash']='fake'
    if change=='language': data['customer_truth']['language_bank']['emotional_wording'][0]['evidence_quote']='invented phrase'
    if change=='hook': data['customer_truth']['language_bank']['exact_phrases']=[{'text':'generated hook'}]
    if change=='contradiction': vi['contradictions']=[]
    if change=='limitations': vi['limitations']=[]
    if change=='market': vi['verification']['market_validated']=True
    if change=='purchase': vi['verification']['purchase_validated']=True
    if change=='angle_truth': data['content_strategy']['angle']['truth_type']='OBSERVED'
    if change=='governance_hash': data['lineage']['governance_hash']='wrong'
    if change=='selection_hash': data['lineage']['selection_hash']='wrong'
    if change=='angle_lineage': data['selection']['verified_insight_id']='other'
    if change=='external': data['external_evidence_requirements']=[]
    if change=='scene': data['content_strategy']['value_scene']['desired_future']=data['content_strategy']['value_scene']['current_struggle']
    if change=='product': data['product_opportunity']={'truth_type':'PROPOSED'}
    if change=='writer_permissions': data['creative_execution']['constraints']['do_not_change_customer_truth']=False
    if change=='revision': data['packet_revision']=2
    if change=='source_text': data['customer_truth']['source_snapshots'][0]['text']='changed'
    with pytest.raises(ValueError): ContentIntelligencePacket.model_validate(data)
    data['packet_id']=packet_identity(data)
    with pytest.raises(ValueError):
        candidate=ContentIntelligencePacket.model_validate(data)
        validate_current(candidate,**state)


def test_revision_immutable_and_idempotent(state,tmp_path):
    old=synthetic_packet(state); original=old.model_dump_json()
    assert build_packet(**state,angle_id=old.lineage.angle_id,previous=old)==old
    revised=build_packet(**state,angle_id=old.lineage.angle_id,project_goal='BOTH',previous=old)
    assert revised.packet_revision==2 and revised.packet_id!=old.packet_id
    assert validate_revision(revised,old)==revised and old.model_dump_json()==original
    p=tmp_path/'old.json'; save_packet(old,p,**state); before=p.read_bytes()
    assert save_packet(old,p,**state)==old
    with pytest.raises(ValueError): save_packet(revised,p,**state)
    assert p.read_bytes()==before
    save_packet(revised,tmp_path/'revision2.json',**state)


def test_changed_selected_angle_requires_new_packet(state):
    old=synthetic_packet(state); angle=state['tree'].angles[1]
    a=SelectionAction(request_id='synthetic-second',tree_hash=artifact_hash(state['tree']),angle_id=angle.angle_id,
        angle_hash=artifact_hash(angle),decision='selected',reviewer_id='synthetic-human',human_attested=True)
    ledger=select_angle(state['ledger'],state['reviews'],a)
    new_state={**state,'ledger':ledger,'selected':apply_selection(ledger,state['reviews'])}
    new=build_packet(**new_state,angle_id=angle.angle_id,previous=old)
    assert new.packet_id!=old.packet_id and new.packet_revision==2
    with pytest.raises(ValueError): validate_current(old,**new_state)
    assert ContentIntelligencePacket.model_validate_json(old.model_dump_json())==old


def test_json_schema_and_committed_synthetic_fixture():
    schema=json.loads((ROOT/'contracts/content-intelligence-packet.schema.json').read_text(encoding='utf-8'))
    assert schema==ContentIntelligencePacket.model_json_schema()
    fixture=json.loads((ROOT/'contracts/fixtures/synthetic-content-intelligence-packet.json').read_text(encoding='utf-8'))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(fixture)
    assert load_packet(ROOT/'contracts/fixtures/synthetic-content-intelligence-packet.json').project.project_id=='SYNTHETIC-CONTRACT-FIXTURE'
    for bad in [{**fixture,'schema_version':'wrong'},{k:v for k,v in fixture.items() if k!='schema_version'},
                {k:v for k,v in fixture.items() if k!='customer_truth'},{**fixture,'product_opportunity':{}}]:
        with pytest.raises(jsonschema.ValidationError): jsonschema.validate(bad,schema)


def test_cli_build_validate(state,tmp_path,monkeypatch,capsys):
    from tiktok_insight_miner.cli import main
    paths={}
    for key,value in state.items():
        p=tmp_path/(key+'.json'); atomic_json(p,value); paths[key]=p
    output=tmp_path/'packet.json'; flags=[]
    for flag,key in [('verified-insights','verified'),('content-tree','tree'),('selection','selected'),('reviews','reviews'),('selection-ledger','ledger')]:
        flags.extend(['--'+flag,str(paths[key])])
    def run(args): monkeypatch.setattr('sys.argv',['tim',*args]); main()
    run(['build-content-packet',*flags,'--angle-id',state['tree'].angles[0].angle_id,'-o',str(output)])
    run(['validate-content-packet',str(output),*flags])
    assert 'PASS' in capsys.readouterr().out
    run(['validate-content-packet',str(output)])
    assert 'NOT_CHECKED_OFFLINE' in capsys.readouterr().out
    with pytest.raises(SystemExit): run(['validate-content-packet',str(output),'--reviews',str(paths['reviews'])])


def test_ui_build_preview_export(state,tmp_path):
    from streamlit.testing.v1 import AppTest
    source=tmp_path/'v2-human-review/customer-intelligence'; content=tmp_path/'v2-content-route/customer-intelligence/content-research'
    for path,value in [(source/'verified_insights.json',state['verified']),(source/'insight_reviews.json',state['reviews']),
                       (content/'content_tree.json',state['tree']),(content/'content_selections.json',state['ledger']),
                       (content/'selected_content_angles.json',state['selected'])]: atomic_json(path,value)
    script=('from pathlib import Path\nfrom tiktok_insight_miner.content_packet_ui import render_packet_preview\n'
            f'render_packet_preview(Path({str(tmp_path)!r}))\n')
    app=AppTest.from_string(script,default_timeout=60).run()
    assert not app.exception and not app.error
    next(b for b in app.button if b.label=='Build Packet → Validate').click().run()
    assert not app.exception and not app.error and app.success
    files=list(tmp_path.glob('v2-content-packets/customer-intelligence/content-research/CIP-*.json'))
    assert len(files)==1 and validate_current(load_packet(files[0]),**state)
    revoked=record_review(state['reviews'],action(state['reviews'],'rejected',request_id='revoked'))
    atomic_json(source/'insight_reviews.json',revoked); app.run()
    assert app.error and not app.success
