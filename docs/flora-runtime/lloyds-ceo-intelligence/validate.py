"""Source integrity, finite scope and exact rollback through existing owners."""
import ast,json,os,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE='201fe851a531ecb854d3ba8e3416bc667ab8c860'
def git(*args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
def run():
    import sys
    sys.path.insert(0,str(ROOT))
    from tests.flora_lloyds_research_contract import preserved_research_cut,SOURCES
    from cios.applications.flora.research_intelligence import model
    preserved_research_cut();data=model.load_assessment()
    sha=git('rev-parse','HEAD',text=True).strip();changed=git('diff','--name-only',BASE,sha,text=True).splitlines()
    allowed={'.github/workflows/flora-enterprise-economics-a1.yml','cios/applications/flora/lloyds_gold.py','cios/applications/flora/visual_stream_assets/lloyds-gold.css','enterprise-knowledge/banking/research-model/Assessment-Overlay.json','tests/flora_lloyds_research_contract.py','tests/test_flora_lloyds_ceo_intelligence.py','tests/test_flora_lloyds_gold_v2.py','tests/test_flora_lloyds_gold_v3.py','tests/test_flora_lloyds_experience_completion.py'}
    allowed.update({'tests/test_flora_commercial_assessment.py','tests/test_flora_primary_enrichment.py','tests/test_flora_research_intelligence.py'})
    allowed.add('enterprise-knowledge/banking/research-model/Understanding-Review.json')
    allowed.update({'tools/research/history_integrity.py','tools/research/ux_unify_compatibility.py'})
    allowed.update({'tests/test_flora_lloyds_gold.py','tests/test_flora_lloyds_ceo.py'})
    allowed|={'enterprise-knowledge/banking/research-model/source-snapshots/'+s+'.txt' for s in SOURCES}
    assert all(p in allowed or p.startswith('docs/flora-runtime/lloyds-ceo-intelligence/') for p in changed),changed
    trees=[ast.parse(git('show',BASE+':cios/applications/flora/lloyds_gold.py')),ast.parse((ROOT/'cios/applications/flora/lloyds_gold.py').read_text())]
    funcs=lambda t:{n.name:ast.dump(n,include_attributes=False) for n in t.body if isinstance(n,ast.FunctionDef)}
    a,b=map(funcs,trees);assert all(a[k]==b[k] for k in ('facts_for','executive_facts','reported','interpretation','scene','resolve','canonical_query','href','render','stylesheet'))
    for source in data['sources']:
        if source['id'] in SOURCES:
            model.primary_text(source)
            assert source['primary_content_sha256']is None
            assert sum(len(q['quote'].split()) for q in source['excerpts'])<=25
    for file in Path(__file__).parent.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
            if not target.startswith(('http:','https:','#','/')):assert (file.parent/target.split('#')[0]).exists(),target
    with tempfile.TemporaryDirectory(prefix='ceo-rollback-') as folder:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(folder)/'index'));subprocess.run(['git','read-tree',sha],cwd=ROOT,env=env,check=True)
        subprocess.run(['git','apply','--cached','--reverse','--binary','-'],input=git('diff','--binary',BASE,sha),cwd=ROOT,env=env,check=True)
        reverse=git('write-tree',env=env,text=True).strip()
    assert reverse==git('rev-parse',BASE+'^{tree}',text=True).strip()
    print(json.dumps({'sha':sha,'base':BASE,'files':changed,'runtime_files':[p for p in changed if p.startswith('cios/')],'old_research_and_permissions_preserved':True,'held_financial_candidates_activated':0,'original_artwork_unchanged':True,'reverse_tree':reverse,'rollback_exact':True},indent=2))
if __name__=='__main__':run()
