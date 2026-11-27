"""Loopback CEO journeys using actual Chromium; isolated storage, no live writes."""
import argparse
from copy import deepcopy
from hashlib import sha256
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
from shutil import which
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

sys.path.insert(0, str(Path.cwd()))
from playwright.sync_api import sync_playwright
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora import visual_streams as v

PATH = '/enterprises/lloyds'
VIEWS = {'transaction': '?focus=commercial',
         'envoy': '?stream=inside&focus=applications&detail=envoy',
         'economics': '?focus=economics&detail=costs'}
SIZES = {'desktop': (1440, 1000), 'ipad-landscape': (1194, 834),
         'ipad-portrait': (834, 1194), 'mobile': (390, 844)}


class Quiet(FloraWebHandler):
    def log_message(self, *args):
        pass


def run(phase, out):
    proof = {'phase': phase, 'sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
             'runtime_hashes': {p: sha256(Path(p).read_bytes()).hexdigest() for p in
                               ('cios/applications/flora/lloyds_gold.py',
                                'cios/applications/flora/visual_stream_assets/lloyds-gold.css')},
             'environment': 'Actual loopback Chromium; emulated iPads/touch, not physical Safari or Render',
             'screenshots': {}, 'devices': []}
    with TemporaryDirectory(prefix='flora-activation-') as scratch, sync_playwright() as pw:
        os.environ.update(FLORA_DATA_DIR=scratch, FLORA_ENVIRONMENT='development', FLORA_AUTH_PROVIDER='local',
                          FLORA_TRUST_PROXY_HEADERS='0')
        server = ThreadingHTTPServer(('127.0.0.1', 0), Quiet)
        worker = Thread(target=server.serve_forever, daemon=True); worker.start()
        browser = pw.chromium.launch(executable_path=which('chromium'), args=['--no-sandbox'])
        try:
            for device, (width, height) in SIZES.items():
                page = browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',
                                        viewport={'width': width, 'height': height},
                                        has_touch=device != 'desktop', reduced_motion='reduce')
                errors = []; page.on('pageerror', lambda err: errors.append(str(err)))
                for name, query in VIEWS.items():
                    assert page.goto(PATH + query).status == 200
                    page.evaluate('document.fonts.ready')
                    page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
                    if phase == 'after':
                        if name == 'transaction':
                            page.get_by_role('link', name='Transaction Banking', exact=True).click()
                            page.get_by_role('link', name='Customer economics', exact=True).click()
                        elif name == 'envoy':
                            page.get_by_role('link', name='Value & adoption', exact=True).click()
                        chosen = page.url; page.reload(); assert page.url == chosen
                        page.go_back(); page.go_forward(); assert page.url == chosen
                        audit = page.locator('main').evaluate('''m=>({
                          overflow:document.documentElement.scrollWidth>innerWidth+2,
                          nested:m.querySelectorAll('a a').length,
                          underlined:[...m.querySelectorAll('a[data-canvas-region]')].some(a=>getComputedStyle(a).textDecorationLine.includes('underline')),
                          small:[...m.querySelectorAll('a[data-canvas-region]')].some(a=>{let b=a.getBoundingClientRect();return b.width<44||b.height<44})})''')
                        assert not any(audit.values()), (device, name, audit)
                        target = page.locator('main [data-canvas-region]').last
                        target.focus(); page.keyboard.press('Enter'); page.wait_for_url(lambda url: str(url) != chosen)
                        page.goto(chosen)
                    file = f'{phase}-{device}-{name}.jpg'
                    page.screenshot(path=out/file, full_page=True, quality=72)
                    proof['screenshots'][file] = sha256((out/file).read_bytes()).hexdigest()
                if phase == 'after':
                    page.goto(PATH+'?stream=inside&focus=applications')
                    heading = page.get_by_role('link', name='Envoy', exact=True).locator('.canvas-title')
                    assert heading.bounding_box()['width'] > 100
                    link = page.get_by_role('link', name='Envoy', exact=True)
                    link.scroll_into_view_if_needed(); box = link.bounding_box()
                    hit = page.mouse.click if device == 'desktop' else page.touchscreen.tap
                    hit(box['x'] + box['width']*.8, box['y'] + box['height']*.7)
                    page.wait_for_url(lambda url: 'detail=envoy' in str(url))
                    assert 'detail=envoy' in page.url
                    assert page.goto('/industries/banking').status == 200
                    assert page.goto('/enterprises/easyjet').status == 200
                    assert not page.locator('main .gold-content').count()
                    assert not errors, errors
                proof['devices'].append({'device': device, 'passed': True}); page.close()
            if phase == 'after':
                original = v.current_data
                data = deepcopy(original(v.Context('lloyds', 'landscape')))
                page = browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}')
                route = PATH+'?stream=inside&focus=applications&detail=envoy'
                page.goto(route); assert page.locator('main h2').filter(has_text='Envoy').count()
                next(s for s in data['sources'] if s['id']=='PR-LBG-ENVOY')['withdrawn'] = True
                v.current_data = lambda ctx: data if ctx.scope=='lloyds' else original(ctx)
                try:
                    page.reload(); page.emulate_media(media='print')
                    assert 'Google Cloud' not in page.locator('main').inner_text()
                    assert 'Google Cloud' not in page.locator('main').aria_snapshot()
                    assert not page.locator('main h2').filter(has_text='Envoy').count()
                    proof['withdrawal_reload_print_accessibility'] = True
                finally:
                    v.current_data = original; page.close()
        finally:
            browser.close(); server.shutdown(); server.server_close(); worker.join(2)
    (out/f'Browser-{phase}.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps({'phase': phase, 'screenshots': len(proof['screenshots']), 'devices': len(proof['devices']), 'passed': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['before', 'after']); parser.add_argument('output', type=Path)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True); run(args.phase, args.output)
