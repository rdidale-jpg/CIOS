"""Industry systems remain illustrative, scoped, navigable and reproducible."""
from copy import deepcopy
from html import unescape
import json,subprocess
import pytest
from cios.applications.flora.research_intelligence import model,understanding as u
from cios.applications.flora.research_intelligence.living_map_specs import build_living_map,load_mapping,validate_living_map
from cios.applications.flora.research_intelligence.living_map import render_living_map
from cios.applications.flora.research_intelligence.visual_intelligence_specs import build_intelligence_specs
from tests.test_flora_research_intelligence import web,Links
from cios.applications.flora.public_routes import public_request_target
ASOF='2026-11-10'


def inputs(domain='banking'):
    return model.load_assessment(domain),u.load_review(domain),load_mapping(domain)


def spec(domain='banking'):
    return build_living_map(*inputs(domain),as_of=ASOF)


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_map_is_pinned_repeatable_read_only_and_canonical_ids_retained(domain):
    d,r,m=inputs(domain);before=deepcopy((d,r,m));s=build_living_map(d,r,m,ASOF)
    assert (d,r,m)==before and s==build_living_map(d,r,m,ASOF)
    assert validate_living_map(s,d,r,m,ASOF)
    assert s['industry']['id']==d['industry_twin_id'] and s['enterprise']['id']==d['enterprise_twin_id']
    assert s['authority']=='candidate_intelligence' and len(s['map_nodes'])==9
    assert len({tuple(n['position']) for n in s['map_nodes']})==9
    assert render_living_map(s)==render_living_map(s)


@pytest.mark.parametrize('domain',['banking','aviation'])
@pytest.mark.parametrize('lens',['overview','ai-disruption','regulation'])
def test_each_layer_uses_one_map_and_contextual_inspection_with_original_routes(web,domain,lens):
    status,h=web(f'/industries/{domain}?lens={lens}');assert status==200
    assert h.count("data-living-map='2'")==1
    assert "class='lm-inspector'" in h and '03 / Investigate' in h
    ids=Links(h).ids
    assert all('lm-'+domain+'-'+n['id'] in ids for n in spec(domain)['map_nodes'])
    assert public_request_target(f'/industries/{domain}?lens={lens}')
    assert not public_request_target('/industries/'+domain+'?workspace_id=private')
    assert not public_request_target('/flora/sales/pipeline')
    assert web('/flora/sales/pipeline')[0] in (401,403)
    if lens=='ai-disruption':assert "data-ai='true'" in h
    if lens=='regulation':assert "data-regulation='true'" in h


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_every_major_activity_has_meaningful_scoped_content_and_evidence_link(web,domain):
    s=spec(domain);h=render_living_map(s);links=Links(h)
    for n in s['map_nodes']:
        assert n['purpose'] and n['pressure']
        assert '#lm-'+domain+'-'+n['id'] in links.urls
        assert n['evidence'] and n['capability_links']
        assert all(p['passage'] and p['source_ids'] and p['period'] for p in n['evidence'])
    first=next(p for n in s['map_nodes'] for p in n['evidence'] if p['supported'])
    path,_,fragment=first['url'].partition('#');status,body=web(path)
    assert status==200 and (not fragment or fragment in Links(body).ids)
    assert first['url'] in links.urls


def test_banking_and_aviation_express_different_mechanics():
    b=spec();a=spec('aviation')
    assert {'Money','Risk','Control'}<={f['kind'] for f in b['flows']}
    assert {'Demand','Passengers','Availability'}<={f['kind'] for f in a['flows']}
    assert 'Deposits & funding' in unescape(render_living_map(b))
    assert 'Aircraft & crew' in unescape(render_living_map(a))
    assert 'Maintenance & engineering' in unescape(render_living_map(a))
    assert any(n['illustration']=='wrench' for n in a['map_nodes'])


def test_industry_metrics_keep_definition_scope_and_period_without_false_market_size():
    b=spec();a=spec('aviation');m=b['metrics'][0]
    assert m['value']=='3118' and m['scope_id']=='BK-IND-002'
    assert 'not total assets' in m['scope_note'] and '2026 Q2' in m['period']
    assert a['metrics'][0]['value']=='302' and 'not unique people' in a['metrics'][0]['scope_note']
    assert 'employment' in b['scale_gaps'] and 'shares' in a['scale_gaps']
    assert all(n['size_basis'].startswith('Equal-sized') for n in b['participants'])


def test_enterprise_metric_cannot_become_industry_scale():
    d,r,m=inputs();m['metrics'][0].update(claim_refs=['LBG-Q326-DEPOSITS'],measure='typed')
    s=build_living_map(d,r,m,ASOF);assert s['metrics'][0]['value'] is None
    assert 'Not established' in render_living_map(s)


