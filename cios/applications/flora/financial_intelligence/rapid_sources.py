"""Governed rapid official-source acquisition for Flora Financial Intelligence.

Slice 2A only: this module validates a configured official PDF source and returns
runtime lineage derived from actual downloaded bytes. It does not extract
financial facts, call AI providers, or update canonical Evidence, Observations or
Enterprise Model memory.
"""
from __future__ import annotations

import json, tempfile, time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterator
from urllib.parse import urlparse

from cios.applications.flora.live.documents import DocumentFetchResult, fetch_document, parse_pdf_document

CONFIG_DIR = Path(__file__).resolve().parents[4] / "config" / "flora" / "rapid_sources"

FAILURE_CODES = {
    "rapid_source_configuration_missing", "rapid_source_configuration_invalid", "rapid_source_not_selected",
    "rapid_source_url_missing", "rapid_source_url_invalid", "rapid_source_host_not_approved",
    "rapid_source_http_error", "rapid_source_redirect_rejected", "rapid_source_content_type_rejected",
    "rapid_source_too_small", "rapid_source_too_large", "rapid_source_not_pdf", "rapid_source_parse_failed",
    "rapid_source_identity_mismatch", "rapid_source_period_mismatch", "rapid_source_integrity_failed",
    "rapid_source_timeout",
}

@dataclass(frozen=True)
class RapidSourceManifest:
    configuration_key: str; selected: bool; priority: int; enterprise_id: str; legal_name: str
    reporting_period: str; period_start: str; period_end: str; scope: str; source_id: str
    source_kind: str; authority: str; document_title: str; publication_date: str; artifact_url: str
    approved_hosts: tuple[str, ...]; accepted_content_types: tuple[str, ...]; minimum_bytes: int
    maximum_bytes: int; maximum_redirects: int; identity_markers: tuple[str, ...]; period_markers: tuple[str, ...]

@dataclass(frozen=True)
class RapidSourceReceipt:
    source_id: str; configuration_key: str; enterprise_id: str; legal_name: str; authority: str
    source_kind: str; document_title: str; publication_date: str; reporting_period: str
    period_start: str; period_end: str; scope: str; requested_url: str | None; final_url: str | None
    artifact_host: str | None; http_status: int | None; content_type: str | None; bytes_downloaded: int
    sha256: str | None; retrieved_at: str; request_attempted: bool; redirect_chain: tuple[str, ...]
    pdf_magic_valid: bool; document_parse_result: str; identity_result: str; period_result: str
    validation_result: str; failure_code: str | None; failure_stage: str | None; safe_failure_message: str | None
    ai_call_count: int = 0; provider_cost: float = 0.0; external_source_call_count: int = 0; retry_count: int = 0; elapsed_ms: int = 0
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class AcquiredRapidSource:
    path: Path
    receipt: RapidSourceReceipt

class RapidSourceAcquisitionError(RuntimeError):
    def __init__(self, code: str, stage: str, message: str, receipt: RapidSourceReceipt | None = None, field_errors: dict[str, str] | None = None):
        super().__init__(message); self.code = code; self.stage = stage; self.safe_message = message; self.receipt = receipt; self.field_errors = field_errors or {}

def _receipt(m: RapidSourceManifest | None, **kw: Any) -> RapidSourceReceipt:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    base = dict(source_id="", configuration_key="", enterprise_id="", legal_name="", authority="", source_kind="", document_title="", publication_date="", reporting_period="", period_start="", period_end="", scope="", requested_url=None, final_url=None, artifact_host=None, http_status=None, content_type=None, bytes_downloaded=0, sha256=None, retrieved_at=now, request_attempted=False, redirect_chain=(), pdf_magic_valid=False, document_parse_result="not_attempted", identity_result="not_attempted", period_result="not_attempted", validation_result="rejected", failure_code=None, failure_stage=None, safe_failure_message=None)
    if m:
        base.update({"source_id":m.source_id,"configuration_key":m.configuration_key,"enterprise_id":m.enterprise_id,"legal_name":m.legal_name,"authority":m.authority,"source_kind":m.source_kind,"document_title":m.document_title,"publication_date":m.publication_date,"reporting_period":m.reporting_period,"period_start":m.period_start,"period_end":m.period_end,"scope":m.scope,"requested_url":m.artifact_url})
    base.update(kw); return RapidSourceReceipt(**base)

