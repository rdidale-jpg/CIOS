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
            result.records_quarantined, result.records_rejected) == (1060, 648, 0, 0)
    assert result.canonical_mutations == 0
    assert Counter(candidate["validation_status"] for candidate in candidates) == {
        "accepted": 648, "ignored": 412,
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
        "ai_reinvention_assessment": 7,
    }
    assert not [candidate for candidate in candidates if candidate["validation_status"] == "quarantined"]
    twin = assemble_semantic_twin([candidate for candidate in candidates
                                   if candidate["validation_status"] == "accepted"])
    assert len(twin.objects) == 648
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
    assert len(accepted) == 648
    assert len({candidate["candidate_record_id"] for candidate in governed}) == 1060

    twin_map, status = executive_workspace_page(package.import_run_id, {}, view="workspace")
    assert status == 200
    for inventory in (
        "1 factual profile imported",
        "6 enterprise dossiers imported",
        "17 market participants imported",
        "13 programme records imported",
        "17 opportunities imported",
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
    assert "<tr><th>Quarantined (final staging disposition)</th><td>0</td></tr>" in review
    assert "<tr><th>Accepted canonical candidates</th><td>648</td></tr>" in review
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
    assert "Other Twin content — 507 total" in other
    assert "Residual reason:" in other
    assert "no canonical semantic role" in other
    gaps, gaps_status = executive_workspace_page(package.import_run_id, {}, view="health")
    assert gaps_status == 200
    assert "92 Evidence · 30 Unknowns · 11 Contradictions" in gaps

    # 648 projected + 412 lineage-only = all 1,060; only the
    # accepted projection is visible, and validation never promotes it.
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    assert Counter(c["validation_status"] for c in summary["candidates"]) == {
        "accepted": 648, "ignored": 412,
    }
    accepted_twin = assemble_semantic_twin([c for c in summary["candidates"] if c["validation_status"] == "accepted"])
    accepted_collections = business_collections(accepted_twin)
    assert sum(len(collection.objects) for collection in accepted_collections) == 648
    assert sum(collection.key == "other" and len(collection.objects) or 0
               for collection in accepted_collections) == 95


def test_tel001_researcher_fields_reach_canonical_owner_shapes_losslessly(monkeypatch, tmp_path):
    """The profile adapter maps semantics, retains lineage, and never promotes."""
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    package = BlueprintPackageRegistry().receive(EVIDENCE.read_bytes(), EVIDENCE.name, "regression-auditor")
    result = BlueprintPackageValidator().validate_and_stage(package.package_ref, "regression-auditor")
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    rows = summary["candidates"]
    accepted = [row for row in rows if row["validation_status"] == "accepted"]
    by_kind = {kind: [row for row in accepted if row["candidate_object_class"] == kind] for kind in {
        "industry_twin", "enterprise_twin", "market_participant_twin", "transformation_programme",
        "opportunity_hypothesis", "ai_reinvention_assessment", "evidence", "unknown", "contradiction",
        "relationship", "membership"}}

    assert result.canonical_mutations == 0
    assert len(by_kind["ai_reinvention_assessment"]) == 7
    industry = by_kind["industry_twin"][0]["payload"]
    assert industry["description"] and industry["industry_profile"]["economics"]
    enterprise = by_kind["enterprise_twin"][0]["payload"]
    assert all(enterprise[field] for field in ("description", "strategy", "operating_structure", "financial_context", "technology", "transformation_posture"))
    participant = by_kind["market_participant_twin"][0]["payload"]
    assert participant["role"] and participant["domain"] and participant["significance"] and participant["evidence_refs"]
    programme = by_kind["transformation_programme"][0]["payload"]
    assert all(programme[field] for field in ("title", "owner", "business_unit", "objective", "phase", "timing", "evidence_refs"))
    opportunity = by_kind["opportunity_hypothesis"][0]["payload"]
    assert all(opportunity[field] for field in ("title", "client_problem", "business_unit", "procurement_status", "procurement_timing", "value_range", "commercial_type", "value_type", "evidence_refs"))
    assert len(by_kind["opportunity_hypothesis"]) == 17

    # Every transformed record carries the untouched source and an explicit
    # reconciliation, including fields not consumed by the stable vocabulary.
    for family in by_kind.values():
        for row in family:
            payload = row["payload"]
            assert payload["source_payload"]
            assert {"source_fields", "mapped_fields", "unmapped_fields"} <= set(payload["mapping_diagnostics"])
            assert payload["mapping_diagnostics"]["contract_id"] == "TOP-RESEARCHER-PORTABLE-OBJECTS-v1"
            assert set(payload["mapping_diagnostics"]["source_fields"]) == set(payload["source_payload"])

    twin = assemble_semantic_twin(accepted)
    objects = {obj.original_id: obj for obj in twin.objects}
    for kind in ("enterprise_twin", "market_participant_twin", "transformation_programme", "opportunity_hypothesis", "ai_reinvention_assessment"):
        for obj in twin.of_kind(kind):
            assert obj.evidence_refs
            assert all(ref in objects for ref in obj.evidence_refs)
    for obj in twin.of_kind("relationship") + twin.of_kind("membership"):
        assert len(obj.references) >= 2
    runtime_twin = assemble_semantic_twin(summary["candidates"])
    assert sum(len(collection.objects) for collection in business_collections(runtime_twin)) == 1060
    assert summary["canonical_mutations"] == 0
    assert not (tmp_path / "memory").exists()


def test_tel001_full_ui_service_path_projects_substantive_canonical_fields(monkeypatch, tmp_path):
    """The immutable ZIP must reach the actual deployed explorer page models."""
    from cios.applications.flora.blueprint_import.views import upload_and_validate_blueprint
    from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
    from cios.applications.flora.blueprint_import.semantic_twin import executive_record_view_model

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    monkeypatch.delenv("FLORA_PILOT_AUTO_SIGN_IN", raising=False)

    _, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": EVIDENCE.read_bytes()},
        {"blueprint_zip.filename": EVIDENCE.name,
         "blueprint_zip.content_type": "application/zip", "expected_type": "mixed"}, {},
    )
    assert status == 200
    run_id = target.rsplit("/", 1)[-1]
    summary = BlueprintPackageValidator().staging_summary(run_id)
    accepted = [row for row in summary["candidates"] if row["validation_status"] == "accepted"]
    twin = assemble_semantic_twin(accepted)

    # This is the view-model constructor used by the deployed explorer, not a
    # synthetic canonical object assembled by the test.
    models = [executive_record_view_model(obj) for obj in twin.objects]
    assert Counter(model.kind for model in models) >= Counter({
        "industry_twin": 1, "enterprise_twin": 6, "market_participant_twin": 17,
        "transformation_programme": 13, "opportunity_hypothesis": 17,
        "ai_reinvention_assessment": 7,
    })
    for kind in ("industry_twin", "enterprise_twin", "market_participant_twin",
                 "transformation_programme", "opportunity_hypothesis", "ai_reinvention_assessment"):
        assert all(model.fields for model in models if model.kind == kind)

    expected = {
        "industry-overview": ("£34.7bn, down £0.3bn / 0.8% year-on-year", "Commercial Implications"),
        "enterprises": ("BT Group is a UK-headquartered telecommunications group", "FTTP build and take-up"),
        "market-participants": ("Telecoms access, spectrum, complaints and infrastructure reporting", "Regulator"),
        "transformation-programmes": ("BT FY30 cost and operating-model transformation", "FY26-FY30"),
        "opportunities": ("Virgin Media O2", "Shaping opportunity"),
        "reinvention-assessments": ("Capital-intensive, regulated network operators", "2026-2028"),
    }
    rendered = {}
    for collection, values in expected.items():
        page, page_status = executive_workspace_page(run_id, {}, view="explore", collection=collection)
        assert page_status == 200
        assert all(value in page for value in values), (collection, [value for value in values if value not in page])
        rendered[collection] = page
    assert "Client problem not established" not in rendered["opportunities"]
    assert "Supporting context; not presented as an executive insight" not in rendered["industry-overview"]

    counts = Counter(obj.kind for obj in twin.objects)
    assert (counts["opportunity_hypothesis"], counts["evidence"], counts["unknown"],
            counts["contradiction"], counts["ai_reinvention_assessment"]) == (17, 92, 30, 11, 7)
    assert summary["canonical_mutations"] == 0
    assert not (tmp_path / "memory").exists()


