from pathlib import Path
import zipfile
D=Path(__file__).resolve().parent.parent
states=[('01-uk','UK Economy'),('02-banking','Banking ecosystem'),('03-groups','Major banking groups'),('04-lloyds','Lloyds portrait'),('05-deeper','Explore deeper')]
html='<!doctype html><html lang="en-GB"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLORA LJ-1 design review</title><link rel="stylesheet" href="assets/design.css"><body class="ds-page"><main class="shell"><h1>One visual Banking journey.</h1><p>Design-only prototype · original accepted FLORA foundation · owner acceptance pending.</p><p><a class="button-link" href="01-uk.html">Start at UK Economy →</a> · <a href="README.md">Review storyboard and evidence limits</a></p><img src="previews/desktop-storyboard.jpg" alt="Five-state UK to Lloyds storyboard" style="width:100%;height:auto"><ol>'+''.join(f'<li><a href="{k}.html">{t}</a> · <a href="previews/desktop-{k}.jpg">Desktop preview</a></li>' for k,t in states)+'</ol><p>No live account, API, commercial data or Pipeline operation. Named relationships require existing evidence.</p></main></body></html>'
(D/'index.html').write_text(html)
files=list(D.glob('[0-9][0-9]-*.html'))+[D/'journey.css',D/'Evidence-Mapping.json',D/'Reference-Hashes.json']+list((D/'assets').glob('*'))
with zipfile.ZipFile(D/'LJ-1-demo.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):
  entry=zipfile.ZipInfo(str(p.relative_to(D)),date_time=(2026,11,14,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;z.writestr(entry,p.read_bytes())
 entry=zipfile.ZipInfo('START-HERE.txt',date_time=(2026,11,14,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED
 z.writestr(entry,'FLORA LJ-1 static design prototype. Extract the whole ZIP and open 01-uk.html. No server or JavaScript is required. No live application, identity or Pipeline behaviour is implemented. Owner acceptance is pending. Original evidence and source rights retain their limits; see Sources in each view.\n')
print('Packaged native no-JS prototype; open 01-uk.html')
