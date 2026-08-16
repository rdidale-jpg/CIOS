"""End-to-end acceptance for TEL-001 Enterprise factual presentation."""
from __future__ import annotations

import hashlib
import gc
from html import escape
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.canonical_factual_projection import enterprise_factual_dimensions, enterprise_factual_synthesis, factual_projection_for_enterprise
from cios.applications.flora.blueprint_import.executive_workspace import _dossier, executive_workspace_page
from cios.applications.flora.blueprint_import.presentation_contract import human_import_state
from cios.applications.flora.blueprint_import.runtime_proof import proof_html
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, enterprise_associations, resolve_relationships
from cios.applications.flora.blueprint_import.semantic_twin import SemanticEnterprise, SemanticObject


PACKAGE = Path("docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip")
SHA256 = "bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07"


def _controlled_enterprise(attributes, evidence=("EV-CONTROL",)):
    obj = SemanticObject("candidate-1", "enterprise_twin", "", "Control", evidence, "current", "Medium", "candidate", "control.json", "$.enterprise", False, original_id="ENT-CONTROL", attributes=attributes)
    return SemanticEnterprise("ENT-CONTROL", "control", "Control", (), (obj,))


def test_synthesis_refuses_insufficient_evidence_and_preserves_contradictions():
    insufficient = enterprise_factual_synthesis(_controlled_enterprise({"description": "Control is an enterprise."}, ()))
    assert insufficient.status == "INSUFFICIENT EVIDENCE" and insufficient.statement == ""
    contradictory = enterprise_factual_synthesis(_controlled_enterprise({
        "description": "Control is an enterprise.",
        "operating_model": "Business Model: supplied factual model",
        "contradictions": ["CR-CONTROL"],
        "contradiction_dimensions": {"profile": ["CR-CONTROL"]},
    }))
    assert contradictory.status == "SUPPORTED"
    assert contradictory.contradiction_refs == ("CR-CONTROL",)
    assert contradictory.blocking_contradiction_refs == ("CR-CONTROL",)
    assert contradictory.input_dimensions == ("operating-model",)
    assert "CR-CONTROL" not in contradictory.statement


