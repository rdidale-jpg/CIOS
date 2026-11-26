"""Real isolated HTTP/Chromium CEO and predecessor journeys; no live writes."""
import argparse,json,os,re,subprocess,sys
from copy import deepcopy
from hashlib import sha256
from http.server import ThreadingHTTPServer
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory
from threading import Thread
from unittest.mock import patch
from playwright.sync_api import expect,sync_playwright
sys.path.insert(0,str(Path.cwd()))
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora import visual_streams as v
ROOT=Path.cwd();PATH='/enterprises/lloyds'
DEVICES={'desktop':(1440,1000),'ipad-landscape':(1194,834),'ipad-portrait':(834,1194),'mobile':(390,844)}
class Quiet(FloraWebHandler):
 def log_message(self,*args):pass

def run(phase,output):
 proof={'phase':phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  'environment':'isolated loopback Chromium; simulated iPads; not Render','devices':[],'screenshots':{},'predecessor':{},
  'runtime_hashes':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in (ROOT/'cios/applications/flora').rglob('*') if p.is_file() and p.suffix in {'.py','.css','.js'}}}
 with TemporaryDirectory(prefix='flora-ceo-') as runtime,sync_playwright() as driver:
  os.environ.update(FLORA_DATA_DIR=runtime,FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0');os.environ.pop('OPENAI_API_KEY',None)
  with ThreadingHTTPServer(('127.0.0.1',0),Quiet) as server:
   worker=Thread(target=server.serve_forever,daemon=True);worker.start()
   browser=driver.chromium.launch(**({'executable_path':which('chromium')} if which('chromium') else {}),args=['--no-sandbox']);base=f'http://127.0.0.1:{server.server_port}'
   try:
    for device,(width,height) in DEVICES.items():
     page=browser.new_page(base_url=base,viewport={'width':width,'height':height},has_touch=device!='desktop',reduced_motion='reduce');errors=[];failures=[]
     page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:failures.append(r.url))
     def capture(name):
      page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
      assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(device,name)
      page.evaluate('scrollTo(0,0)');filename=f'{phase}-{device}-{name}.jpg';page.screenshot(path=output/filename,quality=80);proof['screenshots'][filename]=sha256((output/filename).read_bytes()).hexdigest()
     for key,route in [('landscape',PATH),('inside',PATH+'?stream=inside'),('forces',PATH+'?stream=forces'),('preview',PATH+'/preview'),('gold',PATH+'/preview/gold')]:
      target=route.replace(PATH,PATH+'/legacy',1) if phase=='after' and key in {'landscape','inside','forces'} else route
      assert page.goto(target).status==200
      if key!='gold':
       text=re.sub(r'\s+',' ',page.locator('main').inner_text()).strip();proof['predecessor'][device+':'+key]=text
       if phase=='after':assert json.loads((output/'Browser-before.json').read_text())['predecessor'][device+':'+key]==text,(device,key)
      if phase=='before' and key in {'landscape','inside','forces'}:capture(key)
     if phase=='after':
      from cios.applications.flora import lloyds_gold as g
      assert page.goto('/').status==200
      page.get_by_role('navigation',name='Primary product navigation').get_by_role('link',name='Industries',exact=True).click();page.locator('a[href="/industries/banking"]:visible').first.click();page.locator('a[href="/enterprises/lloyds"]:visible').first.click()
      expect(page.locator('main h1')).to_have_text('Group overview');assert not page.locator('[data-preview]').count();expect(page.get_by_role('navigation',name='Reading mode')).to_have_count(0);capture('group')
      for stream,regions in g.REGIONS.items():
       page.get_by_role('navigation',name='Insight streams').get_by_role('link',name=stream.title(),exact=True).click()
       expect(page.get_by_role('navigation',name='Insight streams').locator('[aria-current="page"]')).to_have_text(stream.title())
       for key,label in regions:
        if stream=='inside' and key=='partners':key,label='people','Organisation & workforce'
        if width<1000 and not page.locator('#enterprise-scene').is_visible():
         page.get_by_role('button',name='Explore Lloyds',exact=True).click();expect(page.locator('#enterprise-scene')).to_be_visible()
        target=page.locator('[data-region-key="'+key+'"]');box=target.bounding_box();assert box['width']>=44 and box['height']>=44
        if device=='desktop':target.focus();page.keyboard.press('Enter')
        else:target.tap()
        expect(page.locator('main h1')).to_have_text(label);expect(page.locator('[data-region-key="'+key+'"][aria-current]')).to_have_count(1)
        assert page.url.split('?')[0].endswith(PATH);expect(page.locator('main details')).to_have_count(0)
      for name,query in [('economics','?focus=economics'),('retail','?focus=retail'),('organisation','?stream=inside&focus=people&detail=structure'),('workforce','?stream=inside&focus=people&detail=workforce'),('operating-model','?stream=inside&focus=operations'),('credit','?stream=inside&focus=operations&detail=journey-credit&subject=commercial'),('strategy','?stream=forces&focus=strategy&detail=goals'),('goal-ai','?stream=forces&focus=strategy&detail=objective-ai'),('analysis','?stream=forces&focus=analysis')]:
       assert page.goto(PATH+query).status==200;capture(name)
      expect(page.locator('.gold-swot>section')).to_have_count(4)
      for index in range(8):
       page.locator('main a[href*="detail=theme-'+str(index)+'"]').click();expect(page.locator('main')).to_contain_text('Counter-evidence and decision boundary');page.get_by_role('link',name='← Analysis',exact=True).click()
      for key,row in g.JOURNEYS.items():
       page.goto(PATH+'?stream=inside&focus=operations&detail=journey-'+key);expect(page.locator('main')).to_contain_text('Conceptual activity sequence');expect(page.locator('main')).to_contain_text(row[5])
      for key,*_ in g.OBJECTIVES:
       page.goto(PATH+'?stream=forces&focus=strategy&detail=objective-'+key);expect(page.locator('main')).to_contain_text(g.GOAL_DECISIONS[key][1])
      page.goto(PATH+'?stream=inside&focus=applications&detail=envoy');expect(page.locator('main')).to_contain_text('Contract end / renewal');expect(page.locator('main')).to_contain_text('Unknown')
      page.get_by_role('link',name='Evidence & dates',exact=True).click();expect(page.locator('main h2')).to_have_text('Evidence, dates & boundaries');assert not page.locator('main a[href*=".pdf"]').count()
      page.goto(PATH+'?focus=commercial');page.get_by_role('navigation',name='Insight streams').get_by_role('link',name='Inside',exact=True).click();expect(page.locator('main')).to_contain_text('From Commercial Banking')
      url=page.url;page.reload();assert page.url==url;page.go_back();expect(page.locator('main h1')).to_have_text('Commercial Banking');page.go_forward();expect(page.locator('main')).to_contain_text('From Commercial Banking')
      page.get_by_role('navigation',name='Insight streams').get_by_role('link',name='Landscape',exact=True).click();expect(page.locator('main h1')).to_have_text('Commercial Banking')
      if device=='desktop':page.goto(PATH);page.evaluate("document.documentElement.style.zoom='2'");capture('zoom-200');page.evaluate("document.documentElement.style.zoom='1'")
      if device=='ipad-portrait':page.goto(PATH);page.get_by_role('button',name='Explore Lloyds',exact=True).click();capture('illustration-open')
     for route,title in [('/industries/aviation','Aviation'),('/enterprises/easyjet','easyJet'),(PATH+'?stream=landscape&detail=flagship','Overview')]:
      response=page.goto(route);assert response.status==200,(route,response.status);expect(page.locator('main')).to_contain_text(title)
     assert not errors and not failures,(device,errors,failures)
     proof['devices'].append({'device':device,'previous_default_and_preview_equal':True,'ceo_navigation':phase=='after','fifteen_image_regions':phase=='after','nine_operating_areas_seven_goals_eight_swot_themes':phase=='after','no_overflow':True,'errors':errors,'failed_requests':failures});page.close()
    if phase=='after':
     page=browser.new_page(base_url=base);path=ROOT/'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.json';original=Path.read_text
     def withdrawn(p,*args,**kwargs):
      text=original(p,*args,**kwargs)
      if p==path:doc=json.loads(text);doc['source']['withdrawn']=True;return json.dumps(doc)
      return text
     page.goto(PATH+'?stream=inside&focus=people&detail=leadership');expect(page.locator('main')).to_contain_text('Charlie Nunn');page.goto(PATH+'?focus=economics')
     with patch.object(Path,'read_text',withdrawn):
      page.go_back();expect(page.locator('main')).not_to_contain_text('Charlie Nunn');page.reload();page.emulate_media(media='print');expect(page.locator('main')).not_to_contain_text('Charlie Nunn');page.goto(PATH);expect(page.locator('main')).to_contain_text('£502.8bn')
     original_data=v.current_data;data=deepcopy(original_data(v.Context('lloyds','landscape')));next(s for s in data['sources'] if s['id']=='PR-LBG-Q326')['withdrawn']=True
     page.goto(PATH+'?focus=economics');expect(page.locator('main')).to_contain_text('£502.8bn');page.goto(PATH+'?stream=forces&focus=analysis')
     with patch.object(v,'current_data',lambda ctx:data):
      page.go_back();page.reload()
      for value in ('£502.8bn','£6.3bn','£6.6bn'):expect(page.locator('main')).not_to_contain_text(value)
      assert not page.locator('meter[value="502.8"]').count()
     proof['withdrawal']={'role_history_reload_print':True,'finance_history_reload_print_accessible_values':True}
     context=browser.new_context(base_url=base,java_script_enabled=False);page=context.new_page();page.goto(PATH+'?stream=forces&focus=analysis');page.locator('main a[href*="detail=theme-0"]').click();expect(page.locator('main')).to_contain_text('Counter-evidence');proof['no_javascript']=True;context.close()
   finally:browser.close();server.shutdown();worker.join(2)
 (output/f'Browser-{phase}.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':phase,'devices':len(proof['devices']),'captures':len(proof['screenshots']),'passed':True}))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('phase',choices=['before','after']);parser.add_argument('output',type=Path);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);run(args.phase,args.output.resolve())
