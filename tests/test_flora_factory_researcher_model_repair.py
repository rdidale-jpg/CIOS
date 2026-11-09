"""Repair 02 isolated handoff, actual retained packages and canonical graph gates."""
import hashlib
import json
import os
from pathlib import Path
import pytest

from tests.test_flora_blueprint_import_validation import pkg
from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator, CandidateReviewService
from cios.applications.flora.blueprint_import import researcher_profile_adapter as adapter
from cios.applications.flora.blueprint_import.views import approve_and_promote
from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService, CanonicalJsonlRepository, BlueprintPromotionError
from cios.applications.flora.blueprint_import.review_plan import BlueprintReviewPlanCoordinator
from cios.applications.flora.blueprint_import.mapping import ImportMappingRepository
from cios.applications.flora.blueprint_import.lifecycle import ImportLifecycleService
from cios.applications.flora.blueprint_import.twin_governance import GovernedIdentityResolutionRepository
from cios.applications.flora.memory.repository import EvidenceRepository, ObservationRepository, EnterpriseModelRepository
from cios.applications.flora.enterprise_intelligence.retrieval import BoundedTwinRetrievalService
from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page

HEADERS={'X-Flora-User':'alice','X-Flora-Enterprises':'*','X-Flora-Roles':'blueprint_import_admin'}
IDENTITY=dict(twin_id='IND-SYN',twin_type='industry',primary_subject_id='IND-SYN',primary_subject_name='Synthetic industry',primary_subject_class='industry',governed_scope='UK',canonical_owner='IND-SYN')
CLAIM='Synthetic Enterprise announced a new data platform.'

@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path));monkeypatch.setenv('FLORA_PILOT_DIR',str(tmp_path))
    monkeypatch.setenv('FLORA_ENVIRONMENT','development');monkeypatch.setenv('FLORA_TRUST_PROXY_HEADERS','1')
    from cios.applications.flora.blueprint_import import review_plan
    monkeypatch.setattr(review_plan,'ASYNC_THRESHOLD',100000)


def rows(claim=CLAIM,**changes):
    source=dict(id='EV-1',supported_claim=claim,publication_date='2026-01-01',collection_date='2026-01-02',confidence=80,url='https://example.test/source',supported_object='ENT-ONE')
    source.update(changes)
    return [dict(external_id='EV-1',record_class='evidence',truth_class='evidence_backed',payload=adapter.adapt_researcher_payload('evidence',source)[1]),
            dict(external_id='ENT-ONE',record_class='enterprise_twin',truth_class='package_metadata',payload=adapter.adapt_researcher_payload('enterprise_twin',{'id':'ENT-ONE','name':'Synthetic Enterprise','evidence':['EV-1']})[1])]


def receive(content=None,records=None,version='1.0'):
    reg=BlueprintPackageRegistry()
    r=reg.receive(content or pkg(records=records or rows(),manifest_extra=IDENTITY|{'package_version':version}),'retained.zip','alice')
    BlueprintPackageValidator().validate_and_stage(r.package_ref,'alice',HEADERS)
    r=reg.get(r.package_ref)
    if content: GovernedIdentityResolutionRepository().confirm_explicit(r,IDENTITY,'alice','Isolated owner identity fixture',HEADERS)
    return r


def candidates(r):return BlueprintPackageValidator().staging_summary(r.import_run_id)['candidates']


def prepare(r):
    html,status=prepare_review(r.import_run_id,HEADERS);assert status==200
    job=BlueprintReviewPlanCoordinator().latest_job(r.import_run_id)
    assert job['status'] in {'Ready','Not ready'},job
    return job,html


def handoff(r,wrapper='ENT-ONE',evidence='EV-1',enterprise='ent-one',attribute='events.data_platform',**kw):
    c=next(c for c in candidates(r) if c['original_source_id']==wrapper)
    return adapter.stage_observation_handoff(r.import_run_id,c['candidate_record_id'],evidence,enterprise,
           'enterprise_event_announced',attribute,'alice','Explicit enterprise ownership and verbatim source claim',HEADERS,selected_subset=True,**kw)


