"""Derived visual intelligence: provenance, uncertainty and existing journey contracts."""
from copy import deepcopy
from html.parser import HTMLParser
from html import unescape
import json

import pytest
from cios.applications.flora.research_intelligence import model, understanding as u
from cios.applications.flora.research_intelligence.visual_intelligence_specs import (
    build_intelligence_specs, validate_intelligence_specs, load_profile, FAMILIES, LANES)
from cios.applications.flora.research_intelligence.visual_intelligence import render_intelligence
from cios.applications.flora.research_intelligence.visual_specs import build_visual_specs
from cios.applications.flora.research_intelligence.unified_views import routes_for
from cios.applications.flora.research_intelligence.cycle import digest
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_research_intelligence import web

ASOF='2026-11-10'


def inputs(domain='banking'):
    return model.load_assessment(domain),u.load_review(domain),load_profile(domain)


def build(domain='banking'):
    return build_intelligence_specs(*inputs(domain),as_of=ASOF)


class Elements(HTMLParser):
    def __init__(self,html):
        super().__init__();self.ids=[];self.links=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href',''))


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_pinned_specs_are_reproducible_and_inputs_are_read_only(domain):
    d,r,p=inputs(domain);before=deepcopy((d,r,p));x=build_intelligence_specs(d,r,p,ASOF)
    assert set(x)==set(FAMILIES)
    assert x==build_intelligence_specs(d,r,p,ASOF) and (d,r,p)==before
    assert validate_intelligence_specs(x,d,r,p,ASOF)
    assert len({s['snapshot_digest'] for s in x.values()})==1
    for s in x.values():
        assert s['authority']=='candidate_intelligence' and s['research_assessment_id']==d['assessment_id']
        assert s['industry']['id']==d['industry_twin_id'] and s['enterprise']['id']==d['enterprise_twin_id']
        assert render_intelligence(s)==render_intelligence(s)
    assert len(x['enterprise-story']['nodes'])==9


@pytest.mark.parametrize('domain,slug',[('banking','lloyds'),('aviation','easyjet')])
def test_all_flagship_pages_and_ai_lens_keep_canonical_navigation(web,domain,slug):
    for path,family in [(f'/industries/{domain}','industry-signature'),(f'/industries/{domain}?lens=ai-disruption','industry-signature'),(f'/enterprises/{slug}','enterprise-story'),(f'/enterprises/{slug}?lens=timeline','strategic-timeline')]:
        status,html=web(path);assert status==200,path
        assert f"data-visual-family='{family}'" in html
        assert public_request_target(path)
        assert all(label in html for label in ['Home','Industries','Enterprises','Opportunities','Pipeline'])
        ids=Elements(html).ids;assert len(ids)==len(set(ids))
    assert not public_request_target('/flora/sales/pipeline')
    assert web('/flora/sales/pipeline')[0] in (401,403)
    assert web(f'/enterprises/{slug}?lens=not-registered')[0]==404


@pytest.mark.parametrize('domain,slug',[('banking','lloyds'),('aviation','easyjet')])
def test_every_family_reaches_actual_evidence_and_resolvable_fragment(web,domain,slug):
    for spec in build(domain).values():
        proof=next(e for n in spec['nodes'] for e in n['evidence'] if e['supported'])
        path,_,fragment=proof['url'].partition('#');status,html=web(path)
        assert status==200,proof['url']
        if fragment:assert fragment in Elements(html).ids
        assert proof['passage'] and proof['locator'] and proof['source_ids']
        assert proof['url'] in Elements(render_intelligence(spec)).links


def test_original_six_spec_api_and_explicit_lenses_are_preserved(web):
    for domain in ('banking','aviation'):
        data=model.load_assessment(domain);original=build_visual_specs(data,routes_for(data))
        status,raw=web('/industries/'+domain+'/visual-specs')
        assert status==200 and set(json.loads(raw))==set(original)
        assert set(original)=={'pestle','five-forces','value-chain','operating-model','ecosystem','opportunities'}
        for lens in ('pestle','porter','value-chain'):
            html=web(f'/industries/{domain}?lens={lens}')[1]
            assert 'data-diagram-type=' in html and 'data-visual-family=' not in html


