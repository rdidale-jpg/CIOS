"""Exercise only the disposable demo created by demo_flora_sales.py.

Requires development-only Playwright/Chromium. Edits synthetic demo records.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit, urlencode

from playwright.sync_api import sync_playwright

CRITERIA=('problem','priority','buyer','funding','decision','competition','differentiation','timing','relationship','next_action')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--access-file',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--chromium',default='/usr/bin/chromium')
    args=parser.parse_args()
    access=json.loads(args.access_file.read_text())
    parsed=urlsplit(access['url'])
    if (parsed.scheme!='https' or parsed.hostname!='localhost'
            or access.get('user')!='demo-sales-owner' or access.get('workspace')!='demo-sales-workspace'
            or not Path(access['root']).name.startswith('flora-sales-demo-')):
        parser.error('Only an explicitly disposable localhost sales demo is supported.')
    base=f'https://localhost:{parsed.port}'
    args.output.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox'])
        context=browser.new_context(ignore_https_errors=True,viewport={'width':1440,'height':1000})
        page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(base+'/auth/sign-in')
        page.locator('[name=user_id]').fill(access['user']);page.locator('[name=password]').fill(access['password'])
        page.get_by_role('button',name='Sign in',exact=True).click()
        page.locator('[name=workspace_id]').select_option(access['workspace'])
        page.get_by_role('button',name='Select workspace',exact=True).click()
        page.goto(base+'/flora/banking/explorer')
        page.get_by_role('link',name='Lloyds Banking Group',exact=False).first.click()
        page.get_by_role('link',name='Opportunity landscape',exact=True).click()
        assert 'Lloyds Banking Group' in page.locator('h1').inner_text()
        page.screenshot(path=str(args.output/'lloyds-opportunity-landscape.png'),full_page=True)
        page.locator('a.ex-bank').first.click()
        page.get_by_role('button',name='Add to pipeline & qualify',exact=False).click()
        page.get_by_role('heading',name='What supports qualification?',exact=True).wait_for()
        record_url=page.url.split('#')[0]
        for key in CRITERIA:
            detail=page.locator('details.sales-criterion').filter(has=page.locator('#q_'+key))
            if detail.get_attribute('open') is None:detail.locator('summary').click()
            if key!='funding':
                page.locator('#q_'+key).fill('DEMONSTRATION ONLY: customer evidence exercise for '+key)
                page.locator('#s_'+key).fill('SYNTHETIC-CAPTURE-001 / '+key)
        page.locator('[name=evidence_reviewed]').check()
        page.locator('[name=stage]').select_option('Qualified');page.locator('[name=confirm]').check()
        page.get_by_role('button',name='Save opportunity & activity',exact=True).click()
        assert 'all ten supported qualification inputs' in page.get_by_role('alert').inner_text()
        assert page.locator('#q_problem').input_value().startswith('DEMONSTRATION ONLY')
        funding=page.locator('details.sales-criterion').filter(has=page.locator('#q_funding'))
        if funding.get_attribute('open') is None:funding.locator('summary').click()
        page.locator('#q_funding').fill('DEMO funding criterion; not a real customer budget.')
        page.locator('#s_funding').fill('SYNTHETIC-CAPTURE-001 / funding')
        page.locator('[name=confirm]').check();page.locator('[name=evidence_reviewed]').check()
        page.get_by_role('button',name='Save opportunity & activity',exact=True).click()
        assert 'qualified / demonstration opportunity' in page.locator('.ex-hero').inner_text().lower()
        page.locator('[name=stage]').select_option('Pursuit')
        page.get_by_role('button',name='Save opportunity & activity',exact=True).click()
        assert 'Explicit user confirmation' in page.get_by_role('alert').inner_text()
        page.locator('[name=confirm]').check()
        page.locator('#activity').fill('DEMO capture planning conversation recorded by the browser walkthrough.')
        page.locator('#next_action').fill('DEMO: validate sponsor and mutual next step in a customer conversation.')
        page.get_by_role('button',name='Save opportunity & activity',exact=True).click()
        assert 'pursuit / demonstration opportunity' in page.locator('.ex-hero').inner_text().lower()
        page.screenshot(path=str(args.output/'qualification-workspace.png'),full_page=True)
        page.goto(base+'/flora/sales/pipeline?'+urlencode({'enterprise':'Lloyds Banking Group','view':'board'}))
        assert 'Active pursuit' in page.locator('main').inner_text()
        page.goto(base+'/flora/sales/new?enterprise=barclays')
        page.locator('#title').fill('DEMO manual service discovery')
        page.locator('#problem').fill('Demonstration hypothesis only; customer requirement remains unconfirmed.')
        page.locator('#next_action').fill('Review source material and seek validation.')
        page.get_by_role('button',name='Create & qualify',exact=False).click()
        assert 'discovered / demonstration opportunity' in page.locator('.ex-hero').inner_text().lower()
        pages=[('pipeline','/flora/sales/pipeline?view=board'),('barclays-landscape','/flora/banking/explorer/barclays/opportunities'),('qualification',urlsplit(record_url).path)]
        for width,height in [(1440,1000),(1024,768),(768,1024)]:
            page.set_viewport_size({'width':width,'height':height})
            for name,path in pages:
                page.goto(base+path)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(name,width)
                if width==1024:
                    page.screenshot(path=str(args.output/f'{name}-ipad.png'),full_page=True)
        page.goto(base+'/flora/banking/explorer/barclays/opportunities?theme=technology')
        assert page.locator('a.ex-bank').count()>=1
        assert not errors,errors
        browser.close()
    print('PASS: real sign-in, enterprise discovery, capture, recovered validation draft, explicit qualification/pursuit, activity/history, manual creation, board/filter views, desktop/iPad layouts; no JS errors.')


if __name__=='__main__':main()
