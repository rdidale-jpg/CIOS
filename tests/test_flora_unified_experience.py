"""Unified product journey, visual lineage and compatibility contracts."""
from copy import deepcopy
from html.parser import HTMLParser
import json
from urllib.parse import urlsplit
import pytest
from cios.applications.flora.research_intelligence import model, unified_views as views
from cios.applications.flora.research_intelligence.visual_specs import build_visual_specs,validate_visual_spec
from cios.applications.flora.research_intelligence.visual_templates import render_visual
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_research_intelligence import web
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor


class Navigation(HTMLParser):
    def __init__(self,html):
        super().__init__();self.primary=False;self.labels=[];self.in_link=False;self.urls=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='nav' and a.get('aria-label')=='Primary product navigation':self.primary=True
        if tag=='a':
            self.urls.append(a.get('href',''))
            if self.primary:self.in_link=True
    def handle_endtag(self,tag):
        if tag=='nav':self.primary=False
        if tag=='a':self.in_link=False
    def handle_data(self,text):
        if self.primary and self.in_link:self.labels.append(text)


def test_primary_navigation_is_consistent_and_specialist_tools_are_contextual(web):
    for path in ['/','/industries','/enterprises','/opportunities','/industries/banking','/enterprises/lloyds','/flora/banking','/flora/banking/research/sources']:
        status,html=web(path);assert status==200,path
        assert Navigation(html).labels==['Home','Industries','Enterprises','Opportunities','Pipeline']
        assert '/flora/sales/pipeline' in Navigation(html).urls
        assert 'Research &amp; specialist tools' in html or 'Research & specialist tools' in html
    assert not public_request_target('/flora/sales/pipeline')


def test_canonical_home_industry_enterprise_opportunity_journey(web):
    for path,required in [('/', '/industries'),('/industries','/industries/banking'),('/industries/banking','/enterprises/lloyds'),('/enterprises/lloyds','/opportunities')]:
        status,html=web(path);assert status==200 and required in Navigation(html).urls
    html=web('/opportunities')[1]
    for row in model.commercial_candidates(shortlisted_only=True):
        target=views.ROUTES['candidates']+'/'+row['id'];assert target in Navigation(html).urls
        status,detail=web(target);assert status==200
        for c in row['claim_ids'][:1]:assert web(views.ROUTES['evidence']+'/'+c)[0]==200


def test_canonical_bank_pages_and_other_historical_profiles_are_explicit(web):
    assert "rel='canonical' href='/industries/banking'" in web('/industries/banking')[1]
    assert "rel='canonical' href='/enterprises/lloyds'" in web('/enterprises/lloyds')[1]
    for slug in ['barclays','hsbc-uk','natwest','santander-uk']:
        assert 'Historical supporting profile' in web('/enterprises/'+slug)[1]


def test_legacy_entry_urls_retain_supporting_content_and_canonical_destinations(web):
    for path,target in [('/flora/banking','/industries/banking'),('/flora/banking/explorer','/industries/banking'),('/flora/banking/research','/industries/banking'),('/flora/banking/lloyds','/industries/banking'),('/flora/banking/explorer/lloyds','/enterprises/lloyds'),('/flora/banking/research/lloyds','/enterprises/lloyds')]:
        status,html=web(path);assert status==200 and "data-legacy-compatibility='true'" in html
        assert target in Navigation(html).urls and 'Open retained' in html
    assert web('/flora/banking/explorer/lloyds/insights')[0]==200


def test_all_six_specs_are_derived_from_the_existing_research_contract():
    d=model.load_assessment();s=views.specs(d)
    assert set(s)=={'pestle','five-forces','value-chain','operating-model','ecosystem','opportunities'}
    assert [len(s[k]['nodes']) for k in s]==[6,5,8,10,4,9]
    for spec in s.values():
        assert validate_visual_spec(spec,d,views.ROUTES)
        assert spec['last_research_update']==d['assessed_at']
        assert all(n['enterprise_url']=='/enterprises/lloyds' for n in spec['nodes'])
        assert all(n['last_research_update']==d['assessed_at'] for n in spec['nodes'])
        assert all(n['priority'] is None for n in spec['nodes']) if spec['diagram_type']!='opportunities' else all(n['verification']=='unqualified opportunity hypothesis' for n in spec['nodes'])


def test_visuals_use_distinct_framework_geometries_and_keyboard_destinations():
    s=views.specs();rendered={k:render_visual(v) for k,v in s.items()}
    assert '<circle' in rendered['pestle'] and ' A 185 185' in rendered['pestle']
    assert 'M450 130' in rendered['five-forces']
    assert rendered['value-chain'].count('<polygon')==8
    assert 'BUSINESS CAPABILITIES' in rendered['operating-model']
    assert 'stroke-dasharray' in rendered['ecosystem']
    assert 'Relevance' in rendered['opportunities'] and '/3' in rendered['opportunities']
    for k,html in rendered.items():
        assert "role='group'" in html and '<title' in html and "tabindex='0'" in html
        for node in s[k]['nodes']:assert node['url'] in Navigation(html).urls


