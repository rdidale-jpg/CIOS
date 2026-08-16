"""Acceptance for the read-only Executive Enterprise Intelligence derivative."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.executive_enterprise_intelligence import executive_enterprise_intelligence
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
        assert result.opportunities == canonical_opportunities
        assert result.unknown_refs
        assert "does not by itself establish an active procurement" in result.commercial_significance
        assert all(signal.source_id and signal.evidence_refs for signal in result.signals)
        assert result.watchpoints and all(watch.source_id for watch in result.watchpoints)

        html = _dossier(enterprise, twin, package.import_run_id, None)
        assert html.index("Human import state:</strong> Candidate — awaiting human import decision") < html.index("Executive Intelligence") < html.index("Organisation Overview")
        assert all(label in html for label in ("Situation", "Commercial significance", "Change &amp; investment signals", "Commercial opportunities", "Watchpoints", "Evidence position", "Why am I seeing this?"))
        assert all(f"data-business-object-id='{business_object_id(item)}'" in html for item in result.opportunities)
        assert "Domain:</strong> Not established" in html
        assert "Enterprise Economics</h2><p><strong>Architectural intent — not implemented." in html
        assert "Leadership / Governance</h2><p><strong>Architectural intent — not implemented." in html

    assert before == tuple((item.record_id, item.governance, dict(item.attributes)) for item in twin.objects)
    assert len(resolve_relationships(twin)) == 308
