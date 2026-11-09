"""Repair 02 discovery: source boundaries, explicit identity and read-only access."""
from dataclasses import replace
from pathlib import Path
from hashlib import sha256
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import json,os
import pytest
from cios.applications.flora import digital_twins as dt
from cios.applications.flora.web import app
from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator
from cios.applications.flora.blueprint_import.lifecycle import ImportLifecycleService
from cios.applications.flora.blueprint_import.twin_governance import GovernedIdentityResolutionRepository
from cios.applications.flora.blueprint_import.review import mark_import_reviewed
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository,repair_enterprise_canvas_access
from cios.applications.flora.memory.repository import EnterpriseModelRepository
from cios.applications.flora.memory.models import EnterpriseUnknown,EnterpriseModelAttribute
from tests.test_flora_blueprint_import_validation import pkg
from tests.test_flora_experience_assurance_repair import visible

H={'X-Flora-User':'alice','X-Flora-Enterprises':'*','X-Flora-Roles':'blueprint_import_admin','X-Flora-Active-Workspace':'workspace-a'}
IDENTITY=dict(twin_id='IND-TEST',twin_type='industry',primary_subject_id='TEST-INDUSTRY',primary_subject_name='Synthetic industry',primary_subject_class='industry',governed_scope='UK',canonical_owner='TEST-INDUSTRY')

@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path/'data'));monkeypatch.setenv('FLORA_PILOT_DIR',str(tmp_path/'data'))
    monkeypatch.setenv('FLORA_ENVIRONMENT','development');monkeypatch.setenv('FLORA_TRUST_PROXY_HEADERS','1')
    from cios.applications.flora.enterprise_intelligence import pipeline
    from cios.applications.flora.blueprint_import import review_plan
    monkeypatch.setattr(pipeline.run_pipeline,'__defaults__',(tmp_path/'derived',None,None));monkeypatch.setattr(review_plan,'ASYNC_THRESHOLD',100000)


def receive(version='1.0',workspace='workspace-a',name='Synthetic industry',subject='TEST-INDUSTRY',stage=True,confirm=True):
    identity=IDENTITY|dict(twin_id='IND-'+subject,primary_subject_name=name,primary_subject_id=subject)
    p=BlueprintPackageRegistry().receive(pkg(manifest_extra=identity|{'package_version':version},records=[]),'wrong-enterprise-name.zip','alice',workspace)
    if stage:BlueprintPackageValidator().validate_and_stage(p.package_ref,'alice',H)
    p=BlueprintPackageRegistry().get(p.package_ref)
    if confirm:GovernedIdentityResolutionRepository().confirm_explicit(p,identity,'alice','Isolated synthetic identity',H)
    return BlueprintPackageRegistry().get(p.package_ref)


def imported(snapshot):return [i for i in snapshot.items if i.population=='industry_import']

def fixture_model(enterprise='test-airline',workspace='workspace-a',user='alice',persist=True):
    if persist:
        m=EnterpriseModelRepository().get(enterprise);m.unknowns['TEST-UNKNOWN']=EnterpriseUnknown('TEST-UNKNOWN',enterprise,'Synthetic missing buyer evidence','commercial');EnterpriseModelRepository().save(m)
    return repair_enterprise_canvas_access(enterprise,workspace,user)


def files():
    p=Path(os.environ['FLORA_DATA_DIR']);return {str(f.relative_to(p)):sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}


def test_empty_storage_exposes_curated_banking_without_inventing_a_twin():
    s=dt.intelligence_discovery(H)
    assert len(s.items)==1 and s.items[0].population=='curated'
    assert s.items[0].status=='Source-curated' and s.items[0].destination=='/flora/banking'
    assert s.items[0].meaningful_update=='Unknown'
    assert EnterpriseCanvasAccessRepository().list()==[]
    for html in (app._flora_home_page(H),app._flora_intelligence_page(H,{'tab':['industries']}),dt.digital_twins_landing_page(H)):
        text=visible(html);assert 'Curated repository Banking pilot' in text and 'Intelligence discovery' in text
        assert '1 governed' not in text


