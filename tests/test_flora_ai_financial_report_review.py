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


def test_financial_intelligence_refresh_creates_missing_nested_directories(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'flora'))
    import importlib
    import cios.applications.flora.document_review as review
    review = importlib.reload(review)
    pdf = b'%PDF-1.4\nFLORA PDF PAGE 1 (Revenue was 20.4 billion GBP) Tj\n'
    class Fetch:
        succeeded = True; status_code = 200; media_type = 'application/pdf'; content = pdf; checksum = 'b' * 64
        local_path = str(tmp_path / 'bt.pdf'); retrieval_date = review.now_iso(); error = ''; final_url = 'https://www.bt.com/report.pdf'; url = final_url; redirect_chain = ()
    def fake_extract(self, document, schema=None, page_ranges=None):
        return ExtractionRun(run_id='x', route='openai-direct', provider='openai', model='gpt-5.5', status='completed', started_at=review.now_iso(), completed_at=review.now_iso(), latency_seconds=0, facts=[fact()])
    monkeypatch.setattr(review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(review.OpenAIDirectPDFProvider, 'extract_facts', fake_extract)
    monkeypatch.setattr(review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})

    run = review.refresh_financial_intelligence()

    assert run['status'] == 'completed'
    assert (tmp_path / 'flora' / 'ai_financial_reports' / 'runs' / f"{run['run_id']}.json").exists()
    assert (tmp_path / 'flora' / 'memory' / 'observations.jsonl').exists()
    assert (tmp_path / 'flora' / 'memory' / 'enterprise_models').is_dir()
    assert run['openai_invoked'] is True


def test_financial_intelligence_persistence_failure_is_not_provider_failure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    class Fetch:
        succeeded = False; status_code = 403; media_type = 'text/plain'; content = b''; checksum = ''; local_path = ''
        retrieval_date = ai_review.now_iso(); error = 'HTTP 403'; final_url = 'https://www.bt.com/report.pdf'; url = final_url; redirect_chain = ()
    monkeypatch.setattr(ai_review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(ai_review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})
    def fail_write(path, data):
        from cios.applications.flora.storage import PersistenceError
        raise PersistenceError('disk read-only')
    monkeypatch.setattr(ai_review, '_write_json', fail_write)

    run = ai_review.refresh_financial_intelligence()

    assert run['status'] == 'persistence_failed'
    assert run['failure_category'] == 'persistence_failed'
    assert run['exceptions'][0]['exception_type'] == 'persistence_failed'
    assert run['openai_invoked'] is False


def test_provider_request_failures_remain_classified(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    pdf = b'%PDF-1.4\nBT Annual Report fixture'
    class Fetch:
        succeeded = True; status_code = 200; media_type = 'application/pdf'; content = pdf; checksum = 'c' * 64
        local_path = str(tmp_path / 'bt.pdf'); retrieval_date = ai_review.now_iso(); error = ''; final_url = 'https://www.bt.com/report.pdf'; url = final_url; redirect_chain = ()
    def fake_extract(self, document, schema=None, page_ranges=None):
        return ExtractionRun(run_id='x', route='openai-direct', provider='openai', model='gpt-5.5', status='request_failed', started_at=ai_review.now_iso(), completed_at=ai_review.now_iso(), latency_seconds=0, provider_errors=['timeout'])
    monkeypatch.setattr(ai_review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(ai_review.OpenAIDirectPDFProvider, 'extract_facts', fake_extract)
    monkeypatch.setattr(ai_review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})

    run = ai_review.refresh_financial_intelligence()

    assert run['status'] == 'provider_request_failed'
    assert run['openai_invoked'] is True


def test_missing_financial_intelligence_run_returns_usable_page(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'flora'))
    import importlib
    import cios.applications.flora.document_review as review
    review = importlib.reload(review)

    html, status = review.financial_intelligence_run_response('fi-0304783822cb')

    assert status == 410
    assert 'This previous refresh result is no longer available.' in html
    assert 'Start a new refresh to collect the latest financial intelligence.' in html
    assert 'Start new refresh' in html


def test_old_financial_intelligence_url_does_not_raise(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'flora'))
    import importlib
    import cios.applications.flora.document_review as review
    review = importlib.reload(review)

    html = review.financial_intelligence_run_page('fi-old-missing')

    assert 'This previous refresh result is no longer available.' in html
    assert 'FileNotFoundError' not in html


