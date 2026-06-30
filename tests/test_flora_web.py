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
