"""Capture exact predecessor and current browser evidence from isolated loopback instances."""
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
from cios.applications.flora.research_intelligence import model
from cios.applications.flora.web.app import FloraWebHandler

output = Path(sys.argv[1]).resolve()
output.mkdir(parents=True, exist_ok=True)
phase = sys.argv[2]
route = '/industries/technology/experience/enterprise?detail=financials'
observations = []
with TemporaryDirectory() as temporary, MonkeyPatch.context() as patch, sync_playwright() as playwright:
    root = Path(temporary)
    patch.setenv('FLORA_DATA_DIR', str(root / 'app'))
    patch.setenv('FLORA_ENVIRONMENT', 'development')
    patch.setenv('FLORA_AUTH_PROVIDER', 'local')
    patch.delenv('FLORA_PILOT_DIR', raising=False)
    if phase == 'after':
        from cios.applications.flora.research_intelligence.statement_sources import PACKAGE
        shutil.copytree(model.REPO / PACKAGE, root / PACKAGE)
        patch.setattr(model, 'REPO', root)
        record = root / PACKAGE / 'EEI3-EQUINIX-10K-2025.json'
        original = record.read_text()
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = f'http://127.0.0.1:{server.server_port}'
    browser = playwright.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
    try:
        for name, width, height in [('desktop', 1440, 1000), ('ipad-landscape', 1194, 834), ('ipad-portrait', 834, 1194)]:
            page = browser.new_page(base_url=base, viewport={'width': width, 'height': height}, has_touch=name != 'desktop')
            response = page.goto(route)
            assert response.ok, response.status
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            summary = page.locator('#eei-summary')
            if phase == 'before':
                expect(summary).to_have_count(0)
                page.locator('#enterprise-detail').scroll_into_view_if_needed()
            else:
                expect(summary).to_have_text('Financial statements')
                expect(page.get_by_role('region', name='Balance sheet')).to_contain_text('40,141')
                summary.evaluate("(node) => node.parentElement.scrollIntoView({block:'start'})")
            page.screenshot(path=output / f'{phase}-{name}.jpg', quality=82)
            if phase == 'after':
                nav = page.get_by_role('link', name='FLORA Insight', exact=True)
                if name == 'desktop':
                    nav.focus()
                    nav.press('Enter')
                else:
                    nav.tap()
                page.wait_for_url(lambda url: 'reading=insight' in url)
                expect(page.locator('.eei-annual')).to_contain_text('+5.36')
                page.screenshot(path=output / f'insight-{name}.jpg', quality=82)
                page.go_back()
                expect(page.get_by_role('region', name='Cash flow statement')).to_contain_text('3,911')
                try:
                    record.write_text(json.dumps({**json.loads(original), 'withdrawn': True}))
                    assert page.reload().ok
                    expect(page.get_by_role('region', name='Cash flow statement')).not_to_contain_text('3,911')
                    expect(page.get_by_role('region', name='Cash flow statement')).to_contain_text('3,249')
                finally:
                    record.write_text(original)
            observations.append({'viewport': name, 'before_after': phase, 'reading_history_withdrawal': phase == 'after'})
            page.close()
    finally:
        browser.close()
        server.shutdown()
        server.server_close()
        worker.join(2)
(output / f'{phase}.json').write_text(json.dumps({
    'checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'observations': observations,
}, indent=2) + '\n')
