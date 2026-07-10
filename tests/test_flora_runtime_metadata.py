from __future__ import annotations

from cios.applications.flora.live import runtime
from cios.applications.flora.web.app import deployment_payload


def test_deployment_metadata_prefers_render_environment(monkeypatch):
    runtime.application_revision.cache_clear()
    monkeypatch.setenv("RENDER_GIT_COMMIT", "a" * 80)
    monkeypatch.setenv("RENDER_GIT_BRANCH", "work")
    monkeypatch.setenv("RENDER_BUILD_TIMESTAMP", "1783684800")
    monkeypatch.setenv("FLORA_DEPLOYMENT_VERSION", "flora-live")

    metadata = runtime.deployment_metadata()

    assert metadata["deployment_version"] == "flora-live"
    assert metadata["commit_sha"] == "a" * 64
    assert metadata["branch"] == "work"
    assert metadata["build_timestamp"].startswith("2026-")
    assert deployment_payload()["service"] == "flora"
