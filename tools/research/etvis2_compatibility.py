"""Exact additive ET-VIS-2 dispatch evolution, never a test-baseline exception.

Restore only the reviewed literal additions, then byte-compare the ENTIRE owner
against the validated AUTH-2 main cut. Old controls/order remain unchanged.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = 'fbac4c37910ed07b2baa516e1a5c8d7f329086de'


def reviewed_predecessor(root, path):
    records = json.loads((ROOT/'docs/flora-runtime/et-vis2-659/Owner-Evolution.json').read_text())
    record = records[path]
    before = subprocess.check_output(['git', 'show', BASE+':'+path], cwd=ROOT)
    assert sha256(before).hexdigest() == record['before_sha256']
    current = (Path(root)/path).read_bytes()
    if current == before:
        return before
    assert sha256(current).hexdigest() == record['reviewed_sha256'], 'Unreviewed ET-VIS owner change: '+path
    for addition in record['literal_additions']:
        raw = addition.encode()
        assert current.count(raw) == 1, 'Exactly one additive preview binding is required'
        current = current.replace(raw, b'', 1)
    assert current == before, 'An existing dispatcher, source boundary or authority control changed: '+path
    return before


def validate(root=ROOT):
    for path in ('cios/applications/flora/web/app.py', 'cios/applications/flora/public_routes.py'):
        reviewed_predecessor(root, path)
    return {'original_owners': 2, 'production_controls_changed': 0, 'comparison': 'full-byte predecessor equality after three exact additions'}
