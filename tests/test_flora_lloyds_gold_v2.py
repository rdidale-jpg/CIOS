"""Whole-enterprise depth over the original Source, research and presentation owners."""
from copy import deepcopy
from pathlib import Path
import json,subprocess
import pytest
from cios.applications.flora import lloyds_gold as g,visual_streams as v,leadership_agenda as a
from cios.applications.flora.research_intelligence import model
from cios.applications.flora.financial_intelligence import candidate_analytics
from tests.test_flora_living_enterprise_preview import http

pytestmark=pytest.mark.real_security_boundary
ROOT=Path(__file__).resolve().parents[1]
BASE='1c8c8ae17bb2af3c95bf264d7df9befb60b0b576'


def view(stream='landscape',focus='group',detail=''):
    return g.render({'stream':[stream],'focus':[focus],'detail':[detail]},canonical=True).split('<main ',1)[1].split('</main>',1)[0]


def test_original_research_and_permissions_are_preserved_with_only_additive_claims():
    path='enterprise-knowledge/banking/research-model/Assessment-Overlay.json'
    old=json.loads(subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT));new=model.load_assessment()
    for key in old:
        if key in ('sources','claims'):
            byid={r['id']:r for r in new[key]}
            assert all(byid[r['id']]==r for r in old[key])
        elif key!='assessed_at':assert new[key]==old[key]
    assert len(new['claims'])-len(old['claims'])==39
    assert len(new['sources'])-len(old['sources'])==7
    protected=('architecture/decisions','cios/applications/flora/security_store.py','cios/applications/flora/security_web.py','cios/applications/flora/research_intelligence/source_import.py','cios/applications/flora/financial_intelligence','cios/applications/flora/blueprint_import','tools/ci/flora-baseline-v1.json','tools/ci/flora_ci.py')
    assert not subprocess.check_output(['git','diff','--name-only',BASE,'--',*protected],cwd=ROOT,text=True)
    assert candidate_analytics.public_factual_projection()=={}


def test_whole_group_arrival_and_distinct_business_models():
    body=view();assert 'Group overview' in body and 'One Group, different economic engines' in body
    assert '28 million' in body and 'Leadership’s agenda' in body and '£502.8bn' in body and '£6.6bn' in body
    assert '115,687' not in body and '97.4%' not in body
    assert 'BCB' not in body  # No unexplained acronym-first overview.
    commercial=view(focus='commercial')
    assert 'Business &amp; Commercial Banking' in commercial and 'Corporate &amp; Institutional Banking' in commercial
    assert 'Amanda Murphy' in commercial and 'John Langley' in commercial
    assert 'Cash timing is the customer problem' not in commercial
    assert 'Natasha Condon' in view(focus='commercial',detail='transactions')
    insurance=view(focus='retirement');assert 'Scottish Widows' in insurance and 'Insurance and investment return' in insurance


def test_brands_are_not_legal_or_segment_allocations():
    body=view(detail='brands')
    for name in ('Lloyds Bank','Bank of Scotland','Scottish Widows','MBNA','Black Horse','Lex Autolease','Tusker'):assert name in body
    assert 'SC095000' in body and 'not necessarily a legal entity' in body
    assert 'not a legal ownership or exclusive segment allocation' in body


def test_thirteen_roles_are_scoped_membership_and_only_one_real_reporting_line():
    body=view('inside','people','leadership')
    assert all(name in body for _,name,*_ in g.V2_LEADERS)
    assert len(g.V2_LEADERS)==13 and 'reporting lines not inferred' in body
    assert 'Natasha Condon will report to John Langley' in body
    assert 'no verified purchase mandate' not in body  # Detail, not repetitive default notices.
    detail=view('inside','people','leader-chalmers')
    assert 'William Chalmers is listed' in detail and 'not a verified purchase mandate' in detail


def test_people_populations_and_dates_are_not_summed_or_mistaken_for_workforce_cost():
    body=view('inside','people','workforce')
    assert 'more than 60,000 colleagues' in body and 'undated' in body
    assert '65,000' in body and 'not reconciled' in body
    assert 'more than 1,000 AI-related roles' in body and 'not net hires' in body
    assert 'more than 700 colleagues' in body and 'course' in body
    assert '<table' not in body and 'Licences are not people' in body
    assert 'No workforce reduction, net hiring, FTE distribution, salary cost or productivity saving is calculated' in body


def test_real_technology_and_supplier_context_preserves_actual_target_and_contract_limits():
    body=view('inside','applications','frontier')
    assert '40,000' in body and '97%' in body and 'over 10,000' in body
    assert 'multi-year agreement' in body and 'not total technology headcount' in body
    assert 'independent service improvement or net economic return' in body
    suppliers=view('inside','partners');assert 'Microsoft agreement' in suppliers and 'price and expiry not disclosed' in suppliers
    fraud=view('inside','applications','fraud');assert 'Envoy-built' in fraud and 'override AI suggestions' in fraud and 'Tom Martin' in fraud
    assert '£1 billion' not in fraud and '£100 million' not in fraud


@pytest.mark.parametrize('key',('renewal','ai','access','reporting','investment','efficiency','payments'))
def test_each_goal_connects_to_evidence_role_dependencies_risk_and_decision(key):
    body=view('forces','strategy','objective-'+key)
    for text in ('From goal to executive decision','Dependencies to establish','Risks and counter-evidence','Next decision','delegated authority remain hypotheses'):assert text in body
    assert '<table' not in body and 'qualified Material Pressures' in body
    assert 'progress percentage' not in body


def test_forces_is_a_cohesive_agenda_with_distinct_horizons_and_no_claimed_pressures():
    body=view('forces','markets')
    assert 'Executive agenda' in body
    for t in ('2026','2027','2030','Executive choices','AI value beyond deployment','Resilience through change','qualified Material Pressure'):assert t in body
    assert '115,687' not in body and 'data-semantic-type="calculated"' not in body


