"""Run Technology journey checks against an isolated local handler."""
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

base = '/industries/technology/experience'
output = Path(sys.argv[1])
phase = sys.argv[2]
output.mkdir(parents=True, exist_ok=True)
results = []

with TemporaryDirectory() as storage, MonkeyPatch.context() as patch, sync_playwright() as p:
    patch.setenv('FLORA_DATA_DIR', storage)
    patch.setenv('FLORA_ENVIRONMENT', 'development')
    patch.setenv('FLORA_AUTH_PROVIDER', 'local')
    patch.delenv('FLORA_PILOT_DIR', raising=False)
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    origin = f'http://127.0.0.1:{server.server_port}'
    browser = p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
    try:
        for label, width, height in [('desktop', 1440, 1000), ('ipad-landscape', 1194, 834),
                                     ('ipad-portrait', 834, 1194), ('mobile', 390, 844)]:
            page = browser.new_page(base_url=origin, viewport={'width': width, 'height': height},
                                    has_touch=label != 'desktop')
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            assert page.goto('/industries').ok
            page.locator(f'a[href="{base}"]').first.click()
            page.wait_for_url(origin + base)
            expect(page.locator('.exp-hotspot')).to_have_count(8)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=output / f'{phase}-landscape-{label}.jpg', quality=83)
            provider = base + '/enterprise?enterprise=nvidia&district=ai'
            assert page.goto(provider).ok
            page.screenshot(path=output / f'{phase}-nvidia-{label}.jpg', quality=83)
            if phase == 'after':
                main = page.locator('[data-region="main"]')
                expect(main).to_have_attribute('data-reading', 'facts')
                expect(main.get_by_text('UK programmes & activity')).to_be_visible()
                selector = page.get_by_role('link', name='FLORA Insight', exact=True)
                if label == 'desktop':
                    selector.focus()
                    selector.press('Enter')
                else:
                    selector.tap()
                page.wait_for_url(lambda url: 'enterprise=nvidia' in url and 'reading=insight' in url)
                expect(main.get_by_text('Commercial pressures')).to_be_visible()
                page.go_back()
                expect(main).to_have_attribute('data-reading', 'facts')
                page.go_forward()
                expect(main).to_have_attribute('data-reading', 'insight')
                assert page.reload().ok
                expect(main).to_have_attribute('data-reading', 'insight')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.screenshot(path=output / f'after-insight-{label}.jpg', quality=83)
                assert page.goto(base + '/participants').ok
                expect(page.locator('tr[data-participant]')).to_have_count(80)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert page.goto(base + '/enterprise?enterprise=equinix&detail=financials').ok
                expect(main.locator('.exp-financials')).to_contain_text('$9.217bn')
                expect(main.locator('.eei-annual')).to_contain_text('3,911')
                main.get_by_role('navigation', name='Reading mode', exact=True).get_by_role('link', name='FLORA Insight').click()
                expect(main).to_have_attribute('data-reading', 'insight')
                expect(main.locator('.eei-annual')).to_contain_text('3,911')
                main.get_by_role('navigation', name='Financial reading mode', exact=True).get_by_role('link', name='FLORA Insight').click()
                expect(main.locator('.eei-annual')).to_contain_text('+5.36')
                page.go_back()
                expect(main.locator('.eei-annual')).to_contain_text('3,911')
                assert page.goto('/industries/technology/providers?provider=nvidia').ok
                assert page.goto('/industries/technology?lens=uses&relationship=programme-67-1').ok
                assert page.request.get(base + '/enterprise?enterprise=nvidia&reading=insight&workspace=private').status == 403
            assert not errors, errors
            results.append({'viewport': label, 'artwork_districts': 8, 'layout_pass': True,
                            'reading_history_directory_and_identity': phase == 'after'})
            page.close()
    finally:
        browser.close()
        server.shutdown()
        server.server_close()
        worker.join(2)

(output / f'{phase}-browser.json').write_text(json.dumps({
    'checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'results': results,
}, indent=2) + '\n')
print(results)
