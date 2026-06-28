"""Tests for CIOS Sprint 6 decision engine foundation models."""

from __future__ import annotations

import importlib
from pathlib import Path

from cios.core import Evidence, Observation, Recommendation
from cios.decision_engine import (
    DecisionAssessment,
    DecisionCriteria,
    DecisionInput,
    DecisionOption,
    DecisionOutput,
    DecisionRationale,
)
from cios.graph import GraphNode, KnowledgeGraphRecord
from cios.reasoning import ReasoningResult, ReasoningStep, ReasoningTrace
from cios.scoring import Score, ScoringModel, ScoringResult


def _sample_scoring_result() -> ScoringResult:
    return ScoringResult(
        scoring_model=ScoringModel(name="Decision readiness"),
        overall_score=Score(name="Readiness", value=74),
    )


def test_decision_inputs_reference_graph_reasoning_and_scoring_records() -> None:
    """Decision inputs retain references to graph, reasoning, and scoring outputs."""

    node = GraphNode(wrapped_id="opp-001", wrapped_type="Opportunity", source_package="core")
    graph_record = KnowledgeGraphRecord(name="Opportunity graph", nodes=[node])
    trace = ReasoningTrace(name="Qualification trace", steps=[ReasoningStep(sequence=1, description="Review evidence")])
    result = ReasoningResult(summary="Opportunity has strong executive sponsorship.", trace=trace)
    scoring_result = _sample_scoring_result()
    evidence = Evidence(title="Customer note", source="discovery-call")
    observation = Observation(statement="Executive sponsor is active.", evidence_ids=[evidence.id])

    decision_input = DecisionInput(
        name="Bid/no-bid input",
        question="Should we pursue the opportunity?",
        graph_records=[graph_record],
        reasoning_traces=[trace],
        reasoning_results=[result],
        scoring_results=[scoring_result],
        evidence=[evidence],
        observations=[observation],
    )

    assert decision_input.graph_records[0].nodes[0].wrapped_id == "opp-001"
    assert decision_input.reasoning_traces[0].steps[0].sequence == 1
    assert decision_input.reasoning_results[0].summary.startswith("Opportunity")
    assert decision_input.scoring_results[0].overall_score.value == 74
    assert decision_input.evidence[0].id == evidence.id
    assert decision_input.observations[0].evidence_ids == [evidence.id]


def test_decision_options_and_criteria_can_be_created() -> None:
    """Decision options and criteria are thin serializable records."""

    option = DecisionOption(
        title="Pursue opportunity",
        description="Invest capture resources in the opportunity.",
        actions=["Schedule executive alignment session"],
        evidence_ids=["evidence-001"],
    )
    criteria = DecisionCriteria(name="Strategic fit", description="Alignment to target markets", weight=0.6)

    assert option.title == "Pursue opportunity"
    assert option.actions == ["Schedule executive alignment session"]
    assert criteria.name == "Strategic fit"
    assert criteria.weight == 0.6


def test_decision_outputs_serialize_correctly() -> None:
    """Decision outputs serialize nested options, criteria, assessments, and rationales."""

    option = DecisionOption(title="Pursue")
    criteria = DecisionCriteria(name="Win probability")
    score = Score(name="Win probability", value=68)
    assessment = DecisionAssessment(option_id=option.id, criteria_scores={criteria.id: score}, overall_score=score)
    rationale = DecisionRationale(summary="Evidence and scoring support a qualified pursuit.", score_ids=[score.id])
    recommendation = Recommendation(title="Proceed", rationale="Strong fit and acceptable risk.")
    output = DecisionOutput(
        title="Bid decision",
        selected_option_id=option.id,
        options=[option],
        criteria=[criteria],
        assessments=[assessment],
        rationales=[rationale],
        recommendations=[recommendation],
        outcome="selected",
    )

    serialized = output.model_dump(mode="json")

    assert serialized["title"] == "Bid decision"
    assert serialized["status"] == "draft"
    assert serialized["selected_option_id"] == option.id
    assert serialized["options"][0]["title"] == "Pursue"
    assert serialized["criteria"][0]["name"] == "Win probability"
    assert serialized["assessments"][0]["criteria_scores"][criteria.id]["value"] == 68
    assert serialized["rationales"][0]["score_ids"] == [score.id]
    assert serialized["recommendations"][0]["title"] == "Proceed"


def test_rationales_reference_evidence_reasoning_and_scores() -> None:
    """Decision rationales hold traceability links across evidence, reasoning, and scores."""

    scoring_result = _sample_scoring_result()
    rationale = DecisionRationale(
        summary="Proceed because evidence, reasoning, and scores align.",
        evidence_ids=["evidence-001"],
        reasoning_trace_ids=["trace-001"],
        reasoning_result_ids=["result-001"],
        score_ids=[scoring_result.overall_score.id],
        scoring_result_ids=[scoring_result.id],
        confidence="high",
    )

    assert rationale.evidence_ids == ["evidence-001"]
    assert rationale.reasoning_trace_ids == ["trace-001"]
    assert rationale.reasoning_result_ids == ["result-001"]
    assert rationale.score_ids == [scoring_result.overall_score.id]
    assert rationale.scoring_result_ids == [scoring_result.id]
    assert rationale.confidence == "high"


def test_no_circular_imports_exist_for_decision_engine() -> None:
    """Decision engine imports independently and only references allowed CIOS layers."""

    core_models = importlib.import_module("cios.core.models")
    graph_models = importlib.import_module("cios.graph.models")
    reasoning_models = importlib.import_module("cios.reasoning.models")
    scoring_models = importlib.import_module("cios.scoring.models")
    decision_models = importlib.import_module("cios.decision_engine.models")

    assert core_models.Evidence(title="Core evidence", source="note")
    assert graph_models.KnowledgeGraphRecord(name="Graph")
    assert reasoning_models.ReasoningTrace(name="Trace")
    assert scoring_models.Score(name="Score", value=50)
    assert decision_models.DecisionOption(title="Option")

    decision_source = Path("cios/decision_engine/models.py").read_text()
    decision_init_source = Path("cios/decision_engine/__init__.py").read_text()

    for source in (decision_source, decision_init_source):
        assert "from cios.agents" not in source
        assert "from cios.memory" not in source
        assert "from cios.applications" not in source
        assert "from cios.ontology" not in source
