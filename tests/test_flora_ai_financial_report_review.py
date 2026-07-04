from experiments.document_understanding.schema import ExtractionRun, FoundationFact
from cios.applications.flora import document_review as ai_review
from cios.applications.flora.document_review import apply_accepted, create_upload_run, update_reviews
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository


def fact(**overrides):
    base = dict(
        fact_id='f1', canonical_enterprise_id='bt-group-plc', claim_type='financial_metric_reported',
        subject_type='enterprise', subject_name='BT Group plc', predicate='reported revenue', object_type='financial_metric',
        value_number=20.4, scale='billion', currency='GBP', period_label='FY26', state='actual',
        source_document_id='doc', source_page_start=12, source_page_end=12, source_excerpt='Revenue was £20.4bn in FY26.',
        extraction_confidence=.91, explicit_in_source=True, extractor_provider='openai', extractor_model='gpt-5.5', extractor_version='test',
    )
    base.update(overrides)
    return FoundationFact(**base)


def test_ai_financial_report_review_applies_accepted_claim(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def fake_extract(self, document, schema=None, page_ranges=None):
        return ExtractionRun(run_id='x', route='openai-direct', provider='openai', model='gpt-5.5', status='completed', started_at=ai_review.now_iso(), completed_at=ai_review.now_iso(), latency_seconds=0, facts=[fact()])

    monkeypatch.setattr(ai_review.OpenAIDirectPDFProvider, 'extract_facts', fake_extract)
    pdf = tmp_path / 'bt.pdf'
    pdf.write_bytes(b'%PDF-1.4\nBT Annual Report fixture')

    run = create_upload_run(pdf)
    assert run['provider'] == 'openai'
    assert run['model'] == 'gpt-5.5'
    assert run['claims'][0]['page_reference'] == '12'

    update_reviews(run['run_id'], {f"action_{run['claims'][0]['claim_id']}": ['accept']})
    applied = apply_accepted(run['run_id'])

    assert applied['applied_results']
    assert ObservationRepository().list()
    model = EnterpriseModelRepository().get('bt-group-plc')
    assert 'financial_performance.metrics.reported_revenue.FY26.actual' in model.attributes


def test_review_page_exposes_accept_amend_reject(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    def fake_extract(self, document, schema=None, page_ranges=None):
        return ExtractionRun(run_id='x', route='openai-direct', provider='openai', model='gpt-5.5', status='completed', started_at=ai_review.now_iso(), completed_at=ai_review.now_iso(), latency_seconds=0, facts=[fact()])
    monkeypatch.setattr(ai_review.OpenAIDirectPDFProvider, 'extract_facts', fake_extract)
    pdf = tmp_path / 'bt.pdf'; pdf.write_bytes(b'%PDF-1.4')
    run = create_upload_run(pdf)
    html = ai_review.run_page(run['run_id'])
    assert 'Accept' in html and 'Amend' in html and 'Reject' in html
    assert 'Enterprise Memory' in html


def test_financial_intelligence_records_source_retrieval_failure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    class Fetch:
        succeeded = False
        status_code = 403
        media_type = 'text/plain'
        content = b''
        checksum = ''
        local_path = ''
        retrieval_date = ai_review.now_iso()
        error = 'HTTP 403: Forbidden'
        final_url = 'https://www.bt.com/report.pdf'
        url = final_url
        redirect_chain = ()
    monkeypatch.setattr(ai_review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(ai_review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})

    run = ai_review.refresh_financial_intelligence()

    assert run['status'] == 'source_retrieval_failed'
    assert run['exceptions'][0]['exception_type'] == 'source_retrieval_failed'
    assert run['exceptions'][0]['user_message'] == 'Flora could not retrieve the financial report.'
    assert run['collection']['http_status'] == 403
    assert run['collection']['content_type'] == 'text/plain'
    assert run['collection']['final_url'] == 'https://www.bt.com/report.pdf'


def test_financial_intelligence_records_provider_not_configured(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    pdf = b'%PDF-1.4\nBT Annual Report fixture (Revenue was 20.4 billion GBP).'
    class Fetch:
        succeeded = True
        status_code = 200
        media_type = 'application/pdf'
        content = pdf
        checksum = 'a' * 64
        local_path = str(tmp_path / 'bt.pdf')
        retrieval_date = ai_review.now_iso()
        error = ''
        final_url = 'https://www.bt.com/report.pdf'
        url = final_url
        redirect_chain = ()
    (tmp_path / 'bt.pdf').write_bytes(pdf)
    monkeypatch.setattr(ai_review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(ai_review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})

    run = ai_review.refresh_financial_intelligence()

    assert run['status'] == 'provider_not_configured'
    assert run['provider_status'] == 'not_executed'
    assert run['exceptions'][0]['exception_type'] == 'provider_not_configured'
    assert run['exceptions'][0]['user_message'] == 'Financial document understanding is temporarily unavailable.'
    assert 'provider_or_source_unavailable' not in str(run)


def test_outcome_summary_uses_plain_language_and_retry_for_zero_changes():
    html = ai_review._outcome_summary({
        'run_id': 'fi-test',
        'status': 'provider_not_configured',
        'collection': {'retrieval_time': '2026-07-04T00:00:00+00:00'},
        'exceptions': [{'exception_type': 'provider_not_configured', 'user_message': 'Financial document understanding is temporarily unavailable.'}],
        'claims': [],
        'applied_results': [],
        'enterprise_attributes_changed': [],
    })
    assert 'No financial intelligence was added because processing did not complete.' in html
    assert 'Financial document understanding is temporarily unavailable.' in html
    assert '<button>Retry</button>' in html
    assert 'attributes changed or strengthened' not in html
