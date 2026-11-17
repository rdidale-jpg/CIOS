"""Explicit presentation-only owner evolution; never a failure baseline writer."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def assert_evolution(root,path,previous):
    records=json.loads((ROOT/'docs/flora-runtime/uxr1-650/Owner-Evolution.json').read_text())
    record=records[path]
    assert sha256(previous).hexdigest()in record['prior_sha256'],'Unrecognised historical owner: '+path
    from tools.research.auth2_compatibility import reviewed_predecessor
    assert sha256(reviewed_predecessor(root,path)).hexdigest()==record['reviewed_sha256'],'Unreviewed UX owner change: '+path