def test_candidate_and_reviewed_source_packages_use_existing_workspace():
    p=receive();s=imported(dt.intelligence_discovery(H));assert len(s)==1
    assert s[0].status=='Candidate' and s[0].destination==f'/blueprint-import/{p.import_run_id}/intelligence'
    mark_import_reviewed(p.import_run_id,H,'isolated-review-fingerprint')
    i=imported(dt.intelligence_discovery(H))[0];assert i.status=='Under review'
    assert 'not promoted' in i.availability and dict(i.identities)['Import run']==p.import_run_id


def test_current_partial_release_uses_owner_status_not_complete_acceptance():
    p=receive();ImportLifecycleService().mark_promoted(p.import_run_id,'alice',1)
    i=imported(dt.intelligence_discovery(H))[0]
    assert i.status=='Partially promoted' and i.current is True and i.owner_state=='promoted'
    assert 'complete Industry Twin acceptance' in ' '.join(i.unknowns)
    assert i.meaningful_update=='Unknown' and i.event_kind=='Release lifecycle event'
    assert not EnterpriseCanvasAccessRepository().list()


def test_superseded_release_stays_distinct_and_inspectable():
    old=receive('1.0');new=receive('2.0');life=ImportLifecycleService()
    life.mark_promoted(old.import_run_id,'alice',1);life.mark_promoted(new.import_run_id,'alice',1);life.mark_superseded(old.import_run_id,'alice',new.import_run_id)
    rows=imported(dt.intelligence_discovery(H));assert len(rows)==2
    by={dict(i.identities)['Import run']:i for i in rows}
    assert by[old.import_run_id].status=='Superseded' and by[old.import_run_id].current is False
    assert by[new.import_run_id].current is True and by[old.import_run_id].destination!=by[new.import_run_id].destination
    text=visible(dt.digital_twins_landing_page(H));assert 'Superseded' in text and 'Current release: No' in text


def test_receipt_date_does_not_become_intelligence_update_and_unstaged_is_inspection(monkeypatch):
    p=receive(stage=False);p=replace(p,received_at='2099-12-31T00:00:00Z');monkeypatch.setattr(BlueprintPackageRegistry,'list',lambda self:[p])
    i=imported(dt.intelligence_discovery(H))[0];assert i.meaningful_update=='Unknown'
    assert i.destination==f'/blueprint-import/{p.import_run_id}/inspect'
    assert '2099' not in visible(dt.digital_twins_landing_page(H))


def test_authorised_persisted_model_and_canvas_are_discoverable_but_not_fully_assured():
    record=fixture_model();rows=[i for i in dt.intelligence_discovery(H).items if i.population=='enterprise_canvas'];assert len(rows)==1
    i=rows[0];assert i.status=='Model-backed' and i.destination=='/digital-twins/test-airline/canvas'
    assert dict(i.identities)['Canonical Enterprise']=='test-airline' and i.meaningful_update=='Unknown'
    assert 'complete Commercial Digital Twin assurance' in ' '.join(i.unknowns)


def test_only_explicit_current_model_material_date_is_displayed():
    fixture_model();repo=EnterpriseModelRepository();m=repo.get('test-airline')
    m.attributes['enterprise.latest_material_change']=EnterpriseModelAttribute('enterprise','latest_material_change','2026-04-02',50,'2026-05-01','current',(),(),'synthetic-test');repo.save(m)
    i=next(i for i in dt.intelligence_discovery(H).items if i.population=='enterprise_canvas');assert i.meaningful_update=='2026-04-02'


def test_no_canvas_access_means_no_model_backed_entry_or_registration():
    p=receive();m=EnterpriseModelRepository().get('unregistered-test');EnterpriseModelRepository().save(m)
    assert not [i for i in dt.intelligence_discovery(H).items if i.population=='enterprise_canvas']
    assert EnterpriseCanvasAccessRepository().list()==[]
    assert imported(dt.intelligence_discovery(H))[0].destination.endswith('/intelligence')


def test_existing_canvas_without_model_is_explicitly_unavailable_not_model_backed():
    fixture_model(persist=False)
    i=next(i for i in dt.intelligence_discovery(H).items if i.population=='enterprise_canvas')
    assert i.status=='Unavailable' and 'model unavailable' in i.availability
    assert i.meaningful_update=='Unknown'


