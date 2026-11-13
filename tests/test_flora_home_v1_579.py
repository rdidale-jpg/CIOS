"""Home design preview: scope, real authority, provenance and native navigation."""
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
import json
from urllib.parse import urlencode

import pytest
from cios.applications.flora import home_v1 as home
from cios.applications.flora.storage import data_path
from cios.applications.flora.commercial_mission import save_commercial_mission
from tests.test_flora_offers_v1 import authority, actor, pilot, draft, approved
from tests.test_flora_sales_pipeline import web

pytestmark = pytest.mark.real_security_boundary


class DOM(HTMLParser):
    def __init__(self, html): super().__init__(); self.nodes=[]; self.feed(html)
    def handle_starttag(self, tag, attrs): self.nodes.append((tag,dict(attrs)))


@pytest.mark.parametrize('market', ['GB', 'FR'])
def test_public_and_selected_market_are_explicit_and_not_security_context(web, market):
    status, html, _ = web('/home?' + urlencode({'market':market}), authenticated=False)
    assert status == 200 and f'data-market="{market}"' in html
    assert 'Selected market' in html and 'Global forces' in html
    assert 'My Commercial Focus' in html and 'Recommended Sales Plays' in html
    assert 'pilot-seller' not in html and 'Illustrative UK employer' not in html
    assert web.last_headers['Cache-Control'] == 'no-store'


def test_current_canonical_home_is_retained_pending_owner_acceptance(web):
    status, html, _ = web('/', authenticated=False)
    assert status == 200 and 'Home v1 · Design preview' not in html
    assert 'home-world' not in html


def test_three_native_industry_regions_have_initial_text_labels_and_canonical_routes(web):
    status, html, _ = web('/home?market=GB', authenticated=False)
    dom = DOM(html)
    regions = [a for tag,a in dom.nodes if a.get('data-industry')]
    assert status == 200 and len(regions) == 3
    assert {a['href'] for a in regions} == {r[2] for r in home.REGIONS}
    assert all(name in html for _,name,_,_,_ in home.REGIONS)
    assert not any(tag == 'iframe' for tag,_ in dom.nodes)
    assert not any(tag == 'script' and a.get('src','').startswith('/home') for tag,a in dom.nodes)
    assert sum(tag == 'h1' for tag,_ in dom.nodes) == 1


def test_second_country_is_a_layout_test_without_uk_briefing_or_false_local_regions(web):
    status, html, _ = web('/home?market=FR', authenticated=False)
    assert status == 200 and 'Country layout preview' in html and '/home/assets/fr-artwork' in html
    assert 'data-industry=' not in html and 'class="world-change"' not in html
    assert 'data-assessment-id=' not in html and 'Lloyds describes' not in html
    assert 'UK industry library' in html and 'UK enterprise library' in html
    assert 'no local industry briefing' in html


@pytest.mark.parametrize('query', ['market=US', 'market=GB&market=FR', 'market=GB&workspace=foreign',
    'market=GB&user=pilot-seller', 'market=GB&promote=true', 'market=../../security', 'market=', 'lens=legal'])
def test_unknown_ambiguous_or_privileged_home_selectors_fail_closed(web, query):
    assert web('/home?' + query, authenticated=False)[0] in {403,404}


@pytest.mark.parametrize('lens', ['overview', *home.LENSES])
def test_global_pestle_overview_and_all_six_lenses_are_read_only_native_views(web, lens):
    status, html, _ = web('/home/global-forces?' + urlencode({'market':'GB','lens':lens}), authenticated=False)
    assert status == 200 and 'Global PESTLE lenses' in html
    assert 'A wider lens.' in html
    assert all(label in html for label,_ in home.LENSES.values())
    assert 'private_draft' not in html
    if lens == 'economic':
        assert 'No selected signal is presented' in html
        assert 'class="macro-reading"' in html


def test_country_switch_keeps_explicit_macro_lens_and_cites_country_specific_sources(web):
    _, gb, _ = web('/home/global-forces?market=GB&lens=legal', authenticated=False)
    _, fr, _ = web('/home/global-forces?market=FR&lens=legal', authenticated=False)
    assert 'name="lens" value="legal"' in gb and 'name="lens" value="legal"' in fr
    assert 'UK listed-issuer' in gb and 'France: reporting law and transposition differ' in fr
    assert 'UK listed-issuer' not in fr
    assert 'No measured national or enterprise impact is inferred' in fr


def test_global_origin_and_local_exposure_are_not_a_measured_country_claim(web):
    _, html, _ = web('/home/global-forces?market=GB&lens=technological', authenticated=False)
    assert 'Across markets' in html and 'Local exposure to test' in html
    assert 'not a global prevalence estimate' in html
    assert 'Follow the industry and enterprise context' in html


