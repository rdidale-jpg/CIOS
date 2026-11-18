"""Real read-only preview boundary/lineage/selection tests, never production writes."""
from copy import deepcopy
from html.parser import HTMLParser
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
import json
import threading
from urllib.parse import parse_qs, urlsplit

import pytest
from cios.applications.flora import enterprise_preview as v
from cios.applications.flora.public_routes import public_request_target, public_route_catalog
from cios.applications.flora.research_intelligence import model
from tests.test_flora_research_intelligence import web

pytestmark = pytest.mark.real_security_boundary


@pytest.mark.parametrize('query', [{}, {'stream':['forces']}, {'capability':['network-planning']}, {'stream':['changing'],'capability':['customer-service']}])
def test_finite_state_roundtrips_all_selectors(query):
    ctx = v.resolve(query)
    assert v.resolve(parse_qs(urlsplit(v.url(ctx)).query)) == ctx
    for stream in v.STREAMS:
        switched = v.resolve(parse_qs(urlsplit(v.url(ctx,stream=stream)).query))
        assert switched.capability == ctx.capability and switched.stream == stream


@pytest.mark.parametrize('query', [ {'stream':['']}, {'stream':['inside']}, {'stream':['forces','landscape']}, {'capability':['lloyds']}, {'capability':['AV-ENT-001']}, {'capability':[]}, {'capability':'fleet-operations'}, {'enterprise':['BK-ENT-001']}, {'source':['SRC-AV-AR25']}, {'workspace':['private']}, {'stream':['LANDSCAPE']}])
def test_forged_perimeters_and_ambiguous_selection_fail_closed(query):
    with pytest.raises(ValueError): v.resolve(query)


@pytest.mark.parametrize('capability', list(v.CAPABILITIES))
@pytest.mark.parametrize('stream', list(v.STREAMS))
def test_capability_content_and_selection_are_scope_specific(capability,stream):
    html=v.render({'capability':[capability],'stream':[stream]})
    assert '<main ' in html and '<aside ' in html
    assert f'data-capability="{capability}"' in html
    assert '<h1 id="main-title" tabindex="-1">'+v.CAPABILITIES[capability][0]+'</h1>' in html
    assert 'Conceptual value flow' in html and 'Operating capabilities' in html
    assert 'Sources &amp; reasoning' not in html and '<blockquote' not in html
    assert 'AV-ENT-001' not in html and 'SRC-AV-' not in html
    assert not any(term in html.lower() for term in ['~30%','14,000','163 airports','37 countries','supplier budget','qualified opportunity'])
    assert v._capability_available(v.Context(stream,capability))


def test_fleet_and_network_have_distinct_economics_with_exact_historical_scope():
    fleet=v.render({});network=v.render({'capability':['network-planning']})
    assert '356 aircraft' in fleet and '30 September 2025' in fleet
    assert '1,202 routes' in network and 'Winter / summer 2025' in network
    assert 'route counts alone do not measure profitability' in network
    assert '356 aircraft' not in network and '1,202 routes' not in fleet
    assert 'Skywise' in fleet and 'Skywise' not in network
    assert 'does not identify easyJet’s organisation, system connections or supplier contracts' in fleet


@pytest.mark.parametrize('identifier', list(v.DISCLOSURES))
def test_every_enterprise_disclosure_resolves_original_primary_support(identifier):
    data=model.load_assessment('aviation');fact=v.fact(data,identifier)
    assert fact is not None and fact.semantic_type=='reported'
    claim=next(c for c in data['claims'] if c['id']==identifier)
    assert model.primary_claim_supported(data,claim)
    assert v._fingerprint(claim)==v.CLAIM_PINS[identifier]
    assert fact.canonical_status=='candidate_intelligence'


