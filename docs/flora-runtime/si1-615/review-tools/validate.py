"""Design artifact acceptance checks. Not a substitute for application security CI."""
from pathlib import Path
from hashlib import sha256
import copy,json,subprocess,unittest
from lxml import html
from jsonschema import Draft202012Validator,FormatChecker,ValidationError
from referencing import Registry,Resource
ROOT=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parents[1]
BASE='fe66516c15726dc45de147ede2674c9172f8cac6'
refdoc=json.loads((D/'Evidence-References.json').read_text());refs=refdoc['references'];proof=json.loads((D/'Proof-Cases.json').read_text());agendas=json.loads((D/'AgendaViews.json').read_text())
schema=json.loads((D/'IssueView.schema.json').read_text());aschema=json.loads((D/'AgendaView.schema.json').read_text())
registry=Registry().with_resource(schema['$id'],Resource.from_contents(schema));validator=Draft202012Validator(schema,format_checker=FormatChecker());av=Draft202012Validator(aschema,registry=registry,format_checker=FormatChecker())
class DesignAcceptance(unittest.TestCase):
 def test_proposed_schemas_and_three_agendas(self):
  Draft202012Validator.check_schema(schema);Draft202012Validator.check_schema(aschema)
  for a in agendas:av.validate(a)
  self.assertEqual([len(a['issues'])for a in agendas],[2,2,3])
 def test_source_owners_unchanged(self):
  for r in refs.values():
   self.assertEqual(sha256((ROOT/r['owner_path']).read_bytes()).hexdigest(),r['owner_sha256'])
   self.assertFalse(r['canonical_acceptance_asserted'])
   self.assertTrue(r['sources']);self.assertTrue(r['reporting_period'])
   for s in r['sources']:self.assertTrue(s['rights']);self.assertTrue(s['url'].startswith('https://'))
  for pin in json.loads((D/'Authority-Index.json').read_text())['references']:
   self.assertEqual(sha256((ROOT/pin['path']).read_bytes()).hexdigest(),pin['sha256'])
 def test_dates_and_statistics_binding(self):
  self.assertNotEqual(refs['UK-TECHNOLOGICAL']['reporting_period'],refs['UK-TECHNOLOGICAL']['review_cutoff'])
  self.assertIn('2025',refs['UK-TECHNOLOGICAL']['reporting_period'])
  self.assertIn('ONS-BB-2026',refs['UK-GVA-2024']['locator']);self.assertIn('GVA2',refs['UK-GVA-2024']['locator'])
  fr=next(n for n in proof['negative_cases']if n['id']=='fr-law-lloyds');self.assertIsNone(fr['source_date'])
  self.assertIsNone(refs['GM-CSRD-FR']['sources'][0]['published_at'])
 def test_all_references_resolve(self):
  for a in agendas:
   for item in a['issues']:
    for r in item['source_refs']:self.assertIn(r,refs)
    for c in item['challenges']:
     for r in c['source_refs']:self.assertIn(r,refs)
  for n in proof['negative_cases']:
   for r in n.get('source_refs',[])+n.get('excluded_source_refs',[]):self.assertIn(r,refs)
 def test_traces_do_not_launder_unknown_edges(self):
  self.assertEqual(len(proof['traces']),7)
  self.assertEqual(sum(bool(t['conditional_transmission_path'])for t in proof['traces']),3)
  for trace in proof['traces']:
   self.assertEqual([e['status']for e in trace['admission_path']],['source_supported','interpretation','interpretation','recommendation'])
   for edge in trace['conditional_transmission_path']:
    self.assertFalse(edge['eligible_agenda_support']);self.assertTrue(edge['challenge'])
    for r in edge['support_refs']:self.assertIn(r,refs)
 def test_preserved_gaps_and_identity(self):
  self.assertEqual(proof['preserved_lloyds_gaps'],['FIN-01','FIN-02','ORG-01','OPS-01','REL-01','REG-01','ORG-02','INF-01','COM-01'])
  n=proof['negative_cases'][0];self.assertNotEqual(n['runtime_reference'],n['repository_twin_reference_not_joined']);self.assertFalse(n['historical_tiers_changed'])
 def test_pain_and_strengths_have_no_false_promotions(self):
  for a in agendas:
   for i in a['issues']:
    self.assertEqual(i['pain']['classification'],'no_pain_claim');self.assertEqual(i['analysis']['swot']['weaknesses'],[])
    if i['view_ref']!='design:lloyds-ai':self.assertEqual(i['analysis']['swot']['strengths'],[])
 def test_schema_rejects_unsupported_commercial_mutations(self):
  item=agendas[-1]['issues'][0]
  mutations=[('budget',lambda x:x['commercial'].__setitem__('budget',100000000)),('TCV',lambda x:x['commercial'].__setitem__('contract_value',100000000)),('Pipeline',lambda x:x['commercial'].__setitem__('pipeline_handoff',True)),('named buyer',lambda x:x['leadership'].__setitem__('named_leader','Invented buyer')),('pain',lambda x:x['pain'].__setitem__('classification','demonstrated')),('canonical',lambda x:x['qualification'].__setitem__('new_canonical_objects',True)),('qualified pressure',lambda x:x['qualification'].__setitem__('qualified_pressure_refs',['invented'])),('score',lambda x:x.__setitem__('priority_score',99)),('early window',lambda x:x['decision'].__setitem__('influence','Early'))]
  for label,mutate in mutations:
   with self.subTest(label=label):
    x=copy.deepcopy(item);mutate(x)
    with self.assertRaises(ValidationError):validator.validate(x)
 def test_artwork_and_runtime_boundary(self):
  manifest=json.loads((ROOT/'cios/applications/flora/visual_stream_assets/artwork.json').read_text())
  self.assertEqual(len(manifest['scenes']),7)
  for row in manifest['scenes'].values():
   original=subprocess.check_output(['git','show',manifest['design_commit']+':'+row['original_path']],cwd=ROOT)
   self.assertEqual(sha256(original).hexdigest(),row['original_sha256'])
   for v in row['variants']:self.assertEqual(sha256((ROOT/'cios/applications/flora/visual_stream_assets'/v['file']).read_bytes()).hexdigest(),v['sha256'])
  paths=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines()
  allowed=lambda p:p.startswith('docs/flora-runtime/si1-615/')or p=='docs/architecture/flora/SI-001-Strategic-Intelligence-Analysis-Model-v1.0.md'
  self.assertTrue(all(allowed(p)for p in paths),paths)
 def test_html_has_unique_ids_and_shared_agendas(self):
  for file in (D/'prototype').glob('*.html'):
   doc=html.fromstring(file.read_text());ids=doc.xpath('//@id');self.assertEqual(len(ids),len(set(ids)),file.name)
  for scope in ['uk','banking','lloyds']:
   agenda_html=[]
   for file in (D/'prototype').glob(scope+'-*.html'):
    node=html.fromstring(file.read_text()).xpath('//*[@data-agenda-scope]')[0]
    agenda_html.append(html.tostring(node))
   self.assertEqual(len(set(agenda_html)),1,scope)
 def test_original_source_urls_are_preserved(self):
  expected={s['url']for r in refs.values()for s in r['sources']}
  for file in (D/'prototype').glob('*.html'):
   doc=html.fromstring(file.read_text())
   anchors=doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," source-binding ")]//a/@href')
   self.assertTrue(anchors,file.name)
   for href in anchors:self.assertIn(href,expected,(file.name,href))
   for href in doc.xpath('//a/@href'):self.assertNotIn('onrender.comhttps',href)
 def test_analytical_method_and_inventory(self):
  d=(D/'Analytical-Design.md').read_text()
  for name in ['Political','Economic','Social','Technological','Legal','Environmental','Rivalry','New entrants','Substitutes','Supplier power','Buyer power']:self.assertIn(name,d)
  index=json.loads((D/'Discovery-Index.json').read_text())
  for r in index['code']+index['available_test_modules']:self.assertTrue((ROOT/r['path']).is_file(),r['path'])
if __name__=='__main__':unittest.main(verbosity=2)
