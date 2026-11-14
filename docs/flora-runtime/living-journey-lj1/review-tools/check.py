from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib,subprocess,zipfile
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent.parent
class Doc(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.bad=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if 'id'in d:
   assert d['id']not in self.ids,('Duplicate ID',d['id'])
   self.ids.add(d['id'])
  for k in ['href','src']:
   if k in d:self.links.append(d[k])
  if t in ['script','form','iframe']:self.bad.append(t)
parsed={}
for p in D.glob('*.html'):
 d=Doc();d.feed(p.read_text());parsed[p.resolve()]=d
n=0
for p,d in parsed.items():
 assert not d.bad,(p,d.bad)
 for link in d.links:
  u=urlsplit(link)
  if u.scheme:continue
  assert not u.path.startswith('/'),(p,link)
  target=(p.parent/unquote(u.path)).resolve() if u.path else p
  assert target.is_relative_to(D)and target.is_file(),(p,link)
  if target in parsed:assert not u.fragment or u.fragment in parsed[target].ids,(p,link)
  n+=1
for p,h in json.loads((D/'Reference-Hashes.json').read_text()).items():
 assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 assert (R/p).read_bytes()==subprocess.check_output(['git','show','0cb07c2:'+p],cwd=R)
for f in ['01-uk.html','02-banking.html','03-groups.html','04-lloyds.html','05-deeper.html']:
 with zipfile.ZipFile(D/'LJ-1-demo.zip')as z:assert z.read(f)==(D/f).read_bytes()
report={'base':'0cb07c2e78ccb16240c799b31cd62736e2135529','html_pages':len(parsed),'local_links_and_assets_checked':n,'broken_links':0,'script_form_iframe_count':0,'source_hashes_match_original_main':True,'portable_demo_matches_files':True,'review_scope':'docs/flora-runtime/living-journey-lj1 only; application, workflows, IAM, research, matcher, Offers and Pipeline untouched'}
(D/'Design-Checks.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
