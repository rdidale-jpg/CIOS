"""Read-only bridge contract tests for issue #560-style integration pilot."""
from copy import deepcopy
from html import unescape
from cios.applications.flora.research_intelligence import model, unified_views
from cios.applications.flora.research_intelligence.commercial_intelligence import commercial_projection
from cios.applications.flora.research_intelligence.enterprise_opportunity import (
    enterprise_overlay, pursuit_preview, MODULES,
)
from tests.test_flora_commercial_visual_v3 import store_hash


def test_overlay_only_uses_canonical_capability_links_and_retains_unknown_business_owner():
    data=model.load_assessment(); before=deepcopy(data)
    projection=commercial_projection(data,as_of='2026-11-11'); previous=deepcopy(projection)
    html=unescape(enterprise_overlay(data,projection))
    assert 'Enterprise capability landscape' in html
    assert 'Business owner: Unknown' in html
    assert 'procurement' in html.lower()
    for row in projection['candidates']:
        if any(cid in {cap['id'] for cap in data['capabilities']} for cid in row.get('capability_ids',[])):
            assert row['url'] in html
    assert data==before and projection==previous
    assert 'data-eo-choice' in html and 'aria-pressed' in html


def test_priority_cockpit_is_read_only_with_eight_modules_and_unknowns():
    data=model.load_assessment(); rows=commercial_projection(data,as_of='2026-11-11')['candidates']
    assert len(MODULES)==8
    assert len({m[0] for m in MODULES})==8
    for cid in ('RCO-LBG-002','RCO-LBG-001','RCO-LBG-009'):
        row=next(r for r in rows if r['id']==cid)
        html=unescape(pursuit_preview(row))
        assert 'Business ownership' in html and 'Stakeholder network' in html
        assert 'Hot buttons' in html and 'Competitors & alternatives' in html
        assert 'Business owner' in html and 'Unknown' in html
        assert '#commercial-capture' in html
        assert row['commercial']['next_commercial_action'] in html


def test_public_rendering_does_not_modify_pipeline_or_canonical_record():
    baseline=store_hash()
    page=unified_views.enterprise_page('lloyds','opportunities')
    assert 'Enterprise opportunity overlay' in page
    assert 'Business owner: Unknown' in page
    assert '/flora/banking/research/candidates/' in page
    assert store_hash()==baseline


def test_aviation_route_remains_existing_visual_and_no_pursuit_overlay():
    page=unified_views.enterprise_page('easyjet','opportunities')
    assert 'Enterprise opportunity overlay' not in page


def test_html_escapes_untrusted_capability_labels():
    data=model.load_assessment(); data['capabilities'][0]['title']='<script>alert(1)</script>'
    html=enterprise_overlay(data,commercial_projection(model.load_assessment(),as_of='2026-11-11'))
    assert '<script>alert(1)</script>' not in html


def test_default_lloyds_operating_model_preserves_illustration_and_adds_context_overlay():
    html=unified_views.enterprise_page('lloyds','operating-model')
    assert 'Enterprise capability landscape' in html
    assert 'Research capability · not organisation ownership' in html
    assert 'How the business works' in html


def test_priority_hypotheses_put_visual_story_and_cockpit_before_one_full_research_choice():
    from cios.applications.flora.research_intelligence.commercial_views import candidate_overview
    from cios.applications.flora.research_intelligence.enterprise_opportunity import opportunity_story
    data=model.load_assessment();projection=commercial_projection(data,as_of='2026-11-11')
    for cid in ('RCO-LBG-002','RCO-LBG-001','RCO-LBG-009'):
        row=next(r for r in projection['candidates'] if r['id']==cid)
        html=candidate_overview(data,row,projection)
        assert 'Understand where this opportunity could sit' in html
        assert 'Full research & evidence' in html
        assert html.index('Understand where this opportunity could sit') < html.index('Opportunity development / read-only preview') < html.index('Full research & evidence')
        assert html.count("id='full-research-evidence'")==1
        assert '#commercial-capture' in html
        assert 'Business owner, addressable spend, budget, demand and procurement: Unknown' in html
        assert 'Executive hypothesis summary' in html
        assert 'Counterevidence, contradictions' in html


def test_unmapped_hypothesis_stays_discoverable_without_fake_capability():
    data=model.load_assessment(); projection=commercial_projection(data,as_of='2026-11-11')
    from copy import deepcopy
    p=deepcopy(projection)
    p['candidates'][0]['capability_ids']=['MISSING-SYNTHETIC-CAPABILITY']
    html=unescape(enterprise_overlay(data,p))
    assert 'Capability not yet mapped' in html
    assert p['candidates'][0]['url'] in html
    assert 'Business owner: Unknown' in html
    assert 'data-eo-choice' in html


