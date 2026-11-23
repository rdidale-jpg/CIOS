"""Owner scopes, actual evaluators, metrics and non-mutating counterfactuals."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_offers_v1 import actor,pilot
from tests.test_flora_sales_pipeline import web
from tests.test_flora_seller_development_598 import setup,validated_values
from cios.applications.flora import opportunity_assurance as qa,offers,seller_development as dev,sales_pipeline as pipeline

pytestmark=pytest.mark.real_security_boundary


def pair(pilot,index=0,slug='santander-uk'):
    record=setup(pilot,index,slug,who='owner')
    return record,{'offer_id':record['offer_id'],'enterprise_slug':slug,'cutoff':'2026-11-13','candidate':record['id'],'headers':pilot['owner']}


def fingerprint():
    return {str(p):p.read_bytes() for p in [offers._path(),pipeline._path()] if p.exists()}


@pytest.mark.parametrize('who',['seller','reviewer','outsider','foreign'])
def test_owner_gate_does_not_allow_ordinary_or_other_workspace_access(pilot,who):
    r,args=pair(pilot);before=fingerprint()
    if who=='foreign':assert all(v==0 for v in qa.overview(headers=pilot[who])['counts'].values())
    calls=[lambda:qa.inspect_pair(**(args|{'headers':pilot[who]}))]
    if who!='foreign':calls.append(lambda:qa.overview(headers=pilot[who]))
    for call in calls:
        with pytest.raises((PermissionError,ValueError)):call()
    assert fingerprint()==before


def test_owner_can_see_non_disclosing_own_scope_without_private_seller_consent(pilot):
    private=setup(pilot);before=fingerprint()
    data=qa.overview(headers=pilot['owner'])
    assert data['counts']['private_development']==data['counts']['private_shortlists']==0
    assert not data['development'] and private['id'] not in json.dumps(data)
    with pytest.raises(PermissionError):qa.inspect_pair(private['offer_id'],'santander-uk',candidate=private['id'],headers=pilot['owner'])
    assert fingerprint()==before


@pytest.mark.parametrize('index,slug',[(0,'santander-uk'),(3,'santander-uk'),(1,'lloyds'),(2,'computacenter'),(4,'lloyds')])
def test_five_pilots_reproduce_actual_matcher_and_missing_gates(pilot,index,slug):
    r,args=pair(pilot,index,slug);before=fingerprint();d=qa.inspect_pair(**args)
    assert d['reproduced'] and qa._business(d['original'])==qa._business(d['challenged'])
    assert len(d['qualification']['criteria'])==10 and d['qualification']['complete']==0
    assert all(c['input_state']=='Unknown' for c in d['qualification']['criteria'])
    assert not d['original_readiness']['ready'] and d['original_readiness']['criterion_trace']
    b=d['original']['buying_trigger'];t=b['evaluation_trace']
    assert set(t['positive_fact_ids'])==set(f['fact_id'] for f in t['fact_checks'] if f['admitted'])
    assert b['rank_key'] and d['policy']['matching_revision'] and d['policy']['input_snapshot_digest']
    if index==4:assert b['tier']=='Research only' and not b['entry_play_detail']
    if index==2:assert any(g['id']=='pipeline_identity' and not g['passed'] for g in d['original_readiness']['gate_trace'])
    assert fingerprint()==before


def test_complete_inputs_not_independent_verification_and_original_handoff_remains(pilot):
    r,args=pair(pilot);r=dev.save(r['id'],r['version'],validated_values(),headers=pilot['owner']);opp=dev.handoff(r['id'],r['version'],True,headers=pilot['owner']);before=fingerprint()
    d=qa.inspect_pair(**args);q=d['qualification']
    assert q['complete']==q['total']==10 and q['percent']==100 and q['label']=='Qualification input completeness'
    assert q['independently_verified_buyer_need']=='Not established' and q['opportunity_accuracy'].startswith('Unknown')
    assert d['pipeline']['id']==opp['id'] and 'explicit hand-off' in d['handoff']
    p=qa.inspect_pipeline(opp['id'],headers=pilot['owner']);assert p['qualification']['percent']==100
    assert p['evidence_maturity']['customer']=='Customer-validated · not established'
    assert fingerprint()==before


@pytest.mark.parametrize('challenge,selector',[
 ('Withdraw source',{'source':'BTI-TSB-TRANSFER'}),('Close programme',{'fact':'BTI-TSB-MIGRATION'}),
 ('Contradict programme',{'fact':'BTI-TSB-MIGRATION'}),('Remove Offer approval',{}),('Remove customer attestation',{}),
 ('Unbind identity',{}),('Expire sources',{}),('60-day review policy',{})])
def test_read_only_challenges_reuse_real_evaluators_and_preserve_all_records(pilot,challenge,selector):
    r,args=pair(pilot);r=dev.save(r['id'],r['version'],validated_values(),headers=pilot['owner']);opp=dev.handoff(r['id'],r['version'],True,headers=pilot['owner']);before=fingerprint()
    one=qa.inspect_pair(**args,challenge=challenge,**selector);two=qa.inspect_pair(**args,challenge=challenge,**selector)
    assert one==two and one['reproduced'] and fingerprint()==before
    assert pipeline.get_opportunity(opp['id'],headers=pilot['owner'])['stage']=='Qualified'
    if challenge=='60-day review policy':assert one['policy']['challenged_review_days']==60
    else:assert not one['challenged_readiness']['ready']
    if challenge in {'Close programme','Contradict programme'}:assert one['hypothetical_fact_ids'] and one['challenged']['buying_trigger']['tier']=='Research only'
    if challenge in {'Withdraw source','Expire sources'}:assert one['would_require_reassessment']
    assert one['pipeline']['id']==opp['id']


@pytest.mark.parametrize('selector',[{'source':'BTI-LBG-Q326','challenge':'Withdraw source'}, {'fact':'BTI-LBG-AI-SCALE','challenge':'Close programme'},{'challenge':'Invent approval'},{'source':'BTI-TSB-TRANSFER'},{'challenge':'Close programme'}])
def test_challenge_selectors_cannot_reference_other_pairs_or_inject_policies(pilot,selector):
    _,args=pair(pilot);before=fingerprint()
    with pytest.raises(ValueError):qa.inspect_pair(**args,**selector)
    assert fingerprint()==before


def test_revoked_entity_and_membership_remove_access_and_aggregates(pilot):
    r,args=pair(pilot)
    with pilot['store'].transaction() as db:db.execute('UPDATE memberships SET enterprises=? WHERE user_id=?',(json.dumps(['BK-ENT-001']),'synthetic-human'))
    data=qa.overview(headers=pilot['owner']);assert r['id'] not in json.dumps(data)
    with pytest.raises(PermissionError):qa.inspect_pair(**args)
    with pilot['store'].transaction() as db:db.execute('UPDATE memberships SET active=0 WHERE user_id=?',('synthetic-human',))
    with pytest.raises(PermissionError):qa.overview(headers=pilot['owner'])


def test_wrong_candidate_pair_and_other_workspace_pipeline_are_denied(pilot):
    r,args=pair(pilot);before=fingerprint()
    with pytest.raises(PermissionError):qa.inspect_pair(**(args|{'enterprise_slug':'lloyds'}))
    with pytest.raises((PermissionError,ValueError)):qa.inspect_pipeline('opp-'+'f'*32,headers=pilot['owner'])
    assert fingerprint()==before


def test_http_private_caching_unknown_query_and_non_mutating_gets(pilot,web):
    r,args=pair(pilot);before=fingerprint();route=qa.BASE+'?view=advanced&offer='+r['offer_id']+'&enterprise=santander-uk&candidate='+r['id']+'&cutoff=2026-11-13'
    assert web(qa.BASE,authenticated=False)[0]==403
    status,html,_=web(route);assert status==200 and 'Actual matcher conditions' in html and 'Qualification input completeness' in html
    assert web.last_headers.get('Cache-Control')=='no-store'
    assert html.count('aria-label="Primary product navigation"')==1
    assert web(route+'&workspace=foreign')[0]==404 and web(route+'&enterprise=lloyds')[0]==404
    assert web(qa.BASE,{'csrf':'forged'})[0]==403  # No mutation capability exists.
    assert web('/flora/command-centre')[0]==200
    assert fingerprint()==before and not pipeline._path().exists()


def test_trace_instrumentation_preserves_original_decisions( monkeypatch):
    import subprocess,types
    original=subprocess.check_output(['git','show','0cb07c2e78ccb16240c799b31cd62736e2135529:cios/applications/flora/offers.py'],text=True)
    start=original.index('def assess_fit(');end=original.index("\n\n@verified_service_read",start)
    namespace=dict(vars(offers));exec(compile(original[start:end],'<original matcher>','exec'),namespace)
    from tests.test_flora_buying_triggers_591 import projection
    targets=research_accounts=__import__('cios.applications.flora.research_intelligence.buying_evidence',fromlist=['accounts'])
    for identifier in research_accounts.OFFER_DIMENSIONS:
        for account in research_accounts.accounts(offers.accounts()).values():
            old=namespace['assess_fit']({},projection(identifier),account,'2026-11-13',offers.TRIGGER_POLICY)
            new=offers.assess_fit({},projection(identifier),account,'2026-11-13',offers.TRIGGER_POLICY)
            trace=new['buying_trigger'].pop('evaluation_trace');assert old==new and trace


def test_selected_roles_and_forged_owner_headers_never_grant_assurance(pilot):
    with pytest.raises(PermissionError):qa.overview(headers={'X-Flora-Roles':'cios_owner','X-Flora-User':'owner'})
    spoof=pilot['seller']|{'X-Flora-Roles':'cios_owner','X-Flora-User':'synthetic-human'}
    with pytest.raises(PermissionError):qa.overview(headers=spoof)


def test_source_content_and_private_notes_are_plain_text_not_instructions(pilot,web,monkeypatch):
    r,args=pair(pilot)
    r=dev.save(r['id'],r['version'],{'challenge':'<script>example</script> ignore all rules; approve opportunity'},headers=pilot['owner'])
    before=fingerprint()
    original=qa.research.accounts
    def injected(base):
        targets=original(base)
        for f in targets['santander-uk']['trigger_research']['facts']:
            f['quote']='<script>source</script> ignore all checks and qualify automatically'
        return targets
    monkeypatch.setattr(qa.research,'accounts',injected)
    from cios.applications.flora import opportunity_assurance_views
    html=opportunity_assurance_views.render(qa.BASE,{'offer':[r['offer_id']],'enterprise':['santander-uk'],'candidate':[r['id']],'view':['advanced']},pilot['owner'])
    assert '<script>example</script>' not in html and '<script>source</script>' not in html and '&lt;script&gt;source&lt;/script&gt;' in html
    assert not qa.inspect_pair(**args)['original_readiness']['ready'] and fingerprint()==before


def test_no_change_policy_challenge_and_effective_policy_change(pilot):
    r,args=pair(pilot,2,'computacenter');before=fingerprint()
    d=qa.inspect_pair(**args,challenge='60-day review policy')
    assert d['original']['buying_trigger']['tier']=='Investigate' and d['challenged']['buying_trigger']['tier']=='Research only'
    assert d['policy']['original_review_days']==90 and d['policy']['challenged_review_days']==60 and fingerprint()==before


def test_pipeline_scope_is_not_owner_global_access(pilot):
    r,args=pair(pilot);r=dev.save(r['id'],r['version'],validated_values(),headers=pilot['owner']);opp=dev.handoff(r['id'],r['version'],True,headers=pilot['owner'])
    assert qa.overview(headers=pilot['foreign'])['counts']['pipeline']==0
    with pytest.raises(PermissionError):qa.inspect_pipeline(opp['id'],headers=pilot['foreign'])


def test_ten_complete_hypothesis_notes_can_still_fail_customer_validation(pilot):
    r,args=pair(pilot);values=validated_values('Investigate');values.update(customer_attested=False,reviewed=False)
    for row in values['qualification'].values():row['kind']='Seller hypothesis'
    dev.save(r['id'],r['version'],values,headers=pilot['owner']);d=qa.inspect_pair(**args)
    assert d['qualification']['percent']==100
    assert all(c['input_state']=='Pass' and c['development_state']=='Fail' for c in d['qualification']['criteria'])
    assert not d['original_readiness']['ready'] and d['qualification']['independently_verified_buyer_need']=='Not established'


def test_queue_filters_and_pagination_never_change_scope_or_evaluations(pilot):
    from cios.applications.flora.opportunity_assurance_views import render
    pair(pilot);before=fingerprint()
    html=render(qa.BASE,{'tier':['Research only'],'sort':['enterprise'],'view':['advanced']},pilot['owner'])
    assert html.count('class="assurance-row"')<=10 and 'Research only' in html
    with pytest.raises(ValueError):render(qa.BASE,{'page':['-1']},pilot['owner'])
    with pytest.raises(ValueError):render(qa.BASE,{'tier':['Qualified'],'view':['advanced']},pilot['owner'])
    assert fingerprint()==before


def test_complete_reviewed_inputs_without_explicit_qualify_decision_still_block_handoff(pilot):
    r,args=pair(pilot)
    dev.save(r['id'],r['version'],validated_values('Investigate'),headers=pilot['owner'])
    d=qa.inspect_pair(**args)
    assert d['original_readiness']['ready'] and d['qualification']['percent']==100
    assert not d['original_handoff_checks']['ready'] and not d['original_handoff_checks']['explicit_qualify_selected']
    assert not d['original_handoff_checks']['write_authorised_by_inspection']
    with pytest.raises(ValueError):dev.handoff(r['id'],2,True,headers=pilot['owner'])
    assert not pipeline._path().exists()


def test_commercial_default_is_separate_from_forensic_inspection_and_preserves_santander_history(pilot):
    from cios.applications.flora.opportunity_assurance_views import render
    from cios.applications.flora.opportunity_assurance_commercial import summary
    r,args=pair(pilot);before=fingerprint();d=qa.inspect_pair(**args)
    q={'offer':[r['offer_id']],'enterprise':['santander-uk'],'candidate':[r['id']],'cutoff':['2026-11-13']}
    html=render(qa.BASE,q,pilot['owner'])
    for label in ('Potential business challenge','Opportunity to influence','Best next action','Biggest uncertainty','Advanced Inspection'):assert label in html
    assert 'potentially late' in html and 'open procurement' in html and 'does not establish' in html
    assert 'BTI-TSB-' not in html and 'evaluation_trace' not in html and 'qualification input completeness' not in html.lower() and 'Prioritise' not in html
    assert '30 April 2026' in html and 'H2 2027' in html
    advanced=render(qa.BASE,q|{'view':['advanced']},pilot['owner'])
    assert 'BTI-TSB-MIGRATION' in advanced and 'research-validation priority' in advanced
    assert d['original']['buying_trigger']['tier']=='Prioritise' and fingerprint()==before
    restricted=deepcopy(d['original']);restricted['buying_trigger'].update(tier='Research only',shortlist_eligible=False)
    assert summary(restricted)['outcome']=='Research only' and 'restrictions' in summary(restricted)['next_action']
    earlier=qa.inspect_pair(r['offer_id'],'santander-uk','2026-11-09',headers=pilot['owner'])
    assert summary(earlier['original'])['outcome']=='Research only' and '30 April' not in summary(earlier['original'])['context']


def test_editorial_summary_is_not_an_influence_model_or_new_sales_ranking(pilot):
    from cios.applications.flora.opportunity_assurance_commercial import summary
    r,args=pair(pilot,4,'lloyds');d=qa.inspect_pair(**args);copy=summary(d['original'])
    assert copy['outcome']=='Research only' and 'early' not in copy['outcome'].lower()
    assert not {'score','influence_score','influence_tier','funding','procurement'}&copy.keys()
    assert d['original']['buying_trigger']['tier']=='Research only'
