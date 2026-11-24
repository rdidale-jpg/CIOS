"""Scope, references, source inventory, capture hashes and exact reverse-tree proof."""
from hashlib import sha256
import json,os,re,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from importlib.util import spec_from_file_location,module_from_spec
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE='eaca26f2b31c3c9227bb797d60f7d3492a8313d1'
def git(*args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
allowed={'.github/workflows/flora-enterprise-economics-a1.yml','cios/applications/flora/lloyds_gold.py',
 'cios/applications/flora/visual_stream_assets/lloyds-gold.css','cios/applications/flora/living_enterprise_preview.py',
 'cios/applications/flora/public_routes.py','cios/applications/flora/web/app.py','tests/test_flora_lloyds_gold.py',
 'tests/test_flora_living_enterprise_preview.py','tools/research/ux_unify_compatibility.py'}
files=git('diff','--name-only',BASE,'HEAD',text=True).splitlines()
assert files and all(p in allowed or p.startswith('docs/flora-runtime/lloyds-gold-standard/') for p in files)
assert sorted(HERE.joinpath('Changed-Files.txt').read_text().splitlines())==sorted(files)
spec=spec_from_file_location('gold_audit',HERE/'audit.py');module=module_from_spec(spec);spec.loader.exec_module(module)
assert module.report()==json.loads((HERE/'Inventory.json').read_text())
links=0
for path in HERE.glob('*.md'):
 for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
  if '://' in link or link.startswith('#'):continue
  target=path.parent/link.split('#')[0].split('?')[0]
  assert target.exists(),(path.name,link)
  links+=1
captures=0
for phase in ('before','after'):
 proof=json.loads((HERE/('Browser-'+phase+'.json')).read_text())
 for name,digest in proof['screenshots'].items():
  assert sha256((HERE/'previews'/name).read_bytes()).hexdigest()==digest;captures+=1
 if phase=='after':
  for path,digest in proof['runtime_hashes'].items():assert sha256((ROOT/path).read_bytes()).hexdigest()==digest
# Isolated index, no checkout/branch/ref change and no data reversal needed.
with tempfile.TemporaryDirectory(prefix='flora-gold-rollback-') as temp:
 env=dict(os.environ,GIT_INDEX_FILE=temp+'/index')
 subprocess.run(['git','read-tree','HEAD'],cwd=ROOT,env=env,check=True)
 diff=git('diff','--binary',BASE,'HEAD')
 subprocess.run(['git','apply','--cached','--reverse','--binary'],input=diff,cwd=ROOT,env=env,check=True)
 restored=git('write-tree',env=env,text=True).strip();expected=git('rev-parse',BASE+'^{tree}',text=True).strip()
 assert restored==expected
print(json.dumps({'head':git('rev-parse','HEAD',text=True).strip(),'files':len(files),'links':links,'captures':captures,'rollback_tree':restored,'source_authority_delta':False,'passed':True},indent=2))
