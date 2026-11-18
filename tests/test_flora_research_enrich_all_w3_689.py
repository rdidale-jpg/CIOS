"""Bounded documentary QA. Mutations prove rejection; no network or runtime stores."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

PACK = Path(__file__).resolve().parents[1]/'docs/flora-runtime/research-enrich-all-w3-689'
spec = importlib.util.spec_from_file_location('w3_research_qa', PACK/'validate.py')
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


def test_complete_pack_and_research_only_boundary():
    counts = qa.validate()
    assert counts['actor_occurrences'] == 76 and counts['design_keys'] == 16


@pytest.mark.parametrize('recipe', qa.read('Financial-Reconciliations.json'), ids=lambda x: x['id'])
def test_original_transcription_reconciles(recipe):
    assert qa.check_bridge(recipe, qa.index(qa.read('Financial-Measurements.json'))) == qa.Decimal(recipe['expected'])


@pytest.mark.parametrize('field,value', [
    ('subject_key', 'wrong legal bank'), ('reporting_period', 'wrong quarter'),
    ('currency', 'EUR'), ('unit', 'billion'), ('basis', 'target/adjusted'),
    ('stock_flow', 'stock'), ('measurement_state', 'target'),
    ('semantic_type', 'estimated'), ('semantic_type', 'assumed'),
    ('value', 'NaN'), ('value', '999999')])
def test_wrong_context_or_numeric_semantics_fail_closed(field, value):
    r = qa.read('Financial-Reconciliations.json')[0]
    m = qa.index(qa.read('Financial-Measurements.json'))
    m[r['input_terms'][0]['measurement_id']][field] = value
    with pytest.raises(AssertionError):
        qa.check_bridge(r, m)


def test_withdrawal_removes_exact_fact_and_all_dependent_interpretations():
    c = qa.read('Claims.json')
    alive = qa.survivors(c, ['LBG-ENVOY'])
    assert 'LBG-4' not in alive and 'I-LBG' not in alive and 'I-GOOG' not in alive
    assert {'I-NWG', 'I-HOL', 'I-COV'} <= alive


def test_source_removal_does_not_leave_orphaned_public_claim():
    c = qa.index(qa.read('Claims.json'))
    s = qa.index(qa.read('Sources.json'))
    del s['LBG-ENVOY']
    with pytest.raises(AssertionError):
        qa.claim_check(c['LBG-4'], s, c)


def test_documentary_cycles_rejected():
    c = deepcopy(qa.read('Claims.json'))
    lookup = qa.index(c)
    lookup['LBG-1']['input_claim_ids'] = ['I-LBG']
    with pytest.raises(AssertionError, match='cyclic'):
        qa.survivors(c)


def test_unsupported_proposition_cannot_pass():
    c = qa.index(qa.read('Claims.json'))
    bad = deepcopy(c['LBG-1'])
    bad['source_ids'] = []
    with pytest.raises(AssertionError, match='unsupported'):
        qa.claim_check(bad, qa.index(qa.read('Sources.json')), c)


def test_public_canonical_or_archive_authority_cannot_be_invented():
    s = deepcopy(qa.read('Sources.json')[0])
    for key, value in [('canonical_acceptance', True), ('public_use', 'granted'),
                       ('original_bytes_sha256', 'fabricated')]:
        bad = dict(s, **{key: value})
        with pytest.raises(AssertionError):
            qa.source_check(bad)


def test_collision_and_related_dossier_are_not_identity_or_economic_aliases():
    assert not qa.same_owner_identity(('LegacyManifest', 'BK-ENT-003'), ('BankingPortfolio', 'BK-ENT-003'))
    rows = {x['original_actor_id']: x for x in qa.read('Banking-Portfolio-Crosswalk.json')['occurrence_rows']}
    assert rows['actor:barclays']['dossier_id'] == 'barclays'
    assert rows['actor:barclays']['exact_new_research_subject'] is None
    assert rows['actor:barclays']['candidate_research_readiness'] == 'Unavailable'
    assert rows['actor:tsb']['related_research_claims'] == []


def test_estimated_proxy_and_latest_actual_remain_different():
    c = qa.index(qa.read('Claims.json'))
    assert c['STAR-3']['semantic_type'] == 'estimated'
    assert c['NVDA-1']['reporting_period'] != c['NVDA-2']['reporting_period']
    assert 'interim CEO' in c['NVDA-2']['statement']


def test_exact_actor_event_and_participant_roles_survive_group_isolation():
    rows = {x['original_actor_id']: x for x in qa.read('Banking-Portfolio-Crosswalk.json')['occurrence_rows']}
    bank = rows['actor:barclays-uk']
    assert bank['exact_new_research_subject'] is None
    assert bank['exact_element_bindings'][0]['claim_ids'] == ['BARC-3']
    assert bank['exact_element_bindings'][0]['financial_metric_binding'] is False
    assert rows['actor:natwest']['exact_element_bindings'][0]['edge_ids'] == ['e-chaps-natwest']
    assert rows['actor:lloyds']['exact_element_bindings'][0]['candidate_Facts'] == 'Partial'


def test_operator_roles_and_prohibited_joins_stay_separate():
    e = qa.index(qa.read('Typed-Relationships.json'))
    assert e['e-chaps-lloyds']['predicate'] == 'listed_direct_participant_of'
    assert e['e-envoy']['to_subject'] == 'GOOGLE::CloudBrand'
    assert e['n-envoy']['status'] == 'rejected_join'
    assert e['n-payuk']['status'] == 'rejected_join'
    assert e['n-demand']['status'] == 'rejected_join'
