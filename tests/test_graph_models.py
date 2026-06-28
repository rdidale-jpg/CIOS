"""Tests for CIOS Sprint 3 graph foundation models."""

from __future__ import annotations

import importlib

from cios.core import Entity, Evidence
from cios.graph import Dependency, EvidenceLink, GraphEdge, GraphNode, Influence, KnowledgeGraphRecord
from cios.ontology import Capability, Customer


def test_graph_nodes_can_wrap_ontology_and_core_identifiers() -> None:
    """Graph nodes can reference identifiers owned by core and ontology."""

    entity = Entity(name="Acme Corp", entity_type="organisation")
    customer = Customer(name="Acme Corp", entity_id=entity.id)
    capability = Capability(name="Resilience advisory")

    core_node = GraphNode(wrapped_id=entity.id, wrapped_type="Entity", source_package="core", label=entity.name)
    customer_node = GraphNode(
        wrapped_id=customer.id,
        wrapped_type="Customer",
        source_package="ontology",
        label=customer.name,
    )
    capability_node = GraphNode(
        wrapped_id=capability.id,
        wrapped_type="Capability",
        source_package="ontology",
    )

    assert core_node.wrapped_id == entity.id
    assert customer_node.source_package == "ontology"
    assert capability_node.wrapped_type == "Capability"


def test_graph_edges_can_connect_two_nodes() -> None:
    """Graph edges connect a source node to a target node."""

    source = GraphNode(wrapped_id="customer_123", wrapped_type="Customer", source_package="ontology")
    target = GraphNode(wrapped_id="capability_123", wrapped_type="Capability", source_package="ontology")

    edge = GraphEdge(source_node_id=source.id, target_node_id=target.id, edge_type="needs")

    assert edge.source_node_id == source.id
    assert edge.target_node_id == target.id
    assert edge.edge_type == "needs"


def test_evidence_links_can_reference_evidence_identifiers() -> None:
    """Evidence links provide traceability from graph objects to evidence IDs."""

    evidence = Evidence(title="Customer strategy note", source="crm-note")
    node = GraphNode(wrapped_id="customer_123", wrapped_type="Customer", source_package="ontology")

    link = EvidenceLink(subject_id=node.id, evidence_ids=[evidence.id])

    assert link.subject_id == node.id
    assert link.evidence_ids == [evidence.id]


def test_knowledge_graph_record_serialization_works() -> None:
    """Graph records serialize nested graph foundation models to dictionaries."""

    source = GraphNode(wrapped_id="customer_123", wrapped_type="Customer", source_package="ontology")
    target = GraphNode(wrapped_id="capability_123", wrapped_type="Capability", source_package="ontology")
    edge = GraphEdge(source_node_id=source.id, target_node_id=target.id, edge_type="needs")
    dependency = Dependency(dependent_node_id=source.id, required_node_id=target.id)
    influence = Influence(source_node_id=target.id, target_node_id=source.id, influence_type="improves", direction="positive")
    evidence_link = EvidenceLink(subject_id=edge.id, evidence_ids=["evidence_123"])
    record = KnowledgeGraphRecord(
        name="Opportunity graph",
        nodes=[source, target],
        edges=[edge],
        dependencies=[dependency],
        influences=[influence],
        evidence_links=[evidence_link],
        metadata={"sprint": 3},
    )

    serialized = record.model_dump(mode="json")

    assert serialized["name"] == "Opportunity graph"
    assert serialized["nodes"][0]["id"] == source.id
    assert serialized["edges"][0]["target_node_id"] == target.id
    assert serialized["dependencies"][0]["dependency_type"] == "requires"
    assert serialized["influences"][0]["direction"] == "positive"
    assert serialized["evidence_links"][0]["evidence_ids"] == ["evidence_123"]
    assert serialized["metadata"] == {"sprint": 3}


def test_no_circular_imports_between_core_ontology_and_graph() -> None:
    """Graph imports independently with only core and ontology dependencies."""

    core_models = importlib.import_module("cios.core.models")
    ontology_models = importlib.import_module("cios.ontology.models")
    graph_models = importlib.import_module("cios.graph.models")

    assert core_models.Entity(name="Core Entity", entity_type="organisation")
    assert ontology_models.Customer(name="Ontology Customer")
    assert graph_models.GraphNode(wrapped_id="entity_123", wrapped_type="Entity", source_package="core")
