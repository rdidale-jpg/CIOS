import json
import zipfile
from pathlib import Path

import pytest

from cios.applications.flora.blueprint_import.researcher_profile_adapter import CONTRACT, adapt_researcher_payload

TEL001 = "docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip"


def _first(path):
    with zipfile.ZipFile(TEL001) as archive:
        data = json.loads(archive.read(path))
    return data[0] if isinstance(data, list) else data


def test_flora_adapter_is_driven_by_governed_profile_contract():
    assert CONTRACT["document_id"] == "TOP-RESEARCHER-PORTABLE-OBJECTS-v1"
    assert "opportunity_hypothesis" in CONTRACT["profiles"]


def test_tel001_opportunity_shape_projects_required_owner_fields():
    _, payload = adapt_researcher_payload("opportunity_hypothesis", _first("content/source/opportunity_objects_wave5.json"))
    assert payload["client_problem"]
    assert payload["procurement_timing"]
    assert payload["value_range"]
    assert payload["affected_enterprises"]
    assert payload["mapping_diagnostics"]["contract_id"] == CONTRACT["document_id"]


def test_tel001_supported_object_families_share_profile_contract():
    cases = {
        "industry_twin": "content/source/industry_overview_wave5.json",
        "enterprise_twin": "content/source/enterprise_dossiers_wave5.json",
        "market_participant_twin": "content/source/market_participant_profiles_wave5.json",
        "transformation_programme": "content/source/programme_objects_wave5.json",
        "opportunity_hypothesis": "content/source/opportunity_objects_wave5.json",
        "ai_reinvention_assessment": "content/source/reinvention_assessments_wave5.json",
    }
    for record_class, path in cases.items():
        canonical_class, payload = adapt_researcher_payload(record_class, _first(path))
        assert canonical_class in CONTRACT["profiles"]
        assert payload["mapping_diagnostics"]["mapped_fields"], record_class


def _validate_against_contract(record_class, payload, declared_profile_version=None):
    if declared_profile_version is not None and declared_profile_version != CONTRACT["profile_version"]:
        raise ValueError("profile version drift")
    canonical_class, mapped = adapt_researcher_payload(record_class, payload)
    if canonical_class not in CONTRACT["profiles"]:
        raise ValueError("unsupported profile class")
    required = CONTRACT["profiles"][canonical_class].get("required_fields", ())
    missing = [field for field in required if not mapped.get(field)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    return mapped


def test_external_researcher_pack_includes_same_profile_and_validation_consumes_it():
    canonical = json.loads(Path("cios/contracts/twin_object_profiles/researcher_v1.json").read_text())
    packed = json.loads(Path("knowledge-packs/researcher/contracts/researcher_v1.json").read_text())
    manifest = Path("knowledge-packs/researcher/manifest.yaml").read_text()
    assert packed == canonical == CONTRACT
    assert "contracts/researcher_v1.json" in manifest
    assert "TOP-RESEARCHER-PORTABLE-OBJECTS-v1" in manifest

    conformant = _first("content/source/opportunity_objects_wave5.json")
    mapped = _validate_against_contract("opportunity_hypothesis", conformant, "1.0.0")
    assert mapped["client_problem"] and mapped["procurement_timing"]

    with pytest.raises(ValueError, match="missing required fields"):
        _validate_against_contract("opportunity_hypothesis", {"opportunity_title": "bad"}, "1.0.0")
    with pytest.raises(ValueError, match="profile version drift"):
        _validate_against_contract("opportunity_hypothesis", conformant, "9.9.9")
    with pytest.raises(ValueError, match="unsupported profile class"):
        _validate_against_contract("invented_profile", {"id": "bad"}, "1.0.0")


def test_profile_version_drift_protection_agrees_across_researcher_flora_package_and_fixture():
    with zipfile.ZipFile(TEL001) as archive:
        package_version = json.loads(archive.read("blueprint_manifest.json"))["profile_version"]
    fixture_profile_version = "1.0.0"
    researcher_pack_version = json.loads(Path("knowledge-packs/researcher/contracts/researcher_v1.json").read_text())["profile_version"]
    flora_loaded_version = CONTRACT["profile_version"]
    assert {researcher_pack_version, flora_loaded_version, package_version, fixture_profile_version} == {"1.0.0"}
