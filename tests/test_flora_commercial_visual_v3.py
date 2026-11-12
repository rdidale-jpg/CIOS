"""Evidence-backed visual journey, deliberate capture and inherited authority controls."""
from copy import deepcopy
import hashlib,json,subprocess
from html import unescape
from pathlib import Path
import pytest
from cios.applications.flora.research_intelligence import model,understanding as u
from cios.applications.flora.research_intelligence.commercial_intelligence import commercial_projection,commercial_map
from cios.applications.flora.research_intelligence.commercial_views import enterprise_body,candidate_overview
from cios.applications.flora.research_intelligence.living_map_specs import build_living_map
from cios.applications.flora.research_intelligence.living_map import render_living_map
from cios.applications.flora import sales_pipeline as sales
from cios.applications.flora.storage import data_path
from cios.applications.flora.security_store import canonical
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor,web,complete
from tests.test_flora_research_intelligence import Links
ASOF='2026-11-10'
CORE='VI-LBG-PLATFORMS'
ORIGIN='RCO-LBG-001'


def projection(domain='banking'):
    return commercial_projection(model.load_assessment(domain),as_of=ASOF)


def store_hash():
    p=data_path('sales_pipeline','opportunities.json')
    return hashlib.sha256(p.read_bytes() if p.exists() else b'absent').hexdigest()


@pytest.mark.parametrize('domain,total',[('banking',9),('aviation',6)])
def test_projection_is_reproducible_read_only_and_preserves_existing_identities(domain,total):
    d=model.load_assessment(domain);r=u.load_review(domain);before=deepcopy((d,r))
    p=commercial_projection(d,r,ASOF)
    assert p==commercial_projection(d,r,ASOF) and (d,r)==before
    assert len(p['candidates'])==total
    assert {c['id'] for c in p['candidates']}=={c['id'] for c in d['candidates']}
    assert p['authority']=='candidate_intelligence' and not p['automatic_capture'] and not p['automatic_qualification']
    assert all(c['status']=='Unqualified research hypothesis' for c in p['candidates'])


def test_core_platforms_exposes_existing_lloyds_hypothesis_and_coverage_is_not_ownership():
    d=model.load_assessment();p=projection();scene=build_living_map(d,as_of=ASOF);before=deepcopy(scene)
    decorated=commercial_map(scene,p);assert scene==before
    n=next(n for n in decorated['map_nodes'] if n['id']==CORE)
    assert ORIGIN in {r['id'] for r in n['commercial_candidates']}
    assert n['commercial_supported_count']==sum(r['context_supported'] for r in n['commercial_candidates'])
    html=render_living_map(decorated,'commercial')
    assert 'Research coverage association' in html and 'not a confirmed implementation dependency' in html
    assert '/enterprises/lloyds?lens=commercial#activity-'+CORE in unescape(html)
    assert 'market attractiveness' in html and 'counts are not additive' in html
    original=deepcopy(p)
    n['commercial_candidates'][0]['title']='Synthetic view edit'
    assert p==original


def test_zero_signal_activity_is_valid_and_does_not_invent_content():
    p=projection();p['candidates']=[]
    scene=commercial_map(build_living_map(model.load_assessment(),as_of=ASOF),p)
    assert all(n['commercial_supported_count']==0 and not n['commercial_candidates'] for n in scene['map_nodes'])
    h=render_living_map(scene,'commercial')
    assert 'Zero signals is valid' in h and "class='lm-commercial-count'" not in h
    assert ORIGIN not in h


def test_withdrawn_or_index_only_support_leaves_authored_ratings_historical_and_context_unknown():
    d=model.load_assessment();r=u.load_review('banking')
    for source in d['sources']:
        if source['verification']=='primary_retrieved':source['retrieval_extent']='Search-index-only excerpt; original unverified'
    from cios.applications.flora.research_intelligence.cycle import digest
    r['baseline_digest']=digest(d)
    for review in r['claim_reviews']:
        for link in review['links']:link['locator']='Not reviewed in this synthetic fixture'
    p=commercial_projection(d,r,ASOF)
    assert not any(c['context_supported'] for c in p['candidates'])
    assert all(c['dimensions'] and 'not a recomputed' in c['assessment_limitation'].lower() for c in p['candidates'])
    html=candidate_overview(d,p['candidates'][0],p)
    assert 'Current source support is missing' in html
    assert 'Current source support missing' in html.split('</header>')[0]


