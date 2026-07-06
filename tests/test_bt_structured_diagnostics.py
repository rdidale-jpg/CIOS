import json, zipfile, shutil
from pathlib import Path
import pytest
from urllib.error import HTTPError, URLError

from cios.applications.flora.financial_intelligence import bt_structured as bt


def _cfg(tmp_path, **overrides):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
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


def test_production_search_page_configuration_remains_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'data'))
    monkeypatch.delenv('FLORA_STRUCTURED_SOURCE_CONFIG', raising=False)
    run = bt.ingest_bt_fy26('fi-production-search-page')
    assert run['failure_code'] == 'artifact_url_not_downloadable'
    diagnostic = run['structured_diagnostics'][0]
    assert diagnostic['failure_stage'] == 'governed source configuration'
    assert diagnostic['request_attempted'] is False
    assert diagnostic['safe_failure_message'] == 'The configured source is a search page rather than a filing download.'

@pytest.mark.parametrize('override,code', [
    ({'enterprise_id':'BT'}, 'enterprise_identity_mismatch'),
    ({'reporting_period':'FY2026'}, 'reporting_period_mismatch'),
    ({'artifact_url':''}, 'artifact_url_missing'),
    ({'artifact_url':'https://data.fca.org.uk/#/nsm/nationalstoragemechanism'}, 'artifact_url_not_downloadable'),
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
    if code == 'artifact_url_not_downloadable':
        diagnostic = run['structured_diagnostics'][0]
        assert diagnostic['failure_stage'] == 'governed source configuration'
        assert diagnostic['request_attempted'] is False
        assert diagnostic['safe_failure_message'] == 'The configured source is a search page rather than a filing download.'


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
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    receipt = bt.RetrievedPackage(bad, '0'*64, cfg['artifact_url'], 200, 'application/zip', 7)
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.extract_candidates(bad, cfg, receipt)
    assert exc.value.code == 'invalid_zip'
    unsafe = tmp_path / 'unsafe.zip'
    with zipfile.ZipFile(unsafe, 'w') as z: z.writestr('../x', 'x')
    with pytest.raises(bt.StructuredIngestionError) as slip:
        bt.validate_archive(unsafe, cfg)
    assert slip.value.code == 'unsafe_archive_path'


def test_adapter_handoff_diagnostic_and_correlation(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    receipt = bt.RetrievedPackage(tmp_path/'x.zip', 'a'*64, cfg['artifact_url'], 200, 'application/zip', 10)
    diag = bt._diagnostic('fi-ok', cfg, bt.StructuredIngestionError('', 'none', 'completed'), receipt, 4, 3, True)
    assert diag['support_reference'] == 'FI-ok'
    assert diag['adapter_handoff_attempted'] is True
    assert diag['candidate_fact_count'] == 4
    assert diag['canonical_fact_count'] == 3


def _ix_body(metric=True):
    facts = '<ix:nonFraction name="ifrs-full:Revenue" contextRef="c1" unitRef="GBP">1</ix:nonFraction>' if metric else ''
    return f'''<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:xbrli="http://www.xbrl.org/2003/instance">
    <xbrli:context id="c1"><xbrli:entity><xbrli:identifier>213800LRO7NS5CYQMN21</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:startDate>2025-04-01</xbrli:startDate><xbrli:endDate>2026-03-31</xbrli:endDate></xbrli:period></xbrli:context>{facts}</html>'''


def test_archive_diagnostics_and_nested_ixbrl_locator(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'nested.zip'
    with zipfile.ZipFile(package, 'w') as z:
        z.writestr('META-INF/reports.json', '{}')
        z.writestr('BT_Group_FY26/reports/consolidated/report.xhtml', _ix_body())
        z.writestr('BT_Group_FY26/taxonomy/bt-2026.xsd', '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"/>')
    diag = bt.inspect_archive(package, cfg)
    assert diag['central_directory_readable'] is True
    assert diag['archive_entry_count'] == 3
    assert diag['first_failing_safety_rule'] is None
    located = bt.locate_ixbrl_report(package, cfg)
    assert located['report_path'] == 'BT_Group_FY26/reports/consolidated/report.xhtml'
    assert located['diagnostics']['locator_decision'] == 'BT_Group_FY26/reports/consolidated/report.xhtml'


def test_precise_safety_failure_codes(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    too_many = tmp_path / 'too_many.zip'
    with zipfile.ZipFile(too_many, 'w') as z:
        z.writestr('a.txt', 'a'); z.writestr('b.txt', 'b')
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.validate_archive(too_many, {**cfg, 'entry_count_limit': 1})
    assert exc.value.code == 'archive_entry_limit_exceeded'
    too_big = tmp_path / 'too_big.zip'
    with zipfile.ZipFile(too_big, 'w') as z: z.writestr('a.txt', 'aaaa')
    with pytest.raises(bt.StructuredIngestionError) as big:
        bt.validate_archive(too_big, {**cfg, 'expanded_size_limit_bytes': 2})
    assert big.value.code == 'archive_expanded_size_exceeded'


def test_crc_failure_is_reported(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'crc.zip'
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_STORED) as z: z.writestr('a.txt', 'abc')
    data = bytearray(package.read_bytes()); idx = data.index(b'abc'); data[idx] ^= 0xFF; package.write_bytes(data)
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.validate_archive(package, cfg)
    assert exc.value.code in {'zip_crc_failure', 'invalid_zip'}


def test_locator_ambiguous_and_unsupported_layout(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    no_ix = tmp_path / 'no_ix.zip'
    with zipfile.ZipFile(no_ix, 'w') as z: z.writestr('nested/report.xhtml', '<html/>')
    with pytest.raises(bt.StructuredIngestionError) as missing:
        bt.locate_ixbrl_report(no_ix, cfg)
    assert missing.value.code == 'ixbrl_report_not_found'
    amb = tmp_path / 'amb.zip'
    with zipfile.ZipFile(amb, 'w') as z:
        z.writestr('a/report.xhtml', _ix_body())
        z.writestr('b/report.xhtml', _ix_body())
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.locate_ixbrl_report(amb, cfg)
    assert exc.value.code == 'multiple_ixbrl_reports_ambiguous'


def _ix_full(lei='213800LRO7NS5CYQMN21', start='2025-04-01', end='2026-03-31', facts=True):
    fact = '<ix:nonFraction name="ifrs-full:Revenue" contextRef="c1" unitRef="GBP">1</ix:nonFraction>' if facts else ''
    return f'''<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink">
    <head><ix:header><ix:references><link:schemaRef xlink:href="bt-2026.xsd"/></ix:references></ix:header></head>
    <body><xbrli:context id="c1"><xbrli:entity><xbrli:identifier>{lei}</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:startDate>{start}</xbrli:startDate><xbrli:endDate>{end}</xbrli:endDate></xbrli:period></xbrli:context>
    <ix:nonNumeric name="lei:LegalName" contextRef="c1">BT GROUP PLC</ix:nonNumeric>{fact}</body></html>'''


def test_htm_case_insensitive_candidate_discovery_and_marker_validation(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'bt.zip'
    with zipfile.ZipFile(package, 'w') as z:
        z.writestr('ixbrl-viewer.HTM', _ix_full())
    diag = bt.inspect_archive(package, cfg)
    assert diag['candidate_xhtml_html'] == ['ixbrl-viewer.HTM']
    located = bt.locate_ixbrl_report(package, cfg)
    assert located['report_path'] == 'ixbrl-viewer.HTM'
    selected = located['selected_candidate']
    assert {'ix:header', 'ix:nonFraction', 'ix:nonNumeric', 'xbrli:context', 'schemaRef'}.issubset(set(selected['markers_found']))
    assert selected['fact_count'] > 0
    assert selected['identity_result'] == 'matched'
    assert selected['period_result'] == 'matched'


def test_ordinary_html_and_viewer_wrapper_without_inline_facts_rejected(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'ordinary.zip'
    with zipfile.ZipFile(package, 'w') as z:
        z.writestr('index.htm', '<html><body>BT GROUP PLC</body></html>')
        z.writestr('viewer.html', '<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"><body>viewer shell</body></html>')
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.locate_ixbrl_report(package, cfg)
    assert exc.value.code == 'ixbrl_report_not_found'


@pytest.mark.parametrize('body', [_ix_full(lei='00000000000000000000'), _ix_full(start='2024-04-01', end='2025-03-31')])
def test_identity_and_period_mismatch_rejected(tmp_path, body):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'mismatch.zip'
    with zipfile.ZipFile(package, 'w') as z: z.writestr('ixbrl-viewer.htm', body)
    with pytest.raises(bt.StructuredIngestionError) as exc:
        bt.locate_ixbrl_report(package, cfg)
    assert exc.value.code == 'structured_report_locator_failed'


def test_taxonomy_linkbase_and_top_level_classification(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'classify.zip'
    with zipfile.ZipFile(package, 'w') as z:
        z.writestr('ixbrl-viewer.htm', _ix_full())
        z.writestr('bt-2026.xsd', '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"/>')
        z.writestr('bt-2026_pre.xml', '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase"/>')
        z.writestr('bt-2026_def.xml', '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase"/>')
        z.writestr('bt-2026_lab-en.xml', '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase"/>')
        z.writestr('bt-2026_cal.xml', '<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase"/>')
        z.writestr('META-INF/catalog.xml', '<catalog/>')
        z.writestr('META-INF/taxonomyPackage.xml', '<tp/>')
    diag = bt.inspect_archive(package, cfg)
    assert 'META-INF' in diag['top_level_directories']
    assert 'ixbrl-viewer.htm' in diag['top_level_files']
    assert diag['standalone_xbrl_instances'] == []
    assert 'bt-2026.xsd' in diag['extension_schemas']
    assert {'bt-2026_pre.xml','bt-2026_def.xml','bt-2026_lab-en.xml','bt-2026_cal.xml'} == set(diag['linkbases'])
    assert diag['catalog_metadata'] == ['META-INF/catalog.xml']
    assert diag['taxonomy_package_metadata'] == ['META-INF/taxonomyPackage.xml']

def test_incremental_marker_scanner_late_and_boundary_markers(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'late.zip'
    late = b'a' * 3_000_000 + b'<html xmlns:abc="http://www.xbrl.org/2013/inlineXBRL"><abc:nonFraction>1</abc:nonFraction>'
    with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('ixbrl-viewer.htm', late)
    with zipfile.ZipFile(package) as z:
        scan = bt._scan_ixbrl_markers(z, 'ixbrl-viewer.htm', chunk_size=1_000_001, overlap=64)
    assert scan['chunks_processed'] > 1
    assert scan['bytes_scanned'] == len(late)
    assert scan['end_of_entry_reached'] is True
    assert 'inline_xbrl_namespace_or_fact' in scan['markers_found']
    assert scan['memory_before_kb'] is not None


def test_namespace_equivalent_inline_xbrl_is_selected(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'ns.zip'
    body = '''<html xmlns:i="http://www.xbrl.org/2013/inlineXBRL" xmlns:x="http://www.xbrl.org/2003/instance"><i:header><i:references><link:schemaRef xmlns:link="http://www.xbrl.org/2003/linkbase"/></i:references></i:header><x:context id="c1"><x:entity><x:identifier>213800LRO7NS5CYQMN21</x:identifier></x:entity><x:period><x:startDate>2025-04-01</x:startDate><x:endDate>2026-03-31</x:endDate></x:period></x:context><i:nonFraction name="ifrs-full:Revenue" contextRef="c1" unitRef="GBP">1</i:nonFraction></html>'''
    with zipfile.ZipFile(package, 'w') as z:
        z.writestr('ixbrl-viewer.htm', body)
    located = bt.locate_ixbrl_report(package, cfg)
    assert located['report_path'] == 'ixbrl-viewer.htm'
    diag = located['diagnostics']
    assert diag['selected_report_path'] == 'ixbrl-viewer.htm'
    assert diag['identity_result']['ixbrl-viewer.htm'] == 'matched'
    assert diag['period_result']['ixbrl-viewer.htm'] == 'matched'
    assert diag['inline_xbrl_marker_results'][0]['marker_scan']['end_of_entry_reached'] is True


def test_no_supported_facts_not_reported_before_adapter_handoff(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    diag = bt._diagnostic('fi-x', cfg, bt.StructuredIngestionError('missing', 'no_supported_facts', 'structured fact validation'), adapter=False)
    assert diag['adapter_handoff_attempted'] is False
    assert diag['failure_code'] != 'no_supported_facts'
    assert diag['failure_stage'] == 'structured package recognition'


def test_viewer_wrapper_embedded_and_external_discovery(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'viewer.zip'
    embedded = '<script type="application/json" id="ixbrl-data">{"report":"reports/bt.xhtml"}</script>'
    external = '<script src="viewer.js"></script><a href="reports/bt.xhtml">raw</a>'
    with zipfile.ZipFile(package, 'w') as z:
        z.writestr('ixbrl-viewer.htm', f'<html><head>{embedded}</head><body>{external}</body></html>')
        z.writestr('META-INF/catalog.xml', '<catalog><rewriteURI uriStartString="https://x/" rewritePrefix="taxonomy/"/></catalog>')
        z.writestr('META-INF/taxonomyPackage.xml', '<taxonomyPackage><identifier>bt-fy26</identifier><name>BT GROUP PLC 2026</name><entryPoint><entryPointDocument href="bt-2026.xsd"/></entryPoint></taxonomyPackage>')
        z.writestr('bt-2026.xsd', '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="https://www.bt.com/2026"><xsd:annotation><xsd:appinfo><link:schemaRef xmlns:link="http://www.xbrl.org/2003/linkbase" xlink:href="base.xsd" xmlns:xlink="http://www.w3.org/1999/xlink"/></xsd:appinfo></xsd:annotation></xsd:schema>')
    result = bt.classify_structured_package(package, cfg)
    assert result['package_type'] == 'viewer_with_embedded_filing'
    assert result['raw_structured_data_exists_in_package'] is True
    assert 'reports/bt.xhtml' in result['embedded_filing_locations']
    assert 'reports/bt.xhtml' in result['external_filing_references']
    assert result['metadata']['taxonomy_package']['identifier'] == 'bt-fy26'


def test_scope_rejections_for_parent_and_subsidiary(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    parent = _ix_full().replace('<xbrli:entity>', '<xbrli:entity><xbrli:segment><xbrldi:explicitMember xmlns:xbrldi="http://xbrl.org/2006/xbrldi" dimension="scope">ParentCompany</xbrldi:explicitMember></xbrli:segment>')
    sub = _ix_full(lei='213800IM9RLR1AU4R889')
    for body, code in [(parent, 'structured_report_locator_failed'), (sub, 'structured_report_locator_failed')]:
        package = tmp_path / f'{code}{len(body)}.zip'
        with zipfile.ZipFile(package, 'w') as z: z.writestr('report.xhtml', body)
        with pytest.raises(bt.StructuredIngestionError) as exc:
            bt.locate_ixbrl_report(package, cfg)
        assert exc.value.code == code


def test_direct_raw_filing_retrieval_and_temp_cleanup(tmp_path, monkeypatch):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    raw = tmp_path / 'raw.xhtml'; raw.write_text(_ix_full())
    prepared = bt.prepare_raw_report_from_package(raw, 'report.xhtml', tmp_path / 'work')
    assert prepared.exists()
    shutil.rmtree(prepared.parent)
    assert not prepared.exists()


def test_prepare_raw_report_extracts_selected_zip_entry_not_whole_package(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'bt.zip'
    body = _ix_full()
    with zipfile.ZipFile(package, 'w') as z:
        z.writestr('ixbrl-viewer.htm', body)
        z.writestr('taxonomy/bt-2026.xsd', '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"/>')
    prepared = bt.prepare_raw_report_from_package(package, 'ixbrl-viewer.htm', tmp_path / 'work')
    assert prepared.name == 'ixbrl-viewer.htm'
    assert prepared.read_text() == body
    assert not zipfile.is_zipfile(prepared)
    located = bt.locate_ixbrl_report(package, cfg)
    assert located['report_path'] == 'ixbrl-viewer.htm'


def test_viewer_only_package_has_definitive_non_null_classification(tmp_path):
    cfg = json.loads(Path('tests/fixtures/bt_structured_source_config.json').read_text())
    package = tmp_path / 'viewer_only.zip'
    with zipfile.ZipFile(package, 'w') as z:
        z.writestr('ixbrl-viewer.htm', '<html><head><script src="viewer.js"></script></head><body>Rendered annual report shell</body></html>')
        z.writestr('META-INF/taxonomyPackage.xml', '<taxonomyPackage><entryPoint><entryPointDocument href="bt-2026.xsd"/></entryPoint></taxonomyPackage>')
        z.writestr('bt-2026.xsd', '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"/>')
    result = bt.classify_structured_package(package, cfg)
    assert result['package_type'] == 'viewer_only_no_structured_report'
    assert result['raw_structured_data_exists_in_package'] is False
    assert result['raw_report_path'] is None
