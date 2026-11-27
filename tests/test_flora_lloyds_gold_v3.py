"""v3 connects existing public intelligence without changing any owning service."""
import ast,subprocess
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import pytest
from cios.applications.flora import lloyds_gold as g,visual_streams as v
from cios.applications.flora.financial_intelligence.candidate_analytics import public_factual_projection
from tests.test_flora_living_enterprise_preview import http

BASE='08763fca342fcaf67c37f261948d8a8c9642d2c3'
ROOT=Path(__file__).resolve().parents[1]
pytestmark=pytest.mark.real_security_boundary


def facts():
    data=v.current_data(v.Context('lloyds','landscape'))
    return g.executive_facts(data,g.facts_for(data))


def page(stream,focus,detail='',subject=None):
    return g.render({'stream':[stream],'focus':[focus],'detail':[detail],'subject':[subject or focus]},canonical=True).split('<main ',1)[1].split('</main>',1)[0]


PAIRS=[(key,start,end) for key,title,views in g.V3_PATHS for start in views for end in views if start!=end]
@pytest.mark.parametrize('key,start,end',PAIRS)
def test_every_connected_subject_has_reversible_finite_public_urls(key,start,end):
    subject='commercial' if key in {'commercial','transactions'} else 'retail'
    state=g.State(start[0],start[1],subject,start[2],g.CANONICAL)
    dest=g.href(state,stream=end[0]);query=parse_qs(urlsplit(dest).query,keep_blank_values=True)
    resolved=g.resolve(query)
    assert (resolved.stream,resolved.focus,resolved.detail)==end
    assert resolved.subject==subject
    assert urlsplit(dest).path==g.CANONICAL
    back=g.resolve(parse_qs(urlsplit(g.href(resolved,stream=start[0])).query,keep_blank_values=True))
    assert (back.stream,back.focus,back.detail)==start
    assert back.subject==subject


def test_general_group_payments_are_not_silently_promoted_to_cib():
    state=g.State('inside','operations','operations','journey-payments',g.CANONICAL)
    q=parse_qs(urlsplit(g.href(state,stream='forces')).query,keep_blank_values=True)
    assert q['detail']==[''] and q['focus']==['markets']
    assert g.connected_path(state) is None
    assert 'No Group wallet/Curve initiative' in page('inside','operations','commercial-context','commercial')


@pytest.mark.parametrize('field,value',[('scope','Lloyds Bank PLC'),('period','FY2026'),('unit','GBP billion'),('basis','underlying annual profit'),('measurement_state','target'),('value',Decimal('500')),('value',Decimal('-50')),('value',Decimal('NaN'))])
def test_financial_graph_rejects_wrong_scope_period_unit_basis_or_disclosure_binding(field,value):
    items=facts();items['LBG-AI26-REPORTED']=replace(items['LBG-AI26-REPORTED'],**{field:value})
    body=g.v3_ai_horizons(g.State(),items)
    assert 'data-claim-id="LBG-AI26-REPORTED"' not in body
    assert 'data-claim-id="LBG-AI26-EXPECTED"' in body


def test_corrected_existing_typed_value_changes_graph_without_old_number_or_new_recipe():
    items=facts();old=items['LBG-AI26-REPORTED'];sources=tuple(replace(s,quote=s.quote.replace('50','60')) for s in old.sources)
    items['LBG-AI26-REPORTED']=replace(old,value=Decimal('60'),text=old.text.replace('50','60'),sources=sources)
    body=g.v3_ai_horizons(g.State(),items)
    assert 'About £60m' in body and 'About £50m' not in body
    assert 'No growth rate' in body and 'More than £100m' in body


def test_actual_expectation_and_target_never_become_progress_or_divisional_return():
    body=page('landscape','economics','ai-value')
    assert 'About £50m' in body and 'More than £100m' in body
    assert 'data-measurement-state="expectation"' in body and 'FY2025' in body
    assert 'not a measured accounting bridge' in body
    assert 'no Group amount is attributed to Envoy, Copilot, CIB or a supplier' in body
    assert all(x not in body for x in ('100% achieved','50% delivered','£11.084bn','3.21%','£477.5bn','.pdf'))
    targets=page('landscape','group')
    assert 'Below 45%' in targets and 'About £2bn' in targets and 'Management target' in targets
    assert len(public_factual_projection()['facts']) == 3


