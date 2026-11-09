"""Repair 03: import-scoped presentation, governed identities and truthful counts."""
from dataclasses import replace
from html import unescape
from pathlib import Path
import hashlib
import json
import os
import time
import pytest

from tests.test_industry_twin_semantic_reconciliation import row
from tests.test_flora_blueprint_import_validation import pkg
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, enterprise_associations, opportunity_enterprise_names
from cios.applications.flora.blueprint_import.key_reports import key_reports_for_enterprise
from cios.applications.flora.blueprint_import.canonical_factual_projection import enterprise_factual_dimensions
from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator
from cios.applications.flora.blueprint_import.views import completion_page,approve_and_promote
from cios.applications.flora.blueprint_import import review_plan
from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page,_semantic_candidates
from cios.applications.flora.blueprint_import.twin_governance import GovernedIdentityResolutionRepository
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page
from cios.applications.flora.memory.repository import EnterpriseModelRepository

HEADERS={'X-Flora-User':'alice','X-Flora-Enterprises':'*','X-Flora-Roles':'blueprint_import_admin','X-Flora-Active-Workspace':'workspace-a'}
IDENTITY=dict(twin_id='IND-TEST',twin_type='industry',primary_subject_id='IND-TEST',primary_subject_name='Isolated industry',primary_subject_class='industry',governed_scope='UK',canonical_owner='IND-TEST')

@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path));monkeypatch.setenv('FLORA_PILOT_DIR',str(tmp_path))
    monkeypatch.setenv('FLORA_ENVIRONMENT','development');monkeypatch.setenv('FLORA_TRUST_PROXY_HEADERS','1')
    monkeypatch.setattr(review_plan,'ASYNC_THRESHOLD',100000)


def banking_rows():
    return [row('ENT-BARCLAYS','enterprise_twin',{'enterprise_name':'Barclays PLC','evidence':['EV-AR'],'financial_position':{'economic_model':'Source-supplied banking economics narrative.','current_signal':'Source interpretation, not a numeric financial fact.','latest_reporting':['EV-AR']}}),
            row('ENT-OTHER','enterprise_twin',{'enterprise_name':'Other Bank'}),
            row('PROG-B','transformation_programme',{'title':'Supplied bank programme','objective':'Supplied programme objective','evidence_refs':['EV-AR']}),
            row('OPP-B','opportunity_hypothesis',{'title':'Supplied commercial hypothesis','client_problem':'Source supplied problem','evidence_refs':['EV-AR']}),
            row('R-P','relationship',{'source':'ENT-BARCLAYS','target':'PROG-B','relationship_type':'Owner owns Programme'}),
            row('R-O','relationship',{'source':'ENT-BARCLAYS','target':'OPP-B','relationship_type':'Enterprise has Opportunity Hypothesis'}),
            row('EV-AR','evidence',{'title':'Barclays PLC Annual Report 2025','supported_object':'Barclays','publisher':'Other Publisher','evidence_quality':'Primary source','url':'https://example.test/annual.pdf','publication_date':'2026-02-10','supported_claim':'Source report context.'})]


def test_banking_associations_are_typed_directional_and_shared_by_customer_view():
    twin=assemble_semantic_twin(banking_rows());ent=next(e for e in twin.enterprises if e.name=='Barclays PLC')
    assert {r[0].original_id for r in enterprise_associations(twin,ent,{'transformation_programme','opportunity_hypothesis'})}=={'PROG-B','OPP-B'}
    other=next(e for e in twin.enterprises if e.name=='Other Bank')
    assert not enterprise_associations(twin,other,{'transformation_programme','opportunity_hypothesis'})
    opp=next(o for o in twin.objects if o.original_id=='OPP-B')
    assert opportunity_enterprise_names(twin,opp)==('Barclays PLC',)


@pytest.mark.parametrize('kind',['Owner owns Programme','Enterprise has Opportunity Hypothesis'])
def test_reverse_or_wrong_family_edges_do_not_create_associations(kind):
    rows=banking_rows();edge=next(r for r in rows if r['payload'].get('relationship_type')==kind)
    edge['payload']['source'],edge['payload']['target']=edge['payload']['target'],edge['payload']['source']
    twin=assemble_semantic_twin(rows);ent=next(e for e in twin.enterprises if e.name=='Barclays PLC')
    excluded='PROG-B' if kind=='Owner owns Programme' else 'OPP-B'
    assert excluded not in {r[0].original_id for r in enterprise_associations(twin,ent,{'transformation_programme','opportunity_hypothesis'})}


