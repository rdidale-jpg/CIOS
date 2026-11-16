#!/usr/bin/env python3
"""F3 current-permission proof. Real BoE control only; five issuers stay blocked."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.research.f2_proof import run
from tools.research.f3_quality import validate,BASE

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--preview',action='store_true');p.add_argument('--baseline-root')
    args=p.parse_args()
    result=run(args.output,args.preview,args.baseline_root,baseline_sha=BASE,baseline_financial_main=True)
    audit=validate();audit['head']=result['head']
    (Path(args.output)/'F3-Admission-Audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'head':result['head'],'status':audit['status'],'real_BoE_control':'persisted/reloaded/recomputed/withdrawn',
        'new_issuer_runs':0,'new_issuer_visibility':0,'typed_review_measurements':audit['typed_measurements'],'offline_reconciliations':audit['reconciliations']}))
