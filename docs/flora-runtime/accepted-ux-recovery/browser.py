"""Real loopback journeys; no production, provider or canonical writes.

Run from the checkout to capture, with this script's absolute path when the
checkout is the baseline: python browser.py OUTPUT before|after.
"""
from http.server import ThreadingHTTPServer
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

sys.path.insert(0, str(Path.cwd()))
from playwright.sync_api import sync_playwright, expect
from cios.applications.flora.web.app import FloraWebHandler

output, phase = Path(sys.argv[1]).resolve(), sys.argv[2]
output.mkdir(parents=True, exist_ok=True)
observations = []
with TemporaryDirectory() as directory, sync_playwright() as playwright:
    os.environ.update(FLORA_DATA_DIR=directory, FLORA_ENVIRONMENT='development',
                      FLORA_AUTH_PROVIDER='local', FLORA_TRUST_PROXY_HEADERS='0')
    os.environ.pop('OPENAI_API_KEY', None)
    server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    browser = playwright.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
    try:
        for device, width, height in [('desktop', 1440, 1000), ('ipad-landscape', 1194, 834), ('ipad-portrait', 834, 1194)]:
            errors, failed = [], []
            page = browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',
                                    viewport={'width': width, 'height': height}, has_touch=device != 'desktop')
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('requestfailed', lambda request: failed.append(request.url))
            page.set_default_timeout(10000)

            def capture(name):
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), name
                page.screenshot(path=output / f'{phase}-{device}-{name}.jpg', quality=80)

            assert page.goto('/').status == 200
            primary = page.get_by_role('navigation', name='Primary product navigation')
            primary.get_by_role('link', name='Industries', exact=True).click()
            page.locator('a[href="/industries/banking"]:visible').first.click()
            capture('banking')
            page.locator('a[href="/enterprises/lloyds"]:visible').first.click()
            capture('lloyds-arrival')
            expect(page.get_by_role('navigation', name='Explore this enterprise')).to_contain_text('Economics')
            page.get_by_role('link', name='Explore Lloyds' if phase == 'after' else 'Explore the Lloyds flagship', exact=True).click()
            capture('lloyds-overview')
            expect(page.locator('.ltv-hero img')).to_be_visible()
            assert page.locator('.ltv-hero img').evaluate('(image) => image.complete && image.naturalWidth > 0')
            if phase == 'after':
                main = page.locator('main')
                expect(page.get_by_role('navigation', name='Reading mode')).to_have_count(0)
                expect(main.locator('details')).to_have_count(0)
                assert 'Reviewed excerpt' not in main.inner_text()
                jump = page.get_by_role('navigation', name='Twin sections')
                jump.get_by_role('link', name='Explore', exact=True).click()
                expect(page.locator('#ltv-inside')).to_be_in_viewport()
                jump.get_by_role('link', name='Investigate', exact=True).focus()
                page.keyboard.press('Enter')
                page.get_by_role('navigation', name='Perspectives', exact=True).get_by_role('link', name='SWOT', exact=True).click()
                quadrants = page.get_by_role('navigation', name='SWOT quadrants')
                themes = []
                for quadrant in ['Strength', 'Weakness', 'Opportunity', 'Threat']:
                    quadrants.get_by_role('link', name=quadrant, exact=True).click()
                    choices = page.get_by_role('navigation', name=quadrant + ' themes')
                    expect(choices.get_by_role('link')).to_have_count(2)
                    for link in choices.get_by_role('link').all():
                        href = link.get_attribute('href')
                        link.click()
                        expect(page.locator(href)).to_be_visible()
                        expect(page.locator(href)).to_contain_text('FLORA Insight')
                        themes.append(href)
                assert len(set(themes)) == 8
                selected = themes[-1]
                page.reload()
                expect(page.locator(selected)).to_be_visible()
                page.go_back()
                expect(page.locator(themes[-2])).to_be_visible()
                page.go_forward()
                expect(page.locator(selected)).to_be_visible()
                capture('swot')
                jump.get_by_role('link', name='Overview', exact=True).click()
                expect(page.locator('#ltv-landscape')).to_be_in_viewport()
                observations.append({'device': device, 'eight_swot_themes': True,
                                     'keyboard_touch_hash_reload_history': True, 'executive_disclosures': 0})
            for stream in ['inside', 'forces']:
                page.get_by_role('navigation', name='Insight streams').get_by_role('link', name=stream.title(), exact=True).click()
                expect(page.locator('main')).to_contain_text('Lloyds')
                if phase == 'after':
                    expect(page.get_by_role('navigation', name='Reading mode')).to_have_count(0)
                    expect(page.locator('main details')).to_have_count(0)
                capture('lloyds-' + stream)
            page.get_by_role('navigation', name='Current scope').get_by_role('link', name='Banking', exact=True).click()
            assert page.url.endswith('/industries/banking')
            assert page.goto('/').status == 200
            page.get_by_role('navigation', name='Primary product navigation').get_by_role('link', name='Industries', exact=True).click()
            page.locator('a[href="/industries/aviation"]:visible').first.click()
            page.locator('a[href="/enterprises/easyjet"]:visible').first.click()
            capture('easyjet')
            for stream in ['inside', 'forces', 'landscape']:
                page.get_by_role('navigation', name='Insight streams').get_by_role('link', name=stream.title(), exact=True).click()
                expect(page.locator('main')).to_contain_text('easyJet')
                if phase == 'after':expect(page.get_by_role('navigation', name='Reading mode')).to_have_count(0)
            for enterprise in ['lloyds', 'easyjet']:
                page.get_by_role('navigation', name='Primary product navigation').get_by_role('link', name='Enterprises', exact=True).click()
                page.locator(f'a[href="/enterprises/{enterprise}"]:visible').first.click()
                assert page.url.split('?')[0].endswith('/enterprises/' + enterprise)
            assert not errors and not failed, (errors, failed)
            observations.append({'device': device, 'four_native_journeys': True, 'industry_breadcrumb': True,
                                 'aviation_streams': True, 'page_errors': errors, 'failed_requests': failed})
            page.close()
        if phase == 'after':
            context = browser.new_context(java_script_enabled=False)
            page = context.new_page()
            assert page.goto(f'http://127.0.0.1:{server.server_port}/enterprises/lloyds?stream=landscape&detail=flagship').status == 200
            expect(page.locator('[id^="llf-swot-"]')).to_have_count(8)
            assert all(panel.is_visible() for panel in page.locator('[id^="llf-swot-"]').all())
            context.close()
    finally:
        browser.close()
        server.shutdown(); server.server_close(); worker.join(2)
(output / (phase + '.json')).write_text(json.dumps({
    'checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'runtime_sha256': {str(path.relative_to(Path.cwd())):sha256(path.read_bytes()).hexdigest()
                       for path in sorted((Path.cwd()/'cios/applications/flora').rglob('*'))
                       if path.is_file() and path.suffix in {'.py','.css','.js'}},
    'captures_sha256': {path.name:sha256(path.read_bytes()).hexdigest() for path in sorted(output.glob(phase+'-*.jpg'))},
    'phase': phase, 'environment': 'isolated loopback Chromium; simulated iPads; not live Render',
    'observations': observations,
}, indent=2) + '\n')
print(json.dumps({'phase': phase, 'observations': len(observations), 'passed': True}))
