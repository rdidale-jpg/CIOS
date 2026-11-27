"""Actual isolated browser comparison and executive comprehension journeys."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
from hashlib import sha256
from http.server import ThreadingHTTPServer
from tempfile import TemporaryDirectory
from threading import Thread
sys.path.insert(0,str(Path.cwd()))
from playwright.sync_api import sync_playwright
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora.research_intelligence import model

class Quiet(FloraWebHandler):
    def log_message(self,*args):pass
VIEWS={'group':'','inside':'?stream=inside&focus=operations','leadership':'?stream=inside&focus=people&detail=leadership','workforce':'?stream=inside&focus=people&detail=workforce','programmes':'?stream=inside&focus=programmes','forces':'?stream=forces'}
DEEP={'commercial':'?focus=commercial','insurance':'?focus=retirement','economics':'?focus=economics&detail=comparison','technology':'?stream=inside&focus=applications&detail=frontier','fraud':'?stream=inside&focus=applications&detail=fraud','ai':'?stream=forces&focus=strategy&detail=objective-ai','brands':'?focus=group&detail=brands'}

def run(out,phase):
    out.mkdir(parents=True,exist_ok=True);root=Path.cwd()
    runtime=('cios/applications/flora/lloyds_gold.py','cios/applications/flora/leadership_agenda.py','cios/applications/flora/visual_stream_assets/lloyds-gold.css','enterprise-knowledge/banking/research-model/Assessment-Overlay.json')
    proof={'phase':phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'runtime_hashes':{p:sha256((root/p).read_bytes()).hexdigest() for p in runtime},'runtime_matches_sha':all(subprocess.check_output(['git','show','HEAD:'+p])==(root/p).read_bytes() for p in runtime),'environment':'Actual isolated HTTP Chromium; emulated iPads/mobile, not Render or physical Safari','captures':{},'devices':[],'checks':{}}
    with TemporaryDirectory(prefix='gold-v2-browser-') as tmp,sync_playwright() as pw:
        repo=Path(tmp);shutil.copytree(root/'enterprise-knowledge',repo/'enterprise-knowledge');model.REPO=repo;model.DATA=repo/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json'
        os.environ.update(FLORA_DATA_DIR=str(repo/'runtime'),FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0');os.environ.pop('OPENAI_API_KEY',None)
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);Thread(target=server.serve_forever,daemon=True).start()
        browser=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
        try:
            for device,size in [('desktop',(1440,1000)),('ipad-landscape',(1194,834)),('ipad-portrait',(834,1194)),('mobile',(390,844))]:
                page=browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',viewport=dict(width=size[0],height=size[1]),has_touch=device!='desktop',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                def capture(name):
                    page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),(device,name,'overflow')
                    if phase=='after':
                        audit=page.locator('main').evaluate("m=>({nested:m.querySelectorAll('a a').length,small:[...m.querySelectorAll('[data-canvas-region]')].some(a=>{let b=a.getBoundingClientRect();return b.width<44||b.height<44}),bare:[...m.querySelectorAll('.gold-content a[href]')].some(a=>a.getAttribute('href').startsWith('/')&&!a.matches('[data-canvas-region],[data-canvas-exception]')&&!a.closest('.gold-inspect')),underlined:[...m.querySelectorAll('[data-canvas-region]')].some(a=>getComputedStyle(a).textDecorationLine.includes('underline'))})")
                        assert not any(audit.values()),(device,name,audit)
                    file=f'{phase}-{device}-{name}.jpg';page.screenshot(path=out/file,full_page=True,quality=72);proof['captures'][file]=sha256((out/file).read_bytes()).hexdigest()
                for name,q in VIEWS.items():
                    assert page.goto('/enterprises/lloyds'+q).status==200;capture(name)
                if phase=='after':
                    def activate(label):
                        target=page.locator('main').get_by_role('link',name=label,exact=True);target.scroll_into_view_if_needed();box=target.bounding_box()
                        if device=='desktop':page.mouse.click(box['x']+box['width']*.7,box['y']+box['height']*.75)
                        else:page.touchscreen.tap(box['x']+box['width']*.7,box['y']+box['height']*.75)
                    page.goto('/enterprises/lloyds');activate('Commercial Banking');page.wait_for_url('**focus=commercial**')
                    assert 'Amanda Murphy' in page.locator('main').inner_text() and 'John Langley' in page.locator('main').inner_text()
                    activate('Transaction Banking');page.wait_for_url('**detail=transactions**');assert 'Natasha Condon' in page.locator('main').inner_text()
                    chosen=page.url;page.reload();page.go_back();page.go_forward();assert page.url==chosen
                    page.goto('/enterprises/lloyds'+VIEWS['leadership']);target=page.get_by_role('link',name='William Chalmers',exact=True);target.focus();page.keyboard.press('Enter');page.wait_for_url('**detail=leader-chalmers**');assert 'Group finance chief' in page.locator('main').inner_text()
                    page.goto('/enterprises/lloyds'+VIEWS['forces']);activate('Create lasting operating leverage');page.wait_for_url('**detail=objective-efficiency**');assert 'Next decision' in page.locator('main').inner_text()
                    for q in DEEP.values():
                        assert page.goto('/enterprises/lloyds'+q).status==200
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                    for path in ('/industries/banking','/industries/aviation','/enterprises/easyjet','/enterprises/lloyds/legacy','/enterprises/lloyds/preview'):
                        assert page.goto(path).status==200,path
                    if device=='desktop':
                        for name,q in DEEP.items():page.goto('/enterprises/lloyds'+q);capture(name)
                        page.goto('/enterprises/lloyds');page.evaluate("document.documentElement.style.zoom='2'");capture('zoom-200')
                    assert not errors,errors
                proof['devices'].append(device);page.close()
            if phase=='after':
                page=browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',viewport={'width':1194,'height':834})
                for sid,q,removed in [('LGV2-LEADERS',VIEWS['leadership'],'William Chalmers'),('LGV2-FRONTIER',DEEP['technology'],'40,000')]:
                    file=model.DATA;data=json.loads(file.read_text());original=file.read_text()
                    page.goto('/enterprises/lloyds'+q);assert removed in page.locator('main').inner_text();page.goto('/enterprises/easyjet')
                    next(s for s in data['sources'] if s['id']==sid)['withdrawn']=True;file.write_text(json.dumps(data))
                    page.go_back();page.reload();page.emulate_media(media='print');assert removed not in page.locator('main').inner_text() and removed not in page.locator('main').aria_snapshot()
                    page.goto('/enterprises/lloyds');assert '£502.8bn' in page.locator('main').inner_text()
                    file.write_text(original);page.emulate_media(media='screen')
                context=browser.new_context(base_url=f'http://127.0.0.1:{server.server_port}',java_script_enabled=False);p=context.new_page();p.goto('/enterprises/lloyds'+VIEWS['leadership']);p.get_by_role('link',name='William Chalmers',exact=True).click();assert 'detail=leader-chalmers' in p.url;context.close()
                proof['checks']={'native_physical_targets':True,'keyboard':True,'touch':True,'history_reload_direct_links':True,'withdrawal_history_print_accessibility':True,'independent_funding_survives':True,'no_javascript':True,'banking_easyjet_legacy':True};page.close()
        finally:browser.close();server.shutdown();server.server_close()
    (out/(phase+'-browser.json')).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':phase,'captures':len(proof['captures']),'devices':len(proof['devices']),'passed':True}))

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('out',type=Path);cli.add_argument('phase',choices=['before','after']);args=cli.parse_args();run(args.out,args.phase)
