"""Semantic acceptance tests for ADR-026 Material Pressure qualification."""
from cios.applications.flora.blueprint_import.material_pressure import (
    PressureCandidate, qualify_candidates,
)


def candidate(**changes):
    values = dict(canonical_input_id="OBS-1", canonical_input_type="observation",
                  enterprise_id="ENT-1", condition="A binding condition acts on operations",
                  affected_domain="operational", consequence="Delivery capacity is constrained",
                  consequence_domain="operational", evidence_refs=("EV-1",),
                  unknown_refs=("UN-SEVERITY",))
    values.update(changes)
    return PressureCandidate(**values)


def test_all_six_mandatory_gates_are_required_and_rejections_are_explainable():
    failures = (
        ({"canonical_input_type": "renderer_text"}, "ineligible input"),
        ({"applicable": False}, "wrong Enterprise"),
        ({"pressure_semantics": False}, "insufficient Pressure semantics"),
        ({"materiality_established": False}, "materiality not established"),
        ({"consequence_established": False}, "Enterprise consequence not established"),
        ({"lineage_established": False}, "insufficient lineage"),
    )
    for change, reason in failures:
        assessment = qualify_candidates((candidate(**change),)).assessments[0]
        assert assessment.qualification == "REJECTED" and assessment.reason == reason


def test_keyword_generic_metric_programme_opportunity_and_procurement_inputs_do_not_qualify():
    for source_type in ("keyword", "generic_assumption", "financial_metric", "programme", "opportunity", "procurement"):
        result = qualify_candidates((candidate(canonical_input_type=source_type),))
        assert not result.qualified and result.rejected[0].reason == "ineligible input"


def test_identity_singularity_is_semantic_and_duplicate_evidence_does_not_create_pressure():
    first = candidate(evidence_refs=("EV-1",))
    duplicate = candidate(canonical_input_id="OBS-2", evidence_refs=("EV-2",))
    result = qualify_candidates((first, duplicate))
    assert len(result.qualified) == 1
    assert result.rejected[0].reason == "duplicate/same Pressure"


def test_non_core_unknown_and_contradiction_are_preserved_but_core_conflict_is_unresolved():
    supported = qualify_candidates((candidate(contradiction_refs=("CR-SEVERITY",)),)).qualified[0]
    assert supported.candidate.unknown_refs == ("UN-SEVERITY",)
    assert supported.candidate.contradiction_refs == ("CR-SEVERITY",)
    core = qualify_candidates((candidate(core_contradiction=True),))
    assert not core.qualified and core.unresolved[0].reason == "core contradiction"


def test_true_empty_state_and_no_domain_object_creation():
    result = qualify_candidates(())
    assert result.projection_state == "EMPTY"
    assert result.qualified == result.rejected == result.unresolved == ()
