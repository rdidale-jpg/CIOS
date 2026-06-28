"""Tests for CIOS Sprint 4 reasoning foundation models."""

from __future__ import annotations

import importlib
from pathlib import Path

from cios.core import Evidence, Observation, Recommendation
from cios.reasoning import (
    Explanation,
    Hypothesis,
    Inference,
    ReasoningResult,
    ReasoningStep,
    ReasoningTrace,
    Signal,
)


def test_reasoning_steps_can_be_created() -> None:
    """Reasoning steps capture ordered explainable reasoning activity."""

    step = ReasoningStep(
        sequence=1,
        description="Assess whether the customer has transformation pressure.",
        input_ids=["observation_123"],
        output_ids=["hypothesis_123"],
    )

    assert step.sequence == 1
    assert step.description == "Assess whether the customer has transformation pressure."
    assert step.input_ids == ["observation_123"]
    assert step.output_ids == ["hypothesis_123"]


def test_hypotheses_can_reference_evidence_identifiers() -> None:
    """Hypotheses retain evidence identifiers without importing graph models."""

    evidence = Evidence(title="Strategy update", source="crm-note")
    hypothesis = Hypothesis(
        statement="Customer urgency is increasing.", evidence_ids=[evidence.id], confidence="high"
    )

    assert hypothesis.evidence_ids == [evidence.id]
    assert hypothesis.confidence == "high"


def test_reasoning_traces_serialize_correctly() -> None:
    """Reasoning traces serialize nested steps to dictionaries."""

    step = ReasoningStep(sequence=1, description="Identify a signal.", output_ids=["signal_123"])
    trace = ReasoningTrace(
        name="Opportunity reasoning trace",
        description="Trace for a commercial assessment.",
        steps=[step],
        hypothesis_ids=["hypothesis_123"],
        inference_ids=["inference_123"],
        explanation_ids=["explanation_123"],
        metadata={"sprint": 4},
    )

    serialized = trace.model_dump(mode="json")

    assert serialized["name"] == "Opportunity reasoning trace"
    assert serialized["steps"][0]["sequence"] == 1
    assert serialized["steps"][0]["output_ids"] == ["signal_123"]
    assert serialized["hypothesis_ids"] == ["hypothesis_123"]
    assert serialized["metadata"] == {"sprint": 4}


def test_explanations_can_reference_observations_and_recommendations() -> None:
    """Explanations link to observation and recommendation identifiers."""

    observation = Observation(statement="The customer has accelerated the procurement timetable.")
    recommendation = Recommendation(title="Engage early", rationale="Time pressure is increasing.")
    explanation = Explanation(
        summary="The recommendation is based on observed urgency.",
        observation_ids=[observation.id],
        recommendation_ids=[recommendation.id],
    )

    assert explanation.observation_ids == [observation.id]
    assert explanation.recommendation_ids == [recommendation.id]


def test_reasoning_result_can_bundle_foundation_objects() -> None:
    """Reasoning results bundle traces and reasoning objects without executing decisions."""

    signal = Signal(name="Urgency", source_ids=["observation_123"], strength="high")
    hypothesis = Hypothesis(statement="The buyer is under time pressure.")
    inference = Inference(
        statement="Early engagement is commercially important.", premise_ids=[signal.id, hypothesis.id]
    )
    explanation = Explanation(summary="Urgency signal supports early engagement.", inference_ids=[inference.id])
    trace = ReasoningTrace(name="Trace", steps=[ReasoningStep(sequence=1, description="Review urgency signal.")])

    result = ReasoningResult(
        summary="Prioritise early customer engagement.",
        trace=trace,
        hypotheses=[hypothesis],
        signals=[signal],
        inferences=[inference],
        explanations=[explanation],
    )

    serialized = result.model_dump(mode="json")

    assert serialized["trace"]["name"] == "Trace"
    assert serialized["signals"][0]["strength"] == "high"
    assert serialized["inferences"][0]["premise_ids"] == [signal.id, hypothesis.id]


def test_no_circular_imports_exist_for_reasoning() -> None:
    """Reasoning imports independently and does not require ontology or graph imports."""

    core_models = importlib.import_module("cios.core.models")
    reasoning_models = importlib.import_module("cios.reasoning.models")

    assert core_models.Evidence(title="Core evidence", source="note")
    assert reasoning_models.ReasoningStep(sequence=1, description="Reason over core evidence.")

    reasoning_source = Path("cios/reasoning/models.py").read_text()

    assert "from cios.graph" not in reasoning_source
    assert "from cios.ontology" not in reasoning_source
