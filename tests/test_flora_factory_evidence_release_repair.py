"""Repair 01: actual UI defaults, scoped citations and compensated releases.

External retained packages are optional, hash-pinned audit inputs; never fetched
or treated as production acceptance. All writes use pytest temporary roots.
"""
from pathlib import Path
import hashlib
import os
import pytest

from tests.test_flora_blueprint_import_validation import pkg
from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator, ImportMappingService, CandidateReviewService, DryRunPlanningService
from cios.applications.flora.blueprint_import.mapping import ImportMappingRepository
from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService, BlueprintPromotionError
from cios.applications.flora.blueprint_import.review_plan import BlueprintReviewPlanCoordinator
from cios.applications.flora.blueprint_import.twin_governance import GovernedIdentityResolutionRepository, project_twin_identity
from cios.applications.flora.blueprint_import.lifecycle import ImportLifecycleService, TwinImportLifecycleService
from cios.applications.flora.blueprint_import.views import review_page, approve_and_promote
from cios.applications.flora.memory.repository import EvidenceRepository

HEADERS={'X-Flora-User':'alice','X-Flora-Enterprises':'*','X-Flora-Roles':'blueprint_import_admin'}
IDENTITY=dict(twin_id='IND-SYN',twin_type='industry',primary_subject_id='IND-SYN',primary_subject_name='Synthetic industry',primary_subject_class='industry',governed_scope='UK synthetic',canonical_owner='IND-SYN')

@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    monkeypatch.setenv('FLORA_PILOT_DIR',str(tmp_path))
    monkeypatch.setenv('FLORA_ENVIRONMENT','development')
    monkeypatch.setenv('FLORA_TRUST_PROXY_HEADERS','1')
    from cios.applications.flora.blueprint_import import review_plan
    monkeypatch.setattr(review_plan,'ASYNC_THRESHOLD',100000)


def evidence(quote='Original',external='EV-1',**extra):
    return dict(external_id=external,record_class='evidence',truth_class='evidence_backed',payload=dict(quote=quote,source_url='https://example.test/source',**extra))


def receive(records=None,version='1',owner='synthetic-enterprise',identity=None,content=None):
    records=records if records is not None else [evidence(),dict(external_id='UNK-1',record_class='unknown',truth_class='unknown',payload={'evidence_ids':['EV-1']})]
    fields=dict(package_version=version+".0",enterprise_id=owner)
    if identity: fields.update(identity)
    reg=BlueprintPackageRegistry();r=reg.receive(content or pkg(manifest_extra=fields,records=records),'retained-or-synthetic.zip','alice')
    BlueprintPackageValidator().validate_and_stage(r.package_ref,'alice',HEADERS)
    return reg.get(r.package_ref)


def candidates(r):
    return BlueprintPackageValidator().staging_summary(r.import_run_id)['candidates']


def prepare(r):
    html,status=review_page(r.import_run_id,HEADERS)
    assert status==200
    job=BlueprintReviewPlanCoordinator().latest_job(r.import_run_id)
    assert job['status'] in {'Ready','Not ready'},job
    return job,html


def promote(r):
    job,_=prepare(r)
    svc=CanonicalPromotionService();a=svc.approve_plan(r.import_run_id,job['plan_id'],'alice','Isolated owner acceptance',HEADERS)
    return svc,a,svc.execute_approved_plan(r.import_run_id,a.approval_id,'alice',HEADERS)


def confirm(r,identity=IDENTITY,headers=HEADERS):
    form={key:[value] for key,value in identity.items()}|{'rationale':['Explicit isolated test owner decision'],'confirm_identity':['yes']}
    from cios.applications.flora.blueprint_import import views
    html,status=views.confirm_import_identity(r.import_run_id,form,headers)
    assert status==200,(status,html)
    return html


def mappings(r):
    return {m['external_id']:m for m in ImportMappingRepository().list(r.import_run_id)}


def test_ui_defaults_preserve_source_citation_and_lineage():
    r=receive();svc,a,result=promote(r)
    row=EvidenceRepository().get('EV-1')
    assert row and row['quote']=='Original'
    assert mappings(r)['EV-1']['canonical_id']=='EV-1'
    unknown=svc.generic_repos['unknown'].list()[0]
    assert unknown['evidence_ids']==['EV-1']
    assert unknown['blueprint_import_lineage']['evidence_id_bindings']=={'EV-1':'EV-1'}
    assert row['source_release_provenance'][0]['approval_id']==a.approval_id
    assert result.final_execution_status=='succeeded'