def test_financial_intelligence_navigation_uses_start_page_not_missing_historic_run(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'flora'))
    import importlib
    import cios.applications.flora.document_review as review
    review = importlib.reload(review)
    monkeypatch.setattr(review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf'})

    html = review.financial_intelligence_page()

    assert "action='/financial-intelligence/bt-group-plc/refresh'" in html
    assert '/financial-intelligence/fi-0304783822cb' not in html
    assert 'No Financial Intelligence refresh has run yet.' in html


def test_newly_written_financial_intelligence_run_can_be_loaded(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'flora'))
    import importlib
    import cios.applications.flora.document_review as review
    review = importlib.reload(review)
    run = {'run_id': 'fi-loadable', 'claims': [], 'applied_results': [], 'collection': {}, 'exceptions': []}

    review._write_json(review._run_path(run['run_id']), run)

    assert review.load_run('fi-loadable')['run_id'] == 'fi-loadable'


def test_financial_intelligence_reads_and_writes_use_same_resolved_root(monkeypatch, tmp_path):
    root = tmp_path / 'same-root'
    monkeypatch.setenv('FLORA_DATA_DIR', str(root))
    import importlib
    import cios.applications.flora.document_review as review
    review = importlib.reload(review)
    run = {'run_id': 'fi-same-root', 'claims': [], 'applied_results': [], 'collection': {}, 'exceptions': []}

    path = review._run_path(run['run_id'])
    review._write_json(path, run)

    assert path.resolve().is_relative_to(root.resolve())
    assert review.load_run('fi-same-root')['run_id'] == 'fi-same-root'


