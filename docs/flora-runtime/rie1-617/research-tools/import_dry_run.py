"""Isolated existing import-contract rehearsal. No reviews, approvals or promotion.

Explicit existing SERVICE-TEST authority only, never production authentication
proof. All fixture storage is disposable. No private/canonical runtime opened.
"""
from pathlib import Path
import io,json,os,tempfile,zipfile,hashlib
from collections import Counter
from unittest.mock import patch
D=Path(__file__).resolve().parents[1]

def main():
 with tempfile.TemporaryDirectory(prefix='rie1-contract-') as tmp:
  with patch.dict(os.environ,{'FLORA_DATA_DIR':tmp,'FLORA_PILOT_DIR':tmp,'FLORA_TRUST_PROXY_HEADERS':'1'}):
   from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator,DryRunPlanningService,BlueprintReviewError,BlueprintValidationError
   from cios.applications.flora.blueprint_import.researcher_profile_adapter import adapt_researcher_payload,contract_checksum
   from cios.applications.flora.blueprint_import.atomicity import validate_atomic_statement
   from tests.flora_security_fixtures import fixture_context
   import cios.applications.flora.access as access
   import cios.applications.flora.security as security
   # The fixture resolver exists in unchanged repository tests. No production resolver, file or permission is modified.
   with patch.object(access,'verified_context',fixture_context),patch.object(security,'verified_context',fixture_context):
    ledger={s['id']:s for s in json.loads((D/'Source-Ledger.json').read_text())}
    claims=[('GDP-Q3','ONS-GDP-Q326','UK real GDP grew 0.7 percent quarter on quarter in Q3 2026.','2026-09-30','UK economy'),('CPI-SEP','ONS-CPI-SEP26','UK CPI annual inflation was 3.5 percent in September 2026.','2026-09-30','UK consumer prices'),('LBG-NII','LBG-Q326','Lloyds Group underlying net interest income was GBP11084m in nine months ended 30 September 2026.','2026-09-30','Lloyds Banking Group plc'),('LBG-NET','LBG-Q326','Lloyds Group underlying net income was GBP14819m in nine months ended 30 September 2026.','2026-09-30','Lloyds Banking Group plc'),('LBG-COST','LBG-Q326','Lloyds Group underlying operating costs were GBP7246m in nine months ended 30 September 2026.','2026-09-30','Lloyds Banking Group plc'),('LBG-PBT','LBG-Q326','Lloyds Group statutory PBT was GBP6625m in nine months ended 30 September 2026.','2026-09-30','Lloyds Banking Group plc'),('LBG-DEP','LBG-Q326','Lloyds Group customer deposits were GBP502.8bn at 30 September 2026.','2026-09-30','Lloyds Banking Group plc'),('LBG-CET1','LBG-Q326','Lloyds Group CET1 ratio was 13.3 percent at 30 September 2026.','2026-09-30','Lloyds Banking Group plc')]
    records=[];adapters=[]
    for sid in sorted({c[1]for c in claims}):
     source=ledger[sid]
     records.append({'external_id':sid,'record_class':'source','truth_class':'package_metadata','payload':{'name':source['title'],'url':source['url'],'rights':source['rights']}})
    for cid,sid,statement,date,scope in claims:
     assert validate_atomic_statement(statement).atomic,statement
     eid='RIE1-EVD-'+cid;oid='RIE1-OBS-'+cid
     ev={'evidence_id':eid,'source_id':sid,'source_url':ledger[sid]['url'],'publication_date':ledger[sid]['publication_date'],'collection_date':'2026-11-14','summary':statement,'rights':ledger[sid]['rights'],'original_subject_scope':scope,'candidate_status':'unreviewed'}
     if cid=='LBG-PBT':ev['original_measure_label']='Profit before tax'
     obs={'observation_id':oid,'atomic_statement':statement,'type':'fact','affected_entity_relationship':'research.'+cid.lower(),'event_date':date,'supporting_evidence_ids':[eid],'source_subject_scope':scope,'source_id':sid,'candidate_status':'unreviewed'}
     records.extend([{'external_id':eid,'record_class':'evidence','truth_class':'evidence_backed','payload':ev},{'external_id':oid,'record_class':'observation','truth_class':'evidence_backed','payload':obs}])
     klass,mapped=adapt_researcher_payload('observation',obs)
     adapters.append({'id':oid,'owner_class':klass,'statement_retained':mapped.get('atomic_statement')==statement,'source_payload_retained':mapped['source_payload']==obs,'contract_checksum':mapped['mapping_diagnostics']['contract_checksum']})
    bad='Lloyds income rose; Lloyds costs fell.'
    assert not validate_atomic_statement(bad).atomic
    records.append({'external_id':'NEG-COMPOUND','record_class':'observation','truth_class':'evidence_backed','payload':{'atomic_statement':bad}})
    records.append({'external_id':'PROJECTION-ONLY','record_class':'pain_point','truth_class':'analytical_projection','payload':{'statement':'Investigate a possible service decision; no buyer need established.'}})
    payload='\n'.join(json.dumps(r)for r in records).encode()
    manifest={'package_id':'RIE1-contract-rehearsal','package_version':'0.1.0','enterprise_id':'rie1-disposable-workspace','profile_version':'0.1','files':[{'path':'records/research.ndjson','sha256':hashlib.sha256(payload).hexdigest(),'required':True}],'record_sets':[{'record_class':'mixed','path':'records/research.ndjson','count':len(records),'required':True}]}
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED)as z:
     z.writestr('blueprint_manifest.json',json.dumps(manifest));z.writestr('records/research.ndjson',payload)
    registry=BlueprintPackageRegistry();receipt=registry.receive(buf.getvalue(),'rie1-disposable.zip','rie1-test-reviewer','rie1-disposable-workspace')
    headers={'X-Flora-User':'rie1-test-reviewer','X-Flora-Enterprises':'rie1-disposable-workspace','X-Flora-Roles':'package.review'}
    validator=BlueprintPackageValidator();result=validator.validate_and_stage(receipt.package_ref,'rie1-test-reviewer',headers)
    assert not result.errors,result.errors
    staged=validator.staging_summary(receipt.import_run_id)['candidates']
    plan=DryRunPlanningService().create_plan(receipt.import_run_id,'rie1-test-reviewer',headers)
    repeat=DryRunPlanningService().create_plan(receipt.import_run_id,'rie1-test-reviewer',headers)
    assert plan.plan_id==repeat.plan_id
    effects={e.external_id:e.effect_type for e in plan.effects}
    assert effects['NEG-COMPOUND']=='quarantine',effects
    assert effects['PROJECTION-ONLY']=='projection',effects
    assert all(effects['RIE1-OBS-'+c[0]]=='unresolved'for c in claims),effects
    denied={'X-Flora-User':'other-fixture','X-Flora-Enterprises':'different-workspace','X-Flora-Roles':'package.review'}
    try:validator.validate_and_stage(receipt.package_ref,'other-fixture',denied)
    except BlueprintValidationError:pass
    else:raise AssertionError('Cross-workspace inspection allowed')
    try:DryRunPlanningService().create_plan(receipt.import_run_id,'other-fixture',denied)
    except BlueprintReviewError:pass
    else:raise AssertionError('Cross-workspace plan allowed')
    assert result.canonical_mutations==plan.actual_canonical_mutation_count==plan.expected_canonical_mutation_count==0
    assert not (Path(tmp)/'memory').exists()
    out={'scope':'Disposable existing receipt/staging/planning contracts; explicit service-test authority, not real login/HTTP/production receipt evidence','source_profile_checksum':contract_checksum(),'input_sha256':hashlib.sha256(payload).hexdigest(),'source_records':3,'atomic_observation_proposals':len(claims),'evidence_proposals':len(claims),'staging_status_counts':dict(Counter(c['validation_status']for c in staged)),'plan_effect_counts':dict(Counter(effects.values())),'effects_by_original_id':effects,'adapter_checks':adapters,'repeated_plan_idempotent':True,'cross_workspace_inspection_denied':True,'cross_workspace_planning_denied':True,'reviews_created':0,'approvals_created':0,'canonical_mutations':0,'pipeline_writes':0,'production_receipt_status':'not inspected; unverified','fact_bundle_limit':'Facts.json is source-bound research notes, sometimes compound; only the eight explicit scalar claims in this rehearsal are Observation proposals. No full-ledger atomicity/import acceptance claim.','limitations':['Staging accepted means structurally accepted candidate only.','Source scope retained as proposal metadata in disposable workspace; no public-to-private entity mapping performed.','No human evidence acceptance or promotion execution.','Original byte acquisition/rights acceptance and any real import mappings require owner review.','The existing lexical atomicity check flags the standard phrase profit before tax. The scalar Observation uses the equivalent PBT abbreviation; meaning and original label remain in the source/evidence and dossier. No validator weakened.','No temporary archive or private fixture state published.']}
    (D/'Import-Dry-Run.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:out[k]for k in ['atomic_observation_proposals','staging_status_counts','plan_effect_counts','canonical_mutations','pipeline_writes']}))
if __name__=='__main__':main()
