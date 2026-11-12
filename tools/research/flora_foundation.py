"""Explicit-root, operator-invoked research steps. No scheduler or production writes.

Actual acquisitions come from a separately invoked approved collector. The CLI
never fabricates retrievals or substitutes offline fixtures for live verification.
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from cios.applications.flora.research_intelligence.foundation.operations import Operations
from cios.applications.flora.research_intelligence.foundation.contracts import Programme

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path)
    sub=p.add_subparsers(dest='command',required=True)
    init=sub.add_parser('create');init.add_argument('--programme',required=True,type=Path);init.add_argument('--key',required=True)
    for command in ('status','cancel','assure','release','advance','mission','rebuild'):
        cmd=sub.add_parser(command);cmd.add_argument('--job',required=True)
        if command=='release':cmd.add_argument('--output',type=Path)
    request=sub.add_parser('request');request.add_argument('--job',required=True);request.add_argument('--role',choices=['researcher','verifier'],required=True);request.add_argument('--source',required=True)
    ingest=sub.add_parser('ingest');ingest.add_argument('--job',required=True);ingest.add_argument('--receipt',type=Path,required=True)
    fail=sub.add_parser('fail');fail.add_argument('--job',required=True);fail.add_argument('--request',required=True);fail.add_argument('--reason',required=True)
    withdraw=sub.add_parser('withdraw');withdraw.add_argument('--job',required=True);withdraw.add_argument('--claim',required=True);withdraw.add_argument('--reason',required=True)
    a=p.parse_args();ops=Operations(a.root)
    if a.command=='create':result={'job_id':ops.create(Programme(**json.loads(a.programme.read_text())),a.key)}
    elif a.command=='advance':
        from cios.applications.flora.research_intelligence.foundation.workflow import establish,AwaitingAcquisition
        def bridge(request):raise AwaitingAcquisition()
        result=establish(ops,a.job,bridge)
    elif a.command=='mission':
        from cios.applications.flora.research_intelligence.foundation.workflow import mission_manifest
        with ops.db() as db:_,programme=ops._job(db,a.job)
        result=mission_manifest(programme)
    elif a.command=='rebuild':result={'active_claims':ops.rebuild(a.job)}
    elif a.command=='request':result=ops.request(a.job,a.role,a.source)
    elif a.command=='ingest':result={'excerpt_digest':ops.ingest(a.job,json.loads(a.receipt.read_text()))}
    elif a.command=='fail':ops.fail_request(a.job,a.request,a.reason);result=ops.status(a.job)
    elif a.command=='assure':result=ops.assure(a.job)
    elif a.command=='release':
        result=ops.release(a.job)
        if a.output:
            # Export only to the isolated operational root. Public repository publication
            # remains a reviewed code delta; this cannot write into a live website.
            path=a.output.resolve()
            if not path.is_relative_to(ops.root):raise PermissionError('Export must remain inside isolated root')
            path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and json.loads(path.read_text())!=result:raise ValueError('Versioned export cannot overwrite an earlier release')
            path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    elif a.command=='withdraw':result=ops.withdraw(a.job,a.claim,a.reason)
    elif a.command=='cancel':ops.cancel(a.job);result=ops.status(a.job)
    else:result=ops.status(a.job)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
