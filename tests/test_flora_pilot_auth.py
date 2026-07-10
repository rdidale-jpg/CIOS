from __future__ import annotations

from cios.applications.flora.access import (
    authenticated_flora_user,
    active_flora_workspace,
    blueprint_upload_authorisation,
    flora_roles,
    user_enterprise_access,
)
from cios.applications.flora.blueprint_import.views import import_blueprint_entry_page, upload_and_validate_blueprint
from cios.applications.flora.pilot_auth import clear_session_cookie, issue_session_cookie
from tests.test_flora_blueprint_import_validation import pkg


def enable(monkeypatch):
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "0")
    monkeypatch.setenv("FLORA_PILOT_AUTH_ENABLED", "1")
    monkeypatch.setenv("FLORA_PILOT_ACCESS_SECRET", "test-secret")
    monkeypatch.setenv("FLORA_PILOT_OWNER_ID", "owner-1")
    monkeypatch.setenv("FLORA_PILOT_WORKSPACE", "CIOS")
    monkeypatch.setenv("FLORA_PILOT_ROLE", "cios_owner")


def headers(cookie: str):
    return {"Cookie": cookie.split(";", 1)[0]}


def test_valid_pilot_session_cookie_resolves_owner_workspace_role_and_policy(monkeypatch):
    enable(monkeypatch)
    cookie = issue_session_cookie(secure=False)
    h = headers(cookie)
    decision = blueprint_upload_authorisation(h)
    assert authenticated_flora_user(h) == "owner-1"
    assert active_flora_workspace(h) == "CIOS"
    assert user_enterprise_access(h) == {"CIOS"}
    assert "cios_owner" in flora_roles(h)
    assert decision.owner_recognised is True
    assert decision.resolved_membership == "resolved"
    assert decision.resolved_role == "cios_owner"
    assert "package.upload" in decision.effective_permissions
    assert decision.decision == "allowed"
    assert decision.authentication_source == "pilot_session_cookie"


def test_cookie_security_attributes_for_https_deployment(monkeypatch):
    enable(monkeypatch)
    cookie = issue_session_cookie(secure=True)
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=Lax" in cookie
    assert "Path=/" in cookie
    assert "Max-Age=" in cookie
    cleared = clear_session_cookie(secure=True)
    assert "Max-Age=0" in cleared and "Expires=Thu, 01 Jan 1970" in cleared


def test_synthetic_headers_ignored_and_tampered_cookie_rejected(monkeypatch):
    enable(monkeypatch)
    fake = {"X-Flora-User":"mallory","X-Flora-Enterprises":"CIOS","X-Flora-Active-Workspace":"CIOS","X-Flora-Roles":"cios_owner,package.upload"}
    assert blueprint_upload_authorisation(fake).decision == "denied"
    cookie = issue_session_cookie(secure=False).split(";", 1)[0] + "tamper"
    assert blueprint_upload_authorisation({"Cookie": cookie}).decision == "denied"


def test_blueprint_get_and_post_use_same_signed_session_and_anonymous_denied(monkeypatch, tmp_path):
    enable(monkeypatch)
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    anon_page, anon_status = import_blueprint_entry_page({})
    assert anon_status == 403
    assert "Sign in for pilot access" in anon_page
    cookie_headers = headers(issue_session_cookie(secure=False))
    page, status = import_blueprint_entry_page(cookie_headers)
    assert status == 200 and "Upload and validate" in page
    html, post_status, target = upload_and_validate_blueprint({"blueprint_zip": pkg({"enterprise_id":"CIOS"})}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, cookie_headers)
    assert post_status == 200
    assert "Validation result" in html
    assert target.startswith("/blueprint-import/bpi-run-")
    assert not (tmp_path / "memory" / "observations.jsonl").exists()


def test_pilot_sign_in_route_accepts_secret_only_by_post_and_sets_cookie(monkeypatch):
    import threading
    from http.client import HTTPConnection
    from http.server import ThreadingHTTPServer
    from cios.applications.flora.web.app import FloraWebHandler

    enable(monkeypatch)
    server = ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        conn = HTTPConnection("127.0.0.1", server.server_port)
        conn.request("GET", "/pilot-sign-in?pilot_secret=test-secret")
        response = conn.getresponse(); body = response.read().decode(); conn.close()
        assert response.status == 200
        assert "Set-Cookie" not in dict(response.getheaders())
        assert "Pilot access secret" in body

        conn = HTTPConnection("127.0.0.1", server.server_port)
        conn.request("POST", "/pilot-sign-in", "pilot_secret=wrong", {"Content-Type":"application/x-www-form-urlencoded"})
        response = conn.getresponse(); body = response.read().decode(); conn.close()
        assert response.status == 403
        assert "Invalid pilot access secret" in body

        conn = HTTPConnection("127.0.0.1", server.server_port)
        conn.request("POST", "/pilot-sign-in", "pilot_secret=test-secret", {"Content-Type":"application/x-www-form-urlencoded"})
        response = conn.getresponse(); response.read(); headers = dict(response.getheaders()); conn.close()
        assert response.status == 303
        assert headers["Location"] == "/flora"
        assert "flora_pilot_session=" in headers["Set-Cookie"]
        assert "HttpOnly" in headers["Set-Cookie"]
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)

def test_persistent_cookie_has_30_day_expiry_survives_restart_and_rejects_expired(monkeypatch):
    import time
    from cios.applications.flora.pilot_auth import resolve_pilot_session, session_ttl_seconds
    enable(monkeypatch)
    monkeypatch.setenv("FLORA_PILOT_SESSION_DAYS", "30")
    cookie = issue_session_cookie(secure=False)
    assert session_ttl_seconds() == 30 * 24 * 60 * 60
    assert "Max-Age=2592000" in cookie
    assert "Expires=" in cookie
    browser_restarted_cookie = cookie.split(";", 1)[0]
    assert resolve_pilot_session({"Cookie": browser_restarted_cookie}).user_id == "owner-1"
    expired = issue_session_cookie(secure=False, now=int(time.time()) - session_ttl_seconds() - 5).split(";", 1)[0]
    assert resolve_pilot_session({"Cookie": expired}) is None


def test_sign_out_clears_persistent_cookie(monkeypatch):
    enable(monkeypatch)
    cleared = clear_session_cookie(secure=False)
    assert "flora_pilot_session=" in cleared
    assert "Max-Age=0" in cleared
    assert "Expires=Thu, 01 Jan 1970 00:00:00 GMT" in cleared