def test_metrics_do_not_mix_enterprise_and_industry_or_forecast_and_actual():
    b=build();a=build('aviation')
    assert all(m['value'] is None for m in b['industry-signature']['metrics'])
    assert [str(m['value']) for m in b['enterprise-story']['metrics']]==['502.8','6.6']
    assert a['industry-signature']['metrics'][0]['state']=='Forecast, not actual'
    assert [str(m['value']) for m in a['enterprise-story']['metrics']]==['78','552']
    assert a['enterprise-story']['metrics'][1]['period']!=b['enterprise-story']['metrics'][1]['period']
    assert 'causal' not in a['enterprise-story']['metrics'][0]
    d,r,p=inputs();p['metrics']['industry'][0].update(claim_refs=['LBG-Q326-DEPOSITS'],measure='typed')
    assert build_intelligence_specs(d,r,p,ASOF)['industry-signature']['metrics'][0]['value'] is None


def test_numeric_data_without_matching_passage_is_not_rendered():
    for unsupported in (987654321,2.8): # A numeric substring is not evidence for another measure.
        d,r,p=inputs();c=next(c for c in d['claims'] if c['id']=='LBG-Q326-DEPOSITS')
        c['metric_value']=unsupported;r['baseline_digest']=digest(d)
        spec=build_intelligence_specs(d,r,p,ASOF)['enterprise-story']
        assert spec['metrics'][0]['value'] is None
        assert spec['metrics'][0]['state']=='Not established'


def test_index_only_or_unreviewed_evidence_cannot_supply_a_metric():
    d,r,p=inputs('aviation');p['metrics']['enterprise'][0].update(claim_refs=['AV-Q3'],measure='quote',pattern=r'GBP(?P<value>[0-9]+)m',unit='GBP million')
    assert build_intelligence_specs(d,r,p,ASOF)['enterprise-story']['metrics'][0]['value'] is None
    r=u.load_review('aviation')
    for cr in r['claim_reviews']:
        for link in cr['links']:link['locator']='Unverified invented locator'
    x=build_intelligence_specs(d,r,p,ASOF)
    assert all(m['value'] is None for m in x['enterprise-story']['metrics'])


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_seven_lanes_preserve_unknown_dates_and_scenario_uncertainty(domain):
    spec=build(domain)['strategic-timeline']
    assert spec['lanes']==list(LANES)
    undated=[n for n in spec['nodes'] if n['temporal_kind'] in ('unknown','scenario')]
    assert len(undated)>=2 and all(n['start_year'] is None and n['end_year'] is None for n in undated)
    assert all(n['date_label']=='Date unknown' for n in undated)
    assert all(n['readiness'] and n['consequence'] for n in spec['nodes'])
    html=render_intelligence(spec)
    assert 'Unscheduled / still Unknown' in html and 'data-vi-filter' in html
    assert 'no verified date' in html
    assert all(lane in unescape(html) for lane in LANES)
    assert all('An announcement/forecast is not a completed' in n['limitations'] for n in spec['nodes'])


def test_timeline_does_not_turn_publication_dates_or_plans_into_go_live():
    bank=build()['strategic-timeline'];av=build('aviation')['strategic-timeline']
    pub=[n for n in bank['nodes']+av['nodes'] if n['date_basis']=='publication']
    assert pub and all(n['precision']=='Publication day (not go-live)' for n in pub)
    assert 'Published 2026-05-01' in render_intelligence(bank)
    assert 'Published 2026-10-05' in render_intelligence(av)
    wifi=next(n for n in av['nodes'] if n['id']=='VI-EJ-WIFI')
    assert wifi['temporal_kind']=='announced commitment'
    assert (wifi['start_year'],wifi['end_year'])==(2027,2028)
    assert 'half' in wifi['date_label'] and 'early' in wifi['date_label']
    regulatory=next(n for n in bank['nodes'] if n['lane']=='Regulation')
    assert regulatory['date_label']=='18 March 2027'
    assert regulatory['applicability']=='Industry context; enterprise applicability unverified'


