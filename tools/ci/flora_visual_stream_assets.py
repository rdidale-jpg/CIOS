"""Offline, deterministic responsive encodings of the seven owner-approved scenes.

Requires Pillow for asset preparation only, never at application runtime.
Original bytes remain in the pinned design commit; no redraw/crop/research call.
"""
from pathlib import Path
import hashlib, io, json, subprocess
from PIL import Image
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[2]
DESIGN='c6bf2280594922db6951c5c36205984c85ca4aea'
SOURCE='docs/flora-runtime/living-journey-lj1/lj3/assets/'
OUT=ROOT/'cios/applications/flora/visual_stream_assets'
NAMES={'uk-landscape':'uk-economy.webp','uk-forces':'uk-forces.png',
       'banking-landscape':'banking-combined.png','banking-forces':'banking-forces.png',
       'lloyds-inside':'lloyds-inside.png','lloyds-landscape':'lloyds-world.png','lloyds-forces':'lloyds-forces.png'}

def geometry():
 class Scene(HTMLParser):
  def __init__(self):super().__init__();self.spots=[];self.current=None;self.small=False;self.depth=0;self.description=''
  def handle_starttag(self,tag,attrs):
   attrs=dict(attrs)
   if tag=='figure':self.description=attrs.get('aria-label','')
   if 'data-label-id' in attrs:
    self.current={'id':attrs['data-label-id'],'position':attrs['style'],'label':'','small':''};self.spots.append(self.current);self.depth=1
   elif self.current:self.depth+=1
   if self.current and tag=='small':self.small=True
  def handle_endtag(self,tag):
   if tag=='small':self.small=False
   if self.current:
    self.depth-=1
    if self.depth==0:self.current=None
  def handle_data(self,text):
   if self.current:self.current['small' if self.small else 'label']+=text
 scenes={}
 for scene in NAMES:
  text=subprocess.check_output(['git','show',DESIGN+':docs/flora-runtime/living-journey-lj1/lj3/'+scene+'.html'],cwd=ROOT,text=True)
  parsed=Scene();parsed.feed(text)
  for spot in parsed.spots:
   spot['label']=spot['label'].replace('›','').replace('↗','').strip();spot['small']=spot['small'].strip()
  scenes[scene]={'description':parsed.description,'spots':parsed.spots}
 (OUT/'scenes.json').write_text(json.dumps({'design_commit':DESIGN,'authority':'Presentation geometry and labels only; never facts, research status, relationships or permissions','scenes':scenes},indent=2)+'\n')

def build():
 OUT.mkdir(parents=True,exist_ok=True)
 manifest={'design_commit':DESIGN,'encoding':'Pillow WebP quality 87, method 6; proportional LANCZOS resize, no crop or composition changes',
 'rights':'Owner-commissioned image_gen conceptual FLORA illustrations; accepted for implementation in #612. Not photographs, source evidence, company premises, ownership, magnitude or geographic maps. Original creation and prior conversion provenance retained in PR #610.',
 'originals_retained':'Exact seven original files remain unchanged in the pinned Git design commit; runtime serves only deterministic derivatives.', 'scenes':{}}
 for scene,name in NAMES.items():
  raw=subprocess.check_output(['git','show',DESIGN+':'+SOURCE+name],cwd=ROOT)
  image=Image.open(io.BytesIO(raw)).convert('RGB'); row={'original_path':SOURCE+name,'original_sha256':hashlib.sha256(raw).hexdigest(),'original_bytes':len(raw),'width':image.width,'height':image.height,'variants':[]}
  for width in [768,1152,1536]:
   variant=image.resize((width,round(width*image.height/image.width)),Image.Resampling.LANCZOS) if width!=image.width else image
   buf=io.BytesIO();variant.save(buf,'WEBP',quality=87,method=6);data=buf.getvalue();sha=hashlib.sha256(data).hexdigest();filename=f'{scene}-{width}-{sha[:12]}.webp';(OUT/filename).write_bytes(data)
   row['variants'].append({'width':width,'height':variant.height,'file':filename,'sha256':sha,'bytes':len(data)})
  manifest['scenes'][scene]=row
 paths=['enterprise-knowledge/banking/research-model/Assessment-Overlay.json','enterprise-knowledge/macro/research-model/Macro-Context-v1.json','cios/applications/flora/visual_v2_assets/economy.json']
 manifest['caption_source_pins']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [ROOT/q for q in paths]}
 (OUT/'artwork.json').write_text(json.dumps(manifest,indent=2)+'\n')
 geometry()
 print('Encoded seven exact accepted originals; '+str(sum(v['bytes']for s in manifest['scenes'].values()for v in s['variants']))+' bytes across 21 responsive files.')
if __name__=='__main__':build()
