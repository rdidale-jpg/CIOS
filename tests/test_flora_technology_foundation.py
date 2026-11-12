"""Governed Page recovery, scope boundaries and read-only HTTP integration."""
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import pytest
from cios.applications.flora.research_intelligence import technology as t, technology_views as v
from cios.applications.flora.research_intelligence import source_import
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_research_intelligence import web
from tests.test_flora_sales_pipeline import actor, web as sales_web
from tests.test_flora_security_repair_01b import authority


class DOM(HTMLParser):
    def __init__(self,html):
        super().__init__();self.ids=[];self.links=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href',''))


def test_all_80_views_reconcile_exactly_to_the_page_population_with_no_entity_creation():
    d,blocks=t.load();population=next(b['markdown'] for b in blocks.values() if b['markdown'].startswith('| Primary placement'))
    selected=[n for line in population.splitlines()[2:-1] for n in line.split('|')[2].strip().split('; ')]
    assert [r['label'] for r in d['providers']]==selected and len(selected)==len(set(selected))==80
    assert all(r['canonical_enterprise_id'] is None and r['identity_status']=='unbound' for r in d['providers'])
    assert all(r['selection_block'] in blocks for r in d['providers'])
    assert all('source-operation' in ' '.join(r['gaps']) for r in d['providers'])


def test_population_groups_and_overlapping_segments_have_separate_denominators():
    d,_=t.load();assert len({r['primary_group'] for r in d['providers']})==8 and len(d['segments'])==7
    rows={r['label']:r for r in d['providers']}
    assert rows['Microsoft']['memberships']==['applications','cloud','ai','cyber']
    assert 'shared group' in rows['Google DeepMind']['identity_note']
    for name in ('TCS / Diligenta','Atos / Eviden','Broadcom / VMware','VodafoneThree','Pega'):
        assert rows[name]['canonical_enterprise_id'] is None and rows[name]['identity_note']
    assert sum(len(r['memberships']) for r in d['providers'])>80


def test_source_segments_preserve_actual_page_rows_and_never_claim_original_bytes():
    d,blocks=t.load();handoff=t.handoff()
    assert len(handoff['relationships'])==34 and len(handoff['atomic_passage_references'])==24
    for row,mapping in zip(d['relationships'],handoff['relationships']):
        s=mapping['source_segment'];c=mapping['candidate_claim'];item=mapping['evidence_package_item']
        assert s['content'] in blocks[row['source_block']]['markdown']
        assert hashlib.sha256(s['content'].encode()).hexdigest()==s['content_hash']
        assert c['source_segment_id']==s['segment_id'] and c['enterprise_scope']==''
        assert item['enterprise_id']=='' and item['truth_status']=='page_research_not_accepted_evidence'
        assert mapping['canonical_evidence_id'] is None and mapping['publisher_original_sha256'] is None
        assert mapping['status']=='withheld' and not mapping['eligible_for_import']
    assert handoff['accepted']==handoff['eligible']==0 and handoff['canonical_mutation'] is handoff['pipeline_mutation'] is False
    assert all(x['retrieved_at'] is None and x['rights']=='unestablished' for x in handoff['atomic_passage_references'])


def test_import_mapping_is_deterministic_and_does_not_relabel_date_only_provenance():
    a=t.handoff();b=t.handoff();assert a==b
    assert json.loads(json.dumps(a))==json.loads((t.ASSETS/'Candidate-Handoff.json').read_text())
    for r in a['relationships']:
        assert r['retrieval_date']=='2026-11-12' and r['retrieved_at'] is None
        assert {'source_operation_rights_unestablished','canonical_identity_unbound','publisher_source_not_reacquired'}<=set(r['reasons'])


@pytest.mark.parametrize('mutation',['other_customer','cross_join','made_up_source'])
def test_candidate_mapping_rejects_fabricated_or_cross_row_page_passages(mutation):
    d,b=t.load();r=deepcopy(d['relationships'][0]);block=b[r['source_block']]
    if mutation=='other_customer':r['source_text']=r['source_text'].replace('BT Group','Invented bank')
    elif mutation=='cross_join':r['source_text']='Lloyds Banking Group | ServiceNow | Service management, Service Bridge, Now Assist for TSM | '+r['boundary']
    else:r['source_text']+=' https://invented.example/'
    with pytest.raises(ValueError):t.candidate_mapping(r,block)


