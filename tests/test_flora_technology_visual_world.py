"""Presentation reset preserves research ownership and makes imagery navigable."""
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
import xml.etree.ElementTree as ET
import pytest
from cios.applications.flora.research_intelligence import technology as t,technology_scene as scene,technology_views as views
from tests.test_flora_research_intelligence import web


class Elements(HTMLParser):
    def __init__(self,html):
        super().__init__();self.rows=[];self.feed(html)
    def handle_starttag(self,tag,attrs):self.rows.append((tag,dict(attrs)))


@pytest.mark.parametrize('lens',['how','uses','work'])
def test_primary_lenses_are_navigable_svg_scenes_with_no_card_grid(web,lens):
    status,html=web(t.BASE+'?lens='+lens);assert status==200
    dom=Elements(html)
    scenes=[a for tag,a in dom.rows if tag=='svg' and a.get('data-scene-contract')==scene.CONTRACT]
    assert len(scenes)==2 and {a['data-scene-mode'] for a in scenes}=={lens}
    classes=[a.get('class','').split() for _,a in dom.rows]
    assert not any(set(c)&{'tech-nodes','tech-grid','tech-theme','tech-chain','tech-programme-list'} for c in classes)
    assert not any('world-detail' in c for c in classes)
    assert 'Partial research' in html and 'No visual position encodes provider importance' in html


@pytest.mark.parametrize('compact',[False,True])
def test_every_district_is_a_native_link_with_an_accessible_name(compact):
    d,_=t.load();root=ET.fromstring(scene.svg(d,'how','','','','',compact));ns={'s':'http://www.w3.org/2000/svg'}
    nodes=[a for a in root.findall('.//s:a',ns) if 'scene-role' in a.get('class','').split()]
    assert {a.get('data-role') for a in nodes}==set(t.SEGMENTS)
    for a in nodes:
        assert a.get('data-truth-class')=='conceptual' and a.get('aria-label')
        assert 'segment='+a.get('data-role')+'#landscape' in a.get('href')
        assert a.find('s:title',ns) is not None
    ids=[n.get('id') for n in root.iter() if n.get('id')];assert len(ids)==len(set(ids))


@pytest.mark.parametrize('role',list(t.SEGMENTS))
def test_role_selection_keeps_the_scene_and_uses_existing_provider_navigation(web,role):
    status,html=web(t.BASE+'?lens=how&segment='+role);assert status==200
    dom=Elements(html);assert any(a.get('class','').startswith('world-detail tech-inspector') for _,a in dom.rows)
    assert any(a.get('data-role')==role and a.get('aria-current')=='true' for _,a in dom.rows)
    assert '/industries/technology/providers?' in html and 'conceptual' in html.lower()


def test_all_six_hypotheses_are_seams_and_retain_evidence_alternatives_and_questions(web):
    d,_=t.load()
    for r in d['themes']:
        _,html=web(t.BASE+'?lens=work&theme='+r['key']);dom=Elements(html)
        hotspots=[a for tag,a in dom.rows if tag=='a' and a.get('data-theme')]
        assert len(hotspots)==12 and {a['data-truth-class'] for a in hotspots}=={'hypothesis'}
        assert any(a.get('id')==r['key'] and tag=='aside' for tag,a in dom.rows)
        assert 'Unqualified research hypothesis' in html and views.inline(r['alternative']) in html and views.inline(r['qualification']) in html
        assert r['relationship_keys'] and all('relationship='+k in html for k in r['relationship_keys'])
        assert 'No Pipeline record created' in html


def test_all_programme_ribbons_retain_exact_record_scope_and_evidence(web):
    d,_=t.load()
    for r in d['relationships']:
        status,html=web(t.BASE+'?lens=uses&relationship='+r['key']);assert status==200
        assert 'data-truth-class="attributed_report"' in html and views.inline(r['customer']) in html
        assert views.inline(r['offering']) in html and views.inline(r['participants']) in html
        assert views.inline(r['boundary']) in html and r['source_block'] in html
        assert (r['publication_date'] or 'Unknown') in html and 'unestablished' in html


def test_provider_drill_retains_scene_and_partial_identity_instead_of_creating_an_enterprise(web):
    _,html=web(t.BASE+'/providers?provider=microsoft');dom=Elements(html)
    assert any(a.get('id')=='provider' and tag=='aside' for tag,a in dom.rows)
    assert any(a.get('class')=='world-focus-provider' for _,a in dom.rows)
    assert 'Canonical identity unbound' in html and 'partial profile' in html


@pytest.mark.parametrize('selection',[{'lens':'private'},{'selected':'private'},{'theme':'accepted-opportunity'},{'relationship':'private-record'},{'provider':'canonical-new'}])
def test_scene_rejects_unknown_selection_instead_of_falling_back(selection):
    d,_=t.load()
    with pytest.raises(ValueError):scene.scene(d,**selection)


def test_new_theme_selector_remains_finite_and_cannot_request_private_state(web):
    assert web(t.BASE+'?lens=work&theme=private-record')[0]==404
    assert web(t.BASE+'?lens=work&theme=theme-1&workspace=private')[0]==403
    assert web(t.BASE+'?lens=work&theme=theme-1&theme=theme-2')[0]==403


def test_research_data_and_all_acceptance_navigation_owners_are_byte_preserved():
    paths=['cios/applications/flora/research_intelligence/technology.py','cios/applications/flora/research_intelligence/registry.py','cios/applications/flora/research_intelligence/source_import.py','cios/applications/flora/sales_pipeline.py','cios/applications/flora/blueprint_import/views.py']
    paths += [str(p.relative_to(t.ROOT)) for p in t.ASSETS.glob('*.json')]
    for path in paths:assert subprocess.check_output(['git','show','20637fefcbdb799e405b06d3eb5ca7abffc435d0:'+path],cwd=t.ROOT)==(t.ROOT/path).read_bytes(),path
    h=t.handoff();assert h['accepted']==h['eligible']==0 and not h['canonical_mutation'] and not h['pipeline_mutation']


def test_svg_escapes_research_text_without_interpreting_it_as_markup():
    d,_=t.load();d=deepcopy(d);d['relationships'][4]['customer']='<script>alert(1)</script>'
    svg=scene.svg(d,'uses','','','','',False)
    ET.fromstring(svg);assert '<script>' not in svg and '&lt;script&gt;' in svg
