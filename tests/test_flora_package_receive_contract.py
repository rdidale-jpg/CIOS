from __future__ import annotations

from pathlib import Path

import pytest

from cios.applications.flora.blueprint_import.models import BlueprintPackageRecord
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.validator import BlueprintPackageValidator
from cios.applications.flora.blueprint_import.views import (
    _failure_details_view_model, _failure_summary, upload_and_validate_blueprint,
)
from cios.applications.flora.storage import PersistenceError
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


def test_startup_probe_and_receive_reach_blueprint_inspection(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path / "flora"))
    from cios.applications.flora.storage import startup_storage_status

    assert startup_storage_status()["ready"] is True
    registry = BlueprintPackageRegistry()
    result = registry.receive(pkg(), "synthetic.zip", "alice", "synthetic-enterprise")

    assert result.import_run_id.startswith("bpi-run-")
    assert result.package_inspection
    assert registry.get(result.package_ref) == result
    assert (tmp_path / "flora" / "blueprint_import" / "packages").is_dir()


def test_registry_persists_repository_package_and_preserves_failed_create_cause(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    fixture = Path("MOD-CDT-v1.3-Flora-Blueprint 2.zip")
    registry = BlueprintPackageRegistry()

    result = registry.receive(fixture.read_bytes(), fixture.name, "alice", "synthetic-enterprise")

    assert result.import_run_id.startswith("bpi-run-")
    assert registry.get(result.package_ref) == result

    failed_root = tmp_path / "failed-receive"
    monkeypatch.setenv("FLORA_DATA_DIR", str(failed_root))
    before = tuple((failed_root / "memory").rglob("*")) if (failed_root / "memory").exists() else ()

    def fail_record_create(path, data):
        if path.parent.name == "packages":
            raise PermissionError(13, "Permission denied", str(path))
        from cios.applications.flora.storage import atomic_write_json
        return atomic_write_json(path, data)

    monkeypatch.setattr("cios.applications.flora.blueprint_import.registry.atomic_write_json", fail_record_create)
    with pytest.raises(PersistenceError) as raised:
        BlueprintPackageRegistry().receive(pkg(), "synthetic.zip", "alice")

    assert isinstance(raised.value.__cause__, PermissionError)
    assert "operation=create; model=BlueprintPackageRecord" in str(raised.value)
    assert raised.value.context["operation"] == "package_record_write"
    assert not list((failed_root / "blueprint_import" / "runs").glob("*.json"))
    assert not list((failed_root / "blueprint_import" / "archives").rglob("*.zip"))
    after = tuple((failed_root / "memory").rglob("*")) if (failed_root / "memory").exists() else ()
    assert after == before == ()


@pytest.mark.parametrize("concrete_error", [
    TypeError("cannot encode secret-token=do-not-display"),
    OSError(28, "disk full at /sensitive/runtime/path"),
])
def test_receive_failure_exposes_safe_root_cause_without_canonical_changes(
    monkeypatch, tmp_path, caplog, concrete_error
):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    canonical = tmp_path / "memory"

    def fail_record_create(path, data):
        if path.parent.name == "packages":
            raise concrete_error
        from cios.applications.flora.storage import atomic_write_json
        return atomic_write_json(path, data)

    monkeypatch.setattr("cios.applications.flora.blueprint_import.registry.atomic_write_json", fail_record_create)
    caplog.set_level("ERROR")

    html, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": pkg()}, FIELDS, HEADERS
    )

    assert status == 400 and target == "/blueprint-import"
    assert f"<th>Underlying exception class</th><td>builtins.{type(concrete_error).__name__}</td>" in html
    assert "<th>Underlying safe message</th><td>" in html
    assert "<th>Persistence operation</th><td>create</td>" in html
    assert "<th>Record/model</th><td>BlueprintPackageRecord</td>" in html
    assert "<th>Storage connection</th><td>PASS</td>" in html
    assert "<th>Minimal BlueprintPackageRecord persistence path</th><td>FAIL</td>" in html
    assert "Grouped failure reasons" not in html
    assert "secret-token" not in html and "/sensitive/runtime/path" not in html
    assert not canonical.exists()
    logged = next(record for record in caplog.records if record.message.startswith("blueprint_package_receive_persistence_failed"))
    assert logged.flora_event["diagnostic_reference"].startswith("bpi-diag-")
    assert logged.exc_info[1].__cause__ is concrete_error