def test_publisher_policy_and_existing_observation_owners_are_unchanged():
    before=subprocess.check_output(['git','show','c3b818c:cios/applications/flora/research_intelligence/source_import.py'],cwd=t.ROOT)
    assert before==(t.ROOT/'cios/applications/flora/research_intelligence/source_import.py').read_bytes()
    with pytest.raises(ValueError):source_import.official_url('https://www.anthropic.com/news/barclays-scales-claude')
    assert any('publisher_not_in_existing_allowlist' in r['reasons'] for r in t.handoff()['relationships'])
    for path in ('cios/applications/flora/memory/models.py','cios/applications/flora/blueprint_import/views.py','cios/applications/flora/sales_pipeline.py'):
        assert subprocess.check_output(['git','show','c3b818c:'+path],cwd=t.ROOT)==(t.ROOT/path).read_bytes()


@pytest.mark.parametrize('name',['Foundation.json','Research-Page.json'])
def test_changed_source_assets_fail_closed(tmp_path,monkeypatch,name):
    for file in ('Foundation.json','Research-Page.json'):(tmp_path/file).write_bytes((t.ASSETS/file).read_bytes())
    monkeypatch.setattr(t,'ASSETS',tmp_path)
    monkeypatch.setattr(t,'ROOT',tmp_path)
    with (tmp_path/name).open('a') as f:f.write(' ')
    with pytest.raises(ValueError, match='changed'):t.load()


def test_historical_and_prospective_relationship_boundaries_are_not_collapsed():
    d,_=t.load();rows={r['key']:r for r in d['relationships']}
    assert rows['programme-202-3']['event_date']=='2023-05-10' and rows['programme-202-3']['publication_date']=='2023-05-16'
    assert rows['programme-222-4']['temporal_status']=='planned / collaboration'
    assert 'not every insurer' in rows['programme-222-4']['role_boundary']
    assert 'live since 2025' in rows['programme-222-2']['role_boundary']
    assert 'no financial commitment' in rows['programme-222-5']['boundary'].lower() or 'No financial commitment' in rows['programme-222-5']['role_boundary']
    assert 'research collaboration' in rows['quantum-collaboration']['temporal_status']
    assert rows['programme-213-1']['event_date'] is None
    assert 'separate Deloitte' in rows['programme-213-2']['boundary']


def test_existing_navigation_is_exact_and_never_joins_hsbc_group_to_hsbc_uk():
    d,_=t.load();bycustomer={r['customer']:r for r in d['relationships']}
    assert t.existing_navigation(bycustomer['Lloyds Banking Group']).id=='BK-ENT-001'
    assert t.existing_navigation(bycustomer['easyJet']).id=='AV-ENT-001'
    assert t.existing_navigation(bycustomer['HSBC']) is None
    assert t.existing_navigation(bycustomer['BT Group']) is None
    assert t.existing_navigation(bycustomer['Barclays']).slug=='barclays'


def test_every_theme_has_its_underlying_research_and_remains_unqualified():
    d,b=t.load();assert len(d['themes'])==6
    ids={r['key'] for r in d['relationships']}
    for row in d['themes']:
        assert row['status']=='Unqualified research hypothesis'
        assert row['budget'] is row['procurement_date'] is row['pipeline_record_id'] is None
        assert row['qualification'] and row['alternative'] and row['intervention']
        assert row['relationship_keys'] and not set(row['relationship_keys'])-ids
        assert not set(row['support_blocks'])-set(b)


