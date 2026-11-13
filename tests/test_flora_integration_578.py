"""Narrow industry-context banner over the integrated participant comparison."""
from html.parser import HTMLParser
import pytest
from cios.applications.flora.research_intelligence import technology_experience as x
from tests.test_flora_research_intelligence import web


class DOM(HTMLParser):
    def __init__(self, html): super().__init__(); self.nodes = []; self.feed(html)
    def handle_starttag(self, tag, attrs): self.nodes.append((tag, dict(attrs)))


@pytest.mark.parametrize('route', ['/participants', '/district?district=cloud', '/district?district=ai'])
def test_banner_has_native_keyboard_link_and_preserves_comparison(web, route):
    status, html = web(x.BASE + route)
    assert status == 200
    nodes = DOM(html).nodes
    banner = [(tag, a) for tag, a in nodes if a.get('class') == 'commercial-sector-banner']
    assert len(banner) == 1 and banner[0][0] == 'a'
    assert banner[0][1]['href'] == x.BASE and banner[0][1]['aria-label'] == 'Back to UK Technology industry'
    assert html.index('commercial-sector-banner') < html.index('commercial-table')
    assert any(tag == 'img' and a.get('src') == x.ASSET_BASE + 'artwork' and a.get('alt') == '' for tag, a in nodes)
    assert sum(tag == 'h1' for tag, _ in nodes) == 1
    assert 'aria-sort=' in html


def test_banner_does_not_enter_enterprise_or_pipeline_views(web):
    for route in ['/enterprise?enterprise=nvidia', '/pipeline?scope=nvidia']:
        status, html = web(x.BASE + route)
        assert status == 200 and 'class="commercial-sector-banner"' not in html