def test_tel001_deployed_aspect_and_dossier_routes_render_pending_candidate_fields(monkeypatch, tmp_path):
    """Actual HTTP page projections must not hide supplied candidate fields while owner assessment is pending."""
    from cios.applications.flora.blueprint_import.views import upload_and_validate_blueprint
    from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    monkeypatch.delenv("FLORA_PILOT_AUTO_SIGN_IN", raising=False)

    _, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": EVIDENCE.read_bytes()},
        {"blueprint_zip.filename": EVIDENCE.name,
         "blueprint_zip.content_type": "application/zip", "expected_type": "mixed"}, {},
    )
    assert status == 200
    run_id = target.rsplit("/", 1)[-1]

    expected = {
        "industry-overview": ("£34.7bn, down £0.3bn / 0.8% year-on-year", "Commercial Implications"),
        "market-participants": ("Telecoms access, spectrum, complaints and infrastructure reporting", "Regulator"),
        "major-programmes": ("BT FY30 cost and operating-model transformation", "FY26-FY30"),
        "opportunities": ("Virgin Media O2", "Shaping opportunity"),
        "reinvention-timing": ("Capital-intensive, regulated network operators", "2026-2028"),
    }
    for collection, values in expected.items():
        page, page_status = executive_workspace_page(run_id, {}, view="aspect", collection=collection)
        assert page_status == 200
        assert "pending governance" not in page.casefold()
        assert all(value in page for value in values), (collection, [value for value in values if value not in page])
        assert "{'" not in page and "[{'" not in page

    enterprise_index, index_status = executive_workspace_page(run_id, {}, view="aspect", collection="enterprises")
    assert index_status == 200
    assert enterprise_index.count("class='enterprise-card'") == 6
    assert "BT Group is a UK-headquartered telecommunications group" in enterprise_index
    assert "FTTP build and take-up" in enterprise_index
    assert "not supplied" not in enterprise_index.casefold()

    bt_page, bt_status = executive_workspace_page(run_id, {}, view="enterprise", enterprise_id="ent-bt")
    assert bt_status == 200
    for value in (
        "BT Group is a UK-headquartered telecommunications group",
        "FTTP build and take-up",
        "Openreach FTTP",
        "EV-BT-FY26",
    ):
        assert value in bt_page
    assert "governance review pending" not in bt_page.casefold()

    gaps, gaps_status = executive_workspace_page(run_id, {}, view="health")
    assert gaps_status == 200
    assert "What Flora already has" in gaps and "What remains incomplete" in gaps
    assert "Find organisation description" not in gaps


