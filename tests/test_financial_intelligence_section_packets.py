from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cios.applications.flora.financial_intelligence.openai_provider import OpenAIDirectPDFProvider
from cios.applications.flora.financial_intelligence.schema import ExperimentDocument, FoundationFactSet
from cios.applications.flora.financial_intelligence.section_packets import (
    ABSOLUTE_INPUT_TOKEN_CEILING,
    PACKET_MAX_OUTPUT_TOKENS,
    SectionAwareOpenAIProvider,
    build_page_packets,
    merge_packet_facts,
    select_candidate_pages,
    split_oversized_packet,
)
from cios.applications.flora.live.documents import DocumentPage


def doc(tmp_path: Path) -> ExperimentDocument:
    p = tmp_path / 'report.pdf'; p.write_bytes(b'%PDF fixture')
    return ExperimentDocument(document_id='DOC', enterprise_id='bt-group-plc', title='BT Annual Report', source_url='https://bt.test/report.pdf', retrieval_timestamp='2026-07-05T00:00:00+00:00', checksum='abc123', media_type='application/pdf', page_count=10, local_path=str(p))


def test_token_count_payload_excludes_max_output_but_generation_keeps_allowance(tmp_path: Path) -> None:
    provider = OpenAIDirectPDFProvider(model='gpt-5.4-nano', reasoning_effort='none', max_output_tokens=2000)
    d = doc(tmp_path)
    count_payload = provider._token_count_payload(d, FoundationFactSet, 'file_url', Path(d.local_path))
    gen_payload = provider._request_payload(d, FoundationFactSet, 'file_url', Path(d.local_path))
    assert 'max_output_tokens' not in count_payload
    assert gen_payload['max_output_tokens'] == 2000


def test_relevant_pages_selected_with_original_page_numbers() -> None:
    pages = [
        DocumentPage(1, 'Welcome'),
        DocumentPage(3, 'Financial highlights revenue £20bn adjusted EBITDA £8bn net debt £15bn'),
        DocumentPage(7, 'Group income statement operating profit cash flow statement capital expenditure'),
    ]
    selected = select_candidate_pages(pages)
    assert [p.page_number for p in selected] == [3, 7]
    assert selected[0].matched_terms


def test_full_pdf_is_never_submitted_as_one_extraction_request_and_every_packet_preflighted(monkeypatch, tmp_path: Path) -> None:
    calls: dict[str, list[dict[str, Any]]] = {'count': [], 'create': []}

    class Count:
        def count(self, **kwargs: Any) -> dict[str, int]:
            calls['count'].append(kwargs)
            assert 'max_output_tokens' not in kwargs
            text = json.dumps(kwargs)
            assert 'FULL PDF SENTINEL' not in text
            return {'input_tokens': 1000}

    class Responses:
        input_tokens = Count()
        def create(self, **kwargs: Any) -> Any:
            calls['create'].append(kwargs)
            assert kwargs['max_output_tokens'] == PACKET_MAX_OUTPUT_TOKENS
            return {'id': 'r', 'output_text': '{"facts": []}', 'usage': {'input_tokens': 1000, 'output_tokens': 10}}

    class Client:
        def __init__(self, **kwargs: Any):
            self.responses = Responses()

    monkeypatch.setitem(__import__('sys').modules, 'openai', type('OpenAIModule', (), {'OpenAI': Client}))
    pages = [DocumentPage(i, f'revenue adjusted EBITDA net debt £{i}m') for i in range(1, 8)] + [DocumentPage(10, 'FULL PDF SENTINEL')]
    extraction, plan = SectionAwareOpenAIProvider(OpenAIDirectPDFProvider(model='gpt-5.4-nano', reasoning_effort='none', max_output_tokens=2000)).extract_packets(doc(tmp_path), pages)
    assert extraction.status == 'completed'
    assert len(calls['create']) <= 4
    assert len(calls['count']) == len(calls['create'])
    assert plan['candidate_pages'] and 10 not in plan['candidate_pages']


def test_packets_above_ceiling_are_split() -> None:
    packet = build_page_packets([type('C', (), {'page_number': i, 'text': 'revenue £1m', 'score': 1})() for i in range(1, 5)], max_packets=1)[0]
    split = split_oversized_packet(packet)
    assert len(split) == 2
    assert all(p.page_numbers for p in split)
    assert ABSOLUTE_INPUT_TOKEN_CEILING == 75_000


def test_packet_results_are_merged_and_deduplicated(tmp_path: Path) -> None:
    from cios.applications.flora.financial_intelligence.schema import FoundationFact, ClaimType, FactState, ExtractionRun
    fact = FoundationFact(fact_id='f1', canonical_enterprise_id='bt-group-plc', claim_type=ClaimType.financial_metric_reported, subject_type='enterprise', subject_name='BT Group plc', predicate='revenue', object_type='metric', value_number=20.0, scale='bn', unit='GBP', currency='GBP', business_unit='BT Group', period_label='FY26', period_start=None, period_end=None, state=FactState.actual, source_document_id='DOC', source_page_start=3, source_page_end=3, source_excerpt='Revenue £20bn', extraction_confidence=0.9, explicit_in_source=True, extractor_provider='openai', extractor_model='gpt-5.4-nano', extractor_version='gpt-5.4-nano')
    run = ExtractionRun(run_id='r', route='x', provider='openai', model='gpt-5.4-nano', status='completed', started_at='x', completed_at='x', latency_seconds=0, facts=[fact, fact.model_copy(update={'fact_id':'f2'})])
    merged = merge_packet_facts([run], doc(tmp_path))
    assert len(merged.facts) == 1
