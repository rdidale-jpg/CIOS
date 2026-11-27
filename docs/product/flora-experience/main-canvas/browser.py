"""Real loopback canvas comparison and physical interaction proof; no live writes."""
import argparse,json,os,subprocess,sys
from copy import deepcopy
from hashlib import sha256
from http.server import ThreadingHTTPServer
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory
from threading import Thread
from playwright.sync_api import expect,sync_playwright
sys.path.insert(0,str(Path.cwd()))
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora import visual_streams as v,lloyds_gold as g
ROOT=Path.cwd();PATH='/enterprises/lloyds'
VIEWS={'group':'','economics':'?focus=economics','organisation':'?stream=inside&focus=people&detail=structure',
 'operating':'?stream=inside&focus=operations','capabilities':'?stream=inside&focus=capabilities',
 'applications':'?stream=inside&focus=applications','programmes':'?stream=inside&focus=programmes',
 'strategy':'?stream=forces&focus=strategy&detail=goals','swot':'?stream=forces&focus=analysis'}
SIZES={'desktop':(1440,1000),'ipad-landscape':(1194,834),'ipad-portrait':(834,1194),'mobile':(390,844)}
class Quiet(FloraWebHandler):
 def log_message(self,*args):pass

def run(phase,out,smoke=False):
 proof={'phase':phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'runtime_hashes':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in [ROOT/'cios/applications/flora/lloyds_gold.py',ROOT/'cios/applications/flora/visual_stream_assets/lloyds-gold.css']},
 'environment':'Isolated HTTP Chromium; emulated iPads/touch; no Render or physical Safari claim',
 'screenshots':{},'devices':[],'audits':{}}
 with TemporaryDirectory(prefix='flora-canvas-')as scratch,sync_playwright()as pw:
  os.environ.update(FLORA_DATA_DIR=scratch,FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0');os.environ.pop('OPENAI_API_KEY',None)
  server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);worker=Thread(target=server.serve_forever,daemon=True);worker.start()
  browser=pw.chromium.launch(**({'executable_path':which('chromium')}if which('chromium')else{}),args=['--no-sandbox']);base=f'http://127.0.0.1:{server.server_port}'
  try:
   for device,(width,height)in SIZES.items():
    if smoke and device!='desktop':continue
    page=browser.new_page(base_url=base,viewport={'width':width,'height':height},has_touch=device!='desktop',reduced_motion='reduce');errors=[];failed=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:failed.append(r.url))
    def capture(name):
     page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(device,name)
     page.evaluate('scrollTo(0,0)');file=f'{phase}-{device}-{name}.jpg';page.screenshot(path=out/file,quality=80);proof['screenshots'][file]=sha256((out/file).read_bytes()).hexdigest()
    for name,query in VIEWS.items():
     response=page.goto(PATH+query);assert response.status==200,(name,response.status)
     if phase=='before':
      proof['audits'][device+':'+name]=page.locator('main').evaluate("m=>({underlinedInternal:[...m.querySelectorAll('a[href]')].filter(a=>a.getAttribute('href').startsWith('/')&&!a.closest('.gold-inspect')&&getComputedStyle(a).textDecorationLine.includes('underline')).length,visualRegions:m.querySelectorAll('[data-canvas-region]').length})")
     if phase=='after':
      audit=page.locator('main').evaluate('''main=>({
       underlined:[...main.querySelectorAll('a[data-canvas-region]')].filter(a=>getComputedStyle(a).textDecorationLine.includes('underline')).map(a=>a.textContent),
       small:[...main.querySelectorAll('a[data-canvas-region]')].filter(a=>{const b=a.getBoundingClientRect();return b.width<44||b.height<44}).map(a=>a.textContent),
       bare:[...main.querySelectorAll('.gold-content a[href]')].filter(a=>!a.matches('[data-canvas-region],[data-canvas-exception]')&&!a.closest('.gold-inspect')&&a.getAttribute('href').startsWith('/')).map(a=>a.outerHTML),
       nested:main.querySelectorAll('a a').length,regions:main.querySelectorAll('[data-canvas-region]').length})''')
      assert not audit['underlined']and not audit['small']and not audit['bare']and not audit['nested'],(device,name,audit)
      proof['audits'][device+':'+name]=audit
     capture(name)
    if phase=='after' and not smoke:
     def physical(query,selector,expected):
      page.goto(PATH+query);target=page.locator(selector).first;target.scroll_into_view_if_needed();box=target.bounding_box()
      # Physical body hit, away from the heading's position.
      x=box['x']+box['width']*.72;y=box['y']+box['height']*.78
      if device=='desktop':page.mouse.click(x,y)
      else:page.touchscreen.tap(x,y)
      page.wait_for_url(lambda url:expected in str(url))
      assert expected in page.url,(device,selector,page.url)
     physical('', 'main .canvas-businesses a','focus=')
     physical('?focus=economics','main .ce-capital>a[aria-label=Funding]','detail=funding')
     physical('?focus=economics&detail=funding','main .canvas-stock','detail=comparison')
     physical('?stream=inside&focus=operations','main .ce-operating>a[href*="detail=journey-"]','detail=journey-')
     physical('?stream=inside&focus=people&detail=structure','main .canvas-businesses a','stream=landscape')
     physical('?stream=inside&focus=capabilities','main .ce-operating>a[href*="detail=journey-"]','detail=journey-')
     physical('?stream=inside&focus=programmes','main .canvas-timeline a','detail=')
     physical('?stream=forces&focus=strategy&detail=goals','main .canvas-goal-rail a','detail=objective-')
     # Quadrant's upper-right surface and the full theme surface are distinct.
     page.goto(PATH+'?stream=forces&focus=analysis');quad=page.locator('main .canvas-quadrant').first;box=quad.bounding_box();(page.mouse.click if device=='desktop'else page.touchscreen.tap)(box['x']+box['width']*.85,box['y']+60)
     page.wait_for_url(lambda url:'detail=quadrant-'in str(url));assert 'detail=quadrant-'in page.url
     page.goto(PATH+'?stream=forces&focus=analysis');target=page.locator('main .canvas-themes>a').first;target.scroll_into_view_if_needed();box=target.bounding_box();(page.mouse.click if device=='desktop'else page.touchscreen.tap)(box['x']+box['width']*.75,box['y']+box['height']*.8);page.wait_for_url(lambda url:'detail=theme-'in str(url));assert 'detail=theme-'in page.url
     chosen=page.url;page.reload();assert page.url==chosen;page.go_back();page.go_forward();assert page.url==chosen
     page.goto(PATH+'?stream=inside&focus=applications&detail=envoy');inspection=page.get_by_role('link',name='Evidence & dates',exact=True);expect(inspection).to_be_visible();box=inspection.bounding_box();assert box['width']>=44 and box['height']>=44
     inspection.click();expect(page.locator('main h2')).to_have_text('Evidence, dates & boundaries');assert not page.locator('main a[href*=".pdf"]').count()
     page.goto(PATH);link=page.locator('main .ce-economy>a[data-canvas-region=business]').first;link.hover();assert link.evaluate('e=>getComputedStyle(e).textDecorationLine')=='none';assert link.evaluate('e=>getComputedStyle(e).boxShadow')!='none';link.focus();assert link.evaluate('e=>getComputedStyle(e).outlineStyle')=='solid';page.keyboard.press('Enter');expect(page.locator('main h1')).to_have_text('Retail Banking')
     if device=='desktop':
      page.goto(PATH);page.evaluate("document.documentElement.style.zoom='2'");capture('zoom-200');page.evaluate("document.documentElement.style.zoom='1'")
     for route in (PATH+'/legacy',PATH+'/preview','/industries/banking','/industries/aviation','/enterprises/easyjet'):
      assert page.goto(route).status==200,route
    assert not errors and not failed,(errors,failed);proof['devices'].append({'device':device,'physical_hits':phase=='after'and not smoke,'inspection_visible_and_44px':phase=='after'and not smoke,'no_overflow':True,'errors':errors});page.close()
   if phase=='after' and not smoke:
    context=browser.new_context(base_url=base,java_script_enabled=False);page=context.new_page();page.goto(PATH+'?stream=forces&focus=analysis');page.locator('main .canvas-themes>a').first.click();expect(page.locator('main')).to_contain_text('Counter-evidence');context.close();proof['no_javascript']=True
    original=v.current_data;data=deepcopy(original(v.Context('lloyds','landscape')));next(s for s in data['sources']if s['id']=='PR-LBG-Q326')['withdrawn']=True
    page=browser.new_page(base_url=base);page.goto(PATH+'?focus=economics');assert '502.8'in page.locator('main').aria_snapshot();page.goto(PATH+'?stream=forces&focus=analysis');v.current_data=lambda ctx:data
    try:
     page.go_back();page.reload();page.emulate_media(media='print')
     for value in ('£502.8bn','£6.3bn','£6.6bn'):assert value not in page.locator('main').inner_text()and value not in page.locator('main').aria_snapshot()
     assert not page.locator('main meter[value="502.8"]').count();proof['withdrawal_history_reload_print_accessibility']=True
    finally:v.current_data=original
  finally:browser.close();server.shutdown();server.server_close();worker.join(2)
 (out/f'Browser-{phase}.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':phase,'captures':len(proof['screenshots']),'devices':len(proof['devices']),'passed':True}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['before','after']);p.add_argument('output',type=Path);p.add_argument('--smoke',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);run(a.phase,a.output.resolve(),a.smoke)
