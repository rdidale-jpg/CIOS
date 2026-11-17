"""Narrow F2 compatibility check for two historically byte-pinned dispatchers.

All previous statements, imports, decorators, functions and their order remain
exact AST matches. Only one exact new guard at its specified anchor is allowed.
AUTH-1 separately permits one exactly pinned security-store safety repair,
verified against its preserved before-cut. This is test assurance, not runtime
permission or a baseline/signature refresh.
"""
import ast
import subprocess

BASE = '98fcab91aa94180b11c41c60f4cf7e4d4ad39e40'
GUARDS = {
    'cios/applications/flora/security_web.py': ('private_read', '''
if path in {'/industries/banking','/enterprises/lloyds'}:
    from .financial_intelligence.analyst import authorise_request
    return authorise_request(handler.path,headers=handler.headers)
''', "path=parsed.path"),
    'cios/applications/flora/visual_streams.py': ('render', '''
if 'analysis'in query:
    from .financial_intelligence.analyst import selection
    ctx,run_id=selection(path,query)
    return panels(ctx,headers,financial_run_id=run_id)
''', 'from .visual_panels import render as panels'),
}


def dump(node): return ast.dump(node,include_attributes=False)


def assert_owner_compatible(root,path,expected):
    actual=(root/path).read_bytes()
    if actual==expected:
        return
    if path=='cios/applications/flora/security_store.py':
        from tools.research.auth1_quality import assert_store_evolution
        assert_store_evolution(root,path,expected)
        return
    from tools.research.rud1_compatibility import assert_evolution
    import json
    from tools.research.rud1_compatibility import ROOT
    changes=json.loads((ROOT/'docs/flora-runtime/rud1-648/Owner-Evolution.json').read_text())
    ux=ROOT/'docs/flora-runtime/uxr1-650/Owner-Evolution.json'
    if ux.exists():changes.update(json.loads(ux.read_text()))
    if path in changes:
        assert_evolution(root, path, expected)
        return
    assert path in GUARDS, 'No F2 exception for this protected owner: '+path
    baseline=subprocess.check_output(['git','show',BASE+':'+path],cwd=root)
    assert baseline==expected, 'Historical owner must match the verified F1 cut'
    name,guard_text,anchor_text=GUARDS[path]
    tree=ast.parse(actual)
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name]
    assert len(functions)==1
    fn=functions[0]
    guard=ast.parse(guard_text).body[0];anchor=ast.parse(anchor_text).body[0]
    positions=[i for i,node in enumerate(fn.body) if dump(node)==dump(guard)]
    assert len(positions)==1, 'Exactly the reviewed F2 guard is required'
    index=positions[0]
    assert index>0 and dump(fn.body[index-1])==dump(anchor), 'F2 guard moved before the existing authority anchor'
    del fn.body[index]
    assert dump(tree)==dump(ast.parse(expected)), 'A previous owner statement or contract changed'
