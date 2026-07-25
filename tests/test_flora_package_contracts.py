import io
import json
import zipfile

import pytest

from cios.applications.flora.blueprint_import.archive import inspect_zip_inventory
from cios.applications.flora.blueprint_import.package_contracts import PackageContract, PackageContractDetector
from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator


def package(*members):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as archive:
        for name, value in members:
            archive.writestr(name, json.dumps(value) if isinstance(value, (dict, list)) else value)
    return data.getvalue()


def inspect(content):
    return PackageContractDetector().detect(content, inspect_zip_inventory(content))


def test_blueprint_contract_is_exact_and_does_not_change_validation_boundary():
    result = inspect(package(("blueprint_manifest.json", {"package_id": "bp", "package_version": "1"})))
    assert result.contract_type is PackageContract.BLUEPRINT
    assert result.manifest_filename == "blueprint_manifest.json"
    assert result.package_identifier == "bp"
    assert result.promotion_eligible is False


def test_research_workspace_inventory_separates_promotable_assets_from_lineage():
    result = inspect(package(
        ("mission_state.json", {"workspace_id": "research-1", "workspace_version": "2"}),
        ("industry_twin_delta_for_Flora.json", {"records": []}),
        ("research_queue.json", []),
        ("deterministic_restart_state.json", {}),
        ("checkpoint_metadata.json", {}),
        ("evidence.json", {}),
    ))
    assert result.contract_type is PackageContract.RESEARCH_WORKSPACE
    assert {a.artefact_type for a in result.promotable_artefacts if a.promotable} == {"Industry Twin Delta", "Evidence"}
    assert {a.artefact_type for a in result.promotable_artefacts if not a.promotable} == {"Research Queue", "Restart State", "Checkpoint Metadata"}
    assert result.promotion_eligible


def test_standalone_delta_routes_as_delta_contract():
    result = inspect(package(("industry_twin_delta_for_Flora.json", {"delta_id": "d-1", "delta_version": "1"})))
    assert result.contract_type is PackageContract.INDUSTRY_TWIN_DELTA
    assert result.package_identifier == "d-1"


def test_unknown_and_similar_names_fail_closed():
    result = inspect(package(("copy_blueprint_manifest.json", {}), ("notes.txt", "temporary")))
    assert result.contract_type is PackageContract.UNKNOWN
    assert result.blocking_errors == ("Unknown package contract.",)
    assert not result.promotion_eligible
    assert "No canonical changes performed" in result.warnings[0]


def test_detector_requires_shared_safe_inventory_and_result_metadata_is_immutable():
    content = package(("mission_state.json", {"workspace_id": "r"}))
    with pytest.raises(ValueError):
        PackageContractDetector().detect(content, ())
    result = inspect(content)
    with pytest.raises(TypeError):
        result.package_metadata["workspace_id"] = "changed"


def test_unsafe_archive_is_rejected_before_detection():
    content = package(("../mission_state.json", {}))
    with pytest.raises(ValueError, match="Unsafe package member path"):
        inspect_zip_inventory(content)


def test_tms_nested_governed_package_is_detected_and_inventory_is_complete():
    result = inspect(package(
        ("TMS-001/00_manifest.json", {"mission_id": "TMS-001", "version": "1"}),
        ("TMS-001/industry-twin-delta-for-flora.json", {"records": []}),
        ("TMS-001/knowledge-graph.json", {}),
    ))
    assert result.contract_type is PackageContract.GOVERNED_INDUSTRY_TWIN
    assert result.manifest_filename == "00_manifest.json"
    assert result.package_identifier == "TMS-001"
    assert result.archive_summary.file_count == 3


def test_dist_modular_flora_package_is_detected():
    result = inspect(package(
        ("00_manifest.json", {"mission_id": "DIST-001", "version": "2"}),
        ("flora/promotion-manifest.json", {"mission_id": "DIST-001"}),
        ("flora/industry_twin_delta_for_Flora.json", {"records": []}),
    ))
    assert result.contract_type is PackageContract.GOVERNED_INDUSTRY_TWIN
    assert next(a.path for a in result.promotable_artefacts if a.artefact_type == "Industry Twin Delta") == "flora/industry_twin_delta_for_Flora.json"


def test_inspection_surfaces_normalised_governance_fields_and_register_counts():
    result = inspect(package(
        ("00_manifest.json", {
            "mission_id": "UKEU-001", "package_title": "Utilities & Energy",
            "research_state": "complete", "decision_maturity": "governed",
        }),
        ("industry-twin-delta-for-flora.json", {"records": [
            {"external_id": "EV-1", "record_class": "evidence", "payload": {}},
        ]}),
        ("registers/unknowns.json", {"unknowns": [{"id": "U-1"}, {"id": "U-2"}]}),
        ("registers/contradictions.json", [{"id": "C-1"}]),
    )).to_dict()

    assert result["industry_or_package_title"] == "Utilities & Energy"
    assert result["research_state"] == "complete"
    assert result["decision_maturity"] == "governed"
    assert result["unknown_count"] == 2
    assert result["contradiction_count"] == 1
    assert result["promotable_objects"] == ["EV-1"]