def test_cross_release_reuses_exact_content_and_preserves_releases():
    first=receive(identity=IDENTITY);promote(first)
    prior=EvidenceRepository().get('EV-1')
    second=receive(version='2',identity=IDENTITY);svc,a,result=promote(second)
    assert len(EvidenceRepository().list())==1
    row=EvidenceRepository().get('EV-1')
    assert row['quote']==prior['quote'] and len(row['source_release_provenance'])==2
    assert mappings(second)['EV-1']['reconciliation_kind']=='unchanged'
    assert ImportLifecycleService().get(first.import_run_id).state=='superseded'
    assert ImportLifecycleService().get(second.import_run_id).current
    assert BlueprintPackageRegistry().get(first.package_ref)
    before=row.copy();assert svc.execute_approved_plan(second.import_run_id,a.approval_id,'alice',HEADERS).final_execution_status=='repeat_no_change'
    assert EvidenceRepository().get('EV-1')==before


@pytest.mark.parametrize('owner,identity',[('different-enterprise',IDENTITY),('synthetic-enterprise',IDENTITY|{'governed_scope':'different industry scope'})])
def test_colliding_source_ids_are_scoped_and_citations_rebound(owner,identity):
    first=receive(identity=IDENTITY);promote(first)
    old=EvidenceRepository().get('EV-1')
    records=[evidence(),dict(external_id='UNK-2',record_class='unknown',truth_class='unknown',payload={'evidence_ids':['EV-1']})]
    second=receive(records,version='2',owner=owner,identity=identity);svc,a,result=promote(second)
    target=mappings(second)['EV-1']['canonical_id']
    assert target!='EV-1' and EvidenceRepository().get('EV-1')==old
    assert len(EvidenceRepository().list())==2
    row=next(row for row in svc.generic_repos['unknown'].list() if row['blueprint_import_lineage']['import_run_id']==second.import_run_id)
    assert row['evidence_ids']==[target]
    assert row['blueprint_import_lineage']['evidence_id_bindings']=={'EV-1':target}
    assert ImportLifecycleService().get(first.import_run_id).current


def test_explicit_rebind_preserved_by_ui_defaults():
    r=receive();prepare(r)
    c=next(c for c in candidates(r) if c['candidate_object_class']=='evidence')
    ImportMappingService().record_mapping(c,'propose_create','alice',HEADERS,'Evidence','OWNER-EV-1','Explicit canonical target')
    svc,a,result=promote(r)
    assert EvidenceRepository().get('OWNER-EV-1')
    assert svc.generic_repos['unknown'].list()[0]['evidence_ids']==['OWNER-EV-1']
    assert not EvidenceRepository().get('EV-1')


@pytest.mark.parametrize('decision',['reject','defer','quarantine','unsupported'])
def test_ineligible_package_evidence_cannot_support_approved_records(decision):
    r=receive();prepare(r)
    c=next(c for c in candidates(r) if c['candidate_object_class']=='evidence')
    CandidateReviewService().record_decision(c['candidate_record_id'],decision,'alice','Not approved',HEADERS)
    # New plan uses the actual UI-generated mappings, with explicit human review.
    plan=DryRunPlanningService().create_plan(r.import_run_id,'alice',HEADERS)
    svc=CanonicalPromotionService()
    with pytest.raises(BlueprintPromotionError):
        a=svc.approve_plan(r.import_run_id,plan.plan_id,'alice','test',HEADERS)
        svc.execute_approved_plan(r.import_run_id,a.approval_id,'alice',HEADERS)
    assert not EvidenceRepository().list()
    assert not ImportLifecycleService().get(r.import_run_id).current


def test_changed_content_requires_explicit_update_and_retains_history():
    r=receive(identity=IDENTITY);promote(r)
    second=receive([evidence('Changed')],version='2',identity=IDENTITY)
    prepare(second)
    assert mappings(second)['EV-1']['reconciliation_kind']=='unresolved identity'
    c=candidates(second)[0]
    ImportMappingService().record_mapping(c,'propose_update','alice',HEADERS,'Evidence','EV-1','Reviewed changed source assertion')
    promote(second)
    row=EvidenceRepository().get('EV-1')
    assert row['quote']=='Changed'
    assert row['blueprint_import_lineage']['prior_canonical_version']['quote']=='Original'


