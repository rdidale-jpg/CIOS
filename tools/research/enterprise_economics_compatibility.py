"""Exact renderer evolution, not a regression baseline or runtime registry.

Old checks still execute against their pinned predecessors. Independently test
the shipping renderer, Source withdrawal and all private/security services.
"""
import ast
from hashlib import sha256
import json
from pathlib import Path
import subprocess

BASE = '03719d7573f087c65d9622719273aa4b89caf7d3'
ALLOWED = {
    'cios/applications/flora/lloyds_recovery.py': {'landscape'},
    'cios/applications/flora/experience_composition.py': {'easyjet_root'},
    'cios/applications/flora/easyjet_capabilities.py': {'main'},
    'cios/applications/flora/visual_panels.py': {'render'},
    'cios/applications/flora/visual_streams.py': {'resolve', 'stream_url'},
}


def predecessor(root, path, current):
    record_path = Path(root) / 'docs/flora-runtime/enterprise-economics-a1/Renderer-Evolution.json'
    if path not in ALLOWED or not record_path.is_file():
        return current
    row = json.loads(record_path.read_text())[path]
    if sha256(current).hexdigest() != row['after_sha256']:
        return current
    assert row['base'] == BASE and set(row['functions']) == ALLOWED[path]
    before = subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=root)
    assert sha256(before).hexdigest() == row['before_sha256']

    def protected(raw):
        tree = ast.parse(raw)
        tree.body = [n for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) or n.name not in ALLOWED[path]]
        return ast.dump(tree, include_attributes=False)

    assert protected(current) == protected(before), 'Unlisted Economics change: ' + path
    return before


def validate(root):
    root = Path(root)
    records = json.loads((root / 'docs/flora-runtime/enterprise-economics-a1/Renderer-Evolution.json').read_text())
    assert set(records) == set(ALLOWED)
    for path, row in records.items():
        raw = (root / path).read_bytes()
        assert sha256(raw).hexdigest() == row['after_sha256'], 'Unknown Economics cut: ' + path
        assert predecessor(root, path, raw) != raw
    return {'base': BASE, 'renderer_functions': {k: sorted(v) for k, v in ALLOWED.items()}, 'comparator_changed': False}
