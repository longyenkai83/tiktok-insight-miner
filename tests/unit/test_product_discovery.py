"""Explicitly synthetic human Priority Needs; never real customer decisions or live API."""
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from tests.unit.test_governance import sample, action
from tiktok_insight_miner.governance_engine import prepare_review, record_review, apply_reviews
from tiktok_insight_miner.governance_models import PriorityDecision
from tiktok_insight_miner.governance_store import atomic_json
from tiktok_insight_miner.pattern_models import artifact_hash
from tiktok_insight_miner.product_engine import (AnthropicProducts, build_discovery, checked_discovery,
    extend_discovery, new_discovery, priority_inputs)
from tiktok_insight_miner.product_models import ProductDiscovery
from tiktok_insight_miner.product_store import (ProductAction, ProductLedger, SelectedProducts,
    apply_products, decide_product, decide_product_file, export_products, load_discovery,
    load_product_ledger, prepare_product_file, prepare_products, require_products, save_discovery)


def priority_fixture(status='priority_need'):
    q = prepare_review(sample())
    q = record_review(q, action(q, priority=PriorityDecision(priority_status=status)))
    return apply_reviews(q), q


def proposed(text): return dict(text=text)


class ProductProvider:
    name = 'synthetic-product-provider'
    def generate(self, payload, schema):
        v = payload['priority_need']
        job = next(r['evidence_id'] for r in v['evidence_refs'] if r['signal_path'].startswith('jobs.'))
        pain = next(r['evidence_id'] for r in v['evidence_refs'] if r['signal_path'].startswith('pains.'))
        result = []
        for n in range(min(payload['requested_count'], 2)):
            result.append(dict(local_id=f'o{n}', verified_insight_id=v['verified_insight_id'],
                opportunity_statement=proposed(['A worksheet for comparing retained income choices.', 'A guided session for examining cost pressure.'][n]),
                opportunity_type=['worksheet', 'service'][n],
                mechanism=proposed(['Walk through an editable cost comparison independently.', 'Talk through alternatives with a human facilitator.'][n]),
                delivery_mode=['self_service', 'human_service'][n], commercial_model='undecided',
                progress=dict(struggle_ref=pain, job_ref=job, desired_progress=proposed('A clearer view of tradeoffs.')),
                value_map=dict(products_services=[dict(local_id='s', description=proposed('A structured comparison resource.'), target_refs=[job,pain])],
                    pain_relievers=[dict(local_id='pr', service_id='s', target_ref=pain, mechanism=proposed('Make the rent burden visible during comparison.'))], gain_creators=[]),
                assumptions=[dict(local_id='a', risk_category='DESIRABILITY', observable_behavior='Complete the comparison exercise',
                    offered_value='The proposed comparison resource', observation_method='Observe completion during a voluntary session')],
                experiments=[dict(local_id='e', assumption_id='a', target_evidence_level=2, experiment_type='prototype_reaction',
                    procedure='Invite a scoped participant to try a paper mockup.', measurement='Record whether the comparison is completed.',
                    success_condition='Participant completes the comparison without assistance.', failure_condition='Participant cannot complete the comparison.',
                    evidence_to_collect='Observed mockup reaction with permission.')]))
        return dict(candidates=result)


def tree_fixture():
    v, q = priority_fixture()
    return build_discovery(v,q,project_id='synthetic',run_id='test',provider=ProductProvider()), q


def choose(tree, decision='explore', **changes):
    o = tree.opportunities[0]
    data = dict(request_id='synthetic-decision', tree_hash=artifact_hash(tree), product_opportunity_id=o.product_opportunity_id,
        opportunity_hash=artifact_hash(o), decision=decision, reviewer_id='synthetic-human', human_attested=True,
        rationale='Review of a synthetic proposal only.')
    return ProductAction(**{**data, **changes})


@pytest.mark.parametrize('status', ['unassessed','monitor'])
def test_non_priority_rejected_before_generation(status):
    v,q = priority_fixture(status); provider = Mock()
    with pytest.raises(ValueError, match='human_priority_need_required'):
        build_discovery(v,q,project_id='p',run_id='r',provider=provider)
    provider.generate.assert_not_called()


