#!/usr/bin/env python3
"""Reproducible Offers owner walkthrough using isolated SYNTHETIC identities.

No deployment, external research, model calls or production data. Requires local
Playwright/Chromium. Private fixture authority and logs stay outside the repo.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import ssl
import sys
import time
import urllib.request
import threading
from http.server import ThreadingHTTPServer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--baseline-root', help='Optional clean main checkout for before/parity previews')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='flora-offers-synthetic-') as scratch:
        root = Path(scratch)
        os.environ['FLORA_DATA_DIR'] = str(root / 'runtime')
        os.environ['FLORA_PUBLIC_ORIGIN'] = 'https://127.0.0.1:8996'
        from cios.applications.flora.security_store import SecurityStore, canonical, digest
        from cios.applications.flora.security_operator import reconcile, plan, apply
        from cios.applications.flora.commercial_mission import save_employer_context
        from cios.applications.flora.security_web import CSRF_COOKIE
        from cios.applications.flora.security_store import COOKIE
        from cios.applications.flora import offers
        snapshot = root / 'snapshot'; snapshot.mkdir()
        (snapshot / 'synthetic.json').write_text(json.dumps([{'actor_id': user, 'workspace_id': 'preview-workspace'} for user in ('preview-owner', 'preview-seller', 'preview-reviewer')]))
        evidence = reconcile(snapshot)
        manifest = {'approved': True, 'operator': 'SYNTHETIC-preview-operator',
            'approval_reference': 'SYNTHETIC-fixture-only-approval', 'snapshot_digest': digest(canonical(evidence)),
            'evidence': evidence['files'], 'bindings': [
                {'user_id': user, 'workspace_id': 'preview-workspace', 'roles': ['cios_owner'],
                 'enterprise_ids': ['BK-ENT-001', 'AV-ENT-001']} for user, roles in
                [('preview-owner', ['cios_owner']), ('preview-seller', ['commercial_context.view', 'commercial_context.edit']),
                 ('preview-reviewer', ['commercial_context.view', 'commercial_context.edit'])]]}
        store = SecurityStore(); store.initialize_offline()
        proposed = plan(store, snapshot, manifest)
        apply(store, snapshot, proposed, proposed['digest'])
        # The existing bootstrap admits owners only. Narrow these synthetic fixture
        # memberships before any enrollment/session; no production authority is touched.
        with store.transaction() as db:
            db.execute('UPDATE memberships SET roles=?,version=version+1 WHERE user_id IN (?,?)',
                (canonical(['commercial_context.view', 'commercial_context.edit']), 'preview-seller', 'preview-reviewer'))
        password = 'Synthetic preview phrase 47!'
        headers = {}
        for user in ('preview-owner', 'preview-seller', 'preview-reviewer'):
            delivery = root / user
            store.enroll_offline(user, delivery)
            pre, csrf = store.preauth(); store.enroll(delivery.read_text().strip(), password, pre, csrf)
            pre, csrf = store.preauth(); token, csrf = store.login(user, password, pre, csrf)
            token, csrf = store.select(token, csrf, 'preview-workspace')
            headers[user] = {'Cookie': f'{COOKIE}={token}; {CSRF_COOKIE}={csrf}'}
        owner, seller, reviewer = (headers[u] for u in ('preview-owner', 'preview-seller', 'preview-reviewer'))
        save_employer_context(owner, {'organisation': 'Illustrative UK services company', 'capabilities': ['Synthetic diagnostics only']})
        binding = offers.bind_employer(list(headers), ['preview-reviewer'], 'SYNTHETIC-employer-review', headers=owner)
        for h in headers.values(): offers.select_employer(binding['id'], headers=h)
        offer_ids = []
        for key, content in offers.TEMPLATES.items():
            record = offers.save_offer(content | {'evidence': 'SYNTHETIC-capability-review / illustrative only; not company proof'}, headers=seller)
            offers.transition(record['id'], 1, 'submit', headers=seller)
            record = offers.transition(record['id'], 2, 'approve', 'SYNTHETIC-independent-rights-review', headers=reviewer)
            offer_ids.append(record['id'])
        private = offers.save_offer({'name': 'Banking service resilience', 'icp': 'Banking',
            'entry_play': 'Ask the accountable service owner to map one dependency before proposing change.'},
            parent_id=offer_ids[0], parent_version=3, headers=seller)
        pending = offers.save_offer(offers.TEMPLATES['ai'] | {'name': 'AI value workshop — review candidate'}, headers=seller)
        offers.transition(pending['id'], 1, 'submit', headers=seller)
        from cios.applications.flora.web.app import FloraWebHandler
        class QuietHandler(FloraWebHandler):
            def log_message(self, *_): pass
        server = ThreadingHTTPServer(('127.0.0.1', 8996), QuietHandler)
        # Real HTTPS keeps the production Secure-cookie/origin requirements intact.
        cert, key = root / 'localhost.crt', root / 'localhost.key'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', str(key),
            '-out', str(cert), '-days', '1', '-subj', '/CN=127.0.0.1'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); tls.load_cert_chain(cert, key)
        server.socket = tls.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        baseline_process = None
        if args.baseline_root:
            baseline = Path(args.baseline_root).resolve()
            baseline_env = dict(os.environ, FLORA_DATA_DIR=str(root / 'baseline-runtime'), PYTHONPATH=str(baseline))
            baseline_process = subprocess.Popen([sys.executable, '-c',
                'from http.server import ThreadingHTTPServer; from cios.applications.flora.web.app import FloraWebHandler; ThreadingHTTPServer(("127.0.0.1",8997),FloraWebHandler).serve_forever()'],
                cwd=baseline, env=baseline_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for attempt in range(100):
                try:
                    urllib.request.urlopen('http://127.0.0.1:8997/health', timeout=1).close()
                    break
                except OSError:
                    time.sleep(.1)
            else:
                raise RuntimeError('Baseline fixture server did not start')
        config = root / 'preview.json'
        config.write_text(json.dumps({'base': 'https://127.0.0.1:8996', 'output': str(output),
            'password': password, 'private_id': private['id'], 'first_offer': offer_ids[0],
            'second_offer': offer_ids[1], 'baseline': 'http://127.0.0.1:8997' if baseline_process else None}))
        try:
            subprocess.run(['node', str(Path(__file__).with_name('flora_offers_preview.cjs')), str(config)], check=True)
        finally:
            server.shutdown(); server.server_close(); thread.join(2)
            if baseline_process:
                baseline_process.terminate(); baseline_process.wait(timeout=5)
        if (Path(os.environ['FLORA_DATA_DIR']) / 'sales_pipeline' / 'opportunities.json').exists():
            raise AssertionError('Preview unexpectedly wrote Pipeline')
    print('Synthetic responsive walkthrough completed; no Pipeline writes.')


if __name__ == '__main__':
    main()