def test_industry_lenses_and_enterprise_views_open_each_template(web):
    for path,kind in [('/industries/banking?lens=pestle','pestle'),('/industries/banking?lens=porter','five-forces'),('/industries/banking?lens=value-chain','value-chain'),('/enterprises/lloyds','operating-model'),('/enterprises/lloyds?lens=ecosystem','ecosystem'),('/enterprises/lloyds?lens=opportunities','opportunities')]:
        status,html=web(path);assert status==200 and "data-diagram-type='"+kind+"'" in html
        assert '/opportunities' in Navigation(html).urls


def test_specification_json_endpoint_matches_page_inputs_and_is_public(web):
    status,body=web('/industries/banking/visual-specs');assert status==200
    assert json.loads(body)==views.specs()
    assert public_request_target('/industries/banking/visual-specs')
    for bad in ['/industries/banking/visual-specs?workspace=private','/enterprises/private','/industries/../../private','/industries/banking?lens=porter&lens=pestle']:
        assert not public_request_target(bad)
    assert web('/industries/banking?lens=unimplemented')[0]==404


def test_visual_nodes_only_link_to_existing_finite_public_evidence_and_research(web):
    for spec in views.specs().values():
        for node in spec['nodes']:
            assert public_request_target(node['url']) and web(node['url'])[0]==200
            for edge in node['evidence']:
                assert public_request_target(edge['url']) and web(edge['url'])[0]==200
            for edge in node['opportunity_links']:
                assert public_request_target(edge['url']) and web(edge['url'])[0]==200


def test_visual_contract_rejects_invented_labels_edges_and_claim_upgrades():
    d=model.load_assessment();original=views.specs(d)['ecosystem']
    for mutate in [lambda s:s['nodes'][0].update(label='Invented supplier'),lambda s:s['nodes'][0].update(verification='verified exclusive incumbent'),lambda s:s['relationships'][0].update(verified=True),lambda s:s['nodes'][0].update(evidence_refs=['unknown-claim']),lambda s:s['nodes'][0].update(summary='An invented budget has been approved'),lambda s:s['nodes'].pop(),lambda s:s['relationships'].pop()]:
        bad=deepcopy(original);mutate(bad)
        with pytest.raises(ValueError):validate_visual_spec(bad,d,views.ROUTES)
    bad=deepcopy(original);bad['nodes'][0]['url']='https://external.example/private'
    with pytest.raises(ValueError):validate_visual_spec(bad,d,views.ROUTES)


def test_visual_contract_rejects_changed_periods_ratings_or_priorities():
    d=model.load_assessment();original=views.specs(d)['opportunities']
    for mutate in [lambda s:s['nodes'][0].update(priority=999),lambda s:s['nodes'][0]['ratings']['commercial_accessibility'].update(score=3),lambda s:s['nodes'][0]['evidence'][0].update(status='customer-confirmed demand'),lambda s:s['nodes'][0]['evidence'][0].update(period='invented period')]:
        bad=deepcopy(original);mutate(bad)
        with pytest.raises(ValueError):validate_visual_spec(bad,d,views.ROUTES)


def test_supplier_visual_preserves_unknown_contracts_and_reported_history():
    spec=views.specs()['ecosystem'];nodes={n['id']:n for n in spec['nodes']}
    assert 'source-supported relationship' in nodes['SUP-GOOGLE']['verification']
    assert nodes['SUP-AWS']['verification']=='enterprise relationship unverified'
    assert nodes['SUP-ORACLE']['verification']=='enterprise relationship unverified'
    assert 'primary verification pending' in nodes['SUP-MICROSOFT']['verification']
    assert any(e['verified'] for e in spec['relationships']) and any(not e['verified'] for e in spec['relationships'])


def test_current_historical_and_inferred_evidence_remain_available(web):
    html=web('/enterprises/lloyds')[1]
    assert 'Key findings &amp; important changes' in html or 'Key findings & important changes' in html
    assert 'Evidence, historical observations & research gaps' in html
    assert 'source-supported disclosure' in html and 'historical' in html
    assert '/flora/banking/research/sources' in html and '/flora/banking/research/gaps' in html
    assert 'Historical Horizon scenarios' in web('/opportunities')[1]


def test_visual_reading_preserves_existing_pipeline_and_qualification(actor):
    from cios.applications.flora import sales_pipeline as sales
    r=sales.create_opportunity('lloyds','RCO-LBG-002',headers=actor[3])
    before=sales.get_opportunity(r['id'],headers=actor[3])
    views.industry_page(headers=actor[3]);views.enterprise_page(headers=actor[3]);views.opportunities_body();views.specs()
    assert sales.get_opportunity(r['id'],headers=actor[3])==before
    assert len(sales.list_opportunities(headers=actor[3]))==1
    assert before['stage']=='Discovered' and before['qualification']=={} and not before['evidence_reviewed']


def test_generic_sector_configuration_uses_the_same_visual_api_without_banking_routing():
    d=model.load_assessment();routes={k:'/generic/'+k for k in views.ROUTES};routes['opportunities']='/generic/opportunities'
    # Existing facts remain unchanged; only presentation destinations differ.
    original=deepcopy(d);priorities=model.commercial_candidates(d)
    s=build_visual_specs(d,routes,priorities)
    assert d==original
    for spec in s.values():
        assert spec['opportunities_url']=='/generic/opportunities'
        assert all(n['url'].startswith('/generic/') and n['enterprise_url']=='/generic/enterprise' for n in spec['nodes'])
        assert '<svg' in render_visual(spec)