def approve(r,c):
    CandidateReviewService().record_decision(c['candidate_record_id'],'approve','alice','Reviewed exact source claim and target enterprise',HEADERS)


def promote(r):
    job,html=prepare(r);assert job['status']=='Ready',job
    page,status=approve_and_promote(r.import_run_id,{'plan_id':[job['plan_id']],'confirm_plan':['yes'],'confirm_mutations':['yes'],'rationale':['Isolated selected subset approval']},HEADERS)
    assert status==200,page[-2500:]
    return page


def assert_consumers(enterprise,statement):
    model=EnterpriseModelRepository().get(enterprise)
    assert len(model.attributes)==1 and next(iter(model.attributes.values())).current_value==statement
    request=ReasoningRequestV1.create(enterprise,enterprise,'alice',evidence_cut_off='2026-11-08')
    retrieved=BoundedTwinRetrievalService().retrieve(request)
    assert retrieved.selected_observations and [i for i in retrieved.all_items() if i.object_class=='evidence']
    assert retrieved.selected_observations[0].statement==statement
    from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
    canvas=EnterpriseCanvasService().get_canvas(enterprise,HEADERS)
    html,status=enterprise_canvas_page(enterprise,HEADERS,canvas.tiles[0].tile_view_id)
    from html import unescape
    assert status==200 and statement in unescape(html)
    assert 'Model Explorer' in html and 'governed' in html.lower()
    assert not model.material_pressures
    return retrieved,html


def test_governed_handoff_is_separately_reviewed_and_uses_existing_consumers():
    r=receive();prepare(r);c=handoff(r)
    assert not ObservationRepository().list() and not EvidenceRepository().list()
    assert not EnterpriseModelRepository().get('ent-one').attributes
    from cios.applications.flora.blueprint_import.review import CandidateReviewRepository
    assert CandidateReviewRepository().latest_by_candidate(r.import_run_id)[c['candidate_record_id']]['decision']=='defer'
    prepare(r)
    assert CandidateReviewRepository().latest_by_candidate(r.import_run_id)[c['candidate_record_id']]['decision']=='defer'
    approve(r,c);page=promote(r)
    assert 'partial' in page.lower()
    assert '/digital-twins/ent-one/canvas' in page and 'Accepted model views' in page
    assert len(ObservationRepository().list())==1
    obs=ObservationRepository().list()[0]
    assert EvidenceRepository().get(obs.supporting_evidence_ids[0])['enterprise_id']=='ent-one'
    assert obs.human_provenance['source_date']=='2026-01-01'
    assert_consumers('ent-one',CLAIM)


@pytest.mark.parametrize('changes',[{'publication_date':'2026'},{'collection_date':'Unknown'},{'publication_date':'2099-01-01'}, {'status':'rejected'},{'freshness':'expired'},{'effective_date':'2099-01-01'},{'verified':False},{'supported_claim':'The enterprise may buy a new platform.'},{'supported_claim':'A new platform launched; revenue increased.'}])
def test_unsupported_handoff_preserves_candidate_only(changes):
    r=receive(records=rows(**changes))
    with pytest.raises((ValueError,PermissionError)):handoff(r)
    assert not ObservationRepository().list() and not EvidenceRepository().list()


def test_wrong_enterprise_or_unlinked_evidence_is_rejected():
    r=receive()
    with pytest.raises(ValueError):handoff(r,evidence='MISSING')
    handoff(r)
    with pytest.raises(ValueError,match='another enterprise'):handoff(r,enterprise='other-enterprise')


def test_owner_permission_required_for_target_enterprise():
    r=receive();c=next(c for c in candidates(r) if c['original_source_id']=='ENT-ONE')
    with pytest.raises(PermissionError):
        adapter.stage_observation_handoff(r.import_run_id,c['candidate_record_id'],'EV-1','ent-one','enterprise_event_announced','events.test','mallory','test',{'X-Flora-User':'mallory','X-Flora-Enterprises':'synthetic-enterprise','X-Flora-Roles':'package.review'},selected_subset=True)


