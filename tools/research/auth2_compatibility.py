"""Individually pinned AUTH-2 owner evolution, separate from CI comparators.

Retain every historical cut and run its original checks against the immediate
AUTH-1 predecessor. Current code must match an exact reviewed SHA256 and only
the listed function bodies may change. Unknown before/after cuts fail closed.
"""
import ast
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE='7b056b21cd5d824bc4359b4e1ed49a1673a7f5fc'
ALLOWED={
 'cios/applications/flora/security_store.py': {'_token','enroll','login','_supabase_login','select','logout','resolve'},
 'cios/applications/flora/security_web.py': {'page','auth_get','auth_post'},
 'cios/applications/flora/security_readiness.py': {'inspect_security_storage'},
 'cios/applications/flora/visual_panels.py': {'render','_nationwide_service','_authorised_nationwide'},
 'cios/applications/flora/financial_intelligence/candidate_analytics.py': {'public_nationwide_projection'},
}


def old(path):
    return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)


def reviewed_predecessor(root,path):
    current=(Path(root)/path).read_bytes()
    if path not in ALLOWED:
        return current
    previous=old(path)
    if current==previous:
        return current
    record=json.loads((ROOT/'docs/flora-runtime/auth2-655/Owner-Evolution.json').read_text())[path]
    assert record['base']==BASE
    assert sha256(previous).hexdigest()==record['before_sha256']
    assert sha256(current).hexdigest()==record['reviewed_sha256'], 'Unreviewed AUTH-2 owner change: '+path
    def retained(raw):
        tree=ast.parse(raw)
        for node in ast.walk(tree):
            if hasattr(node,'body')and isinstance(node.body,list):
                node.body=[n for n in node.body if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))or n.name not in ALLOWED[path]]
        return ast.dump(tree,include_attributes=False)
    assert retained(current)==retained(previous), 'Unlisted AUTH-2 control changed: '+path
    return previous


def validate():
    for path in ALLOWED:
        assert reviewed_predecessor(ROOT,path)==old(path)
    from tools.research.auth1_quality import validate as historical
    report=historical()
    assert report['original_visual_files']==51
    from cios.applications.flora.financial_intelligence.candidate_analytics import public_nationwide_projection
    projection=public_nationwide_projection()
    assert len(projection['measurements'])==8
    assert [r['value']for r in projection['results']]==['2026','1490']
    return {'base':BASE,'bounded_owner_changes':{k:sorted(v)for k,v in ALLOWED.items()},
            'original_artwork':51,'public_measurements':8,'source_permissions_added':0,'historical_quality':report}


if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT))
    print(json.dumps(validate(),indent=2))
