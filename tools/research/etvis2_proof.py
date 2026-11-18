#!/usr/bin/env python3
"""Actual HTTP app/browser proof; only isolated copies of source data mutate."""
import argparse
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
BASE = 'fbac4c37910ed07b2baa516e1a5c8d7f329086de'


def run(output, baseline_root):
    import pytest
    from cios.applications.flora.research_intelligence import model, registry
    from cios.applications.flora.web.app import FloraWebHandler
    from tools.research.etvis2_compatibility import validate
    output = Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=baseline_root,text=True).strip()==BASE
    with tempfile.TemporaryDirectory(prefix='flora-etvis2-isolated-') as scratch, pytest.MonkeyPatch.context() as patch:
        root=Path(scratch)
        copied=root/'source-copy'
        shutil.copytree(ROOT/'enterprise-knowledge',copied/'enterprise-knowledge')
        patch.setenv('FLORA_DATA_DIR',str(root/'empty-authority'))
        patch.setenv('FLORA_TRUST_PROXY_HEADERS','0')
        patch.setattr(model,'REPO',copied)
        patch.setattr(registry,'REPO',copied)
        patch.setattr(model,'DATA',copied/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json')
        class Quiet(FloraWebHandler):
            def log_message(self,*args): pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
        server.daemon_threads=True
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        code='''import sys
from http.server import ThreadingHTTPServer
from cios.applications.flora.web.app import FloraWebHandler
class Quiet(FloraWebHandler):
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
print(s.server_port,flush=True)
s.serve_forever()
'''
        baseline=subprocess.Popen([sys.executable,'-c',code],cwd=baseline_root,
            env=dict(os.environ,PYTHONPATH=str(baseline_root)),stdout=subprocess.PIPE,text=True)
        baseline_port=int(baseline.stdout.readline().strip())
        source=copied/'enterprise-knowledge/aviation/research-model/Assessment-Overlay.json'
        cfg=root/'browser.json';cfg.write_text(json.dumps({'base':f'http://127.0.0.1:{server.server_port}',
            'baseline':f'http://127.0.0.1:{baseline_port}','source_package':str(source),'output':str(output)}))
        try:
            subprocess.run(['node',str(ROOT/'tools/ci/flora_etvis2_preview.cjs'),str(cfg)],check=True)
        finally:
            server.shutdown();server.server_close();thread.join(2);baseline.terminate();baseline.wait(timeout=5)
        assert not (root/'empty-authority').exists(), 'Public preview unexpectedly created persistent authority/data'
        proof={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'base':BASE,'boundary':validate(),'production_writes':0,'canonical_changes':0,
            'source_inputs':'Existing retained reviewed short excerpts; no new acquisition or permissions',
            'authority':'Guest HTTP requests with real production access guards; private routes denied',
            'devices':'Chromium viewport/touch emulation, not physical device testing'}
        (output/'Proof.json').write_text(json.dumps(proof,indent=2)+'\n')
        return proof


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--baseline-root',required=True)
    a=p.parse_args();print(json.dumps(run(a.output,Path(a.baseline_root)),indent=2))
