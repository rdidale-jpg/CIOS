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

import hashlib
from pathlib import Path


def _persist_run(tmp_path, run):
    monkey_dir = tmp_path / 'ai_financial_reports' / 'runs'
    monkey_dir.mkdir(parents=True, exist_ok=True)
    review._write_json(monkey_dir / f"{run['run_id']}.json", run)
    return json.loads((monkey_dir / f"{run['run_id']}.json").read_text())


def _canonical_fingerprint(root: Path):
    files = [root / 'memory' / 'evidence.jsonl', root / 'memory' / 'observations.jsonl']
    files += sorted((root / 'memory' / 'enterprise_models').glob('*.json')) if (root / 'memory' / 'enterprise_models').exists() else []
    h = hashlib.sha256()
    counts = {'evidence': 0, 'observations': 0, 'enterprise_model_files': 0}
    for p in files:
        if not p.exists():
            continue
        data = p.read_bytes(); h.update(str(p.relative_to(root)).encode()+b'\0'+data)
        if p.name == 'evidence.jsonl': counts['evidence'] = len([l for l in data.splitlines() if l.strip()])
        elif p.name == 'observations.jsonl': counts['observations'] = len([l for l in data.splitlines() if l.strip()])
        elif p.suffix == '.json': counts['enterprise_model_files'] += 1
    return counts, h.hexdigest()


def test_persisted_queued_progress_cached_duplicate_success_failure_have_diagnostics(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    branches = [
        {'run_id':'fi-q','status':'queued','state':'queued','claims':[],'applied_results':[]},
        {'run_id':'fi-pg','status':'retrieving_source','collection':{'retrieved':False},'claims':[],'applied_results':[]},
        {'run_id':'fi-cache','status':'completed','cached_output_reused':True,'collection':{'retrieved':True,'http_status':200,'document_size':9},'document':{'media_type':'application/pdf','page_count':3,'source_url':'https://example.com/r.pdf'},'claims':[{'id':'c'}],'applied_results':[]},
        {'run_id':'fi-dupe','status':'provider_request_failed','exceptions':[{'exception_type':'duplicate_in_progress','user_message':'already running'}],'claims':[],'applied_results':[]},
        {'run_id':'fi-ok','status':'completed','claims':[{'id':'c'}],'applied_results':[]},
        {'run_id':'fi-bad','status':'source_retrieval_failed','collection':{'error':'failed at /var/data/flora/tmp/x.pdf'},'exceptions':[{'exception_type':'source_retrieval_failed','failure_stage':'retrieval','user_message':'failed at /var/data/flora/tmp/x.pdf'}],'claims':[],'applied_results':[]},
    ]
    for run in branches:
        saved = _persist_run(tmp_path, run)
        assert saved['deployed_revision']
        assert saved['support_reference'].startswith('FI-')
        assert saved['support_diagnostic']['support_reference'] == saved['support_reference']
        assert saved['support_diagnostic']['deployed_revision'] == saved['deployed_revision']
    queued = json.loads((tmp_path/'ai_financial_reports/runs/fi-q.json').read_text())['support_diagnostic']
    assert queued['request_attempted'] is False
    assert queued['http_status'] == 'not_reached'
    assert queued['parser_name'] == 'not_reached'
    assert queued['extraction_status'] == 'not_reached'
    assert queued['candidate_count'] == 0


def test_filesystem_paths_redacted_recursively_and_business_slashes_preserved():
    payload = {'a':'/tmp/example /var/data/flora/x /home/user/y /workspace/CIOS/z C:\\Users\\name\\x file:///tmp/a.pdf sk-live Bearer abc.def', 'nested':[{'note':'margin/revenue is normal business text'}]}
    clean = review._sanitize_diagnostic_payload(payload)
    dumped = json.dumps(clean)
    for forbidden in ['/tmp/example','/var/data','/home/user','/workspace','C:\\Users','file:///tmp','sk-live','Bearer abc.def']:
        assert forbidden not in dumped
    assert 'REDACTED_PATH' in dumped
    assert 'sk-REDACTED' in dumped
    assert 'Bearer REDACTED' in dumped
    assert 'margin/revenue is normal business text' in dumped


def test_support_html_and_download_redact_paths_and_do_not_reacquire_or_change_canonical(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    called = {'fetch': 0}
    monkeypatch.setattr(review, 'fetch_document', lambda *a, **k: called.__setitem__('fetch', called['fetch']+1))
    before = _canonical_fingerprint(tmp_path)
    run = {'run_id':'fi-redact','created_at':'2026-07-06T00:00:00+00:00','status':'source_retrieval_failed','support_reference':'FI-redact','collection':{'active_source_url':'file:///tmp/source.pdf','error':'see /workspace/CIOS/secret'},'exceptions':[{'exception_type':'source_retrieval_failed','failure_stage':'retrieval','user_message':'see /home/user/secret api_key=abc'}],'claims':[], 'applied_results':[]}
    review._write_json(tmp_path / 'ai_financial_reports' / 'runs' / 'fi-redact.json', run)
    mid = _canonical_fingerprint(tmp_path)
    html = review.financial_intelligence_support_diagnostic_page('fi-redact')
    payload = review.financial_intelligence_support_diagnostic_payload('fi-redact')
    after = _canonical_fingerprint(tmp_path)
    assert before == mid == after
    assert called['fetch'] == 0
    dumped = json.dumps(payload) + html
    assert '/workspace' not in dumped and '/home/user' not in dumped and 'file:///tmp' not in dumped and 'api_key=abc' not in dumped
    assert 'REDACTED_PATH' in dumped and 'api_key=REDACTED' in dumped
