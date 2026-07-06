from pathlib import Path

import pytest

from cios.applications.flora.financial_intelligence.page_aware_pdf import parse_page_aware_pdf, parser_version


def _make_pdf(path: Path, pages: list[str]) -> None:
    fitz = pytest.importorskip('fitz')
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        if text:
            page.insert_text((72, 72), text, fontsize=10, fontname='courier')
    doc.save(str(path))
    doc.close()


def test_page_aware_parser_dependency_is_available() -> None:
    assert parser_version() != 'unavailable'


def test_page_aware_parser_retains_page_text_and_tolerates_empty_irrelevant_page(tmp_path: Path) -> None:
    pdf = tmp_path / 'structural-bt-family.pdf'
    _make_pdf(pdf, ['BT Group plc\nFY26', '', 'Group statutory results\nGBP m\nRevenue | 1 | 0 | statutory | Group'])
    parsed = parse_page_aware_pdf(pdf)
    assert parsed.status == 'parsed'
    assert parsed.page_count == 3
    assert parsed.pages_successfully_read == (1, 3)
    assert [e['page_number'] for e in parsed.page_errors] == [2]
    assert 'Revenue' in parsed.pages[2].text


def test_page_aware_parser_rejects_unreadable_pdf(tmp_path: Path) -> None:
    pdf = tmp_path / 'blank.pdf'
    _make_pdf(pdf, ['', ''])
    parsed = parse_page_aware_pdf(pdf)
    assert parsed.status == 'failed'
    assert parsed.failure_class == 'no_meaningful_text'
