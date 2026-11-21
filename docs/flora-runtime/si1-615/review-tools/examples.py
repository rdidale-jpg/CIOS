"""Authored, source-bound design specimens. Not a live synthesiser or qualifier."""
from pathlib import Path
import json
D=Path(__file__).resolve().parents[1]


def issue(key,scope,title,why,refs,roles,decision,uncertainty,next_test,counter,stated,financial,pestle,force,chain,swot,offer=None):
 return {'view_ref':'design:'+key,'scope':scope,'title':title,'why_it_matters':why,'assertion_class':'interpretation',
 'source_refs':refs,'as_of':'2026-11-14','horizon':'Use original reporting/effective periods; remaining decision dates unknown',
 'materiality_argument':why,'financial_operational_consequence':{'statement':financial,'class':'interpretation','quantified_external_value':None},
 'leadership':{'status':'authorised_corporate_priority'if stated else 'FLORA_derived_issue','attribution_basis':stated,'named_leader':None,'role_hypotheses':roles,'role_ownership_confirmed':False},
 'decision':{'question':decision,'already_committed':stated or 'Only the source-specific rule or event is established; enterprise implementation is unknown.','remaining_choices':'Unknown until the accountable party confirms the decision and alternatives.','influence':'Not established','decision_date':None},
 'biggest_uncertainty':uncertainty,'counter_evidence':counter,'pain':{'classification':'no_pain_claim','adverse_outcome_evidence_refs':[],'customer_confirmed':False},
 'commercial':{'next_investigation':next_test,'disposition':'Investigate; no qualified opportunity','offer_library_reference':offer,'private_employer_offer_fit':'Not assessed; requires existing authorised Offer approval and matcher','budget':None,'contract_value':None,'external_need':'Unknown','pipeline_handoff':False},
 'analysis':{'pestle':pestle,'five_forces':force,'value_chain':chain,'swot':swot},
 'qualification':{'owner':'ADR-026 / existing MaterialPressureQualification; not executed in SI-1','qualified_pressure_refs':[],'new_canonical_objects':False}}

uk=[
 issue('uk-continuity','uk','Protect continuity in a connected service economy',
  'A reviewed UK cyber-risk context and service-led growth make operational continuity a useful national question; they do not prove a company incident or a sector loss.',
  ['UK-TECHNOLOGICAL','UK-ECONOMIC','UK-GVA-2024'],['Public-policy and industry resilience roles — not a named buyer'],
  'Which service and supplier dependencies deserve closer sector-level investigation?',
  'Sector-specific incidence, loss and control effectiveness are not established.',
  'Choose a material service chain and obtain current sector-specific disruption and dependency evidence before selecting an enterprise hypothesis.',
  ['Aggregate threat evidence cannot identify a deficient bank.','Existing resilience capability may already address the exposure.','Quarterly real GDP growth is not cyber loss or enterprise growth.'],None,
  'Possible interruption of service delivery; no loss, customer pain or external spend is quantified.',
  ['Technological','Economic'],['Supplier power/dependency is a conditional sector mechanism, not a national Porter score.'],
  ['Service creation → technology/supplier enablement → customer continuity; actual dependencies need evidence.'],
  {'strengths':[], 'context':['Observed service contribution to quarterly growth; not proof of operational resilience.'], 'weaknesses':[],
   'opportunities':['Hypothesis: improve dependency visibility where a specific gap is evidenced.'],'threats':['UK aggregate cyber-risk context; enterprise effects remain conditional.']}),
 issue('uk-reporting','uk','Make reporting preparation fit the actual issuer scope',
  'The reviewed FCA reporting rules have specified issuer scope and future accounting periods. Preparation choices matter only for entities actually covered.',
  ['UK-ENVIRONMENTAL','UK-LEGAL'],['Issuer finance, reporting and policy roles — ownership to confirm'],
  'Which issuers and reporting periods are covered, and what preparation is already owned?',
  'No company-specific readiness deficit or unresolved external requirement is demonstrated.',
  'Verify the exact listed legal entity, commencement/reliefs and current preparation before discussing data/control work.',
  ['First reporting follows the specified accounting periods; it is not a universal immediate deadline.','Existing teams or advisers may already cover preparation.','Cyber reform is a separate proposal, not evidence that these reporting rules apply to every enterprise.'],None,
  'Potential reporting-data/control preparation; no measured compliance failure or cost is asserted.',
  ['Legal','Environmental'],['No automatic rivalry or competitive advantage inferred from common rules.'],
  ['Issuer reporting → finance/data/control dependencies; legal scope is a prerequisite.'],
  {'strengths':[], 'weaknesses':[], 'opportunities':['Hypothesis: targeted reporting-process improvement for covered issuers.'],'threats':['Potential transition burden where the rule applies; readiness unknown.']})]
