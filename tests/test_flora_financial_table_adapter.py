from cios.applications.flora.financial_intelligence.adapters import PdfFinancialTableAdapter
from cios.applications.flora.financial_intelligence.pdf_document_adapter import CanonicalPdfDocument, CanonicalPdfPage, ParserAttempt
from cios.applications.flora.financial_intelligence.schema import ExperimentDocument


def _doc(text):
    exp = ExperimentDocument(document_id='DOC', enterprise_id='bt-group-plc', title='BT', source_url='file://bt.pdf', retrieval_timestamp='2026-07-05T00:00:00+00:00', checksum='abc', media_type='application/pdf', page_count=1, local_path='')
    page = CanonicalPdfPage(0, 42, None, text, (text,), ('Financial highlights',), len(text), 1, .5, 1, 'DOC', 'embedded_text')
    attempt = ParserAttempt('embedded_text','parsed',1,1,len(text),len(text),1,.5,0,False,True,'text_extraction_usable',1)
    return CanonicalPdfDocument(exp, (page,), (attempt,), 'embedded_text', 'text_extraction_usable', {})


def test_pdf_financial_table_adapter_extracts_visible_row_column_period_and_table_scale():
    text = 'Financial highlights\n£m\nYear ended 31 March 2026\nRevenue 19,654\nAdjusted EBITDA 8,230'
    result = PdfFinancialTableAdapter().extract_from_canonical(_doc(text))
    revenue = next(c for c in result.candidates if c.raw_metric_label.lower() == 'revenue')
    assert revenue.reported_amount == 19654
    assert revenue.currency == 'GBP'
    assert revenue.reported_scale == 'millions'
    assert revenue.raw_period_text == 'Year ended 31 March 2026'
    assert revenue.source_page == 42
    assert '£m' in revenue.supporting_excerpt
    assert result.ai_calls_made == 0


def test_table_level_millions_context_propagates_and_scale_is_not_inferred_from_magnitude():
    result = PdfFinancialTableAdapter().extract_from_canonical(_doc('£m\nFY26\nRevenue 1\nNet debt 999999999'))
    assert {c.raw_metric_label.lower(): c.reported_scale for c in result.candidates} == {'revenue': 'millions', 'net debt': 'millions'}
    ambiguous = PdfFinancialTableAdapter().extract_from_canonical(_doc('FY26\nRevenue 999999999'))
    assert ambiguous.candidates[0].exception == 'financial_scale_ambiguous'
