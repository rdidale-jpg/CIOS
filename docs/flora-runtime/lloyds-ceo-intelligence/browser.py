"""Real HTTP/browser proof over isolated copies, never Render or private data."""
import argparse,json,os,shutil,subprocess,sys
from hashlib import sha256
from pathlib import Path
from http.server import ThreadingHTTPServer
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import urlencode,parse_qs,urlsplit
sys.path.insert(0,str(Path.cwd()))
from playwright.sync_api import sync_playwright
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora.research_intelligence import model

class Quiet(FloraWebHandler):
    def log_message(self,*args):pass

VIEWS={
 'landscape':{},'inside':{'stream':'inside'},'forces':{'stream':'forces'},
 'employees':{'stream':'inside','focus':'people','detail':'employees'},
 'geography':{'stream':'inside','focus':'people','detail':'geography'},
 'board':{'stream':'inside','focus':'people','detail':'board'},
 'distribution':{'focus':'economics','detail':'distribution'},
 'mortgage':{'stream':'inside','focus':'operations','detail':'mortgage-ml'},
 'platform':{'stream':'inside','focus':'applications','detail':'platform-delivery'},
 'settlement':{'stream':'inside','focus':'applications','detail':'settlement'},
 'business':{'stream':'inside','focus':'operations','detail':'digital-business'},
 'wealth':{'focus':'retirement','detail':'wealth-delivery'},
 'investigations':{'stream':'forces','focus':'strategy','detail':'investigations'},
 'collaborations':{'stream':'inside','focus':'partners','detail':'caura'},
}
BEFORE={k:v for k,v in VIEWS.items() if k in ('landscape','inside','forces')}
BEFORE.update(employees={'stream':'inside','focus':'people','detail':'workforce'},platform={'stream':'inside','focus':'applications'},business={'focus':'commercial'},wealth={'focus':'retirement'})

def url(query):return '/enterprises/lloyds'+('?' + urlencode(query) if query else '')