def test_ambiguous_contract_fails_closed():
    result = inspect(package(
        ("blueprint_manifest.json", {}),
        ("00_manifest.json", {}),
    ))
    assert result.contract_type is PackageContract.UNKNOWN
    assert result.blocking_errors[0].startswith("Ambiguous package contract")


def test_governed_package_missing_delta_is_inspectable_but_not_promotable():
    result = inspect(package(("00_manifest.json", {"mission_id": "UKEU-001"})))
    assert result.contract_type is PackageContract.GOVERNED_INDUSTRY_TWIN
    assert "missing an Industry Twin Delta" in result.blocking_errors[-1]
    assert not result.promotion_eligible


def test_archive_compression_bomb_is_constrained():
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("payload.txt", "0" * 100_000)
    with pytest.raises(ValueError, match="compression-ratio safety limit"):
        inspect_zip_inventory(data.getvalue())


def test_governed_delta_uses_existing_registry_and_staging(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package(
        ("00_manifest.json", {"mission_id": "UKEU-001", "version": "1"}),
        ("flora/industry-twin-delta-for-flora.json", {"records": [
            {"external_id": "EV-1", "record_class": "evidence", "truth_class": "asserted", "payload": {"statement": "governed"}},
        ]}),
        ("research_queue.json", [{"instruction": "never promote"}]),
    )
    receipt = BlueprintPackageRegistry().receive(content, "ukeu.zip", "auditor")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "auditor")
    summary = BlueprintPackageValidator().staging_summary(receipt.import_run_id)
    assert result.records_accepted_into_staging == 1
    assert [c["original_source_id"] for c in summary["candidates"]] == ["EV-1"]
    assert receipt.package_inspection["contract_type"] == "Governed Industry Twin Package"
    assert receipt.archive_path


def test_operation_oriented_governed_delta_preserves_identity_and_stages(tmp_path, monkeypatch):
    """Regression for producer Deltas that do not use the legacy records array."""
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package(
        ("00_manifest.json", {"package_id": "DIST-001", "version": "1.0", "industry": "Distribution"}),
        ("flora/industry-twin-delta-for-flora.json", {"delta": {"creates": [
            {"id": "DIST-OBS-001", "object_type": "observation", "data": {"statement": "Distribution demand is changing."}},
        ], "evidence": [
            {"stable_id": "DIST-EV-001", "statement": "A governed source supports the observation."},
        ]}}),
    )
    receipt = BlueprintPackageRegistry().receive(content, "DIST-001.zip", "auditor")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "auditor")
    candidates = BlueprintPackageValidator().staging_summary(receipt.import_run_id)["candidates"]

    assert receipt.original_filename == "DIST-001.zip"
    assert receipt.identity.package_id == "DIST-001"
    assert receipt.identity.enterprise_id == "DIST-001"
    assert receipt.package_inspection["contract_type"] == "Governed Industry Twin Package"
    assert result.candidate_records_staged == 2
    assert not result.errors
    assert {row["original_source_id"] for row in candidates} == {"DIST-OBS-001", "DIST-EV-001"}
    assert {row["payload"]["twin_type"] for row in candidates} == {"industry"}


def test_empty_governed_delta_is_an_explicit_blocking_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package(
        ("00_manifest.json", {"package_id": "DIST-001", "version": "1.0"}),
        ("flora/industry-twin-delta-for-flora.json", {"delta": {"creates": []}}),
    )
    receipt = BlueprintPackageRegistry().receive(content, "DIST-001.zip", "auditor")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "auditor")

    assert result.candidate_records_staged == 0
    assert "no staging candidates could be extracted" in result.errors[0]
    assert result.execution_trace[-1]["status"] == "Failed"
    assert result.execution_trace[-1]["delta_location"] == "flora/industry-twin-delta-for-flora.json"


