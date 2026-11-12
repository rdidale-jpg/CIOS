"""Market context, evidence limits, genuine navigation and existing authority boundaries."""
from copy import deepcopy
from html import unescape
import json
from pathlib import Path
import pytest
from cios.applications.flora.research_intelligence import macro_intelligence as m, macro_views as views
from cios.applications.flora.research_intelligence.model import load_assessment, primary_text
from cios.applications.flora.public_routes import public_request_target,public_route_catalog
from cios.applications.flora import sales_pipeline as sales
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor,web
from tests.test_flora_commercial_visual_v3 import store_hash


def choose(**values):
    from urllib.parse import urlencode
    return m.selection(urlencode(values))


def test_seven_primary_excerpts_reuse_unaccepted_semantic_and_evidence_contracts():
    data=m.load_context();twin=m.semantic_projection(data)
    assert len(twin.objects)==len(data['sources'])==7
    assert any(o['candidate']['claim_type']=='observed_trend' for o in data['observations'])
    assert next(f for f in data['forces'] if f['id']=='cyber')['kind']=='threat_or_scenario'
    for obj in twin.objects:
        assert not obj.eligible_conclusion and obj.validation_status=='candidate'
        attrs=obj.attributes
        assert attrs['segment']['content']==attrs['candidate_claim']['statement']
        assert attrs['evidence_item']['lineage'][0]==attrs['segment']['segment_id']
    for source in data['sources']:
        assert source['primary_content_sha256'] is None
        assert source['excerpts'][0]['quote'] in primary_text(source)
        assert source['retrieval_method']=='approved_web_research_tool'


@pytest.mark.parametrize('industry',['banking','aviation'])
def test_gb_and_fr_reuse_one_industry_model_without_copying_or_mutating_research(industry):
    data=load_assessment(industry);before=deepcopy(data)
    gb=m.context_spec(choose(market='GB',industry=industry))
    fr=m.context_spec(choose(market='FR',industry=industry))
    assert gb['industry_model_id']==fr['industry_model_id']==data['assessment_id']
    assert data==before==load_assessment(industry)
    assert gb['markets'][0]['country_id']=='GB' and fr['markets'][0]['country_id']=='FR'
    assert 'incomplete' in fr['markets'][0]['coverage']


def test_global_cyber_is_one_force_with_separately_scoped_country_edges():
    data=m.load_context();spec=m.context_spec(choose(market='global'))
    assert sum(f['id']=='cyber' for f in data['forces'])==1
    assert {edge['country_id'] for edge in spec['edges']}=={'GB','FR'}
    assert len({edge['id'] for edge in spec['edges']})==len(spec['edges'])
    for edge in spec['edges']:
        if edge['predicate']!='MOTIVATES_INVESTIGATION':assert edge['source_ids']==['GM-CYBER-'+edge['country_id']]
    assert all(edge['claim_ids'] and edge['source_ids'] and edge['limitations'] for edge in spec['edges'])
    assert all(edge['status']=='interpreted' for edge in spec['edges'] if edge['predicate']=='INTERPRETED_PESTLE_IMPACT')


def test_navigation_region_is_not_legal_jurisdiction():
    data=m.load_context()
    europe=next(a for a in data['areas'] if a['id']=='EUROPE')
    assert set(europe['members'])=={'GB','FR'}
    assert 'navigation' in europe['membership_kind']
    assert 'EUROPE' not in {j['id'] for j in data['jurisdictions']}
    assert {'EU-CSRD','FR-CSRD'}<={j['id'] for j in data['jurisdictions']}


@pytest.mark.parametrize('industry',['banking','aviation'])
@pytest.mark.parametrize('force',['social-value','uk-srs','cyber-bill'])
def test_uk_instruments_do_not_propagate_to_french_procurement_or_enterprises(industry,force):
    category='cyber' if force=='cyber-bill' else 'sustainability'
    chosen=choose(market='FR',industry=industry,category=category,force=force,view='enterprise')
    spec=m.context_spec(chosen)
    assert not spec['edges'] and not spec['candidates']
    html=unescape(views.render(__import__('urllib.parse',fromlist=['urlencode']).urlencode(chosen.model_dump())))
    assert 'Outside reviewed country coverage' in html
    assert 'Country coverage is not a legal applicability decision' in html
    if force=='social-value':assert 'Supplier nationality and buyer jurisdiction are different questions' in html
    assert 'Unknown' in html


