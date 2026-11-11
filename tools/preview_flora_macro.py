"""Localhost-only macro journeys and screenshots; no seeding or mutation routes.

Optional development Playwright/Chromium required. Start isolated FLORA first.
Human comprehension and physical-device acceptance are not automated here.
"""
import argparse,json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();origin=urlsplit(args.url)
    if origin.scheme not in {'http','https'} or origin.hostname not in {'localhost','127.0.0.1'} or origin.path not in {'','/'} or origin.username or origin.password or origin.query or origin.fragment:
        parser.error('Use a credential-free localhost application origin only')
    base=args.url.rstrip('/');out=args.output;out.mkdir(parents=True,exist_ok=True)
    result={'pages':[],'journeys':[],'pdfs':[],'errors':[]}
    routes=[('atlas',''),('cyber-pestle','market=GB&view=industry'),('lloyds-context','market=GB&view=enterprise'),
        ('social-value','market=GB&category=sustainability&force=social-value'),
        ('easyjet-reporting','market=GB&industry=aviation&category=sustainability&force=uk-srs&view=enterprise'),
        ('france-reporting','market=FR&category=sustainability&force=eu-csrd&view=industry'),
        ('france-cyber','market=FR&industry=aviation&view=enterprise'),
        ('proposed-bill','market=GB&force=cyber-bill'),('coverage-gap','category=economy')]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for device,w,h in [('desktop',1440,1080),('tablet',1024,768),('mobile',390,844)]:
            context=browser.new_context(ignore_https_errors=True,viewport={'width':w,'height':h},has_touch=device!='desktop',reduced_motion='reduce')
            page=context.new_page();page.on('pageerror',lambda ex:result['errors'].append(str(ex)))
            for name,query in routes:
                response=page.goto(base+'/macro'+('?'+query if query else ''))
                assert response.status==200,(name,device,response.status)
                assert page.locator('#macro-inspector').count()==1
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(name,device)
                if name in ('lloyds-context','easyjet-reporting','france-cyber'):assert 'Unknown' in page.locator('#macro-inspector').inner_text()
                if name=='proposed-bill':assert 'Proposed legislation' in page.locator('#macro-inspector').inner_text()
                if name=='coverage-gap':assert 'Not researched yet' in page.locator('#macro-inspector').inner_text()
                page.screenshot(path=str(out/f'{name}-{device}.png'))
                if device!='desktop':
                    page.locator('.mi-stage').scroll_into_view_if_needed()
                    page.screenshot(path=str(out/f'{name}-{device}-visual.png'))
                result['pages'].append({'page':name,'viewport':device,'status':response.status,'overflow':False})
            # New seller: declare an offering, learn terminology, inspect a pressure,
            # then an existing hypothesis. Back retains the selection, not a CRM write.
            page.goto(base+'/macro?market=GB&mode=new&offering=ai-delivery')
            assert 'In plain language' in page.locator('#macro-inspector').inner_text()
            page.get_by_role('link',name='Trace industry impact →',exact=True).click();page.wait_for_url('**view=industry**')
            target=page.locator('.mi-portable a[href*="factor=Technological"]') if device!='mobile' else page.locator('.mi-mobile-nav a[href*="factor=Technological"]')
            target.focus();page.keyboard.press('Enter');page.wait_for_url('**factor=Technological**')
            assert 'Technological' in page.locator('#macro-inspector').inner_text()
            page.get_by_role('link',name='Inspect enterprise →',exact=True).click();page.wait_for_url('**view=enterprise**')
            assert 'Customer demand and territorial eligibility: Unverified' in page.locator('#macro-inspector').inner_text()
            prior=page.url
            page.locator('#macro-inspector a[href$="/RCO-LBG-005"]').click();page.wait_for_url('**/candidates/RCO-LBG-005')
            assert page.locator('h1').count()>=1
            page.go_back();page.wait_for_url(prior)
            assert page.locator('[name=offering]').input_value()=='ai-delivery'
            result['journeys'].append({'persona':'new seller','device':device,'result':'passed; relevance not customer demand'})
            # Expert: direct primary evidence, bypassing visual orientation.
            page.goto(base+'/macro?market=FR&category=sustainability&force=eu-csrd&mode=expert')
            page.get_by_role('link',name='Evidence first →',exact=True).click();page.wait_for_url('**/macro/evidence?**#macro-evidence')
            assert page.locator('#macro-evidence').bounding_box()['y']<h
            assert 'Ces nouveaux seuils' in page.locator('#macro-evidence').inner_text()
            assert page.locator('#macro-evidence a[href*="esma.europa.eu"]').count()==1
            result['journeys'].append({'persona':'experienced seller','device':device,'result':'passed; source/date/transposition inspected directly'})
            # Intermediate: compare the same selected policy across countries and
            # return through browser history without silently changing the force.
            page.goto(base+'/macro?market=GB&category=sustainability&force=social-value&mode=explore')
            page.locator('[name=market]').select_option('FR');page.get_by_role('button',name='Apply context →',exact=True).click()
            page.wait_for_url('**market=FR**')
            assert 'Outside the reviewed instrument territory' in page.locator('#macro-inspector').inner_text()
            assert page.locator('[name=force]').input_value()=='social-value'
            page.get_by_role('link',name='Trace industry impact →',exact=True).click();page.wait_for_url('**view=industry**')
            assert 'No reviewed impact mechanism' in page.locator('#macro-inspector').inner_text()
            page.go_back();page.wait_for_function('!new URL(location.href).searchParams.has("view") || new URL(location.href).searchParams.get("view")==="atlas"')
            result['journeys'].append({'persona':'intermediate seller','device':device,'result':'passed; country/force retained, no policy transfer'})
            if device=='desktop':
                for label,query in [('cyber','market=GB'),('social','market=GB&category=sustainability&force=social-value'),('france','market=FR&category=sustainability&force=eu-csrd')]:
                    for mode in ('executive','appendix'):
                        page.goto(base+('/macro/evidence?' if mode=='appendix' else '/macro?')+query)
                        page.evaluate('(mode)=>document.documentElement.dataset.macroPrint=mode',mode)
                        filename=f'{label}-{mode}.pdf';page.pdf(path=str(out/filename),format='A4',print_background=True)
                        page.wait_for_function('!document.documentElement.dataset.macroPrint')
                        result['pdfs'].append(filename)
            context.close()
        nojs=browser.new_context(ignore_https_errors=True,java_script_enabled=False,viewport={'width':390,'height':844})
        page=nojs.new_page();page.goto(base+'/macro?market=FR')
        page.locator('.mi-mobile-nav a[href*="category=sustainability"]').click()
        assert 'transposition' in page.locator('#macro-inspector').inner_text()
        page.get_by_role('link',name='Trace industry impact →',exact=True).click()
        assert page.locator('.mi-mobile-nav a[href*="factor=Legal"]').count()==1
        page.get_by_role('link',name='Primary evidence & full dossier →',exact=True).click()
        assert 'Ces nouveaux seuils' in page.locator('#macro-evidence').inner_text()
        result['no_javascript']='passed; country → theme → PESTLE → exact source'
        nojs.close();browser.close()
    assert not result['errors'],result['errors']
    (out/'browser-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
