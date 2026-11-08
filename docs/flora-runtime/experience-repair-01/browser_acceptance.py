"""Same visible-browser checks against pinned main and Repair 01, isolated stores."""
from pathlib import Path
import argparse,json,time
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--before-port',type=int,default=18790);parser.add_argument('--after-port',type=int,default=18791);args=parser.parse_args()
root=args.output;root.mkdir(parents=True,exist_ok=True)
paths=[('home','/'),('landing','/flora/banking'),('bank','/flora/banking/barclays'),('opportunity','/flora/banking/barclays/opportunity/COH-BAR-001'),('evidence','/flora/banking/barclays/evidence'),('signals','/flora/banking/signals'),('timeline','/flora/banking/timeline'),('ai-native','/flora/banking/ai-native'),('portfolio','/flora/banking/portfolio'),('pipeline','/flora/banking/pipeline'),('heatmap','/flora/banking/heatmap?mode=opportunity-value'),('heatmap-detail','/flora/banking/heatmap/detail?mode=opportunity-value&theme=Cost%20transformation&bank=barclays'),('compare','/flora/banking/compare'),('competitors','/flora/banking/competitors'),('events','/flora/banking/barclays/event-timeline'),('industry-inspection','/industries/uk-banking'),('intelligence','/intelligence?tab=industries')]
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for version,port in [('before',args.before_port),('after',args.after_port)]:
  for viewport,width,height in [('desktop',1440,1050),('ipad',1024,1366)]:
   page=b.new_page(viewport={'width':width,'height':height},has_touch=viewport=='ipad',is_mobile=viewport=='ipad',extra_http_headers={'X-Flora-User':'alice','X-Flora-Enterprises':'*','X-Flora-Roles':'blueprint_import_admin'})
   for tag,path in paths:
    started=time.perf_counter();resp=page.goto(f'http://127.0.0.1:{port}'+path,wait_until='load',timeout=60000);text=page.locator('body').inner_text();checks={}
    def check(name,required):
     checks[name]=all(page.get_by_text(s,exact=False).first.is_visible() for s in required)
    checks['HTTP 200']=resp.status==200
    checks['No unsupported buying assertion']='entering buying activity' not in text
    if tag=='home':
     check('H/I scoped estate',['1 curated Banking pilot','0 candidate imports','0 partial releases','Complete Industry Twin acceptance: Not established']);checks['No governed count']='1 governed' not in text
    elif tag=='intelligence':check('I curated route',['Curated repository Banking pilot','not accepted canonical Industry intelligence'])
    else:
     check('I/M visible source scope',['Curated repository Banking pilot','not accepted canonical intelligence','Claim-level accepted Evidence: Not supplied by this pilot'])
     check('G working rankings and horizons',['strategic working scenarios'])
     if tag=='landing':check('F editorial conviction',['Editorial conviction: High','list position','not calibrated Evidence confidence'])
     if tag=='signals':check('F editorial conviction',['editorial working assessments','not calibrated Evidence confidence'])
     if tag in ['bank','opportunity','heatmap-detail']:
      check('B/C explicit sizing and timing',['Illustrative, unverified commercial scenario','£60m–£120m','£70m × category 0.95 × scope 1.25','Customer-confirmed budget: Unknown','Qualified commercial pipeline: Not established','Scenario timing assumption','Confirmed procurement dates / customer milestones / buying triggers: Unknown'])
     if tag=='bank':check('A scenario sum',['£205m','85 + 80 + 40','not customer-confirmed budget or qualified commercial pipeline'])
     if tag in ['opportunity','heatmap-detail']:check('D supplier inference',['Accenture','Inferred supplier position','2025-01-01','Major-bank transformation services market presence','Contract-specific accepted Evidence: Not supplied','not a verified contract date'])
     if tag=='opportunity':check('E no current demand',['no current buying activity is established'])
     if tag=='evidence':check('J honest provenance',['canonical Evidence IDs / accepted Observation mappings / source locators: Not supplied','view identity only','does not prove claim-level provenance'])
    out=root/version/viewport;out.mkdir(parents=True,exist_ok=True);(out/(tag+'.txt')).write_text(text)
    row={'version':version,'viewport':viewport,'route':path,'checks':checks,'passed':all(checks.values()),'seconds':round(time.perf_counter()-started,3),'horizontal_overflow_px':page.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')};results.append(row)
    if tag in ['home','landing','opportunity','bank','evidence','industry-inspection']:
     if tag=='opportunity' and version=='after':page.get_by_role('heading',name='Estimated value',exact=True).scroll_into_view_if_needed()
     page.screenshot(path=str(out/(tag+'.png')))
    if tag=='opportunity' and version=='after':
     page.get_by_role('heading',name='Supplier landscape',exact=True).scroll_into_view_if_needed();page.screenshot(path=str(out/'opportunity-supplier.png'))
    (root/'results.json').write_text(json.dumps(results,indent=2))
   # Exercise the actual preserved links, not only direct page requests.
   page.goto(f'http://127.0.0.1:{port}/');page.locator('a[href="/flora/banking"]').first.click();page.wait_for_load_state('load');page.locator('a[href="/flora/banking/barclays"]').first.click();page.wait_for_load_state('load');page.locator('a[href="/flora/banking/barclays/opportunity/COH-BAR-001"]').first.click();page.wait_for_load_state('load');results.append({'version':version,'viewport':viewport,'click_journey':'Home -> Banking -> Barclays -> scenario detail','passed':page.url.endswith('COH-BAR-001')});page.close()
 b.close()
(root/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps({v:{'checks':sum(len(r.get('checks',{})) for r in results if r['version']==v),'failed_routes':sum(not r['passed'] for r in results if r['version']==v),'journeys':len([r for r in results if r['version']==v])} for v in ['before','after']},indent=2))
raise SystemExit(int(any(not r['passed'] for r in results if r['version']=='after')))
