import json, zipfile
from pathlib import Path
import pytest
from urllib.error import HTTPError, URLError

from cios.applications.flora.financial_intelligence import bt_structured as bt


def _cfg(tmp_path, **overrides):
    cfg = json.loads(Path('cios/config/flora/structured_sources/bt-group-plc-fy26.json').read_text())
    cfg.update(overrides)
    path = tmp_path / 'cfg.json'; path.write_text(json.dumps(cfg))
    return cfg, path


def test_missing_source_configuration_classified(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'data'))
    monkeypatch.setenv('FLORA_STRUCTURED_SOURCE_CONFIG', str(tmp_path / 'missing.json'))
    run = bt.ingest_bt_fy26('fi-missing')
    assert run['failure_code'] == 'source_configuration_missing'
    assert run['failure_stage'] == 'governed source configuration'
    assert run['support_reference'] == 'FI-missing'
    assert run['ai_calls_made'] == run['pdf_fallback_calls_made'] == 0
    assert not run['trusted_twin_changed']

@pytest.mark.parametrize('override,code', [
    ({'enterprise_id':'BT'}, 'enterprise_identity_mismatch'),
    ({'reporting_period':'FY2026'}, 'reporting_period_mismatch'),
    ({'artifact_url':''}, 'artifact_url_missing'),
    ({'artifact_url':'https://evil.example/file.zip'}, 'host_not_allowed'),
])
def test_configuration_and_selection_failures(monkeypatch, tmp_path, override, code):
    cfg, path = _cfg(tmp_path, **override)
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / code))
    monkeypatch.setenv('FLORA_STRUCTURED_SOURCE_CONFIG', str(path))
    run = bt.ingest_bt_fy26('fi-'+code)
    assert run['failure_code'] == code
    assert run['user_message'] == 'Structured financial source unavailable'
    assert 'Failure stage:' in run['user_message_display']


def test_off_host_redirect_and_http_error_classification(tmp_path, monkeypatch):
    cfg, _ = _cfg(tmp_path)
    class Opener:
        def open(self, *a, **k): raise HTTPError(cfg['artifact_url'], 404, 'nope', {}, None)
    monkeypatch.setattr(bt, 'build_opener', lambda *a: Opener())
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.retrieve_package(cfg)
    assert exc.value.code == 'http_404'
    handler = bt._NoOffHostRedirect({'www.bt.com'})
    with pytest.raises(bt.StructuredIngestionError) as redir:
        handler.redirect_request(None, None, 302, 'Found', {}, 'https://example.com/x.zip')
    assert redir.value.code == 'redirect_host_rejected'


def test_timeout_dns_tls_incomplete_and_size_classification(tmp_path, monkeypatch):
    cfg, _ = _cfg(tmp_path, compressed_size_limit_bytes=3)
    class TimeoutOpener:
        def open(self, *a, **k): raise TimeoutError('timed out')
    monkeypatch.setattr(bt, 'build_opener', lambda *a: TimeoutOpener())
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.retrieve_package(cfg)
    assert exc.value.code == 'download_timeout'

    class DnsOpener:
        def open(self, *a, **k): raise URLError('Name or service not known')
    monkeypatch.setattr(bt, 'build_opener', lambda *a: DnsOpener())
    with pytest.raises(bt.StructuredIngestionError) as dns:
        bt.retrieve_package(cfg)
    assert dns.value.code == 'dns_failure'

    class Resp:
        status=200; headers={'content-type':'application/zip','content-length':'5'}
        def __enter__(self): return self
        def __exit__(self,*a): pass
        def read(self,n):
            if getattr(self, 'done', False): return b''
            self.done=True; return b'ab'
        def geturl(self): return cfg['artifact_url']
    class IncompleteOpener:
        def open(self,*a,**k): return Resp()
    monkeypatch.setattr(bt, 'build_opener', lambda *a: IncompleteOpener())
    with pytest.raises(bt.StructuredIngestionError) as inc:
        bt.retrieve_package({**cfg, 'compressed_size_limit_bytes': 99})
    assert inc.value.code == 'download_incomplete'


def test_package_validation_invalid_zip_and_unsafe_archive(tmp_path):
    bad = tmp_path / 'bad.zip'; bad.write_bytes(b'not zip')
    cfg = json.loads(Path('cios/config/flora/structured_sources/bt-group-plc-fy26.json').read_text())
    receipt = bt.RetrievedPackage(bad, '0'*64, cfg['artifact_url'], 200, 'application/zip', 7)
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.extract_candidates(bad, cfg, receipt)
    assert exc.value.code == 'invalid_zip'
    unsafe = tmp_path / 'unsafe.zip'
    with zipfile.ZipFile(unsafe, 'w') as z: z.writestr('../x', 'x')
    with pytest.raises(bt.StructuredIngestionError) as slip:
        bt.validate_archive(unsafe, cfg)
    assert slip.value.code == 'unsafe_archive'


def test_adapter_handoff_diagnostic_and_correlation(tmp_path):
    cfg = json.loads(Path('cios/config/flora/structured_sources/bt-group-plc-fy26.json').read_text())
    receipt = bt.RetrievedPackage(tmp_path/'x.zip', 'a'*64, cfg['artifact_url'], 200, 'application/zip', 10)
    diag = bt._diagnostic('fi-ok', cfg, bt.StructuredIngestionError('', 'none', 'completed'), receipt, 4, 3, True)
    assert diag['support_reference'] == 'FI-ok'
    assert diag['adapter_handoff_attempted'] is True
    assert diag['candidate_fact_count'] == 4
    assert diag['canonical_fact_count'] == 3