def test_machine_and_bare_flag_rejected():
    q = prepare_review(sample())
    for v in (sample(), {'human_verified':True}, apply_reviews(q)):
        with pytest.raises(ValueError): priority_inputs(v,q)


def test_priority_multiple_alternatives_and_full_trace():
    tree,q = tree_fixture()
    assert len(tree.opportunities)==len(tree.value_maps)==len(tree.assumptions)==len(tree.experiment_plans)==2
    assert not tree.validation_issues
    assert ProductDiscovery.model_validate_json(tree.model_dump_json()) == tree
    for o in tree.opportunities:
        assert o.truth_type=='PROPOSED' and o.status=='proposed'
        assert o.customer_need_evidence_level==1 and o.solution_evidence_level==0
        assert not o.validation.validated_product and not o.validation.purchase_validated
        assert o.priority_need.priority.priority_status=='priority_need'
        assert o.evidence_refs==o.priority_need.evidence_refs
        assert o.contradictions==o.priority_need.contradictions and o.scope==o.priority_need.scope
        assert o.customer_progress.supported_gain is None
        assert o.customer_progress.desired_progress.truth_type=='PROPOSED'
    for m in tree.value_maps:
        assert not m.gain_creators and m.truth_type=='PROPOSED'
        assert m.pain_relievers[0].target_customer_profile_ref.signal_path.startswith('pains.')
    assert all(a.truth_type=='HYPOTHESIS' and a.evidence_strength==0 and a.importance=='unknown' and not a.riskiest_assumption for a in tree.assumptions)
    assert all(e.truth_type=='PROPOSED' and e.current_evidence_level==0 and e.status=='plan_only' for e in tree.experiment_plans)
    from tiktok_insight_miner.product_ui import why_product
    view = why_product(tree,tree.opportunities[0])
    assert view['exact_evidence'] and view['patterns_signals_sources']['input_signals']['records']


@pytest.mark.parametrize('mode,code', [
    ('unknown_insight','unknown_upstream_id'), ('invented_pain','unknown_customer_profile_ref'),
    ('pain_is_job','wrong_customer_profile_role'), ('gain_is_pain','wrong_customer_profile_role'),
    ('orphan','orphan_value_map_item'), ('empty_target','invalid_candidate_schema'),
    ('invented_quote','invalid_candidate_schema'), ('validated','invalid_candidate_schema'),
    ('purchase','unsupported_demand_or_validation'), ('statistic','unsupported_numeric_claim'),
    ('content','invalid_candidate_schema'), ('content_prose','content_contamination'),
    ('compound','compound_assumption'), ('untestable','untestable_assumption'),
    ('score','invalid_candidate_schema'), ('assumption_truth','invalid_candidate_schema'),
    ('evidence_level','invalid_candidate_schema'), ('unknown_assumption','unknown_or_unplanned_assumption'),
    ('target_level','experiment_level_mismatch'), ('unlabelled_threshold','invalid_candidate_schema'),
    ('duplicate_service','duplicate_local_id'), ('empty_services','invalid_candidate_schema'),
    ('fake_quote_prose','unsupported_quote'), ('demographic','demographic_outside_scope')])
