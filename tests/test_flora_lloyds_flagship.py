"""The flagship projection preserves public Source and enterprise boundaries."""
from copy import deepcopy
import json
from urllib.parse import parse_qs, urlsplit

import pytest

from cios.applications.flora import lloyds_flagship as flagship, visual_streams as visual
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
    for value in ('118,762', '92,548', '79,323', 'HM Treasury', 'Evidence &amp; scope'):
        assert value in facts
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
    ('PR-LBG-ENVOY', 'Strength · existing AI capability'),
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
    assert 'Opportunity · payments' not in render('insight')

def test_flagship_preserves_supplier_relationship_gate(monkeypatch):
    data = deepcopy(visual.current_data(visual.resolve(PATH, {})))
    for row in data['relationships']:
        if row['object'] == 'SUP-GOOGLE':
            row['verified'] = False
    monkeypatch.setattr(visual, 'current_data', lambda context: data)
    assert 'Google Cloud' not in render('insight')


def test_executive_arrival_preserves_source_withdrawal_and_replay_boundaries(monkeypatch):
    arrival = visual.render(PATH, {})
    assert 'Curve acquisition reported complete' in arrival
    assert 'Integration scope and external procurement remain unproven.' in arrival
    assert 'What’s changed' in arrival and 'data-commercial-change' not in arrival

    data = deepcopy(visual.current_data(visual.resolve(PATH, {})))
    next(source for source in data['sources'] if source['id'] == 'PR-LBG-Q326')['withdrawn'] = True
    monkeypatch.setattr(visual, 'current_data', lambda context: data)
    withheld = visual.render(PATH, {})
    assert 'No recent change is available' in withheld
    assert 'Curve acquisition reported complete' not in withheld

    airline = visual.render('/enterprises/easyjet', {})
    assert 'No recent change is available' in airline
    assert 'Curve acquisition' not in airline and 'data-commercial-change' not in airline