def test_tel001_imported_twin_observation_builder_generalises_supported_families(monkeypatch, tmp_path):
    """Industry, enterprise and programme records use the same candidate Observation runtime."""
    from cios.applications.flora.blueprint_import.observation_runtime import build_candidate_observation, OBSERVATION_BUILDER_NAME
    from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", "1")
    package = BlueprintPackageRegistry().receive(EVIDENCE.read_bytes(), EVIDENCE.name, "regression-auditor")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "regression-auditor")
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    twin = assemble_semantic_twin([candidate for candidate in summary["candidates"] if candidate["validation_status"] == "accepted"])

    industry = next(obj for obj in twin.objects if obj.original_id == "IND-UK-TELECOMS")
    bt = next(obj for obj in twin.objects if obj.original_id == "ENT-BT")
    programme = next(obj for obj in twin.objects if obj.kind == "transformation_programme" and obj.evidence_refs)

    built = [build_candidate_observation(obj) for obj in (industry, bt, programme)]
    assert [reason for _observation, reason, _detail in built] == ["observation_generated"] * 3
    observations = [observation for observation, _reason, _detail in built]
    assert all(observation and observation.builder == OBSERVATION_BUILDER_NAME for observation in observations)
    assert observations[0].originating_object == "IND-UK-TELECOMS"
    assert observations[0].originating_fields == ("industry_profile",)
    assert "£34.7bn" in observations[0].statement
    assert observations[1].originating_object == "ENT-BT"
    assert observations[1].originating_fields == ("description",)
    assert "BT Group is a UK-headquartered telecommunications group" in observations[1].statement
    assert observations[2].originating_fields == ("objective",)
    assert observations[2].evidence_refs

    advanced, status = executive_workspace_page(package.import_run_id, {"X-Flora-User": "regression-auditor", "X-Flora-Enterprises": "TEL-001", "X-Flora-Active-Workspace": "TEL-001", "X-Flora-Roles": "blueprint_import_admin,package.review"}, view="diagnostics")
    assert status == 200
    for expected in ("ImportedTwinSemanticObservationBuilder", "generated statement", "evidence count", "Observation persistence"):
        assert expected in advanced
    assert "Canonical Factual Projection" in advanced and "sections projected" in advanced
    assert "runtime fingerprint" in advanced and "Projected fields" in advanced and "Rendered fields" in advanced
    assert "Omitted fields" in advanced and "exact omission reason" in advanced
    assert "fields projected 0" not in advanced and "projection result omitted" not in advanced
    assert "IND-UK-TELECOMS" in advanced and "ENT-BT" in advanced and "observation_generated" in advanced


