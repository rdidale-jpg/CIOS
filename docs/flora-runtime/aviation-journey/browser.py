from contextlib import contextmanager
from hashlib import sha256
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import sync_playwright, expect
from pytest import MonkeyPatch

repo = Path.cwd()
sys.path.insert(0, str(repo))
from cios.applications.flora.research_intelligence import model, registry
from cios.applications.flora.web.app import FloraWebHandler

output, mode = Path(sys.argv[1]), sys.argv[2]
output.mkdir(parents=True, exist_ok=True)
root = '/enterprises/easyjet'
preview = root + '/preview'
industry = '/industries/aviation'
results = []


@contextmanager
def app():
    with TemporaryDirectory() as temp, MonkeyPatch.context() as patch:
        isolated = Path(temp)
        knowledge = isolated / 'enterprise-knowledge'
        shutil.copytree(repo / 'enterprise-knowledge', knowledge)
        patch.setattr(model, 'REPO', isolated)
        patch.setattr(model, 'DATA', knowledge / 'banking/research-model/Assessment-Overlay.json')
        patch.setattr(registry, 'REPO', isolated)
        patch.setenv('FLORA_DATA_DIR', str(isolated / 'app'))
        patch.setenv('FLORA_ENVIRONMENT', 'development')
        patch.setenv('FLORA_AUTH_PROVIDER', 'local')
        patch.delenv('FLORA_PILOT_DIR', raising=False)
        server = ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f'http://127.0.0.1:{server.server_port}', knowledge
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)


def activate(locator, touch):
    if touch:
        locator.tap()
    else:
        locator.focus()
        locator.press('Enter')


with app() as (base, knowledge), sync_playwright() as p:
    browser = p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
    for label, width, height in [('desktop', 1440, 1000), ('ipad-landscape', 1194, 834), ('ipad-portrait', 834, 1194)]:
        touch = label.startswith('ipad')
        page = browser.new_page(base_url=base, viewport={'width': width, 'height': height}, has_touch=touch)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        assert page.goto('/industries').ok
        activate(page.locator(f'a[href="{industry}"]').first, touch)
        page.wait_for_url(base + industry)
        if mode == "before":
            assert page.goto(industry + "?lens=pestle").ok
        activate(page.locator(f'a[href="{root}"]:visible').first, touch)
        page.wait_for_url(base + root)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=output / f'{mode}-{label}.jpg', quality=86)
        if mode == 'before':
            expect(page.locator('[data-region="main"][data-scope="easyjet"]')).to_have_count(0)
            results.append({'viewport': label, 'path': root, 'legacy_before': True})
            page.close()
            continue

        main = page.locator('main[data-identity="AV-ENT-001"]')
        expect(main).to_have_attribute('data-stream', 'landscape')
        expect(page.locator('[data-region="top"]')).to_have_count(1)
        expect(page.locator('[data-region="left"]')).to_have_count(1)
        expect(page.locator('.econ-stages')).to_be_visible()
        for entry in ('/enterprises', industry + '?lens=pestle'):
            assert page.goto(entry).ok
            activate(page.locator(f'a[href="{root}"]:visible').first, touch)
            page.wait_for_url(base + root)
            expect(main).to_be_visible()
            page.go_back()
            assert page.url == base + entry

        page.goto(root)
        activate(page.locator('.econ-stages [data-stage="airline-return"]'), touch)
        expect(page.locator('.econ-stages [aria-current]')).to_have_attribute('data-stage', 'airline-return')
        facts_url = page.url
        activate(page.get_by_role('link', name='FLORA Insight', exact=True), touch)
        expect(page.locator('.econ-focus [data-semantic-type="insight"]')).to_have_count(1)
        insight_url = page.url
        assert 'detail=airline-return' in insight_url and 'reading=insight' in insight_url
        page.go_back()
        assert page.url == facts_url
        page.go_forward()
        assert page.url == insight_url
        assert page.reload().ok
        expect(page.locator('.econ-stages [aria-current]')).to_have_attribute('data-stage', 'airline-return')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=output / f'after-economics-insight-{label}.jpg', quality=86)
        activate(page.get_by_role('link', name='Close economic detail', exact=True), touch)
        page.wait_for_url(lambda url: 'detail=' not in url and 'reading=insight' in url)

        for detail in ('fleet-operations', 'network-planning', 'customer-service'):
            assert page.goto(preview + '?stream=inside&detail=' + detail + '&reading=insight').ok
            expect(main).to_have_attribute('data-stream', 'inside')
            assert page.reload().ok
        assert page.goto(industry).ok
        for summary in page.locator('details:has(a[href$="?lens=operating-model"]) > summary').all():
            if summary.is_visible() and not summary.evaluate("(el) => el.parentElement.open"):
                activate(summary, touch)
        legacy = page.locator('a[href="/enterprises/easyjet?lens=operating-model"]:visible').first
        activate(legacy, touch)
        expect(page.get_by_text('original documents not directly verified', exact=False).first).to_be_attached()
        for lens in ('timeline', 'ecosystem', 'opportunities', 'commercial'):
            assert page.request.get(root + '?lens=' + lens).ok
        for destination in ('/understanding', '/research-diagnostic'):
            assert page.request.get(root + destination).ok
        assert page.request.get('/flora/aviation/research/easyjet').ok
        for destination in (root+'?workspace=private', preview+'?run_id=private', root+'/canvas'):
            assert page.request.get(destination).status in (403, 404)

        assert page.goto(root).ok
        expect(main).to_contain_text('356 aircraft')
        expect(main).to_contain_text('1,202 routes')
        assert not any(value in main.inner_text() for value in ('£10,106', '£665m'))
        disclosure = page.locator('.econ-basis > summary')
        activate(disclosure, touch)
        expect(page.locator('.econ-basis[open]')).to_have_count(1)
        overlay = knowledge / 'aviation/research-model/Assessment-Overlay.json'
        source = overlay.read_text()
        try:
            page.goto('/enterprises')
            data = json.loads(source)
            next(row for row in data['sources'] if row['id'] == 'SRC-AV-AR25')['withdrawn'] = True
            overlay.write_text(json.dumps(data))
            page.go_back()
            expect(main).not_to_contain_text('356 aircraft')
            assert page.reload().ok
            assert all(value not in page.content() for value in ('356 aircraft', '1,202 routes'))
        finally:
            overlay.write_text(source)

        assert not errors, errors
        results.append({'viewport': label, 'desktop_keyboard_or_tablet_touch': True,
                        'catalogue_and_industry_entry': True, 'economics_and_history': True,
                        'legacy_and_detail_routes': True, 'private_access_denied': True,
                        'source_withdrawal_back_and_reload': True})
        page.close()
    browser.close()

(output / f'{mode}-browser.json').write_text(json.dumps({
    'base_or_checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'runtime': {name: sha256((repo / name).read_bytes()).hexdigest() for name in (
        'cios/applications/flora/web/app.py', 'cios/applications/flora/research_intelligence/unified_views.py')},
    'observations': results,
}, indent=2) + '\n')
print(json.dumps(results, indent=2))
