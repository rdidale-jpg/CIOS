"""Executive comprehension, existing ownership, interactions and source lifecycle."""
from copy import deepcopy
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import ast,subprocess
import pytest
from cios.applications.flora import lloyds_gold as g,visual_streams as v
from cios.applications.flora.financial_intelligence.candidate_analytics import public_factual_projection
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_living_enterprise_preview import http

pytestmark=pytest.mark.real_security_boundary
ROOT=Path(__file__).resolve().parents[1]
BASE='3d9bdb84e64908a3a99dea1f857fecb57b835b88'


def view(stream='landscape',focus='group',detail=''):
    html=g.render({'stream':[stream],'focus':[focus],'detail':[detail]},canonical=True)
    return html.split('<main ',1)[1].split('</main>',1)[0]


class Links(HTMLParser):
    def __init__(self,html):super().__init__();self.links=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.links.append(dict(attrs))


def test_three_first_views_have_different_connected_business_compositions():
    economy=view();operating=view('inside','operations');strategy=view('forces','markets')
    assert 'ce-economy' in economy and 'ce-operating' in operating and 'ce-strategy' in strategy
    assert 'ce-connections' in economy and 'ce-connections' in operating and 'ce-connections' in strategy
    assert 'gold-economic-map' not in economy and 'canvas-operating-band' not in operating and 'v2-choice-map' not in strategy
    assert 'not financial shares' in economy and 'not reporting lines' in operating
    assert 'not proven causes' in strategy and 'ranked Material Pressures' in strategy
    assert '£502.8bn' in economy and '£6.6bn' in economy
    assert all(name in economy for name in ('Retail','Commercial Banking','Insurance, Pensions &amp; Investments'))
    assert all(name in operating for name in ('Lending &amp; credit','Data &amp; AI','Envoy in fraud operations','Microsoft in colleague work'))
    assert all(year in strategy for year in ('2026','2027','2030'))


@pytest.mark.parametrize('focus,terms',[
 ('retail',('asset-finance','depreciation','MBNA','Tusker','matched income')),
 ('commercial',('capital capacity','Amanda Murphy','John Langley','working-capital')),
 ('retirement',('long-duration','Scottish Widows','Lloyds Wealth','banking net-interest-margin')),
])
def test_business_selection_has_differentiated_economics_and_actual_context(focus,terms):
    body=unescape(view(focus=focus))
    assert all(term in body for term in terms)
    assert 'Commercial investigation' in body and 'No measured profit split' in body
    assert ('v3-commercial-system' if focus=='commercial' else 'ce-business-portrait') in body


@pytest.mark.parametrize('detail',('funding','income','costs','capital'))
def test_financial_detail_keeps_actuals_periods_and_unmeasured_mechanisms_separate(detail, monkeypatch):
    monkeypatch.setattr(g.lloyds_financials.public_statements, 'statement_series', lambda subject: ())
    body=view(focus='economics',detail=detail)
    assert 'ce-capital' in body and '£6.6bn' in body and 'Nine months to 30 September 2026' in body
    assert 'No area, line width or connector measures an allocation' in body
    assert 'Executive decision' in body
    assert all(held not in body for held in ('£11.084bn','3.21%','£477.5bn','£1,252m','.pdf'))
    assert public_factual_projection()=={}
    if detail=='funding':assert '£6.3bn' in body and 'organic inflow' in body and 'funding-price' in body
    if detail=='capital':assert 'Funding is not capital' in body and 'risk-weighted' in body and 'Current capital ratios' in body
    if detail=='costs':assert 'Gross savings are not realised net profit' in body


@pytest.mark.parametrize('key',tuple(g.JOURNEYS))
def test_activity_selection_connects_real_context_capabilities_and_commercial_question(key):
    body=view('inside','operations','journey-'+key)
    if key=='service':
        assert 'detail=service' in body and 'Customer operations' in body
        return
    for text in ('Conceptual activity sequence','Lloyds context','Economic and operational significance','Capabilities behind the activity','Dependencies and counter-evidence','Commercial investigation'):
        assert text in body
    assert 'verified process ownership or purchase mandates' in body
    assert 'no verified application, role or supplier dependency is inferred' in body.lower()
    assert 'ce-activity-thread' in body
    links=Links(body).links
    assert all(public_request_target(a['href'].split('#')[0]) for a in links if a.get('href','').startswith('/'))


@pytest.mark.parametrize('source,removed,routes',[
 ('LGV2-LEADERS','William Chalmers',[('inside','people','leader-chalmers'),('inside','operations','journey-finance'),('landscape','economics','capital')]),
 ('LGV2-BRANDS','Lex Autolease',[('landscape','retail',''),('landscape','group','brands')]),
 ('LGV2-FRAUD','Tom Martin',[('inside','operations','journey-risk'),('inside','capabilities','risk'),('inside','applications','fraud')]),
 ('LGV2-FRONTIER','40,000',[('inside','operations','journey-platforms'),('inside','applications','frontier')]),
 ('LGV2-TRANSACTIONS','Natasha Condon',[('inside','operations','journey-payments'),('landscape','commercial','transactions')]),
])
@pytest.mark.parametrize('flag',('withdrawn','revoked','owner_only','stale','superseded','contradictory'))
def test_withdrawal_removes_source_dependent_detail_and_retains_unrelated_funding(monkeypatch,source,removed,routes,flag):
    data=deepcopy(v.current_data(v.Context('lloyds','inside')))
    next(s for s in data['sources'] if s['id']==source)[flag]=True
    monkeypatch.setattr(v,'current_data',lambda _:data)
    for route in routes:assert removed not in view(*route)
    assert '£502.8bn' in view()


