#!/usr/bin/env python3
"""OA-1 owner assurance read-only review using isolated HTTPS example workspaces.

The worker explicitly seeds three illustrative seller portfolios. Browser GETs
must preserve private domain bytes; one deliberate private shortlist POST is allowed; Pipeline and mission bytes must remain intact.
No production data, Pipeline writes or external services are used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer


def worker(config_file):
    config=json.loads(Path(config_file).read_text())
    with tempfile.TemporaryDirectory(prefix='flora-library-example-') as scratch:
        root=Path(scratch)
        os.environ['FLORA_DATA_DIR']=str(root/'runtime')
        os.environ['FLORA_PUBLIC_ORIGIN']=f"https://127.0.0.1:{config['port']}"
        from cios.applications.flora.security_store import SecurityStore, canonical, digest, COOKIE
        from cios.applications.flora.security_web import CSRF_COOKIE
        from cios.applications.flora.security_operator import reconcile, plan, apply
        from cios.applications.flora.commercial_mission import save_employer_context, save_commercial_mission
        from cios.applications.flora import offers
        users=('preview-owner','preview-seller','preview-reviewer','preview-saas','preview-mssp','preview-strategic')
        snapshot=root/'snapshot';snapshot.mkdir()
        (snapshot/'synthetic.json').write_text(json.dumps([{'actor_id':u,'workspace_id':'preview-workspace'} for u in users]))
        evidence=reconcile(snapshot)
        manifest={'approved':True,'operator':'SYNTHETIC-preview-operator','approval_reference':'SYNTHETIC-fixture-only-approval',
            'snapshot_digest':digest(canonical(evidence)),'evidence':evidence['files'],
            'bindings':[{'user_id':u,'workspace_id':'preview-workspace','roles':['cios_owner'],'enterprise_ids':['BK-ENT-001','AV-ENT-001','BK-ENT-003','BK-ENT-005','BK-ENT-006','bt-group-plc']} for u in users]}
        store=SecurityStore();store.initialize_offline();proposed=plan(store,snapshot,manifest);apply(store,snapshot,proposed,proposed['digest'])
        with store.transaction() as db:
            db.execute('UPDATE memberships SET roles=?,version=version+1 WHERE user_id NOT IN (?,?)',(canonical(['commercial_context.view','commercial_context.edit']),'preview-owner','preview-strategic'))
        headers={}
        for user in users:
            delivery=root/user;store.enroll_offline(user,delivery);pre,csrf=store.preauth();store.enroll(delivery.read_text().strip(),config['password'],pre,csrf)
            pre,csrf=store.preauth();token,csrf=store.login(user,config['password'],pre,csrf);token,csrf=store.select(token,csrf,'preview-workspace')
            headers[user]={'Cookie':f'{COOKIE}={token}; {CSRF_COOKIE}={csrf}'}
        owner,seller,reviewer=(headers[u] for u in users[:3])
        save_employer_context(owner,{'organisation':'Example UK services company','capabilities':['Example diagnostics — illustration only']})
        binding=offers.bind_employer(list(users),['preview-reviewer'],'Example employer setup — preview only',headers=owner)
        for h in headers.values():offers.select_employer(binding['id'],headers=h)
        record=offers.save_offer(offers.TEMPLATES['service']|{'name':'Example offer — service diagnostic','evidence':'Example proof reference — illustration only; no actual corporate capability established'},headers=seller)
        record=offers.transition(record['id'],record['version'],'submit',headers=seller)
        record=offers.transition(record['id'],record['version'],'approve','Example independent review — preview only',headers=reviewer)
        private=offers.save_offer({'name':'Example private offer variation','entry_play':'Example private context — illustration only'},parent_id=record['id'],parent_version=record['version'],headers=seller)
        save_commercial_mission(seller,{'executive_role':'Client partner','commercial_objective':'Example service discovery — illustration only','priority_accounts':['Lloyds Banking Group'],'geography':['United Kingdom','France']})
        pilots = {}
        if hasattr(offers, 'adopt_library'):
            from cios.applications.flora import offer_library as library
            for key, organisation, categories, identifiers, h in [
                ('si','Example systems integrator',['consulting','engineering','cloud'],['tech-consulting-01','tech-engineering-01','tech-cloud-01'],seller),
                ('saas','Example software supplier',['software','data'],['tech-software-01','tech-software-02','tech-data-01'],headers['preview-saas']),
                ('mssp','Example managed security provider',['cyber','managed'],['tech-cyber-01','tech-cyber-02','tech-managed-01'],headers['preview-mssp'])]:
                offers.declare_employer(organisation,offers.resolve_employer_context(owner).version,headers=owner)
                employer=offers.bind_employer(['preview-owner','preview-reviewer',next(u for u,v in headers.items() if v==h)],['preview-reviewer'],'Example owner binding — preview only',headers=owner)
                offers.select_employer(employer['id'],headers=h)
                mission=offers.resolve_commercial_mission(h)
                mission=offers.configure_library(categories,employer['id'],employer['version'],mission.version if mission else 0,headers=h)
                refs=[{k:v for k,v in library.source_ref(library.template(i)).items() if k in {'id','version','digest'}} for i in identifiers]
                adopted=offers.adopt_library(refs,employer['id'],employer['version'],mission.version,True,headers=h)
                first=adopted[0]
                first=offers.save_offer({'evidence':'Example delivery and partner-rights review — illustration only'},first['id'],first['version'],headers=h)
                first=offers.transition(first['id'],first['version'],'submit',headers=h)
                offers.select_employer(employer['id'],headers=reviewer)
                first=offers.transition(first['id'],first['version'],'approve','Example separate reviewer — illustration only',headers=reviewer)
                pilots[key]={'user':next(u for u,v in headers.items() if v==h),'employer_id':employer['id'],'employer_version':employer['version'],'categories':categories,'offer_id':first['id'],'count':len(adopted)}
            offers.select_employer(pilots['si']['employer_id'],headers=owner)
            offers.select_employer(pilots['si']['employer_id'],headers=seller)
            mission=offers.resolve_commercial_mission(seller)
            offers.configure_library(pilots['si']['categories'],pilots['si']['employer_id'],pilots['si']['employer_version'],mission.version,headers=seller)
        strategic = None
        if hasattr(offers, 'adopt_library') and library.catalogue().get('strategic_priorities'):
            h=headers['preview-strategic']
            offers.declare_employer('Example enterprise transformation seller',offers.resolve_employer_context(owner).version,headers=owner)
            employer=offers.bind_employer(['preview-owner','preview-reviewer','preview-strategic'],['preview-reviewer'],'Example owner setup — illustration only',headers=owner)
            for person in (h,reviewer,owner):offers.select_employer(employer['id'],headers=person)
            mission=offers.configure_library(['consulting','data','cyber','engineering','advisory'],employer['id'],employer['version'],0,delivery_specialisms=['systems-integration'],headers=h)
            identifiers=library.catalogue()['strategic_priorities']
            refs=[{k:v for k,v in library.source_ref(library.template(i)).items() if k in {'id','version','digest'}} for i in identifiers]
            adopted=offers.adopt_library(refs,employer['id'],employer['version'],mission.version,True,headers=h)
            first=adopted[0]
            first=offers.save_offer({'evidence':'Example enterprise programme delivery and rights reference — fixture only'},first['id'],1,headers=h)
            first=offers.transition(first['id'],first['version'],'submit',headers=h)
            first=offers.transition(first['id'],first['version'],'approve','Example independent employer review — fixture only',headers=reviewer)
            strategic={'user':'preview-strategic','offers':dict(zip(identifiers,[r['id'] for r in adopted])),'count':len(adopted)}
            samples=[]
            for slug in offers.accounts():
                account=offers.discover('account',slug,headers=h)
                for identifier,record in zip(identifiers,adopted):
                    a=next(r for r in account if r['offer_id']==record['id'])
                    b=next(r for r in offers.discover('offer',record['id'],headers=h) if r['enterprise_slug']==slug)
                    assert a==b
                    samples.append({'library_id':identifier,'offer':library.template(identifier)['name'],'enterprise':a['enterprise_name'],'enterprise_slug':slug,'why_account':a['why_account'],'why_offer':a['why_offer'],'why_now':a['why_now'],'entry_play':a['entry_play'],'next_test':a['next_validation_action'],'posture':a['recommended_posture'],'economics':a['economics'],'value_case':a['economic_value_hypothesis'],'pipeline_eligible':a['pipeline_eligible'],'seller_status':a['credibility'],'source_claim_ids':[r['claim_id'] for r in a['evidence_lineage']],'matching_modes_identical':True,'classification':'Example seller hypothesis using existing reviewed account context; not customer demand'})
            Path(config['samples']).write_text(json.dumps({'source_cutoff':'2026-11-13','policy':offers.POLICY,'samples':samples},indent=2)+'\n')
        trigger_samples=[]
        if hasattr(offers,'TRIGGER_POLICY'):
            from cios.applications.flora.research_intelligence import buying_evidence as research
            h=headers['preview-strategic']
            # Each fixture Offer receives explicit example proof and separate review.
            for ident,oid in strategic['offers'].items():
                current=next(r for r in offers.snapshot(headers=h)['offers'] if r['id']==oid and r['current'])
                if current['state']!='employer_approved':
                    current=offers.save_offer({'evidence':'Example programme delivery and rights review — fixture only'},oid,current['version'],headers=h)
                    current=offers.transition(oid,current['version'],'submit',headers=h)
                    offers.transition(oid,current['version'],'approve','Example independent employer review — fixture only',headers=reviewer)
                a=offers.discover('offer',oid,intelligence=True,headers=h)
                for r in a:
                    same=next(x for x in offers.discover('account',r['enterprise_slug'],intelligence=True,headers=h) if x['offer_id']==oid)
                    assert r==same
                    trigger_samples.append({'offer_id':ident,'offer_name':library.template(ident)['name'],'enterprise':r['enterprise_name'],'enterprise_slug':r['enterprise_slug'],'tier':r['buying_trigger']['tier'],'stage':r['buying_trigger']['stage'],'why':r['why_account'],'entry_play':r['entry_play'],'entry_play_detail':r['buying_trigger'].get('entry_play_detail'),'deciding_question':r['next_validation_action'],'economic_value_hypothesis':r['economic_value_hypothesis'],'economics':r['economics'],'pipeline_eligible':r['pipeline_eligible'],'counter_evidence':r['contradictions'],'unknowns':r['buying_trigger']['unknowns'],'next_evidence_task':r['buying_trigger']['next_evidence_task'],'identity_scope':r['buying_trigger']['identity_scope'],'evidence':[{'id':f['id'],'source_id':f['source_id'],'url':f['source_url'],'published_on':f['publication_date'],'effective_date':f['effective_date'],'effective_period':f['effective_period'],'last_verified':f['last_verified'],'locator':f['locator'],'classification':f['candidate_claim']['status']} for f in r['buying_trigger']['timeline']],'both_modes_identical':True,'seller_approval':'Example fixture approval only; no real company capability asserted','qualification':'Unknown; research candidate only'})
            Path(config['samples']).write_text(json.dumps({'as_of':'2026-11-13','policy':offers.TRIGGER_POLICY,'samples':trigger_samples,'manual_practitioner_review':'Pending owner acceptance; no human sign-off fabricated'},indent=2)+'\n')
        development=None
        if '/flora/offers/development' in offers.READ_PATHS:
            from cios.applications.flora import seller_development as dev
            h=headers['preview-strategic'];development={}
            for key,ident,slug in [('digital','tech-strategic-digital-transformation','santander-uk'),('legacy','tech-strategic-complex-legacy-modernisation','santander-uk'),('ai','tech-strategic-ai-first-transformation','lloyds'),('cyber','tech-strategic-cybersecurity-resilience','computacenter'),('esg','tech-strategic-social-value-esg','lloyds')]:
                oid=strategic['offers'][ident]
                row=next(r for r in offers.snapshot(headers=h)['offers'] if r['id']==oid and r['current'])
                a=next(r for r in offers.discover('offer',oid,intelligence=True,headers=h) if r['enterprise_slug']==slug)
                selected=offers.snapshot(headers=h)['selected']
                review=offers.save_shortlist(oid,row['version'],selected['version'],'2026-11-13',research.DATA_SHA256,[a['assessment_id']],'Example fixture reviewed research; no customer demand inferred',confirmed=True,headers=h)
                candidate=dev.create(review['id'],review['version'],a['assessment_id'],True,headers=h)
                development[key]=candidate['id']
            Path(config['samples']).with_name('Development-Pilots.json').write_text(json.dumps({'classification':'Isolated example seller; customer-confirmed inputs used later are invented fixture evidence, not real customer claims','pilots':[{k:v for k,v in dev.records(identifier,headers=h).items() if k not in {'author','development_owner','workspace_id','employer_id'}} for identifier in development.values()]},indent=2)+'\n')
        if development:
            from cios.applications.flora import sales_pipeline as existing_pipeline
            candidate=dev.records(development['digital'],headers=h)
            values={'state':'Qualify','challenge':'Example fixture customer-reported journey ownership gap, not real demand',
                'proof':'Example separate delivery/rights review','alternatives':'Example incumbent plan reviewed',
                'next_action':'Example seller to review a permitted journey map with the programme function',
                'customer_attested':True,'reviewed':True,
                'qualification':{key:{'note':'Example fixture '+label+' evidence; not a real customer claim',
                    'source':'Private example meeting/reference '+key,'kind':'Seller review' if key in {'competition','differentiation'} else 'Customer statement','date':'2026-11-13'} for key,(label,_) in existing_pipeline.CRITERIA.items()}}
            candidate=dev.save(candidate['id'],candidate['version'],values,headers=h)
            dev.handoff(candidate['id'],candidate['version'],True,headers=h)
            if '/flora/command-centre' in offers.READ_PATHS:
                from cios.applications.flora import opportunity_assurance as qa
                samples=[]
                for name,identifier in development.items():
                    rec=dev.records(identifier,headers=h)
                    args={'offer_id':rec['offer_id'],'enterprise_slug':rec['enterprise_slug'],'candidate':identifier,'cutoff':'2026-11-13','headers':h}
                    actual=qa.inspect_pair(**args)
                    challenges={}
                    for challenge in qa.CHALLENGES:
                        selectors={}
                        if challenge=='Withdraw source':
                            timeline=actual['original']['buying_trigger']['timeline']
                            if not timeline:continue
                            selectors={'source':timeline[0]['source_id']}
                        if challenge in {'Close programme','Contradict programme'}:
                            selected=next((f for f in actual['original']['buying_trigger']['timeline'] if f.get('programme_id')),None)
                            if not selected:continue
                            selectors={'fact':selected['id']}
                        changed=qa.inspect_pair(**args,challenge=challenge,**selectors)
                        challenges[challenge]={'tier':changed['challenged']['buying_trigger']['tier'],'ready':changed['challenged_readiness']['ready'],'changed_dependencies':changed['changed_dependencies']}
                    samples.append({'pilot':name,'enterprise':rec['enterprise'],'offer':rec['offer_name'],'tier':actual['original']['buying_trigger']['tier'],
                        'trace':actual['original']['buying_trigger']['evaluation_trace'],'policy':actual['policy'],'criteria':actual['qualification'],
                        'gate_readiness':actual['original_readiness'],'handoff_checks':actual['original_handoff_checks'],'reproduced':actual['reproduced'],'handoff':actual['handoff'],'challenges':challenges})
                Path(config['samples']).with_name('Assurance-Pilots.json').write_text(json.dumps({'fixture_only':True,'samples':samples},indent=2)+'\n')
        from cios.applications.flora import sales_pipeline
        pipeline=sales_pipeline.create_opportunity('lloyds',values={'title':'Example independent pre-existing opportunity','problem':'Unvalidated fixture context'},headers=seller)
        before_offers=json.loads(offers._path().read_text())
        tracked=[Path(os.environ['FLORA_DATA_DIR'])/'sales_pipeline'/'opportunities.json', Path(os.environ['FLORA_DATA_DIR'])/'commercial_context'/'commercial_missions.json']
        hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
        from cios.applications.flora.web.app import FloraWebHandler
        class QuietHandler(FloraWebHandler):
            def log_message(self,*_):pass
        server=ThreadingHTTPServer(('127.0.0.1',config['port']),QuietHandler)
        cert,key=root/'local.crt',root/'local.key'
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=127.0.0.1'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);tls.load_cert_chain(cert,key);server.socket=tls.wrap_socket(server.socket,server_side=True)
        stop=threading.Event();signal.signal(signal.SIGTERM,lambda *_:stop.set())
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        Path(config['ready']).write_text(json.dumps({'strategic':strategic,'pilots':pilots,'offer_id':record['id'],'private_id':private['id'],'development':development}))
        stop.wait()
        server.shutdown();server.server_close();thread.join(2)
        if any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in hashes.items() if not development or 'sales_pipeline' not in p):raise AssertionError('Research walkthrough changed mission or independent Pipeline bytes')
        after_offers=json.loads(offers._path().read_text())
        assert before_offers==after_offers, 'Owner assurance changed private records'
        assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items()), 'Owner assurance changed Pipeline or mission bytes'
        Path(config['samples']).with_name('Read-Only-Integrity.json').write_text(json.dumps({'all_private_domain_bytes_unchanged':True,'pipeline_unchanged':True,'mission_unchanged':True,'fixture_only':True},indent=2)+'\n')



def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output');parser.add_argument('--baseline-root');parser.add_argument('--worker-config')
    args=parser.parse_args()
    if args.worker_config:return worker(args.worker_config)
    if not args.output or not args.baseline_root:parser.error('output and baseline-root required')
    output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='flora-library-compare-') as scratch:
        root=Path(scratch);processes=[];config={'output':str(output),'password':'Synthetic design phrase 47!','servers':{}}
        try:
            for name,port,repo in [('before',9061,Path(args.baseline_root).resolve()),('after',9060,Path(__file__).resolve().parents[2])]:
                ready=root/(name+'-ready.json');cfg=root/(name+'.json')
                cfg.write_text(json.dumps({'port':port,'password':config['password'],'ready':str(ready),'samples':str(output/'Assessment-Matrix.json')}));cfg.chmod(0o600)
                proc=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker-config',str(cfg)],cwd=repo,env=dict(os.environ,PYTHONPATH=str(repo)),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                processes.append(proc)
                for _ in range(1800):
                    if proc.poll() is not None:raise RuntimeError(name+' fixture server failed')
                    if ready.exists():break
                    time.sleep(.1)
                else:raise RuntimeError(name+' fixture server timed out')
                config['servers'][name]={'base':f'https://127.0.0.1:{port}',**json.loads(ready.read_text())}
            file=root/'browser.json';file.write_text(json.dumps(config));file.chmod(0o600)
            subprocess.run(['node',str(Path(__file__).with_suffix('.cjs')),str(file)],check=True)
        finally:
            for p in processes:
                if p.poll() is None:p.terminate()
            for p in processes:
                code=p.wait(timeout=15)
                if code:raise RuntimeError('Fixture domain-preservation check failed')
    print('Owner assurance walkthrough complete: all private domain and Pipeline bytes unchanged.')


if __name__=='__main__':main()
