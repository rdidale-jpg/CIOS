"""Actual shipping factual method and isolated restriction/withdrawal browser proof."""
import argparse
from hashlib import sha256
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


def run(output):
    import pytest
    from cios.applications.flora.research_intelligence import model
    from cios.applications.flora.web.app import FloraWebHandler
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    relative=Path('enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json')
    original=(ROOT/relative).read_bytes()
    with tempfile.TemporaryDirectory(prefix='flora-public-financial-') as scratch,pytest.MonkeyPatch.context() as patch:
        root=Path(scratch)
        shutil.copytree(ROOT/'enterprise-knowledge',root/'enterprise-knowledge')
        patch.setattr(model,'REPO',root)
        patch.setenv('FLORA_DATA_DIR',str(root/'isolated-app'))
        patch.delenv('FLORA_PILOT_DIR',raising=False)
        patch.setenv('FLORA_ENVIRONMENT','development')
        class Quiet(FloraWebHandler):
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        source=root/relative
        cfg=root/'browser.json';cfg.write_text(json.dumps({'base':f'http://127.0.0.1:{server.server_port}',
            'source':str(source),'output':str(output)}))
        try:subprocess.run(['node',str(ROOT/'tools/ci/flora_public_financial_preview.cjs'),str(cfg)],check=True)
        finally:server.shutdown();server.server_close();thread.join(2)
    assert (ROOT/relative).read_bytes()==original
    result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'shipping_state':'Independent ordinary factual analysis active; existing Source determination recorded',
        'restriction_challenge':'ISOLATED applicable-restriction test only; no live Source change',
        'production_or_canonical_writes':0,'live_Render_or_Supabase_checked':False,
        'shipping_source_sha256':sha256(original).hexdigest()}
    (output/'Proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    run(parser.parse_args().output)