@pytest.mark.parametrize('who',[{},H|{'X-Flora-User':'mallory','X-Flora-Enterprises':'none','X-Flora-Roles':''},H|{'X-Flora-Active-Workspace':'workspace-b'}])
def test_no_item_names_counts_ids_or_destinations_leak_to_wrong_context(who):
    p=receive(name='Protected Source Name');fixture_model('protected-test')
    s=dt.intelligence_discovery(who);assert len(s.items)==1 and not imported(s)
    for html in (dt.digital_twins_landing_page(who),app._flora_intelligence_page(who,{'tab':['industries']}),app._flora_home_page(who)):
        assert 'Protected Source Name' not in html and p.import_run_id not in html and 'protected-test' not in html
        assert p.package_ref not in html and '/digital-twins/protected' not in html


def test_canvas_acl_is_required_even_with_wildcard_enterprise_access():
    fixture_model(user='other-owner');assert not [i for i in dt.intelligence_discovery(H).items if i.population=='enterprise_canvas']


def test_equal_display_names_do_not_merge_source_import_and_model_identity():
    a=receive('1.0',name='Barclays',subject='EXPLICIT-ONE');b=receive('2.0',name='Barclays',subject='EXPLICIT-TWO');fixture_model('barclays-plc')
    s=dt.intelligence_discovery(H);assert len(imported(s))==2
    assert len({i.key for i in s.items})==len(s.items)
    for i in imported(s):
        assert 'Canonical Enterprise' not in dict(i.identities)
        assert dict(i.identities)['Primary subject'] in {'EXPLICIT-ONE','EXPLICIT-TWO'}
        assert i.destination.startswith('/blueprint-import/')


def test_missing_identity_is_unresolved_never_filled_from_zip_name():
    p=receive(confirm=False);BlueprintPackageRegistry().update_inspection(p.package_ref,{'twin_id':None,'governed_scope':None,'primary_subject_id':None,'canonical_owner':None})
    i=imported(dt.intelligence_discovery(H))[0]
    assert i.identity_status=='ambiguous' and 'unresolved' in ' '.join(i.unknowns).lower()
    assert 'wrong-enterprise-name' not in i.name and 'Canonical Enterprise' not in dict(i.identities)


def test_discovery_does_not_call_canvas_repair_or_write_any_owner_state(monkeypatch):
    receive();fixture_model();before=files()
    from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
    def forbidden(*a,**kw):raise AssertionError('discovery invoked mutating Canvas path')
    monkeypatch.setattr(EnterpriseCanvasService,'get_canvas',forbidden)
    dt.intelligence_discovery(H);dt.digital_twins_landing_page(H);app._flora_home_page(H);app._flora_intelligence_page(H)
    assert files()==before


def test_inspection_aliases_reach_the_same_existing_view():
    server=ThreadingHTTPServer(('127.0.0.1',0),app.FloraWebHandler);thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        responses=[]
        for path in ['/industries/uk-banking','/flora/banking/inspect']:
            try:
                with urlopen(Request(f'http://127.0.0.1:{server.server_port}'+path,headers=H)) as r:responses.append((r.status,r.read().decode()))
            except HTTPError as exc:responses.append((exc.code,exc.read().decode()))
        assert [r[0] for r in responses]==[200,200]
        assert all('Curated repository Banking pilot' in r[1] for r in responses)
        assert responses[0][1]==responses[1][1]
    finally:server.shutdown();server.server_close();thread.join()


