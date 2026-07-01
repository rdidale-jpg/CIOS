from cios.applications.flora.observatory.engine import build_observatory
from cios.applications.flora.observatory.models import HypothesisStatus


def test_observatory_builds_three_board_usable_cases() -> None:
    obs = build_observatory()
    assert obs.critique_path.endswith("Enterprise_Transformation_Observatory_Architectural_Critique.md")
    assert len(obs.organisations) == 3
    assert all(org.case_for_change.why_act for org in obs.organisations)
    assert all(org.case_for_change.supporting_evidence_ids for org in obs.organisations)
    assert all(org.case_for_change.conversation_level in {"Operational", "Business", "Executive", "Board"} for org in obs.organisations)


def test_genome_dimensions_are_explainable_not_hidden_scores() -> None:
    obs = build_observatory()
    dimension_names = {dimension.name for org in obs.organisations for dimension in org.genome}
    assert "Transformation Inevitability Index (TII)" in dimension_names
    for org in obs.organisations:
        for dimension in org.genome:
            assert dimension.reasoning
            assert dimension.unknowns
            assert dimension.evidence_quality
            assert isinstance(dimension.confidence, int)


def test_research_notebook_retains_hypothesis_status_and_evidence() -> None:
    obs = build_observatory()
    assert {h.status for h in obs.hypotheses} >= {HypothesisStatus.STRENGTHENING, HypothesisStatus.NEEDS_MORE_EVIDENCE}
    assert all(h.supporting_evidence_ids for h in obs.hypotheses)
    assert all(h.commercial_implications for h in obs.hypotheses)


def test_knowledge_graph_edges_separate_observed_and_inferred_relationships() -> None:
    obs = build_observatory()
    assert any(not edge.inferred for edge in obs.graph_edges)
    assert any(edge.inferred for edge in obs.graph_edges)
    assert all(edge.evidence_ids for edge in obs.graph_edges)
