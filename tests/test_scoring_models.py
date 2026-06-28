"""Tests for CIOS Sprint 5 scoring foundation models."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from pydantic import ValidationError

from cios.reasoning import ReasoningTrace
from cios.scoring import (
    Score,
    ScoreBand,
    ScoreComponent,
    ScoringModel,
    ScoringResult,
    TransformationPressureScore,
)


def test_score_components_can_be_created() -> None:
    """Score components retain their score, weight, and rationale."""

    score = Score(name="Urgency", value=82.5, rationale="Customer deadline is accelerating.")
    component = ScoreComponent(name="Urgency component", score=score, weight=0.4)

    assert component.name == "Urgency component"
    assert component.score.value == 82.5
    assert component.weight == 0.4


def test_scoring_results_serialize_correctly() -> None:
    """Scoring results serialize nested models to dictionaries."""

    band = ScoreBand(name="High", minimum=70, maximum=100)
    model = ScoringModel(name="Transformation Pressure", version="0.1.0", bands=[band])
    overall = Score(name="Overall transformation pressure", value=78)
    component = ScoreComponent(name="Urgency", score=Score(name="Urgency", value=80), weight=0.5)
    trace = ReasoningTrace(name="Scoring trace")
    result = ScoringResult(
        scoring_model=model,
        overall_score=overall,
        components=[component],
        band=band,
        reasoning_trace=trace,
        metadata={"sprint": 5},
    )

    serialized = result.model_dump(mode="json")

    assert serialized["scoring_model"]["name"] == "Transformation Pressure"
    assert serialized["overall_score"]["value"] == 78
    assert serialized["components"][0]["score"]["name"] == "Urgency"
    assert serialized["band"]["name"] == "High"
    assert serialized["reasoning_trace"]["name"] == "Scoring trace"
    assert serialized["metadata"] == {"sprint": 5}


def test_transformation_pressure_score_can_be_instantiated() -> None:
    """Transformation Pressure score bundles a scoring result and driver scores."""

    model = ScoringModel(name="Transformation Pressure")
    result = ScoringResult(scoring_model=model, overall_score=Score(name="Overall", value=65))
    transformation_pressure = TransformationPressureScore(
        result=result,
        urgency_score=Score(name="Urgency", value=70),
        strategic_importance_score=Score(name="Strategic importance", value=60),
    )

    assert transformation_pressure.result.overall_score.value == 65
    assert transformation_pressure.urgency_score is not None
    assert transformation_pressure.urgency_score.name == "Urgency"


def test_score_values_reject_invalid_ranges() -> None:
    """Scores must stay within the normalized 0-to-100 range."""

    with pytest.raises(ValidationError):
        Score(name="Too low", value=-1)

    with pytest.raises(ValidationError):
        Score(name="Too high", value=101)

    with pytest.raises(ValidationError):
        ScoreBand(name="Invalid", minimum=80, maximum=20)


def test_no_circular_imports_exist_for_scoring() -> None:
    """Scoring imports independently and only references allowed CIOS layers."""

    core_models = importlib.import_module("cios.core.models")
    reasoning_models = importlib.import_module("cios.reasoning.models")
    scoring_models = importlib.import_module("cios.scoring.models")

    assert core_models.Evidence(title="Core evidence", source="note")
    assert reasoning_models.ReasoningTrace(name="Trace")
    assert scoring_models.Score(name="Score", value=50)

    scoring_source = Path("cios/scoring/models.py").read_text()

    assert "from cios.decision_engine" not in scoring_source
    assert "from cios.agents" not in scoring_source
    assert "from cios.memory" not in scoring_source
    assert "from cios.graph" not in scoring_source
    assert "from cios.ontology" not in scoring_source