banking=[
 issue('banking-funding','banking','Balance customer value with returns as funding conditions change',
  'The November Bank Rate decision is current context for deposit and lending economics. Its effect on any bank depends on repricing, funding mix and customer behaviour.',
  ['UK-RATE-NOV26','UK-VALUE','UK-CAPITAL','UK-GVA-2024'],['Bank treasury, finance and product roles — hypotheses'],
  'Which pricing and service choices would materially change the bank’s funding economics?',
  'Deposit sensitivity, matched-period margin movement and customer switching are unmeasured.',
  'Obtain a matched-period bank-level funding/margin bridge and test customer/pricing alternatives before proposing transformation.',
  ['Rate direction alone does not establish lost margin.','The value-system/capital anchors are historical interpretations, not current thresholds or market shares.','Finance & insurance GVA is not Banking revenue or a bank profit pool.'],None,
  'Possible funding and customer-value trade-off; no adverse bank consequence is demonstrated.',
  ['Economic','Social'],['Buyer bargaining power and rivalry are conditional interpretations; entrant/capital constraints are historical context.'],
  ['Customer acquisition → deposits/funding → lending → service outcomes.'],
  {'strengths':[], 'context':['Historical hypothesis: primary-account relationships may support funding stability; current magnitude unknown.'],
   'weaknesses':[], 'opportunities':['Hypothesis: service/pricing choices that preserve value if a bank-specific trade-off is demonstrated.'],
   'threats':['Conditional repricing/switching exposure; no measured current loss.']}),
 issue('banking-reporting','banking','Prepare incident reporting at the right legal-entity boundary',
  'Reviewed PRA/FCA reporting changes identify a dated industry requirement. Applicability and existing readiness must be checked for each regulated entity.',
  ['UK-PRA-REPORT27','UK-FCA-REPORT27','UK-CTP'],['Operational resilience, risk and compliance roles — hypotheses'],
  'Which reporting/control decisions remain unresolved after current internal and incumbent preparation?',
  'Entity applicability, readiness gaps, existing coverage and external scope remain unknown.',
  'Validate the regulated legal entity and readiness owner; compare the current incident/third-party reporting process with the final applicable requirements.',
  ['A known implementation date is not an open procurement or proof of non-compliance.','Older critical-third-party context is not current designation evidence.','An internal or incumbent-led solution may already be sufficient.'],None,
  'Possible incident-data/control preparation; no bank-specific adverse consequence or supplier requirement is established.',
  ['Legal','Technological'],['Supplier dependencies may shape resilience choices; bargaining power is unmeasured.'],
  ['Third-party/platform enablement → risk and incident detection → regulatory reporting.'],
  {'strengths':[], 'context':['Lloyds reports existing Envoy controls; a single-company counterexample cannot establish a sector-wide strength.'],
   'weaknesses':[], 'opportunities':['Hypothesis: narrowly evidenced reporting/control improvement after scope and gap confirmation.'],
   'threats':['Potential implementation exposure for covered entities; not established failure.']})]
