"""Commercial priority is not research rank, a pipeline stage or buyer authority."""
from copy import deepcopy
import json
import subprocess

import pytest

from cios.applications.flora.research_intelligence import model, views
from tests.test_flora_research_intelligence import web
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor


def test_three_dimensions_remain_separate_and_all_nine_are_assessed():
    data=model.load_assessment();rows=model.commercial_candidates(data)
    assert len(rows)==9 and {r['id'] for r in rows}=={c['id'] for c in data['candidates']}
    assert [r['id'] for r in model.commercial_candidates(data,True)]==['RCO-LBG-002','RCO-LBG-001','RCO-LBG-009']
    assert model.ranked_candidates()[0]['id']=='RCO-LBG-001'
    assert rows[0]['id']=='RCO-LBG-002' and rows[0]['rank']==2 and rows[0]['commercial_rank']==1
    for row in rows:
        c=row['commercial']
        assert set(('strategic_relevance','commercial_accessibility','evidence_maturity'))<=c.keys()
        assert c['commercial_accessibility']['score']<=1 and c['evidence_maturity']['score']<=2
        assert c['qualification_state']=='Unqualified research hypothesis'
        assert c['indicative_contract_value'] is None and c['procurement_date'] is None
        assert not c['confirmed_supplier_demand'] and c['verified_buyer_names']==[]
        assert 'Inferred' in c['buyer_status'] and c['next_commercial_action']
        assert c['supplier_position'] and c['route_to_market'] and c['delivery_and_competition']


def test_scores_have_anchors_and_no_combined_win_probability():
    data=model.load_assessment();context=data['commercial_assessment']
    assert 'AI-enabled transformation' in context['seller_profile']
    assert 'No composite score or win probability' in context['ranking_policy']
    for anchors in context['rating_anchors'].values():assert set(anchors)=={'0','1','2','3'}
    assert 'customer' in context['rating_anchors']['commercial_accessibility']['3'].lower()
    changed=deepcopy(data);changed['commercial_assessment']['assessments'][0]['strategic_relevance']['score']=4
    with pytest.raises(ValueError):model.validate(changed)


def test_access_process_evidence_does_not_become_open_demand():
    data=model.load_assessment();claims={c['id']:c for c in data['claims']}
    for ref in data['commercial_assessment']['access_claim_ids']:assert model.primary_claim_supported(data,claims[ref])
    assert 'invitation-only' in claims['LBG-FSQS-ACCESS']['statement']
    assert 'no invitation' in claims['LBG-SOURCING-ACCESS']['statement'].lower()
    for change in [{'indicative_contract_value':100000},{'procurement_date':'2027-01-01'},
                   {'confirmed_supplier_demand':True},{'qualification_state':'Qualified'}]:
        bad=deepcopy(data);bad['commercial_assessment']['assessments'][0].update(change)
        with pytest.raises(ValueError):model.validate(bad)
    bad=deepcopy(data);bad['commercial_assessment']['assessments'][0]['commercial_accessibility']['score']=2
    with pytest.raises(ValueError):model.validate(bad)


def test_existing_twenty_two_primary_claims_and_all_opportunities_are_preserved():
    previous=json.loads(subprocess.check_output(['git','show','97c7de62676d9c103b7e8c8c94a30976188cb5ec:enterprise-knowledge/banking/research-model/Assessment-Overlay.json'],cwd=model.REPO,text=True))
    data=model.load_assessment()
    assert data['claims'][:len(previous['claims'])]==previous['claims']
    assert data['sources'][:len(previous['sources'])]==previous['sources']
    assert data['candidates']==previous['candidates']
    assert len(data['claims'])==len(previous['claims'])+2
    assert len(data['sources'])==len(previous['sources'])+2


def test_only_wider_evidence_informs_industry_capability_feedback():
    data=model.load_assessment();claims={c['id']:c for c in data['claims']}
    edges=[r for r in data['relationships'] if r['id'].startswith('COMM-IND-')]
    assert len(edges)==2
    for row in edges:
        assert row['subject']=='BK-IND-002' and not row['verified']
        assert all(claims[ref]['asset_id']=='BK-IND-002' for ref in row['claim_ids'])
    assert 'outsourcing trend' in next(f for f in data['frameworks'] if f['id']=='PESTLE-L')['commercial_implication']


def test_commercial_evidence_must_resolve_and_cover_every_candidate_once():
    data=model.load_assessment()
    bad=deepcopy(data);bad['commercial_assessment']['assessments'].append(bad['commercial_assessment']['assessments'][0])
    with pytest.raises(ValueError):model.validate(bad)
    bad=deepcopy(data);bad['commercial_assessment']['assessments'][0]['evidence_claim_ids']=['UNSUPPORTED']
    with pytest.raises(ValueError):model.validate(bad)


def test_public_shortlist_and_customer_briefs_are_navigable(web):
    status,html=web(model.ROOT+'/opportunities')
    assert status==200 and 'Commercial opportunity shortlist' in html and 'zero confirmed contract opportunities' in html
    for row in model.commercial_candidates():
        status,body=web(model.ROOT+'/candidates/'+row['id'])
        assert status==200 and 'Potential buyer / decision function' in body
        assert 'Contract value and procurement date' in body and row['commercial']['offer'] in body
    for ref in model.load_assessment()['commercial_assessment']['access_claim_ids']:
        assert web(model.ROOT+'/evidence/'+ref)[0]==200


def test_reading_shortlist_cannot_create_or_qualify_pipeline_records(actor):
    from cios.applications.flora import sales_pipeline as sales
    assert sales.list_opportunities(headers=actor[3])==[]
    views.opportunities_page(headers=actor[3])
    views.candidate_page('RCO-LBG-002',headers=actor[3])
    model.commercial_candidates(shortlisted_only=True)
    assert sales.list_opportunities(headers=actor[3])==[]
    captured=sales.create_opportunity('lloyds','RCO-LBG-002',headers=actor[3])
    assert captured['stage']=='Discovered' and captured['qualification']=={} and not captured['evidence_reviewed']