def test_changes_dates_are_original_publication_dates_and_lineage_survives():
    rows = home.changes('GB')
    assert 3 <= len(rows) <= 5
    assert all(row['date'] in {s.get('publication_date') for s in row['sources']} for row in rows)
    assert all(row['lineage'] and row['sources'] for row in rows)
    assert home.changes('FR') == []


def test_retrieval_or_update_time_cannot_manufacture_recent_news(monkeypatch):
    original_assessment = home.load_assessment
    original_macro = home.macro.load_context
    def no_dates(domain):
        value=deepcopy(original_assessment(domain))
        for source in value['sources']:
            source['publication_date']=None;source['retrieved_at']='2026-11-13T12:00:00Z'
        return value
    def no_macro_dates():
        value=deepcopy(original_macro())
        for source in value['sources']:
            source['publication_date']=None;source['retrieved_at']='2026-11-13T12:00:00Z'
        return value
    monkeypatch.setattr(home,'load_assessment',no_dates)
    monkeypatch.setattr(home.macro,'load_context',no_macro_dates)
    assert home.changes('GB') == []


def test_public_and_forged_header_modes_never_enumerate_private_offer_store(monkeypatch):
    def forbidden(*args,**kwargs): raise AssertionError('Private offer enumeration')
    monkeypatch.setattr(home.offers,'snapshot',forbidden)
    for headers in ({},{'X-Flora-User':'pilot-seller','X-Flora-Roles':'cios_owner','X-Flora-Active-Workspace':'synthetic-workspace'}):
        html=home.render('/home',{'market':['GB']},headers)
        assert 'Sign in to personalise' in html and 'data-assessment-id=' not in html


def test_personal_focus_and_recommendations_reuse_authorised_offer_assessments(pilot):
    approved(pilot,'service');approved(pilot,'ai')
    save_commercial_mission(pilot['seller'],{'executive_role':'Seller','commercial_objective':'Validate real fit',
        'priority_accounts':['Lloyds Banking Group'],'geography':['United Kingdom','France'],'commercial_horizon':'2027'})
    html=home.render('/home',{'market':['GB']},pilot['seller'])
    assert 'Illustrative UK employer' in html and 'Seller territory' in html
    assert 'United Kingdom · France' in html and 'Lloyds Banking Group' in html
    ids={a['data-assessment-id'] for tag,a in DOM(html).nodes if a.get('data-assessment-id')}
    matches=home.offers.discover(headers=pilot['seller'])
    assert 1 <= len(ids) <= 3
    assert ids <= {r['assessment_id'] for r in matches}
    assert 'No buying intent or funding established' in html


def test_private_or_unapproved_offers_are_not_home_recommendations(pilot):
    draft(pilot,'service',name='Private candidate only')
    html=home.render('/home',{},pilot['seller'])
    assert 'Private candidate only' not in html and 'data-assessment-id=' not in html
    assert 'Offers available' in html


def test_other_sellers_private_material_never_leaks_to_owner_or_public(pilot):
    save_commercial_mission(pilot['seller'],{'executive_role':'PRIVATE-ROLE','commercial_objective':'PRIVATE-OBJECTIVE',
        'priority_accounts':['PRIVATE-ACCOUNT']})
    draft(pilot,name='PRIVATE-OFFER')
    for headers in ({},pilot['owner'],pilot['reviewer'],pilot['foreign'],pilot['outsider']):
        html=home.render('/home',{},headers)
        for forbidden in ['PRIVATE-ROLE','PRIVATE-OBJECTIVE','PRIVATE-ACCOUNT','PRIVATE-OFFER']:
            assert forbidden not in html


def test_country_change_preserves_employer_authority_and_never_matches_unsupported_market(pilot,monkeypatch):
    approved(pilot)
    save_commercial_mission(pilot['seller'],{'executive_role':'Seller','commercial_objective':'Validate', 'geography':['United Kingdom']})
    before={str(p):p.read_bytes() for p in data_path().rglob('*') if p.is_file() and 'security' not in p.parts}
    selected=home.offers.snapshot(headers=pilot['seller'])['selected']
    def forbidden(*args,**kwargs):raise AssertionError('No France account discovery supported')
    monkeypatch.setattr(home.offers,'discover',forbidden)
    html=home.render('/home',{'market':['FR']},pilot['seller'])
    assert 'Seller territory' in html and 'United Kingdom' in html and 'Illustrative UK employer' in html
    assert 'data-assessment-id=' not in html
    assert home.offers.snapshot(headers=pilot['seller'])['selected']==selected
    after={str(p):p.read_bytes() for p in data_path().rglob('*') if p.is_file() and 'security' not in p.parts}
    assert before==after and not data_path('sales_pipeline','opportunities.json').exists()


