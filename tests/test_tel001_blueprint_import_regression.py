"""Regression proof for the immutable TEL-001 Import Twin evidence package."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin


EVIDENCE = Path("docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip")
EVIDENCE_SHA256 = "bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07"


def test_tel001_evidence_inventory_manifest_counts_checksums_and_shapes():
    assert EVIDENCE.is_file()
    content = EVIDENCE.read_bytes()
    assert hashlib.sha256(content).hexdigest() == EVIDENCE_SHA256

    with zipfile.ZipFile(EVIDENCE) as archive:
        names = archive.namelist()
        assert len(names) == 125
        assert [name for name in names if "/" not in name] == ["blueprint_manifest.json"]
        assert sum(name.startswith("record_sets/") for name in names) == 36
        assert sum(name.startswith("content/") for name in names) == 88
        manifest = json.loads(archive.read("blueprint_manifest.json"))
        assert {key: manifest[key] for key in (
            "schema_version", "package_version", "profile_version"
        )} == {
            "schema_version": "1.0",
            "package_version": "5.0-corrected.import.2",
            "profile_version": "1.0.0",
        }
        assert len(manifest["files"]) == 88
        assert len(manifest["record_sets"]) == 36
        for item in manifest["files"]:
            assert hashlib.sha256(archive.read(item["path"])).hexdigest() == item["sha256"]
        for record_set in manifest["record_sets"]:
            rows = [json.loads(line) for line in archive.read(record_set["path"]).splitlines() if line.strip()]
            assert len(rows) == record_set["count"]
            assert all(isinstance(row, dict) for row in rows)
        evidence = json.loads(archive.read("record_sets/evidence_register_wave5.ndjson").splitlines()[0])
        opportunity = json.loads(archive.read("record_sets/opportunity_objects_wave5.ndjson").splitlines()[0])
        relationship = json.loads(archive.read("record_sets/relationship_register_wave5.ndjson").splitlines()[0])
        assert {"id", "title", "publisher", "url", "supported_claim"} <= evidence.keys()
        assert {"opportunity_id", "client_problem", "buyer", "evidence", "unknowns"} <= opportunity.keys()
        assert {"id", "source", "target", "relationship_type", "evidence"} <= relationship.keys()


def test_unchanged_tel001_package_reaches_semantic_staging_without_promotion(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    before = hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()
    package = BlueprintPackageRegistry().receive(EVIDENCE.read_bytes(), EVIDENCE.name, "regression-auditor")
    result = BlueprintPackageValidator().validate_and_stage(package.package_ref, "regression-auditor")
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    candidates = summary["candidates"]

    assert package.package_sha256 == before == EVIDENCE_SHA256
    assert hashlib.sha256(EVIDENCE.read_bytes()).hexdigest() == before
    assert package.package_inspection["contract_type"] == "Blueprint Package"
    assert (result.candidate_records_staged, result.records_accepted_into_staging,
            result.records_quarantined, result.records_rejected) == (1060, 640, 7, 0)
    assert result.canonical_mutations == 0
    assert Counter(candidate["validation_status"] for candidate in candidates) == {
        "accepted": 640, "ignored": 413, "quarantined": 7,
    }
    assert Counter(candidate["candidate_object_class"] for candidate in candidates
                   if candidate["validation_status"] == "accepted") == {
        "industry_twin": 1,
        "enterprise_twin": 6,
        "market_participant_twin": 17,
        "opportunity_hypothesis": 17,
        "transformation_programme": 13,
        "evidence": 92,
        "unknown": 30,
        "contradiction": 11,
        "relationship": 358,
        "refresh_trigger": 95,
    }
    assert Counter(candidate["candidate_object_class"] for candidate in candidates
                   if candidate["validation_status"] == "quarantined") == {
        "transformation_pressure_view": 7,
    }
    twin = assemble_semantic_twin([candidate for candidate in candidates
                                   if candidate["validation_status"] == "accepted"])
    assert len(twin.objects) == 640
    assert len(twin.enterprises) == 6
    assert not (tmp_path / "memory").exists()


def test_tel001_candidates_are_shared_by_governance_twin_map_and_research_gaps(monkeypatch, tmp_path):
    """Runtime boundary regression: staging is the shared candidate read owner."""
    from cios.applications.flora.blueprint_import.candidates import CandidateStagingRepository
    from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    monkeypatch.delenv("FLORA_PILOT_AUTO_SIGN_IN", raising=False)

    package = BlueprintPackageRegistry().receive(EVIDENCE.read_bytes(), EVIDENCE.name, "regression-auditor")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "regression-auditor")

    # Governance and projection must enumerate the same persisted candidate identities.
    governed = CandidateStagingRepository().list_candidates(package.import_run_id)
    accepted = [candidate for candidate in governed if candidate["validation_status"] == "accepted"]
    assert len(governed) == 1060
    assert len(accepted) == 640
    assert len({candidate["candidate_record_id"] for candidate in governed}) == 1060

    twin_map, status = executive_workspace_page(package.import_run_id, {}, view="workspace")
    assert status == 200
    for inventory in (
        "1 canonical Industry Twin concept(s)",
        "6 canonical enterprise(s)",
        "17 canonical participant(s)",
        "13 canonical programme hypothesis/hypotheses",
        "17 canonical opportunity hypothesis/hypotheses",
    ):
        assert inventory in twin_map

    gaps, status = executive_workspace_page(package.import_run_id, {}, view="health")
    assert status == 200
    assert "6 enterprise profiles require enrichment" in gaps
    assert "17 market participant concepts require enrichment or classification" in gaps
    assert "13 major-programme hypotheses require enrichment" in gaps
    assert "17 opportunity hypotheses require enrichment" in gaps
