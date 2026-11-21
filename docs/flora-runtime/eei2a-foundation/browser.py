"""Real loopback Economics proof with an isolated, labelled synthetic view."""
from http.server import ThreadingHTTPServer
from pathlib import Path
import json
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import expect, sync_playwright
from pytest import MonkeyPatch

sys.path.insert(0, str(Path.cwd()))
from cios.applications.flora import easyjet_capabilities as easyjet, enterprise_economics as economics
from cios.applications.flora.web.app import FloraWebHandler
from tests.test_flora_eei2a import example

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
original = easyjet.main
record, subject = example('corporate.easyjet.com', 'Synthetic travel group', 'GBP')


def fixture_main(ctx):
    return original(ctx) + economics.source_statement_summary(record, subject=subject, insight=ctx.reading == 'insight', fixture=True)


with TemporaryDirectory() as storage, MonkeyPatch.context() as patch, sync_playwright() as p:
    patch.setenv('FLORA_DATA_DIR', storage)
    patch.setenv('FLORA_ENVIRONMENT', 'development')
    patch.setenv('FLORA_AUTH_PROVIDER', 'local')
    patch.delenv('FLORA_PILOT_DIR', raising=False)
    patch.setattr(easyjet, 'main', fixture_main)
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    browser = p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
    base = f'http://127.0.0.1:{server.server_port}'
    proof = []
    try:
        for name, width, height in [('desktop', 1440, 1000), ('ipad-landscape', 1194, 834), ('ipad-portrait', 834, 1194)]:
            page = browser.new_page(base_url=base, viewport={'width': width, 'height': height}, has_touch=name != 'desktop')
            for company, route in (
                ('nationwide', '/industries/banking?stream=landscape&selected=nationwide'),
                ('synthetic', '/enterprises/easyjet/preview?stream=landscape'),
            ):
                assert page.goto(route).ok
                summary = page.locator('section[aria-labelledby="eei-summary"]')
                expect(summary).to_contain_text('Income statement')
                expect(summary).to_contain_text('Balance sheet')
                expect(summary).to_contain_text('Cash flow statement')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                if company == 'nationwide':
                    expect(summary).to_contain_text('£6,378m')
                    expect(summary).to_contain_text('No eligible figures')
                else:
                    expect(summary).to_contain_text('Synthetic review fixture')
                    expect(summary).to_contain_text('GBP 72m')
                summary.scroll_into_view_if_needed()
                page.screenshot(path=out / f'{company}-{name}.jpg', quality=85)
            page.get_by_role('link', name='FLORA Insight', exact=True).click()
            page.wait_for_url(lambda url: 'reading=insight' in url)
            expect(summary).to_contain_text('Assets and obligations describe')
            page.go_back()
            expect(summary).to_contain_text('GBP 72m')
            record['withdrawn'] = True
            assert page.reload().ok
            expect(summary).to_have_count(0)
            assert 'GBP 72m' not in page.content()
            record.pop('withdrawn')
            proof.append({'viewport': name, 'eligible_nationwide': True, 'labelled_synthetic': True, 'history_and_withdrawal': True})
            page.close()
    finally:
        browser.close()
        server.shutdown()
        server.server_close()
        thread.join(2)
(out / 'browser.json').write_text(json.dumps({
    'checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'results': proof,
}, indent=2) + '\n')
print(proof)