def test_persistence_diagnostic_reaches_failure_view_model_as_values_not_reasons():
    concrete_error = TypeError("private payload must not be projected")
    try:
        raise PersistenceError("receipt persistence failed") from concrete_error
    except PersistenceError as exc:
        diagnostic = BlueprintPackageRegistry.persistence_diagnostic(exc, {
            "storage_connection": "PASS",
            "schema_reachable": "PASS",
            "minimal_persistence": "FAIL",
            "schema_alignment": "UNKNOWN",
        })

    model = _failure_details_view_model("Package receipt failed; stage=Package received", diagnostic)
    values = dict(model.operational_diagnostic.rows())

    assert values["Underlying exception class"] == "builtins.TypeError"
    assert values["Underlying safe message"] == "The record could not be serialized for storage."
    assert values["Persistence operation"] == "create"
    assert values["Record/model"] == "BlueprintPackageRecord"
    assert values["Storage backend"] or values["Storage backend"] == "UNKNOWN"
    assert model.validation_failure_reasons == ()

    html = _failure_summary("Package receipt failed; stage=Package received", diagnostic)
    assert "<th>Underlying exception class</th><td>builtins.TypeError</td>" in html
    assert "Grouped failure reasons" not in html
    assert "validation failure details were reported" not in html


def test_normal_validation_failure_reasons_still_group_without_operational_diagnostic():
    reasons = "; ".join(["Missing required file: manifest.json"] * 4)

    model = _failure_details_view_model(reasons)
    html = _failure_summary(reasons)

    assert model.validation_failure_reasons == ("Missing required file: manifest.json",) * 4
    assert "4 validation failure details were reported" in html
    assert "Grouped failure reasons" in html
    assert "<td>Missing required file</td><td>4</td>" in html


def test_health_probe_failure_does_not_replace_chained_receive_error(monkeypatch, tmp_path, caplog):
    """The diagnostic probe must not discard the receipt failure it is inspecting."""
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    concrete_error = OSError(28, "No space left on device", "private-run-path")

    from cios.applications.flora.blueprint_import import registry as registry_module
    from cios.applications.flora import storage

    real_replace = storage.os.replace

    def fail_run_write(source, destination):
        if Path(destination).parent.name == "runs":
            raise concrete_error
        return real_replace(source, destination)

    real_data_path = registry_module.data_path

    def fail_diagnostic_path(*parts):
        if parts == ("blueprint_import", "packages"):
            raise PersistenceError("diagnostic path unavailable")
        return real_data_path(*parts)

    monkeypatch.setattr(storage.os, "replace", fail_run_write)
    monkeypatch.setattr(registry_module, "data_path", fail_diagnostic_path)
    caplog.set_level("ERROR")

    html, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": pkg()}, FIELDS, HEADERS
    )

    assert status == 400 and target == "/blueprint-import"
    assert "<th>Underlying exception class</th><td>builtins.OSError</td>" in html
    assert "<th>Underlying safe message</th><td>The filesystem storage operation failed.</td>" in html
    assert "<th>Persistence operation</th><td>create</td>" in html
    assert "<th>Record/model</th><td>BlueprintPackageRecord</td>" in html
    logged = next(record for record in caplog.records if record.message.startswith("blueprint_package_receive_persistence_failed"))
    received_error = logged.exc_info[1]
    assert isinstance(received_error, PersistenceError)
    assert received_error.__cause__ is concrete_error
    assert "Failed to persist Flora data" in str(received_error)


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