def test_corroborating_and_contradictory_are_distinct():
    r=receive([evidence(collection_date='2026-01-01')],identity=IDENTITY);promote(r)
    second=receive([evidence(collection_date='2026-01-02')],version='2',identity=IDENTITY)
    prepare(second)
    assert mappings(second)['EV-1']['reconciliation_kind']=='corroborating'
    promote(second)
    third=receive([evidence('Opposing',contradicts_evidence_id='EV-1')],version='3',identity=IDENTITY)
    review_page(third.import_run_id,HEADERS)
    assert mappings(third)['EV-1']['reconciliation_kind']=='contradictory'
    plan=DryRunPlanningService().create_plan(third.import_run_id,'alice',HEADERS)
    with pytest.raises(BlueprintPromotionError): CanonicalPromotionService().approve_plan(third.import_run_id,plan.plan_id,'alice','test',HEADERS)


@pytest.mark.parametrize('status',['retired','expired','rejected','quarantined'])
def test_inactive_canonical_target_is_ineligible(status):
    r=receive();promote(r)
    repo=EvidenceRepository();repo.save(repo.get('EV-1')|{'status':status})
    second=receive(version='2');prepare(second)
    assert mappings(second)['EV-1']['disposition']=='unresolved'
    with pytest.raises(BlueprintPromotionError): promote(second)


def test_similar_url_or_wording_does_not_merge_different_source_ids():
    r=receive([evidence(),evidence(external='EV-2')]);promote(r)
    assert {row['evidence_id'] for row in EvidenceRepository().list()}=={'EV-1','EV-2'}


def test_identity_decision_is_explicit_audited_and_not_a_legacy_rewrite():
    r=receive([dict(external_id='IND-1',record_class='industry_twin',truth_class='package_metadata',payload={}),evidence()])
    html,status=review_page(r.import_run_id,HEADERS)
    assert status==200 and '/identity' in html
    assert mappings(r)['EV-1']['disposition']=='unresolved'
    with pytest.raises(BlueprintPromotionError): promote(r)
    confirm(r)
    assert project_twin_identity(r).status=='recognised'
    assert GovernedIdentityResolutionRepository().get(r.import_run_id)['actor']=='alice'
    promote(r)
    with pytest.raises(ValueError,match='silently rewritten'):
        GovernedIdentityResolutionRepository().confirm_explicit(r,IDENTITY,'alice','test',HEADERS)


def test_identity_confirmation_requires_authority_and_complete_fields():
    r=receive()
    with pytest.raises(PermissionError):
        GovernedIdentityResolutionRepository().confirm_explicit(r,IDENTITY,'mallory','test',{'X-Flora-User':'mallory','X-Flora-Enterprises':'*','X-Flora-Roles':'package.review'})
    with pytest.raises(ValueError): GovernedIdentityResolutionRepository().confirm_explicit(r,{},'alice','test',HEADERS)


def test_target_changed_after_approval_fails_closed():
    r=receive();job,_=prepare(r);svc=CanonicalPromotionService()
    a=svc.approve_plan(r.import_run_id,job['plan_id'],'alice','test',HEADERS)
    EvidenceRepository().save({'evidence_id':'EV-1','enterprise_id':'synthetic-enterprise','quote':'Concurrent write'})
    with pytest.raises(BlueprintPromotionError,match='changed after review'): svc.execute_approved_plan(r.import_run_id,a.approval_id,'alice',HEADERS)
    assert not ImportLifecycleService().get(r.import_run_id).current


@pytest.mark.parametrize('interrupt',[False,True])
def test_receipt_failure_or_interruption_does_not_make_release_current(monkeypatch,interrupt):
    first=receive(identity=IDENTITY);promote(first)
    second=receive([evidence(),evidence(external='EV-2')],version='2',identity=IDENTITY)
    job,_=prepare(second);svc=CanonicalPromotionService()
    a=svc.approve_plan(second.import_run_id,job['plan_id'],'alice','test',HEADERS)
    save=svc.repo.save_result
    def fail(run,result):
        if result.final_execution_status=='succeeded':
            if interrupt: raise KeyboardInterrupt('Simulated hard interruption')
            raise OSError('Simulated receipt failure')
        return save(run,result)
    monkeypatch.setattr(svc.repo,'save_result',fail)
    with pytest.raises(KeyboardInterrupt if interrupt else BlueprintPromotionError): svc.execute_approved_plan(second.import_run_id,a.approval_id,'alice',HEADERS)
    assert ImportLifecycleService().get(first.import_run_id).current
    assert not ImportLifecycleService().get(second.import_run_id).current
    if not interrupt: assert not EvidenceRepository().get('EV-2')
    else:
        # Canonical files need operator recovery; lifecycle still shows old state.
        with pytest.raises(BlueprintPromotionError,match='backup'): svc.execute_approved_plan(second.import_run_id,a.approval_id,'alice',HEADERS)


