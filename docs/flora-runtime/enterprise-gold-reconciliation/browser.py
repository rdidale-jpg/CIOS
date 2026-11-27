"""Real isolated Flora browser comparison; no production writes."""
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

VIEWS={'service':'?stream=inside&focus=operations&detail=service',
       'economics':'?focus=economics&detail=costs',
       'strategy':'?stream=forces&focus=strategy&detail=objective-ai',
       'workforce':'?stream=inside&focus=people&detail=workforce'}

def run(out,phase):
    out.mkdir(parents=True,exist_ok=True)
    proof={'phase':phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
           'environment':'Actual isolated Chromium; emulated iPads/mobile, not Render or physical Safari','captures':{},'devices':[]}
    runtime=Path('cios/applications/flora/lloyds_gold.py')
    proof['runtime_sha256']=sha256(runtime.read_bytes()).hexdigest()
    proof['runtime_matches_sha']=subprocess.check_output(['git','show','HEAD:'+str(runtime)])==runtime.read_bytes()
    proof['worktree_dirty']=bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip())
    with TemporaryDirectory(prefix='gold-reconcile-') as tmp,sync_playwright() as pw:
        root=Path(tmp);shutil.copytree(model.REPO/'enterprise-knowledge',root/'enterprise-knowledge');model.REPO=root
        os.environ.update(FLORA_DATA_DIR=str(root/'runtime'),FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0')
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);Thread(target=server.serve_forever,daemon=True).start()
        browser=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
        try:
            for device,size in [('desktop',(1440,1000)),('ipad-landscape',(1194,834)),('ipad-portrait',(834,1194)),('mobile',(390,844))]:
                page=browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',viewport=dict(width=size[0],height=size[1]),has_touch=device!='desktop',reduced_motion='reduce')
                for name,q in VIEWS.items():
                    assert page.goto('/enterprises/lloyds'+q).status==200
                    page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                    file=f'{phase}-{device}-{name}.jpg';page.screenshot(path=out/file,full_page=True,quality=72);proof['captures'][file]=sha256((out/file).read_bytes()).hexdigest()
                if phase=='after':
                    page.goto('/enterprises/lloyds'+VIEWS['service'])
                    page.get_by_role('link',name='Banking and credit cards',exact=False).click();page.wait_for_url('**detail=service-bankcards*')
                    assert 'stream=inside' in page.url and 'focus=operations' in page.url
                    assert '66.37%' in page.locator('main').inner_text() and '97.4%' in page.locator('main').inner_text()
                    chosen=page.url;page.reload();assert page.url==chosen;page.go_back();page.go_forward();assert page.url==chosen
                    link=page.get_by_role('link',name='Home finance',exact=False);link.focus();page.keyboard.press('Enter');page.wait_for_url('**detail=service-mortgages*')
                    assert '62.57%' in page.locator('main').inner_text()
                    assert not page.locator('main [data-canvas-region]').evaluate_all("nodes=>nodes.some(a=>{let b=a.getBoundingClientRect();return b.width<44||b.height<44||getComputedStyle(a).textDecorationLine.includes('underline')})")
                    for q in ('?stream=landscape','?stream=inside','?stream=forces'):
                        assert page.goto('/enterprises/lloyds'+q).status==200
                    for path in ('/industries/banking','/industries/aviation','/enterprises/easyjet'):
                        assert page.goto(path).status==200
                proof['devices'].append(device);page.close()
            if phase=='after':
                page=browser.new_page(base_url=f'http://127.0.0.1:{server.server_port}',viewport={'width':1194,'height':834})
                page.goto('/enterprises/lloyds'+VIEWS['service']);page.goto('/enterprises/easyjet')
                file=root/'enterprise-knowledge/banking/research-model/source-snapshots/FCA-Lloyds-Products-H126.json'
                data=json.loads(file.read_text());data['sources'][0]['withdrawn']=True;file.write_text(json.dumps(data))
                page.go_back();assert '115,687' not in page.locator('main').inner_text();page.emulate_media(media='print')
                assert '97.4%' not in page.locator('main').inner_text();assert '115,687' not in page.locator('main').inner_html()
                proof['withdrawal_history_print_accessibility']=True;page.close()
        finally:browser.close();server.shutdown();server.server_close()
    (out/(phase+'-browser.json')).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':phase,'captures':len(proof['captures']),'passed':True}))

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('out',type=Path);cli.add_argument('phase',choices=['before','after']);args=cli.parse_args();run(args.out,args.phase)
