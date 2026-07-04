import json, os
from pathlib import Path
import pytest
from pydantic import ValidationError
from experiments.document_understanding.schema import FoundationFact, FoundationFactSet, ClaimType, FactState, ExperimentDocument
from experiments.document_understanding.providers import OpenAIDirectPDFProvider, AnthropicDirectPDFProvider, LayoutOpenAIProvider
from experiments.document_understanding.verification import verify_fact

def fact(**kw):
    base=dict(fact_id='f1',canonical_enterprise_id='bt-group-plc',claim_type='financial_metric_reported',subject_type='enterprise',subject_name='BT Group plc',subject_id=None,predicate='reported revenue',object_type='financial_metric',value_text=None,value_number=20.4,scale='billion',unit=None,currency='GBP',business_unit=None,period_label='FY26',period_start='2025-04-01',period_end='2026-03-31',state='actual',source_document_id='doc',source_page_start=1,source_page_end=1,source_excerpt='Revenue £20.4 billion FY26',extraction_confidence=.9,explicit_in_source=True,extractor_provider='test',extractor_model='test',extractor_version='v')
    base.update(kw); return FoundationFact(**base)

def test_schema_strict_unknown_fields_rejected():
    with pytest.raises(ValidationError): FoundationFactSet(facts=[], extra_field=True)
    with pytest.raises(ValidationError): fact(extra_field=True)

def test_unsupported_claim_type_rejected():
    with pytest.raises(ValidationError): fact(claim_type='commercial_pressure')

def test_one_fact_contains_one_metric_or_relationship():
    with pytest.raises(ValidationError): fact(value_text='twenty point four', value_number=20.4)
    assert fact(value_number=20.4)

def test_actual_target_guidance_distinct():
    assert fact(claim_type=ClaimType.financial_metric_reported,state=FactState.actual)
    with pytest.raises(ValidationError): fact(claim_type=ClaimType.financial_guidance_stated,state=FactState.actual)
    assert fact(claim_type=ClaimType.financial_guidance_stated,state=FactState.guidance,predicate='guided revenue')
    assert fact(claim_type=ClaimType.financial_target_stated,state=FactState.target,predicate='targeted revenue')

def test_provider_adapters_return_canonical_result_type(monkeypatch, tmp_path):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False); monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False); monkeypatch.delenv('GOOGLE_APPLICATION_CREDENTIALS', raising=False); monkeypatch.delenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', raising=False); monkeypatch.delenv('AZURE_DOCUMENT_INTELLIGENCE_KEY', raising=False)
    doc=ExperimentDocument(document_id='d',enterprise_id='bt',title='t',source_url='',retrieval_timestamp='now',checksum='x',media_type='application/pdf',page_count=1,local_path=str(tmp_path/'missing.pdf'))
    for provider in (OpenAIDirectPDFProvider(), AnthropicDirectPDFProvider(), LayoutOpenAIProvider()):
        run=provider.extract_facts(doc, FoundationFactSet)
        assert run.status=='not_executed'
        assert isinstance(run.provider_errors, list)
        assert run.latency_seconds == 0

def test_raw_provider_responses_are_not_observations():
    run=OpenAIDirectPDFProvider().extract_facts(ExperimentDocument(document_id='d',enterprise_id='bt',title='t',source_url='',retrieval_timestamp='now',checksum='x',media_type='application/pdf',page_count=1,local_path=None),FoundationFactSet)
    assert not hasattr(run, 'observations')
    assert run.raw_response_location is None

def test_page_references_required_and_excerpt_bounded():
    with pytest.raises(ValidationError): fact(source_page_start=0)
    with pytest.raises(ValidationError): fact(source_excerpt='x'*421)

def test_deterministic_verification_detects_incorrect_values():
    ok=verify_fact(fact(), {1:'Revenue £20.4 billion FY26'})
    bad=verify_fact(fact(value_number=21.0), {1:'Revenue £20.4 billion FY26'})
    assert ok.status=='supported'
    assert bad.status=='unsupported'

def test_unsupported_facts_cannot_pass_verification():
    res=verify_fact(fact(source_excerpt='Adjusted EBITDA £8.2 billion FY26'), {1:'Revenue £20.4 billion FY26'})
    assert res.status=='unsupported'

def test_missing_credentials_produce_not_executed(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    doc=ExperimentDocument(document_id='d',enterprise_id='bt',title='t',source_url='',retrieval_timestamp='now',checksum='x',media_type='application/pdf',page_count=1,local_path=None)
    assert OpenAIDirectPDFProvider().extract_facts(doc,FoundationFactSet).status == 'not_executed'

def test_cost_and_latency_metadata_recorded(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    doc=ExperimentDocument(document_id='d',enterprise_id='bt',title='t',source_url='',retrieval_timestamp='now',checksum='x',media_type='application/pdf',page_count=1,local_path=None)
    run=OpenAIDirectPDFProvider().extract_facts(doc,FoundationFactSet)
    assert run.latency_seconds >= 0
    assert run.estimated_cost_usd is None

def test_experiment_outputs_contain_no_secrets():
    text=Path('docs/Architecture/experiments/results/BT_Document_Understanding_Summary.json').read_text()
    assert 'sk-' not in text and 'api_key' not in text.lower()
    data=json.loads(text); assert data['contains_secrets'] is False

def test_production_collection_behaviour_unchanged():
    src=Path('cios/applications/flora/live/collect.py').read_text()+Path('cios/applications/flora/live/documents.py').read_text()
    assert 'experiments.document_understanding' not in src
