"""Finite change-scope, documentation, asset preservation and reverse-tree check."""
import json,os,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE='3d9bdb84e64908a3a99dea1f857fecb57b835b88'
def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=ROOT,**kwargs)
def run():
    sha=git('rev-parse','HEAD',text=True).strip()
    changed=git('diff','--name-only',BASE,sha,text=True).splitlines()
    allowed={'.github/workflows/flora-enterprise-economics-a1.yml','cios/applications/flora/lloyds_gold.py','cios/applications/flora/visual_stream_assets/lloyds-gold.css','docs/product/flora-experience/main-canvas/browser.py','tests/test_flora_lloyds_ceo.py','tests/test_flora_lloyds_gold.py','tests/test_flora_lloyds_gold_v2.py','tests/test_flora_main_canvas.py','tests/test_flora_lloyds_experience_completion.py'}
    assert all(p in allowed or p.startswith('docs/flora-runtime/lloyds-experience-completion/') for p in changed),changed
    assert not git('diff','--name-only',BASE,sha,'--','enterprise-knowledge','architecture/decisions','tools/ci/flora_ci.py','tools/ci/flora-baseline-v1.json')
    art=git('diff','--name-only',BASE,sha,'--','*.webp','*.png','*.svg','*.jpg',text=True).splitlines()
    assert all(p.startswith('docs/flora-runtime/lloyds-experience-completion/previews/') for p in art)
    missing=[]
    for file in (ROOT/'docs/flora-runtime/lloyds-experience-completion').glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
            if not target.startswith(('http:','https:','#','/')) and not (file.parent/target.split('#')[0]).exists():missing.append(target)
    assert not missing,missing
    with tempfile.TemporaryDirectory(prefix='experience-reverse-') as temp:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(temp)/'index'))
        subprocess.run(['git','read-tree',sha],cwd=ROOT,env=env,check=True)
        patch=git('diff','--binary',BASE,sha)
        subprocess.run(['git','apply','--cached','--reverse','--binary','-'],cwd=ROOT,env=env,input=patch,check=True)
        reverse=git('write-tree',env=env,text=True).strip()
    base_tree=git('rev-parse',BASE+'^{tree}',text=True).strip();assert reverse==base_tree
    result={'sha':sha,'base':BASE,'changed_files':changed,'runtime_files':[p for p in changed if p.startswith('cios/')],'source_artwork_security_financial_owners_unchanged':True,'documentation_links_valid':True,'reverse_tree':reverse,'base_tree':base_tree,'rollback_exact':True}
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
