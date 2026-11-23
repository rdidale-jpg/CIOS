"""Capture Flora's existing public industry catalogue with challenge data absent."""
from pathlib import Path
import shutil
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

from cios.applications.flora import design_system
from cios.applications.flora.web.app import FloraWebHandler

handler = object.__new__(FloraWebHandler)
handler.path = '/industries'
handler.headers = {}
handler.requestline = 'GET /industries HTTP/1.1'
handler.storage_status = {'ready': True}
responses = []
handler._body = lambda *args, **kwargs: responses.append(args)
handler.send_error = lambda code, message: responses.append((code, message))
handler.do_GET()
(raw, _, status), = responses
assert status == 200 and isinstance(raw, bytes)

output = Path(__file__).parent / 'previews'
output.mkdir(exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=shutil.which('chromium'),
                                           args=['--no-sandbox'])
    for label, width, height in (
        ('desktop', 1280, 850), ('ipad-portrait', 768, 1024), ('ipad-landscape', 1024, 768),
    ):
        tablet = label.startswith('ipad')
        page = browser.new_page(viewport={'width': width, 'height': height},
                                is_mobile=tablet, has_touch=tablet)

        def serve(route):
            path = urlsplit(route.request.url).path
            if path == '/industries':
                route.fulfill(body=raw, content_type='text/html; charset=utf-8')
            elif path.startswith('/design-system/assets/'):
                content, mime = design_system.asset(path.rsplit('/', 1)[-1])
                route.fulfill(body=content, content_type=mime)
            else:
                route.abort()

        page.route('**/*', serve)
        page.goto('http://flora-fixture.test/industries', wait_until='networkidle')
        assert page.get_by_role('main').is_visible()
        assert page.locator('[data-commercial-change]').count() == 0
        assert page.evaluate('document.documentElement.scrollWidth') <= width
        page.screenshot(path=str(output / f'catalogue-{label}.jpg'), quality=85)
        page.close()
    browser.close()
