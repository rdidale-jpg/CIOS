"""F3 current-policy, typed financial and proposed-use exception assurance."""
from copy import deepcopy
from datetime import date
import json
from pathlib import Path

import pytest

from cios.applications.flora.financial_intelligence import candidate_analytics as f, analyst
from cios.applications.flora import document_review as review
from cios.applications.flora.enterprise_intelligence.models import stable_hash
from cios.applications.flora.research_intelligence.source_use_review import SeriesUseProposal,SeriesUseRequest,assess_proposed_use,inspect_current_origin
from tests.fixtures.financial_analyst import measurement,reference
from tests.test_flora_f1_642 import permitted,authority,changed
from tools.research import f3_quality as quality

pytestmark=pytest.mark.real_security_boundary


def proposal_and_request():
    p=SeriesUseProposal.model_validate(quality.load('Series-Use-Proposals.json')[0])
    r=SeriesUseRequest(category=p.category,publisher=p.publisher,document_url=p.seed_documents[0],reporting_subject=p.reporting_subjects[0],
        terms_review_record_revision=p.terms_review_record_revision,purpose=p.purpose,uses=('numerical_reuse','measurement_retention'),
        audience='owner_review',retained_form='minimal_measurements_and_provenance',measurements_in_document=24,documents_in_window=4,
        cumulative_extraction_review='Synthetic review condition only; no scheduled collection or legal safe harbour.',as_of='2026-11-16')
    return p,r


def annuals():
    rows=[]
    for key,value,start,end in [('prior','100.00','2024-04-01','2025-03-31'),('current','110.00','2025-04-01','2026-03-31')]:
        m=measurement('fictional-annual',key,value,metric='revenue')
        rows.append(changed(m,period={'kind':'duration','label':'Synthetic complete FY','start':start,'end':end,'fiscal_year_end':'03-31'}))
    return rows


def annual_recipe(rows,formula='difference'):
    return f.Derivation(derivation_id='synthetic-annual-only',formula=formula,comparison='duration_dates',inputs=tuple(map(reference,rows)))


def statement_rows():
    return [measurement('fictional-statement',k,v,metric=k) for k,v in [('total_income','1000'),('operating_costs','-600'),('credit_impairment','-50'),('profit_before_tax','350')]]


def statement_recipe(rows,**changes):
    data=dict(derivation_id='synthetic-statement-only',mode='reported_statement',opening=reference(rows[0]),adjustments=tuple(map(reference,rows[1:-1])),endpoint=reference(rows[-1]),
        opening_basis='statutory',adjustment_basis='statutory',endpoint_basis='statutory',adjustment_roles=('operating_costs','credit_impairment'))
    data.update(changes);return f.Reconciliation(**data)


def test_five_owner_candidates_are_typed_reproducible_and_not_admitted():
    report=quality.validate()
    assert report['status']=='PARTIAL F3' and report['typed_measurements']==32 and report['reconciliations']==5
    assert report['new_issuer_persisted_runs']==report['new_issuer_runtime_visibility']==report['new_issuer_permissions']==0
    assert set(report['banks'])=={'natwest-group','hsbc-uk','santander-tsb','nationwide','starling'}


def test_one_series_review_covers_many_measurements_without_granting_permission():
    p,r=proposal_and_request()
    result=assess_proposed_use(p,r)
    assert result['proposed_conditions_match'] and result['disposition']=='owner_decision_required'
    assert result['authority']=='proposed_review_only_not_source_permission'
    assert result['technical_admission']==result['canonical_acceptance']=='not_granted'
    assert 'can_use'not in result


@pytest.mark.parametrize('field,value,reason',[
    ('category','issuer_announcement','different_source_category'),('publisher','Other issuer','different_publisher'),
    ('document_url','https://example.invalid/report.pdf','outside_proposed_series'),
    ('reporting_subject','National Westminster Bank PLC','different_reporting_subject'),
    ('terms_review_record_revision','a'*64,'terms_review_changed'),('purpose','AI training','different_purpose'),
    ('uses',['expression_redistribution'],'use_not_in_proposal'),('audience','public','audience_not_in_proposal'),
    ('retained_form','full_text_or_graphics','expression_or_full_text_requires_separate_decision'),
    ('measurements_in_document',25,'document_extraction_limit'),('documents_in_window',5,'cumulative_extraction_limit'),
    ('as_of','2027-01-01','review_date_exception'),('lifecycle','withdrawn','source_lifecycle_exception'),
    ('lifecycle','revoked','source_lifecycle_exception'),('lifecycle','stale','source_lifecycle_exception'),
    ('lifecycle','contradicted','source_lifecycle_exception'),('lifecycle','superseded','source_lifecycle_exception'),
    ('lifecycle','private','source_lifecycle_exception')])
