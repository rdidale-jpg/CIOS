from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
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
for p in D.glob('*.html'):
 doc=Document();doc.feed(p.read_text());parsed[p.name]=doc
count=0
for name,doc in parsed.items():
 assert doc.scripts==0
 for href in doc.links:
  u=urlsplit(href)
  if u.scheme:continue
  if u.path.endswith('.css'):assert (D/u.path).is_file();continue
  target=u.path or name
  assert target in parsed,(name,href)
  assert not u.fragment or u.fragment in parsed[target].ids,(name,href)
  count+=1
report={'html_pages':len(parsed),'local_links_checked':count,'broken_links':0,'scripts':0,'production_changes':False,'browser_report':'previews/Browser-Checks.json','scope':'Design artifacts and standalone review tool only; no app/workflow/research edits'}
(D/'Design-Checks.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
