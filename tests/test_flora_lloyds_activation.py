"""CEO enrichment cannot admit recovered candidates or escape existing Source/IAM owners."""
from copy import deepcopy
from urllib.parse import parse_qs, urlsplit

import pytest

from cios.applications.flora import lloyds_gold as gold, visual_streams as visual
from cios.applications.flora.research_intelligence import model
from cios.applications.flora.financial_intelligence import candidate_analytics
from tests.test_flora_living_enterprise_preview import http

pytestmark = pytest.mark.real_security_boundary


def query(focus='commercial', detail='transaction-customers'):
    return {'stream': ['inside' if focus == 'applications' else 'landscape'],
            'focus': [focus], 'detail': [detail]}


def main(q):
    return gold.render(q, canonical=True).split('<main ', 1)[1].split('</main>', 1)[0]


def test_transaction_business_model_does_not_promote_recovered_appointments_or_supplier_relationships():
    body = main(query())
    assert 'Customer receipts' in body and 'Working capital' in body
    assert 'Conceptual service model' in body and 'Separate Group payments context' in body
    for forbidden in ('Natasha Condon', 'John Langley', 'Export Assist', 'TradeSpeed', 'Complidata', '£100m opportunity'):
        assert forbidden not in body
    assert candidate_analytics.public_factual_projection() == {}
    commercial = main(query(detail='transaction-investigation'))
    assert 'Hypothesis.' in commercial and 'Existing teams, tools or suppliers' in commercial
    assert 'does not establish procurement, budget or a sales opportunity' in commercial


@pytest.mark.parametrize('flag', ['withdrawn', 'revoked', 'owner_only', 'stale', 'superseded', 'contradictory'])
@pytest.mark.parametrize('detail', ['envoy-build', 'envoy-controls', 'envoy-value', 'envoy-investigation'])
def test_envoy_withdrawal_removes_every_new_dependent_view(monkeypatch, flag, detail):
    data = deepcopy(visual.current_data(visual.Context('lloyds', 'landscape')))
    next(s for s in data['sources'] if s['id'] == 'PR-LBG-ENVOY')[flag] = True
    monkeypatch.setattr(visual, 'current_data', lambda ctx: data)
    body = main(query('applications', detail))
    assert '<h2>Envoy</h2>' not in body and 'Google Cloud' not in body
    assert 'Start with one agreed workflow' not in body and 'Platform capability is a starting point' not in body
    assert 'Microsoft Copilot' in body  # Independent eligible research remains useful.


def test_invalid_source_revision_cannot_fall_back_to_recovered_candidate_files(monkeypatch):
    original = model.primary_text
    def changed(source):
        if source['id'] == 'PR-LBG-ENVOY':
            raise ValueError('Changed revision digest')
        return original(source)
    monkeypatch.setattr(model, 'primary_text', changed)
    # Existing model validation rejects a corrupt snapshot before presentation;
    # do not catch that denial and substitute a candidate/replayed document.
    with pytest.raises(ValueError, match='Changed revision digest'):
        main(query('applications', 'envoy-build'))


def test_benefit_withdrawal_does_not_remove_independent_platform_but_removes_numeric_analysis(monkeypatch):
    data = deepcopy(visual.current_data(visual.Context('lloyds', 'landscape')))
    next(s for s in data['sources'] if s['id'] == 'PR-LBG-AI26')['withdrawn'] = True
    monkeypatch.setattr(visual, 'current_data', lambda ctx: data)
    body = main(query('applications', 'envoy-value'))
    assert '<h2>Envoy</h2>' in body and 'Google Cloud' in body
    assert 'GBP50m' not in body and 'GBP100m' not in body
    assert 'The earlier reported contribution and later expectation' not in body
    assert 'not Envoy users' in body


def test_group_payment_disclosures_do_not_survive_source_withdrawal(monkeypatch):
    data = deepcopy(visual.current_data(visual.Context('lloyds', 'landscape')))
    for source in data['sources']:
        if source['id'] in {'PR-LBG-A2030', 'PR-LBG-Q326'}:
            source['withdrawn'] = True
    monkeypatch.setattr(visual, 'current_data', lambda ctx: data)
    body = main(query(detail='transaction-delivery'))
    assert 'Separate Group payments context' not in body
    assert 'Curve acquisition' not in body
    assert 'Client instruction' in body  # Explicit conceptual mechanism is not an issuer claim.


@pytest.mark.parametrize('field,value', [('entity_scope', 'Lloyds Bank plc'),
    ('reporting_period', 'FY2025'), ('metric_unit', 'GBP million; annual underlying profit'),
    ('kind', 'management_expectation')])
def test_new_economic_view_rejects_wrong_entity_period_unit_or_actual_basis(monkeypatch, field, value):
    data = deepcopy(visual.current_data(visual.Context('lloyds', 'landscape')))
    next(c for c in data['claims'] if c['id'] == 'LBG-Q326-PROFIT')[field] = value
    monkeypatch.setattr(visual, 'current_data', lambda ctx: data)
    body = main(query('economics', 'income'))
    assert '£6.6bn' not in body and 'Follow the earnings bridge' in body


def test_economic_target_is_not_an_actual_or_divisional_allocation():
    body = main(query('economics', 'costs'))
    assert 'cost-to-income ratio below 45%' not in body and 'detail=objective-efficiency' in body
    goal=main({'stream':['forces'],'focus':['strategy'],'detail':['objective-efficiency']})
    assert 'cost-to-income ratio below 45%' in goal
    assert 'Gross savings are not net profit' in body
    assert 'Unavailable</td>' not in body
    assert '£6.6bn' not in body


@pytest.mark.parametrize('selector', ['workspace=private', 'analysis=private', 'subject=BK-ENT-003', 'source=owner-only'])
def test_new_drilldowns_cannot_select_private_workspaces_models_or_sources(http, selector):
    status, _, _ = http('/enterprises/lloyds?focus=commercial&detail=transaction-value&' + selector)
    assert status in {403, 404}


def test_new_state_uses_existing_history_and_subject_serialisation():
    state = gold.resolve(query(detail='transaction-value'))
    state = gold.replace(state, route=gold.CANONICAL, subject='commercial')
    inside = parse_qs(urlsplit(gold.href(state, stream='inside')).query)
    assert inside['subject'] == ['commercial']
    returned = parse_qs(urlsplit(gold.href(gold.resolve(inside), stream='landscape')).query)
    assert returned['focus'] == ['commercial'] and returned['subject'] == ['commercial']
