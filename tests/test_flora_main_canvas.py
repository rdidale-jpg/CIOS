"""Whole-region executive interaction; current rendering and immutable authority."""
import ast
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import parse_qs,urlsplit
import pytest
from cios.applications.flora import lloyds_gold as g,visual_streams as v
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_living_enterprise_preview import http
ROOT=Path(__file__).resolve().parents[1]
BASE='cc8d93fe7183fdd86fd4c4e81907a2a0764227a5'
pytestmark=pytest.mark.real_security_boundary

class Links(HTMLParser):
 def __init__(self,html):
  super().__init__();self.links=[];self.stack=[];self.nested=False;self.feed(html)
 def handle_starttag(self,tag,attrs):
  data=dict(attrs)
  if tag=='a':
   self.nested|=any(t=='a'for t,_ in self.stack)
   if any(d.get('data-canvas')=='visual'for _,d in self.stack):self.links.append((data,tuple(t for t,_ in self.stack)))
  if tag not in {'img','br','meta','link','input','hr','path','polygon','rect','meter'}:self.stack.append((tag,data))
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==tag:self.stack=self.stack[:i];break

def query(stream,focus,detail=''):return {'stream':[stream],'focus':[focus],'detail':[detail]}
def main(html):return html.split('<main ',1)[1].split('</main>',1)[0]
CASES=[(stream,focus,detail)for stream,rows in g.REGIONS.items()for focus,_ in rows for detail in ('',*g.DETAILS[focus])]+[('inside','people',d)for d in ('',*g.DETAILS['people'])]

@pytest.mark.parametrize('stream,focus,detail',CASES)
def test_all_default_executive_navigation_is_semantic_region_or_inspection(stream,focus,detail):
 html=v.render(g.CANONICAL,query(stream,focus,detail));dom=Links(html)
 assert not dom.nested
 for attrs,ancestors in dom.links:
  target=attrs.get('href','')
  if target.startswith('/'):
   assert 'data-canvas-region'in attrs or attrs.get('data-canvas-exception')=='inspection',(stream,focus,detail,attrs)
   assert not {'li','td','th'}&set(ancestors),'Navigation must not be a tiny label in a data row'
   assert public_request_target(target.split('#')[0]),target
  else:assert detail=='sources','Only optional source inspection contains external citations'
 assert 'Reading mode'not in html and '<details'not in main(html)


def test_primary_business_compositions_wrap_customer_and_economic_context():
 html=main(v.render(g.CANONICAL,{}))
 for title,customer,activity,driver,key in g.twin.DIVISIONS:
  link=next(a for a,_ in Links(v.render(g.CANONICAL,{})).links if a.get('aria-label')==title)
  assert link['data-canvas-region']=='business'
  assert 'focus='+key in link['href']
  start=html.index('aria-label="'+title.replace('&','&amp;')+'"');body=html[start:html.index('</a>',start)]
  assert customer in body and driver.replace('&','&amp;')in body
 assert 'Reporting businesses · not financial shares'in html


def test_financial_flows_and_bars_are_full_native_targets_without_new_measurements():
 html=v.render(g.CANONICAL,query('landscape','economics'));dom=Links(html)
 for name in ('Funding','Lending & income','Costs & impairment','Capital & returns'):
  assert any(a.get('aria-label')==name and a.get('data-canvas-region')=='money'for a,_ in dom.links)
 assert 'ce-capital' in html and '£6.6bn' in html
 funding=v.render(g.CANONICAL,query('landscape','economics','funding'))
 assert sum(a.get('data-canvas-region')=='financial-chart'for a,_ in Links(funding).links)==2
 assert all(value in funding for value in ('£502.8bn','£496.5bn','£6.3bn'))
 assert 'not an organic inflow' in funding.lower() and 'not adjusted for consolidation' in funding
 assert all(x not in html+funding for x in ('£11.084bn','3.21%','£477.5bn','.pdf'))


def test_operating_value_system_layers_have_distinct_existing_destinations():
 html=v.render(g.CANONICAL,query('inside','operations'))
 for key in g.JOURNEYS:
  assert ('detail=service#' if key=='service' else 'detail=journey-'+key) in html
 assert 'Connected enterprise operating model' in html and 'ce-connections' in html
 assert 'canvas-operating-band' not in html
 html=v.render(g.CANONICAL,query('inside','operations','journey-credit'))
 for label in ('Business / value stream','Durable capabilities','Organisation / accountable role','Applications / data','Technology / infrastructure','Suppliers / contracts'):
  assert any(a.get('aria-label')==label for a,_ in Links(html).links)
 assert 'no verified application, role or supplier dependency is inferred'in html


