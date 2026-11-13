"""Presentation unification with unchanged source, permission and write owners."""
from concurrent.futures import ThreadPoolExecutor
from html import escape, unescape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import time

import pytest

from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_sales_pipeline import actor, web
from tests.test_flora_offers_v1 import pilot, draft, approved, add_actor
from cios.applications.flora import design_system as ds, visual_v2 as v, offers
from cios.applications.flora.research_intelligence import technology_experience as x, technology_commercial as c
from cios.applications.flora.storage import data_path


class DOM(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.nodes=[]; self.feed(html)
    def handle_starttag(self, tag, attrs): self.nodes.append((tag,dict(attrs)))


def body(html): return html.split('<main',1)[1].split('>',1)[1].split('</main>',1)[0]


@pytest.mark.parametrize('path',['/','/flora','/flora/'])
def test_candidate_canonical_home_uses_approved_world_without_private_or_old_modules(web,path):
    status,html,_=web(path,authenticated=False)
    assert status==200 and html.count('data-sic=')==20
    assert html.count('data-research=')==3 and '£2.62tn' in html
    assert all(s not in body(html) for s in ['My Commercial Focus','What’s Changing','Recommended Sales Plays','More from','Explore industries'])
    assert '2024 · current basic prices' in html
    assert '/flora/sales/pipeline' in html  # Same protected owner, never a demo replacement.


@pytest.mark.parametrize('path,query',[(x.BASE,{}),(x.BASE+'/district',{'district':'frontier'}),
    (x.BASE+'/enterprise',{'enterprise':'nvidia'}),(x.BASE+'/operating-model',{}),
    (v.BASE,{}),(v.BASE+'/pestle',{'factor':['technological']})])
def test_shared_header_and_one_optional_source_location(path,query):
    html=v.render(path,query) if path.startswith(v.BASE) else x.render(path,query)
    dom=DOM(html)
    assert sum(t=='nav' and a.get('aria-label')=='Primary product navigation' for t,a in dom.nodes)==1
    assert html.count('Sources & method</summary>')==1
    assert all(s not in body(html) for s in ['More from Flora','commercial-district-nav','commercial-jumps','Inspect evidence'])
    assert 'FLORA' in html and '/design-system/assets/styles' in html
    assert sum(t=='h1' for t,a in dom.nodes)==1


def test_participant_table_has_six_sortable_columns_and_only_company_row_navigation():
    html=x.render(x.BASE+'/participants',{})
    table=body(html).split('<tbody>',1)[1].split('</tbody>',1)[0]
    assert table.count('<tr ')==80
    for row in table.split('<tr ')[1:]:
        assert row.count('<a ')==1
        assert 'commercial-source' not in row and '<details' not in row
    assert html.count('data-comparison-sort=')==6
    assert '£1.419bn' in html and '4,357' in html  # Existing scoped source metrics retained.
    assert 'Average monthly' in html and 'not gross invoiced' in html
    row=table.split('data-participant="nvidia"',1)[1].split('</tr>',1)[0]
    assert '<td data-metric="uk_revenue"></td>' in row


def test_estimates_keep_visible_est_and_on_demand_range_basis_scope_sources():
    from copy import deepcopy
    from cios.applications.flora.research_intelligence import technology_commercial_views as cv
    data=c.load(); metric=deepcopy(data['participants']['computacenter']['uk_revenue'])
    metric.update(kind='estimate',basis='SYNTHETIC defensible test calculation',range=[1000000000,1800000000])
    @ds.view_scope
    def render():
        primary=cv.metric_cell(metric,data)
        return ds.header()+ '<main>'+primary+'</main>'
    html=render()
    assert 'commercial-est">EST' in body(html)
    assert 'Range:' in html and metric['basis'] in html and 'FY2025' in html
    assert data['sources']['CC-FY25']['url'] in html
    assert not metric['canonical_accepted']


def test_nvidia_material_financial_relationship_programme_and_buyer_facts_preserved():
    profile=c.load()['profiles']['nvidia'];html=x.render(x.BASE+'/enterprise',{'enterprise':'nvidia','district':'frontier'})
    main=body(html)
    assert [a for t,a in DOM(main).nodes if t=='h2'] and main.count('<h2>')==3
    assert all(name in main for name in ['At a glance','Commercial ecosystem','Potential sales plays'])
    for key in ['strategy','pressures','relationships','programmes','opportunities']:
        for row in profile[key]:
            for field in ('title','name','text','role','scope','period','value','buyer'):
                if row.get(field): assert escape(row[field]) in main, (key,field)
            for field in ('boundary','qualification','countercase','basis'):
                if row.get(field): assert escape(row[field]) in html, (key,field)
    for value in ['$215.938bn','$120.067bn','71.1%','$96.221bn','c. 42,000']:
        assert value in main
    assert 'Global group · FY2026 ended 25 January 2026 · USD' in main
    assert main.count('Potential buyer:')==3 and main.count('commercial-hypothesis">Hypothesis')==3
    assert '/flora/sales/capture' not in html
    assert 'scope=nvidia' in html and '/flora/sales/pipeline' in html


def test_technology_and_pestle_use_exact_approved_art_and_economic_basis():
    manifest=json.loads((Path(__file__).resolve().parents[1]/'docs/flora-runtime/design-system-585/Protected-Owners.json').read_text())
    for path,digest in manifest['approved_assets'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
    assert ds.section_scale('J').find('6.6%')>=0
    assert '8.1%' in ds.section_scale('K') and '3.6%' in ds.section_scale('H')
    assert v.basis()['published_section_weight_sum']==1002
    assert len(v.FACTORS)==6 and len(v.basis()['districts'])==20


def test_conceptual_model_uses_existing_questions_and_native_image_reveal_only():
    for area,question in [('facilities','funded requirement'),('interconnection','owns the decision')]:
        html=x.render(x.BASE+'/operating-model',{'area':area});main=body(html)
        assert 'ds-model-insight' in main and question in main
        assert html.index('id="operating-area"')<html.index('</section>',html.index('class="ds-model ds-image-surface"'))
        assert 'not a disclosed organisation chart' in html and 'demand and budget not established' in html
        assert 'macro=cyber' in html and 'scope=equinix' in html
        assert '/flora/sales/capture' not in html


def test_aviation_sales_context_keeps_its_existing_industry_identity():
    from cios.applications.flora.banking_explorer import _crumb
    from cios.applications.flora.research_intelligence.registry import enterprise_reference
    @ds.view_scope
    def render():
        _crumb(enterprise_reference('easyjet'))
        return ds.header()
    html=render()
    assert '/industries/aviation' in html and '/enterprises/easyjet' in html
    assert '/industries/banking' not in html


def test_root_scope_resets_on_success_failure_and_concurrent_requests():
    @ds.view_scope
    def scoped(value,fail=False):
        ds.source_note('<p>'+value+'</p>');time.sleep(.01)
        if fail:raise ValueError('SYNTHETIC render failure')
        return ds.header()
    with ThreadPoolExecutor(max_workers=4) as pool: result=list(pool.map(scoped,['seller-one','seller-two','public-three','public-four']))
    for i,html in enumerate(result):
        assert ['seller-one','seller-two','public-three','public-four'][i] in html
        assert sum(s in html for s in ['seller-one','seller-two','public-three','public-four'])==1
    with pytest.raises(ValueError):scoped('PRIVATE-failed',True)
    assert not ds.active() and 'PRIVATE-failed' not in ds.header()


def test_caught_nested_failure_cannot_publish_partially_collected_private_notes():
    @ds.view_scope
    def inner():
        ds.source_note('PRIVATE failed nested content');ds.context_link('/private-failed','PRIVATE link');raise ValueError('SYNTHETIC')
    @ds.view_scope
    def outer():
        ds.source_note('Public source')
        try:inner()
        except ValueError:pass
        return ds.header()
    html=outer();assert 'Public source' in html and 'PRIVATE' not in html


def test_private_offer_sources_preserve_every_assessment_dimension_and_lineage(pilot):
    approved(pilot)
    from cios.applications.flora import offers_views
    results=offers.discover('account','lloyds','2026-11-13',headers=pilot['seller'])
    before=offers._path().read_bytes()
    html=offers_views.render('/flora/offers/discover',{'mode':['account'],'selected':['lloyds']},pilot['seller'])
    assert results and html.count('Sources & method</summary>')==1
    for result in results:
        for key in ['why_account','why_offer','why_now','entry_play','next_validation_action','capability_fit','credibility','relationship_access','trigger_evaluation','delivery_risk','offer_evidence','assessment_id','source_cut_off','policy_version']:
            assert escape(result[key]) in html,key
        for key in ['unknowns','contradictions','competitive_alternatives','what_not_to_claim','limitations']:
            for value in result[key]:assert escape(value) in html,key
        for ref in result['evidence_lineage']:
            assert escape(ref['statement']) in html
            for source in ref['source_refs']:assert escape(source['url'],quote=True) in html and escape(source['title']) in html
    assert '<div class="source-list">' not in body(html)
    assert offers._path().read_bytes()==before
    assert not data_path('sales_pipeline','opportunities.json').exists()


def test_private_notes_are_escaped_and_never_cached_across_sellers_or_failed_authority(pilot):
    from cios.applications.flora import offers_views
    record=draft(pilot,name='PRIVATE <script>fixture</script>',evidence='PRIVATE <img src=x onerror=bad>')
    own=offers_views.render('/flora/offers/edit',{'offer':[record['id']]},pilot['seller'])
    assert '<script>fixture</script>' not in own and 'PRIVATE &lt;script&gt;' in own
    for headers in [pilot['outsider'],pilot['foreign'],None,{'X-User':'pilot-seller','X-Roles':'cios_owner'}]:
        try: other=offers_views.render('/flora/offers',{},headers)
        except PermissionError:other=''
        assert 'PRIVATE &lt;script&gt;' not in other
    assert not ds.active()
    public=v.render(v.BASE,{})
    assert 'PRIVATE' not in public and 'Illustrative UK employer' not in public


def test_signed_out_private_routes_and_real_forms_keep_access_csrf_and_no_store(web):
    for path in ['/flora/offers','/flora/sales/pipeline']:
        assert web(path,authenticated=False)[0]!=200
        status,html,_=web(path);assert status==200
        assert 'no-store' in web.last_headers['Cache-Control']
        assert 'name="csrf"' in html or "name='csrf'" in html
    status,html,_=web('/flora/sales/new?enterprise=lloyds')
    assert status==200 and "action='/flora/sales/create'" in html
    assert 'Discovered' in html and 'unknown value' in html
    assert not data_path('sales_pipeline','opportunities.json').exists()


def test_protected_intelligence_security_permissions_matching_and_pipeline_bytes():
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'docs/flora-runtime/design-system-585/Protected-Owners.json').read_text())
    for path,digest in manifest['unchanged_files'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
    assert manifest['base_sha']=='19ab36d241dbca2099ffb9b5d519c68c493a914a'


def test_shared_text_and_focus_tokens_have_accessible_contrast():
    css=(ds.ASSETS/'design.css').read_text()
    colors={key:re.search('--'+key+r':(#[0-9a-f]{6})',css).group(1) for key in ['paper','ink','muted','focus']}
    def luminance(color):
        rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)]
        linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
    def ratio(a,b):
        x,y=sorted([luminance(a),luminance(b)])
        return (y+.05)/(x+.05)
    assert ratio(colors['ink'],colors['paper'])>=7
    assert ratio(colors['muted'],colors['paper'])>=4.5
    assert ratio(colors['focus'],colors['paper'])>=3


@pytest.mark.parametrize('name',['../offers.py','/etc/passwd','private','design.css'])
def test_shared_assets_are_finite_local_files(name):
    with pytest.raises(ValueError):ds.asset(name)
