"""Read-only completion-view checks; isolated localhost HTTPS, no identities/seeding."""
import argparse,json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-url',required=True);p.add_argument('--baseline-url',required=True);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
for url in (a.base_url,a.baseline_url):
    u=urlsplit(url)
    if u.scheme!='https' or u.hostname not in ('localhost','127.0.0.1') or u.username or u.password or u.query or u.fragment:p.error('Isolated localhost HTTPS only')
a.output.mkdir(parents=True,exist_ok=True);route='/research/programmes/uk-technology';results=[]
with sync_playwright() as api:
    browser=api.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for name,w,h in [('desktop',1440,1050),('tablet',1024,1366),('mobile',390,844)]:
        ctx=browser.new_context(ignore_https_errors=True,viewport={'width':w,'height':h},is_mobile=name=='mobile',has_touch=name!='desktop');page=ctx.new_page();errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
        for view in ('research','briefings&provider=microsoft','assurance'):
            label=view.split('&')[0]
            if name=='desktop':
                page.goto(a.baseline_url+route+'?view='+view+'#research-detail');page.screenshot(path=str(a.output/f'before-{label}-desktop.jpg'),full_page=False,type='jpeg',quality=80)
            page.goto(a.base_url+route+'?view='+view+'#research-detail');text=page.locator('#research-detail').inner_text()
            assert 'key_present' not in text and 'FLORA_REASONING_API_KEY' not in text
            if label=='research':
                control=page.get_by_text('Inspect legal identities and remaining scope gaps',exact=True);control.focus();page.keyboard.press('Enter');assert page.get_by_role('link',name='ADVANIA UK (CCS) LIMITED / 04418144').count()==1
                assert page.get_by_role('link',name='ADVANIA UK LIMITED / 03645998').count()==1
                page.keyboard.press('Enter')
            elif label=='briefings':assert 'material influence from de facto control' in text
            else:
                assert 'False acceptance 0/19' in text and 'All not executed' in text
                assert page.locator('.s2-source').count()==7 and page.locator('.s2-completion-source').count()==1
                assert page.get_by_role('link',name='CMA summary').get_attribute('href').endswith('1._MS.OAI_-_Summary.pdf')
            assert page.locator('body').evaluate('(n)=>n.scrollWidth')<=w
            page.locator('#research-detail').evaluate("n=>n.scrollIntoView({block:'start'})")
            page.screenshot(path=str(a.output/f'{label}-{name}.jpg'),full_page=False,type='jpeg',quality=80)
        page.get_by_role('link',name='Banking & Aviation',exact=True).click();assert page.get_by_role('link',name='Explore existing enterprise opportunities').count()==2
        assert page.locator('#research-detail').inner_text().count('Buyer, budget, procurement and deployment: Unknown')==2
        page.emulate_media(media='print');assert 'No verified Microsoft deployment' in page.locator('#research-detail').inner_text()
        assert not errors
        results.append({'viewport':name,'width':w,'height':h,'changed_views':3,'legal_identity_keyboard_disclosure':True,'historical_and_new_source_cards':8,'public_runtime_secrets_exposed':False,'enterprise_journeys':2,'print_unknowns_preserved':True,'no_horizontal_overflow':True,'javascript_errors':errors});ctx.close()
    browser.close()
(a.output/'Browser-Results.json').write_text(json.dumps({'browser':'Chromium / Playwright','results':results,'limits':'Functional/render checks only; no owner usefulness assessment or live semantic verification. Screenshots only for changed research, Microsoft briefing and assurance views.'},indent=2)+'\n')
print(json.dumps(results))
