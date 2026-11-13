"""Two-screen proof: statistical scope, source lineage and real access boundaries."""
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path

import pytest

from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_sales_pipeline import actor, web
from tests.test_flora_offers_v1 import pilot, add_actor, draft
from cios.applications.flora import visual_v2 as v, offers
from cios.applications.flora.public_routes import public_route_catalog
from cios.applications.flora.storage import data_path


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.rows = []; self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.rows.append((tag, dict(attrs)))


def test_full_nonoverlapping_uk_statistical_denominator_not_only_researched_sectors():
    data = v.basis()
    assert data['country'] == 'GB' and data['year'] == 2024
    assert data['classification'] == 'UK SIC 2007'
    assert data['measure'] == 'GVA' and data['valuation'] == 'current basic prices'
    rows = data['districts']
    assert {r['sic'] for r in rows} == set('ABCDEFGHIJKLMNOPQRST')
    assert len(rows) == len({r['id'] for r in rows}) == 20
    assert sum(r['weight_per_thousand'] for r in rows) == 1002
    assert data['denominator_per_thousand'] == 1000  # Do not quietly normalise.
    assert not any(r['sic'] in {'B-E','G-T','U'} for r in rows)
    assert data['published_total_billion'] == 2623
    assert all(r['source_id'] == 'ONS-GDP-2026-09' for r in rows)


def test_official_published_weights_retained_with_rounding_not_estimated_rankings():
    expected = dict(zip('ABCDEFGHIJKLMNOPQRST', [7,7,87,19,12,57,94,36,28,66,81,142,87,54,51,59,84,15,15,1]))
    assert {r['sic']:r['weight_per_thousand'] for r in v.basis()['districts']} == expected
    html = v.render(v.BASE, {})
    assert '£2.62tn' in html and '2024 · current basic prices' in html
    assert '100.2%' in html and 'imputed owner-occupier rents' in html
    assert 'not a quantitative map' in html
    assert 'SIC 2026 is not silently mixed in' in html


def test_no_false_subsector_gva_or_unsupported_industry_navigation():
    html = v.render(v.BASE, {})
    links = [(a['data-research'],a['href'],a['aria-label']) for t,a in Elements(html).rows if 'data-research' in a]
    assert {r[0] for r in links} == {'technology','banking','aviation'}
    assert {r[1] for r in links} == {'/industries/technology/experience','/industries/banking','/industries/aviation'}
    assert all('broader' in r[2] for r in links)
    assert 'share of GDP' not in html and 'Banking 8.1%' not in html
    for tag, attrs in Elements(html).rows:
        if 'data-sic' in attrs:
            assert tag == 'div' and 'href' not in attrs and 'onclick' not in attrs and 'tabindex' not in attrs


def test_economic_volume_growth_cannot_be_reused_as_industry_or_nominal_gva_growth():
    data = v.basis()['growth']; row = v.insight('economic')
    assert data['value_pct'] == 0.7 and data['measure'] == 'real GDP volume change'
    assert data['period'] == 'three months to September 2026'
    assert 'previous three months' in row['text'] and '2024 current-price GVA' in row['text']
    assert 'not industry growth, global growth' in row['details']
    assert row['lineage']['source_ids'] == ['ONS-GDP-2026-09']
    assert not row['lineage'].get('accepted')


@pytest.mark.parametrize('factor', list(v.FACTORS))
def test_six_image_native_insights_retain_uk_lineage_and_optional_single_sources(factor):
    html = v.render(v.BASE+'/pestle', {'factor':[factor]})
    rows = Elements(html).rows
    assert sum('class' in a and a['class']=='image-insight' for t,a in rows) == 1
    assert sum(t=='nav' for t,a in rows) == 1
    assert html.count('Sources & method</summary>') == 1
    assert html.index('class="image-insight"') < html.rindex('</figure>')
    assert 'tabindex="-1" aria-labelledby="insight-title"' in html
    row = v.insight(factor)
    assert row['lineage']['source_ids']
    assert all(s.get('primary_content_sha256') is None for s in row['sources'])
    assert all(s['id'] not in {'GM-CYBER-FR','GM-CSRD','GM-CSRD-FR'} for s in row['sources'])
    if factor != 'economic':
        data = v.macro.load_context()
        force = next(f for f in data['forces'] if f['id'] == row['lineage']['force_id'])
        assert row['lineage']['as_of'] == data['as_of']
        assert force['counter'] in row['details']
        assert row['lineage']['source_ids'] == force['country_source_ids']['GB']
        assert row['lineage']['kind'] == force['kind']


def test_no_permanent_cards_or_body_navigation_in_two_screen_contract():
    for path in (v.BASE,v.BASE+'/pestle'):
        html = v.render(path,{})
        assert '<footer' not in html and '<article' not in html
        assert 'My Commercial Focus' not in html and 'What’s Changing' not in html
        assert 'Recommended Sales Plays' not in html and 'More from' not in html
        assert 'Inspect evidence' not in html
        assert html.count('<figure') == html.count('<nav') == 1
        assert html.index('<nav') < html.index('<main')
        assert 'class="image-insight"' not in html
        assert 'Select a labelled factor' in html if path.endswith('pestle') else 'All 20 domestic SIC' in html


