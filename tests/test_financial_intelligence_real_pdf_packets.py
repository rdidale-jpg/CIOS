from __future__ import annotations

import base64
from pathlib import Path

import pytest

from cios.applications.flora.financial_intelligence.candidate_validation import parse_foundation_fact_candidates
from cios.applications.flora.financial_intelligence.schema import ExperimentDocument
from cios.applications.flora.financial_intelligence.section_packets import (
    PageCandidate,
    _packet_payload,
    build_real_page_packets,
    validate_packet_pdf_bytes,
)


def test_pymupdf_is_declared_as_production_dependency() -> None:
    assert 'PyMuPDF' in Path('requirements.txt').read_text()


def test_placeholder_extraction_messages_never_become_candidate_facts() -> None:
    parsed, exceptions, status = parse_foundation_fact_candidates(
        '{"facts":[{"source_excerpt":"[EXTRACT NOT AVAILABLE: Packet page 8 content not provided in prompt.]"}]}',
        packet_id='packet-1', provider='openai', model='gpt-5.4-nano'
    )
    assert parsed.facts == []
    assert status == 'packet_content_unavailable'
    assert exceptions[0]['exception_type'] == 'packet_content_unavailable'


def _fitz():
    return pytest.importorskip('fitz', reason='PyMuPDF is required for real PDF packet byte tests')


def _pdf(tmp_path: Path, page_count: int = 5) -> Path:
    fitz = _fitz()
    path = tmp_path / 'fixture.pdf'
    doc = fitz.open()
    for idx in range(page_count):
        page = doc.new_page()
        page.insert_text((72, 72), f'Original page {idx + 1} revenue £{idx + 1}m adjusted EBITDA')
    doc.save(path)
    doc.close()
    return path


def _document(path: Path, page_count: int) -> ExperimentDocument:
    return ExperimentDocument(document_id='DOC', enterprise_id='bt-group-plc', title='Fixture Annual Report', source_url='https://example.test/report.pdf', retrieval_timestamp='2026-07-05T00:00:00+00:00', checksum='sha', media_type='application/pdf', page_count=page_count, local_path=str(path))


def test_selected_pages_are_copied_to_non_empty_packet_with_original_mapping(tmp_path: Path) -> None:
    path = _pdf(tmp_path, 5)
    packets = build_real_page_packets([PageCandidate(2, 50, ('revenue',), 'Revenue £2m')], _document(path, 5), max_packets=1)
    assert packets[0].pdf_bytes
    assert packets[0].byte_size > 0
    assert packets[0].page_count == 4
    assert packets[0].packet_page_to_original == {1: 2, 2: 3, 3: 4, 4: 5}


def test_provider_input_contains_pdf_file_data_not_page_number_only(tmp_path: Path) -> None:
    path = _pdf(tmp_path, 3)
    packet = build_real_page_packets([PageCandidate(1, 50, ('revenue',), 'Revenue £1m')], _document(path, 3), max_packets=1)[0]
    payload = _packet_payload(type('P', (), {'model': 'gpt-5.4-nano', 'reasoning_effort': 'none'})(), _document(path, 3), packet, __import__('cios.applications.flora.financial_intelligence.schema', fromlist=['ProviderFoundationFactSet']).ProviderFoundationFactSet)
    content = payload['input'][0]['content']
    file_item = content[0]
    assert file_item['type'] == 'input_file'
    assert file_item['file_data'].startswith('data:application/pdf;base64,')
    assert base64.b64decode(file_item['file_data'].split(',', 1)[1]) == packet.pdf_bytes


def test_zero_byte_or_zero_page_packets_fail_locally() -> None:
    with pytest.raises(ValueError, match='byte size is zero'):
        validate_packet_pdf_bytes(b'', (1,))
    with pytest.raises(ValueError, match='zero selected'):
        validate_packet_pdf_bytes(b'%PDF', ())
