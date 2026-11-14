from pathlib import Path
import json,zipfile,hashlib
D=Path(__file__).resolve().parent.parent
manifest={'authority':'Design-only; no original source/status/rights changes','UK':'Original panorama and 20 positions; registry visual_v2.RESEARCH','banking':'New image_gen purpose-composition, then image_gen removal of five unwanted empty plaques; no publisher photo, logo, real premises or ownership claim','lloyds':'Retained independent LJ-1R enterprise world, not a crop of Banking','assets':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (D/'assets').iterdir()},'actor_metric_mapping':'Landscape-Trace.json; all five bank identities now share Banking scene','force_mapping':'Force-Trace.json','growth':'Frozen ONS +0.7% real GDP, 3 months to Sep 2026 vs prior 3 months; separate from 2024 current-price GVA','gaps':'Nine original research gaps unchanged; macro coverage deficiency separately documented'}
(D/'Provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=list(D.glob('*.html'))+[D/'lj2.css',D/'context.js',D/'Force-Trace.json',D/'Landscape-Trace.json',D/'Research-Gaps.md',D/'Provenance.json']+list((D/'assets').iterdir())
with zipfile.ZipFile(D/'LJ-2-demo.zip','w',zipfile.ZIP_DEFLATED)as z:
 for p in files:
  i=zipfile.ZipInfo(str(p.relative_to(D)),(2026,11,14,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,p.read_bytes())
 z.writestr('START-HERE.txt','Extract whole ZIP and open uk-landscape.html. Three scopes; two lenses each. Enterprise Builder is a future scope note, no model. Sources retain their original dates/rights/status. External profile/industry links require connectivity and destination access. Design only; owner approval pending.')