def test_invalid_transport(mode, code):
    v,q = priority_fixture(); tree = new_discovery(v,q,project_id='p',run_id='r')
    provider = ProductProvider(); original = provider.generate
    def invalid(payload,schema):
        r = original(payload,schema); c = r['candidates'][0]; r['candidates']=[c]
        fit = c['value_map']['pain_relievers'][0]; a=c['assumptions'][0]; e=c['experiments'][0]
        if mode=='unknown_insight': c['verified_insight_id']='unknown'
        if mode=='invented_pain': c['progress']['struggle_ref']='invented'
        if mode=='pain_is_job': fit['target_ref']=c['progress']['job_ref']
        if mode=='gain_is_pain': c['value_map']['gain_creators']=[{**fit,'local_id':'gc'}]
        if mode=='orphan': fit['service_id']='unknown'
        if mode=='empty_target': c['value_map']['products_services'][0]['target_refs']=[]
        if mode=='invented_quote': c['evidence_refs']=[{'evidence_quote':'invented'}]
        if mode=='validated': c['validated_product']=True
        if mode=='purchase': c['mechanism']=proposed('Customers will pay for this solution.')
        if mode=='statistic': c['mechanism']=proposed('This serves 90% of the market.')
        if mode=='content': c['hook']='An invented hook'
        if mode=='content_prose': c['mechanism']=proposed('Write a content angle for a script.')
        if mode=='compound': a['observable_behavior']='Complete the exercise and buy the resource'
        if mode=='untestable': a['observable_behavior']='Good'
        if mode=='score': a['importance']='high'
        if mode=='assumption_truth': a['truth_type']='OBSERVED'
        if mode=='evidence_level': a['evidence_strength']=5
        if mode=='unknown_assumption': e['assumption_id']='unknown'
        if mode=='target_level': e['target_evidence_level']=5
        if mode=='unlabelled_threshold': e['threshold']=dict(metric='completion',value=2,unit='participants',operator='>=')
        if mode=='duplicate_service': c['value_map']['products_services']*=2
        if mode=='empty_services': c['value_map']['products_services']=[]
        if mode=='fake_quote_prose': c['mechanism']=proposed('A customer said "I will buy".')
        if mode=='demographic': c['mechanism']=proposed('Help teenagers compare costs.')
        return r
    provider.generate=invalid
    result=extend_discovery(tree,q,verified_insight_id=v.verified_insights[0].verified_insight_id,provider=provider)
    assert not result.opportunities
    assert [i.code for i in result.validation_issues]==[code]


def test_proposed_threshold_not_market_statistic():
    v,q=priority_fixture(); provider=ProductProvider(); original=provider.generate
    def threshold(payload,schema):
        r=original(payload,schema)
        for c in r['candidates']:
            c['experiments'][0]['threshold']=dict(label='PROPOSED_TEST_THRESHOLD',metric='completion',value=2,unit='participants',operator='>=')
        return r
    provider.generate=threshold
    tree=build_discovery(v,q,project_id='p',run_id='r',provider=provider)
    assert tree.experiment_plans[0].plan.threshold.value==2
    assert tree.opportunities[0].solution_evidence_level==0


def test_duplicate_mechanism_not_new_alternative():
    tree,q=tree_fixture()
    result=extend_discovery(tree,q,verified_insight_id=tree.opportunities[0].verified_insight_id,count=7,provider=ProductProvider())
    assert len(result.opportunities)==2
    assert [i.code for i in result.validation_issues]==['duplicate_mechanism']*2


@pytest.mark.parametrize('comment_count', [1, 8])
def test_supported_gains_and_breadth_do_not_validate_solution(comment_count):
    from tests.unit.test_insight_engine import FakeProvider, candidate
    from tiktok_insight_miner.signal_extractor import source_from_comment, validate_batch
    from tiktok_insight_miner.signal_models import SignalsEnvelope
    from tiktok_insight_miner.pattern_engine import build_patterns
    from tiktok_insight_miner.insight_engine import build_insights
    sources=[source_from_comment(dict(id=f'synthetic-{i}', text='I want stable income but rent consumes profit; I want predictable costs.')) for i in range(comment_count)]
    rows,_=validate_batch(sources,dict(results=[dict(comment_id=s.comment_id, signals=[
        dict(category=cat,subcategory=sub,evidence_quote=quote,truth_type='OBSERVED',confidence='high')
        for cat,sub,quote in [('jobs','functional','I want stable income'),('pains','costs','rent consumes profit'),
                              ('gains','desired','I want predictable costs')]]) for s in sources]))
    p=build_patterns(SignalsEnvelope(model='synthetic',records=rows))
    raw=build_insights(p,provider=FakeProvider([candidate(p,relationship_type='pattern_relationship',support_pattern_ids=[x.pattern_id for x in p.patterns])]))
    q=prepare_review(raw); q=record_review(q,action(q,priority=PriorityDecision(priority_status='priority_need'))); v=apply_reviews(q)
    provider=ProductProvider(); original=provider.generate
    def with_gain(payload,schema):
        result=original(payload,schema)
        gain=next(r['evidence_id'] for r in payload['priority_need']['evidence_refs'] if r['signal_path'].startswith('gains.'))
        for c in result['candidates']:
            c['progress']['gain_ref']=gain
            c['value_map']['products_services'][0]['target_refs'].append(gain)
            c['value_map']['gain_creators']=[dict(local_id='gc',service_id='s',target_ref=gain,mechanism=proposed('Explore cost predictability through comparison.'))]
        return result
    provider.generate=with_gain
    tree=build_discovery(v,q,project_id='p',run_id='r',provider=provider)
    assert not tree.validation_issues
    assert tree.opportunities[0].evidence_summary.comment_count==comment_count
    assert tree.opportunities[0].customer_need_evidence_level==1
    assert tree.assumptions[0].evidence_strength==tree.experiment_plans[0].current_evidence_level==0
    assert tree.value_maps[0].gain_creators[0].target_customer_profile_ref.evidence_quote=='I want predictable costs'
    assert tree.opportunities[0].customer_progress.desired_progress.truth_type=='PROPOSED'


