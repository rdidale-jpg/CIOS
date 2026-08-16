"""Read-only report navigation over governed Evidence candidates.

The projection owns neither Evidence nor financial facts.  It selects metadata
already supplied by the import-scoped Evidence owner and links back to that
unchanged candidate.  In particular, it never manufactures a URL or promotes
an external view into a company fact.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from urllib.parse import urlparse

from .semantic_twin import SemanticEnterprise, SemanticObject, business_object_id
from .evidence_semantics import classify_evidence


@dataclass(frozen=True)
class KeyReport:
    source: SemanticObject
    provenance: str
    title: str
    publisher: str
    publication_date: str
    reporting_period: str
    findings: tuple[str, ...]
    source_url: str
    availability: str
    source_document_supplied: bool


@dataclass(frozen=True)
class EnterpriseKeyReports:
    company_report: KeyReport | None
    external_report: KeyReport | None


def _value(obj: SemanticObject, name: str) -> str:
    value = (obj.attributes or {}).get(name)
    return str(value).strip() if value not in (None, "", [], {}) else ""


def _valid_governed_url(value: str) -> str:
    """Return only an explicitly supplied HTTP(S) source location."""
    if not value:
        return ""
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and bool(parsed.netloc) else ""


def _date_key(value: str) -> tuple[int, int, int]:
    try:
        parsed = date.fromisoformat(value)
        return parsed.year, parsed.month, parsed.day
    except ValueError:
        try:
            return int(value), 0, 0
        except (TypeError, ValueError):
            return 0, 0, 0


def _report_kind(obj: SemanticObject) -> str:
    semantics = classify_evidence(obj)
    if semantics.is_external_research:
        return "external"
    return "company" if semantics.is_company_financial_reporting else ""


def _financial_evidence(obj: SemanticObject) -> bool:
    semantics = classify_evidence(obj)
    return semantics.is_financial_reporting_evidence and not semantics.is_company_financial_reporting


def _findings(obj: SemanticObject) -> tuple[str, ...]:
    # These are governed extracts/summaries, not newly inferred report facts.
    supplied = [_value(obj, "supported_claim") or obj.statement,
                _value(obj, "extracted_fact_or_summary")]
    return tuple(dict.fromkeys(item for item in supplied if item))[:5]


def _project(obj: SemanticObject, provenance: str, *, report_established: bool = True) -> KeyReport:
    source_url = _valid_governed_url(_value(obj, "url"))
    findings = _findings(obj)
    if not report_established:
        availability = "FINANCIAL REPORTING EVIDENCE AVAILABLE"
    elif source_url:
        availability = "REPORT AVAILABLE — DIRECT SOURCE LINK AVAILABLE"
    elif provenance != "Company disclosure" and findings:
        availability = "REPORT AVAILABLE — EVIDENCE/EXTRACT AVAILABLE"
    else:
        availability = "REPORT REFERENCED — SOURCE DOCUMENT NOT SUPPLIED"
    return KeyReport(obj, provenance, _value(obj, "title") or business_object_id(obj),
                     _value(obj, "publisher") or "Publisher not supplied",
                     _value(obj, "publication_date") or obj.freshness,
                     _value(obj, "relevant_period"), findings, source_url, availability,
                     report_established and bool(source_url))


def key_reports_for_enterprise(ent: SemanticEnterprise) -> EnterpriseKeyReports:
    """Select latest qualifying reports deterministically from owned Evidence."""
    evidence = tuple(obj for obj in ent.records if obj.kind == "evidence")
    def latest(kind: str) -> KeyReport | None:
        rows = [obj for obj in evidence if _report_kind(obj) == kind]
        if not rows:
            return None
        # Richer extracts win duplicate same-date report references, then the
        # governed immutable identity supplies a stable final tie-break.
        selected = max(rows, key=lambda obj: (
            _date_key(_value(obj, "publication_date") or obj.freshness),
            bool(_value(obj, "relevant_period")), len(_findings(obj)), business_object_id(obj)))
        return _project(selected, "Company disclosure" if kind == "company" else "External analyst view")
    company = latest("company")
    if company is None:
        # Financial intelligence is not the same thing as a supplied report.
        # Preserve the governed evidence path without promoting it to a report.
        rows = [obj for obj in evidence if _financial_evidence(obj)]
        if rows:
            selected = max(rows, key=lambda obj: (
                _date_key(_value(obj, "publication_date") or obj.freshness),
                bool(_value(obj, "relevant_period")), len(_findings(obj)), business_object_id(obj)))
            company = _project(selected, "Financial reporting evidence", report_established=False)
    return EnterpriseKeyReports(company, latest("external"))
