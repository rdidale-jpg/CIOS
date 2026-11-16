"""Routine lawful working research, exact factual binding and isolated exceptions."""
from copy import deepcopy
import json
import shutil
from pathlib import Path

import pytest

from cios.applications.flora.financial_intelligence import candidate_analytics as f, analyst
from cios.applications.flora.research_intelligence import source_import as source, model
from cios.applications.flora import leadership_agenda as agenda, visual_streams as visual, document_review as review
from cios.applications.flora.security_web import mutation_capability
from tests.test_flora_f1_642 import permitted, authority

pytestmark = pytest.mark.real_security_boundary
KEY='nationwide-fy2026'


@pytest.fixture
def retained(tmp_path, monkeypatch):
    root=tmp_path/'retained';shutil.copytree(model.REPO/'enterprise-knowledge',root/'enterprise-knowledge')
    monkeypatch.setattr(model,'REPO',root)
    return root/'enterprise-knowledge/banking/research-model/source-snapshots/RUD1-Public-Facts.json'


def mutate(path, fn):
    data=json.loads(path.read_text());fn(data);path.write_text(json.dumps(data));return data


def test_actual_issuer_financials_persist_reload_reproduce_and_enter_main(permitted):
    _,headers,_=permitted
    identities=f.refresh_research(headers=headers)
    identity=f.find_existing_run(KEY,'BK-IND-002',headers=headers)
    assert identity in identities and len(identities)==2
    raw=review.load_run(identity);before=review._run_path(identity).read_bytes()
    assert raw['canonical_update']=={'enterprise_model_updated':False,'observations_created':0}
    projection=f.read_analysis(identity,headers=headers)
    assert len(projection['measurements'])==8
    assert [r['value']for r in projection['results']]==['2026','1490']
    assert {m['period']['end']for m in projection['measurements']}=={'2026-03-31'}
    assert {m['value']['currency']for m in projection['measurements']}=={'GBP'}
    html=visual.render('/industries/banking',{'selected':['nationwide'],'analysis':[identity]},headers)
    for text in ('£2.026bn','£1.49bn','FLORA Insight','£399m member reward','Source-use basis','2026-05-21'):
        assert text in html
    detail=review.run_page(identity,headers=headers)
    assert 'Two reviewed database rows' not in detail and 'Reconciled endpoint' in detail
    assert '(closing − opening)' not in detail
    assert f.refresh_research(headers=headers)==identities
    assert review._run_path(identity).read_bytes()==before


@pytest.mark.parametrize('slug,period,value',[
    ('natwest','1 January–30 June 2026','92,548'),('hsbc-uk','1 January–30 June 2026','79,323'),
    ('santander-uk','1 January–30 June 2026','61,365'),('tsb','1 January–30 June 2026','29,908'),
    ('nationwide','1 October 2025–31 March 2026','100,886'),('starling','1 October 2025–31 March 2026','15,223')])
def test_six_legal_banks_actual_periods_and_public_context(slug,period,value):
    issue=agenda.routine_service_issue(slug)
    assert issue and all(f.period==period for f in issue.facts)
    assert value in issue.conclusion.text
    ctx=visual.resolve('/industries/banking',{'selected':[slug]})
    assert ctx.selected==slug
    assert ctx.selected==visual.resolve('/industries/banking',{'selected':[slug],'stream':['forces']}).selected
    assert 'not a causal diagnosis' in issue.conclusion.reasoning
    assert not any(f.unit=='currency'for f in issue.facts)


@pytest.mark.parametrize('field,value',[(x,True)for x in ('owner_only','withdrawn','revoked','contradictory','stale','superseded')]+[('freshness','stale')])
@pytest.mark.parametrize('level',['package','source','row'])
def test_owner_lifecycle_restrictions_never_leak_service_rows(retained,level,field,value):
    def change(d):
        target=d if level=='package' else d['sources'][0] if level=='source' else d['service_profiles'][-1]
        target[field]=value
    mutate(retained,change)
    assert agenda.routine_service_issue('starling') is None
    if level!='package':assert f._current_inputs(KEY).measurements


@pytest.mark.parametrize('field,value',[('received',999999),('closed',15223),('upheld','99.99'),('period','1 January–30 June 2026'),('name','NatWest Group'),('scope','Global Group')])
def test_profile_must_match_exact_retained_entity_period_measure(retained,field,value):
    mutate(retained,lambda d:d['service_profiles'][-1].__setitem__(field,value))
    assert agenda.routine_service_issue('starling') is None


