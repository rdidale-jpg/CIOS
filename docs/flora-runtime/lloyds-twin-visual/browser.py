"""Capture the approved baseline and visual candidate with loopback Chromium."""
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import expect, sync_playwright
from pytest import MonkeyPatch

sys.path.insert(0, str(Path.cwd()))
from cios.applications.flora.web.app import FloraWebHandler

output = Path(sys.argv[1]).resolve()
phase = sys.argv[2]
output.mkdir(parents=True, exist_ok=True)
evidence = []
with TemporaryDirectory() as directory, MonkeyPatch.context() as patch, sync_playwright() as playwright:
    patch.setenv('FLORA_DATA_DIR', directory)
    patch.setenv('FLORA_ENVIRONMENT', 'development')
    patch.setenv('FLORA_AUTH_PROVIDER', 'local')
    patch.delenv('FLORA_PILOT_DIR', raising=False)
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    browser = playwright.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
    try:
        for device, width, height in (('desktop', 1440, 1000), ('ipad-landscape', 1194, 834), ('ipad-portrait', 834, 1194)):
            page = browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',
                                    viewport={'width': width, 'height': height}, has_touch=device != 'desktop')
            page.set_default_timeout(8000)
            assert page.goto('/enterprises/lloyds').ok
            if phase != 'main':
                page.get_by_role('link', name='Explore the Lloyds flagship').click()
            if phase == 'after':
                expect(page.get_by_role('heading', name='Lloyds Banking Group', exact=True)).to_be_visible()
                expect(page.locator('.ltv-grid .ltv-division')).to_have_count(3)
                assert page.locator('.ltv-hero img').evaluate('(image) => image.complete && image.naturalWidth > 0')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=output / f'{phase}-{device}.jpg', quality=83)
            if phase == 'after':
                nav = page.get_by_role('navigation', name='Twin sections')
                nav.get_by_role('link', name='Inside Lloyds').click()
                expect(page.get_by_role('heading', name='Customer operations and their dependencies')).to_be_in_viewport()
                page.screenshot(path=output / f'inside-{device}.jpg', quality=83)
                page.get_by_role('link', name='FLORA Insight', exact=True).click()
                thread = page.get_by_role('list', name='Follow the strategic issue')
                expect(thread.get_by_role('link')).to_have_count(5)
                expect(page.locator('#ltv-thread')).to_contain_text('Core renewal and application retirement matter')
                page.get_by_role('navigation', name='Twin sections').get_by_role('link', name='Core renewal').click()
                page.screenshot(path=output / f'insight-{device}.jpg', quality=83)
                thread.get_by_role('link', name='Operations').click()
                expect(page.get_by_role('heading', name='Credit and customer service')).to_be_visible()
                page.go_back()
                expect(page.locator('#ltv-thread')).to_be_visible()
                page.locator('#llf-benchmark > summary').click()
                expect(page.locator('#llf-benchmark')).to_contain_text('118,762')
            evidence.append({'viewport': device, 'phase': phase, 'no_page_overflow': True,
                             'inside_thread_mode_history_and_peer': phase == 'after'})
            page.close()
    finally:
        browser.close()
        server.shutdown()
        server.server_close()
        worker.join(2)
(output / f'{phase}.json').write_text(json.dumps({
    'checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'observations': evidence,
}, indent=2) + '\n')
