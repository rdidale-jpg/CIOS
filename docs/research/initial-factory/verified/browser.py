"""Render before/after Flora handler responses captured by the isolated proof."""
import argparse
import shutil
from pathlib import Path
from io import BytesIO
from urllib.parse import urlsplit
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
from cios.applications.flora import visual_streams
from cios.applications.flora import design_system
from cios.applications.flora.research_intelligence import technology_experience

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('responses', type=Path)
parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'previews')
parser.add_argument('--baseline-responses', type=Path, help='Compare with approved changes rendered at the prior head')
args = parser.parse_args()
src, out = args.responses, args.output
out.mkdir(parents=True, exist_ok=True)
assets={'/design-system/assets/':design_system.asset, '/visual-streams/assets/':visual_streams.asset,
        '/industries/technology/experience/assets/':technology_experience.asset}

def capture(browser, stem, state, viewport, tablet=False):
    page=browser.new_page(viewport=viewport, is_mobile=tablet, has_touch=tablet)
    def serve(request):
        path=urlsplit(request.request.url).path
        if path=='/preview':
            if state == 'before' and args.baseline_responses:
                response = args.baseline_responses / f'{stem}-route-after.html'
            else:
                response = src / f'{stem}-route-{state}.html'
            request.fulfill(body=response.read_bytes(), content_type='text/html; charset=utf-8')
            return
        for prefix, asset in assets.items():
            if path.startswith(prefix):
                data,mime=asset(path[len(prefix):])
                request.fulfill(body=data,content_type=mime)
                return
        request.abort()
    page.route('**/*',serve)
    page.goto('http://flora-fixture.test/preview',wait_until='networkidle')
    page.locator('main').wait_for()
    assert page.evaluate('document.documentElement.scrollWidth') <= viewport['width'], stem
    section=page.locator('[data-commercial-change]').first
    overview=Image.open(BytesIO(page.screenshot())).convert('RGB')
    evidence=None
    if state=='after':
        assert section.is_visible()
        assert section.get_attribute('open') is None

        def expand(summary):
            if tablet:
                summary.tap()
            else:
                summary.focus()
                page.keyboard.press('Enter')
            assert summary.locator('..').get_attribute('open') is not None

        expand(section.locator(':scope > summary'))
        expand(section.get_by_text('What supports this?', exact=True))
        evidence=Image.open(BytesIO(section.screenshot())).convert('RGB')
        if evidence.height>640: evidence=evidence.crop((0,0,evidence.width,640))
    page.close()
    return overview,evidence

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
    responses = sorted(src.glob('*-route-after.html'))
    assert len(responses) == 4, 'Expected all four enterprise route captures'
    for file in responses:
        stem=file.name.removesuffix('-route-after.html')
        for width,height,suffix in [(1100,730,'desktop'),(768,1024,'ipad-portrait'),(1024,768,'ipad-landscape')]:
            before,_=capture(browser,stem,'before',dict(width=width,height=height),suffix!='desktop')
            after,evidence=capture(browser,stem,'after',dict(width=width,height=height),suffix!='desktop')
            right=max(width,evidence.width)
            panel=Image.new('RGB',(width+right,height+evidence.height+72),'#f4f2ed')
            draw=ImageDraw.Draw(panel)
            draw.text((16, 13), ('Before | approved card on main' if args.baseline_responses else
                                'Before | existing Flora route'), fill='#17211b')
            draw.text((width+16, 13), 'After | same route with compact change', fill='#17211b')
            panel.paste(before,(0,35))
            panel.paste(after,(width,35))
            draw.text((width+16,height+49),'After | change and supporting evidence',fill='#17211b')
            panel.paste(evidence,(width,height+72))
            panel.thumbnail((1800,1500))
            panel.save(out/f'{stem}-route-{suffix}.jpg',quality=85,optimize=True)
    browser.close()
