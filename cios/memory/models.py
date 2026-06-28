"""Passive memory record models for the CIOS SDK.

Sprint 7D establishes serializable records that can hold evidence, assessment,
decision, and outcome references for future persistence adapters. The memory
package is intentionally passive: it defines data shapes only and must not call
reasoning, scoring, decision engine, agents, applications, databases, LLMs, or
external services.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from cios.core.identifiers import generate_identifier
from cios.core.models import CIOSBaseModel, Evidence
from cios.core.validation import require_non_empty, utc_now
from cios.graph.models import KnowledgeGraphRecord

MEMORY_SCHEMA_VERSION = "1.0.0"


class MemoryRecord(CIOSBaseModel):
    """Base persisted memory record.

    The base record stores identifiers and JSON-compatible payloads so upstream
    artefacts can be remembered without importing their owning orchestration
    packages. Persistence adapters are intentionally out of scope.
    """

    id: str = Field(default_factory=lambda: generate_identifier("memory_record"))
    schema_version: str = Field(default=MEMORY_SCHEMA_VERSION, description="Persisted memory schema version.")
    record_type: str = Field(..., description="Memory record category.")
    subject_id: str | None = Field(default=None, description="Primary CIOS object identifier this memory concerns.")
    related_ids: list[str] = Field(default_factory=list, description="Related CIOS object identifiers.")
    evidence_ids: list[str] = Field(default_factory=list, description="Core Evidence identifiers related to the memory.")
    graph_record_ids: list[str] = Field(default_factory=list, description="KnowledgeGraphRecord identifiers related to the memory.")
    payload: dict[str, Any] = Field(default_factory=dict, description="JSON-compatible passive payload snapshot.")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("schema_version", "record_type")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)

    @field_validator("subject_id")
    @classmethod
    def _validate_subject_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "subject_id")

    @field_validator("related_ids", "evidence_ids", "graph_record_ids")
    @classmethod
    def _validate_identifier_lists(cls, value: list[str], info: Any) -> list[str]:
        return [require_non_empty(identifier, info.field_name) for identifier in value]


class EvidenceMemoryRecord(MemoryRecord):
    """Passive memory snapshot for evidence and evidence-derived context."""

    id: str = Field(default_factory=lambda: generate_identifier("evidence_memory_record"))
    record_type: Literal["evidence"] = "evidence"
    evidence: list[Evidence] = Field(default_factory=list, description="Optional core Evidence snapshots.")


class AssessmentMemoryRecord(MemoryRecord):
    """Passive memory snapshot for an assessment produced elsewhere."""

    id: str = Field(default_factory=lambda: generate_identifier("assessment_memory_record"))
    record_type: Literal["assessment"] = "assessment"
    assessment_id: str | None = Field(default=None, description="External assessment identifier.")
    graph_records: list[KnowledgeGraphRecord] = Field(default_factory=list, description="Optional graph context snapshots.")

    @field_validator("assessment_id")
    @classmethod
    def _validate_assessment_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "assessment_id")


class DecisionMemoryRecord(MemoryRecord):
    """Passive memory reference to a decision output created by another package."""

    id: str = Field(default_factory=lambda: generate_identifier("decision_memory_record"))
    record_type: Literal["decision"] = "decision"
    decision_id: str = Field(..., description="Identifier of the decision output being remembered.")
    decision_payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Serialized decision output payload; avoids importing cios.decision_engine.",
    )

    @field_validator("decision_id")
    @classmethod
    def _validate_decision_id(cls, value: str) -> str:
        return require_non_empty(value, "decision_id")


class OutcomeMemoryRecord(MemoryRecord):
    """Passive memory snapshot for observed outcomes after actions are taken."""

    id: str = Field(default_factory=lambda: generate_identifier("outcome_memory_record"))
    record_type: Literal["outcome"] = "outcome"
    outcome: str = Field(..., description="Observed result or outcome summary.")
    decision_id: str | None = Field(default=None, description="Optional decision identifier linked to the outcome.")

    @field_validator("outcome")
    @classmethod
    def _validate_outcome(cls, value: str) -> str:
        return require_non_empty(value, "outcome")

    @field_validator("decision_id")
    @classmethod
    def _validate_decision_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "decision_id")
