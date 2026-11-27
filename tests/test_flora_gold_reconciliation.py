"""Gold reconciliation is a view over existing owners, not a qualification engine."""
from copy import deepcopy
from pathlib import Path
import csv,json,subprocess

import pytest
from cios.applications.flora import lloyds_gold as g, visual_streams as v
from cios.applications.flora.financial_intelligence import candidate_analytics as financial
from tests.test_flora_rud1_648 import retained as rud_retained, mutate
from tests.test_flora_living_enterprise_preview import http

pytestmark=pytest.mark.real_security_boundary
ROOT=Path(__file__).resolve().parents[1]


def main(stream='inside',focus='operations',detail='service'):
    return g.render({'stream':[stream],'focus':[focus],'detail':[detail]},canonical=True).split('<main ',1)[1].split('</main>',1)[0]


def test_service_has_one_operating_home_and_contextual_economics_links():
    service=main()
    assert '115,687' in service and '66.12%' in service and '118,861' in service
    assert 'Customer operations' in main(detail='')
    for detail in ('','costs','service-workload','service-bankcards','service-mortgages'):
        body=main('landscape','economics',detail)
        assert '115,687' not in body and '97.4%' not in body
        assert 'stream=inside' in body and 'focus=operations' in body and 'detail=service#' in body
    assert 'data-intelligence="service-recovery"' not in main('landscape','group','')


@pytest.mark.parametrize('key,rate,share',[('bankcards','66.37%','97.4%'),('mortgages','62.57%','2.3%'),('insurance','11.42%','0.3%')])
def test_product_depth_distinguishes_observation_explanation_consequence_and_response(key,rate,share):
    body=main(detail='service-'+key)
    for text in (rate,share,'Activity, outcome and consequence','Possible explanations','Hypotheses.',
                 'Management response','does not identify a complaints-specific remedy','Commercial investigation',
                 'not the financial or customer impact','not the share of customers harmed'):
        assert text in body
    assert 'Financial loss' not in body and 'CEO hot button' not in body
    inspect=main(detail='sources')
    assert '115798 / 118861 × 100' in inspect and 'closed-case mix' in inspect


@pytest.mark.parametrize('focus',('markets','resilience','competition','strategy','analysis'))
def test_service_volume_is_not_promoted_into_forces_or_a_pressure(focus):
    body=main('forces',focus,'')
    assert all(text not in body for text in ('115,687','97.4%','lloyds-product-workload','FCA-LLOYDS-PRODUCTS-H126'))


def test_ai_group_performance_has_one_primary_home_and_no_computed_progress():
    body=main('forces','strategy','objective-ai')
    assert 'data-claim-id="LBG-AI26-REPORTED"' in body and 'data-claim-id="LBG-AI26-EXPECTED"' in body
    assert 'FY2025' in body and '2026' in body and 'Management response already in place' in body
    assert 'data-semantic-type="calculated"' not in body
    assert 'No amount is attributed to Envoy' in body
    platform=main('inside','applications','envoy-value')
    assert 'data-claim-id="LBG-AI26-REPORTED"' not in platform
    assert 'detail=objective-ai' in platform and 'not an attributed financial result' in platform
    assert '30,000' not in platform  # Colleague licences have their own home.


@pytest.mark.parametrize('source_id',('PR-LBG-AI26','PR-LBG-ENVOY'))
def test_ai_source_withdrawal_is_precise_and_preserves_independent_evidence(monkeypatch,source_id):
    data=deepcopy(v.current_data(v.Context('lloyds','inside')))
    next(s for s in data['sources'] if s['id']==source_id)['withdrawn']=True
    monkeypatch.setattr(v,'current_data',lambda ctx:data)
    body=main('forces','strategy','objective-ai')
    if source_id=='PR-LBG-AI26':
        assert 'data-claim-id="LBG-AI26-REPORTED"' not in body and 'data-claim-id="LBG-AI26-EXPECTED"' not in body
        assert 'Envoy' in main('inside','applications','envoy')
    else:
        assert 'data-claim-id="LBG-AI26-REPORTED"' in body
        assert 'Management response already in place' not in body


def test_workforce_uses_scoped_signals_not_empty_tables_or_licence_proxy():
    body=main('inside','people','workforce')
    assert 'Licences are not people' in body and '<table' not in body
    assert '30,000' not in body and '30000' not in body and 'detail=copilot' in body
    assert 'rules out related role reductions' in body and 'Group-wide workforce growth' in body
    assert '30,000' in main('inside','applications','copilot')


