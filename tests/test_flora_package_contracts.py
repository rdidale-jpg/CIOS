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
