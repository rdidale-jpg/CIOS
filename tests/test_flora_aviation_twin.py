"""Aviation reuses the evidence/qualification spine; fixtures never seed production."""
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import json
from urllib.parse import urlsplit
import pytest
from cios.applications.flora.research_intelligence import model, sector_views
from cios.applications.flora.research_intelligence.registry import enterprise_reference
from cios.applications.flora.public_routes import public_request_target, public_read_path
from cios.applications.flora import sales_pipeline as sales
from cios.applications.flora.security_store import canonical
from tests.test_flora_research_intelligence import web
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor, complete, web as sales_web

ROOT='/flora/aviation/research'


class Links(HTMLParser):
    def __init__(self,html):
        super().__init__();self.urls=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            u=dict(attrs).get('href','')
            if u.startswith('/flora/aviation/'):self.urls.append(u)


@pytest.fixture
def aviation_actor(actor):
    with actor[0].transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?',(canonical(['AV-ENT-001','BK-ENT-001','BK-ENT-002']),))
    return actor


def test_same_schema_and_semantic_evidence_contracts_support_both_industries():
    banking=model.load_assessment();aviation=model.load_assessment('aviation')
    assert banking['industry_twin_id']=='BK-IND-002'
    assert aviation['industry_twin_id']=='AV-IND-001' and len(aviation['claims'])==22
    for data in (banking,aviation):
        assert model.validate(data)
        for c in data['claims']:
            semantic=model.candidate_claim(data,c);evidence=model.evidence_item(data,c)
            assert isinstance(semantic,model.CandidateClaim) and isinstance(evidence,model.EvidencePackageItem)
            assert semantic.authority=='candidate_intelligence'
            assert semantic.subject==(data['enterprise_twin_id'] if c['asset_id']==data['enterprise_twin_id'] else data['industry_twin_id'])


def test_complete_frameworks_and_resolved_force_capability_candidate_links():
    d=model.load_assessment('aviation')
    assert {l:sum(r['lens']==l for r in d['frameworks']) for l in model.LENSES}=={'pestle':6,'porter':5,'value-chain':8}
    for candidate in d['candidates']:
        assert candidate['driver_ids'] and candidate['capability_ids'] and candidate['programme_ids']
        assert all(any(r['subject']==cap and r['object']==candidate['id'] for r in d['relationships']) for cap in candidate['capability_ids'])
    assert not any(r['verified'] for r in d['relationships'] if r['predicate']=='may_affect')


def test_source_dates_originals_and_index_only_limits_are_honest():
    d=model.load_assessment('aviation');sources={s['id']:s for s in d['sources']}
    assert len(sources)==14 and sum(s['verification']=='primary_retrieved' for s in sources.values())==13
    assert sources['SRC-AV-AR25']['publication_date'] is None
    assert sources['SRC-AV-Q326']['publication_date'] is None
    assert 'search-index' in sources['SRC-AV-Q326']['retrieval_extent']
    assert 'search-index' in sources['SRC-AV-HOL26']['retrieval_extent']
    assert sources['SRC-AV-EURO26']['verification']=='citation_only'
    for s in sources.values():
        assert s['primary_content_sha256'] is None
        if s['verification']=='primary_retrieved':
            text=model.primary_text(s)
            assert hashlib.sha256(text.encode()).hexdigest()==s['text_sha256']
            assert sum(len(x['quote'].split()) for x in s['excerpts'])<=25
    for c in d['claims']:assert model.primary_claim_supported(d,c)


def test_snapshot_tamper_and_cross_sector_source_substitution_are_rejected(tmp_path,monkeypatch):
    d=model.load_assessment('aviation');s=d['sources'][0]
    for path in d['assets'].values():
        dest=tmp_path/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((model.REPO/path).read_bytes())
    dest=tmp_path/s['text_path'];dest.parent.mkdir(parents=True);dest.write_text('tampered')
    monkeypatch.setattr(model,'REPO',tmp_path)
    with pytest.raises(ValueError,match='digest mismatch'):model.primary_text(s)
    bad=deepcopy(d);bad['sources'][0]['research_domain']='banking'
    with pytest.raises(ValueError,match='registered research domain'):model.validate(bad)