def test_provider_truncation_rejected_and_cache_metadata_only():
    from types import SimpleNamespace
    client=Mock()
    client.messages.create.return_value=SimpleNamespace(stop_reason='max_tokens', content=[], usage=SimpleNamespace(cache_read_input_tokens=25))
    provider=AnthropicProducts(client=client)
    with pytest.raises(ValueError,match='incomplete_product_response'): provider.generate({}, {})
    with pytest.raises(ValueError,match='payload_limit'): provider.generate({'text':'x'*200001}, {})
    assert client.messages.create.call_count==1


def test_counter_evidence_survives_product_and_why_view():
    from tests.unit.test_insight_engine import FakeProvider, candidate
    from tiktok_insight_miner.signal_extractor import source_from_comment, validate_batch
    from tiktok_insight_miner.signal_models import SignalsEnvelope
    from tiktok_insight_miner.pattern_engine import build_patterns
    from tiktok_insight_miner.insight_engine import build_insights
    from tiktok_insight_miner.product_ui import why_product
    sources=[source_from_comment(dict(id=f'c{i}',text=t)) for i,t in enumerate([
        'I want stable income; rent is painful.', 'I want stable income; rent is manageable.'])]
    rows,_=validate_batch(sources,dict(results=[dict(comment_id=s.comment_id,signals=[
        dict(category='jobs',subcategory='functional',evidence_quote='I want stable income',truth_type='OBSERVED',confidence='high'),
        dict(category='pains',subcategory='costs',evidence_quote=s.text.split('; ')[1],truth_type='OBSERVED',confidence='high')]) for s in sources]))
    provider=Mock(); provider.name='synthetic-counter-evidence'
    def compare(catalog):
        pains=[c for c in catalog if c['signal_path'].startswith('pains.')]
        return dict(relations=[dict(left=pains[0]['evidence_id'],right=pains[1]['evidence_id'],kind='contradiction')])
    provider.compare.side_effect=compare
    p=build_patterns(SignalsEnvelope(model='synthetic',records=rows),provider=provider)
    ids=[x.pattern_id for x in p.patterns if x.pattern_type=='jobs' or (x.pattern_type=='pains' and x.evidence_refs[0].comment_id=='c0')]
    raw=build_insights(p,provider=FakeProvider([candidate(p,support_pattern_ids=ids)]))
    q=prepare_review(raw); q=record_review(q,action(q,priority=PriorityDecision(priority_status='priority_need'))); v=apply_reviews(q)
    tree=build_discovery(v,q,project_id='p',run_id='r',provider=ProductProvider())
    assert tree.opportunities[0].contradictions
    assert tree.opportunities[0].contradictions==v.verified_insights[0].contradictions
    assert why_product(tree,tree.opportunities[0])['priority_need']['contradictions']


def test_atomic_interruption_preserves_existing_product_tree(tmp_path, monkeypatch):
    tree,q=tree_fixture(); p=tmp_path/'tree.json'; save_discovery(tree,p,q); before=p.read_bytes()
    monkeypatch.setattr('tiktok_insight_miner.governance_store.os.replace', Mock(side_effect=OSError('interrupted')))
    with pytest.raises(OSError): save_discovery(tree,p,q,expected_hash=artifact_hash(tree))
    assert p.read_bytes()==before
    assert not list(tmp_path.glob('.review-*.tmp'))


