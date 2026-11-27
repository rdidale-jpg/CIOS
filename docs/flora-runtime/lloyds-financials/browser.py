"""Exercise the native financial views on an isolated local Flora server."""
from pathlib import Path
from shutil import which
import os
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, str(Path.cwd()))
from cios.applications.flora.web.app import FloraWebHandler


def check(base_url, output, browser):
    for name, width, height in (('desktop', 1440, 1000), ('ipad-landscape', 1366, 1024),
                                ('ipad-portrait', 1024, 1366)):
        page = browser.new_page(base_url=base_url, viewport={'width': width, 'height': height},
                                has_touch=name != 'desktop')
        income = '/enterprises/lloyds?focus=economics&detail=income'
        assert page.goto(income).status == 200
        expect(page.locator('main')).to_contain_text('1,947')
        expect(page.locator('main h3').get_by_text('Income to statutory profit')).to_be_visible()
        page.evaluate('document.fonts.ready')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=output / (name + '.jpg'), quality=82)
        target = page.get_by_role('link', name='Income to statutory profit', exact=False)
        if name == 'desktop':
            target.focus()
            page.keyboard.press('Enter')
        else:
            target.tap()
        expect(page.locator('#financial-evidence')).to_be_visible()
        assert 'detail=sources' in page.url
        page.reload()
        expect(page.locator('#financial-evidence')).to_contain_text('EDGAR')
        page.go_back()
        expect(page.locator('main')).to_contain_text('1,947')
        assert page.goto('/enterprises/lloyds?focus=economics&detail=divisions').status == 200
        expect(page.locator('main')).to_contain_text('4,293')
        assert page.goto('/enterprises/lloyds?focus=commercial').status == 200
        expect(page.locator('main')).to_contain_text('1,425')
        assert page.goto('/enterprises/lloyds?stream=forces&focus=strategy&detail=objective-efficiency').status == 200
        expect(page.locator('main')).to_contain_text('FY2026 guidance')
        for route in ('/industries/banking', '/industries/aviation', '/enterprises/easyjet',
                      '/enterprises/lloyds/legacy', '/enterprises/lloyds/preview'):
            assert page.goto(route).status == 200
        page.close()
        print(name, 'passed', flush=True)


if __name__ == '__main__':
    captures = Path(sys.argv[1])
    captures.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='flora-financial-browser-') as runtime, sync_playwright() as playwright:
        os.environ.update(FLORA_DATA_DIR=runtime, FLORA_ENVIRONMENT='development',
                          FLORA_AUTH_PROVIDER='local', FLORA_TRUST_PROXY_HEADERS='0')
        os.environ.pop('OPENAI_API_KEY', None)
        with ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler) as server:
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                browser = playwright.chromium.launch(executable_path=which('chromium'))
                check(f'http://127.0.0.1:{server.server_port}', captures, browser)
                browser.close()
            finally:
                server.shutdown()
                thread.join()
