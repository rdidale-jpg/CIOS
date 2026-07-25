import io
import json
import zipfile

import pytest

from cios.applications.flora.blueprint_import.archive import inspect_zip_inventory
from cios.applications.flora.blueprint_import.package_contracts import PackageContract, PackageContractDetector


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
