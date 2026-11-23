"""Bounded implementation inventory, protected ownership and exact source rollback."""
import ast
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
BASE='97d316c640c96d99c2301819f8aac00b3b9c1398'
DESIGN='da1a6c7b5e4b95e85ef2de3697bc8c506368192c'
PREFIX='docs/flora-runtime/living-enterprise-preview/'
ALLOWED={'.github/workflows/flora-enterprise-economics-a1.yml',
 'cios/applications/flora/living_enterprise_preview.py','cios/applications/flora/lloyds_flagship.py',
 'cios/applications/flora/visual_stream_assets/living-enterprise-preview.css',
 'cios/applications/flora/visual_stream_assets/living-enterprise-preview.js',
 'cios/applications/flora/visual_panels.py','cios/applications/flora/public_routes.py',
 'cios/applications/flora/web/app.py','tests/test_flora_living_enterprise_preview.py',
 'tests/test_flora_accepted_ux_recovery.py','tools/research/eei2b_compatibility.py'}

def git(*args,env=None,input=None):
    return subprocess.check_output(['git',*args],cwd=ROOT,env=env,input=input)


def without_functions(raw,names):
    tree=ast.parse(raw);tree.body=[node for node in tree.body if not (isinstance(node,ast.FunctionDef) and node.name in names)]
    return ast.dump(tree,include_attributes=False)


def validate():
    git('merge-base','--is-ancestor',BASE,'HEAD')
    paths=sorted(set(git('diff','--name-only',BASE).decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines()))
    assert paths and all(path in ALLOWED or path.startswith(PREFIX) for path in paths),paths
    assert not any(path.endswith(('.pdf','.sqlite','.db')) for path in paths)
    assets={}
    for path in git('ls-tree','-r','--name-only',BASE,'cios/applications/flora').decode().splitlines():
        if Path(path).suffix.lower() in {'.jpg','.jpeg','.png','.webp','.svg'}:
            raw=(ROOT/path).read_bytes();assert raw==git('show',BASE+':'+path),path
            assets[path]=sha256(raw).hexdigest()
    for path,names in [('cios/applications/flora/visual_panels.py',{'_frame'}),('cios/applications/flora/lloyds_flagship.py',{'_facts'})]:
        assert without_functions((ROOT/path).read_bytes(),names)==without_functions(git('show',BASE+':'+path),names),path
    web='cios/applications/flora/web/app.py'
    def protected_web(raw):
        tree=ast.parse(raw)
        tree.body=[node for node in tree.body if not (isinstance(node,ast.FunctionDef) and node.name=='_content_type_for_path')]
        for node in tree.body:
            if isinstance(node,ast.ClassDef) and node.name=='FloraWebHandler':
                node.body=[method for method in node.body if not (isinstance(method,ast.FunctionDef) and method.name in {'do_GET','do_HEAD'})]
        return ast.dump(tree,include_attributes=False)
    assert protected_web((ROOT/web).read_bytes())==protected_web(git('show',BASE+':'+web))
    baseline='tools/ci/flora-baseline-v1.json'
    assert (ROOT/baseline).read_bytes()==git('show',BASE+':'+baseline)
    links=0
    for path in [ROOT/name for name in paths if name.endswith('.md')]:
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            url=urlsplit(target)
            if url.scheme or not url.path:continue
            destination=(path.parent/url.path).resolve()
            assert destination.is_relative_to(ROOT) and destination.exists(),(path,target)
            links+=1
    with TemporaryDirectory(prefix='flora-preview-index-') as temporary:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(temporary)/'index'))
        git('read-tree','HEAD',env=env);git('add','--',*paths,env=env)
        tree=git('write-tree',env=env).decode().strip()
        patch=git('diff','--binary',BASE,tree)
        git('apply','--cached','--reverse','-',env=env,input=patch)
        restored=git('write-tree',env=env).decode().strip()
        assert restored==git('rev-parse',BASE+'^{tree}').decode().strip()
    return {'base':BASE,'design_reference':DESIGN,'checkout':git('rev-parse','HEAD').decode().strip(),
        'changed_files':paths,'changed_file_count':len(paths),'unchanged_images':assets,
        'unchanged_security_comparator_baseline_sha256':sha256((ROOT/baseline).read_bytes()).hexdigest(),
        'protected_frame_and_flagship_functions_unchanged':True,'protected_web_methods_unchanged':True,
        'local_links_checked':links,'reverse_patch_restores_base_tree':restored,
        'source_research_rights_auth_canonical_pipeline_schema_changes':[]}

if __name__=='__main__':
    report=validate()
    if '--check' not in sys.argv:(HERE/'Integrity-Proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('checkout','changed_file_count','local_links_checked','reverse_patch_restores_base_tree')}))
