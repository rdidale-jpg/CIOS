"""Scoped evidence decisions and immutable handoff design, not compliance tests."""
from copy import deepcopy
import json
from html import unescape
import pytest
from cios.applications.flora.research_intelligence import macro_intelligence as m, macro_trace as t, macro_views as v
from cios.applications.flora.research_intelligence.model import load_assessment, commercial_capture
from tests.test_flora_global_macro import choose
from tests.test_flora_sales_pipeline import authority, actor, web
from tests.test_flora_commercial_visual_v3 import store_hash
from cios.applications.flora import sales_pipeline as sales


def test_new_cut_retains_source_truth_and_reuses_semantic_owner():
    data,combined=t.load_traces()
    assert len(data['sources'])==4 and len(combined['sources'])==11
    assert len(m.semantic_projection(combined).objects)==11
    assert all(not o['accepted_observation'] for o in combined['observations'])
    for source in data['sources']:
        assert source['primary_content_sha256'] is None
        assert len(source['excerpts'][0]['quote'].split())<=25
        assert source['excerpts'][0]['quote'] in m.primary_text(source)
        observation=next(o for o in data['observations'] if o['source_id']==source['id'])
        assert observation['candidate']['scope']==source['reporting_period']


@pytest.mark.parametrize('market,force,category', [('GB','cyber','cyber'),('FR','eu-csrd','sustainability')])
def test_separate_edge_decisions_do_not_collapse_identity_into_demand(market,force,category):
    trace=t.trace_projection(choose(market=market,force=force,category=category))
    edges={e['predicate']:e for e in trace['edges']}
    assert len(edges)==6
    assert edges['ENTITY_IDENTIFICATION']['status']==('verified' if market=='GB' else 'unknown')
    assert edges['INSTRUMENT_STATUS']['status']=='source_supported'
    for predicate in ('FORMAL_APPLICABILITY','CUSTOMER_RESPONSE','SUPPLIER_OPPORTUNITY'):
        assert edges[predicate]['status']=='unknown'
    assert len(trace['alternatives'])>=2 and trace['contradictions']
    assert all(e['country_id']==market and e['assessed_at']=='2026-11-12' for e in edges.values())
    assert all(e['claim_ids'] and e['source_ids'] for name,e in edges.items() if name!='ENTITY_IDENTIFICATION')


@pytest.mark.parametrize('query',['','market=FR','market=GB&force=cyber-bill','market=GB&industry=aviation',
                                 'market=GB&category=sustainability&force=eu-csrd'])
def test_unreviewed_context_does_not_inherit_entity_or_trace(query):
    assert t.trace_projection(m.selection(query)) is None


def test_france_has_national_text_but_no_entity_or_transplanted_candidate():
    tr=t.trace_projection(choose(market='FR',category='sustainability',force='eu-csrd'))
    assert tr['entity']['registry_id'] is None and tr['hypothesis_id'] is None
    assert 'phase' in tr['scope_reason'] and 'exemption' in tr['scope_reason']
    assert 'Industry-only' in tr['consequence']


def test_uk_investigates_ongoing_resilience_not_new_deadline_or_bank_deficiency():
    tr=t.trace_projection(choose(market='GB'))
    assert tr['entity']['legal_entity_id']=='GB-COH-00002065'
    assert tr['instrument_effective_from']=='2022-03-31'
    assert tr['implementation_milestone']=='2025-03-31'
    assert tr['hypothesis_id']=='RCO-LBG-005'
    assert 'not evidence of a Lloyds deficiency' in tr['consequence']


@pytest.mark.parametrize('mutation',['registry','identity','applicability','hypothesis','source','prior_digest','duplicate','claim_scope','source_digest','accepted'])
def test_trace_and_source_tampering_fails_closed(tmp_path,monkeypatch,mutation):
    data,_=t.load_traces();data=deepcopy(data)
    if mutation=='registry':data['traces'][0]['entity']['registry_id']='99999999'
    elif mutation=='identity':data['traces'][0]['entity']['legal_entity_id']='PARENT'
    elif mutation=='applicability':data['traces'][0]['applicability']='verified'
    elif mutation=='hypothesis':data['traces'][1]['hypothesis_id']='RCO-LBG-005'
    elif mutation=='source':data['traces'][0]['source_ids']=['PRIVATE-SOURCE']
    elif mutation=='prior_digest':data['previous_context_digest']='0'*64
    elif mutation=='duplicate':data['traces'].append(deepcopy(data['traces'][0]))
    elif mutation=='claim_scope':data['observations'][0]['candidate']['time_scope']='OTHER'
    elif mutation=='source_digest':data['sources'][0]['text_sha256']='0'*64
    else:data['observations'][0]['accepted_observation']=True
    p=tmp_path/'trace.json';p.write_text(json.dumps(data));monkeypatch.setattr(t,'PATH',p)
    with pytest.raises(ValueError):t.load_traces()