W5=Path(__file__).resolve().parents[1]/'docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip'
RETAINED={
    'W5':(W5,'bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07'),
    'W6':(Path(os.getenv('FLORA_AUDIT_TEL_W6','/missing/TEL-W6.zip')),'c24cbf67c687883947fc4020b098c81c84b343e618980989b0af9665e2210ffb'),
    'BNK':(Path(os.getenv('FLORA_AUDIT_BNK_W1','/missing/BNK-W1.zip')),'1c2d18ebf0d48a32f4093c9ff7ce16a2e1203fedd2cc8ef3760367b033a56313')}


def retained(name):
    path,sha=RETAINED[name]
    if not path.exists(): pytest.skip(f'Actual retained {name} package unavailable; set FLORA_AUDIT_TEL_W6 / FLORA_AUDIT_BNK_W1')
    content=path.read_bytes();assert hashlib.sha256(content).hexdigest()==sha
    return receive(content=content)


def link_retained_identity(r,twin):
    # Explicit isolated owner decision, not producer metadata or production signoff.
    identity=IDENTITY|dict(twin_id=twin,primary_subject_id=twin,primary_subject_name='Isolated '+twin,canonical_owner=twin,governed_scope='UK '+twin)
    anchor=receive([],version='identity-anchor',owner=r.identity.enterprise_id,identity=identity)
    GovernedIdentityResolutionRepository().confirm_existing(r,anchor.package_ref,'alice','Explicit isolated linkage to governed fixture identity')
    return r


def accept_retained(r,twin):
    link_retained_identity(r,twin)
    svc,a,result=promote(r)
    assert result.final_execution_status=='succeeded'
    refs=mappings(r)
    for c in candidates(r):
        if c['candidate_object_class']=='evidence' and c['validation_status']=='accepted':
            m=refs[c['original_source_id']];row=EvidenceRepository().get(m['canonical_id'])
            assert row and row['source_payload']==c['payload']['source_payload']
            assert m['external_id']==row['source_external_id']
    # Verify each actual canonical supporting reference via the approved mapping.
    targets={m['canonical_id'] for m in refs.values() if m['record_class']=='evidence'}
    count=0
    for repo in svc.generic_repos.values():
        for row in repo.list():
            for source,target in (row.get('blueprint_import_lineage') or {}).get('evidence_id_bindings',{}).items():
                assert EvidenceRepository().get(target)
                if row['blueprint_import_lineage']['import_run_id']==r.import_run_id:
                    assert target in targets;count+=1
    assert count>0
    assert not svc.observation_repo.list() # existing wrapper/model boundary unchanged
    return svc,a,result


def test_retained_tel_w5_normal_ui_citation_binding():
    r=retained('W5');accept_retained(r,'IND-TEL-001')
    assert len(EvidenceRepository().list())==92
    assert all(EvidenceRepository().get(c['original_source_id']) for c in candidates(r) if c['candidate_object_class']=='evidence')


def test_retained_tel_w5_w6_reconciliation_and_replay():
    first=retained('W5');accept_retained(first,'IND-TEL-001')
    second=retained('W6');svc,a,result=accept_retained(second,'IND-TEL-001')
    rows=EvidenceRepository().list()
    assert len(rows)==102
    kinds=[m['reconciliation_kind'] for m in mappings(second).values() if m['record_class']=='evidence']
    assert kinds.count('unchanged')==92 and kinds.count('new')==10
    assert sum(len(row['source_release_provenance'])==2 for row in rows)==92
    assert ImportLifecycleService().get(first.import_run_id).state=='superseded'
    assert ImportLifecycleService().get(second.import_run_id).current
    assert svc.execute_approved_plan(second.import_run_id,a.approval_id,'alice',HEADERS).final_execution_status=='repeat_no_change'
    assert len(EvidenceRepository().list())==102


def test_retained_bnk_same_citation_contract():
    r=retained('BNK');accept_retained(r,'IND-BNK-001')
    assert len(EvidenceRepository().list())==65