@pytest.mark.parametrize('path',['','?lens=uses','?lens=work','/providers','/providers?provider=pega','/models','/timeline','/evidence','/handoff'])
def test_public_technology_views_work_without_account_or_private_stores(web,path):
    code,html=web(t.BASE+path);assert code==200
    if path=='/handoff':assert json.loads(html)==json.loads(json.dumps(t.handoff()))
    else:
        dom=DOM(html);assert len(dom.ids)==len(set(dom.ids))
        assert '/industries/technology?lens=how' in dom.links
        assert '/industries/technology?lens=uses' in dom.links
        assert '/industries/technology?lens=work' in dom.links
        assert '<form method="post"' not in html.lower() and '/flora/sales/capture' not in html


@pytest.mark.parametrize('query',['?workspace=other','?provider=lloyds','?lens=how&lens=uses','?lens=%00','/../../blueprint-import/history','/private','/handoff?promote=yes'])
def test_unregistered_selectors_or_paths_are_rejected(web,query):
    assert not public_request_target(t.BASE+query)
    assert web(t.BASE+query)[0] in (403,404)


@pytest.mark.parametrize('query',['?lens=unknown','?segment=private','?relationship=private'])
def test_unknown_registered_selection_values_cannot_read_arbitrary_data(web,query):
    assert web(t.BASE+query)[0]==404


def test_public_journey_does_not_read_or_mutate_pipeline(actor,sales_web,monkeypatch):
    from cios.applications.flora import sales_pipeline as sales
    assert sales.list_opportunities(headers=actor[3])==[]
    def forbidden(*args,**kwargs):raise AssertionError('Technology read attempted private Pipeline access')
    monkeypatch.setattr(sales,'list_opportunities',forbidden)
    for path in [t.BASE,t.BASE+'?lens=uses',t.BASE+'?lens=work',t.BASE+'/providers',t.BASE+'/evidence',t.BASE+'/handoff']:
        status,html,_=sales_web(path,authenticated=False);assert status==200
        assert 'synthetic-workspace' not in html and 'synthetic-user' not in html
    with pytest.raises((ValueError,PermissionError)):sales.create_opportunity('lloyds','theme-1',headers=actor[3])


def test_markup_escapes_source_prose_and_rejects_non_https_links():
    html=v.prose('<script>alert(1)</script> [x](javascript:alert(1)) [safe](https://example.com/)')
    assert '<script>' not in html and 'href=\'javascript:' not in html and 'https://example.com/' in html


def test_existing_sector_journeys_and_catalogue_entry_are_preserved(web):
    assert '/industries/technology' in web('/industries')[1]
    assert '/industries/technology' in web('/flora/industries')[1]
    for path in ('/industries/banking','/industries/aviation','/enterprises/lloyds','/enterprises/easyjet','/macro'):
        assert web(path)[0]==200


def test_every_provider_drills_to_its_own_profile_and_explicit_identity_gap(web):
    d,_=t.load()
    for row in d['providers']:
        status,html=web(t.BASE+'/providers?provider='+row['key'])
        assert status==200 and 'Canonical identity unbound' in html
        assert row['label'].replace('&','&amp;') in html
    assert '15 views in this filter' in web(t.BASE+'/providers?segment=applications')[1]


def test_head_content_types_match_the_new_finite_http_views():
    from cios.applications.flora.web.app import _content_type_for_path
    for suffix in ('','/providers','/evidence','/models','/timeline'):
        assert _content_type_for_path(t.BASE+suffix)=='text/html; charset=utf-8'
    assert _content_type_for_path(t.BASE+'/handoff')=='application/json'
    assert not public_request_target(t.BASE+'/providers/private')


def test_new_views_cannot_be_posted_to_import_or_create_opportunities(sales_web):
    for path in (t.BASE,t.BASE+'/handoff',t.BASE+'/providers'):
        status,_,_=sales_web(path,{'promote':'yes','enterprise_id':'BK-ENT-001'},authenticated=False)
        assert status in (403,404)


def test_all_displayed_relationships_have_source_urls_and_own_temporal_scope():
    data,_=t.load()
    for row in data['relationships']:
        assert row['source_links'] and row['publication_date']!=row['retrieval_date']
        html=v.source_detail(row)
        assert (row['publication_date'] or 'Unknown') in html
        assert (row['event_date'] or 'Unknown') in html
        assert 'unestablished' in html and 'not accepted Evidence' in html
        assert row['source_block'] in html
