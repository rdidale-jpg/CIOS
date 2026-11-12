"""Held-out controlled support evaluation; not independent real-world ground truth."""
from collections import Counter,defaultdict
import hashlib,json
from pathlib import Path
from . import assurance


def evaluate(path):
    data=json.loads(Path(path).read_text())
    actual=hashlib.sha256(Path(assurance.__file__).read_bytes()).hexdigest()
    if actual!=data['evaluator_sha256']:raise ValueError('Evaluator changed after held-out freeze; a new evaluation protocol is required')
    results=[];counts=defaultdict(Counter)
    for case in data['cases']:
        result=assurance.assess(case['proposal'],case['passages'],as_of='2026-11-12',run_id='HELDOUT-CONTROLLED-V1',verifier_id='fixture-verifier')
        expected=case['reference_outcome'];observed=result['outcome'];counts[case['claim_type']][expected+' -> '+observed]+=1
        matches=observed==expected and ('reference_source_family_count' not in case or result['source_family_count']==case['reference_source_family_count'])
        results.append({'id':case['id'],'claim_type':case['claim_type'],'reference':expected,'observed':observed,'matches_rubric':matches,'reasons':result['reasons'],'source_family_count':result['source_family_count']})
    accepted_refs=sum(r['reference']=='accept_bounded' for r in results);non_accept_refs=len(results)-accepted_refs
    false_accepts=sum(r['observed']=='accept_bounded' and r['reference']!='accept_bounded' for r in results)
    false_rejects=sum(r['observed']=='reject' and r['reference']=='accept_bounded' for r in results)
    unresolved=sum(r['observed']=='unresolved' for r in results)
    return {'schema_version':1,'split':data['split'],'evaluator_sha256':actual,'held_out_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
      'reference_method':data['reference_method'],'calibration_limit':data['calibration_limit'],'cases':results,'by_claim_type':dict(counts),
      'false_acceptance':{'count':false_accepts,'denominator':non_accept_refs,'rate':false_accepts/non_accept_refs if non_accept_refs else None},
      'false_rejection':{'count':false_rejects,'denominator':accepted_refs,'rate':false_rejects/accepted_refs if accepted_refs else None},
      'unresolved':{'count':unresolved,'denominator':len(results),'rate':unresolved/len(results)},
      'mismatches':[r['id'] for r in results if not r['matches_rubric']],
      'general_semantic_accuracy':'not measured; controlled synthetic support benchmark only'}