def test_all_four_scores_are_distinct_bounded_rationales_not_win_probabilities():
    d=model.load_assessment('aviation');rows=model.commercial_candidates(d)
    assert [r['id'] for r in model.commercial_candidates(d,True)]==['RCO-EJ-001','RCO-EJ-002','RCO-EJ-003']
    assert model.commercial_dimensions(d)==('strategic_relevance','commercial_accessibility','evidence_maturity','seller_fit')
    for r in rows:
        a=r['commercial']
        assert all(type(a[k]['score']) is int and a[k]['score'] in range(4) and a[k]['reason'] for k in model.commercial_dimensions(d))
        assert a['commercial_accessibility']['score']<=1 and a['evidence_maturity']['score']<=2
        assert a['indicative_contract_value'] is None and a['procurement_date'] is None
        assert a['verified_buyer_names']==[] and not a['confirmed_supplier_demand']
        assert 'Inferred' in a['buyer_status'] and a['next_commercial_action']
    bad=deepcopy(d);bad['commercial_assessment']['assessments'][0]['seller_fit']['score']=True
    with pytest.raises(ValueError):model.validate(bad)


def test_supplier_edges_preserve_historical_and_planned_scope():
    d=model.load_assessment('aviation')
    edges={r['object']:r for r in d['relationships'] if r['verified']}
    assert '2023' in edges['AV-SUP-AIRBUS']['temporal_scope']
    assert edges['AV-SUP-STARLINK']['predicate']=='announced_planned_connectivity'
    assert '2027' in edges['AV-SUP-STARLINK']['temporal_scope']
    assert not any('incumbent'==r['predicate'] for r in d['relationships'])


def test_industry_home_navigation_reaches_easyjet_and_existing_banking(web):
    status,home=web('/')
    assert status==200 and '/industries' in home and '/industries/aviation' in home
    status,html=web('/flora/industries')
    assert status==200 and ROOT in html and model.ROOT in html
    for path,text in [(ROOT,'Aviation.'),(ROOT+'/easyjet','easyJet.'),(model.ROOT,'Banking.'),(model.ROOT+'/lloyds','Lloyds.')]:
        status,html=web(path);assert status==200 and text in html


def test_lenses_svg_keyboard_and_mobile_navigation_open_knowledge_nodes(web):
    for lens in model.LENSES:
        status,html=web(ROOT+'?lens='+lens)
        assert status==200
        assert 'Analyst interpretation' in html or 'conceptual' in html
        for u in Links(html).urls:
            assert public_request_target(u)
    status,html=web(ROOT+'?lens=value-chain')
    assert status==200 and "data-diagram-type='value-chain'" in html
    assert '<svg' in html and "role='group'" in html
    for row in model.load_assessment('aviation')['frameworks']:
        if row['lens']=='value-chain':
            assert web(ROOT+'/nodes/'+row['id'])[0]==200
    # The operating diagram renders the Banking data contract unchanged too.
    assert 'VC-' in sector_views.operating_model(model.load_assessment())


def test_all_generated_local_drilldowns_resolve_and_unknown_resources_stay_closed(web):
    d=model.load_assessment('aviation');paths=[ROOT,ROOT+'/easyjet',ROOT+'/opportunities',ROOT+'/sources',ROOT+'/gaps']
    paths += [ROOT+'/'+category+'/'+r['id'] for key,category in [('claims','evidence'),('candidates','candidates'),('frameworks','nodes'),('capabilities','nodes'),('suppliers','nodes'),('programmes','nodes')] for r in d[key]]
    seen=set(paths)
    for path in paths:
        status,body=web(path);assert status==200,path
        for url in Links(body).urls:
            if urlsplit(url).path not in seen:
                assert web(urlsplit(url).path)[0]==200,url
                seen.add(urlsplit(url).path)
    for target in [ROOT+'/evidence/private',ROOT+'/../banking/research',ROOT+'/easyjet?workspace=foreign',ROOT+'?lens=pestle&lens=porter',ROOT+'/sources/anything']:
        assert not public_request_target(target)
    assert not public_read_path(ROOT+'/candidates/RCO-LBG-001')