def test_core_platform_counterevidence_keeps_exact_source_scope_and_lineage(web):
    r=next(r for r in projection()['candidates'] if r['id']==ORIGIN)
    assert len(r['counterevidence'])==2 and r['conflicts']
    for proof in r['counterevidence']:
        assert proof['passage'] and proof['locator'] and proof['source_ids'] and proof['period']
        path,_,fragment=proof['url'].partition('#');status,html,_=web(path,authenticated=False)
        assert status==200 and fragment in Links(html).ids
    h=candidate_overview(model.load_assessment(),r,projection())
    assert 'Counterevidence, contradictions' in h and 'Competing periods or denominators' in h
    assert all(p['id'] in h for p in r['counterevidence'])


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_ten_questions_unknowns_and_explainable_separate_ratings(domain):
    d=model.load_assessment(domain);p=projection(domain);r=p['candidates'][0]
    h=unescape(candidate_overview(d,r,p))
    for term in ['Potential business problem','Why might the enterprise act','Evidence supporting','Counterevidence','Potential technology','Possible stakeholders','Supplier and competitive','Missing commercial','Attractiveness and actionability','Next commercial action']:assert term in h
    assert 'Customer budget: Unknown' in h and 'Procurement date: Unknown' in h and 'Confirmed decision-maker: Unknown' in h
    assert 'Inferred' in h or 'inferred' in h
    for dimension in r['dimensions']:assert dimension['reason'] in h and dimension['anchor'] in h
    assert 'No combined score, win probability' in h


def test_historical_supplier_context_and_current_contract_uncertainty_are_preserved():
    p=projection('aviation');r=next(r for r in p['candidates'] if r['id']=='RCO-EJ-005')
    h=candidate_overview(model.load_assessment('aviation'),r,p)
    assert any('2023' in e['period'] or '2023' in e['label'] for e in r['support'])
    assert 'current supplier contract' in h and ('unknown' in h.lower() or 'unverified' in h.lower())


@pytest.mark.parametrize('domain,slug',[('banking','lloyds'),('aviation','easyjet')])
def test_public_commercial_routes_and_other_lenses_remain_available(web,domain,slug):
    for lens in ('overview','ai-disruption','regulation','commercial'):
        path=f'/industries/{domain}?lens={lens}';status,h,_=web(path,authenticated=False)
        assert status==200 and public_request_target(path)
        assert "data-living-map='2'" in h
    assert web(f'/enterprises/{slug}?lens=commercial',authenticated=False)[0]==200
    status,h,_=web(f'/industries/{domain}/visual-specs',authenticated=False)
    assert status==200 and set(json.loads(h))=={'pestle','five-forces','value-chain','operating-model','ecosystem','opportunities'}
    assert not public_request_target(f'/industries/{domain}?lens=commercial&workspace_id=other')


def test_exploration_never_reads_or_creates_private_pipeline_records(web,actor):
    before=store_hash()
    for path in ['/industries/banking?lens=commercial','/enterprises/lloyds?lens=commercial','/flora/banking/research/candidates/'+ORIGIN]:assert web(path)[0]==200
    assert store_hash()==before and sales.list_opportunities(headers=actor[3])==[]
    r=sales.create_opportunity('lloyds',ORIGIN,headers=actor[3]);frozen=store_hash()
    for authenticated in (True,False):
        status,h,_=web('/flora/banking/research/candidates/'+ORIGIN,authenticated=authenticated)
        assert status==200 and r['id'] not in h
    assert store_hash()==frozen