lloyds=[
 issue('lloyds-core','lloyds','Renew core platforms without disrupting customer service',
  'Core renewal is a company-stated strategy priority. Service continuity is a plausible decision constraint, but the selected evidence does not establish the current system map or an outage problem.',
  ['LBG-A2030-PLATFORMS','LBG-A2030-INVESTMENT','LBG-Q326-DEPOSITS','UK-RATE-NOV26','UK-CAPITAL'],['Technology and operations leadership — ownership not confirmed'],
  'Which core-renewal choices and customer journeys are still open to influence?',
  'The affected estate, current programme ownership, decision gates and external delivery scope are unknown.',
  'Ask the accountable platform/service owner for the unresolved options and service-dependency evidence; test incumbent/internal coverage before any delivery proposition.',
  ['A stated renewal priority may already have approved delivery arrangements.','Planned group investment is not a supplier budget.','Deposit balances do not quantify migration scope or value.','A national rate change does not establish a Lloyds migration pressure.'],
  'The authorised corporate strategy prioritises core-platform renewal for 2027–2030; no named executive attribution is made.',
  'Potential service-continuity and delivery trade-offs; deposits are contextual stock, not contract value.',
  ['Technological','Economic'],['Supplier power/entry/capital mechanisms may constrain options, but enterprise-specific bargaining and funding sensitivity are unknown.'],
  ['Core platforms/data → lending, payments and servicing; actual dependencies require OPS-01.'],
  {'strengths':[], 'strategic_responses':['Published core-renewal commitment; successful execution not established.'],'weaknesses':[],
   'opportunities':['Hypothesis: shape an unresolved service/architecture choice if the owner confirms it remains open.'],
   'threats':['Conditional transition/continuity risk; no actual service failure claimed.']},'tech-strategic-complex-legacy-modernisation'),
 issue('lloyds-efficiency','lloyds','Turn the efficiency ambition into evidenced operating choices',
  'The 2030 cost:income ambition is below 45%. That target establishes strategic intent, not current excessive cost, realised savings or available external spend.',
  ['LBG-A2030-CIR','LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','UK-RATE-NOV26'],['Finance and operations leadership — ownership not confirmed'],
  'What matched-period cost and customer-outcome evidence would justify the next operating-model choice?',
  'Current income/cost decomposition, comparable growth and remaining funded decisions are unresolved.',
  'Request a reconciled income/cost baseline and already-funded change scope; identify one customer process whose net outcome could be tested without assuming a technology purchase.',
  ['A target is not an observed adverse outcome.','Nine-month profit cannot be annualised or treated as investable budget.','Deposit stock is not revenue.','Internal teams and existing programmes may already cover the target.'],
  'The authorised strategy states a 2030 efficiency ambition; it does not establish a named leader’s private belief.',
  'Potential efficiency/customer-outcome trade-off; current cost pain and quantified external value are not established.',
  ['Economic','Technological'],['Bank pricing/rivalry mechanisms are context only; current Lloyds margin erosion is not proven.'],
  ['Funding/income → operating activity → customer outcomes; no invented cost allocation.'],
  {'strengths':[], 'context':['Reported nine-month Group profit; neither excess cash nor operational superiority established.'],'weaknesses':[],
   'opportunities':['Hypothesis: a specific operating-process improvement, conditional on a reconciled baseline and unmet need.'],
   'threats':['Conditional failure to realise future ambition; no current target miss claimed.']},'tech-strategic-digital-transformation'),
 issue('lloyds-ai','lloyds','Prove benefit on the AI capability already being built',
  'Lloyds describes Envoy, Google Cloud collaboration and built-in controls. A useful discussion tests realised service outcomes, rather than presuming a missing AI platform or absent controls.',
  ['LBG-ENVOY-CONTROLS','LBG-ENVOY-GOOGLE','LBG-A2030-DATA','UK-TECHNOLOGICAL'],['Service/business and technology/data leadership — ownership not confirmed'],
  'Which service outcome remains unproven after existing platform and control work?',
  'Net benefits, control effectiveness, workflow adoption and residual external need remain unknown.',
  'Select one service workflow and ask its owner for outcome/control evidence and a process-only alternative; test whether the incumbent platform already meets the need.',
  ['The announced platform and existing controls defeat a generic greenfield AI or missing-control pitch.','An announcement proves neither effective controls nor realised net benefit.','The named collaboration establishes no exclusivity, renewal or unallocated scope.','UK cyber context is not a Lloyds incident.'],
  'The bank’s announcement and strategy describe capability and data priorities; no CEO belief or buyer name is inferred.',
  'Potential service-benefit/control trade-off; no measured adverse outcome, budget or deal value.',
  ['Technological'],['One supported platform collaboration does not measure supplier bargaining power or lock-in.'],
  ['Data/platform capability → frontline/service workflow → customer outcome; actual dependency and outcome validation required.'],
  {'strengths':['Source-reported Envoy capability and controls, with effectiveness unverified.'],'weaknesses':[],
   'opportunities':['Hypothesis: a residual workflow or assurance need, if current delivery does not already resolve it.'],
   'threats':['Conditional control/adoption risk; not an observed deficiency.']},'tech-strategic-ai-first-transformation')]