def test_financial_position_uses_existing_dimension_and_retains_source_evidence():
    ent=assemble_semantic_twin(banking_rows()).enterprises[0]
    dim=next(d for d in enterprise_factual_dimensions(ent) if d.key=='financial')
    assert dim.present and any('Source-supplied banking economics narrative' in s for s in dim.values)
    assert dim.evidence_refs==('EV-AR',)
    assert not EnterpriseModelRepository().get(ent.identity_key).attributes
    other=next(e for e in assemble_semantic_twin(banking_rows()).enterprises if e.name=='Other Bank')
    assert not next(d for d in enterprise_factual_dimensions(other) if d.key=='financial').present


def test_barclays_report_uses_explicit_governed_alias_not_publisher():
    twin=assemble_semantic_twin(banking_rows());ent=next(e for e in twin.enterprises if e.name=='Barclays PLC')
    report=key_reports_for_enterprise(ent,twin)
    assert report.company_report and report.company_report.source.original_id=='EV-AR'
    assert report.company_report.publisher=='Other Publisher'


@pytest.mark.parametrize('subject',['','Unknown subject','Barclays UK','Other Bank'])
def test_missing_competitor_or_group_subject_is_not_guessed(subject):
    rows=banking_rows();rows[-1]['payload']['supported_object']=subject;rows[-1]['payload']['publisher']='Barclays PLC'
    twin=assemble_semantic_twin(rows);ent=next(e for e in twin.enterprises if e.name=='Barclays PLC')
    assert not key_reports_for_enterprise(ent,twin).company_report


def test_duplicate_explicit_report_subject_alias_remains_ambiguous():
    rows=banking_rows();rows[1]['payload']['aliases']=['Barclays']
    twin=assemble_semantic_twin(rows)
    assert not any(key_reports_for_enterprise(e,twin).company_report for e in twin.enterprises)


def test_producer_supplied_alias_is_resolved_without_legal_suffix_guessing():
    rows=banking_rows();rows[0]['payload']['enterprise_name']='Example Holdings Limited';rows[0]['payload']['aliases']=['Example group report subject'];rows[-1]['payload']['supported_object']='Example group report subject'
    twin=assemble_semantic_twin(rows);ent=next(e for e in twin.enterprises if e.name=='Example Holdings Limited')
    assert key_reports_for_enterprise(ent,twin).company_report
    rows[0]['payload'].pop('aliases');rows[-1]['payload']['supported_object']='Example Holdings'
    twin=assemble_semantic_twin(rows);ent=next(e for e in twin.enterprises if e.name=='Example Holdings Limited')
    assert not key_reports_for_enterprise(ent,twin).company_report


def receive(records=None,content=None,industry=True):
    r=BlueprintPackageRegistry().receive(content or pkg(records=records or [],manifest_extra=IDENTITY if industry else None),'isolated.zip','alice',HEADERS['X-Flora-Active-Workspace'])
    BlueprintPackageValidator().validate_and_stage(r.package_ref,'alice',HEADERS)
    return BlueprintPackageRegistry().get(r.package_ref)


def test_industry_completion_opens_existing_workspace_and_does_not_create_enterprise_canvas_access():
    r=receive();page=completion_page(r.import_run_id,{'final_execution_status':'succeeded'},HEADERS)
    assert f"href='/blueprint-import/{r.import_run_id}/intelligence'" in page
    assert 'Open Industry Twin workspace' in page and 'Open Enterprise Canvas' not in page
    assert EnterpriseCanvasAccessRepository().get(r.identity.enterprise_id) is None
    assert 'Complete Industry Twin acceptance' in page and 'Not established' in page
    assert 'Not verified from an approval record' in page


def test_enterprise_completion_preserves_enterprise_canvas_navigation():
    r=receive(industry=False);page=completion_page(r.import_run_id,{'final_execution_status':'succeeded'},HEADERS)
    assert 'Open Enterprise Canvas' in page


def test_generic_canvas_has_no_mod_strategy_or_receipt_material_change():
    r=receive([{'external_id':'PP-1','record_class':'pain_point','truth_class':'analytical_projection','payload':{'statement':'Source-supplied context'}}],industry=False)
    from cios.applications.flora.enterprise_canvas.access import repair_blueprint_canvas_access
    repair_blueprint_canvas_access(r.import_run_id,HEADERS)
    canvas=EnterpriseCanvasService().get_canvas(r.identity.enterprise_id,HEADERS)
    assert canvas.header.latest_material_change=='Unknown'
    assert all(tile.material_change!=r.received_at for tile in canvas.tiles)
    html,status=enterprise_canvas_page(r.identity.enterprise_id,HEADERS)
    assert status==200 and 'MOD is being read' not in html and 'governed MOD Twin records' not in html
    assert 'durable model intelligence unavailable' in html