def test_complete_http_banking_lloyds_hypothesis_capture_qualification_pipeline_and_link(web,actor):
    status,maphtml,_=web('/industries/banking?lens=commercial');assert status==200
    enterprise='/enterprises/lloyds?lens=commercial'
    assert enterprise+'#activity-'+CORE in unescape(maphtml)
    status,h,_=web(enterprise);assert status==200 and 'activity-'+CORE in Links(h).ids
    candidate='/flora/banking/research/candidates/'+ORIGIN
    assert candidate+'#from-'+CORE in Links(h).urls
    status,h,_=web(candidate);assert status==200 and 'Counterevidence' in h and 'name="csrf"' in h
    assert sales.list_opportunities(headers=actor[3])==[]
    status,_,where=web('/flora/sales/capture',{'enterprise':'lloyds','origin':ORIGIN});assert status==303
    identifier=where.split('#')[0].rsplit('/',1)[1];r=sales.get_opportunity(identifier,headers=actor[3])
    assert r['stage']=='Discovered' and r['demonstration'] and r['qualification']=={} and not r['evidence_reviewed']
    assert r['amount']=='' and r['value_basis']=='Unknown'
    provenance=deepcopy(r['provenance']);assert len(provenance['commercial_review']['counterevidence_claim_ids'])==2
    before=store_hash()
    assert web('/flora/sales/'+identifier+'/save',{'version':r['version'],'stage':'Qualified','confirm':'yes'})[0]==422
    assert store_hash()==before
    fields={'version':r['version'],'stage':'Qualified','confirm':'yes','evidence_reviewed':'yes','activity':'Synthetic acceptance only; no Lloyds customer conversation asserted'}
    for key,value in complete().items():fields['q_'+key]=value['note'];fields['s_'+key]=value['source']
    assert web('/flora/sales/'+identifier+'/save',fields)[0]==303
    qualified=sales.get_opportunity(identifier,headers=actor[3])
    assert qualified['stage']=='Qualified' and qualified['provenance']==provenance
    assert web('/flora/sales/pipeline?stage=Qualified')[0]==200
    assert 'Qualified sales opportunity' in web('/flora/sales/pipeline?stage=Qualified')[1]
    status,_,linked=web('/flora/sales/capture',{'enterprise':'lloyds','origin':ORIGIN})
    assert status==303 and linked==where and sales.get_opportunity(identifier,headers=actor[3])==qualified
    assert len(sales.list_opportunities(headers=actor[3]))==1
    with actor[0].transaction() as db:
        events=[json.loads(row[0]) for row in db.execute("SELECT payload FROM audit WHERE event='sales_opportunity_mutation'")]
    assert len(events)==2 and events[-1]['workspace_id']==r['workspace_id']


def test_aviation_can_capture_existing_hypothesis_without_inventing_a_new_record_model(actor):
    with actor[0].transaction() as db:db.execute('UPDATE memberships SET enterprises=?',(canonical(['BK-ENT-001','AV-ENT-001']),))
    r=sales.create_opportunity('easyjet','RCO-EJ-001',headers=actor[3])
    assert r['origin_id']=='RCO-EJ-001' and r['stage']=='Discovered' and r['qualification']=={}
    assert r['enterprise_id']=='AV-ENT-001' and r['provenance']['commercial_review']['authority']=='candidate_intelligence'


@pytest.mark.parametrize('negative',['anonymous','csrf','workspace_override','foreign_origin'])
def test_rejected_http_capture_keeps_business_store_hash_unchanged(web,actor,negative):
    before=store_hash();fields={'enterprise':'lloyds','origin':ORIGIN};auth=True
    if negative=='anonymous':auth=False
    if negative=='csrf':fields['csrf']='synthetic-invalid'
    if negative=='workspace_override':fields['workspace_id']='other'
    if negative=='foreign_origin':fields['enterprise']='barclays'
    status,_,_=web('/flora/sales/capture',fields,authenticated=auth)
    assert status in (403,422) and store_hash()==before


