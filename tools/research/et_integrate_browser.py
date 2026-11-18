"""Capture and check the integrated easyJet experience on an isolated loopback app."""
from http.server import ThreadingHTTPServer
from pathlib import Path
import shutil
import sys
from threading import Thread
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright

from cios.applications.flora.web.app import FloraWebHandler


class Quiet(FloraWebHandler):
    def log_message(self, *_args):
        pass


def run(output):
    with ThreadingHTTPServer(("127.0.0.1", 0), Quiet) as server, sync_playwright() as playwright:
        Thread(target=server.serve_forever, daemon=True).start()
        root = f"http://127.0.0.1:{server.server_port}"
        route = root + "/enterprises/easyjet/preview"
        browser = playwright.chromium.launch(executable_path=shutil.which("chromium"), args=["--no-sandbox"])
        try:
            for label, width, height in (
                ("desktop", 1440, 1000), ("ipad-landscape", 1180, 820), ("ipad-portrait", 820, 1180),
                ("mobile", 390, 844), ("mobile-320", 320, 740),
            ):
                page = browser.new_page(viewport={"width": width, "height": height},
                                        java_script_enabled=label != "mobile-320",
                                        has_touch=label != "desktop", reduced_motion="reduce")
                assert page.goto(root + "/enterprises/easyjet").status == 200
                page.get_by_role("link", name="Explore the illustrated easyJet operating system").click()
                assert page.url == route
                page.get_by_role("link", name="Inside", exact=True).click()
                if label in {"mobile", "mobile-320"}:
                    page.locator(".compact-scene > summary").click()
                    page.screenshot(path=output / f"scene-{label}.jpg", quality=76)
                    page.locator(".compact-scene > summary").click()
                for key, name in (
                    ("fleet-operations", "Fleet Operations"), ("network-planning", "Network Planning"),
                    ("customer-service", "Customer Service"),
                ):
                    compact = page.locator(".compact-scene > summary")
                    if compact.is_visible():
                        compact.click()
                    scene = page.get_by_role("navigation", name="Capabilities in the illustration")
                    link = scene.get_by_role("link", name=name, exact=True).filter(visible=True)
                    if label == "desktop":
                        page.keyboard.press("Tab")
                        link.focus()
                        assert link.evaluate("el => getComputedStyle(el).outlineStyle") == "solid"
                        page.keyboard.press("Enter")
                    else:
                        link.tap()
                    assert page.locator("main h1").inner_text() == name
                    assert page.locator(".reading-mode [aria-current]").inner_text() == "Facts"
                    assert page.request.get(root + page.locator(".et-picture img").first.get_attribute("src")).ok
                    page.screenshot(path=output / f"{key}-facts-{label}.jpg", quality=76)
                    page.get_by_role("link", name="FLORA Insight", exact=True).click()
                    assert page.locator("main h1").inner_text() == name
                    state = parse_qs(urlsplit(page.url).query)
                    assert state == {"stream": ["inside"], "detail": [key], "reading": ["insight"]}
                    assert page.locator("main [data-semantic-type=insight]").count() == 1
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / f"{key}-insight-{label}.jpg", quality=76)
                    page.go_back()
                    assert page.locator(".reading-mode [aria-current]").inner_text() == "Facts"
                    page.go_forward()
                    page.reload()
                    assert page.locator(".reading-mode [aria-current]").inner_text() == "FLORA Insight"
                    for perspective in ("Forces", "Landscape", "Inside"):
                        page.get_by_role("link", name=perspective, exact=True).click()
                        assert parse_qs(urlsplit(page.url).query) == {**state, "stream": [perspective.lower()]}
                if label == "mobile":
                    page.evaluate("document.documentElement.style.zoom='2'")
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / "customer-service-insight-200pct.jpg", quality=76)
                assert page.goto(route + "?detail=private").status in {403, 404}
                assert page.goto(route + "?workspace=private").status == 403
                page.close()
                print(f"PASS {label}", flush=True)
        finally:
            browser.close()
            server.shutdown()


if __name__ == "__main__":
    destination = Path(sys.argv[1])
    destination.mkdir(parents=True, exist_ok=True)
    run(destination)