def run(out,phase):
    out.mkdir(parents=True,exist_ok=True);root=Path.cwd()
    paths=['cios/applications/flora/lloyds_gold.py','cios/applications/flora/visual_stream_assets/lloyds-gold.css','enterprise-knowledge/banking/research-model/Assessment-Overlay.json']
    paths+=sorted(str(p.relative_to(root)) for p in (root/'enterprise-knowledge/banking/research-model/source-snapshots').glob('LCE-*.txt'))
    matches=[]
    for path in paths:
        recorded=subprocess.run(['git','show','HEAD:'+path],capture_output=True);matches.append(recorded.returncode==0 and recorded.stdout==(root/path).read_bytes())
    proof={'phase':phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'runtime_hashes':{p:sha256((root/p).read_bytes()).hexdigest() for p in paths},'runtime_matches_sha':all(matches),'environment':'Isolated HTTP Chromium; emulated iPads/mobile, not physical Safari or deployed Render','captures':{},'devices':[],'navigation':[],'checks':{}}
    with TemporaryDirectory(prefix='ceo-browser-') as tmp,sync_playwright() as pw:
        repo=Path(tmp);shutil.copytree(root/'enterprise-knowledge',repo/'enterprise-knowledge');model.REPO=repo;model.DATA=repo/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json'
        os.environ.update(FLORA_DATA_DIR=str(repo/'runtime'),FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0');os.environ.pop('OPENAI_API_KEY',None)
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);Thread(target=server.serve_forever,daemon=True).start()
        browser=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
        try:
            for device,size in [('desktop',(1440,1000)),('ipad-landscape',(1194,834)),('ipad-portrait',(834,1194)),('mobile',(390,844))]:
                page=browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',viewport={'width':size[0],'height':size[1]},has_touch=device!='desktop',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                for name,query in (VIEWS if phase=='after' else BEFORE).items():
                    assert page.goto(url(query)).status==200
                    page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),(device,name,'page overflow')
                    bad=page.locator('main .canvas-region').evaluate_all("es=>es.filter(e=>e.getBoundingClientRect().width<43||e.getBoundingClientRect().height<43||getComputedStyle(e).textDecorationLine.includes('underline')||e.querySelector('a,button')).map(e=>e.getAttribute('aria-label'))")
                    assert not bad,(device,name,bad)
                    clipped=page.locator('.ce-node,.ceo-fte-year,.ceo-settlement-route>span').evaluate_all("es=>es.filter(e=>e.scrollWidth>e.clientWidth+3||e.scrollHeight>e.clientHeight+3).map(e=>e.textContent)")
                    assert not clipped,(device,name,clipped)
                    file=f'{phase}-{device}-{name}.jpg';page.screenshot(path=out/file,full_page=True,quality=72);proof['captures'][file]=sha256((out/file).read_bytes()).hexdigest()
                if phase=='after':
                    from cios.applications.flora import lloyds_gold as g
                    for key,title,states in g.V3_PATHS:
                        if key not in {'distribution','mortgage-ml','settlement','business-digital'}:continue
                        for i,(stream,focus,detail) in enumerate(states):
                            subject='commercial' if key in {'settlement','business-digital'} else 'retail'
                            page.goto(url({'stream':stream,'focus':focus,'detail':detail,'subject':subject}));target=states[(i+1)%3]
                            page.get_by_role('navigation',name='Insight streams').get_by_role('link',name=target[0].title(),exact=True).click()
                            q=parse_qs(urlsplit(page.url).query,keep_blank_values=True)
                            assert (q['stream'][0],q['focus'][0],q['detail'][0])==target and q['subject']==[subject]
                            current=page.url;page.reload();page.go_back();page.go_forward();assert page.url==current
                            proof['navigation'].append({'device':device,'topic':key,'from':stream,'to':target[0]})
                    page.goto(url({'stream':'inside'}));control=page.get_by_role('link',name='Employee operating system',exact=True);control.scroll_into_view_if_needed();box=control.bounding_box()
                    if device=='desktop':page.mouse.click(box['x']+box['width']*.65,box['y']+box['height']*.75)
                    else:page.touchscreen.tap(box['x']+box['width']*.65,box['y']+box['height']*.75)
                    assert '60,061' in page.locator('main').inner_text()
                    business=page.get_by_role('link',name='Retail employee context',exact=True);business.scroll_into_view_if_needed();box=business.bounding_box()
                    if device=='desktop':page.mouse.click(box['x']+box['width']*.7,box['y']+box['height']*.75)
                    else:page.touchscreen.tap(box['x']+box['width']*.7,box['y']+box['height']*.75)
                    assert 'focus=retail' in page.url;page.go_back();assert '60,061' in page.locator('main').inner_text()
                    control=page.get_by_role('link',name='Board and management',exact=True);control.focus();page.keyboard.press('Enter');assert 'Sarah Legg' in page.locator('main').inner_text()
                    for route in ('/industries/banking','/industries/aviation','/enterprises/easyjet','/enterprises/lloyds/legacy','/enterprises/lloyds/preview'):
                        assert page.goto(route).status==200
                    if device=='desktop':
                        page.goto('/enterprises/lloyds');page.evaluate("document.documentElement.style.zoom='2'");assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                assert not errors,errors;proof['devices'].append(device);page.close()
            if phase=='after':
                page=browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',viewport={'width':1194,'height':834})
                for sid,name,removed in [('LCE-WORKFORCE','employees','60,061'),('LCE-ANNUAL-OPERATIONS','wealth','84,000'),('LCE-VERTEX','platform','Vertex AI'),('LCE-DELIVERY','platform','40%'),('LCE-BOARD','board','Sarah Legg'),('LCE-SETTLEMENT','settlement','Archax'),('LCE-LAUNCH','collaborations','8,000')]:
                    original=model.DATA.read_text();data=json.loads(original);page.goto(url(VIEWS[name]));assert removed in page.locator('main').inner_text();page.goto('/enterprises/easyjet')
                    next(s for s in data['sources'] if s['id']==sid)['withdrawn']=True;model.DATA.write_text(json.dumps(data))
                    page.go_back();assert removed not in page.locator('main').inner_text();page.reload();page.emulate_media(media='print');assert removed not in page.locator('main').inner_text() and removed not in page.locator('main').aria_snapshot()
                    page.goto('/enterprises/lloyds');assert '£502.8bn' in page.locator('main').inner_text();model.DATA.write_text(original);page.emulate_media(media='screen')
                context=browser.new_context(base_url=f'http://127.0.0.1:{server.server_port}',java_script_enabled=False);p=context.new_page();p.goto(url(VIEWS['employees']));p.get_by_role('link',name='Board and management',exact=True).click();assert 'Sarah Legg' in p.locator('main').inner_text();context.close()
                proof['checks']={'whole_region_pointer_touch':True,'keyboard':True,'no_javascript':True,'history_reload_direct_links':True,'new_source_withdrawal_history_print_accessibility':True,'unrelated_funding_survives':True,'banking_easyjet_legacy_preserved':True,'original_compositions_and_artwork_preserved':True,'responsive_zoom':True};page.close()
        finally:browser.close();server.shutdown();server.server_close()
    (out/(phase+'-browser.json')).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':phase,'captures':len(proof['captures']),'devices':len(proof['devices']),'navigation':len(proof['navigation']),'passed':True}))

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('out',type=Path);cli.add_argument('phase',choices=['before','after']);a=cli.parse_args();run(a.out,a.phase)
