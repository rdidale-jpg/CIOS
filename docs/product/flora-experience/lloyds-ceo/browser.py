"""Capture the real public Gold Standard route on an isolated HTTP server."""
import argparse
from http.server import ThreadingHTTPServer
import os
from pathlib import Path
from shutil import which
import sys
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, str(Path.cwd()))
from cios.applications.flora.web.app import FloraWebHandler

PATH = '/enterprises/lloyds/preview/gold'
DEVICES = {'desktop': (1440, 1000), 'ipad-landscape': (1366, 1024), 'ipad-portrait': (1024, 1366)}


def inspect(page, output, device, phase):
    route = PATH + '?stream=forces&focus=strategy'
    assert page.goto(route).status == 200
    expect(page.locator('main h1')).to_have_text('Strategy & change')
    if phase == 'after':
        goals = page.get_by_role('link', name='Goals & tests of progress')
        if device == 'desktop':
            goals.click()
        else:
            goals.tap()
        expect(page.locator('main')).to_contain_text('Test progress')
        selected = page.url
        page.reload()
        assert page.url == selected
        page.go_back()
        expect(page.get_by_role('link', name='Goals & tests of progress')).to_be_visible()
        page.go_forward()
        expect(page.locator('main')).to_contain_text('Test progress')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.evaluate('document.fonts.ready')
    page.screenshot(path=output / f'{phase}-{device}.jpg', quality=82)
    if phase == 'after':
        for query, copy in [
            ('focus=economics&detail=comparison', 'Balance growth and capital'),
            ('stream=inside&focus=operations&detail=people', 'How to trace accountability'),
            ('stream=inside&focus=operations&detail=credit&subject=commercial', 'From Commercial Banking'),
        ]:
            assert page.goto(PATH + '?' + query).status == 200
            expect(page.locator('main')).to_contain_text(copy)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        focused = page.get_by_role('link', name='Risk capability', exact=True)
        focused.focus()
        page.keyboard.press('Enter')
        expect(page.locator('main h1')).to_have_text('Capabilities')
        expect(page.locator('main')).to_contain_text('From Commercial Banking')
        page.locator('main a[href*="detail=sources"]').click()
        expect(page.locator('main h2')).to_have_text('Evidence, dates & boundaries')
    for route in ('/enterprises/lloyds', '/enterprises/lloyds/preview', '/enterprises/easyjet'):
        assert page.goto(route).status == 200


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['before', 'after'])
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='flora-lloyds-ceo-') as runtime, sync_playwright() as driver:
        os.environ.update(FLORA_DATA_DIR=runtime, FLORA_ENVIRONMENT='development',
                          FLORA_AUTH_PROVIDER='local', FLORA_TRUST_PROXY_HEADERS='0')
        os.environ.pop('OPENAI_API_KEY', None)
        with ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler) as server:
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                browser = driver.chromium.launch(executable_path=which('chromium'))
                for device, (width, height) in DEVICES.items():
                    page = browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',
                                            viewport={'width': width, 'height': height},
                                            has_touch=device != 'desktop')
                    inspect(page, args.output, device, args.phase)
                    page.close()
                browser.close()
            finally:
                server.shutdown()
                thread.join()
    print(f'{args.phase}: {len(DEVICES)} Chromium viewports passed')


if __name__ == '__main__':
    main()
