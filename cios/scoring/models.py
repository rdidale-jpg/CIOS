"""Scoring foundation models for the CIOS SDK.

Sprint 5 establishes thin, serializable Pydantic models for CIOS scoring
objects. These models define score values, components, bands, model metadata,
scoring results, and a Transformation Pressure score bundle only. They do not
implement a decision engine, agents, memory, UI, persistence, or application
logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from cios.core.identifiers import generate_identifier
from cios.core.models import CIOSBaseModel
from cios.core.validation import require_non_empty, utc_now
from cios.reasoning.models import ReasoningTrace


class Score(CIOSBaseModel):
    """Normalized score value with optional evidence and rationale."""

    id: str = Field(default_factory=lambda: generate_identifier("score"))
    name: str = Field(..., description="Human-readable score name.")
    value: float = Field(..., ge=0, le=100, description="Normalized score value from 0 to 100.")
    rationale: str | None = Field(default=None, description="Optional explanation for the score value.")
    evidence_ids: list[str] = Field(default_factory=list, description="Evidence identifiers supporting the score.")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")

    @field_validator("rationale")
    @classmethod
    def _validate_rationale(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "rationale")

    @field_validator("evidence_ids")
    @classmethod
    def _validate_evidence_ids(cls, value: list[str]) -> list[str]:
        return [require_non_empty(evidence_id, "evidence_id") for evidence_id in value]


class ScoreComponent(CIOSBaseModel):
    """Weighted component that contributes to a scoring result."""

    id: str = Field(default_factory=lambda: generate_identifier("score_component"))
    name: str = Field(..., description="Component name.")
    score: Score = Field(..., description="Score assigned to this component.")
    weight: float = Field(default=1.0, ge=0, description="Non-negative component weight.")
    rationale: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")

    @field_validator("rationale")
    @classmethod
    def _validate_rationale(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "rationale")


class ScoreBand(CIOSBaseModel):
    """Named inclusive score range used to interpret normalized scores."""

    id: str = Field(default_factory=lambda: generate_identifier("score_band"))
    name: str = Field(..., description="Band label.")
    minimum: float = Field(..., ge=0, le=100, description="Inclusive lower bound.")
    maximum: float = Field(..., ge=0, le=100, description="Inclusive upper bound.")
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")

    @model_validator(mode="after")
    def _validate_range(self) -> "ScoreBand":
        if self.minimum > self.maximum:
            raise ValueError("minimum must be less than or equal to maximum")
        return self


class ScoringModel(CIOSBaseModel):
    """Metadata describing a scoring model and its interpretation bands."""

    id: str = Field(default_factory=lambda: generate_identifier("scoring_model"))
    name: str = Field(..., description="Scoring model name.")
    version: str = Field(default="0.1.0", description="Scoring model version.")
    description: str | None = None
    bands: list[ScoreBand] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name", "version")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class ScoringResult(CIOSBaseModel):
    """Serializable output bundle for a scoring assessment."""

    id: str = Field(default_factory=lambda: generate_identifier("scoring_result"))
    scoring_model: ScoringModel = Field(..., description="Model used to produce the result.")
    overall_score: Score = Field(..., description="Overall normalized score.")
    components: list[ScoreComponent] = Field(default_factory=list)
    band: ScoreBand | None = Field(default=None, description="Band matching the overall score, if assigned.")
    reasoning_trace: ReasoningTrace | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class TransformationPressureScore(CIOSBaseModel):
    """Foundation bundle for Transformation Pressure scoring outputs."""

    id: str = Field(default_factory=lambda: generate_identifier("transformation_pressure_score"))
    result: ScoringResult = Field(..., description="Scoring result for transformation pressure.")
    urgency_score: Score | None = Field(default=None)
    strategic_importance_score: Score | None = Field(default=None)
    change_pressure_score: Score | None = Field(default=None)
    capability_gap_score: Score | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