def test_mod_specific_read_model_is_retained_without_claiming_receipt_is_material_change():
    r=BlueprintPackageRegistry().receive(pkg(records=[{'external_id':'PP','record_class':'pain_point','truth_class':'analytical_projection','payload':{'statement':'MOD source context'}}],manifest_extra={'enterprise_id':'MOD'}),'mod.zip','alice')
    BlueprintPackageValidator().validate_and_stage(r.package_ref,'alice',HEADERS)
    from cios.applications.flora.enterprise_canvas.access import repair_blueprint_canvas_access
    repair_blueprint_canvas_access(r.import_run_id,HEADERS)
    canvas=EnterpriseCanvasService().get_canvas('MOD',HEADERS)
    assert canvas.header.enterprise_name=='MOD' and canvas.header.latest_material_change=='Unknown'
    html,status=enterprise_canvas_page('MOD',HEADERS)
    assert status==200 and 'Model Explorer' in html


def test_review_counts_partition_staged_support_nonpersistable_and_canonical_effects():
    from cios.applications.flora.blueprint_import.review_plan import review_effect_counts
    cs=[{'candidate_record_id':str(i),'candidate_object_class':rc,'validation_status':'accepted'} for i,rc in enumerate(['evidence','enterprise_twin','source','relationship'])]
    effects=[{'candidate_id':str(i),'record_class':rc,'effect_type':'defer' if rc=='relationship' else 'mapped' if rc=='source' else 'create','expected_mutation_count':1 if rc=='evidence' else 0} for i,rc in enumerate(['evidence','enterprise_twin','source','relationship'])]
    p,rec=review_effect_counts(cs,effects)
    assert p['Creates']==1 and p['Accepted but non-persistable']==1 and p['Accepted support records']==1
    assert rec['accepted_staged']==4 and rec['accepted_canonical']==2 and rec['counts_reconcile'] and rec['passes']


def test_failed_completion_does_not_claim_successful_partial_promotion_or_model_acceptance():
    r=receive();page=completion_page(r.import_run_id,{'final_execution_status':'failed','model_projection_results':[{'enterprise_id':'wrong','status':'applied'}]},HEADERS)
    assert 'Canonical promotion not successful' in page and 'Accepted model views' not in page


W5=Path(__file__).resolve().parents[1]/'docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip'
ARTIFACTS={
'TEL-W5':(W5,'bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07'),
'TEL-W6':(Path(os.getenv('FLORA_AUDIT_TEL_W6','/missing/W6.zip')),'c24cbf67c687883947fc4020b098c81c84b343e618980989b0af9665e2210ffb'),
'BNK-W1':(Path(os.getenv('FLORA_AUDIT_BNK_W1','/missing/BNK.zip')),'1c2d18ebf0d48a32f4093c9ff7ce16a2e1203fedd2cc8ef3760367b033a56313')}


