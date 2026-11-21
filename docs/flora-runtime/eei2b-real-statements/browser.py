"""Loopback proof of the real annual statement view and scoped withdrawal."""
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
from cios.applications.flora.research_intelligence import model, registry
from cios.applications.flora.web.app import FloraWebHandler
from tests.test_flora_eei2b import PATH

output = Path(sys.argv[1])
output.mkdir(parents=True, exist_ok=True)
proof = []
with TemporaryDirectory() as storage, MonkeyPatch.context() as patch, sync_playwright() as p:
    root = Path(storage)
    shutil.copytree('enterprise-knowledge', root / 'enterprise-knowledge')
    patch.setattr(model, 'REPO', root)
    patch.setattr(registry, 'REPO', root)
    patch.setattr(model, 'DATA', root / 'enterprise-knowledge/banking/research-model/Assessment-Overlay.json')
    patch.setenv('FLORA_DATA_DIR', str(root / 'app'))
    patch.setenv('FLORA_ENVIRONMENT', 'development')
    patch.setenv('FLORA_AUTH_PROVIDER', 'local')
    patch.delenv('FLORA_PILOT_DIR', raising=False)
    record = root / PATH
    original = record.read_text()
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    browser = p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
    base = f'http://127.0.0.1:{server.server_port}'
    route = '/industries/banking?stream=landscape&selected=nationwide'
    try:
        for name, width, height in [('desktop', 1440, 1000), ('ipad-landscape', 1194, 834), ('ipad-portrait', 834, 1194)]:
            page = browser.new_page(base_url=base, viewport={'width': width, 'height': height}, has_touch=name != 'desktop')
            assert page.goto(route).ok
            summary = page.locator('section[aria-labelledby="eei-summary"]')
            expect(summary).to_contain_text('Cash flow statement')
            expect(summary).to_contain_text('38,411')
            expect(summary).to_contain_text('361 days')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            summary.scroll_into_view_if_needed()
            page.screenshot(path=output / f'facts-{name}.jpg', quality=85)
            link = page.get_by_role('link', name='FLORA Insight', exact=True)
            if name == 'desktop':
                link.focus()
                link.press('Enter')
            else:
                link.tap()
            page.wait_for_url(lambda url: 'reading=insight' in url)
            expect(summary).to_contain_text('+8,928')
            expect(summary).to_contain_text('each contributed cash')
            summary.scroll_into_view_if_needed()
            page.screenshot(path=output / f'insight-{name}.jpg', quality=85)
            page.go_back()
            expect(summary).to_contain_text('3,904')
            data = json.loads(original)
            data['withdrawn'] = True
            record.write_text(json.dumps(data))
            try:
                response = page.reload()
                assert response.ok and response.headers['cache-control'] == 'no-store'
                expect(summary).to_contain_text('No eligible figures')
                assert '3,904' not in page.content() and '38,411' not in page.content()
            finally:
                record.write_text(original)
            proof.append({'viewport': name, 'facts_insight': True, 'history_and_withdrawal': True})
            page.close()
    finally:
        browser.close()
        server.shutdown()
        server.server_close()
        worker.join(2)
(output / 'browser.json').write_text(json.dumps({
    'checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'observations': proof,
}, indent=2) + '\n')
print(proof)
