"""Frozen source-support references; zero-call plan/result when live evaluation is absent."""
import hashlib,json
from pathlib import Path
from ...model import REPO
from .metrics import decision_matrix
from .runtime import readiness


def calibration_plan():
    frozen=json.loads((REPO/'docs/flora-runtime/research-sprint2/completion/Calibration-Freeze-v1.json').read_text())
    for name,expected in frozen['files'].items():
        if hashlib.sha256((REPO/name).read_bytes()).hexdigest()!=expected:raise ValueError('Frozen reference/rubric changed')
    dataset=json.loads((REPO/'tests/fixtures/research-sprint2/real-source-cases-v1.json').read_text())
    rows=[{'id':x['id'],'split':x['split'],'claim_type':x['claim']['truth_class'],'reference':x['reference'],'decision':'not_executed'} for x in dataset['cases']]
    held=[r for r in rows if r['split']=='held_out']
    return {'schema_version':1,'status':'not_executed','configuration':readiness(),'model_calls':0,'network_calls':0,
      'reference_hashes':frozen['files'],'reference_dependence':frozen['reference_dependence'],
      'all_cases':decision_matrix(rows),'held_out':decision_matrix(held),
      'by_claim_type':{t:decision_matrix([r for r in held if r['claim_type']==t]) for t in sorted({r['claim_type'] for r in held})},
      'records':rows,'limitation':'This is a frozen evaluation plan and honest not-executed register, not a live result or accuracy estimate. Controlled fixture tests are separate.'}


def evaluate_case(case_id,retrieve,*,runtime=None):
    """Explicit single-case live evaluation; reference outcome is never sent to a model.

    One case is selected before acquisition. The existing per-run budget/three-call
    cap remains in force; never silently runs a paid corpus or substitutes fixtures.
    """
    from datetime import datetime,timezone
    import uuid
    from .runtime import verify_claim,eligible_passages
    plan=calibration_plan()
    dataset=json.loads((REPO/'tests/fixtures/research-sprint2/real-source-cases-v1.json').read_text())
    matches=[x for x in dataset['cases'] if x['id']==case_id]
    if len(matches)!=1:raise ValueError('Select one frozen calibration case ID')
    case=matches[0]
    if runtime is None and not plan['configuration']['ready_for_bounded_generation']:
        return {'case_id':case_id,'status':'not_executed','decision':'not_executed','reference':case['reference'],'model_calls':0,'network_calls':0,'configuration':plan['configuration']}
    passages=[]
    for source in case['source_ids']:
        nonce='CAL-'+uuid.uuid4().hex;issued=datetime.now(timezone.utc)
        p=retrieve(source,'researcher',nonce);eligible_passages([p])
        if p['request_id']!=nonce or p['role']!='researcher' or datetime.fromisoformat(p['retrieved_at'])<issued:raise ValueError('Fresh calibration source acquisition required')
        if p['sha256']!=case['source_sha256']:raise ValueError('Frozen source changed; new reference version required before evaluation')
        passages.append(p)
    result=verify_claim(case['claim'],passages,retrieve,runtime=runtime)
    mapping={'publish_source_reported':'accepted','publish_labelled_interpretation':'accepted','reject':'rejected','withhold':'unresolved'}
    executed=result['status'] in ('completed','completed_with_conflict')
    return {'case_id':case_id,'status':result['status'],'decision':mapping[result['decision']] if executed else 'not_executed',
      'reference':case['reference'],'reference_reason':case['reference_reason'],'assurance_receipt':result,
      'reference_independence':'Frozen before evaluation; not externally adjudicated. Not supplied in model payload.'}
