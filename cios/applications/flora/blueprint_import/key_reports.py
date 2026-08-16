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
    title = _value(obj, "title").casefold()
    publisher = _value(obj, "publisher").casefold()
    quality = _value(obj, "evidence_quality").casefold()
    source_type = _value(obj, "source_type").casefold()
    combined = " ".join((title, publisher, quality, source_type))
    external = ("analyst", "broker", "equity research", "market research", "market analysis")
    if any(term in combined for term in external):
        return "external"
    financial = ("annual report", "results", "earnings", "trading update", "financial report",
                 "investor results", "record performance")
    primary = any(term in quality for term in ("primary", "company", "filing"))
    return "company" if primary and any(term in combined for term in financial) else ""


def _findings(obj: SemanticObject) -> tuple[str, ...]:
    # These are governed extracts/summaries, not newly inferred report facts.
    supplied = [_value(obj, "supported_claim") or obj.statement,
                _value(obj, "extracted_fact_or_summary")]
    return tuple(dict.fromkeys(item for item in supplied if item))[:5]


def _project(obj: SemanticObject, provenance: str) -> KeyReport:
    source_url = _valid_governed_url(_value(obj, "url"))
    findings = _findings(obj)
    if source_url:
        availability = "REPORT AVAILABLE — DIRECT SOURCE LINK AVAILABLE"
    elif findings:
        availability = "REPORT AVAILABLE — EVIDENCE/EXTRACT AVAILABLE"
    else:
        availability = "REPORT REFERENCED — SOURCE DOCUMENT NOT SUPPLIED"
    return KeyReport(obj, provenance, _value(obj, "title") or business_object_id(obj),
                     _value(obj, "publisher") or "Publisher not supplied",
                     _value(obj, "publication_date") or obj.freshness,
                     _value(obj, "relevant_period"), findings, source_url, availability)


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
    return EnterpriseKeyReports(latest("company"), latest("external"))
