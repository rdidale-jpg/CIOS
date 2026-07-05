from __future__ import annotations

import json, sys, types
from pathlib import Path

from cios.applications.flora.financial_intelligence.config import financial_intelligence_settings
from cios.applications.flora.financial_intelligence.openai_provider import OpenAIDirectPDFProvider
from cios.applications.flora.financial_intelligence.schema import ExperimentDocument, FoundationFactSet, openai_strict_json_schema
from cios.applications.flora import document_review


def _doc(tmp_path: Path, checksum: str = 'hash') -> ExperimentDocument:
    pdf = tmp_path / 'bt.pdf'; pdf.write_bytes(b'%PDF-1.4 fixture')
    return ExperimentDocument(document_id='DOC', enterprise_id='bt-group-plc', title='BT', source_url='https://example.com/bt.pdf', retrieval_timestamp=document_review.now_iso(), checksum=checksum, media_type='application/pdf', page_count=1, local_path=str(pdf))


def test_low_cost_defaults_and_overrides(monkeypatch):
    monkeypatch.delenv('FLORA_FINANCIAL_INTELLIGENCE_MODEL', raising=False)
    monkeypatch.delenv('FLORA_DOCUMENT_UNDERSTANDING_MODEL', raising=False)
    settings = financial_intelligence_settings()
    assert settings.model == 'gpt-5.4-nano'
    assert settings.reasoning_effort == 'none'
    monkeypatch.setenv('FLORA_FINANCIAL_INTELLIGENCE_MODEL', 'gpt-custom')
    assert financial_intelligence_settings().model == 'gpt-custom'


def test_token_count_precedes_model_invocation_and_bounds_request(monkeypatch, tmp_path):
    calls = []
    class Count:
        def create(self, **kwargs):
            calls.append('count'); return {'input_tokens': 100}
    class Responses:
        input_tokens = Count()
        def create(self, **kwargs):
            calls.append(('create', kwargs));
            return types.SimpleNamespace(id='r1', output_text=json.dumps({'facts': []}), usage=types.SimpleNamespace(model_dump=lambda: {'input_tokens': 100, 'output_tokens': 5}), model_dump=lambda mode='json': {'id': 'r1', 'output_text': json.dumps({'facts': []}), 'usage': {'input_tokens': 100, 'output_tokens': 5}})
    class Client:
        def __init__(self, **kwargs): self.responses = Responses()
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    monkeypatch.setitem(sys.modules, 'openai', types.SimpleNamespace(OpenAI=Client))
    run = OpenAIDirectPDFProvider(model='gpt-low', max_output_tokens=123).extract_facts(_doc(tmp_path))
    assert run.status == 'completed'
    assert calls[0] == 'count'
    assert calls[1][0] == 'create'
    assert calls[1][1]['reasoning'] == {'effort': 'none'}
    assert calls[1][1]['max_output_tokens'] == 123


def test_cost_ceiling_blocks_model_invocation(monkeypatch, tmp_path):
    class Count:
        def create(self, **kwargs): return {'input_tokens': 10_000_000}
    class Responses:
        input_tokens = Count()
        def create(self, **kwargs): raise AssertionError('model invocation must be blocked')
    class Client:
        def __init__(self, **kwargs): self.responses = Responses()
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    monkeypatch.setitem(sys.modules, 'openai', types.SimpleNamespace(OpenAI=Client))
    run = OpenAIDirectPDFProvider(model='gpt-low', max_run_cost_usd=0.01).extract_facts(_doc(tmp_path))
    assert run.status == 'cost_limit_exceeded'


def test_successful_same_document_can_be_reused_without_provider_call(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_ROOT', str(tmp_path / 'data'))
    monkeypatch.setenv('FLORA_FINANCIAL_INTELLIGENCE_MODEL', 'gpt-5.4-nano')
    doc = _doc(tmp_path, checksum='same')
    document_review.ensure_writable_dir(document_review._run_dir())
    cached = {'run_id': 'fi-old', 'created_at': document_review.now_iso(), 'status': 'completed', 'document': doc.model_dump(), 'model': 'gpt-5.4-nano', 'schema_version': financial_intelligence_settings().schema_version, 'prompt_version': financial_intelligence_settings().prompt_version, 'claims': [], 'applied_results': []}
    document_review._write_json(document_review._run_path('fi-old'), cached)
    assert document_review._successful_cached_run(doc, 'gpt-5.4-nano')['run_id'] == 'fi-old'


def test_schema_still_valid_and_no_hard_coded_fallback():
    schema = openai_strict_json_schema(FoundationFactSet)
    assert schema['additionalProperties'] is False
    assert 'gpt-5.5' not in Path('cios/applications/flora/financial_intelligence/openai_provider.py').read_text()