def test_reimport_and_release_history_do_not_duplicate_confidence():
    r=receive();c=handoff(r);approve(r,c);promote(r)
    before=EnterpriseModelRepository().get('ent-one').to_dict();promote(r)
    assert EnterpriseModelRepository().get('ent-one').to_dict()==before
    second=receive(version='2.0');c2=handoff(second);approve(second,c2);promote(second)
    assert len(ObservationRepository().list())==1
    assert len(EvidenceRepository().list())==1
    assert len(EvidenceRepository().list()[0]['source_release_provenance'])==2
    assert EnterpriseModelRepository().get('ent-one').to_dict()==before
    assert ImportLifecycleService().get(r.import_run_id).state=='superseded'


def test_tampered_staging_invalidates_owner_approval():
    from cios.applications.flora.storage import data_path,atomic_write_json
    r=receive();c=handoff(r);approve(r,c);job,_=prepare(r)
    svc=CanonicalPromotionService();a=svc.approve_plan(r.import_run_id,job['plan_id'],'alice','test',HEADERS)
    c['payload']['atomic_statement']='A substituted unsupported claim.'
    atomic_write_json(data_path('blueprint_import','staging',r.import_run_id,'candidates',c['candidate_record_id']+'.json'),c)
    with pytest.raises(BlueprintPromotionError,match='changed after approval'):svc.execute_approved_plan(r.import_run_id,a.approval_id,'alice',HEADERS)
    assert not ObservationRepository().list()


def test_rejected_selected_evidence_cannot_support_handoff():
    r=receive();c=handoff(r);approve(r,c)
    source=next(c for c in candidates(r) if c['original_source_id']=='EV-1')
    CandidateReviewService().record_decision(source['candidate_record_id'],'reject','alice','Rejected',HEADERS)
    job,_=prepare(r);svc=CanonicalPromotionService()
    with pytest.raises(BlueprintPromotionError):
        a=svc.approve_plan(r.import_run_id,job['plan_id'],'alice','test',HEADERS)
        svc.execute_approved_plan(r.import_run_id,a.approval_id,'alice',HEADERS)
    assert not ObservationRepository().list()


def test_dangling_domain_edges_are_deferred_without_creating_wrappers():
    extra=dict(external_id='REL-1',record_class='relationship',truth_class='evidence_backed',payload={'source':'ENT-ONE','target':'OPP-NOT-CANONICAL'})
    r=receive(records=rows()+[extra]);job,_=prepare(r)
    from cios.applications.flora.blueprint_import.planning import DryRunPlanRepository
    plan=CanonicalPromotionService()._load_plan(r.import_run_id,job['plan_id'])
    effect=next(e for e in plan['effects'] if e['record_class']=='relationship')
    assert effect['effect_type']=='defer' and 'endpoints unresolved' in effect['reason']
    promote(r)
    assert not CanonicalJsonlRepository('relationship').list()
    assert not CanonicalJsonlRepository('entity').list()


def test_existing_governed_endpoints_allow_relationships():
    CanonicalJsonlRepository('entity').save({'canonical_id':'ENTITY-A','enterprise_id':'synthetic-enterprise'})
    CanonicalJsonlRepository('entity').save({'canonical_id':'ENTITY-B','enterprise_id':'synthetic-enterprise'})
    rel=dict(external_id='REL-1',record_class='relationship',truth_class='evidence_backed',payload={'source':'ENTITY-A','target':'ENTITY-B'})
    r=receive(records=[rel]);prepare(r);promote(r)
    assert len(CanonicalJsonlRepository('relationship').list())==1


W5=Path(__file__).resolve().parents[1]/'docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip'
ARTIFACTS={
 'TEL-W5':(W5,'bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07','ENT-VODAFONETHREE','EV-VT-OWN-COMPLETE26'),
 'TEL-W6':(Path(os.getenv('FLORA_AUDIT_TEL_W6','/missing/W6.zip')),'c24cbf67c687883947fc4020b098c81c84b343e618980989b0af9665e2210ffb','ENT-VODAFONETHREE','EV-VT-OWN-COMPLETE26'),
 'BNK-W1':(Path(os.getenv('FLORA_AUDIT_BNK_W1','/missing/BNK.zip')),'1c2d18ebf0d48a32f4093c9ff7ce16a2e1203fedd2cc8ef3760367b033a56313','ENT-BARCLAYS','EV-BARCLAYS-MICROSOFT-COPILOT-2025')}


