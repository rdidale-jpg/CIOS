"""Tests for the production Flora web entry point."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from http.client import HTTPConnection

from cios.applications.flora.web.app import FloraWebHandler, env_port


def _get(path: str) -> tuple[int, str, bytes]:
    server = __import__("http.server").server.ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = HTTPConnection("127.0.0.1", server.server_port)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        return response.status, response.getheader("Content-Type") or "", body
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_health_returns_200_plain_json() -> None:
    status, content_type, body = _get("/health")
    assert status == 200
    assert content_type == "application/json"
    assert json.loads(body.decode("utf-8")) == {"status": "healthy", "service": "flora"}


def test_root_renders_morning_edition_content() -> None:
    status, content_type, body = _get("/")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Good Morning Rob" in html
    assert "Morning Edition" in html


def test_bt_case_route_renders_case_file() -> None:
    status, content_type, body = _get("/case/BT")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Flora Case File" in html
    assert "BT" in html
    assert "Evidence Ledger" in html


def test_web_app_uses_port_environment_variable(monkeypatch) -> None:
    monkeypatch.setenv("PORT", "54321")
    monkeypatch.setenv("FLORA_PORT", "12345")
    assert env_port() == 54321


def test_existing_cli_command_still_works() -> None:
    result = subprocess.run([sys.executable, "-m", "cios.applications.flora.main"], check=True, text=True, capture_output=True)
    assert "Flora Daily Intelligence Brief" in result.stdout


def test_publisher_command_still_works(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    result = subprocess.run([sys.executable, "-m", "cios.applications.flora.publisher.morning_edition"], check=True, text=True, capture_output=True)
    assert "Flora Morning Edition generated" in result.stdout


def test_live_dashboard_renders(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    status, content_type, body = _get("/live")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Flora Live Evidence" in html
    assert "Sources attempted" in html


def test_live_status_returns_json(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    status, content_type, body = _get("/live/status")
    payload = json.loads(body.decode("utf-8"))
    assert status == 200
    assert content_type == "application/json"
    assert payload["evidence_objects_collected"] == 0


def test_live_evidence_empty_state(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    status, _, body = _get("/live/evidence")
    html = body.decode("utf-8")
    assert status == 200
    assert "No live evidence available" in html
    assert "/live/collect" in html


def test_homepage_morning_edition_live_banner(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    status, _, body = _get("/")
    assert status == 200
    assert "NO LIVE EVIDENCE AVAILABLE" in body.decode("utf-8")


def test_live_sources_route(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    status, content_type, body = _get("/live/sources")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Live source coverage" in html
    assert "Recommended action" in html


def test_radar_quadrant_counts_match_table_counts() -> None:
    from collections import Counter
    from cios.applications.flora.portfolio import build_radar_rows
    from cios.applications.flora.workspace.views import radar_page

    rows = build_radar_rows()
    counts = Counter(r.quadrant for r in rows)
    html = radar_page()
    for quadrant in ["Priority Pursuits", "Investigate", "Monitor", "Coverage Gap"]:
        assert f"<strong>{quadrant}:</strong>" in html
        assert f"{quadrant} <span class='pill'>{counts[quadrant]}</span>" in html


def test_all_organisations_appear_in_exactly_one_radar_quadrant() -> None:
    from cios.applications.flora.portfolio import build_radar_rows
    from cios.applications.flora.seed_data import sample_watchlist

    rows = build_radar_rows()
    organisations = [r.organisation for r in rows]
    assert len(organisations) == len(set(organisations))
    assert set(organisations) == {account.organisation_name for account in sample_watchlist()}
    assert all(r.quadrant in {"Priority Pursuits", "Investigate", "Monitor", "Coverage Gap"} for r in rows)


def test_score_bt_renders() -> None:
    status, content_type, body = _get("/score/BT")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "BT score explainability" in html
    assert "final score" in html


def test_score_facets_render() -> None:
    status, _, body = _get("/score/BT")
    html = body.decode("utf-8")
    assert status == 200
    for facet in ["Base strategic fit", "Live evidence uplift", "Evidence confidence", "Missing evidence penalty"]:
        assert facet in html


def test_evidence_trace_renders() -> None:
    status, _, body = _get("/score/BT")
    html = body.decode("utf-8")
    assert status == 200
    assert "Score Trace" in html
    assert "score contribution" in html


def test_missing_evidence_renders() -> None:
    status, _, body = _get("/score/BT")
    html = body.decode("utf-8")
    assert status == 200
    assert "Missing evidence that would increase confidence" in html
    assert "executive sponsor" in html
    assert "internal pain owner" in html


def test_radar_links_to_score_pages() -> None:
    status, _, body = _get("/radar")
    html = body.decode("utf-8")
    assert status == 200
    assert "Explain score" in html
    assert "/score/BT" in html


def test_watchlist_links_to_score_pages() -> None:
    status, _, body = _get("/")
    html = body.decode("utf-8")
    assert status == 200
    assert "Explain score" in html
    assert "/score/BT" in html


def test_scoring_renders_model_explanation() -> None:
    status, content_type, body = _get("/scoring")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Flora scoring model" in html
    assert "Base score" in html
    assert "Final score cap" in html
