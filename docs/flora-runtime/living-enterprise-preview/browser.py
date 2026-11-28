"""Actual Flora runtime journeys, baseline equivalence and withdrawal in Chromium."""
from copy import deepcopy
from hashlib import sha256
from http.server import ThreadingHTTPServer
import argparse
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

# Running this same script from the baseline checkout captures the real previous
# runtime, not a reimplementation. The working directory selects that checkout.
sys.path.insert(0,str(Path.cwd()))
from playwright.sync_api import sync_playwright, expect
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora import visual_streams as v

cli=argparse.ArgumentParser();cli.add_argument('output');cli.add_argument('phase',choices=('before','after'));args=cli.parse_args()
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
proof={'phase':args.phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'devices':[],'baseline_content':{},'baseline_html_sha256':{},'screenshots':{}}
with TemporaryDirectory(prefix='flora-living-preview-') as directory, sync_playwright() as playwright:
    os.environ.update(FLORA_DATA_DIR=directory,FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0')
    os.environ.pop('OPENAI_API_KEY',None)
    server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler)
    worker=Thread(target=server.serve_forever,daemon=True);worker.start()
    executable=shutil.which('chromium')
    browser=playwright.chromium.launch(**({'executable_path':executable} if executable else {}),args=['--no-sandbox'])
    base='http://127.0.0.1:'+str(server.server_port)
    try:
        for device,width,height in [('desktop',1440,1000),('ipad-landscape',1194,834),('ipad-portrait',834,1194),('mobile',390,844)]:
            page=browser.new_page(base_url=base,viewport={'width':width,'height':height},has_touch=device!='desktop',reduced_motion='reduce')
            errors=[];failures=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('requestfailed',lambda request:failures.append(request.url))
            def capture(name):
                page.evaluate('document.fonts.ready')
                page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),name
                name=args.phase+'-'+device+'-'+name+'.jpg'
                page.screenshot(path=out/name,quality=80)
                proof['screenshots'][name]=sha256((out/name).read_bytes()).hexdigest()
            # The ordinary public journey, not a direct preview-only URL.
            assert page.goto('/').status==200
            page.get_by_role('navigation',name='Primary product navigation').get_by_role('link',name='Industries',exact=True).click()
            page.locator('a[href="/industries/banking"]:visible').first.click()
            page.locator('a[href="/enterprises/lloyds"]:visible').first.click()
            legacy = '/enterprises/lloyds/legacy' if '/enterprises/lloyds/legacy' in v.ROUTES else '/enterprises/lloyds'
            if legacy.endswith('/legacy'):
                expect(page.locator('[data-experience="lloyds-ceo"]')).to_have_count(1)
                page.goto(legacy)
            expect(page.locator('main')).to_contain_text('From funding to earnings')
            capture('current-lloyds')
            for stream in ('landscape','inside','forces'):
                page.goto(legacy+'?stream='+stream)
                text=re.sub(r'\s+',' ',page.locator('main').inner_text().replace('Preview New Experience','')).strip()
                proof['baseline_content'][device+':'+stream]=text
                html=v.render(legacy,{'stream':[stream]})
                entry='<p class="reading-context" data-preview-entry><a href="/enterprises/lloyds/preview">Preview New Experience</a></p>'
                proof['baseline_html_sha256'][stream]=sha256(html.replace(entry,'').encode()).hexdigest()
                if args.phase=='after':
                    previous=json.loads((out/'Browser-before.json').read_text())
                    assert previous['baseline_content'][device+':'+stream]==text,(device,stream,'Default content changed')
                    assert previous['baseline_html_sha256'][stream]==proof['baseline_html_sha256'][stream],(stream,'Default renderer changed outside the entry link')
            if args.phase=='after':
                from cios.applications.flora import living_enterprise_preview as preview
                page.get_by_role('link',name='Preview New Experience',exact=True).click()
                expect(page.get_by_role('region',name='Experimental design')).to_be_visible()
                for stream in preview.REGIONS:
                    page.get_by_role('navigation',name='Insight streams').get_by_role('link',name=stream.title(),exact=True).click()
                    for key,label,*_ in preview.REGIONS[stream]:
                        if width<1000 and not page.locator('#enterprise-scene').is_visible():page.get_by_role('button',name='Explore Lloyds').click()
                        target=page.locator('[data-region-key="'+key+'"]')
                        size=target.bounding_box();assert size['width']>=44 and size['height']>=44
                        if device=='desktop':target.focus();page.keyboard.press('Enter')
                        else:target.tap()
                        expect(page.locator('main h1')).to_have_text(label)
                        expect(page.locator('[data-region-key="'+key+'"][aria-current]')).to_have_count(1)
                        expect(page.locator('main details:not(.econ-basis)')).to_have_count(0);assert page.locator('main details.econ-basis').count()<=1
                    key={'landscape':'funding','inside':'data','forces':'renewal'}[stream]
                    page.goto(preview.href(preview.State(stream,key,key)))
                    if width<1000:
                        capture('preview-'+stream+'-compact')
                        page.get_by_role('button',name='Explore Lloyds').click()
                    capture('preview-'+stream)
                    if stream=='forces':
                        for quadrant in ('Strength','Weakness','Opportunity','Threat'):
                            page.get_by_role('navigation',name='SWOT quadrants').get_by_role('link',name=quadrant,exact=True).click()
                            links=page.get_by_role('navigation',name=quadrant+' themes').get_by_role('link')
                            for link in links.all():
                                link.click();expect(page.locator(link.get_attribute('href'))).to_be_visible()
                        capture('preview-swot')
                page.goto(preview.PATH+'?stream=landscape&focus=commercial&subject=commercial')
                page.get_by_role('navigation',name='Insight streams').get_by_role('link',name='Inside',exact=True).click()
                expect(page.locator('main')).to_contain_text('From Commercial Banking')
                current=page.url;page.reload();assert page.url==current
                page.go_back();expect(page.locator('main h1')).to_have_text('Commercial Banking')
                page.go_forward();expect(page.locator('main')).to_contain_text('From Commercial Banking')
                page.get_by_role('link',name='Return to current experience',exact=True).click()
                assert '/preview' not in page.url
                if legacy.endswith('/legacy'):
                    expect(page.locator('[data-experience="lloyds-ceo"]')).to_have_count(1)
                else:
                    expect(page.get_by_role('link',name='Preview New Experience',exact=True)).to_be_visible()
                assert not page.locator('[data-preview="experimental-design"]').count()
            # Preserve both ordinary Industries and Enterprises arrival routes.
            for path,title in [('/industries/aviation','Aviation'),('/enterprises/easyjet','easyJet'),('/enterprises/lloyds','Lloyds')]:
                assert page.goto(path).status==200
                assert title.lower() in page.locator('body').inner_text().lower()
            page.goto('/enterprises/easyjet/preview?stream=inside');capture('easyjet-inside')
            assert 'Preview New Experience' not in page.content()
            assert not errors and not failures,(errors,failures)
            proof['devices'].append({'device':device,'default_main_matches_baseline':args.phase=='after','public_industry_enterprise_journeys':True,'twelve_preview_regions':args.phase=='after','eight_swot_themes':args.phase=='after','history_reload_context_return':args.phase=='after','keyboard_or_touch':True,'page_errors':errors})
            page.close()
        if args.phase=='after':
            context=browser.new_context(java_script_enabled=False,viewport={'width':834,'height':1194})
            page=context.new_page();page.goto(base+preview.PATH+'?stream=forces&focus=renewal')
            assert all(panel.is_visible() for panel in page.locator('[id^="llf-swot-"]').all())
            assert page.locator('[data-region-key]').count()==4 and not page.get_by_role('button',name='Explore Lloyds').is_visible()
            context.close()
            original=v.current_data;state={'withdrawn':False}
            def current_data(ctx):
                data=deepcopy(original(ctx))
                if state['withdrawn'] and data:
                    next(source for source in data['sources'] if source['id']=='PR-LBG-Q326')['withdrawn']=True
                return data
            v.current_data=current_data
            try:
                page=browser.new_page(base_url=base,viewport={'width':1440,'height':1000})
                page.goto(preview.PATH+'?stream=landscape&focus=funding')
                expect(page.locator('main')).to_contain_text('£502.8bn')
                page.get_by_role('navigation',name='Insight streams').get_by_role('link',name='Inside',exact=True).click()
                state['withdrawn']=True
                page.go_back();expect(page.locator('main')).not_to_contain_text('£502.8bn')
                expect(page.locator('.change-marker')).to_have_count(0)
                page.emulate_media(media='print');expect(page.locator('main')).not_to_contain_text('£6.6bn')
                page.reload();expect(page.locator('main')).not_to_contain_text('£502.8bn')
                assert 'Curve: acquisition reported complete' not in page.content()
                page.close()
            finally:v.current_data=original
            proof['source_withdrawal_history_reload_print_accessible_marker']=True
            proof['no_javascript_fallback']=True
    finally:
        browser.close();server.shutdown();server.server_close();worker.join(2)
proof['browser']='Chromium; emulated iPad/touch, not physical iPad or live Render'
proof['worktree_dirty']=bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip())
if args.phase=='after':
    paths=('living_enterprise_preview.py','lloyds_flagship.py','visual_panels.py','public_routes.py','web/app.py',
           'visual_stream_assets/living-enterprise-preview.css','visual_stream_assets/living-enterprise-preview.js')
    proof['runtime_source_sha256']={name:sha256((Path('cios/applications/flora')/name).read_bytes()).hexdigest() for name in paths}
(out/('Browser-'+args.phase+'.json')).write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'phase':args.phase,'devices':len(proof['devices']),'captures':len(proof['screenshots']),'passed':True}))