@pytest.mark.parametrize('name',ARTIFACTS)
def test_actual_retained_source_to_memory_retrieval_and_view(name):
    path,sha,wrapper,ev=ARTIFACTS[name]
    if not path.exists():pytest.skip('Retained artifact unavailable: '+name)
    content=path.read_bytes();assert hashlib.sha256(content).hexdigest()==sha
    r=receive(content=content);initial,_=prepare(r)
    plan=CanonicalPromotionService()._load_plan(r.import_run_id,initial['plan_id'])
    graph=[e for e in plan['effects'] if e['record_class']=='relationship']
    offered=adapter.handoff_offers(candidates(r));counts={'wrappers':sum(c['candidate_object_class']=='enterprise_twin' for c in candidates(r)),'candidate_assertions':len(offered),'supported_atomic_candidates':sum(not o['reason'] for o in offered),'deferred_assertions':sum(bool(o['reason']) for o in offered)}
    c=handoff(r,wrapper,ev,wrapper.lower(),'events.researcher_source_announcement')
    assert not EvidenceRepository().list() and not ObservationRepository().list()
    approve(r,c);promote(r)
    obs=ObservationRepository().list()[0];retrieved,html=assert_consumers(wrapper.lower(),obs.atomic_statement)
    assert EvidenceRepository().get(obs.supporting_evidence_ids[0])['source_payload']==c['payload']['source_payload']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
    assert not CanonicalJsonlRepository('relationship').list()
    counts.update(package_sha256=sha,approved_observations=1,model_attributes=1,evidence_refs_resolved=len(obs.supporting_evidence_ids),canonical_relationships=0,source_relationships=len(graph),unresolved_source_edges=sum(e['effect_type']=='defer' for e in graph),unresolved_endpoint_diagnostics=[e['reason'] for e in graph if e['effect_type']=='defer'][:8],retrieval_observations=sum(i.object_class=='observation' for i in retrieved.selected_observations),retrieval_evidence=len([i for i in retrieved.all_items() if i.object_class=='evidence']),view_visible_facts=1)
    output=os.getenv('FLORA_REPAIR02_EVIDENCE')
    if output:
        root=Path(output);root.mkdir(exist_ok=True,parents=True)
        (root/(name+'.json')).write_text(json.dumps(counts,indent=2))
        (root/(name+'-canvas.html')).write_text(html)


def test_explicit_wrong_enterprise_source_is_not_reassigned():
    r=receive(records=rows(canonical_enterprise_id='some-other-enterprise'))
    with pytest.raises(ValueError,match='another enterprise'):handoff(r)
    assert not ObservationRepository().list()


def test_uncertainty_dates_and_historical_retrieval_are_preserved():
    r=receive(records=rows(effective_date='2025-12-31',uncertainty='Source reports announcement, implementation not verified'))
    c=handoff(r);approve(r,c);promote(r)
    obs=ObservationRepository().list()[0]
    assert obs.human_provenance['effective_date']=='2025-12-31'
    assert obs.human_provenance['researcher_handoff']['uncertainty']=='Source reports announcement, implementation not verified'
    result=BoundedTwinRetrievalService().retrieve(ReasoningRequestV1.create('ent-one','ent-one','alice',evidence_cut_off='2025-12-30'))
    assert not result.selected_observations and not result.selected_entities_and_relationships


def test_explicit_source_contradiction_is_not_promoted_as_certain():
    r=receive(records=rows(contradiction_state='unresolved'))
    with pytest.raises(ValueError,match='contradiction'):handoff(r)
    assert not ObservationRepository().list()


