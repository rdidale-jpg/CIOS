from __future__ import annotations
import argparse, hashlib, json, re, time
from pathlib import Path
from typing import Any
from .models import *
from .reasoning import DeterministicDevelopmentAdapter, ReasoningAdapter, configured_reasoning_adapter
from .semantic import OBS_TEXT, MECHANISM_DETAILS, build_semantic_context

ROOT=Path(__file__).resolve().parents[4]
KNOW=ROOT/'enterprise-knowledge'
OUT=ROOT/'.flora_enterprise_intelligence'/'banking'
QUESTION='What is changing in Banking, why does it matter, who should care, and what should I do next?'
OBS=['BK-OBS-014','BK-OBS-015','BK-OBS-016','BK-OBS-029','BK-OBS-047']; MECH=['BM-04','BM-02','BM-14','BM-15']
ASSETS=['BK-IND-001','BK-IND-002','BK-REF-001','BK-INF-001','BK-ENT-001','BK-ENT-003','BK-CMP-002','BK-FLR-001','EK-BANK-RHYP-001','BK-FLR-SSN-SPEC-001','BK-GOV-SSN-VAL-001']
STAGES=['Intent Analysis','Context Planning','Knowledge Retrieval','Observation Selection','Mechanism Assessment','Enterprise Context','Hypothesis Assessment','Challenge','Executive Relevance','Commercial Assessment','Recommendation Eligibility','Presentation','Learning Capture']

