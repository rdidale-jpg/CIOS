"""Gold Standard composition: authority, financial semantics and live withdrawal."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import ast
import subprocess

import pytest
from cios.applications.flora import lloyds_gold as gold,visual_streams as v,living_enterprise_preview as old,security
from cios.applications.flora.public_routes import public_request_target
from cios.applications.flora.security_store import digest
from tests.test_flora_living_enterprise_preview import http
from tests.test_flora_security_repair_01b import authority,signed
from tests.test_flora_research_intelligence import web

pytestmark=pytest.mark.real_security_boundary
ROOT=Path(__file__).resolve().parents[1]
BASE='eaca26f2b31c3c9227bb797d60f7d3492a8313d1'

def main(html):return html.split('<main ',1)[1].split('</main>',1)[0]

def data():return deepcopy(v.current_data(v.Context('lloyds','landscape')))


def test_group_arrival_and_optional_preservation():
    body=main(gold.render({}))
    assert '<h1>Group overview</h1>' in body and '£502.8bn' in body and '£6.625bn' in body
    assert 'Gold Standard evaluation' in old.render({})
    assert '<h1>Retail Banking</h1>' in old.render({})
    assert 'From funding to earnings' in v.render('/enterprises/lloyds/legacy',{})
    assert gold.PATH+'?' not in v.render('/enterprises/lloyds',{})
    assert 'Original preview' in body and 'Current experience' in body
    for forbidden in ('<details','Explore the business','Investigate forces','Reading mode','Financial runs'):
        assert forbidden not in body


@pytest.mark.parametrize('stream',gold.REGIONS)
def test_all_fifteen_subjects_and_deep_states_are_finite_native_links(stream):
    for focus,label in gold.REGIONS[stream]:
        for detail in ('',*gold.DETAILS[focus]):
            state=gold.State(stream,focus,focus,detail)
            html=gold.render({'stream':[stream],'focus':[focus],'detail':[detail]})
            assert '<h1>'+label.replace('&','&amp;')+'</h1>' in html
            assert html.count('data-region-key=')==5 and html.count('aria-current="true"')==1
            assert html.count('data-region="')==3
            canvas=main(html)
            assert canvas.count('<details')==canvas.count('<details class="econ-basis">')<=1
            assert '.pdf' not in html and 'primary_content_sha256' not in html
            assert public_request_target(gold.href(state).split('#',1)[0])


@pytest.mark.parametrize('query',[{'workspace':['private']},{'analysis':['fi-private']},{'focus':['BK-ENT-003']},
 {'detail':['secret']},{'focus':['retail'],'detail':['envoy']},{'stream':['forces','inside']},
 {'stream':['private']},{'subject':['foreign']},{'focus':'group'},{'detail':[]}])
def test_state_does_not_select_identity_permissions_or_private_financial_data(query):
    with pytest.raises(ValueError):gold.render(query)


@pytest.mark.parametrize('suffix',['?workspace=private','?analysis=fi-private','?lens=inspection','?selected=natwest',
 '/snapshot','/export','//private','%2fprivate','/../private','?focus=group&focus=retail','/assets/styles?analysis=fi-private'])
def test_route_catalogue_does_not_expand_private_or_export_surface(http,suffix):
    status,_,_=http(gold.PATH+suffix)
    assert status==403 and not public_request_target(gold.PATH+suffix)


def test_http_read_only_headers_and_semantic_head(http):
    for path in (gold.PATH,gold.PATH+'/assets/styles'):
        status,headers,body=http(path)
        assert status==200 and headers['Cache-Control']=='no-store'
        status,headers,body=http(path,'HEAD')
        assert status==200 and headers['Cache-Control']=='no-store' and not body
    assert http(gold.PATH+'?focus=private','HEAD')[0]==404
    assert http(gold.PATH,'POST')[0]==403


@pytest.mark.parametrize('flag',['withdrawn','revoked','owner_only','stale','superseded','contradictory'])
def test_withdrawn_sources_remove_all_dependent_numeric_accessibility_and_analysis_outputs(monkeypatch,flag):
    d=data();next(s for s in d['sources'] if s['id']=='PR-LBG-Q326')[flag]=True
    monkeypatch.setattr(v,'current_data',lambda ctx:d)
    from cios.applications.flora.research_intelligence import source_import
    monkeypatch.setattr(source_import,'current_source_records',lambda _domain: d['sources'])
    for query in ({},{'focus':['economics']},{'focus':['economics'],'detail':['sources']},
                  {'stream':['forces'],'focus':['analysis']},{'stream':['forces'],'focus':['strategy']}):
        html=gold.render(query)
        assert '£502.8bn' not in html and '£6.6bn' not in html and 'value="502.8"' not in html
        assert 'href="'+gold.PATH+'?stream=forces&amp;focus=analysis&amp;subject=analysis&amp;detail=theme-4' not in html
    assert '£496.5bn' in gold.render({'focus':['economics'],'detail':['funding']})


def test_withdrawn_collaboration_does_not_survive_in_application_or_supplier_descriptions(monkeypatch):
    d=data()
    # Google now has a separately inspected platform disclosure as well as
    # the Envoy collaboration. Both must be withdrawn to require its absence.
    for source in d['sources']:
        if source['id'] in {'PR-LBG-ENVOY','LCE-VERTEX'}:source['withdrawn']=True
    monkeypatch.setattr(v,'current_data',lambda ctx:d)
    from cios.applications.flora.research_intelligence import source_import
    monkeypatch.setattr(source_import,'current_source_records',lambda _domain: d['sources'])
    for focus,detail in [('applications','envoy'),('partners','google'),('partners','')]:
        html=main(gold.render({'stream':['inside'],'focus':[focus],'detail':[detail]}))
        assert 'Google Cloud' not in html and '<h2>Envoy</h2>' not in html
    assert 'Microsoft Copilot' in gold.render({'stream':['inside'],'focus':['applications']})


@pytest.mark.parametrize('field,value',[('entity_scope','TSB Bank plc'),('reporting_period','Year ended 2025'),
 ('metric_unit','USD billion'),('metric_unit','GBP billion; underlying pretax profit'),('kind','management_expectation'),
 ('metric_value',999),('metric_value',float('nan')),('metric_value',-1)])
def test_financial_entity_period_basis_unit_actual_and_value_binding(monkeypatch,field,value):
    d=data()
    for c in d['claims']:
        if c['id'] in gold.recovery.MEASURES:c[field]=value
    monkeypatch.setattr(v,'current_data',lambda ctx:d)
    from cios.applications.flora.research_intelligence import source_import
    monkeypatch.setattr(source_import,'current_source_records',lambda _domain: d['sources'])
    html=gold.render({'focus':['economics']})
    assert '£502.8bn' not in html and '£496.5bn' not in html and '£6.6bn' not in html
    # Invalid legacy claims cannot change the independently verified Source lines.
    assert '£999bn' not in html and '£6.625bn' in html


def test_held_investor_site_figures_remain_inactive_without_independent_filings(monkeypatch):
    monkeypatch.setattr(gold.lloyds_financials.public_statements, 'statement_series', lambda subject: ())
    from cios.applications.flora.financial_intelligence import candidate_analytics
    assert len(candidate_analytics.public_factual_projection()['facts']) == 3
    html=''.join(gold.render({'stream':[s],'focus':[f],'detail':[d]}) for s,rows in gold.REGIONS.items() for f,_ in rows for d in ('',*gold.DETAILS[f]))
    for held in ('4,293','£395.3','£321.8','.pdf','£100m opportunity'):
        assert held not in html
    assert 'Different businesses, different economics' in html and '£2.256bn' in html
    assert 'underlying reporting-segment results' in html and 'none is allocated' in html
    assert all(x in html for x in ('£2.256bn','£1.425bn','£4.215bn','£6.625bn'))


def test_capability_relationships_and_unknown_contracts_never_become_verified_edges():
    d=data();f=gold.facts_for(d)
    html=gold.main(gold.State('inside','applications','applications','envoy'),d,f)
    # The executive view now explains the material limits instead of rendering
    # empty contract/expiry fields. Keep the same anti-inference boundary.
    for word in ('does not establish a contracting entity', 'an exclusive cloud estate',
                 'application used by any particular division', 'not an asserted Lloyds architecture'):
        assert word in html
    # A specific Vertex deployment is now source-backed; that does not prove
    # an Envoy/whole-estate dependency or a commercial contract.
    assert 'Vertex AI' in html and 'detail=platform-delivery' in html
    for false in ('AWS','Oracle','2030-12-31','Contracted Google Cloud service'):
        assert false not in html
    # Unverified graph inventory is not read by this renderer.
    d['relationships']=[{'subject':'Lloyds','predicate':'depends_on','object':'Oracle','verified':False}]
    assert gold.main(gold.State('inside','applications','applications','envoy'),d,f)==html


def test_eight_swot_themes_live_only_at_analysis_and_are_research_not_qualification():
    html=gold.render({'stream':['forces'],'focus':['analysis']})
    assert 'Four-quadrant SWOT' in html
    for index in range(8):assert 'detail=theme-'+str(index) in html
    for focus,_ in gold.REGIONS['forces']:
        if focus!='analysis':assert 'Four-quadrant SWOT' not in gold.render({'stream':['forces'],'focus':[focus]})
    html=gold.render({'stream':['forces'],'focus':['analysis'],'detail':['theme-2']})
    assert 'already a decision taken' in html and 'No buyer mandate' in html


def test_subject_survives_cross_perspective_and_returns_to_original_division():
    state=gold.State('landscape','commercial','commercial')
    target=gold.href(state,stream='inside')
    assert 'focus=operations' in target and 'subject=commercial' in target
    state=gold.State('inside','operations','commercial')
    assert 'focus=commercial' in gold.href(state,stream='landscape')
    assert 'From Commercial Banking' in gold.render({'stream':['inside'],'subject':['commercial']})


@pytest.mark.parametrize('state',['guest','forged','owner','expired','revoked-membership'])
def test_public_private_equivalence_without_financial_run_discovery(authority,tmp_path,monkeypatch,state):
    from cios.applications.flora.financial_intelligence import candidate_analytics,analyst
    from cios.applications.flora import document_review as review
    def forbidden(*args,**kwargs):raise AssertionError('Private service read prohibited')
    monkeypatch.setattr(candidate_analytics,'find_existing_run',forbidden)
    monkeypatch.setattr(review,'load_run',forbidden)
    monkeypatch.setattr(analyst,'_selected_financial',forbidden)
    headers={}
    if state=='forged':headers={'X-Flora-Roles':'cios_owner','X-Flora-Workspace':'foreign'}
    if state in {'owner','expired','revoked-membership'}:
        store,token,_,headers,_=signed(authority,tmp_path)
        if state!='owner':
            with store.transaction() as db:
                if state=='expired':db.execute('UPDATE tokens SET expires=0 WHERE hash=?',(digest(token),))
                else:db.execute('UPDATE memberships SET active=0,version=version+1')
            assert security.verified_context(headers) is None
    assert main(gold.render({}))==main(gold.render({},headers))


def test_original_assets_and_default_renderers_are_byte_unchanged_except_optional_preview_link():
    from cios.applications.flora import visual_panels
    assert (ROOT/'cios/applications/flora/visual_panels.py').read_bytes()==subprocess.check_output(['git','show',BASE+':cios/applications/flora/visual_panels.py'],cwd=ROOT)
    art=ROOT/'cios/applications/flora/visual_stream_assets'/(gold.twin.ART+'.webp')
    assert sha256(art.read_bytes()).hexdigest()=='13827db67c3077e5a390965499c38ec2a93d3003cde580895d86eac82140d80f'
    current=(ROOT/'cios/applications/flora/living_enterprise_preview.py').read_text()
    assert current.replace('<a href="/enterprises/lloyds/preview/gold">Gold Standard evaluation</a>','')==subprocess.check_output(['git','show',BASE+':cios/applications/flora/living_enterprise_preview.py'],cwd=ROOT,text=True)


def test_exact_route_evolution_preserves_historical_pins_and_denies_arbitrary_mutations(monkeypatch):
    from tools.research import ux_unify_compatibility as c
    original=ast.parse(subprocess.check_output(['git','show',BASE+':tools/research/ux_unify_compatibility.py'],cwd=ROOT))
    for node in original.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id.isupper():
            assert getattr(c,node.targets[0].id)==ast.literal_eval(node.value)
    read=Path.read_bytes
    for path,pin in c.GOLD_ROUTE_PINS.items():
        target=ROOT/path;current=target.read_bytes()
        reviewed=c.ceo_predecessor(ROOT,path,current)
        assert sha256(reviewed).hexdigest()==pin
        previous=c.gold_route_predecessor(ROOT,path,reviewed)
        assert previous==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
        assert c.predecessor(ROOT,path)!=current
        mutation=current+b'\n# Unreviewed routing mutation\n'
        assert c.gold_route_predecessor(ROOT,path,mutation)==mutation
        with monkeypatch.context() as patch:
            patch.setattr(Path,'read_bytes',lambda self:mutation if self==target else read(self))
            assert c.predecessor(ROOT,path)==mutation
    # Every handler method except the finite read-only GET/HEAD dispatch remains
    # the original AST, including POST, mutation, auth and workspace enforcement.
    def methods(source):
        tree=ast.parse(source)
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='FloraWebHandler')
        return {n.name:ast.dump(n) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name not in {'do_GET','do_HEAD'}}
    path='cios/applications/flora/web/app.py'
    assert methods((ROOT/path).read_text())==methods(subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT,text=True))


@pytest.mark.parametrize('mutation',[{'enterprise_twin_id':'BK-ENT-003'},{'owner_only':True},{'withdrawn':True}])
def test_assessment_identity_and_private_metadata_are_denied_before_model_content(monkeypatch,mutation):
    d=data();d.update(mutation);d['capabilities'][0]['title']='PRIVATE CAPABILITY'
    monkeypatch.setattr(v,'current_data',lambda ctx:d)
    from cios.applications.flora.research_intelligence import source_import
    monkeypatch.setattr(source_import,'current_source_records',lambda _domain: d['sources'])
    for stream in gold.REGIONS:
        with pytest.raises(PermissionError):gold.render({'stream':[stream]})


def test_private_model_rows_and_wrong_claim_identity_are_not_published(monkeypatch):
    d=data();d['capabilities'][0].update(owner_only=True,title='PRIVATE CAPABILITY')
    d['programmes'][0].update(owner_only=True,title='PRIVATE PROGRAMME')
    next(c for c in d['claims'] if c['id']=='LBG-Q326-PROFIT')['asset_id']='BK-ENT-003'
    monkeypatch.setattr(v,'current_data',lambda ctx:d)
    from cios.applications.flora.research_intelligence import source_import
    monkeypatch.setattr(source_import,'current_source_records',lambda _domain: d['sources'])
    assert '£6.6bn' not in gold.render({})
    assert 'PRIVATE CAPABILITY' not in gold.render({'stream':['inside'],'focus':['capabilities']})
    assert 'PRIVATE PROGRAMME' not in gold.render({'stream':['inside'],'focus':['programmes']})


def test_every_counted_eligible_claim_has_substantive_non_source_main_output():
    import re
    found=set()
    subjects=[(stream,focus) for stream,rows in gold.REGIONS.items() for focus,_ in rows]+[('inside','people')]
    for stream,focus in subjects:
        for detail in ('',*(d for d in gold.DETAILS[focus] if d!='sources')):
            body=main(gold.render({'stream':[stream],'focus':[focus],'detail':[detail]}))
            found.update(re.findall('data-claim-id="([^"]+)"',body))
    # Scale figures use the existing amount component; they are checked above.
    assert set(gold.LLOYDS_IDS)-set(gold.recovery.MEASURES)<=found


def test_other_existing_owners_supply_scoped_service_outcomes_and_stock_recipe():
    from cios.applications.flora import leadership_agenda
    service=main(gold.render({'stream':['inside'],'focus':['operations'],'detail':['service']}))
    assert 'data-intelligence="lloyds-product-workload"' in service and '115,687' in service
    assert 'Lloyds Bank PLC' in service and 'not the consolidated Group or Retail' in service
    assert all(value in service for value in ('118,762','118,861','66.12'))
    assert 'Open Government Licence' in service and 'different cohorts' in service
    economics=main(gold.render({'focus':['economics'],'detail':['funding']}))
    assert 'data-owner-item="customer_deposits-movement"' in economics
    assert '6320m' in economics and 'data-semantic-type="calculated"' in economics
    assert 'not adjusted for consolidation' in economics
    issue=next(row for row in leadership_agenda.agenda('lloyds',data()) if row.key=='funding-base')
    assert issue.facts[-1].method=='502.8 − 496.5 = 6.3 GBP billion; arithmetic comparison of the published stocks.'


@pytest.mark.parametrize('release',['base','service'])
def test_fca_source_withdrawal_removes_dependent_service_outputs_only(monkeypatch,release):
    import json
    from cios.applications.flora import leadership_agenda as a
    target=a.CANDIDATE if release=='base' else a.model.REPO/'enterprise-knowledge/banking/research-model/source-snapshots/EAI1-FCA-Service-Candidate.json'
    read=Path.read_text
    def withdraw(path,*args,**kw):
        text=read(path,*args,**kw)
        if path==target:
            package=json.loads(text);package['source']['withdrawn']=True
            return json.dumps(package)
        return text
    monkeypatch.setattr(Path,'read_text',withdraw)
    html=main(gold.render({'stream':['inside'],'focus':['operations'],'detail':['service']}))
    if release=='base':
        assert '118,762' not in html and 'data-owner-item=' not in html
    else:
        assert '118,762' in html and '118,861' not in html and '66.12' not in html
    assert '£502.8bn' in gold.render({})


def test_stock_withdrawal_removes_existing_calculated_result(monkeypatch):
    d=data();next(s for s in d['sources'] if s['id']=='PR-LBG-AR25')['withdrawn']=True
    monkeypatch.setattr(v,'current_data',lambda ctx:d)
    from cios.applications.flora.research_intelligence import source_import
    monkeypatch.setattr(source_import,'current_source_records',lambda _domain: d['sources'])
    html=gold.render({'focus':['economics'],'detail':['funding']})
    assert '£6.3bn' not in html and 'funding-stock-change' not in html
    assert '£502.777bn' in html and '6320m' in html
    # Current Q3 source independently reports both stocks; the withdrawn
    # annual-source recipe must not replace or suppress that current input.
    from cios.applications.flora import leadership_agenda
    assert 'funding-base' not in {x.key for x in leadership_agenda.agenda('lloyds',d)}


def test_deep_link_serialisation_and_parent_navigation_do_not_lose_or_trap_detail():
    from urllib.parse import urlsplit,parse_qs
    state=gold.State('inside','operations','operations','service')
    assert gold.resolve(parse_qs(urlsplit(gold.href(state)).query,keep_blank_values=True))==state
    assert 'detail=&amp;' not in gold.link(state,'Back')
    assert 'detail=#visual-content' in gold.link(state,'Back')


def test_ceo_deep_links_keep_subject_and_withdraw_strategy_goals(http, monkeypatch):
    state = gold.State('forces', 'strategy', 'commercial', 'goals')
    target = gold.href(state).split('#', 1)[0]
    status, _, html = http(target)
    assert status == 200
    assert 'From Commercial Banking' in html
    assert 'data-claim-id="LBG-A2030-CIR"' in html
    assert 'Management objectives, on their own reporting horizons.' in html
    current = data()
    next(source for source in current['sources'] if source['id'] == 'PR-LBG-A2030')['withdrawn'] = True
    monkeypatch.setattr(v, 'current_data', lambda ctx: current)
    from cios.applications.flora.research_intelligence import source_import
    monkeypatch.setattr(source_import,'current_source_records',lambda _domain: current['sources'])
    status, _, html = http(target)
    assert status == 200
    assert 'From Commercial Banking' in html
    assert 'data-claim-id="LBG-A2030-CIR"' not in html
    assert 'Improve cost efficiency' not in html
    assert 'data-claim-id="LBG-Q326-INVESTMENT"' in html


def test_people_view_withdraws_workforce_evidence_without_inventing_accountability(monkeypatch):
    query = {'stream': ['inside'], 'focus': ['people'], 'detail': ['workforce']}
    html = gold.render(query)
    assert 'detail=frontier' in html and '30,000' not in html
    assert 'Licences are not people' in html
    current = data()
    next(source for source in current['sources'] if source['id'] == 'PR-LBG-AR25')['withdrawn'] = True
    monkeypatch.setattr(v, 'current_data', lambda ctx: current)
    from cios.applications.flora.research_intelligence import source_import
    monkeypatch.setattr(source_import,'current_source_records',lambda _domain: current['sources'])
    html = gold.render(query)
    # The independent, source-bound June 2026 disclosure survives withdrawal
    # of the older annual-report source; the older claim does not.
    assert 'detail=frontier' in html
    assert 'data-claim-id="LBG-AR25-COPILOT"' not in html
    assert 'Licences are not people' in html
