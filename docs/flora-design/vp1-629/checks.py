#!/usr/bin/env python3
"""Reproducible VP-1 artifact/semantics/ownership checks; not a second engine."""
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.parse import urlsplit, unquote

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=HERE/'prototype'
BASE='8a53777d1dec359f56b66e533d512c0a86881939'
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('vp1_design_build',HERE/'build.py')
build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
STATES=json.loads((HERE/'Prototype-States.json').read_text())
ART=json.loads((HERE/'Artwork-Provenance.json').read_text())

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.children=[];self.stack=[];self.inside=False;self.links=[];self.ids=set();self.tags=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.tags.append((tag,a))
        if 'id'in a:self.ids.add(a['id'])
        if 'href'in a:self.links.append(a['href'])
        if tag=='body':self.inside=True;return
        if not self.inside:return
        if not self.stack:self.children.append((tag,a))
        if tag not in {'img','input','meta','link','br','hr','source'}:self.stack.append(tag)
    def handle_endtag(self,tag):
        if tag=='body':self.inside=False;return
        if self.inside and tag in self.stack:self.stack=self.stack[:len(self.stack)-1-self.stack[::-1].index(tag)]

class VP1(unittest.TestCase):
    def test_no_existing_repository_file_or_runtime_owner_changed(self):
        changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
        new=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
        for name in changed+new:self.assertTrue(name.startswith('docs/flora-design/vp1-629/')or name=='.github/workflows/flora-vp1-design.yml',name)
        self.assertEqual(subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT).returncode,0)

    def test_original_seven_historical_masters_have_exact_hashes(self):
        original=json.loads((ROOT/'cios/applications/flora/visual_stream_assets/artwork.json').read_text())
        self.assertEqual(len(original['scenes']),7)
        for r in original['scenes'].values():
            body=subprocess.check_output(['git','show',original['design_commit']+':'+r['original_path']],cwd=ROOT)
            self.assertEqual(hashlib.sha256(body).hexdigest(),r['original_sha256'])
            self.assertEqual(len(body),r['original_bytes'])

    def test_twenty_one_runtime_variants_and_seven_delivery_references(self):
        original=json.loads((ROOT/'cios/applications/flora/visual_stream_assets/artwork.json').read_text());count=0
        for key,r in original['scenes'].items():
            for v in r['variants']:
                body=(ROOT/'cios/applications/flora/visual_stream_assets'/v['file']).read_bytes();self.assertEqual(hashlib.sha256(body).hexdigest(),v['sha256']);count+=1
            self.assertEqual((OUT/'assets'/('original-'+key+'.webp')).read_bytes(),(ROOT/'cios/applications/flora/visual_stream_assets'/r['variants'][1]['file']).read_bytes())
        self.assertEqual(count,21)

    def test_eight_unique_generated_masters_and_delivery_hashes(self):
        hashes=set()
        for r in ART['artworks']:
            body=(HERE/r['master']).read_bytes();self.assertEqual(hashlib.sha256(body).hexdigest(),r['master_sha256']);hashes.add(r['master_sha256'])
            if r['key']!='uk-skyline':self.assertEqual(r['dimensions'],[1024,1536]);self.assertIn('original',r)
            for v in r['variants']:
                body=(OUT/v['file']).read_bytes();self.assertEqual(hashlib.sha256(body).hexdigest(),v['sha256']);self.assertEqual(len(body),v['bytes'])
        self.assertEqual(len(hashes),8)

    def test_exactly_three_regions_every_product_composition(self):
        for name in [r['file']for r in STATES['states']]+STATES['concepts']+['index.html']:
            p=Page((OUT/name).read_text());self.assertEqual(sum(t=='h1' for t,a in p.tags),1);self.assertEqual([(tag,a.get('data-region'))for tag,a in p.children],[('header','top'),('aside','left'),('main','main')],name)

    def test_all_native_local_links_and_fragments_exist(self):
        for path in OUT.glob('*.html'):
            for link in Page(path.read_text()).links:
                url=urlsplit(link)
                if url.scheme:
                    self.assertEqual(url.scheme,'https');self.assertIn(url.hostname,{'www.ons.gov.uk','www.fca.org.uk','www.gov.uk','www.bankofengland.co.uk','www.lloydsbankinggroup.com','www.nationalarchives.gov.uk'});continue
                target=(OUT/(unquote(url.path)or path.name)).resolve();self.assertTrue(target.is_relative_to(OUT.resolve()));self.assertTrue(target.is_file(),str(target))
                if url.fragment:self.assertIn(url.fragment,Page(target.read_text()).ids)

    def test_no_script_form_api_private_route_or_owner_metadata(self):
        prohibited=['canonical_status','canonical_acceptance','source_ids','workspace_id','tenant_id','seller_id','/research/gaps','EAI1-','sec.gov/Archives','Research gaps','Completeness','Next action','What should']
        for r in STATES['states']:
            text=(OUT/r['file']).read_text();p=Page(text)
            self.assertFalse(any(t in {'script','form','iframe'}for t,a in p.tags))
            for word in prohibited:self.assertNotIn(word,text)
            for t,a in p.tags:self.assertFalse(any(k.startswith('on')for k in a))

    def test_actual_available_streams_and_scoped_selection(self):
        for r in STATES['states']:
            p=Page((OUT/r['file']).read_text());streams=[a for t,a in p.tags if t=='a'and a.get('id','').startswith('stream-')]
            expected=build.SCOPES[r['scope']][1];self.assertEqual(len(streams),len(expected))
            for a in streams:
                self.assertIn(r['scope']+'-',a['href']);self.assertIn(r['focus'],a['href'])if r['focus']!='overview'else None
            self.assertEqual(sum('aria-current'in a for a in streams),1)

    def test_future_concepts_are_inert_and_explicit(self):
        news=(OUT/'concept-news.html').read_text();tools=(OUT/'concept-tools.html').read_text()
        for text in (news,tools):self.assertIn('Future concept · not available',text);self.assertNotIn('class="streams"',text)
        self.assertIn('Source published 1 May 2026',news);self.assertIn('not a current news edition',news)
        self.assertIn('<fieldset disabled>',tools);self.assertNotIn('<button',tools);self.assertNotIn('<form',tools)
        self.assertIn('no model has been run',tools)

    def test_permitted_source_owners_match_base_and_recorded_pins(self):
        ledger=json.loads((HERE/'Content-Lineage.json').read_text())
        self.assertFalse(ledger['canonical_mutation']);self.assertFalse(ledger['pending_branch_content_incorporated'])
        for r in ledger['source_owners']:
            body=(ROOT/r['path']).read_bytes();self.assertEqual(hashlib.sha256(body).hexdigest(),r['sha256']);self.assertEqual(body,subprocess.check_output(['git','show',BASE+':'+r['path']],cwd=ROOT))

    def test_six_types_and_uncertainty_not_laundered(self):
        all_text=''.join((OUT/r['file']).read_text()for r in STATES['states'])
        for label in ['Reported','Calculated','Estimated','Working assumption','FLORA Insight','Hypothesis']:self.assertIn(label,all_text)
        b,total,share,assumption,estimate=build.uk_values()
        self.assertEqual(assumption.semantic_type,'assumed');self.assertEqual(estimate.semantic_type,'estimated');self.assertIn('assumed',estimate.dependency_types)
        self.assertIn('£211–214bn',estimate.text);self.assertIn('not a statistical confidence interval',estimate.caveats[0])
        self.assertEqual(share.semantic_type,'calculated');self.assertIn('broader', (OUT/'uk-landscape.html').read_text().replace('includes more than','broader'))

    def test_financial_values_match_existing_public_definitions(self):
        _,rows=build.statements();self.assertEqual(str(rows['LBG-Q326-DEPOSITS'].value),'502.8');self.assertEqual(str(rows['LBG-Q326-PROFIT'].value),'6.6');self.assertEqual(str(rows['LBG-AR25-DEPOSITS'].value),'496.5')
        text=(OUT/'lloyds-inside-economics.html').read_text()
        for item in ['0–600bn','nine-month flow','30 September 2026','31 December 2025','Management target','not achieved performance','not an investment allocation','No organic-flow claim']:self.assertIn(item,text)
        self.assertIn('id="deposit-reference"',text)

    def test_hypothesis_has_existing_response_countercase_and_falsifier(self):
        text=(OUT/'lloyds-inside-technology.html').read_text()
        for item in ['Hypothesis','Counter-test','Existing teams or incumbents','no adoption deficit or external work','not achieved net benefit']:self.assertIn(item,text)
        self.assertNotIn('£100m opportunity',text)

    def test_licence_attribution_retained_on_demand(self):
        self.assertIn('Crown copyright',(OUT/'uk-landscape.html').read_text())
        self.assertIn('Contains Financial Conduct Authority information',(OUT/'lloyds-inside-agenda.html').read_text())
        self.assertIn('open-government-licence/version/3/',(OUT/'lloyds-inside-agenda.html').read_text())

    def test_watermarks_are_nine_unique_decorative_line_treatments(self):
        files=list((OUT/'assets').glob('watermark-*.svg'));self.assertEqual(len(files),9);self.assertEqual(len({p.read_bytes()for p in files}),9)
        css=(OUT/'assets/design.css').read_text();self.assertIn('@media(forced-colors:active)',css);self.assertIn('opacity:.045',css)

    def test_rebuild_is_byte_reproducible(self):
        paths=list(OUT.glob('*.html'))+[HERE/'Content-Lineage.json',HERE/'Prototype-States.json']
        before={p:p.read_bytes()for p in paths};build.main();self.assertEqual(before,{p:p.read_bytes()for p in paths})

if __name__=='__main__':unittest.main(verbosity=2)
