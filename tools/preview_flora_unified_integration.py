"""Actual localhost-only unified journeys, viewports and exports.

Optional Playwright/Chromium. Deliberate capture requires an explicit flag and
local test-access file; never invoke against a remote or production origin.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright


def local(value):
    p=urlsplit(value)
    if p.scheme!='https' or p.hostname not in ('localhost','127.0.0.1') or p.username or p.password or p.query or p.fragment or p.path not in ('','/'):
        raise argparse.ArgumentTypeError('Credential-free HTTPS localhost origin required')
    return value.rstrip('/')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--url',required=True,type=local);ap.add_argument('--before-url',type=local)
    ap.add_argument('--output',required=True,type=Path);ap.add_argument('--test-access-file',type=Path)
    ap.add_argument('--permit-local-capture',action='store_true');args=ap.parse_args()
    if args.permit_local_capture and not args.test_access_file:ap.error('Local capture needs isolated test access')
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    result={'pages':[],'personas':[],'pdfs':[],'errors':[],'pipeline':[]}
    cases=[('global','/macro'),('macro','/macro?market=GB&view=enterprise&offering=cyber'),
           ('banking','/industries/banking'),('enterprise','/enterprises/lloyds'),
           ('overlay','/enterprises/lloyds?lens=opportunities'),
           ('ai','/flora/banking/research/candidates/RCO-LBG-002'),
           ('cyber','/flora/banking/research/candidates/RCO-LBG-005'),
           ('cockpit','/flora/banking/research/candidates/RCO-LBG-005')]
    def overflow(page):assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    def activate(locator,device):
        if device=='desktop':locator.focus();locator.press('Enter')
        else:locator.tap()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for device,w,h in [('desktop',1440,1080),('tablet',1024,768),('mobile',390,844)]:
            context=browser.new_context(ignore_https_errors=True,viewport={'width':w,'height':h},has_touch=device!='desktop',reduced_motion='reduce')
            page=context.new_page();page.on('pageerror',lambda err:result['errors'].append(str(err)))
            for label,path in cases:
                if args.before_url and label in ('macro','enterprise','ai'):
                    r=page.goto(args.before_url+path);assert r.status==200
                    page.screenshot(path=str(out/f'before-{label}-{device}-first.png'))
                    result['pages'].append({'revision':'before #566','view':label,'device':device,'state':'first viewport','status':200})
                r=page.goto(args.url+path);assert r.status==200,(label,device,r.status)
                overflow(page);page.screenshot(path=str(out/f'{label}-{device}-first.png'))
                if label=='global':
                    target=page.locator('.mi-mobile-nav a[href*="category=sustainability"]') if device=='mobile' else page.locator('.mi-atlas a[href*="category=sustainability"]')
                    activate(target,device);page.wait_for_url('**category=sustainability**')
                    page.locator('#macro-inspector').scroll_into_view_if_needed();assert page.locator('#macro-inspector').count()==1
                elif label=='macro':
                    page.locator('#macro-inspector').scroll_into_view_if_needed()
                    assert 'Formal applicability: Unknown' in page.locator('#macro-inspector').inner_text()
                    assert '00002065' in page.locator('#macro-inspector').inner_text()
                elif label=='banking':
                    page.locator('.lm[data-ready=true]').wait_for()
                    if not page.locator('[data-lm-target]:visible').count():
                        equivalent=page.locator('.lm-keyboard>summary')
                        if not equivalent.evaluate('(e)=>e.parentElement.open'):activate(equivalent,device)
                    target=page.locator('[data-lm-target]:visible').first
                    if device=='tablet' and target.get_attribute('class')=='lm-flow-link':target=target.locator('text').first
                    activate(target,device)
                    page.locator('.lm-inspector').scroll_into_view_if_needed()
                    assert page.locator('.lm-panel:visible').count()==1
                elif label=='enterprise':
                    target=page.locator('[data-vi-pick]:visible').first
                    destination=target.get_attribute('data-vi-pick');activate(target,device)
                    page.locator('#'+destination).scroll_into_view_if_needed()
                    assert page.locator('#'+destination).get_attribute('open') is not None
                elif label=='overlay':
                    activate(page.locator('.eo-node').first,device)
                    activate(page.locator('.eo-row[data-eo-choice]:visible').first,device)
                    assert page.locator('.eo-inspector article:visible').count()==1
                    page.locator('.eo-inspector article:visible').scroll_into_view_if_needed()
                else:
                    assert page.locator('.eo-module').count()==8
                    if label=='cockpit':
                        activate(page.locator('.eo-module[data-eo-choice="competition"]'),device)
                        page.locator('#eo-module-competition').scroll_into_view_if_needed()
                        assert 'no active competitive procurement' in page.locator('#eo-module-competition').inner_text().lower()
                    else:
                        activate(page.locator('.eo-story-node').nth(3),device)
                        page.locator('#eo-story-3').scroll_into_view_if_needed()
                        assert 'Unknown' in page.locator('#eo-story-3').inner_text()
                    assert page.locator('#full-research-evidence').get_attribute('open') is None
                overflow(page);page.screenshot(path=str(out/f'{label}-{device}-selected.png'))
                result['pages'].append({'revision':'integrated','view':label,'device':device,'states':['first viewport','selected inspector'],'status':200,'overflow':False})

            # A: follow source-owned macro context through both existing enterprise views.
            page.goto(args.url+'/macro?market=GB&mode=new&offering=cyber')
            activate(page.get_by_role('link',name='Trace industry impact →',exact=True),device);page.wait_for_url('**view=industry**')
            target=page.locator('.mi-mobile-nav a[href*="factor=Legal"]') if device=='mobile' else page.locator('.mi-portable a[href*="factor=Legal"]')
            activate(target,device);page.wait_for_url('**factor=Legal**')
            activate(page.get_by_role('link',name='Inspect enterprise →',exact=True),device);page.wait_for_url('**view=enterprise**')
            macro_return=page.url
            activate(page.get_by_role('link',name='Explore existing Enterprise Twin →',exact=True),device);page.wait_for_url('**/enterprises/lloyds')
            activate(page.locator('.ux-tabs a[href$="lens=opportunities"]'),device);page.wait_for_url('**lens=opportunities')
            activate(page.locator('.eo-node').filter(has_text='Risk, conduct').first,device)
            activate(page.locator('[data-eo-choice="candidate-RCO-LBG-005"]:visible').first,device)
            activate(page.locator('.eo-inspector article:visible .eo-action'),device);page.wait_for_url('**/candidates/RCO-LBG-005')
            assert page.locator('.eo-module').count()==8
            for button in page.locator('.eo-module').all():
                activate(button,device);assert button.get_attribute('aria-pressed')=='true'
            page.go_back();page.wait_for_url('**lens=opportunities');page.go_back();page.wait_for_url('**/enterprises/lloyds');page.go_back();page.wait_for_url(macro_return)
            assert page.locator('[name=offering]').input_value()=='cyber'
            result['personas'].append({'persona':'A / new industry seller','device':device,'result':'Macro → PESTLE → scoped entity → existing Enterprise Twin → capability → original cyber hypothesis → eight modules; Back restores offering/context'})

            # B: deep entry, exact canonical source and original full dossier.
            page.goto(args.url+'/enterprises/lloyds')
            target=page.locator('[data-vi-pick]:visible').first;activate(target,device)
            activate(page.locator('.ux-tabs a[href$="lens=opportunities"]'),device);page.wait_for_url('**lens=opportunities')
            activate(page.locator('.eo-node').first,device)
            activate(page.locator('[data-eo-choice="candidate-RCO-LBG-002"]:visible').first,device)
            activate(page.locator('.eo-inspector article:visible .eo-action'),device);page.wait_for_url('**RCO-LBG-002')
            exact=page.locator('.eo-story a').filter(has_text='Exact passage').first
            assert exact.count()==1
            activate(exact,device);page.wait_for_url('**/evidence/**')
            assert 'Locator' in page.locator('body').inner_text() or 'locator' in page.locator('body').inner_text()
            page.go_back();page.wait_for_url('**RCO-LBG-002')
            activate(page.locator('#full-research-evidence>summary'),device)
            assert page.locator('#full-research-evidence').get_attribute('open') is not None
            result['personas'].append({'persona':'B / industry expert','device':device,'result':'Direct enterprise → capability → AI hypothesis → exact source → complete dossier; no mandatory Macro introduction'})

            # C: same force/industry/offering survives geographic comparison and detail.
            page.goto(args.url+'/macro?market=GB&category=sustainability&force=eu-csrd&view=industry&offering=reporting')
            assert 'Outside reviewed country coverage' in page.locator('#macro-inspector').inner_text()
            page.locator('[name=market]').select_option('FR');activate(page.get_by_role('button',name='Apply context →',exact=True),device);page.wait_for_url('**market=FR**')
            assert page.locator('[name=force]').input_value()=='eu-csrd'
            activate(page.get_by_role('link',name='Inspect enterprise →',exact=True),device);page.wait_for_url('**view=enterprise**')
            assert 'Exact French legal entity' in page.locator('#macro-inspector').inner_text()
            current=page.url
            activate(page.get_by_role('link',name='Decision & evidence dossier →',exact=True),device);page.wait_for_url('**#entity-trace')
            assert page.locator('#entity-trace a[href*="legifrance.gouv.fr"]').count()==1
            page.go_back();page.wait_for_url(current)
            assert page.locator('[name=offering]').input_value()=='reporting'
            result['personas'].append({'persona':'C / intermediate seller','device':device,'result':'UK/France same-force comparison → scoped PESTLE → unresolved entity → national source → Back; no false legal exemption or French opportunity'})

            # Other sector and existing framework routes stay usable.
            for path in ('/industries/aviation','/enterprises/easyjet','/industries/banking?lens=porter','/industries/banking?lens=value-chain'):
                assert page.goto(args.url+path).status==200;overflow(page)
            context.close()

        # Exports use the same current integrated app and original print owners.
        ctx=browser.new_context(ignore_https_errors=True,viewport={'width':1440,'height':1080});page=ctx.new_page()
        exports=[('macro','/macro?market=GB&view=enterprise','macroPrint'),
                 ('france','/macro?market=FR&category=sustainability&force=eu-csrd&view=enterprise','macroPrint'),
                 ('ai','/flora/banking/research/candidates/RCO-LBG-002','depthPrint'),
                 ('cyber','/flora/banking/research/candidates/RCO-LBG-005','depthPrint'),
                 ('banking','/industries/banking','depthPrint'),('enterprise','/enterprises/lloyds','depthPrint')]
        for label,path,owner in exports:
            for mode in ('executive','appendix'):
                actual=path.replace('/macro?','/macro/evidence?') if owner=='macroPrint' and mode=='appendix' else path
                page.goto(args.url+actual)
                before=page.locator('details').evaluate_all('(els)=>els.map(e=>e.open)')
                page.evaluate('([owner,mode])=>document.documentElement.dataset[owner]=mode',[owner,mode])
                target=out/f'{label}-{mode}.pdf';page.pdf(path=str(target),format='A4',print_background=True)
                page.wait_for_function('(s)=>JSON.stringify([...document.querySelectorAll("details")].map(e=>e.open))===JSON.stringify(s)',arg=before)
                assert page.locator('body>.depth-print-output').count()==0
                text=' '.join(subprocess.check_output(['pdftotext',str(target),'-'],text=True).split())
                assert 'Unknown' in text or 'unverified' in text.lower(),(label,mode)
                if label=='macro':assert 'ss121-march-22.pdf' in text
                if label=='france':assert 'legifrance.gouv.fr' in text
                if label in ('ai','cyber'):assert 'https://' in text
                info=subprocess.check_output(['pdfinfo',str(target)],text=True)
                count=int(next(line.split(':')[1] for line in info.splitlines() if line.startswith('Pages:')))
                result['pdfs'].append({'file':target.name,'pages':count,'sha256':sha(target),'text_and_restoration':'passed'})
        ctx.close()

        # No-JS research and development remain reachable through native controls.
        ctx=browser.new_context(ignore_https_errors=True,java_script_enabled=False,viewport={'width':390,'height':844});page=ctx.new_page()
        page.goto(args.url+'/macro?market=GB&view=enterprise')
        page.get_by_role('link',name='Explore existing Enterprise Twin →',exact=True).click()
        page.locator('.ux-tabs a[href$="lens=opportunities"]').click()
        page.locator('.eo-fallback>summary').click()
        page.locator('.eo-comparison a[href$="RCO-LBG-005"]').click()
        assert page.locator('#eo-module-owner').is_visible()
        page.locator('#full-research-evidence>summary').click();assert page.locator('#full-research-evidence').get_attribute('open') is not None
        result['no_javascript']='passed: Macro → Enterprise → accessible opportunity comparison → cyber cockpit → full evidence';ctx.close()

        (out/'public-browser-results.json').write_text(json.dumps(result,indent=2)+'\n')
        if args.permit_local_capture:
            access=json.loads(args.test_access_file.read_text())
            store=Path(access['data_root'])/'sales_pipeline/opportunities.json'
            for device,w,h in [('desktop',1440,1080),('tablet',1024,768),('mobile',390,844)]:
                ctx=browser.new_context(ignore_https_errors=True,viewport={'width':w,'height':h},has_touch=device!='desktop',reduced_motion='reduce')
                ctx.add_cookies([{'name':key,'value':value,'url':args.url,'secure':True,'sameSite':'Strict'} for key,value in access['cookies'].items()])
                page=ctx.new_page();page.goto(args.url+'/flora/banking/research/candidates/RCO-LBG-005')
                before=sha(store)
                # CSRF is supplied by the real server-rendered form, never injected.
                form=page.locator('#commercial-capture form');assert form.locator('[name=csrf]').count()==1
                activate(form.locator('button'),device);page.wait_for_url('**/opp-*#qualification')
                data=json.loads(store.read_text());assert len(data['records'])==1
                record=next(iter(data['records'].values()));frozen=deepcopy(record);captured=sha(store)
                assert record['origin_id']=='RCO-LBG-005' and record['stage']=='Discovered'
                record_url=page.url;page.goto(record_url.split('#')[0]);overflow(page)
                qualification_count=page.locator('[name^=q_]').count();assert qualification_count==10
                page.screenshot(path=str(out/f'pipeline-{device}-first.png'))
                page.locator('#qualification').scroll_into_view_if_needed();page.screenshot(path=str(out/f'pipeline-{device}-selected.png'))
                page.locator('[name=stage]').select_option('Qualified');page.locator('[name=confirm]').check()
                with page.expect_navigation(wait_until='load') as rejected:
                    activate(page.get_by_role('button',name='Save opportunity & activity',exact=True),device)
                assert rejected.value.status==422
                assert page.locator('.sales-error').inner_text().strip()
                assert sha(store)==captured and json.loads(store.read_text())['records'][record['id']]==frozen
                page.goto(args.url+'/flora/banking/research/candidates/RCO-LBG-005')
                activate(page.locator('#commercial-capture form button'),device);page.wait_for_url('**/opp-*#qualification')
                assert sha(store)==captured and len(json.loads(store.read_text())['records'])==1
                assert json.loads(store.read_text())['records'][record['id']]['provenance']==frozen['provenance']
                page.goto(args.url+'/flora/sales/pipeline');overflow(page)
                page.screenshot(path=str(out/f'pipeline-{device}-list.png'))
                result['pipeline'].append({'device':device,'stage':'Discovered','customer_qualified':False,'rejected_qualification_status':rejected.value.status,'before':before,'after_capture':captured,'after_rejection_and_duplicate':sha(store),'unchanged_after_rejection_and_duplicate':True,'qualification_inputs':qualification_count,'provenance_unchanged':True,'synthetic_test_workspace_only':True})
                ctx.close()
        browser.close()
    assert not result['errors'],result['errors']
    result['unperformed']=['Physical iPad/Safari','Screen-reader evaluation','Human comprehension and owner acceptance']
    (out/'browser-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pages':len(result['pages']),'personas':len(result['personas']),'pdfs':result['pdfs'],'pipeline':result['pipeline'],'errors':result['errors']},indent=2))


if __name__=='__main__':main()
