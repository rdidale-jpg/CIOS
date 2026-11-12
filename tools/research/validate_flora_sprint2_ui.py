"""Read-only local screenshot validation; no accounts, seeding or deployment."""
import argparse,json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-url',required=True);p.add_argument('--baseline-url',required=True);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
for url in (a.base_url,a.baseline_url):
    u=urlsplit(url)
    if u.scheme!='https' or u.hostname not in ('localhost','127.0.0.1') or u.username or u.password:p.error('Isolated local HTTPS only')
a.output.mkdir(parents=True,exist_ok=True);route='/research/programmes/uk-technology';results=[]
with sync_playwright() as api:
    browser=api.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for name,w,h in [('desktop',1440,1050),('tablet',1024,1366),('mobile',390,844)]:
        ctx=browser.new_context(ignore_https_errors=True,viewport={'width':w,'height':h},is_mobile=name=='mobile',has_touch=name!='desktop')
        page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        if name=='desktop':
            page.goto(a.baseline_url+route);page.screenshot(path=str(a.output/'before-programme-desktop.jpg'),full_page=True,type='jpeg',quality=85)
        page.goto(a.base_url+route);page.get_by_role('link',name='Industry research',exact=True).click();page.wait_for_url('**view=research#research-panel')
        page.screenshot(path=str(a.output/f'research-{name}.jpg'),full_page=True,type='jpeg',quality=85)
        assert page.locator('body').evaluate('(n)=>n.scrollWidth')<=w
        if name=='mobile':page.locator('.s2-mobile').get_by_role('link',name='Oxford Ionics',exact=True).click()
        else:
            link=page.locator('.s2-map svg').get_by_role('link',name='Oxford Ionics',exact=True)
            if name=='desktop':link.focus();page.keyboard.press('Enter')
            else:link.click()
        assert 'Oxford Ionics' in page.locator('#research-detail').inner_text()
        assert 'not proof of completion' in page.locator('#research-detail').inner_text()
        page.screenshot(path=str(a.output/f'provider-{name}.jpg'),full_page=True,type='jpeg',quality=85)
        page.get_by_role('link',name='Banking & Aviation',exact=True).click()
        assert page.get_by_role('link',name='Explore existing enterprise opportunities').count()==2
        assert page.locator('#research-detail').inner_text().count('Buyer, budget, procurement and deployment: Unknown')==2
        if name=='desktop':page.screenshot(path=str(a.output/'journeys-desktop.jpg'),full_page=True,type='jpeg',quality=85)
        page.get_by_role('link',name='Evidence & assurance',exact=True).click()
        assert page.locator('.s2-source').count()==7
        assert page.locator('.s2-source a').count()==14
        assert 'General natural-language semantic verification is unavailable' in page.locator('#research-detail').inner_text()
        assert page.locator('body').evaluate('(n)=>n.scrollWidth')<=w and not errors
        results.append({'viewport':name,'width':w,'height':h,'programme_navigation':True,'provider_drill_down':True,'journeys':2,'source_drill_throughs':7,'no_overflow':True,'javascript_errors':errors})
        ctx.close()
    browser.close()
(a.output/'Browser-Results.json').write_text(json.dumps({'browser':'Chromium / Playwright','desktop_keyboard_svg_activation':True,'results':results,'limitation':'Automated functional/rendering validation; owner comprehension/usefulness not evaluated'},indent=2)+'\n')
print(json.dumps(results))
