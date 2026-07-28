from __future__ import annotations

import json

from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.views import (
    approve_and_promote,
    import_blueprint_entry_page,
    upload_and_validate_blueprint,
    validation_result_page,
)
from cios.applications.flora.pilot_import import pilot_import_bypass_enabled
from tests.test_flora_blueprint_import_validation import pkg

FIELDS = {"blueprint_zip.filename": "pilot.zip", "blueprint_zip.content_type": "application/zip"}


def test_bypass_defaults_false_and_only_explicit_true_enables(monkeypatch):
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    assert pilot_import_bypass_enabled() is False
    for value in ("1", "yes", "on", "false", " true-ish"):
        monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", value)
        assert pilot_import_bypass_enabled() is False
    monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", "TrUe")
    assert pilot_import_bypass_enabled() is True


def test_disabled_preserves_anonymous_denial(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    page, status = import_blueprint_entry_page({})
    assert status == 200 and "Sign in or select a workspace" in page
    _, status, _ = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, {})
    assert status == 403


def test_enabled_renders_form_without_identity_or_secret(monkeypatch):
    monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", "true")
    page, status = import_blueprint_entry_page({})
    assert status == 200
    assert "Pilot import bypass active" in page
    assert "temporarily disabled for this pilot environment" in page
    assert "Upload Twin" in page and "blueprint_zip" in page and "Import history" in page
    assert "pilot-sign-in" not in page and "Capability decision" not in page
    assert "Sign in for pilot access" not in page


def test_anonymous_multipart_contract_receives_inspects_and_stages_candidate(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", "TRUE")
    html, status, target = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, {})
    assert status == 200 and target.startswith("/blueprint-import/bpi-run-")
    record = BlueprintPackageRegistry().list()[0]
    assert record.received_by == "flora-pilot"
    assert record.workspace_id == "flora-pilot-workspace"
    assert record.package_inspection["authentication_mode"] == "pilot_import_bypass"
    assert record.package_inspection["actor_type"] == "pilot_operator"
    assert "Validation result" in html
    result, result_status = validation_result_page(record.import_run_id, {})
    assert result_status == 200 and "Pilot import bypass active" in result
    summary = json.loads((tmp_path / "blueprint_import" / "staging" / record.import_run_id / "summary.json").read_text())
    assert summary["candidate_records_staged"] > 0
    assert not (tmp_path / "memory" / "observations.jsonl").exists()
    events = (tmp_path / "blueprint_import" / "audit" / "events.jsonl").read_text()
    assert "pilot_import_bypass_used" in events and "bypassed for pilot" in events


def test_invalid_zip_and_size_safety_are_not_bypassed(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", "true")
    html, status, _ = upload_and_validate_blueprint({"blueprint_zip": b"not a zip"}, FIELDS, {})
    assert status == 400 and "Stage failed: Package received" in html
    assert "Account recognised</th><td>Bypassed for pilot" in html
    assert "No active workspace" not in html and "package.upload denied" not in html
    monkeypatch.setattr("cios.applications.flora.blueprint_import.views.MAX_UPLOAD_BYTES", 3)
    html, status, _ = upload_and_validate_blueprint({"blueprint_zip": b"1234"}, FIELDS, {})
    assert status == 400 and "upload limit" in html


def test_bypass_does_not_grant_promotion_and_can_be_disabled_again(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", "true")
    _, status, target = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, {})
    assert status == 200
    run_id = target.rsplit("/", 1)[-1]
    _, promote_status = approve_and_promote(run_id, {}, {})
    assert promote_status == 403
    monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", "false")
    _, status, _ = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, {})
    assert status == 403
