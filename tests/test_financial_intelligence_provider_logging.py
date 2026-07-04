import io
import logging
import sys
import types

from cios.applications.flora import document_review
from experiments.document_understanding.providers import OpenAIDirectPDFProvider


def _doc(tmp_path):
    pdf = tmp_path / 'bt.pdf'
    pdf.write_bytes(b'%PDF-1.4\nfixture')
    return document_review.ExperimentDocument(
        document_id='DOC', enterprise_id='bt-group-plc', title='BT Annual Report',
        source_url='https://www.bt.com/report.pdf', retrieval_timestamp=document_review.now_iso(),
        checksum='x', media_type='application/pdf', page_count=1, local_path=str(pdf),
    )


def _capture_logger(monkeypatch):
    stream = io.StringIO()
    logger = logging.getLogger('flora.financial_intelligence')
    old_handlers = logger.handlers[:]
    logger.handlers = [logging.StreamHandler(stream)]
    logger.setLevel(logging.ERROR)
    logger.propagate = False
    monkeypatch.setattr(logger, 'handlers', logger.handlers)
    return stream, old_handlers


def _install_openai(monkeypatch, exc):
    class Responses:
        def create(self, **kwargs):
            raise exc
    class Client:
        def __init__(self, **kwargs):
            self.responses = Responses()
    monkeypatch.setitem(sys.modules, 'openai', types.SimpleNamespace(OpenAI=Client))


def test_handled_provider_failures_log_same_support_reference_and_distinct_types(monkeypatch, tmp_path):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-secret-value')
    cases = [
        ('AuthenticationError', 401, 'invalid_api_key', 'provider_authentication_failed'),
        ('RateLimitError', 429, 'insufficient_quota', 'provider_quota_exceeded'),
        ('NotFoundError', 404, 'model_not_found', 'provider_model_unavailable'),
        ('BadRequestError', 400, 'invalid_request_error', 'provider_request_invalid'),
        ('APITimeoutError', None, None, 'provider_timeout'),
        ('APIResponseValidationError', 200, 'invalid_response', 'provider_response_invalid'),
    ]
    for name, status_code, code, expected_category in cases:
        stream, _ = _capture_logger(monkeypatch)
        Exc = type(name, (Exception,), {'status_code': status_code, 'code': code})
        _install_openai(monkeypatch, Exc(f'{name} sk-secret-value Bearer abc123'))
        run = OpenAIDirectPDFProvider(model='gpt-test').extract_facts(_doc(tmp_path), correlation_id=f'corr-{name}')
        category = document_review._provider_failure_category(run)
        logged = stream.getvalue()
        assert category == expected_category
        assert f'FI-corr-{name}' in logged
        assert run.diagnostics[-1]['correlation_id'] == f'corr-{name}'
        assert name in logged
        assert 'sk-secret-value' not in logged
        assert 'Bearer abc123' not in logged


def test_unexpected_provider_exception_logs_traceback(monkeypatch, tmp_path):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-secret-value')
    stream, _ = _capture_logger(monkeypatch)
    _install_openai(monkeypatch, RuntimeError('boom'))

    run = OpenAIDirectPDFProvider(model='gpt-test').extract_facts(_doc(tmp_path), correlation_id='unexpected-1')

    logged = stream.getvalue()
    assert run.status == 'failed'
    assert 'FI-unexpected-1' in logged
    assert 'Traceback (most recent call last)' in logged
    assert 'sk-secret-value' not in logged


def test_production_logging_configures_console_handler(monkeypatch):
    logger = logging.getLogger('flora.financial_intelligence')
    logger.handlers = []

    configured = document_review.configure_financial_intelligence_logging()

    assert configured.level == logging.ERROR
    assert configured.handlers
    assert any(isinstance(h, logging.StreamHandler) and h.stream in {sys.stderr, sys.stdout} for h in configured.handlers)
