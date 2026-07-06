import json
from http.client import HTTPConnection
from cios.applications.flora import document_review as review
from cios.applications.flora.web.app import FloraWebHandler, ThreadingHTTPServer


def test_deployed_revision_and_unknown(monkeypatch):
    monkeypatch.setenv('RENDER_GIT_COMMIT', 'abc123')
    run = {'run_id':'fi-r','status':'completed','claims':[], 'applied_results':[]}
    review.attach_financial_run_diagnostic(run)
    assert run['deployed_revision'] == 'abc123'
    monkeypatch.delenv('RENDER_GIT_COMMIT', raising=False)
    monkeypatch.delenv('GIT_COMMIT', raising=False)
    run2 = {'run_id':'fi-r2','status':'completed','claims':[], 'applied_results':[]}
    review.attach_financial_run_diagnostic(run2)
    assert run2['deployed_revision'] == 'unknown'


def test_early_retrieval_failure_diagnostic_sanitises_url():
    run = {'run_id':'fi-fail','status':'source_retrieval_failed','support_reference':'FI-fail','deployed_revision':'rev', 'collection': {'http_status': None, 'document_size': 0, 'active_source_url':'https://example.com/report.pdf?token=secret&ok=1'}, 'exceptions':[{'exception_type':'source_retrieval_failed','failure_stage':'retrieval','user_message':'boom /tmp/secret sk-test'}]}
    diag = review._run_diagnostic(run)
    assert diag['request_attempted'] is True
    assert diag['http_status'] == 'unknown'
    assert diag['bytes_downloaded'] == 0
    assert diag['parser_name'] == 'not_reached'
    assert 'secret' not in diag['requested_url']
    assert 'REDACTED' in diag['requested_url']
    assert 'sk-test' not in diag['safe_failure_message']


def test_parsing_and_extraction_diagnostics_retain_prior_state():
    parsing = {'run_id':'fi-p','status':'section_selection_failed','collection': {'retrieved':True,'http_status':200,'document_size':1234,'content_type':'application/pdf'}, 'document': {'media_type':'application/pdf','page_count':10,'extraction_method':'embedded_text','extraction_version':'v'}, 'claims': []}
    d = review._run_diagnostic(parsing)
    assert d['http_status'] == 200
    assert d['bytes_downloaded'] == 1234
    assert d['pdf_magic_result'] is True
    extraction = {'run_id':'fi-e','status':'failed','collection': {'retrieved':True,'http_status':200,'document_size':1234,'content_type':'application/pdf'}, 'document': {'media_type':'application/pdf','page_count':10,'extraction_method':'embedded_text','extraction_version':'v'}, 'claims': [{'claim_id':'c1'}]}
    e = review._run_diagnostic(extraction)
    assert e['candidate_count'] == 1
    assert e['canonical_write_count'] == 0


def test_support_diagnostic_view_requires_authorisation(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('FLORA_SUPPORT_TOKEN', 'support-token')
    run = {'run_id':'fi-auth','created_at':'2026-07-06T00:00:00+00:00','status':'completed','support_reference':'FI-auth','claims':[], 'applied_results':[]}
    review.attach_financial_run_diagnostic(run)
    path = tmp_path / 'ai_financial_reports' / 'runs'
    path.mkdir(parents=True)
    (path / 'fi-auth.json').write_text(json.dumps(run))
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    try:
        import threading
        t = threading.Thread(target=server.serve_forever, daemon=True); t.start()
        host, port = server.server_address
        c = HTTPConnection(host, port)
        c.request('GET', '/financial-intelligence/fi-auth/support-diagnostic')
        assert c.getresponse().status == 403
        c = HTTPConnection(host, port)
        c.request('GET', '/financial-intelligence/fi-auth/support-diagnostic/download', headers={'Authorization':'Bearer support-token'})
        r = c.getresponse(); body = r.read().decode()
        assert r.status == 200
        assert 'support_reference' in body
    finally:
        server.shutdown()
