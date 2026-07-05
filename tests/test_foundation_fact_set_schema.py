from __future__ import annotations

from typing import Any

from cios.applications.flora.financial_intelligence.schema import (
    FoundationFactSet,
    openai_strict_json_schema,
)
from cios.applications.flora.financial_intelligence.openai_provider import OpenAIDirectPDFProvider
from cios.applications.flora import document_review


def _assert_openai_strict_objects(node: Any, path: str = '$') -> None:
    if isinstance(node, dict):
        properties = node.get('properties')
        if isinstance(properties, dict):
            assert set(node.get('required', [])) == set(properties.keys()), path
            assert node.get('additionalProperties') is False, path
        for key, value in node.items():
            _assert_openai_strict_objects(value, f'{path}.{key}')
    elif isinstance(node, list):
        for index, item in enumerate(node):
            _assert_openai_strict_objects(item, f'{path}[{index}]')


def test_foundation_fact_set_schema_is_openai_strict_and_keeps_lineage_fields() -> None:
    schema = openai_strict_json_schema(FoundationFactSet)

    _assert_openai_strict_objects(schema)
    assert set(schema['required']) == set(schema['properties'].keys())

    fact = schema['$defs']['FoundationFact']
    assert 'subject_id' in fact['properties']
    assert 'subject_id' in fact['required']
    assert 'source_document_id' in fact['required']
    assert 'source_page_start' in fact['required']
    assert 'period_label' in fact['required']
    assert 'value' in fact['required']
    assert 'value_text' not in fact['properties']
    assert 'value_number' not in fact['properties']
    assert 'value' in fact['properties']


def test_openai_provider_uses_canonical_strict_foundation_fact_set_schema() -> None:
    captured: dict[str, Any] = {}

    class Responses:
        def create(self, **kwargs: Any) -> None:
            captured.update(kwargs)
            raise RuntimeError('stop before provider call')

    class Client:
        responses = Responses()

    provider = OpenAIDirectPDFProvider(model='gpt-test')

    try:
        provider._invoke(Client(), type('Doc', (), {'source_url': 'https://example.test/report.pdf'})(), FoundationFactSet, 'file_url', None)
    except RuntimeError:
        pass

    runtime_schema = captured['text']['format']['schema']
    assert runtime_schema == openai_strict_json_schema(FoundationFactSet)
    _assert_openai_strict_objects(runtime_schema)


def test_invalid_json_schema_is_provider_request_invalid_and_non_retryable(monkeypatch, tmp_path) -> None:
    pdf = tmp_path / 'bt.pdf'
    pdf.write_bytes(b'%PDF-1.4\nfixture')
    doc = document_review.ExperimentDocument(
        document_id='DOC', enterprise_id='bt-group-plc', title='BT Annual Report',
        source_url='https://www.bt.com/report.pdf', retrieval_timestamp=document_review.now_iso(),
        checksum='x', media_type='application/pdf', page_count=1, local_path=str(pdf),
    )

    class InvalidSchemaError(Exception):
        status_code = 400
        code = 'invalid_json_schema'

    class Responses:
        def create(self, **kwargs: Any) -> None:
            raise InvalidSchemaError('invalid_json_schema')

    class Client:
        def __init__(self, **kwargs: Any):
            self.responses = Responses()

    monkeypatch.setenv('OPENAI_API_KEY', 'sk-secret-value')
    monkeypatch.setattr('cios.applications.flora.financial_intelligence.openai_provider.openai_sdk_readiness', lambda: {'available': True})
    monkeypatch.setitem(__import__('sys').modules, 'openai', type('OpenAIModule', (), {'OpenAI': Client}))

    run = OpenAIDirectPDFProvider(model='gpt-test').extract_facts(doc, correlation_id='schema-1')

    assert run.status == 'provider_request_invalid'
    assert run.diagnostics[-1]['provider_error_code'] == 'invalid_json_schema'
    assert run.diagnostics[-1]['retryable'] is False
    assert document_review._provider_failure_category(run) == 'provider_request_invalid'
