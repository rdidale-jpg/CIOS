"""Bounded AUTH-1 owner-change audit; no authority or data writes."""
import ast
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
BASE='836a4c29015c59117b873e6324c9618f7eb41930'
CHANGES={'cios/applications/flora/security_store.py':{'transaction'},
 'cios/applications/flora/protected_storage.py':{'recover'},
 'cios/applications/flora/security_operator.py':{'main'}}


def cut(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)


def assert_store_evolution(root,path,previous):
    """One reviewed security-owner evolution; not a comparator exemption."""
    row=json.loads((ROOT/'docs/flora-runtime/auth1-652/Owner-Compatibility.json').read_text())
    assert path==row['path']=='cios/applications/flora/security_store.py'
    assert row['base_sha']==BASE
    assert sha256(cut(path)).hexdigest()==row['before_sha256']
    assert sha256(previous).hexdigest()==row['before_sha256'],'Unknown historical security owner'
    from tools.research.auth2_compatibility import reviewed_predecessor
    assert sha256(reviewed_predecessor(root,path)).hexdigest()==row['reviewed_sha256'],'Unreviewed security owner change'


def unchanged_definitions(raw,allowed,*,operator_current=False):
    tree=ast.parse(raw)
    if operator_current:
        current=ast.parse("if __name__ == '__main__':\n raise SystemExit(main())").body[0]
        original=ast.parse("if __name__ == '__main__':\n main()").body[0]
        assert ast.dump(tree.body[-1],include_attributes=False)==ast.dump(current,include_attributes=False)
        tree.body[-1]=original
    for node in ast.walk(tree):
        if hasattr(node,'body')and isinstance(node.body,list):
            node.body=[n for n in node.body if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))or n.name not in allowed]
    return ast.dump(tree,include_attributes=False)


def validate():
    path='cios/applications/flora/security_store.py'
    assert_store_evolution(ROOT,path,cut(path))
    for path,allowed in CHANGES.items():
        from tools.research.auth2_compatibility import reviewed_predecessor
        assert unchanged_definitions(cut(path),allowed)==unchanged_definitions(reviewed_predecessor(ROOT,path),allowed,operator_current=path.endswith('/security_operator.py')),path
    untouched=['cios/applications/flora/security.py','cios/applications/flora/security_web.py','cios/applications/flora/access.py',
        'cios/applications/flora/pilot_auth.py','cios/applications/flora/storage.py','cios/applications/flora/web/app.py',
        'cios/applications/flora/financial_intelligence/candidate_analytics.py',
        'render.yaml','tools/ci/flora_ci.py','tools/ci/flora-baseline-v1.json']
    checked=[]
    for path in untouched:
        assert reviewed_predecessor(ROOT,path)==cut(path),path
        checked.append(path)
    from tools.research.uxr1_quality import validate as prior_quality
    existing=prior_quality()
    return {'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'base':BASE,
        'bounded_existing_function_changes':CHANGES_TO_JSON,'unchanged_control_files':checked,
        'original_visual_files':existing['original_asset_files'],'retained_research_files':178,
        'new_authority_producers':0,'production_mutations':0,'live_Render_authentication':'UNKNOWN'}
CHANGES_TO_JSON={path:sorted(names)for path,names in CHANGES.items()}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
