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
            panel = page.locator('.llf')
            count = panel.locator('details').count()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=output / f'{phase}-{device}.jpg', quality=83)
            if phase == 'after':
                expect(panel.get_by_role('heading', name='Lloyds Banking Group', exact=True)).to_be_visible()
                assert count == 0 and 'Research inspection' not in panel.inner_text()
                segments = panel.get_by_role('navigation', name='Reporting segments')
                segments.get_by_role('link', name='Commercial Banking').click()
                expect(panel.locator('#llf-commercial')).to_be_visible()
                expect(panel.locator('#llf-retail')).to_be_hidden()
                panel.locator('#llf-commercial').get_by_role('link', name='Group operating examples').click()
                expect(panel.locator('#ltv-inside')).to_be_in_viewport()
                page.get_by_role('link', name='FLORA Insight', exact=True).click()
                thread = panel.get_by_role('navigation', name='Follow the strategic issue')
                thread.get_by_role('link', name='Operations').click()
                expect(panel.locator('#llf-stage-operations')).to_be_visible()
                assert page.request.get('/enterprises/lloyds?stream=landscape&detail=flagship&lens=inspection').status == 403
                perspectives = panel.get_by_role('navigation', name='Perspectives', exact=True)
                perspectives.get_by_role('link', name='SWOT', exact=True).click()
                expect(panel.locator('.llf-swot > nav a')).to_have_count(4)
                panel.get_by_role('link', name='Weakness', exact=True).click()
                expect(panel.get_by_role('navigation', name='Weakness themes').get_by_role('link')).to_have_count(2)
                panel.get_by_role('link', name='migration exposure', exact=True).click()
                expect(panel.locator('#llf-swot-1')).to_contain_text('remaining estate')
                page.screenshot(path=output / f'swot-{device}.jpg', quality=83)
                perspectives.get_by_role('link', name='Strategy timeline').click()
                panel.locator('.llf-timeline nav a').last.click()
                expect(panel.locator('#llf-timeline-3')).to_contain_text('management plans')
                perspectives.get_by_role('link', name='Peer evidence · service operations').click()
                expect(panel.locator('#llf-benchmark meter')).to_have_count(3)
                expect(panel.locator('#llf-benchmark')).to_contain_text('cannot rank service quality')
                page.go_back()
                expect(panel.locator('#llf-timeline-3')).to_be_visible()
            evidence.append({'viewport': device, 'phase': phase, 'no_page_overflow': True,
                             'disclosure_count': count, 'choices_sources_and_history': phase == 'after'})
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
