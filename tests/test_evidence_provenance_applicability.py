"""Generic regressions for Evidence provenance versus applicability."""
from __future__ import annotations

from cios.applications.flora.blueprint_import.key_reports import key_reports_for_enterprise
from cios.applications.flora.blueprint_import.semantic_twin import (
    SemanticEnterprise, SemanticObject, SemanticTwin, evidence_applicability,
    evidence_publisher, evidence_subject,
)


def _evidence(identity: str, subject: str, publisher: str, date: str, *, report: bool = True):
    return SemanticObject(identity, "evidence", "Revenue and EBITDA were reported.", subject, (), date,
        "High", "candidate", "evidence.json", {}, False, original_id=identity,
        attributes={"title": "Annual results" if report else "Regulatory market review",
                    "supported_object": subject, "publisher": publisher,
                    "publication_date": date,
                    "evidence_quality": "Primary company filing" if report else "Primary regulator",
                    "url": f"https://example.test/{identity}"})


def _enterprise(identity: str, name: str, records=()):
    return SemanticEnterprise(identity, identity.casefold(), name, (name,), tuple(records), identity, identity, identity)


def _context(identity: str, subject: str, refs: tuple[str, ...]):
    return SemanticObject(identity, "observation", "Relevant context.", subject, refs, "2026-01-01",
                          "High", "candidate", "context.json", {}, True, original_id=identity)


def test_newer_competitor_report_cannot_replace_enterprise_report():
    own = _evidence("EV-A", "Enterprise A", "Enterprise A", "2025-01-01")
    competitor = _evidence("EV-B", "Enterprise B", "Enterprise B", "2026-01-01")
    a = _enterprise("ENT-A", "Enterprise A", (own, _context("OBS-A", "Enterprise A", ("EV-B",))))
    b = _enterprise("ENT-B", "Enterprise B", (competitor,))
    twin = SemanticTwin((own, competitor, *a.records[1:]), (a, b))

    paths = {row.evidence.original_id: row for row in evidence_applicability(twin, a)}
    assert paths["EV-B"].verdict == "CROSS-ENTERPRISE-EXPLAINED"
    assert key_reports_for_enterprise(a, twin).company_report.source is own


def test_competitor_report_does_not_fill_an_empty_company_slot():
    competitor = _evidence("EV-B", "Enterprise B", "Enterprise B", "2026-01-01")
    context = _context("OBS-A", "Enterprise A", ("EV-B",))
    a = _enterprise("ENT-A", "Enterprise A", (context,))
    twin = SemanticTwin((competitor, context), (a, _enterprise("ENT-B", "Enterprise B", (competitor,))))
    assert key_reports_for_enterprise(a, twin).company_report is None


def test_shared_regulatory_evidence_retains_subject_and_publisher():
    regulator = _evidence("EV-REG", "Telecoms market", "Regulator", "2026-01-01", report=False)
    a_context = _context("OBS-A", "Enterprise A", ("EV-REG",))
    b_context = _context("OBS-B", "Enterprise B", ("EV-REG",))
    a, b = _enterprise("ENT-A", "Enterprise A", (a_context,)), _enterprise("ENT-B", "Enterprise B", (b_context,))
    twin = SemanticTwin((regulator, a_context, b_context), (a, b))
    assert all(any(row.evidence is regulator for row in evidence_applicability(twin, ent)) for ent in (a, b))
    assert evidence_subject(regulator) == "Telecoms market"
    assert evidence_publisher(regulator) == "Regulator"
    assert all(key_reports_for_enterprise(ent, twin).company_report is None for ent in (a, b))


def test_parent_report_can_apply_without_becoming_subsidiary_report():
    parent_report = _evidence("EV-PARENT", "Parent plc; Subsidiary Ltd", "Parent plc", "2026-01-01")
    parent = _enterprise("ENT-PARENT", "Parent plc", (parent_report,))
    subsidiary = _enterprise("ENT-SUB", "Subsidiary Ltd", ())
    twin = SemanticTwin((parent_report,), (parent, subsidiary))
    paths = evidence_applicability(twin, subsidiary)
    assert paths and paths[0].verdict == "DIRECT"
    assert "primary subject remains Parent plc" in paths[0].path
    assert key_reports_for_enterprise(subsidiary, twin).company_report is None