def test_changed_source_use_audience_version_and_extent_require_exceptions(field,value,reason):
    p,r=proposal_and_request();raw=r.model_dump(mode='json');raw[field]=value
    result=assess_proposed_use(p,SeriesUseRequest.model_validate(raw))
    assert result['disposition']=='exception_review_required' and reason in result['exceptions']
    assert result['technical_admission']=='not_granted'


@pytest.mark.parametrize('status',['approved','accepted','permitted'])
def test_caller_cannot_approve_proposal(status):
    p,r=proposal_and_request();raw=p.model_dump(mode='json');raw['status']=status
    with pytest.raises(ValueError):SeriesUseProposal.model_validate(raw)
    raw=p.model_dump(mode='json');raw['approved']=True
    with pytest.raises(ValueError):SeriesUseProposal.model_validate(raw)


@pytest.mark.parametrize('url',['https://example.invalid/','http://example.invalid/reports/','https://u:p@example.invalid/reports/',
    'https://example.invalid/reports/../private/','https://example.invalid/reports/%2e%2e/private/','https://example.invalid/reports/%252e%252e/private/','https://example.invalid/reports/%0a/','https://example.invalid/reports//alias/','https://example.invalid/reports/?allow=true'])
def test_proposed_series_is_not_host_wide_or_unsafe_url(url):
    p,r=proposal_and_request();raw=p.model_dump(mode='json');raw['original_prefixes']=[url]
    with pytest.raises(ValueError):SeriesUseProposal.model_validate(raw)


def test_unknown_terms_scope_and_withdrawn_proposal_do_not_match():
    p,r=proposal_and_request()
    for update,reason in [({'terms_applicability':'unresolved'},'terms_applicability_unresolved'),({'status':'withdrawn'},'proposal_not_current')]:
        raw=p.model_dump(mode='json');raw.update(update)
        assert reason in assess_proposed_use(SeriesUseProposal.model_validate(raw),r)['exceptions']


@pytest.mark.parametrize('selection',['natwest-group','hsbc-uk','santander-tsb','nationwide','starling','F3-SERIES-NW'])
def test_no_named_issuer_or_proposed_review_can_create_an_actual_financial_run(permitted,selection):
    _,headers,_=permitted
    before={p.name:p.read_bytes() for p in review._run_dir().glob('*') if p.is_file()}
    with pytest.raises(PermissionError):f.create_run(selection,headers=headers)
    assert before=={p.name:p.read_bytes() for p in review._run_dir().glob('*') if p.is_file()}


def test_current_origin_is_neither_source_rights_nor_canonical_authority():
    result=inspect_current_origin('https://www.bankofengland.co.uk/boeapps/database/')
    assert result=={'origin_admission':'current_origin_check_passed','rights_decision':'not_established_by_origin_check'}
    for source in quality.load('Source-Use-Register.json'):
        assert inspect_current_origin(source['original_url'])['origin_admission']==('current_origin_check_passed' if source['source_id']=='F3-NB-REVIEW' else 'blocked')


def test_explicit_statement_same_basis_signed_roles_and_endpoint_reconcile():
    rows=statement_rows();result=f.reconcile(statement_recipe(rows),rows)
    assert result['value']=='350' and result['semantic_type']=='calculated' and result['formula']=='signed_bridge'
    with pytest.raises(ValueError):f.reconcile(statement_recipe(rows,mode='basis_reconciliation',adjustment_roles=()),rows)


