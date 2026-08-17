"""Regression proof for governed Opportunity-to-Enterprise projection."""
from cios.applications.flora.blueprint_import.executive_workspace import _opportunity_card
from cios.applications.flora.blueprint_import.semantic_twin import (
    assemble_semantic_twin, opportunity_enterprise_names, resolve_relationships,
)


def row(identifier, kind, payload):
    return {
        "candidate_record_id": f"cand-{identifier}",
        "original_source_id": identifier,
        "candidate_object_class": kind,
        "governance_status": "accepted",
        "payload": {"id": identifier, **payload},
    }


def test_governed_opportunity_relationship_drives_customer_and_preserves_title_domain():
    twin = assemble_semantic_twin([
        row("ENT-CADENT", "enterprise_twin", {"enterprise_name": "Cadent Gas"}),
        row("OPP-CADENT-1", "opportunity_hypothesis", {
            "opportunity_title": "Network resilience modernisation",
            "domain": "Energy & Utilities",
            "client_problem": "Maintain network resilience",
            "evidence_refs": ["EV-1"],
        }),
        row("REL-1", "relationship", {
            "source": "OPP-CADENT-1", "target": "ENT-CADENT",
            "relationship_type": "Opportunity targets Enterprise",
        }),
    ])
    opportunity = next(o for o in twin.objects if o.original_id == "OPP-CADENT-1")

    assert resolve_relationships(twin)[0].resolved
    assert opportunity_enterprise_names(twin, opportunity) == ("Cadent Gas",)
    assert opportunity.statement == "Network resilience modernisation"
    assert opportunity.domains == ("energy & utilities",)
    html = _opportunity_card(opportunity, "run-1", twin)
    assert "<strong>Customer:</strong> Cadent Gas" in html
    assert "<h3>Network resilience modernisation</h3>" in html
    assert "Relevant domain:</strong> Energy &amp; Utilities" in html


def test_opportunity_without_governed_enterprise_edge_remains_explicitly_unknown():
    twin = assemble_semantic_twin([
        row("ENT-CADENT", "enterprise_twin", {"enterprise_name": "Cadent Gas"}),
        row("OPP-UNLINKED", "opportunity_hypothesis", {
            "opportunity_title": "Unlinked hypothesis",
            "affected_enterprises": ["Cadent Gas"],
        }),
    ])
    opportunity = next(o for o in twin.objects if o.original_id == "OPP-UNLINKED")

    assert opportunity_enterprise_names(twin, opportunity) == ()
    assert "<strong>Customer:</strong> Affected enterprise not established" in _opportunity_card(
        opportunity, "run-1", twin)
