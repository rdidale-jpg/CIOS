"""Regression proof for the immutable TEL-001 Import Twin evidence package."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, business_collections


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
            result.records_quarantined, result.records_rejected) == (1060, 641, 7, 0)
    assert result.canonical_mutations == 0
    assert Counter(candidate["validation_status"] for candidate in candidates) == {
        "accepted": 641, "ignored": 412, "quarantined": 7,
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
        "relationship": 308,
        "membership": 50,
        "refresh_trigger": 95,
        "release_manifest": 1,
    }
    assert Counter(candidate["candidate_object_class"] for candidate in candidates
                   if candidate["validation_status"] == "quarantined") == {
        "transformation_pressure_view": 7,
    }
    twin = assemble_semantic_twin([candidate for candidate in candidates
                                   if candidate["validation_status"] == "accepted"])
    assert len(twin.objects) == 641
    assert len(twin.enterprises) == 6
    collections = {collection.key: len(collection.objects) for collection in business_collections(twin, include_empty=True)}
    expected_collections = {
        "industry-overview": 1, "enterprises": 6, "opportunities": 17,
        "evidence-sources": 92, "unknowns": 30, "contradictions": 11,
        "memberships": 50, "release-manifests": 1,
    }
    assert {key: collections[key] for key in expected_collections} == expected_collections
    assert collections["other"] == 95  # monitoring triggers are genuinely residual
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
    assert len(accepted) == 641
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


def test_exact_tel001_pilot_import_reaches_candidate_governance_review(monkeypatch, tmp_path):
    """The immutable reported package opens review without adding promotion authority."""
    from cios.applications.flora.blueprint_import import review_plan
    from cios.applications.flora.blueprint_import.promotion import can_approve_blueprint_promotion
    from cios.applications.flora.blueprint_import.views import review_page, upload_and_validate_blueprint

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    monkeypatch.delenv("FLORA_PILOT_AUTO_SIGN_IN", raising=False)
    monkeypatch.setattr(review_plan, "ASYNC_THRESHOLD", 2000)

    _, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": EVIDENCE.read_bytes()},
        {"blueprint_zip.filename": EVIDENCE.name, "blueprint_zip.content_type": "application/zip", "expected_type": "mixed"},
        {},
    )
    assert status == 200
    review, review_status = review_page(target.rsplit("/", 1)[-1], {})

    assert review_status == 200
    assert "You are not authorised to review" not in review
    assert "Review Blueprint proposed changes" in review
    assert "industry_twin" in review
    assert "Accepted" in review and "Quarantined" in review
    # Identity is genuinely absent from the producer contract: record content
    # may describe telecoms, but must not silently become governance authority.
    assert "Primary subject</th><td>Unresolved" in review
    assert "Governed scope</th><td>Unresolved" in review
    assert "Canonical owner</th><td>Unresolved" in review
    assert "Confirm the proposed Twin identity, primary subject, governed scope and canonical owner" in review
    # Final staging quarantine is seven explicit records, not the 1,060 items
    # provisionally withheld from promotion while identity remains unresolved.
    assert "<tr><th>Quarantined (final staging disposition)</th><td>7</td></tr>" in review
    assert "<tr><th>Accepted canonical candidates</th><td>641</td></tr>" in review
    assert "Promotion permission required" in review
    assert not can_approve_blueprint_promotion({}, "TEL-001")
    assert not (tmp_path / "memory").exists()


def test_duplicate_tel001_upload_restages_persisted_candidates_for_deployed_ui(monkeypatch, tmp_path):
    """A checksum-deduplicated upload must not reuse a pre-semantic staging run."""
    from cios.applications.flora.blueprint_import.candidates import CandidateImportRecord, CandidateStagingRepository
    from cios.applications.flora.blueprint_import.ledger import utc_now
    from cios.applications.flora.blueprint_import.views import upload_and_validate_blueprint
    from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
    from cios.applications.flora.storage import atomic_write_json

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    package = BlueprintPackageRegistry().receive(EVIDENCE.read_bytes(), EVIDENCE.name, "regression-auditor")
    staging = CandidateStagingRepository()
    # Reproduce the representation left by the deployed pre-fix import.  The
    # registry deliberately returns this same run for an identical checksum.
    for index in range(1060):
        staging.save_candidate(CandidateImportRecord(
            "1.0", f"legacy-{index:04d}", package.package_ref, package.package_sha256,
            "record_sets/legacy.ndjson", "", {"line": index + 1}, f"legacy-{index}",
            "unclassified", "unknown", {"id": f"legacy-{index}"}, "accepted", (),
            f"legacy-fingerprint-{index}", utc_now(), package.import_run_id,
        ))
    atomic_write_json(staging.root_for(package.import_run_id) / "summary.json", {
        "mapping_version": "mod-cdt-twin-spine-mapping-v1.3.3",
        "candidate_records_staged": 1060,
        "execution_trace": [{"status": "Passed"}],
    })

    _, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": EVIDENCE.read_bytes()},
        {"blueprint_zip.filename": EVIDENCE.name, "blueprint_zip.content_type": "application/zip",
         "expected_type": "mixed"}, {},
    )
    assert status == 200
    assert target == f"/blueprint-import/{package.import_run_id}"

    persisted = staging.list_candidates(package.import_run_id)
    assert len(persisted) == 1060
    assert not any(candidate["candidate_record_id"].startswith("legacy-") for candidate in persisted)
    assert Counter(candidate["candidate_object_class"] for candidate in persisted) >= Counter({
        "industry_twin": 1, "enterprise_twin": 6, "market_participant_twin": 17,
        "transformation_programme": 13, "opportunity_hypothesis": 17,
        "evidence": 92, "unknown": 30, "contradiction": 11,
    })
    assert all("candidate_object_class" in candidate for candidate in persisted)
    assert all("record_class" not in candidate.get("payload", {}) for candidate in persisted
               if candidate["candidate_object_class"] in {"industry_twin", "enterprise_twin", "evidence"})

    collection_counts = {
        "industry-overview": 1, "enterprises": 6, "market-participants": 17,
        "transformation-programmes": 13, "opportunities": 17,
        "evidence-sources": 92, "unknowns": 30, "contradictions": 11,
    }
    for key, count in collection_counts.items():
        page, page_status = executive_workspace_page(package.import_run_id, {}, view="explore", collection=key)
        assert page_status == 200
        assert f"{count} total" in page
    other, other_status = executive_workspace_page(package.import_run_id, {}, view="explore", collection="other")
    assert other_status == 200
    assert "Other Twin content — 514 total" in other
    assert "Residual reason:" in other
    assert "no canonical semantic role" in other
    gaps, gaps_status = executive_workspace_page(package.import_run_id, {}, view="health")
    assert gaps_status == 200
    assert "92 Evidence · 30 Unknowns · 11 Contradictions" in gaps

    # 641 projected + 7 quarantined + 412 lineage-only = all 1,060; only the
    # accepted projection is visible, and validation never promotes it.
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    assert Counter(c["validation_status"] for c in summary["candidates"]) == {
        "accepted": 641, "ignored": 412, "quarantined": 7,
    }
    accepted_twin = assemble_semantic_twin([c for c in summary["candidates"] if c["validation_status"] == "accepted"])
    accepted_collections = business_collections(accepted_twin)
    assert sum(len(collection.objects) for collection in accepted_collections) == 641
    assert sum(collection.key == "other" and len(collection.objects) or 0
               for collection in accepted_collections) == 95
    runtime_twin = assemble_semantic_twin(summary["candidates"])
    assert sum(len(collection.objects) for collection in business_collections(runtime_twin)) == 1060
    assert summary["canonical_mutations"] == 0
    assert not (tmp_path / "memory").exists()
