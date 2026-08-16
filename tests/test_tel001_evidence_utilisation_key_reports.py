"""TEL-001 acceptance for governed report utilisation and truthful states."""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.executive_enterprise_intelligence import executive_enterprise_intelligence
from cios.applications.flora.blueprint_import.executive_workspace import _dossier, _semantic_candidates
from cios.applications.flora.blueprint_import.key_reports import key_reports_for_enterprise
from cios.applications.flora.blueprint_import.semantic_twin import SemanticEnterprise, SemanticObject, assemble_semantic_twin, resolve_relationships


FIXTURE = Path("docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip")


def _runtime(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    package = BlueprintPackageRegistry().receive(FIXTURE.read_bytes(), FIXTURE.name, "evidence-auditor")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "evidence-auditor")
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    return package, summary, assemble_semantic_twin(_semantic_candidates(package, summary["candidates"]))


def test_bt_key_report_is_latest_governed_company_evidence(monkeypatch, tmp_path):
    package, summary, twin = _runtime(monkeypatch, tmp_path)
    bt = next(ent for ent in twin.enterprises if ent.name == "BT Group")
    before = tuple((obj.record_id, obj.attributes) for obj in twin.objects)
    reports = key_reports_for_enterprise(bt)

    assert reports.company_report is not None
    assert reports.company_report.source.original_id == "EV-BT-Q1FY27-W4"
    assert reports.company_report.publication_date == "2026-07-23"
    assert reports.company_report.reporting_period == "Q1 FY27"
    assert reports.company_report.source_url == reports.company_report.source.attributes["url"]
    assert reports.company_report.findings[0] == reports.company_report.source.attributes["supported_claim"]
    assert reports.company_report.provenance == "Company disclosure"
    assert reports.external_report is None

    html = _dossier(bt, twin, package.import_run_id, None)
    assert "Key reports" in html and "Latest company financial reporting" in html
    assert "Company disclosure" in html and "EV-BT-Q1FY27-W4" in html
    assert "REPORT AVAILABLE — DIRECT SOURCE LINK AVAILABLE" in html
    assert "Latest external analyst / market research" in html
    assert "NO QUALIFYING REPORT SUPPLIED" in html
    assert "External analyst view" not in html
    assert before == tuple((obj.record_id, obj.attributes) for obj in twin.objects)
    counts = Counter(row["candidate_object_class"] for row in summary["candidates"] if row["validation_status"] == "accepted")
    assert (counts["relationship"], counts["transformation_programme"], counts["opportunity_hypothesis"]) == (308, 13, 17)
    assert len(resolve_relationships(twin)) == 308


def test_report_states_external_label_and_no_fabricated_url():
    base = SemanticObject("ev-1", "evidence", "A governed market conclusion.", "Example", (),
                          "2026-01-01", "High", "candidate", "evidence.ndjson", {"line": 1}, False,
                          original_id="EV-EXTERNAL", attributes={"title": "Market analysis", "publisher": "Analyst House",
                          "publication_date": "2026-01-01", "evidence_quality": "External market analysis",
                          "supported_claim": "A governed market conclusion.", "url": "not a governed URL"})
    ent = SemanticEnterprise("ENT-X", "x", "Example", (), (base,))
    report = key_reports_for_enterprise(ent).external_report
    assert report is not None and report.provenance == "External analyst view"
    assert report.source_url == ""
    assert report.availability == "REPORT AVAILABLE — EVIDENCE/EXTRACT AVAILABLE"

    referenced = replace(base, statement="", attributes={"title": "Equity research note", "publisher": "Broker",
                         "publication_date": "2026-02-01", "evidence_quality": "Broker research"})
    report = key_reports_for_enterprise(replace(ent, records=(referenced,))).external_report
    assert report is not None
    assert report.availability == "REPORT REFERENCED — SOURCE DOCUMENT NOT SUPPLIED"
    assert report.findings == () and report.source_url == ""


def test_bt_executive_corrections_consume_canonical_identity_and_timing(monkeypatch, tmp_path):
    _package, _summary, twin = _runtime(monkeypatch, tmp_path)
    bt = next(ent for ent in twin.enterprises if ent.name == "BT Group")
    result = executive_enterprise_intelligence(bt, twin)
    assert len({signal.source_id for signal in result.signals}) == len(result.signals)
    assert len(result.watchpoints) == 3
    assert all("Next monitoring date:" in watch.explanation for watch in result.watchpoints)
    assert {watch.explanation.split(" · ", 1)[0] for watch in result.watchpoints} == {
        "Next monitoring date: 2026-10-31", "Next monitoring date: 2026-11-30"}
    assert all(watch.source_id.startswith("OPP-BT-") for watch in result.watchpoints)
    panel = " ".join((signal.title + " " + signal.explanation) for signal in result.signals)
    assert "Ai Pressure:" not in panel
    assert "investment budget remains unknown" in panel
