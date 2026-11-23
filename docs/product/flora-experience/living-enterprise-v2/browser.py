"""Actual Chromium journeys, responsive captures and self-contained-preview validation."""
from hashlib import sha256
from pathlib import Path
import json
import os
import socket
import subprocess
import sys
import time
from urllib.request import urlopen
sys.path.insert(0,str(Path(__file__).parent))
import prototype as d
from playwright.sync_api import sync_playwright, expect

out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
server=subprocess.Popen([sys.executable,str(d.HERE/'prototype.py'),'--port',str(port)],cwd=d.ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
checks=[]
try:
    for attempt in range(60):
        try:
            if urlopen(f'http://127.0.0.1:{port}{d.PATH}',timeout=1).status==200:break
        except Exception:time.sleep(.1)
    else:raise AssertionError('Design server unavailable')
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for device,width,height in [('desktop',1440,1000),('ipad-landscape',1194,834),('ipad-portrait',834,1194),('mobile',390,844)]:
            page=browser.new_page(viewport={'width':width,'height':height},has_touch=device!='desktop',reduced_motion='reduce')
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            def wait_images():
                page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
            def capture(name):
                wait_images();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),name
                page.screenshot(path=out/(device+'-'+name+'.jpg'),quality=82)
            assert page.goto(f'http://127.0.0.1:{port}/enterprises/lloyds').status==200
            if device!='mobile':capture('current-landscape')
            for stream in d.REGIONS:
                assert page.goto(f'http://127.0.0.1:{port}'+d.href(d.State(),stream=stream)).status==200
                if width<1000:
                    page.get_by_role('button',name='Explore Lloyds').click()
                    expect(page.locator('#enterprise-scene')).to_be_visible()
                expect(page.locator('[data-region-key]')).to_have_count(4)
                marker=page.locator('.change-marker').bounding_box()
                if marker:assert marker['width']>=44 and marker['height']>=44
                for key,label,*_ in d.REGIONS[stream]:
                    anchor=page.locator('[data-region-key="'+key+'"]')
                    if width<1000 and not page.locator('#enterprise-scene').is_visible():page.get_by_role('button',name='Explore Lloyds').click()
                    bounds=anchor.bounding_box();assert bounds['width']>=44 and bounds['height']>=44
                    if device=='desktop':anchor.focus();page.keyboard.press('Enter')
                    else:anchor.tap()
                    expect(page.locator('main h1')).to_have_text(label)
                    expect(page.locator('[data-region-key="'+key+'"][aria-current]')).to_have_count(1)
                    assert '<details' not in page.locator('main').inner_html()
                # Pin meaningful captures rather than only the last selected item.
                preferred={'landscape':'funding','inside':'data','forces':'renewal'}[stream]
                page.goto(f'http://127.0.0.1:{port}'+d.href(d.State(stream,preferred,preferred),focus=preferred))
                if width<1000:
                    capture(stream+'-compact');page.get_by_role('button',name='Explore Lloyds').click()
                capture(stream)
                if stream=='forces':
                    assert page.locator('[id^="llf-swot-"]').count()==8
                    for quadrant in ['Strength','Weakness','Opportunity','Threat']:
                        page.get_by_role('navigation',name='SWOT quadrants').get_by_role('link',name=quadrant,exact=True).click()
                        themes=page.get_by_role('navigation',name=quadrant+' themes').get_by_role('link')
                        for link in themes.all():link.click();expect(page.locator(link.get_attribute('href'))).to_be_visible()
                    if device=='desktop':capture('swot')
            page.goto(f'http://127.0.0.1:{port}{d.PATH}?stream=landscape&focus=commercial&subject=commercial')
            page.get_by_role('navigation',name='Insight streams').get_by_role('link',name='Inside',exact=True).click()
            assert 'subject=commercial' in page.url
            expect(page.locator('main')).to_contain_text('From Commercial Banking')
            url=page.url;page.reload();assert page.url==url
            page.go_back();expect(page.locator('main h1')).to_have_text('Commercial Banking')
            page.go_forward();expect(page.locator('main')).to_contain_text('From Commercial Banking')
            assert page.request.post(f'http://127.0.0.1:{port}{d.PATH}',data='').status==405
            assert page.request.get(f'http://127.0.0.1:{port}{d.PATH}?workspace=private').status==404
            page.goto(f'http://127.0.0.1:{port}/industries/banking');capture('industry-comparison')
            assert d.v.BANKING_ART_SMALL in page.content()
            assert not errors,errors
            checks.append({'device':device,'four_regions_per_layer':True,'three_perspectives':True,'eight_swot_themes':True,'keyboard_or_touch':True,'history_reload_subject_continuity':True,'errors':errors})
            page.close()
        context=browser.new_context(java_script_enabled=False,viewport={'width':1440,'height':1000})
        page=context.new_page();page.goto(f'http://127.0.0.1:{port}{d.PATH}?stream=forces&focus=renewal&subject=renewal')
        assert all(node.is_visible() for node in page.locator('[id^="llf-swot-"]').all());context.close()
        # Validate the self-contained document over loopback. Managed Chromium
        # explicitly blocks file://; do not override that administrator policy.
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];requests=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:requests.append(request.url) if request.resource_type!='document' and not request.url.startswith('data:') else None)
        page.goto(f'http://127.0.0.1:{port}/design/preview.html')
        expect(page.locator('main h1')).to_have_text('Retail Banking')
        page.locator('[data-region-key="commercial"]').click();expect(page.locator('main h1')).to_have_text('Commercial Banking')
        page.get_by_role('navigation',name='Insight streams').get_by_role('link',name='Inside',exact=True).click()
        expect(page.locator('main')).to_contain_text('From Commercial Banking')
        page.reload();expect(page.locator('main')).to_contain_text('From Commercial Banking')
        page.go_back();expect(page.locator('main h1')).to_have_text('Commercial Banking');page.go_forward()
        assert not errors and not requests,(errors,requests)
        page.close();browser.close()
finally:
    server.terminate();server.wait(timeout=10)
proof={'base':d.BASE,'checkout':subprocess.check_output(['git','rev-parse','HEAD'],cwd=d.ROOT,text=True).strip(),
       'tested_prototype_sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in d.HERE.glob('*') if p.suffix in {'.py','.css','.js','.html'}},
       'checks':checks,'self_contained_preview_no_subrequests':True,'file_url_check':'Blocked by managed browser administrator policy; not overridden','no_javascript_fallback':True,'screenshots':{p.name:sha256(p.read_bytes()).hexdigest() for p in out.glob('*.jpg')},
       'actual_browser':'system Chromium, emulated touch/tablets; not physical iPad or live Render'}
(out/'Browser-Proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'passed':True,'devices':len(checks),'screenshots':len(proof['screenshots']),'self_contained_preview':True}))
