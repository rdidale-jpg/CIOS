from __future__ import annotations

import zipfile
from pathlib import Path
from types import SimpleNamespace

from cios.applications.flora.document_review import refresh_financial_intelligence
from cios.applications.flora.financial_intelligence import bt_structured


def _zip(path: Path, body: str, name='report.xhtml'):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(name, body)


def _body(extra=''):
    return f'''<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:xbrldi="http://xbrl.org/2006/xbrldi">
    <xbrli:context id="c1"><xbrli:entity><xbrli:identifier scheme="http://standards.iso.org/iso/17442">213800LRO7NS5CYQMN21</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:startDate>2025-04-01</xbrli:startDate><xbrli:endDate>2026-03-31</xbrli:endDate></xbrli:period></xbrli:context>
    <xbrli:unit id="GBP"><xbrli:measure>iso4217:GBP</xbrli:measure></xbrli:unit>
    <ix:nonFraction name="ifrs-full:Revenue" contextRef="c1" unitRef="GBP" decimals="-6">19,654</ix:nonFraction>
    <ix:nonFraction name="ifrs-full:OperatingProfitLoss" contextRef="c1" unitRef="GBP" decimals="-6">2,897</ix:nonFraction>
    <ix:nonFraction name="ifrs-full:ProfitLossBeforeTax" contextRef="c1" unitRef="GBP" decimals="-6">1,436</ix:nonFraction>{extra}</html>'''


def test_bt_structured_ingestion_creates_evidence_observations_model_and_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    z = tmp_path/'bt.zip'; _zip(z, _body())
    cfg = bt_structured.source_config()
    monkeypatch.setattr(bt_structured, 'retrieve_package', lambda cfg: bt_structured.RetrievedPackage(z, 'abc123', cfg['artifact_url'], 200, 'application/zip', z.stat().st_size))

    first = refresh_financial_intelligence(run_id='fi-bt-first')
    assert first['status'] == 'completed'
    assert first['run_status']['ai_calls_made'] == 0
    assert first['run_status']['pdf_fallback_calls_made'] == 0
    assert first['run_status']['structured_evidence_records'] == 3
    assert first['evidence_ids'] == ['EV-BT-FY26-REVENUE','EV-BT-FY26-OPERATING-PROFIT','EV-BT-FY26-PROFIT-BEFORE-TAX']
    assert first['enterprise_attributes_changed'] == [
        'financial_performance.metrics.revenue.FY26.actual',
        'financial_performance.metrics.operating_profit.FY26.actual',
        'financial_performance.metrics.profit_before_tax.FY26.actual',
    ]
    second = refresh_financial_intelligence(run_id='fi-bt-second')
    assert second['status'] == 'completed'
    assert second['run_status']['trusted_twin_changed'] is False
    assert second['trusted_state_after']['observations'] == 3
    assert second['trusted_state_after']['attributes'] == 3


def test_bt_structured_quarantines_wrong_period_dimension_and_zip_slip(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    bad = '<xbrli:context id="seg"><xbrli:entity><xbrli:identifier>213800LRO7NS5CYQMN21</xbrli:identifier><xbrli:segment><xbrldi:explicitMember dimension="x:y">x:z</xbrldi:explicitMember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:startDate>2025-04-01</xbrli:startDate><xbrli:endDate>2026-03-31</xbrli:endDate></xbrli:period></xbrli:context><ix:nonFraction name="ifrs-full:Revenue" contextRef="seg" unitRef="GBP">1</ix:nonFraction>'
    z = tmp_path/'bt.zip'; _zip(z, _body(bad))
    receipt = bt_structured.RetrievedPackage(z, 'abc123', 'https://www.bt.com/a.zip', 200, 'application/zip', z.stat().st_size)
    candidates, quarantine = bt_structured.extract_candidates(z, bt_structured.source_config(), receipt)
    assert len(candidates) == 3
    assert any(q['reason'] == 'unsupported_dimension_or_segment' for q in quarantine)
    slip = tmp_path/'slip.zip'
    with zipfile.ZipFile(slip, 'w') as zipf: zipf.writestr('../evil.xhtml', 'x')
    try:
        bt_structured.validate_archive(slip, bt_structured.source_config())
    except bt_structured.StructuredIngestionError as exc:
        assert exc.code == 'unsafe_archive_path'
    else:
        raise AssertionError('zip slip accepted')