negative=[{'id':'santander-early-influence','scope':'santander-uk','runtime_reference':'BK-ENT-005','repository_twin_reference_not_joined':'BK-ENT-007',
 'title':'Already in motion; an early shaping window is not demonstrated',
 'source_refs':['BTI-TSB-APPLICATION','BTI-TSB-MIGRATION','BTI-TSB-LEGAL'],'source_date':'2026-11-10',
 'observed':'The release reports a conditional business transfer application, a named target platform/channel direction and conditional H2 2027 customer migration. The banks remain separate legal entities.',
 'interpretation':'Original programme/architecture formation may already be too mature for an early prime transformation play. This is a decision-specific inference, not proof all future choices are closed.',
 'what_is_not_known':['Current sourcing/procurement','Unallocated external work','Accountable contracting entity','Remaining design/service decisions','Seller access','Buyer demand or budget'],
 'decision_specific_result':'Research only for a new early programme-shaping thesis; no supported early pursuit recommendation.',
 'next_test':'If authorised access exists, ask which residual service/data-reconciliation choices remain open and what internal/incumbent work already covers them. Do not pitch a replacement programme on the announcement alone.',
 'pain':'No demonstrated adverse outcome in these excerpts','pipeline_handoff':False,'contract_value':None,
 'historical_tiers_changed':False,'as_of':'2026-11-14'},
 {'id':'lloyds-greenfield-ai','scope':'lloyds','title':'A greenfield missing-AI-control thesis is not supported',
 'source_refs':['LBG-ENVOY-CONTROLS','LBG-ENVOY-GOOGLE'],'source_date':'2026-05-01',
 'observed':'The bank reports an existing announced platform and built-in controls.',
 'interpretation':'Do not admit a leadership issue claiming no AI platform or controls. Effectiveness and residual outcome gaps remain separate questions.',
 'decision_specific_result':'Quiet/rejected claim: no missing-platform issue admitted; use the qualified benefit question instead.',
 'pipeline_handoff':False,'contract_value':None,'as_of':'2026-11-14'},
 {'id':'fr-law-lloyds','scope':'lloyds','title':'Foreign-country law is not a demonstrated UK banking duty',
 'source_refs':[],'excluded_source_refs':['GM-CSRD-FR'],'source_date':None,
 'observed':'The proposed input is a France-scoped legal-context reference, not a confirmed Lloyds legal-entity obligation.',
 'interpretation':'Stop the applicability edge; neither a Lloyds pain point nor an agenda recommendation follows.',
 'decision_specific_result':'Applicability not established; preserve a research question for an exact entity, including any relevant EU subsidiary, only with a lawful basis.',
 'pipeline_handoff':False,'contract_value':None,'as_of':'2026-11-14'}]


# These are authored explanations, not a causal inference engine.
WORKED={
 'design:uk-continuity':[
  ('UK aggregate cyber survey','Potential supplier/service concentration','inferred','UK-TECHNOLOGICAL','Survey fieldwork August–December 2025; no named dependency or supplier concentration measured.'),
  ('Potential supplier/service concentration','Service-chain interruption exposure','unknown','UK-TECHNOLOGICAL','No supported chain-specific dependency or interruption loss.'),
  ('Service-chain interruption exposure','Verified internal weakness','blocked','UK-TECHNOLOGICAL','Unknown exposure cannot become a verified weakness or support the agenda.')],
 'design:banking-funding':[
  ('November Bank Rate decision','Buyer switching and deposit repricing','inferred','UK-RATE-NOV26','A possible bargaining mechanism, not observed deposit beta or switching.'),
  ('Buyer switching and deposit repricing','Bank funding and lending value chain','inferred','UK-VALUE','Historical conceptual value-system anchor; current magnitude unmeasured.'),
  ('Bank funding and lending value chain','Current adverse bank margin consequence','unknown','UK-CAPITAL','Need matched-period bank-level funding, capital and margin evidence; no inferred pain.')],
 'design:lloyds-core':[
  ('UK funding conditions — PESTLE Economic','Potential bank buyer switching/repricing — industry economics','inferred','UK-RATE-NOV26','A conditional market mechanism; no measured deposit beta, switching or margin change.'),
  ('Potential bank buyer switching/repricing — industry economics','Funding and service activity — value chain','inferred','UK-VALUE','Historical conceptual value-chain anchor; not a current measured economic effect.'),
  ('Funding and service activity — value chain','Actual Lloyds core/service exposure','unknown','LBG-A2030-PLATFORMS','The stated core-renewal priority supports company intent, not a causal rate-to-platform dependency. OPS-01 remains unresolved.'),
  ('Actual Lloyds core/service exposure','Conditional continuity threat — SWOT','hypothesis','LBG-A2030-PLATFORMS','A transition may affect continuity, but no outage or verified internal weakness is evidenced.'),
  ('Conditional continuity threat — SWOT','Verified current Lloyds pain — rejected strategic conclusion','blocked','LBG-A2030-PLATFORMS','Unknown dependency and hypothetical threat cannot establish demonstrated service pain.'),
  ('Verified current Lloyds pain — rejected strategic conclusion','Pain-led Leadership Agenda admission — rejected','blocked','LBG-A2030-PLATFORMS','No pain-led admission or sales recommendation follows. The separate direct-source path admits only a question about the stated renewal priority.'),
  ('Pain-led Leadership Agenda admission — rejected','Supplier pursuit or qualified opportunity — rejected','blocked','LBG-A2030-PLATFORMS','No external need, owner-confirmed remaining decision or Pipeline qualification exists.')]

}