def test_missing_date_support_does_not_keep_a_profile_authored_date():
    d,r,p=inputs();event=next(e for e in p['events'] if e['date_basis']=='claim-date')
    event['date_needle']='18 March 2099'
    x=build_intelligence_specs(d,r,p,ASOF)['strategic-timeline']
    n=next(n for n in x['nodes'] if n['id']==event['id'])
    assert n['start_year'] is None and n['temporal_kind']=='unknown'
    assert '2099' not in render_intelligence(x)


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_supplier_activity_associations_do_not_claim_incumbency_or_causality(domain):
    x=build(domain)['enterprise-story']
    suppliers=[s for n in x['nodes'] for s in n['supplier_context']]
    assert suppliers
    assert all('unknown' in s['status'] or 'unverified' in s['status'] for s in suppliers)
    assert all(f['state']=='Conceptual activity relationship; not verified enterprise topology' for f in x['conceptual_flows'])
    html=render_intelligence(x)
    assert 'not verified implementation' in html and 'not establish this activity' in html
    assert 'Related commercial hypotheses — separate and unqualified' in html
    assert 'does not establish customer demand' in html


def test_documented_historical_supplier_keeps_period_and_unknown_current_scope():
    spec=build('aviation')['enterprise-story']
    supplier=next(s for n in spec['nodes'] for s in n['supplier_context'] if s['periods'])
    assert any('2023' in p for p in supplier['periods'])
    assert supplier['claim_ids'] and 'current contract unknown' in supplier['status']


def test_contradictions_are_visible_not_erased():
    x=build()['enterprise-story'];challenged=[n for n in x['nodes'] if n['conflict_ids']]
    assert challenged
    assert all(n['state']=='Challenged / scope unresolved' for n in challenged)
    html=render_intelligence(x)
    assert 'Scope unresolved' in html and 'Challenged / scope unresolved' in html
    assert all(c['treatment'] in html for c in x['conflicts'] if any(c['id'] in n['conflict_ids'] for n in challenged))


def test_new_supplier_renders_without_drawing_changes_and_without_verified_relationship():
    d,r,p=inputs();supplier=deepcopy(d['suppliers'][0]);supplier.update(id='TEST-SUPPLIER',title='Synthetic future research supplier')
    d['suppliers'].append(supplier);r['baseline_digest']=digest(d) # Explicitly reviewed synthetic next-snapshot fixture.
    x=build_intelligence_specs(d,r,p,ASOF)['industry-signature']
    n=next(n for n in x['nodes'] if n['id']=='VI-ACTOR-TEST-SUPPLIER')
    assert n['state']=='Unknown' and n['evidence']==[]
    assert 'Synthetic future research supplier' in render_intelligence(x)
    assert x['snapshot_digest']!=build()['industry-signature']['snapshot_digest']


def test_research_review_change_alters_visual_status_without_renderer_edits():
    d,r,p=inputs('aviation');before=build_intelligence_specs(d,r,p,ASOF)
    for cr in r['claim_reviews']:
        for link in cr['links']:link['locator']='Unreviewed replacement'
    after=build_intelligence_specs(d,r,p,ASOF)
    assert before['enterprise-story']['snapshot_digest']!=after['enterprise-story']['snapshot_digest']
    assert before['enterprise-story']['metrics'][0]['value'] is not None
    assert after['enterprise-story']['metrics'][0]['value'] is None


