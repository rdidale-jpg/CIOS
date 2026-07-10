import json

import pytest

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.enterprise_canvas import EnterpriseCanvasAccessError, EnterpriseCanvasService
from cios.applications.flora.memory.models import EnterpriseModel, EnterpriseModelAttribute, EnterpriseUnknown
from cios.applications.flora.memory.repository import EnterpriseModelRepository, EvidenceRepository
from tests.test_flora_blueprint_import_validation import pkg

HEADERS = {"X-Flora-User": "alice", "X-Flora-Enterprises": "synthetic-enterprise", "X-Flora-Roles": "package.review"}


def model(tmp_path):
    attrs = {
        "enterprise.name": EnterpriseModelAttribute("enterprise", "name", "Synthetic Health", 95, "2026-06-01", "current", ("obs-name",), ("ev-name",), "evidence-backed"),
        "enterprise.purpose": EnterpriseModelAttribute("enterprise", "purpose", "Improve care outcomes", 90, "2026-06-01", "current", ("obs-purpose",), ("ev-purpose",), "evidence-backed"),
        "enterprise.twin_version": EnterpriseModelAttribute("enterprise", "twin_version", "v1.2", 90, "2026-06-03", "current", ("obs-tv",), ("ev-tv",), "evidence-backed"),
        "enterprise.source_cut_off": EnterpriseModelAttribute("enterprise", "source_cut_off", "2026-06-30", 90, "2026-06-30", "current", ("obs-cut",), ("ev-cut",), "evidence-backed"),
        "enterprise.governing_thesis": EnterpriseModelAttribute("enterprise", "governing_thesis", "Care closer to home", 80, "2026-06-05", "current", ("obs-thesis",), ("ev-thesis",), "human-supplied"),
        "care_board.display_name": EnterpriseModelAttribute("organisation", "care_board.display_name", "Care Board", 95, "2026-06-10", "current", ("obs-board",), ("ev-board",), "evidence-backed"),
        "care_board.role": EnterpriseModelAttribute("organisation", "care_board.role", "Coordinates regional care delivery", 90, "2026-06-10", "current", ("obs-role",), ("ev-board",), "evidence-backed"),
        "care_board.accountable_role": EnterpriseModelAttribute("organisation", "care_board.accountable_role", "Chief Operating Officer", 80, "2026-06-10", "current", ("obs-owner",), ("ev-board",), "evidence-backed"),
        "care_board.current_state": EnterpriseModelAttribute("organisation", "care_board.current_state", "Operating with constrained workforce capacity", 85, "2026-06-15", "stale", ("obs-state",), ("ev-state",), "evidence-backed"),
        "care_board.material_change": EnterpriseModelAttribute("organisation", "care_board.material_change", "Demand shifted into community services", 80, "2026-06-15", "current", ("obs-change",), ("ev-change",), "evidence-backed", contradiction_state="supported", conflicting_observation_ids=("obs-conflict",)),
        "care_board.nested_twin_available": EnterpriseModelAttribute("organisation", "care_board.nested_twin_available", "true", 75, "2026-06-15", "current", ("obs-nested",), ("ev-nested",), "evidence-backed"),
    }
    unknowns = {"unk-1": EnterpriseUnknown("unk-1", "synthetic-enterprise", "Which workforce constraints are material?", "care_board")}
    EnterpriseModelRepository().save(EnterpriseModel("synthetic-enterprise", attrs, unknowns))
    EvidenceRepository().save({"evidence_id": "ev-board", "source_id": "src-board"})
    EvidenceRepository().save({"evidence_id": "ev-state", "source_id": "src-state"})


