#!/usr/bin/env python3
"""Before/after design review with two isolated synthetic HTTPS workspaces.

The helper intentionally seeds a local demonstration Pipeline record. Browsing
must preserve domain bytes; no production endpoint or credential is used.
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
    with tempfile.TemporaryDirectory(prefix='flora-design-synthetic-') as scratch:
        root=Path(scratch)
        os.environ['FLORA_DATA_DIR']=str(root/'runtime')
        os.environ['FLORA_PUBLIC_ORIGIN']=f"https://127.0.0.1:{config['port']}"
        from cios.applications.flora.security_store import SecurityStore, canonical, digest, COOKIE
        from cios.applications.flora.security_web import CSRF_COOKIE
        from cios.applications.flora.security_operator import reconcile, plan, apply
        from cios.applications.flora.commercial_mission import save_employer_context, save_commercial_mission
        from cios.applications.flora import offers, sales_pipeline
        users=('preview-owner','preview-seller','preview-reviewer')
        snapshot=root/'snapshot';snapshot.mkdir()
        (snapshot/'synthetic.json').write_text(json.dumps([{'actor_id':u,'workspace_id':'preview-workspace'} for u in users]))
        evidence=reconcile(snapshot)
        manifest={'approved':True,'operator':'SYNTHETIC-preview-operator','approval_reference':'SYNTHETIC-fixture-only-approval',
            'snapshot_digest':digest(canonical(evidence)),'evidence':evidence['files'],
            'bindings':[{'user_id':u,'workspace_id':'preview-workspace','roles':['cios_owner'],'enterprise_ids':['BK-ENT-001','AV-ENT-001']} for u in users]}
        store=SecurityStore();store.initialize_offline();proposed=plan(store,snapshot,manifest);apply(store,snapshot,proposed,proposed['digest'])
        with store.transaction() as db:
            db.execute('UPDATE memberships SET roles=?,version=version+1 WHERE user_id IN (?,?)',(canonical(['commercial_context.view','commercial_context.edit']),'preview-seller','preview-reviewer'))
        headers={}
        for user in users:
            delivery=root/user;store.enroll_offline(user,delivery);pre,csrf=store.preauth();store.enroll(delivery.read_text().strip(),config['password'],pre,csrf)
            pre,csrf=store.preauth();token,csrf=store.login(user,config['password'],pre,csrf);token,csrf=store.select(token,csrf,'preview-workspace')
            headers[user]={'Cookie':f'{COOKIE}={token}; {CSRF_COOKIE}={csrf}'}
        owner,seller,reviewer=(headers[u] for u in users)
        save_employer_context(owner,{'organisation':'Example UK services company','capabilities':['Example diagnostics — illustration only']})
        binding=offers.bind_employer(list(users),['preview-reviewer'],'Example employer setup — preview only',headers=owner)
        for h in headers.values():offers.select_employer(binding['id'],headers=h)
        record=offers.save_offer(offers.TEMPLATES['service']|{'name':'Example offer — service diagnostic','evidence':'Example proof reference — illustration only; no actual corporate capability established'},headers=seller)
        record=offers.transition(record['id'],record['version'],'submit',headers=seller)
        record=offers.transition(record['id'],record['version'],'approve','Example independent review — preview only',headers=reviewer)
        private=offers.save_offer({'name':'Example private offer variation','entry_play':'Example private context — illustration only'},parent_id=record['id'],parent_version=record['version'],headers=seller)
        save_commercial_mission(seller,{'executive_role':'Client partner','commercial_objective':'Example service discovery — illustration only','priority_accounts':['Lloyds Banking Group'],'geography':['United Kingdom','France']})
        pipeline=sales_pipeline.create_opportunity('lloyds',values={'title':'Example opportunity — service discovery','problem':'Example unvalidated service scenario','next_action':'Validate the opportunity with the customer'},headers=seller)
        tracked=[offers._path(), Path(os.environ['FLORA_DATA_DIR'])/'sales_pipeline'/'opportunities.json']
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
        Path(config['ready']).write_text(json.dumps({'pipeline_id':pipeline['id'],'offer_id':record['id'],'private_id':private['id']}))
        stop.wait()
        server.shutdown();server.server_close();thread.join(2)
        if any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise AssertionError('GET walkthrough changed commercial domain state')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output');parser.add_argument('--baseline-root');parser.add_argument('--worker-config')
    args=parser.parse_args()
    if args.worker_config:return worker(args.worker_config)
    if not args.output or not args.baseline_root:parser.error('output and baseline-root required')
    output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='flora-design-compare-') as scratch:
        root=Path(scratch);processes=[];config={'output':str(output),'password':'Synthetic design phrase 47!','servers':{}}
        try:
            for name,port,repo in [('before',9001,Path(args.baseline_root).resolve()),('after',9000,Path(__file__).resolve().parents[2])]:
                ready=root/(name+'-ready.json');cfg=root/(name+'.json')
                cfg.write_text(json.dumps({'port':port,'password':config['password'],'ready':str(ready)}));cfg.chmod(0o600)
                proc=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker-config',str(cfg)],cwd=repo,env=dict(os.environ,PYTHONPATH=str(repo)),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                processes.append(proc)
                for _ in range(300):
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
    print('Design walkthrough complete: synthetic fixtures only; browsing preserved Offers/Pipeline bytes.')


if __name__=='__main__':main()
