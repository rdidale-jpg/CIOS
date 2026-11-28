"""Actual integrated enterprise journey, responsive geometry and lifecycle proof."""
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
VIEWS={'group':'','inside':'?stream=inside&focus=operations','leadership':'?stream=inside&focus=people&detail=leadership','workforce':'?stream=inside&focus=people&detail=workforce','programmes':'?stream=inside&focus=programmes','forces':'?stream=forces','capital':'?focus=economics&detail=capital','capability':'?stream=inside&focus=capabilities&detail=data','payments':'?stream=inside&focus=operations&detail=journey-payments'}
DEEP={'commercial':'?focus=commercial','insurance':'?focus=retirement','economics':'?focus=economics&detail=comparison','technology':'?stream=inside&focus=applications&detail=frontier','fraud':'?stream=inside&focus=applications&detail=fraud','ai':'?stream=forces&focus=strategy&detail=objective-ai','brands':'?focus=group&detail=brands','funding':'?focus=economics&detail=funding','retail':'?focus=retail','data-activity':'?stream=inside&focus=operations&detail=journey-data','platform-activity':'?stream=inside&focus=operations&detail=journey-platforms'}

def run(out,phase):
    out.mkdir(parents=True,exist_ok=True);root=Path.cwd()
    runtime=('cios/applications/flora/lloyds_gold.py','cios/applications/flora/visual_stream_assets/lloyds-gold.css','enterprise-knowledge/banking/research-model/Assessment-Overlay.json')
    proof={'phase':phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'runtime_hashes':{p:sha256((root/p).read_bytes()).hexdigest() for p in runtime},'runtime_matches_sha':all(subprocess.check_output(['git','show','HEAD:'+p])==(root/p).read_bytes() for p in runtime),'environment':'Actual isolated HTTP Chromium; emulated iPads/mobile, not Render or physical Safari','captures':{},'devices':[],'checks':{},'navigation_pairs':[],'print_findings':{}}
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
                        overflow=page.locator('main .ce-node').evaluate_all("nodes=>nodes.filter(n=>{let b=n.getBoundingClientRect(),p=n.parentElement.getBoundingClientRect();return n.scrollHeight>n.clientHeight+3||b.bottom>p.bottom+3||b.top<p.top-3}).map(n=>({label:n.getAttribute('aria-label'),height:n.clientHeight,content:n.scrollHeight}))")
                        assert not overflow,(device,name,overflow)
                    file=f'{phase}-{device}-{name}.jpg';page.screenshot(path=out/file,full_page=True,quality=72);proof['captures'][file]=sha256((out/file).read_bytes()).hexdigest()
                views=dict(VIEWS) if phase=='after' else {k:VIEWS[k] for k in ('group','inside','forces','workforce')}
                views.update({'commercial':'?focus=commercial','ai-goal':'?stream=forces&focus=strategy&detail=objective-ai'})
                if phase=='after':views.update({'commercial-context':'?stream=inside&focus=operations&subject=commercial&detail=commercial-context','commercial-direction':'?stream=forces&focus=competition&subject=commercial&detail=commercial-direction','ai-economics':'?stream=landscape&focus=economics&detail=ai-value','finance-leader':'?stream=inside&focus=people&detail=leader-chalmers'})
                for name,q in views.items():
                    assert page.goto('/enterprises/lloyds'+q).status==200;capture(name)
                if phase=='after':
                    from cios.applications.flora import lloyds_gold as g
                    from urllib.parse import urlencode, urlsplit, parse_qs
                    for key,title,states in g.V3_PATHS:
                        for stream,focus,detail in states:
                            subject='commercial' if key in {'commercial','transactions'} else 'group'
                            page.goto('/enterprises/lloyds?'+urlencode({'stream':stream,'focus':focus,'detail':detail,'subject':subject}))
                            target=states[(list(states).index((stream,focus,detail))+1)%3]
                            page.get_by_role('navigation',name='Insight streams').get_by_role('link',name=target[0].title(),exact=True).click()
                            selected=parse_qs(urlsplit(page.url).query,keep_blank_values=True)
                            assert (selected['stream'][0],selected['focus'][0],selected['detail'][0])==target,(key,target,selected)
                            assert selected['subject']==[subject]
                            chosen=page.url;page.reload();page.go_back();page.go_forward();assert page.url==chosen
                            proof['navigation_pairs'].append({'device':device,'topic':key,'from':stream,'to':target[0],'subject':subject})
                    if device=='desktop':
                        page.goto('/enterprises/lloyds?stream=forces')
                        proof['print_findings']['screen_main_background']=page.locator('main').evaluate('e=>getComputedStyle(e).backgroundColor')
                        proof['print_findings']['screen_node_backgrounds']=page.locator('.ce-node').evaluate_all('es=>[...new Set(es.map(e=>getComputedStyle(e).backgroundColor))]')
                        page.pdf(path=str(out/'forces-print.pdf'),print_background=True,format='A4')
                        page.emulate_media(media='print')
                        proof['print_findings']['print_node_backgrounds']=page.locator('.ce-node').evaluate_all('es=>[...new Set(es.map(e=>getComputedStyle(e).backgroundColor))]')
                        page.emulate_media(media='screen')
                    def activate(label):
                        target=page.locator('main').get_by_role('link',name=label,exact=True);target.scroll_into_view_if_needed();box=target.bounding_box()
                        if device=='desktop':page.mouse.click(box['x']+box['width']*.7,box['y']+box['height']*.75)
                        else:page.touchscreen.tap(box['x']+box['width']*.7,box['y']+box['height']*.75)
                    page.goto('/enterprises/lloyds');activate('Commercial Banking');page.wait_for_url('**focus=commercial**')
                    assert 'Amanda Murphy' in page.locator('main').inner_text() and 'John Langley' in page.locator('main').inner_text()
                    activate('Transaction Banking');page.wait_for_url('**detail=transactions**');assert 'Natasha Condon' in page.locator('main').inner_text()
                    chosen=page.url;page.reload();page.go_back();page.go_forward();assert page.url==chosen
                    page.goto('/enterprises/lloyds?stream=inside');activate('Risk & controls');page.wait_for_url('**detail=journey-risk**');assert 'Tom Martin' in page.locator('main').inner_text()
                    page.goto('/enterprises/lloyds?focus=economics');activate('Funding');page.wait_for_url('**detail=funding**');assert all(x in page.locator('main').inner_text() for x in ('£502.777bn','£496.457bn','6320m'))
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
                proof['checks']={'integrated_business_operating_strategy_journeys':True,'node_content_inside_touch_regions':True,'native_physical_targets':True,'keyboard':True,'touch':True,'history_reload_direct_links':True,'withdrawal_history_print_accessibility':True,'independent_funding_survives':True,'no_javascript':True,'banking_easyjet_legacy':True};page.close()
        finally:browser.close();server.shutdown();server.server_close()
    (out/(phase+'-browser.json')).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':phase,'captures':len(proof['captures']),'devices':len(proof['devices']),'passed':True}))

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('out',type=Path);cli.add_argument('phase',choices=['before','after']);args=cli.parse_args();run(args.out,args.phase)
