from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,subprocess,hashlib,zipfile
D=Path(__file__).resolve().parent.parent;R=Path(__file__).resolve().parents[5]
class H(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set()
 def handle_starttag(self,t,a):
  d=dict(a);assert t not in ['form','iframe','canvas']
  if 'id'in d:assert d['id']not in self.ids;self.ids.add(d['id'])
  for k in ['href','src']:
   if k in d:self.links.append(d[k])
  if t=='script':assert d.get('src')=='context.js'
ps={}
for p in D.glob('*.html'):
 h=H();h.feed(p.read_text());ps[p.resolve()]=h
n=0
for p,h in ps.items():
 for href in h.links:
  u=urlsplit(href)
  if u.scheme:assert u.scheme in ['https','http'];continue
  t=(p.parent/unquote(u.path)).resolve()if u.path else p
  assert t.is_relative_to(D)and t.is_file(),(p,href)
  if t in ps:assert not u.fragment or u.fragment in ps[t].ids,(p,href)
  assert 'groups.html'not in href and '05-'not in href
  n+=1
for href in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',(D/'README.md').read_text()):
 if not urlsplit(href).scheme and href!='Design-Checks.json':assert(D/href).is_file(),href
assets={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(D/'assets').iterdir()}
for f in ['uk-economy.webp','banking-combined.png','lloyds-world.png']:
 assert (D/'assets'/f).read_bytes()==subprocess.check_output(['git','show','f4a62d8:docs/flora-runtime/living-journey-lj1/lj2/assets/'+f],cwd=R)
assert(D/'Research-Gaps.md').read_bytes()==(D.parent/'lj2/Research-Gaps.md').read_bytes()
assert len(set(assets.values()))==7
with zipfile.ZipFile(D/'LJ-3-demo.zip')as z:
 assert len([s for s in z.namelist()if s.endswith('.html')])==17
 for p in D.glob('*.html'):assert z.read(p.name)==p.read_bytes()
r={'HTML_states':len(ps),'local_links_assets':n,'broken_links':0,'preserved_landscape_hashes':{f:assets[f]for f in ['uk-economy.webp','banking-combined.png','lloyds-world.png']},'new_art':{f:h for f,h in assets.items()if f not in ['uk-economy.webp','banking-combined.png','lloyds-world.png']},'nine_gaps_unchanged':True,'model_or_qualification_engine':False,'scope':'New design artifacts only; no canonical/app/IAM/Offers/Pipeline changes','art_provenance':'image_gen original purpose-composed UK/Banking/Lloyds currents/pressure/contour scenes and internal cutaway, 2026-11-14; original UK artistic language reference; not real premises, hierarchy, severity, geography or weather prediction. Unedited originals retained.'}
(D/'Design-Checks.json').write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items()if k not in ['preserved_landscape_hashes','new_art','art_provenance']})