@pytest.mark.parametrize('field', ['evidence','truth','level','source','gain','priority','counts'])
def test_persisted_tampering_rejected(field):
    tree,q=tree_fixture(); data=tree.model_dump(mode='json'); o=data['opportunities'][0]
    if field=='evidence': o['evidence_refs'][0]['source_hash']='fake'
    if field=='truth': o['truth_type']='OBSERVED'
    if field=='level': o['customer_need_evidence_level']=5
    if field=='source': o['customer_progress']['job']['evidence_quote']='invented'
    if field=='gain': o['customer_progress']['supported_gain']=o['customer_progress']['current_struggle']
    if field=='priority': o['priority_need']['priority']['priority_status']='unassessed'
    if field=='counts': o['evidence_summary']['comment_count']=999
    with pytest.raises(ValidationError): ProductDiscovery.model_validate(data)


@pytest.mark.parametrize('decision,count',[('explore',1),('reject',0),('defer',0)])
def test_explicit_human_product_decisions(decision,count):
    tree,q=tree_fixture(); ledger=prepare_products(tree,q)
    assert not apply_products(ledger,tree,q).selected_opportunities
    a=choose(tree,decision); new=decide_product(ledger,tree,q,a)
    assert decide_product(new,tree,q,a)==new
    output=apply_products(new,tree,q)
    assert len(require_products(output,new,tree,q))==count
    assert SelectedProducts.model_validate_json(output.model_dump_json())==output


def test_human_can_choose_first_assumption_without_changing_original():
    tree,q=tree_fixture(); before=tree.model_dump_json(); ledger=prepare_products(tree,q)
    a=choose(tree,assumption_to_test_first=tree.assumptions[0].assumption_id,assumption_importance='high',riskiest_assumption=True)
    new=decide_product(ledger,tree,q,a)
    assert apply_products(new,tree,q).selected_opportunities[0].assumption_importance=='high'
    assert apply_products(new,tree,q).selected_opportunities[0].riskiest_assumption
    assert not tree.assumptions[0].riskiest_assumption
    with pytest.raises(ValidationError): choose(tree,riskiest_assumption=True)
    assert tree.model_dump_json()==before and tree.assumptions[0].importance=='unknown'
    with pytest.raises(ValueError): decide_product(ledger,tree,q,choose(tree,assumption_to_test_first=tree.assumptions[1].assumption_id))
    with pytest.raises(ValidationError): choose(tree,human_attested=False)


def test_history_revocation_and_new_tree_stale():
    tree,q=tree_fixture(); ledger=decide_product(prepare_products(tree,q),tree,q,choose(tree))
    output=apply_products(ledger,tree,q)
    revoked=decide_product(ledger,tree,q,choose(tree,'reject',request_id='later'))
    assert revoked.events[:1]==ledger.events and not apply_products(revoked,tree,q).selected_opportunities
    with pytest.raises(ValueError): require_products(output,revoked,tree,q)
    updated=extend_discovery(tree,q,verified_insight_id=tree.opportunities[0].verified_insight_id,provider=ProductProvider())
    with pytest.raises(ValueError): apply_products(ledger,updated,q)
    latest=prepare_products(updated,q,ledger)
    assert latest.events==ledger.events and not apply_products(latest,updated,q).selected_opportunities
    bad=latest.model_dump(mode='json'); bad['events'][0]['action']['reviewer_id']='forged'
    with pytest.raises(ValidationError): ProductLedger.model_validate(bad)


def test_upstream_priority_revoked_blocks_all_boundaries():
    tree,q=tree_fixture(); ledger=prepare_products(tree,q)
    q2=record_review(q,action(q,request_id='remove-priority'))
    for call in [lambda:checked_discovery(tree,q2), lambda:decide_product(ledger,tree,q2,choose(tree)), lambda:apply_products(ledger,tree,q2)]:
        with pytest.raises(ValueError): call()


