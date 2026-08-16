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

from .semantic_twin import (SemanticEnterprise, SemanticObject, SemanticTwin,
                            business_object_id, evidence_applicability,
                            evidence_subject_matches_enterprise)
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
    trace: KeyReportsTrace | None = None
    financial_state: str = "STATE 4"
    financial_selection: KeyReport | None = None
    report_reference: KeyReport | None = None
    financial_evidence: KeyReport | None = None


@dataclass(frozen=True)
class EvidenceQualification:
    """The decisions made for one actual object during report selection."""
    source: SemanticObject
    financial_related: bool
    company_candidate: bool
    report_identity: bool
    source_document: bool
    source_url: bool
    supplied_report: bool
    financial_reporting_evidence: bool
    eligible: bool
    rejection_stage: str
    rejection_reason: str
    applicable: bool = True
    applicability_reason: str = "Direct Enterprise Evidence."
    subject_match: bool = False
    company_report_eligible: bool = False


@dataclass(frozen=True)
class KeyReportsTrace:
    enterprise_identity: str
    evidence: tuple[SemanticObject, ...]
    qualifications: tuple[EvidenceQualification, ...]
    financial_candidates: int
    financial_reporting_evidence: int
    supplied_reports: int
    external_candidates: int
    report_references: int = 0
    fallback_candidates: int = 0


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


def _latest(rows: list[SemanticObject]) -> SemanticObject | None:
    """Apply the existing governed chronology/richness ordering."""
    if not rows:
        return None
    return max(rows, key=lambda obj: (
        _date_key(_value(obj, "publication_date") or obj.freshness),
        bool(_value(obj, "relevant_period") or _value(obj, "reporting_period")),
        len(_findings(obj)), business_object_id(obj)))


def key_reports_for_enterprise(ent: SemanticEnterprise, twin: SemanticTwin | None = None) -> EnterpriseKeyReports:
    """Select latest qualifying reports deterministically from owned Evidence."""
    # SemanticTwin is the canonical import-scoped Evidence owner.  The fallback
    # retains compatibility for callers constructing a standalone Enterprise.
    applicability = evidence_applicability(twin, ent) if twin is not None else ()
    evidence = (tuple(row.evidence for row in applicability) if twin is not None else
                tuple(obj for obj in ent.records if obj.kind == "evidence"))
    applicability_by_id = {business_object_id(row.evidence): row for row in applicability}
    qualifications = []
    for obj in evidence:
        semantics = classify_evidence(obj)
        identity = bool(_value(obj, "title"))
        url = bool(_valid_governed_url(_value(obj, "url")))
        # The canonical Evidence object can establish a report document only
        # through an explicitly governed source location/document field.
        document = url or bool(_value(obj, "source_document") or _value(obj, "document_reference"))
        subject_match = evidence_subject_matches_enterprise(obj, ent)
        supplied = semantics.is_company_financial_reporting and document and subject_match
        eligible = semantics.is_financial_reporting_evidence and subject_match
        if semantics.is_company_financial_reporting and not subject_match:
            stage, reason = ("ENTERPRISE SUBJECT", "Evidence is not company financial reporting for the dossier Enterprise.")
        elif eligible:
            stage, reason = ("None", "Eligible financial-reporting Evidence.")
        else:
            stage, reason = ("FINANCIAL SEMANTICS", semantics.rationale)
        qualifications.append(EvidenceQualification(
            obj, semantics.is_financial_reporting_evidence,
            semantics.is_company_financial_reporting, identity, document, url,
            supplied, semantics.is_financial_reporting_evidence, eligible, stage, reason,
            True, applicability_by_id.get(business_object_id(obj)).path if twin is not None else
            "Standalone Enterprise Evidence input.", subject_match,
            semantics.is_company_financial_reporting and subject_match))
    def latest(kind: str) -> KeyReport | None:
        rows = [obj for obj in evidence if _report_kind(obj) == kind and
                (kind != "company" or evidence_subject_matches_enterprise(obj, ent))]
        if not rows:
            return None
        # Richer extracts win duplicate same-date report references, then the
        # governed immutable identity supplies a stable final tie-break.
        selected = _latest(rows)
        assert selected is not None
        return _project(selected, "Company disclosure" if kind == "company" else "External analyst view")
    company_rows = [row.source for row in qualifications if row.supplied_report]
    reference_rows = [row.source for row in qualifications if row.company_report_eligible
                      and row.report_identity and not row.source_document]
    fallback_rows = [row.source for row in qualifications if row.financial_reporting_evidence
                     and not row.company_candidate and row.subject_match]
    company_source = _latest(company_rows)
    reference_source = _latest(reference_rows)
    fallback_source = _latest(fallback_rows)
    company = _project(company_source, "Company disclosure") if company_source else None
    reference = (_project(reference_source, "Governed report reference")
                 if reference_source else None)
    fallback = (_project(fallback_source, "Governed financial-reporting Evidence",
                         report_established=False) if fallback_source else None)
    if company:
        financial_state, financial_selection = "STATE 1", company
    elif reference:
        financial_state, financial_selection = "STATE 3", reference
    elif fallback:
        financial_state, financial_selection = "STATE 2", fallback
    else:
        financial_state, financial_selection = "STATE 4", None
    external = latest("external")
    trace = KeyReportsTrace(
        ent.identity_key, evidence, tuple(qualifications),
        sum(row.company_candidate for row in qualifications),
        sum(row.financial_reporting_evidence for row in qualifications),
        sum(row.supplied_report for row in qualifications),
        sum(classify_evidence(obj).is_external_research for obj in evidence),
        len(reference_rows), len(fallback_rows),
    )
    return EnterpriseKeyReports(company_report=company, external_report=external, trace=trace,
                                financial_state=financial_state,
                                financial_selection=financial_selection,
                                report_reference=reference, financial_evidence=fallback)


def functional_acceptance_for_financial_position(
    reports: EnterpriseKeyReports, financial_position_evidence_ids: tuple[str, ...]
) -> str:
    """Reject the demonstrated semantic contradiction, not merely unloaded code."""
    trace = reports.trace
    if trace is None:
        return "FAIL"
    if financial_position_evidence_ids and not trace.evidence:
        return "FAIL"
    expected_state = ("STATE 1" if any(row.supplied_report for row in trace.qualifications)
                      else "STATE 3" if trace.report_references
                      else "STATE 2" if trace.fallback_candidates else "STATE 4")
    selection_required = expected_state != "STATE 4"
    return "PASS" if (reports.financial_state == expected_state and
                      bool(reports.financial_selection) == selection_required) else "FAIL"
