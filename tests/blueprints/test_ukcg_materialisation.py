from __future__ import annotations

import json, zipfile
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from tools.blueprints.materialise_ukcg import HANDOVER, materialise
import importlib.util
_BUILDER = Path(__file__).resolve().parents[2] / "tools/knowledge-packs/build_uk_government_blueprint_package.py"
_spec = importlib.util.spec_from_file_location("ukcg_builder", _BUILDER)
ukcg_builder = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(ukcg_builder)
build = ukcg_builder.build
sha256 = ukcg_builder.sha256


def test_ukcg_source_to_twin_spine_mapping_preserves_governed_controls(monkeypatch, tmp_path):
    asset_dir = tmp_path / "assets"
    materialise(asset_dir)
    zip_path = build(asset_dir, tmp_path / "dist")
    with zipfile.ZipFile(zip_path) as zf:
        assert "blueprint_manifest.json" in zf.namelist()
        manifest = json.loads(zf.read("blueprint_manifest.json"))
        assert manifest["final_twin_spine_workbook"] == "twin_spine/UKCG-CDT-01-Twin-Spine-v1.0.xlsx"
        declared = {f["path"]: f["sha256"] for f in manifest["files"]}
        assert all((asset_dir / p).exists() and sha256(asset_dir / p) == h for p, h in declared.items())
        assert declared[manifest["final_twin_spine_workbook"]] == sha256(asset_dir / manifest["final_twin_spine_workbook"])
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path / "flora"))
    receipt = BlueprintPackageRegistry().receive(zip_path.read_bytes(), zip_path.name, "tester")
    result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "tester")
    assert result.candidate_records_staged == 152
    assert result.records_accepted_into_staging == 116
    assert result.records_quarantined == 36
    assert result.canonical_mutations == 0
    summary = BlueprintPackageValidator().staging_summary(receipt.import_run_id)
    candidates = summary["candidates"]
    by_source = {c["original_source_id"]: c for c in candidates}
    handover_text = HANDOVER.read_text(encoding="utf-8")
    for stable_id in ["EVID-UKCG-SRC-001", "OBS-UKCG-001", "UNK-UKCG-001", "CON-UKCG-001"]:
        assert stable_id in handover_text
        assert stable_id in by_source
    assert by_source["EVID-UKCG-SRC-001"]["payload"]["status"] == "Candidate"
    assert by_source["OBS-UKCG-001"]["payload"]["confidence"] == "Medium-High"
    assert by_source["OBS-UKCG-001"]["payload"]["lineage_resolution"][0]["resolved_staged_candidate"]
    assert by_source["UNK-UKCG-001"]["candidate_object_class"] == "unknown"
    assert by_source["CON-UKCG-001"]["candidate_object_class"] == "contradiction"
    assert by_source["NC-UKCG-004"]["payload"]["status"] == "explicit_non_claim"
    assert by_source["VH-UKCG-254"]["payload"]["status"] == "validation_hold"
    assert by_source["VH-UKCG-255"]["payload"]["status"] == "validation_hold"
    quarantined = [c for c in candidates if c["validation_status"] == "quarantined"]
    assert len(quarantined) == 36
    assert {c["candidate_object_class"] for c in quarantined} == {"pain_point"}
    assert all(any(f["code"] == "projection_only" for f in c["validation_findings"]) for c in quarantined)
    assert all(c["canonical_mutation_count"] == 0 for c in candidates)
