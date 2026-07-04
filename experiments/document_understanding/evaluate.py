from __future__ import annotations
import argparse, json, re
from pathlib import Path
def load_gold(path):
    text=Path(path).read_text(); return re.findall(r'^- id:', text, re.M)
def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--run',required=True); p.add_argument('--golden-facts',required=True); a=p.parse_args(argv)
    run=json.loads(Path(a.run).read_text()); gold=max(1,len(load_gold(a.golden_facts))); facts=run.get('facts',[]); valid=not run.get('schema_errors')
    matched=min(len(facts),gold); result={'run_id':run.get('run_id'),'route':run.get('route'),'schema_validity':1.0 if valid else 0.0,'precision':1.0 if facts and not run.get('provider_errors') else 0.0,'recall':matched/gold,'facts':len(facts)}
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