def _fail(code: str, stage: str, message: str, m: RapidSourceManifest | None = None, field_errors: dict[str,str] | None = None, **kw: Any) -> None:
    raise RapidSourceAcquisitionError(code, stage, message, _receipt(m, failure_code=code, failure_stage=stage, safe_failure_message=message, **kw), field_errors)

def _manifest_from_dict(data: dict[str, Any]) -> RapidSourceManifest:
    required = RapidSourceManifest.__dataclass_fields__.keys(); errors = {k:"missing" for k in required if k not in data}
    if errors: _fail("rapid_source_configuration_invalid", "configuration", "Rapid source configuration is missing required fields.", None, errors)
    return RapidSourceManifest(**{**data, "approved_hosts":tuple(data["approved_hosts"]), "accepted_content_types":tuple(x.lower() for x in data["accepted_content_types"]), "identity_markers":tuple(data["identity_markers"]), "period_markers":tuple(data["period_markers"])})

def load_rapid_source_manifest(enterprise_id: str, reporting_period: str, configuration_key: str | None = None, config_dir: Path = CONFIG_DIR) -> RapidSourceManifest:
    if not config_dir.exists(): _fail("rapid_source_configuration_missing", "configuration", "Rapid source configuration directory is missing.")
    matches=[]
    for path in sorted(config_dir.glob("*.json")):
        data=json.loads(path.read_text())
        if configuration_key and data.get("configuration_key") != configuration_key: continue
        if data.get("enterprise_id") == enterprise_id and data.get("reporting_period") == reporting_period: matches.append(data)
    if not matches: _fail("rapid_source_configuration_missing", "configuration", "No matching rapid source configuration was found.")
    return _manifest_from_dict(sorted(matches, key=lambda d: d.get("priority", 999))[0])

def validate_rapid_source_manifest(m: RapidSourceManifest, enterprise_id: str, reporting_period: str) -> None:
    errors={}
    if not m.selected: _fail("rapid_source_not_selected", "configuration", "Rapid source configuration is not selected.", m)
    if m.enterprise_id != enterprise_id: errors["enterprise_id"]="does not match request"
    if m.reporting_period != reporting_period: errors["reporting_period"]="does not match request"
    if not (m.artifact_url or "").strip(): _fail("rapid_source_url_missing", "configuration", "Rapid source artifact URL is missing.", m)
    parsed=urlparse(m.artifact_url)
    if parsed.scheme != "https" or not parsed.netloc: _fail("rapid_source_url_invalid", "configuration", "Rapid source artifact URL must be HTTPS.", m)
    if parsed.hostname not in m.approved_hosts: _fail("rapid_source_host_not_approved", "configuration", "Rapid source artifact host is not approved.", m)
    if m.minimum_bytes < 0 or m.maximum_bytes <= m.minimum_bytes: errors["byte_limits"]="invalid"
    if errors: _fail("rapid_source_configuration_invalid", "configuration", "Rapid source configuration is invalid.", m, errors)

def _source(m: RapidSourceManifest):
    return SimpleNamespace(source_id=m.source_id, source_name=m.document_title, organisation=m.legal_name, url=m.artifact_url, source_type=m.source_kind, evidence_tier="tier_1_company", authority_tier="tier_1_company_authoritative")

