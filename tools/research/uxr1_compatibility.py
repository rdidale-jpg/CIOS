"""Explicit presentation-only owner evolution; never a failure baseline writer."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def assert_evolution(root,path,previous):
    records=json.loads((ROOT/'docs/flora-runtime/uxr1-650/Owner-Evolution.json').read_text())
    record=records[path]
    assert sha256(previous).hexdigest()in record['prior_sha256'],'Unrecognised historical owner: '+path
    assert sha256((Path(root)/path).read_bytes()).hexdigest()==record['reviewed_sha256'],'Unreviewed UX owner change: '+path