@pytest.mark.parametrize('flag',('withdrawn','revoked','owner_only','stale','superseded','contradictory'))
@pytest.mark.parametrize('sid,route,removed',[
 ('LGV2-LEADERS',('inside','people','leader-chalmers'),'William Chalmers'),
 ('LGV2-FRONTIER',('inside','applications','frontier'),'40,000'),
 ('LGV2-FRAUD',('inside','applications','fraud'),'Tom Martin'),
 ('LGV2-TRANSACTIONS',('landscape','commercial','transactions'),'Natasha Condon'),
])
def test_new_source_lifecycle_removes_only_dependent_intelligence(monkeypatch,flag,sid,route,removed):
    data=deepcopy(v.current_data(v.Context('lloyds','inside')))
    next(s for s in data['sources'] if s['id']==sid)[flag]=True
    monkeypatch.setattr(v,'current_data',lambda _:data)
    assert removed not in view(*route)
    assert '£502.8bn' in view()


@pytest.mark.parametrize('mutation',('issuer','period','entity','statement','rights','url','published','legal_restriction'))
def test_new_claims_fail_closed_for_wrong_source_identity_or_meaning(monkeypatch,mutation):
    data=deepcopy(v.current_data(v.Context('lloyds','inside')))
    source=next(s for s in data['sources'] if s['id']=='LGV2-FRONTIER');claim=next(c for c in data['claims'] if c['id']=='LBG-V2-MSADOPTION')
    if mutation=='issuer':source['publisher']='Different issuer'
    elif mutation=='period':source['reporting_period']='Different period'
    elif mutation=='entity':claim['entity_scope']='Lloyds Bank PLC'
    elif mutation=='statement':claim['statement']='The bank has a confirmed buying need and budget.'
    elif mutation=='rights':source['rights']['status']='pending'
    elif mutation=='url':source['url']=source['retrieval_url']='https://www.lloydsbankinggroup.com/other.html'
    elif mutation=='published':source['publication_date']='2026-06-05'
    else:source['restrictions']=['public_read_only']
    monkeypatch.setattr(v,'current_data',lambda _:data)
    assert '40,000' not in view('inside','applications','frontier')
    assert '£502.8bn' in view()


def test_old_source_releases_are_not_rewound_before_new_enterprise_facts():
    data=v.current_data(v.Context('lloyds','inside'));assert data['assessed_at']=='2026-11-27'
    public=a._public_data(data);assert public['assessed_at']==data['assessed_at']
    assert any(c['id']=='LBG-FCA-H126-RECEIVED' for c in public['claims'])
    service=a._eai_bank_data(public,'service');assert service['assessed_at']==data['assessed_at']
    assert any(c['id']=='EAI-LBG-CLOSED' for c in service['claims'])
    model.validate(service)
    assert '115,687' in view('inside','operations','service-bankcards')


@pytest.mark.parametrize('route',('?focus=group&detail=brands','?stream=inside&focus=people&detail=leader-chalmers','?stream=inside&focus=applications&detail=frontier','?stream=inside&focus=applications&detail=fraud'))
def test_public_views_do_not_admit_private_workspace_financial_or_post_actions(http,route):
    path='/enterprises/lloyds'+route
    assert http(path)[0]==200
    for suffix in ('&workspace=foreign','&analysis=fi-private'):assert http(path+suffix)[0]==403
    assert http(path+'&selected=natwest')[0]==404
    assert http(path,'POST')[0]==403


@pytest.mark.parametrize('flag',('withdrawn','revoked','owner_only','stale','superseded','contradictory'))
def test_optional_public_research_inspection_cannot_revive_withdrawn_new_facts(flag):
    from cios.applications.flora.research_intelligence import views
    data=deepcopy(v.current_data(v.Context('lloyds','inside')))
    next(s for s in data['sources'] if s['id']=='LGV2-LEADERS')[flag]=True
    with pytest.raises(ValueError):views.evidence_page('LBG-V2-CHALMERS',data=data)
    assert 'William Chalmers' not in views.claims_html(data,['LBG-V2-CHALMERS'])
    assert 'Charlie Nunn' not in views.node_page('BK-ENT-001',data=data).split('Supporting research statements',1)[-1].split('Connected capabilities',1)[0]


@pytest.mark.parametrize('change',('material_exception','pending_rights','changed_document'))
def test_internal_inspection_honours_source_owned_legal_and_identity_exceptions(change):
    from cios.applications.flora.research_intelligence import views
    data=deepcopy(v.current_data(v.Context('lloyds','inside')))
    source=next(s for s in data['sources'] if s['id']=='LGV2-FRONTIER')
    if change=='material_exception':source['rights']['material_exceptions']=['Publication use withheld']
    elif change=='pending_rights':source['rights']['status']='pending'
    else:source['title']='Different document'
    with pytest.raises(ValueError):views.evidence_page('LBG-V2-MSADOPTION',data=data)
    assert '40,000' not in views.claims_html(data,['LBG-V2-MSADOPTION'])


def test_historical_owner_compatibility_rejects_unknown_changes():
    from tools.research.ux_unify_compatibility import ceo_predecessor
    for path in ('cios/applications/flora/intelligence_presentation.py','cios/applications/flora/leadership_agenda.py','cios/applications/flora/research_intelligence/views.py'):
        raw=(ROOT/path).read_bytes()
        assert ceo_predecessor(ROOT,path,raw)!=raw
        unknown=raw+b'\n# Unreviewed mutation\n'
        assert ceo_predecessor(ROOT,path,unknown)==unknown
