from pathlib import Path
import zipfile
D=Path(__file__).resolve().parent.parent
files=list(D.glob('[0-9][0-9]-*.html'))+[D/'rich.css',D/'Research-Audit.json',D/'Research-Gaps.md',D/'Evidence-to-Visual.json',D/'Interaction-Mapping.json',D/'Artwork-Provenance.json']+list((D/'assets').glob('*'))
with zipfile.ZipFile(D/'LJ-1R-demo.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):
  entry=zipfile.ZipInfo(str(p.relative_to(D)),date_time=(2026,11,14,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;z.writestr(entry,p.read_bytes())
 entry=zipfile.ZipInfo('START-HERE.txt',date_time=(2026,11,14,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED
 z.writestr(entry,'FLORA LJ-1R. Extract the entire ZIP and open 01-uk.html. Four-level static design prototype; no server or JavaScript. The original UK panorama and three new purpose-composed generated scenes are conceptual, not actual premises. Technology/Aviation and other-bank existing-profile links visit existing FLORA public routes and require connectivity/destination access. Owner visual acceptance pending. Model the Enterprise is a future scope note only, no engine. Current financial/entity/supplier data gaps are recorded, not filled. No application, Offers, IAM or Pipeline is implemented or changed.\n')
index='''<!doctype html><html lang="en-GB"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LJ-1R design review</title><link rel="stylesheet" href="rich.css"><body><main style="padding:36px"><h1>Four levels. One rich visual language.</h1><p>Original UK retained; three purpose-composed deeper illustrations. Owner review pending.</p><p><a href="01-uk.html">Start at UK Economy →</a> · <a href="LJ-1R-demo.zip">Download offline demo</a> · <a href="README.md">Evidence, comparisons and review</a></p><img src="previews/desktop-continuity.jpg" alt="Four-screen style-continuity board" style="width:100%;height:auto"></main></body></html>'''
(D/'index.html').write_text(index)
print('Packaged',len(files),'design files; open 01-uk.html')
