"""Semantic acceptance tests for ADR-026 Material Pressure qualification."""
import pytest
from cios.applications.flora.blueprint_import.material_pressure import (
    MaterialPressureQualification, PressureCandidate, qualify_candidates,
)


def candidate(**changes):
    values = dict(canonical_input_id="OBS-1", canonical_input_type="observation",
                  enterprise_id="ENT-1", condition="A binding condition acts on operations",
                  affected_domain="operational", consequence="Delivery capacity is constrained",
                  consequence_domain="operational", evidence_refs=("EV-1",),
                  unknown_refs=("UN-SEVERITY",), time_context="2026-Q4")
    values.update(changes)
    return PressureCandidate(**values)


@pytest.fixture(autouse=True)
def governed_inputs(tmp_path,monkeypatch):
    """Positive gates need actual owned inputs, not previously trusted ID strings."""
    from cios.applications.flora.memory.models import Observation
    from cios.applications.flora.memory.repository import ObservationRepository,EvidenceRepository,ContradictionRepository
    from cios.applications.flora.blueprint_import.promotion import CanonicalJsonlRepository
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    data=dict(condition='A binding condition acts on operations',condition_concept='delivery-capacity-constraint',
        affected_domain='operational',scope='delivery operations',time_context='2026-Q4',
        condition_basis='A binding condition acts on operations.',mechanism='The condition constrains delivery.',
        consequence='Delivery capacity is constrained',consequence_domain='operational',
        materiality_rationale='The constraint limits service delivery.',identity_rationale='The condition constrains delivery.')
    summary='A binding condition acts on operations. The condition constrains delivery. Delivery capacity is constrained. The constraint limits service delivery.'
    for i in (1,2):
        EvidenceRepository().save(dict(evidence_id=f'EV-{i}',enterprise_id='ent-1',summary=summary,confidence=80))
        ObservationRepository().save(Observation('ent-1','fact',f'The binding delivery condition is recorded in position {i}.',
            '2026-11-01','2026-11-02','events.delivery',80,(f'EV-{i}',),observation_id=f'OBS-{i}',human_provenance={'material_pressure':data}))
    CanonicalJsonlRepository('unknown').save(dict(canonical_id='UN-SEVERITY',enterprise_id='ent-1',affected_field='severity'))
    ContradictionRepository().save(dict(contradiction_id='CR-SEVERITY',enterprise_id='ent-1',affected_field='severity',status='open',counter_evidence_ids=['EV-2']))


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
    assert result.discovery_state == "NO_ELIGIBLE_INPUT"
    assert result.qualified == result.rejected == result.unresolved == ()


def test_candidate_discovery_states_distinguish_false_empty_and_failure():
    rejected = qualify_candidates((candidate(materiality_established=False),))
    assert rejected.discovery_state == "ASSESSED_NONE_QUALIFIED"
    assert rejected.eligible_input_count == rejected.candidates_assessed == 1
    assert qualify_candidates((candidate(),)).discovery_state == "ASSESSED_WITH_RESULTS"
    failed = MaterialPressureQualification((), pipeline_error="discovery unavailable")
    assert failed.discovery_state == "PIPELINE_FAILURE"
    assert failed.projection_state == "FAILURE"
