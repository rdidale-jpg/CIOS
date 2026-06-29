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