def test_capability_organisation_and_technology_regions_preserve_boundaries():
 html=v.render(g.CANONICAL,query('inside','capabilities'))
 assert 'Connected enterprise operating model' in html and 'not reporting lines or verified system dependencies' in html
 org=v.render(g.CANONICAL,query('inside','people','structure'))
 assert 'Financial reporting businesses'in org
 assert 'Financial reporting businesses' in org and 'spending authority' in org
 apps=v.render(g.CANONICAL,query('inside','applications'))
 assert any(a.get('aria-label')=='Envoy'and a.get('data-canvas-region')=='technology'for a,_ in Links(apps).links)
 assert 'installed estate inventory'in apps


def test_specialist_evidence_entry_uses_visible_inspection_not_visual_region_container():
 html=v.render(g.CANONICAL,query('inside','applications','envoy'))
 assert '<p class="gold-inspect"><a class="canvas-inspection-link"'in html
 assert 'data-canvas-exception="inspection"'in html
 assert 'Evidence &amp; dates'in html


def test_disclosure_and_goal_rails_do_not_claim_progress_or_event_timing():
 html=v.render(g.CANONICAL,query('inside','programmes'))
 assert 'First displayed source date · not a delivery milestone'in html
 assert 'Transformation disclosures by publication date'in html
 goals=v.render(g.CANONICAL,query('forces','strategy','goals'))
 for key,*_ in g.OBJECTIVES:assert 'detail=objective-'+key in goals
 assert 'no measured progress-to-target chart'in goals.lower()
 assert 'FY2025 reported / 2026 expectation'in goals and '2030 management ambition'in goals


@pytest.mark.parametrize('quadrant',['strength','weakness','opportunity','threat'])
def test_full_quadrant_and_theme_links_are_distinct_and_share_existing_evidence(quadrant):
 html=v.render(g.CANONICAL,query('forces','analysis'))
 dom=Links(html)
 assert sum(a.get('data-canvas-region')=='quadrant'for a,_ in dom.links)==4
 assert sum(a.get('data-canvas-region')=='theme'for a,_ in dom.links)==8
 target=next(a['href']for a,_ in dom.links if a.get('aria-label')==quadrant.title())
 q=parse_qs(urlsplit(target).query);assert q['detail']==['quadrant-'+quadrant]
 assert quadrant.title()+' themes'in v.render(g.CANONICAL,q)
 assert not Links(v.render(g.CANONICAL,q)).nested


def test_related_customer_and_funding_views_remain_in_canvas_and_old_urls_still_work(http):
 dom=Links(v.render(g.CANONICAL,{}))
 for title,detail in [('Customer operations','service'),('Funding comparison','comparison')]:
  target=next(a['href']for a,_ in dom.links if a.get('aria-label')==title)
  assert 'detail='+detail in target and 'focus='in target
  assert http(target.split('#')[0])[0]==200
 for old in ('?agenda=service-recovery','?agenda=funding-base'):
  assert http(g.CANONICAL+old)[0]==200


@pytest.mark.parametrize('flag',['withdrawn','owner_only','revoked','stale','contradictory','superseded'])
def test_source_withdrawal_removes_dependent_regions_values_and_accessible_labels(monkeypatch,flag):
 data=deepcopy(v.current_data(v.Context('lloyds','landscape')))
 next(s for s in data['sources']if s['id']=='PR-LBG-Q326')[flag]=True
 monkeypatch.setattr(v,'current_data',lambda ctx:data)
 html=main(v.render(g.CANONICAL,query('landscape','economics','funding')))
 for token in ('£502.8bn','£6.3bn','£6.6bn','value="502.8"','Compare customer deposits at 30 September 2026'):assert token not in html
 assert '£496.5bn'in html
 swot=v.render(g.CANONICAL,query('forces','analysis'))
 assert 'detail=theme-4'not in swot


def test_source_ownership_financials_iam_and_original_left_are_unchanged():
 before=ast.parse(subprocess.check_output(['git','show',BASE+':cios/applications/flora/lloyds_gold.py'],cwd=ROOT))
 after=ast.parse((ROOT/'cios/applications/flora/lloyds_gold.py').read_text())
 functions=lambda tree:{n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,ast.FunctionDef)}
 a,b=functions(before),functions(after)
 # Cross-perspective href selection is intentionally evolved by v3.
 for name in ('facts_for','reported','interpretation','scene','resolve','render','stylesheet'):
  assert a[name]==b[name],name
 for name in ('security_store.py','security_web.py','public_routes.py','visual_streams.py','research_intelligence/source_import.py','financial_intelligence/candidate_analytics.py'):
  path='cios/applications/flora/'+name
  assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
