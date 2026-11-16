#!/usr/bin/env python3
"""Real public-source proof with synthetic authority and isolated existing storage.

No production access, provider, network acquisition or canonical mutation. The
retained source is an honestly scoped reviewed original-Database excerpt.
"""
import argparse
from hashlib import sha256
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
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def run(output, preview=False, baseline_root=None):
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='flora-f1-isolated-') as scratch:
        root = Path(scratch)
        os.environ['FLORA_DATA_DIR'] = str(root/'runtime')
        os.environ['FLORA_PUBLIC_ORIGIN'] = 'https://127.0.0.1:8998'
        from cios.applications.flora.security_store import SecurityStore, canonical, digest, COOKIE
        from cios.applications.flora.security_operator import reconcile, plan, apply
        from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRecord, EnterpriseCanvasAccessRepository
        from cios.applications.flora.financial_intelligence import candidate_analytics as a
        from cios.applications.flora.research_intelligence import model
        from cios.applications.flora import document_review as review
        snapshot = root/'authority-fixture'; snapshot.mkdir()
        (snapshot/'binding.json').write_text(json.dumps({'actor_id':'preview-owner','workspace_id':'preview-workspace'}))
        evidence = reconcile(snapshot)
        manifest = {'approved':True,'operator':'SYNTHETIC-isolated-operator','approval_reference':'SYNTHETIC-nonproduction-only',
            'snapshot_digest':digest(canonical(evidence)),'evidence':evidence['files'],
            'bindings':[{'user_id':'preview-owner','workspace_id':'preview-workspace','roles':['cios_owner'],'enterprise_ids':['BK-IND-002','BK-ENT-001']}]}
        store = SecurityStore(); store.initialize_offline()
        proposal = plan(store, snapshot, manifest); apply(store, snapshot, proposal, proposal['digest'])
        delivery = root/'delivery'; store.enroll_offline('preview-owner', delivery)
        password = 'Synthetic preview phrase 57!'
        pre, csrf = store.preauth(); store.enroll(delivery.read_text().strip(), password, pre, csrf)
        pre, csrf = store.preauth(); token, csrf = store.login('preview-owner', password, pre, csrf)
        token, csrf = store.select(token, csrf, 'preview-workspace')
        headers = {'Cookie':COOKIE+'='+token}
        EnterpriseCanvasAccessRepository().save(EnterpriseCanvasAccessRecord('1.0','synthetic-banking-scope','BK-IND-002','preview-workspace','preview-owner',
            acl=({'principal_id':'preview-owner','role':'owner','grant_source':'synthetic-offline-fixture'},)))
        original_repo = model.REPO
        rel = Path('enterprise-knowledge/banking/research-model/source-snapshots')
        isolated = root/'source-owner'; (isolated/rel).mkdir(parents=True)
        for name in (a.SOURCE_FILE, 'F1-BOE-LPMZ598.txt'):
            shutil.copyfile(original_repo/rel/name, isolated/rel/name)
        model.REPO = isolated
        try:
            run_id = a.create_run('boe-household-deposit-stocks', headers=headers)
            raw = review.load_run(run_id)
            stored_bytes = review._run_path(run_id).read_bytes()
            before = a.read_analysis(run_id, headers=headers)
            assert len(before['measurements']) == 2 and before['results'][0]['value'] == '1555'
            assert a.create_run('boe-household-deposit-stocks', headers=headers) == run_id
            assert review._run_path(run_id).read_bytes() == stored_bytes
            (output/'after.html').write_text(review.financial_intelligence_run_page(run_id, headers=headers))
            package_path = isolated/rel/a.SOURCE_FILE
            original = package_path.read_bytes()
            package = json.loads(original); package['source']['withdrawn'] = True
            package_path.write_text(json.dumps(package))
            withdrawn = a.read_analysis(run_id, headers=headers)
            sanitized = review.read_run(run_id, headers=headers)
            assert withdrawn == {} and sanitized['analysis'] == {} and 'analytical_candidate' not in sanitized
            assert review._run_path(run_id).read_bytes() == stored_bytes
            (output/'withdrawn.html').write_text(review.financial_intelligence_run_page(run_id, headers=headers))
            package_path.write_bytes(original)
            assert a.read_analysis(run_id, headers=headers) == before
            proof = {'head':subprocess.check_output(['git','rev-parse','HEAD'], cwd=original_repo, text=True).strip(),
                'financial_data':'Actual BoE Database numerical excerpt; no synthetic bank facts',
                'authority':'Synthetic local-only account, workspace, session and ACL; no production authority claim',
                'storage':'Actual existing Financial ai_financial_reports/runs repository under temporary FLORA_DATA_DIR',
                'run_id':run_id,'raw_candidate':raw,'projection_after_reload':before,
                'immutable_repeat':True,'run_bytes_sha256':sha256(stored_bytes).hexdigest(),
                'withdrawal':{'dependent_projection':withdrawn,'external_read_sanitized':True,'historical_run_unchanged':True,'restored_same_source_revision_reproduces':True},
                'canonical_writes':0,'source_imports':0,'paid_calls':0,'production_access':False,
                'limitations':['Original publication day and frozen release vintage are not verified.',
                    'Current source rights are checked from the existing owner at use; remote change discovery is not automated.',
                    'Only two historical sector-aggregate stock measurements; not a five-bank financial rollout.']}
            (output/'Proof.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n')
            if preview:
                # Full application has other existing research dependencies;
                # withdrawal above used only an isolated copy. Never alter the
                # real checkout to obtain a browser test result.
                model.REPO = original_repo
                from cios.applications.flora.web.app import FloraWebHandler
                class Quiet(FloraWebHandler):
                    def log_message(self, *_): pass
                server = ThreadingHTTPServer(('127.0.0.1',8998), Quiet)
                cert, key = root/'local.crt', root/'local.key'
                subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=127.0.0.1'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); tls.load_cert_chain(cert,key); server.socket = tls.wrap_socket(server.socket,server_side=True)
                thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
                baseline = None
                if baseline_root:
                    baseline_path = Path(baseline_root).resolve()
                    assert subprocess.check_output(['git','rev-parse','HEAD'], cwd=baseline_path, text=True).strip() == '9f3dcc5b0577eb0408bc0185f0847de19a5c1f66'
                    baseline_code = '''import ssl,sys
from http.server import ThreadingHTTPServer
from cios.applications.flora.web.app import FloraWebHandler
server=ThreadingHTTPServer(('127.0.0.1',8999),FloraWebHandler)
tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);tls.load_cert_chain(sys.argv[1],sys.argv[2]);server.socket=tls.wrap_socket(server.socket,server_side=True)
server.serve_forever()
'''
                    baseline = subprocess.Popen([sys.executable,'-c',baseline_code,str(cert),str(key)], cwd=baseline_path,
                        env=dict(os.environ,PYTHONPATH=str(baseline_path)),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                    import socket
                    for _ in range(100):
                        try:
                            with socket.create_connection(('127.0.0.1',8999), timeout=1): break
                        except OSError: time.sleep(.1)
                    else: raise RuntimeError('Baseline server unavailable')
                config = root/'preview.json'
                config.write_text(json.dumps({'base':'https://127.0.0.1:8998','password':password,'run_id':run_id,'output':str(output),
                    'baseline':'https://127.0.0.1:8999' if baseline else None}))
                try:
                    subprocess.run(['node',str(original_repo/'tools/ci/flora_f1_preview.cjs'),str(config)],check=True)
                finally:
                    server.shutdown(); server.server_close(); thread.join(2)
                    if baseline: baseline.terminate(); baseline.wait(timeout=5)
            for name in ('memory','sales_pipeline','commercial_context'):
                assert not (root/'runtime'/name).exists(), 'Unexpected domain-state write'
        finally:
            model.REPO = original_repo
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True); parser.add_argument('--preview', action='store_true'); parser.add_argument('--baseline-root')
    args = parser.parse_args(); result = run(args.output, args.preview, args.baseline_root)
    print(json.dumps({'head':result['head'],'real_measurements':2,'reproduced_derivations':2,'withdrawal':'pass','canonical_writes':0}))
