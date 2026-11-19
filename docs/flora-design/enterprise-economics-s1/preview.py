"""Loopback-only static design preview and browser proof, no FLORA runtime."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import subprocess
import tempfile
import threading

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def run(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(HERE/'prototype'),**kwargs)
        def log_message(self,*args): pass
        def translate_path(self,path):
            if path.startswith('/shots/'):
                target=(output/path.removeprefix('/shots/').split('?')[0]).resolve()
                if target.is_relative_to(output):return str(target)
                return str(output/'not-found')
            return super().translate_path(path)
    server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread = threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory(prefix='flora-economics-design-') as td:
            config=Path(td)/'config.json'
            config.write_text(json.dumps({'base':f'http://127.0.0.1:{server.server_port}', 'output':str(output)}))
            subprocess.run(['node',str(HERE/'preview.cjs'),str(config)],cwd=ROOT,check=True)
    finally:
        server.shutdown();server.server_close();thread.join(2)
    proof={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'base':'03719d7573f087c65d9622719273aa4b89caf7d3','static_design_only':True,
        'live_Render_or_authentication_checked':False,'runtime_or_canonical_writes':0,
        'lloyds':'No restricted values or PDF links; §2 and §5 unchanged',
        'limitations':'Chromium viewport emulation; not physical iPad/Safari or human screen-reader certification.'}
    (output/'Proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
