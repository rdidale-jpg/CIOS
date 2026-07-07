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


def test_product_result_pages_show_safe_support_report_for_failed_and_partial(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    failed = {'run_id':'fi-ui-failed','created_at':'2026-07-06T00:00:00+00:00','status':'source_retrieval_failed','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','support_reference':'FI-ui-failed','claims':[], 'applied_results':[], 'exceptions':[{'exception_type':'source_retrieval_failed','failure_stage':'retrieval','user_message':'No source'}]}
    partial = {'run_id':'fi-ui-partial','created_at':'2026-07-06T00:01:00+00:00','execution_mode':review.DUAL_SPEED_FINANCIAL_INTELLIGENCE_MODE,'workflow':'financial_intelligence','enterprise_id':'bt-group-plc','overall_status':'partial','completion_class':'partial','support_reference':'FI-ui-partial','rapid_intelligence':{'status':'partial','evidence_status':'official_source_retrieved','source_receipt':{'document_title':'FY26 results','authority':'BT Group plc','reporting_period':'FY26'},'candidates':[{'raw_metric_label':'Revenue','original_displayed_value':'1','proposed_canonical_metric_id':'revenue'}]},'verification':{},'canonical_update':{},'cost_summary':{}}
    review._write_json(tmp_path / 'ai_financial_reports' / 'runs' / 'fi-ui-failed.json', failed)
    review._write_json(tmp_path / 'ai_financial_reports' / 'runs' / 'fi-ui-partial.json', partial)
    failed_html, status = review.financial_intelligence_run_response('fi-ui-failed')
    partial_html, status2 = review.financial_intelligence_run_response('fi-ui-partial')
    assert status == status2 == 200
    assert 'Download support report' in failed_html
    assert '/financial-intelligence/fi-ui-failed/support-report' in failed_html
    assert 'Download support report' in partial_html
    from cios.applications.flora.digital_twins import bt_twin_page
    twin = bt_twin_page()
    assert 'Open result' in twin
    assert 'Download support report' not in twin
    assert '/financial-intelligence/fi-ui-partial/support-report' not in twin


def test_safe_support_report_product_download_authz_persisted_no_reacquire_no_ai(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.delenv('FLORA_SUPPORT_TOKEN', raising=False)
    called = {'fetch':0, 'ai':0}
    monkeypatch.setattr(review, 'fetch_document', lambda *a, **k: called.__setitem__('fetch', called['fetch']+1))
    run = {'run_id':'fi-product-auth','created_at':'2026-07-06T00:00:00+00:00','status':'source_retrieval_failed','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','support_reference':'FI-product-auth','support_diagnostic':{'run_id':'fi-product-auth','support_reference':'FI-product-auth','safe_failure_message':'secret sk-live at /tmp/x api_key=abc','ai_call_count':0,'request_attempted': True},'claims':[], 'applied_results':[]}
    path = tmp_path / 'ai_financial_reports' / 'runs'; path.mkdir(parents=True)
    (path / 'fi-product-auth.json').write_text(json.dumps(run))
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    try:
        import threading
        t = threading.Thread(target=server.serve_forever, daemon=True); t.start()
        host, port = server.server_address
        def get(headers=None):
            c = HTTPConnection(host, port)
            c.request('GET', '/financial-intelligence/fi-product-auth/support-report', headers=headers or {})
            r = c.getresponse(); body = r.read().decode(); return r.status, body
        assert get()[0] == 403
        assert get({'X-Flora-User':'alice','X-Flora-Enterprises':'other-enterprise'})[0] == 403
        status, body = get({'X-Flora-User':'rob','X-Flora-Enterprises':'bt-group-plc'})
        assert status == 200
        payload = json.loads(body)
        assert payload['support_reference'] == 'FI-product-auth'
        assert payload['run_id'] == 'fi-product-auth'
        assert '/tmp' not in body and 'sk-live' not in body and 'api_key=abc' not in body
        assert 'REDACTED_PATH' in body and 'sk-REDACTED' in body and 'api_key=REDACTED' in body
        assert called == {'fetch':0, 'ai':0}
    finally:
        server.shutdown()


def test_missing_persisted_support_report_has_friendly_message(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    run = {'run_id':'fi-old','created_at':'2026-07-06T00:00:00+00:00','status':'failed','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','support_reference':'FI-old','claims':[], 'applied_results':[]}
    path = tmp_path / 'ai_financial_reports' / 'runs'; path.mkdir(parents=True)
    (path / 'fi-old.json').write_text(json.dumps(run))
    payload = review.financial_intelligence_safe_support_report_payload('fi-old')
    assert payload['report_available'] is False
    assert payload['message'] == 'A support report is not available for this earlier run.'
    assert payload['support_reference'] == 'FI-old'


def test_safe_support_report_support_token_and_malformed_run_id(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('FLORA_SUPPORT_TOKEN', 'support-token')
    run = {'run_id':'fi-support-token','created_at':'2026-07-06T00:00:00+00:00','status':'failed','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','support_reference':'FI-support-token','support_diagnostic':{'run_id':'fi-support-token','support_reference':'FI-support-token','safe_failure_message':'safe'},'claims':[], 'applied_results':[]}
    path = tmp_path / 'ai_financial_reports' / 'runs'; path.mkdir(parents=True)
    (path / 'fi-support-token.json').write_text(json.dumps(run))
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    try:
        import threading
        t = threading.Thread(target=server.serve_forever, daemon=True); t.start()
        host, port = server.server_address
        c = HTTPConnection(host, port)
        c.request('GET', '/financial-intelligence/fi-support-token/support-report', headers={'Authorization':'Bearer support-token'})
        r = c.getresponse(); body = r.read().decode()
        assert r.status == 200
        assert 'FI-support-token' in body
        c = HTTPConnection(host, port)
        c.request('GET', '/financial-intelligence/../secret/support-report', headers={'X-Flora-User':'rob','X-Flora-Enterprises':'*'})
        r = c.getresponse(); r.read()
        assert r.status == 404
    finally:
        server.shutdown()


def test_rendered_product_support_report_link_is_safe_get_and_read_only(monkeypatch, tmp_path):
    import re
    import threading
    from cios.applications.flora.web import app as webapp

    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.delenv('FLORA_SUPPORT_TOKEN', raising=False)
    calls = {'progress':0, 'refresh':0, 'dual':0, 'source':0, 'extract':0, 'ai':0}
    monkeypatch.setattr(webapp, 'create_financial_intelligence_progress_run', lambda *a, **k: (_ for _ in ()).throw(AssertionError('progress run created')))
    monkeypatch.setattr(webapp, 'refresh_financial_intelligence', lambda *a, **k: (_ for _ in ()).throw(AssertionError('refresh invoked')))
    monkeypatch.setattr(review, 'coordinate_dual_speed_financial_intelligence_run', lambda *a, **k: calls.__setitem__('dual', calls['dual']+1), raising=False)
    monkeypatch.setattr(review, 'fetch_document', lambda *a, **k: calls.__setitem__('source', calls['source']+1), raising=False)
    monkeypatch.setattr(review, 'extract_rapid_financial_candidates', lambda *a, **k: calls.__setitem__('extract', calls['extract']+1), raising=False)

    run = {'run_id':'fi-rendered-link','created_at':'2026-07-06T00:00:00+00:00','status':'source_retrieval_failed','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','support_reference':'FI-rendered-link','support_diagnostic':{'run_id':'fi-rendered-link','support_reference':'FI-rendered-link','safe_failure_message':'safe','execution_mode':'structured_standard_financials','ai_call_count':0,'request_attempted': False},'claims':[], 'applied_results':[]}
    runs = tmp_path / 'ai_financial_reports' / 'runs'; runs.mkdir(parents=True)
    (runs / 'fi-rendered-link.json').write_text(json.dumps(run))
    before_files = sorted(p.name for p in runs.glob('*.json'))
    before_payload = (runs / 'fi-rendered-link.json').read_text()
    before_canon = _canonical_fingerprint(tmp_path)

    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    try:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        host, port = server.server_address
        headers = {'X-Flora-User':'rob','X-Flora-Enterprises':'bt-group-plc'}
        c = HTTPConnection(host, port)
        c.request('GET', '/financial-intelligence/fi-rendered-link', headers=headers)
        r = c.getresponse(); html = r.read().decode()
        assert r.status == 200
        m = re.search(r"<a[^>]+class='support-report-link'[^>]+href='([^']+)'[^>]*>Download support report</a>", html)
        assert m, html
        url = m.group(1)
        assert url == '/financial-intelligence/fi-rendered-link/support-report'
        assert '<button' not in m.group(0)
        form_spans = [html[x.start():html.find('</form>', x.start())] for x in re.finditer(r"<form[^>]+action='/financial-intelligence/bt-group-plc/refresh'", html)]
        assert all('Download support report' not in span for span in form_spans)

        c = HTTPConnection(host, port)
        c.request('GET', url, headers=headers)
        r = c.getresponse(); body = r.read().decode()
        assert r.status == 200
        assert json.loads(body)['support_reference'] == 'FI-rendered-link'
        assert json.loads(body)['run_id'] == 'fi-rendered-link'
        assert sorted(p.name for p in runs.glob('*.json')) == before_files
        assert (runs / 'fi-rendered-link.json').read_text() == before_payload
        assert _canonical_fingerprint(tmp_path) == before_canon
        assert all(v == 0 for v in calls.values())
    finally:
        server.shutdown()


def test_result_and_support_report_share_session_access_and_missing_diagnostic(monkeypatch, tmp_path):
    import threading
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    runs = tmp_path / 'ai_financial_reports' / 'runs'; runs.mkdir(parents=True)
    run = {'run_id':'fi-old-session','created_at':'2026-07-06T00:00:00+00:00','status':'failed','workflow':'financial_intelligence','enterprise_id':'bt-group-plc','support_reference':'FI-old-session','claims':[], 'applied_results':[]}
    (runs / 'fi-old-session.json').write_text(json.dumps(run))
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    try:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        host, port = server.server_address
        def get(path, headers=None):
            c = HTTPConnection(host, port); c.request('GET', path, headers=headers or {}); r=c.getresponse(); return r.status, r.read().decode()
        assert get('/financial-intelligence/fi-old-session')[0] == 403
        assert get('/financial-intelligence/fi-old-session/support-report')[0] == 403
        assert get('/financial-intelligence/fi-old-session', {'X-Flora-User':'mallory','X-Flora-Enterprises':'other'})[0] == 403
        assert get('/financial-intelligence/fi-old-session/support-report', {'X-Flora-User':'mallory','X-Flora-Enterprises':'other'})[0] == 403
        assert get('/financial-intelligence/fi-old-session', {'X-Flora-User':'rob','X-Flora-Enterprises':'bt-group-plc'})[0] == 200
        status, body = get('/financial-intelligence/fi-old-session/support-report', {'X-Flora-User':'rob','X-Flora-Enterprises':'bt-group-plc'})
        assert status == 200
        payload = json.loads(body)
        assert payload['report_available'] is False
        assert payload['message'] == 'A support report is not available for this earlier run.'
        assert payload['support_reference'] == 'FI-old-session'
    finally:
        server.shutdown()
