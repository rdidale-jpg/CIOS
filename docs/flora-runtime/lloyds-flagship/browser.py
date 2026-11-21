"""Capture the Lloyds flagship on the existing public journey in loopback Chromium."""
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

out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
observations = []
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
        for name, width, height in [('desktop', 1440, 1000), ('ipad-landscape', 1194, 834),
                                    ('ipad-portrait', 834, 1194)]:
            page = browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',
                                    viewport={'width': width, 'height': height}, has_touch=name != 'desktop')
            assert page.goto('/enterprises/lloyds').ok
            panel = page.get_by_role('region', name='Lloyds flagship overview')
            expect(panel.get_by_role('heading', name='Renew the bank while it runs')).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=out / f'facts-{name}.jpg', quality=83)
            page.get_by_role('link', name='FLORA Insight', exact=True).click()
            expect(panel).to_contain_text('Core renewal and application retirement matter')
            panel.get_by_text('Risks & pressures', exact=True).click()
            expect(panel.get_by_text('Time-bound pressure · incident reporting')).to_be_visible()
            panel.get_by_text('Peer evidence · service operations', exact=True).click()
            expect(panel.get_by_text('118,762', exact=True)).to_be_visible()
            panel.get_by_text('Risks & pressures', exact=True).evaluate(
                "(node) => node.scrollIntoView({block:'start'})")
            page.screenshot(path=out / f'insight-{name}.jpg', quality=83)
            panel.get_by_role('link', name='Operations', exact=True).click()
            expect(page.get_by_role('heading', name='Credit and customer service')).to_be_visible()
            page.go_back()
            expect(panel.get_by_role('heading', name='Renew the bank while it runs')).to_be_visible()
            observations.append({'viewport': name, 'facts_insight': True, 'peer_evidence': True,
                                 'operating_detail_and_back': True})
            page.close()
    finally:
        browser.close()
        server.shutdown()
        server.server_close()
        worker.join(2)
(out / 'browser.json').write_text(json.dumps({
    'checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'observations': observations,
}, indent=2) + '\n')