@pytest.mark.parametrize('mutation',['substring','sign','entity','period','currency','basis','source-version','date'])
def test_financial_measurements_bound_to_located_source_facts(retained,mutation):
    def change(d):
        m=d['financial_selections'][0]['measurements'][4]
        if mutation=='substring':m['value']['amount']='149'
        if mutation=='sign':m['value']['amount']='-1490'
        if mutation=='entity':m['subject_id']='research-subject:other'
        if mutation=='period':m['period']['start']='2025-01-01'
        if mutation=='currency':m['value']['currency']='USD'
        if mutation=='basis':m['accounting_basis']='underlying'
        if mutation=='source-version':m['source']['source_revision']='f'*64
        if mutation=='date':m['source']['published']='2026-05-20'
    mutate(retained,change)
    with pytest.raises((PermissionError,ValueError)):f._current_inputs(KEY)


@pytest.mark.parametrize('mutation',['withdrawn','rights','third-party','restriction','purpose','retention','audience','origin'])
def test_routine_method_is_not_a_caller_or_publisher_grant(retained,mutation):
    def change(d):
        s=d['sources'][1]
        if mutation=='withdrawn':s['withdrawn']=True
        elif mutation=='rights':s['rights']['status']='revoked'
        elif mutation=='third-party':s['third_party_material']=True
        elif mutation=='restriction':s['restrictions']=['Actual applicable restriction']
        elif mutation=='origin':s['url']='https://www.lloydsbankinggroup.com/report.pdf'
        else:s[mutation]='full_text_or_bulk_training'
    mutate(retained,change)
    with pytest.raises(PermissionError):f._current_inputs(KEY)
    assert agenda.routine_service_issue('starling')


def test_one_source_withdrawal_removes_results_without_blocking_another(permitted,retained):
    _,headers,_=permitted
    identity=f.create_run(KEY,headers=headers);before=review._run_path(identity).read_bytes()
    mutate(retained,lambda d:d['sources'][1].__setitem__('withdrawn',True))
    assert f.read_analysis(identity,headers=headers)=={}
    assert identity not in analyst.navigation(visual.Context('banking','landscape'),headers)
    assert not analyst.authorise_request('/industries/banking?analysis='+identity,headers=headers)
    assert len(f.refresh_research(headers=headers))==1
    assert agenda.routine_service_issue('starling')
    assert review._run_path(identity).read_bytes()==before


def test_bad_financial_row_isolated_before_nested_write_transaction(permitted,retained):
    _,headers,_=permitted
    mutate(retained,lambda d:d['financial_selections'][0]['measurements'][4]['value'].__setitem__('amount','149'))
    assert len(f.refresh_research(headers=headers))==1
    assert f.find_existing_run('boe-household-deposit-stocks','BK-IND-002',headers=headers)


@pytest.mark.parametrize('target',[
    'https://www.nationwide.co.uk/private/report.pdf','https://www.nationwide.co.uk.evil.invalid/-/assets/report.pdf',
    'https://www.nationwide.co.uk/-/assets/nationwidecouk/documents/about/how-we-are-run/results-and-accounts/2025-2026/2026-preliminary-results.pdf?redirect=private',
    'http://www.nationwide.co.uk/report.pdf','https://u:p@www.nationwide.co.uk/report.pdf'])
def test_narrow_origin_improvement_does_not_open_host_or_redirects(target):
    with pytest.raises(ValueError):source.official_url(target)


def test_research_refresh_is_existing_upload_capability_not_promotion():
    assert mutation_capability('/financial-research/refresh')=='package.upload'
    assert mutation_capability('/financial-research/refresh/anything')==''
    with pytest.raises(PermissionError):f.refresh_research(headers={})


@pytest.mark.parametrize('case',['source','financial-key','service-key'])
def test_conflicting_identities_are_omitted_without_first_wins(retained,case):
    def change(d):
        if case=='source':
            duplicate=deepcopy(d['sources'][0]);duplicate['withdrawn']=True;d['sources'].append(duplicate)
        elif case=='financial-key':d['financial_selections'].append(deepcopy(d['financial_selections'][0]))
        else:d['service_profiles'].append(deepcopy(d['service_profiles'][-1]))
    mutate(retained,change)
    if case=='financial-key':
        with pytest.raises(PermissionError):f._current_inputs(KEY)
    else:assert agenda.routine_service_issue('starling') is None
    if case=='source':assert f._current_inputs(KEY).measurements


@pytest.mark.parametrize('bad',[[-1],[999],[True],[0,0],['0'],[]])
def test_malformed_source_indices_omit_only_dependent_research(retained,bad):
    mutate(retained,lambda d:d['sources'][0]['fact_bindings'][-1].__setitem__('excerpt_indices',bad))
    assert agenda.routine_service_issue('starling') is None
    assert f._current_inputs(KEY).measurements


def test_source_missing_identity_does_not_block_unrelated_research(retained):
    mutate(retained,lambda d:d['sources'].append({'withdrawn':True}))
    assert agenda.routine_service_issue('starling')
    assert f._current_inputs(KEY).measurements
