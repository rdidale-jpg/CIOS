from __future__ import annotations

import json
from pathlib import Path

import pytest

from cios.applications.flora import architecture_export as ae
from cios.applications.flora.web.app import _content_type_for_path

OWNER = {"X-Flora-User":"rob","X-Flora-Active-Workspace":"CIOS","X-Flora-Enterprises":"CIOS","X-Flora-Roles":"owner"}
NON_OWNER = {"X-Flora-User":"alice","X-Flora-Active-Workspace":"CIOS","X-Flora-Enterprises":"CIOS","X-Flora-Roles":"viewer"}

VALID_METADATA = {
    "package_name": "FLORA-Architecture-Baseline-abc1234.zip",
    "repository": "Rob/CIOS",
    "branch": "main",
    "commit_sha": "abc1234567890",
    "generated_at": "2026-07-11T00:00:00Z",
    "release_tag": "architecture-baseline-latest",
    "release_url": "https://github.com/Rob/CIOS/releases/tag/architecture-baseline-latest",
    "asset_url": "https://github.com/Rob/CIOS/releases/download/architecture-baseline-latest/FLORA-Architecture-Baseline-abc1234.zip",
    "checksum": "a" * 64,
    "file_count": 12,
    "total_size": 3456,
    "export_profile": "architecture-reconciliation",
    "workflow_run_id": "12345",
}


def test_owner_can_access_architecture_export(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(ae, "validated_export_metadata", lambda: None)
    html, status = ae.architecture_export_page(OWNER)
    assert status == 200
    assert "Architecture Export" in html
    assert "Architecture package unavailable" in html
    assert "Generate architecture package" not in html


def test_non_owner_cannot_access_architecture_export(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html, status = ae.architecture_export_page(NON_OWNER)
    assert status == 403
    assert "User not authorised" in html


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


def test_valid_metadata_shows_ready_commit_checksum_and_download(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(ae, "validated_export_metadata", lambda: VALID_METADATA)
    html, status = ae.architecture_export_page(OWNER)
    assert status == 200
    assert "Ready" in html
    assert VALID_METADATA["commit_sha"] in html
    assert VALID_METADATA["checksum"] in html
    assert html.count("Download latest package") == 1
    assert "Open GitHub release" in html


def test_missing_metadata_shows_clear_unavailable_state(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(ae, "validated_export_metadata", lambda: (_ for _ in ()).throw(RuntimeError("No published architecture baseline was found.")))
    html, status = ae.architecture_export_page(OWNER)
    assert status == 200
    assert "Architecture package unavailable" in html
    assert "No published architecture baseline was found." in html
    assert "Open GitHub Actions" in html
    assert "Open GitHub releases" in html


def test_download_link_points_to_published_release_asset(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(ae, "validated_export_metadata", lambda: VALID_METADATA)
    metadata = ae.record_download(OWNER)
    assert metadata["asset_url"] == VALID_METADATA["asset_url"]
    assert "releases/download/architecture-baseline-latest" in metadata["asset_url"]


def test_download_requires_authorisation(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    with pytest.raises(PermissionError):
        ae.record_download(NON_OWNER)


def test_flora_does_not_require_or_render_github_token(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_GITHUB_TOKEN", "super-secret-token")
    monkeypatch.setattr(ae, "validated_export_metadata", lambda: VALID_METADATA)
    html, _ = ae.architecture_export_page(OWNER)
    assert "super-secret-token" not in html
    assert ae.github_integration_status()["status"] == "Ready"


def test_no_workflow_dispatch_or_polling_is_attempted(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    calls = []
    monkeypatch.setattr(ae, "_fetch_json", lambda url: calls.append(url) or VALID_METADATA)
    assert ae.github_integration_status()["status"] == "Ready"
    assert len(calls) == 1
    assert "/dispatches" not in calls[0]
    assert "/actions/" not in calls[0]


def test_optional_export_url_overrides_metadata_asset(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ARCHITECTURE_EXPORT_URL", "https://cdn.example.com/export.zip")
    monkeypatch.setattr(ae, "load_export_metadata", lambda: VALID_METADATA)
    assert ae.validated_export_metadata()["asset_url"] == "https://cdn.example.com/export.zip"


def test_export_does_not_mutate_canonical_twin_data(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(ae, "validated_export_metadata", lambda: VALID_METADATA)
    ae.record_download(OWNER)
    assert not (tmp_path / "memory").exists()
    assert (tmp_path / "architecture_exports" / "download_log.jsonl").exists()


def test_content_type_covers_architecture_export_route():
    assert _content_type_for_path("/settings/architecture-export") == "text/html; charset=utf-8"
