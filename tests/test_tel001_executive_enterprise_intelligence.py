"""Acceptance for the read-only Executive Enterprise Intelligence derivative."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.executive_enterprise_intelligence import (
    executive_enterprise_intelligence, executive_intelligence_quality)
from cios.applications.flora.blueprint_import.executive_workspace import _dossier, _semantic_candidates
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, business_object_id, enterprise_associations, resolve_relationships


FIXTURE = Path("docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip")
ENTERPRISES = {"BT Group", "CityFibre", "Openreach", "TalkTalk", "Virgin Media O2", "VodafoneThree"}


def test_executive_intelligence_is_governed_rendered_derivative(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    package = BlueprintPackageRegistry().receive(FIXTURE.read_bytes(), FIXTURE.name, "executive-auditor")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "executive-auditor")
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    accepted = _semantic_candidates(package, summary["candidates"])
    twin = assemble_semantic_twin(accepted)
    counts = Counter(row["candidate_object_class"] for row in summary["candidates"] if row["validation_status"] == "accepted")
    assert counts["relationship"] == 308
    assert counts["transformation_programme"] == 13
    assert counts["opportunity_hypothesis"] == 17
    assert {enterprise.name for enterprise in twin.enterprises} == ENTERPRISES

    before = tuple((item.record_id, item.governance, dict(item.attributes)) for item in twin.objects)
    for enterprise in twin.enterprises:
        result = executive_enterprise_intelligence(enterprise, twin)
        canonical_opportunities = tuple(row[0] for row in enterprise_associations(twin, enterprise, {"opportunity_hypothesis"}))
        assert result.situation and result.source_fact_ids and result.evidence_refs
        assert tuple(card.source for card in result.opportunities) == canonical_opportunities[:3]
        assert result.unknown_refs
        assert "does not by itself establish an active procurement" in result.commercial_significance
        assert all(signal.source_id and signal.evidence_refs for signal in result.signals)
        assert len(result.signals) <= 5
        assert len(result.opportunities) <= 3
        assert len(result.watchpoints) <= 3
        assert all(watch.source_id and not watch.title.startswith(("UN-", "CR-")) for watch in result.watchpoints)

        html = _dossier(enterprise, twin, package.import_run_id, None)
        assert html.index("Human import state:</strong> Candidate — awaiting human import decision") < html.index("Executive Intelligence") < html.index("Organisation Overview")
        assert all(label in html for label in ("Situation", "Commercial significance", "Change &amp; investment signals", "Commercial opportunities", "Watchpoints", "Evidence position", "Why am I seeing this?"))
        executive = html.split("<section class='card executive-intelligence'", 1)[1].split("<nav class='section-nav'", 1)[0]
        assert executive.count("class='executive-opportunity-card'") <= 3
        assert executive.count(">View opportunity</a>") == len(result.opportunities)
        for card in result.opportunities:
            assert card.name in executive and card.why_it_matters in executive
            assert card.timing in executive and card.maturity in executive
            assert card.source.record_id not in card.name
        default_panel = executive.split("<details class='executive-explain'", 1)[0]
        prohibited = ("{'", '"opportunity_id"', "affected_business_unit", "customer_consequence",
                      "customer_problem", "financial_consequence", "operational_consequence",
                      "regulatory_consequence", "strategic_consequence", "why_problem_exists")
        assert not any(token in default_panel for token in prohibited)
        assert "Source factual dimensions:" in executive and "Evidence references:" in executive
        assert "Existing evidence shows change or pressure across" not in executive
        assert "does not by itself establish an active procurement" in executive
        assert "Domain:</strong> Not established" in html
        assert "Enterprise Economics</h2><p><strong>Architectural intent — not implemented." in html
        assert "Leadership / Governance</h2><p><strong>Architectural intent — not implemented." in html

    assert before == tuple((item.record_id, item.governance, dict(item.attributes)) for item in twin.objects)
    assert len(resolve_relationships(twin)) == 308


def test_six_enterprise_executive_quality_and_raw_label_contract(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    package = BlueprintPackageRegistry().receive(FIXTURE.read_bytes(), FIXTURE.name, "quality-auditor")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "quality-auditor")
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    twin = assemble_semantic_twin(_semantic_candidates(package, summary["candidates"]))
    panels = {}
    for enterprise in (item for item in twin.enterprises if item.name in ENTERPRISES):
        html = _dossier(enterprise, twin, package.import_run_id, None)
        normal = html.split("<h2>Advanced Inspection</h2>", 1)[0]
        assert "Ai:" not in normal and "AI:" not in normal
        assert "Oss Bss:" not in normal
        assert "Business transformation</strong>" not in normal
        assert "Technology modernisation</strong>" not in normal
        assert "Unknown" in normal
        panels[enterprise.name] = html.split("<section class='card executive-intelligence'", 1)[1].split("</section>", 1)[0]
        quality = executive_intelligence_quality(enterprise, twin)
        assert quality.unknown_integrity == "PASS"
        assert quality.contradiction_integrity == "PASS"
        assert quality.overall == "PASS"
    assert len(set(panels.values())) == 6
