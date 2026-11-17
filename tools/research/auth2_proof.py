#!/usr/bin/env python3
"""Real HTTPS FLORA journeys, isolated authority and labelled provider double.

No Supabase tenant, credentials, production, source grants or live sign-in claim.
Test fixtures supply artificial identity only; existing retained financial facts
and all application/session/ACL/Financial services are real.
"""
import argparse
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import ssl
import subprocess
import sys
import tempfile
import threading

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
BASE='7b056b21cd5d824bc4359b4e1ed49a1673a7f5fc'


def run(output,baseline_root):
    import pytest
    from tests.test_flora_security_repair_01b import authority
    from tests.test_flora_f1_642 import permitted
    from tests.test_flora_auth2_655 import provider,bind,EMAIL,PASSWORD
    from cios.applications.flora import supabase_identity as identity
    from cios.applications.flora.financial_intelligence import candidate_analytics as financial
    from cios.applications.flora import document_review as review
    from cios.applications.flora.research_intelligence import model
    from cios.applications.flora.web.app import FloraWebHandler
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=baseline_root,text=True).strip()==BASE
    with tempfile.TemporaryDirectory(prefix='flora-auth2-isolated-')as scratch, pytest.MonkeyPatch.context()as patch:
        root=Path(scratch)
        auth=authority.__wrapped__(root,patch)
        store,headers,_=permitted.__wrapped__(auth,root)
        run_id=financial.create_run('nationwide-fy2026',headers=headers)
        state=provider.__wrapped__(patch);bind(store)
        patch.setenv('FLORA_PUBLIC_ORIGIN','https://127.0.0.1:8994')
        copied=root/'source-owner';shutil.copytree(model.REPO/'enterprise-knowledge',copied/'enterprise-knowledge');patch.setattr(model,'REPO',copied)
        source=copied/'enterprise-knowledge/banking/research-model/source-snapshots/RUD1-Public-Facts.json'
        control=root/'provider-state.json';control.write_text('{}')
        fake=identity.Provider.request
        def controlled(self,*args,**kwargs):
            state['offline']=json.loads(control.read_text()).get('offline',False)
            return fake(self,*args,**kwargs)
        patch.setattr(identity.Provider,'request',controlled)
        cert,key=root/'tls.crt',root/'tls.key'
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=127.0.0.1'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        class Quiet(FloraWebHandler):
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',8994),Quiet)
        tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);tls.load_cert_chain(cert,key);server.socket=tls.wrap_socket(server.socket,server_side=True)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        code='''import ssl,sys
from http.server import ThreadingHTTPServer
from cios.applications.flora.web.app import FloraWebHandler
s=ThreadingHTTPServer(('127.0.0.1',8995),FloraWebHandler)
t=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);t.load_cert_chain(sys.argv[1],sys.argv[2]);s.socket=t.wrap_socket(s.socket,server_side=True)
s.serve_forever()
'''
        env={k:v for k,v in os.environ.items()if not k.startswith('FLORA_SUPABASE_')}
        env.update(FLORA_AUTH_PROVIDER='local',PYTHONPATH=str(baseline_root),FLORA_PUBLIC_ORIGIN='https://127.0.0.1:8995')
        baseline=subprocess.Popen([sys.executable,'-c',code,str(cert),str(key)],cwd=baseline_root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        cfg=root/'browser.json';cfg.write_text(json.dumps({'base':'https://127.0.0.1:8994','baseline':'https://127.0.0.1:8995',
            'email':EMAIL,'password':PASSWORD,'run_id':run_id,'output':str(output),'control':str(control),
            'authority_path':str(store.path),'source_package':str(source),'python':sys.executable}))
        original=review._run_path(run_id).read_bytes()
        try:
            subprocess.run(['node',str(ROOT/'tools/ci/flora_auth2_preview.cjs'),str(cfg)],check=True)
            assert review._run_path(run_id).read_bytes()==original
        finally:
            server.shutdown();server.server_close();thread.join(2);baseline.terminate();baseline.wait(timeout=5)
        report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'base':BASE,
            'identity':'Isolated provider double, NOT live Supabase verification',
            'authority':'Actual existing CIOS store/session/workspace/resource ACL services, synthetic accounts',
            'financial':'Eight genuine existing permitted Nationwide facts; two reproducible bridges',
            'live_supabase':'NOT_CONFIGURED_OR_VERIFIED','live_Render_sign_in':'NOT_VERIFIED',
            'production_changes':0,'canonical_promotions':0}
        (output/'Proof.json').write_text(json.dumps(report,indent=2)+'\n')
        return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--baseline-root',required=True)
    args=p.parse_args();print(json.dumps(run(args.output,Path(args.baseline_root)),indent=2))
