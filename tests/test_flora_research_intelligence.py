"""Research lineage, framework navigation and unqualified commercial capture."""
from copy import deepcopy
from datetime import date
import hashlib
from html import unescape
from html.parser import HTMLParser
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import threading
from urllib.parse import urlsplit, urlencode

import pytest

from cios.applications.flora.research_intelligence import model, views
from cios.applications.flora.public_routes import public_request_target


class Links(HTMLParser):
    def __init__(self,html):
        super().__init__();self.urls=[];self.ids=set();self.feed(html)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'href' in a:self.urls.append(a['href'])
        if 'id' in a:self.ids.add(a['id'])


@pytest.fixture
def web(tmp_path,monkeypatch):
    from cios.applications.flora.web.app import FloraWebHandler
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    def get(path):
        conn=HTTPConnection('127.0.0.1',server.server_port,timeout=30)
        try:
            conn.request('GET',path);r=conn.getresponse();return r.status,r.read().decode()
        finally:conn.close()
    yield get
    server.shutdown();server.server_close();worker.join(2)


def test_existing_twin_ids_and_source_contracts_are_reused():
    data=model.load_assessment()
    assert data['industry_twin_id']=='BK-IND-002' and data['enterprise_twin_id']=='BK-ENT-001'
    for item in data['claims']:
        segment=model.claim_segment(data,item)
        claim=model.candidate_claim(data,item)
        evidence=model.evidence_item(data,item)
        assert isinstance(segment,model.SourceSegment) and isinstance(claim,model.CandidateClaim)
        assert isinstance(evidence,model.EvidencePackageItem)
        assert segment.content_hash==hashlib.sha256(segment.content.encode()).hexdigest()
        assert '#L' in segment.source_location and claim.source_segment_id==segment.segment_id
        assert evidence.truth_status==('source_supported_public_claim' if item['verification']=='source_supported' else 'repository_reported_not_primary_verified')
        assert claim.authority=='candidate_intelligence'
        assert ('Source-supported' if item['verification']=='source_supported' else 'Provisional') in claim.confidence


def test_all_six_pestle_five_forces_and_value_activities_are_explicit():
    data=model.load_assessment()
    counts={lens:len([r for r in data['frameworks'] if r['lens']==lens]) for lens in model.LENSES}
    assert counts=={'pestle':6,'porter':5,'value-chain':8}
    environmental=next(r for r in data['frameworks'] if r['id']=='PESTLE-ENV')
    assert environmental['claim_ids']==[] and 'G-CLIMATE' in environmental['gap_ids']
    assert len(data['programmes'])==5 and all(p['funding']=='Unknown' and p['procurement']=='Unknown' for p in data['programmes'])


def test_repository_citations_cannot_be_upgraded_by_status_or_hash_alone():
    data=model.load_assessment()
    changed=deepcopy(data);changed['sources'][0]['verification']='primary_retrieved'
    with pytest.raises(ValueError):model.validate(changed)
    changed=deepcopy(data);changed['claims'][0]['verification']='source_supported'
    with pytest.raises(ValueError):model.validate(changed)
    changed=deepcopy(data);changed['claims'][0]['repository_quote']='A made-up factual claim'
    with pytest.raises(ValueError):model.validate(changed)


def test_missing_dates_staleness_and_future_assessment_are_visible():
    data=model.load_assessment();state=model.freshness(data,date(2026,11,9))
    assert state['primary_verified']==10 and state['upstream_age_days']==115
    assert all(s['publication_date'] is None and s['retrieved_at'] is None for s in data['sources'] if s['verification']=='citation_only')
    assert model.ranked_candidates(data,date(2026,8,1))==[]
    html=views.sources_page()
    assert 'Publication date:</strong> Unknown' in html and 'Not retrieved' in html


def test_no_fabricated_budget_dates_or_customer_demand_in_ranked_candidates():
    rows=model.ranked_candidates()
    assert len(rows)==9 and [r['rank'] for r in rows]==list(range(1,10))
    assert all(r['estimated_value'] is None and r['procurement_date'] is None for r in rows)
    assert all(r['rank_basis']['primary_supported_claims']>0 for r in rows)
    assert all(r['readiness']=='Research candidate; customer qualification outstanding' for r in rows)
    assert {r['family'] for r in rows}=={'ai-enablement','modernisation','channel-outcomes','customer-economics','payments-integration'}
    assert not any('fraud' in r['title'].lower() or 'BPO' in r['title'] for r in rows)
    assert next(r for r in rows if 'Curve' in r['title'])['review']['change']=='added'