def test_revocation_removes_private_focus_and_plays(pilot):
    approved(pilot)
    with pilot['store'].transaction() as db:
        db.execute('UPDATE memberships SET active=0,version=version+1 WHERE user_id=?',('pilot-seller',))
    html=home.render('/home',{},pilot['seller'])
    assert 'Illustrative UK employer' not in html and 'data-assessment-id=' not in html


def test_home_offer_matches_retain_account_access_boundary(pilot):
    approved(pilot)
    with pilot['store'].transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?,version=version+1 WHERE user_id=?',(json.dumps(['AV-ENT-001']),'pilot-seller'))
    html=home.render('/home',{},pilot['seller'])
    matches=[a['data-assessment-id'] for tag,a in DOM(html).nodes if a.get('data-assessment-id')]
    allowed={r['assessment_id'] for r in home.offers.discover(headers=pilot['seller']) if r['enterprise_slug']=='easyjet'}
    assert matches and set(matches)<=allowed


def test_private_profile_values_are_escaped(pilot):
    save_commercial_mission(pilot['seller'],{'executive_role':'Seller','commercial_objective':'Validate',
        'priority_accounts':['<script>alert(1)</script>']})
    html=home.render('/home',{},pilot['seller'])
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html and '<script>alert(1)</script>' not in html


def test_home_and_country_selection_make_no_domain_or_pipeline_writes(pilot,web):
    before={str(p):p.read_bytes() for p in data_path().rglob('*') if p.is_file() and 'security' not in p.parts}
    for path in ['/home?market=GB','/home?market=FR','/home/global-forces?market=FR&lens=legal']:
        assert web(path)[0]==200
    after={str(p):p.read_bytes() for p in data_path().rglob('*') if p.is_file() and 'security' not in p.parts}
    assert before==after and not data_path('sales_pipeline','opportunities.json').exists()


@pytest.mark.parametrize('path', ['/home/private','/home/assets/unknown','/home/assets/styles?market=GB',
    '/home/global-forces?market=US','/home/global-forces?market=FR&lens=legal&lens=economic'])
def test_finite_asset_and_macro_routes_reject_other_scopes(web,path):
    assert web(path,authenticated=False)[0] in {403,404}


def test_home_play_links_address_the_actual_existing_offer_assessment(pilot):
    from urllib.parse import urlsplit, parse_qs
    from cios.applications.flora.offers_views import render
    approved(pilot)
    html=home.render('/home',{},pilot['seller'])
    href=next(a['href'] for tag,a in DOM(html).nodes if tag=='a' and a.get('href','').startswith('/flora/offers/discover?'))
    target=urlsplit(href)
    detail=render(target.path,parse_qs(target.query),pilot['seller'])
    assert target.fragment and target.fragment in {a.get('id') for _,a in DOM(detail).nodes}


def test_unavailable_personal_context_is_visible_without_invented_recommendations(pilot,monkeypatch):
    def unavailable(*args,**kwargs):raise OSError('synthetic unavailable store')
    monkeypatch.setattr(home.offers,'snapshot',unavailable)
    html=home.render('/home',{},pilot['seller'])
    assert 'Your focus is temporarily unavailable' in html
    assert 'data-assessment-id=' not in html and 'Illustrative UK employer' not in html


def test_home_and_macro_composition_never_make_network_or_paid_model_calls(pilot,monkeypatch):
    import socket
    approved(pilot)
    def no_network(*args,**kwargs):raise AssertionError('Unexpected outgoing network call')
    monkeypatch.setattr(socket,'create_connection',no_network)
    assert 'Recommended Sales Plays' in home.render('/home',{},pilot['seller'])
    assert 'Global PESTLE lenses' in home.render('/home/global-forces',{},pilot['seller'])


def test_signed_in_without_commercial_permission_gets_discovery_not_private_context(pilot,tmp_path,monkeypatch):
    from tests.test_flora_offers_v1 import add_actor
    headers=add_actor(pilot['store'],tmp_path,'home-noncommercial',roles=['package.inspect'])
    def forbidden(*args,**kwargs):raise AssertionError('Unauthorised commercial read')
    monkeypatch.setattr(home.offers,'snapshot',forbidden)
    html=home.render('/home',{},headers)
    assert 'Commercial focus is not available in this workspace' in html
    assert 'Choose workspace' in html and 'data-assessment-id=' not in html
    assert 'Illustrative UK employer' not in html


def test_approved_offer_without_any_proof_reference_is_not_a_home_recommendation(pilot):
    record=draft(pilot,'service')
    home.offers.transition(record['id'],1,'submit',headers=pilot['seller'])
    home.offers.transition(record['id'],2,'approve','SYNTHETIC-review',headers=pilot['reviewer'])
    html=home.render('/home',{},pilot['seller'])
    assert 'Offers available' in html and 'data-assessment-id=' not in html
