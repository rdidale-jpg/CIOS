from __future__ import annotations
import json
import pytest
from pydantic import ValidationError
from cios.applications.flora.financial_intelligence.candidate_validation import parse_foundation_fact_candidates
from cios.applications.flora.financial_intelligence.schema import FoundationFact, FoundationFactSet, openai_strict_json_schema


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
