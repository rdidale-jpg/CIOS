from cios.applications.flora import document_review as review
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository


def test_route_level_golden_deterministic_refresh_second_refresh_zero_openai(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    pdf_text = b'%PDF-1.4\n(FLORA PDF PAGE 1 Financial highlights) Tj\n(Income statement) Tj\n(Year ended 31 March 2026) Tj\n(GBP millions) Tj\n(Revenue 19,654) Tj\n(Adjusted EBITDA 8,230) Tj\n(Net debt 8,200) Tj\n'
    pdf = tmp_path / 'bt.pdf'; pdf.write_bytes(pdf_text)
    class Fetch:
        succeeded = True; status_code = 200; media_type = 'application/pdf'; content = pdf_text; checksum = 'd' * 64
        local_path = str(pdf); retrieval_date = review.now_iso(); error = ''; final_url = 'https://www.bt.com/report.pdf'; url = final_url; redirect_chain = ()
    monkeypatch.setattr(review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})
    def fail_openai(*a, **k):
        raise AssertionError('OpenAI must not be called for deterministic standard metrics')
    monkeypatch.setattr(review.OpenAIDirectPDFProvider, 'extract_facts', fail_openai)

    first = review.refresh_financial_intelligence(extraction_mode='pdf_supporting_evidence')
    second = review.refresh_financial_intelligence(extraction_mode='pdf_supporting_evidence')

    assert first['openai_invoked'] is False and first['openai_calls_made'] == 0
    assert second['openai_invoked'] is False and second['openai_calls_made'] == 0
    assert first['auto_accepted_count'] >= 3
    model = EnterpriseModelRepository().get('bt-group-plc')
    assert model.attributes['financial_performance.metrics.revenue.FY26.actual'].current_value == 19654000000
    assert model.attributes['financial_performance.metrics.adjusted_ebitda.FY26.actual'].current_value == 8230000000
    assert all('Year ended' not in key for key in model.attributes)
    assert all('reported FY26' not in str(attr.current_value) for attr in model.attributes.values())
    assert ObservationRepository().list()
    html = review.financial_intelligence_run_page(first['run_id'])
    assert 'Financial Intelligence' in html
    assert 'OpenAI' not in html
