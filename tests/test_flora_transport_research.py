"""Research-only integrity and negative cases; no live services or canonical writes."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

PACK = Path(__file__).resolve().parents[1] / 'docs/flora-runtime/uk-transport-twin-research'
spec = importlib.util.spec_from_file_location('transport_documentary_qa', PACK / 'validate.py')
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


def test_bounded_pack_and_preserved_owners():
    counts = qa.validate()
    assert counts['subindustries'] == 8 and counts['dossiers'] == 12


@pytest.mark.parametrize('recipe', qa.read('Calculations.json'), ids=lambda x: x['id'])
def test_original_inputs_reproduce(recipe):
    qa.check_calculation(recipe, qa.index(qa.read('Measurements.json')))


@pytest.mark.parametrize('field,value', [
    ('entity_id', 'NRIL'), ('period', '2024/25'), ('basis', 'statutory IFRS'),
    ('currency', 'EUR'), ('unit', 'billion'), ('measurement_state', 'plan'),
    ('stock_flow', 'stock'), ('semantic_type', 'estimated'), ('semantic_type', 'assumption'),
    ('value', 'NaN'), ('value', 'Infinity'), ('value', '999999')])
def test_financial_context_and_finiteness_rejected(field, value):
    recipe = qa.read('Calculations.json')[0]
    m = qa.index(qa.read('Measurements.json'))
    m[recipe['terms'][0]['measurement_id']][field] = value
    with pytest.raises(AssertionError):
        qa.check_calculation(recipe, m)


def test_reported_rounding_residual_not_silently_changed():
    recipe = next(x for x in qa.read('Calculations.json') if x['id'] == 'TFL-rounded')
    assert qa.check_calculation(recipe, qa.index(qa.read('Measurements.json'))) == qa.Decimal('7')
    assert recipe['expected'] == '6'
    bad = deepcopy(qa.read('Calculations.json')[0]); bad['tolerance'] = '100000'
    with pytest.raises(AssertionError, match='undeclared tolerance'):
        qa.check_calculation(bad, qa.index(qa.read('Measurements.json')))


def test_withdrawal_invalidates_financial_input_and_documentary_descendants_only():
    alive = qa.documentary_survivors(qa.read('Claims.json'), ['NR-REG'])
    assert not {'NR-1', 'NR-2', 'IN-NR', 'HY-NR'} & alive
    assert {'NR-3', 'IN-IAG', 'IN-TFL'} <= alive
    with pytest.raises(AssertionError, match='withdrawn'):
        qa.check_calculation(qa.read('Calculations.json')[0], qa.index(qa.read('Measurements.json')), ['NR-REG'])


def test_missing_source_and_inference_cycle_rejected():
    claims = qa.index(qa.read('Claims.json')); sources = qa.index(qa.read('Sources.json'))
    entities = qa.index(qa.read('Entities.json'))
    del sources['NR-REG']
    with pytest.raises(AssertionError, match='missing source'):
        qa.claim_check(claims['NR-1'], sources, entities, claims)
    claims['NR-1']['input_claim_ids'] = ['HY-NR']
    with pytest.raises(AssertionError, match='cyclic'):
        qa.documentary_survivors(list(claims.values()))


@pytest.mark.parametrize('field,value', [('canonical_acceptance', True), ('public_source_admission', True),
                                      ('original_bytes_sha256', 'invented'), ('published_on', '2027-01-01')])
def test_no_fabricated_authority_archives_or_future_publication(field, value):
    source = deepcopy(qa.read('Sources.json')[0]); source[field] = value
    with pytest.raises(AssertionError):
        qa.source_check(source)


@pytest.mark.parametrize('edge', [e for e in qa.read('Relationships.json') if e['status'] == 'rejected_join'], ids=lambda e: e['id'])
def test_each_negative_join_stays_rejected(edge):
    bad = deepcopy(edge); bad['status'] = 'supported_candidate'
    with pytest.raises(AssertionError, match='unsupported'):
        qa.edge_check(bad, qa.index(qa.read('Entities.json')), qa.index(qa.read('Sources.json')))


def test_invalid_endpoint_or_fictional_contract_not_admitted():
    edge = deepcopy(qa.read('Relationships.json')[0]); edge['to_entity'] = 'invented-bank'
    with pytest.raises(AssertionError, match='endpoint'):
        qa.edge_check(edge, qa.index(qa.read('Entities.json')), qa.index(qa.read('Sources.json')))
    edge = deepcopy(qa.read('Relationships.json')[0]); edge['contract_value'] = '£100m'
    with pytest.raises(AssertionError):
        qa.edge_check(edge, qa.index(qa.read('Entities.json')), qa.index(qa.read('Sources.json')))


def test_current_and_proposed_identity_and_undated_event_remain_explicit():
    entities = qa.index(qa.read('Entities.json'))
    assert entities['GBR']['kind'] == 'proposed_public_body'
    assert entities['DFTO']['identity_basis'].startswith('Companies House 07141122')
    assert entities['IDS']['identity_basis'].startswith('Companies House 08680755')
    assert entities['EASYJET']['canonical_identity']['research_enterprise_id'] == 'AV-ENT-001'
    assert entities['EASYJET']['canonical_identity']['accepted_model_id'] is None
    sources = qa.index(qa.read('Sources.json'))
    assert sources['IAG-SKY']['published_on'] is None
    assert sources['HEATHROW-PDF']['exception'] and sources['TFL']['acquisition_extent'].startswith('original report')
