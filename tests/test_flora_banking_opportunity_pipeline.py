from cios.applications.flora.enterprise_intelligence.opportunity_pipeline import generate_banking_opportunity_pipeline, classify
from cios.applications.flora.web.app import _flora_focus_page, _flora_explore_page, _flora_shape_page


def test_opportunity_pipeline_contract_and_safety():
    p = generate_banking_opportunity_pipeline()
    assert p.industry == 'Banking'
    assert 3 <= len(p.opportunities) <= 10
    ids = [o.opportunity_id for o in p.opportunities]
    assert len(ids) == len(set(ids))
    supported_names = {'Nationwide / Virgin Money'}
    for o in p.opportunities:
        assert o.object_type == 'commercial_opportunity'
        assert o.authority == 'derived_runtime'
        assert o.persistence_class == 'transient_runtime'
        assert o.primary_hypothesis_ids
        assert o.supporting_observation_ids
        assert o.lineage['path'] == ['Evidence','Observation','Mechanism','Enterprise Context','Reinvention Hypothesis','Commercial Opportunity','Horizon','Next Action']
        assert o.movement_criteria
        assert o.stronger_actions_prohibited
        assert o.named_executives == []
        assert o.enterprise_name in supported_names | {''}
    assert p.portfolio_summary['horizon_2_count'] >= 1
    assert p.portfolio_summary['horizon_3_count'] >= 1
    assert p.portfolio_summary['not_actionable_count'] >= 1


def test_horizon_classifier_policy_constraints():
    h1 = classify(enterprise_specificity='High', timing='current', programme=True, roles=True, contradictions=False, eligibility='shape workshop', confidence='Medium-High')
    assert h1.horizon == 'horizon_1'
    h2 = classify(enterprise_specificity='Medium', timing='current', programme=False, roles=True, contradictions=False, eligibility='gather evidence', confidence='Medium')
    assert h2.horizon == 'horizon_2'
    h3 = classify(enterprise_specificity='Low', timing='long_term', programme=False, roles=True, contradictions=True, eligibility='monitor', confidence='Low')
    assert h3.horizon == 'horizon_3'
    na = classify(enterprise_specificity='Low', timing='weak', programme=False, roles=False, contradictions=True, eligibility='defer', confidence='Low')
    assert na.horizon == 'not_actionable'


def test_focus_pipeline_renders_cards_detail_filters_and_no_raw_primary_ids():
    html = _flora_focus_page({}, {})
    assert 'Banking Opportunity Pipeline' in html
    for text in ['Horizon 1 — Act now', 'Horizon 2 — Build conviction', 'Horizon 3 — Shape the future', 'Not currently actionable']:
        assert text in html
    for text in ['Why now', 'Executive relevance', 'Confidence', 'Evidence strength', 'Next action', 'Moves when']:
        assert text in html
    filtered = _flora_focus_page({}, {'horizon':['horizon_3']})
    assert 'Shared-access ecosystem participant' in filtered
    enterprise_filtered = _flora_focus_page({}, {'enterprise':['Nationwide']})
    assert 'Nationwide / Virgin Money' in enterprise_filtered
    role_filtered = _flora_focus_page({}, {'executive_role':['Chief Customer Officer']})
    assert 'Chief Customer Officer' in role_filtered
    detail = _flora_focus_page({}, {'opportunity':['BK-OPP-001']})
    for text in ['Opportunity thesis','Unknowns','Contradictions','Horizon rationale','Movement criteria','What should not yet be done','Lineage']:
        assert text in detail


def test_explore_links_to_pipeline_and_shape_preserves_context():
    explore = _flora_explore_page({})
    assert 'View Banking Opportunity Pipeline' in explore
    shape = _flora_shape_page({}, {'opportunity':['BK-OPP-001']})
    assert 'Selected opportunity context preserved' in shape
    assert 'BK-OPP-001' in shape
    assert 'Unsupported proposal action' in shape