def test_flora_data_dir_is_optional_for_ephemeral_pilot_operation(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('FLORA_DATA_DIR', raising=False)
    from cios.applications.flora import storage

    status = storage.startup_storage_status()

    assert status['ready'] is True
    assert status['storage_mode'] == 'ephemeral pilot storage'
    assert status['ephemeral'] is True
    assert (tmp_path / '.flora_pilot' / 'ai_financial_reports' / 'runs').is_dir()


def test_provider_timeout_is_distinct_and_records_safe_diagnostic(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    pdf = b'%PDF-1.4\nBT Annual Report fixture'
    class Fetch:
        succeeded = True; status_code = 200; media_type = 'application/pdf'; content = pdf; checksum = 'd' * 64
        local_path = str(tmp_path / 'bt.pdf'); retrieval_date = ai_review.now_iso(); error = ''; final_url = 'https://www.bt.com/report.pdf'; url = final_url; redirect_chain = ()
    (tmp_path / 'bt.pdf').write_bytes(pdf)
    def fake_extract(self, document, schema=None, page_ranges=None):
        return ExtractionRun(
            run_id='corr-1', route='openai-direct', provider='openai', model='gpt-5.5', status='timeout',
            started_at=ai_review.now_iso(), completed_at=ai_review.now_iso(), latency_seconds=1,
            provider_errors=['APITimeoutError: timed out'],
            diagnostics=[{'correlation_id': 'corr-1', 'timestamp': ai_review.now_iso(), 'provider': 'openai', 'requested_model': 'gpt-5.5', 'request_stage': 'model_invocation', 'source_document_retrieval_result': True, 'source_content_type': 'application/pdf', 'source_file_size': len(pdf), 'pdf_upload_succeeded': True, 'http_status_code': None, 'provider_error_type': 'APITimeoutError', 'provider_error_code': None, 'sanitised_provider_error_message': 'timed out', 'retryable': True, 'elapsed_time': 1}]
        )
    monkeypatch.setattr(ai_review, 'fetch_document', lambda url: Fetch())
    monkeypatch.setattr(ai_review.OpenAIDirectPDFProvider, 'extract_facts', fake_extract)
    monkeypatch.setattr(ai_review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf', 'source_type': 'annual_report', 'authority_tier': 'tier_1_company_authoritative', 'publisher': 'BT Group plc'})

    run = ai_review.refresh_financial_intelligence()

    assert run['status'] == 'provider_timeout'
    assert run['support_reference'] == 'FI-corr-1'
    assert run['provider_diagnostics'][-1]['request_stage'] == 'model_invocation'
    assert 'sk-' not in str(run['provider_diagnostics'])
    assert 'Support reference: FI-corr-1' in ai_review._outcome_summary(run)


def test_openai_governed_pdf_url_uses_file_url_without_files_api(monkeypatch, tmp_path):
    import sys, types, json
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    captured = {}
    class Resp:
        id = 'resp-1'; usage = None; output_text = json.dumps({'facts': []})
        def model_dump(self, mode='json'):
            return {'id': self.id, 'output_text': self.output_text, 'usage': {}}
    class Responses:
        def create(self, **kwargs):
            captured.update(kwargs); return Resp()
    class Files:
        def create(self, **kwargs):
            raise AssertionError('Files API must not be called')
    class Client:
        def __init__(self, **kwargs): self.responses = Responses(); self.files = Files()
    monkeypatch.setitem(sys.modules, 'openai', types.SimpleNamespace(OpenAI=Client))
    pdf = tmp_path / 'bt.pdf'; pdf.write_bytes(b'%PDF-1.4\nfixture')
    doc = ai_review.ExperimentDocument(document_id='DOC', enterprise_id='bt-group-plc', title='BT Annual Report', source_url='https://www.bt.com/report.pdf', retrieval_timestamp=ai_review.now_iso(), checksum='x', media_type='application/pdf', page_count=1, local_path=str(pdf))

    run = ai_review.OpenAIDirectPDFProvider(model='gpt-test').extract_facts(doc)

    assert run.status == 'completed'
    file_part = captured['input'][0]['content'][0]
    assert file_part == {'type': 'input_file', 'file_url': 'https://www.bt.com/report.pdf'}
    assert run.diagnostics[-1]['source_input_mode'] == 'file_url'
    assert run.diagnostics[-1]['pdf_upload_succeeded'] is False


def test_openai_inaccessible_file_url_uses_base64_fallback(monkeypatch, tmp_path):
    import sys, types, json
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    calls = []
    class BadRequest(Exception):
        status_code = 400; code = 'invalid_file_url'
    class Resp:
        id = 'resp-2'; usage = None; output_text = json.dumps({'facts': []})
        def model_dump(self, mode='json'):
            return {'id': self.id, 'output_text': self.output_text, 'usage': {}}
    class Responses:
        def create(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1: raise BadRequest('OpenAI could not retrieve external file URL')
            return Resp()
    class Client:
        def __init__(self, **kwargs): self.responses = Responses(); self.files = types.SimpleNamespace(create=lambda **kw: (_ for _ in ()).throw(AssertionError('Files API must not be called')))
    monkeypatch.setitem(sys.modules, 'openai', types.SimpleNamespace(OpenAI=Client))
    pdf = tmp_path / 'bt.pdf'; pdf.write_bytes(b'%PDF-1.4\nfixture')
    doc = ai_review.ExperimentDocument(document_id='DOC', enterprise_id='bt-group-plc', title='BT Annual Report', source_url='https://www.bt.com/report.pdf', retrieval_timestamp=ai_review.now_iso(), checksum='x', media_type='application/pdf', page_count=1, local_path=str(pdf))

    run = ai_review.OpenAIDirectPDFProvider(model='gpt-test').extract_facts(doc)

    assert run.status == 'completed'
    assert calls[0]['input'][0]['content'][0]['file_url'] == 'https://www.bt.com/report.pdf'
    fallback = calls[1]['input'][0]['content'][0]
    assert fallback['type'] == 'input_file'
    assert fallback['filename'].endswith('.pdf')
    assert fallback['file_data'].startswith('data:application/pdf;base64,')
    assert [d['source_input_mode'] for d in run.diagnostics] == ['file_url', 'file_data']


def test_invalid_and_oversized_pdfs_fail_before_provider_request(monkeypatch, tmp_path):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    invalid = ai_review.ExperimentDocument(document_id='DOC', enterprise_id='bt-group-plc', title='BT Annual Report', source_url='https://www.bt.com/report.html', retrieval_timestamp=ai_review.now_iso(), checksum='x', media_type='text/html', page_count=1, local_path=None)
    invalid_run = ai_review.OpenAIDirectPDFProvider(model='gpt-test').extract_facts(invalid)
    assert invalid_run.status == 'not_executed'
    assert invalid_run.diagnostics[0]['provider_error_type'] == 'source_not_pdf'

    import experiments.document_understanding.providers as provider_mod
    pdf = tmp_path / 'large.pdf'; pdf.write_bytes(b'%PDF-1.4')
    monkeypatch.setattr(provider_mod, 'MAX_RESPONSES_PDF_BYTES', 4)
    large = ai_review.ExperimentDocument(document_id='DOC2', enterprise_id='bt-group-plc', title='BT Annual Report', source_url='https://www.bt.com/report.pdf', retrieval_timestamp=ai_review.now_iso(), checksum='y', media_type='application/pdf', page_count=1, local_path=str(pdf))
    oversized_run = ai_review.OpenAIDirectPDFProvider(model='gpt-test').extract_facts(large)
    assert oversized_run.status == 'not_executed'
    assert oversized_run.diagnostics[0]['provider_error_type'] == 'source_oversized'


def test_financial_intelligence_page_requires_no_manual_bt_upload(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'flora'))
    monkeypatch.setattr(ai_review, '_bt_annual_report_source', lambda: {'source_id': 'bt-annual-report-2026', 'source_name': 'BT Group plc Annual Report 2026', 'url': 'https://www.bt.com/report.pdf'})

    html = ai_review.financial_intelligence_page()

    assert 'no download or upload is required' in html
    assert "action='/financial-intelligence/bt-group-plc/refresh'" in html
