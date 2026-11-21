"""Read existing public owners into a design-only source-reference index.

No research collection, canonical acceptance, private lookup or domain write.
"""
from pathlib import Path
from hashlib import sha256
import json
from cios.applications.flora import visual_v2
from cios.applications.flora.research_intelligence import model, macro_intelligence, buying_evidence

ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]

def digest(path):return sha256((ROOT/path).read_bytes()).hexdigest()
def build():
 b=model.load_assessment();m=macro_intelligence.load_context();t=buying_evidence.load();basis=visual_v2.basis();refs={}
 owner='enterprise-knowledge/banking/research-model/Assessment-Overlay.json';sources={s['id']:s for s in b['sources']}
 wanted=['UK-RATE-NOV26','UK-PRA-REPORT27','UK-FCA-REPORT27','UK-CAPITAL','UK-VALUE','UK-CTP','LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-A2030-CIR','LBG-A2030-PLATFORMS','LBG-A2030-DATA','LBG-A2030-INVESTMENT','LBG-ENVOY-CONTROLS','LBG-ENVOY-GOOGLE','LBG-BRAND26-TIMING']
 for key in wanted:
  c=next(c for c in b['claims']if c['id']==key)
  refs[key]={'owner_path':owner,'owner_sha256':digest(owner),'locator':'claims[id='+key+']','scope':c.get('entity_scope',c['asset_id']),
   'subject_id':c['asset_id'],'statement':c['statement'],'original_kind':c['kind'],'original_verification':c['verification'],
   'authority':b['authority'],'canonical_acceptance_asserted':False,'reporting_period':c['reporting_period'],'review_cutoff':b['assessed_at'],
   'sources':[{'id':s['id'],'title':s['title'],'url':s['url'],'published_at':s.get('publication_date'),'retrieved_at':s.get('retrieved_at'),
     'extent':s.get('content_kind','citation_only'),'rights':s.get('rights',s.get('limitation','Original source terms and citation limits remain; no new redistribution rights.')),
     'limitation':s.get('limitation','Primary verification not established for this historical citation.'),'original_bytes_sha256':s.get('primary_content_sha256')}for s in [sources[i]for i in c['source_ids']]]}
 for factor in visual_v2.FACTORS:
  row=visual_v2.insight(factor);key='UK-'+factor.upper()
  owner=('cios/applications/flora/visual_v2_assets/economy.json'if factor=='economic'else 'enterprise-knowledge/macro/research-model/Macro-Context-v1.json')
  refs[key]={'owner_path':owner,'owner_sha256':digest(owner),'locator':'visual_v2.insight('+factor+') / '+str(row['lineage']),
   'scope':'UK; no automatic industry or enterprise applicability','subject_id':'GB','statement':row['text'],'original_kind':row['lineage'].get('kind','reported_GDP_volume_change'),
   'original_verification':'existing_public_presentation_extract','authority':'candidate_intelligence','canonical_acceptance_asserted':False,
   'reporting_period':basis['growth']['period']if factor=='economic'else ' | '.join(s.get('reporting_period') or 'Unknown; owner establishes no reporting period'for s in row['sources']),'review_cutoff':('2026-11-12'if factor=='economic'else m['as_of']),
   'sources':[{'id':s['id'],'title':s['title'],'url':s['url'],'published_at':s.get('publication_date'),'retrieved_at':s.get('retrieved_at'),
     'extent':'reviewed excerpt; not full original archive','rights':s.get('rights','Existing public short excerpt and link; no full article redistribution assumed.'),'limitation':row['details'],'original_bytes_sha256':s.get('primary_content_sha256')}for s in row['sources']]}
 # Rejected applicability remains inspectable, without promoting a foreign rule to a UK obligation.
 source=next(s for s in m['sources']if s['id']=='GM-CSRD-FR')
 owner='enterprise-knowledge/macro/research-model/Macro-Context-v1.json'
 refs['GM-CSRD-FR']={'owner_path':owner,'owner_sha256':digest(owner),'locator':'sources[id=GM-CSRD-FR]',
  'scope':'France national implementation guidance; Lloyds exact-entity applicability not established','subject_id':'FR',
  'statement':'Existing French guidance says new thresholds require French transposition. It does not determine an obligation for a Lloyds entity.',
  'original_kind':'national_implementation_notice','original_verification':'reviewed_excerpt_candidate','authority':'candidate_intelligence','canonical_acceptance_asserted':False,
  'reporting_period':source['reporting_period'],'review_cutoff':m['as_of'],
  'sources':[{'id':source['id'],'title':source['title'],'url':source['url'],'published_at':source.get('publication_date'),
   'retrieved_at':source.get('retrieved_at'),'extent':source.get('retrieval_extent'),'rights':'Existing public bounded excerpt and citation only; no new redistribution right.',
   'limitation':'No verified legal-entity assessment; an EU subsidiary could require separate review. Publication date unknown.','original_bytes_sha256':None}]}
 key='UK-GVA-2024';owner='cios/applications/flora/visual_v2_assets/economy.json'
 refs[key]={'owner_path':owner,'owner_sha256':digest(owner),'locator':'published_total_billion / sources[ONS-BB-2026] page 2; districts[*].weight_per_thousand / sources[ONS-GDP-2026-09] GVA2 appendix page index 27',
  'scope':'UK SIC 2007 sections; 2024 current basic prices','subject_id':'GB','statement':'Published UK GVA total GBP2623bn; rounded display GBP2.62tn. Finance & insurance share 8.1%; not Banking-only market size.',
  'original_kind':'nominal_GVA_statistical_extract','original_verification':'existing_public_presentation_extract','authority':basis['authority'],'canonical_acceptance_asserted':False,
  'reporting_period':'2024','review_cutoff':'2026-11-12','sources':[{'id':s['id'],'title':s['title'],'url':s['url'],'published_at':s.get('publication_date'),'retrieved_at':s.get('retrieved_at'),'source_role':('total GVA and valuation basis'if s['id']=='ONS-BB-2026'else '2024 section weights, GVA2 appendix; GDP growth separate'if s['id']=='ONS-GDP-2026-09'else 'classification context only'),'original_locator':s.get('locator'),'extent':'reviewed ONS extract','rights':'Crown copyright / Open Government Licence; original source limits retained','limitation':'GVA not GDP at market prices, sector sales, profit pool or bank revenue. Rounded section shares sum 100.2%; no normalisation.','original_bytes_sha256':None}for s in basis['sources']]}
 ts=next(s for s in t['sources']if s['id']=='BTI-TSB-TRANSFER')
 for fact in t['facts']:
  if fact['enterprise_slug']!='santander-uk':continue
  owner='enterprise-knowledge/technology/research-model/Buying-Trigger-Pilot.json'
  refs[fact['id']]={'owner_path':owner,'owner_sha256':digest(owner),'locator':'facts[id='+fact['id']+']','scope':'Santander UK / TSB separately identified parties; contracting identity unverified',
   'subject_id':'public_reference:BK-ENT-005','statement':fact['statement'],'original_kind':fact['kind'],'original_verification':'source_supported_candidate',
   'authority':t['authority'],'canonical_acceptance_asserted':False,'reporting_period':fact.get('effective_period')or'Unknown effective period; source publication and review are separate','review_cutoff':'2026-11-13',
   'sources':[{'id':ts['id'],'title':ts['title'],'url':ts['url'],'published_at':ts['publication_date'],'retrieved_at':ts.get('retrieved_at'),
    'extent':'bounded reviewed excerpt, not full source archive','rights':ts['rights'],'limitation':fact['interpretation_limit'],'original_bytes_sha256':None}]}
 data={'status':'SI-1 design reference index; not a research/Observation store','base':'fe66516c15726dc45de147ede2674c9172f8cac6','references':refs,
 'scope_limits':['All pilot references are existing public candidate/presentation records; none is promoted to accepted Evidence or Observation by SI-1.','No new source retrieval or private data read.','A report disclosure is evidence of the reported statement, not independently verified business effectiveness.'],
 'identity_conflicts':[{'runtime_public_reference':'BK-ENT-005','repository_twin_reference':'BK-ENT-007','repository_path':'enterprise-knowledge/banking/enterprises/santander-uk/Santander-UK-Enterprise-Twin.md','action':'No name-based identity join. Repository-reported acquisition completion not adopted as verified runtime fact.'}]}
 (D/'Evidence-References.json').write_text(json.dumps(data,indent=2)+'\n')
 print(str(len(refs))+' existing reference bindings; no new evidence or canonical writes.')
if __name__=='__main__':build()