def test_normal_ui_owner_approval_reports_partial_canonical_outcome():
    r=receive(identity=IDENTITY);job,_=prepare(r)
    html,status=approve_and_promote(r.import_run_id,{'plan_id':[job['plan_id']],'rationale':['Isolated owner decision'],'confirm_plan':['yes'],'confirm_mutations':['yes']},HEADERS)
    assert status==200 and 'Canonical Evidence reconciliation' in html
    assert 'do not establish complete Industry Twin acceptance' in html
    assert ImportLifecycleService().get(r.import_run_id).current
    assert ImportLifecycleService().get(r.import_run_id).acceptance_execution_id


def test_operator_can_record_explicit_mapping_without_ui_defaults_overwriting_it():
    from cios.applications.flora.blueprint_import import views
    r=receive();prepare(r)
    c=next(c for c in candidates(r) if c['candidate_object_class']=='evidence')
    html,status=views.record_evidence_mapping(r.import_run_id,{'candidate_id':[c['candidate_record_id']],'disposition':['propose_create'],'canonical_id':['OWNER-REBOUND'],'rationale':['Source ID collision owner decision'],'confirm_mapping':['yes']},HEADERS)
    assert status==200
    promote(r)
    assert EvidenceRepository().get('OWNER-REBOUND')
    assert not EvidenceRepository().get('EV-1')


def test_relationship_endpoints_and_citations_bind_without_rewriting_source_payload():
    r=receive([evidence(),dict(external_id='REL-1',record_class='relationship',truth_class='evidence_backed',payload={'relationship_source':'EV-1','source':'EV-1','references':['EV-1','ENT-1'],'evidence_refs':['EV-1'],'source_payload':{'evidence':['EV-1']}})])
    prepare(r);c=next(c for c in candidates(r) if c['candidate_object_class']=='evidence')
    ImportMappingService().record_mapping(c,'propose_create','alice',HEADERS,'Evidence','BOUND-EV','explicit target')
    svc,a,result=promote(r);row=svc.generic_repos['relationship'].list()[0]
    assert row['source']==row['relationship_source']=='BOUND-EV'
    assert row['references']==['BOUND-EV','ENT-1'] and row['evidence_refs']==['BOUND-EV']
    assert row['source_payload']=={'evidence':['EV-1']}


def test_missing_explicit_reuse_or_update_target_is_rejected():
    r=receive();prepare(r);c=candidates(r)[0]
    c=next(c for c in candidates(r) if c['candidate_object_class']=='evidence')
    for disposition in ('map_existing','propose_update'):
        with pytest.raises(PermissionError,match='does not exist'):
            ImportMappingService().record_mapping(c,disposition,'alice',HEADERS,'Evidence','MISSING','invalid target')


def test_foreign_explicit_target_rejected_even_with_wide_operator_access():
    first=receive(identity=IDENTITY);promote(first)
    second=receive([evidence()],version='2',owner='different-enterprise',identity=IDENTITY)
    c=next(c for c in candidates(second) if c['candidate_object_class']=='evidence')
    with pytest.raises(PermissionError,match='crosses Enterprise'):
        ImportMappingService().record_mapping(c,'map_existing','alice',HEADERS,'Evidence','EV-1','not allowed')


def test_identity_change_after_approval_invalidates_execution():
    r=receive(identity=IDENTITY);job,_=prepare(r);svc=CanonicalPromotionService()
    a=svc.approve_plan(r.import_run_id,job['plan_id'],'alice','test',HEADERS)
    confirm(r,IDENTITY|{'governed_scope':'different scope'})
    with pytest.raises(BlueprintPromotionError,match='identity changed'):
        svc.execute_approved_plan(r.import_run_id,a.approval_id,'alice',HEADERS)
    assert not EvidenceRepository().list()


def test_ambiguous_source_identity_fails_closed():
    r=receive(identity=IDENTITY);promote(r)
    row=EvidenceRepository().get('EV-1')
    EvidenceRepository().save(row|{'evidence_id':'DUPLICATE-TARGET'})
    second=receive(version='2',identity=IDENTITY);prepare(second)
    assert mappings(second)['EV-1']['disposition']=='unresolved'
    with pytest.raises(BlueprintPromotionError): promote(second)


