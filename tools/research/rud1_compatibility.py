"""Explicit RUD-1 owner evolution, separate from inherited-failure comparators.

The old immutable research and control cuts remain evidence. Only individually
reviewed owners below may differ, against exact recorded before/after digests.
This is code-change assurance, never a runtime source or Evidence admission.
"""
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def assert_evolution(root, path, previous):
    changes=json.loads((ROOT/'docs/flora-runtime/rud1-648/Owner-Evolution.json').read_text())
    record=changes[path]
    assert sha256(previous).hexdigest() in record['prior_sha256'], 'Unrecognised historical owner cut: '+path
    assert sha256((Path(root)/path).read_bytes()).hexdigest()==record['reviewed_sha256'], 'Unreviewed owner evolution: '+path
