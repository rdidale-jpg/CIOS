"""Pinned input/source reconciliation and proposed gap changes; never source-owner mutation."""
from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];RIE1='c57ed9728473563b5535db36d5bfbe5e96a8c572'
def write(n,x):(D/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
def prior(n):return json.loads(subprocess.check_output(['git','show',RIE1+':docs/flora-runtime/rie1-617/'+n],cwd=ROOT))
s=json.loads((D/'Source-Ledger.json').read_text());old={r['url']:r['id']for r in prior('Source-Ledger.json')};rows=[]
for source in s:
 rows.append({'rie2_id':source['id'],'original_url':source['url'],'rie1_id':old.get(source['url']),'relation':'fresh reinspection of same original; not independent corroboration'if source['url']in old else'new document to this research ledger, still candidate','canonical_action':'none; acceptance/dedup mapping unapproved'})
write('Source-Delta.json',{'rie1_commit':RIE1,'sources':rows,'new_document_urls':sum(r['rie1_id']is None for r in rows),'reinspected_document_urls':sum(r['rie1_id']is not None for r in rows),'special_case':'Envoy datedPDF is a new inspected document surface for the same disclosed platform event, not independent corroboration of the HTML.','research_scope':'Prior20-sector/UK baseline and other4agenda candidates remain pinned, not refreshed or promoted.'})
limits={
'FIN-01':'Group/segment/APM/statutory bridges now acquired for named periods. Unit cost-to-serve, legal-company current accounts and fully reconciled investment allocation remain open.',
'FIN-02':'Within-issuer segment growth/returns context improved; matched cross-bank capital/product scope and Q3segmentP&L remain unacquired; no performance ranking.',
'ORG-01':'Dated principal direct/indirect holdings acquired at 31Dec2025; full current register and intermediate parents remain unverified.',
'ORG-02':'Public current professional roles and IFRS8CODM identified; exact service/procurement/budget accountability remains unknown.',
'OPS-01':'Product/economic mechanisms and platform capabilities acquired; actual critical-service/process/system map, unit cost and measured control effectiveness remain open.',
'REL-01':'Microsoft multi-year scope and Google/Envoy disclosure refreshed; all price/workshare/exclusivity/renewal/exit and other major supplier contracts remain unknown.',
'REG-01':'CTP effective dates/provider legal entities acquired; exact Lloyds legal-entity/service applicability, readiness and breach evidence remain unknown.',
'INF-01':'Provider/system context is not a Lloyds payment-infrastructure membership/service-operating edge; original infrastructure gap remains open.',
'COM-01':'Public evidence establishes no customer-confirmed need, economic buyer, unallocated funding/procurement, external scope or influence window.'}
g=json.loads((D/'Gap-Dispositions.json').read_text())
for r in g['visual_nine']:
 r['rie1_remaining']=r.pop('remaining',r.get('rie1_remaining'));r['rie2_remaining']=limits[r['id']]
updates={
'G-PRIMARY':(['R2-LBG-FY25','R2-LBG-H126','R2-LBG-Q326','R2-LBG-20F25'],'Selected original tables/notes now inspected; full original-byte archive/hash and acceptance remain open.'),
'G-CUSTOMER-EVIDENCE':([], 'No customer-confirmed problem, funded decision process, buyer or mutual action; public complaints do not resolve this.'),
'G-REGULATORY':(['R2-HMT-CTP','R2-LBG-RING'],'Dated provider-designation scope acquired, not an exact bank readiness/compliance determination.'),
'G-ALLOCATION':(['R2-LBG-Q326'],'Company explains cost/investment direction; no external programme allocation or supplier budget verified.'),
'G-OUTCOMES':(['R2-FCA-H126','R2-FOS-APRSEP26','R2-IPSOS-AUG26'],'Firm service measures acquired on exact scopes/windows; causal journey harm, trend, unit economics and survey score-label alignment remain open.'),
'G-PRIMACY':(['R2-LBG-H126','R2-NW-H126'],'Savings/pricing explanation and peer mix acquired; salary/DD concentration, elasticity and cohort primary-relationship status remain unknown.'),
'G-WORKLOADS':(['R2-LBG-MS26','R2-LBG-ENVOY-PDF'],'Disclosed capability boundaries refined; no workload dependency map, approved sourcing or delivery choice verified.'),
'G-AI-BENEFITS':(['R2-LBG-AI26','R2-LBG-MS26'],'Actual-claim versus expected and adoption clarified; net realised2026 customer/use-case benefit and control costs remain unknown.'),
'G-SUPPLIER':(['R2-LBG-MS26','R2-LBG-ENVOY-PDF'],'Known disclosed agreements/capabilities only; workshare, obligations, terms/value/renewal/exit unverified.'),
'G-CURVE':(['R2-LBG-Q326'],'Completion remains established as in baseline; no integration roadmap, open architecture or procurement inferred.'),
'G-FRAUD':([], 'No new Lloyds-specific fraud loss/false-positive/customer-outcome evidence; all original requirements remain open.'),
'G-CLIMATE':([], 'No new portfolio financed-emission/transition materiality or customer needs; do not substitute a generic environmental mechanism.'),
'G-MARKET':(['R2-NW-H126','R2-BAR-H126','R2-LG-H126'],'Comparable-within-issuer mechanism examples acquired; national matched market shares, profit pools and entrant economics remain open.')}
for r in g['overlay_thirteen']:
 refs,change=updates[r['id']];r['source_refs']=refs;r['rie2_evidence_delta']=change
 r['proposed_disposition']='partial evidence enrichment; original owner status unchanged'if refs else'open; no resolving evidence'
write('Gap-Dispositions.json',g)
paths=['cios/applications/flora/visual_streams.py','cios/applications/flora/visual_v2_assets/economy.json','enterprise-knowledge/banking/research-model/Assessment-Overlay.json','enterprise-knowledge/macro/research-model/Macro-Context-v1.json','cios/contracts/twin_object_profiles/researcher_v1.json','cios/applications/flora/live/source_registry.py','cios/applications/flora/financial_intelligence/schema.py','tools/ci/flora-baseline-v1.json','tools/ci/flora_ci.py','.github/workflows/flora-validation.yml','architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md']
write('Ownership-Checks.json',{'main':'fe66516c15726dc45de147ede2674c9172f8cac6','owners':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),'matches_validated_main':(ROOT/p).read_bytes()==subprocess.check_output(['git','show','fe66516c15726dc45de147ede2674c9172f8cac6:'+p],cwd=ROOT)}for p in paths],'canonical_writes':0,'source_registration_writes':0,'runtime_changes':0,'pipeline_changes':0,'production_import_receipts':'not inspected; unverified'})
# Reproduction inputs are source-bound authored data; original bytes are never invented.
write('Acquisition-Limits.json',{'cutoff':'2026-11-14','direct_bytes':{'attempts':2,'sources':['R2-LBG-H126','R2-LBG-FY25'],'result':'URLError; no bytes or hashes obtained'},'official_source_blockers':[{'source':'Full original2025 annual-report incorporated rendering','url':'https://www.sec.gov/Archives/edgar/data/1160106/000116010626000010/lyg-20251231.htm','status':'research tool size limit; compact official Form20F_d2 original and FYresults used within their actual extent'},{'source':'Ipsos provider-to-score chart alignment','url':'https://www.ipsos.com/sites/default/files/PCAGB_3rd_Party_Aug2026_v1.pdf_0.pdf','status':'PDFtext labels missing; screenshot unavailable. No score assignment or visual table check claimed.'},{'source':'IBM/middleware recruitment page','url':'https://www.lloydsbankinggroup.com/careers/job-search/workday-job.159303.html','status':'400; no technology-inventory/contract conclusion adopted. A job deadline is not a publication date.'}],'current_production_receipts':'Unverified; no private runtime ledger accessed','source_rights':'Public factual values and bounded paraphrases only; full source redistribution/ingestion permissions not assumed'})
print('Source delta:',sum(r['rie1_id']is None for r in rows),'new document URLs;',sum(r['rie1_id']is not None for r in rows),'fresh reinspections; source owners unchanged')
