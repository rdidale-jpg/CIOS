"""Exact reviewed scope, existing owners, original artwork and reversible tree."""
import json,os,re,subprocess,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE='8be67e3d49ad17886c1cc14da3c646271b21017e'
sys.path.insert(0,str(ROOT))
def git(*args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
def run():
    from tools.research.public_financial_compatibility import validate
    from tools.research.history_integrity import verify_history
    from tests.flora_lloyds_research_contract import preserved_research_cut
    from cios.applications.flora.financial_intelligence.public_statements import economic_projection
    validate(ROOT);verify_history(ROOT);preserved_research_cut()
    sha=git('rev-parse','HEAD',text=True).strip();changed=git('diff','--name-only',BASE,sha,text=True).splitlines()
    forbidden=('cios/applications/flora/security','cios/applications/flora/supabase','cios/domain/','cios/services/','architecture/decisions/','tools/ci/flora_ci.py','tools/ci/flora-baseline-v1.json','render','requirements')
    assert not [p for p in changed if p.startswith(forbidden)]
    runtime={'cios/applications/flora/'+p for p in ('lloyds_gold.py','visual_stream_assets/lloyds-gold.css','financial_intelligence/candidate_analytics.py','financial_intelligence/public_statements.py','research_intelligence/source_import.py')}
    assert {p for p in changed if p.startswith('cios/')}==runtime
    protected=('cios/applications/flora/financial_intelligence/run_store.py','cios/applications/flora/security_store.py','cios/applications/flora/security_web.py','cios/applications/flora/supabase_identity.py','cios/applications/flora/public_routes.py','cios/applications/flora/visual_streams.py','cios/applications/flora/intelligence_presentation.py','tools/ci/flora_ci.py','tools/ci/flora-baseline-v1.json')
    assert not git('diff',BASE,sha,'--',*protected)
    art=git('ls-tree','-r','--name-only',BASE,'cios/applications/flora/visual_stream_assets','cios/applications/flora/easyjet_art',text=True).splitlines()
    count=0
    for path in art:
        if Path(path).suffix.lower() in {'.png','.jpg','.jpeg','.webp','.avif','.svg'}:
            assert (ROOT/path).read_bytes()==git('show',BASE+':'+path);count+=1
    q,h=map(economic_projection,('lloyds-q3','lloyds-h1'));assert len(q['lines'])==35 and len(h['lines'])==74
    assert q['bridges']['statutory-earnings']['value']=='6625'
    for path in Path(__file__).parent.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if not target.startswith(('https:','http:','#','/')):assert (path.parent/target.split('#')[0]).exists(),target
    with tempfile.TemporaryDirectory(prefix='facts-rollback-') as folder:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(folder)/'index'));subprocess.run(['git','read-tree',sha],cwd=ROOT,env=env,check=True)
        subprocess.run(['git','apply','--cached','--reverse','--binary','-'],input=git('diff','--binary',BASE,sha),cwd=ROOT,env=env,check=True)
        tree=git('write-tree',env=env,text=True).strip()
    assert tree==git('rev-parse',BASE+'^{tree}',text=True).strip()
    print(json.dumps({'sha':sha,'base':BASE,'files':changed,'runtime_files':sorted(runtime),'original_artworks_verified':count,'typed_source_facts':109,'new_private_runs':0,'canonical_writes':0,'comparator_changed':False,'rollback_exact':True,'rollback_tree':tree},indent=2))
if __name__=='__main__':run()
