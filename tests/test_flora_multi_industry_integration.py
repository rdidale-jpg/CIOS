"""Both sectors share presentation, evidence lineage and the authorised Pipeline."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit
import subprocess
import pytest
from cios.applications.flora.research_intelligence import model,unified_views as views
from cios.applications.flora.public_routes import public_request_target
from cios.applications.flora.security_store import canonical
from tests.test_flora_research_intelligence import web
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor,complete,web as sales_web


class DOM(HTMLParser):
    def __init__(self,html):
        super().__init__();self.ids=[];self.links=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href',''))


def test_both_sectors_and_all_supported_enterprises_share_the_canonical_catalogues(web):
    for path in ['/','/industries','/flora/industries']:
        code,html=web(path);assert code==200
        assert '/industries/banking' in html and '/industries/aviation' in html
    html=web('/enterprises')[1]
    for slug in ['lloyds','easyjet','barclays','natwest','hsbc-uk','santander-uk']:
        assert '/enterprises/'+slug in DOM(html).links
    for domain,slug in [('banking','lloyds'),('aviation','easyjet')]:
        assert '/enterprises/'+slug in DOM(web('/industries/'+domain)[1]).links
        # VEX-1 return links retain stream and selected enterprise in the query.
        assert '/industries/'+domain in [urlsplit(href).path for href in DOM(web('/enterprises/'+slug)[1]).links]


@pytest.mark.parametrize('domain,slug,origin',[('banking','lloyds','RCO-LBG-002'),('aviation','easyjet','RCO-EJ-001')])
def test_complete_sector_to_evidence_to_confirmed_pipeline_journey(domain,slug,origin,actor,sales_web):
    from cios.applications.flora import sales_pipeline as sales
    with actor[0].transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?',(canonical(['BK-ENT-001','AV-ENT-001']),))
    request=sales_web;data=model.load_assessment(domain);routes=views.routes_for(data)
    for path in [routes['industry'],routes['enterprise'],routes['enterprise']+'?lens=opportunities']:
        assert request(path,authenticated=False)[0]==200
    candidate=routes['candidates']+'/'+origin;status,html,_=request(candidate)
    assert status==200 and origin in html
    row=next(r for r in data['candidates'] if r['id']==origin)
    assert request(routes['evidence']+'/'+row['claim_ids'][0],authenticated=False)[0]==200
    assert sales.list_opportunities(headers=actor[3])==[]
    status,_,location=request('/flora/sales/capture',{'enterprise':slug,'origin':origin});assert status==303
    path=location.split('#')[0];record=sales.get_opportunity(path.rsplit('/',1)[1],headers=actor[3])
    assert record['stage']=='Discovered' and record['qualification']=={} and not record['evidence_reviewed']
    assert record['provenance']['origin_url']==candidate and record['enterprise_id']==data['enterprise_twin_id']
    assert routes['enterprise'] in request(path)[1]
    assert request(path+'/save',{'version':record['version'],'stage':'Qualified','confirm':'yes'})[0]==422
    assert sales.get_opportunity(record['id'],headers=actor[3])==record
    fields={'version':record['version'],'stage':'Qualified','confirm':'yes','evidence_reviewed':'yes'}
    for key,value in complete().items():fields['q_'+key]=value['note'];fields['s_'+key]=value['source']
    assert request(path+'/save',fields)[0]==303
    assert data['enterprise_name'] in request('/flora/sales/pipeline?stage=Qualified')[1]


def test_every_sector_uses_all_six_shared_templates_and_retains_score_dimensions(web):
    for domain,slug in [('banking','lloyds'),('aviation','easyjet')]:
        data=model.load_assessment(domain);specs=views.specs(data)
        assert set(specs)=={'pestle','five-forces','value-chain','operating-model','ecosystem','opportunities'}
        for lens,kind in [('pestle','pestle'),('porter','five-forces'),('value-chain','value-chain')]:
            assert "data-diagram-type='"+kind+"'" in web('/industries/'+domain+'?lens='+lens)[1]
        for kind in ['operating-model','ecosystem','opportunities']:
            assert "data-diagram-type='"+kind+"'" in web('/enterprises/'+slug+'?lens='+kind)[1]
        status,payload=web('/industries/'+domain+'/visual-specs');assert status==200 and json.loads(payload)==specs
        assert len(specs['opportunities']['nodes'])==(9 if domain=='banking' else 6)
        assert all(len(n['ratings'])==(3 if domain=='banking' else 4) for n in specs['opportunities']['nodes'])
    html=web('/opportunities')[1];dom=DOM(html)
    assert len(dom.ids)==len(set(dom.ids))
    assert 'opportunities-banking' in dom.ids and 'opportunities-aviation' in dom.ids
    assert 'Seller fit' in html and 'no cross-industry aggregate score' in html


def test_original_research_and_all_six_easyjet_hypotheses_are_byte_preserved():
    for ref,domain in [('a8515b91ea4e177bdb9700e05813c1d448ba189f','banking'),('cfa9016e6b76e9b30b7e889d16501ccfa06881ef','aviation')]:
        path='enterprise-knowledge/'+domain+'/research-model/Assessment-Overlay.json'
        assert subprocess.check_output(['git','show',ref+':'+path],cwd=model.REPO)==(model.REPO/path).read_bytes()
    data=model.load_assessment('aviation')
    assert {r['id'] for r in data['candidates']}=={'RCO-EJ-'+str(i).zfill(3) for i in range(1,7)}
    assert all(c['qualification_state']=='Unqualified research hypothesis' and c['indicative_contract_value'] is None and c['procurement_date'] is None for c in data['commercial_assessment']['assessments'])


def test_partial_sources_and_future_supplier_plans_do_not_become_current_verified_contracts(web):
    html=web('/enterprises/easyjet')[1]
    assert '2 official search-index excerpts only' in html and 'original documents not directly verified' in html
    assert 'source citations still require primary verification' in html
    ecosystem=web('/enterprises/easyjet?lens=ecosystem')[1]
    assert 'Announced plan / not yet live' in ecosystem
    assert 'no current incumbency is implied' in ecosystem
    from cios.applications.flora.research_intelligence.visual_specs import claim_state
    data=model.load_assessment('aviation');sources={s['id']:s for s in data['sources']}
    for identifier in ['AV-Q3','AV-HOLIDAYS']:
        claim=next(c for c in data['claims'] if c['id']==identifier)
        assert 'search-index' in sources[claim['source_ids'][0]]['retrieval_extent']
        assert sources[claim['source_ids'][0]]['primary_content_sha256'] is None
        assert claim_state(data,claim)=='official search-index excerpt; original unverified'


def test_finite_public_routes_do_not_grant_enterprise_write_access(actor):
    from cios.applications.flora import sales_pipeline as sales
    for domain in ['banking','aviation']:assert public_request_target('/industries/'+domain)
    for target in ['/industries/private','/enterprises/AV-ENT-001','/industries/aviation?workspace=other','/flora/aviation/research/candidates/RCO-LBG-001','/enterprises/easyjet/canvas','/flora/sales/pipeline']:
        assert not public_request_target(target)
    with pytest.raises(PermissionError):sales.create_opportunity('easyjet','RCO-EJ-001',headers=actor[3])
    assert sales.list_opportunities(headers=actor[3])==[]


def test_exact_58_to_57_inherited_failure_reconciliation_is_preserved():
    old=json.loads(subprocess.check_output(['git','show','ac2861e855257f3f70322bf4c1568434e565945a:tools/ci/flora-baseline-v1.json'],cwd=model.REPO))
    new=json.loads((model.REPO/'tools/ci/flora-baseline-v1.json').read_text())
    flatten=lambda d:{id:r for s in d['profiles']['01b']['suites'].values() for id,r in s['cases'].items()}
    a,b=flatten(old),flatten(new);before={id for id,r in a.items() if r['status']=='failed'};after={id for id,r in b.items() if r['status']=='failed'}
    fixed='tests/test_flora_enterprise_canvas.py::test_home_page_does_not_expose_synthetic_canvas_route'
    assert len(before)==58 and len(after)==57 and before-after=={fixed} and not after-before
    proof=json.loads((model.REPO/'docs/flora-runtime/unified-experience/Inherited-UI-Comparison.json').read_text())
    changed={id for id in after if a[id]['signature']!=b[id]['signature']}
    assert changed=={r['test_id'] for r in proof['cases'] if r['candidate']['status']=='failed'}
    for r in proof['cases']:assert b[r['test_id']]==r['candidate']
    assert {id:r for id,r in a.items() if r['status']=='skipped'}=={id:r for id,r in b.items() if r['status']=='skipped'}
