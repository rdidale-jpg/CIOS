from __future__ import annotations

from cios.applications.flora.runtime.increment1 import (
    ContractValidationError,
    open_focus_object,
    read_json,
    validate_contract,
    validate_fixture_corpus,
    FIXTURE_DIR,
)


def test_lloyds_workspace_reading_order_and_boundaries():
    workspace = open_focus_object().to_dict()
    assert list(workspace) == [
        "focus_object",
        "relationships",
        "evidence_observation_availability",
        "unknowns",
        "contradictions",
        "lineage",
        "workspace_state",
        "safe_unavailable_notices",
    ]
    assert workspace["focus_object"]["identity"]["object_id"] == "BK-ENT-001"
    assert workspace["focus_object"]["persistence_class"] == "read_projection"
    assert workspace["workspace_state"]["focus_object_id"] == "BK-ENT-001"
    forbidden_workspace_keys = {"evidence", "observations", "unknowns", "contradictions", "canonical_objects"}
    assert forbidden_workspace_keys.isdisjoint(workspace["workspace_state"])


def test_all_valid_and_partial_fixtures_pass_and_invalid_fails_correctly():
    outcome = validate_fixture_corpus()
    assert all("valid/" in p or "partial/" in p or "safe-unavailable/" in p or p.endswith("invalid/ingestion-identifier-collision.json") for p in outcome["passed"])
    assert outcome["failed"] == ["fixtures/flora-runtime/increment-1/uk-banking/invalid/focus-object-missing-authority.json"]


def test_invalid_focus_object_missing_authority_fails_schema():
    payload = read_json(FIXTURE_DIR / "invalid" / "focus-object-missing-authority.json")
    try:
        validate_contract(payload, "focus-object-projection-v0.1.schema.json")
    except ContractValidationError as exc:
        assert "authority_status" in str(exc)
    else:
        raise AssertionError("invalid fixture unexpectedly passed")


def test_safe_unavailable_for_unsupported_object_is_consistent():
    response = open_focus_object("unsupported-object")
    assert response["status"] == "safe_unavailable"
    assert response["reason_code"] == "identifier_unresolved"
    assert response["retryable"] is False


def test_architecture_compliance_preserves_separation_and_lineage():
    workspace = open_focus_object().to_dict()
    availability = workspace["evidence_observation_availability"]
    assert availability["evidence_count"] >= 1
    assert availability["observation_count"] >= 1
    assert availability["accepted_observation_count"] <= availability["observation_count"]
    assert workspace["unknowns"][0]["statement"]
    assert workspace["contradictions"][0]["conflicting_references"]
    node_types = {node["node_type"] for node in workspace["lineage"]["lineage_nodes"]}
    assert {"source", "evidence", "observation", "governed_object", "projection"}.issubset(node_types)