@pytest.mark.parametrize('level', ['source','claim','assessment'])
@pytest.mark.parametrize('restriction', [ {'withdrawn':True}, {'revoked':True}, {'denied':True}, {'stale':True}, {'superseded':True}, {'owner_only':True}, {'retracted':True}, {'contradictory':True}, {'freshness':'stale'}, {'rights':{'status':'revoked'}}, {'rights':{'status':'denied'}}, {'rights':{'status':'unknown'}}, {'rights':[]}])
def test_all_existing_lifecycle_and_rights_encodings_remove_dependent_content(level,restriction):
    data=model.load_assessment('aviation')
    row=data if level=='assessment' else next(r for r in data['sources' if level=='source' else 'claims'] if r['id']==('SRC-AV-AR25' if level=='source' else 'AV-FLEET'))
    row.update(restriction)
    assert v.fact(data,'AV-FLEET') is None
    if level!='assessment': assert v.fact(data,'AV-CHAT') is not None


@pytest.mark.parametrize('field,value', [('asset_id','BK-ENT-001'),('entity_scope','easyJet Airline Company Limited'),('reporting_period','Year ended 2026'),('statement','A different revision'),('metric_unit','USD')])
def test_claim_perimeter_period_and_revision_dont_inherit_editorial_authority(field,value):
    data=model.load_assessment('aviation');next(c for c in data['claims'] if c['id']=='AV-FLEET')[field]=value
    assert v.fact(data,'AV-FLEET') is None
    assert v.fact(data,'AV-CHAT') is not None


@pytest.mark.parametrize('field,value', [('research_domain','banking'),('retrieval_extent','search-index only')])
def test_source_wrong_domain_and_index_only_are_not_public_facts(field,value):
    data=model.load_assessment('aviation');next(s for s in data['sources'] if s['id']=='SRC-AV-AR25')[field]=value
    assert v.fact(data,'AV-FLEET') is None


def test_source_bytes_tamper_fails_closed(monkeypatch):
    data=model.load_assessment('aviation');source=next(s for s in data['sources'] if s['id']=='SRC-AV-AR25');source['text_sha256']='0'*64
    assert v.fact(data,'AV-FLEET') is None
    assert v.fact(data,'AV-CHAT') is not None


def test_profile_node_withdrawal_removes_selected_content(monkeypatch):
    profile=v._profile();next(a for a in profile['activities'] if a['id']=='VI-EJ-FLEET')['withdrawn']=True
    monkeypatch.setattr(v,'_profile',lambda:profile)
    assert not v._capability_available(v.Context())
    assert '356 aircraft' not in v.render({})
    assert v._capability_available(v.Context(capability='network-planning'))


@pytest.mark.parametrize('field,value', [('research_domain','banking'),('enterprise_twin_id','BK-ENT-001'),('industry_twin_id','BK-IND-002'),('assessed_at','2099-01-01'),('owner_only',True),('withdrawn',True)])
def test_entire_research_perimeter_and_future_assessment_guard(monkeypatch,field,value):
    data=model.load_assessment('aviation');data[field]=value
    monkeypatch.setattr(v,'_read_assessment',lambda:data)
    assert v._data() is None
    assert '356 aircraft' not in v.render({})


def test_catalogue_is_exact_additive_and_has_no_private_selector():
    from tools.research.etvis2_compatibility import validate
    assert validate()['production_controls_changed']==0
    assert public_request_target(v.ROUTE+'?stream=forces&capability=network-planning')
    for suffix in ['/../lloyds','/assets/../../security','?enterprise=BK-ENT-001','?workspace=x','?stream=forces&stream=landscape','/assets/artwork?source=private']:
        assert not public_request_target(v.ROUTE+suffix)
    assert public_route_catalog()['/enterprises/easyjet'].query_keys==frozenset({'lens'})


@pytest.mark.parametrize('path',[v.ROUTE, v.ROUTE+'?stream=changing&capability=network-planning',v.ASSET_BASE+'artwork',v.ASSET_BASE+'styles',v.ASSET_BASE+'interactions'])
def test_actual_public_handler_and_assets(web,path):
    status,body=web(path);assert status==200
    assert body


