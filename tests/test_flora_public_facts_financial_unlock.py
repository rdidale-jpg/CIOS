"""Ordinary factual analysis, real LEI data and preserved consequential boundaries."""
from copy import deepcopy
from decimal import Decimal
import hashlib,json,shutil
from pathlib import Path
import pytest
from cios.applications.flora.research_intelligence import model,source_import as source
from cios.applications.flora.financial_intelligence import public_statements as ps,candidate_analytics as f
from cios.applications.flora import lloyds_gold as g
from tests.test_flora_living_enterprise_preview import http

PATH='enterprise-knowledge/banking/research-model/source-snapshots/'
@pytest.fixture
def records(tmp_path,monkeypatch):
    root=tmp_path/'repo';shutil.copytree(model.REPO/'enterprise-knowledge',root/'enterprise-knowledge');monkeypatch.setattr(model,'REPO',root)
    return root/PATH

def edit(folder,file,fn):
    path=folder/file;s=json.loads(path.read_text());fn(s)
    s['facts_sha256']=hashlib.sha256(json.dumps({k:s[k]for k in ('document_identity','fact_bindings')},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    path.write_text(json.dumps(s));return s

def view(focus='group',detail=''):
    return g.render({'stream':['landscape'],'focus':[focus],'detail':[detail]},canonical=True).split('<main ',1)[1].split('</main>',1)[0]

def test_real_lei_group_and_division_financials_are_now_presented():
    q=ps.economic_projection('lloyds-q3');h=ps.economic_projection('lloyds-h1')
    assert len(q['lines'])==35 and len(h['lines'])==74
    assert {k:v['value']for k,v in q['bridges'].items()}=={'underlying-earnings':'6582','statutory-earnings':'6625'}
    assert q['comparisons']['profit_before_tax-movement']['value']=='1947'
    assert q['comparisons']['remediation-movement']['value']=='851'
    assert q['comparisons']['customer_deposits-movement']['value']=='6320'
    assert {k:v['value']for k,v in h['comparisons'].items()if k.endswith('underlying_profit_before_tax-movement')}=={'retail-underlying_profit_before_tax-movement':'282','commercial-underlying_profit_before_tax-movement':'231','retirement-underlying_profit_before_tax-movement':'101','central-underlying_profit_before_tax-movement':'40','group-underlying_profit_before_tax-movement':'654'}
    root=view();assert all(x in root for x in ('£6.625bn','£11.084bn','£14.819bn','£2.256bn','£1.425bn','£245m'))
    for focus,value in [('retail','£2.256bn'),('commercial','£1.425bn'),('retirement','£245m')]:assert value in view(focus)
    assert len(f.public_factual_projection()['facts'])==3


def test_no_publisher_permission_or_resolution_record_needed_for_ordinary_facts(records):
    s=json.loads((records/'PFI-Lloyds-Q326.json').read_text())
    for key in ('policy_reference','method_review','contract_restriction_found','material_exceptions'):
        s['rights'].pop(key,None)
    assert source.routine_factual_use(s)=='minimal_factual_analysis'
    for host in ('www.lloydsbankinggroup.com','investors.example.com','www.easyjet.com'):
        x=deepcopy(s);x['url']=x['retrieval_url']='https://'+host+'/results';x['rights']['attribution_url']='https://'+host+'/'
        assert source.routine_factual_use(x)=='minimal_factual_analysis'
    s['rights']['material_exceptions']=[{'issue':'old_unestablished_concern','operations':['independent_facts'],'status':'unresolved'}]
    assert source.routine_factual_use(s)=='minimal_factual_analysis'


@pytest.mark.parametrize('change',[{'expression_reuse':True},{'contract_restriction_found':True},
 {'material_exceptions':[{'issue':'binding_access_agreement','operations':['independent_facts'],'applicable':True}]},
 {'material_exceptions':[{'issue':'restricted_data_licence','operations':['public_read_only'],'status':'denied'}]}])
def test_actual_restrictions_remain_effective(records,change):
    edit(records,'PFI-Lloyds-Q326.json',lambda s:s['rights'].update(change))
    assert ps.economic_projection('lloyds-q3')=={} and f.public_factual_projection()=={}
    assert ps.economic_projection('lloyds-h1')
    assert '£6.625bn'not in view() and '£2.256bn'in view()


@pytest.mark.parametrize('flag',['withdrawn','revoked','denied','stale','owner_only','superseded'])
def test_source_withdrawal_omits_dependent_views_and_preserves_unrelated_research(records,flag):
    edit(records,'PFI-Lloyds-Q326.json',lambda s:s.update({flag:True}))
    assert ps.economic_projection('lloyds-q3')=={} and f.public_factual_projection()=={}
    for focus,detail in [('group',''),('economics','income'),('economics','costs'),('economics','capital')]:
        body=view(focus,detail);assert '£6.625bn'not in body and '£11.084bn'not in body
    assert '£2.256bn'in view('retail')


def test_correction_is_reloaded_and_cannot_leave_a_stale_bridge(records):
    before=ps.economic_projection('lloyds-q3');old=next(x for x in before['lines']if x.measurement_id=='profit_before_tax-2026')
    edit(records,'PFI-Lloyds-Q326.json',lambda s:next(r for r in s['fact_bindings']if r['key']==old.measurement_id)['facts']['value'].update(amount='6626'))
    current=ps.economic_projection('lloyds-q3');assert current['source_revision']!=before['source_revision']
    assert current['comparisons']['profit_before_tax-movement']['value']=='1948'
    assert 'statutory-earnings'not in current['bridges']
    assert '£6.626bn'in view() and '£6.625bn'not in view()
    assert 'reconcile this to' not in view('economics','income')


@pytest.mark.parametrize('field,value',[('subject_id','other-enterprise'),('subject_name','Lloyds Bank plc'),('state','target')])
def test_wrong_identity_or_nonactual_input_is_rejected(records,field,value):
    edit(records,'PFI-Lloyds-Q326.json',lambda s:s['fact_bindings'][0]['facts'].update({field:value}))
    assert ps.economic_projection('lloyds-q3')=={}


@pytest.mark.parametrize('mutation',['period','basis','unit','perimeter'])
def test_incompatible_axes_never_produce_comparisons(records,mutation):
    def change(s):
        row=next(r['facts']for r in s['fact_bindings']if r['key']=='profit_before_tax-2025')
        if mutation=='period':row['period']['end']='2025-06-30'
        elif mutation=='basis':row['accounting_basis']='underlying'
        elif mutation=='unit':row['value']['currency']='USD'
        else:row['perimeter']='Retail segment'
    edit(records,'PFI-Lloyds-Q326.json',change)
    assert ps.economic_projection('lloyds-q3')=={}
    assert ps.economic_projection('lloyds-h1')['lines']


def test_actual_and_proforma_capital_cannot_be_compared_as_one_basis():
    q=ps.economic_projection('lloyds-q3');by={x.measurement_id:x for x in q['lines']}
    assert by['cet1-2025'].state=='actual' and by['cet1-proforma-2025'].state=='pro_forma'
    assert by['cet1-2025'].perimeter=='prudential consolidated Group'
    assert '13.3%'in view('economics','capital') and '13.2%'in view('economics','capital')


def test_public_analysis_does_not_enumerate_or_create_private_runs(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('Public factual analysis touched private runs')
    for name in ('find_existing_run','create_run','read_analysis','_run_record'):
        monkeypatch.setattr(f,name,forbidden)
    assert '£6.625bn'in view() and '£2.256bn'in view('retail')
    assert not any('lloyds' in x for x in f.permitted_selection_keys())


def test_no_protected_documents_or_pdf_links_are_published():
    for focus,detail in [('group',''),('economics','income'),('economics','capital'),('economics','central'),('retail','')]:
        body=view(focus,detail);assert '.pdf'not in body and 'contract_restriction_found'not in body and 'lloyds_section_2'not in body
    for selection in ('lloyds-q3','lloyds-h1'):
        record,_=source.public_statement_record(selection)
        assert record['primary_content_sha256']is None
        assert all(k not in record for k in ('raw_path','text_path','raw_content'))
        assert record['canonical_mutation']is False


def test_authorised_owner_cut_preserves_all_private_functions_and_rejects_unknown_mutation():
    from tools.research.public_financial_compatibility import validate
    from tools.research.ux_unify_compatibility import ceo_predecessor
    import ast,subprocess
    root=Path(__file__).resolve().parents[1]
    assert validate(root)['ci_comparator_changed'] is False
    path='cios/applications/flora/financial_intelligence/candidate_analytics.py'
    old=ast.parse(subprocess.check_output(['git','show','8be67e3d49ad17886c1cc14da3c646271b21017e:'+path],cwd=root))
    new=ast.parse((root/path).read_bytes())
    functions=lambda tree:{n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,ast.FunctionDef)}
    a,b=functions(old),functions(new)
    # Only three public arithmetic/projection functions evolve. The entire
    # private-run service, ACL/resource access and persistence remain exact.
    assert all(a[k]==b[k] for k in a if k not in {'calculate','reconcile','public_factual_projection'})
    raw=(root/path).read_bytes()+b'\n# unreviewed private-owner mutation\n'
    assert ceo_predecessor(root,path,raw)==raw


def test_source_catalogue_rejects_a_changed_issuer_even_with_resealed_numbers(records):
    def change(s):
        s['publisher']=s['document_identity']['publisher']='Lloyds Bank PLC'
    edit(records,'PFI-Lloyds-Q326.json',change)
    assert ps.economic_projection('lloyds-q3')=={}
    assert ps.economic_projection('lloyds-h1')['lines']


@pytest.mark.parametrize('flag',['withdrawn','revoked','owner_only','stale','superseded','contradictory'])
def test_existing_document_source_denial_cannot_be_bypassed_by_numeric_representation(records,flag):
    path=records.parent/'Assessment-Overlay.json';data=json.loads(path.read_text())
    next(s for s in data['sources']if s['id']=='PR-LBG-Q326')[flag]=True
    path.write_text(json.dumps(data))
    assert ps.economic_projection('lloyds-q3')=={}
    assert f.public_factual_projection()=={}
    assert ps.economic_projection('lloyds-h1')['lines']
    assert '£11.084bn'not in view() and '£2.256bn'in view('retail')


def test_existing_source_identity_change_does_not_leave_an_unbound_snapshot_visible(records):
    path=records.parent/'Assessment-Overlay.json';data=json.loads(path.read_text())
    next(s for s in data['sources']if s['id']=='PR-LBG-Q326')['url']='https://www.lloydsbankinggroup.com/other.pdf'
    path.write_text(json.dumps(data))
    assert ps.economic_projection('lloyds-q3')=={} and f.public_factual_projection()=={}
