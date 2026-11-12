"""Repeatable read-only browser validation; never starts/seeds/deploys a service."""
import argparse,json
from urllib.parse import urlsplit
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description='Read-only local FLORA research UI validation; requires Playwright and Chromium')
parser.add_argument('--base-url',required=True);parser.add_argument('--baseline-url',required=True);parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
for url in (args.base_url,args.baseline_url):
 parsed=urlsplit(url)
 if parsed.scheme!='https' or parsed.hostname not in ('localhost','127.0.0.1') or parsed.username or parsed.password:parser.error('Isolated local HTTPS servers only')
out=args.output;out.mkdir(parents=True,exist_ok=True)
checks=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for label,width,height in [('desktop',1440,1050),('tablet',1024,1366),('mobile',390,844)]:
  context=browser.new_context(ignore_https_errors=True,viewport={'width':width,'height':height},device_scale_factor=1,is_mobile=label=='mobile',has_touch=label!='desktop')
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  if label=='desktop':
   page.goto(args.baseline_url+'/industries');page.screenshot(path=str(out/'before-industries-desktop.png'),full_page=True)
  page.goto(args.base_url+'/industries');page.get_by_role('link',name='Explore technology research').click()
  page.wait_for_url('**/research/programmes/uk-technology');page.screenshot(path=str(out/f'programme-{label}.png'),full_page=True)
  assert page.locator('body').evaluate('(e)=>e.scrollWidth')<=width
  page.locator('.rf-links' if label=='mobile' else 'svg').get_by_role('link',name='Data & AI',exact=True).click()
  assert 'coverage gap' in page.locator('#research-panel').inner_text().lower() or 'gap' in page.locator('#research-panel').inner_text().lower()
  page.get_by_role('link',name='Provider baseline',exact=True).click()
  assert 'ADVANIA UK (CCS) LIMITED' in page.locator('#research-panel').inner_text()
  page.screenshot(path=str(out/f'provider-{label}.png'),full_page=True)
  page.get_by_role('link',name='Evidence & assurance',exact=True).click()
  assert page.locator('#research-panel .rf-claim').count()==5
  assert page.locator('#research-panel a[href^="https://www.gca.gov.uk/"]').count()==6
  page.get_by_role('link',name='Gaps & next actions',exact=True).click()
  assert page.locator('#research-panel li').count()==16
  if label=='desktop':
   page.goto(args.base_url+'/industries');page.screenshot(path=str(out/'after-industries-desktop.png'),full_page=True)
   page.goto(args.base_url+'/research/programmes/uk-technology')
   page.locator('svg .rf-node').first.focus();page.keyboard.press('Enter');page.wait_for_url('**segment=software#research-panel')
   assert 'Software & applications' in page.locator('#panel-title').inner_text()
   page.goto(args.base_url+'/research/programmes/uk-technology?view=evidence');page.emulate_media(media='print');page.pdf(path=str(out/'evidence-print.pdf'),format='A4',print_background=True)
  checks.append({'viewport':label,'size':[width,height],'industry_navigation':True,'category_selection':True,'provider_baseline':True,'evidence_sources':5,'gap_actions':16,'horizontal_overflow':False,'javascript_errors':errors})
  assert not errors
  context.close()
 browser.close()
(out/'Browser-Validation.json').write_text(json.dumps({'browser':'Chromium / Playwright','synthetic_accounts':False,'live_web_research_in_browser':False,'checks':checks,'keyboard_category_link':True,'print_artifact':'Local A4 evidence PDF, inspected separately'},indent=2)+'\n')
print(json.dumps(checks))
