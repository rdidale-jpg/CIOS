"""Proposed design view schemas only; does not install runtime/canonical contracts."""
from pathlib import Path
import json
D=Path(__file__).resolve().parents[1]
def obj(props,required=None):return {'type':'object','properties':props,'required':required or list(props),'additionalProperties':False}
s={'type':'string','minLength':1};texts={'type':'array','items':s};null={'type':'null'}
issue=obj({
 'view_ref':{'type':'string','pattern':'^design:'},'scope':{'enum':['uk','banking','lloyds']},'title':s,'why_it_matters':s,
 'assertion_class':{'const':'interpretation'},'source_refs':texts,'as_of':{'type':'string','format':'date'},'horizon':s,'materiality_argument':s,
 'financial_operational_consequence':obj({'statement':s,'class':{'const':'interpretation'},'quantified_external_value':null}),
 'leadership':obj({'status':{'enum':['authorised_corporate_priority','FLORA_derived_issue']},'attribution_basis':{'type':['string','null']},'named_leader':null,'role_hypotheses':texts,'role_ownership_confirmed':{'const':False}}),
 'decision':obj({'question':s,'already_committed':s,'remaining_choices':s,'influence':{'const':'Not established'},'decision_date':null}),
 'biggest_uncertainty':s,'counter_evidence':texts,
 'pain':obj({'classification':{'const':'no_pain_claim'},'adverse_outcome_evidence_refs':{'type':'array','maxItems':0},'customer_confirmed':{'const':False}}),
 'commercial':obj({'next_investigation':s,'disposition':{'const':'Investigate; no qualified opportunity'},'offer_library_reference':{'type':['string','null']},'private_employer_offer_fit':s,'budget':null,'contract_value':null,'external_need':{'const':'Unknown'},'pipeline_handoff':{'const':False}}),
 'analysis':obj({'pestle':texts,'five_forces':texts,'value_chain':texts,'swot':obj({k:texts for k in ['strengths','weaknesses','opportunities','threats','context','strategic_responses']},['strengths','weaknesses','opportunities','threats'])}),
 'qualification':obj({'owner':s,'qualified_pressure_refs':{'type':'array','maxItems':0},'new_canonical_objects':{'const':False}}),
 'challenges':{'type':'array','minItems':1,'items':obj({'statement':s,'class':{'enum':['source_backed_counter_evidence','alternative_or_methodological_limit']},'source_refs':texts})}})
issue={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:flora:si1:design:issue','title':'SI-1 authored pilot IssueView — proposal, not a canonical contract',**issue}
agenda=obj({'status':{'const':'design proposal; no persisted agenda'},'scope':{'enum':['uk','banking','lloyds']},'subject_reference':s,'as_of':{'type':'string','format':'date'},'policy_version':s,'dependency_owner_hashes':{'type':'object','additionalProperties':{'type':'string','pattern':'^[0-9a-f]{64}$'}},'issues':{'type':'array','items':{'$ref':'urn:flora:si1:design:issue'}},'ordering_basis':s,'research_completeness':{'const':'Incomplete; no full national/industry/enterprise diagnosis claimed'},'qualified_opportunities_created':{'const':0}})
agenda={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:flora:si1:design:agenda','title':'SI-1 authored pilot AgendaView — proposal',**agenda}
(D/'IssueView.schema.json').write_text(json.dumps(issue,indent=2)+'\n');(D/'AgendaView.schema.json').write_text(json.dumps(agenda,indent=2)+'\n')
refs=json.loads((D/'Evidence-References.json').read_text())['references'];examples=json.loads((D/'Proof-Cases.json').read_text())
rows=[]
for scope,items in examples['agendas'].items():
 rows.append({'status':'design proposal; no persisted agenda','scope':scope,'subject_reference':{'uk':'public:GB','banking':'public:BK-IND-002','lloyds':'public:BK-ENT-001'}[scope],
 'as_of':examples['as_of'],'policy_version':examples['policy'],'dependency_owner_hashes':{refs[r]['owner_path']:refs[r]['owner_sha256']for item in items for r in item['source_refs']},
 'issues':items,'ordering_basis':'Qualitative editorial order: source-grounded decision relevance and distinct consequences; no numeric score or implied opportunity rank.',
 'research_completeness':'Incomplete; no full national/industry/enterprise diagnosis claimed','qualified_opportunities_created':0})
(D/'AgendaViews.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Proposed pilot presentation schemas and three reproducible agenda specimens.')
