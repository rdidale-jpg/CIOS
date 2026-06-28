"""Graph foundation models for the CIOS SDK.

Sprint 3 establishes graph-level primitives as thin, serializable Pydantic
models. These models represent graph nodes, edges, evidence links, dependencies,
influences, and portable knowledge graph records only. They do not implement a
graph database, persistence, reasoning, scoring, decision engine, agents, memory,
UI, or application logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from cios.core.identifiers import generate_identifier
from cios.core.models import CIOSBaseModel
from cios.core.validation import require_non_empty, utc_now


class GraphNode(CIOSBaseModel):
    """Node wrapper for a core or ontology object identifier."""

    id: str = Field(default_factory=lambda: generate_identifier("graph_node"))
    wrapped_id: str = Field(..., description="Identifier of the core or ontology object represented by this node.")
    wrapped_type: str = Field(..., description="Type or model name of the wrapped object.")
    source_package: Literal["core", "ontology"] = Field(
        ..., description="CIOS package that owns the wrapped identifier."
    )
    label: str | None = Field(default=None, description="Optional human-readable node label.")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("wrapped_id", "wrapped_type")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)

    @field_validator("label")
    @classmethod
    def _validate_label(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "label")


class GraphEdge(CIOSBaseModel):
    """Directed relationship connecting two graph nodes."""

    id: str = Field(default_factory=lambda: generate_identifier("graph_edge"))
    source_node_id: str = Field(..., description="Source GraphNode identifier.")
    target_node_id: str = Field(..., description="Target GraphNode identifier.")
    edge_type: str = Field(..., description="Relationship category between source and target nodes.")
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("source_node_id", "target_node_id", "edge_type")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class EvidenceLink(CIOSBaseModel):
    """Traceability link from a graph object to core Evidence identifiers."""

    id: str = Field(default_factory=lambda: generate_identifier("evidence_link"))
    subject_id: str = Field(..., description="Graph node, edge, dependency, influence, or record identifier.")
    evidence_ids: list[str] = Field(default_factory=list, description="Core Evidence identifiers supporting the subject.")
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("subject_id")
    @classmethod
    def _validate_subject_id(cls, value: str) -> str:
        return require_non_empty(value, "subject_id")

    @field_validator("evidence_ids")
    @classmethod
    def _validate_evidence_ids(cls, value: list[str]) -> list[str]:
        return [require_non_empty(evidence_id, "evidence_id") for evidence_id in value]


class Dependency(CIOSBaseModel):
    """Graph-level dependency from one node to another."""

    id: str = Field(default_factory=lambda: generate_identifier("dependency"))
    dependent_node_id: str = Field(..., description="GraphNode identifier that depends on another node.")
    required_node_id: str = Field(..., description="GraphNode identifier required by the dependent node.")
    dependency_type: str = Field(default="requires", description="Dependency category.")
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("dependent_node_id", "required_node_id", "dependency_type")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class Influence(CIOSBaseModel):
    """Graph-level influence relationship between two nodes."""

    id: str = Field(default_factory=lambda: generate_identifier("influence"))
    source_node_id: str = Field(..., description="GraphNode identifier exerting influence.")
    target_node_id: str = Field(..., description="GraphNode identifier receiving influence.")
    influence_type: str = Field(..., description="Influence category.")
    direction: Literal["positive", "negative", "neutral", "unknown"] = "unknown"
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("source_node_id", "target_node_id", "influence_type")
    @classmethod
    def _validate_required_text(cls, value: str, info: Any) -> str:
        return require_non_empty(value, info.field_name)


class KnowledgeGraphRecord(CIOSBaseModel):
    """Serializable collection of graph foundation objects."""

    id: str = Field(default_factory=lambda: generate_identifier("knowledge_graph_record"))
    name: str = Field(..., description="Human-readable record name.")
    description: str | None = None
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    evidence_links: list[EvidenceLink] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)
    influences: list[Influence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")
