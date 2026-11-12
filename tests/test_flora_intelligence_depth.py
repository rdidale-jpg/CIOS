"""Issue #556: appended candidate provenance, decision views and authority boundary."""
from copy import deepcopy
import json
import pytest
from cios.applications.flora.research_intelligence import model,understanding as u,unified_views as views
from cios.applications.flora.research_intelligence import intelligence_depth as depth
from cios.applications.flora.research_intelligence.commercial_intelligence import commercial_projection
from tests.test_flora_sales_pipeline import actor,web
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_commercial_visual_v3 import store_hash


def test_current_candidate_review_is_reproducible_and_does_not_accept_or_mutate():
    d=model.load_assessment();r=u.load_review('banking');before=deepcopy((d,r));a=depth.assessment(d)
    assert a==depth.assessment(d) and (d,r)==before
    assert not a['automatic_acceptance'] and not a['pipeline_mutation']
    assert len([c for c in a['claims'] if c['id'].startswith('RC-DEPTH-')])==4


@pytest.mark.parametrize('key',['AI','LEGACY','WALLET','CURVE'])
def test_new_primary_passages_retain_exact_scope_dates_locator_and_unaccepted_observation(key):
    r=u.load_review('banking');a=depth.assessment(model.load_assessment());sid='DEPTH-LBG-'+key
    source=next(s for s in r['sources'] if s['id']==sid);claim=next(c for c in a['claims'] if c['id']=='RC-'+sid)
    assert claim['direct_support_reviewed'] and not claim['independent_corroboration']
    assert claim['subject']=='BK-ENT-001' and claim['links'][0]['passage_present']
    assert source['retrieved_at'].startswith('2026-11-10') and source['retrieval_reference']
    assert source['primary_content_sha256'] is None and source['content_kind']=='reviewed_web_excerpt'
    assert source['excerpts'][0]['quote'] in model.primary_text(source)
    assert next(o for o in r['observations'] if o['source_id']==sid)['accepted_observation'] is False
    if key in ('LEGACY','WALLET'):assert source['publication_date'] is None


@pytest.mark.parametrize('cid',list(depth.PRIORITIES))
def test_priority_hypotheses_show_specific_question_options_scope_and_unknown_money(cid):
    d=model.load_assessment();row=next(c for c in commercial_projection(d)['candidates'] if c['id']==cid)
    h=depth.hypothesis_depth(d,row)
    assert depth.PRIORITIES[cid][2] in h and 'Budget/value: Unknown' in h and 'External service gap: Unverified' in h
    assert '#commercial-counterevidence' in h and 'candidate' in h.lower()
    assert 'Print executive brief' in h and 'Print full evidence appendix' in h


def test_old_coverage_and_historical_cloud_conflict_are_not_resolved_by_new_retrieval():
    d=model.load_assessment();a=depth.assessment(d)
    assert a['contradictions'] and len(depth.coverage_inventory(d))==14
    assert '50% / 60%' in depth.operating_depth(d)
    assert 'never average' in depth.operating_depth(d)
    assert 'Missing / interpreted' in depth.coverage_body(d)


@pytest.mark.parametrize('lens',['pestle','porter','value-chain'])
def test_frameworks_show_pressure_direction_and_questions_without_arbitrary_scores(lens):
    h=views.industry_page(lens)
    assert 'Pressure → capability → investigation' in h
    assert 'Interpretive direction, not proven causation' in h
    assert 'no numerical attractiveness' in h and 'Scoped examples, sources' in h


def test_single_source_projection_preserves_nine_and_six_candidates():
    for domain,count in [('banking',9),('aviation',6)]:
        d=model.load_assessment(domain);p=commercial_projection(d)
        assert len(p['candidates'])==count
        assert {c['id'] for c in p['candidates']}=={c['id'] for c in d['candidates']}
    register=depth.decision_register(model.load_assessment())
    assert register.count('Research priority')==9 and 'Buyer access, budget and procurement: Unknown' in register


def test_historical_snapshot_does_not_receive_mismatched_current_depth_annotations():
    d=deepcopy(model.load_assessment());d['revision']='synthetic historical revision'
    assert not depth.available(d) and depth.operating_depth(d)==''


def test_executive_print_is_separate_cited_and_restores_original_page():
    h=depth.executive(model.load_assessment())
    assert 'beforeprint' in h and 'afterprint' in h and 'cloneNode(true)' in h and 'copy.className' in h
    assert 'data-depth-print=\'appendix\'' in h and 'body>.depth-print-output' in h
    assert 'innerHTML' not in h and 'fetch(' not in h
    assert 'https://www.lloydsbankinggroup.com/' in h and 'publication Unknown' in h


def test_public_depth_inspection_never_creates_or_reads_private_pipeline(web,actor,monkeypatch):
    from cios.applications.flora import sales_pipeline as sales
    before=store_hash()
    def forbidden(*a,**k):raise AssertionError('Private enumeration from public research')
    monkeypatch.setattr(sales,'list_opportunities',forbidden)
    for path in ['/enterprises/lloyds','/industries/banking?lens=pestle','/opportunities','/flora/banking/research/candidates/RCO-LBG-009']:
        assert web(path,authenticated=False)[0]==200
    assert store_hash()==before


def test_new_text_escapes_untrusted_display_values():
    d=model.load_assessment();row=next(c for c in commercial_projection(d)['candidates'] if c['id']=='RCO-LBG-001')
    row['commercial']['business_problem']='<script>synthetic</script>'
    assert '<script>synthetic' not in depth.hypothesis_depth(d,row)


@pytest.mark.parametrize('cid',list(depth.PRIORITIES))
def test_new_support_is_source_owned_snapshot_bound_and_captured_immutably(actor,cid):
    from cios.applications.flora import sales_pipeline as sales
    row=next(r for r in commercial_projection(model.load_assessment())['candidates'] if r['id']==cid)
    key=depth.PRIORITIES[cid][0];proof='RC-DEPTH-LBG-'+key
    assert proof in {p['id'] for p in row['support']}
    captured=sales.create_opportunity('lloyds',cid,headers=actor[3])
    assert proof in captured['provenance']['commercial_review']['support_claim_ids']
    assert captured['stage']=='Discovered' and not captured['evidence_reviewed']
    assert sales.create_opportunity('lloyds',cid,headers=actor[3])==captured
