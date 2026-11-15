"""Deterministic offline consolidation of immutable candidate inputs; never an importer."""
from pathlib import Path
import hashlib,json,subprocess
from collections import Counter
from urllib.parse import urlsplit,urlunsplit
ROOT=Path(__file__).resolve().parents[4]; D=ROOT/'docs/flora-runtime/ric1'
PINS={'RIE1':'c57ed9728473563b5535db36d5bfbe5e96a8c572','RIE2':'71d34bb50cff4a7e99cf49f53a0ee5c8724c3df5','SI1':'85317167b4001dc027216c1c4e2faf058f0631a3'}
DIRS={'RIE1':'docs/flora-runtime/rie1-617/','RIE2':'docs/flora-runtime/rie2-619/','SI1':'docs/flora-runtime/si1-615/'}
inputs={}
def raw(pack,name):
 p=DIRS[pack]+name;b=subprocess.check_output(['git','show',PINS[pack]+':'+p],cwd=ROOT);inputs[pack+':'+name]={'package':pack,'commit':PINS[pack],'path':p,'repository_content_sha256':hashlib.sha256(b).hexdigest()};return b
def read(pack,name):return json.loads(raw(pack,name))
def write(name,value):(D/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def urlkey(url):
 p=urlsplit(url);return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path,p.query,''))