def test_programme_only_association_is_visible_but_not_a_claim_of_ownership():
    data=model.load_assessment(); projection=commercial_projection(data,as_of='2026-11-11')
    from copy import deepcopy
    p=deepcopy(projection)
    assert data['programmes'], 'Fixture must include programme records'
    target=p['candidates'][0]
    target['capability_ids']=[]
    target['programme_ids']=[data['programmes'][0]['id']]
    html=unescape(enterprise_overlay(data,p))
    assert 'Programme signal' in html
    assert data['programmes'][0]['title'] in html
    assert target['url'] in html
    assert 'Business owner: Unknown' in html
    assert 'not organisation ownership' in html


import pytest
from tests.test_flora_sales_pipeline import actor, web
from tests.test_flora_security_repair_01b import authority
import re


@pytest.mark.parametrize('cid',['RCO-LBG-002','RCO-LBG-001','RCO-LBG-009'])
def test_priority_route_has_one_principal_dossier_and_visible_controlled_capture(web,cid):
    status,html,_=web('/flora/banking/research/candidates/'+cid,authenticated=False)
    assert status==200
    assert "id='full-research-evidence'" in html
    assert "class='cv-full-research' id='full-research-evidence' open" not in html
    assert html.index("id='full-research-evidence'") < html.index("class='cv-legacy'") < html.index("id='commercial-capture'")
    assert html.count("class='eo-story-node'")==4
    assert html.count("class='eo-module'")==8
    controls=re.findall("aria-controls='(eo-(?:module|story)-[^']+)'",html)
    assert len(controls)==len(set(controls))==12
    assert "data-depth-print='executive'" in html
    financials=re.search("id='eo-module-financials'>(.*?)</article>",html,re.S).group(1)
    owner=re.search("id='eo-module-owner'>(.*?)</article>",html,re.S).group(1)
    assert 'Unknown' in financials and 'unverified' in owner
    capture=html.split("id='commercial-capture'",1)[1].split('</section>',1)[0]
    assert '<form' not in capture


def test_overlay_candidate_inspectors_preserve_all_identities_and_separate_ratings():
    data=model.load_assessment();p=commercial_projection(data,as_of='2026-11-11')
    html=enterprise_overlay(data,p)
    for row in p['candidates']:
        inspector=re.search("id='eo-candidate-"+row['id']+"'>(.*?)</article>",html,re.S).group(1)
        assert row['url'] in inspector
        assert inspector.count('<dt>')==len(row['dimensions'])
        assert row['commercial']['next_commercial_action'] in unescape(inspector)
    assert 'counts overlap' in unescape(html)
    # No inferred organisational ownership or synthetic relation is stored.
    assert 'not organisation ownership' in unescape(html)


def test_missing_context_does_not_gain_a_source_claim_or_qualification():
    data=model.load_assessment();p=commercial_projection(data,as_of='2026-11-11')
    row=p['candidates'][0];row['context_supported']=False
    for proof in row['support']:proof['supported']=False
    html=unescape(enterprise_overlay(data,p))
    node=re.search("id='eo-candidate-"+row['id']+"'>(.*?)</article>",html,re.S).group(1)
    assert 'Current source support missing' in node
    assert 'Inspect exact passage' not in node
    assert 'unverified' in node


@pytest.mark.parametrize('cid',['RCO-LBG-002','RCO-LBG-001','RCO-LBG-009'])
def test_inspection_preserves_existing_private_capture_and_immutable_provenance(web,actor,cid):
    from cios.applications.flora import sales_pipeline as sales
    record=sales.create_opportunity('lloyds',cid,headers=actor[3])
    before=store_hash();snapshot=deepcopy(record)
    for path in ['/enterprises/lloyds','/enterprises/lloyds?lens=opportunities','/flora/banking/research/candidates/'+cid]:
        assert web(path)[0]==200
    assert store_hash()==before
    assert sales.get_opportunity(record['id'],headers=actor[3])==snapshot
    assert sales.create_opportunity('lloyds',cid,headers=actor[3])==snapshot
    with pytest.raises(sales.SalesValidationError):
        sales.update_opportunity(record['id'],record['version'],{'stage':'Qualified','confirm':'yes'},headers=actor[3])
    assert store_hash()==before
