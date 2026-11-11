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
        assert html.count('id=\\'full-research-evidence\\'')==1
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
