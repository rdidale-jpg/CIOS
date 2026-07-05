from __future__ import annotations
import json
import pytest
from pydantic import ValidationError
from cios.applications.flora.financial_intelligence.candidate_validation import parse_foundation_fact_candidates
from cios.applications.flora.financial_intelligence.schema import FoundationFact, FoundationFactSet, ProviderFoundationFact, openai_strict_json_schema


def candidate(**kw):
    base = dict(fact_id='f1', canonical_enterprise_id='bt-group-plc', claim_type='financial_metric_reported', subject_type='enterprise', subject_name='BT Group plc', subject_id=None, predicate='revenue', object_type='metric', value={'kind':'numeric','amount':'20.8','scale':'bn','unit':'GBP','currency':'GBP'}, business_unit='BT Group', period_label='FY26', period_start=None, period_end=None, state='actual', source_document_id='DOC', source_page_start=3, source_page_end=3, source_excerpt='Revenue was £20.8bn.', extraction_confidence=0.9, explicit_in_source=True, extractor_provider='openai', extractor_model='gpt-5.5', extractor_version='gpt-5.5')
    base.update(kw)
    return base


def parse(facts):
    return parse_foundation_fact_candidates(json.dumps({'facts': facts}), packet_id='packet-1', provider='openai', model='gpt-5.5')


def test_candidate_with_two_value_fields_is_rejected_individually():
    bad = candidate(value_text='revenue text')
    good = candidate(fact_id='f2')
    parsed, exceptions, status = parse([bad, good])
    assert status == 'completed_with_exceptions'
    assert [f.fact_id for f in parsed.facts] == ['f2']
    assert exceptions[0]['exception_type'] == 'candidate_fact_validation_failed'
    assert set(exceptions[0]['populated_value_fields']) == {'value', 'value_text'}


def test_candidate_with_no_value_is_rejected_individually():
    bad = candidate(); bad.pop('value')
    parsed, exceptions, status = parse([bad])
    assert status == 'provider_response_invalid'
    assert parsed.facts == []
    assert exceptions[0]['fact_id'] == 'f1'
    assert exceptions[0]['populated_value_fields'] == []


def test_valid_candidates_same_packet_still_proceed_and_invalid_quarantined():
    bad = candidate(fact_id='bad'); bad.pop('value')
    good = candidate(fact_id='good')
    parsed, exceptions, status = parse([bad, good])
    assert status == 'completed_with_exceptions'
    assert len(parsed.facts) == 1
    assert parsed.facts[0].fact_id == 'good'
    assert exceptions[0]['machine_candidate']['fact_id'] == 'bad'


def provider_candidate(**kw):
    c = candidate()
    c.pop('value')
    c.update(dict(value_kind='numeric', numeric_value='20.8', text_value=None, date_value=None, boolean_value=None))
    c.update(kw)
    return c


def test_provider_numeric_text_date_and_boolean_map_to_canonical_values():
    facts = [
        provider_candidate(fact_id='n', value_kind='numeric', numeric_value='20.8', text_value=None, date_value=None, boolean_value=None),
        provider_candidate(fact_id='t', claim_type='strategic_pillar_stated', state='current', value_kind='text', numeric_value=None, text_value='cost transformation', date_value=None, boolean_value=None, currency=None, unit=None, scale=None),
        provider_candidate(fact_id='d', claim_type='executive_appointment_announced', state='announced', value_kind='date', numeric_value=None, text_value=None, date_value='2026-04-01', boolean_value=None, currency=None, unit=None, scale=None),
        provider_candidate(fact_id='b', claim_type='enterprise_identity_confirmed', state='current', value_kind='boolean', numeric_value=None, text_value=None, date_value=None, boolean_value=True, currency=None, unit=None, scale=None),
    ]
    parsed, exceptions, status = parse(facts)
    assert status == 'completed'
    assert not exceptions
    assert [f.value.kind for f in parsed.facts] == ['numeric','text','date','boolean']


def test_provider_multiple_value_fields_quarantines_only_that_candidate():
    bad = provider_candidate(fact_id='bad', text_value='extra')
    good = provider_candidate(fact_id='good')
    parsed, exceptions, status = parse([bad, good])
    assert status == 'completed_with_exceptions'
    assert [f.fact_id for f in parsed.facts] == ['good']
    assert exceptions[0]['fact_id'] == 'bad'