@pytest.mark.parametrize('flag',('withdrawn','revoked','owner_only','stale','superseded','contradictory'))
def test_financial_withdrawal_removes_all_new_visual_and_accessible_financial_values(monkeypatch,flag):
    data=deepcopy(v.current_data(v.Context('lloyds','landscape')))
    next(s for s in data['sources'] if s['id']=='PR-LBG-Q326')[flag]=True
    monkeypatch.setattr(v,'current_data',lambda _:data)
    for route in [('landscape','group',''),('landscape','economics','capital'),('landscape','economics','funding'),('forces','markets','')]:
        body=view(*route)
        assert all(value not in body for value in ('£502.8bn','£6.6bn','£6.3bn'))
    assert '£496.5bn' in view(focus='economics',detail='funding')


@pytest.mark.parametrize('scope,focus,detail',[
 ('landscape','group',''),('landscape','economics','capital'),('inside','operations',''),
 ('inside','operations','journey-data'),('inside','capabilities','technology'),('forces','markets',''),
])
def test_public_routes_keep_private_financial_and_foreign_workspace_access_closed(http,scope,focus,detail):
    path=g.CANONICAL+'?stream='+scope+'&focus='+focus+'&detail='+detail
    assert http(path)[0]==200
    for extra in ('&workspace=foreign','&analysis=fi-private'):assert http(path+extra)[0]==403
    assert http(path,'POST')[0]==403


def test_only_presentation_changes_and_no_research_or_protected_owner_evolution():
    from tests.flora_lloyds_research_contract import preserved_research_cut
    preserved_research_cut()
    paths=('architecture/decisions','cios/applications/flora/security_store.py',
      'cios/applications/flora/security_web.py','cios/applications/flora/public_routes.py',
      'cios/applications/flora/visual_streams.py','cios/applications/flora/research_intelligence/source_import.py',
      'cios/applications/flora/financial_intelligence','cios/applications/flora/blueprint_import',
      'tools/ci/flora-baseline-v1.json','tools/ci/flora_ci.py')
    from tests.test_flora_lloyds_financials import assert_only_public_financial_changes
    assert_only_public_financial_changes(ROOT, BASE, paths)
    before=ast.parse(subprocess.check_output(['git','show',BASE+':cios/applications/flora/lloyds_gold.py'],cwd=ROOT));after=ast.parse((ROOT/'cios/applications/flora/lloyds_gold.py').read_text())
    functions=lambda tree:{n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,ast.FunctionDef)}
    old,new=functions(before),functions(after)
    # v3 deliberately evolves cross-perspective URL selection; Source, IAM
    # resolution, rendering ownership and the remaining protected functions stay fixed.
    assert all(old[k]==new[k] for k in ('facts_for','executive_facts','reported','interpretation','scene','resolve','render','stylesheet'))
    assert public_factual_projection()=={}


def test_corrected_typed_presenter_inputs_do_not_leave_hardcoded_old_numbers():
    # Isolated presenter input, not a substituted issuer fact or publication.
    from dataclasses import replace
    from decimal import Decimal
    facts=g.executive_facts(v.current_data(v.Context('lloyds','landscape')),g.facts_for(v.current_data(v.Context('lloyds','landscape'))))
    facts['LBG-Q326-PROFIT']=replace(facts['LBG-Q326-PROFIT'],value=Decimal('6.7'))
    facts['LBG-Q326-DEPOSITS']=replace(facts['LBG-Q326-DEPOSITS'],value=Decimal('503.1'))
    for body in (g.experience_landscape(g.State(route=g.CANONICAL),facts,()),g.experience_forces(g.State('forces','markets','markets',route=g.CANONICAL),facts)):
        assert '£6.7bn' in body and '£503.1bn' in body
        assert '£6.6bn' not in body and '£502.8bn' not in body


def test_withdrawn_operating_example_does_not_survive_as_secondary_fact(monkeypatch):
    data=deepcopy(v.current_data(v.Context('lloyds','inside')))
    next(s for s in data['sources'] if s['id']=='LGV2-FRAUD')['withdrawn']=True
    monkeypatch.setattr(v,'current_data',lambda _:data)
    assert 'Envoy in fraud operations' not in view('inside','operations')
    for route in [('inside','operations','journey-data'),('inside','operations','journey-risk'),('inside','capabilities','data')]:
        body=view(*route)
        assert 'A real Envoy workflow combines' not in body and 'The disclosed fraud workflow retains' not in body
        assert 'Tom Martin' not in body