@pytest.mark.parametrize('flag',('withdrawn','revoked','owner_only','stale','superseded','contradictory'))
@pytest.mark.parametrize('source,removed,states',[
 ('PR-LBG-AI26',('About £50m','More than £100m','Contribution is disclosed'),(('landscape','economics','ai-value'),('forces','markets',''))),
 ('LGV2-TRANSACTIONS',('Natasha Condon','18 November 2026','leadership is a real change'),(('landscape','commercial',''),('inside','operations','commercial-context'),('forces','competition','commercial-direction'))),
 ('LGV2-LEADERS',('William Chalmers','Ron van Kemenade','Sharon Doherty'),(('inside','operations',''),('inside','people','leader-chalmers'))),
 ('PR-LBG-Q326',('£6.6bn','£502.8bn','acquisition is reported complete'),(('landscape','group',''),('landscape','economics','customer-value'))),
 ('LGV2-FRONTIER',('40,000','97%','10,000'),(('inside','people','workforce'),)),
])
def test_withdrawal_removes_new_ordinary_hidden_and_derived_content(monkeypatch,source,removed,states,flag):
    data=deepcopy(v.current_data(v.Context('lloyds','landscape')))
    next(s for s in data['sources'] if s['id']==source)[flag]=True
    monkeypatch.setattr(v,'current_data',lambda _:data)
    for stream,focus,detail in states:
        body=page(stream,focus,detail,'commercial' if source=='LGV2-TRANSACTIONS' else None)
        assert all(word not in body for word in removed)
    if source!='PR-LBG-Q326':assert '£502.8bn' in page('landscape','group')


def test_real_reporting_edge_is_not_a_synthetic_organisation_or_supplier_contract():
    body=page('landscape','commercial')
    assert 'Natasha Condon' in body and 'John Langley' in body and 'Reports to' in body
    assert 'Business &amp; Commercial Banking' in body and 'Amanda Murphy' in body
    assert 'No measured profit split' in body
    assert 'Microsoft deployment or Google collaboration is assigned to CIB' in body
    assert body.count('aria-label="Transaction Banking"')==1
    force=page('forces','competition','transaction-direction','commercial')
    assert '18 November 2026' in force and 'decision already taken' in force
    assert 'do not establish CIB allocation' in force


@pytest.mark.parametrize('stream,focus,detail',[(a,b,c) for _,_,views in g.V3_PATHS for a,b,c in views])
def test_new_states_keep_post_private_selector_and_cross_tenant_denials(http,stream,focus,detail):
    route=g.CANONICAL+'?stream='+stream+'&focus='+focus+'&detail='+detail+'&subject=commercial'
    assert http(route)[0]==200
    assert http(route,'POST')[0]==403
    for private in ('&workspace=other','&analysis=fi-private','&source=owner-only','&topic=arbitrary'):
        assert http(route+private)[0] in {403,404}


def test_owners_research_original_images_and_comparator_are_byte_preserved():
    from tests.flora_lloyds_research_contract import preserved_research_cut
    preserved_research_cut()
    paths=('architecture/decisions','cios/applications/flora/security_store.py','cios/applications/flora/security_web.py','cios/applications/flora/supabase_identity.py','cios/applications/flora/public_routes.py','cios/applications/flora/visual_streams.py','cios/applications/flora/blueprint_import','tools/ci/flora_ci.py','tools/ci/flora-baseline-v1.json')
    assert not subprocess.check_output(['git','diff','--name-only',BASE,'--',*paths],cwd=ROOT)
    from tools.research.public_financial_compatibility import validate
    assert validate(ROOT)['ci_comparator_changed'] is False
    old=ast.parse(subprocess.check_output(['git','show',BASE+':cios/applications/flora/lloyds_gold.py'],cwd=ROOT));new=ast.parse((ROOT/'cios/applications/flora/lloyds_gold.py').read_text())
    funcs=lambda t:{n.name:ast.dump(n,include_attributes=False) for n in t.body if isinstance(n,ast.FunctionDef)}
    a,b=funcs(old),funcs(new)
    assert all(a[k]==b[k] for k in ('facts_for','executive_facts','reported','interpretation','scene','resolve','canonical_query','render','stylesheet'))
    assert len(public_factual_projection()['facts']) == 3
