"""Agent-facing contract models for the CIOS SDK.

Sprint 9A establishes structured contracts that future agent implementations may
use to exchange inputs, findings, recommendations, and trace metadata. These
models are intentionally passive: they do not execute agents, call LLMs, access
memory, persist records, invoke applications, or bypass reasoning, scoring, or
decision policy.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field, field_validator

from cios.core.identifiers import generate_identifier
from cios.core.models import CIOSBaseModel
from cios.core.types import ConfidenceLevel
from cios.core.validation import require_non_empty, utc_now


class AgentRole(StrEnum):
    """Supported non-autonomous role labels for agent-facing contracts."""

    OBSERVER = "observer"
    REASONING_ASSISTANT = "reasoning_assistant"
    SCORING_ASSISTANT = "scoring_assistant"
    DECISION_ASSISTANT = "decision_assistant"
    EXPLAINABILITY_ASSISTANT = "explainability_assistant"


class AgentExecutionContext(CIOSBaseModel):
    """Explicit boundary and traceability context supplied to an agent."""

    id: str = Field(default_factory=lambda: generate_identifier("agent_execution_context"))
    role: AgentRole = Field(..., description="Role requested for the agent-facing interaction.")
    user_id: str | None = Field(default=None, description="Optional caller or human decision-maker identifier.")
    session_id: str | None = Field(default=None, description="Optional interaction/session identifier.")
    evidence_ids: list[str] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    reasoning_trace_ids: list[str] = Field(default_factory=list)
    score_ids: list[str] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    recommendation_ids: list[str] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("user_id", "session_id")
    @classmethod
    def _validate_optional_text(cls, value: str | None, info: Any) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, info.field_name)

    @field_validator(
        "evidence_ids",
        "observation_ids",
        "reasoning_trace_ids",
        "score_ids",
        "decision_ids",
        "recommendation_ids",
        "rule_ids",
    )
    @classmethod
    def _validate_identifier_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(identifier, info.field_name) for identifier in value]


class AgentInput(CIOSBaseModel):
    """Structured input envelope for a future agent implementation."""

    id: str = Field(default_factory=lambda: generate_identifier("agent_input"))
    role: AgentRole = Field(..., description="Agent role requested for this input.")
    objective: str = Field(..., description="Bounded task objective; not an autonomous execution instruction.")
    context: AgentExecutionContext | None = Field(default=None)
    allowed_reference_ids: list[str] = Field(
        default_factory=list,
        description="Optional whitelist of existing artefact identifiers the agent may reference.",
    )
    constraints: list[str] = Field(default_factory=list, description="Human-readable boundary constraints.")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("objective")
    @classmethod
    def _validate_objective(cls, value: str) -> str:
        return require_non_empty(value, "objective")

    @field_validator("allowed_reference_ids", "constraints")
    @classmethod
    def _validate_text_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(item, info.field_name) for item in value]


class AgentFinding(CIOSBaseModel):
    """Structured finding returned by an agent-facing contract."""

    id: str = Field(default_factory=lambda: generate_identifier("agent_finding"))
    title: str = Field(..., description="Short finding title.")
    statement: str = Field(..., description="Finding stated as a concise claim.")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    evidence_ids: list[str] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    reasoning_trace_ids: list[str] = Field(default_factory=list)
    score_ids: list[str] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("title", "statement")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)

    @field_validator("evidence_ids", "observation_ids", "reasoning_trace_ids", "score_ids", "rule_ids")
    @classmethod
    def _validate_identifier_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(identifier, info.field_name) for identifier in value]


class AgentRecommendation(CIOSBaseModel):
    """Structured, non-binding agent recommendation candidate."""

    id: str = Field(default_factory=lambda: generate_identifier("agent_recommendation"))
    title: str = Field(..., description="Short recommendation candidate title.")
    rationale: str = Field(..., description="Rationale grounded in existing CIOS artefacts.")
    recommendation_type: Literal["candidate", "explanation", "review", "escalation"] = "candidate"
    evidence_ids: list[str] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    reasoning_trace_ids: list[str] = Field(default_factory=list)
    score_ids: list[str] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    recommendation_ids: list[str] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("title", "rationale")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)

    @field_validator(
        "evidence_ids",
        "observation_ids",
        "reasoning_trace_ids",
        "score_ids",
        "decision_ids",
        "recommendation_ids",
        "rule_ids",
    )
    @classmethod
    def _validate_identifier_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(identifier, info.field_name) for identifier in value]


class AgentTrace(CIOSBaseModel):
    """Trace metadata describing contract-level inputs and outputs only."""

    id: str = Field(default_factory=lambda: generate_identifier("agent_trace"))
    agent_input_id: str | None = Field(default=None)
    context_id: str | None = Field(default=None)
    referenced_evidence_ids: list[str] = Field(default_factory=list)
    referenced_observation_ids: list[str] = Field(default_factory=list)
    referenced_reasoning_trace_ids: list[str] = Field(default_factory=list)
    referenced_score_ids: list[str] = Field(default_factory=list)
    referenced_decision_ids: list[str] = Field(default_factory=list)
    referenced_recommendation_ids: list[str] = Field(default_factory=list)
    referenced_rule_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("agent_input_id", "context_id")
    @classmethod
    def _validate_optional_ids(cls, value: str | None, info: Any) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, info.field_name)

    @field_validator(
        "referenced_evidence_ids",
        "referenced_observation_ids",
        "referenced_reasoning_trace_ids",
        "referenced_score_ids",
        "referenced_decision_ids",
        "referenced_recommendation_ids",
        "referenced_rule_ids",
        "notes",
    )
    @classmethod
    def _validate_text_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(item, info.field_name) for item in value]


class AgentOutput(CIOSBaseModel):
    """Structured output envelope returned by an agent-facing contract."""

    id: str = Field(default_factory=lambda: generate_identifier("agent_output"))
    role: AgentRole = Field(..., description="Role that produced the structured output.")
    input_id: str | None = Field(default=None)
    summary: str = Field(..., description="Concise structured-output summary.")
    findings: list[AgentFinding] = Field(default_factory=list)
    recommendations: list[AgentRecommendation] = Field(default_factory=list)
    trace: AgentTrace | None = Field(default=None)
    status: Literal["draft", "complete", "blocked"] = "complete"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, value: str) -> str:
        return require_non_empty(value, "summary")

    @field_validator("input_id")
    @classmethod
    def _validate_input_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "input_id")
