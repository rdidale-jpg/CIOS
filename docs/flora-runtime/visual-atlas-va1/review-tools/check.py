"""Check local design links, including nested review artifacts; no app requests."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
D=Path(__file__).resolve().parent.parent
class Document(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.scripts=0
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.add(d['id'])
  if 'href' in d:self.links.append(d['href'])
  if tag=='script':self.scripts+=1
parsed={}
for p in D.rglob('*.html'):
 doc=Document();doc.feed(p.read_text());parsed[p.resolve()]=doc
count=0;preserved_routes=0
for page,doc in parsed.items():
 # Only the unchanged accepted baseline retains its original optional script.
 assert doc.scripts==0 or page.name=='baseline.html'
 for href in doc.links:
  u=urlsplit(href)
  if u.scheme:continue
  if u.path.startswith('/'):
   assert page.name=='baseline.html'
   preserved_routes+=1;continue
  target=(page.parent/unquote(u.path)).resolve() if u.path else page
  assert target.is_relative_to(D),(page,href)
  assert target.is_file(),(page,href)
  if target in parsed:assert not u.fragment or u.fragment in parsed[target].ids,(page,href)
  count+=1
report={'html_pages':len(parsed),'local_links_checked':count,'broken_links':0,'scripts_in_new_designs':0,'preserved_baseline_app_routes':preserved_routes,'production_changes':False,'browser_reports':['previews/Browser-Checks.json','simplicity/previews/Browser-Review.json'],'scope':'Design artifacts and standalone review tooling only; no app/workflow/research edits'}
(D/'Design-Checks.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
