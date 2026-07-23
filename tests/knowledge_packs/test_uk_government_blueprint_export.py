from __future__ import annotations

import json
import zipfile

import pytest

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
import importlib.util
from pathlib import Path

_BUILDER = Path(__file__).resolve().parents[2] / "tools" / "knowledge-packs" / "build_uk_government_blueprint_package.py"
_SPEC = importlib.util.spec_from_file_location("ukgov_blueprint_builder", _BUILDER)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build = _MODULE.build
from tests.test_flora_blueprint_import_validation import xlsx_workbook


def write_required_assets(root):
    workbook = xlsx_workbook([
        ("03_Sources", "rIdSrc", "worksheets/sheet1.xml", [["source_id", "title"], ["SRC-UKCG-1", "Synthetic source"]]),
        ("04A_Evidence", "rIdEv", "worksheets/sheet2.xml", [["evidence_id", "source_id", "summary"], ["EVD-UKCG-1", "SRC-UKCG-1", "Synthetic evidence"]]),
        ("05_Observations", "rIdObs", "worksheets/sheet3.xml", [["observation_id", "source_id", "atomic_statement"], ["OBS-UKCG-1", "SRC-UKCG-1", "UK Central Government has a synthetic test observation."]]),
    ])
    assets = {
        "twin_spine/UKCG-CDT-01-Twin-Spine-v1.0.xlsx": workbook,
        "docs/UKCG-CDT-00-Delivery-and-Input-Manifest-v1.0.md": b"# Delivery manifest\n",
        "docs/UKCG-CDT-02-Governed-Commercial-Digital-Twin-v1.0.md": b"# Governed twin\n",
        "docs/UKCG-CDT-04-Research-Completion-and-Validation-Report-v1.0.md": b"# Validation report\n",
    }
    for rel, data in assets.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def test_uk_government_export_uses_existing_blueprint_manifest_and_validates_in_flora(tmp_path, monkeypatch):
    source = tmp_path / "assets"
    write_required_assets(source)
    zip_path = build(source, tmp_path / "dist")
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        manifest = json.loads(zf.read("blueprint_manifest.json"))
    assert "blueprint_manifest.json" in names
    assert manifest["package_id"] == "UKCG-CDT-Blueprint"
    assert manifest["enterprise_id"] == "UK-Central-Government"
    assert manifest["final_twin_spine_workbook"] == "twin_spine/UKCG-CDT-01-Twin-Spine-v1.0.xlsx"
    assert not any(name.startswith("CIOS-Researcher-Knowledge-Pack") for name in names)

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path / "flora"))
    record = BlueprintPackageRegistry().receive(zip_path.read_bytes(), zip_path.name, "alice")
    result = BlueprintPackageValidator().validate_and_stage(record.package_ref, "alice", {"X-Flora-User":"alice", "X-Flora-Enterprises":"UK-Central-Government", "X-Flora-Roles":"package.review"})
    assert not result.errors
    assert result.records_accepted_into_staging == 3
    assert result.canonical_mutations == 0


def test_uk_government_export_fails_until_required_structured_assets_exist(tmp_path):
    with pytest.raises(SystemExit, match="Missing required UK Government Blueprint assets"):
        build(tmp_path / "missing", tmp_path / "dist")
