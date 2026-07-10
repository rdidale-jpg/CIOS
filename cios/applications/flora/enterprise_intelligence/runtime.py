from __future__ import annotations
import json, time, uuid
from typing import Any
from cios.applications.flora.storage import atomic_write_text, data_path
from .models import ReasoningRequestV1, now_iso, stable_hash, SCHEMA_VERSION, PROFILE_ID
from .profile import PROFILE
from .provider import provider_from_env, LLMProviderError
from .retrieval import BoundedTwinRetrievalService
from .validator import ClaimValidator

SECTIONS=['Executive Summary','What Has Changed','Material Pressures','How MOD Works','Change Portfolio','Decision and Stakeholder Landscape','Commercial Relevance','Unknowns and Contradictions','Recommended Next Moves','Evidence and Lineage']

def output_schema():
    return {'name':'ExecutiveCommercialBriefV1','strict':True,'required':['brief_id','enterprise_id','twin_version','reasoning_profile','generated_at','evidence_cut_off','executive_summary','material_pressures','unknowns','contradictions','recommended_next_moves','lineage_manifest','validation_status']}

def _theme(statement):
    s=statement.casefold()
    for t in ['affordability and productivity','readiness and availability','programme-to-operational-effect conversion','data and AI adoption','industrial and supplier resilience','workforce and skills','decision ownership','commercial accessibility']:
        if any(w in s for w in t.replace(' and ',',').replace('-to-',',').split(',')): return t.title()
    return 'Enterprise Pressure'

def deterministic_brief(request, package, reason='deterministic evidence-bounded fallback'):
    obs=[i for i in package.selected_observations if i.object_class=='observation']
    pressures=[]
    for i in obs[:8]:
        pressures.append({'title':_theme(i.statement),'situation':i.statement,'why_now':'Included because bounded retrieval ranked it as material, current, decision-relevant or commercially relevant within the evidence package.','affected_areas':i.linked_objects or [],'business_or_operational_consequence':'Commercial or operating consequence requires validation against the cited governed evidence.','supporting_observation_ids':[i.stable_id],'supporting_evidence_ids':list(i.lineage),'linked_unknown_ids':[u.stable_id for u in package.selected_unknowns[:2]],'linked_contradiction_ids':[c.stable_id for c in package.selected_contradictions[:2]],'confidence':'medium' if int(i.confidence or 0)<80 else 'high','freshness':i.freshness,'interpretation_status':'transient_interpretation','commercial_implication':'Use as a learning and validation route; do not claim a specific opportunity until ownership, route and incumbent constraints are evidenced.'})
    if not pressures:
        pressures=[{'title':'Evidence-limited MOD view','situation':'The governed evidence package does not contain enough material observations for a strong executive interpretation.','why_now':'A strategic sales director should avoid generic claims until evidence improves.','affected_areas':[],'business_or_operational_consequence':'Low conviction.','supporting_observation_ids':[],'supporting_evidence_ids':[],'linked_unknown_ids':[u.stable_id for u in package.selected_unknowns],'linked_contradiction_ids':[c.stable_id for c in package.selected_contradictions],'confidence':'low','freshness':package.freshness,'interpretation_status':'evidence_limited','commercial_implication':'Learn and validate first.'}]
    themes=list(dict.fromkeys(p['title'] for p in pressures))
    brief={'brief_id':'brief-'+uuid.uuid4().hex[:16],'enterprise_id':package.enterprise_id,'twin_version':request.twin_version,'reasoning_profile':PROFILE_ID,'generated_at':now_iso(),'evidence_cut_off':request.evidence_cut_off,
    'executive_summary':{'what_is_happening':f"MOD is showing governed signals around {', '.join(themes[:4])}.",'why_it_matters':'These themes affect where reinvention pressure, decision ownership and commercial access may concentrate. Conviction remains bounded by cited evidence only.','what_changed':'Recent or material accepted observations and projections have been prioritised over record count.','what_deserves_attention':themes[:5],'conviction':'Higher where multiple governed observations and evidence IDs align; lower where Unknowns, contradictions, human knowledge or projections are the basis.'},
    'enterprise_situation':'Evidence-bounded interpretation generated from the governed Twin only; not canonical memory.', 'material_changes':[{'statement':p['situation'],'evidence':p['supporting_observation_ids']} for p in pressures[:5]], 'material_pressures':pressures,
    'operating_model_summary':'How MOD works is summarised only from selected governed entities, relationships, programmes and cited observations.', 'change_portfolio':[{'initiative':i.statement,'evidence':[i.stable_id],'confidence':i.confidence} for i in package.selected_programmes_and_initiatives[:8]],
    'stakeholder_assessments':[{'person_or_role':i.statement.split(':',1)[-1].strip() if ':' in i.statement else i.statement,'relevance':'Potential decision or operating relevance in the bounded Twin.','likely_authority':'Validate authority before claiming ownership.','evidence_basis':[i.stable_id], 'confidence':i.confidence,'unknowns':[u.stable_id for u in package.selected_unknowns[:2]],'relationship_to_pressure':'Linked through selected entity/relationship evidence.','recommended_engagement_posture':'learn → validate → shape → engage'} for i in package.selected_entities_and_relationships[:6]],
    'commercial_relevance_assessments':[{'enterprise_need':p['title'],'materiality':p['confidence'],'why_now':p['why_now'],'likely_buyer_or_problem_owner':'Validate named owner in governed evidence before asserting.','plausible_intervention':'Evidence-backed discovery, operating model validation, data/AI or productivity shaping where supported.','route_to_market':'Not yet evidenced; inspect lineage and validate procurement/access route.','incumbent_or_access_constraints':'Do not assume displacement; identify incumbent constraints in follow-up.','addressability':'plausible_but_unconfirmed','evidence_basis':p['supporting_observation_ids']+p['supporting_evidence_ids'],'unknowns':p['linked_unknown_ids'],'contradictions':p['linked_contradiction_ids'],'recommended_posture':'learn → validate → shape → engage','what_not_to_claim':'Do not claim budget, sponsor, procurement route or solution fit without cited evidence.'} for p in pressures[:6]],
    'unknowns':[{'unknown_id':u.stable_id,'statement':u.statement,'truth_status':'unknown','confidence':u.confidence,'lineage':list(u.lineage)} for u in package.selected_unknowns], 'contradictions':[{'contradiction_id':c.stable_id,'statement':c.statement,'truth_status':c.truth_status,'confidence':c.confidence,'lineage':list(c.lineage)} for c in package.selected_contradictions],
    'recommended_next_moves':[{'action':'Validate the highest-material pressure with the cited owner or operating lead.','who':'Strategic sales director or trusted adviser','why_now':p['why_now'],'why_them':'They can test commercial relevance without overstating unsupported claims.','supporting_evidence':p['supporting_observation_ids']+p['supporting_evidence_ids'],'question_to_ask':'Which owner, programme, constraint or outcome does this pressure map to?','evidence_to_seek':'Named owner, funded initiative, procurement route, incumbent position, target outcome.','what_not_to_claim':p['commercial_implication'],'outcome_increasing_conviction':'A governed source confirms owner, timing, consequence and route-to-market.','confidence':p['confidence'],'lineage':p['supporting_observation_ids']+p['supporting_evidence_ids']} for p in pressures[:5]],
    'evidence_limitations':['The model must not use public knowledge outside the evidence package. Human-supplied knowledge and projections remain labelled. Unknowns and contradictions are visible.'], 'overall_confidence':'medium' if obs else 'low', 'lineage_manifest':{'evidence_package_id':package.package_id,'evidence_package_hash':stable_hash(package.to_dict()),'retrieved_object_ids':[i.stable_id for i in package.all_items()]}, 'model_metadata':{'provider':'deterministic-fallback','model':'bounded-local','reason':reason}, 'validation_status':{}}
    return brief