@pytest.mark.parametrize('negative',['read_only','revoked','wrong_workspace','expired'])
def test_existing_membership_workspace_capability_session_boundary_blocks_direct_service(actor,negative):
    r=sales.create_opportunity('lloyds',ORIGIN,headers=actor[3]);before=store_hash()
    with actor[0].transaction() as db:
        if negative=='read_only':db.execute('UPDATE memberships SET roles=?,version=version+1',(canonical(['commercial_context.view']),))
        if negative=='revoked':db.execute('UPDATE memberships SET active=0,version=version+1')
        if negative=='wrong_workspace':
            db.execute("UPDATE memberships SET workspace_id='other',enterprises=?",(canonical(['*']),));db.execute("UPDATE tokens SET workspace_id='other'")
        if negative=='expired':db.execute('UPDATE tokens SET expires=0')
    with pytest.raises(PermissionError):sales.update_opportunity(r['id'],r['version'],{'title':'Rejected'},headers=actor[3])
    assert store_hash()==before


def test_existing_acl_and_forged_browser_identity_cannot_capture(actor):
    before=store_hash()
    with pytest.raises(PermissionError):sales.create_opportunity('lloyds',ORIGIN,headers={'X-Flora-User':'synthetic-human','X-Flora-Roles':'cios_owner'})
    assert store_hash()==before
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository,EnterpriseCanvasAccessRecord
    EnterpriseCanvasAccessRepository().save(EnterpriseCanvasAccessRecord('synthetic-acl','synthetic-canvas','BK-ENT-001','synthetic-workspace','another-owner'))
    with pytest.raises(PermissionError):sales.create_opportunity('lloyds',ORIGIN,headers=actor[3])
    assert store_hash()==before


def test_review_snapshot_is_immutable_and_duplicate_link_does_not_rewrite_prior_capture(actor,monkeypatch):
    from tests.test_flora_primary_enrichment import prior
    original_loader=model.load_assessment
    historical=prior()
    monkeypatch.setattr(model,'load_assessment',lambda:historical)
    old_capture=model.commercial_capture('lloyds',ORIGIN)
    assert 'commercial_review' not in old_capture['provenance']
    assert len(old_capture['provenance']['claim_ids'])==2
    monkeypatch.setattr(model,'load_assessment',original_loader)
    r=sales.create_opportunity('lloyds',ORIGIN,headers=actor[3]);original=model.commercial_capture
    def newer(*args):
        x=original(*args);x['provenance']['commercial_review']['review_digest']='synthetic-new-review';return x
    monkeypatch.setattr(model,'commercial_capture',newer)
    assert sales.create_opportunity('lloyds',ORIGIN,headers=actor[3])==r
    before=store_hash()
    with pytest.raises(sales.SalesValidationError):sales.update_opportunity(r['id'],r['version'],{'provenance':{}},headers=actor[3])
    assert store_hash()==before


def test_public_ui_has_finite_return_navigation_print_and_accessible_controls():
    p=projection();r=next(r for r in p['candidates'] if r['id']==ORIGIN)
    h=candidate_overview(model.load_assessment(),r,p)
    assert "class='cv-link cv-return'" in h and 'Object.prototype.hasOwnProperty' in h
    assert '#lm-banking-'+CORE in h and 'beforeprint' in h and 'afterprint' in h
    assert 'prefers-reduced-motion' in h and ':focus-visible' in h
    assert 'innerHTML' not in h and 'fetch(' not in h
    r=deepcopy(r);r['title']='<img src=x onerror=bad()>'
    assert '<img src=x' not in candidate_overview(model.load_assessment(),r,p)
    r['activities'][0]['label']='<script>synthetic-label</script>'
    h=candidate_overview(model.load_assessment(),r,p)
    import re
    payload=re.search(r"data-cv-returns>(.*?)</script>",h).group(1)
    assert json.loads(payload)[r['activities'][0]['id']]['label']==r['activities'][0]['label']
    assert '<script>synthetic-label' not in payload


def test_projection_cannot_be_attached_to_another_industry_map():
    with pytest.raises(ValueError):commercial_map(build_living_map(model.load_assessment('aviation')),projection())


def test_no_existing_research_history_or_source_identity_is_changed():
    # Both stacks are approved additions; their exact source bytes and original
    # records remain protected. Unknown paths and modifications still fail.
    from tools.research.history_integrity import verify_history
    verify_history(Path(__file__).resolve().parents[1])
