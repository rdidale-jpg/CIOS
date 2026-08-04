import io
import json
from pathlib import Path
import zipfile

import pytest

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, PackageReceiptError
from cios.applications.flora.blueprint_import.contract import BlueprintManifest, build_manifest
from tools.blueprints.validate_package import validate


FIXTURE = Path("tests/fixtures/blueprint_packages/minimal/blueprint_manifest.json")


def package(manifest, extra=()):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("blueprint_manifest.json", json.dumps(manifest, sort_keys=True))
        for path, content in extra:
            archive.writestr(path, content)
    return stream.getvalue()


def test_known_valid_fixture_uses_model_and_real_flora_path(tmp_path, monkeypatch):
    manifest = json.loads(FIXTURE.read_text())
    assert build_manifest(**manifest) == manifest
    archive = tmp_path / "minimal.zip"
    archive.write_bytes(package(manifest))
    validate(archive)


@pytest.mark.parametrize("change", [
    {"schema_version": "2.0"},
    {"inferred_release_shape": {}},
])
def test_unsupported_version_and_unexpected_fields_fail_at_receipt(tmp_path, monkeypatch, change):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    manifest = json.loads(FIXTURE.read_text()) | change
    with pytest.raises(PackageReceiptError, match="required Blueprint manifest structure"):
        BlueprintPackageRegistry().receive(package(manifest), "invalid.zip", "researcher")


def test_generated_schema_prohibits_additional_fields():
    schema = BlueprintManifest.model_json_schema()
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"package_id", "package_version", "enterprise_id", "profile_version"}
