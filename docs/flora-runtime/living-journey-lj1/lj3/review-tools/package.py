from pathlib import Path
import zipfile,json,hashlib
D=Path(__file__).resolve().parent.parent
files=list(D.glob('*.html'))+[D/n for n in ['lj3.css','context.js','Stream-Mapping.json','Landscape-Trace.json','Research-Audit.json','Research-Gaps.md']]+list((D/'assets').iterdir())
with zipfile.ZipFile(D/'LJ-3-demo.zip','w',zipfile.ZIP_DEFLATED)as z:
 for p in files:
  i=zipfile.ZipInfo(str(p.relative_to(D)),(2026,11,14,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,p.read_bytes())
 z.writestr('START-HERE.txt','Extract all files and open uk-landscape.html. LJ-3 design-only. UK/Banking: Landscape | Forces; Lloyds: Inside | Landscape | Forces. No application, model, pressure qualification, scenario or Pipeline engine. Original source limitations and nine gaps remain. Art is metaphorical, not actual premises, severity or weather data. External links require destination access. Owner visual and architecture acceptance pending.')