@pytest.mark.parametrize('name',['TEL-W5','TEL-W6','BNK-W1'])
def test_actual_retained_packages_use_generic_discovery_and_keep_factory_boundaries(name):
    from tests import test_flora_factory_presentation_repair as retained
    path,_=retained.ARTIFACTS[name]
    if not path.exists():pytest.skip('Actual retained artifact unavailable: '+name)
    BlueprintPackageRegistry().receive(path.read_bytes(),path.name,'alice','workspace-a')
    retained.test_actual_retained_user_journey_and_honest_promotion(name)
    s=dt.intelligence_discovery(H);rows=imported(s);assert len(rows)==1
    assert rows[0].status=='Partially promoted' and rows[0].current is True
    assert rows[0].destination.endswith('/intelligence') and rows[0].meaningful_update=='Unknown'
    assert rows[0].owner_state=='promoted' and 'complete Industry Twin acceptance' in ' '.join(rows[0].unknowns)
    assert not [i for i in s.items if i.population=='enterprise_canvas']
    out=os.getenv('FLORA_DISCOVERY_EVIDENCE')
    if out:
        from dataclasses import asdict
        dest=Path(out)/name;dest.mkdir(parents=True,exist_ok=True)
        (dest/'discovery.json').write_text(json.dumps({'items':[asdict(i) for i in s.items],'data_root':os.environ['FLORA_DATA_DIR']},indent=2))
        (dest/'directory.html').write_text(dt.digital_twins_landing_page(H))
    if name=='BNK-W1':
        run=dict(rows[0].identities)['Import run']
        # An isolated lifecycle transition, not a claim of a real accepted successor.
        ImportLifecycleService().mark_superseded(run,'alice','synthetic-successor-fixture')
        historical=imported(dt.intelligence_discovery(H))[0]
        assert historical.status=='Superseded' and historical.current is False
        from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
        assert executive_workspace_page(run,H)[1]==200
        if out:
            (dest/'historical.json').write_text(json.dumps({'item':asdict(historical),'transition':'Synthetic lifecycle-only fixture; no real successor accepted'},indent=2))


def test_mismatched_model_payload_is_unavailable_without_cross_identity_link():
    fixture_model('allowed-test');path=EnterpriseModelRepository().path_for('allowed-test')
    data=json.loads(path.read_text());data['enterprise_id']='private-other-model';path.write_text(json.dumps(data))
    s=dt.intelligence_discovery(H)
    assert 'Enterprise Canvas' in s.unavailable_sources
    assert not [i for i in s.items if i.population=='enterprise_canvas']
    html=dt.digital_twins_landing_page(H)
    assert 'private-other-model' not in html and '/digital-twins/allowed-test/canvas' not in html


def test_industry_intake_inspection_never_sends_identity_to_enterprise_canvas():
    from cios.applications.flora.blueprint_import.views import validation_result_page
    p=receive(stage=False);html,status=validation_result_page(p.import_run_id,H)
    assert status==200 and f'/blueprint-import/{p.import_run_id}/intelligence' in html
    assert '/canvas' not in html


@pytest.mark.parametrize('value,observed,trust',[('2099-01-01','2026-01-01','trusted'),('2026-01-01','2099-01-01','trusted'),('2026-01-01','2026-01-01','retired')])
def test_future_or_retired_model_attributes_are_not_meaningful_updates(value,observed,trust):
    fixture_model();repo=EnterpriseModelRepository();m=repo.get('test-airline')
    m.attributes['enterprise.latest_material_change']=EnterpriseModelAttribute('enterprise','latest_material_change',value,50,observed,'current',(),(),'synthetic-test',trust_state=trust);repo.save(m)
    i=next(i for i in dt.intelligence_discovery(H).items if i.population=='enterprise_canvas')
    assert i.meaningful_update=='Unknown'


def test_anonymous_discovery_does_not_read_protected_owner_stores(monkeypatch):
    def protected(*a,**kw):raise AssertionError('anonymous discovery read protected store')
    monkeypatch.setattr(BlueprintPackageRegistry,'list',protected)
    monkeypatch.setattr(EnterpriseCanvasAccessRepository,'list',protected)
    s=dt.intelligence_discovery({});assert len(s.items)==1 and s.items[0].population=='curated'


def test_unreadable_owner_state_is_generic_unavailable_not_raw_metadata(monkeypatch):
    def corrupt(*a,**kw):raise ValueError('private-source-sentinel')
    monkeypatch.setattr(BlueprintPackageRegistry,'list',corrupt)
    s=dt.intelligence_discovery(H);assert 'Industry imports' in s.unavailable_sources
    html=dt.render_intelligence_discovery(s)
    assert 'details unavailable' in html and 'private-source-sentinel' not in html
    assert 'Source-curated' in visible(html)

# Domain tests use an explicit fixture identity provider, never HTTP trust.
pytestmark = pytest.mark.usefixtures("verified_flora_test_authority")