def test_evidence_views_show_period_scope_locator_and_original_hash_limit(web):
    for c in model.load_assessment('aviation')['claims']:
        status,html=web(ROOT+'/evidence/'+c['id'])
        assert status==200 and c['quote_locator'] in html
        assert 'Original file SHA256: Unavailable' in html and 'candidate_intelligence' in html
    assert 'Quarter ended 30 June 2026' in web(ROOT+'/evidence/AV-Q3')[1]
    assert 'not FY2026 actual profit' in web(ROOT+'/evidence/AV-Q3')[1]


def test_public_reading_and_candidate_capture_do_not_qualify_or_mutate_bank_records(aviation_actor):
    h=aviation_actor[3]
    old=sales.create_opportunity('lloyds','RCO-LBG-002',headers=h)
    before=sales.get_opportunity(old['id'],headers=h)
    d=model.load_assessment('aviation')
    sector_views.enterprise(d,h);sector_views.opportunities(d,h);sector_views.detail(d,'candidates','RCO-EJ-001',h)
    assert len(sales.list_opportunities(headers=h))==1
    record=sales.create_opportunity('easyjet','RCO-EJ-001',headers=h)
    assert record['enterprise_id']=='AV-ENT-001' and record['industry']=='Aviation'
    assert record['stage']=='Discovered' and record['qualification']=={} and not record['evidence_reviewed']
    assert record['provenance']['origin_url']==ROOT+'/candidates/RCO-EJ-001'
    assert sales.get_opportunity(old['id'],headers=h)==before
    assert sales.create_opportunity('easyjet','RCO-EJ-001',headers=h)['id']==record['id']


def test_easyjet_capture_needs_its_own_enterprise_access_and_origin_lineage(actor):
    with pytest.raises(PermissionError):sales.create_opportunity('easyjet','RCO-EJ-001',headers=actor[3])
    assert sales.list_opportunities(headers=actor[3])==[]
    with actor[0].transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?',(canonical(['AV-ENT-001']),))
    with pytest.raises(sales.SalesValidationError):sales.create_opportunity('easyjet','RCO-LBG-001',headers=actor[3])
    with pytest.raises(sales.SalesValidationError):sales.create_opportunity('easyjet','RCO-EJ-001',{'workspace_id':'other'},headers=actor[3])
    with pytest.raises(PermissionError):sales.create_opportunity('easyjet','RCO-EJ-001',headers={'X-Flora-User':'owner'})
    assert sales.list_opportunities(headers=actor[3])==[]


def test_easyjet_http_capture_explicit_qualification_and_return_to_origin(aviation_actor,sales_web):
    request=sales_web
    status,body,location=request('/flora/sales/capture',{'enterprise':'easyjet','origin':'RCO-EJ-001'})
    assert status==303
    path=location.split('#')[0];record=sales.get_opportunity(path.rsplit('/',1)[1],headers=aviation_actor[3])
    status,body,_=request(path)
    assert status==200 and ROOT+'/opportunities' in body and '/enterprises/easyjet' in body
    assert request(path+'/save',{'version':record['version'],'stage':'Qualified','confirm':'yes'})[0]==422
    fields={'version':record['version'],'stage':'Qualified','confirm':'yes','evidence_reviewed':'yes'}
    for key,value in complete().items():fields['q_'+key]=value['note'];fields['s_'+key]=value['source']
    assert request(path+'/save',fields)[0]==303
    status,body,_=request('/flora/sales/pipeline?stage=Qualified&view=board')
    assert status==200 and 'easyJet' in body and 'Qualified sales opportunity' in body
