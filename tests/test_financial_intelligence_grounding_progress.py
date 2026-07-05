import json

from cios.applications.flora.financial_intelligence.candidate_validation import parse_foundation_fact_candidates


def provider_fact(**overrides):
    base = {
        'fact_id':'f1','canonical_enterprise_id':'bt-group-plc','claim_type':'financial_metric_reported',
        'subject_type':'enterprise','subject_name':'BT Group plc','subject_id':None,
        'predicate':'reported revenue','object_type':'financial_metric','value_kind':'numeric',
        'numeric_value':'20.8','text_value':None,'date_value':None,'boolean_value':None,
        'currency':'GBP','unit':None,'scale':'bn','business_unit':'BT Group plc','period_label':'FY2026',
        'period_start':None,'period_end':None,'state':'actual','source_document_id':'DOC',
        'source_page_start':1,'source_page_end':1,'packet_page_number':1,'original_pdf_page_number':None,
        'source_excerpt':'Revenue was £20.8bn.','extraction_confidence':0.91,'explicit_in_source':True,
        'extractor_provider':'openai','extractor_model':'gpt-5.4-nano','extractor_version':'financial-material-facts-v1'
    }
    base.update(overrides)
    return base


def test_packet_page_one_maps_to_original_pdf_page_three_and_persists_both_refs():
    parsed, exceptions, status = parse_foundation_fact_candidates(
        json.dumps({'facts':[provider_fact()]}), packet_id='packet-1', provider='openai', model='gpt-5.4-nano', packet_page_map={1:3,2:4}
    )
    assert status == 'completed'
    assert not exceptions
    fact = parsed.facts[0]
    assert fact.packet_page_number == 1
    assert fact.original_pdf_page_number == 3
    assert fact.source_page_start == 3


def test_packet_local_page_valid_not_rejected_and_out_of_range_quarantined_individually():
    good = provider_fact(fact_id='good', packet_page_number=1, source_page_start=1, source_page_end=1)
    bad = provider_fact(fact_id='bad', packet_page_number=9, source_page_start=9, source_page_end=9)
    parsed, exceptions, status = parse_foundation_fact_candidates(
        json.dumps({'facts':[good, bad]}), packet_id='packet-1', provider='openai', model='gpt-5.4-nano', packet_page_map={1:3}
    )
    assert status == 'completed_with_exceptions'
    assert [f.fact_id for f in parsed.facts] == ['good']
    assert exceptions[0]['fact_id'] == 'bad'
    assert exceptions[0]['validation_error_code'] == 'packet_page_out_of_range'
    assert exceptions[0]['returned_page_reference'] == 9
    assert exceptions[0]['supporting_excerpt_length'] > 0
    assert exceptions[0]['deterministic_repair_possible'] is False
