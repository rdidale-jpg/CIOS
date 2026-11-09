"""Optional local browser walkthrough of the public research model (no seeding)."""
import argparse
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8780')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    target=urlsplit(args.url)
    if target.scheme!='http' or target.hostname not in {'localhost','127.0.0.1'}:
        parser.error('This walkthrough only targets a local public-source instance')
    args.output.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        base=args.url
        page.goto(base+'/flora/banking/explorer')
        page.get_by_role('link',name='Industry Twin research:',exact=False).click()
        page.get_by_role('heading',name='Banking.').wait_for()
        page.screenshot(path=str(args.output/'industry-pestle-desktop.png'),full_page=True)
        page.locator('svg a').filter(has=page.locator('text',has_text='Technological')).click()
        page.get_by_role('heading',name='Technological',exact=True).wait_for()
        page.get_by_role('link',name='Lloyds deep research',exact=True).click()
        page.get_by_role('heading',name='Lloyds.').wait_for()
        page.screenshot(path=str(args.output/'lloyds-deep-research.png'),full_page=True)
        page.get_by_role('link',name='Research priorities',exact=True).click()
        assert page.locator('.research-rank').count()==8
        page.locator('a[href$="/candidates/RCO-LBG-001"]').first.click()
        page.get_by_role('link',name='Inspect quotation, dates & provenance',exact=False).first.click()
        page.get_by_role('heading',name='Inspect the evidence boundary.',exact=True).wait_for()
        assert 'not a newly retrieved quotation' in page.locator('main').inner_text()
        for lens in ['pestle','porter','value-chain']:
            page.goto(base+'/flora/banking/research?lens='+lens)
            assert page.locator('h3').count()>=5
        for width,height in [(1440,1000),(1024,768),(768,1024),(390,844)]:
            page.set_viewport_size({'width':width,'height':height})
            for name,path in [('opportunities','/flora/banking/research/opportunities'),('lloyds','/flora/banking/research/lloyds'),('value-chain','/flora/banking/research?lens=value-chain')]:
                page.goto(base+path)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(name,width)
                if width==1024:page.screenshot(path=str(args.output/f'{name}-tablet.png'),full_page=True)
        page.goto(base+'/flora/banking/research/sources')
        assert 'Publication date: Unknown' in page.locator('main').inner_text()
        assert not errors,errors
        browser.close()
    print('PASS: Industry lenses → enterprise → ranked candidate → quotation/source provenance; desktop/tablet/mobile navigation and no overflow or JS errors. No sign-in, private records or demo seeding.')


if __name__=='__main__':main()
