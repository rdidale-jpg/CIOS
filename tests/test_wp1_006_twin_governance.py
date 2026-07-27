from __future__ import annotations

from pathlib import Path

from cios.applications.flora.blueprint_import.archive import inspect_zip_inventory
from cios.applications.flora.blueprint_import.models import BlueprintPackageIdentity, BlueprintPackageRecord
from cios.applications.flora.blueprint_import.package_contracts import PackageContractDetector
from cios.applications.flora.blueprint_import.twin_governance import (
    DownstreamReconciliationRepository, TwinDependencyService, assess_impacts,
    governed_semantics, project_twin_identity,
)
from cios.applications.flora.blueprint_import.views import _business_category, _commercial_change_summary, _executive_summary, _identity_resolution_section
from cios.applications.flora.storage import atomic_write_json, data_path


FIXTURE = Path(__file__).parents[1] / "enterprise-knowledge" / "TMS-001_High_Fidelity_Industry_Twin_Upgrade.zip"


def package(package_id: str, run_id: str, inspection: dict, checksum: str = "a" * 64) -> BlueprintPackageRecord:
    return BlueprintPackageRecord("1.0", f"pkg-{package_id}", BlueprintPackageIdentity(package_id, "1.0", package_id, "1.0"),
        checksum, 1, "fixture.zip", "archive", (), "received", "now", "alice", run_id, package_inspection=inspection)


def test_tms_identity_is_explicit_and_business_categories_use_governed_semantics():
    content = FIXTURE.read_bytes()
    inspection = PackageContractDetector().detect(content, inspect_zip_inventory(content)).to_dict()
    tms = package("TMS-001", "run-tms", inspection)
    identity = project_twin_identity(tms)
    assert identity.status == "recognised"
    assert identity.twin_type == "industry"
    assert identity.primary_subject_id == "IND-TMS-001"
    assert identity.primary_subject_name == "Telecommunications, Media and Sport Industry Twin"
    assert identity.primary_subject_class == "industry"
    assert identity.canonical_owner == "IND-TMS-001"
    assert "telecommunications" in identity.governed_scope
    html = _identity_resolution_section(tms)
    for text in ("Primary subject", "Governed scope", "Canonical owner", "Unresolved", "Industry"):
        assert text in html
    candidates = [
        {"candidate_object_class": "entity", "payload": {"object_type": "enterprise"}, "validation_status": "accepted"},
        {"candidate_object_class": "entity", "payload": {"object_type": "market_participant", "role": "supplier"}, "validation_status": "accepted"},
        {"candidate_object_class": "entity", "payload": {"name": "Opportunity-shaped label"}, "validation_status": "accepted"},
    ]
    assert [_business_category(row) for row in candidates] == ["Enterprises", "Market Participants", "Classification unavailable"]
    assert governed_semantics(candidates[1]) == {"canonical_identity_type": "market_participant", "commercial_roles": ["supplier"], "package_role": None, "projection_role": None}
    summary = _commercial_change_summary(candidates, inspection)
    assert "Commercial Intelligence" in summary
    assert "Governance Intelligence" in summary
    assert "13</div><strong>Market Participants" in summary
    assert "9</div><strong>Opportunities" in summary
    assert "16</div><strong>Capabilities &amp; Offers" in summary


def test_enterprise_supplier_role_is_not_a_supplier_twin_and_ambiguous_identity_stays_ambiguous():
    enterprise = package("ENT-GENIUS", "run-genius", {"contract_type": "Blueprint Package", "twin_type": "enterprise",
        "primary_subject_id": "ENT-GENIUS", "primary_subject_name": "Genius Sports", "primary_subject_class": "enterprise",
        "governed_scope": "enterprise intelligence", "canonical_owner": "ENT-GENIUS", "package_version": "2"})
    identity = project_twin_identity(enterprise)
    assert identity.status == "recognised" and identity.twin_type == "enterprise"
    semantics = governed_semantics({"payload": {"object_type": "enterprise", "roles": ["supplier", "partner"]}})
    assert semantics["canonical_identity_type"] == "enterprise"
    assert semantics["commercial_roles"] == ["supplier", "partner"]
    ambiguous = package("UNKNOWN", "run-unknown", {"contract_type": "Blueprint Package"})
    assert project_twin_identity(ambiguous).status == "ambiguous"


def test_stable_id_dependency_creates_idempotent_review_without_dependent_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    source = package("ENT-GENIUS", "run-source", {"contract_type": "Blueprint Package", "twin_type": "enterprise",
        "primary_subject_id": "ENT-GENIUS", "primary_subject_name": "Genius Sports", "primary_subject_class": "enterprise",
        "governed_scope": "enterprise intelligence", "canonical_owner": "ENT-GENIUS"})
    dependent = package("TMS-001", "run-dependent", {"twin_type": "industry", "primary_subject_id": "IND-TMS-001",
        "primary_subject_name": "UK TMS", "primary_subject_class": "industry", "governed_scope": "UK TMS", "canonical_owner": "IND-TMS-001"}, "b" * 64)
    atomic_write_json(data_path("blueprint_import", "lifecycle", "run-dependent.json"), {"import_run_id": "run-dependent", "state": "promoted"})
    monkeypatch.setattr("cios.applications.flora.blueprint_import.twin_governance.BlueprintPackageRegistry.list", lambda self: [source, dependent])
    source_rows = [{"candidate_object_class": "fact"}, {"candidate_object_class": "relationship"}, {"candidate_object_class": "unknown"}, {"candidate_object_class": "contradiction"}]
    dependent_rows = [{"candidate_record_id": "projection-1", "payload": {"canonical_id": "ENT-GENIUS", "name": "A different display name"}}]
    monkeypatch.setattr("cios.applications.flora.blueprint_import.twin_governance.CandidateStagingRepository.list_candidates", lambda self, run: source_rows if run == "run-source" else dependent_rows)
    dependencies = TwinDependencyService().discover(source)
    assert len(dependencies) == 1 and dependencies[0]["confidence"] == "confirmed"
    impacts = assess_impacts(source, dependencies)
    before = dependent.to_dict()
    repo = DownstreamReconciliationRepository()
    first = repo.create_pending(source, "2", impacts, "alice")
    second = repo.create_pending(source, "2", impacts, "alice")
    assert first == second and len(repo.list_for_source("ENT-GENIUS")) == 1
    assert first[0]["unknowns"] == first[0]["contradictions"] == 1
    assert first[0]["dependent_twin_mutated"] is False
    assert dependent.to_dict() == before

    # A name-only candidate is deliberately insufficient.
    monkeypatch.setattr("cios.applications.flora.blueprint_import.twin_governance.CandidateStagingRepository.list_candidates", lambda self, run: source_rows if run == "run-source" else [{"payload": {"name": "Genius Sports"}}])
    assert TwinDependencyService().discover(source) == []