@pytest.mark.parametrize('state',['sparse','dense','missing-evidence','no-dates','competing'])
def test_principal_data_states_remain_inspectable(state):
    d,r,p=inputs()
    if state=='sparse':p['actors']=p['actors'][:1];p['activities']=[];p['activity_flows']=[]
    if state=='dense':p['actors'] += [{**p['actors'][0],'id':'SYNTHETIC-'+str(i),'label':'Additional synthetic participant '+str(i)} for i in range(35)]
    if state=='missing-evidence':
        for row in p['activities']:row['claim_refs']=['MISSING'];row['resource_ids']=[]
    if state=='no-dates':
        for row in p['events']:row['claim_refs']=[]
    if state=='competing':
        p['actors'].append({**p['actors'][0],'id':'SYNTHETIC-CONFLICT','label':'Alternative research perspective','presentation_state':'unknown'})
    x=build_intelligence_specs(d,r,p,ASOF)
    for spec in x.values():
        html=render_intelligence(spec);assert html and len(Elements(html).ids)==len(set(Elements(html).ids))
    if state=='sparse':assert 'No research-linked activities' in render_intelligence(x['enterprise-story'])
    if state=='no-dates':
        assert x['strategic-timeline']['years']==[]
        assert 'no date axis has been fabricated' in render_intelligence(x['strategic-timeline'])
    if state=='missing-evidence':assert all(n['state']=='Unknown' for n in x['enterprise-story']['nodes'])


@pytest.mark.parametrize('field,value',[('start_year',2099),('date_label','Invented 2099')])
def test_spec_validator_rejects_tampered_dates(field,value):
    d,r,p=inputs();x=build_intelligence_specs(d,r,p,ASOF);x['strategic-timeline']['nodes'][0][field]=value
    with pytest.raises(ValueError,match='drift'):validate_intelligence_specs(x,d,r,p,ASOF)


def test_spec_validator_rejects_tampered_metric_and_unsupported_flow():
    d,r,p=inputs();x=build_intelligence_specs(d,r,p,ASOF);x['enterprise-story']['metrics'][0]['value']='Invented'
    with pytest.raises(ValueError):validate_intelligence_specs(x,d,r,p,ASOF)
    p['activity_flows'][0]['target']='FOREIGN'
    with pytest.raises(ValueError,match='flow'):build_intelligence_specs(d,r,p,ASOF)


@pytest.mark.parametrize('domain',['banking','aviation'])
def test_ai_lens_never_asserts_entrant_names_displacement_or_predicted_dates(domain):
    x=build(domain)['industry-signature'];html=render_intelligence(x,'ai-disruption')
    assert len(x['scenarios'])==2 and all(n['state']=='Scenario' for n in x['scenarios'])
    assert 'Scenario — no displacement prediction' in html
    assert 'Structural defences' in html and 'Named AI-native entrants' in x['participant_limitation']
    assert all('start_year' not in n for n in x['scenarios'])


def test_accessible_text_navigation_escaping_and_no_write_script():
    d,r,p=inputs();p['actors'][0]['label']='<script>unsafe()</script>'
    x=build_intelligence_specs(d,r,p,ASOF)['industry-signature'];html=render_intelligence(x)
    assert '<script>unsafe()' not in html and '&lt;script&gt;' in html
    assert "aria-label='Equivalent text navigation'" in html
    assert 'prefers-reduced-motion:reduce' in html and ':focus-visible' in html
    assert 'aria-live' in html and 'innerHTML' not in html and 'fetch(' not in html
    assert 'tabindex=' in html and 'data-vi-pick' in html
    p['actors'][0]['label']='A very long synthetic research participant name needing bounded labels'
    html=render_intelligence(build_intelligence_specs(d,r,p,ASOF)['industry-signature'])
    assert p['actors'][0]['label']+' — inspect purpose and evidence' in html
    assert '<title>'+p['actors'][0]['label'] in html and '…' in html


def test_invalid_profile_or_future_snapshot_is_rejected():
    d,r,p=inputs();p['domain']='aviation'
    with pytest.raises(ValueError):build_intelligence_specs(d,r,p,ASOF)
    with pytest.raises(ValueError):build_intelligence_specs(*inputs(),as_of='2099-01-01')
    d,r,p=inputs();p['actors'].append(deepcopy(p['actors'][0]))
    with pytest.raises(ValueError,match='Duplicate'):build_intelligence_specs(d,r,p,ASOF)
