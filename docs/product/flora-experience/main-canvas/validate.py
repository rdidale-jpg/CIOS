"""Exact canvas scope, immutable source/Left, browser evidence and rollback."""
import argparse,ast,json,os,re,subprocess,sys,tempfile
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
BASE='cc8d93fe7183fdd86fd4c4e81907a2a0764227a5'
ALLOWED={'.github/workflows/flora-enterprise-economics-a1.yml','cios/applications/flora/lloyds_gold.py',
 'cios/applications/flora/visual_stream_assets/lloyds-gold.css','docs/product/flora-experience/FLORA-Experience-Contract-v1.0.md',
 'docs/product/flora-experience/Main-Canvas-Interaction-Contract.md','tests/test_flora_lloyds_ceo.py',
 'tests/test_flora_main_canvas.py','tools/ci/flora_eai2_preview.cjs','docs/product/flora-experience/lloyds-ceo/browser.py'}
def git(*args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
def validate(browser=None):
 paths=git('diff','--name-only',BASE,'HEAD',text=True).splitlines()
 assert sorted(paths)==(HERE/'Changed-Files.txt').read_text().splitlines()
 assert all(p in ALLOWED or p.startswith('docs/product/flora-experience/main-canvas/')for p in paths),paths
 raw=git('show',BASE+':cios/applications/flora/lloyds_gold.py');current=(ROOT/'cios/applications/flora/lloyds_gold.py').read_bytes()
 funcs=lambda text:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
 before,after=funcs(raw),funcs(current)
 for name in ('facts_for','reported','interpretation','scene','resolve','href','render','stylesheet'):assert before[name]==after[name],name
 images=[];research=0
 for path in git('ls-tree','-r','--name-only',BASE,'enterprise-knowledge','cios/applications/flora',text=True).splitlines():
  original=path.startswith('enterprise-knowledge/')
  artwork=Path(path).suffix.lower()in {'.png','.jpg','.jpeg','.webp','.svg','.avif'}
  if original or artwork:
   assert (ROOT/path).read_bytes()==git('show',BASE+':'+path),path
   research+=original
   if artwork:images.append({'path':path,'sha256':sha256((ROOT/path).read_bytes()).hexdigest()})
 for name in ('security_store.py','security_web.py','public_routes.py','visual_streams.py','research_intelligence/source_import.py','financial_intelligence/candidate_analytics.py'):
  path='cios/applications/flora/'+name;assert (ROOT/path).read_bytes()==git('show',BASE+':'+path),path
 links=0
 for file in HERE.glob('*.md'):
  for link in re.findall(r'\]\(([^)]+)\)',file.read_text()):
   if '://'in link or link.startswith('#'):continue
   assert (file.parent/link.split('#')[0]).exists(),(file.name,link);links+=1
 captures=0
 for phase in ('before','after'):
  proof=json.loads((HERE/f'Browser-{phase}.json').read_text())
  assert len(proof['devices'])==4
  for file,digest in proof['screenshots'].items():assert sha256((HERE/'previews'/file).read_bytes()).hexdigest()==digest;captures+=1
  if phase=='after':
   for file,digest in proof['runtime_hashes'].items():assert sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
   assert proof['no_javascript']and proof['withdrawal_history_reload_print_accessibility']
   assert all(d['physical_hits']for d in proof['devices'])
   assert all(not r['underlined']and not r['small']and not r['bare']and not r['nested']for r in proof['audits'].values())
 if browser:
  proof=json.loads((browser/'Browser-after.json').read_text());assert proof['sha']==git('rev-parse','HEAD',text=True).strip()
  for file,digest in proof['runtime_hashes'].items():assert sha256((ROOT/file).read_bytes()).hexdigest()==digest
 with tempfile.TemporaryDirectory(prefix='canvas-rollback-')as temp:
  env=dict(os.environ,GIT_INDEX_FILE=temp+'/index');subprocess.run(['git','read-tree','HEAD'],cwd=ROOT,env=env,check=True)
  subprocess.run(['git','apply','--cached','--reverse','--binary'],input=git('diff','--binary',BASE,'HEAD'),cwd=ROOT,env=env,check=True)
  restored=git('write-tree',env=env,text=True).strip();assert restored==git('rev-parse',BASE+'^{tree}',text=True).strip()
 return {'head':git('rev-parse','HEAD',text=True).strip(),'files':len(paths),'links':links,'captures':captures,
  'research_files_unchanged':research,'original_artwork_files_unchanged':len(images),'source_and_permission_delta':False,
  'rollback_tree':restored,'passed':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--browser',type=Path);args=p.parse_args();print(json.dumps(validate(args.browser),indent=2))
