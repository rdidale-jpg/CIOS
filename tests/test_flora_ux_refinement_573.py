"""Issue #573 display contract, commercial depth, source boundaries and access."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from html import unescape
import json
import subprocess

import pytest
from cios.applications.flora.research_intelligence import technology as t
from cios.applications.flora.research_intelligence import technology_experience as x
from cios.applications.flora.research_intelligence import technology_commercial as c
from cios.applications.flora.research_intelligence import technology_commercial_views as v
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_research_intelligence import web


class DOM(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.nodes=[]; self.feed(text)
    def handle_starttag(self, tag, attrs): self.nodes.append((tag, dict(attrs)))


def test_industry_has_eight_labelled_native_embedded_regions_without_intermediate_overlay():
    html=x.scene(); dom=DOM(html)
    regions=[a for tag,a in dom.nodes if a.get('data-district')]
    assert len(regions)==8
    assert {a['aria-label'] for a in regions}=={v[0] for v in x.DISTRICTS.values()}
    assert all('/district?district=' in a['href'] for a in regions)
    assert any(tag=='img' and a.get('src')==x.ASSET_BASE+'artwork' for tag,a in dom.nodes)
    assert '<iframe' not in html and 'Explore by name</summary>' not in html
    assert 'commercial-district-nav' in html  # Mobile label key, not a collapsed legend.


@pytest.mark.parametrize('suffix', ['/participants', '/district?district=ai', '/district?district=channels&sort=uk_revenue&direction=desc',
                                  '/enterprise?enterprise=nvidia&district=ai', '/pipeline?scope=nvidia'])
def test_finite_public_sprint_routes_and_links(web,suffix):
    status,html=web(x.BASE+suffix); assert status==200
    for tag,a in DOM(html).nodes:
        if tag=='a' and a.get('href','').startswith(x.BASE):
            assert public_request_target(a['href'].split('#')[0]), a['href']


@pytest.mark.parametrize('query', ['enterprise=private-record', 'scope=private-workspace', 'sort=private', 'direction=random',
                                 'enterprise=../../security', 'search='+('a'*81)])
def test_unknown_private_selectors_and_sort_inputs_fail_closed(web,query):
    assert web(x.BASE+'/participants?'+query)[0]==404


@pytest.mark.parametrize('query', ['enterprise=nvidia&enterprise=equinix','workspace=private','promote=true'])
def test_ambiguous_or_privileged_selector_keys_remain_forbidden(web,query):
    assert web(x.BASE+'/participants?'+query)[0]==403


def test_comparison_preserves_the_80_view_population_and_all_unbound_identities():
    rows=c.participants(); foundation,_=t.load()
    assert {r['key'] for r in rows}=={r['key'] for r in foundation['providers']}
    assert len(rows)==80 and all(r['canonical_enterprise_id'] is None for r in rows)
    assert all(r['identity_status']=='unbound' for r in rows)
    # A view association is not a rewritten foundation membership.
    assert any(r['key']=='equinix' for r in c.participants('cloud'))
    assert next(r for r in foundation['providers'] if r['key']=='equinix')['memberships']==['infrastructure']


def test_uk_cells_are_blank_instead_of_nvidia_group_values_or_status_prose(web):
    _,html=web(x.BASE+'/district?district=ai')
    row=html.split('<tr data-participant="nvidia">')[1].split('</tr>')[0]
    assert '<td data-metric="uk_revenue"></td>' in row and '<td data-metric="uk_workforce"></td>' in row
    assert '$215' not in row and '42,000' not in row
    for text in ('Unknown','not known','identity unbound','missing','unproven'):
        assert text not in row


def test_computacenter_uk_values_have_matching_periods_and_different_measure_bases():
    d=c.load();r=d['participants']['computacenter']
    assert r['uk_revenue']['value']==1419200000 and r['uk_workforce']['value']==4357
    assert r['uk_revenue']['period']==r['uk_workforce']['period']=='FY2025'
    assert 'not gross invoiced' in r['uk_revenue']['basis']
    assert 'Average monthly' in r['uk_workforce']['basis']
    html=v.metric_cell(r['uk_revenue'],d)
    assert '1,419,200,000 GBP' in html and 'FY2025' in html and 'UK segment' in html
    assert d['sources']['CC-FY25']['url'] in html


def test_numeric_sort_is_numeric_and_blanks_stay_last_in_both_directions(monkeypatch):
    d=c.load();sample=d['participants']['computacenter']['uk_revenue']
    for key,value in [('microsoft',9000000),('nvidia',100000000)]:
        d['participants'][key]['uk_revenue']={**sample,'value':value}
    monkeypatch.setattr(c,'load',lambda:d)
    asc=c.participants(sort='uk_revenue',direction='asc');desc=c.participants(sort='uk_revenue',direction='desc')
    assert [r['key'] for r in asc[:3]]==['microsoft','nvidia','computacenter']
    assert [r['key'] for r in desc[:3]]==['computacenter','nvidia','microsoft']
    assert asc[-1]['uk_revenue'] is desc[-1]['uk_revenue'] is None


def test_estimate_has_highlighted_label_and_secondary_basis_range_date_and_source():
    d=c.load();metric=deepcopy(d['participants']['computacenter']['uk_revenue'])
    metric.update(kind='estimate',basis='Test-only transparent calculation from a dated source.',range=[1000000000,1800000000])
    html=v.metric_cell(metric,d)
    assert 'class="commercial-est">EST' in html and 'Range:' in html and metric['basis'] in html
    assert 'FY2025' in html and d['sources']['CC-FY25']['url'] in html
    assert not metric['canonical_accepted']
    # Production presentation data does not invent a UK estimate to fill a cell.
    assert all(r.get(k) is None or r[k]['kind']=='reported' for r in d['participants'].values() for k in ('uk_revenue','uk_workforce'))


@pytest.mark.parametrize('mutation', ['basis','range','source','scope','accepted','nan','currency'])
def test_metrics_cannot_be_unsupported_estimates_or_cross_scope_values(mutation):
    d=c.load();metric=deepcopy(d['participants']['computacenter']['uk_revenue'])
    if mutation=='basis':metric.update(kind='estimate',basis='',range=[0,2000000000])
    if mutation=='range':metric.update(kind='estimate',basis='Example calculation',range=None)
    if mutation=='source':metric['source_ids']=['invented']
    if mutation=='scope':metric['scope']='Global group'
    if mutation=='accepted':metric['canonical_accepted']=True
    if mutation=='nan':metric['value']=float('nan')
    if mutation=='currency':
        d['participants']['computacenter']['uk_revenue']['unit']='USD'
        with pytest.raises(ValueError):c.validate(d)
        return
    with pytest.raises(ValueError):c.validate_metric(metric,d['sources'],uk=True)


def test_nvidia_profile_is_commercially_substantial_and_not_a_large_diagram(web):
    _,html=web(x.BASE+'/enterprise?enterprise=nvidia&district=ai')
    for section in ('Financial context','Strategic priorities','Commercial pressures','Customers, partners & suppliers','UK programmes & activity','Where sales work may emerge'):
        assert section in unescape(html)
    for name in ('Nebius','University of Bristol','CoreWeave','Microsoft','Nscale','TSMC','Samsung','SK hynix','Micron'):
        assert name in html
    assert '<img' not in html and '<svg' not in html
    assert 'Global group · FY2026 ended 25 January 2026 · USD' in html
    assert '$215.938bn' in html and '$120.067bn' in html and '71.1%' in html and 'c. 42,000' in html
    assert 'Q2 FY2027 ended 26 July 2026' in html and '$96.221bn' in html
    assert html.count('class="commercial-hypothesis">Hypothesis')==3
    assert 'scope=nvidia' in html and '/flora/sales/capture' not in html


def test_nvidia_relationships_preserve_roles_scope_anonymity_and_event_status():
    p=c.load()['profiles']['nvidia']; relationships=p['relationships']
    assert next(r for r in relationships if r['name']=='Nebius')['role']=='Deployment operator'
    assert 'direct purchase' in next(r for r in relationships if r['name']=='Nebius')['boundary']
    assert all(r['category']=='Suppliers' for r in relationships if r['name'] in ('TSMC','Samsung','SK hynix','Micron'))
    assert 'does not name' in p['pressures'][1]['boundary']
    assert p['programmes'][0]['status']=='Announced commitment'
    assert 'Not UK revenue' in p['programmes'][0]['boundary']
    assert all(r['kind']=='hypothesis' and r['source_ids'] and r['qualification'] and r['countercase'] for r in p['opportunities'])


def test_source_projection_reuses_existing_contracts_and_never_claims_acceptance():
    p=c.source_projection('NV-10K')
    assert p['source_segment']['content_hash']==sha256(p['source_segment']['content'].encode()).hexdigest()
    assert p['candidate_claim']['status']=='withheld'
    assert not p['eligible_for_import'] and p['canonical_evidence_id'] is p['canonical_enterprise_id'] is None
    assert p['rights']=='unestablished' and p['publisher_original_sha256'] is None


def test_changed_presentation_source_cannot_silently_relabel_a_verified_value(tmp_path,monkeypatch):
    file=tmp_path/'Commercial-Views.json';file.write_bytes(c.DATA.read_bytes()+b' ')
    monkeypatch.setattr(c,'DATA',file);monkeypatch.setattr(c.technology,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='changed'):c.load()


def test_source_and_inference_validation_fail_closed():
    d=c.load();d['sources']['NV-10K']['url']='javascript:alert(1)'
    with pytest.raises(ValueError):c.validate(d)
    d=c.load();d['profiles']['nvidia']['opportunities'][0]['kind']='observation'
    with pytest.raises(ValueError):c.validate(d)


def test_search_and_source_labels_are_escaped_without_markup_execution(web):
    _,html=web(x.BASE+'/participants?search=%3Cscript%3E')
    assert 'value="&lt;script&gt;"' in html and '<script>' not in html
    d=c.load();metric=deepcopy(d['participants']['computacenter']['uk_revenue']);metric['basis']='<img src=x onerror=alert(1)>'
    assert '<img' not in v.metric_cell(metric,d)


def test_refined_views_never_read_or_mutate_private_pipeline_or_promote(web,monkeypatch):
    from cios.applications.flora import sales_pipeline
    from cios.applications.flora.blueprint_import import views
    def forbidden(*args,**kwargs):raise AssertionError('Private owner called')
    for name in ('list_opportunities','create_opportunity'):monkeypatch.setattr(sales_pipeline,name,forbidden)
    monkeypatch.setattr(views,'approve_and_promote',forbidden)
    for suffix in ('/participants','/enterprise?enterprise=nvidia','/pipeline?scope=nvidia'):
        assert web(x.BASE+suffix)[0]==200
    assert all(r['enterprise']!='NVIDIA' for r in x.DEMO_ROWS)
    assert t.handoff()['accepted']==t.handoff()['eligible']==0


def test_protected_data_access_and_sector_owners_remain_byte_identical():
    paths=['cios/applications/flora/sales_pipeline.py','cios/applications/flora/security.py','cios/applications/flora/access.py',
           'cios/applications/flora/blueprint_import/views.py','cios/applications/flora/research_intelligence/registry.py',
           'cios/applications/flora/research_intelligence/technology.py','cios/applications/flora/research_intelligence/unified_views.py']
    paths += [str(p.relative_to(t.ROOT)) for p in t.ASSETS.glob('*.json')]
    for path in paths:
        assert subprocess.check_output(['git','show','854a783:'+path],cwd=t.ROOT)==(t.ROOT/path).read_bytes(),path


def test_participant_config_preserves_text_without_script_breakout(monkeypatch):
    foundation,blocks=t.load();foundation=deepcopy(foundation)
    target=next(r for r in foundation['providers'] if r['key']=='microsoft')
    target['label']='A </script><img src=x> & B'
    monkeypatch.setattr(t,'load',lambda:(foundation,blocks))
    html=x.render(x.BASE,{})
    config=html.split('id="experience-config">')[1].split('</script>')[0]
    assert '</script>' not in config and '<img' not in config
    assert json.loads(config)['participants']['microsoft']=='A </script><img src=x> & B'


def test_no_javascript_pipeline_fallback_keeps_empty_values_blank():
    html=x.baseline_rows('industry')
    assert 'Not set' not in html and 'Unassigned' not in html
    connectivity=html.split('Connectivity upgrade')[1].split('</tr>')[0]
    assert '£0' not in connectivity


def test_every_comparison_participant_opens_its_own_public_profile(web):
    foundation,_=t.load()
    for row in foundation['providers']:
        status,html=web(x.BASE+'/enterprise?enterprise='+row['key'])
        assert status==200,row['key']
        assert '<h1>'+__import__('html').escape(row['label'])+'</h1>' in html
