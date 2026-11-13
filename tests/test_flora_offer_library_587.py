"""Sprint A acceptance with real, revocable, isolated authority; no external IO."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
import pytest
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_offers_v1 import actor, pilot, draft, approved
from tests.test_flora_sales_pipeline import web
from cios.applications.flora import offer_library as library, offers, offers_views
from cios.applications.flora.commercial_mission import resolve_commercial_mission, save_commercial_mission
from cios.applications.flora.storage import data_path

pytestmark = pytest.mark.real_security_boundary


def refs(*ids):
    return [{k: v for k, v in library.source_ref(library.template(i)).items() if k in {'id','version','digest'}} for i in ids]


def preferences(pilot, cats=('engineering','data'), who='seller'):
    h=pilot[who];m=resolve_commercial_mission(h);e=pilot['employer']
    return offers.configure_library(list(cats), e['id'],e['version'],m.version if m else 0,headers=h)


def adopt(pilot, *ids, who='seller', **kw):
    e=pilot['employer'];m=resolve_commercial_mission(pilot[who])
    return offers.adopt_library(refs(*ids),e['id'],e['version'],m.version,confirmed=True,headers=pilot[who],**kw)


def test_coverage_sources_and_all_playbooks_have_distinct_commercial_logic():
    d=library.catalogue();rows=d['offers'];deep=[r for r in rows if r['stage']=='deep']
    assert len(rows)==89 and len(deep)==29 and len({r['id'] for r in rows})==89
    assert len({r['name'].casefold() for r in rows})==89
    assert len(d['subindustries'])==12
    districts={district for r in rows for district in r['districts']}
    assert districts=={'applications','cloud','ai','cyber','services','channels','infrastructure','frontier'}
    ids={r['id'] for r in rows};source_ids={s['id'] for s in d['sources']}
    for c in d['subindustries']:
        additional = {'consulting': 2, 'data': 1, 'cyber': 1, 'engineering': 1}.get(c['id'], 0)
        assert sum(r['family']==c['id'] for r in rows)==7+additional
        assert sum(r['family']==c['id'] for r in deep)==2+additional
    for r in deep:
        assert library.current(library.source_ref(r))
        assert len(r['structural_triggers'])>=2 and len(r['event_triggers'])>=2
        assert 2<=len(r['entry_plays'])<=3 and r['validation_tests'] and r['seller_validation']
        assert r['jurisdiction']['territories']==['GB'] and r['constraints'] and r['exclusions']
        assert set(r['adjacent_offer_ids'])<=ids and set(r['source_ids'])<=source_ids
        assert r['source_lineage'] and r['revision_history'] and r['reviewed_on']=='2026-11-13'
        for p in r['structural_triggers']+r['event_triggers']:
            assert all(p[k] for k in ['observable','rival_explanation','decay','importance','evaluation'])
            assert p['evaluation'].startswith('Not observed')
        for p in r['entry_plays']:
            assert all(p[k] for k in ['buyer','conversation','workshop_or_proof','evidence_needed','disconfirming_question','follow_on','stop_conditions'])
        assert library.offer_content(r)['evidence']==''
    for k in ['outcome','ideal_customer_profile','commercial_model']:
        assert len({r[k] for r in deep})==29
    assert len({r['entry_plays'][0]['disconfirming_question'] for r in deep})==29
    assert all(s['url'].startswith('https://') and s['rights'] and 'Taxonomy' in s['boundary'] for s in d['sources'])


@pytest.mark.parametrize('bad',[[],['unknown'],['cloud','cloud'],'cloud',[True],list(range(13))])
def test_categories_fail_closed(bad):
    with pytest.raises(ValueError):library.categories(bad)


def test_suggestions_deduplicate_multi_category_and_honestly_reject_catalogue_only():
    rows=library.suggestions(['consulting','engineering','cloud'])
    assert len(rows)==len({r['id'] for r in rows})
    assert rows[0]['subindustries'][0]=='consulting'
    assert library.suggestions(['data'],'bounded AI')[0]['id']=='tech-data-02'
    assert library.suggestions(['data'],'nomatchingphrase')==[]
    for identifier,version in [('tech-data-03',1),('missing',1),('tech-data-01',2),('tech-data-01',True)]:
        with pytest.raises(ValueError):library.template(identifier,version)


def test_preferences_preserve_mission_and_are_not_customer_sector_or_employer_authority(pilot):
    h=pilot['seller']
    existing={'executive_role':'Account lead','employer':'Existing private employer text','commercial_objective':'Retain scope',
        'industries':['Banking'],'excluded_accounts':['easyjet'],'offer_portfolio':['Private portfolio'],
        'competitors':['Private competitor'],'partners':['Private partner'],'strategic_propositions':['Private strategy'],
        'delivery_constraints':['Private limits'],'geography':['United Kingdom']}
    save_commercial_mission(h,existing)
    before=asdict(resolve_commercial_mission(h));m=preferences(pilot)
    after=asdict(m)
    for k,v in before.items():
        if k not in {'technology_subindustries','offer_library_employer_id','version'}:assert after[k]==v,k
    assert m.technology_subindustries==('engineering','data')
    assert m.offer_library_employer_id==pilot['employer']['id'] and m.version==before['version']+1
    assert resolve_commercial_mission(pilot['reviewer']) is None


@pytest.mark.parametrize('who',['outsider','foreign'])
def test_preferences_and_adoption_require_real_employer_binding(pilot,who):
    with pytest.raises(PermissionError):preferences(pilot,who=who)
    e=pilot['employer']
    with pytest.raises(PermissionError):offers.adopt_library(refs('tech-data-02'),e['id'],e['version'],1,True,headers=pilot[who])


def test_private_versioned_adoption_is_atomic_idempotent_and_not_company_evidence(pilot):
    preferences(pilot,('engineering','data','cloud'));before=library.ASSET.read_bytes()
    selected=adopt(pilot,'tech-engineering-01','tech-data-02','tech-cloud-01')
    assert len(selected)==3
    again=adopt(pilot,'tech-data-02','tech-cloud-01')
    assert {r['id'] for r in again}<={r['id'] for r in selected}
    assert all(r['version']==1 and r['state']=='private_draft' and r['canonical_offer_ref'] is None for r in selected)
    assert all(r['content']['evidence']=='' and r['template_source'] and r['library_playbook'] for r in selected)
    assert not offers.snapshot(headers=pilot['reviewer'])['offers']
    assert not offers.snapshot(headers=pilot['owner'])['offers']
    assert library.ASSET.read_bytes()==before
    assert offers.snapshot(headers=pilot['seller'])['studio_enabled'] is False
    assert not data_path('sales_pipeline','opportunities.json').exists()
    with pilot['store'].transaction() as db:
        audit=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='commercial_offer_mutation'")]
    assert sum(r['action']=='library_example_adopted' for r in audit)==3
    assert all('content' not in r for r in audit)


def test_entire_batch_rejected_before_writes_and_cas_confirmation(pilot):
    m=preferences(pilot);e=pilot['employer'];before=offers._path().read_bytes()
    good=refs('tech-engineering-01')[0]
    for batch,ev,mv,confirm in [([good,good],e['version'],m.version,True),([good,good|{'digest':'bad'}],e['version'],m.version,True),([good],e['version']+1,m.version,True),([good],e['version'],m.version+1,True),([good],e['version'],m.version,False),([],e['version'],m.version,True),(refs('tech-channel-01'),e['version'],m.version,True)]:
        with pytest.raises(ValueError):offers.adopt_library(batch,e['id'],ev,mv,confirm,headers=pilot['seller'])
        assert offers._path().read_bytes()==before


def test_failed_second_persist_rolls_back_whole_batch_and_audit(pilot,monkeypatch):
    preferences(pilot);before=offers._path().read_bytes();original=offers._persist;count=0
    with pilot['store'].transaction() as db:before_audit=db.execute('SELECT count(*) FROM audit').fetchone()[0]
    def fail(envelope,headers,action,resource):
        nonlocal count
        original(envelope,headers,action,resource)
        if action=='library_example_adopted':
            count+=1
            if count==2:raise OSError('Injected atomic batch failure')
    monkeypatch.setattr(offers,'_persist',fail)
    with pytest.raises(OSError):adopt(pilot,'tech-engineering-01','tech-data-02')
    assert offers._path().read_bytes()==before
    with pilot['store'].transaction() as db:
        # Rollback event may append, committed domain mutation must not survive.
        assert db.execute("SELECT count(*) FROM audit WHERE event='commercial_offer_mutation' AND payload LIKE '%library_example_adopted%'").fetchone()[0]==0


def test_library_lineage_survives_edit_review_variation_rejection_and_retirement(pilot):
    preferences(pilot);r=adopt(pilot,'tech-engineering-01')[0];source=deepcopy(r['template_source'])
    edited=offers.save_offer({'name':'My bounded modernisation offer','evidence':'Example private delivery and rights review reference'},r['id'],r['version'],headers=pilot['seller'])
    assert edited['template_source']==source and edited['library_playbook']==r['library_playbook']
    submitted=offers.transition(r['id'],edited['version'],'submit',headers=pilot['seller'])
    with pytest.raises(PermissionError):offers.transition(r['id'],submitted['version'],'approve','self',headers=pilot['seller'])
    rejected=offers.transition(r['id'],submitted['version'],'reject','Example rejection',headers=pilot['reviewer'])
    edited=offers.save_offer({},r['id'],rejected['version'],headers=pilot['seller'])
    submitted=offers.transition(r['id'],edited['version'],'submit',headers=pilot['seller'])
    master=offers.transition(r['id'],submitted['version'],'approve','Example independent proof and rights review',headers=pilot['reviewer'])
    variation=offers.save_offer({'entry_play':'My private conversation'},parent_id=r['id'],parent_version=master['version'],headers=pilot['owner'])
    assert variation['template_source']==source and variation['state']=='private_draft'
    retired=offers.transition(r['id'],master['version'],'retire',headers=pilot['reviewer'])
    assert not next(o for o in offers.snapshot(headers=pilot['owner'])['offers'] if o['id']==variation['id'])['eligible']
    assert retired['template_source']==source


def test_no_employer_approval_without_seller_proof(pilot):
    preferences(pilot);r=adopt(pilot,'tech-data-02')[0]
    r=offers.transition(r['id'],r['version'],'submit',headers=pilot['seller'])
    with pytest.raises(ValueError,match='Seller delivery proof'):offers.transition(r['id'],r['version'],'approve','Example reviewer',headers=pilot['reviewer'])


@pytest.mark.parametrize('change',['version','withdraw','content'])
def test_stale_template_is_retained_but_ineligible_without_silent_upgrade(pilot,monkeypatch,change):
    preferences(pilot);r=adopt(pilot,'tech-data-02')[0];before=offers._path().read_bytes();data=library.catalogue()
    row=next(x for x in data['offers'] if x['id']=='tech-data-02')
    if change=='version':row['version']+=1
    elif change=='withdraw':row['status']='withdrawn'
    else:row['outcome']='Changed authored method'
    monkeypatch.setattr(library,'catalogue',lambda:deepcopy(data))
    snap=offers.snapshot(headers=pilot['seller'])
    assert snap['offers'][0]['library_playbook']==r['library_playbook'] and not snap['offers'][0]['eligible']
    with pytest.raises(ValueError):offers.transition(r['id'],1,'submit',headers=pilot['seller'])
    with pytest.raises(ValueError):offers.discover('offer',r['id'],headers=pilot['seller'])
    assert offers._path().read_bytes()==before


def test_same_matcher_both_routes_distinct_account_patterns_and_no_pipeline(pilot):
    preferences(pilot);rows=adopt(pilot,'tech-engineering-01','tech-data-02')
    before=offers._path().read_bytes()
    account=offers.discover('account','lloyds',headers=pilot['seller'])
    assert len(account)==2
    assert account[0]['why_account']!=account[1]['why_account']
    assert account[0]['entry_play']!=account[1]['entry_play']
    for row in rows:
        a=next(r for r in account if r['offer_id']==row['id'])
        b=next(r for r in offers.discover('offer',row['id'],headers=pilot['seller']) if r['enterprise_slug']=='lloyds')
        assert a==b and len(a['entry_plays'])==2 and a['pipeline_eligible'] is False
        assert a['economics'] is None and a['why_now'].endswith('no urgency inferred.')
        assert all(p['evaluation'].startswith('Not observed') for p in a['library_context']['event_patterns'])
        assert a['status']=='pilot_interpretation_not_accepted_APPA'
    assert offers._path().read_bytes()==before
    assert not data_path('sales_pipeline','opportunities.json').exists()


def test_http_onboarding_csrf_origin_strict_input_and_accessible_read_only_get(pilot,web):
    assert web('/flora/offers/start',authenticated=False)[0]==403
    before=offers._path().read_bytes();status,html,_=web('/flora/offers/start')
    assert status==200 and 'Primary technology category' in html and 'name="csrf"' in html
    assert html.count('aria-label="Primary product navigation"')==1
    assert offers._path().read_bytes()==before
    e=pilot['employer'];base={'employer_id':e['id'],'employer_version':e['version'],'mission_version':0,'primary':'engineering'}
    assert web('/flora/offers/onboard-preferences',base|{'csrf':'forged'})[0]==403
    assert web('/flora/offers/onboard-preferences',base|{'permission':'approve'})[0]==403
    assert web('/flora/offers/onboard-preferences',base)[0]==303
    status,html,_=web('/flora/offers/start?search='+urlencode({'q':'<script>alert(1)</script>'}).split('=',1)[1])
    assert status==200 and '<script>alert(1)</script>' not in html
    status,html,_=web('/flora/offers/start')
    assert status==200 and 'name="templates"' in html and 'name="templates" value=' in html
    for inp in html.split('<input ')[1:]:
        tag=inp.split('>',1)[0]
        if 'name="templates"' in tag:assert 'checked' not in tag
    assert '89 offer types, 29 developed playbooks' in html and html.count('Sources & method</summary>')==1
    ref=library.source_ref(library.template('tech-engineering-01'))
    payload={'employer_id':e['id'],'employer_version':e['version'],'mission_version':1,'templates':f"{ref['id']}:{ref['version']}:{ref['digest']}",'confirmed':'yes'}
    assert web('/flora/offers/onboard-adopt',payload)[0]==303
    record=next(r for r in offers.snapshot(headers=pilot['owner'])['offers'] if r['current'])
    assert record['state']=='private_draft'
    status,html,_=web('/flora/offers/edit?offer='+record['id'])
    assert status==200 and 'retained source snapshot' in html and 'Seller proof required' in html
    assert not data_path('sales_pipeline','opportunities.json').exists()


@pytest.mark.parametrize('categories,identifiers',[
    (('consulting','engineering','cloud'),('tech-consulting-01','tech-engineering-01','tech-cloud-01')),
    (('software','data'),('tech-software-01','tech-software-02','tech-data-01')),
    (('cyber','managed'),('tech-cyber-01','tech-cyber-02','tech-managed-01'))])
def test_three_seller_pilots_three_distinct_examples_and_independent_approval(pilot,categories,identifiers):
    preferences(pilot,categories);rows=adopt(pilot,*identifiers)
    assert len({r['id'] for r in rows})==3
    suggestions=library.suggestions(categories)
    assert len(suggestions)==len({r['id'] for r in suggestions})
    r=rows[0]
    r=offers.save_offer({'evidence':'Example permissioned delivery, capacity and partner-rights review; fixture only'},r['id'],1,headers=pilot['seller'])
    r=offers.transition(r['id'],r['version'],'submit',headers=pilot['seller'])
    r=offers.transition(r['id'],r['version'],'approve','Example independent employer review; fixture only',headers=pilot['reviewer'])
    assert r['state']=='employer_approved'
    assert len([x for x in offers.snapshot(headers=pilot['seller'])['offers'] if x['current']])==3
    assert offers.snapshot(headers=pilot['reviewer'])['offers'][-1]['state']=='employer_approved'
    assert offers.discover('account','lloyds',headers=pilot['seller'])
    assert not data_path('sales_pipeline','opportunities.json').exists()


def test_new_routes_share_existing_permission_and_input_envelope(pilot):
    from cios.applications.flora.offer_library_views import submit
    assert offers.BASE+'/start' in offers.READ_PATHS
    assert all(offers.BASE+p in offers.WRITE_PATHS for p in ['/onboard-company','/onboard-preferences','/onboard-adopt'])
    for suffix,values in [('/onboard-company',{'employer_id':['a','b']}),('/onboard-preferences',{'primary':['cloud'],'additional':['cloud','cloud']}),('/onboard-adopt',{'confirmed':['yes'],'templates':['bad']}),('/onboard-adopt',{'permission':['approve']})]:
        with pytest.raises((ValueError,PermissionError)):submit(suffix,values,pilot['seller'])


def test_explicit_587_owner_revisions_preserve_existing_authority_and_matching_entry_points():
    import ast
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'docs/flora-runtime/offer-library-587/Owner-Compatibility.json').read_text())
    for path,expected in manifest['unchanged_control_functions'].items():
        tree=ast.parse((root/path).read_text())
        functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
        for name,checksum in expected.items():
            assert hashlib.sha256(ast.dump(functions[name],include_attributes=False).encode()).hexdigest()==checksum,(path,name)
    # There is still one matching call in both modes; no library matching service.
    assert 'def assess_fit' not in (root/'cios/applications/flora/offer_library.py').read_text()
    assert 'def discover' not in (root/'cios/applications/flora/offer_library.py').read_text()
    assert 'sales_pipeline' not in (root/'cios/applications/flora/offer_library.py').read_text()


def test_legacy_profile_save_preserves_additive_supplier_preferences(pilot):
    preferences(pilot)
    save_commercial_mission(pilot['seller'],{'executive_role':'Account director','commercial_objective':'Updated customer mission','industries':['Banking']})
    m=resolve_commercial_mission(pilot['seller'])
    assert m.technology_subindustries==('engineering','data')
    assert m.offer_library_employer_id==pilot['employer']['id']
    assert m.industries==('Banking',)