def test_truthful_absence_and_unrelated_unknown_do_not_invent_or_block():
    absent = enterprise_factual_synthesis(_controlled_enterprise({}))
    assert absent.status == "TRUTHFUL ABSENCE" and not absent.statement
    supported = enterprise_factual_synthesis(_controlled_enterprise({
        "operating_model": "Control operates a supplied service model",
        "unknowns": ["UN-LEADERSHIP"],
    }))
    assert supported.status == "SUPPORTED"
    assert supported.unknown_refs == ("UN-LEADERSHIP",)
    assert supported.blocking_unknown_refs == ()
    assert supported.propositions[0].evidence_refs == ("EV-CONTROL",)
    blocked = enterprise_factual_synthesis(_controlled_enterprise({
        "operating_model": "Control operating model is not established",
        "unknowns": ["UN-OPERATING-MODEL"],
        "unknown_dimensions": {"operating-model": ["UN-OPERATING-MODEL"]},
    }))
    assert blocked.status == "INSUFFICIENT EVIDENCE" and not blocked.statement
    assert blocked.blocking_unknown_refs == ("UN-OPERATING-MODEL",)


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

    rendered_statements = {}
    association_sets = {}
    confidence_rendered = False
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
        canonical = factual_projection_for_enterprise(enterprise)
        assert synthesis.status == "SUPPORTED"
        assert synthesis.input_dimensions == ("profile", "operating-model", "strategy")
        assert len(synthesis.input_fact_ids) == 3 and synthesis.evidence_refs
        assert synthesis.assessment_required is False
        assert synthesis.unknown_refs == dimensions["profile"].unknown_refs
        assert synthesis.contradiction_refs == dimensions["profile"].contradiction_refs
        assert canonical.enterprise_synthesis == synthesis
        assert identity.attributes.get("organisation_description") in (None, "")

        html = _dossier(enterprise, twin, package.import_run_id, None)
        rendered_statements[enterprise.name] = synthesis.statement
        assert escape(synthesis.statement) in html
        assert "Organisation description not supplied" not in html
        assert "Human import state:</strong> Candidate — awaiting human import decision" in html
        assert "assessment not yet performed" not in html.casefold()
        confidence_rendered = confidence_rendered or "Confidence:</strong> Supplied" in html
        assert "{'" not in html and "\": {" not in html
        assert (identity.governance, identity.sufficiency) == before
        association_sets[enterprise.name] = (
            tuple(sorted(o.original_id for o, _, _ in enterprise_associations(twin, enterprise, {"transformation_programme"}))),
            tuple(sorted(o.original_id for o, _, _ in enterprise_associations(twin, enterprise, {"opportunity_hypothesis"}))),
        )

        del html
        gc.collect()

    # Actual cross-surface routes use the same contract and diagnostics vocabulary.
    diagnostics, diagnostic_status = executive_workspace_page(package.import_run_id, {}, view="explore")
    assert diagnostic_status == 200
    assert "ENTERPRISE FACTUAL PRESENTATION RECONCILIATION" in diagnostics
    assert "ENTERPRISE FACTUAL SYNTHESIS TRACE" in diagnostics
    assert all(label in diagnostics for label in (
        "Source profile", "Qualifying factual inputs", "Qualification result",
        "Executive consumption", "Rendered", "SUPPORTED",
    ))
    assert "EXPECTED ABSENCE" in diagnostics and "UNSUPPORTED" in diagnostics
    assert "Present but incomplete" not in diagnostics

    # The first historical divergence was in this reconciliation consumer: it
    # treated explicit-profile absence as final absence.  Every governed
    # synthesis now agrees with the dossier while preserving that explicit
    # source/candidate distinction.
    for enterprise in twin.enterprises:
        start = diagnostics.index(f"<tr><td>{escape(enterprise.name)}</td><td>Organisation / Enterprise Profile</td>")
        row = diagnostics[start:diagnostics.index("</tr>", start)]
        assert "<td>Absent</td><td>Absent</td><td>Present</td><td>Present</td><td>Present</td>" in row
        assert "<td>PASS</td><td>None</td>" in row
        assert rendered_statements[enterprise.name] == enterprise_factual_synthesis(enterprise).statement

    assert len(association_sets) == 6
    assert sum(len(programmes) for programmes, _ in association_sets.values()) > 0
    assert sum(len(opportunities) for _, opportunities in association_sets.values()) > 0
    resolved = resolve_relationships(twin)
    for enterprise in twin.enterprises:
        subject = (enterprise.relationship_subject_identity or enterprise.identity_key).casefold()
        expected_programmes = tuple(sorted({row.target_id for row in resolved
            if row.resolved and row.relationship_type == "Enterprise owns Programme"
            and row.source_id.casefold() == subject}))
        expected_opportunities = tuple(sorted({row.source_id for row in resolved
            if row.resolved and row.relationship_type == "Opportunity targets Enterprise"
            and row.target_id.casefold() == subject}))
        assert association_sets[enterprise.name] == (expected_programmes, expected_opportunities)

    for obsolete in (
        "assessment not yet performed", "pending governance review",
        "awaiting governance review", "governance review pending",
    ):
        assert obsolete not in diagnostics.casefold()
    assert confidence_rendered
    assert "Candidate — awaiting human import decision" in diagnostics
    assert human_import_state(None, False) == "Candidate — awaiting human import decision"

    assert ("Expected change</th><td><code>Imported-Twin Evidence Path Reconciliation &amp; "
            "Functional Acceptance Truth</code>" in proof_html())
    assert "Functional acceptance</th><td><code>PASS</code>" in proof_html()
