"""The visual journey is public presentation; sales edits never reach private stores."""
from html.parser import HTMLParser
from http.client import HTTPConnection
from copy import deepcopy
import json
import pytest

from cios.applications.flora.research_intelligence import technology_experience as x
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_research_intelligence import web


class DOM(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.nodes=[]; self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


@pytest.mark.parametrize('suffix', ['', '/district?district=cloud', '/enterprise', '/enterprise?detail=financials',
                                    '/enterprise?detail=strategy', '/operating-model', '/operating-model?area=interconnection',
                                    '/pipeline?scope=industry', '/pipeline?scope=equinix', '/opportunity?record=cooling'])
def test_journey_http_views_are_public_and_native_links_are_finite(web, suffix):
    code, html = web(x.BASE + suffix)
    assert code == 200
    dom = DOM(html)
    ids = [a['id'] for _,a in dom.nodes if 'id' in a]
    assert len(ids) == len(set(ids))
    for tag, a in dom.nodes:
        if tag == 'a' and a.get('href','').startswith(x.BASE):
            assert public_request_target(a['href'].split('#')[0]), a['href']
    assert '/industries/technology/evidence' in html  # Specialist provenance remains addressable; default views stay commercial.


def test_asset_urls_follow_existing_extension_free_route_guard():
    for name, mime in x.ASSET_TYPES.items():
        assert public_request_target(x.ASSET_BASE + name)
        raw, actual = x.asset(name)
        assert raw and actual == mime
        assert not public_request_target(x.ASSET_BASE + name + '?workspace=private')
    assert x.asset('artwork')[0].startswith(b'RIFF')
    for name in ['../secret', '/etc/passwd', 'uk-technology.webp', 'anything']:
        with pytest.raises(ValueError): x.asset(name)


def test_asset_symlink_is_not_followed(tmp_path, monkeypatch):
    (tmp_path / 'experience.js').symlink_to('/etc/hosts')
    monkeypatch.setattr(x, 'ASSETS', tmp_path)
    with pytest.raises(ValueError): x.asset('interactions')


@pytest.mark.parametrize('query', [{'scope':'private'}, {'district':'../secret'}, {'selected':'<script>'},
                                   {'record':'other-workspace'}, {'detail':'private'}, {'area':'unknown'}, {'workspace':'private'}])
def test_selectors_do_not_resolve_private_or_unregistered_records(query):
    with pytest.raises(ValueError): x.render(x.BASE, query)


@pytest.mark.parametrize('target', ['/assets/../secret', '?scope=industry&scope=equinix', '?workspace=private',
                                   '/pipeline?promote=true', '/assets/interactions?record=cooling'])
def test_http_rejects_unregistered_scope_and_duplicate_selectors(web, target):
    assert web(x.BASE + target)[0] in (403, 404)


def test_all_eight_districts_remain_keyboard_addressable_and_image_relative(web):
    code, html = web(x.BASE)
    hotspots = [a for tag,a in DOM(html).nodes if a.get('data-district')]
    assert len(hotspots) == 8 and {a['data-district'] for a in hotspots} == set(x.DISTRICTS)
    assert all(a.get('aria-label') and a.get('href') and '%' in a['style'] for a in hotspots)
    for district in x.DISTRICTS:
        assert web(x.BASE + '?selected=' + district)[0] == 200
        assert web(x.BASE + '/district?district=' + district)[0] == 200
    assert 'Evidence</button>' not in html and 'commercial hypothesis' not in html.lower()


def test_market_and_annual_figures_keep_their_geographic_and_period_boundaries(web):
    _, market = web(x.BASE + '/district?district=cloud')
    assert 'Cloud benchmark, not total district value' in market and x.CMA_URL in market
    _, enterprise = web(x.BASE + '/enterprise?detail=financials')
    for text in ['Global figures · USD', 'FY2025', '$9.217bn', '$6.475bn', '$1.655bn', 'No UK-only financial figure is inferred']:
        assert text in enterprise
    assert x.REPORT_URL in enterprise and 'operating entity' in enterprise


def test_enterprise_model_is_explicitly_conceptual_not_a_disclosed_org_chart(web):
    _, html = web(x.BASE + '/operating-model')
    assert 'Flora conceptual operating view' in html
    assert 'not a disclosed organisation chart' in html and 'demand and budget not established' in html
    assert '?scope=equinix' in html
    for category in ('technology','economy','sustainability','cyber'):
        assert 'macro='+category in html


def test_equnix_scope_does_not_seed_a_research_hypothesis_as_a_sales_record(web):
    assert all(r['enterprise'] != 'Equinix' for r in x.DEMO_ROWS)
    _, html = web(x.BASE + '/pipeline?scope=equinix')
    assert 'Add an illustrative opportunity to explore this scope.' in html
    assert not any(r.get('scopeEnterprise') == 'equinix' for r in x.DEMO_ROWS)
    assert '<tbody id="pipeline-rows"><tr><td colspan="8">Add an illustrative' in html


def test_journey_reads_do_not_invoke_private_pipeline_or_model_clients(web, monkeypatch):
    from cios.applications.flora import sales_pipeline
    from cios.applications.flora.blueprint_import import views
    def forbidden(*args, **kwargs): raise AssertionError('Private sales/import owner accessed')
    monkeypatch.setattr(sales_pipeline, 'list_opportunities', forbidden)
    monkeypatch.setattr(sales_pipeline, 'create_opportunity', forbidden)
    monkeypatch.setattr(views, 'approve_and_promote', forbidden)
    for path in x.PATHS:
        assert web(path)[0] == 200


def test_browser_interactions_are_tab_local_not_network_writes():
    js = x.asset('interactions')[0].decode()
    assert 'sessionStorage.setItem' in js and 'localStorage' not in js
    for forbidden in ('fetch(', 'XMLHttpRequest', 'sendBeacon', '/flora/sales/capture', 'innerHTML = row.need'):
        assert forbidden not in js
    assert 'esc(row.need' in js and 'esc(n.text)' in js


def test_enterprise_detail_is_clickable_without_javascript(web):
    _, html = web(x.BASE + '/enterprise')
    assert '/enterprise?detail=financials' in html and '/enterprise?detail=strategy' in html
    _, html = web(x.BASE + '/operating-model?area=interconnection')
    assert '<h2>Interconnection</h2>' in html
    _, html = web(x.BASE + '/opportunity?record=cooling&scope=industry')
    assert '<h1>Cooling optimisation</h1>' in html and 'Confirm need, sponsor and funding' in html


@pytest.mark.parametrize('suffix,scope', [('', 'industry'), ('/district?district=cloud', 'cloud'),
                                        ('/enterprise', 'equinix'), ('/operating-model', 'equinix')])
def test_primary_pipeline_entry_inherits_industry_district_or_enterprise_scope(web, suffix, scope):
    _, html = web(x.BASE + suffix)
    links = [a for tag,a in DOM(html).nodes if tag == 'a' and a.get('href') == x.url('/pipeline', scope=scope)]
    assert len(links) == 1  # #585: one scoped demo entry; no replacement of the protected live Pipeline.
    assert any(tag=='a' and a.get('href')=='/flora/sales/pipeline' for tag,a in DOM(html).nodes)


def test_macro_drill_keeps_technology_context_instead_of_inheriting_banking(web):
    _, html = web(x.BASE + '/district?district=cloud&macro=technology')
    assert 'AI and hybrid workloads' in html and 'id="macro-context"' in html
    assert '/district?macro=economy&amp;district=cloud' in html
    assert '/macro?market=GB' not in html
    assert web(x.BASE + '/district?macro=private')[0] == 404
