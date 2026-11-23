"""Read-only integration integrity and exact rollback proof; no live services."""
import ast
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[3]
BASE = '9822c883f90bd1bff1e1eb4d6bc284c003e92b25'
RECOVERY = 'e9daf762131c1e70cf83bebca5c811c56f4138d9'


def git(*args, **kwargs):
    return subprocess.check_output(['git', *args], cwd=ROOT, **kwargs)


def original(revision, path):
    return git('show', revision + ':' + path)


def function(raw, name):
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.dump(node, include_attributes=False)


head = git('rev-parse', 'HEAD').decode().strip()
assert not git('status', '--porcelain'), 'Commit the complete reviewable candidate before validation'
assert git('merge-base', BASE, head).decode().strip() == BASE
changed = git('diff', '--name-only', BASE, head).decode().splitlines()
protected = ('enterprise-knowledge/', 'docs/architecture/decisions/',
             'cios/applications/flora/financial_intelligence/', 'cios/applications/flora/research_intelligence/',
             'cios/applications/flora/security', 'cios/applications/flora/supabase',
             'cios/applications/flora/access', 'cios/applications/flora/public_routes',
             'cios/applications/flora/offers', 'cios/applications/flora/pipeline',
             'cios/applications/flora/seller_development')
assert not any(path.startswith(protected) for path in changed)
for path in ('tools/ci/flora_ci.py', 'tools/ci/flora-baseline-v1.json',
             'cios/applications/flora/design_system.py', 'cios/applications/flora/design_assets/design.css'):
    assert original(BASE, path) == (ROOT / path).read_bytes(), path
assets = [p for p in git('ls-tree', '-r', '--name-only', BASE, 'cios/applications/flora').decode().splitlines()
          if Path(p).suffix.lower() in {'.webp', '.png', '.jpg', '.jpeg', '.avif', '.svg'}]
for path in assets:
    assert original(BASE, path) == (ROOT / path).read_bytes(), path
assert not any(path.startswith('cios/applications/flora/') and Path(path).suffix in {'.webp','.png','.jpg','.svg'} for path in changed)
reused = ['cios/applications/flora/lloyds_twin_visual.py',
          'cios/applications/flora/visual_stream_assets/lloyds-twin.css']
for path in reused:
    assert original(RECOVERY, path) == (ROOT / path).read_bytes(), path
path = 'cios/applications/flora/visual_stream_assets/lloyds-twin.js'
assert original(RECOVERY, path).decode().replace("      if (panel) select('#' + panel.id);", "      select(panel ? '#' + panel.id : links[0].hash);") == (ROOT / path).read_text()
path = 'cios/applications/flora/visual_panels.py'
for name in ('_trail', '_top', '_enterprise_arrival'):
    assert function(original(BASE, path), name) == function((ROOT / path).read_bytes(), name), name
# Reconstruct the original tree in a private index. The real checkout/index is untouched.
with TemporaryDirectory() as scratch:
    env = dict(os.environ, GIT_INDEX_FILE=str(Path(scratch) / 'index'))
    git('read-tree', head, env=env)
    patch = git('diff', '--binary', BASE, head)
    subprocess.run(['git','apply','--cached','--reverse','--binary'],input=patch,cwd=ROOT,env=env,check=True)
    tree = git('write-tree', env=env).decode().strip()
assert tree == git('rev-parse', BASE + '^{tree}').decode().strip()
links = []
for doc in Path(__file__).parent.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)', doc.read_text()):
        if target.startswith(('http:', 'https:', '#')):
            continue
        assert (doc.parent / target.split('#')[0]).exists(), (doc, target)
        links.append(target)
print(json.dumps({'head':head,'base':BASE,'recovered_from':RECOVERY,'changed_files':changed,
                  'protected_paths_unchanged':True,'original_runtime_images_unchanged':len(assets),
                  'exact_712_reuse':reused,'726_navigation_functions_unchanged':True,
                  'reverse_tree':tree,'rollback_matches_baseline':True,'local_links_checked':len(links),
                  'production_or_canonical_writes':0,'paid_calls':0},indent=2))
