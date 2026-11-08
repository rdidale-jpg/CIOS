"""Visible local discovery, isolation and navigation checks on identical fixtures."""
from pathlib import Path
from hashlib import sha256
import json,time
from playwright.sync_api import sync_playwright
import os
root=Path(os.environ['FLORA_DISCOVERY_BROWSER_EVIDENCE']).resolve();out=root/'browser';out.mkdir(exist_ok=True)
meta=json.loads((root/'browser-fixtures/fixture-metadata.json').read_text());run=meta['source_import_run_id'];name='UK Banking and Financial Services (isolated test)'
H={'X-Flora-User':'alice','X-Flora-Enterprises':'*','X-Flora-Roles':'blueprint_import_admin','X-Flora-Active-Workspace':'workspace-a'}
paths=[('home','/'),('intelligence','/intelligence?tab=industries'),('directory','/digital-twins')]
rows=[]
def files(path):return {str(p.relative_to(path)):sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}
before_files={d:files(root/'browser-fixtures'/d) for d in ['before-current','current','history','empty']}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for version,port in [('before',18800),('after',18801)]:
  for viewport,width,height in [('desktop',1440,1050),('ipad',1024,1366)]:
   for audience,headers in [('owner',H),('wrong-workspace',H|{'X-Flora-Active-Workspace':'workspace-b'}),('anonymous',{})]:
    page=browser.new_page(viewport={'width':width,'height':height},is_mobile=viewport=='ipad',has_touch=viewport=='ipad',extra_http_headers=headers)
    for tag,path in paths:
     start=time.perf_counter();response=page.goto(f'http://127.0.0.1:{port}'+path,wait_until='load');text=page.locator('body').inner_text();checks={}
     def visible(s):return page.get_by_text(s,exact=False).first.is_visible()
     checks['HTTP 200']=response.status==200
     checks['shared visible discovery']=visible('Intelligence discovery')
     checks['curated source remains visible']=visible('Source-curated') and visible('Curated repository Banking pilot')
     checks['no false governed count']='1 governed' not in text and 'Status: Governed' not in text
     checks['typed entries without duplicates']=page.locator('.discovery-item').count()==(4 if audience=='owner' else 1)
     checks['no horizontal overflow']=page.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')==0
     if audience=='owner':
      checks['actual BNK partial workspace']=visible(name) and visible('Status: Partially promoted') and page.locator(f'a[href="/blueprint-import/{run}/intelligence"]').count()>0
      checks['model-backed existing Canvas']=visible('Status: Model-backed') and page.locator('a[href="/digital-twins/synthetic-airline/canvas"]').count()>0
      checks['identity ambiguity visible']=visible('ambiguous') and visible('Identity unresolved')
      checks['private model absent']='private-protected-fixture' not in page.content()
     else:
      checks['no protected names IDs destinations']=all(s not in page.content() for s in [name,run,'synthetic-airline','private-protected-fixture','Ambiguous source fixture'])
     dest=out/version/viewport/audience;dest.mkdir(parents=True,exist_ok=True);(dest/(tag+'.txt')).write_text(text)
     if audience=='owner' or (version=='after' and viewport=='ipad'):
      page.screenshot(path=str(dest/(tag+'.png')))
     rows.append({'version':version,'viewport':viewport,'audience':audience,'path':path,'checks':checks,'passed':all(checks.values()),'seconds':round(time.perf_counter()-start,3)})
    page.close()
   # Both supported inspection aliases must reach the same existing source view.
   page=browser.new_page(viewport={'width':width,'height':height},extra_http_headers=H)
   responses=[]
   for path in ['/industries/uk-banking','/flora/banking/inspect']:
    response=page.goto(f'http://127.0.0.1:{port}'+path);responses.append((response.status,page.locator('body').inner_text()))
   checks={'both aliases 200':all(s==200 for s,_ in responses),'same visible source view':responses[0][1]==responses[1][1]}
   rows.append({'version':version,'viewport':viewport,'audience':'owner','path':'inspection aliases','checks':checks,'passed':all(checks.values())});page.close()
 # New existing-route journey, actual retained source content; no external research.
 for viewport,width,height in [('desktop',1440,1050),('ipad',1024,1366)]:
  page=browser.new_page(viewport={'width':width,'height':height},has_touch=viewport=='ipad',is_mobile=viewport=='ipad',extra_http_headers=H)
  base='http://127.0.0.1:18801';page.goto(base+'/');page.get_by_role('link',name='Intelligence',exact=True).first.click();page.wait_for_load_state('load')
  item=page.locator('.discovery-item').filter(has=page.get_by_role('heading',name=name,exact=True));item.get_by_role('link').click();page.wait_for_load_state('load');assert page.url.endswith('/intelligence')
  page.locator(f'a[href="/blueprint-import/{run}/aspects/enterprises?domain=all"]').first.click();page.wait_for_load_state('load')
  page.locator('a.enterprise-card').filter(has=page.get_by_role('heading',name='Barclays PLC',exact=True)).click();page.wait_for_load_state('load');assert 'Evidence and Uncertainty' in page.locator('body').inner_text()
  dest=out/'after'/viewport/'journey';dest.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(dest/'dossier.png'))
  local=page.get_by_role('link',name='Open evidence',exact=True).first.get_attribute('href');assert local.startswith('/blueprint-import/')
  page.get_by_role('link',name='Open evidence',exact=True).first.click();page.wait_for_load_state('load');assert page.url.startswith(base+'/blueprint-import/')
  assert 'Evidence' in page.locator('body').inner_text();page.screenshot(path=str(dest/'evidence.png'))
  rows.append({'version':'after','viewport':viewport,'audience':'owner','path':'Home -> Intelligence -> Industry -> enterprise dossier -> Evidence','checks':{'existing click journey':True},'passed':True})
  page.goto(base+'/digital-twins');page.locator('a[href="/digital-twins/synthetic-airline/canvas"]').click();page.wait_for_load_state('load');assert 'synthetic' in page.locator('body').inner_text().lower()
  rows.append({'version':'after','viewport':viewport,'audience':'owner','path':'Discovery -> existing authorised Canvas','checks':{'model destination available':True},'passed':True});page.close()
  for label,port,status in [('history',18802,'Superseded'),('empty',18803,'Source-curated')]:
   page=browser.new_page(viewport={'width':width,'height':height},extra_http_headers=H)
   for tag,path in paths:
    response=page.goto(f'http://127.0.0.1:{port}'+path);text=page.locator('body').inner_text();checks={'HTTP 200':response.status==200,'visible owner status':page.get_by_text('Status: '+status,exact=False).first.is_visible(),'no horizontal overflow':page.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')==0}
    if label=='history':checks['historical is not current']='Current release: No' in text
    else:checks['no fake model/import']='Imported Industry Twin workspace' not in text and 'Status: Model-backed' not in text
    dest=out/'after'/viewport/label;dest.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(dest/(tag+'.png')));rows.append({'version':'after','viewport':viewport,'audience':label,'path':path,'checks':checks,'passed':all(checks.values())})
   page.close()
 browser.close()
after_files={d:files(root/'browser-fixtures'/d) for d in before_files}
integrity={d:before_files[d]==after_files[d] for d in before_files};assert all(integrity.values())
(out/'results.json').write_text(json.dumps({'observations':rows,'owner_store_bytes_unchanged':integrity},indent=2))
summary={v:{'observations':sum(x['version']==v for x in rows),'checks':sum(len(x['checks']) for x in rows if x['version']==v),'failures':[{'path':x['path'],'viewport':x['viewport'],'audience':x['audience'],'failed':[k for k,w in x['checks'].items() if not w]} for x in rows if x['version']==v and not x['passed']]} for v in ['before','after']};print(json.dumps(summary,indent=2));raise SystemExit(int(bool(summary['after']['failures'])))
