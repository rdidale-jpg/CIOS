"""TEL-001 acceptance for governed report utilisation and truthful states."""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.executive_enterprise_intelligence import executive_enterprise_intelligence
from cios.applications.flora.blueprint_import.executive_workspace import _dossier, _semantic_candidates
from cios.applications.flora.blueprint_import.key_reports import key_reports_for_enterprise
from cios.applications.flora.blueprint_import.evidence_semantics import classify_evidence
from cios.applications.flora.blueprint_import.semantic_twin import (SemanticEnterprise, SemanticObject,
    assemble_semantic_twin, business_object_id, enterprise_associations, resolve_relationships)


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
    assert "No qualifying external analyst or market-research report is supplied in this Twin." in html
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
    assert "evidenced or hypothesised by function" not in panel
    assert "associated investment level is not established" in panel


def test_financial_report_semantics_are_canonical_and_cannot_silently_empty(monkeypatch, tmp_path):
    package, _summary, twin = _runtime(monkeypatch, tmp_path)
    bt = next(ent for ent in twin.enterprises if ent.name == "BT Group")
    financial_refs = {"EV-BT-FY26", "EV-BT-Q1FY27", "EV-BT-AR26"}
    governed = [obj for obj in bt.records if obj.original_id in financial_refs]
    assert {obj.original_id for obj in governed} == financial_refs
    assert all(classify_evidence(obj).is_company_financial_reporting for obj in governed)
    # Semantic acceptance: an authoritative upstream classification and an
    # empty Key Reports derivative may never both pass.
    reports = key_reports_for_enterprise(bt)
    assert not (governed and reports.company_report is None)
    assert classify_evidence(reports.company_report.source).is_company_financial_reporting

    html = _dossier(bt, twin, package.import_run_id, None)
    major = html.split("<h2>Major Programmes</h2>", 1)[1].split("</section>", 1)[0]
    executive = html.split("<h3>Change &amp; investment signals</h3>", 1)[1].split("</article>", 1)[0]
    title = "Multi-year cost, simplification, AI/data and cash-generation programme."
    assert major.count(title) == 1
    assert executive.count(title) == 1
    assert executive.count("data-signal-source-id='PROG-BT-TRANSFORMATION'") == 1
    reinvention = html.split("<h2>Reinvention Timing</h2>", 1)[1].split("</section>", 1)[0]
    assert "Ai Pressure:" not in reinvention
    assert "evidenced or hypothesised by function" not in reinvention
    assert "associated investment level is not established" in reinvention
    assert "Relevant evidence exists, but these facts have not yet been established from it." in html
    for forbidden in ("ai pressure:", "evidenced or hypothesised by function",
                      "pending governance review", "awaiting governance team"):
        assert forbidden not in html.casefold()


def test_one_canonical_programme_does_not_repeat_its_statement_across_presentation_fields(monkeypatch):
    """Duplicate fields on one source concept are not separate executive signals."""
    programme = SemanticObject(
        "programme", "transformation_programme", "One governed concept.", "Example", (), "", "High",
        "candidate", "programmes.json", {}, False, original_id="PROG-ONE",
        attributes={"title": "One governed concept."},
    )
    enterprise = SemanticEnterprise("ENT-X", "x", "Example", (), (programme,))
    from cios.applications.flora.blueprint_import import executive_enterprise_intelligence as module
    from cios.applications.flora.blueprint_import.semantic_twin import SemanticTwin
    twin = SemanticTwin((programme,), (enterprise,))
    monkeypatch.setattr(module, "enterprise_associations",
                        lambda _twin, _ent, kinds: ((programme, None, None),)
                        if "transformation_programme" in kinds else ())
    result = executive_enterprise_intelligence(enterprise, twin)
    signal = next(item for item in result.signals if item.source_id == "PROG-ONE")
    assert signal.title == "One governed concept."
    assert signal.explanation == ""


def test_classification_is_identity_agnostic_and_distinct_programmes_remain_distinct():
    evidence = SemanticObject("candidate-x", "evidence", "", "Example", (), "2027-01-01", "High",
        "candidate", "evidence.json", {"row": 1}, False, original_id="UNRELATED-ID",
        attributes={"title": "Example plc annual results", "publisher": "Example plc",
                    "evidence_quality": "Primary company filing", "publication_date": "2027-01-01"})
    assert classify_evidence(evidence).is_company_financial_reporting
    assert key_reports_for_enterprise(SemanticEnterprise("ENT-X", "x", "Example", (), (evidence,))).company_report

    first = SemanticObject("one", "transformation_programme", "Same label", "Example", (), "", "", "candidate", "", {}, False, original_id="PROG-1")
    second = replace(first, record_id="two", original_id="PROG-2")
    assert first.original_id != second.original_id and first.statement == second.statement


def test_six_enterprise_rendered_semantic_regression(monkeypatch, tmp_path):
    package, summary, twin = _runtime(monkeypatch, tmp_path)
    names = {"BT Group", "CityFibre", "Openreach", "TalkTalk", "Virgin Media O2", "VodafoneThree"}
    enterprises = [ent for ent in twin.enterprises if ent.name in names]
    assert {ent.name for ent in enterprises} == names
    for ent in enterprises:
        reports = key_reports_for_enterprise(ent)
        classified = [obj for obj in ent.records if classify_evidence(obj).is_company_financial_reporting]
        assert bool(reports.company_report) == bool(classified)
        assert reports.external_report is None
        html = _dossier(ent, twin, package.import_run_id, None)
        executive = html.split("<section class='card executive-intelligence'", 1)[1].split("</section>", 1)[0]
        reinvention = html.split("<h2>Reinvention Timing</h2>", 1)[1].split("</section>", 1)[0]
        assert "Ai Pressure:" not in executive
        assert "Ai Pressure:" not in reinvention
        programme_ids = [business_object_id(obj) for obj, _, _ in enterprise_associations(
            twin, ent, {"transformation_programme"})]
        assert len(programme_ids) == len(set(programme_ids))
        for programme_id in programme_ids:
            assert html.count(f"data-business-object-id='{programme_id}'") == 1
    counts = Counter(row["candidate_object_class"] for row in summary["candidates"] if row["validation_status"] == "accepted")
    assert (counts["relationship"], counts["transformation_programme"], counts["opportunity_hypothesis"]) == (308, 13, 17)
