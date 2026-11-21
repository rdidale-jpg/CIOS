"""Export public baseline presentation for the isolated SI-1 design build."""
import json
from pathlib import Path
from cios.applications.flora import visual_streams as v,design_system as ds
D=Path(__file__).resolve().parents[1]
rows={}
for scope,binding in v.SCOPES.items():
 for stream in binding['streams']:
  path=binding['route'];query={'stream':[stream]}
  html=v.render(path,query)
  details={}
  for spot in v.geometry()[scope+'-'+stream]['spots']:
   if scope=='uk'and stream=='landscape':continue
   details[spot['id']]=v.render(path,query|{'detail':[spot['id']]})
  rows[scope+'-'+stream]={'scope':scope,'stream':stream,'html':html,'details':details}
# Outside the repository: transient public render export, not a new research store.
Path('/tmp/si1-public-base.json').write_text(json.dumps(rows))
print('Exported seven public renderings; no private records or writes.')