@pytest.mark.parametrize('flag',('withdrawn','revoked','owner_only','superseded','stale','contradictory'))
def test_source_withdrawal_removes_all_new_service_depth_and_yields_meaningful_absence(rud_retained,flag):
    path=rud_retained.with_name('FCA-Lloyds-Products-H126.json')
    mutate(path,lambda d:d['sources'][0].__setitem__(flag,True))
    for detail in ('service-bankcards','service-mortgages'):
        body=main(detail=detail)
        assert 'cannot be shown for this selection' in body
        assert all(s not in body for s in ('115,687','97.4%','case types recur','closed-case mix'))
    assert '£502.8bn' in main('landscape','economics','funding')


@pytest.mark.parametrize('detail',('service','service-bankcards','service-mortgages','service-insurance'))
def test_new_home_is_public_but_private_selectors_remain_denied(http,detail):
    path='/enterprises/lloyds?stream=inside&focus=operations&detail='+detail
    status,headers,body=http(path)
    assert status==200 and '115,687' in body and 'no-store' in headers.get('Cache-Control','')
    assert http(path+'&workspace=foreign')[0]==403
    assert http(path+'&analysis=fi-private')[0]==403


def test_no_research_or_protected_owner_changes_and_no_held_financial_activation():
    assert financial.public_factual_projection()=={}
    protected=('enterprise-knowledge','cios/applications/flora/security_store.py','cios/applications/flora/security_web.py',
               'cios/applications/flora/research_intelligence/source_import.py','cios/applications/flora/financial_intelligence',
               'cios/applications/flora/blueprint_import/material_pressure.py')
    assert subprocess.check_output(['git','diff','--name-only','7f003982088b6f71fc2e365f3663b7beb3772d21','--',*protected],cwd=ROOT,text=True)==''
    for path in ('cios/applications/flora/lloyds_gold.py',):
        import ast
        old=ast.parse(subprocess.check_output(['git','show','7f003982:'+path],cwd=ROOT));new=ast.parse((ROOT/path).read_text())
        funcs=lambda tree:{n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,ast.FunctionDef)}
        a,b=funcs(old),funcs(new)
        assert all(a[k]==b[k] for k in ('facts_for','scene','resolve','href','render'))


def test_assessment_is_complete_as_a_view_without_scores_or_new_truth():
    path=ROOT/'docs/flora-runtime/enterprise-gold-reconciliation/Lloyds-Assessment.csv'
    rows=list(csv.DictReader(path.open()));assert len(rows)==18
    allowed={'Evidenced','Partial','Unknown','Contradictory','Restricted','Not Applicable'}
    assert {r['perspective'] for r in rows}=={'Landscape','Inside','Forces'}
    for r in rows:
        assert r['evidence_state'] in allowed and r['overall_state'] in allowed
        assert all(r[k] for k in ('available_evidence','primary_home','evidence_ids_and_version','missing_or_restricted','specific_improvement'))
        assert all((ROOT/p.strip()).is_file() for p in r['source_paths'].split(';'))
    assert 'score' not in rows[0] and 'completeness_percentage' not in rows[0]


@pytest.mark.parametrize('mutation',('none','command','permissions','extra_path','previous_cut'))
def test_legacy_workflow_retirement_compatibility_is_exact_and_rejects_other_changes(tmp_path,mutation):
    from tests.flora_f2_owner_contract import assert_owner_compatible
    path='.github/workflows/flora-validation.yml'
    previous=subprocess.check_output(['git','show','6b10935:'+path],cwd=ROOT)
    actual=(ROOT/path).read_bytes()
    if mutation=='command':actual=actual.replace(b'python tools/ci/flora_ci.py',b'echo skipped')
    elif mutation=='permissions':actual=actual.replace(b'contents: read',b'contents: write')
    elif mutation=='extra_path':actual=actual.replace(b"      - 'tests/**'\n",b'')
    elif mutation=='previous_cut':previous+=b'\n'
    target=tmp_path/path;target.parent.mkdir(parents=True);target.write_bytes(actual)
    if mutation=='none':assert_owner_compatible(tmp_path,path,previous)
    else:
        with pytest.raises(AssertionError):assert_owner_compatible(tmp_path,path,previous)
