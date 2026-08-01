"""Real-browser regression coverage for the native Twin package control."""
from __future__ import annotations

import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.web.app import FloraWebHandler
from tests.test_flora_blueprint_import_validation import pkg


def test_native_file_control_selects_and_submits_package_bytes(monkeypatch, tmp_path):
    """Exercise the same visible control and multipart handler used by deployment."""
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    package = pkg()
    archive = tmp_path / "representative-twin.zip"
    archive.write_bytes(package)

    server = ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with playwright.sync_playwright() as manager:
            browser = manager.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{server.server_port}/blueprint-import")

            upload = page.locator("input[type=file]")
            assert upload.count() == 1
            assert upload.is_visible() and upload.is_enabled()
            assert upload.get_attribute("id") == "twin-package"
            assert upload.get_attribute("name") == "blueprint_zip"
            assert upload.evaluate("el => el.form.enctype") == "multipart/form-data"
            assert page.locator("label[for='twin-package']").count() == 1
            assert upload.evaluate("el => getComputedStyle(el).pointerEvents") != "none"
            box = upload.bounding_box()
            assert box and box["width"] > 0 and box["height"] > 0
            centre_owner = upload.evaluate("""el => {
                const r = el.getBoundingClientRect();
                const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
                return hit === el || hit?.closest("label")?.htmlFor === el.id;
            }""")
            assert centre_owner, "the file chooser click target is covered by another element"

            select_box = page.locator("#expected_type").bounding_box()
            label_box = page.locator("label[for='twin-package']").bounding_box()
            assert select_box and label_box
            assert select_box["y"] + select_box["height"] <= label_box["y"]

            # The associated label and the native input both activate the same chooser.
            with page.expect_file_chooser() as label_chooser:
                page.locator("label[for='twin-package']").click()
            label_chooser.value.set_files(str(archive))
            upload.focus()
            assert upload.evaluate("el => el.matches(':focus-visible')")
            with page.expect_file_chooser() as keyboard_chooser:
                upload.press("Space")
            keyboard_chooser.value.set_files(str(archive))
            assert upload.evaluate("el => el.files.length") == 1
            assert upload.evaluate("el => el.files[0].name") == archive.name
            assert upload.input_value().endswith(archive.name)

            page.locator("button[type=submit]").click()
            page.wait_for_url("**/blueprint-import/bpi-run-*")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    record = BlueprintPackageRegistry().list()[0]
    received = Path(record.archive_path).read_bytes()
    assert received == package
    assert record.original_filename == archive.name