@pytest.mark.parametrize('industry',['banking','aviation'])
def test_fr_sustainability_retains_eu_enactment_vs_national_transposition_unknown(industry):
    spec=m.context_spec(choose(market='FR',industry=industry,category='sustainability',force='eu-csrd'))
    assert spec['force']['kind']=='enacted_law'
    assert spec['force']['jurisdiction_ids']==['EU-CSRD','FR-CSRD']
    assert spec['enterprise']['applicability']=='unknown'
    assert all(e['status']=='unknown' for e in spec['edges'] if e['predicate']=='ENTERPRISE_APPLICABILITY')
    assert not spec['candidates'] # Never transplant UK group hypotheses into France.


def test_parent_identity_never_proves_child_identity_or_inherits_an_obligation():
    scope={'id':'SYNTHETIC-PARENT-SCOPE','enterprise_id':'SYNTHETIC-GROUP','legal_entity_id':'PARENT',
           'registry_id':'SYNTHETIC-REGISTRY','legal_name':'Synthetic parent only','status':'verified','evidence_ids':['SYNTHETIC-IDENTITY']}
    assert m.exact_entity_identity(scope,'PARENT') is True
    assert m.exact_entity_identity(scope,'CHILD') is False
    assert m.exact_entity_identity(scope,None) is False
    for row in m.load_context()['legal_entity_scopes']:
        assert row['status']=='unknown' and row['registry_id'] is None
    spec=m.context_spec(choose())
    edge=next(e for e in spec['edges'] if e['predicate']=='ENTERPRISE_APPLICABILITY')
    with pytest.raises(ValueError):m.ContextEdge(**{**edge,'status':'verified'})


@pytest.mark.parametrize('missing',['registry_id','legal_name','evidence_ids'])
def test_verified_entity_identity_requires_explicit_evidence(missing):
    fields={'id':'S','enterprise_id':'E','legal_entity_id':'L','registry_id':'R','legal_name':'N','status':'verified','evidence_ids':['Q']}
    fields[missing]=[] if missing=='evidence_ids' else None
    with pytest.raises(ValueError):m.LegalEntityScope(**fields)


@pytest.mark.parametrize('change',['effective_date','legal_kind'])
def test_proposed_bill_cannot_be_upgraded_to_enacted_duty(change):
    data=m.load_context();force=next(f for f in data['forces'] if f['id']=='cyber-bill')
    if change=='effective_date':force['effective_from']='2027-01-01'
    else:force['kind']='enacted_law'
    with pytest.raises(ValueError):m.validate_context(data)


@pytest.mark.parametrize('field',['content_hash','asset_id','source_location'])
def test_source_passage_identity_and_digest_cannot_drift(field):
    data=m.load_context();data['observations'][0]['segment'][field]='UNSUPPORTED'
    with pytest.raises(ValueError):m.validate_context(data)


@pytest.mark.parametrize('query',['market=DE','market=FR&market=GB','workspace_id=private','force=made-up',
    'category=cyber&force=uk-srs','industry=private','capability=PRIVATE-RESOURCE','factor=made-up','mode=admin'])
def test_ambiguous_or_unregistered_contexts_fail_closed(query):
    with pytest.raises(ValueError):m.selection(query)


@pytest.mark.parametrize('target',['/macro/private','/macro/../evidence','/macro//','/macro%2fspec',
    '/macro?workspace_id=secret','/macro?market=GB&market=FR','/macro/spec?account_id=other'])
def test_public_macro_catalogue_never_accepts_private_selectors_or_prefixes(target):
    assert not public_request_target(target)


def test_all_three_macro_routes_are_explicitly_public_and_bound_to_repo_data():
    for path in ('/macro','/macro/evidence','/macro/spec'):
        assert public_request_target(path)
        policy=public_route_catalog()[path]
        assert 'repository' in policy.source_boundary and 'authority' in policy.source_boundary


@pytest.mark.parametrize('offering',['none','cyber','ai-delivery','reporting'])
def test_seller_fit_is_ephemeral_not_customer_demand_or_territorial_permission(offering):
    spec=m.context_spec(choose(market='GB',offering=offering))
    assert spec['seller_relevance']['declared_offering']==offering
    assert spec['seller_relevance']['customer_demand']=='unverified'
    assert spec['seller_relevance']['territory_permission']=='unverified'
    assert spec['automatic_capture'] is False and spec['automatic_qualification'] is False


