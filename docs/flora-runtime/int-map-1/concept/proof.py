"""Serve only repository files for isolated design preview; never start FLORA."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path
import subprocess
import threading

ROOT=Path(__file__).resolve().parents[4]


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    url=f'http://127.0.0.1:{server.server_port}/docs/flora-runtime/int-map-1/concept/index.html'
    try:
        subprocess.run(['node',str(Path(__file__).with_name('check.cjs')),url,str(out)],check=True)
        (out/'Proof.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'baseline':'fbac4c37910ed07b2baa516e1a5c8d7f329086de','application_started':False,'production_or_canonical_writes':0,'external_acquisition':False},indent=2)+'\n')
    finally:server.shutdown();server.server_close();thread.join(2)


if __name__=='__main__':main()