class EnterpriseIntelligenceRuntime:
    def __init__(self, retrieval=None, provider=None, validator=None): self.retrieval=retrieval or BoundedTwinRetrievalService(); self.provider=provider or provider_from_env(); self.validator=validator or ClaimValidator()
    def generate(self, request):
        start=time.time(); package=self.retrieval.retrieve(request); audit={'request_id':request.request_id,'enterprise_id':package.enterprise_id,'twin_version':request.twin_version,'evidence_package_hash':stable_hash(package.to_dict()),'retrieved_object_ids':[i.stable_id for i in package.all_items()],'prompt_version':request.prompt_version_ref,'reasoning_profile':request.reasoning_profile}
        try:
            prompt=json.dumps({'profile':PROFILE,'request':request.to_dict(),'evidence_package':package.to_dict()}, ensure_ascii=False)
            result=self.provider.generate_structured(prompt=prompt, schema=output_schema(), timeout_s=30, token_budget=request.maximum_evidence_volume)
            brief=result.payload; brief.setdefault('model_metadata',{}).update({'provider':result.provider,'model':result.model,'token_usage':result.token_usage,'duration_ms':result.duration_ms})
        except Exception as exc:
            brief=deterministic_brief(request, package, type(exc).__name__+': '+str(exc))
            result=None
        brief=self.validator.validate(brief, package); audit.update({'model_provider':brief.get('model_metadata',{}).get('provider'),'model_name':brief.get('model_metadata',{}).get('model'),'token_usage':brief.get('model_metadata',{}).get('token_usage',{}),'execution_duration_ms':int((time.time()-start)*1000),'validation_outcome':brief.get('validation_status',{}).get('status'),'rejected_claims':brief.get('validation_status',{}).get('rejected_claims',[]),'generated_brief_id':brief.get('brief_id')})
        atomic_write_text(data_path('enterprise_intelligence','audit',request.request_id+'.json'), json.dumps(audit, indent=2, sort_keys=True))
        return {'request':request.to_dict(),'evidence_package':package.to_dict(),'brief':brief,'audit':audit}

def safe_fallback(reason, last_successful_brief=None, evidence_cut_off='', enterprise_id='MOD'):
    return {'title':'Executive Intelligence Brief unavailable','reason':reason,'last_successful_brief':last_successful_brief,'evidence_cut_off':evidence_cut_off,'retry_action':'Retry generation when the reasoning provider is available or use deterministic bounded fallback explicitly.','model_explorer_url':f'/digital-twins/{enterprise_id}/canvas'}
