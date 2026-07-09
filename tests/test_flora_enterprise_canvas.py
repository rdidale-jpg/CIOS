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
