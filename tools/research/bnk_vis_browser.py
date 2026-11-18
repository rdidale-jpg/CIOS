"""Capture the Banking stage journey through the actual loopback FLORA app."""
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


def run(output, *, depth=False):
    with ThreadingHTTPServer(("127.0.0.1", 0), Quiet) as server, sync_playwright() as playwright:
        Thread(target=server.serve_forever, daemon=True).start()
        root = f"http://127.0.0.1:{server.server_port}"
        banking = root + "/industries/banking"
        browser = playwright.chromium.launch(executable_path=shutil.which("chromium"), args=["--no-sandbox"])
        try:
            for label, width, height in (
                ("desktop", 1440, 1000), ("ipad-landscape", 1180, 820), ("ipad-portrait", 820, 1180),
                ("mobile", 390, 844), ("mobile-320", 320, 740),
            ):
                page = browser.new_page(viewport={"width": width, "height": height},
                                        java_script_enabled=label != "mobile-320",
                                        has_touch=label != "desktop", reduced_motion="reduce")
                assert page.goto(root).status == 200
                compact = page.locator(".compact-scene > summary")
                if compact.is_visible():
                    compact.click()
                page.locator('[data-research=banking]:visible').first.click()
                assert urlsplit(page.url).path == "/industries/banking"
                page.screenshot(path=output / f"after-{label}.jpg", quality=76)
                if compact.is_visible():
                    compact.click()
                    page.screenshot(path=output / f"expanded-{label}.jpg", quality=76)
                    compact.click()
                for key, title in (("customers", "Customers & businesses"), ("funding", "Funding & lending"),
                                   ("payments", "Payments & settlement"), ("providers", "Technology & infrastructure")):
                    if compact.is_visible():
                        compact.click()
                    choice = page.locator(f'.portrait [data-label-id="{key}"]:visible')
                    if label == "desktop":
                        page.keyboard.press("Tab")
                        choice.focus()
                        assert choice.evaluate("el => getComputedStyle(el).outlineStyle") == "solid"
                        page.keyboard.press("Enter")
                    else:
                        choice.tap()
                    assert page.locator("main h1").inner_text() == title
                    assert page.locator(".reading-mode [aria-current]").inner_text() == "Facts"
                    page.screenshot(path=output / f"{key}-facts-{label}.jpg", quality=76)
                    page.get_by_role("link", name="FLORA Insight", exact=True).click()
                    assert page.locator("main h1").inner_text() == title
                    assert parse_qs(urlsplit(page.url).query)["detail"] == [key]
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / f"{key}-insight-{label}.jpg", quality=76)
                    if depth and label == "mobile":
                        page.evaluate("document.documentElement.style.zoom='2'")
                        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                        page.screenshot(path=output / f"{key}-insight-200pct.jpg", quality=76)
                        page.evaluate("document.documentElement.style.zoom=''")
                    page.go_back()
                    assert page.locator(".reading-mode [aria-current]").inner_text() == "Facts"
                    page.go_forward()
                    page.reload()
                    assert page.locator(".reading-mode [aria-current]").inner_text() == "FLORA Insight"
                page.locator("main").get_by_role("link",name="Lloyds technology & data").click()
                assert urlsplit(page.url).path == "/enterprises/lloyds"
                page.go_back()
                assert "detail=providers" in page.url
                assert page.goto(banking + "?detail=funding").status == 200
                page.locator("main").get_by_role("link",name="Nationwide Group earnings").click()
                assert "selected=nationwide" in page.url
                assert "6,378" in page.locator("main").inner_text()
                assert page.goto(root + "/?stream=forces").status == 200
                page.get_by_role("link",name="Explore these forces in Banking").click()
                assert "13 July 2026" in page.locator(".reading-pulse").inner_text()
                if label == "mobile":
                    page.evaluate("document.documentElement.style.zoom='2'")
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=output / "forces-200pct.jpg", quality=76)
                page.close()
                print(f"PASS {label}", flush=True)
        finally:
            browser.close()
            server.shutdown()


if __name__ == "__main__":
    destination = Path(sys.argv[1])
    destination.mkdir(parents=True, exist_ok=True)
    run(destination, depth="--depth" in sys.argv)
