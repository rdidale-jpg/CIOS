"""Finite v3 scope, original-owner preservation and exact reverse-tree check."""
import ast,json,os,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE='08763fca342fcaf67c37f261948d8a8c9642d2c3'
def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=ROOT,**kwargs)
def run():
    sha=git('rev-parse','HEAD',text=True).strip()
    changed=git('diff','--name-only',BASE,sha,text=True).splitlines()
    allowed={'.github/workflows/flora-validation.yml','.github/workflows/flora-enterprise-economics-a1.yml','cios/applications/flora/lloyds_gold.py','cios/applications/flora/visual_stream_assets/lloyds-gold.css','tests/test_flora_lloyds_gold_v3.py','tests/test_flora_lloyds_experience_completion.py','tests/test_flora_main_canvas.py','tests/test_flora_gold_reconciliation.py','tests/flora_f2_owner_contract.py'}
    assert all(p in allowed or p.startswith('docs/flora-runtime/lloyds-gold-v3/') for p in changed),changed
    old=git('show',BASE+':.github/workflows/flora-validation.yml')
    actual=(ROOT/'.github/workflows/flora-validation.yml').read_bytes()
    assert old.count(b'timeout-minutes: 30')==1
    assert actual==old.replace(b'timeout-minutes: 30',b'timeout-minutes: 45',1)
    trees=[ast.parse(git('show',BASE+':cios/applications/flora/lloyds_gold.py')),ast.parse((ROOT/'cios/applications/flora/lloyds_gold.py').read_text())]
    funcs=lambda t:{n.name:ast.dump(n,include_attributes=False) for n in t.body if isinstance(n,ast.FunctionDef)}
    a,b=map(funcs,trees)
    assert all(a[k]==b[k] for k in ('facts_for','executive_facts','reported','interpretation','scene','resolve','canonical_query','render','stylesheet'))
    for file in Path(__file__).parent.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
            if not target.startswith(('http:','https:','#','/')):assert (file.parent/target.split('#')[0]).exists(),target
    with tempfile.TemporaryDirectory(prefix='v3-reverse-') as folder:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(folder)/'index'))
        subprocess.run(['git','read-tree',sha],cwd=ROOT,env=env,check=True)
        subprocess.run(['git','apply','--cached','--reverse','--binary','-'],cwd=ROOT,env=env,input=git('diff','--binary',BASE,sha),check=True)
        reverse=git('write-tree',env=env,text=True).strip()
    baseline=git('rev-parse',BASE+'^{tree}',text=True).strip();assert reverse==baseline
    print(json.dumps({'sha':sha,'base':BASE,'files':changed,'runtime_files':[p for p in changed if p.startswith('cios/')],'protected_owners_and_original_artwork_unchanged':True,'workflow_budget_only':True,'rollback_exact':True,'reverse_tree':reverse},indent=2))
if __name__=='__main__':run()
