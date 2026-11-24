"""Exact CEO scope, current browser, source/image history and reverse-tree proof."""
import argparse,ast,importlib.util,json,os,re,subprocess,sys,tempfile
from hashlib import sha256
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT))
BASE='1c13e6962516dbb071b2133f2c1a3de87647e2ac'
APPROVED={
 '.github/workflows/flora-enterprise-economics-a1.yml',
 'cios/applications/flora/lloyds_gold.py','cios/applications/flora/public_routes.py',
 'cios/applications/flora/research_intelligence/source_import.py','cios/applications/flora/visual_stream_assets/lloyds-gold.css',
 'cios/applications/flora/visual_streams.py','cios/applications/flora/web/app.py',
 'docs/flora-runtime/accepted-ux-recovery/browser.py','docs/flora-runtime/living-enterprise-preview/browser.py','docs/flora-runtime/lloyds-gold-standard/browser.py',
 'tests/test_flora_lloyds_ceo.py','tests/test_flora_lloyds_gold.py','tests/test_flora_living_enterprise_preview.py','tests/test_flora_accepted_ux_recovery.py',
 'tests/test_flora_lloyds_flagship.py','tests/test_flora_enterprise_economics_a1.py','tests/test_flora_experience_684.py','tests/test_flora_visual_panels_632.py',
 'tests/test_flora_visual_streams_612.py','tools/ci/flora_vp2_preview.cjs','tools/ci/flora_enterprise_economics_preview.cjs','tools/research/eei2b_compatibility.py','tools/research/ux_unify_compatibility.py','tools/research/history_integrity.py',
 'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.json',
 'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.txt',
}
def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=ROOT,**kwargs)
def validate(browser=None):
 from tools.research.history_integrity import verify_history
 from tools.research.ux_unify_compatibility import CEO_PINS,ceo_predecessor
 spec=importlib.util.spec_from_file_location('ceo_audit',HERE/'audit.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
 assert audit.report()==json.loads((HERE/'Knowledge-Audit.json').read_text())
 files=git('diff','--name-only',BASE,'HEAD',text=True).splitlines()
 assert sorted(files)==sorted((HERE/'Changed-Files.txt').read_text().splitlines())
 assert all(p in APPROVED or p.startswith('docs/product/flora-experience/lloyds-ceo/') for p in files),files
 for path in git('ls-tree','-r','--name-only',BASE,'enterprise-knowledge',text=True).splitlines():assert (ROOT/path).read_bytes()==git('show',BASE+':'+path),path
 assert verify_history(ROOT)['old_review_records_retained']
 for path,digest in CEO_PINS.items():
  current=(ROOT/path).read_bytes();assert sha256(current).hexdigest()==digest
  assert ceo_predecessor(ROOT,path,current)==git('show',BASE+':'+path)
  assert ceo_predecessor(ROOT,path,current+b'changed')==current+b'changed'
 path='cios/applications/flora/research_intelligence/source_import.py'
 old=ast.parse(git('show',BASE+':'+path));new=ast.parse((ROOT/path).read_text())
 new.body=[n for n in new.body if not isinstance(n,ast.FunctionDef)or n.name!='public_enterprise_role']
 assert ast.dump(new,include_attributes=False)==ast.dump(old,include_attributes=False)
 images=0
 for path in git('ls-tree','-r','--name-only',BASE,'cios/applications/flora',text=True).splitlines():
  if Path(path).suffix.lower()not in {'.webp','.jpg','.jpeg','.png','.avif'}:continue
  assert git('show',BASE+':'+path)==(ROOT/path).read_bytes(),path;images+=1
 links=0
 for path in HERE.glob('*.md'):
  for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
   if '://'in link or link.startswith('#'):continue
   assert (path.parent/link.split('#')[0].split('?')[0]).exists(),(path.name,link);links+=1
 captures=0
 for phase in ('before','after'):
  proof=json.loads((HERE/f'Browser-{phase}.json').read_text())
  for name,digest in proof['screenshots'].items():assert sha256((HERE/'previews'/name).read_bytes()).hexdigest()==digest;captures+=1
  if phase=='after':
   for name,digest in proof['runtime_hashes'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 if browser:
  proof=json.loads((browser/'Browser-after.json').read_text())
  assert proof['sha']==git('rev-parse','HEAD',text=True).strip()
  assert proof['withdrawal'] and proof['no_javascript'] and len(proof['devices'])==4
  for name,digest in proof['runtime_hashes'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 with tempfile.TemporaryDirectory(prefix='flora-ceo-rollback-')as temp:
  env=dict(os.environ,GIT_INDEX_FILE=temp+'/index');subprocess.run(['git','read-tree','HEAD'],cwd=ROOT,env=env,check=True)
  subprocess.run(['git','apply','--cached','--reverse','--binary'],input=git('diff','--binary',BASE,'HEAD'),cwd=ROOT,env=env,check=True)
  restored=git('write-tree',env=env,text=True).strip();assert restored==git('rev-parse',BASE+'^{tree}',text=True).strip()
 return {'head':git('rev-parse','HEAD',text=True).strip(),'files':len(files),'links':links,'captures':captures,'images_unchanged':images,'rollback_tree':restored,'canonical_or_production_writes':0,'passed':True}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--browser',type=Path);args=parser.parse_args();print(json.dumps(validate(args.browser),indent=2))
