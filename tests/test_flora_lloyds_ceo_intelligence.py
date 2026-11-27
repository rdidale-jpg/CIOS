"""Real retained issuer facts through existing owners; no fixtures as research."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import hashlib,json,shutil,subprocess
import pytest
from cios.applications.flora import lloyds_gold as g,visual_streams as v
from cios.applications.flora.research_intelligence import model
from cios.applications.flora.financial_intelligence.candidate_analytics import public_factual_projection
from tests.test_flora_living_enterprise_preview import http
from tests.flora_lloyds_research_contract import preserved_research_cut,SOURCES,BASE,ROOT

pytestmark=pytest.mark.real_security_boundary
VIEWS={
 'employees':('inside','people','employees'),'geography':('inside','people','geography'),
 'board':('inside','people','board'),'distribution':('landscape','economics','distribution'),
 'mortgage':('inside','operations','mortgage-ml'),'platform':('inside','applications','platform-delivery'),
 'settlement':('inside','applications','settlement'),'business':('inside','operations','digital-business'),
 'wealth':('landscape','retirement','wealth-delivery'),'collaboration':('inside','partners','caura'),
 'investigations':('forces','strategy','investigations'),
}
def view(name):
    stream,focus,detail=VIEWS[name]
    return g.render({'stream':[stream],'focus':[focus],'detail':[detail]},canonical=True).split('<main ',1)[1].split('</main>',1)[0]

def data():return deepcopy(v.current_data(v.Context('lloyds','inside')))

def test_genuine_retained_originals_old_records_and_existing_source_policy():
    preserved_research_cut();x=model.load_assessment()
    for s in x['sources']:
        if s['id'] not in SOURCES:continue
        text=model.primary_text(s)
        assert s['url'].startswith('https://www.lloydsbankinggroup.com/')
        assert s['primary_content_sha256'] is None and s['retrieval_reference']
        assert sum(len(q['quote'].split()) for q in s['excerpts'])<=25
        assert all(q['quote'] in text for q in s['excerpts'])
        assert s['rights']['status']=='permitted_public_factual_category'
        assert all(c['source_ids']==[s['id']] for c in x['claims'] if c['id'] in {b['claim_id'] for b in s['disclosure_bindings']})
    assert public_factual_projection()=={}


def test_additive_review_reconciliation_does_not_grant_old_judgments_to_new_research():
    from cios.applications.flora.research_intelligence import understanding
    from cios.applications.flora.research_intelligence.commercial_intelligence import commercial_projection
    x=model.load_assessment();review=understanding.load_review('banking')
    path='enterprise-knowledge/banking/research-model/Understanding-Review.json'
    old_review=json.loads(subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT))
    with pytest.raises(ValueError,match='baseline/scope/cut-off mismatch'):
        understanding.assess(x,old_review,'2026-11-27')
    assessed=understanding.assess(x,review,'2026-11-27')
    new=[c for c in assessed['claims'] if c['id'].startswith('LBG-CE-')]
    assert len(new)==58 and all(not c['direct_support_reviewed'] and not c['independent_corroboration'] for c in new)
    edges=[r for r in assessed['relationships'] if r['id'].startswith('LCE-REL-')]
    assert len(edges)==5 and all(r['state']!='Verified factual relationship' and not r['causation_proven'] for r in edges)
    old_data=json.loads(subprocess.check_output(['git','show',BASE+':enterprise-knowledge/banking/research-model/Assessment-Overlay.json'],cwd=ROOT))
    before=commercial_projection(old_data,old_review)['candidates'];after=commercial_projection(x,review)['candidates']
    fields=('id','commercial_rank','readiness','recommendation_eligibility','commercial','status')
    assert [{k:r.get(k) for k in fields} for r in before]==[{k:r.get(k) for k in fields} for r in after]
    assert [[p['id'] for p in r['support']] for r in before]==[[p['id'] for p in r['support']] for r in after]
    damaged=deepcopy(review)
    next(s for s in damaged['sources'] if s['id']=='DEPTH-LBG-AI')['assessment_digest']='0'*64
    denied=next(r for r in commercial_projection(x,damaged)['candidates'] if r['id']=='RCO-LBG-002')
    assert 'RC-DEPTH-LBG-AI' not in {p['id'] for p in denied['support']}
    assert 'LBG-CE-VERTEX' not in {p['id'] for p in denied['support']}


def test_actual_employee_inventory_closes_populations_without_inventing_costs():
    body=view('employees')
    assert all(s in body for s in ('60,061','61,228','62,569','27,574','7,955','6,025','18,507','24,005','659'))
    assert 'reconciles to the disclosed Group total' in body
    assert 'not headcount, current 2026 staffing' in body
    assert 'not a salary, capability-cost or profit allocation' in body
    assert sum((27574,7955,6025,18507))==60061
    geo=view('geography');assert '60,062 against 60,061' in geo
    assert 'no geographic shares, correction or workforce allocation is inferred' in geo


def test_actual_target_and_programme_types_remain_separate():
    body=view('distribution');assert 'About 45%' in body and 'About 50%' in body
    assert 'data-measurement-state="actual"' in body and 'data-measurement-state="target"' in body
    assert 'no percentage achieved' in body and 'not a whole-Group productivity measure' in body
    assert all(x not in body for x in ('90% delivered','£11,084','£477.5bn','3.21%'))
    business=view('business');assert 'over 50%' in business and '2026 target early' in business
    assert 'Volume growth is not income growth or margin' in business


def test_named_platform_and_pilot_do_not_create_supplier_contracts_or_false_perimeters():
    platform=view('platform');assert all(x in platform for x in ('Vertex AI','15 modelling systems','on-premise infrastructure','300','80','18','Gemini','57'))
    assert 'different definitions and dates' in platform and 'all Envoy workloads' in platform
    assert 'Contract price, renewal, exclusivity' in platform
    mortgage=view('mortgage');assert 'days to seconds' in mortgage
    assert 'one step, not the complete mortgage' in mortgage and 'intake is closed' in mortgage
    pilot=view('settlement');assert all(x in pilot for x in ('Jersey','Visa','Archax','Canton','under an hour'))
    assert 'not Lloyds Bank PLC or proof of a CIB-wide programme' in pilot
    assert 'not a new customer payment product' in pilot
    research=model.load_assessment()
    relations=[r for r in research['relationships'] if r['id'].startswith('LCE-REL-')]
    assert len(relations)==5 and all(r['verified'] for r in relations)
    assert all(r['predicate'] not in {'contract_with','has_budget','needs_supplier'} for r in relations)


def test_board_oversight_and_existing_management_membership_stay_distinct():
    body=view('board');assert all(x in body for x in ('Robin Budenberg','Sarah Legg','Catherine Woods','Cathy Turner','Amanda Mackenzie','Danuta Gray','Nathan Bostock'))
    assert 'Concurrent meetings do not merge legal boards' in body
    assert 'not inferred process owners or purchasing sponsors' in body
    assert 'thirteen issuer-listed executive members' in body


def test_investigation_priority_is_core_operating_delivery_not_the_easiest_pilot():
    body=view('investigations')
    assert all(x in body for x in ('Distribution and full cost','Industrialise a proven AI use case','Commercial growth and operating depth'))
    assert 'Visa' not in body and 'qualified Material Pressures or opportunities' in body
    investigation=body.split('class="ceo-investigations">',1)[1].split('</section>',1)[0]
    assert investigation.count('data-canvas-region=')==3


SOURCE_CASES=[
 ('LCE-WORKFORCE','employees','60,061'),('LCE-ANNUAL-OPERATIONS','wealth','84,000'),
 ('LCE-VERTEX','platform','Vertex AI'),('LCE-DELIVERY','platform','40%'),
 ('LCE-BOARD','board','Sarah Legg'),('LCE-SETTLEMENT','settlement','Archax'),('LCE-LAUNCH','collaboration','8,000'),
]
@pytest.mark.parametrize('source,route,removed',SOURCE_CASES)
@pytest.mark.parametrize('flag',('withdrawn','revoked','owner_only','stale','superseded','contradictory'))
def test_source_lifecycle_removes_facts_figures_and_hidden_markup_without_blanket_hold(monkeypatch,source,route,removed,flag):
    x=data();next(s for s in x['sources'] if s['id']==source)[flag]=True
    monkeypatch.setattr(v,'current_data',lambda _:x)
    assert removed not in view(route)
    group=g.render({},canonical=True);assert '£502.8bn' in group and '£6.6bn' in group
    if source!='LCE-BOARD':assert 'Sarah Legg' in view('board')


@pytest.mark.parametrize('mutation',('issuer','period','entity','value','unit','basis','kind','rights','restrictions','url','date','relationship'))
def test_mismatched_axes_or_authority_fail_closed(monkeypatch,mutation):
    x=data();s=next(s for s in x['sources'] if s['id']=='LCE-WORKFORCE');c=next(c for c in x['claims'] if c['id']=='LBG-CE-FTE25')
    if mutation=='issuer':s['publisher']='Nationwide'
    elif mutation=='period':
        s['reporting_period']='FY2026';c['reporting_period']='FY2026'
        next(b for b in s['disclosure_bindings'] if b['claim_id']==c['id'])['reporting_period']='FY2026'
    elif mutation=='entity':c['entity_scope']='Lloyds Bank PLC'
    elif mutation=='value':c['metric_value']='600610'
    elif mutation in {'unit','basis'}:c['metric_unit']='GBP million; cost'
    elif mutation=='kind':c['kind']='management_expectation'
    elif mutation=='rights':s['rights']['status']='pending'
    elif mutation=='restrictions':s['restrictions']=['public_read_only']
    elif mutation=='url':s['url']=s['retrieval_url']='https://www.lloydsbankinggroup.com/other.pdf'
    elif mutation=='date':s['publication_date']='2026-02-14'
    else:c['relationship']={'subject':'BK-ENT-001','predicate':'buys_from','object':'SUP-GOOGLE'}
    monkeypatch.setattr(v,'current_data',lambda _:x)
    assert '60,061' not in view('employees')
    assert '£502.8bn' in g.render({},canonical=True)


def test_real_source_owner_correction_reloads_figures_and_suppresses_unreconciled_partition(tmp_path,monkeypatch):
    repo=tmp_path/'repo';shutil.copytree(ROOT/'enterprise-knowledge',repo/'enterprise-knowledge')
    monkeypatch.setattr(model,'REPO',repo);monkeypatch.setattr(model,'DATA',repo/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json')
    original=view('employees');assert '60,061' in original
    x=json.loads(model.DATA.read_text());s=next(s for s in x['sources'] if s['id']=='LCE-WORKFORCE');c=next(c for c in x['claims'] if c['id']=='LBG-CE-FTE25')
    # Isolated correction challenge, not a change to authentic retained research.
    c['statement']=c['statement'].replace('60,061','60,060');c['metric_value']='60060';c['primary_quotes'][s['id']]='60,060'
    b=next(b for b in s['disclosure_bindings'] if b['claim_id']==c['id']);b.update({k:c[k] for k in ('statement','metric_value','primary_quotes')})
    for q in s['excerpts']:
        if q['quote']=='60,061':q['quote']='60,060'
    snap=repo/s['text_path'];snap.write_text(snap.read_text().replace('60,061','60,060'));s['text_sha256']=hashlib.sha256(snap.read_bytes()).hexdigest()
    s['document_identity']['version']='isolated-correction-challenge';model.DATA.write_text(json.dumps(x))
    model.load_assessment();changed=view('employees')
    assert '60,060' in changed and '60,061' not in changed
    assert 'ceo-fte-distribution' not in changed
    assert public_factual_projection()=={}


@pytest.mark.parametrize('route',VIEWS.values())
def test_new_public_routes_do_not_accept_private_selectors_or_writes(http,route):
    stream,focus,detail=route;url=f'/enterprises/lloyds?stream={stream}&focus={focus}&detail={detail}'
    status,headers,body=http(url);assert status==200
    assert 'no-store' in headers.get('Cache-Control','')
    assert '.pdf' not in body and 'Private run' not in body
    assert http(url,'POST')[0]==403
    for suffix in ('&workspace=other','&analysis=fi-private','&source=owner-only','&selected=natwest'):
        assert http(url+suffix)[0] in {403,404}


def test_source_inspection_keeps_homepage_attribution_and_held_measures_off():
    for focus in ('people','applications','operations','economics','partners'):
        stream='landscape' if focus=='economics' else 'inside'
        body=g.render({'stream':[stream],'focus':[focus],'detail':['sources']},canonical=True)
        assert '.pdf' not in body and 'https://www.lloydsbankinggroup.com/' in body
    assert public_factual_projection()=={}
    protected=('cios/applications/flora/security_store.py','cios/applications/flora/security_web.py','cios/applications/flora/financial_intelligence','cios/applications/flora/research_intelligence','cios/applications/flora/intelligence_presentation.py','tools/ci/flora_ci.py','tools/ci/flora-baseline-v1.json','architecture/decisions')
    from tests.test_flora_lloyds_financials import assert_only_public_financial_changes
    assert_only_public_financial_changes(ROOT, BASE, protected)
