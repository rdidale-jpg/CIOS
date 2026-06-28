"""Reasoning foundation models for the CIOS SDK.

Sprint 4 establishes Commercial Reasoning Language primitives as thin,
serializable Pydantic models. These models capture traces, steps, hypotheses,
signals, inferences, explanations, and results only. They do not implement
scoring, decision engines, graph traversal, AI agents, memory, UI, persistence,
or application logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from cios.core.identifiers import generate_identifier
from cios.core.models import CIOSBaseModel
from cios.core.types import ConfidenceLevel
from cios.core.validation import require_non_empty, utc_now


class ReasoningStep(CIOSBaseModel):
    """Single explainable step in a reasoning trace."""

    id: str = Field(default_factory=lambda: generate_identifier("reasoning_step"))
    sequence: int = Field(..., ge=1, description="One-based step order within a trace.")
    description: str = Field(..., description="Human-readable description of the reasoning step.")
    input_ids: list[str] = Field(default_factory=list, description="Identifiers consumed by this step.")
    output_ids: list[str] = Field(
        default_factory=list, description="Identifiers produced or referenced by this step."
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("description")
    @classmethod
    def _validate_description(cls, value: str) -> str:
        return require_non_empty(value, "description")

    @field_validator("input_ids", "output_ids")
    @classmethod
    def _validate_identifier_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(identifier, info.field_name) for identifier in value]


class Hypothesis(CIOSBaseModel):
    """Candidate commercial interpretation supported by evidence identifiers."""

    id: str = Field(default_factory=lambda: generate_identifier("hypothesis"))
    statement: str = Field(..., description="Hypothesis stated as a concise claim.")
    evidence_ids: list[str] = Field(
        default_factory=list, description="Evidence identifiers supporting the hypothesis."
    )
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("statement")
    @classmethod
    def _validate_statement(cls, value: str) -> str:
        return require_non_empty(value, "statement")

    @field_validator("evidence_ids")
    @classmethod
    def _validate_evidence_ids(cls, value: list[str]) -> list[str]:
        return [require_non_empty(evidence_id, "evidence_id") for evidence_id in value]


class Signal(CIOSBaseModel):
    """Reasoning-level signal observed from input, evidence, or analysis."""

    id: str = Field(default_factory=lambda: generate_identifier("signal"))
    name: str = Field(..., description="Short signal name.")
    description: str | None = Field(default=None, description="Optional signal description.")
    source_ids: list[str] = Field(default_factory=list, description="Identifiers that produced the signal.")
    strength: Literal["low", "medium", "high", "unknown"] = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")

    @field_validator("description")
    @classmethod
    def _validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "description")

    @field_validator("source_ids")
    @classmethod
    def _validate_source_ids(cls, value: list[str]) -> list[str]:
        return [require_non_empty(source_id, "source_id") for source_id in value]


class Inference(CIOSBaseModel):
    """Conclusion derived from hypotheses, signals, observations, or evidence."""

    id: str = Field(default_factory=lambda: generate_identifier("inference"))
    statement: str = Field(..., description="Inferred conclusion.")
    premise_ids: list[str] = Field(
        default_factory=list, description="Identifiers of premises used for the inference."
    )
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("statement")
    @classmethod
    def _validate_statement(cls, value: str) -> str:
        return require_non_empty(value, "statement")

    @field_validator("premise_ids")
    @classmethod
    def _validate_premise_ids(cls, value: list[str]) -> list[str]:
        return [require_non_empty(premise_id, "premise_id") for premise_id in value]


class Explanation(CIOSBaseModel):
    """Human-readable explanation with traceability to observations and recommendations."""

    id: str = Field(default_factory=lambda: generate_identifier("explanation"))
    summary: str = Field(..., description="Concise explanation summary.")
    observation_ids: list[str] = Field(
        default_factory=list, description="Observation identifiers referenced by the explanation."
    )
    recommendation_ids: list[str] = Field(
        default_factory=list, description="Recommendation identifiers referenced by the explanation."
    )
    inference_ids: list[str] = Field(
        default_factory=list, description="Inference identifiers referenced by the explanation."
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, value: str) -> str:
        return require_non_empty(value, "summary")

    @field_validator("observation_ids", "recommendation_ids", "inference_ids")
    @classmethod
    def _validate_identifier_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(identifier, info.field_name) for identifier in value]


class ReasoningTrace(CIOSBaseModel):
    """Serializable record of the reasoning path followed for an assessment."""

    id: str = Field(default_factory=lambda: generate_identifier("reasoning_trace"))
    name: str = Field(..., description="Human-readable trace name.")
    description: str | None = None
    steps: list[ReasoningStep] = Field(default_factory=list)
    hypothesis_ids: list[str] = Field(default_factory=list)
    inference_ids: list[str] = Field(default_factory=list)
    explanation_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")


class ReasoningResult(CIOSBaseModel):
    """Portable output bundle for reasoning foundation objects."""

    id: str = Field(default_factory=lambda: generate_identifier("reasoning_result"))
    summary: str = Field(..., description="Summary of the reasoning result.")
    trace: ReasoningTrace | None = None
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    signals: list[Signal] = Field(default_factory=list)
    inferences: list[Inference] = Field(default_factory=list)
    explanations: list[Explanation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, value: str) -> str:
        return require_non_empty(value, "summary")
