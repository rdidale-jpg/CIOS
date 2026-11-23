"""Render before/after Flora handler responses captured by the isolated proof."""
import argparse
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
            request.fulfill(body=(src/f'{stem}-route-{state}.html').read_bytes(),content_type='text/html; charset=utf-8')
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
        source=section.get_by_text('What supports this?').first
        if tablet:
            source.tap()
        else:
            source.focus()
            page.keyboard.press('Enter')
        assert source.locator('..').get_attribute('open') is not None
        evidence=Image.open(BytesIO(section.screenshot())).convert('RGB')
        if evidence.height>640: evidence=evidence.crop((0,0,evidence.width,640))
    page.close()
    return overview,evidence

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
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
            draw.text((16,13),'Before | existing Flora route',fill='#17211b')
            draw.text((width+16,13),'After | same route with governed evidence in isolated storage',fill='#17211b')
            panel.paste(before,(0,35))
            panel.paste(after,(width,35))
            draw.text((width+16,height+49),'After | change and supporting evidence',fill='#17211b')
            panel.paste(evidence,(width,height+72))
            panel.thumbnail((1800,1500))
            panel.save(out/f'{stem}-route-{suffix}.jpg',quality=85,optimize=True)
    browser.close()
