"""Rehearse actual proposed records in disposable existing import services only.

SERVICE-TEST fixtures do not prove real HTTP authentication, rights acceptance,
owner review or production receipts. No reviews/approvals/promotions are invoked.
"""
from pathlib import Path
import io,json,os,tempfile,zipfile,hashlib,sys
from unittest.mock import patch
from collections import Counter
ROOT=Path(__file__).resolve().parents[4];D=ROOT/'docs/flora-runtime/ric1'
if __name__=='__main__':sys.path.insert(0,str(ROOT))
def main():
 with tempfile.TemporaryDirectory(prefix='ric1-disposable-')as tmp:
  with patch.dict(os.environ,{'FLORA_DATA_DIR':tmp,'FLORA_PILOT_DIR':tmp,'FLORA_TRUST_PROXY_HEADERS':'1'}):
   from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator,DryRunPlanningService,BlueprintReviewError,BlueprintValidationError
   from cios.applications.flora.blueprint_import.researcher_profile_adapter import adapt_researcher_payload,contract_checksum
   from cios.applications.flora.blueprint_import.atomicity import validate_atomic_statement
   from tests.flora_security_fixtures import fixture_context
   import cios.applications.flora.access as access
   import cios.applications.flora.security as security
   with patch.object(access,'verified_context',fixture_context),patch.object(security,'verified_context',fixture_context):
    records=[json.loads(x)for x in (D/'Proposed-Records.ndjson').read_text().splitlines()]
    checks=[]
    for r in records:
     if r['record_class']=='observation':
      assert validate_atomic_statement(r['payload']['atomic_statement']).atomic,r['external_id']
      klass,payload=adapt_researcher_payload('observation',r['payload'])
      assert klass=='observation'and payload['source_payload']==r['payload']
      assert payload['atomic_statement']==r['payload']['atomic_statement']
      checks.append({'id':r['external_id'],'source_payload_lossless':True,'atomic':True})
    records.extend([{'external_id':'NEG-COMPOUND','record_class':'observation','truth_class':'evidence_backed','payload':{'atomic_statement':'Lloyds income rose; Lloyds costs fell.'}},{'external_id':'PROJECTION-ONLY','record_class':'pain_point','truth_class':'analytical_projection','payload':{'statement':'Investigate net AI value; no customer need confirmed.'}}])
    payload='\n'.join(json.dumps(x)for x in records).encode()
    manifest={'package_id':'RIC1-contract-rehearsal','package_version':'0.1.0','enterprise_id':'ric1-disposable-workspace','profile_version':'0.1','files':[{'path':'records/proposals.ndjson','sha256':hashlib.sha256(payload).hexdigest(),'required':True}],'record_sets':[{'record_class':'mixed','path':'records/proposals.ndjson','count':len(records),'required':True}]}
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED)as z:
     z.writestr('blueprint_manifest.json',json.dumps(manifest));z.writestr('records/proposals.ndjson',payload)
    registry=BlueprintPackageRegistry();receipt=registry.receive(buf.getvalue(),'ric1-disposable.zip','ric1-fixture-reviewer','ric1-disposable-workspace')
    headers={'X-Flora-User':'ric1-fixture-reviewer','X-Flora-Enterprises':'ric1-disposable-workspace','X-Flora-Roles':'package.review'}
    validator=BlueprintPackageValidator();result=validator.validate_and_stage(receipt.package_ref,'ric1-fixture-reviewer',headers)
    assert not result.errors,result.errors
    plan=DryRunPlanningService().create_plan(receipt.import_run_id,'ric1-fixture-reviewer',headers)
    repeat=DryRunPlanningService().create_plan(receipt.import_run_id,'ric1-fixture-reviewer',headers)
    assert repeat.plan_id==plan.plan_id
    effects={x.external_id:x.effect_type for x in plan.effects}
    assert effects['NEG-COMPOUND']=='quarantine'and effects['PROJECTION-ONLY']=='projection'
    assert all(effects[r['external_id']]=='unresolved'for r in records if r['record_class']in {'evidence','observation'}and r['external_id']!='NEG-COMPOUND'),effects
    denied={'X-Flora-User':'different-fixture','X-Flora-Enterprises':'other-workspace','X-Flora-Roles':'package.review'}
    for operation,error in [(lambda:validator.validate_and_stage(receipt.package_ref,'different-fixture',denied),BlueprintValidationError),(lambda:DryRunPlanningService().create_plan(receipt.import_run_id,'different-fixture',denied),BlueprintReviewError)]:
     try:operation()
     except error:pass
     else:raise AssertionError('Cross-workspace inspection/planning was allowed')
    assert result.canonical_mutations==plan.actual_canonical_mutation_count==plan.expected_canonical_mutation_count==0
    assert not(Path(tmp)/'memory').exists()
    out={'scope':'Disposable existing import services with explicit SERVICE-TEST fixture; not production or real-login verification','proposed_payload_sha256':hashlib.sha256((D/'Proposed-Records.ndjson').read_bytes()).hexdigest(),'contract_checksum':contract_checksum(),'atomic_observation_proposals':len(checks),'adapter_checks':checks,'effect_counts':dict(Counter(effects.values())),'cross_workspace_inspection_denied':True,'cross_workspace_planning_denied':True,'repeated_plan_idempotent':True,'reviews_created':0,'approvals_created':0,'canonical_mutations':0,'pipeline_writes':0,'source_registrations':0,'production_acceptance':'UNVERIFIED'}
    return out
if __name__=='__main__':
 out=main()
 if '--record' in sys.argv:(D/'Import-Dry-Run.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2))