def test_atomic_storage_stale_writer_and_export(tmp_path):
    tree,q=tree_fixture(); tp=tmp_path/'tree.json'; dp=tmp_path/'decisions.json'; op=tmp_path/'selected.json'
    save_discovery(tree,tp,q); assert load_discovery(tp)==tree
    with pytest.raises(ValueError): save_discovery(tree,tp,q)
    ledger=prepare_product_file(tree,q,dp)
    new=decide_product_file(dp,tree,q,choose(tree),expected_history_hash=artifact_hash(ledger))
    assert load_product_ledger(dp)==new
    with pytest.raises(ValueError): decide_product_file(dp,tree,q,choose(tree,request_id='late'),expected_history_hash=artifact_hash(ledger))
    result=export_products(dp,op,tree,q)
    assert len(result.selected_opportunities)==1
    assert SelectedProducts.model_validate_json(op.read_text(encoding='utf-8'))==result


def test_provider_error_is_private_and_no_auto_choice():
    v,q=priority_fixture(); provider=Mock(); provider.name='synthetic'
    provider.generate.side_effect=RuntimeError('secret-private-exception')
    tree=build_discovery(v,q,project_id='p',run_id='r',provider=provider)
    assert tree.validation_issues[0].code=='generation_error'
    assert not tree.opportunities and 'secret-private-exception' not in tree.model_dump_json()


def test_cli_workflow(tmp_path,monkeypatch):
    from tiktok_insight_miner.cli import main
    v,q=priority_fixture(); vp,qp,tp,dp,op=[tmp_path/n for n in ['verified.json','reviews.json','tree.json','decisions.json','selected.json']]
    atomic_json(vp,v); atomic_json(qp,q)
    monkeypatch.setattr(AnthropicProducts,'generate',ProductProvider.generate)
    def run(args): monkeypatch.setattr('sys.argv',['tim',*args]); main()
    run(['build-product-opportunities','--verified-insights',str(vp),'--reviews',str(qp),'--project-id','p','--run-id','r','-o',str(tp)])
    base=['--tree',str(tp),'--reviews',str(qp),'--decisions',str(dp)]
    run(['prepare-product-selection',*base]); tree=load_discovery(tp); a=choose(tree)
    run(['select-product-opportunity',*base,'--tree-hash',a.tree_hash,'--opportunity-id',a.product_opportunity_id,
        '--opportunity-hash',a.opportunity_hash,'--request-id','cli','--reviewer','synthetic-human','--confirm-human',
        '--decision','explore','--rationale','Synthetic review'])
    run(['export-product-selection',*base,'-o',str(op)])
    assert len(SelectedProducts.model_validate_json(op.read_text(encoding='utf-8')).selected_opportunities)==1


def test_ui_generation_and_human_test_decision(tmp_path):
    from streamlit.testing.v1 import AppTest
    from tiktok_insight_miner.governance_ui import review_workspace
    v,q=priority_fixture(); source=review_workspace(tmp_path,'customer-intelligence')
    atomic_json(source/'insight_reviews.json',q); atomic_json(source/'verified_insights.json',v)
    script=('from pathlib import Path\nfrom tests.unit.test_product_discovery import ProductProvider\n'
        'from tiktok_insight_miner.product_ui import render_product_discovery\n'
        f'render_product_discovery(Path({str(tmp_path)!r}), "synthetic-human", provider=ProductProvider())\n')
    app=AppTest.from_string(script,default_timeout=60).run()
    def label(items,s): return next(i for i in items if i.label==s)
    assert not app.exception and not app.error
    label(app.button,'Tạo phương án sản phẩm').click().run()
    assert not app.exception and not app.error
    dp=tmp_path/'v2-product-discovery/customer-intelligence/product-research/product_decisions.json'
    assert not load_product_ledger(dp).events
    label(app.selectbox,'Quyết định thử nghiệm').select('explore')
    label(app.text_area,'Lý do quyết định').input('Synthetic product test decision.')
    label(app.checkbox,'Tôi đã xem bằng chứng và đưa ra quyết định thử nghiệm này.').check()
    label(app.button,'Lưu quyết định sản phẩm').click().run()
    assert not app.exception and not app.error
    assert len(load_product_ledger(dp).events)==1
    app=AppTest.from_string(script,default_timeout=60).run()
    assert not app.exception and not app.error
    assert len(load_product_ledger(dp).events)==1
