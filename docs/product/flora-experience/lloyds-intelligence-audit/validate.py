"""Diagnostic QA and unchanged-runtime/authority proof. No baseline writes."""
import ast,csv,hashlib,json,os,re,subprocess,tempfile
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
BASE='3a4c7e0f6ad81af7ef32ed477a1a584ac2efae87'
PREFIX=str(HERE.relative_to(ROOT))+'/'
def git(*a,**kw):return subprocess.check_output(['git',*a],cwd=ROOT,**kw)
def check():
 changed=set(git('diff','--name-only',BASE,text=True).splitlines())|set(git('ls-files','--others','--exclude-standard',text=True).splitlines())
 assert changed and all(p.startswith(PREFIX)for p in changed),sorted(changed)
 assert sorted(changed)==(HERE/'File-Inventory.txt').read_text().splitlines()
 subprocess.run(['git','diff','--exit-code',BASE,'--','cios','enterprise-knowledge','architecture','tests','.github','requirements.txt','requirements-browser.txt'],cwd=ROOT,check=True,capture_output=True)
 # All tracked paths outside this new diagnostic folder must stay byte-identical.
 for p in git('ls-tree','-r','--name-only',BASE,text=True).splitlines():
  if not p.startswith(PREFIX):
   assert (ROOT/p).is_file(),p
 # Git performs the exact complete tracked-tree comparison, including binary art.
 assert not git('diff','--name-only',BASE,'--','.',':(exclude)'+PREFIX,text=True).strip()
 a=json.loads((HERE/'Audit.json').read_text());i=json.loads((HERE/'Inventory.json').read_text());b=json.loads((HERE/'Baseline.json').read_text());v=json.loads((HERE/'previews/Browser-Diagnostic.json').read_text())
 assert b['baseline']==b['main']==b['deployment']['sha']==i['baseline']==v['runtime_baseline']==BASE
 assert b['deployment']['status']=='live'and b['owner_acceptance'].startswith('Visual/commercial acceptance withheld')
 assert len(a['domains'])==17 and len({d['id']for d in a['domains']})==17
 assert len(a['screens'])==16 and len(a['recoverable_and_backlog'])==21
 for group in ('domains','recoverable_and_backlog'):
  for row in a[group]:
   assert set(row['root_causes'].split(','))<=set('ABCDEFGH')
   assert all(k in a['references']for k in row['refs'].split(','))
 for key,(p,ref)in a['references'].items():git('cat-file','-e',(ref or BASE)+':'+p)
 for name,key in [('Coverage','domains'),('Traceability','screens'),('Recovery-Backlog','recoverable_and_backlog')]:
  with (HERE/(name+'.csv')).open()as f:assert list(csv.DictReader(f))==a[key]
 for row in i['research_census']:
  assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
 assert len(i['screens'])==96 and sum(not r['detail']for r in i['screens'])==16
 assert len(i['public_projection'])==24 and len({r['id']for r in i['public_projection']})==24
 assert sum(r['id'].startswith('LBG-')for r in i['public_projection'])==19
 assert i['finite_measures']['projection_ids_not_observed_by_finite_text_or_measure_match']==[]
 assert i['finite_measures']['empty_focus_fact_lists']==['commercial','retirement']
 assert len(i['verified_relationships'])==1 and i['verified_relationships'][0]['id']=='REV-ENVOY-GOOGLE'
 assert len(i['existing_reconciliations'])==13 and all(r['arithmetic_reproduces']for r in i['existing_reconciliations'])
 assert len(i['initial_factory']['replay_claims'])==6
 assert i['initial_factory']['verified_isolated_classes']=={'evidence':1,'observation':1}
 assert i['initial_factory']['body_article_candidates']==6 and not any(i['initial_factory']['body_publication_flags'])
 assert all(r['conclusion_eligible']for r in i['agenda'])
 assert all(r['scope']and r['period']and r['basis']for r in i['existing_reconciliations'])
 assert len(v['screens'])==33 and len(v['files'])==57 and not v['runtime_errors']
 assert not any(s['horizontalOverflow']or s['clippedText']for s in v['screens'].values())
 for device in ('desktop','ipad-landscape','ipad-portrait'):
  rows=v['screens'][device+':credit']['narrowLayerTitles'];assert len(rows)==3
  assert all(r['width']==65 and r['markPosition']=='absolute'for r in rows)
 for p,h in v['files'].items():assert hashlib.sha256((HERE/'previews'/p).read_bytes()).hexdigest()==h,p
 assert set(v['pdf'])=={'economics','credit','strategy'}and all(d['pages']==3 for d in v['pdf'].values())
 assert v['pdf']['economics']['text_per_page'][-1]==63
 for f in HERE.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
 links=0
 for f in HERE.glob('*.md'):
  for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if '://'in target or target.startswith('#'):continue
   assert (f.parent/target.split('#')[0]).exists(),(f.name,target);links+=1
 head=git('rev-parse','HEAD',text=True).strip();rollback='not yet committed; docs-only boundary checked'
 if head!=BASE:
  with tempfile.TemporaryDirectory(prefix='lloyds-audit-reverse-')as t:
   env=dict(os.environ,GIT_INDEX_FILE=t+'/index');subprocess.run(['git','read-tree','HEAD'],cwd=ROOT,env=env,check=True)
   subprocess.run(['git','apply','--cached','--reverse','--binary'],input=git('diff','--binary',BASE,'HEAD'),cwd=ROOT,env=env,check=True)
   restored=git('write-tree',env=env,text=True).strip();assert restored==git('rev-parse',BASE+'^{tree}',text=True).strip();rollback=restored
 return {'head':head,'runtime_baseline':BASE,'passed':True,'changed_files':len(changed),'runtime_or_existing_research_changes':False,
  'domains':17,'default_screen_assessments':16,'finite_states':96,'browser_views':33,'capture_files':57,'reconciliations':13,
  'research_census_files':len(i['research_census']),'local_markdown_links':links,'rollback_tree':rollback,
  'limitations':['live DOM / owner PDFs / physical iPad not inspected','production canonical/private records unverified','no source/legal or evidence acceptance']}
if __name__=='__main__':print(json.dumps(check(),indent=2))