@pytest.mark.parametrize('bad',['opening','endpoint','subtotal','duplicate-role','missing-role','basis','entity','perimeter','period','currency','state','source-version','sign','reported-endpoint','residual'])
def test_statement_rejects_ambiguous_roles_incompatible_meaning_or_residual(bad):
    rows=statement_rows();changes={}
    if bad=='opening':rows[0]=changed(rows[0],metric='total_assets')
    elif bad=='endpoint':rows[-1]=changed(rows[-1],metric='ebitda')
    elif bad=='subtotal':rows[1]=changed(rows[1],metric='profit_before_impairment')
    elif bad=='duplicate-role':changes['adjustment_roles']=('operating_costs','operating_costs')
    elif bad=='missing-role':changes['adjustment_roles']=()
    elif bad=='basis':changes['adjustment_basis']='adjusted'
    elif bad=='entity':rows[1]=changed(rows[1],subject_id='other')
    elif bad=='perimeter':rows[1]=changed(rows[1],perimeter='Subsidiary')
    elif bad=='period':rows[1]=changed(rows[1],period={'kind':'duration','label':'Other','start':'2025-01-01','end':'2025-06-30','fiscal_year_end':'12-31'})
    elif bad=='currency':rows[1]=changed(rows[1],value={'kind':'numeric','amount':'-600','currency':'USD','scale':'millions','unit':'currency'})
    elif bad=='state':rows[1]=changed(rows[1],state='target')
    elif bad=='source-version':
        source=rows[1].source.model_dump(mode='json');source['source_revision']='a'*64;rows[1]=changed(rows[1],source=source)
    elif bad=='sign':rows[1]=changed(rows[1],value={'kind':'numeric','amount':'600','currency':'GBP','scale':'millions','unit':'currency'})
    elif bad=='reported-endpoint':rows[-1]=changed(rows[-1],semantic_type='assumed',assumption_owner='synthetic',assumption_version='1')
    elif bad=='residual':rows[-1]=changed(rows[-1],value={'kind':'numeric','amount':'351','currency':'GBP','scale':'millions','unit':'currency'})
    with pytest.raises(ValueError):f.reconcile(statement_recipe(rows,**changes),rows)


def test_annual_arithmetic_reproduces_full_years_without_annualisation():
    rows=annuals()
    assert f.calculate(annual_recipe(rows),rows)['value']=='10.00'
    assert f.calculate(annual_recipe(rows,'percent_change'),rows)['value']=='10.0'
    result=f.calculate(annual_recipe(rows),rows)
    assert result['comparison']=='duration_dates' and len(result['periods'])==2
    assert rows[0].period.start.isoformat()=='2024-04-01'


@pytest.mark.parametrize('bad',['361-days','h1','wrong-fye','overlap','nonadjacent','entity','definition','perimeter','state','unit','source-vintage','zero-denominator'])
def test_annual_comparison_rejects_incompatible_years_scopes_or_vintages(bad):
    rows=annuals();target=0
    if bad=='361-days':rows[0]=changed(rows[0],period={'kind':'duration','label':'361day','start':'2024-04-05','end':'2025-03-31','fiscal_year_end':'03-31'})
    elif bad=='h1':rows[0]=changed(rows[0],period={'kind':'duration','label':'H1','start':'2024-04-01','end':'2024-09-30','fiscal_year_end':'03-31'})
    elif bad=='wrong-fye':rows[1]=changed(rows[1],period={'kind':'duration','label':'Other','start':'2025-04-01','end':'2026-03-31','fiscal_year_end':'12-31'})
    elif bad=='overlap':rows[1]=changed(rows[1],period=rows[0].period.model_dump(mode='json'))
    elif bad=='nonadjacent':rows[0]=changed(rows[0],period={'kind':'duration','label':'Earlier','start':'2022-04-01','end':'2023-03-31','fiscal_year_end':'03-31'})
    elif bad=='entity':rows[0]=changed(rows[0],subject_id='Different legal bank')
    elif bad=='definition':rows[0]=changed(rows[0],definition='Different revenue definition')
    elif bad=='perimeter':rows[0]=changed(rows[0],perimeter='Group before acquisition')
    elif bad=='state':rows[0]=changed(rows[0],state='target')
    elif bad=='unit':rows[0]=changed(rows[0],value={'kind':'numeric','amount':'100','currency':'USD','unit':'currency','scale':'millions'})
    elif bad=='source-vintage':
        source=rows[0].source.model_dump(mode='json');source['source_revision']='b'*64;rows[0]=changed(rows[0],source=source)
    elif bad=='zero-denominator':rows[0]=changed(rows[0],value={'kind':'numeric','amount':'0','currency':'GBP','unit':'currency','scale':'millions'})
    with pytest.raises(ValueError):f.calculate(annual_recipe(rows,'percent_change'if bad=='zero-denominator'else'difference'),rows)