def traces(issues):
 out=[]
 for item in issues:
  key=item['view_ref'];primary=item['source_refs'][0]
  # An independently bounded direct path admits a question, never the unresolved causal conclusion.
  admission=[
   {'from':'source:'+primary,'to':key+':reported_statement','status':'source_supported','support_refs':[primary],
    'rationale':'Existing source-backed candidate supports only the reported statement/context; original authority remains candidate.'},
   {'from':key+':reported_statement','to':key+':issue','status':'interpretation','support_refs':[primary],
    'rationale':item['why_it_matters']},
   {'from':key+':issue','to':key+':agenda','status':'interpretation','support_refs':item['source_refs'],
    'rationale':'Qualitative editorial admission of a decision question, with no demonstrated pain or proven external need.'},
   {'from':key+':agenda','to':key+':investigation','status':'recommendation','support_refs':item['source_refs'],
    'rationale':item['commercial']['next_investigation']}]
  conditional=[{'from':a,'to':b,'status':status,'support_refs':[ref],'rationale':why,
   'scope':item['scope'],'as_of':item['as_of'],'eligible_agenda_support':False,
   'counter_evidence':item['counter_evidence'],'challenge':item['biggest_uncertainty']}
   for a,b,status,ref,why in WORKED.get(key,[])]
  out.append({'id':key+':trace','issue':key,'scope':item['scope'],'as_of':item['as_of'],
   'admission_path':admission,'conditional_transmission_path':conditional,
   'admitted_conclusion':'A strategic learning/decision question; no adverse outcome, buyer need or opportunity qualification.',
   'excluded_conclusion':'No unknown transmission edge may support a stronger company consequence or a verified SWOT weakness.',
   'qualified_material_pressure_refs':[],'news_input':'Future only; not collected or rendered.'})
 return out


def build():
 for item in uk+banking+lloyds:
  actual=['LBG-ENVOY-CONTROLS','LBG-ENVOY-GOOGLE']if item['view_ref']=='design:lloyds-ai'else []
  item['challenges']=[{'statement':text,'class':'source_backed_counter_evidence'if index==0 and actual else 'alternative_or_methodological_limit',
   'source_refs':actual if index==0 else []}for index,text in enumerate(item['counter_evidence'])]
 data={'schema':'SI-1 authored design specimens v1.0','authority':'proposal / candidate interpretation; no canonical contracts or writes',
  'base':'fe66516c15726dc45de147ede2674c9172f8cac6','as_of':'2026-11-14','policy':'si1-design-editorial-v1.0',
  'agendas':{'uk':uk,'banking':banking,'lloyds':lloyds},'negative_cases':negative,'traces':traces(uk+banking+lloyds),
  'preserved_lloyds_gaps':['FIN-01','FIN-02','ORG-01','OPS-01','REL-01','REG-01','ORG-02','INF-01','COM-01'],
  'coverage_note':'Complete analytical model design; incomplete evidence. Two UK and two Banking issues are deliberate; zero evidenced internal weakness is not replaced by research gaps.',
  'external_value_note':'Potential £100m+ reinvention is the intended commercial domain, not a valuation for these cases. Budget, TCV, external need and buyer identity remain unproven.'}
 (D/'Proof-Cases.json').write_text(json.dumps(data,indent=2)+'\n');print('Seven bounded issue examples, seven explicit traces and three negative/quiet cases.')
if __name__=='__main__':build()
