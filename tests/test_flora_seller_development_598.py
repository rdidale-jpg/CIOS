"""Real isolated authority, seller evidence distinctions and atomic Pipeline handoff."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import json
import pytest
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_offers_v1 import actor,pilot
from tests.test_flora_sales_pipeline import web
from tests.test_flora_offer_library_587 import preferences,adopt
from cios.applications.flora import offers,seller_development as dev,sales_pipeline as pipeline
from cios.applications.flora.research_intelligence import buying_evidence

pytestmark=pytest.mark.real_security_boundary
IDS=list(buying_evidence.OFFER_DIMENSIONS)


def setup(pilot,index=0,slug='santander-uk',who='seller',approve=True):
    with pilot['store'].transaction() as db:
        db.execute('UPDATE memberships SET enterprises=? WHERE user_id IN (?,?,?)',(json.dumps(['BK-ENT-001','BK-ENT-005','BK-ENT-003','AV-ENT-001']),'pilot-seller','pilot-reviewer','synthetic-human'))
    preferences(pilot,('consulting','data','cyber','engineering','advisory'),who=who)
    h=pilot[who];r=adopt(pilot,IDS[index],who=who)[0]
    if approve:
        r=offers.save_offer({'evidence':'Example fixture delivery and rights review; not real seller proof'},r['id'],r['version'],headers=h)
        r=offers.transition(r['id'],r['version'],'submit',headers=h)
        r=offers.transition(r['id'],r['version'],'approve','Example separate employer review',headers=pilot['reviewer'])
    assessment=next(a for a in offers.discover('offer',r['id'],intelligence=True,headers=h) if a['enterprise_slug']==slug)
    shortlist=offers.save_shortlist(r['id'],r['version'],pilot['employer']['version'],'2026-11-13',buying_evidence.DATA_SHA256,[assessment['assessment_id']],'Example reviewed shortlist',confirmed=True,headers=h)
    return dev.create(shortlist['id'],shortlist['version'],assessment['assessment_id'],True,headers=h)


def validated_values(state='Qualify'):
    return {'state':state,'challenge':'Example fixture customer reports an unresolved journey ownership decision',
        'insight':'Example fixture insight: test service continuity against the conditional plan',
        'diagnostic':'Example customer-permitted one-journey diagnostic and acceptance record',
        'proof':'Example separately reviewed delivery evidence and permitted rights; fixture only',
        'alternatives':'Example incumbent plan and supported retention alternative reviewed',
        'next_action':'Example seller owner to review a customer-approved journey map with the programme function',
        'customer_attested':True,'reviewed':True,
        'qualification':{key:{'note':'Example fixture '+label+' evidence; not a real customer claim',
            'source':'Private example meeting/reference '+key,'kind':'Customer statement' if key not in {'competition','differentiation'} else 'Seller review','date':'2026-11-13'} for key,(label,_) in pipeline.CRITERIA.items()}}


def test_versioned_private_candidate_snapshot_and_idempotent_creation(pilot):
    r=setup(pilot);assert r['version']==1 and r['state']=='Investigate' and r['pipeline_id'] is None
    assert r['assessment_snapshot']['buying_trigger']['identity_scope']['slug']=='santander-uk'
    assert 'conditional' in r['first_conversation'] and 'separate legal entities' in r['first_conversation']
    assert all(x['status']=='Hypothesis' for x in r['buying_group'].values())
    s=offers.shortlist_snapshot(headers=pilot['seller'])[0]
    again=dev.create(s['id'],s['version'],s['entries'][0]['assessment_id'],True,headers=pilot['seller']);assert again==r
    assert not pipeline._path().exists()
    revised=dev.save(r['id'],1,{'challenge':'Example hypothesis only','next_action':'Example ask for permission'},headers=pilot['seller'])
    assert revised['version']==2 and not revised['reviewed']
    with pytest.raises(ValueError):dev.save(r['id'],1,{'challenge':'stale overwrite'},headers=pilot['seller'])
    history=offers._load()['users'][offers._key(offers._actor(pilot['seller']))]['development'][r['id']]
    assert len(history)==2 and history[0]['challenge']==''


@pytest.mark.parametrize('who',['owner','reviewer','outsider','foreign'])
def test_private_candidate_all_reads_and_writes_deny_other_principals(pilot,who):
    r=setup(pilot);before=offers._path().read_bytes()
    for call in [lambda:dev.records(r['id'],headers=pilot[who]),lambda:dev.save(r['id'],1,{},headers=pilot[who]),lambda:dev.reassess(r['id'],1,True,headers=pilot[who]),lambda:dev.handoff(r['id'],1,True,headers=pilot[who])]:
        with pytest.raises((ValueError,PermissionError)):call()
    assert offers._path().read_bytes()==before and not pipeline._path().exists()


@pytest.mark.parametrize('index,slug',[(0,'santander-uk'),(3,'santander-uk'),(1,'lloyds'),(2,'computacenter'),(4,'lloyds')])
def test_five_pilots_retain_distinct_hypotheses_and_never_auto_qualify(pilot,index,slug):
    r=setup(pilot,index,slug);v=dev.records(r['id'],headers=pilot['seller'])
    assert not v['qualification_review']['ready'] and not v['stale'] and not pipeline._path().exists()
    with pytest.raises(ValueError):dev.handoff(r['id'],1,True,headers=pilot['seller'])
    if index==4:
        assert r['assessment_snapshot']['buying_trigger']['tier']=='Research only'
        with pytest.raises(ValueError):dev.save(r['id'],1,validated_values(),headers=pilot['seller'])
    elif slug=='computacenter':
        assert 'framework' in r['first_conversation'] and 'assurance' in r['diagnostic']
        with pytest.raises(ValueError,match='unbound identity'):dev.save(r['id'],1,validated_values(),headers=pilot['seller'])
    elif index==1:
        assert 'process' in r['first_conversation'] and 'non-AI' in r['first_conversation']
        with pytest.raises(ValueError):dev.save(r['id'],1,{'state':'Validate','challenge':'AI use-case growth'},headers=pilot['seller'])


@pytest.mark.parametrize('state',['Validate','Create Preference','Qualify'])
def test_internal_progress_does_not_establish_customer_validation(pilot,state):
    r=setup(pilot);before=offers._path().read_bytes()
    with pytest.raises(ValueError):dev.save(r['id'],1,{'state':state,'customer_attested':True,'reviewed':True},headers=pilot['seller'])
    assert before==offers._path().read_bytes() and not pipeline._path().exists()


@pytest.mark.parametrize('change',[{'kind':'Public evidence'},{'kind':'Seller hypothesis'},{'source':'BTI-TSB-TRANSFER'},{'date':'2099-01-01'},{'date':''},{'source':'Unknown'}])
def test_public_and_unsupported_evidence_cannot_be_customer_confirmation(pilot,change):
    r=setup(pilot);v=validated_values();v['qualification']['problem'].update(change);before=offers._path().read_bytes()
    with pytest.raises(ValueError):dev.save(r['id'],1,v,headers=pilot['seller'])
    assert offers._path().read_bytes()==before and not pipeline._path().exists()


def test_deliberate_stages_pause_retire_resume_and_customer_attestation_reset(pilot):
    r=setup(pilot)
    for step in dev.STEPS[1:]:r=dev.save(r['id'],r['version'],validated_values(step),headers=pilot['seller'])
    assert r['state']=='Qualify' and not pipeline._path().exists()
    r=dev.save(r['id'],r['version'],{'activity':'Paused'},headers=pilot['seller']);assert not r['reviewed']
    with pytest.raises(ValueError):dev.handoff(r['id'],r['version'],True,headers=pilot['seller'])
    r=dev.save(r['id'],r['version'],{'activity':'Retired'},headers=pilot['seller'])
    r=dev.save(r['id'],r['version'],validated_values()|{'activity':'Active'},headers=pilot['seller'])
    assert r['state']=='Qualify' and dev.records(r['id'],headers=pilot['seller'])['qualification_review']['ready']


def test_explicit_qualified_handoff_uses_pipeline_contract_and_is_idempotent(pilot):
    independent=pipeline.create_opportunity('lloyds',values={'title':'Example independent opportunity','problem':'Example pre-existing notes'},headers=pilot['seller'])
    before=deepcopy(independent);r=setup(pilot);r=dev.save(r['id'],1,validated_values(),headers=pilot['seller'])
    with pytest.raises(ValueError):dev.handoff(r['id'],r['version'],False,headers=pilot['seller'])
    opp=dev.handoff(r['id'],r['version'],True,headers=pilot['seller'])
    assert opp['stage']=='Qualified' and opp['evidence_reviewed'] and not pipeline.qualification(opp)['missing']
    assert opp['amount']=='' and opp['value_basis']=='Unknown' and opp['demonstration'] is True
    assert pipeline.evidence_maturity(opp)['customer']=='Customer-validated · not established'
    assert r['id'] in str(opp['history'])
    again=dev.handoff(r['id'],r['version'],True,headers=pilot['seller']);assert again==opp
    assert len(pipeline.list_opportunities(headers=pilot['seller']))==2
    assert pipeline.get_opportunity(before['id'],headers=pilot['seller'])==before
    assert dev.records(r['id'],headers=pilot['seller'])['pipeline_id']==opp['id']
    with pytest.raises(ValueError):dev.save(r['id'],r['version']+1,{'challenge':'overwrite'},headers=pilot['seller'])


@pytest.mark.parametrize('phase',['update','link'])
def test_atomic_handoff_rolls_back_both_files_and_audit_on_failure(pilot,monkeypatch,phase):
    r=setup(pilot);r=dev.save(r['id'],1,validated_values(),headers=pilot['seller']);before=offers._path().read_bytes()
    original=offers._persist
    def fail(*args,**kw):
        if args[2]=='development_pipeline_handoff':raise OSError('Example injected final link failure')
        return original(*args,**kw)
    if phase=='link':monkeypatch.setattr(offers,'_persist',fail)
    else:monkeypatch.setattr(pipeline,'update_opportunity',lambda *a,**k:(_ for _ in ()).throw(OSError('Example failure')))
    with pytest.raises(OSError):dev.handoff(r['id'],r['version'],True,headers=pilot['seller'])
    assert offers._path().read_bytes()==before and not pipeline._path().exists()


def test_source_cancellation_drift_preserves_notes_and_never_mutates_pipeline(pilot,monkeypatch):
    r=setup(pilot);r=dev.save(r['id'],1,{'challenge':'Example seller note retained'},headers=pilot['seller']);before=offers._path().read_bytes()
    original=offers.discover
    def cancelled(*args,**kwargs):
        rows=original(*args,**kwargs)
        for a in rows:
            if a['enterprise_slug']=='santander-uk':
                a['buying_trigger']['timeline']=[];a['buying_trigger']['research_digest']='example-cancelled-test-only';a['buying_trigger']['tier']='Research only';a['buying_trigger']['stage']='No current trigger found'
        return rows
    monkeypatch.setattr(offers,'discover',cancelled)
    view=dev.records(r['id'],headers=pilot['seller']);assert view['stale'] and 'fact:BTI-TSB-MIGRATION' in view['changed_dependencies']
    assert view['challenge']=='Example seller note retained' and offers._path().read_bytes()==before
    with pytest.raises(ValueError):dev.save(r['id'],r['version'],validated_values(),headers=pilot['seller'])
    new=dev.reassess(r['id'],r['version'],True,headers=pilot['seller']);assert new['challenge']==r['challenge'] and new['state']=='Investigate'
    assert new['assessment_snapshot']['buying_trigger']['tier']=='Research only' and not pipeline._path().exists()


def test_offer_and_entry_play_revision_and_acl_revocation(pilot,monkeypatch):
    from cios.applications.flora import buying_entry_plays
    r=setup(pilot);before=offers._path().read_bytes()
    monkeypatch.setattr(buying_entry_plays,'REVISION','example-revision')
    assert 'entry_play' in dev.records(r['id'],headers=pilot['seller'])['changed_dependencies']
    assert offers._path().read_bytes()==before
    with pilot['store'].transaction() as db:db.execute('UPDATE memberships SET enterprises=? WHERE user_id=?',(json.dumps(['BK-ENT-001']),'pilot-seller'))
    assert dev.records(headers=pilot['seller'])==[]
    with pytest.raises(PermissionError):dev.records(r['id'],headers=pilot['seller'])


@pytest.mark.parametrize('values',[{'workspace_id':'other'},{'author':'other'},{'pipeline_id':'forged'},{'state':'Qualified'},{'buying_group':{'Invented name':{}}}])
def test_scope_and_pipeline_fields_cannot_be_injected(pilot,values):
    r=setup(pilot);before=offers._path().read_bytes()
    with pytest.raises((ValueError,PermissionError)):dev.save(r['id'],1,values,headers=pilot['seller'])
    assert before==offers._path().read_bytes()


def test_real_http_acl_csrf_origin_escaping_and_gets_preserve_store(pilot,web):
    r=setup(pilot,who='owner');before=offers._path().read_bytes()
    assert web('/flora/offers/development',authenticated=False)[0]==403
    status,html,_=web('/flora/offers/development?candidate='+r['id']);assert status==200 and 'First conversation' in html
    assert html.count('aria-label="Primary product navigation"')==1 and html.count('Sources &amp; method')<=1
    assert offers._path().read_bytes()==before
    payload={'candidate':r['id'],'version':'1','state':'Investigate','challenge':'<script>example</script>'}
    assert web('/flora/offers/development-save',payload|{'csrf':'forged'})[0]==403
    assert web('/flora/offers/development-save',payload|{'workspace_id':'foreign'})[0]==403
    assert web('/flora/offers/development-save',payload)[0]==303
    status,html,_=web('/flora/offers/development?candidate='+r['id']);assert status==200 and '&lt;script&gt;example&lt;/script&gt;' in html and '<script>example</script>' not in html
    assert web('/flora/offers/development-handoff',{'candidate':r['id'],'version':'2','confirmed':'yes'})[0]==403
    assert not pipeline._path().exists() and offers.snapshot(headers=pilot['owner'])['studio_enabled'] is False


@pytest.mark.parametrize('field',['challenge','proof','alternatives','next_action'])
def test_unknown_commercial_inputs_do_not_qualify(pilot,field):
    r=setup(pilot);v=validated_values();v[field]='Unknown'
    with pytest.raises(ValueError):dev.save(r['id'],1,v,headers=pilot['seller'])
    assert not pipeline._path().exists()


def test_private_offer_is_developable_but_cannot_qualify(pilot):
    r=setup(pilot,approve=False)
    assert r['assessment_snapshot']['buying_trigger']['tier']=='Investigate'
    with pytest.raises(ValueError,match='employer approval'):dev.save(r['id'],1,validated_values(),headers=pilot['seller'])
    assert not pipeline._path().exists()


def test_offer_change_preserves_candidate_and_blocks_promotion(pilot):
    r=setup(pilot);offer=next(x for x in offers.snapshot(headers=pilot['seller'])['offers'] if x['id']==r['offer_id'] and x['current'])
    offers.save_offer({'entry_play':'Example revised entry play'},offer['id'],offer['version'],headers=pilot['reviewer'])
    view=dev.records(r['id'],headers=pilot['seller']);assert view['stale'] and 'offer' in view['changed_dependencies']
    assert view['assessment_snapshot']==r['assessment_snapshot'] and not pipeline._path().exists()


def test_wrong_origin_on_real_development_write_is_denied(pilot,actor):
    from http.server import ThreadingHTTPServer
    from http.client import HTTPConnection
    from urllib.parse import urlencode
    import threading
    from cios.applications.flora.web.app import FloraWebHandler
    r=setup(pilot,who='owner');before=offers._path().read_bytes()
    server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    conn=HTTPConnection('127.0.0.1',server.server_port)
    try:
        conn.request('POST','/flora/offers/development-save',urlencode({'candidate':r['id'],'version':1,'csrf':actor[2],'challenge':'foreign origin'}),headers={**actor[3],'Content-Type':'application/x-www-form-urlencoded','Origin':'https://foreign.example'})
        response=conn.getresponse();assert response.status==403;response.read()
    finally:conn.close();server.shutdown();server.server_close();thread.join(2)
    assert offers._path().read_bytes()==before and not pipeline._path().exists()
