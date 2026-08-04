import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
from pydantic import TypeAdapter, ValidationError

from cios.applications.flora.blueprint_import import BlueprintManifest, BlueprintPackageRegistry, BlueprintPackageValidator

ROOT = Path(__file__).parents[2]
CONTRACT = ROOT / "knowledge-packs/researcher/package-contracts/flora-blueprint-import"
SCHEMA = CONTRACT / "blueprint_manifest.schema.json"
EXAMPLE = CONTRACT / "blueprint_manifest.example.json"
UTILITY = CONTRACT / "build_flora_import.py"


def load_utility():
    spec = importlib.util.spec_from_file_location("portable_blueprint_builder", UTILITY)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def test_published_schema_is_exact_canonical_export_and_example_validates():
    schema = json.loads(SCHEMA.read_text())
    assert schema == BlueprintManifest.model_json_schema()
    BlueprintManifest.model_validate_json(EXAMPLE.read_text())
    load_utility().validate_schema(json.loads(EXAMPLE.read_text()), schema, schema)


def test_knowledge_pack_build_regenerates_contract(tmp_path):
    before = SCHEMA.read_text()
    subprocess.run([sys.executable, "tools/knowledge-packs/build_researcher_pack.py", "--version", "2.8.0", "--output-dir", str(tmp_path)], cwd=ROOT, check=True)
    assert SCHEMA.read_text() == before
    with zipfile.ZipFile(tmp_path / "CIOS-Researcher-Knowledge-Pack-v2.8.0.zip") as archive:
        names = archive.namelist()
        assert any(n.endswith("/package-contracts/flora-blueprint-import/blueprint_manifest.schema.json") for n in names)
        assert any(n.endswith("/package-contracts/flora-blueprint-import/build_flora_import.py") for n in names)


def build(tmp_path, manifest, files=None):
    folder=tmp_path/"content"; folder.mkdir(); (folder/"blueprint_manifest.json").write_text(json.dumps(manifest))
    for name,data in (files or {}).items():
        path=folder/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    output=tmp_path/"import.zip"
    result=subprocess.run([sys.executable,str(UTILITY),str(folder),"--output",str(output)],text=True,capture_output=True)
    return result, output


def minimal(**changes): return json.loads(EXAMPLE.read_text()) | changes


def test_portable_output_passes_real_receipt_and_inspection(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR",str(tmp_path/"flora"))
    result, archive=build(tmp_path,minimal())
    assert result.returncode == 0 and "VALID" in result.stdout
    package=BlueprintPackageRegistry().receive(archive.read_bytes(),archive.name,"researcher")
    inspection=BlueprintPackageValidator().validate_and_stage(package.package_ref,"researcher")
    assert inspection.errors == ()


@pytest.mark.parametrize("manifest,files,error", [
    (minimal(files=[{"path":"missing.json"}]), {}, "missing declared file"),
    (minimal(files=[{"path":"data.json","sha256":"0"*64}]), {"data.json":b"x"}, "SHA-256 mismatch"),
    (minimal(files=[{"path":"../data.json"}]), {}, "unsafe or non-normalized"),
    (minimal(files=[{"path":"data.json"},{"path":"data.json"}]), {"data.json":b"x"}, "duplicate declared path"),
    (minimal(unknown=True), {}, "unsupported additional properties"),
])
def test_portable_rejects_invalid_packages(tmp_path,manifest,files,error):
    result,_=build(tmp_path,manifest,files)
    assert result.returncode == 2 and error in result.stderr


def test_missing_manifest_and_identifiers_rejected(tmp_path):
    folder=tmp_path/"empty"; folder.mkdir()
    result=subprocess.run([sys.executable,str(UTILITY),str(folder),"--output",str(tmp_path/"x.zip")],text=True,capture_output=True)
    assert result.returncode == 2 and "manifest missing" in result.stderr


@pytest.mark.parametrize("names,error", [
    (["blueprint_manifest.json", "blueprint_manifest.json"], "duplicate ZIP paths"),
    (["blueprint_manifest.json", "../escape.json"], "unsafe or non-normalized"),
])
def test_zip_inventory_rejects_duplicate_and_unsafe_paths(tmp_path, names, error):
    archive=tmp_path/"hostile.zip"
    with zipfile.ZipFile(archive,"w") as zf:
        for name in names: zf.writestr(name,"{}")
    with pytest.raises(ValueError, match=error): load_utility().inventory(archive)


def test_invalid_structure_rejected_by_schema_and_flora(tmp_path, monkeypatch):
    invalid=minimal(package_id="x")
    result,_=build(tmp_path,invalid)
    assert result.returncode == 2
    with pytest.raises(ValidationError): BlueprintManifest.model_validate(invalid)
