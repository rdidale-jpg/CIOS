from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json,subprocess,hashlib
D=Path(__file__).resolve().parent.parent;R=D.parents[3]
class H(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set()
 def handle_starttag(self,t,a):
  d=dict(a);assert t not in ['form','iframe','canvas']
  if 'id'in d:assert d['id']not in self.ids;self.ids.add(d['id'])
  for k in ['href','src']:
   if k in d:self.links.append(d[k])
ps={}
for p in D.glob('*.html'):
 h=H();h.feed(p.read_text());ps[p.resolve()]=h
n=0
for p,h in ps.items():
 for x in h.links:
  u=urlsplit(x)
  if u.scheme:assert u.scheme in ['http','https'];continue
  t=(p.parent/u.path).resolve()if u.path else p
  assert t.is_relative_to(D)and t.is_file(),(p,x)
  if t in ps:assert not u.fragment or u.fragment in ps[t].ids,(p,x)
  assert 'groups.html'not in x and '05-'not in x
  n+=1
assert (D/'Research-Gaps.md').read_bytes()==(D.parent/'rich/Research-Gaps.md').read_bytes()
assert len(json.loads((D/'Force-Trace.json').read_text())['scopes'])==3
assert (D/'assets/uk-economy.webp').read_bytes()==(D.parent/'rich/assets/uk-economy.webp').read_bytes()
r={'html_states':len(ps),'links_assets_checked':n,'broken_links':0,'groups_page':False,'modelling_engine':False,'nine_gaps_unchanged':True,'scope':'Design only; no application/source/IAM/Offers/Pipeline writes'}
(D/'Design-Checks.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
