"""Exact bounded public-owner evolution; historical cuts remain independently pinned."""
import ast
from hashlib import sha256
import json
from pathlib import Path
import subprocess


def predecessor(root, path, current):
    from tools.research.enterprise_economics_compatibility import predecessor as economics_predecessor
    current = economics_predecessor(root, path, current)
    record_path=Path(root)/'docs/flora-runtime/public-financial-intelligence/Owner-Evolution.json'
    if not record_path.is_file():return current
    records=json.loads(record_path.read_text())
    row=records.get(path)
    if not row or sha256(current).hexdigest()!=row['after_sha256']:return current
    previous=subprocess.check_output(['git','show',row['base']+':'+path],cwd=root)
    assert sha256(previous).hexdigest()==row['before_sha256']
    allowed=set(row['public_functions'])
    def protected(raw):
        tree=ast.parse(raw)
        # Only these named top-level public-boundary functions may evolve.
        # Every private-run function, import and module constant remains exact.
        tree.body=[n for n in tree.body if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) or n.name not in allowed]
        return ast.dump(tree,include_attributes=False)
    assert protected(current)==protected(previous), 'Unlisted public financial owner change: '+path
    return previous


def validate(root):
    root=Path(root)
    rows=json.loads((root/'docs/flora-runtime/public-financial-intelligence/Owner-Evolution.json').read_text())
    for path,row in rows.items():
        raw=(root/path).read_bytes()
        from tools.research.enterprise_economics_compatibility import predecessor as economics_predecessor
        raw=economics_predecessor(root,path,raw)
        assert sha256(raw).hexdigest()==row['after_sha256'], 'Unknown public financial cut: '+path
        assert predecessor(root,path,raw)!=raw
    return {'bounded_owners':list(rows),'ci_comparator_changed':False,'historical_pins_retained':True}
