"""End-to-end acceptance for TEL-001 Enterprise factual presentation."""
from __future__ import annotations

import hashlib
import gc
from html import escape
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.canonical_factual_projection import enterprise_factual_dimensions, enterprise_factual_synthesis
from cios.applications.flora.blueprint_import.executive_workspace import _dossier, executive_workspace_page
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin
from cios.applications.flora.blueprint_import.semantic_twin import SemanticEnterprise, SemanticObject


PACKAGE = Path("docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip")
SHA256 = "bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07"


def _controlled_enterprise(attributes):
    obj = SemanticObject("candidate-1", "enterprise_twin", "", "Control", ("EV-CONTROL",), "current", "Medium", "candidate", "control.json", "$.enterprise", False, original_id="ENT-CONTROL", attributes=attributes)
    return SemanticEnterprise("ENT-CONTROL", "control", "Control", (), (obj,))


def test_synthesis_refuses_insufficient_evidence_and_preserves_contradictions():
    insufficient = enterprise_factual_synthesis(_controlled_enterprise({"description": "Control is an enterprise."}))
    assert insufficient.status == "INSUFFICIENT EVIDENCE" and insufficient.statement == ""
    contradictory = enterprise_factual_synthesis(_controlled_enterprise({
        "description": "Control is an enterprise.",
        "operating_model": "Business Model: supplied factual model",
        "contradictions": ["CR-CONTROL"],
    }))
    assert contradictory.status == "GENERATED"
    assert contradictory.contradiction_refs == ("CR-CONTROL",)
    assert "CR-CONTROL" not in contradictory.statement


def test_tel001_facts_survive_without_assessment_and_render_on_actual_routes(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    package = BlueprintPackageRegistry().receive(PACKAGE.read_bytes(), PACKAGE.name, "factual-auditor")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "factual-auditor")
    candidates = BlueprintPackageValidator().staging_summary(package.import_run_id)["candidates"]
    twin = assemble_semantic_twin([c for c in candidates if c["validation_status"] == "accepted"])

    assert hashlib.sha256(PACKAGE.read_bytes()).hexdigest() == SHA256
    assert sum(c["candidate_object_class"] == "relationship" and c["validation_status"] == "accepted" for c in candidates) == 308
    assert sum(c["candidate_object_class"] == "transformation_programme" and c["validation_status"] == "accepted" for c in candidates) == 13
    assert sum(c["candidate_object_class"] == "opportunity_hypothesis" and c["validation_status"] == "accepted" for c in candidates) == 17

    for enterprise in twin.enterprises:
        dimensions = {d.key: d for d in enterprise_factual_dimensions(enterprise)}
        assert dimensions["profile"].present
        assert dimensions["operating-model"].present
        assert dimensions["financial"].present
        assert dimensions["industry"].status == "EXPECTED ABSENCE"
        assert dimensions["economics"].status == "UNSUPPORTED"
        identity = next(o for o in enterprise.records if o.kind == "enterprise_twin")
        before = (identity.governance, identity.sufficiency)
        synthesis = enterprise_factual_synthesis(enterprise)
        assert synthesis.status == "GENERATED"
        assert synthesis.input_dimensions == ("profile", "operating-model", "strategy")
        assert len(synthesis.input_fact_ids) == 3 and synthesis.evidence_refs
        assert synthesis.assessment_required is False
        assert synthesis.unknown_refs == dimensions["profile"].unknown_refs
        assert synthesis.contradiction_refs == dimensions["profile"].contradiction_refs

        html = _dossier(enterprise, twin, package.import_run_id, None)
        assert escape(dimensions["profile"].values[0]) in html
        assert "Assessment status:</strong> Assessment not yet performed" in html
        assert "{'" not in html and "\": {" not in html
        assert (identity.governance, identity.sufficiency) == before
        del html
        gc.collect()

    # Actual cross-surface routes use the same contract and diagnostics vocabulary.
    diagnostics, _ = executive_workspace_page(package.import_run_id, {}, view="explore")
    assert "ENTERPRISE FACTUAL PRESENTATION RECONCILIATION" in diagnostics
    assert "ENTERPRISE FACTUAL SYNTHESIS TRACE" in diagnostics
    assert "EXPECTED ABSENCE" in diagnostics and "UNSUPPORTED" in diagnostics
    assert "Present but incomplete" not in diagnostics
