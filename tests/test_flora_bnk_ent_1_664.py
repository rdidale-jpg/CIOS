"""Isolated documentary QA: no live source admission, model or Pipeline writes."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

PACK = Path(__file__).resolve().parents[1] / 'docs/flora-runtime/bnk-ent-1'
SPEC = importlib.util.spec_from_file_location('bnk_ent_1_qa', PACK / 'validate.py')
QA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(QA)


@pytest.fixture
def finance():
    data = QA.read('Financial-Reconciliation.json')
    return data, QA.unique(data['measurements'])


def test_complete_documentary_reconciliation_and_preserved_owners():
    result = QA.validate()
    assert result['preserved_files'] == 450
    assert result['reconciliations']['BE-CALC-NBS-UPBT'] == '2026'
    assert result['reconciliations']['BE-CALC-NBS-SPBT'] == '1490'
    assert result['canonical_writes'] == result['runtime_changes'] == 0


@pytest.mark.parametrize('field,value', [
    ('subject_ref', 'lloyds-bank'), ('currency', 'USD'), ('unit', 'percent'),
    ('scale', 'billions'), ('state', 'target'), ('accounting_basis', 'statutory'),
    ('period', {'kind': 'duration', 'start': '2024-01-01', 'end': '2024-12-31', 'as_at': None}),
])
def test_wrong_perimeter_or_definition_cannot_enter_bank_bridge(finance, field, value):
    data, measurements = finance
    measurements['LBG25-nii'][field] = value
    with pytest.raises(AssertionError):
        QA.reconcile(data['recipes'][0], measurements)


def test_stock_inputs_cannot_be_treated_as_income_flow(finance):
    data, measurements = finance
    recipe = data['recipes'][0]
    for mid in [*recipe['inputs'], recipe['target']]:
        measurements[mid]['period'] = {'kind': 'stock', 'as_at': '2025-12-31'}
    with pytest.raises(AssertionError, match='stock'):
        QA.reconcile(recipe, measurements)


def test_target_basis_cannot_be_relabelled_underlying(finance):
    data, measurements = finance
    recipe = next(r for r in data['recipes'] if r['id'] == 'BE-CALC-NBS-SPBT')
    measurements[recipe['target']]['accounting_basis'] = 'underlying'
    with pytest.raises(AssertionError, match='target accounting'):
        QA.reconcile(recipe, measurements)


def test_integration_cost_cannot_be_deducted_twice(finance):
    data, measurements = finance
    recipe = next(r for r in data['recipes'] if r['id'] == 'BE-CALC-NBS-UPBT')
    measurements['NBS26-cost']['value'] = '4148'  # 4021 already includes 127.
    with pytest.raises(AssertionError, match='reconciliation failed'):
        QA.reconcile(recipe, measurements)


def test_member_reward_is_not_a_positive_profit_adjustment(finance):
    data, measurements = finance
    recipe = next(r for r in data['recipes'] if r['id'] == 'BE-CALC-NBS-SPBT')
    recipe['signs'][-1] = 1
    with pytest.raises(AssertionError, match='reconciliation failed'):
        QA.reconcile(recipe, measurements)


@pytest.mark.parametrize('wrong_subject', ['google-emea', 'google-ireland', 'google-brand'])
def test_cloud_segment_results_cannot_become_legal_or_brand_accounts(finance, wrong_subject):
    data, measurements = finance
    for mid in ('GCQ326-revenue', 'GCQ326-operating-income'):
        measurements[mid]['subject_ref'] = wrong_subject
    with pytest.raises(AssertionError, match='segment profit'):
        QA.cloud_segment_ratio(data['ratio_review'], measurements)


@pytest.mark.parametrize('field,value', [('currency','GBP'), ('scale','billions'), ('state','target')])
def test_cloud_ratio_rejects_incompatible_measurements(finance, field, value):
    data, measurements = finance
    measurements['GCQ326-operating-income'][field] = value
    with pytest.raises(AssertionError):
        QA.cloud_segment_ratio(data['ratio_review'], measurements)


@pytest.mark.parametrize('restriction', ['revoked', 'denied', 'contradictory', 'stale', 'superseded', 'withdrawn', 'retracted', 'core_contradiction'])
def test_source_lifecycle_blocks_dependants_without_blocking_unrelated_claims(restriction):
    sources = QA.unique(QA.read('Source-Ledger.json')['sources'])
    claims = QA.read('Claims.json')['claims']
    affected = next(c for c in claims if c['source_ids'] == ['PR-LBG-Q326'])
    unaffected = next(c for c in claims if c['source_ids'] == ['RUD1-NATIONWIDE-FY26'])
    assert QA.research_available(affected, sources)
    sources['PR-LBG-Q326'][restriction] = True
    assert not QA.research_available(affected, sources)
    assert QA.research_available(unaffected, sources)


def test_excluded_payment_guide_is_never_business_evidence():
    sources = QA.unique(QA.read('Source-Ledger.json')['sources'])
    assert not QA.research_available({'source_ids':['BE-S-PAY-FPS-GUIDE']}, sources)
    assert all('BE-S-PAY-FPS-GUIDE' not in c['source_ids'] for c in QA.read('Claims.json')['claims'])


@pytest.mark.parametrize('change', ['brand_guarantor', 'scheme_company', 'brand_contract', 'effective_date', 'promotion'])
def test_invalid_relationship_joins_and_authority_are_rejected(change):
    entities = QA.unique(QA.read('Identity-Crosswalk.json')['entities'], 'ref')
    claims = QA.unique(QA.read('Claims.json')['claims'])
    sources = QA.unique(QA.read('Source-Ledger.json')['sources'])
    edges = QA.read('Relationship-Handoff.json')['edges']
    predicate = {'brand_guarantor':'lists_as_guarantor_member', 'scheme_company':'reported_operator_of',
        'brand_contract':'reported_envoy_collaboration_with', 'effective_date':'designates_critical_third_party',
        'promotion':'registered_person_with_significant_control_of'}[change]
    edge = deepcopy(next(e for e in edges if e['predicate'] == predicate))
    if change == 'brand_guarantor': edge['object_ref'] = 'google-brand'
    if change == 'scheme_company': edge['object_ref'] = 'lloyds-bank'
    if change == 'brand_contract': edge['object_ref'] = 'google-emea'
    if change == 'effective_date': edge['dates']['effective'] = edge['dates']['published']
    if change == 'promotion': edge['canonical_acceptance'] = True
    with pytest.raises(AssertionError):
        QA.validate_edge(edge, entities, claims, sources)


def test_bare_legacy_identifier_is_not_a_safe_enterprise_join():
    collision = next(c for c in QA.read('Identity-Crosswalk.json')['collisions'] if c['identifier'] == 'BK-ENT-003')
    assert collision['left_owner'] != collision['right_owner']
    assert 'Nationwide' in collision['left_meaning'] and 'NatWest' in collision['right_meaning']
    assert 'no_alias_merge' in collision['disposition']


def test_actual_and_expected_ai_values_cannot_become_achieved_saving_difference():
    from decimal import Decimal
    from cios.applications.flora.intelligence_presentation import Source, Statement, difference
    source = QA.unique(QA.read('Source-Ledger.json')['sources'])['PR-LBG-AI26']
    original = Source(source['title'], source['url'])
    actual = Statement('Reported AI value', 'reported', 'Lloyds Banking Group', 'FY2025',
        (original,), 'reported_source', 'working_research', measurement_state='actual',
        value=Decimal('50'), unit='GBP million', basis='company_reported_AI_value')
    expected = Statement('Expected AI value', 'reported', 'Lloyds Banking Group', 'FY2026',
        (original,), 'reported_source', 'working_research', measurement_state='expected',
        value=Decimal('100'), unit='GBP million', basis='company_reported_AI_value')
    with pytest.raises(ValueError, match='Incompatible'):
        difference(expected, actual, text='Achieved savings doubled')
    claims = QA.unique(QA.read('Claims.json')['claims'])
    thesis = claims['BE-LBG-AI-THESIS']
    assert thesis['semantic_type'] == 'hypothesis' and thesis['counter_evidence'] and thesis['falsifier']
    assert 'no Envoy attribution' in claims['BE-LBG-AI-VALUE']['caveat']
