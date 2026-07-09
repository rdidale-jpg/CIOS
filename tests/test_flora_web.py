"""Tests for the production Flora web entry point."""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from http.client import HTTPConnection

from cios.applications.flora.web.app import FloraWebHandler, RELEASE_IDENTIFIER, env_port


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


def _wait_for_port(port: int, process: subprocess.Popen[str]) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise AssertionError(f"production server exited before listening: {output}")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.1)
    raise AssertionError(f"production server did not listen on port {port}")


def _subprocess_get(port: int, path: str, headers: dict[str, str] | None = None) -> tuple[int, str, str, str]:
    connection = HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request("GET", path, headers=headers or {})
        response = connection.getresponse()
        body = response.read().decode("utf-8", errors="replace")
        return response.status, response.getheader("Content-Type") or "", response.getheader("X-Flora-Route") or "", body
    finally:
        connection.close()


def test_render_start_command_serves_flora_home_from_actual_server(tmp_path) -> None:
    port = 8766
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["FLORA_HOST"] = "127.0.0.1"
    env["FLORA_PILOT_DIR"] = str(tmp_path / "pilot")
    env.pop("HOST", None)
    process = subprocess.Popen(
        [sys.executable, "-m", "cios.applications.flora.web.app"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_for_port(port, process)
        request_scenarios = (
            None,
            {"Cookie": "product-session=BT; flora_enterprise=BT; selected_enterprise=BT"},
            {"Cookie": "flora-session=authorised; flora_role=admin"},
            {"Cookie": "flora-session=expired; product-session=BT"},
        )
        legacy_cookie = request_scenarios[1]
        for path in ("/", "/flora", "/flora/"):
            for headers in request_scenarios:
                status, content_type, route, html = _subprocess_get(port, path, headers=headers)
                assert status == 200
                assert content_type == "text/html; charset=utf-8"
                assert route == "home"
                assert re.search(r"<title>Flora Home</title>", html)
                assert "Flora Home" in html
                assert "Import Blueprint" in html
                assert "Enterprise Canvas" in html
                assert "Import History" in html
                assert "Release " in html
                assert "<h1>Executive Brief</h1>" not in html
        status, content_type, route, html = _subprocess_get(port, "/flora/bt-collection", headers=legacy_cookie)
        assert status == 200
        assert content_type == "text/html; charset=utf-8"
        assert route == ""
        assert "<h1>Executive Brief</h1>" in html
        assert "Flora Home" not in html
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_health_returns_200_plain_json() -> None:
    status, content_type, body = _get("/health")
    assert status == 200
    assert content_type == "application/json"
    assert json.loads(body.decode("utf-8")) == {"status": "healthy", "service": "flora"}


def test_root_renders_flora_home_from_production_handler() -> None:
    status, content_type, body = _get("/")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Flora Home" in html
    assert "Import Blueprint" in html
    assert "Enterprise Canvas" in html
    assert "Import History" in html
    assert "BT Collection" in html
    assert f"Release {RELEASE_IDENTIFIER}" in html
    assert "<h1>Executive Brief</h1>" not in html


def test_flora_route_renders_same_home_experience() -> None:
    status, content_type, body = _get("/flora")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Flora Home" in html
    assert "Import Blueprint" in html
    assert "Enterprise Canvas" in html
    assert "Import History" in html
    assert f"Release {RELEASE_IDENTIFIER}" in html
    assert "<h1>Executive Brief</h1>" not in html


def test_flora_trailing_slash_route_renders_same_home_experience() -> None:
    status, content_type, body = _get("/flora/")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Flora Home" in html
    assert "Import Blueprint" in html
    assert "Enterprise Canvas" in html
    assert "Import History" in html
    assert f"Release {RELEASE_IDENTIFIER}" in html
    assert "<h1>Executive Brief</h1>" not in html


def test_bt_collection_is_labelled_specialist_route_not_default() -> None:
    status, _, body = _get("/flora/bt-collection")
    html = body.decode("utf-8")
    assert status == 200
    assert "<h1>Executive Brief</h1>" in html
    assert "Flora Home" not in html



def test_render_start_command_uses_production_web_entrypoint() -> None:
    render_config = __import__("pathlib").Path("render.yaml").read_text(encoding="utf-8")
    assert "startCommand: python -m cios.applications.flora.web.app" in render_config


def test_home_responses_disable_stale_proxy_cache() -> None:
    server = __import__("http.server").server.ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = HTTPConnection("127.0.0.1", server.server_port)
    try:
        connection.request("GET", "/")
        response = connection.getresponse()
        response.read()
        assert response.getheader("Cache-Control") == "no-store, max-age=0"
        assert response.getheader("Pragma") == "no-cache"
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

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


def test_homepage_does_not_auth_redirect_to_bt_collection(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    status, _, body = _get("/")
    html = body.decode("utf-8")
    assert status == 200
    assert "Access denied" not in html
    assert "<h1>Executive Brief</h1>" not in html


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


def test_home_import_blueprint_navigation_uses_governed_route() -> None:
    status, _, body = _get("/")
    html = body.decode("utf-8")
    assert status == 200
    assert "Open Import Blueprint" in html
    assert "/flora/blueprint-import" in html


def test_blueprint_import_get_does_not_mutate_canonical_data(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FLORA_BLUEPRINT_IMPORT_DIR", str(tmp_path / "imports"))
    status, _, body = _get("/flora/blueprint-import")
    html = body.decode("utf-8")
    assert status == 200
    assert "Import Blueprint" in html
    assert not (tmp_path / "imports" / "history.jsonl").exists()


def test_scoring_renders_model_explanation() -> None:
    status, content_type, body = _get("/scoring")
    html = body.decode("utf-8")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Flora scoring model" in html
    assert "Base score" in html
    assert "Final score cap" in html


def test_live_scoring_trace_consistency_and_audit(monkeypatch, tmp_path) -> None:
    from cios.applications.flora.live import store
    from cios.applications.flora.score_explainability import score_detail
    from cios.applications.flora.portfolio import HIGH_CONFIDENCE_THRESHOLD, HIGH_POTENTIAL_THRESHOLD, build_radar_rows
    from cios.applications.flora.publisher.morning_edition import build_publication_context
    from cios.applications.flora.workspace.views import radar_page

    evidence_path = tmp_path / "evidence.jsonl"
    rows = [
        {"source_id": "bt-news", "organisation": "BT", "source_name": "BT newsroom", "source_url": "https://example.com/bt", "source_type": "official_newsroom", "snippet": "BT expands AI network operations for resilience.", "extraction_timestamp": "2026-06-29T00:00:00+00:00", "commercial_condition": "AI Modernisation", "likely_capability": "network intelligence", "confidence": 90, "overall_evidence_quality": 88, "evidence_tier": "tier_1_company"},
        {"source_id": "bt-reg", "organisation": "BT", "source_name": "Regulator", "source_url": "https://example.com/reg", "source_type": "regulator", "snippet": "Regulatory reporting highlights operational resilience.", "extraction_timestamp": "2026-06-30T00:00:00+00:00", "commercial_condition": "Operational Resilience", "likely_capability": "network intelligence", "confidence": 85, "overall_evidence_quality": 82, "evidence_tier": "tier_1_regulator"},
    ]
    store.write_jsonl(rows, evidence_path)
    monkeypatch.setattr("cios.applications.flora.portfolio.DEFAULT_PATH", evidence_path)
    monkeypatch.setattr("cios.applications.flora.score_explainability.DEFAULT_PATH", evidence_path)
    monkeypatch.setattr("cios.applications.flora.publisher.morning_edition.read_jsonl", lambda path=None: store.read_jsonl(evidence_path))
    monkeypatch.setattr("cios.applications.flora.workspace.state.read_jsonl", lambda path=None: store.read_jsonl(evidence_path))

    radar_bt = next(row for row in build_radar_rows() if row.organisation == "BT")
    detail = score_detail("BT")
    pub_bt = next(row for row in build_publication_context()["top_organisations"] if row["organisation"] == "BT")

    assert radar_bt.final_score == detail["final_score"] == pub_bt["final_score"]
    assert detail["total_platform_live_evidence_count"] == 2
    assert detail["unique_evidence_count"] == 2
    assert detail["live_scoring_mode"] in {"LIVE", "MIXED"}
    audit = detail["audit"]
    assert (
        audit["base_seeded_score"]
        + audit["live_evidence_uplift"]
        + audit["source_diversity_uplift"]
        + audit["condition_relevance_uplift"]
        + audit["evidence_quality_uplift"]
        - audit["missing_evidence_penalty"]
    ) == audit["final_score"]
    assert radar_bt.quadrant_reason
    assert f"final score &ge; {HIGH_POTENTIAL_THRESHOLD}" in radar_page()
    assert f"evidence confidence &ge; {HIGH_CONFIDENCE_THRESHOLD}" in radar_page()


def test_seeded_fallback_label_when_no_live_evidence(monkeypatch, tmp_path) -> None:
    from cios.applications.flora.score_explainability import score_detail
    from cios.applications.flora.workspace.views import score_page

    evidence_path = tmp_path / "empty.jsonl"
    evidence_path.write_text("", encoding="utf-8")
    monkeypatch.setattr("cios.applications.flora.portfolio.DEFAULT_PATH", evidence_path)
    monkeypatch.setattr("cios.applications.flora.score_explainability.DEFAULT_PATH", evidence_path)

    detail = score_detail("BT")
    assert detail["live_scoring_mode"] == "SEEDED FALLBACK"
    html = score_page("BT")
    assert "SEEDED FALLBACK" in html
    assert "total platform live evidence objects" in html


def test_threshold_changes_support_early_pilot_distribution() -> None:
    from cios.applications.flora.portfolio import quadrant_for

    assert quadrant_for(65, 40) == "Priority Pursuits"
    assert quadrant_for(65, 39) == "Investigate"
    assert quadrant_for(64, 40) == "Monitor"
    assert quadrant_for(64, 39) == "Coverage Gap"


def test_observatory_home_renders_enterprise_weather() -> None:
    status, _, body = _get("/observatory")
    html = body.decode("utf-8")
    assert status == 200
    assert "Enterprise Transformation Observatory" in html
    assert "Enterprise Weather" in html
    assert "Research Notebook" in html
    assert "/observatory/DWP" in html


def test_observatory_organisation_case_for_change_is_explainable() -> None:
    status, _, body = _get("/observatory/DWP")
    html = body.decode("utf-8")
    assert status == 200
    assert "DWP Transformation Genome" in html
    assert "Strategic Conviction Engine" in html
    assert "Case for Change" in html
    assert "Why Act?" in html
    assert "Supporting Evidence Framework" in html
    assert "Never" not in html


def test_observatory_critique_route_renders_preimplementation_critique() -> None:
    status, _, body = _get("/observatory/critique")
    html = body.decode("utf-8")
    assert status == 200
    assert "Architectural Critique" in html
    assert "evidence-to-hypothesis reasoning spine" in html
