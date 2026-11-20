"""Public factual method and isolated legal-resolution proofs, never live clearance."""
from copy import deepcopy
from dataclasses import asdict
from datetime import date
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from cios.applications.flora.financial_intelligence import candidate_analytics as f
from cios.applications.flora.research_intelligence import model, source_import as source
from cios.applications.flora import visual_streams as visual, intelligence_presentation as p
from tests.test_flora_f1_642 import permitted, authority

PATH = 'enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json'
pytestmark = pytest.mark.real_security_boundary


def seal(s):
    payload = {k:s[k] for k in ('document_identity','fact_bindings')}
    s['facts_sha256'] = hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    return s


@pytest.fixture
def retained(tmp_path, monkeypatch):
    root = tmp_path/'retained'
    shutil.copytree(model.REPO/'enterprise-knowledge',root/'enterprise-knowledge')
    monkeypatch.setattr(model,'REPO',root)
    return root/PATH


def edit(path, fn, *, reseal=False):
    s=json.loads(path.read_text());fn(s)
    if reseal:seal(s)
    path.write_text(json.dumps(s));return s


@pytest.fixture
def resolved(retained):
    # Explicit isolated owner double; not publisher consent or a live decision.
    def resolve(s):
        s['rights']['contract_restriction_found']=False
        item=s['rights']['material_exceptions'][0]
        item.update(status='resolved_for_factual_method',resolved_by='ISOLATED Source-owner test double',
                    resolved_on=date.today().isoformat(),basis='ISOLATED test only: no live legal clearance')
    edit(retained,resolve)
    return retained


def test_shipped_lloyds_remains_inactive_without_mutating_existing_release(retained):
    before=retained.read_bytes()
    assert f.public_factual_projection()=={} and f.public_factual_html()==''
    assert retained.read_bytes()==before
    assert len(f.public_nationwide_projection()['measurements'])==8
    assert len(source.minimal_factual_integrity(json.loads(retained.read_text())))==3


def test_positive_three_fact_projection_has_exact_meaning_and_no_internal_pdf(resolved):
    result=f.public_factual_projection();facts=result['facts']
    assert [(str(x.value),x.unit,x.basis) for x in facts]==[
        ('11084','GBP millions','underlying'),('3.21','%','issuer banking NIM alternative performance measure'),
        ('477.5','GBP billions','issuer period-average banking assets')]
    assert all(x.semantic_type=='reported' and x.measurement_state=='actual' for x in facts)
    assert all(x.period=='1 January–30 September 2026' and p.eligible(x) for x in facts)
    assert facts[0].scope!=facts[1].scope and 'average' in facts[2].basis
    assert p.eligible(result['analysis']) and result['analysis'].counter_evidence
    assert result['analysis'].semantic_type=='insight' and len(result['analysis'].dependencies)==3
    public=json.dumps(result,default=lambda v:asdict(v) if hasattr(v,'__dataclass_fields__')else str(v))
    assert '.pdf' not in public and 'lloyds_section_2' not in public
    html=f.public_factual_html()
    for text in ('£11.084bn','3.21%','£477.5bn','Reported','Nine months to 30 September 2026'):assert text in html
    assert 'href="https://www.lloydsbankinggroup.com/"' in html
    assert all(text not in html for text in ('<details','Unknown','approval','method_review','.pdf'))
    assert 'FLORA Insight' in f.public_factual_html(insight=True)


def test_one_method_covers_other_already_admitted_issuers_without_number_approvals(resolved):
    s=json.loads(resolved.read_text());s['rights']['material_exceptions']=[]
    for domain in ('www.easyjet.com','www.lloydsbank.com'):
        s['url']=s['retrieval_url']='https://'+domain+'/investor-results'
        s['rights']['attribution_url']='https://'+domain+'/'
        assert source.routine_factual_use(s)=='minimal_factual_analysis'


@pytest.mark.parametrize('url',[
    'https://www.sec.gov/report','https://www.ons.gov.uk/report','http://www.lloydsbank.com/report',
    'https://www.lloydsbankinggroup.com.evil.invalid/report','https://user@www.lloydsbankinggroup.com/report'])
def test_category_never_admits_unknown_or_unsafe_origins(resolved,url):
    s=json.loads(resolved.read_text());s['url']=url
    with pytest.raises((ValueError,PermissionError)):source.routine_factual_use(s)


