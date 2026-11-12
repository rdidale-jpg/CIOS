"""Read-only localhost evidence-trace gallery; optional development Playwright only."""
import argparse, json, hashlib, subprocess
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright


def local(value):
    parsed=urlsplit(value)
    if parsed.scheme not in ('http','https') or parsed.hostname not in ('localhost','127.0.0.1') or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
        raise argparse.ArgumentTypeError('Credential-free localhost origin required')
    return value.rstrip('/')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True,type=local)
    parser.add_argument('--before-url',required=True,type=local)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    result={'pages':[],'journeys':[],'pdfs':[],'errors':[]}
    queries={'uk':'market=GB&view=enterprise&offering=ai-delivery',
             'france':'market=FR&category=sustainability&force=eu-csrd&view=enterprise'}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for device,w,h in [('desktop',1440,1080),('tablet',1024,768),('mobile',390,844)]:
            context=browser.new_context(ignore_https_errors=True,viewport={'width':w,'height':h},has_touch=device!='desktop',reduced_motion='reduce')
            page=context.new_page();page.on('pageerror',lambda error:result['errors'].append(str(error)))
            for name,query in queries.items():
                for revision,base in [('before',args.before_url),('after',args.url)]:
                    response=page.goto(base+'/macro?'+query);assert response.status==200
                    assert page.locator('#macro-inspector').count()==1
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                    page.screenshot(path=str(out/f'{name}-{revision}-{device}.png'))
                    page.locator('#macro-inspector').scroll_into_view_if_needed()
                    page.screenshot(path=str(out/f'{name}-{revision}-{device}-panel.png'))
                    result['pages'].append({'case':name,'revision':revision,'device':device,'status':200,'overflow':False})
                text=page.locator('#macro-inspector').inner_text()
                assert 'Unknown' in text and 'what next' in text.lower()
                assert ('00002065' in text if name=='uk' else 'Exact French legal entity' in text)
                original=page.url
                dossier=page.get_by_role('link',name='Decision & evidence dossier →',exact=True)
                dossier.focus();page.keyboard.press('Enter');page.wait_for_url('**#entity-trace')
                assert page.locator('#entity-trace').count()==1
                assert page.locator('#entity-trace a[href*="company/00002065"]').count()==(1 if name=='uk' else 0)
                assert 'Counter-tests' in page.locator('#entity-trace').inner_text()
                page.go_back();page.wait_for_url(original)
                result['journeys'].append({'case':name,'device':device,'keyboard_evidence_and_back':'passed'})
                if device=='desktop':
                    for mode in ('executive','appendix'):
                        page.goto(args.url+('/macro/evidence?' if mode=='appendix' else '/macro?')+query)
                        page.evaluate('(mode)=>document.documentElement.dataset.macroPrint=mode',mode)
                        path=out/f'{name}-{mode}.pdf';page.pdf(path=str(path),format='A4',print_background=True)
                        page.wait_for_function('!document.documentElement.dataset.macroPrint')
                        extracted=subprocess.check_output(['pdftotext',str(path),'-'],text=True)
                        normal=' '.join(extracted.split());assert 'Unknown' in normal
                        if mode=='appendix':
                            assert 'Counter-tests' in normal and 'Versioned edge manifest' in normal
                            assert ('LLOYDS BANK PLC' in normal if name=='uk' else "Toute société consolidante" in normal)
                        info=subprocess.check_output(['pdfinfo',str(path)],text=True)
                        pages=int(next(line.split(':')[1].strip() for line in info.splitlines() if line.startswith('Pages:')))
                        result['pdfs'].append({'file':path.name,'pages':pages,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'located_text_verified':True})
            context.close()
        context=browser.new_context(ignore_https_errors=True,java_script_enabled=False,viewport={'width':390,'height':844})
        page=context.new_page();page.goto(args.url+'/macro?'+queries['uk'])
        page.get_by_role('link',name='Decision & evidence dossier →',exact=True).click()
        assert '00002065' in page.locator('#entity-trace').inner_text()
        result['no_javascript']='passed: enterprise → exact-source dossier'
        context.close();browser.close()
    assert not result['errors']
    result['limitations']=['No physical Safari/iPad, screen-reader or human comprehension test performed.']
    (out/'browser-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
