#!/usr/bin/env python3
"""Local-only VP-1 review against the unchanged merged public renderer."""
import argparse
from http.server import ThreadingHTTPServer
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='flora-vp1-public-preview-')as temp:
        os.environ['FLORA_DATA_DIR']=temp
        sys.path.insert(0,str(ROOT))
        from cios.applications.flora.web.app import FloraWebHandler
        class Quiet(FloraWebHandler):
            def log_message(self,*_):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            subprocess.run(['node',str(HERE/'review.cjs'),str(output),f'http://127.0.0.1:{server.server_port}'],check=True)
        finally:server.shutdown();server.server_close();thread.join(2)
        for name in ['sales_pipeline/opportunities.json','commercial_context/offers-v1/context.json']:
            if (Path(temp)/name).exists():raise AssertionError('Domain write during public visual capture')
    print('VP-1 design review complete, isolated public baseline; no production or domain writes.')

if __name__=='__main__':main()
