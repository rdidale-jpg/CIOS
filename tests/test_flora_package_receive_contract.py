from __future__ import annotations

from cios.applications.flora.blueprint_import.models import BlueprintPackageRecord
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.validator import BlueprintPackageValidator
from cios.applications.flora.blueprint_import.views import upload_and_validate_blueprint
from tests.test_flora_blueprint_import_validation import pkg

HEADERS = {
    "X-Flora-User": "alice",
    "X-Flora-Enterprises": "synthetic-enterprise",
    "X-Flora-Roles": "package.upload,package.review,candidate.promote",
}
FIELDS = {
    "blueprint_zip.filename": "synthetic.zip",
    "blueprint_zip.content_type": "application/zip",
}


def test_registry_canonical_receive_result_has_stable_receipt_contract(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    result = BlueprintPackageRegistry().receive(pkg(), "synthetic.zip", "alice", "synthetic-enterprise")

    assert isinstance(result, BlueprintPackageRecord)
    assert result.receipt_success is True
    assert result.status == "received"
    assert result.registry_reference == result.package_ref
    assert result.import_run_id.startswith("bpi-run-")
    assert result.archive_path and result.package_sha256 and result.original_filename == "synthetic.zip"
    assert result.received_at and isinstance(result.warnings, tuple) and result.blocking_error == ""
    assert "accepted" not in result.to_dict()


def test_browser_adapter_rejects_stale_mapping_shape_without_rendering_keyerror(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(BlueprintPackageRegistry, "receive", lambda *args, **kwargs: {"accepted": True})

    html, status, target = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, HEADERS)

    assert status == 400 and target == "/blueprint-import"
    assert "expected response=BlueprintPackageRecord" in html
    assert "actual response=dict keys=[&#x27;accepted&#x27;]" in html
    assert "Package received: no" in html and "Canonical changes occurred: no" in html
    assert "KeyError" not in html and "<p>&#x27;accepted&#x27;</p>" not in html


def test_safe_receipt_is_retryable_when_inspection_fails(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    def fail_inspection(*args, **kwargs):
        raise KeyError("accepted")

    monkeypatch.setattr(BlueprintPackageValidator, "validate_and_stage", fail_inspection)
    html, status, target = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, HEADERS)

    assert status == 400 and target.startswith("/blueprint-import/bpi-run-")
    assert "Package received: yes" in html and "Package inspected: no" in html
    assert "Package available for retry: yes" in html
    assert "service=cios.applications.flora.blueprint_import.validator" in html
    assert "KeyError" in html and "&#x27;accepted&#x27;" not in html
    assert next((tmp_path / "blueprint_import" / "archives").rglob("synthetic.zip")).is_file()


def test_unsafe_archive_is_disposed_and_not_retryable(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    html, status, _ = upload_and_validate_blueprint({"blueprint_zip": b"not-a-zip"}, FIELDS, HEADERS)

    assert status == 400
    assert "Package received: no" in html and "Package available for retry: no" in html
    assert not (tmp_path / "blueprint_import" / "archives").exists()


def test_normal_browser_upload_receives_then_starts_inspection(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    html, status, target = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, HEADERS)

    assert status == 200 and target.startswith("/blueprint-import/bpi-run-")
    assert "Package Inspection" in html and "Validation result" in html
    assert "Archive safety, checksum generation and package receipt passed" in html