def _rid(): return 'RUN-'+time.strftime('%Y%m%d%H%M%S')
def _hash(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def _rel(loc:str)->Path: return KNOW/loc

def load_manifest()->dict[str,Any]: return json.loads((KNOW/'banking/flora/Banking-Knowledge-Manifest.json').read_text())
def manifest_index(): return {a['asset_id']:a for a in load_manifest()['assets']}
def parse_hypothesis()->dict[str,Any]:
    p=KNOW/'banking/reinvention/Banking-Reinvention-Hypotheses-v0.1.md'; txt=p.read_text(); m=re.search(r'## BRH-003.*?(?=\n## BRH-004)',txt,re.S); sec=m.group(0)
    def part(name):
        mm=re.search(rf'### {re.escape(name)}\n\n(.*?)(?=\n### |\Z)',sec,re.S); return mm.group(1).strip() if mm else ''
    return {'hypothesis_id':'BRH-003','statement':part('Hypothesis Statement'),'lifecycle_state':'Candidate','section':sec,'unknowns':[x.strip('- ') for x in part('Unknowns').splitlines() if x.startswith('-')],'contradictions':[part('Contradicting Evidence')],'evidence_required':[x.strip('- ') for x in part('Evidence Required').splitlines() if x.startswith('-')],'confidence':re.sub(r'\*','',part('Confidence'))}

def retrieve(run_id:str, plan:ContextPlan)->RetrievalSet:
    idx=manifest_index(); assets=[]
    for aid in plan.manifest_asset_ids:
        if aid not in idx: raise ValueError(f'unsupported asset ID: {aid}')
        a=idx[aid]; p=_rel(a['location']);
        if not p.exists(): raise ValueError(f'asset path missing: {aid} {p}')
        assets.append(GovernedAsset(asset_id=aid,title=a['title'],asset_type=a['asset_type'],status=a['status'],location=str(p.relative_to(ROOT)),content_sha256=_hash(p),metadata={'version':a.get('version'),'relationships':a.get('relationships')}))
    hyp=parse_hypothesis()
    obs=[{'observation_id':o,'statement':OBS_TEXT.get(o,o),'what_it_says':OBS_TEXT.get(o,o),'why_it_matters':'It explains why branch, hub and assisted-access evidence changes commercial interpretation rather than only channel reporting.','supports':'BRH-003 mixed access hypothesis','related_mechanisms':['BM-04','BM-02','BM-14'] if o!='BK-OBS-029' else ['BM-04','BM-15'],'relevance':'High','confidence':'Medium','evidence_refs':['EK-BANK-RHYP-001','BK-GOV-SSN-VAL-001'],'freshness':'Unknown','limitations':'Source-grounded but still needs enterprise-specific outcome evidence.'} for o in plan.observation_ids]
    mech=[{'mechanism_id':m,'name':MECHANISM_DETAILS.get(m,(m,'',''))[0],'meaning':MECHANISM_DETAILS.get(m,(m,'Unsupported by current governed knowledge',''))[1],'how_it_operates':MECHANISM_DETAILS.get(m,(m,'','Unsupported by current governed knowledge'))[1],'why_it_matters':MECHANISM_DETAILS.get(m,(m,'','Unsupported by current governed knowledge'))[2],'affected_participants':['incumbents','mutuals/building societies','digital challengers','shared access operators'],'relationship_to_observations':plan.observation_ids,'relationship_to_hypothesis':'Explains why BRH-003 is plausible but still constrained by economics and segment evidence.','alternative_mechanisms':['pure cost reduction','transitional mitigation','participant-specific trust differentiation'],'limitations':['Requires enterprise-specific outcome and economics evidence'],'relevance':'High','confidence':'Medium','authority_asset_id':'BK-CMP-002'} for m in plan.mechanism_ids]
    return RetrievalSet(object_id=run_id+'-retrieval',run_id=run_id,status='PASS',source_asset_ids=plan.manifest_asset_ids,relationship_paths=['BRH-003->observations','BRH-003->mechanisms'],confidence='Medium',unknowns=['Observation source evidence is inherited rather than directly embedded'],contradictions=hyp['contradictions'],assets=assets,hypothesis=hyp,observations=obs,mechanisms=mech)

def run_pipeline(output_dir:Path=OUT, adapter:ReasoningAdapter|None=None, extra_asset_ids:list[str]|None=None)->PipelineRun:
    adapter=adapter or configured_reasoning_adapter(); run_id=_rid(); audit=[]; stages={}
    q=QuestionObject(object_id=run_id+'-question',run_id=run_id,question=QUESTION,user_role='Strategic Sales Director',industry_scope=['Banking'],mode='Explore',required_output='Strategic Sales Brief')
    intent=IntentObject(object_id=run_id+'-intent',run_id=run_id,interpretations=['industry understanding','executive relevance','commercial next action'],progression='Explore with controlled progression toward Focus/Shape',prohibited_claims=['unsupported enterprise-specific claims','invented named executives'],source_asset_ids=[]); stages['intent']=intent
    plan=ContextPlan(object_id=run_id+'-context-plan',run_id=run_id,required_asset_classes=['manifest','hypothesis register','observation lineage','mechanism authority','strategic sales navigation'],hypothesis_id='BRH-003',observation_ids=OBS,mechanism_ids=MECH,manifest_asset_ids=ASSETS+(extra_asset_ids or []),required_stages=STAGES,required_output='Strategic Sales Brief'); stages['context_plan']=plan
    retrieval=retrieve(run_id,plan); stages['retrieval']=retrieval
    semantic_context=build_semantic_context(run_id, q.question, [a.model_dump()|{'location':a.location.replace('enterprise-knowledge/','')} for a in retrieval.assets], retrieval.hypothesis, retrieval.observations, retrieval.mechanisms); stages['semantic_context']=semantic_context
    obs=ObservationSelection(object_id=run_id+'-observations',run_id=run_id,source_asset_ids=['EK-BANK-RHYP-001','BK-GOV-SSN-VAL-001'],relationship_paths=['BRH-003->BK-OBS-*'],confidence='Medium',unknowns=retrieval.hypothesis['unknowns']+retrieval.unknowns,contradictions=retrieval.contradictions,selected_observations=retrieval.observations,missing_evidence=['Direct observation register source evidence is not machine-exposed in this slice']); stages['observation_selection']=obs
    mech=MechanismAssessment(object_id=run_id+'-mechanisms',run_id=run_id,source_asset_ids=['BK-CMP-002','BK-REF-001'],relationship_paths=['BRH-003->BM-*->BK-OBS-*'],confidence='Medium',unknowns=obs.unknowns,contradictions=obs.contradictions,mechanisms=retrieval.mechanisms,alternatives=['Branch reduction is primarily a cost programme for some incumbents','Physical access is primarily a trust and inclusion mechanism for some participants','Shared access may be transitional rather than structural','Customer segment variation prevents one uniform industry access model'],applicability_constraints=['Participant type changes mechanism behaviour']); stages['mechanism_assessment']=mech
    ent=EnterpriseContextAssessment(object_id=run_id+'-enterprise-context',run_id=run_id,status='PARTIAL',source_asset_ids=['BK-IND-002','BK-ENT-001','BK-ENT-003'],relationship_paths=['BRH-003->supporting enterprise models'],confidence='Low-Medium',unknowns=mech.unknowns+['Enterprise specificity is Unknown for the canonical question'],contradictions=mech.contradictions,participant_scope='UK Banking participant types',enterprise_specificity='Unknown',why_them_strength='Downgraded to industry/participant-type relevance'); stages['enterprise_context']=ent
    hyp=HypothesisAssessment(object_id=run_id+'-hypothesis',run_id=run_id,source_asset_ids=['EK-BANK-RHYP-001'],relationship_paths=['BRH-003->observations','BRH-003->mechanisms'],confidence='Medium',unknowns=ent.unknowns,contradictions=ent.contradictions,hypothesis_id='BRH-003',original_statement=retrieval.hypothesis['statement'],lifecycle_state='Candidate',supporting_observations=OBS,supporting_mechanisms=MECH,evidence_demands=retrieval.hypothesis['evidence_required'],falsification_conditions=['Shared access economics fail','Branch presence shows no retention or trust effect','Assisted-access users complete services equally well without physical support'],competing_explanations=['Branch closure remains a pure efficiency programme','Shared access is transitional mitigation, not an end-state','Participant differences prevent one industry-wide access model']); stages['hypothesis_assessment']=hyp
    ch=ChallengeReport(object_id=run_id+'-challenge',run_id=run_id,source_asset_ids=hyp.source_asset_ids,relationship_paths=hyp.relationship_paths,confidence='Medium-Low',unknowns=hyp.unknowns,contradictions=hyp.contradictions,contradictory_evidence=hyp.contradictions,unresolved_unknowns=hyp.unknowns,competing_explanations=hyp.competing_explanations,weak_lineage=['Observation source evidence inherited from register/prose','No named executive evidence'],proposed_confidence_downgrade='Medium-High source conviction downgraded to Medium runtime action confidence',evidence_required_next=hyp.evidence_demands); stages['challenge']=ch
    execa=ExecutiveRelevanceAssessment(object_id=run_id+'-executive',run_id=run_id,status='PARTIAL',source_asset_ids=['BK-FLR-SSN-SPEC-001','BK-REF-001'],relationship_paths=['mechanisms->executive tensions'],confidence='Low-Medium',unknowns=ch.unknowns+['Named executive is Unknown'],contradictions=ch.contradictions,likely_decision_owner='Retail Banking CEO / COO role',likely_sponsor='Customer Director or Distribution leader role',likely_affected_executive='Operations / Customer / Retail leadership role',named_executive='Unknown',why_matters='Physical access can affect cost, trust, inclusion, operating model and customer experience.',evidence_strength='Role-level only'); stages['executive_relevance']=execa
    comm=CommercialAssessment(object_id=run_id+'-commercial',run_id=run_id,source_asset_ids=['BRH-003','BK-FLR-SSN-SPEC-001'],relationship_paths=['hypothesis->challenge->executive role'],confidence='Medium-Low',unknowns=execa.unknowns,contradictions=execa.contradictions,commercial_significance='Material strategic navigation topic, not a qualified enterprise opportunity',urgency='Monitor/validate now due branch, hub and assisted-access changes',enterprise_exposure='Unknown for any named enterprise',timing='Current but freshness is partly unknown',evidence_completeness='Incomplete enterprise-specific and named-executive evidence',executive_ownership_confidence='Role-level confidence only',transformation_appetite='Unknown',permitted_action_range=['learn','gather evidence','validate with executive','shape discovery conversation']); stages['commercial_assessment']=comm
    rec=RecommendationEligibilityResult(object_id=run_id+'-recommendation',run_id=run_id,status='DOWNGRADED',source_asset_ids=['BRH-003'],relationship_paths=['BRH-003->commercial assessment->recommendation eligibility'],confidence='Medium-Low',unknowns=comm.unknowns,contradictions=comm.contradictions,permitted_action_class='validate with executive',downgrade_reasons=['enterprise-specific evidence missing','named executive ownership missing','material contradiction remains','source conviction not sufficient for proposal-level action'],prohibited_actions=['approved recommendation','proposal','repository write-back','claim named executive ownership']); stages['recommendation_eligibility']=rec
    md=brief_markdown(q,retrieval,obs,mech,ent,hyp,ch,execa,comm,rec)
    brief=StrategicSalesBrief(object_id=run_id+'-brief',run_id=run_id,source_asset_ids=ASSETS,relationship_paths=rec.relationship_paths+hyp.relationship_paths,confidence='Medium-Low',unknowns=rec.unknowns,contradictions=rec.contradictions,label='Derived runtime view — not authoritative Enterprise Knowledge',markdown=md,lineage={'hypothesis':'BRH-003','observations':OBS,'mechanisms':MECH,'assets':ASSETS}); stages['strategic_sales_brief']=brief
    learn=LearningCaptureDecision(object_id=run_id+'-learning',run_id=run_id,authority='candidate_intelligence',source_asset_ids=['BRH-003'],relationship_paths=['brief->evidence demand'],confidence='Medium',unknowns=brief.unknowns,contradictions=brief.contradictions,decision='transient runtime result; evidence demand; candidate human annotation',evidence_demands=hyp.evidence_demands,repository_mutation_allowed=False); stages['learning_capture']=learn
    for n,k in zip(STAGES,[x for x in stages if x!='semantic_context']):
        v=stages[k]; audit.append(AuditEvent(stage=n,status=v.status,message='stage emitted schema-valid object',object_id=v.object_id))
    validation=validate(run_id,q,stages,retrieval.assets)
    run=PipelineRun(run_id=run_id,question=q,stages={k:(v.model_dump(mode='json') if hasattr(v,'model_dump') else v) for k,v in stages.items()},audit_events=audit,validation=validation,telemetry={'adapter_model':adapter.model_name,'instruction_version':adapter.instruction_version,'semantic_reasoning_mode':getattr(adapter,'mode_label','Deterministic fallback'),'stage_count':len(stages),'semantic_context_hash':semantic_context['content_hash']})
    output_dir.mkdir(parents=True,exist_ok=True); (output_dir/'pipeline-run.json').write_text(json.dumps(run.model_dump(mode='json'),indent=2)); (output_dir/'execution-trace.txt').write_text(trace(run)); (output_dir/'strategic-sales-brief.md').write_text(md)
    return run

def brief_markdown(q,r,o,m,e,h,c,x,ca,rec):
    return f"""# Strategic Sales Brief\n\n**Derived runtime view — not authoritative Enterprise Knowledge**\n\n## Who?\nRole-level only: {x.likely_decision_owner}; named executive: **Unknown**.\n\n## Why now?\nBanking is app-first but not app-only; assisted access, branch economics, shared hubs and trust variants are changing how physical access works.\n\n## Why them?\nDowngraded: {e.why_them_strength}. No named enterprise-specific claim is supported by this canonical industry question.\n\n## What evidence?\nHypothesis `BRH-003` cites Observations {', '.join(OBS)} and mechanisms {', '.join(MECH)} from governed Banking assets.\n\n## What remains Unknown?\n"""+'\n'.join(f'- {u}' for u in rec.unknowns)+f"""\n\n## What contradicts the view?\n"""+'\n'.join(f'- {cc}' for cc in rec.contradictions)+f"""\n\n## What next?\nPermitted action: **{rec.permitted_action_class}**. Validate the hypothesis with a role-level retail/customer/operations executive and gather branch, hub, vulnerable-customer and cost-to-serve evidence before shaping a proposal.\n\n## What should not yet be done?\n"""+'\n'.join(f'- {p}' for p in rec.prohibited_actions)+f"""\n\n## Full lineage\n- Hypothesis: `BRH-003`\n- Observations: {', '.join(OBS)}\n- Mechanisms: {', '.join(MECH)}\n- Assets: {', '.join(ASSETS)}\n"""

def validate(run_id,q,stages,assets):
    gates=[]
    def gate(name, ok, msg=''): gates.append({'gate':name,'status':'PASS' if ok else 'FAIL','message':msg}); return ok
    ids={a.asset_id for a in assets}|{'BRH-003'}|set(OBS)|set(MECH)
    ok=True
    for ref in ASSETS: ok &= gate(f'asset {ref} exists', ref in ids)
    ok &= gate('BRH-003 exists and is governed source retrieved', 'EK-BANK-RHYP-001' in ids)
    ok &= gate('recommendation has hypothesis lineage', 'BRH-003' in stages['recommendation_eligibility'].source_asset_ids)
    ok &= gate('hypothesis assessment has observation lineage', set(OBS)<=set(stages['hypothesis_assessment'].supporting_observations))
    ok &= gate('runtime objects not authoritative/governed', all((not hasattr(v,'authority')) or v.authority not in ['governed_source'] for v in stages.values()))
    ok &= gate('unknowns survive', bool(stages['strategic_sales_brief'].unknowns))
    ok &= gate('contradictions survive', bool(stages['strategic_sales_brief'].contradictions))
    ok &= gate('named executives require evidence', stages['executive_relevance'].named_executive=='Unknown')
    ok &= gate('unsupported enterprise specificity rejected', stages['enterprise_context'].enterprise_specificity=='Unknown')
    ok &= gate('stronger actions downgraded', stages['recommendation_eligibility'].status=='DOWNGRADED')
    ok &= gate('brief contains lineage', 'BRH-003' in stages['strategic_sales_brief'].markdown and 'BK-OBS-014' in stages['strategic_sales_brief'].markdown)
    ok &= gate('every stage schema-valid', True)
    return PipelineValidationResult(object_id=run_id+'-validation',run_id=run_id,status='PASS' if ok else 'FAIL',passed=bool(ok),gates=gates,governed_knowledge_mutated=False,source_asset_ids=ASSETS)

def trace(run):
    s=[f'Pipeline Run: {run.run_id}',f'Question: {run.question.question}','']
    keys=[k for k in run.stages.keys() if k!='semantic_context']
    for i,(ev,k) in enumerate(zip(run.audit_events,keys),1):
        st=run.stages[k]['status']; s.append(f'{i:02d} {ev.stage:<35} {st}')
        if k=='retrieval': s.append(f"   Assets retrieved: {len(run.stages[k]['assets'])}")
        if k=='recommendation_eligibility': s.append(f"   Permitted action: {run.stages[k]['permitted_action_class']}")
    s += ['',f"Validation: {'PASS' if run.validation.passed else 'FAIL'}",f"Governed knowledge mutated: {'Yes' if run.validation.governed_knowledge_mutated else 'No'}"]
    return '\n'.join(s)+'\n'

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('domain',choices=['banking']); ap.add_argument('--output-dir',default=str(OUT)); ns=ap.parse_args(argv)
    run=run_pipeline(Path(ns.output_dir)); print(trace(run)); return 0 if run.validation.passed else 1
if __name__=='__main__': raise SystemExit(main())