@pytest.mark.parametrize('suffix',['?stream=inside','?capability=private','?stream=','?source=SRC-AV-AR25','/assets/private'])
def test_invalid_requests_never_expose_private_records(web,suffix):
    status,body=web(v.ROUTE+suffix)
    assert status in {403,404}
    assert '356 aircraft' not in body


def test_existing_aviation_and_banking_routes_are_unchanged(web):
    for path in ['/enterprises/easyjet','/industries/aviation','/industries/banking','/enterprises/lloyds']:
        status,html=web(path);assert status==200
        assert 'Enterprise Twin · Preview' not in html
    for path in ['/financial-intelligence','/flora/offers','/sales-pipeline','/flora/owner/assurance']:
        status,_=web(path);assert status in {403,404}


def test_presentation_has_no_private_service_or_write_calls():
    import ast
    tree=ast.parse(Path(v.__file__).read_text())
    imports=[ast.unparse(n)for n in ast.walk(tree)if isinstance(n,(ast.Import,ast.ImportFrom))]
    assert not any(term in '\n'.join(imports)for term in ['memory.repository','seller_development','sales_pipeline','financial_intelligence','sqlite','requests','supabase'])
    for n in ast.walk(tree):
        if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute):
            assert n.func.attr not in {'write_text','write_bytes','mkdir','unlink','save','create','promote','qualify','execute'}


def test_actual_render_isolates_a_bad_primary_snapshot(monkeypatch):
    primary=model.primary_text
    def scoped_failure(source):
        if source['id']=='SRC-AV-AR25':raise ValueError('Damaged source snapshot')
        return primary(source)
    monkeypatch.setattr(model,'primary_text',scoped_failure)
    assert '356 aircraft' not in v.render({})
    html=v.render({'capability':['network-planning'],'stream':['changing']})
    assert 'ChatGPT discovery directs customers' in html


@pytest.mark.parametrize('mutation',['withdrawn','owner_only','stale','removed'])
def test_referenced_research_capability_lifecycle_is_respected(monkeypatch,mutation):
    data=v._data()
    if mutation=='removed':data['capabilities']=[c for c in data['capabilities']if c['id']!='AV-CAP-MRO']
    else:next(c for c in data['capabilities']if c['id']=='AV-CAP-MRO')[mutation]=True
    monkeypatch.setattr(v,'_read_assessment',lambda:data)
    assert '356 aircraft' not in v.render({})
    assert '1,202 routes' in v.render({'capability':['network-planning']})


@pytest.mark.parametrize('field,value',[('url','https://www.natwestgroup.com/'),('publisher','Another issuer'),('reporting_period','Year ended 2026'),('publication_date','2026-01-01')])
def test_source_identity_and_temporal_changes_cannot_inherit_old_projection(field,value):
    data=v._data();next(s for s in data['sources']if s['id']=='SRC-AV-AR25')[field]=value
    assert v.fact(data,'AV-FLEET') is None
    assert v.fact(data,'AV-CHAT') is not None


@pytest.mark.parametrize('root',[None,[],[{}],{'schema_version':1,'authority':'candidate_intelligence','claims':None}, {'schema_version':1,'authority':'candidate_intelligence','sources':[None]}])
def test_malformed_assessment_roots_fail_bounded(monkeypatch,root):
    monkeypatch.setattr(v,'_read_assessment',lambda:root)
    assert v._data() is None
    assert '356 aircraft' not in v.render({})


def test_adjacent_announcements_do_not_claim_capability_change():
    html=v.render({'stream':['changing'],'capability':['network-planning']})
    assert 'adjacent commercial-channel context' in html
    assert 'does not establish a change in this capability' in html


def test_source_lineage_and_original_artwork_inventory():
    from tools.research.etvis2_quality import validate
    report=validate()
    assert report['unchanged_visual_stream_files']==51
    assert report['public_disclosures']==7 and report['existing_source_records']==6


def test_generic_operating_mechanisms_are_not_misclassified_as_eligible_insights():
    html=v.render({'stream':['forces']})
    assert 'Conceptual operating mechanism' in html
    assert 'FLORA Insight' not in html
