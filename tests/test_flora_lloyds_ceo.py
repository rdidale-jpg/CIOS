"""CEO default, historical compatibility and exact Source/financial authority."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
import ast,json,subprocess
import pytest
from cios.applications.flora import lloyds_gold as g,visual_streams as v,security
from cios.applications.flora.research_intelligence import source_import as source
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_living_enterprise_preview import http
from tests.test_flora_security_repair_01b import authority,signed
from tests.test_flora_research_intelligence import web
pytestmark=pytest.mark.real_security_boundary
ROOT=Path(__file__).resolve().parents[1]
BASE='1c13e6962516dbb071b2133f2c1a3de87647e2ac'

def main(html):return html.split('<main ',1)[1].split('</main>',1)[0]
def query(stream='landscape',focus='group',detail=''):return {'stream':[stream],'focus':[focus],'detail':[detail]}


def test_promoted_default_has_group_identity_and_only_three_primary_perspectives(http):
    code,headers,body=http('/enterprises/lloyds')
    assert code==200 and headers['Cache-Control']=='no-store'
    assert 'data-experience="lloyds-ceo"'in body and '<h1>Group overview</h1>'in body
    assert g.twin.ART in body and '£502.8bn'in body and '£6.6bn'in body
    for obsolete in ('Gold Standard · owner evaluation','Original preview','Current experience','Preview New Experience','Reading mode','Explore the business','Investigate forces'):
        assert obsolete not in main(body)
    assert body.count('aria-label="Insight streams"')==1
    assert '<details'not in main(body)


@pytest.mark.parametrize('stream',g.REGIONS)
def test_perspectives_and_canonical_native_links_keep_subject_and_scope(stream):
    body=v.render('/enterprises/lloyds',{'stream':[stream]})
    assert 'data-experience="lloyds-ceo"'in body and 'data-stream="'+stream+'"'in body
    assert body.count('data-region-key=')==5 and body.count('aria-current="true"')==1
    assert g.PATH+'?' not in body
    assert 'data-region-key="people"'in body if stream=='inside' else True
    state=g.State('inside','people','commercial','workforce',g.CANONICAL)
    assert g.href(state).startswith(g.CANONICAL+'?')
    assert g.resolve(parse_qs(urlsplit(g.href(state)).query,keep_blank_values=True)).detail=='workforce'


@pytest.mark.parametrize('suffix',['?workspace=foreign','?analysis=fi-private','?focus=group&focus=retail','?focus=private','?subject=BK-ENT-003','?market=FR','?selected=natwest','?focus=people&stream=landscape','?detail=private'])
def test_new_default_never_expands_private_or_foreign_selectors(http,suffix):
    status,_,body=http(g.CANONICAL+suffix)
    assert status in {403,404}
    assert 'data-experience="lloyds-ceo"' not in body


def test_old_specialist_deep_links_and_previous_presentations_remain_available(http):
    for target,expected in [('/enterprises/lloyds/legacy','From funding to earnings'),('/enterprises/lloyds/preview','Experimental design'),('/enterprises/lloyds/preview/gold','Gold Standard · owner evaluation'),('/enterprises/lloyds?stream=landscape&detail=flagship','Overview')]:
        status,_,body=http(target);assert status==200 and expected in body
    assert http('/enterprises/lloyds?analysis=fi-private')[0]==403
    assert http('/enterprises/lloyds?lens=inspection')[0]==403
    assert http('/enterprises/lloyds','POST')[0]==403


def test_named_role_is_dated_government_context_not_current_mandate_or_buyer():
    html=main(v.render(g.CANONICAL,query('inside','people','leadership')))
    assert 'Charlie Nunn' in html and '22 March 2026'in html
    assert 'not a verified current mandate or purchasing authority'in html
    assert 'Open Government Licence'in html
    assert all(name not in html for name in ('Amanda Murphy','John Langley','Ron van Kemenade','William Chalmers'))
    package=source.public_enterprise_role();assert package and package[1]['current_mandate_verified']is False


@pytest.mark.parametrize('level',['package','source','fact'])
@pytest.mark.parametrize('flag',['withdrawn','revoked','owner_only','stale','contradictory','superseded'])
def test_role_lifecycle_hides_all_dependent_names_and_context(monkeypatch,level,flag):
    path=source.model.REPO/'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.json' if hasattr(source,'model') else ROOT/'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.json'
    original=Path.read_text
    def read(p,*args,**kw):
        text=original(p,*args,**kw)
        if p==path:
            doc=json.loads(text);target=doc if level=='package' else doc['source']if level=='source' else doc['facts'][0];target[flag]=True
            return json.dumps(doc)
        return text
    monkeypatch.setattr(Path,'read_text',read)
    assert not source.public_enterprise_role()
    for q in ({},query('inside','people','leadership'),query('inside','people','sources')):
        assert 'Charlie Nunn'not in main(v.render(g.CANONICAL,q))
    assert '£502.8bn'in v.render(g.CANONICAL,{})


@pytest.mark.parametrize('field,value',[('subject_id','BK-ENT-003'),('legal_name','Lloyds Bank plc'),('period','2026-11-24'),('current_mandate_verified',True),('name','Private person'),('role','Confirmed buyer')])
def test_government_fact_scope_and_dated_meaning_are_not_self_relabelled(monkeypatch,field,value):
    target=ROOT/'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.json';read=Path.read_text
    def altered(p,*a,**kw):
        text=read(p,*a,**kw)
        if p==target:
            doc=json.loads(text);doc['facts'][0][field]=value;return json.dumps(doc)
        return text
    monkeypatch.setattr(Path,'read_text',altered)
    assert not source.public_enterprise_role()


def test_workforce_is_unavailable_without_proxy_counts_or_invented_chart():
    html=main(v.render(g.CANONICAL,query('inside','people','workforce')))
    assert 'Comparable workforce totals and distribution are unavailable' in html
    assert 'Licences are not people'in html and 'No headcount or workforce chart is derived'in html
    assert '<meter'not in html and 'data-semantic-type="calculated"'not in html
    assert '30,000' in html or '30000' in html
    assert 'Correspondence address'not in html and 'Date of birth'not in html


def test_business_hierarchy_does_not_merge_legal_entities_segments_functions_people():
    html=main(v.render(g.CANONICAL,query('inside','people','structure')))
    assert 'Reporting businesses · not legal subsidiaries'in html
    assert 'Conceptual function lenses · not a verified organisation chart'in html
    assert 'Named owner / mandate unavailable'in html


@pytest.mark.parametrize('key',tuple(g.JOURNEYS))
def test_deep_journeys_separate_conceptual_paths_from_specific_estate_edges(key):
    html=main(v.render(g.CANONICAL,query('inside','operations','journey-'+key)))
    assert 'no verified application, role or supplier dependency is inferred'in html
    assert 'Commercial significance'in html and 'Account investigation'in html
    assert 'No buyer need, budget, procurement event or supplier demand'in html
    for invented in ('Oracle installation','AWS contract','Renewal: 2030','£100m opportunity'):assert invented not in html


@pytest.mark.parametrize('row',g.OBJECTIVES)
def test_objectives_use_real_horizons_and_do_not_claim_unsupported_progress(row):
    key,horizon,title,*_=row
    html=main(v.render(g.CANONICAL,query('forces','strategy','objective-'+key)))
    assert title in html and horizon in html
    assert 'no inferred progress percentage'in html
    assert 'not verified buying authority'in html
    assert 'External intervention is a hypothesis only'in html


def test_held_financials_are_not_promoted_by_the_new_default():
    from cios.applications.flora.financial_intelligence import candidate_analytics as financial
    assert financial.public_factual_projection()=={}
    html=''.join(main(v.render(g.CANONICAL,query('landscape','economics',detail))) for detail in ('income','costs','capital','divisions'))
    for held in ('2,256','1,425','4,215','£6,625','£11,084','3.21%','17.9%','.pdf'):assert held not in html
    assert 'Unavailable'in html and 'not a proxy'not in html
    assert 'different' in html or 'Separate' in html


def test_core_source_permissions_and_all_existing_functions_remain_unchanged():
    path='cios/applications/flora/research_intelligence/source_import.py'
    old=ast.parse(subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT))
    new=ast.parse((ROOT/path).read_text())
    strip=lambda t:ast.dump(ast.Module(body=[n for n in t.body if not isinstance(n,ast.FunctionDef)or n.name!='public_enterprise_role'],type_ignores=[]),include_attributes=False)
    assert strip(old)==strip(new)

@pytest.mark.parametrize('route',[g.CANONICAL,g.LEGACY,g.PATH])
def test_head_responses_do_not_cache_source_dependent_public_representations(http,route):
    status,headers,body=http(route,'HEAD')
    assert status==200 and headers['Cache-Control']=='no-store' and not body


def test_exact_compatibility_cut_rejects_unreviewed_bytes_and_keeps_all_historic_pins():
    from tools.research import ux_unify_compatibility as compatibility
    for name,digest in compatibility.CEO_PINS.items():
        current=(ROOT/name).read_bytes()
        assert sha256(current).hexdigest()==digest
        assert compatibility.ceo_predecessor(ROOT,name,current)==subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
        mutated=current+b'\n# unreviewed mutation\n'
        assert compatibility.ceo_predecessor(ROOT,name,mutated)==mutated
    old=ast.parse(subprocess.check_output(['git','show',BASE+':tools/research/ux_unify_compatibility.py'],cwd=ROOT,text=True))
    new=ast.parse((ROOT/'tools/research/ux_unify_compatibility.py').read_text())
    constants=lambda tree:{n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
    before,after=constants(old),constants(new)
    assert all(after[name]==value for name,value in before.items())


@pytest.mark.parametrize('section,field,value',[('source','url','https://unapproved.invalid/'),('source','publication_date','2026-11-24'),('source','restrictions',['no-public-use']),('rights','status','pending'),('rights','terms_url','https://unapproved.invalid/'),('rights','material_exceptions',['unresolved']),('rights','revoked',True),('package','canonical_mutation',True),('package','authority','canonical')])
def test_role_publication_requires_the_exact_existing_open_government_scope(monkeypatch,section,field,value):
    target=ROOT/'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.json';read=Path.read_text
    def altered(p,*a,**kw):
        text=read(p,*a,**kw)
        if p==target:
            doc=json.loads(text);record=doc if section=='package' else doc['source']['rights'] if section=='rights' else doc['source'];record[field]=value
            return json.dumps(doc)
        return text
    monkeypatch.setattr(Path,'read_text',altered)
    assert not source.public_enterprise_role()
    assert 'Charlie Nunn'not in main(v.render(g.CANONICAL,query('inside','people','leadership')))


def test_strategy_questions_are_distinct_and_do_not_create_progress_or_buyers():
    questions=[context[1] for context in g.GOAL_DECISIONS.values()]
    assert len(set(questions))==len(g.OBJECTIVES)==7
    for key,*_ in g.OBJECTIVES:
        html=main(v.render(g.CANONICAL,query('forces','strategy','objective-'+key)))
        assert g.GOAL_DECISIONS[key][1] in html.replace('&amp;','&')
        assert 'role hypothesis, not verified buying authority'in html
        assert 'no inferred progress percentage'in html

@pytest.mark.parametrize('change',['json','txt','unknown'])
def test_history_keeps_new_role_bytes_exact_and_rejects_unreviewed_additions(tmp_path,monkeypatch,change):
    import shutil
    from tools.research import history_integrity as history
    # Reuse immutable historical git objects, while changing only an isolated copy.
    root=tmp_path/'repo';shutil.copytree(ROOT/'enterprise-knowledge',root/'enterprise-knowledge')
    shutil.copytree(ROOT/'docs/flora-runtime/public-financial-intelligence',root/'docs/flora-runtime/public-financial-intelligence')
    original=history._git;monkeypatch.setattr(history,'_git',lambda _,*args:original(ROOT,*args))
    assert history.verify_history(root)['old_review_records_retained']is True
    file=root/'enterprise-knowledge/banking/research-model/source-snapshots'/('unknown.txt'if change=='unknown'else'CEO1-GOV-ROLE.'+change)
    file.write_text(file.read_text()+'\nchanged'if file.exists()else'unknown')
    with pytest.raises(AssertionError):history.verify_history(root)


def test_existing_eai_outcomes_and_funding_still_have_one_source_guarded_entry():
    html=main(v.render(g.CANONICAL,{}))
    assert html.count('data-intelligence="funding-base"')==1
    assert html.count('agenda=service-recovery#agenda-insight')==1
    assert 'Funding comparison'in html and 'Customer outcomes'in html


def test_existing_isolated_replay_owner_is_preserved_without_guest_or_production_authority(monkeypatch):
    from cios.applications.flora.memory import commercial_views
    calls=[]
    def guarded(binding,stream,headers):
        calls.append((binding,stream,headers));return ''
    monkeypatch.setattr(commercial_views,'commercial_change',guarded)
    v.render(g.CANONICAL,{'stream':['forces']})
    assert calls==[('lloyds','forces',None)]
    assert 'data-commercial-change'not in v.render(g.CANONICAL,{'stream':['forces']})