def test_real_candidates_preserve_distinct_entities_acquisition_windows_and_basis():
    banks={b['id']:b for b in quality.load('Five-Bank-Candidates.json')}
    assert {m['value']['currency'] for m in banks['hsbc-uk']['measurements']}=={'USD'}
    tsb=next(m for m in banks['santander-tsb']['measurements'] if m['subject_id']=='research-subject:tsb-contribution' and m['metric']=='profit_before_tax')
    assert tsb['period']['start']=='2026-05-01' and tsb['period']['end']=='2026-09-30'
    assert 'standalone annual'in tsb['perimeter']
    nb=banks['nationwide'];assert {m['accounting_basis'] for m in nb['measurements']}=={'underlying','statutory','disclosed_bridge'}
    st=[f.Measurement.model_validate(m) for m in banks['starling']['measurements']if m['metric']=='revenue']
    with pytest.raises(ValueError,match='perimeter'):f.calculate(annual_recipe(st),st)
    assert not any(m['metric']in {'arr','platform_accounts','integration_costs'} for b in banks.values()for m in b['measurements'])


def test_f1_payload_and_id_remain_exactly_the_validated_f2_contract():
    assert f._run_record('boe-household-deposit-stocks',f._current_inputs('boe-household-deposit-stocks'),'synthetic-f3-compatibility')==quality.load('F1-Compatibility.json')


def test_synthetic_complete_annual_values_survive_existing_guarded_run_reload(permitted,monkeypatch):
    _,headers,_=permitted;rows=annuals()
    source={'title':'Synthetic annual contract only','url':'https://example.invalid/financial-contract','publication_date':None,'retrieved_at':'2026-11-16T00:00:00+00:00',
        'retrieval_extent':'Synthetic fixture, no real company or source-use grant','reporting_period':'Synthetic complete years',
        'rights':{'attribution':'Synthetic fixture only','licence_url':'https://example.invalid/not-a-licence'}}
    bundle=f.InputBundle('BK-IND-002','Synthetic annual contract only',tuple(rows),source)
    with monkeypatch.context() as patch:
        patch.setattr(f,'_current_inputs',lambda _:bundle)
        identity=f.create_run('synthetic-f3-annual',headers=headers)
        raw=review.load_run(identity);assert raw['workflow']==f.WORKFLOW and raw['analytical_candidate']['derivations'][0]['comparison']=='duration_dates'
        current=f.read_analysis(identity,headers=headers)
        assert current['results'][0]['value']=='10.00'
        html=analyst.compose(current)
        assert 'Annual difference'in html and 'Synthetic annual contract only'in html
        assert '2024'in html and '2026'in html
    assert f.read_analysis(identity,headers=headers)=={}
    assert review.load_run(identity)==raw


def test_annual_comparison_accepts_leap_year_but_retains_weaker_inputs():
    rows=annuals()
    rows[0]=changed(rows[0],period={'kind':'duration','label':'366dayFY','start':'2023-04-01','end':'2024-03-31','fiscal_year_end':'03-31'})
    rows[1]=changed(rows[1],period={'kind':'duration','label':'365dayFY','start':'2024-04-01','end':'2025-03-31','fiscal_year_end':'03-31'},semantic_type='assumed',assumption_owner='synthetic-scenario-owner',assumption_version='1')
    result=f.calculate(annual_recipe(rows),rows)
    assert result['value']=='10.00' and result['semantic_type']=='estimated'
    assert result['dependency_types']==['reported','assumed']
    assert 'Estimated' in analyst._result_card(result,{m.measurement_id:m for m in rows})
    assert 'Reported annual' not in analyst._result_card(result,{m.measurement_id:m for m in rows})
