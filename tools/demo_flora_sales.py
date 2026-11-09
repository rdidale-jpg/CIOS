"""Run a disposable HTTPS Banking sales demo; never uses a production store.

Creates one explicitly synthetic local identity through the existing offline
operator and normal enrollment/session flow. No external services or API keys.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import ssl
import subprocess
import sys
import tempfile


def prepare(port):
    repo=Path(__file__).resolve().parents[1]
    root=Path(tempfile.mkdtemp(prefix='flora-sales-demo-'))
    env={k:v for k,v in os.environ.items() if k in {'PATH','HOME','LANG','LC_ALL','TMPDIR'}}
    env.update(FLORA_DATA_DIR=str(root/'runtime'),FLORA_PILOT_DIR=str(root/'runtime'),
               FLORA_ENVIRONMENT='development',FLORA_PUBLIC_ORIGIN=f'https://localhost:{port}',
               PYTHONPATH=str(repo),PYTHONDONTWRITEBYTECODE='1')
    os.environ.clear();os.environ.update(env)
    sys.path.insert(0,str(repo))
    from cios.applications.flora.security_store import SecurityStore,canonical,digest,COOKIE
    from cios.applications.flora.security_operator import reconcile,plan,apply
    from cios.applications.flora.banking_portfolio import BANKS
    from cios.applications.flora.security_web import CSRF_COOKIE
    from cios.applications.flora.sales_pipeline import create_opportunity,update_opportunity
    snapshot=root/'synthetic-snapshot';snapshot.mkdir()
    (snapshot/'demo.json').write_text(json.dumps({'actor_id':'demo-sales-owner','workspace_id':'demo-sales-workspace'}))
    evidence=reconcile(snapshot)
    manifest={'approved':True,'operator':'local-synthetic-demo-runner',
              'approval_reference':'Owner-requested synthetic demonstration only; no real ownership or production approval asserted',
              'snapshot_digest':digest(canonical(evidence)),'evidence':evidence['files'],
              'bindings':[{'user_id':'demo-sales-owner','workspace_id':'demo-sales-workspace',
                           'roles':['cios_owner'],'enterprise_ids':[b.id for b in BANKS.values()]}]}
    store=SecurityStore();store.initialize_offline()
    proposed=plan(store,snapshot,manifest);apply(store,snapshot,proposed,proposed['digest'])
    delivery=root/'enrollment';store.enroll_offline('demo-sales-owner',delivery)
    password=secrets.token_urlsafe(24)
    pre,csrf=store.preauth();store.enroll(delivery.read_text().strip(),password,pre,csrf)
    pre,csrf=store.preauth();token,csrf=store.login('demo-sales-owner',password,pre,csrf)
    token,csrf=store.select(token,csrf,'demo-sales-workspace')
    headers={'Cookie':f'{COOKIE}={token}; {CSRF_COOKIE}={csrf}'}
    seeds=[]
    for slug in ['lloyds','barclays']:
        for index,source in enumerate(BANKS[slug].opportunities[:2]):
            record=create_opportunity(slug,source.id,headers=headers)
            if index==1:
                record=update_opportunity(record['id'],record['version'],
                    {'stage':'Researching','priority':'High','amount':'15000','value_basis':'Estimate',
                     'value_reference':'Synthetic scope assumption: 15 discovery days × GBP 1,000/day; not customer budget.',
                     'activity':'Demonstration desk-research task opened. No customer engagement asserted.'},headers=headers)
            seeds.append(record['id'])
    store.logout(token,csrf)
    key=root/'local-preview.key';cert=root/'local-preview.crt'
    subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','2',
                    '-keyout',str(key),'-out',str(cert),'-subj','/CN=localhost',
                    '-addext','subjectAltName=DNS:localhost,IP:127.0.0.1'],check=True,capture_output=True)
    key.chmod(0o600)
    access={'url':f'https://localhost:{port}/flora/banking/explorer',
            'pipeline_url':f'https://localhost:{port}/flora/sales/pipeline',
            'user':'demo-sales-owner','password':password,'workspace':'demo-sales-workspace',
            'root':str(root),'records':seeds}
    access_path=root/'demo-access.json';access_path.write_text(json.dumps(access,indent=2));access_path.chmod(0o600)
    return root,cert,key,access_path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8768)
    args=parser.parse_args()
    if not 1024<=args.port<=65535:parser.error('Choose an unprivileged local port.')
    root,cert,key,access_path=prepare(args.port)
    from http.server import ThreadingHTTPServer
    from cios.applications.flora.web.app import FloraWebHandler
    from cios.applications.flora.storage import startup_storage_status
    FloraWebHandler.storage_status=startup_storage_status()
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(cert,key)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),FloraWebHandler)
    server.socket=context.wrap_socket(server.socket,server_side=True)
    print(f'Disposable demo: https://localhost:{args.port}/flora/banking/explorer',flush=True)
    print(f'Local-only demonstration credentials: {access_path}',flush=True)
    print('Uses a temporary self-signed localhost certificate. No production connection. Ctrl-C stops the server.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


if __name__=='__main__':
    main()
