"""The flagship projection preserves public Source and enterprise boundaries."""
from copy import deepcopy
import json
from urllib.parse import parse_qs, urlsplit

import pytest

from cios.applications.flora import lloyds_flagship as flagship, visual_streams as visual
from cios.applications.flora.public_routes import owner_inspection_request_target, public_request_target
from tests.test_flora_research_intelligence import web
from tests.test_flora_security_repair_01b import authority, signed
from cios.applications.flora.visual_panels import research_inspection
from cios.applications.flora.financial_intelligence import candidate_analytics


PATH = '/enterprises/lloyds'


def render(mode='facts'):
    return visual.render(PATH, {'stream': ['landscape'], 'detail': ['flagship'], 'reading': [mode]})


def test_existing_journey_and_connected_issue():
    facts, insight = render(), render('insight')
    assert 'Renew the bank while it runs' in facts
    assert 'Core renewal and application retirement matter' in insight
    assert 'Core renewal and application retirement matter' not in facts
    assert 'Scale AI only after benefit' in insight and 'Scale AI only after benefit' not in facts
    for value in ('118,762', '92,548', '79,323', 'HM Treasury', 'Efficiency ambition'):
        assert value in facts
    assert 'llf-sources' not in facts and 'Reviewed excerpt' not in insight
    root = visual.render(PATH, {})
    assert 'Explore the Lloyds flagship' in root and '118,762' not in root
    ctx = visual.resolve(PATH, {})
    for _, _, stream, detail in flagship.STAGES:
        route = urlsplit(visual.url(ctx, stream=stream, detail=detail))
        assert visual.resolve(route.path, parse_qs(route.query)).detail == detail
    assert candidate_analytics.public_factual_projection() == {}
    detail = visual.render(PATH, {'stream':['landscape'], 'detail':['funding']})
    assert 'Renew the bank while it runs' not in detail and 'From funding to earnings' in detail


@pytest.mark.parametrize('source_id, text', [
    ('PR-LBG-A2030', 'Core renewal and application retirement matter'),
    ('PR-LBG-ENVOY', 'existing AI capability'),
])
def test_source_withdrawal_removes_coupled_insight(monkeypatch, source_id, text):
    assert text in render('insight')
    data = deepcopy(visual.current_data(visual.resolve(PATH, {})))
    next(source for source in data['sources'] if source['id'] == source_id)['withdrawn'] = True
    monkeypatch.setattr(visual, 'current_data', lambda context: data)
    assert text not in render('insight')
    assert 'Strategy timeline' in render('insight')


def test_new_policy_excerpt_provenance_and_lifecycle(monkeypatch):
    assert flagship._payments()
    original = json.loads

    def withdraw(contents):
        source = original(contents)
        return {**source, 'withdrawn': True} if source.get('id') == 'LLF-HMT-PAYMENTS' else source

    monkeypatch.setattr(flagship.json, 'loads', withdraw)
    assert flagship._payments() is None
    assert 'HM Treasury' not in render('insight')
    assert 'id="llf-swot-2"' not in render('insight')

def test_flagship_preserves_supplier_relationship_gate(monkeypatch):
    data = deepcopy(visual.current_data(visual.resolve(PATH, {})))
    for row in data['relationships']:
        if row['object'] == 'SUP-GOOGLE':
            row['verified'] = False
    monkeypatch.setattr(visual, 'current_data', lambda context: data)
    assert 'Google Cloud' not in render('insight')

def test_inspection_separated_from_executive_view(web):
    target = PATH + '?stream=landscape&detail=flagship&lens=inspection'
    assert owner_inspection_request_target(target) and not public_request_target(target)
    status, body = web(target)
    assert status in (403, 404) and 'Lloyds flagship research inspection' not in body


def test_verified_owner_can_inspect_flagship(authority, tmp_path):
    _, _, _, headers, _ = signed(authority, tmp_path)
    query = {'stream': ['landscape'], 'detail': ['flagship'], 'lens': ['inspection']}
    with pytest.raises(PermissionError):
        research_inspection(PATH, query, {'X-Flora-Roles': 'cios_owner'})
    panel = research_inspection(PATH, query, headers)
    assert 'Lloyds flagship research inspection' in panel and 'Reviewed excerpt' in panel
    assert 'Threat · cost of parallel running' in panel
    assert '.pdf' not in panel
