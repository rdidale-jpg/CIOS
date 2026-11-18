"""Capture and exercise the first integrated FLORA slice in the loopback app."""
from http.server import ThreadingHTTPServer
from pathlib import Path
import shutil
import sys
from threading import Thread
from time import monotonic
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright

from cios.applications.flora.web.app import FloraWebHandler


class Quiet(FloraWebHandler):
    def log_message(self, *_args):
        pass


SCENES = (
    ("uk-forces", "/?stream=forces&detail=political", "Political conditions"),
    ("banking-forces", "/industries/banking?stream=forces&detail=buyer-power", "Buyer power"),
    ("lloyds-landscape", "/enterprises/lloyds", "Customer funding and earnings"),
    ("lloyds-inside", "/enterprises/lloyds?stream=inside", "How Lloyds operates"),
    ("lloyds-forces", "/enterprises/lloyds?stream=forces", "Conditions affecting Lloyds"),
    ("easyjet-landscape", "/enterprises/easyjet/preview", "easyJet’s business and network"),
    ("easyjet-inside", "/enterprises/easyjet/preview?stream=inside", "How easyJet operates"),
    ("easyjet-forces", "/enterprises/easyjet/preview?stream=forces", "Conditions affecting easyJet"),
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
                    assert main.get_by_role("heading", name=heading, exact=True).is_visible()
                    current = page.locator(".reading-mode [aria-current]")
                    assert current.inner_text() == "Facts"
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
                    assert current.inner_text() == "FLORA Insight"
                    assert main.get_by_role("heading", name=heading, exact=True).is_visible()
                    before = parse_qs(urlsplit(path).query)
                    after = parse_qs(urlsplit(page.url).query)
                    assert all(after[key] == value for key, value in before.items())
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / f"{name}-insight-{label}.jpg", quality=75)
                    page.go_back()
                    assert current.inner_text() == "Facts"
                    page.go_forward()
                    page.reload()
                    assert current.inner_text() == "FLORA Insight"
                assert page.goto(origin + "/enterprises/easyjet/preview?stream=inside").ok
                ability = page.get_by_role("link", name="Fleet management", exact=True).first
                ability.click() if desktop else ability.tap()
                assert urlsplit(page.url).fragment == "ability-0"
                scene = page.locator(".compact-scene > summary")
                if scene.is_visible():
                    scene.click()
                page.get_by_role("navigation", name="Capabilities in the illustration").get_by_role(
                    "link", name="Network Planning", exact=True).filter(visible=True).click()
                assert page.get_by_role("heading", name="Network Planning", exact=True).is_visible()
                if label == "mobile":
                    page.evaluate("document.documentElement.style.zoom='2'")
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / "easyjet-inside-200pct.jpg", quality=75)
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