def test_ranking_changes_and_overlap_are_traceable():
    html=views.opportunities_page()
    for identifier in ['COH-LBG-001','COH-LBG-002','COH-LBG-003']:
        assert identifier in html
    assert 'BPO/outsourcing demand is not established' in html
    assert 'may compete for the same scope' in html
    assert 'primary-supported claim count: 22' in html
    for row in model.ranked_candidates():
        assert row['claim_ids'] and row['driver_ids'] and row['capability_ids'] and row['gap_ids']
        assert row['ranking_change']


def test_supplier_edges_distinguish_reported_relationship_and_unknown_contract():
    data=model.load_assessment();relations={r['id']:r for r in data['relationships']}
    assert relations['REL-LBG-GCP']['assertion_kind']=='repository_reported_relationship'
    assert relations['REL-LBG-AWS']['assertion_kind']=='unknown'
    assert [r['id'] for r in data['relationships'] if r['verified']]==['REV-ENVOY-GOOGLE']
    changed=deepcopy(data);changed['relationships'][0]['verified']=True
    with pytest.raises(ValueError):model.validate(changed)
    assert 'enterprise contract unknown' in views.node_page('SUP-AWS')


def test_graph_rejects_missing_relationships_duplicate_ids_and_false_lineage():
    data=model.load_assessment()
    for field in ['subject','object']:
        bad=deepcopy(data);bad['relationships'][0][field]='made-up-node'
        with pytest.raises(ValueError):model.validate(bad)
    bad=deepcopy(data);bad['sources'][0]['id']=bad['claims'][0]['id']
    with pytest.raises(ValueError):model.validate(bad)
    bad=deepcopy(data);bad['claims'][0]['source_ids']=['unrecorded-source']
    with pytest.raises(ValueError):model.validate(bad)


def test_research_revision_preserves_established_facts_and_history():
    previous=model.load_assessment();proposed=deepcopy(previous)
    proposed['claims'][0]['statement']='A different amount, overwriting the established fact'
    with pytest.raises(ValueError):model.compare_revision(previous,proposed)
    proposed=deepcopy(previous);old=proposed['claims'].pop(0)
    new=deepcopy(old);new.update(id='LBG-DEPOSITS-CORRECTION',statement='Explicit corrected-period candidate',supersedes=old['id'])
    proposed['claims'].append(new)
    result=model.compare_revision(previous,proposed)
    assert result['retained_history']==previous and not result['automatic_acceptance'] and not result['canonical_mutation']
    assert old['id'] in result['not_in_proposed']
    new['reporting_period']='Different period must not erase the earlier fact'
    with pytest.raises(ValueError):model.compare_revision(previous,proposed)


def test_corroboration_does_not_rewrite_existing_factual_statement():
    old=model.load_assessment();new=deepcopy(old)
    new['claims'][0]['verification']='source_supported'
    result=model.compare_revision(old,new)
    assert result['corroborated']==[old['claims'][0]['id']]
    assert result['retained_history']['claims'][0]['verification']=='repository_reported'
    assert not result['automatic_acceptance']


def test_primary_supported_claim_needs_matching_content_snapshot(tmp_path,monkeypatch):
    # Explicitly synthetic snapshot proof test, not a real publisher retrieval.
    original=model.REPO
    data=json.loads((original/'enterprise-knowledge/banking/research-model/history/2026-11-09-provisional.json').read_text())
    for path in data['assets'].values():
        target=tmp_path/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((original/path).read_bytes())
    source=data['sources'][0]
    text='SYNTHETIC TEST ONLY: primary disclosure excerpt for validator behaviour.'
    relative='enterprise-knowledge/banking/research-model/source-snapshots/synthetic.txt'
    target=tmp_path/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
    source.update(verification='primary_retrieved',retrieved_at='2026-11-09T10:00:00+00:00',retrieval_url=source['url'],
                  primary_content_sha256=hashlib.sha256(text.encode()).hexdigest(),text_sha256=hashlib.sha256(text.encode()).hexdigest(),text_path=relative,raw_path=relative)
    item=data['claims'][0];item['verification']='source_supported';item['primary_quotes']={source['id']:text}
    monkeypatch.setattr(model,'REPO',tmp_path)
    assert model.validate(data) and model.primary_claim_supported(data,item)
    assert model.candidate_claim(data,item).status=='source_supported_candidate'
    item['primary_quotes'][source['id']]='Not present in the retrieved source'
    with pytest.raises(ValueError):model.validate(data)


def test_date_and_entity_scope_are_not_confused():
    data=model.load_assessment();claims={r['id']:r for r in data['claims']}
    assert claims['LBG-AI-TARGET']['kind']=='management_expectation'
    assert 'not achieved' in claims['LBG-AI-TARGET']['metric_unit']
    assert 'not all Group' in claims['LBG-ACCESS']['entity_scope']
    assert all(s['publication_date'] is None for s in data['sources'] if s['verification']=='citation_only')
    bad=deepcopy(data);bad['sources'][0]['publication_date']='2027-01-01'
    with pytest.raises(ValueError):model.validate(bad)