@contextmanager
def acquire_rapid_financial_source(enterprise_id: str, reporting_period: str, configuration_key: str | None = None, *, config_dir: Path = CONFIG_DIR) -> Iterator[AcquiredRapidSource]:
    start=time.monotonic(); temp_path=None; cache_path=None; m=load_rapid_source_manifest(enterprise_id, reporting_period, configuration_key, config_dir); validate_rapid_source_manifest(m, enterprise_id, reporting_period)
    try:
        fetched: DocumentFetchResult = fetch_document(m.artifact_url, max_bytes=m.maximum_bytes)
        cache_path = Path(fetched.local_path) if fetched.local_path else None
        host=urlparse(fetched.final_url or m.artifact_url).hostname
        base=dict(request_attempted=True, final_url=fetched.final_url or m.artifact_url, artifact_host=host, http_status=fetched.status_code, content_type=(fetched.media_type or "").lower(), bytes_downloaded=len(fetched.content), sha256=fetched.checksum or None, redirect_chain=tuple(fetched.redirect_chain), external_source_call_count=1)
        if not fetched.succeeded:
            code = "rapid_source_timeout" if "timed out" in (fetched.error or "").lower() else "rapid_source_http_error"
            _fail(code, "retrieval", "Rapid source retrieval failed.", m, **base)
        if len(base["redirect_chain"]) > m.maximum_redirects + 1 or host not in m.approved_hosts: _fail("rapid_source_redirect_rejected", "retrieval", "Rapid source redirect was rejected.", m, **base)
        if base["content_type"] not in m.accepted_content_types: _fail("rapid_source_content_type_rejected", "retrieval", "Rapid source content type is not accepted.", m, **base)
        if len(fetched.content) < m.minimum_bytes: _fail("rapid_source_too_small", "validation", "Rapid source is smaller than the configured minimum.", m, **base)
        if len(fetched.content) > m.maximum_bytes: _fail("rapid_source_too_large", "validation", "Rapid source is larger than the configured maximum.", m, **base)
        if not fetched.content.startswith(b"%PDF"): _fail("rapid_source_not_pdf", "validation", "Rapid source is not a valid PDF.", m, **base)
        temp = tempfile.NamedTemporaryFile(prefix="flora-rapid-source-", suffix=".pdf", delete=False); temp.write(fetched.content); temp.close(); temp_path=Path(temp.name)
        parse = parse_pdf_document(replace(fetched, local_path=str(temp_path)), _source(m), canonical_enterprise_id=m.enterprise_id)
        parse_result = "parsed" if parse.parser_status == "parsed" and parse.page_count > 0 else "failed"
        if parse_result != "parsed": _fail("rapid_source_parse_failed", "validation", "Rapid source PDF parsing failed.", m, document_parse_result=parse_result, pdf_magic_valid=True, **base)
        text="\n".join(p.text for p in parse.pages)
        if not any(marker in text for marker in m.identity_markers): _fail("rapid_source_identity_mismatch", "validation", "Rapid source issuer identity marker was not found.", m, document_parse_result="parsed", pdf_magic_valid=True, identity_result="mismatch", **base)
        if not any(marker in text for marker in m.period_markers): _fail("rapid_source_period_mismatch", "validation", "Rapid source reporting-period marker was not found.", m, document_parse_result="parsed", pdf_magic_valid=True, identity_result="matched", period_result="mismatch", **base)
        receipt=_receipt(m, **base, pdf_magic_valid=True, document_parse_result="parsed", identity_result="matched", period_result="matched", validation_result="accepted", elapsed_ms=int((time.monotonic()-start)*1000))
        yield AcquiredRapidSource(temp_path, receipt)
    except RapidSourceAcquisitionError as exc:
        if exc.receipt and temp_path and temp_path.exists(): object.__setattr__(exc, "receipt", replace(exc.receipt, elapsed_ms=int((time.monotonic()-start)*1000)))
        raise
    finally:
        for p in (temp_path, cache_path):
            if p:
                try: Path(p).unlink(missing_ok=True)
                except OSError: pass