@pytest.mark.parametrize('mutation', ['missing','duplicate','unresolved','denied','no-basis','no-owner','future','wrong-version','wrong-scope'])
def test_known_section2_exception_cannot_be_deleted_or_self_cleared(resolved,mutation):
    def change(s):
        issues=s['rights']['material_exceptions'];i=issues[0]
        if mutation=='missing':issues.pop(0)
        elif mutation=='duplicate':issues.append(deepcopy(i))
        elif mutation in {'unresolved','denied'}:i['status']=mutation
        elif mutation=='no-basis':i['basis']=''
        elif mutation=='no-owner':i['resolved_by']=''
        elif mutation=='future':i['resolved_on']='2099-01-01'
        elif mutation=='wrong-scope':i['operations']=['public_deep_link']
        else:i['source_version']='other document'
    edit(resolved,change)
    assert f.public_factual_projection()=={} and f.public_factual_html()==''


def test_deep_link_exception_does_not_hold_homepage_facts_after_section2_resolution(resolved):
    edit(resolved,lambda s:s['rights']['material_exceptions'][1].update(status='denied'))
    assert len(f.public_factual_projection()['facts'])==3
    edit(resolved,lambda s:s['rights'].update(attribution_url=s['url']))
    assert f.public_factual_projection()=={}


def test_protected_copy_exception_does_not_hold_independent_facts(resolved):
    edit(resolved,lambda s:s['rights']['material_exceptions'].append(
        {'issue':'protected_copy','operations':['copy_protected_material'],'status':'denied'}))
    assert len(f.public_factual_projection()['facts'])==3


@pytest.mark.parametrize('level',['binding','fact'])
@pytest.mark.parametrize('field,value',[('withdrawn',True),('owner_only',True),('freshness','stale'),('restrictions',['restricted'])])
def test_measure_level_restriction_cannot_be_lost_in_public_render(resolved,level,field,value):
    def change(s):
        row=s['fact_bindings'][0]
        (row if level=='binding' else row['facts'])[field]=value
    edit(resolved,change,reseal=True)
    assert f.public_factual_projection()=={}


@pytest.mark.parametrize('change',[
    {'expression_reuse':True},{'contract_restriction_found':True},{'contract_restriction_found':None},
    {'operations':['read_public','independent_facts','minimal_numerical_retention','public_read_only','archive_documents']},
    {'operations':['read_public']},{'policy_reference':'unaccepted policy'},
    {'material_exceptions':None},{'homepage_conditions_met':False}])
def test_material_legal_scope_is_not_cleared_by_a_policy_label(resolved,change):
    edit(resolved,lambda s:s['rights'].update(change))
    assert f.public_factual_projection()=={}


@pytest.mark.parametrize('field,value',[
    ('document_identity',[]),('fact_bindings',[{'key':'invalid','facts':True}]),('retrieved_at',None),
    ('fact_bindings',None),('publication_date','2027-01-01')])
def test_malformed_nested_provenance_is_an_omission_not_a_server_error(resolved,field,value):
    edit(resolved,lambda s:s.__setitem__(field,value))
    assert f.public_factual_projection()=={}


@pytest.mark.parametrize('field,value',[
    ('withdrawn',True),('revoked',True),('denied',True),('contradictory',True),('stale',True),
    ('superseded',True),('owner_only',True),('freshness','stale'),('canonical_mutation',True),
    ('authority','accepted_canonical'),('verification','unverified'),('primary_content_sha256','f'*64),
    ('text_path','private-report.txt'),('content_kind','reviewed_web_excerpt'),('restrictions',['copy denied']),
    ('audience','private_workspaces'),('purpose','bulk_export'),('retained_form','whole_report'),
    ('retrieval_url','https://www.lloydsbankinggroup.com/other-report')])
def test_source_use_and_lifecycle_changes_omit_only_affected_output(resolved,field,value):
    cached=f.public_factual_html();assert '£11.084bn' in cached
    edit(resolved,lambda s:s.__setitem__(field,value))
    assert f.public_factual_projection()=={} and f.public_factual_html()==''
    assert len(f.public_nationwide_projection()['measurements'])==8
    # A consumer cannot inject its stale view into the live renderer.
    with pytest.raises(TypeError):f.public_factual_html(cached=cached)