def test_unreviewed_or_missing_measurement_does_not_become_zero_or_verified():
    d,r,m=inputs();m['metrics'][0]['claim_refs']=['MISSING']
    assert build_living_map(d,r,m,ASOF)['metrics'][0]['value'] is None
    m=load_mapping('banking')
    cr=next(c for c in r['claim_reviews'] if c['claim_id']==r['observations'][-1]['candidate']['claim_id'])
    cr['links'][0]['locator']='Not the official passage'
    s=build_living_map(d,r,m,ASOF);assert s['metrics'][0]['value'] is None
    assert '3118' not in render_living_map(s)


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_flows_and_role_placement_never_prove_contracts_or_causality(domain):
    s=spec(domain)
    assert all(f['state']=='Conceptual industry flow; not verified enterprise topology' for f in s['flows'])
    assert all('not evidence of a contract' in a['association_state'] for a in s['participants'])
    assert all('Reference-company disclosures' in n['limitations'] for n in s['map_nodes'])
    h=render_living_map(s)
    assert 'No verified causal or contractual claim follows' in h


def test_dated_supplier_relationship_is_specific_historical_and_not_current_incumbency(web):
    s=spec('aviation');a=next(a for a in s['participants'] if a['documented_relationships'])
    edge=a['documented_relationships'][0]
    assert edge['state']=='Verified factual relationship' and edge['period']=='November 2023 launch'
    assert not edge['causation_proven'] and 'Current scope' in edge['missing_evidence'][0]
    h=render_living_map(s);assert 'Documented reference-company relationship' in h
    assert 'current contract unknown' in h
    url=s['enterprise']['url']+'/understanding';assert web(url)[0]==200


def test_reviewed_relationship_changes_update_marker_without_drawing_edits():
    d,r,m=inputs('aviation');s=build_living_map(d,r,m,ASOF)
    assert any(a['documented_relationships'] for a in s['participants'])
    for cr in r['claim_reviews']:
        for link in cr['links']:link['locator']='Evidence no longer reviewed'
    after=build_living_map(d,r,m,ASOF)
    assert not any(a['documented_relationships'] for a in after['participants'])
    assert after['snapshot_digest']!=s['snapshot_digest']


def test_conflicts_remain_visible_and_are_not_erased_by_the_industry_model():
    s=spec();n=next(n for n in s['map_nodes'] if n['conflict_ids'])
    assert n['state']=='Challenged / scope unresolved'
    assert 'Challenged / scope unresolved' in render_living_map(s)


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_ai_and_regulation_are_exposure_mappings_with_real_timeline_links_only(web,domain):
    s=spec(domain);h=render_living_map(s,'ai-disruption')
    assert any(n['ai_scenarios'] for n in s['map_nodes'])
    assert 'Analytical scenario — not a proven threat' in h
    assert 'not proven harm' in h
    n=next(n for n in s['map_nodes'] if n['timeline_events']);event=n['timeline_events'][0]
    path=s['timeline_url'];status,html=web(path);assert status==200
    assert 'vi-strategic-timeline-'+domain+'-'+event['id'] in Links(html).ids
    assert all(t['start_year'] is None for t in s['timeline_events'] if t['temporal_kind'] in ('unknown','scenario'))


@pytest.mark.parametrize('defect',['scope','flow','position','duplicate','empty'])
def test_presentation_mapping_cannot_invent_authoritative_topology_or_invalid_state(defect):
    d,r,m=inputs()
    if defect=='scope':m['domain']='aviation'
    if defect=='flow':m['flows'][0]['state']='Verified factual relationship'
    if defect=='position':m['activities'][0]['position']=[700,1400]
    if defect=='duplicate':m['activities'].append(deepcopy(m['activities'][0]))
    if defect=='empty':m['activities']=[]
    with pytest.raises(ValueError):build_living_map(d,r,m,ASOF)


def test_complete_derived_spec_drift_is_rejected():
    d,r,m=inputs();s=build_living_map(d,r,m,ASOF);s['metrics'][0]['value']='Invented'
    with pytest.raises(ValueError,match='drift'):validate_living_map(s,d,r,m,ASOF)


def test_labels_are_escaped_and_accessible_interaction_and_print_are_explicit():
    d,r,m=inputs();m['activities'][0]['label']='<img src=x onerror=unsafe()>'
    h=render_living_map(build_living_map(d,r,m,ASOF))
    assert '<img src=x' not in h and '&lt;img' in h
    assert 'aria-live' in h and ':focus-visible' in h and 'prefers-reduced-motion' in h
    assert 'Equivalent text navigation' in h and 'beforeprint' in h and '@media print' in h
    assert 'innerHTML' not in h and 'fetch(' not in h
    ids=Links(h).ids
    assert all(t.lstrip('#') in ids for t in Links(h).urls if t.startswith('#lm-'))


def test_history_is_append_only_and_existing_enterprise_visual_profiles_unchanged():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    relative='enterprise-knowledge/banking/research-model/Understanding-Review.json'
    old=json.loads(subprocess.check_output(['git','show','650b92c:'+relative],cwd=root));new=json.loads((root/relative).read_text())
    for key in old:
        if key in ('sources','observations','claim_reviews'):assert new[key][:len(old[key])]==old[key]
        else:assert new[key]==old[key]
    assert len(new['sources'])==len(old['sources'])+1
    for domain in ('banking','aviation'):
        p=f'enterprise-knowledge/{domain}/research-model/Visual-Profile.json'
        assert (root/p).read_bytes()==subprocess.check_output(['git','show','650b92c:'+p],cwd=root)
        assert build_intelligence_specs(model.load_assessment(domain))['enterprise-story']['diagram_type']=='enterprise-story'
