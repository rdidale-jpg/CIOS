"""Decision engine foundation models for the CIOS SDK.

Sprint 6 establishes thin, serializable Pydantic models for decision inputs,
options, criteria, assessments, rationales, and outputs only. These models do
not implement agents, memory, UI, persistence, LLM calls, prompt orchestration,
or application workflows.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from cios.core.identifiers import generate_identifier
from cios.core.models import CIOSBaseModel, Evidence, Observation, Recommendation
from cios.core.types import ConfidenceLevel, DecisionStatus
from cios.core.validation import require_non_empty, utc_now
from cios.graph.models import KnowledgeGraphRecord
from cios.reasoning.models import ReasoningResult, ReasoningTrace
from cios.scoring.models import Score, ScoringResult


class DecisionInput(CIOSBaseModel):
    """Serializable input bundle for a decision assessment."""

    id: str = Field(default_factory=lambda: generate_identifier("decision_input"))
    name: str = Field(..., description="Human-readable name for the decision input.")
    question: str = Field(..., description="Decision question or problem statement to assess.")
    graph_records: list[KnowledgeGraphRecord] = Field(
        default_factory=list, description="Knowledge graph records relevant to the decision."
    )
    reasoning_traces: list[ReasoningTrace] = Field(default_factory=list)
    reasoning_results: list[ReasoningResult] = Field(default_factory=list)
    scoring_results: list[ScoringResult] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name", "question")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class DecisionOption(CIOSBaseModel):
    """Candidate option that may be selected, rejected, or compared."""

    id: str = Field(default_factory=lambda: generate_identifier("decision_option"))
    title: str = Field(..., description="Short option title.")
    description: str | None = Field(default=None)
    actions: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        return require_non_empty(value, "title")

    @field_validator("description")
    @classmethod
    def _validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "description")

    @field_validator("actions", "evidence_ids")
    @classmethod
    def _validate_text_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(item, info.field_name) for item in value]


class DecisionCriteria(CIOSBaseModel):
    """Criterion used to assess or compare decision options."""

    id: str = Field(default_factory=lambda: generate_identifier("decision_criteria"))
    name: str = Field(..., description="Criterion name.")
    description: str | None = None
    weight: float = Field(default=1.0, ge=0, description="Non-negative criterion weight.")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")


class DecisionAssessment(CIOSBaseModel):
    """Assessment of one option against one or more criteria."""

    id: str = Field(default_factory=lambda: generate_identifier("decision_assessment"))
    option_id: str = Field(..., description="DecisionOption identifier being assessed.")
    criteria_scores: dict[str, Score] = Field(
        default_factory=dict, description="Mapping of DecisionCriteria identifiers to scores."
    )
    overall_score: Score | None = Field(default=None)
    rationale: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    reasoning_trace_ids: list[str] = Field(default_factory=list)
    scoring_result_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("option_id")
    @classmethod
    def _validate_option_id(cls, value: str) -> str:
        return require_non_empty(value, "option_id")

    @field_validator("rationale")
    @classmethod
    def _validate_rationale(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "rationale")

    @field_validator("evidence_ids", "reasoning_trace_ids", "scoring_result_ids")
    @classmethod
    def _validate_identifier_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(identifier, info.field_name) for identifier in value]


class DecisionRationale(CIOSBaseModel):
    """Evidence-backed rationale explaining a decision output."""

    id: str = Field(default_factory=lambda: generate_identifier("decision_rationale"))
    summary: str = Field(..., description="Concise rationale summary.")
    evidence_ids: list[str] = Field(default_factory=list)
    reasoning_trace_ids: list[str] = Field(default_factory=list)
    reasoning_result_ids: list[str] = Field(default_factory=list)
    score_ids: list[str] = Field(default_factory=list)
    scoring_result_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, value: str) -> str:
        return require_non_empty(value, "summary")

    @field_validator("evidence_ids", "reasoning_trace_ids", "reasoning_result_ids", "score_ids", "scoring_result_ids")
    @classmethod
    def _validate_identifier_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(identifier, info.field_name) for identifier in value]


class DecisionOutput(CIOSBaseModel):
    """Serializable output bundle produced by a decision assessment."""

    id: str = Field(default_factory=lambda: generate_identifier("decision_output"))
    title: str = Field(..., description="Short decision output title.")
    input_id: str | None = Field(default=None, description="DecisionInput identifier used to produce this output.")
    selected_option_id: str | None = Field(default=None)
    status: DecisionStatus = Field(default=DecisionStatus.DRAFT)
    options: list[DecisionOption] = Field(default_factory=list)
    criteria: list[DecisionCriteria] = Field(default_factory=list)
    assessments: list[DecisionAssessment] = Field(default_factory=list)
    rationales: list[DecisionRationale] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    outcome: Literal["selected", "deferred", "rejected", "unknown"] = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        return require_non_empty(value, "title")

    @field_validator("input_id", "selected_option_id")
    @classmethod
    def _validate_optional_ids(cls, value: str | None, info: Any) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, info.field_name)