@pytest.mark.parametrize('field,value',[
    ('subject_id','research-subject:lloyds-bank-plc'),('subject_name','Lloyds Bank plc'),
    ('perimeter','UK legal bank'),('accounting_basis','statutory'),('definition','Other income'),
    ('metric','supplier_budget'),('state','target'),('semantic_type','estimated'),
    ('precision_dp',5),('rounding','exact')])
def test_changed_issuer_basis_or_semantics_rejected_even_with_valid_retained_hash(resolved,field,value):
    edit(resolved,lambda s:s['fact_bindings'][0]['facts'].__setitem__(field,value),reseal=True)
    assert f.public_factual_projection()=={}


@pytest.mark.parametrize('field,value',[('currency','EUR'),('scale','billions'),('unit','percentage'),('amount','NaN'),('amount','Infinity'),('amount','11084.1')])
def test_units_and_precision_never_turn_into_another_measure(resolved,field,value):
    edit(resolved,lambda s:s['fact_bindings'][0]['facts']['value'].__setitem__(field,value),reseal=True)
    assert f.public_factual_projection()=={}


@pytest.mark.parametrize('field,value',[('start','2026-07-01'),('end','2026-06-30'),('kind','instant'),('fiscal_year_end','03-31')])
def test_reporting_period_not_quarter_or_closing_stock(resolved,field,value):
    edit(resolved,lambda s:s['fact_bindings'][0]['facts']['period'].__setitem__(field,value),reseal=True)
    assert f.public_factual_projection()=={}


def test_changed_factual_data_requires_integrity_and_duplicate_rows_are_not_displayed(resolved):
    s=json.loads(resolved.read_text());s['fact_bindings'][0]['facts']['value']['amount']='99999'
    resolved.write_text(json.dumps(s));assert f.public_factual_projection()=={}
    seal(s);s['fact_bindings'][1]=deepcopy(s['fact_bindings'][0]);seal(s)
    resolved.write_text(json.dumps(s));assert f.public_factual_projection()=={}


@pytest.mark.parametrize('payload',[[],True,'untrusted',{'rights':'granted'},None])
def test_malformed_owner_records_fail_closed_without_500(retained,payload):
    retained.write_text(json.dumps(payload));assert f.public_factual_projection()=={}


def test_missing_corrupt_or_symlinked_case_is_not_a_fallback_to_private_data(resolved,tmp_path):
    saved=resolved.read_bytes();resolved.unlink();assert f.public_factual_projection()=={}
    resolved.write_text('{broken');assert f.public_factual_projection()=={}
    resolved.unlink();private=tmp_path/'private-record';private.write_bytes(saved)
    resolved.symlink_to(private);assert f.public_factual_projection()=={} and private.read_bytes()==saved


def test_public_projection_never_discovers_or_changes_private_runs(resolved,monkeypatch,permitted):
    _,headers,_=permitted
    from cios.applications.flora import document_review as review, security_store as ss
    def forbidden(*a,**k):raise AssertionError('Public factual read reached private state')
    for name in ('find_existing_run','create_run','refresh_research','_current_inputs','read_analysis'):
        monkeypatch.setattr(f,name,forbidden)
    monkeypatch.setattr(review,'load_run',forbidden);monkeypatch.setattr(ss.SecurityStore,'resolve',forbidden)
    assert len(f.public_factual_projection()['facts'])==3 and '£11.084bn' in f.public_factual_html()


def test_guest_and_authorised_main_are_identical_without_private_run_discovery(resolved,permitted,monkeypatch):
    _,headers,_=permitted
    from tests.test_flora_uxr1_650 import main
    def forbidden(*a,**k):raise AssertionError('Public view discovered a private Financial run')
    for name in ('find_existing_run','read_analysis','create_run'):
        monkeypatch.setattr(f,name,forbidden)
    query={'stream':['landscape'],'detail':['lending-income']}
    guest=main(visual.render('/enterprises/lloyds',query,{}))
    private=main(visual.render('/enterprises/lloyds',query,headers))
    assert guest==private and '£11.084bn' in guest
    edit(resolved,lambda s:s.update(withdrawn=True))
    guest=main(visual.render('/enterprises/lloyds',query,{}))
    private=main(visual.render('/enterprises/lloyds',query,headers))
    assert guest==private and '£11.084bn' not in guest