def test_legacy_unknown_scope_requires_explicit_mapping_and_preserves_history():
    EvidenceRepository().save({'evidence_id':'EV-1','enterprise_id':'synthetic-enterprise','quote':'Original','source_url':'https://example.test/source'})
    r=receive(identity=IDENTITY);prepare(r)
    assert mappings(r)['EV-1']['disposition']=='unresolved'
    c=next(c for c in candidates(r) if c['candidate_object_class']=='evidence')
    ImportMappingService().record_mapping(c,'map_existing','alice',HEADERS,'Evidence','EV-1','Owner confirms legacy source scope')
    promote(r)
    assert len(EvidenceRepository().list())==1
    assert EvidenceRepository().get('EV-1')['quote']=='Original'


def test_retained_tel_count_reconciliation_independent_of_citation_assertions():
    first=retained('W5');link_retained_identity(first,'IND-TEL-001');promote(first)
    assert len(EvidenceRepository().list())==92
    second=retained('W6');link_retained_identity(second,'IND-TEL-001');promote(second)
    assert len(EvidenceRepository().list())==102 # baseline produces 194
    assert ImportLifecycleService().get(first.import_run_id).state=='superseded'


@pytest.mark.parametrize('status',['quarantined','rejected'])
def test_staging_ineligible_evidence_cannot_support_a_promoted_reference(status):
    from cios.applications.flora.storage import data_path,atomic_write_json
    r=receive();c=next(c for c in candidates(r) if c['candidate_object_class']=='evidence')
    path=data_path('blueprint_import','staging',r.import_run_id,'candidates',c['candidate_record_id']+'.json')
    atomic_write_json(path,c|{'validation_status':status})
    plan=prepare(r)[0];svc=CanonicalPromotionService()
    with pytest.raises(BlueprintPromotionError):
        a=svc.approve_plan(r.import_run_id,plan['plan_id'],'alice','test',HEADERS)
        svc.execute_approved_plan(r.import_run_id,a.approval_id,'alice',HEADERS)
    assert not EvidenceRepository().list()


def test_conflicting_aliases_fail_before_any_canonical_write():
    r=receive([evidence(id='ALIAS-1'),evidence('Different assertion',external='EV-2',id='ALIAS-1')])
    with pytest.raises(BlueprintPromotionError,match='Ambiguous source Evidence alias'):promote(r)
    assert not EvidenceRepository().list()


def test_same_package_ui_replay_changes_neither_rows_nor_provenance():
    r=receive(identity=IDENTITY);job,_=prepare(r)
    form={'plan_id':[job['plan_id']],'rationale':['Owner approval'],'confirm_plan':['yes'],'confirm_mutations':['yes']}
    _,status=approve_and_promote(r.import_run_id,form,HEADERS);assert status==200
    before=EvidenceRepository().get('EV-1')
    html,status=approve_and_promote(r.import_run_id,form,HEADERS)
    assert status==200 and 'repeat_no_change' in html
    assert EvidenceRepository().get('EV-1')==before


def test_existing_identity_link_cannot_relabel_an_accepted_release():
    r=receive(identity=IDENTITY);promote(r)
    anchor=receive([],version='anchor',identity=IDENTITY|{'governed_scope':'other scope'})
    with pytest.raises(ValueError,match='silently rewritten'):
        GovernedIdentityResolutionRepository().confirm_existing(r,anchor.package_ref,'alice','test')


def test_explicit_source_alias_reuse_preserves_both_source_identities():
    r=receive([evidence()],identity=IDENTITY);promote(r)
    second=receive([evidence(external='EV-2')],version='2',identity=IDENTITY);prepare(second)
    c=candidates(second)[0]
    ImportMappingService().record_mapping(c,'map_existing','alice',HEADERS,'Evidence','EV-1','Owner confirms identical source alias')
    promote(second)
    third=receive([evidence()],version='3',identity=IDENTITY);promote(third)
    assert len(EvidenceRepository().list())==1
    assert EvidenceRepository().get('EV-1')['source_external_id']=='EV-1'
    assert {row['original_external_id'] for row in EvidenceRepository().get('EV-1')['source_release_provenance']}=={'EV-1','EV-2'}


def test_confirmed_industry_overlay_applies_industry_scope_without_wrappers():
    from cios.applications.flora.blueprint_import.mapping import industry_package
    r=receive([evidence(freshness='expired')])
    confirm(r)
    assert industry_package(r)
    with pytest.raises(BlueprintPromotionError,match='inactive'):promote(r)
    assert not EvidenceRepository().list()


def test_source_status_alone_cannot_promote_expired_support_as_current():
    r=receive([evidence(status='expired')])
    with pytest.raises(BlueprintPromotionError,match='inactive'):promote(r)
    assert not EvidenceRepository().list()
