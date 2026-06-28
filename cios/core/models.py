"""Foundational Pydantic models for the CIOS SDK.

Sprint 1 models are intentionally thin, serializable data structures. They do
not perform opportunity intelligence, scoring, agent orchestration, persistence,
or business workflows. Relationship, Opportunity, and Capability live in core as
a tactical Sprint 1 compromise and may migrate to graph or ontology modules as
those modules mature.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cios.core.identifiers import generate_identifier
from cios.core.types import ConfidenceLevel, DecisionStatus, EvidenceKind, RecommendationStatus
from cios.core.validation import require_non_empty, utc_now


class CIOSBaseModel(BaseModel):
    """Base configuration shared by all Sprint 1 core models."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, use_enum_values=True)


class Entity(CIOSBaseModel):
    """Generic object in the CIOS universe.

    Entities provide the smallest reusable unit for representing people,
    organisations, projects, documents, systems, or domain-specific objects.
    """

    id: str = Field(default_factory=lambda: generate_identifier("entity"), description="Unique entity identifier.")
    name: str = Field(..., description="Human-readable entity name.")
    entity_type: str = Field(..., description="Domain-neutral entity category.")
    description: str | None = Field(default=None, description="Optional description of the entity.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional serializable attributes.")
    created_at: datetime = Field(default_factory=utc_now, description="Timezone-aware creation timestamp.")

    @field_validator("name", "entity_type")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class Relationship(CIOSBaseModel):
    """Connection between two entities.

    Provisional Sprint 1 core model: long-term ownership may move to
    :mod:`cios.graph` once graph primitives are implemented.
    """

    id: str = Field(default_factory=lambda: generate_identifier("relationship"))
    source_entity_id: str = Field(..., description="Identifier of the relationship source entity.")
    target_entity_id: str = Field(..., description="Identifier of the relationship target entity.")
    relationship_type: str = Field(..., description="Type of connection between source and target.")
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("source_entity_id", "target_entity_id", "relationship_type")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class Evidence(CIOSBaseModel):
    """Source material supporting a claim, observation, or decision."""

    id: str = Field(default_factory=lambda: generate_identifier("evidence"))
    title: str = Field(..., description="Short evidence title.")
    kind: EvidenceKind = Field(default=EvidenceKind.NOTE, description="Evidence source category.")
    source: str = Field(..., description="Source reference, URI, filename, or note origin.")
    summary: str | None = Field(default=None, description="Brief evidence summary.")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("title", "source")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class Observation(CIOSBaseModel):
    """Detected commercial signal derived from evidence or analysis."""

    id: str = Field(default_factory=lambda: generate_identifier("observation"))
    statement: str = Field(..., description="Observation expressed as a concise statement.")
    evidence_ids: list[str] = Field(default_factory=list, description="Evidence identifiers supporting the observation.")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("statement")
    @classmethod
    def _validate_statement(cls, value: str) -> str:
        return require_non_empty(value, "statement")


class Recommendation(CIOSBaseModel):
    """Proposed action with supporting rationale and evidence."""

    id: str = Field(default_factory=lambda: generate_identifier("recommendation"))
    title: str = Field(..., description="Short recommendation title.")
    rationale: str = Field(..., description="Reason the action is recommended.")
    actions: list[str] = Field(default_factory=list, description="Concrete actions to consider.")
    evidence_ids: list[str] = Field(default_factory=list)
    status: RecommendationStatus = Field(default=RecommendationStatus.PROPOSED)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("title", "rationale")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class Decision(CIOSBaseModel):
    """Decision object with rationale, status, and traceability links."""

    id: str = Field(default_factory=lambda: generate_identifier("decision"))
    title: str = Field(..., description="Short decision title.")
    rationale: str = Field(..., description="Decision rationale.")
    recommendation_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    status: DecisionStatus = Field(default=DecisionStatus.DRAFT)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("title", "rationale")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class Opportunity(CIOSBaseModel):
    """Commercial opportunity being assessed.

    Provisional Sprint 1 core model: long-term ownership may move to
    :mod:`cios.ontology` once ontology primitives are implemented.
    """

    id: str = Field(default_factory=lambda: generate_identifier("opportunity"))
    name: str = Field(..., description="Opportunity name.")
    customer: str = Field(..., description="Customer or buying organisation.")
    description: str | None = None
    value: float | None = Field(default=None, ge=0, description="Optional non-negative opportunity value.")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name", "customer")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class Capability(CIOSBaseModel):
    """Reusable organisational capability.

    Provisional Sprint 1 core model: long-term ownership may move to
    :mod:`cios.ontology` once ontology primitives are implemented.
    """

    id: str = Field(default_factory=lambda: generate_identifier("capability"))
    name: str = Field(..., description="Capability name.")
    description: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")