def test_unsupported_category_is_an_explicit_research_gap_not_zero_risk():
    spec=m.context_spec(choose(category='economy'))
    assert spec['force'] is None and not spec['edges'] and not spec['candidates']
    html=views.render('category=economy')
    assert 'Not researched yet' in html and 'Blank does not mean no risk' in html


@pytest.mark.parametrize('industry,force,category,expected',[('banking','cyber','cyber',['RCO-LBG-005']),('aviation','uk-srs','sustainability',['RCO-EJ-006']),('banking','social-value','sustainability',[])])
def test_existing_hypotheses_are_only_thematic_associations_with_evidence_and_no_new_ids(industry,force,category,expected):
    spec=m.context_spec(choose(market='GB',industry=industry,force=force,category=category))
    assert [c['id'] for c in spec['candidates']]==expected
    known={c['id'] for c in load_assessment(industry)['candidates']}
    assert set(expected)<=known
    for edge in spec['edges']:
        if edge['predicate']=='MOTIVATES_INVESTIGATION':
            assert edge['status']=='interpreted'
            assert any(cid.startswith('GM-CLAIM-') for cid in edge['claim_ids'])
            assert any(not cid.startswith('GM-CLAIM-') for cid in edge['claim_ids'])


def test_generated_contract_schema_matches_the_reusable_models():
    stored=json.loads((m.PATH.parent/'Global-Context-Contracts-v1.schema.json').read_text())
    assert stored==m.context_schema()
    assert {'GeographicArea','Jurisdiction','LegalEntityScope','MarketContext','ContextEdge'}<=set(stored['$defs'])


def test_public_journeys_do_not_enumerate_or_modify_private_pipeline(web,actor,monkeypatch):
    existing=sales.create_opportunity('lloyds','RCO-LBG-005',headers=actor[3]);frozen=deepcopy(existing);before=store_hash()
    def forbidden(*args,**kwargs):raise AssertionError('Public macro route enumerated private pipeline')
    monkeypatch.setattr(sales,'list_opportunities',forbidden)
    for path in ('/macro','/macro?market=FR&view=industry','/macro?view=enterprise','/macro/evidence?category=sustainability&force=social-value','/macro/spec'):
        status,html,_=web(path,authenticated=False);assert status==200,(path,status)
        assert 'synthetic-workspace' not in html and existing['id'] not in html
    assert store_hash()==before and sales.get_opportunity(existing['id'],headers=actor[3])==frozen
    assert sales.create_opportunity('lloyds','RCO-LBG-005',headers=actor[3])==frozen
    with pytest.raises(sales.SalesValidationError):sales.update_opportunity(existing['id'],existing['version'],{'stage':'Qualified','confirm':'yes'},headers=actor[3])
    assert store_hash()==before


@pytest.mark.parametrize('query',['market=DE','force=made-up','factor=private'])
def test_invalid_public_context_is_a_controlled_error_not_server_failure(web,query):
    assert web('/macro?'+query,authenticated=False)[0]==400


def test_selected_page_has_one_inspector_and_keeps_deep_research_on_demand():
    for view in ('atlas','industry','enterprise'):
        html=views.render('view='+view)
        assert html.count("class='mi-inspector'")==1
        assert "class='mi-report'" not in html
        assert 'Primary evidence & full dossier' in unescape(html)
        assert "data-macro-print='executive'" in html
        assert '<canvas' not in html
    html=views.render('',evidence=True)
    assert "class='mi-report'" in html
    assert 'Overall prevalence of cyber breaches or attacks' in html
    assert 'Locator:' in html and 'Retrieved:' in html and 'original checksum unavailable' in html


def test_fr_category_defaults_to_local_evidence_without_transferring_uk_policy():
    chosen=choose(market='FR',category='sustainability')
    assert chosen.force=='eu-csrd'
    assert m.context_spec(chosen)['force']['country_ids']==['FR']


def test_french_reference_switched_to_uk_retains_unknown_scope_and_correct_explanation():
    chosen=choose(market='GB',category='sustainability',force='eu-csrd',view='enterprise')
    spec=m.context_spec(chosen)
    assert not spec['edges'] and not spec['candidates']
    html=unescape(views.render('market=GB&category=sustainability&force=eu-csrd&view=enterprise'))
    assert 'evidence for France does not establish applicability in the selected United Kingdom view' in html
    assert 'Cross-border reach, listing status, entity and activity scope need separate evidence' in html
    assert 'this UK rule/policy' not in html and 'Unknown' in html
