"""Public, localhost-only enterprise/opportunity browser and print checks.

Requires the optional development Playwright/Chromium installation. Does not
seed records, log in, or invoke mutation routes. Start isolated FLORA separately.
"""
from pathlib import Path
import argparse,json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',required=True)
parser.add_argument('--before-url')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
for url in [args.url]+([args.before_url] if args.before_url else []):
 target=urlsplit(url)
 if target.scheme not in {'http','https'} or target.hostname not in {'localhost','127.0.0.1'} or target.username or target.password or target.path not in {'','/'}:
  parser.error('Use a localhost application origin, without credentials or a path.')
out=args.output;out.mkdir(parents=True,exist_ok=True)
results={'viewports':[],'pdfs':[],'errors':[]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for stage,base in ([('before',args.before_url.rstrip('/'))] if args.before_url else [])+[('after',args.url.rstrip('/'))]:
  for name,w,h in [('desktop',1440,1080),('tablet',1024,768),('mobile',390,844)]:
   c=b.new_context(ignore_https_errors=True,viewport={'width':w,'height':h},has_touch=name!='desktop',reduced_motion='reduce')
   page=c.new_page();page.on('pageerror',lambda error:results['errors'].append(str(error)))
   paths=[('overlay','/enterprises/lloyds?lens=opportunities'),('ai','/flora/banking/research/candidates/RCO-LBG-002'),('legacy','/flora/banking/research/candidates/RCO-LBG-001'),('wallet','/flora/banking/research/candidates/RCO-LBG-009'),('enterprise','/enterprises/lloyds')]
   for label,path in paths:
    response=page.goto(base+path);assert response.status==200,(path,response.status)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(stage,name,label,'overflow')
    if label=='overlay':
     assert page.locator('.eo-node').count()>=8
     page.locator('.eo-node').first.click()
     if stage=='after':
      choice=page.locator('.eo-row[data-eo-choice]').first
      expected=choice.inner_text().rsplit('→',1)[0].strip()
      choice.click()
      assert page.locator('.eo-inspector article:visible').count()==1
      assert page.locator('.eo-inspector article:visible h3').inner_text()==expected
      # Return to capability view for matched screenshots.
      page.locator('.eo-node').first.click()
     page.locator('.eo-grid').scroll_into_view_if_needed()
    elif label in ('ai','legacy','wallet'):
     if stage=='after':
      assert page.locator('#full-research-evidence').get_attribute('open') is None
      assert page.locator('.eo-module').count()==8
      for button in page.locator('.eo-module').all():
       button.click();assert button.get_attribute('aria-pressed')=='true'
       assert page.locator('.eo-panel[data-eo-panel]:visible').count()==2 # story + one module
      page.locator('.eo-module').first.click()
      for button in page.locator('.eo-story-node').all():
       button.focus();page.keyboard.press('Enter');assert button.get_attribute('aria-pressed')=='true'
      page.locator('.eo-story-node').first.click()
     page.locator('.eo-story').scroll_into_view_if_needed()
    if stage=='after' or label in ('overlay','ai'):
     page.screenshot(path=str(out/f'{stage}-{label}-{name}.png'))
    results['viewports'].append({'stage':stage,'viewport':name,'page':label,'status':response.status,'overflow':False})
    if stage=='after' and name=='desktop' and label in ('ai','legacy','wallet'):
     original=page.locator('details').evaluate_all('(els)=>els.map(e=>e.open)')
     for mode in ('executive','appendix'):
      page.evaluate('(mode)=>document.documentElement.dataset.depthPrint=mode',mode)
      page.pdf(path=str(out/f'{label}-{mode}.pdf'),format='A4',print_background=True)
      page.wait_for_function('(states)=>JSON.stringify([...document.querySelectorAll("details")].map(e=>e.open))===JSON.stringify(states)',arg=original)
      assert page.locator('body>.depth-print-output').count()==0
      results['pdfs'].append(f'{label}-{mode}.pdf')
   c.close()
 # No-JS retains all canonical links and module content, without private reads.
 c=b.new_context(ignore_https_errors=True,java_script_enabled=False,viewport={'width':390,'height':844})
 page=c.new_page();page.goto(args.url.rstrip('/')+'/enterprises/lloyds?lens=opportunities')
 assert page.locator('a[href*="/candidates/RCO-LBG-"]').count()>=9
 page.goto(args.url.rstrip('/')+'/flora/banking/research/candidates/RCO-LBG-002')
 assert page.locator('#eo-module-owner').is_visible()
 page.locator('#full-research-evidence>summary').click();assert page.locator('#full-research-evidence').get_attribute('open') is not None
 c.close();b.close()
assert not results['errors'],results['errors']
(out/'browser-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
