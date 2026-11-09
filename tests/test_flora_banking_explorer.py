"""Public Banking vertical slice: real HTTP routing, attribution and access boundary."""
from dataclasses import replace
from html.parser import HTMLParser
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import hashlib
import threading
from urllib.parse import urlsplit

import pytest

from cios.applications.flora.banking_explorer import ROOT, enterprise_page, industry_page
from cios.applications.flora.banking_portfolio import BANKS
from cios.applications.flora.public_routes import public_request_target
from cios.applications.flora.web.app import FloraWebHandler


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.hrefs = []
        self.ids = set()
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'href' in attrs:
            self.hrefs.append(attrs['href'])
        if 'id' in attrs:
            self.ids.add(attrs['id'])


@pytest.fixture
def web(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'development')
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def get(path, headers=None):
        conn = HTTPConnection('127.0.0.1', server.server_port, timeout=30)
        try:
            conn.request('GET', path, headers=headers or {})
            response = conn.getresponse()
            return response.status, response.read().decode()
        finally:
            conn.close()

    yield get, tmp_path
    server.shutdown()
    server.server_close()
    thread.join(2)


def test_home_and_industry_entry_are_discoverable(web):
    get, _ = web
    for path in ['/', '/flora/banking']:
        status, html = get(path)
        assert status == 200
        assert ROOT in Links(html).hrefs


def test_industry_selects_every_supported_enterprise(web):
    get, _ = web
    status, html = get(ROOT)
    assert status == 200
    links = Links(html).hrefs
    for slug in BANKS:
        assert f'{ROOT}/{slug}' in links
        status, detail = get(f'{ROOT}/{slug}')
        assert status == 200
        assert BANKS[slug].name in detail
        assert f'{ROOT}/{slug}/insights' in Links(detail).hrefs


def test_enterprise_insight_evidence_drilldown(web):
    get, _ = web
    for bank in BANKS.values():
        status, html = get(f'{ROOT}/{bank.slug}/insights')
        assert status == 200
        for label in ['Observation', 'Interpretation', 'Implication', 'Opportunity', 'Evidence &amp; confidence']:
            assert label in html
        links = Links(html).hrefs
        evidence = f'/flora/banking/{bank.slug}/evidence'
        assert evidence in links
        assert get(evidence)[0] == 200
        for opp in bank.opportunities:
            target = f'/flora/banking/{bank.slug}/opportunity/{opp.id}'
            assert target in links
            assert get(target)[0] == 200


def test_landscape_nodes_have_resolvable_destinations(web):
    get, _ = web
    paths = [ROOT, f'{ROOT}/lloyds', f'{ROOT}/lloyds/insights']
    for path in paths:
        status, html = get(path)
        assert status == 200
        assert "aria-label='Breadcrumb'" in html
        for href in Links(html).hrefs:
            target = urlsplit(href)
            if href.startswith('#'):
                assert target.fragment in Links(html).ids
            elif target.path.startswith(ROOT):
                code, destination = get(target.path)
                assert code == 200
                if target.fragment:
                    assert target.fragment in Links(destination).ids


def test_financial_dates_scope_and_source_attribution():
    bank = BANKS['lloyds']
    html, status = enterprise_page(bank.slug)
    assert status == 200
    for label, value in list(bank.metrics.items())[:6]:
        assert label in html and value.replace('&', '&amp;') in html
    assert 'Historical reporting periods' in html
    assert 'not independently verified' in html
    for source in bank.analyst_sources:
        assert source.replace('&', '&amp;') in html


def test_unknowns_and_scenarios_do_not_become_verified_claims():
    html, _ = enterprise_page('lloyds')
    assert 'Verified bank-specific supplier contracts' in html
    assert 'are not established here' in html
    assert 'not verified contracts or ownership' in html
    html, _ = enterprise_page('lloyds', insights=True)
    assert 'Claim-level accepted Evidence: not supplied' in html
    assert 'not calibrated evidence confidence' in html
    assert 'not customer-confirmed programmes' in html
    assert 'Disconfirming signals' in html


def test_empty_insights_and_unknown_enterprise(monkeypatch):
    bank = BANKS['lloyds']
    monkeypatch.setitem(BANKS, 'lloyds', replace(bank, opportunities=()))
    html, status = enterprise_page('lloyds', insights=True)
    assert status == 200 and 'No strategic hypotheses' in html
    html, status = enterprise_page('not-a-bank')
    assert status == 404 and 'Choose a supported enterprise' in html


def test_fixture_text_is_escaped(monkeypatch):
    bank = BANKS['lloyds']
    monkeypatch.setitem(BANKS, 'lloyds', replace(bank, name='<script>alert(1)</script>'))
    html, _ = enterprise_page('lloyds')
    assert '<script>' not in html
    assert '&lt;script&gt;' in html


def test_public_scope_is_finite_and_query_cannot_select_private_records():
    assert public_request_target(ROOT)
    assert public_request_target(ROOT + '/lloyds/insights')
    for suffix in ['/private', '/lloyds/private', '/lloyds/insights/extra', '/../MOD', '/%2e%2e/MOD', '//lloyds', '?workspace_id=private', '?enterprise=MOD']:
        assert not public_request_target(ROOT + suffix)


def test_canvas_still_requires_verified_authority(web):
    get, _ = web
    assert get(ROOT + '/lloyds')[0] == 200
    status, _ = get('/digital-twins/MOD/canvas', {'X-Flora-User': 'owner', 'X-Flora-Workspace': 'private', 'X-Flora-Role': 'owner'})
    assert status in (401, 403)
    status, _ = get(ROOT + '?workspace_id=private')
    assert status in (401, 403)


def test_public_exploration_does_not_mutate_protected_storage(web):
    get, root = web
    def snapshot():
        return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob('*') if p.is_file()}
    # Resolve anonymous context once before measuring read-only exploration.
    assert get(ROOT)[0] == 200
    before = snapshot()
    for path in [ROOT, ROOT+'/lloyds', ROOT+'/lloyds/insights']:
        assert get(path)[0] == 200
    assert snapshot() == before


def test_responsive_and_keyboard_navigation_contract():
    html = industry_page()
    assert "name='viewport'" in html
    assert 'prefers-reduced-motion' in html
    assert 'ex-map-mobile' in html
    assert 'Skip to explorer content' in html
    assert ':focus-visible' in html