@pytest.mark.parametrize('name',ARTIFACTS)
def test_actual_retained_user_journey_and_honest_promotion(name):
    path,sha=ARTIFACTS[name]
    if not path.exists():pytest.skip('Actual retained artifact not available: '+name)
    content=path.read_bytes();assert hashlib.sha256(content).hexdigest()==sha
    r=receive(content=content)
    identity=IDENTITY|dict(twin_id='IND-BNK-001' if name=='BNK-W1' else 'IND-TEL-001',primary_subject_id='BNK-001' if name=='BNK-W1' else 'TEL-001',primary_subject_name='UK Banking and Financial Services (isolated test)' if name=='BNK-W1' else 'UK Telecommunications (isolated test)',canonical_owner='BNK-001' if name=='BNK-W1' else 'TEL-001')
    GovernedIdentityResolutionRepository().confirm_explicit(r,identity,'alice','Isolated workflow identity decision',HEADERS)
    summary=BlueprintPackageValidator().staging_summary(r.import_run_id)
    twin=assemble_semantic_twin(_semantic_candidates(r,summary['candidates']))
    timings={};pages={}
    def render(tag,**kwargs):
        started=time.perf_counter();html,status=executive_workspace_page(r.import_run_id,HEADERS,**kwargs)
        assert status==200
        assert 'MOD is being read' not in html and 'governed MOD Twin records' not in html
        timings[tag]=round(time.perf_counter()-started,3);pages[tag]=html;return html
    overview=render('industry-overview')
    ent=next(e for e in twin.enterprises if e.name==('Barclays PLC' if name=='BNK-W1' else 'VodafoneThree'))
    dossier=render('enterprise-dossier',view='enterprise',enterprise_id=ent.presentation_key)
    assert f'/blueprint-import/{r.import_run_id}/aspects/enterprises' in overview and 'Evidence and Uncertainty' in dossier
    directory=render('enterprise-directory',view='aspect',collection='enterprises')
    assert ent.presentation_key in directory
    assert "id='enterprise-opportunities'" in dossier and "href='#enterprise-opportunities'" in dossier
    assoc=enterprise_associations(twin,ent,{'transformation_programme','opportunity_hypothesis'})
    if name=='BNK-W1':
        assert {o.original_id for o,_,_ in assoc}>={'PROG-BARCLAYS-M365-COPILOT','OPP-BARCLAYS-AI-CYBER-CONTROLS'}
        assert 'Source-supplied financial narrative' in dossier and 'investment-bank markets/advisory income' in dossier
        assert key_reports_for_enterprise(ent,twin).company_report.source.original_id=='EV-BARCLAYS-AR2025'
        assert 'Source-backed candidate research' in dossier and 'Association lineage' in dossier
    render('financial-context',view='enterprise',enterprise_id=ent.presentation_key)
    programmes=render('programmes-opportunities',view='aspect',collection='major-programmes')
    assert 'Major Programmes' in programmes and 'Aspect unavailable' not in programmes
    render('evidence-provenance',view='explore',collection='evidence-sources')
    html,status=prepare_review(r.import_run_id,HEADERS);assert status==200
    job=review_plan.BlueprintReviewPlanCoordinator().latest_job(r.import_run_id)
    assert job['status']=='Ready' and job['reconciliation']['counts_reconcile']
    assert job['proposed']['Accepted but non-persistable']>0
    done,status=approve_and_promote(r.import_run_id,{'plan_id':[job['plan_id']],'confirm_plan':['yes'],'confirm_mutations':['yes'],'rationale':['Isolated package mechanics; canonical subset only']},HEADERS)
    assert status==200 and 'Open Industry Twin workspace' in done
    assert 'Partial canonical promotion' in done and 'Not established' in done
    assert EnterpriseCanvasAccessRepository().get(r.identity.enterprise_id) is None
    pages['promotion-completion']=done
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
    output=os.getenv('FLORA_REPAIR03_EVIDENCE')
    if output:
        root=Path(output)/name;root.mkdir(parents=True,exist_ok=True)
        for tag,html in pages.items():(root/(tag+'.html')).write_text(html)
        (root/'evidence.json').write_text(json.dumps({'sha256':sha,'import_run_id':r.import_run_id,'isolated_data_root':os.environ['FLORA_DATA_DIR'],'enterprise':ent.name,'associations':[{'id':o.original_id,'type':kind,'relationship_id':ref} for o,kind,ref in assoc],'latency_seconds':timings,'proposed':job['proposed'],'reconciliation':job['reconciliation'],'class_persistence_readiness':job['class_persistence_readiness']},indent=2))


def test_aspect_research_requirements_preserve_existing_filtered_output():
    from cios.applications.flora.blueprint_import.research_requirements import research_requirements
    from cios.applications.flora.blueprint_import.intelligence_projection import executive_assessments
    twin=assemble_semantic_twin(banking_rows());projections=executive_assessments(twin)
    assert research_requirements(twin,projections,aspect='enterprises')==tuple(r for r in research_requirements(twin,projections) if r.aspect=='enterprises')


def test_review_status_counts_do_not_hide_blocking_canonical_mappings():
    from cios.applications.flora.blueprint_import.review_plan import review_effect_counts
    p,rec=review_effect_counts([{'candidate_record_id':'one','candidate_object_class':'evidence','validation_status':'accepted'}],[{'candidate_id':'one','record_class':'evidence','effect_type':'unresolved','expected_mutation_count':0}])
    assert rec['counts_reconcile'] and not rec['passes'] and rec['blocking_canonical_candidates']==['one']


def test_shared_report_remains_parent_company_disclosure_only():
    rows=banking_rows();rows[-1]['payload']['supported_object']='Barclays; Other Bank';rows[1]['payload']['evidence']=['EV-AR']
    twin=assemble_semantic_twin(rows)
    parent=next(e for e in twin.enterprises if e.name=='Barclays PLC');child=next(e for e in twin.enterprises if e.name=='Other Bank')
    assert key_reports_for_enterprise(parent,twin).company_report
    assert not key_reports_for_enterprise(child,twin).company_report

# Domain tests use an explicit fixture identity provider, never HTTP trust.
pytestmark = pytest.mark.usefixtures("verified_flora_test_authority")

from tests.flora_security_fixtures import prepare_review