def test_public_research_navigation_reaches_all_lenses_claims_and_candidates(web):
    for path in [model.ROOT,model.ROOT+'?lens=porter',model.ROOT+'?lens=value-chain',model.ROOT+'/lloyds',model.ROOT+'/sources',model.ROOT+'/gaps',model.ROOT+'/opportunities']:
        status,html=web(path);assert status==200,path
        assert 'Primary-source re-verification partially complete' in html
        assert 'name=\'viewport\'' in html
    data=model.load_assessment()
    for item in data['claims']:
        assert web(model.ROOT+'/evidence/'+item['id'])[0]==200
    for item in data['candidates']:
        status,html=web(model.ROOT+'/candidates/'+item['id'])
        assert status==200 and 'Estimated deal value:</strong> Unknown' in html
        assert 'Sign in to develop this opportunity' in html


def test_research_links_and_diagram_nodes_have_destinations():
    data=model.load_assessment()
    for page in [views.industry_page(),views.enterprise_page(),views.opportunities_page(),views.candidate_page('RCO-LBG-001')]:
        for url in Links(page).urls:
            path=urlsplit(url).path
            if path.startswith(model.ROOT):assert public_request_target(url.split('#',1)[0])
    for key in ['frameworks','capabilities','programmes','suppliers']:
        for node in data[key]:assert node['title'] in unescape(views.node_page(node['id']))


def test_public_research_never_reads_private_models_or_pipeline(monkeypatch):
    from cios.applications.flora.memory.repository import EnterpriseModelRepository,EvidenceRepository
    from cios.applications.flora import sales_pipeline
    def deny(*args,**kwargs):raise AssertionError('Public research cannot resolve private records')
    monkeypatch.setattr(EnterpriseModelRepository,'get',deny)
    monkeypatch.setattr(EvidenceRepository,'list',deny)
    monkeypatch.setattr(sales_pipeline,'_load',deny)
    assert views.enterprise_page() and views.candidate_page('RCO-LBG-001')
    for suffix in ['?workspace_id=private','/nodes/../../private','/evidence/private','/candidates/foreign']:
        assert not public_request_target(model.ROOT+suffix)


def test_existing_twin_assets_and_canonical_intelligence_remain_unchanged():
    data=model.load_assessment()
    for path in [*data['assets'].values(),'enterprise-knowledge/banking/canonical/banking-research-canonical-objects.json']:
        baseline=subprocess.check_output(['git','show','3e703ae99ccfdff46aa1675ae0430f86a9cd52e9:'+path],cwd=model.REPO)
        assert (model.REPO/path).read_bytes()==baseline


from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor


def test_research_capture_preserves_lineage_without_qualification_or_auto_writes(actor):
    from cios.applications.flora import sales_pipeline as sales
    assert sales.list_opportunities(headers=actor[3])==[]
    views.candidate_page('RCO-LBG-001',headers=actor[3])
    assert sales.list_opportunities(headers=actor[3])==[]
    record=sales.create_opportunity('lloyds','RCO-LBG-001',headers=actor[3])
    assert record['stage']=='Discovered' and record['qualification']=={} and not record['evidence_reviewed']
    assert record['demonstration'] and record['amount']=='' and record['confidence']=='Unknown'
    assert record['provenance']['kind']=='research_candidate'
    assert record['provenance']['claim_ids']==model.candidate('RCO-LBG-001')['claim_ids']
    assert record['provenance']['assessment_digest']
    assert sales.qualification(record)['percent']==0
    with pytest.raises(sales.SalesValidationError):
        sales.update_opportunity(record['id'],record['version'],{'stage':'Qualified','confirm':'yes'},headers=actor[3])


def test_research_capture_keeps_existing_snapshot_on_reassessment(actor,monkeypatch):
    from cios.applications.flora import sales_pipeline as sales
    first=sales.create_opportunity('lloyds','RCO-LBG-002',headers=actor[3])
    original=model.commercial_capture
    def revised(*args):
        result=original(*args);result['fields']['title']='A later research revision'
        result['provenance']['assessment_digest']='a-new-revision'
        return result
    monkeypatch.setattr(model,'commercial_capture',revised)
    again=sales.create_opportunity('lloyds','RCO-LBG-002',headers=actor[3])
    assert again==first and len(sales.list_opportunities(headers=actor[3]))==1
    for slug,origin in [('barclays','RCO-LBG-001'),('lloyds','RCO-FOREIGN-001')]:
        with pytest.raises(sales.SalesValidationError):sales.create_opportunity(slug,origin,headers=actor[3])
    with pytest.raises(PermissionError):sales.create_opportunity('lloyds','RCO-LBG-001',headers={'X-Flora-User':'synthetic-human'})