def stage_projections():
    content = pkg(records=[
        {"external_id":"pain-1","record_class":"pain_point","payload":{"statement":"Workforce pressure is affecting care access","effective_date":"2026-06-20","confidence":"medium","status":"accepted","supporting_record_refs":["obs-state"],"evidence_ids":["ev-state"]}},
        {"external_id":"resp-1","record_class":"current_response","payload":{"statement":"What Synthetic Health has done so far: expanded community triage","effective_date":"2026-06-21","status":"accepted"}},
        {"external_id":"resid-1","record_class":"residual_pain","payload":{"statement":"What remains unresolved: weekend capacity remains unclear","effective_date":"2026-06-22","status":"accepted"}},
    ])
    record = BlueprintPackageRegistry().receive(content, "synthetic.zip", "alice")
    BlueprintPackageValidator().validate_and_stage(record.package_ref, "alice", HEADERS)


def test_enterprise_canvas_read_model_foundation(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    model(tmp_path); stage_projections()
    canvas = EnterpriseCanvasService().get_canvas("synthetic-enterprise", HEADERS)
    again = EnterpriseCanvasService().get_canvas("synthetic-enterprise", HEADERS)

    assert canvas.read_only is True
    assert canvas.header.enterprise_name == "Synthetic Health"
    assert canvas.header.enterprise_purpose == "Improve care outcomes"
    assert canvas.header.twin_version == "v1.2"
    assert canvas.header.source_cut_off == "2026-06-30"
    assert canvas.header.freshness_warning == "Some evidence is stale"
    assert canvas.lens == "organisation"
    assert canvas.to_dict() == again.to_dict()
    tile = canvas.tiles[0]
    assert tile.tile_view_id == again.tiles[0].tile_view_id
    assert tile.display_name == "Care Board"
    assert tile.plain_english_role == "Coordinates regional care delivery"
    assert tile.accountable_role == "Chief Operating Officer"
    assert "care board.current state" in " ".join(tile.core_facts)
    assert tile.principal_pain_or_pressure == "Workforce pressure is affecting care access"
    assert tile.what_has_been_done_so_far.startswith("What Synthetic Health has done so far")
    assert tile.what_remains_unresolved.startswith("What remains unresolved")
    assert tile.unknown_indicator is True
    assert tile.contradiction_indicator is True
    assert tile.stale_evidence_indicator is True
    assert tile.nested_twin_available is True
    assert tile.analytical_projections[0].projection_type == "pain_point"
    assert tile.analytical_projections[0].package_or_twin_version == "1.0.0"
    assert any(ref.evidence_ids for ref in tile.lineage_references)
    assert not hasattr(__import__("cios.applications.flora.memory.models", fromlist=["PainPoint"]), "PainPoint")
    assert not hasattr(__import__("cios.applications.flora.memory.models", fromlist=["BurningPlatform"]), "BurningPlatform")
    assert not hasattr(__import__("cios.applications.flora.memory.models", fromlist=["TransformationPressure"]), "TransformationPressure")
    assert "MOD" not in json.dumps(canvas.to_dict())


def test_canvas_handles_incomplete_data_and_blocks_unauthorised_access(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    canvas = EnterpriseCanvasService().get_canvas("synthetic-enterprise", HEADERS)
    assert canvas.header.enterprise_name == "synthetic-enterprise"
    assert canvas.tiles == ()
    with pytest.raises(EnterpriseCanvasAccessError):
        EnterpriseCanvasService().get_canvas("synthetic-enterprise", {"X-Flora-User":"mallory","X-Flora-Enterprises":"other"})


def test_enterprise_canvas_organisation_experience_renders_human_usable_page(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    model(tmp_path); stage_projections()
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page

    html, status = enterprise_canvas_page("synthetic-enterprise", HEADERS)
    assert status == 200
    assert "Synthetic Health" in html
    assert "Improve care outcomes" in html
    assert "Twin version" in html
    assert "Source cut-off" in html
    assert "Organisation lens" in html
    assert "Care Board" in html
    assert "Coordinates regional care delivery" in html
    assert "Principal pain or pressure" in html
    assert "Unknown present" in html
    assert "Contradiction present" in html
    assert "Stale evidence" in html
    assert "Nested Twin available" in html
    assert "aria-label='Open Care Board organisation tile" in html
    assert "href='/digital-twins/synthetic-enterprise/canvas/tiles/canvas-tile-" in html
    assert "Select an organisation tile" in html
    assert "MOD" not in html
    assert "<form" not in html
    assert "method='post'" not in html


def test_enterprise_canvas_tile_detail_plain_language_and_lineage(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    model(tmp_path); stage_projections()
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page

    canvas = EnterpriseCanvasService().get_canvas("synthetic-enterprise", HEADERS)
    tile_id = canvas.tiles[0].tile_view_id
    html, status = enterprise_canvas_page("synthetic-enterprise", HEADERS, selected_tile_id=tile_id)
    assert status == 200
    for heading in [
        "What this area does",
        "Why it matters",
        "Core facts",
        "What has changed",
        "What is causing pressure",
        "What has been done so far",
        "What remains unresolved",
        "Stakeholders or accountable roles",
        "What we still do not know",
        "Evidence freshness",
        "Suggested next posture",
        "Inspect evidence",
    ]:
        assert heading in html
    assert "Workforce pressure is affecting care access" in html
    assert "expanded community triage" in html
    assert "weekend capacity remains unclear" in html
    assert "Source type/reference" in html
    assert "Evidence/date reference" in html
    assert "Close detail panel" in html
    assert "residual pain" not in html
    assert "analytical disposition" not in html
    assert "response-state maturity" not in html


def test_enterprise_canvas_ui_blocks_unauthorised_and_handles_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page

    denied_html, denied_status = enterprise_canvas_page("synthetic-enterprise", {"X-Flora-User":"mallory","X-Flora-Enterprises":"other"})
    assert denied_status == 403
    assert "Access denied" in denied_html
    assert "Care Board" not in denied_html

    empty_html, empty_status = enterprise_canvas_page("synthetic-enterprise", HEADERS)
    assert empty_status == 200
    assert "No organisation areas available" in empty_html
    assert "Select an organisation tile" in empty_html


def test_enterprise_canvas_lineage_inspection_read_only_accessible_and_complete(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    model(tmp_path); stage_projections()
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_lineage_page

    canvas = EnterpriseCanvasService().get_canvas("synthetic-enterprise", HEADERS)
    tile_id = canvas.tiles[0].tile_view_id
    html, status = enterprise_canvas_lineage_page("synthetic-enterprise", tile_id, HEADERS)
    assert status == 200
    for heading in [
        "Why Flora shows this",
        "What was observed",
        "Evidence supporting this",
        "Where the evidence came from",
        "What remains uncertain",
        "Conflicting evidence",
        "Original Blueprint location",
        "Missing or incomplete lineage",
        "Technical inspection references",
    ]:
        assert heading in html
    assert "Read-only lineage inspection" in html
    assert "Return to tile detail" in html
    assert "Supporting Evidence" in html
    assert "src-state" in html
    assert "bpi-pkg-" in html
    assert "records/sources.ndjson" in html
    assert "No human-supplied knowledge is linked" in html
    assert "Which workforce constraints are material?" in html
    assert "No canonical" not in html
    assert "Contribute governed feedback" in html


def test_enterprise_canvas_lineage_blocks_unauthorised_and_distinguishes_missing_from_error(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    model(tmp_path)
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_lineage_page

    canvas = EnterpriseCanvasService().get_canvas("synthetic-enterprise", HEADERS)
    tile_id = canvas.tiles[0].tile_view_id
    denied, denied_status = enterprise_canvas_lineage_page("synthetic-enterprise", tile_id, {"X-Flora-User":"mallory","X-Flora-Enterprises":"other"})
    assert denied_status == 403
    assert "Access denied" in denied
    assert "src-state" not in denied

    html, status = enterprise_canvas_lineage_page("synthetic-enterprise", tile_id, HEADERS)
    assert status == 200
    assert "No imported package location is available" in html
    assert "No Observation could be resolved" in html or "Observation reference" in html
    assert "Broken references" in html


def test_blueprint_owner_canvas_access_repair_preserves_workspace_enterprise_acl_and_link(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    from cios.applications.flora.blueprint_import.views import approve_and_promote, review_page, upload_and_validate_blueprint
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository, repair_blueprint_canvas_access
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page
    import re

    owner = {"X-Flora-User":"rob", "X-Flora-Enterprises":"cios-workspace", "X-Flora-Active-Workspace":"cios-workspace", "X-Flora-Roles":"cios_owner"}
    records=[{"external_id":"PP-MOD-1","record_class":"pain_point","truth_class":"analytical_projection","payload":{"statement":"MOD pressure is visible"}}]
    _, status, target = upload_and_validate_blueprint({"blueprint_zip":pkg(manifest_extra={"enterprise_id":"MOD", "package_id":"MOD-CDT-Blueprint", "package_version":"1.3"}, records=records)}, {"blueprint_zip.filename":"MOD-CDT-v1.3-Flora-Blueprint.zip","blueprint_zip.content_type":"application/zip"}, owner)
    assert status == 200
    run_id = target.rsplit("/", 1)[-1]
    review, review_status = review_page(run_id, owner)
    assert review_status == 200
    plan_id = re.search(r"name='plan_id' value='([^']+)'", review).group(1)
    done, done_status = approve_and_promote(run_id, {"plan_id":[plan_id],"confirm_plan":["yes"],"confirm_mutations":["yes"],"rationale":["owner approved"]}, owner)

    assert done_status == 200
    assert "/digital-twins/MOD/canvas" in done
    record = EnterpriseCanvasAccessRepository().get("MOD")
    assert record.canvas_id == "canvas-mod"
    assert record.enterprise_id == "MOD"
    assert record.workspace_id == "cios-workspace"
    assert record.owner_account == "rob"
    assert record.workspace_members == ("rob",)
    assert record.enterprise_members == ("rob",)
    assert [a for a in record.acl if a["principal_id"] == "rob"] == [{"principal_id":"rob", "role":"owner", "grant_source":"blueprint_promotion_owner"}]
    repair_blueprint_canvas_access(run_id, owner)
    repaired = EnterpriseCanvasAccessRepository().get("MOD")
    assert len([a for a in repaired.acl if a["principal_id"] == "rob"]) == 1
    assert len(EnterpriseCanvasAccessRepository().list()) == 1

    html, canvas_status = enterprise_canvas_page("MOD", owner)
    assert canvas_status == 200
    assert "MOD pressure is visible" in html
    denied, denied_status = enterprise_canvas_page("MOD", {"X-Flora-User":"mallory", "X-Flora-Enterprises":"cios-workspace", "X-Flora-Active-Workspace":"cios-workspace", "X-Flora-Roles":"reader"})
    assert denied_status == 403
    assert "MOD pressure is visible" not in denied


def test_existing_blueprint_canvas_is_repaired_not_duplicated_and_no_reimport_required(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page

    owner = {"X-Flora-User":"rob", "X-Flora-Enterprises":"cios-workspace", "X-Flora-Active-Workspace":"cios-workspace", "X-Flora-Roles":"cios_owner"}
    content = pkg(manifest_extra={"enterprise_id":"MOD", "package_id":"MOD-CDT-Blueprint", "package_version":"1.3"}, records=[{"external_id":"PP-MOD-2","record_class":"pain_point","truth_class":"analytical_projection","payload":{"statement":"Existing import data remains visible"}}])
    package = BlueprintPackageRegistry().receive(content, "MOD-CDT-v1.3-Flora-Blueprint.zip", "rob", "cios-workspace")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "rob", owner)
    assert EnterpriseCanvasAccessRepository().list() == []

    html, status = enterprise_canvas_page("MOD", owner)
    assert status == 200
    assert "Existing import data remains visible" in html
    records = EnterpriseCanvasAccessRepository().list()
    assert len(records) == 1
    assert records[0].import_run_ids == (package.import_run_id,)
    assert len(BlueprintPackageRegistry().list()) == 1
