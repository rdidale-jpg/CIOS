"""Real HTTP/Chromium journeys and unchanged-baseline comparisons."""
from copy import deepcopy
from hashlib import sha256
from http.server import ThreadingHTTPServer
import argparse,json,os,re,shutil,subprocess,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
sys.path.insert(0,str(Path.cwd()))
from playwright.sync_api import sync_playwright,expect
from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora import visual_streams as v
cli=argparse.ArgumentParser();cli.add_argument('output');cli.add_argument('phase',choices=('before','after'));args=cli.parse_args()
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
proof={'phase':args.phase,'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'devices':[],'baseline':{},'screenshots':{},'runtime_hashes':{}}
for path in ('cios/applications/flora/lloyds_gold.py','cios/applications/flora/visual_stream_assets/lloyds-gold.css','cios/applications/flora/web/app.py','cios/applications/flora/public_routes.py'):
 if Path(path).exists():proof['runtime_hashes'][path]=sha256(Path(path).read_bytes()).hexdigest()
with TemporaryDirectory(prefix='flora-gold-browser-') as runtime,sync_playwright() as pw:
 os.environ.update(FLORA_DATA_DIR=runtime,FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0');os.environ.pop('OPENAI_API_KEY',None)
 server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler);worker=Thread(target=server.serve_forever,daemon=True);worker.start()
 executable=shutil.which('chromium');browser=pw.chromium.launch(**({'executable_path':executable} if executable else {}),args=['--no-sandbox'])
 base='http://127.0.0.1:'+str(server.server_port)
 try:
  for device,width,height in [('desktop',1440,1000),('ipad-landscape',1194,834),('ipad-portrait',834,1194),('mobile',390,844)]:
   page=browser.new_page(base_url=base,viewport={'width':width,'height':height},has_touch=device!='desktop',reduced_motion='reduce');errors=[];failed=[]
   page.on('pageerror',lambda err:errors.append(str(err)));page.on('requestfailed',lambda req:failed.append(req.url))
   def capture(name):
    page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)');page.evaluate('scrollTo(0,0)')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(device,name,'overflow')
    filename=args.phase+'-'+device+'-'+name+'.jpg';page.screenshot(path=out/filename,quality=80);proof['screenshots'][filename]=sha256((out/filename).read_bytes()).hexdigest()
   for path,name in [('/enterprises/lloyds','default'),('/enterprises/lloyds/preview','original-preview'),('/enterprises/lloyds/preview?stream=forces&focus=renewal','original-forces')]:
    target='/enterprises/lloyds/legacy' if path=='/enterprises/lloyds' and '/enterprises/lloyds/legacy' in v.ROUTES else path
    assert page.goto(target).status==200
    content=re.sub(r'\s+',' ',page.locator('main').inner_text().replace('Gold Standard evaluation','')).strip();proof['baseline'][device+':'+name]=content
    if args.phase=='after':assert json.loads((out/'Browser-before.json').read_text())['baseline'][device+':'+name]==content,(device,name,'Preserved content changed')
    else:capture(name)
   if args.phase=='after':
    from cios.applications.flora import lloyds_gold as g
    page.get_by_role('link',name='Gold Standard evaluation',exact=True).click();expect(page.locator('main h1')).to_have_text('Group overview');capture('group')
    for stream,rows in g.REGIONS.items():
     page.get_by_role('navigation',name='Insight streams').get_by_role('link',name=stream.title(),exact=True).click()
     for key,label in rows:
      if width<1000 and not page.locator('#enterprise-scene').is_visible():page.get_by_role('button',name='Explore Lloyds',exact=True).click()
      target=page.locator('[data-region-key="'+key+'"]');size=target.bounding_box();assert size['width']>=44 and size['height']>=44
      if device=='desktop':target.focus();page.keyboard.press('Enter')
      else:target.tap()
      expect(page.locator('main h1')).to_have_text(label);expect(page.locator('[data-region-key="'+key+'"][aria-current]')).to_have_count(1);expect(page.locator('main details')).to_have_count(0)
    for focus,stream,name in [('economics','landscape','economics'),('operations','inside','operating-model'),('applications','inside','applications'),('programmes','inside','transformation'),('analysis','forces','analysis')]:
     page.goto(g.href(g.State(stream,focus,focus)));capture(name)
     if focus=='analysis':
      expect(page.locator('.gold-swot>section')).to_have_count(4)
      for index in range(8):
       page.locator('main a[href*="detail=theme-'+str(index)+'"]').click();expect(page.locator('main')).to_contain_text('Counter-evidence and decision boundary');page.get_by_role('link',name='← Analysis',exact=True).click()
     if focus=='applications':
      page.get_by_role('link',name='Envoy',exact=True).click();expect(page.locator('main')).to_contain_text('does not establish a contracting entity');expect(page.locator('main')).to_contain_text('not an asserted Lloyds architecture');expect(page.locator('main')).not_to_contain_text('Contracted Google Cloud service')
      page.get_by_role('link',name='Evidence & dates',exact=True).click();expect(page.locator('main h2')).to_have_text('Evidence, dates & boundaries');assert not page.locator('main a[href*=".pdf"]').count()
    page.goto(g.href(g.State('inside','operations','operations','service')));expect(page.locator('[data-owner-item]')).to_have_count(3);expect(page.locator('main')).to_contain_text('not consolidated Group or Retail');capture('service-outcomes')
    page.goto(g.href(g.State('landscape','commercial','commercial')));page.get_by_role('navigation',name='Insight streams').get_by_role('link',name='Inside',exact=True).click();expect(page.locator('main')).to_contain_text('From Commercial Banking')
    url=page.url;page.reload();assert page.url==url;page.go_back();expect(page.locator('main h1')).to_have_text('Commercial Banking');page.go_forward();expect(page.locator('main')).to_contain_text('From Commercial Banking')
    page.get_by_role('navigation',name='Insight streams').get_by_role('link',name='Landscape',exact=True).click();expect(page.locator('main h1')).to_have_text('Commercial Banking')
    page.get_by_role('link',name='Original preview',exact=True).click();assert '/gold' not in page.url
    page.get_by_role('link',name='Return to current experience',exact=True).click();assert '/preview' not in page.url
    if device=='desktop':
     page.goto(g.PATH);page.evaluate("document.documentElement.style.zoom='2'");capture('zoom-200');page.evaluate("document.documentElement.style.zoom='1'")
    if device=='ipad-portrait':
     page.goto(g.PATH);page.get_by_role('button',name='Explore Lloyds',exact=True).click();capture('illustration-expanded')
   for path,title in [('/industries/banking','Banking'),('/industries/aviation','Aviation'),('/enterprises/easyjet','easyJet')]:
    assert page.goto(path).status==200;assert title.lower() in page.locator('body').inner_text().lower()
   assert not errors and not failed,(errors,failed)
   proof['devices'].append({'device':device,'fifteen_native_image_selections':args.phase=='after','eight_swot_theme_drills':args.phase=='after','application_evidence_unknowns':args.phase=='after','context_reload_history':args.phase=='after','original_and_previous_default_preserved':True,'no_overflow':True,'keyboard_or_touch':True,'errors':errors});page.close()
  if args.phase=='after':
   page=browser.new_page(base_url=base,viewport={'width':1194,'height':834});source=v.current_data;d=deepcopy(source(v.Context('lloyds','landscape')))
   page.goto(g.href(g.State('landscape','economics','economics')));expect(page.locator('main')).to_contain_text('£502.8bn');page.goto(g.href(g.State('forces','analysis','analysis')))
   next(s for s in d['sources'] if s['id']=='PR-LBG-Q326')['withdrawn']=True;v.current_data=lambda ctx:d
   try:
    page.go_back();expect(page.locator('main')).not_to_contain_text('£502.8bn');assert not page.locator('meter[value="502.8"]').count();expect(page.locator('main')).not_to_contain_text('£6.3bn')
    page.reload();page.emulate_media(media='print');expect(page.locator('main')).not_to_contain_text('£6.6bn');page.screenshot(path=out/'after-withdrawal-ipad.jpg');proof['screenshots']['after-withdrawal-ipad.jpg']=sha256((out/'after-withdrawal-ipad.jpg').read_bytes()).hexdigest()
    page.goto(g.href(g.State('forces','analysis','analysis')));assert not page.locator('main a[href*="detail=theme-4"]').count();proof['withdrawal']={'browser_history_reload_print_accessible_values':True}
   finally:v.current_data=source
   ns=browser.new_context(base_url=base,java_script_enabled=False);page=ns.new_page();page.goto(g.PATH+'?stream=forces&focus=analysis');page.locator('main a[href*="detail=theme-0"]').click();expect(page.locator('main')).to_contain_text('Counter-evidence');proof['no_javascript']=True;ns.close()
  (out/('Browser-'+args.phase+'.json')).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'phase':args.phase,'devices':len(proof['devices']),'captures':len(proof['screenshots']),'passed':True}))
 finally:browser.close();server.shutdown();server.server_close();worker.join(2)
