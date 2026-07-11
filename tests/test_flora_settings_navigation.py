from __future__ import annotations

import http.client
from http.server import ThreadingHTTPServer

from cios.applications.flora import architecture_export as ae
from cios.applications.flora.web.app import FloraWebHandler, _flora_home_page
from cios.applications.flora.workspace.views import general_settings_page, settings_page

OWNER = {"X-Flora-User":"rob","X-Flora-Active-Workspace":"CIOS","X-Flora-Enterprises":"CIOS","X-Flora-Roles":"owner"}
NON_OWNER = {"X-Flora-User":"alice","X-Flora-Active-Workspace":"CIOS","X-Flora-Enterprises":"CIOS","X-Flora-Roles":"viewer"}


def test_opening_screen_shows_owner_settings_access_and_tiles_remain():
    html = _flora_home_page(OWNER)
    assert "href='/settings'" in html
    assert "Import Blueprint" in html
    assert "Enterprise Canvas" in html
    assert "Import History" in html


def test_non_owner_opening_screen_hides_owner_settings_access():
    assert "href='/settings'" not in _flora_home_page(NON_OWNER)


def test_settings_landing_page_sections_and_architecture_navigation():
    html = settings_page()
    assert "<h1>Settings</h1>" in html
    assert "General Configuration" in html
    assert "Architecture Export" in html
    assert "Open Architecture Export" in html
    assert "/settings/architecture-export" in html
    assert "Local editing placeholder" not in html


def test_general_settings_renders_legacy_configuration():
    html = general_settings_page()
    assert "<h1>General Configuration</h1>" in html
    assert "Provider context" in html
    assert "Local editing placeholder" in html


def test_architecture_export_owner_non_owner_commit_and_status(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(ae, "validated_export_metadata", lambda: None)
    owner_html, owner_status = ae.architecture_export_page(OWNER)
    denied_html, denied_status = ae.architecture_export_page(NON_OWNER)
    assert owner_status == 200
    assert "Package status" in owner_html
    assert "Architecture package unavailable" in owner_html
    assert "Open GitHub Actions" in owner_html
    assert "<button>Generate architecture package</button>" not in owner_html
    assert denied_status == 403
    assert "Repository" not in denied_html


def test_existing_settings_links_redirect_and_back_targets_work():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    try:
        import threading
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        host, port = server.server_address
        conn = http.client.HTTPConnection(host, port)
        conn.request("GET", "/settings/configuration", headers=OWNER)
        resp = conn.getresponse(); resp.read()
        assert resp.status == 303
        assert resp.getheader("Location") == "/settings/general"
        conn.request("GET", "/settings", headers=OWNER)
        resp = conn.getresponse(); body = resp.read().decode()
        assert resp.status == 200
        assert "Settings" in body and "Architecture Export" in body
        conn.request("GET", "/settings/general", headers=OWNER)
        resp = conn.getresponse(); body = resp.read().decode()
        assert resp.status == 200
        assert "General Configuration" in body
    finally:
        server.shutdown(); server.server_close()
