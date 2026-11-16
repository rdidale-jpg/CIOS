#!/usr/bin/env python3
"""F2 actual permitted data, actual existing Financial repo, isolated authority.

No live account, production data, canonical promotion, source-policy mutation or
paid call. Source withdrawal modifies a temporary copy, never this checkout.
"""
import argparse
from hashlib import sha256
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
BASE='98fcab91aa94180b11c41c60f4cf7e4d4ad39e40'


def run(output,preview=False,baseline_root=None,*,baseline_sha=BASE,baseline_financial_main=False):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='flora-f2-isolated-') as scratch:
        root=Path(scratch)
        os.environ['FLORA_DATA_DIR']=str(root/'runtime')
        os.environ['FLORA_PUBLIC_ORIGIN']='https://127.0.0.1:8994'
        from cios.applications.flora.security_store import SecurityStore,canonical,digest,COOKIE
        from cios.applications.flora.security_operator import reconcile,plan,apply
        from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRecord,EnterpriseCanvasAccessRepository
        from cios.applications.flora.financial_intelligence import candidate_analytics as f,analyst
        from cios.applications.flora import document_review as review,visual_streams as visual
        from cios.applications.flora.research_intelligence import model
        original_repo=model.REPO
        snapshot=root/'synthetic-authority';snapshot.mkdir()
        (snapshot/'binding.json').write_text(json.dumps([{'actor_id':'preview-owner','workspace_id':'preview-workspace'},{'actor_id':'preview-foreign','workspace_id':'foreign-workspace'}]))
        evidence=reconcile(snapshot)
        bindings=[{'user_id':u,'workspace_id':w,'roles':['cios_owner'],'enterprise_ids':['BK-IND-002','BK-ENT-001']}
                  for u,w in [('preview-owner','preview-workspace'),('preview-foreign','foreign-workspace')]]
        manifest={'approved':True,'operator':'SYNTHETIC-isolated-operator','approval_reference':'SYNTHETIC-F2-only',
            'snapshot_digest':digest(canonical(evidence)),'evidence':evidence['files'],'bindings':bindings}
        store=SecurityStore();store.initialize_offline();proposal=plan(store,snapshot,manifest);apply(store,snapshot,proposal,proposal['digest'])
        password='Synthetic financial preview phrase 91!'
        for user in ('preview-owner','preview-foreign'):
            delivery=root/('delivery-'+user);store.enroll_offline(user,delivery)
            pre,csrf=store.preauth();store.enroll(delivery.read_text().strip(),password,pre,csrf)
        pre,csrf=store.preauth();token,csrf=store.login('preview-owner',password,pre,csrf)
        token,csrf=store.select(token,csrf,'preview-workspace');headers={'Cookie':COOKIE+'='+token}
        EnterpriseCanvasAccessRepository().save(EnterpriseCanvasAccessRecord('1.0','synthetic-banking-scope','BK-IND-002','preview-workspace','preview-owner',
            acl=({'principal_id':'preview-owner','role':'owner','grant_source':'synthetic-isolated-fixture'},)))
        isolated=root/'source-owner';shutil.copytree(original_repo/'enterprise-knowledge',isolated/'enterprise-knowledge')
        model.REPO=isolated
        try:
            run_id=f.create_run('boe-household-deposit-stocks',headers=headers)
            raw=review.load_run(run_id);stored=review._run_path(run_id).read_bytes()
            assert f.find_existing_run('boe-household-deposit-stocks','BK-IND-002',headers=headers)==run_id
            projection=f.read_analysis(run_id,headers=headers)
            html=visual.render('/industries/banking',{'analysis':[run_id]},headers)
            assert '0.0825%'in html and '£1.555bn'in html and 'data-region="main"'in html
            source_path=isolated/'enterprise-knowledge/banking/research-model/source-snapshots'/f.SOURCE_FILE
            source_bytes=source_path.read_bytes();package=json.loads(source_bytes);package['source']['withdrawn']=True
            source_path.write_text(json.dumps(package))
            assert run_id not in analyst.navigation(visual.Context('banking','landscape'),headers)
            assert not analyst.authorise_request('/industries/banking?analysis='+run_id,headers=headers)
            assert f.read_analysis(run_id,headers=headers)=={}
            assert review._run_path(run_id).read_bytes()==stored
            source_path.write_bytes(source_bytes)
            proof={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=original_repo,text=True).strip(),
                'base':baseline_sha,'data':'Two actual retained permitted BoE measurements; no new bank financials',
                'authority':'Synthetic offline identities/workspace/ACL; no production authority',
                'storage':'Actual existing Financial ai_financial_reports/runs in temporary FLORA_DATA_DIR',
                'run_id':run_id,'raw_candidate':raw,'projection_after_reload':projection,
                'source_withdrawal':{'main_entry_omitted':True,'private_selector_denied':True,'dependent_projection':{},'history_sha256_unchanged':sha256(stored).hexdigest()},
                'new_source_permissions':0,'canonical_writes':0,'production_writes':0,'paid_calls':0,
                'limits':['Historical sector aggregate; not a named bank, official flow/growth or latest release.',
                    'Original publication/release vintage unverified; retained reviewed excerpt, original-byte hash null.',
                    'Source-owner withdrawal is rechecked; remote source/licence change discovery is not automated.']}
            (output/'Proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
            if preview:
                from cios.applications.flora.web.app import FloraWebHandler
                class Quiet(FloraWebHandler):
                    def log_message(self,*_):pass
                server=ThreadingHTTPServer(('127.0.0.1',8994),Quiet)
                cert,key=root/'local.crt',root/'local.key'
                subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=127.0.0.1'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);tls.load_cert_chain(cert,key);server.socket=tls.wrap_socket(server.socket,server_side=True)
                thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                baseline=None
                if baseline_root:
                    baseline_path=Path(baseline_root).resolve()
                    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=baseline_path,text=True).strip()==baseline_sha
                    code='''import ssl,sys
from http.server import ThreadingHTTPServer
from cios.applications.flora.web.app import FloraWebHandler
s=ThreadingHTTPServer(('127.0.0.1',8995),FloraWebHandler)
t=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);t.load_cert_chain(sys.argv[1],sys.argv[2]);s.socket=t.wrap_socket(s.socket,server_side=True)
s.serve_forever()
'''
                    baseline=subprocess.Popen([sys.executable,'-c',code,str(cert),str(key)],cwd=baseline_path,
                        env=dict(os.environ,PYTHONPATH=str(baseline_path)),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                    for _ in range(100):
                        try:
                            with socket.create_connection(('127.0.0.1',8995),timeout=1):break
                        except OSError:time.sleep(.1)
                    else:raise RuntimeError('Baseline server unavailable')
                cfg=root/'browser.json'
                assert source_path.is_relative_to(root)
                cfg.write_text(json.dumps({'base':'https://127.0.0.1:8994','baseline':'https://127.0.0.1:8995'if baseline else None,
                    'password':password,'run_id':run_id,'output':str(output),'source_package':str(source_path),
                    'baseline_financial_main':baseline_financial_main}))
                try:subprocess.run(['node',str(original_repo/'tools/ci/flora_f2_preview.cjs'),str(cfg)],check=True)
                finally:
                    server.shutdown();server.server_close();thread.join(2)
                    if baseline:baseline.terminate();baseline.wait(timeout=5)
            assert review._run_path(run_id).read_bytes()==stored
            for name in ('memory','sales_pipeline','commercial_context'):
                assert not(root/'runtime'/name).exists(),'Unexpected canonical/commercial state'
        finally:model.REPO=original_repo
    return proof


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--preview',action='store_true');p.add_argument('--baseline-root')
    args=p.parse_args();r=run(args.output,args.preview,args.baseline_root)
    print(json.dumps({'head':r['head'],'actual_measurements':2,'reproduced_results':2,'withdrawal':'pass','canonical_writes':0}))