def main():
 sources=[];aliases={};byurl={}
 for pack in ['RIE1','RIE2']:
  for s in read(pack,'Source-Ledger.json'):
   key=urlkey(s['url'])
   if key not in byurl:
    doc={'id':'DOC-'+hashlib.sha256(key.encode()).hexdigest()[:16],'original_url':key,'inspections':[],'canonical_acceptance':False,'original_bytes_sha256':None,'rights_acceptance':'not granted; bounded facts/citation proposal only','document_reference_count':1};sources.append(doc);byurl[key]=doc
   doc=byurl[key];doc['inspections'].append({'package':pack,'source_id':s['id'],'record':s});aliases[s['id']]=doc['id']
 write('Source-Ledger.json',sources);write('Source-Aliases.json',aliases)
 # Original bundles are retained losslessly. They are not all atomic memory.
 claims=[]
 for pack,name in [('RIE1','Facts.json'),('RIE2','Claims.json')]:
  for c in read(pack,name):
   claims.append({'id':pack+':'+c['id'],'package':pack,'original_id':c['id'],'record':c,'document_refs':sorted({aliases[s]for s in c['source_refs']}),'canonical_acceptance':False,'owner_mapping':None,'status':'retained candidate; not a canonical Observation'})
 write('Claim-Ledger.json',claims)
 r1g=read('RIE1','Gap-Disposition.json');r2g=read('RIE2','Gap-Dispositions.json')
 write('Gap-Register.json',{'original_RIE1':r1g,'RIE2_enrichment':r2g,'acceptance_effect':'none; all original owner statuses/tier/qualification unchanged','all_twenty_sectors':read('RIE1','Sector-Research.json')})
 # Preserve deep-analysis record sets not exhaustively expressed by Facts/Claims.
 supplementary=[]
 for pack,name in [('RIE1','Lloyds-Financial-Reconciliation.json'),('RIE1','Statistical-Extraction.json'),('RIE2','Financial-Reconciliation.json'),('RIE2','Customer-Outcomes.json'),('RIE2','Operating-Model.json'),('RIE2','Banking-Comparability.json')]:
  data=read(pack,name)
  for key,value in data.items():
   supplementary.append({'id':pack+':'+name+'#/'+key,'input':pack+':'+name,'pointer':'/'+key,'record':value,'acceptance_class':'B','reason':'Preserved reconciliation/context record; individual definitions/locators and rights must be verified before an atomic Evidence/Observation proposal. No wholesale table ingestion.','duplicate_policy':'Where this repeats a Claim-Ledger metric, that claim is the sole scalar proposal; this record is reconciliation context, not another finding count.','canonical_acceptance':False})
 write('Reconciliation-Context.json',supplementary)
 issues=[]
 old=read('RIE1','Agenda-Candidates.json');new={x['id']:x for x in read('RIE2','Leadership-Agenda.json')}
 for x in old:
  versions=[{'package':'RIE1','commit':PINS['RIE1'],'record':x}]
  if x['id']in new:versions.append({'package':'RIE2','commit':PINS['RIE2'],'record':new[x['id']]})
  issues.append({'id':x['id'],'current_version':versions[-1]['package'],'versions':versions,'acceptance_class':'C','authority':'SI-1 Option A read-only synthesis design; not an accepted runtime owner','refresh_warning':'UK/Banking candidates retain RIE1 cutoff; no RIE2 refresh claimed'if len(versions)==1 else'RIE2 refines the same issue identity; RIE1 history retained','canonical_acceptance':False,'material_pressure_qualification':'not executed','pipeline_writes':0})
 write('Strategic-Agendas.json',issues)
 relationships=[]
 for pack,records in [('RIE1',read('RIE1','Relationships.json')),('RIE2',read('RIE2','Relationships.json')['new_edges'])]:
  for r in records:relationships.append({'id':pack+':'+r['id'],'record':r,'document_refs':[aliases[s]for s in r['source_refs']],'acceptance_class':'B','endpoint_mapping':None,'canonical_acceptance':False,'restriction':'A supported endpoint does not prove an edge; role, date, legal perimeter, directness and both authorised canonical endpoint mappings require review.'})
 write('Relationship-Proposals.json',relationships)
 mechanisms=read('RIE2','Relationships.json')['conditional_transmission']
 write('Conditional-Mechanisms.json',mechanisms)
 # Repeated negatives share one control identity with both provenance records.
 negatives={}
 for pack,name in [('RIE1','Negative-Cases.json'),('RIE2','Rejected-and-Contradicted.json')]:
  for n in read(pack,name):
   k=n['id'];row=negatives.setdefault(k,{'id':k,'acceptance_class':'D','versions':[],'scope':'Rejected inference only; supporting source facts are not rejected.','canonical_acceptance':False});row['versions'].append({'package':pack,'record':n})
 write('Contradictions-and-Negatives.json',list(negatives.values()))
 # Explicitly prohibited uses, not a claim that all publisher rights are prohibited.
 exclusions=[{'id':'USE-COMPOUND-PROMOTION','acceptance_class':'E','proposed_use':'Promote compound research prose as an atomic Observation','reason':'Existing blueprint_import.atomicity/EI-012 contract forbids non-atomic Observation promotion.'},{'id':'USE-FULL-SOURCE-REDISTRIBUTION','acceptance_class':'E','proposed_use':'Redistribute full publisher files under the bounded fact/citation permission asserted in these packs','reason':'No full-source redistribution grant exists in the supplied packages; do not infer it from public access.'},{'id':'USE-PRIVATE-NAME-JOIN','acceptance_class':'E','proposed_use':'Use public names to write into a private employer/Twin without authorised identity mapping','reason':'Existing verified workspace/resource scope and explicit canonical mapping authority required.'}]
 exclusions.append({'id':'USE-UNAPPROVED-VISUAL-PUBLISHER','acceptance_class':'E','proposed_use':'Pass SEC or ONS URLs directly into the current visual research source adapter without an authority decision','reason':'research_intelligence.source_import.official_url currently permits neither SEC nor ONS. Evidence review eligibility does not authorise bypassing that publisher policy.'})
 write('Excluded-Uses.json',exclusions)
 # Narrow freshly inspected slice. Excerpt bytes are ours; original source bytes remain unavailable.
 extracts=[
 {'id':'EX-H126','source_id':'R2-LBG-H126','retrieval_reference':'turn339283view0','locator':'SEC rendered lines2544,2549–2551,2555; Note3 printed42','text':'Half-year to 30 June 2026 | Retail£m | Commercial Banking£m | Insurance, Pensions and Investments£m | Other£m | Total£m\nUnderlying operating lease depreciation 1 | (835) | (6) | – | – | (841)\nUnderlying income, net of underlying operating lease depreciation | 5,710 | 2,897 | 747 | 393 | 9,747\nUnderlying operating costs | (2,872) | (1,409) | (494) | (101) | (4,876)\nUnderlying profit before tax | 2,256 | 1,425 | 245 | 289 | 4,215','limitations':'Selected table rows, normalised rendered separators; underlying pre-tax IFRS8 reporting divisions, not standalone legal entity/statutory P&Ls. Costs include lower severance and exclude separate remediation; not fully recurring/normalised costs.'},
 {'id':'EX-FCA','source_id':'R2-FCA-H126','retrieval_reference':'turn544033view2','locator':'All-product Open table, Lloyds Bank PLC row, rendered680; method title2026H1','text':'Lloyds Bank PLC | LLOYDS BANKING GROUP PLC | no | 2026-01-01 to 2026-06-30 | 115,687 | 31 | 2,679 | 339 | 26 | 118,762','limitations':'Firm all-product received complaints total, not Group, unique persons, closed cohort, cause, financial loss or customer demand.'},
 {'id':'EX-ONS','source_id':'ONS-GDP-SEP26','retrieval_reference':'turn339283view2','locator':'PDF index29, GVA3, rendered715–716','text':'Section A-T A B-E B C D E F G-T G H I J K L M N O P Q R S T\n2024 weights 1000 7 124 7 87 19 12 57 812 94 36 28 66 81 142 87 54 51 59 84 15 15 1','limitations':'SIC2007 rounded GVA basic-price weight per thousand, not banking-only revenue, turnover, GDP market-price share or TAM. Disjoint weights sum1002 through rounding; no renormalisation.'}]
 for e in extracts:
  e.update({'document_id':aliases[e['source_id']],'retrieved_at':'2026-11-15','content_kind':'reviewed_web_excerpt','primary_content_sha256':None,'retrieval_method':'approved_web_research_tool','rights':'Bounded factual table citation for owner review; publisher rights retained. No original-file or ingestion/redistribution permission asserted.','canonical_acceptance':False})
  e['excerpt_content_sha256']=hashlib.sha256(e['text'].encode()).hexdigest()
 write('Reviewed-Excerpts.json',extracts)
 selected={'R2-FIN-H12026-0-NET_INCOME':('EX-H126','Lloyds Banking Group Retail underlying net income was GBP5710m in H1 2026.'),'R2-FIN-H12026-0-OPERATING_COSTS':('EX-H126','Lloyds Banking Group Retail underlying operating costs were GBP2872m in H1 2026.'),'R2-FIN-H12026-0-LEASE_DEPRECIATION':('EX-H126','Lloyds Banking Group Retail underlying lease depreciation was GBP835m in H1 2026.'),'R2-FIN-H12026-0-UNDERLYING_PROFIT':('EX-H126','Lloyds Banking Group Retail underlying pre-tax profit was GBP2256m in H1 2026.'),'R2-FIN-H12026-4-NET_INCOME':('EX-H126','Lloyds Banking Group underlying net income was GBP9747m in H1 2026.'),'R2-FIN-H12026-4-UNDERLYING_PROFIT':('EX-H126','Lloyds Banking Group underlying pre-tax profit was GBP4215m in H1 2026.'),'SIC-K-WEIGHT24':('EX-ONS','UK SIC2007 Section K had a rounded 2024 GVA weight of 81 per thousand.')}
 matrix=[];atoms=[]
 for c in claims:
  oid=c['original_id'];record=c['record'];klass='B';reason='Original scoped candidate retained; verify exact original passage/table, dates and permissible use before evidence acceptance.'
  if oid in selected:
   klass='A';reason='Narrow factual value rechecked against retained dated primary table excerpt; eligible for owner review for this bounded citation use, not accepted or promoted.'
   eid,statement=selected[oid];atoms.append({'id':'OBS-'+oid,'claim_ref':c['id'],'excerpt_ref':eid,'statement':statement,'source_refs':record['source_refs'],'scope':record.get('subject',record.get('subject_scope')),'reporting_period':record['reporting_period'],'metric':record.get('metric','rounded_GVA_weight'),'unit':record.get('unit'),'value':record.get('value'),'period_start':record.get('period_start'),'period_end':record.get('period_end'),'accounting_basis':record.get('accounting_basis','GVA at basic prices'),'financial_measurement_state':record.get('financial_measurement_state','actual'),'canonical_acceptance':False,'owner_evidence_acceptance':False,'canonical_entity_id':None})
  if oid=='LAND-L26-F1':reason='Official-index excerpt only: full original unavailable. No verified current property diagnosis; acquire original and locator.'
  if oid=='FR-CSRD26-F1':reason='Negative applicability control only: exact entity/national law version, phase and exemption unresolved; no Lloyds duty admitted.'
  if record.get('assertion_class')in ['leadership_stated_target','reported_policy_plan','reported_policy_timetable']:reason+=' Preserve target/plan/timetable as an attributed statement, never actual outcome.'
  matrix.append({'id':c['id'],'kind':'original_claim_or_bundle','class':klass,'reason':reason,'source_refs':record['source_refs'],'original_truth_class':record.get('assertion_class',record.get('claim_class')),'owner_acceptance':False})
 atoms.append({'id':'OBS-FCA-RECEIVED','claim_ref':'RIE2:R2-OBS-FCA-COMPLAINTS','excerpt_ref':'EX-FCA','statement':'Lloyds Bank PLC received 118762 all-product complaints in January to June 2026.','source_refs':['R2-FCA-H126'],'scope':'Lloyds Bank PLC legal entity, all-product Open table','reporting_period':'January–June2026','period_start':'2026-01-01','period_end':'2026-06-30','metric':'complaints_received','unit':'complaints','value':118762,'accounting_basis':'not applicable','financial_measurement_state':'not applicable','canonical_acceptance':False,'owner_evidence_acceptance':False,'canonical_entity_id':None})
 matrix.append({'id':'OBS-FCA-RECEIVED','kind':'atomised_subclaim','class':'A','reason':'Received-total row rechecked; parent compound note remains B. Scope limited to firm all-products and January–June2026.','source_refs':['R2-FCA-H126'],'owner_acceptance':False})
 for r in supplementary:matrix.append({'id':r['id'],'kind':'reconciliation_context_not_incremental_claim_count','class':'B','reason':r['reason'],'source_refs':[],'owner_acceptance':False})
 for r in relationships:matrix.append({'id':r['id'],'kind':'relationship_candidate','class':'B','reason':r['restriction'],'source_refs':r['record']['source_refs'],'owner_acceptance':False})
 for r in issues:matrix.append({'id':r['id'],'kind':'current_issue_interpretation','class':'C','reason':'Evidence-supported question, role/mechanism/remaining-decision hypothesis; no demonstrated unmet buyer need.','source_refs':r['versions'][-1]['record']['source_refs'],'owner_acceptance':False})
 for r in negatives.values():matrix.append({'id':r['id'],'kind':'rejected_inference','class':'D','reason':'; '.join(v['record']['reason']for v in r['versions']),'source_refs':sorted({s for v in r['versions']for s in v['record']['source_refs']}),'owner_acceptance':False})
 for i,r in enumerate(mechanisms):matrix.append({'id':'MECHANISM-'+str(i+1),'kind':'conditional_mechanism','class':'C','reason':r['status'],'source_refs':r['source_refs'],'owner_acceptance':False})
 for r in exclusions:matrix.append({'id':r['id'],'kind':'prohibited_proposed_use','class':'E','reason':r['reason'],'source_refs':[],'owner_acceptance':False})
 
 for a in atoms:
  if '-4-' in a['id']:
   a['original_scope_label']=a['scope']
   a['scope']='Lloyds Banking Group consolidated total'
 write('Evidence-Acceptance-Matrix.json',matrix);write('Observation-Proposals.json',atoms)
 # Review-only plain NDJSON, no invented canonical/workspace/Twin identity or executable ZIP.
 src={s['id']:s for p in ['RIE1','RIE2']for s in read(p,'Source-Ledger.json')}
 records=[]
 for sid in sorted({s for a in atoms for s in a['source_refs']}):
  s=src[sid];records.append({'external_id':sid,'record_class':'source','truth_class':'package_metadata','payload':{'name':s['title'],'url':s['url'],'rights':s['rights']}})
 for a in atoms:
  sid=a['source_refs'][0];e='EVD-'+a['id'];excerpt=next(x for x in extracts if x['id']==a['excerpt_ref'])
  records.append({'external_id':e,'record_class':'evidence','truth_class':'evidence_backed','payload':{'evidence_id':e,'source_id':sid,'source_url':src[sid]['url'],'publication_date':src[sid]['publication_date'],'collection_date':'2026-11-15','summary':a['statement'],'rights':src[sid]['rights'],'original_subject_scope':a['scope'],'reviewed_excerpt_ref':a['excerpt_ref'],'reviewed_excerpt_sha256':excerpt['excerpt_content_sha256'],'primary_content_sha256':None,'candidate_status':'unreviewed'}})
  records.append({'external_id':a['id'],'record_class':'observation','truth_class':'evidence_backed','payload':{'observation_id':a['id'],'atomic_statement':a['statement'],'type':'fact','affected_entity_relationship':'research.'+a['id'].lower(),'event_date':a['period_end']or'2024-12-31','supporting_evidence_ids':[e],'source_subject_scope':a['scope'],'source_id':sid,'candidate_status':'unreviewed','proposal_identity':a}})
 (D/'Proposed-Records.ndjson').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n'for r in records))
 write('Import-Package-Proposal.json',{'status':'owner-review proposal, not executable production package','records_path':'Proposed-Records.ndjson','records_sha256':hashlib.sha256((D/'Proposed-Records.ndjson').read_bytes()).hexdigest(),'source_records':3,'evidence_records':8,'observation_records':8,'contracts':['cios/contracts/twin_object_profiles/researcher_v1.json','cios/applications/flora/blueprint_import/researcher_profile_adapter.py'],'production_manifest':None,'canonical_target_ids':None,'missing_before_any_real_staging':['Owner evidence decision and specific source/rights use','Current authorised import/acceptance state','Country/industry/enterprise owning workspace and explicit canonical entity mappings','Reviewed original dates, stale/comparator handling and dedup dispositions','Governed Twin identity/release metadata then existing manifest files/checksums generated from actual candidate bytes'],'no_automatic_promotion':True})
 # Pin every primary input and the SI1 exact design contract rather than depending on changing branches.
 raw('SI1','Ownership-and-Contracts.md');raw('SI1','Analytical-Design.md')
 write('Pinned-Inputs.json',{'validated_main':'fe66516c15726dc45de147ede2674c9172f8cac6','packages':PINS,'inputs':list(inputs.values())})
 write('Consolidation-Summary.json',{'source_inspections':71,'original_document_urls':len(sources),'exact_url_reinspections':71-len(sources),'same_event_different_surfaces':['LBG-ENVOY26 / R2-LBG-ENVOY-PDF'],'original_claim_records':len(claims),'original_scalar_financial_candidates':250,'retained_reconciliation_context_records':len(supplementary),'current_issue_identities':8,'issue_version_records':sum(len(x['versions'])for x in issues),'owner_review_atom_proposals':len(atoms),'matrix_counts':dict(Counter(x['class']for x in matrix)),'matrix_note':'Counts include parent bundles, relationship proposals, context, interpretations and rejected uses; do not present as independent facts or accepted Observations.','canonical_mutations':0,'pipeline_writes':0})
 print(json.dumps(json.loads((D/'Consolidation-Summary.json').read_text()),indent=2))
if __name__=='__main__':main()