def test_missing_selected_evidence_after_review_blocks_memory_write():
    from cios.applications.flora.storage import data_path
    r=receive();c=handoff(r);approve(r,c)
    source=next(c for c in candidates(r) if c['original_source_id']=='EV-1')
    data_path('blueprint_import','staging',r.import_run_id,'candidates',source['candidate_record_id']+'.json').unlink()
    job,_=prepare(r);svc=CanonicalPromotionService()
    with pytest.raises(BlueprintPromotionError):svc.approve_plan(r.import_run_id,job['plan_id'],'alice','test',HEADERS)
    assert not ObservationRepository().list()


def test_operator_handoff_and_review_actions_do_not_write_canonical_memory():
    from cios.applications.flora.blueprint_import import views
    r=receive();prepare(r)
    wrapper=next(c for c in candidates(r) if c['original_source_id']=='ENT-ONE')
    form={'wrapper_id':[wrapper['candidate_record_id']],'evidence_source_id':['EV-1'],'enterprise_id':['ent-one'],'observation_type':['enterprise_event_announced'],'attribute':['events.data_platform'],'rationale':['Owner confirms source and target identity'],'confirm_handoff':['yes'],'confirm_subset':['yes']}
    html,status=views.stage_researcher_observation(r.import_run_id,form,HEADERS)
    assert status==200 and 'Researcher-to-Model handoff' in html
    obs=next(c for c in candidates(r) if c['candidate_object_class']=='observation')
    _,status=views.review_researcher_observation(r.import_run_id,{'candidate_id':[obs['candidate_record_id']],'decision':['approve'],'rationale':['Reviewed source']},HEADERS)
    assert status==200 and not EvidenceRepository().list() and not ObservationRepository().list()
    promote(r);assert_consumers('ent-one',CLAIM)


def test_already_accepted_industry_evidence_is_not_copied_to_enterprise():
    r=receive();prepare(r);promote(r)
    assert EvidenceRepository().list()[0]['enterprise_id']=='synthetic-enterprise'
    second=receive(version='2.0')
    with pytest.raises(ValueError,match='already accepted'):handoff(second)
    assert len(EvidenceRepository().list())==1


def test_partial_staging_failure_does_not_inherit_automatic_observation_approval(monkeypatch):
    from cios.applications.flora.blueprint_import.mapping import ImportMappingService
    from cios.applications.flora.blueprint_import.review import CandidateReviewRepository
    r=receive();prepare(r)
    original=ImportMappingService.record_mapping
    calls=[]
    def fail(self,*args,**kwargs):
        calls.append(1)
        if len(calls)==2:raise OSError('Simulated staging mapping failure')
        return original(self,*args,**kwargs)
    monkeypatch.setattr(ImportMappingService,'record_mapping',fail)
    with pytest.raises(OSError):handoff(r)
    monkeypatch.setattr(ImportMappingService,'record_mapping',original)
    prepare(r)
    obs=next(c for c in candidates(r) if c['candidate_object_class']=='observation')
    assert CandidateReviewRepository().latest_by_candidate(r.import_run_id)[obs['candidate_record_id']]['decision']=='defer'
    assert not ObservationRepository().list() and not EvidenceRepository().list()


def test_foreign_canonical_graph_endpoint_requires_access(monkeypatch):
    rel=dict(external_id='REL-1',record_class='relationship',truth_class='evidence_backed',payload={'source':'A1','target':'B1'})
    CanonicalJsonlRepository('entity').save({'canonical_id':'A1','enterprise_id':'synthetic-enterprise'})
    CanonicalJsonlRepository('entity').save({'canonical_id':'B1','enterprise_id':'unrelated-enterprise'})
    r=receive(records=[rel])
    from cios.applications.flora.blueprint_import.planning import DryRunPlanningService
    from cios.applications.flora.blueprint_import.semantic_twin import canonical_relationship_endpoints
    cs=candidates(r)
    result=canonical_relationship_endpoints(cs[0],r,cs,[],{},HEADERS|{'X-Flora-Enterprises':'synthetic-enterprise'})
    assert result['unresolved'] and result['target'] is None


