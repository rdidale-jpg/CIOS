"""Explicit bounded research verification; no scheduler or production/canonical writes.

Readiness and calibration-plan are zero-call commands. connectivity performs only
an authenticated model metadata lookup. cycle requires explicit --execute and
reviewed source/model policy/configuration; it can incur existing-account charges.
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from cios.applications.flora.research_intelligence.foundation.sprint2.runtime import readiness,connectivity_check,research_cycle
from cios.applications.flora.research_intelligence.foundation.sprint2.collector import ApprovedRetriever
from cios.applications.flora.research_intelligence.foundation.sprint2.snapshot import completion
from cios.applications.flora.research_intelligence.foundation.sprint2.calibration import calibration_plan,evaluate_case

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('readiness','connectivity','calibration-plan','calibration-case','cycle'))
    parser.add_argument('--case',help='Exact frozen calibration case ID; one bounded live case only')
    parser.add_argument('--source',action='append',default=[])
    parser.add_argument('--execute',action='store_true',help='Explicit one-claim live cycle; can incur existing-account token charges')
    args=parser.parse_args()
    if args.command=='readiness':result=readiness()
    elif args.command=='connectivity':result=connectivity_check()
    elif args.command=='calibration-plan':result=calibration_plan()
    elif args.command=='calibration-case':
        if not args.execute or not args.case:parser.error('calibration-case requires --execute and --case; can incur token charges')
        try:result=evaluate_case(args.case,ApprovedRetriever(completion()['runtime_registry']))
        except Exception as exc:result={'status':'failed_closed','decision':'not_executed','reason':type(exc).__name__,'canonical_promotion':False,'pipeline_qualification':False}
    else:
        if not args.execute:parser.error('cycle requires --execute; readiness makes no calls')
        registry=completion()['runtime_registry']
        if not args.source or any(s not in registry for s in args.source):parser.error('Choose one to four exact approved registry source IDs')
        try:result=research_cycle(args.source,ApprovedRetriever(registry))
        except Exception as exc:result={'status':'failed_closed','decision':'withhold','reason':type(exc).__name__,'canonical_promotion':False,'pipeline_qualification':False}
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
