"""Bounded research, one matcher, private shortlist integrity; real service authority."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import pytest
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_offers_v1 import actor, pilot
from tests.test_flora_sales_pipeline import web
from tests.test_flora_offer_library_587 import preferences,adopt
from cios.applications.flora import offers,offer_library as library
from cios.applications.flora.research_intelligence import buying_evidence as research
from cios.applications.flora.storage import data_path

pytestmark=pytest.mark.real_security_boundary

@pytest.fixture(scope='module')
def grounded():return research.accounts(offers.accounts())


def projection(identifier,approved=True):
    row=library.template(identifier)
    return {'id':'EXAMPLE-'+identifier,'version':1,'state':'employer_approved' if approved else 'private_draft',
        'content':library.offer_content(row),'template_source':library.source_ref(row),'library_playbook':row}


def fit(accounts,identifier,slug='lloyds',cutoff='2026-11-13',approved=True,seller=None):
    return offers.assess_fit(seller or {},projection(identifier,approved),accounts[slug],cutoff,offers.TRIGGER_POLICY)


def full_scope(pilot):
    with pilot['store'].transaction() as db:
        db.execute('UPDATE memberships SET enterprises=? WHERE user_id IN (?,?)',(json.dumps(['BK-ENT-001','AV-ENT-001','BK-ENT-003','BK-ENT-005','BK-ENT-006','bt-group-plc']),'pilot-seller','synthetic-human'))


def selected_offer(pilot):
    preferences(pilot,('consulting','data','cyber','engineering'))
    return adopt(pilot,*research.OFFER_DIMENSIONS)[0]


def save(pilot,row,results=None,**overrides):
    results=results or offers.discover('offer',row['id'],intelligence=True,headers=pilot['seller'])
    args={'offer_id':row['id'],'expected_offer_version':row['version'],'expected_employer_version':pilot['employer']['version'],
        'cutoff':'2026-11-13','registry_digest':research.DATA_SHA256,'assessment_ids':[results[0]['assessment_id']],
        'note':'Example reviewed research only <script>do not execute</script>','expected_version':0,'confirmed':True}
    args.update(overrides);return offers.save_shortlist(**args,headers=pilot['seller'])


def test_source_registry_and_existing_evidence_observation_contracts(grounded):
    data=research.load();assert len(data['cohort'])==10 and len(data['sources'])==9 and len(data['facts'])==25
    assert set(grounded)=={'lloyds','easyjet','equinix','barclays','natwest','santander-uk','bt','computacenter','arm','nvidia'}
    assert len(data['cohort'][3:])==7
    for s in data['sources']:
        assert s['accepted'] is False and s['collector_enabled'] is False and s['primary_content_sha256'] is None
        assert s['usage_scope']=='public_short_quote_and_link' and len(s['excerpt'].replace(' / ',' ').split())<=25
        assert sha256(s['excerpt'].encode()).hexdigest()==s['excerpt_sha256']
    for a in grounded.values():
        for f in a['trigger_research']['facts']:
            assert f['source_segment']['content_hash']==sha256(f['quote'].encode()).hexdigest()
            assert f['candidate_claim']['authority']=='candidate_intelligence'
            assert f['candidate_observation']['persistence_state']=='candidate_read_projection_only'
            assert f['canonical_evidence_id'] is None and f['accepted'] is False
            assert f['evidence_package_item']['stable_id']
    assert next(f for f in grounded['lloyds']['trigger_research']['facts'] if f['id']=='LBG-AR25-MIGRATION')['source_id']=='PR-LBG-AR25'


@pytest.mark.parametrize('identifier',list(research.OFFER_DIMENSIONS))
def test_five_by_ten_real_assessments_never_invent_qualification(grounded,identifier):
    for slug in grounded:
        r=fit(grounded,identifier,slug);b=r['buying_trigger']
        assert r['economics'] is None and not r['pipeline_eligible']
        assert b['funding']==b['seller_access']==b['buyer_intent']=='Unknown' and not b['procurement_observed']
        assert b['signal_strength'] and b['offer_relevance'] and b['research_completeness']
        assert 'Unknown' in b['residual_need'] and 'candidate' in b['interpretation']
        assert b['tier'] in {'Prioritise','Investigate','Research only'}
        assert r['economic_value_hypothesis']['amount'] is None
        for f in b['timeline']:assert f['id'] and f['source_id'] and f['source_url'] and f['locator']


def test_offer_specific_positive_counter_and_unknown_contrasts(grounded):
    ids=list(research.OFFER_DIMENSIONS)
    assert fit(grounded,ids[0],'santander-uk')['buying_trigger']['tier']=='Prioritise'
    assert fit(grounded,ids[3],'santander-uk')['buying_trigger']['tier']=='Prioritise'
    assert fit(grounded,ids[0],'santander-uk')['next_validation_action']!=fit(grounded,ids[3],'santander-uk')['next_validation_action']
    assert fit(grounded,ids[1],'lloyds')['buying_trigger']['tier']=='Investigate'
    assert fit(grounded,ids[1],'natwest')['buying_trigger']['tier']=='Research only'  # A deployed point tool is not enterprise AI-first.
    assert fit(grounded,ids[0],'natwest')['buying_trigger']['tier']=='Investigate'
    assert fit(grounded,ids[2],'computacenter')['buying_trigger']['tier']=='Investigate'
    cyber=fit(grounded,ids[2],'lloyds');assert cyber['buying_trigger']['tier']=='Research only'
    assert 'LBG-ENVOY-CONTROLS' in cyber['buying_trigger']['counter_evidence']
    for slug in grounded:assert fit(grounded,ids[4],slug)['buying_trigger']['tier']=='Research only'
    for slug in ('arm','nvidia'):
        assert fit(grounded,ids[1],slug)['buying_trigger']['tier']=='Research only'
    assert fit(grounded,ids[3],'equinix')['buying_trigger']['stage']=='No current trigger found'


def test_publication_effective_and_verification_dates_are_distinct(grounded):
    r=fit(grounded,list(research.OFFER_DIMENSIONS)[3],'santander-uk');b=r['buying_trigger']
    event=next(f for f in b['timeline'] if f['id']=='BTI-TSB-MIGRATION')
    assert event['publication_date']=='2026-11-10' and event['effective_date'] is None
    assert '2027' in event['effective_period'] and event['last_verified'].startswith('2026-11-13')
    early=fit(grounded,list(research.OFFER_DIMENSIONS)[3],'santander-uk','2026-11-09')
    assert early['buying_trigger']['tier']=='Research only' and not early['buying_trigger']['timeline']
    old=fit(grounded,list(research.OFFER_DIMENSIONS)[1],'easyjet')
    icc=next(f for f in old['buying_trigger']['timeline'] if f['id']=='AV-ICC')
    assert not icc['dated_current'] and icc['publication_date']=='2024-05-22'


def test_decay_contradiction_supersession_and_policy_sensitivity_without_mutation(grounded):
    raw=research.DATA.read_bytes();ids=list(research.OFFER_DIMENSIONS)
    assert fit(grounded,ids[3],'santander-uk')['buying_trigger']['tier']=='Prioritise'
    assert fit(grounded,ids[3],'santander-uk','2027-03-01')['buying_trigger']['tier']=='Research only'
    altered=deepcopy(grounded);facts=altered['santander-uk']['trigger_research']['facts']
    closure=deepcopy(next(f for f in facts if f['id']=='BTI-TSB-MIGRATION'))
    closure.update(id='EXAMPLE-TEST-CLOSURE',kind='closed',statement='Example test-only programme closure; not a real reported event',supersedes=['BTI-TSB-MIGRATION','BTI-TSB-APPLICATION'])
    facts.append(closure)
    assert fit(altered,ids[3],'santander-uk')['buying_trigger']['tier']=='Research only'
    current=deepcopy(grounded);positive=next(f for f in current['santander-uk']['trigger_research']['facts'] if f['id']=='BTI-TSB-MIGRATION');positive['status']='withdrawn'
    assert fit(current,ids[3],'santander-uk')['buying_trigger']['tier']=='Investigate'  # Catalyst still exists; no current programme.
    narrow=deepcopy(grounded);narrow['computacenter']['trigger_research']['policy']['catalyst_review_days']=60
    assert fit(grounded,ids[3],'computacenter')['buying_trigger']['tier']=='Investigate'
    assert fit(narrow,ids[3],'computacenter')['buying_trigger']['tier']=='Research only'
    assert research.DATA.read_bytes()==raw


def test_private_approval_scope_and_exclusions_are_not_overridden(grounded):
    i=list(research.OFFER_DIMENSIONS)[3]
    assert fit(grounded,i,'santander-uk',approved=False)['buying_trigger']['tier']=='Investigate'
    excluded=fit(grounded,i,'santander-uk',seller={'excluded_accounts':['santander-uk']})
    assert excluded['buying_trigger']['tier']=='Research only' and not excluded['buying_trigger']['shortlist_eligible']


def test_both_modes_use_one_engine_and_permissions_filter_extended_accounts(pilot):
    full_scope(pilot);r=selected_offer(pilot);before=offers._path().read_bytes()
    all_results=offers.discover('offer',r['id'],intelligence=True,headers=pilot['seller']);assert len(all_results)==10
    for a in all_results:
        b=next(x for x in offers.discover('account',a['enterprise_slug'],intelligence=True,headers=pilot['seller']) if x['offer_id']==r['id'])
        assert a==b
    with pilot['store'].transaction() as db:db.execute('UPDATE memberships SET enterprises=? WHERE user_id=?',(json.dumps(['BK-ENT-001','AV-ENT-001']),'pilot-seller'))
    filtered=offers.discover('offer',r['id'],intelligence=True,headers=pilot['seller'])
    assert {x['enterprise_slug'] for x in filtered}=={'lloyds','easyjet','equinix','computacenter','arm','nvidia'}
    assert offers._path().read_bytes()==before and not data_path('sales_pipeline','opportunities.json').exists()


def test_reviewed_shortlist_private_cas_snapshot_audit_and_no_pipeline(pilot):
    full_scope(pilot);r=selected_offer(pilot);matches=offers.discover('offer',r['id'],intelligence=True,headers=pilot['seller'])
    saved=save(pilot,r,matches);assert saved['version']==1 and not saved['pipeline_mutation'] and not saved['canonical_mutation']
    assert len(offers.shortlist_snapshot(headers=pilot['seller']))==1
    assert not offers.shortlist_snapshot(headers=pilot['owner']) and not offers.shortlist_snapshot(headers=pilot['reviewer'])
    with pytest.raises(ValueError,match='Shortlist review changed'):save(pilot,r,matches)
    saved=save(pilot,r,matches,expected_version=1,note='Example second review');assert saved['version']==2
    envelope=json.loads(offers._path().read_text());history=next(iter(next(v for v in envelope['users'].values() if v.get('shortlists'))['shortlists'].values()))
    assert len(history)==2 and 'script' in history[0]['note']
    with pilot['store'].transaction() as db:
        audit=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='commercial_offer_mutation'")]
    assert sum(a['action']=='research_shortlist_reviewed' for a in audit)==2
    assert all('note' not in a and 'entries' not in a for a in audit)
    assert not data_path('sales_pipeline','opportunities.json').exists()
    revised=offers.save_offer({'entry_play':'Example revised seller conversation'},r['id'],r['version'],headers=pilot['seller'])
    assert offers.shortlist_snapshot(headers=pilot['seller'])[0]['stale']


@pytest.mark.parametrize('overrides',[{'confirmed':False},{'registry_digest':'stale'},{'assessment_ids':['forged']},{'expected_offer_version':999},{'expected_employer_version':999},{'cutoff':'2099-01-01'}])
def test_shortlist_stale_forged_and_unreviewed_writes_leave_bytes_unchanged(pilot,overrides):
    r=selected_offer(pilot);before=offers._path().read_bytes()
    with pytest.raises(ValueError):save(pilot,r,**overrides)
    assert offers._path().read_bytes()==before


def test_shortlist_rollback_on_persist_failure_and_enterprise_permission_revocation(pilot,monkeypatch):
    full_scope(pilot);r=selected_offer(pilot);matches=offers.discover('offer',r['id'],intelligence=True,headers=pilot['seller'])
    original=offers._persist;before=offers._path().read_bytes()
    def fail(envelope,headers,action,resource):
        original(envelope,headers,action,resource)
        if action=='research_shortlist_reviewed':raise OSError('Example injected journal failure')
    with monkeypatch.context() as m:
        m.setattr(offers,'_persist',fail)
        with pytest.raises(OSError):save(pilot,r,matches)
    assert offers._path().read_bytes()==before
    chosen=next(x for x in matches if x['enterprise_slug']=='santander-uk')
    save(pilot,r,matches,assessment_ids=[chosen['assessment_id']])
    with pilot['store'].transaction() as db:db.execute('UPDATE memberships SET enterprises=? WHERE user_id=?',(json.dumps(['BK-ENT-001','AV-ENT-001']),'pilot-seller'))
    assert offers.shortlist_snapshot(headers=pilot['seller'])==[]


def test_http_discovery_scoping_csrf_escaping_and_read_only_get(pilot,web):
    full_scope(pilot);preferences(pilot,('consulting','engineering'),who='owner')
    r=adopt(pilot,list(research.OFFER_DIMENSIONS)[0],who='owner')[0]
    assert web('/flora/offers/triggers',authenticated=False)[0]==403
    before=offers._path().read_bytes();status,html,_=web('/flora/offers/triggers?selected='+r['id'])
    assert status==200 and html.count('class="trigger-row"')==10 and html.count('Explore fit</a>')==10
    assert html.count('Sources & method</summary>')==1 and html.count('aria-label="Primary product navigation"')==1
    status,detail,_=web('/flora/offers/trigger-detail?offer='+r['id']+'&enterprise=santander-uk')
    assert status==200 and 'Reported timeline' in detail and '2026-11-10' in detail
    assert offers._path().read_bytes()==before
    results=offers.discover('offer',r['id'],intelligence=True,headers=pilot['owner'])
    payload={'offer_id':r['id'],'offer_version':r['version'],'employer_version':pilot['employer']['version'],'cutoff':'2026-11-13','registry_digest':research.DATA_SHA256,'assessment_ids':results[0]['assessment_id'],'note':'<script>example</script>','expected_version':0,'confirmed':'reviewed'}
    assert web('/flora/offers/shortlist-save',payload|{'csrf':'forged'})[0]==403
    assert web('/flora/offers/shortlist-save',payload|{'permission':'approve'})[0]==403
    assert web('/flora/offers/shortlist-save',payload)[0]==303
    status,html,_=web('/flora/offers/shortlists');assert status==200 and '&lt;script&gt;example&lt;/script&gt;' in html and '<script>example</script>' not in html
    assert web('/flora/offers/trigger-detail?offer='+r['id']+'&enterprise=unknown')[0]==403
    assert not data_path('sales_pipeline','opportunities.json').exists()


def test_source_integrity_rejects_unreviewed_input(monkeypatch,tmp_path):
    fake=tmp_path/'enterprise-knowledge/technology/research-model/Buying-Trigger-Pilot.json';fake.parent.mkdir(parents=True);fake.write_bytes(research.DATA.read_bytes()+b' ')
    monkeypatch.setattr(research,'ROOT',tmp_path);monkeypatch.setattr(research,'DATA',fake)
    with pytest.raises(ValueError,match='changed'):research.load()


@pytest.mark.parametrize('change',[{'usage_scope':'restricted'},{'accepted':True},{'collector_enabled':True},{'primary_content_sha256':'f'*64},{'url':'https://unregistered.example/source','retrieval_url':'https://unregistered.example/source'},{'publication_date':'2099-01-01','publication_date_evidence':'Example unsupported future date'}])
def test_candidate_rights_publisher_dates_and_acceptance_fail_closed(monkeypatch,tmp_path,change):
    data=research.load();data['sources'][0].update(change)
    path=tmp_path/'enterprise-knowledge/technology/research-model/Buying-Trigger-Pilot.json';path.parent.mkdir(parents=True);path.write_text(json.dumps(data))
    monkeypatch.setattr(research,'ROOT',tmp_path);monkeypatch.setattr(research,'DATA',path);monkeypatch.setattr(research,'DATA_SHA256',sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError):research.load()


def test_matcher_and_source_adapter_have_no_network_or_canonical_write(pilot,monkeypatch):
    import urllib.request
    def forbidden(*args,**kwargs):raise AssertionError('Network access is not part of candidate matching')
    monkeypatch.setattr(urllib.request,'urlopen',forbidden)
    row=selected_offer(pilot);before=offers._path().read_bytes()
    assert offers.discover('offer',row['id'],intelligence=True,headers=pilot['seller'])
    assert offers._path().read_bytes()==before and not offers.snapshot(headers=pilot['seller'])['studio_enabled']


@pytest.mark.parametrize('identifier,slug',[
    (list(research.OFFER_DIMENSIONS)[i],s) for i,slugs in [(0,['santander-uk','lloyds','computacenter','bt','natwest']),(1,['lloyds']),(2,['computacenter']),(3,['santander-uk','lloyds','computacenter'])] for s in slugs])
def test_enterprise_entry_plays_require_their_retained_positive_basis(grounded,identifier,slug):
    from cios.applications.flora import buying_entry_plays as plays
    result=fit(grounded,identifier,slug);detail=result['buying_trigger']['entry_play_detail']
    assert detail and detail['conversation'] in result['entry_play'] and detail['diagnostic'] in result['entry_play']
    assert result['next_validation_action']==detail['question'] and detail['stop']
    timeline={f['id']:f for f in result['buying_trigger']['timeline']}
    for ref in detail['evidence']:
        f=timeline[ref['fact_id']]
        assert ref['source_id']==f['source_id'] and ref['publication_date']==f['publication_date'] and ref['source_url']==f['source_url']
    assert detail['revision']==plays.REVISION and 'not customer demand' in detail['classification']
    for removed in detail['required']:
        altered=deepcopy(grounded)
        next(f for f in altered[slug]['trigger_research']['facts'] if f['id']==removed)['status']='withdrawn'
        assert fit(altered,identifier,slug)['buying_trigger']['entry_play_detail'] is None
    assert fit(grounded,identifier,slug,'2027-03-01')['buying_trigger']['entry_play_detail'] is None
    assert fit(grounded,identifier,slug,seller={'excluded_accounts':[slug]})['buying_trigger']['entry_play_detail'] is None


def test_diagnostics_are_substantively_distinct_and_do_not_upgrade_research_only(grounded):
    from cios.applications.flora import buying_entry_plays as plays
    before=json.loads((Path(__file__).resolve().parents[1]/'docs/flora-runtime/buying-trigger-591/Commercial-Before.json').read_text())
    assert before['source_sha']=='a884a6fcf639bc4653072d873781c71eceb0bd05'
    expected={(r['offer_id'],r['enterprise_slug']):r for r in before['samples']}
    tailored=[]
    for identifier in research.OFFER_DIMENSIONS:
        for slug in grounded:
            r=fit(grounded,identifier,slug);old=expected[identifier,slug];b=r['buying_trigger']
            assert (b['tier'],b['stage'],r['why_account'],r['contradictions'])==(old['tier'],old['stage'],old['why'],old['counter_evidence'])
            if b['entry_play_detail']:tailored.append(b['entry_play_detail'])
            if b['tier']=='Research only':
                assert b['entry_play_detail'] is None and 'No programme diagnostic is recommended' in r['entry_play']
    assert len(tailored)==10 and len({p['diagnostic'] for p in tailored})==10
    assert len({p['question'] for p in tailored})==10
    assert 'separate legal entities' in plays.PLAYS[plays.D,'santander-uk']['conversation']
    assert 'completed CRM' in plays.PLAYS[plays.D,'computacenter']['conversation']
    assert 'non-AI baseline' in plays.PLAYS[plays.A,'lloyds']['diagnostic']
    assert 'supported upgrade' in plays.PLAYS[plays.L,'computacenter']['diagnostic']


def test_changed_entry_play_revision_invalidates_saved_review_without_pipeline_write(pilot,monkeypatch):
    from cios.applications.flora import buying_entry_plays as plays
    full_scope(pilot);row=selected_offer(pilot)
    results=offers.discover('offer',row['id'],intelligence=True,headers=pilot['seller'])
    save(pilot,row,results);before=offers._path().read_bytes()
    monkeypatch.setattr(plays,'REVISION','example-test-only-new-commercial-revision')
    assert offers.shortlist_snapshot(headers=pilot['seller'])[0]['stale']
    new=offers.discover('offer',row['id'],intelligence=True,headers=pilot['seller'])
    assert {r['assessment_id'] for r in results}.isdisjoint(r['assessment_id'] for r in new)
    with pytest.raises(ValueError,match='Assessment changed'):
        save(pilot,row,results,expected_version=1)
    assert offers._path().read_bytes()==before and not data_path('sales_pipeline','opportunities.json').exists()
