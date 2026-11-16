"""UX-R1 exact-head, unchanged-history and original-asset validation."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
BASE='93e83d34ee2661ebe17cbc06b047350f6c32e3c3'


def validate():
    from tools.research.rud1_quality import validate as research_quality
    from tools.research.uxr1_compatibility import assert_evolution
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'cios/applications/flora/visual_stream_assets'],cwd=ROOT,text=True).splitlines()
    images={}
    for path in paths:
        current=(ROOT/path).read_bytes()
        assert current==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT),path
        images[path]=sha256(current).hexdigest()
    assert len(images)==51
    for path,entry in json.loads((ROOT/'docs/flora-runtime/uxr1-650/Owner-Evolution.json').read_text()).items():
        previous=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
        assert_evolution(ROOT,path,previous)
        try:assert_evolution(ROOT,path,previous+b' unapproved mutation')
        except AssertionError:pass
        else:raise AssertionError('History assertion accepted an unknown prior cut')
    return {'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'base':BASE,'original_asset_files':len(images),'asset_sha256':images,
        'research_quality':research_quality(),'new_source_permissions':0,'canonical_promotions':0}


if __name__=='__main__':print(json.dumps(validate(),indent=2))