def test_governed_metadata_precedence_and_filename_cannot_override(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package(
        ("00_manifest.json", {"mission_id": "TMS-001", "package_title": "Transport Twin", "package_profile": "industry-twin-v1"}),
        ("flora/promotion-manifest.json", {"mission_id": "TMS-001", "package_title": "Transport Twin"}),
        ("flora/industry_twin_delta_for_Flora.json", {"metadata": {"mission_id": "TMS-001"}, "records": []}),
        ("machine-inspectable/knowledge-graph.json", {"nodes": [], "edges": []}),
    )
    result = inspect(content).to_dict()
    receipt = BlueprintPackageRegistry().receive(content, "DIST-001.zip", "auditor")
    assert result["mission_identifier"] == "TMS-001"
    assert result["metadata_sources"]["mission_identifier"] == "flora/promotion-manifest.json"
    assert receipt.identity.package_id == "TMS-001"


def test_conflicting_governed_mission_ids_block_with_values_and_paths():
    result = inspect(package(
        ("00_manifest.json", {"mission_id": "UKEU-001"}),
        ("flora/promotion-manifest.json", {"mission_id": "DIST-001"}),
        ("flora/industry_twin_delta_for_Flora.json", {"records": []}),
        ("twins/industry-twin.json", {}),
    )).to_dict()
    assert not result["promotion_eligible"]
    assert result["metadata_conflicts"][0]["field"] == "mission_identifier"
    assert "00_manifest.json" in result["blocking_errors"][0]
    assert "flora/promotion-manifest.json" in result["blocking_errors"][0]


def test_missing_optional_governed_metadata_is_not_invented():
    result = inspect(package(
        ("00_manifest.json", {"mission_id": "DIST-001"}),
        ("flora/industry_twin_delta_for_Flora.json", {"records": []}),
        ("twins/industry-twin.json", {}),
    )).to_dict()
    assert result["twin_title"] is None
    assert result["research_state"] is None
    assert result["decision_maturity"] is None


def test_ambiguous_nested_governed_roots_block():
    result = inspect(package(
        ("one/00_manifest.json", {"mission_id": "ONE"}),
        ("one/industry_twin_delta_for_Flora.json", {"records": []}),
        ("two/00_manifest.json", {"mission_id": "TWO"}),
        ("two/industry_twin_delta_for_Flora.json", {"records": []}),
    ))
    assert any("Ambiguous nested package roots" in error for error in result.blocking_errors)
    assert not result.promotion_eligible


def test_dist_modular_assets_and_governed_paths_are_counted_conservatively():
    result = inspect(package(
        ("00_manifest.json", {"mission_id": "DIST-001", "twin_title": "Distribution Industry Twin", "twin_type": "Industry"}),
        ("flora/industry_twin_delta_for_Flora.json", {"records": [{"external_id": "I-1", "twin_type": "industry"}, {"external_id": "E-1", "record_class": "evidence"}]}),
        ("machine-inspectable/knowledge-graph.json", {"nodes": [{"id": "1"}, {"id": "2"}], "edges": [{"from": "1", "to": "2"}]}),
        ("registers/unknowns.json", {"unknowns": [{"id": "U"}]}),
        ("registers/contradictions.json", {"contradictions": [{"id": "C"}]}),
        ("workspace/deterministic_restart_state.json", {"mission_id": "DIST-001"}),
    )).to_dict()
    assert result["graph_location"] == "machine-inspectable/knowledge-graph.json"
    assert result["restart_state_location"] == "workspace/deterministic_restart_state.json"
    assert result["asset_counts"] == {"Industry Twins": 1, "Evidence records": 1, "graph nodes": 2, "graph edges": 1, "Unknowns": 1, "Contradictions": 1}


def test_browser_service_path_resolves_dist_primary_object_references(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package(
        ("flora/promotion-manifest.json", {"mission_id": "DIST-001", "title": "Distribution Industry Twin", "twin_type": "Industry", "package_version": "3", "package_profile": "governed-industry-twin", "research_state": "Research-ready", "decision_maturity": "Decision-ready"}),
        ("flora/industry-twin-delta-for-flora.json", {
            "mission_id": "DIST-001", "title": "Distribution Industry Twin", "research_state": "Research-ready",
            "decision_maturity": "Decision-ready", "primary_objects": {
                "enterprise_twins": ["ENT-1"], "market_participant_twins": ["MP-1"],
                "opportunity_twins": ["OPP-1"], "flow_twins": ["FLOW-1"],
            },
        }),
        ("collections/enterprise-twins.json", {"enterprise_twins": [{"twin_id": "ENT-1", "name": "Enterprise"}]}),
        ("collections/market-participant-twins.json", [{"stable_id": "MP-1", "name": "Participant"}]),
        ("collections/opportunity-twins.json", {"items": [{"object_id": "OPP-1", "name": "Opportunity"}]}),
        ("collections/flow-twins.csv", "id,name\nFLOW-1,Flow\n"),
        ("machine-inspectable/knowledge-graph.json", {"nodes": [{"id": "N1"}], "edges": [{"from": "N1", "to": "N1"}]}),
        ("registers/evidence.json", {"records": [{"id": "E1"}]}),
        ("registers/unknowns.json", {"unknowns": [{"id": "U1"}]}),
        ("registers/contradictions.json", {"contradictions": [{"id": "C1"}]}),
    )
    receipt = BlueprintPackageRegistry().receive(content, "DIST-001.zip", "auditor")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "auditor")
    candidates = BlueprintPackageValidator().staging_summary(receipt.import_run_id)["candidates"]

    assert receipt.package_inspection["package_contract"] == "Governed Industry Twin Package"
    assert receipt.package_inspection["mission_identifier"] == "DIST-001"
    assert receipt.package_inspection["twin_title"] == "Distribution Industry Twin"
    assert receipt.package_inspection["research_state"] == "Research-ready"
    assert receipt.package_inspection["decision_maturity"] == "Decision-ready"
    expected_counts = {"Enterprise Twins": 1, "Market Participant Twins": 1, "Opportunity Twins": 1, "Flow Twins": 1, "graph nodes": 1, "graph edges": 1, "Evidence records": 1, "Unknowns": 1, "Contradictions": 1}
    assert expected_counts.items() <= receipt.package_inspection["asset_counts"].items()
    assert result.records_accepted_into_staging == 4
    assert {row["original_source_id"] for row in candidates} == {"ENT-1", "MP-1", "OPP-1", "FLOW-1"}
    trace_text = json.dumps(result.execution_trace).casefold()
    assert "workbook" not in trace_text and "worksheet" not in trace_text
    assert "collections/flow-twins.csv" in trace_text


def test_primary_object_missing_collection_and_identifier_block_staging(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    base = [("flora/promotion-manifest.json", {"mission_id": "DIST-001"}),
            ("flora/industry-twin-delta-for-flora.json", {"primary_objects": {"enterprise_twins": ["ENT-1"]}})]
    receipt = BlueprintPackageRegistry().receive(package(*base), "missing.zip", "auditor")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "auditor")
    assert "missing governed collection" in result.errors[0]
    assert result.candidate_records_staged == 0

    content = package(*base, ("collections/enterprise-twins.json", [{"name": "No identifier"}]))
    receipt = BlueprintPackageRegistry().receive(content, "identifier.zip", "auditor")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "auditor")
    assert "no stable identifier" in result.errors[0]
    assert result.candidate_records_staged == 0