def test_reference_is_deterministic_server_derived_and_not_a_persistence_payload():
    chosen=choose(market='GB',offering='ai-delivery');before=deepcopy(commercial_capture('lloyds','RCO-LBG-005'))
    ref=t.capture_reference(chosen,'RCO-LBG-005')
    assert ref==t.capture_reference(choose(market='GB',offering='none'),'RCO-LBG-005')
    assert t.validate_reference(ref,chosen,'RCO-LBG-005')==ref
    assert ref['persistence_supported'] is False
    assert ref['reference']['original_hypothesis_id']=='RCO-LBG-005'
    assert commercial_capture('lloyds','RCO-LBG-005')==before


@pytest.mark.parametrize('field',['review_digest','assessment_digest','original_hypothesis_id','entity_scope','claim_ids'])
def test_caller_modified_reference_rejected(field):
    chosen=choose(market='GB');ref=t.capture_reference(chosen,'RCO-LBG-005')
    ref['reference'][field]='forged'
    with pytest.raises(ValueError):t.validate_reference(ref,chosen,'RCO-LBG-005')


@pytest.mark.parametrize('market,hypothesis',[('GB','RCO-LBG-001'),('FR','RCO-LBG-005'),('global','RCO-LBG-005')])
def test_reference_does_not_create_unreviewed_hypothesis_links(market,hypothesis):
    with pytest.raises(ValueError):t.capture_reference(choose(market=market),hypothesis)


def test_public_trace_cannot_read_private_records_or_rewrite_capture(web,actor,monkeypatch):
    existing=sales.create_opportunity('lloyds','RCO-LBG-005',headers=actor[3]);before=store_hash()
    def forbidden(*a,**k):raise AssertionError('Public trace read private pipeline')
    monkeypatch.setattr(sales,'list_opportunities',forbidden)
    for path in ('/macro?market=GB&view=enterprise','/macro?market=FR&category=sustainability&force=eu-csrd&view=enterprise','/macro/evidence?market=GB','/macro/spec?market=GB'):
        status,html,_=web(path,authenticated=False)
        assert status==200 and existing['id'] not in html and 'synthetic-workspace' not in html
    reference=t.capture_reference(choose(market='GB'),'RCO-LBG-005')
    with pytest.raises(sales.SalesValidationError):
        sales.create_opportunity('lloyds','RCO-LBG-005',values={'macro_context':reference},headers=actor[3])
    assert sales.create_opportunity('lloyds','RCO-LBG-005',headers=actor[3])==existing
    with pytest.raises(sales.SalesValidationError):
        sales.update_opportunity(existing['id'],existing['version'],{'stage':'Qualified','confirm':'yes'},headers=actor[3])
    assert store_hash()==before


@pytest.mark.parametrize('market,force,category',[('GB','cyber','cyber'),('FR','eu-csrd','sustainability')])
def test_one_concise_panel_and_deliberate_full_dossier(market,force,category):
    from urllib.parse import urlencode
    q=urlencode(dict(market=market,force=force,category=category,view='enterprise'))
    html=unescape(v.render(q));full=unescape(v.render(q,evidence=True))
    assert html.count("class='mi-inspector'")==1
    assert 'What next' in html
    footer=html.split("class='mi-print-only'")[1]
    assert ('company/00002065' in footer and 'ss121-march-22.pdf' in footer) if market=='GB' else 'legifrance.gouv.fr' in footer
    assert ('Formal applicability: Unknown' if market=='GB' else 'formal applicability: Unknown') in html
    assert 'Decision & evidence dossier' in html and "id='entity-trace'" not in html
    assert "id='entity-trace'" in full and 'Counter-tests' in full and 'Versioned edge manifest' in full


def test_original_opportunity_identities_and_scope_stay_intact():
    assert len(load_assessment('banking')['candidates'])==9
    assert len(load_assessment('aviation')['candidates'])==6
    assert t.trace_projection(choose(market='GB'))['entity']['parent_id'] is None
