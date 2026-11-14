from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib,subprocess,zipfile,re
R=Path(__file__).resolve().parents[5];D=Path(__file__).resolve().parent.parent
class Doc(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.unsafe=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if 'id'in d:
   assert d['id'] not in self.ids,('duplicate ID',d['id']);self.ids.add(d['id'])
  for k in ['href','src']:
   if k in d:self.links.append(d[k])
  if t in ['script','form','iframe','canvas']:self.unsafe.append(t)
parsed={}
for p in D.glob('*.html'):
 d=Doc();d.feed(p.read_text());parsed[p.resolve()]=d
count=0
for p,d in parsed.items():
 assert not d.unsafe,(p,d.unsafe)
 for href in d.links:
  u=urlsplit(href)
  if u.scheme:assert u.scheme in ['http','https'];continue
  assert not u.path.startswith('/'),(p,href)
  target=(p.parent/unquote(u.path)).resolve() if u.path else p
  assert target.is_relative_to(D)and target.is_file(),(p,href)
  if target in parsed:assert not u.fragment or u.fragment in parsed[target].ids,(p,href)
  count+=1
# Canonical review Markdown links must actually exist, including the old committed before images.
for f in [D/'README.md',D/'Research-Gaps.md']:
 for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',f.read_text()):
  u=urlsplit(target)
  if u.scheme:continue
  assert (f.parent/unquote(u.path)).resolve().is_file(),(f,target)
art=json.loads((D/'Artwork-Provenance.json').read_text());hashes=[]
for scene in art['scenes']:
 p=D/scene['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==scene['sha256'];hashes.append(scene['sha256'])
uk=(D/'assets/uk-economy.webp').read_bytes();assert hashlib.sha256(uk).hexdigest()==art['uk_sha256'];assert uk==subprocess.check_output(['git','show','0cb07c2:cios/applications/flora/visual_v2_assets/uk-economy.webp'],cwd=R);assert len(set(hashes+[art['uk_sha256']]))==4
mapping=json.loads((D/'Interaction-Mapping.json').read_text());basis=json.loads((R/'cios/applications/flora/visual_v2_assets/economy.json').read_text());assert [(v['label'],v['position'])for v in mapping['UK_labels']]==[(v['label'],v['position'])for v in basis['districts']];assert sum(bool(v['route'])for v in mapping['UK_labels'])==3
assert len(json.loads((D/'Evidence-to-Visual.json').read_text())['bindings'])==36
research=R/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json';audit=json.loads((D/'Research-Audit.json').read_text());assert hashlib.sha256(research.read_bytes()).hexdigest()==audit['research_sha256'];assert research.read_bytes()==subprocess.check_output(['git','show','2080158:'+str(research.relative_to(R))],cwd=R)
with zipfile.ZipFile(D/'LJ-1R-demo.zip')as z:
 assert not any(n.startswith('05-')for n in z.namelist());assert len([n for n in z.namelist()if n.endswith('.html')])==10
 for p in D.glob('[0-9][0-9]-*.html'):assert z.read(p.name)==p.read_bytes()
before={}
for device in ['desktop','ipad-landscape','ipad-portrait','mobile','mobile-320']:
 for state in ['02-banking','03-groups','04-lloyds']:
  p=D.parent/'previews'/f'{device}-{state}-viewport.jpg';b=p.read_bytes();assert b==subprocess.check_output(['git','show','2080158:'+str(p.relative_to(R))],cwd=R);before[str(p.relative_to(R))]=hashlib.sha256(b).hexdigest()
(D/'Comparison-Provenance.json').write_text(json.dumps({'before_commit':'208015805e12772fb425cb014870db697f878f6d','before_image_hashes':before,'protocol':'Same scope and CSS viewport, original native top-of-page framing, no independent zoom/recrop; full pages also linked. Overlay artwork is new, facts retain audit status.'},indent=2)+'\n')
report={'html_documents':len(parsed),'local_links_assets_checked':count,'broken_links':0,'unsafe_tags':0,'four_distinct_artwork_hashes':True,'UK_original_bytes_labels_positions_preserved':True,'available_public_routes':3,'visual_label_bindings':36,'research_hash_unchanged':True,'before_images_pinned_and_unchanged':15,'archive_has_four_levels_no_fifth_page':True,'modelling_engine':False,'scope':'Design artifacts only; no app/workflow/source/IAM/Offers/Pipeline changes'}
(D/'Design-Checks.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
