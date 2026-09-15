"""Explicit opt-in live-host test. Synthetic current ledgers; creative agents are controlled stubs.

Run directly with --reelo-workspace and --executable. Not part of offline pytest.
Copies only implementation code into a fresh LOCALAPPDATA test workspace. No private assets.
"""
import argparse
import json
import os
import shutil
from pathlib import Path
from uuid import uuid4

from tests.fixtures.content_packet_fixture import synthetic_state, synthetic_packet
from tiktok_insight_miner.reelo_dispatch import send_packet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reelo-workspace', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    args = parser.parse_args()
    root = Path(os.environ['LOCALAPPDATA'])/'Reelo-Phase9-E2E'/uuid4().hex
    workspace = root/'workspace'
    workspace.mkdir(parents=True)
    shutil.copytree(args.reelo_workspace/'integrations', workspace/'integrations',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    workflow = workspace/'.claude/workflows/batch-content.js'
    workflow.parent.mkdir(parents=True)
    state = synthetic_state()
    packet = synthetic_packet(state)
    raw = packet.model_dump(mode='json')
    ref = packet.customer_truth.verified_insight.evidence_refs[0]
    draft = dict(status='DRAFT', title='SYNTHETIC Phase 9 draft — not customer content', format='Reel',
        content='SYNTHETIC TEST ONLY — NOT APPROVED — DO NOT PUBLISH\n\n'
                'Exact fixture wording: '+ref.evidence_quote+'\n\n'
                'This controlled draft tests transport and revision provenance, not creative quality. '
                'The fixture includes contrasting experiences; no purchase or market validation is claimed.',
        issues=[], customer_evidence_ids=[ref.evidence_id],
        external_dispositions=[dict(strategy_field=r.strategy_field, disposition='omitted',
                                    explanation='Synthetic framing is not established external evidence.')
                               for r in packet.external_evidence_requirements])
    passed = dict(plan_fidelity=True, title_meaning_clear=True, reader_centered_pov=True, non_prescriptive_tone=True, findings=[], verdict='PASS', truth_preserved=True, selected_intent_preserved=True,
                  limitations_preserved=True, external_claims_safe=True, title_criteria=[True]*8, blocking_issues=[], notes=[],
                  creator_truth_preserved=True, context_scope_preserved=True, source_verification_complete=True)
    failed = dict(passed, verdict='REVISE', blocking_issues=['synthetic_first_review_requires_revision'])
    library = workspace/'nguyen-ly-tam-ly.md'
    library.write_text('Synthetic mechanism', encoding='utf8')
    def candidate(cid, text):
        return dict(candidate_id=cid, text=text, rationale='Synthetic test only', evidence_refs=[ref.evidence_id],
                    intent_preserved=True, factual_claims_supported=True, natural_and_meaningful=True)
    plan = dict(packet_id=raw['packet_id'], verified_insight_id=raw['customer_truth']['verified_insight']['verified_insight_id'],
        angle_id=raw['content_strategy']['angle']['angle_id'], truth_type='PROPOSED', story_matches=[], knowledge_matches=[],
        illustrations=[], psychology=dict(primary_mechanism='Synthetic mechanism', optional_secondary_mechanism=None,
        library_source=library.as_posix(), rationale='Synthetic only'), format='Reel', treatment_or_truc='Neutral',
        hook_candidates=[candidate('h1','SYNTHETIC'),candidate('h2','SYNTHETIC alternative')],
        title_candidates=[candidate('t1',draft['title']),candidate('t2','SYNTHETIC alternative')],
        recommended_hook_id='h1',recommended_title_id='t1',outline=['Synthetic only'],cta_direction='None',
        creative_constraints=['No publication'],truth_preserved=True,selected_intent_preserved=True,
        reader_centered_pov=True,non_prescriptive_tone=True,issues=[])
    # Test dependency injection in the copy ONLY. Production code has no synthetic bypass.
    stub = 'const fixtureResponses='+json.dumps(dict(CREATIVE_PLAN=plan, WRITER=draft, CRITIC1=failed, REWRITE=draft, CRITIC2=passed))+';\n'
    stub += 'const agent=async(prompt,options)=>{if(!prompt.includes("IMMUTABLE PACKET"))throw new Error("missing_context"); return fixtureResponses[V2_BOUND.stage.stage_type];};\n'
    template = (args.reelo_workspace/'.claude/workflows/batch-content.js').read_text(encoding='utf-8')
    workflow.write_bytes(template.replace('/* V2_BOUND_CONTEXT */', '/* V2_BOUND_CONTEXT */\n'+stub).encode('utf-8'))
    config = dict(execution_workspace=str(workspace), executable=str(args.executable),
                  state_directory=str(root/'state'), read_files=[str(library)])
    (root/'operator-config.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    (root/'packet.json').write_text(packet.model_dump_json(indent=2), encoding='utf-8')
    for name, artifact in state.items():
        (root/(name+'.json')).write_text(artifact.model_dump_json(indent=2), encoding='utf-8')
    # Re-read all current artifacts for every authorization, as CLI/UI do.
    def load_current():
        return {name: type(artifact).model_validate_json((root/(name+'.json')).read_text(encoding='utf-8'))
                for name, artifact in state.items()}
    planned = send_packet(packet, load_current=load_current, config=config, request_id='synthetic-live-plan')
    assert planned.status == 'PLAN_PENDING_APPROVAL'
    from tiktok_insight_miner.reelo_dispatch import consumer_modules
    import importlib
    adapter, _ = consumer_modules(workspace)
    plan_store = importlib.import_module(adapter.__package__+'.creative_plan').PlanStore(root/'state/creative-plans.sqlite')
    saved = planned.host['creative_plan']
    approval = plan_store.review(saved['creative_plan_id'], dict(decision='approved',reviewer='SYNTHETIC TEST fixture',
        human_attested=True,approval_kind='synthetic_fixture',expected_plan_hash=saved['plan_hash']))
    result = send_packet(packet, load_current=load_current, config=config, request_id='synthetic-live-e2e',
        parent_id=planned.generation_id, approval_id=approval['approval_id'])
    assert result.status == 'DRAFT_READY', result.status
    assert result.critic_status == 'PASS' and result.human_approval == 'PENDING'
    assert result.receipt.packet_id == packet.packet_id and result.receipt.packet_hash == packet.packet_id[4:]
    assert len(result.artifacts) == 2 and result.artifacts[1]['parent_version'] == 1
    assert packet.model_dump(mode='json') == raw
    duplicate = send_packet(packet, load_current=load_current, config=config, request_id='synthetic-live-e2e', parent_id=planned.generation_id, approval_id=approval['approval_id'])
    assert duplicate == result
    report = dict(status='PASS', synthetic=True, creative_agents='controlled_stubs_inside_real_native_workflow',
                  customer_approvals='synthetic_fixture_only', real_customer_acceptance='NOT_RUN',
                  result=result.model_dump(mode='json'), root=str(root))
    (root/'e2e-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(status='PASS', root=str(root), generation_id=result.generation_id,
                          packet_id=packet.packet_id, task_ids=[s['host']['task_id'] for s in result.host['stages']])))


if __name__ == '__main__':
    main()
