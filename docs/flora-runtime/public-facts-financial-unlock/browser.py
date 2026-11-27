"""Actual browser over an isolated research copy; no live services or private runs."""
import argparse,json,os,shutil,subprocess,sys
from hashlib import sha256
from pathlib import Path
from http.server import ThreadingHTTPServer
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import urlencode
sys.path.insert(0,str(Path.cwd()))
from playwright.sync_api import sync_playwright
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora.research_intelligence import model
class Quiet(FloraWebHandler):
    def log_message(self,*args):pass
VIEWS={'landscape':{},'income':{'focus':'economics','detail':'income'},'costs':{'focus':'economics','detail':'costs'},'funding':{'focus':'economics','detail':'funding'},'capital':{'focus':'economics','detail':'capital'},'divisions':{'focus':'economics','detail':'central'},'retail':{'focus':'retail'},'commercial':{'focus':'commercial'},'retirement':{'focus':'retirement'}}
def url(q):return '/enterprises/lloyds'+('?' + urlencode(q) if q else '')
def run(out,phase):
    out.mkdir(parents=True,exist_ok=True);root=Path.cwd()
    paths=['cios/applications/flora/'+p for p in ('lloyds_gold.py','visual_stream_assets/lloyds-gold.css','research_intelligence/source_import.py','financial_intelligence/public_statements.py','financial_intelligence/candidate_analytics.py')]
    hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in paths}
    matches=all(subprocess.check_output(['git','show','HEAD:'+p])==(root/p).read_bytes() for p in paths)
    proof={'phase':phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'runtime_hashes':hashes,'runtime_matches_sha':matches,'environment':'Isolated HTTP Chromium, emulated devices; not Render or physical Safari','captures':{},'devices':[],'checks':{}}
    with TemporaryDirectory(prefix='facts-browser-') as temp,sync_playwright() as pw:
        repo=Path(temp);shutil.copytree(root/'enterprise-knowledge',repo/'enterprise-knowledge');model.REPO=repo;model.DATA=repo/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json'
        os.environ.update(FLORA_DATA_DIR=str(repo/'runtime'),FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0');os.environ.pop('OPENAI_API_KEY',None)
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);Thread(target=server.serve_forever,daemon=True).start()
        browser=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
        try:
            for device,size in [('desktop',(1440,1000)),('ipad-landscape',(1194,834)),('ipad-portrait',(834,1194)),('mobile',(390,844))]:
                page=browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',viewport={'width':size[0],'height':size[1]},has_touch=device!='desktop',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                for name,q in VIEWS.items():
                    assert page.goto(url(q)).status==200;page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),(device,name,'overflow')
                    bad=page.locator('main .canvas-region').evaluate_all("es=>es.filter(e=>e.getBoundingClientRect().width<43||e.getBoundingClientRect().height<43||getComputedStyle(e).textDecorationLine.includes('underline')||e.querySelector('a,button')).map(e=>e.getAttribute('aria-label'))")
                    assert not bad,(device,name,bad)
                    if phase=='after':
                        text=page.locator('main').inner_text()
                        expected={'landscape':['£6.625bn','£11.084bn','£2.256bn'],'income':['£6.625bn','£14.819bn','£6.582bn'],'costs':['£7.246bn','£61m'],'funding':['£502.777bn','3.21%'],'capital':['£247.4bn','13.3%'],'divisions':['£2.256bn','£1.425bn','£245m','£289m'],'retail':['£2.256bn'],'commercial':['£1.425bn'],'retirement':['£245m']}
                        assert all(x in text for x in expected[name]),(device,name,text[:300])
                        assert '.pdf' not in page.locator('main').inner_html()
                    file=f'{phase}-{device}-{name}.jpg';page.screenshot(path=out/file,full_page=True,quality=68);proof['captures'][file]=sha256((out/file).read_bytes()).hexdigest()
                if phase=='after':
                    page.goto(url({}));control=page.locator('main .ce-node[aria-label="Retail"]');control.scroll_into_view_if_needed();box=control.bounding_box()
                    if device=='desktop':page.mouse.click(box['x']+box['width']*.7,box['y']+box['height']*.75)
                    else:page.touchscreen.tap(box['x']+box['width']*.7,box['y']+box['height']*.75)
                    page.wait_for_url('**focus=retail**');assert '£2.256bn' in page.locator('main').inner_text()
                    current=page.url;page.go_back();assert '£11.084bn' in page.locator('main').inner_text();page.go_forward();page.reload();assert page.url==current
                    page.goto(url(VIEWS['income']));control=page.get_by_role('link',name='Business contribution',exact=True);control.focus();page.keyboard.press('Enter');page.wait_for_url('**detail=central**');assert '£289m' in page.locator('main').inner_text()
                    for route in ('/industries/banking','/industries/aviation','/enterprises/easyjet','/enterprises/lloyds/legacy','/enterprises/lloyds/preview'):assert page.goto(route).status==200
                    page.goto('/enterprises/lloyds');page.evaluate("document.documentElement.style.zoom='2'");assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                assert not errors,errors;page.close();proof['devices'].append(device)
            if phase=='after':
                page=browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}')
                for file,q,removed,unrelated in [('PFI-Lloyds-Q326.json',VIEWS['income'],'£6.625bn','£2.256bn'),('LEI-Lloyds-H126.json',VIEWS['retail'],'£2.256bn','£11.084bn')]:
                    path=repo/'enterprise-knowledge/banking/research-model/source-snapshots'/file;original=path.read_text();record=json.loads(original)
                    page.goto(url(q));assert removed in page.locator('main').inner_text();page.goto('/enterprises/easyjet');record['withdrawn']=True;path.write_text(json.dumps(record));page.go_back();page.reload()
                    assert removed not in page.locator('main').inner_html();page.emulate_media(media='print');assert removed not in page.locator('main').aria_snapshot()
                    page.goto(url({}));assert unrelated in page.locator('main').inner_text();path.write_text(original);page.emulate_media(media='screen')
                context=browser.new_context(base_url=f'http://127.0.0.1:{server.server_port}',java_script_enabled=False);p=context.new_page();p.goto(url(VIEWS['income']));p.get_by_role('link',name='Business contribution',exact=True).click();assert '£289m' in p.locator('main').inner_text();context.close();page.close()
                proof['checks']={'reported_financials_visible':True,'whole_region_pointer_touch':True,'keyboard_no_js':True,'back_forward_reload':True,'independent_source_withdrawal_history_print_accessibility':True,'banking_easyjet_and_compatibility_routes':True,'responsive_zoom':True}
        finally:browser.close();server.shutdown();server.server_close()
    (out/(phase+'-browser.json')).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':phase,'captures':len(proof['captures']),'runtime_matches_sha':matches,'passed':True}))
if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('out',type=Path);cli.add_argument('phase',choices=['before','after']);a=cli.parse_args();run(a.out,a.phase)
