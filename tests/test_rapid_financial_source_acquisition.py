import hashlib
import json
from pathlib import Path

import pytest
from reportlab.platypus import SimpleDocTemplate, Paragraph

from cios.applications.flora.financial_intelligence import rapid_sources as rapid
from cios.applications.flora.live.documents import DocumentFetchResult


def _pdf_bytes(tmp_path: Path, text="BT Group plc Results for the full year to 31 March 2026 FY26") -> bytes:
    p = tmp_path / (hashlib.sha1(text.encode()).hexdigest() + ".pdf")
    doc = SimpleDocTemplate(str(p))
    story = [Paragraph(text + (" filler" * 1800), None)]
    doc.build(story)
    raw = p.read_bytes()
    assert raw.startswith(b"%PDF")
    return raw


def _config_dir(tmp_path: Path, **overrides):
    data = json.loads(Path("config/flora/rapid_sources/bt-group-plc-fy26.json").read_text())
    data["minimum_bytes"] = 100
    data.update(overrides)
    d = tmp_path / "rapid_sources"; d.mkdir()
    (d / "bt.json").write_text(json.dumps(data))
    return d, data


def _fetch(raw: bytes, media_type="application/pdf", final_url=None, status=200):
    url = "https://www.bt.com/fy26-release.pdf"
    return DocumentFetchResult(url, True, status, media_type, raw, hashlib.sha256(raw).hexdigest(), "", "2026-07-06T00:00:00+00:00", final_url=final_url or url, redirect_chain=())


def test_valid_selected_manifest_loads(tmp_path):
    d, _ = _config_dir(tmp_path)
    m = rapid.load_rapid_source_manifest("bt-group-plc", "FY26", config_dir=d)
    rapid.validate_rapid_source_manifest(m, "bt-group-plc", "FY26")
    assert m.selected is True
    assert m.configuration_key == "bt-group-plc-fy26-results-release"


def test_missing_manifest_fails_before_request(tmp_path, monkeypatch):
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: pytest.fail("no request"))
    with pytest.raises(rapid.RapidSourceAcquisitionError) as exc:
        with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=tmp_path): pass
    assert exc.value.code == "rapid_source_configuration_missing"
    assert exc.value.receipt.request_attempted is False


@pytest.mark.parametrize("override,code", [
    ({"artifact_url":""}, "rapid_source_url_missing"),
    ({"artifact_url":"http://www.bt.com/fy26.pdf"}, "rapid_source_url_invalid"),
    ({"artifact_url":"https://evil.example/fy26.pdf"}, "rapid_source_host_not_approved"),
    ({"selected": False}, "rapid_source_not_selected"),
])
def test_invalid_configuration_fails_before_request(tmp_path, monkeypatch, override, code):
    d, _ = _config_dir(tmp_path, **override)
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: pytest.fail("no request"))
    with pytest.raises(rapid.RapidSourceAcquisitionError) as exc:
        with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=d): pass
    assert exc.value.code == code
    assert exc.value.receipt.request_attempted is False


def test_valid_pdf_bytes_create_accepted_receipt_and_cleanup(tmp_path, monkeypatch):
    raw = _pdf_bytes(tmp_path)
    d, _ = _config_dir(tmp_path)
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: _fetch(raw))
    with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=d) as acquired:
        inside = acquired.path
        assert inside.exists()
        r = acquired.receipt
        assert r.validation_result == "accepted"
        assert r.sha256 == hashlib.sha256(raw).hexdigest()
        assert r.bytes_downloaded == len(raw)
        assert r.identity_result == "matched"
        assert r.period_result == "matched"
        assert r.ai_call_count == 0 and r.provider_cost == 0 and r.external_source_call_count == 1
    assert not inside.exists()


def test_octet_stream_with_valid_pdf_magic_is_accepted(tmp_path, monkeypatch):
    raw = _pdf_bytes(tmp_path)
    d, _ = _config_dir(tmp_path)
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: _fetch(raw, "application/octet-stream"))
    with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=d) as acquired:
        assert acquired.receipt.validation_result == "accepted"


@pytest.mark.parametrize("raw,media_type,code", [
    (b"<html>not pdf</html>" * 20, "application/pdf", "rapid_source_not_pdf"),
    (b"%PDF tiny", "application/pdf", "rapid_source_too_small"),
    (b"%PDF-1.4\n%%EOF" + b"x"*500, "application/pdf", "rapid_source_parse_failed"),
])
def test_invalid_payloads_rejected_and_cleanup(tmp_path, monkeypatch, raw, media_type, code):
    d, _ = _config_dir(tmp_path)
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: _fetch(raw, media_type))
    with pytest.raises(rapid.RapidSourceAcquisitionError) as exc:
        with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=d): pass
    assert exc.value.code == code
    assert exc.value.receipt.request_attempted is True
    assert not list(Path("/tmp").glob("flora-rapid-source-*.pdf"))


def test_oversized_response_is_rejected_safely(tmp_path, monkeypatch):
    raw = _pdf_bytes(tmp_path)
    d, _ = _config_dir(tmp_path, maximum_bytes=len(raw)-1, minimum_bytes=100)
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: _fetch(raw))
    with pytest.raises(rapid.RapidSourceAcquisitionError) as exc:
        with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=d): pass
    assert exc.value.code == "rapid_source_too_large"


def test_redirect_to_unapproved_host_is_rejected(tmp_path, monkeypatch):
    raw = _pdf_bytes(tmp_path)
    d, _ = _config_dir(tmp_path)
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: _fetch(raw, final_url="https://evil.example/fy26.pdf"))
    with pytest.raises(rapid.RapidSourceAcquisitionError) as exc:
        with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=d): pass
    assert exc.value.code == "rapid_source_redirect_rejected"


@pytest.mark.parametrize("text,code", [
    ("Other plc Results for the full year to 31 March 2026 FY26", "rapid_source_identity_mismatch"),
    ("BT Group plc Results for the full year to 31 March 2025 FY25", "rapid_source_period_mismatch"),
])
def test_identity_and_period_mismatch_are_validation_failures(tmp_path, monkeypatch, text, code):
    raw = _pdf_bytes(tmp_path, text)
    d, _ = _config_dir(tmp_path)
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: _fetch(raw))
    with pytest.raises(rapid.RapidSourceAcquisitionError) as exc:
        with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=d): pass
    assert exc.value.code == code
    assert exc.value.stage == "validation"


def test_http_error_receipt_and_no_ai_or_canonical_calls(tmp_path, monkeypatch):
    d, _ = _config_dir(tmp_path)
    monkeypatch.setattr(rapid, "fetch_document", lambda *a, **k: DocumentFetchResult(a[0], False, 404, "text/html", b"", "", "", "now", error="HTTP 404", final_url=a[0]))
    with pytest.raises(rapid.RapidSourceAcquisitionError) as exc:
        with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26", config_dir=d): pass
    assert exc.value.code == "rapid_source_http_error"
    assert exc.value.receipt.ai_call_count == 0


@pytest.mark.skipif(__import__("os").environ.get("FLORA_LIVE_RAPID_SOURCE_TEST") != "1", reason="opt-in live rapid source smoke test")
def test_live_bt_rapid_source_smoke():
    with rapid.acquire_rapid_financial_source("bt-group-plc", "FY26") as acquired:
        r = acquired.receipt
        assert r.http_status and 200 <= r.http_status < 300
        assert r.bytes_downloaded > 0
        assert r.sha256
        assert r.identity_result == "matched"
        assert r.period_result == "matched"
        assert r.validation_result == "accepted"
        assert r.ai_call_count == 0