def test_validation_diagnostics_include_exact_provider_field_locations():
    bad = provider_candidate(fact_id='bt-p1-revenue', extractor_provider='user_provided', extractor_model=None, extractor_version=None)
    parsed, exceptions, status = parse_foundation_fact_candidates(json.dumps({'facts': [bad]}), packet_id='packet-1', provider='user_provided', model='')
    assert status == 'provider_response_invalid'
    assert parsed.facts == []
    fields = {tuple(e['field_location']) for e in exceptions[0]['validation_errors']}
    assert ('extractor_model',) in fields
    assert ('extractor_version',) in fields
    assert {e['candidate_id'] for e in exceptions[0]['validation_errors']} == {'bt-p1-revenue'}
    assert {e['packet_id'] for e in exceptions[0]['validation_errors']} == {'packet-1'}


def test_stored_packet_one_regression_revalidates_with_runtime_provenance_and_single_provider_validation(monkeypatch):
    facts = [
        provider_candidate(fact_id='p1-revenue', predicate='Revenue', numeric_value='19.7', scale='bn', unit='billion', source_excerpt='Revenue £19.7bn', extractor_provider='user_provided', extractor_model=None, extractor_version=None),
        provider_candidate(fact_id='p1-adjusted-ebitda', predicate='Adjusted EBITDA', numeric_value='8.2', scale='bn', unit='billion', source_excerpt='Adjusted EBITDA £8.2bn', extractor_provider='user_provided', extractor_model=None, extractor_version=None),
        provider_candidate(fact_id='p1-capex', predicate='Capital expenditure', numeric_value='5.1', scale='bn', unit='billion', source_excerpt='Capital expenditure £5.1bn', extractor_provider='user_provided', extractor_model=None, extractor_version=None),
        provider_candidate(fact_id='p1-ocf', predicate='Cash flow from operating activities', numeric_value='7.0', scale='bn', unit='billion', source_excerpt='Cash flow from operating activities £7.0bn', extractor_provider='user_provided', extractor_model=None, extractor_version=None),
        provider_candidate(fact_id='p1-nfcf', predicate='Normalised free cash flow', numeric_value='1.5', scale='bn', unit='billion', source_excerpt='Normalised free cash flow £1.5bn', extractor_provider='user_provided', extractor_model=None, extractor_version=None),
    ]
    calls = {'count': 0}
    original = ProviderFoundationFact.model_validate

    def counted(value, *args, **kwargs):
        calls['count'] += 1
        return original(value, *args, **kwargs)

    monkeypatch.setattr(ProviderFoundationFact, 'model_validate', counted)
    parsed, exceptions, status = parse_foundation_fact_candidates(
        json.dumps({'facts': facts}), packet_id='packet-1', provider='openai', model='gpt-5.4-nano',
        request_id='resp_07843598d30e9a5f006a4a5911f57c819e9ce03e825aac62e7', packet_page_map={3: 3}
    )
    assert status == 'completed'
    assert exceptions == []
    assert calls['count'] == 5
    assert [f.extractor_provider for f in parsed.facts] == ['openai'] * 5
    assert [f.extractor_model for f in parsed.facts] == ['gpt-5.4-nano'] * 5
    assert [f.subject_id for f in parsed.facts] == ['bt-group-plc'] * 5
    assert parsed.facts[0].scale == 'bn'
    assert parsed.facts[0].unit == 'billion'

def test_entirely_invalid_response_returns_provider_response_invalid_without_unhandled_exception():
    parsed, exceptions, status = parse_foundation_fact_candidates('{bad json', packet_id='packet-1', provider='openai', model='gpt-5.5')
    assert status == 'provider_response_invalid'
    assert parsed.facts == []
    assert exceptions


def test_provider_schema_replaces_canonical_union_for_openai():
    schema = openai_strict_json_schema(FoundationFactSet)
    assert 'oneOf' not in json.dumps(schema)
    fact = schema['$defs']['ProviderFoundationFact']
    assert {'value_kind','numeric_value','text_value','date_value','boolean_value'} <= set(fact['properties'])
    assert set(fact['required']) == set(fact['properties'])
    assert 'value' not in fact['properties']


def test_discriminated_value_representation_accepts_exactly_one_type():
    assert FoundationFact.model_validate(candidate(value={'kind':'text','text':'stable outlook'})).value.kind == 'text'
    with pytest.raises(ValidationError):
        FoundationFact.model_validate(candidate(value={'kind':'numeric','amount':'1', 'text':'extra', 'scale':None,'unit':None,'currency':None}))
