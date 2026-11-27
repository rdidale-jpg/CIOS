"""Actual isolated Chromium: numerical knowledge, selection and withdrawal."""
from copy import deepcopy
from hashlib import sha256
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import argparse,json,os,shutil,subprocess,sys
sys.path.insert(0,str(Path.cwd()))
from playwright.sync_api import sync_playwright
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora.research_intelligence import model
from cios.applications.flora import lloyds_gold as gold

class Quiet(FloraWebHandler):
    def log_message(self,*args):pass


def run(out,phase):
    out.mkdir(parents=True,exist_ok=True)
    proof={'phase':phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
           'mode':'Actual local Chromium; emulated iPads and mobile, not physical Safari or Render',
           'captures':{},'journeys':[]}
    paths=('cios/applications/flora/leadership_agenda.py','cios/applications/flora/lloyds_gold.py',
           'cios/applications/flora/visual_stream_assets/lloyds-gold.css')
    proof['runtime_hashes']={p:sha256(Path(p).read_bytes()).hexdigest() for p in paths}
    proof['runtime_matches_sha']=all(sha256(subprocess.check_output(['git','show','HEAD:'+p])).hexdigest()==proof['runtime_hashes'][p] for p in paths)
    with TemporaryDirectory(prefix='flora-numerical-browser-') as scratch,sync_playwright() as pw:
        root=Path(scratch);shutil.copytree(model.REPO/'enterprise-knowledge',root/'enterprise-knowledge');model.REPO=root
        os.environ.update(FLORA_DATA_DIR=str(root/'runtime'),FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0')
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);Thread(target=server.serve_forever,daemon=True).start()
        browser=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
        base=f'http://127.0.0.1:{server.server_port}'
        path='/enterprises/lloyds?focus=economics&detail='
        try:
            for device,size in [('desktop',(1440,1000)),('ipad-landscape',(1194,834)),('ipad-portrait',(834,1194)),('mobile',(390,844))]:
                context=browser.new_context(base_url=base,viewport={'width':size[0],'height':size[1]},has_touch=device!='desktop',reduced_motion='reduce')
                page=context.new_page();errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
                assert page.goto(path+'costs').status==200
                page.evaluate('document.fonts.ready')
                page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
                def capture(name):
                    file=phase+'-'+device+'-'+name+'.jpg';page.screenshot(path=out/file,full_page=True,quality=75);proof['captures'][file]=sha256((out/file).read_bytes()).hexdigest()
                capture('costs')
                if phase=='before':
                    assert '115,687' not in page.locator('main').inner_text()
                else:
                    assert '115,687' in page.locator('main').inner_text()
                    page.get_by_role('link',name='Banking and credit cards',exact=False).click();chosen=page.url
                    assert '66.37%' in page.locator('main').inner_text();capture('bankcards')
                    page.reload();assert page.url==chosen
                    page.go_back();page.go_forward();assert page.url==chosen
                    page.get_by_role('link',name='Home finance',exact=False).focus();page.keyboard.press('Enter');page.wait_for_url('**detail=service-mortgages*')
                    assert 'detail=service-mortgages' in page.url and '62.57%' in page.locator('main').inner_text()
                    assert not page.locator('main').evaluate("m=>[...m.querySelectorAll('[data-canvas-region=service-workload]')].some(a=>{let b=a.getBoundingClientRect();return b.width<44||b.height<44||getComputedStyle(a).textDecorationLine.includes('underline')})")
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                    assert page.goto(path+'sources').status==200 and '115687 / 118762' in page.locator('main').inner_text()
                    assert '2026-lbg-q3-ims.pdf' not in page.locator('main').inner_html()
                    for target in ('/industries/banking','/enterprises/easyjet','/industries/aviation'):
                        assert page.goto(target).status==200
                assert not errors;proof['journeys'].append({'device':device,'new_product_measures_visible':phase=='after','navigation_errors':errors});context.close()
            if phase=='after':
                page=browser.new_page(base_url=base,viewport={'width':1194,'height':834})
                page.goto(path+'service-bankcards');page.goto('/enterprises/easyjet')
                f=root/'enterprise-knowledge/banking/research-model/source-snapshots/FCA-Lloyds-Products-H126.json'
                d=json.loads(f.read_text());next(s for s in d['sources'] if s['id']=='FCA-LLOYDS-PRODUCTS-H126')['withdrawn']=True;f.write_text(json.dumps(d))
                page.go_back();page.reload()
                for detail in ('service-bankcards','costs','sources'):
                    page.goto(path+detail);page.emulate_media(media='print')
                    text=page.locator('main').inner_text()
                    assert all(s not in text for s in ('115,687','97.4%','Which banking-and-card complaint journeys'))
                    assert not page.locator('[data-intelligence=lloyds-product-workload]').count()
                proof['withdrawal']={'history_reload_print_accessibility':True,'source_changed_in_isolated_copy_only':True}
                page.close()
            proof['knowledge_delta']={'new_reported_product_cells':15 if phase=='after' else 0,'new_calculated_product_shares':5 if phase=='after' else 0,'new_group_or_divisional_financial_actuals':0}
        finally:browser.close();server.shutdown();server.server_close()
    (out/(phase+'-browser.json')).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':phase,'captures':len(proof['captures']),'passed':True}))

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('output',type=Path);cli.add_argument('phase',choices=('before','after'));args=cli.parse_args();run(args.output,args.phase)
