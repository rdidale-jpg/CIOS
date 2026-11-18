"""Capture and exercise the Banking enterprise cohort in the loopback app."""
from http.server import ThreadingHTTPServer
from pathlib import Path
import shutil
import sys
from threading import Thread
from time import monotonic
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright

from cios.applications.flora.web.app import FloraWebHandler


class Quiet(FloraWebHandler):
    def log_message(self, *_args):
        pass


SCENES = (
    ("natwest-landscape", "/industries/banking?selected=natwest", "National Westminster Bank PLC"),
    ("hsbc-forces", "/industries/banking?selected=hsbc-uk&stream=forces", "HSBC UK Bank Plc"),
    ("nationwide-landscape", "/industries/banking?selected=nationwide", "Nationwide"),
    ("starling-inside", "/industries/banking?selected=starling&stream=inside", "Starling Bank Limited"),
    ("boe-inside", "/industries/banking?selected=boe&stream=inside", "Bank of England"),
)
VIEWPORTS = (("desktop", 1440, 1000), ("ipad-landscape", 1180, 820), ("ipad-portrait", 820, 1180),
             ("mobile", 390, 844), ("mobile-320", 320, 740))


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    with ThreadingHTTPServer(("127.0.0.1", 0), Quiet) as server, sync_playwright() as playwright:
        Thread(target=server.serve_forever, daemon=True).start()
        origin = f"http://127.0.0.1:{server.server_port}"
        browser = playwright.chromium.launch(executable_path=shutil.which("chromium"), args=["--no-sandbox"])
        try:
            for label, width, height in VIEWPORTS:
                desktop = label == "desktop"
                page = browser.new_page(viewport={"width": width, "height": height},
                                        has_touch=not desktop, java_script_enabled=label != "mobile-320",
                                        reduced_motion="reduce")
                loads = []
                for name, path, heading in SCENES:
                    started = monotonic()
                    assert page.goto(origin + path).status == 200
                    loads.append(monotonic() - started)
                    main = page.get_by_role("main")
                    assert heading in main.get_by_role("heading", level=1).inner_text() or name == "nationwide-landscape"
                    current = page.locator(".reading-mode [aria-current]")
                    expect(current).to_have_text("Facts")
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / f"{name}-facts-{label}.jpg", quality=75)
                    choice = page.get_by_role("link", name="FLORA Insight", exact=True)
                    if desktop:
                        page.keyboard.press("Tab")
                        choice.focus()
                        assert choice.evaluate("el => getComputedStyle(el).outlineStyle") == "solid"
                        page.keyboard.press("Enter")
                    else:
                        choice.tap()
                    expect(current).to_have_text("FLORA Insight")
                    assert heading in main.get_by_role("heading", level=1).inner_text() or name == "nationwide-landscape"
                    before = parse_qs(urlsplit(path).query)
                    after = parse_qs(urlsplit(page.url).query)
                    assert all(after[key] == value for key, value in before.items())
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / f"{name}-insight-{label}.jpg", quality=75)
                    page.go_back()
                    expect(current).to_have_text("Facts")
                    page.go_forward()
                    page.reload()
                    expect(current).to_have_text("FLORA Insight")
                assert page.goto(origin + "/industries/banking").ok
                page.get_by_role("navigation", name="Banking cohort").get_by_role(
                    "link", name="Starling Bank Limited", exact=True).click()
                page.get_by_role("link", name="Inside", exact=True).click()
                assert parse_qs(urlsplit(page.url).query)["selected"] == ["starling"]
                assert page.get_by_role("heading", name="Durable capabilities").is_visible()
                if label == "mobile":
                    page.evaluate("document.documentElement.style.zoom='2'")
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / "starling-200pct.jpg", quality=75)
                for route in ("/industries/aviation?lens=porter", "/industries/technology/experience",
                              "/industries/technology/experience/enterprise?enterprise=equinix",
                              "/industries/technology/experience/operating-model",
                              "/industries/banking?selected=nationwide"):
                    assert page.goto(origin + route).status == 200
                assert page.goto(origin + "/industries/banking?stream=forces&detail=private").status == 404
                assert page.goto(origin + "/enterprises/lloyds?stream=inside&workspace=private").status == 403
                page.close()
                print(f"PASS {label}; initial loopback loads {min(loads):.2f}–{max(loads):.2f}s", flush=True)
        finally:
            browser.close()
            server.shutdown()


if __name__ == "__main__":
    run(Path(sys.argv[1]))
