from __future__ import annotations

import json
from pathlib import Path

import pytest

from cios.applications.flora import architecture_export as ae
from cios.applications.flora.web.app import _content_type_for_path

OWNER = {"X-Flora-User":"rob","X-Flora-Active-Workspace":"CIOS","X-Flora-Enterprises":"CIOS","X-Flora-Roles":"owner"}
NON_OWNER = {"X-Flora-User":"alice","X-Flora-Active-Workspace":"CIOS","X-Flora-Enterprises":"CIOS","X-Flora-Roles":"viewer"}


def test_owner_can_access_architecture_export(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html, status = ae.architecture_export_page(OWNER)
    assert status == 200
    assert "Architecture Export" in html
    assert "Generate architecture package unavailable" in html


def test_non_owner_cannot_access_architecture_export(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html, status = ae.architecture_export_page(NON_OWNER)
    assert status == 403
    assert "User not authorised" in html


def test_generate_dispatches_correct_workflow(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_GITHUB_TOKEN", "server-only-token")
    calls = []
    monkeypatch.setattr(ae, "_github", lambda method, endpoint, payload=None: calls.append((method, endpoint, payload)) or {})
    record = ae.dispatch_export(OWNER, requested_ref="abc123", export_profile="architecture-reconciliation")
    assert record.requested_ref == "abc123"
    assert calls[0][0] == "POST"
    assert calls[0][1].endswith("/actions/workflows/export-flora-architecture.yml/dispatches")
    assert calls[0][2]["inputs"]["git_ref"] == "abc123"


def _repo(tmp_path: Path, files: dict[str, str], manifest_files: list[dict]):
    for path, text in files.items():
        p = tmp_path / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")
    (tmp_path / "FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json").write_text(json.dumps({"export_profiles":{"architecture-reconciliation":{"bundles":["b"],"files":manifest_files}}}), encoding="utf-8")


def test_manifest_controls_file_list_and_excludes_unlisted(tmp_path):
    _repo(tmp_path, {"approved.md":"ok", "unlisted.md":"ok"}, [{"path":"approved.md","required":True}])
    result = ae.validate_manifest(tmp_path)
    assert result["files"] == ["approved.md"]
    assert "unlisted.md" not in result["files"]


def test_env_files_are_excluded(tmp_path):
    _repo(tmp_path, {".env":"TOKEN=secret"}, [{"path":".env","required":True}])
    with pytest.raises(ValueError):
        ae.validate_manifest(tmp_path)


def test_secret_detection_fails_closed(tmp_path):
    _repo(tmp_path, {"config.txt":"api_key = 'abcdefghijklmnopqrstuvwxyz'"}, [{"path":"config.txt","required":True}])
    with pytest.raises(ValueError, match="Sensitive content detected"):
        ae.validate_manifest(tmp_path)


def test_path_traversal_is_rejected(tmp_path):
    _repo(tmp_path, {"ok.md":"ok"}, [{"path":"../outside.md","required":True}])
    with pytest.raises(ValueError):
        ae.validate_manifest(tmp_path)


def test_symbolic_link_escape_is_rejected(tmp_path):
    outside = tmp_path.parent / "outside-secret.txt"; outside.write_text("safe words", encoding="utf-8")
    (tmp_path / "link.txt").symlink_to(outside)
    _repo(tmp_path, {}, [{"path":"link.txt","required":True}])
    with pytest.raises(ValueError, match="Symbolic-link escape"):
        ae.validate_manifest(tmp_path)


def test_missing_required_files_fail_export(tmp_path):
    _repo(tmp_path, {}, [{"path":"missing.md","required":True}])
    with pytest.raises(FileNotFoundError):
        ae.validate_manifest(tmp_path)


def test_relative_paths_are_preserved(tmp_path):
    _repo(tmp_path, {"docs/a.md":"ok"}, [{"path":"docs/a.md","required":True}])
    assert ae.validate_manifest(tmp_path)["files"] == ["docs/a.md"]


def test_successful_workflow_exposes_one_download_button(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    rec = ae.ExportAuditRecord("id","rob","CIOS","Rob/CIOS","main",status="Succeeded",requested_at="now")
    d = rec.__dict__.copy(); ae.save_records([d])
    html, status = ae.architecture_export_page(OWNER)
    assert status == 200
    assert html.count("Download latest package") == 1


def test_expired_artifact_shows_regeneration_action(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    d = ae.ExportAuditRecord("id","rob","CIOS","Rob/CIOS","main",status="Succeeded",requested_at="now").__dict__; d["artifact_expired"] = True
    ae.save_records([d])
    html, _ = ae.architecture_export_page(OWNER)
    assert "Architecture package expired" in html
    assert "Generate a new package" in html


def test_download_requires_authorisation(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    with pytest.raises(PermissionError):
        ae.record_download(NON_OWNER)


def test_github_token_never_returned_to_browser(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); monkeypatch.setenv("FLORA_GITHUB_TOKEN", "super-secret-token")
    monkeypatch.setattr(ae, "_remote_integration_reason", lambda repo: "Ready")
    html, _ = ae.architecture_export_page(OWNER)
    assert "super-secret-token" not in html


def test_export_does_not_mutate_canonical_twin_data(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); monkeypatch.setenv("FLORA_GITHUB_TOKEN", "t")
    monkeypatch.setattr(ae, "_github", lambda *a, **k: {})
    ae.dispatch_export(OWNER)
    assert not (tmp_path / "memory").exists()
    assert (tmp_path / "architecture_exports" / "audit_records.json").exists()


def test_optional_release_publishing_requires_confirmation(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); monkeypatch.setenv("FLORA_GITHUB_TOKEN", "t")
    with pytest.raises(PermissionError):
        ae.dispatch_export(OWNER, publish_mode="release")


def test_export_audit_records_are_retained(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); monkeypatch.setenv("FLORA_GITHUB_TOKEN", "t")
    monkeypatch.setattr(ae, "_github", lambda *a, **k: {})
    ae.dispatch_export(OWNER, requested_ref="main")
    records = ae.load_records()
    assert records and records[0]["requested_by"] == "rob"


def test_content_type_covers_architecture_export_route():
    assert _content_type_for_path("/settings/architecture-export") == "text/html; charset=utf-8"


def test_missing_credential_shows_not_configured(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    status = ae.github_integration_status()
    assert status["status"] == "Not configured"
    assert status["reason"] == "GitHub credential unavailable"


def test_invalid_credential_shows_exact_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_GITHUB_TOKEN", "invalid-token")
    monkeypatch.setattr(ae, "_remote_integration_reason", lambda repo: (_ for _ in ()).throw(RuntimeError("Credential invalid")))
    assert ae.github_integration_status()["reason"] == "Credential invalid"


def test_insufficient_permission_shows_exact_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_GITHUB_TOKEN", "limited-token")
    monkeypatch.setattr(ae, "_remote_integration_reason", lambda repo: (_ for _ in ()).throw(RuntimeError("Insufficient Actions permission")))
    assert ae.github_integration_status()["reason"] == "Insufficient Actions permission"


def test_valid_credential_shows_ready(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_GITHUB_TOKEN", "valid-token")
    monkeypatch.setattr(ae, "_remote_integration_reason", lambda repo: "Ready")
    status = ae.github_integration_status()
    assert status["status"] == "Ready"
    assert status["token_available"] is True


def test_workflow_status_and_artifact_metadata_checks_are_called(monkeypatch):
    calls = []
    def fake_github(method, endpoint, payload=None):
        calls.append((method, endpoint, payload)); return {}
    monkeypatch.setattr(ae, "_github", fake_github)
    assert ae._remote_integration_reason("rdidale-jpg/CIOS") == "Ready"
    endpoints = [call[1] for call in calls]
    assert any("/runs?per_page=1" in endpoint for endpoint in endpoints)
    assert any("/actions/artifacts?per_page=1" in endpoint for endpoint in endpoints)


def test_artifact_read_forbidden_exact_failure():
    assert ae._github_failure_reason("/repos/rdidale-jpg/CIOS/actions/artifacts", 403) == "Artifact read forbidden"


def test_credential_value_is_never_logged(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_GITHUB_TOKEN", "super-secret-token")
    monkeypatch.setattr(ae, "_remote_integration_reason", lambda repo: "Ready")
    ae.github_integration_status()
    captured = capsys.readouterr()
    assert "super-secret-token" not in captured.out
    assert "super-secret-token" not in captured.err