def test_explicit_enterprise_mapping_resolves_planned_model_endpoint():
    rel=dict(external_id='REL-1',record_class='relationship',truth_class='evidence_backed',payload={'source':'ENT-ONE','target':'EV-1'})
    r=receive(records=rows()+[rel]);c=handoff(r);approve(r,c)
    edge=next(c for c in candidates(r) if c['candidate_object_class']=='relationship')
    CandidateReviewService().record_decision(edge['candidate_record_id'],'approve','alice','Reviewed governed endpoints',HEADERS)
    promote(r)
    row=CanonicalJsonlRepository('relationship').list()[0]
    assert row['source']=='ent-one' and row['target']=='EV-1'
    assert EnterpriseModelRepository().get(row['source']).attributes
    assert EvidenceRepository().get(row['target'])


def test_reviewed_updated_source_preserves_old_observation_and_model_history():
    from cios.applications.flora.blueprint_import.mapping import ImportMappingService
    r=receive();c=handoff(r);approve(r,c);promote(r)
    old=ObservationRepository().list()[0]
    statement='Synthetic Enterprise launched its data platform.'
    second=receive(records=rows(statement,publication_date='2026-02-01',collection_date='2026-02-02',supersedes_observation_id=old.observation_id),version='2.0')
    updated=handoff(second);approve(second,updated)
    source=next(c for c in candidates(second) if c['original_source_id']=='EV-1')
    ImportMappingService().record_mapping(source,'propose_update','alice',HEADERS,'Evidence','EV-1','Reviewed revised source and dates')
    promote(second)
    assert len(ObservationRepository().list())==2
    assert ObservationRepository().get(old.observation_id)
    assert ObservationRepository().get(updated['payload']['observation_id']).supersedes_observation_id==old.observation_id
    assert EnterpriseModelRepository().get('ent-one').attributes['events.data_platform'].current_value==statement
    assert EvidenceRepository().get('EV-1')['blueprint_import_lineage']['prior_canonical_version']['summary']==CLAIM


def test_actual_tel_w5_w6_handoff_reuses_observation_and_confidence_history():
    selected=[]
    for name in ['TEL-W5','TEL-W6']:
        path,sha,wrapper,ev=ARTIFACTS[name]
        if not path.exists():pytest.skip('Retained artifact unavailable: '+name)
        content=path.read_bytes();assert hashlib.sha256(content).hexdigest()==sha
        r=receive(content=content);prepare(r)
        c=handoff(r,wrapper,ev,wrapper.lower(),'events.researcher_source_announcement')
        approve(r,c);promote(r)
        selected.append(r)
        model=EnterpriseModelRepository().get(wrapper.lower())
        if name=='TEL-W5':before=model.to_dict()
        else:assert model.to_dict()==before
    assert len(ObservationRepository().list())==1
    assert len(EvidenceRepository().list())==1
    assert len(EvidenceRepository().list()[0]['source_release_provenance'])==2
    assert ImportLifecycleService().get(selected[0].import_run_id).state=='superseded'
    assert ImportLifecycleService().get(selected[1].import_run_id).current
    before=EnterpriseModelRepository().get(wrapper.lower()).to_dict();promote(selected[1])
    assert EnterpriseModelRepository().get(wrapper.lower()).to_dict()==before


def test_existing_entity_owner_resolves_through_accepted_import_lineage():
    rel=dict(external_id='REL-1',record_class='relationship',truth_class='evidence_backed',payload={'source':'ENTITY-A','target':'ENTITY-B'})
    r=receive(records=[rel])
    CanonicalJsonlRepository('entity').save({'canonical_id':'ENTITY-A','blueprint_import_lineage':{'package_id':r.package_ref}})
    CanonicalJsonlRepository('entity').save({'canonical_id':'ENTITY-B','enterprise_id':'synthetic-enterprise'})
    prepare(r);promote(r)
    assert len(CanonicalJsonlRepository('relationship').list())==1

# Domain tests use an explicit fixture identity provider, never HTTP trust.
pytestmark = pytest.mark.usefixtures("verified_flora_test_authority")

from tests.flora_security_fixtures import prepare_review