@pytest.mark.parametrize('path,query', [
    (v.BASE,{'market':['FR']}),(v.BASE,{'market':['global']}),(v.BASE,{'market':['']}),
    (v.BASE,{'market':['GB','FR']}),(v.BASE,{'factor':['legal']}),
    (v.BASE,{'workspace':['private']}),(v.BASE,{'enterprise':['BK-ENT-001']}),
    (v.BASE+'/pestle',{'factor':['<script>']}),(v.BASE+'/pestle',{'factor':['']}),
    (v.BASE+'/pestle',{'factor':['social','legal']}),(v.BASE+'/pestle',{'market':['FR'],'factor':['legal']}),
    (v.BASE+'/private',{}),
])
def test_finite_country_and_query_boundary_fails_closed(path,query):
    with pytest.raises(ValueError): v.render(path,query)


@pytest.mark.parametrize('asset', ['../../security_store.py','economy.json','private','uk-artwork/../styles'])
def test_only_explicit_visual_assets_are_addressable(asset):
    with pytest.raises(ValueError): v.asset(asset)
    assert '/visual-v2/assets/'+asset not in public_route_catalog()


def test_public_routes_are_exact_and_all_model_queries_are_bounded():
    routes = public_route_catalog()
    assert routes[v.BASE].query_keys == frozenset({'market'})
    assert routes[v.BASE+'/pestle'].query_keys == frozenset({'market','factor'})
    assert set(p for p in routes if p.startswith(v.BASE)) == {v.BASE,v.BASE+'/pestle',*(v.BASE+'/assets/'+n for n in v.FILES)}


def test_sources_are_primary_narrow_reviewed_extracts_not_fabricated_full_originals():
    for source in v.basis()['sources']:
        assert source['url'].startswith('https://www.ons.gov.uk/')
        assert source['retrieval_method'] == 'approved web research tool'
        assert source['retrieval_reference'] and source['locator']
        assert source['primary_content_sha256'] is None
    assert 'no canonical intelligence promotion' in v.basis()['authority']


def test_public_render_never_reads_private_owners_or_calls_matching_or_network(monkeypatch):
    from cios.applications.flora import sales_pipeline
    import urllib.request
    def forbidden(*a, **kw): raise AssertionError('Forbidden domain or network access')
    for name in ('snapshot','discover','save_offer','select_employer'): monkeypatch.setattr(offers,name,forbidden)
    monkeypatch.setattr(sales_pipeline,'create_opportunity',forbidden)
    monkeypatch.setattr(urllib.request,'urlopen',forbidden)
    for path in (v.BASE,v.BASE+'/pestle'):
        assert 'data-market="GB"' in v.render(path,{}, {'X-User':'forged','X-Workspace':'forged','X-Roles':'cios_owner'})
    for factor in v.FACTORS: assert v.insight(factor)['title']


def test_existing_private_offer_and_employer_data_do_not_enter_public_or_signed_in_scene(pilot):
    record = draft(pilot,name='PRIVATE visual sentinel',evidence='PRIVATE proof')
    before = offers._path().read_bytes()
    for headers in (None,pilot['seller'],pilot['outsider'],pilot['foreign'],{'X-User':'pilot-seller','X-Roles':'cios_owner'}):
        for path in (v.BASE,v.BASE+'/pestle'):
            html = v.render(path,{},headers)
            assert record['id'] not in html and 'PRIVATE visual sentinel' not in html
            assert 'Illustrative UK employer' not in html
    assert offers._path().read_bytes() == before
    assert not data_path('sales_pipeline','opportunities.json').exists()


def test_verified_workspace_context_is_escaped_and_revocation_removes_it(actor):
    store,token,csrf,headers = actor
    html = v.render(v.BASE,{},headers)
    assert 'synthetic-workspace' in html and 'Switch workspace' in html
    store.logout(token,csrf)
    html = v.render(v.BASE,{},headers)
    assert 'synthetic-workspace' not in html and 'Switch workspace' not in html
    assert 'Sign in' in html


def test_real_http_keeps_auth_csrf_cache_and_existing_destination_boundaries(web):
    for path in (v.BASE,v.BASE+'/pestle?factor=technological'):
        status,html,_ = web(path,authenticated=False)
        assert status == 200 and 'Sign in' in html and 'synthetic-workspace' not in html
        assert 'no-store' in web.last_headers['Cache-Control']
        status,html,_ = web(path)
        assert status == 200 and 'Switch workspace' in html
        assert 'name="csrf"' in html or "name='csrf'" in html
    assert web('/flora/offers',authenticated=False)[0] in (302,303,403)
    assert web('/pipeline',authenticated=False)[0] in (302,303,403)
    assert web(v.BASE+'/private')[0] != 200
    assert not data_path('sales_pipeline','opportunities.json').exists()


def test_runtime_source_preserves_canonical_home_and_domain_owners():
    import hashlib
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root/'docs/flora-runtime/visual-v2-583/Protected-Owners.json').read_text())
    for name,digest in manifest['unchanged_files'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
    import ast
    source = (root/'cios/applications/flora/web/app.py').read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='_flora_home_page')
    assert hashlib.sha256(ast.get_source_segment(source,node).encode()).hexdigest() == manifest['canonical_home_sha256']