def test_duplicate_governed_identifier_blocks_and_failure_trace_is_truthful(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package(
        ("flora/promotion-manifest.json", {"mission_id": "DIST-001"}),
        ("flora/industry-twin-delta-for-flora.json", {"primary_objects": {"enterprise_twins": ["ENT-1"]}}),
        ("collections/enterprise-twins.json", [
            {"twin_id": "ENT-1", "name": "First"},
            {"twin_id": "ENT-1", "name": "Duplicate"},
        ]),
    )
    receipt = BlueprintPackageRegistry().receive(content, "duplicate-id.zip", "auditor")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "auditor")
    persisted = BlueprintPackageRegistry().get(receipt.package_ref).package_inspection

    assert result.candidate_records_staged == 0
    assert "duplicate governed identifier 'ENT-1'" in result.errors[0]
    assert persisted["resolved_candidate_count"] == 0
    assert persisted["governed_resolution"]["duplicate_identifier_counts"]["enterprise_twins"] == 1
    actions = [event["action"] for event in result.execution_trace]
    assert "References resolved" not in actions
    assert "Staging candidates created" not in actions
    assert result.execution_trace[-1]["safe_output_summary"] == "Staging not started; 0 candidates"


def test_promotion_manifest_collection_path_has_precedence(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package(
        ("flora/promotion-manifest.json", {
            "mission_id": "DIST-001",
            "collections": {"enterprise_twins": {"path": "governed/enterprises.json"}},
        }),
        ("flora/industry-twin-delta-for-flora.json", {"primary_objects": {"enterprise_twins": ["ENT-1"]}}),
        ("governed/enterprises.json", {"objects": [{"enterprise_twin_id": "ENT-1", "title": "Enterprise"}]}),
        ("collections/enterprise-twins.json", [{"twin_id": "WRONG", "name": "Convention fallback"}]),
    )
    receipt = BlueprintPackageRegistry().receive(content, "manifest-path.zip", "auditor")
    validator = BlueprintPackageValidator()
    result = validator.validate_and_stage(receipt.package_ref, "auditor")
    candidate = validator.staging_summary(receipt.import_run_id)["candidates"][0]

    assert result.records_accepted_into_staging == 1
    assert candidate["original_source_id"] == "ENT-1"
    assert candidate["source_file"] == "governed/enterprises.json"

def test_conflicting_governed_metadata_blocks_service_path_before_staging(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package(
        ("flora/promotion-manifest.json", {"mission_id": "DIST-001"}),
        ("flora/industry-twin-delta-for-flora.json", {"mission_id": "OTHER-001", "records": [{"id": "X", "record_class": "evidence"}]}),
    )
    receipt = BlueprintPackageRegistry().receive(content, "conflict.zip", "auditor")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "auditor")
    assert "Conflicting mission identifier" in result.errors[0]
    assert result.candidate_records_staged == 0