def test_public_slice_is_not_a_financial_run_selection_or_canonical_authority(resolved,permitted):
    _,headers,_=permitted
    assert f.permitted_selection_keys()==('boe-household-deposit-stocks','nationwide-fy2026')
    for selection in ('lloyds-q326-public','PFI-LBG-Q326'):
        with pytest.raises(PermissionError):f.create_run(selection,headers=headers)
    result=f.public_factual_projection()
    assert all(x.canonical_status=='analytical_working_research' for x in result['facts'])


def test_public_method_does_not_implicitly_extend_a_legacy_financial_run_grant(resolved,permitted):
    _,headers,_=permitted
    path=resolved.with_name('RUD1-Public-Facts.json');data=json.loads(path.read_text())
    s=data['sources'][1];ordinary=json.loads(resolved.read_text())['rights']
    s['rights']=dict(ordinary,material_exceptions=[],attribution_url='https://www.nationwide.co.uk/')
    s['document_identity']={'url':s['url'],'publisher':s['publisher'],'title':s['title'],
                            'published':s['publication_date'],'version':'isolated-ordinary-method'}
    path.write_text(json.dumps(data))
    assert source.routine_factual_use(s)=='minimal_factual_analysis'
    assert f.permitted_selection_keys()==('boe-household-deposit-stocks',)
    with pytest.raises(PermissionError):f.create_run('nationwide-fy2026',headers=headers)


def test_malformed_legacy_rights_are_isolated_from_other_public_sources(resolved):
    path=resolved.with_name('RUD1-Public-Facts.json');data=json.loads(path.read_text())
    data['sources'][1]['rights']=None;path.write_text(json.dumps(data))
    assert f.public_nationwide_projection()=={}
    assert len(f.public_factual_projection()['facts'])==3


def test_existing_statement_calculation_preserves_compatible_inputs_and_denies_mixed_perimeters(resolved):
    from dataclasses import replace
    a=f.public_factual_projection()['facts'][0]
    result=p.difference(a,replace(a,text='Same-period comparison',value=a.value-1),text='Difference between two compatible reported amounts')
    assert result.value==1 and result.semantic_type=='calculated'
    with pytest.raises(ValueError):p.difference(a,f.public_factual_projection()['facts'][1],text='Invalid Group ratio')


@pytest.mark.parametrize('reading',['facts','insight'])
def test_lending_main_withdraws_all_new_visible_hidden_and_accessible_outputs(resolved,reading):
    query={'stream':['landscape'],'detail':['lending-income'],'reading':[reading]}
    html=visual.render('/enterprises/lloyds',query,{})
    assert '£11.084bn' in html and '£477.5bn' in html and '3.21%' in html
    assert 'public-financial-title' in html and 'aria-labelledby="public-financial-title"' in html
    edit(resolved,lambda s:s.update(withdrawn=True))
    html=visual.render('/enterprises/lloyds',query,{})
    assert all(x not in html for x in ('£11.084bn','£477.5bn','3.21%','public-financial-title'))
    assert 'From funding to earnings' in html


def test_http_no_store_revalidation_and_no_new_export_or_rights_override(resolved):
    from tests.test_flora_auth1_652 import web
    route='/enterprises/lloyds?stream=landscape&detail=lending-income'
    with web() as get:
        status,html,headers=get(route)
        assert status==200 and '£11.084bn' in html and headers['Cache-Control']=='no-store'
        assert '.pdf' not in html[html.index('public-financial-facts'):html.index('</section>',html.index('public-financial-facts'))]
        # No new export API or URL flag can publish a private/cached/legal record.
        for query in ('&format=csv','&rights=true','&source=PFI-LBG-Q326'):
            status,body,_=get(route+query)
            assert status!=200 and '£11.084bn' not in body
        edit(resolved,lambda s:s.update(withdrawn=True))
        status,html,headers=get(route,{'If-None-Match':'old-public-view'})
        assert status==200 and headers['Cache-Control']=='no-store'
        assert all(x not in html for x in ('£11.084bn','£477.5bn','3.21%','public-financial-title'))


def test_bounded_evolution_keeps_all_private_functions_and_module_state_exact():
    from tools.research.public_financial_compatibility import validate
    assert validate(Path(__file__).resolve().parents[1])['ci_comparator_changed'] is False
