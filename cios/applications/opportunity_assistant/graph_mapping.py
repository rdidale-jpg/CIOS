"""Knowledge graph mapping for the Opportunity Assistant."""

from __future__ import annotations

from cios.core import Evidence
from cios.graph import EvidenceLink, GraphEdge, GraphNode, KnowledgeGraphRecord

from cios.applications.opportunity_assistant.ontology_mapping import OpportunityOntologyResult


def create_graph(ontology: OpportunityOntologyResult, evidence: list[Evidence]) -> KnowledgeGraphRecord:
    """Map ontology records and evidence links into an in-memory graph record."""

    objects = [ontology.customer, ontology.opportunity, ontology.contract, *ontology.capabilities, *ontology.competitors]
    nodes = [GraphNode(wrapped_id=obj.id, wrapped_type=obj.__class__.__name__, source_package="ontology", label=obj.name) for obj in objects]
    by_wrapped_id = {node.wrapped_id: node for node in nodes}
    opportunity_node = by_wrapped_id[ontology.opportunity.id]
    edges = [
        GraphEdge(source_node_id=opportunity_node.id, target_node_id=by_wrapped_id[ontology.customer.id].id, edge_type="for_customer"),
        GraphEdge(source_node_id=opportunity_node.id, target_node_id=by_wrapped_id[ontology.contract.id].id, edge_type="governed_by_contract"),
    ]
    edges.extend(
        GraphEdge(source_node_id=opportunity_node.id, target_node_id=by_wrapped_id[item.id].id, edge_type=edge_type)
        for edge_type, items in [("requires_capability", ontology.capabilities), ("competes_against", ontology.competitors)]
        for item in items
    )
    return KnowledgeGraphRecord(
        name="Opportunity Assistant Knowledge Graph",
        description="In-memory graph record created for the Sprint 7A vertical slice.",
        nodes=nodes,
        edges=edges,
        evidence_links=[EvidenceLink(subject_id=opportunity_node.id, evidence_ids=[item.id for item in evidence])],
    )
