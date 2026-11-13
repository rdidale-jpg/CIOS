#!/usr/bin/env python3
"""Isolated two-screen design review. Synthetic auth only; no deployment."""
import argparse
import json
import os
from pathlib import Path
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--baseline-root')
    args = parser.parse_args()
    output = Path(args.output).resolve(); output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='flora-visual-synthetic-') as scratch:
        root = Path(scratch)
        os.environ['FLORA_DATA_DIR'] = str(root / 'runtime')
        os.environ['FLORA_PUBLIC_ORIGIN'] = 'https://127.0.0.1:8998'
        from cios.applications.flora.security_store import SecurityStore, canonical, digest
        from cios.applications.flora.security_operator import reconcile, plan, apply
        snapshot = root/'snapshot'; snapshot.mkdir()
        (snapshot/'synthetic.json').write_text(json.dumps({'actor_id':'preview-owner','workspace_id':'preview-workspace'}))
        evidence = reconcile(snapshot)
        manifest = {'approved':True,'operator':'SYNTHETIC-preview-operator', 'approval_reference':'SYNTHETIC-fixture-only-approval',
            'snapshot_digest':digest(canonical(evidence)),'evidence':evidence['files'],
            'bindings':[{'user_id':'preview-owner','workspace_id':'preview-workspace','roles':['cios_owner'],'enterprise_ids':['BK-ENT-001','AV-ENT-001']}]}
        store = SecurityStore(); store.initialize_offline()
        proposed = plan(store, snapshot, manifest); apply(store, snapshot, proposed, proposed['digest'])
        password = 'Synthetic design phrase 47!'
        delivery = root / 'enrollment'; store.enroll_offline('preview-owner', delivery)
        pre, csrf = store.preauth(); store.enroll(delivery.read_text().strip(), password, pre, csrf)
        from cios.applications.flora.web.app import FloraWebHandler
        class QuietHandler(FloraWebHandler):
            def log_message(self, *_): pass
        server = ThreadingHTTPServer(('127.0.0.1',8998), QuietHandler)
        cert, key = root/'local.crt', root/'local.key'
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=127.0.0.1'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); tls.load_cert_chain(cert,key); server.socket = tls.wrap_socket(server.socket,server_side=True)
        thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        baseline = None
        if args.baseline_root:
            source = Path(args.baseline_root).resolve()
            baseline = subprocess.Popen([sys.executable,'-c','from http.server import ThreadingHTTPServer; from cios.applications.flora.web.app import FloraWebHandler; ThreadingHTTPServer(("127.0.0.1",8999),FloraWebHandler).serve_forever()'],cwd=source,env=dict(os.environ,PYTHONPATH=str(source),FLORA_DATA_DIR=str(root/'baseline')),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            for _ in range(100):
                try:
                    urllib.request.urlopen('http://127.0.0.1:8999/health',timeout=1).close(); break
                except OSError: time.sleep(.1)
            else: raise RuntimeError('Baseline server unavailable')
        config = root/'config.json'
        config.write_text(json.dumps({'base':'https://127.0.0.1:8998','output':str(output),'password':password,'baseline':'http://127.0.0.1:8999' if baseline else None}))
        try:
            subprocess.run(['node',str(Path(__file__).with_suffix('.cjs')),str(config)],check=True)
        finally:
            server.shutdown(); server.server_close(); thread.join(2)
            if baseline: baseline.terminate(); baseline.wait(timeout=5)
        for path in ('sales_pipeline/opportunities.json','commercial_context/offers-v1/context.json'):
            if (Path(os.environ['FLORA_DATA_DIR'])/path).exists(): raise AssertionError('Preview wrote domain state')
    print('Two-screen synthetic visual review complete; no Offers/Pipeline writes.')


if __name__ == '__main__': main()