def test_tel001_canonical_factual_projection_exposes_shared_contract_metadata(monkeypatch, tmp_path):
    from cios.applications.flora.blueprint_import.canonical_factual_projection import factual_projection_for_object

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    package = BlueprintPackageRegistry().receive(EVIDENCE.read_bytes(), EVIDENCE.name, "regression-auditor")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "regression-auditor")
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    twin = assemble_semantic_twin([candidate for candidate in summary["candidates"] if candidate["validation_status"] == "accepted"])
    bt = next(obj for obj in twin.objects if obj.original_id == "ENT-BT")
    projection = factual_projection_for_object(bt, "Enterprise Dossier")

    assert projection.object_id
    assert projection.family == "Enterprise Dossier"
    assert projection.evidence_refs
    assert projection.source_lineage
    assert projection.candidate_state == "candidate"
    assert projection.completeness_state == "owner_assessment_pending"
    assert projection.projection_version == "canonical-factual-projection-v2"
    assert "cfp=canonical-factual-projection-v2" in projection.runtime_fingerprint
    assert "adapter=mod-cdt-twin-spine-mapping-v1.3.4" in projection.runtime_fingerprint
    assert any("BT Group is a UK-headquartered telecommunications group" in value for section in projection.sections for value in section.values)


def test_tel001_enterprise_association_correction_is_visible_on_import_screen(monkeypatch):
    """The consumer correction and functional-test decision are operationally visible."""
    from cios.applications.flora.blueprint_import.views import import_blueprint_entry_page
    from cios.applications.flora.blueprint_import import pilot_change

    change_id = "TEL-001-ENTERPRISE-ASSOCIATION-CONSUMER-CORRECTION-2026-08-14"
    monkeypatch.setattr(pilot_change, "deployment_metadata", lambda: {
        "deployed_change_marker": change_id,
        "branch": "Unavailable — deployment metadata not configured",
        "build_timestamp": "Unavailable — deployment metadata not configured",
    })

    html, status = import_blueprint_entry_page({})

    assert status == 200
    assert "Enterprise Association Consumer Correction" in html
    assert "Make Enterprise dossiers consume the candidate Programme and Opportunity relationships" in html
    assert "PROG-BT-VERIZON-JV remains absent" in html
    assert "OPP-BT-VERIZON-JV-INTEGRATION appears" in html
    assert "Ready for functional test — deployment metadata incomplete" in html
    assert "Should I test now?" in html and ">YES<" in html
    assert "Known limitation: Deployment metadata incomplete" in html


def test_tel001_relationship_truth_report_reconciles_governed_source_records():
    report = Path("docs/operations/flora/TEL-001-Relationship-Truth-Report.md").read_text()
    executive = Path("docs/operations/flora/TEL-001-Relationship-Truth-Executive-Summary.md").read_text()

    complete_register = report.split("## Complete Relationship register (308 records)", 1)[1]
    relationship_rows = [line for line in complete_register.splitlines() if line.startswith("| `REL-")]
    membership_section = report.split("## Membership audit (50 records)", 1)[1].split("## Runtime comparison", 1)[0]
    membership_rows = [line for line in membership_section.splitlines() if line.startswith("| `MEM-")]

    assert len(relationship_rows) == 308
    assert len(membership_rows) == 50
    assert "**Reconciled total: 308 Relationship records.**" in report
    for enterprise in ("BT Group", "CityFibre", "Openreach", "TalkTalk", "Virgin Media O2", "VodafoneThree"):
        assert f"**{enterprise}: FLORA DEFECT**" in executive
    assert "**Both**" in executive
    assert "no Relationship record has it as source or target" in executive
