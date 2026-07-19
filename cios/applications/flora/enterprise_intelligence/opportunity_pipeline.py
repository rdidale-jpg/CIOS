from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

from .pipeline import OBS, MECH, ASSETS, run_pipeline

Horizon = Literal['horizon_1','horizon_2','horizon_3','not_actionable']
Readiness = Literal['Candidate','Evidence building','Ready for executive validation','Ready to shape','Deferred','Rejected']
Confidence = Literal['Low','Medium-Low','Medium','Medium-High','High']

class Unknown(BaseModel):
    what: str
    why_it_matters: str
    evidence_required: str
    decision_constrained: str

class Contradiction(BaseModel):
    scope: str
    effect: str

class HorizonClassification(BaseModel):
    horizon: Horizon
    rationale: str
    supporting_factors: list[str]
    constraining_factors: list[str]
    movement_criteria: list[str]
    human_review_required: bool = True

class CommercialOpportunity(BaseModel):
    model_config = ConfigDict(extra='forbid')
    opportunity_id: str
    object_type: Literal['commercial_opportunity'] = 'commercial_opportunity'
    run_id: str
    status: str
    authority: Literal['derived_runtime'] = 'derived_runtime'
    title: str
    summary: str
    industry: Literal['Banking'] = 'Banking'
    enterprise_id: str = ''
    enterprise_name: str = ''
    participant_type: str
    primary_hypothesis_ids: list[str]
    supporting_observation_ids: list[str]
    supporting_mechanism_ids: list[str]
    supporting_asset_ids: list[str]
    executive_roles: list[str]
    named_executives: list[str] = Field(default_factory=list)
    why_now: str
    why_this_enterprise: str
    commercial_problem: str
    plausible_intervention: str
    horizon: Horizon
    horizon_rationale: HorizonClassification
    recommendation_eligibility: str
    recommended_next_action: str
    stronger_actions_prohibited: list[str]
    confidence: Confidence
    confidence_explanation: str
    evidence_strength: Confidence
    enterprise_specificity: str
    executive_specificity: str
    unknowns: list[Unknown]
    contradictions: list[Contradiction]
    movement_criteria: list[str]
    last_assessed_at: str
    knowledge_snapshot: str
    stale_after: str
    reassessment_trigger: str
    created_at: str
    created_by: str = 'flora-banking-opportunity-pipeline'
    validation_state: str = 'schema_valid'
    persistence_class: Literal['transient_runtime'] = 'transient_runtime'
    readiness: Readiness
    lineage: dict[str, Any]
    human_supplied_knowledge: list[dict[str, str]] = Field(default_factory=list)

class OpportunityPipelineRun(BaseModel):
    pipeline_id: str
    industry: Literal['Banking'] = 'Banking'
    generated_at: str
    knowledge_snapshot: str
    reasoning_mode: str
    opportunities: list[CommercialOpportunity]
    portfolio_summary: dict[str, int]
    global_unknowns: list[str]
    global_contradictions: list[str]
    validation_state: str = 'schema_valid'

def _now() -> datetime:
    return datetime.now(timezone.utc)

def classify(*, enterprise_specificity: str, timing: str, programme: bool, roles: bool, contradictions: bool, eligibility: str, confidence: Confidence) -> HorizonClassification:
    supporting=[]; constraints=[]
    if enterprise_specificity == 'High': supporting.append('enterprise-specific pressure is evidenced')
    else: constraints.append('enterprise specificity is incomplete')
    if timing == 'current': supporting.append('current timing evidence is present')
    else: constraints.append('near-term timing evidence is weak')
    if programme: supporting.append('programme or transformation activity is evidenced')
    else: constraints.append('active programme evidence is not yet confirmed')
    if roles: supporting.append('executive role relevance is supported')
    else: constraints.append('executive ownership is unknown')
    if contradictions: constraints.append('material contradiction constrains action')
    if eligibility in {'defer','reject'}:
        return HorizonClassification(horizon='not_actionable', rationale='Recommendation Eligibility only permits defer or reject, so Flora must not force this candidate into a horizon.', supporting_factors=supporting, constraining_factors=constraints, movement_criteria=['Resolve the contradiction or add governed evidence of relevance before reconsidering.'])
    if enterprise_specificity == 'High' and timing == 'current' and programme and roles and not contradictions and eligibility in {'validate with executive','prepare executive provocation','shape discovery conversation','shape workshop'}:
        return HorizonClassification(horizon='horizon_1', rationale='Sufficient enterprise, timing, programme and role evidence exists for active but still proportionate engagement.', supporting_factors=supporting, constraining_factors=constraints, movement_criteria=['Moves to Shape when human review confirms executive role, sufficient brief evidence and permitted shaping action.','Downgrade if evidence becomes stale, the programme closes or ownership changes.'])
    if timing == 'long_term' or confidence == 'Low':
        return HorizonClassification(horizon='horizon_3', rationale='The structural reinvention logic is useful, but near-term buying evidence is weak.', supporting_factors=supporting, constraining_factors=constraints, movement_criteria=['Moves to Horizon 2 when enterprise exposure, relevant programme evidence or accountable executive role is detected.','Downgrade to not actionable if enterprise relevance is disproven.'])
    return HorizonClassification(horizon='horizon_2', rationale='The commercial logic is promising, but material evidence about enterprise specificity, timing, economics or ownership remains incomplete.', supporting_factors=supporting, constraining_factors=constraints, movement_criteria=['Moves to Horizon 1 when active transformation, accountable sponsor and enterprise economics are evidenced.','Moves to Horizon 3 if timing weakens or programme evidence does not appear.'])

def _unknown(text: str, evidence: str, decision: str) -> Unknown:
    return Unknown(what=text, why_it_matters='It limits commercial judgement and prevents unsupported escalation.', evidence_required=evidence, decision_constrained=decision)

def _opp(base: dict[str, Any], run_id: str, generated: datetime, mode: str) -> CommercialOpportunity:
    hc=classify(**base.pop('classification'))
    stale=(generated+timedelta(days=90)).date().isoformat()
    supplied_lineage = dict(base.pop('lineage', {}) or {})
    supplied_lineage.update({'path':['Evidence','Observation','Mechanism','Enterprise Context','Reinvention Hypothesis','Commercial Opportunity','Horizon','Next Action'],'reasoning_mode':mode})
    return CommercialOpportunity(run_id=run_id, horizon=hc.horizon, horizon_rationale=hc, movement_criteria=hc.movement_criteria, created_at=generated.isoformat(timespec='seconds'), last_assessed_at=generated.isoformat(timespec='seconds'), stale_after=stale, knowledge_snapshot='Banking governed intelligence snapshot derived from ADR-024 / FEIR-001 / EIRP-001 aligned runtime assets', reassessment_trigger='Reassess when new observations, programme evidence, contradictions, executive ownership or human-supplied account knowledge appear.', lineage=supplied_lineage, **base)

def generate_banking_opportunity_pipeline() -> OpportunityPipelineRun:
    source=run_pipeline(); run_id=source.run_id; s=source.stages; sem=s.get('semantic_context', {}); generated=_now(); mode=source.telemetry.get('semantic_reasoning_mode','Deterministic fallback')
    common_unknowns=[_unknown('Named executive owner or sponsor is not evidenced','Governed executive ownership evidence or labelled human account knowledge','named outreach and workshop shaping'), _unknown('Enterprise operating economics are incomplete','Branch, hub, channel-cost or customer-outcome economics','proposal-level action')]
    base_lineage={'assets':ASSETS,'observations':OBS,'mechanisms':MECH,'hypotheses':['BRH-003'],'semantic_context_hash':source.telemetry.get('semantic_context_hash','')}
    templates=[
        dict(opportunity_id='BK-OPP-001',status='Candidate',title='Redesign physical and assisted access around a mixed distribution model',summary='Branch withdrawal, shared hubs and assisted access create a current operating-model question for large retail incumbents where trust, inclusion and cost collide.',enterprise_id='',enterprise_name='',participant_type='Large retail incumbent',primary_hypothesis_ids=['BRH-003'],supporting_observation_ids=OBS,supporting_mechanism_ids=MECH,supporting_asset_ids=ASSETS,executive_roles=['Chief Operating Officer','Chief Customer Officer','Retail Banking Director'],why_now='Branch withdrawal, banking hubs, Consumer Duty evidence demands and cost simplification are converging now.',why_this_enterprise='Governed knowledge supports this at large retail incumbent participant-type level; Flora does not name a bank without account-specific evidence.',commercial_problem='The bank must reduce cost and simplify channels while maintaining trust and assisted access for customers who cannot be served by app-only journeys.',plausible_intervention='Operating-model discovery and branch/hub economics assessment before any proposal.',recommendation_eligibility='gather evidence',recommended_next_action='Validate operating economics and executive ownership with the account team.',stronger_actions_prohibited=['do not prepare a proposal','do not claim named executive ownership','do not assert bank-specific urgency'],confidence='Medium',confidence_explanation='Multiple governed observations and mechanisms support the thesis, but account economics and ownership are unknown.',evidence_strength='Medium',enterprise_specificity='Participant-type supported; named enterprise unsupported',executive_specificity='Role-level only',unknowns=common_unknowns,contradictions=[Contradiction(scope='Participant variants', effect='For some banks physical access is a cost burden; for others it remains a trust asset.')],readiness='Evidence building',lineage=base_lineage,classification=dict(enterprise_specificity='Medium',timing='current',programme=False,roles=True,contradictions=True,eligibility='gather evidence',confidence='Medium')),
        dict(opportunity_id='BK-OPP-002',status='Candidate',title='Use mutual access and member-service positioning as a trust advantage',summary='Mutual and building-society participants may treat access differently from app-first challengers because member trust and local service can be part of the proposition.',enterprise_id='BK-ENT-003',enterprise_name='Nationwide / Virgin Money',participant_type='Mutual / building society and acquired challenger context',primary_hypothesis_ids=['BRH-003'],supporting_observation_ids=['BK-OBS-014','BK-OBS-015','BK-OBS-029'],supporting_mechanism_ids=['BM-04','BM-15'],supporting_asset_ids=ASSETS,executive_roles=['Retail Banking Director','Chief Customer Officer','Distribution leader'],why_now='Shared access, assisted journeys and member-service expectations are active enough to validate whether trust can be an operating-model advantage.',why_this_enterprise='BRH-003 validation identifies Nationwide and Lloyds variants, but enterprise-specific economics and ownership remain partial.',commercial_problem='Physical and assisted access may be expensive, but could also protect trust, inclusion and differentiated member value.',plausible_intervention='Executive discovery on member access, vulnerable-customer outcomes and hub/branch economics.',recommendation_eligibility='validate with executive',recommended_next_action='Validate whether access strategy is a live executive concern and what evidence the account team can supply.',stronger_actions_prohibited=['do not infer named sponsor','do not overstate integration timing','do not create a proposal'],confidence='Medium-Low',confidence_explanation='Enterprise Twin coverage exists but the specific commercial opportunity remains constrained by missing programme and economics evidence.',evidence_strength='Medium',enterprise_specificity='Partial enterprise context',executive_specificity='Role-level only',unknowns=common_unknowns,contradictions=[Contradiction(scope='Acquisition and participant mix', effect='Virgin Money context may differ from mutual member-service logic.')],readiness='Ready for executive validation',lineage=base_lineage,classification=dict(enterprise_specificity='Medium',timing='current',programme=False,roles=True,contradictions=True,eligibility='validate with executive',confidence='Medium-Low')),
        dict(opportunity_id='BK-OPP-003',status='Candidate',title='Test whether app-first challengers need assisted-access partnerships',summary='Digital challengers may not need proprietary branches, but structural inclusion and trust pressures may create a partnership or shared-access question.',enterprise_id='',enterprise_name='',participant_type='Digital challenger bank',primary_hypothesis_ids=['BRH-003'],supporting_observation_ids=['BK-OBS-016','BK-OBS-029','BK-OBS-047'],supporting_mechanism_ids=['BM-14','BM-15'],supporting_asset_ids=ASSETS,executive_roles=['Chief Customer Officer','Chief Operating Officer','Chief Product Officer'],why_now='The long-term access model is changing, but near-term challenger buying evidence is weak.',why_this_enterprise='Governed knowledge supports participant-type exploration for Monzo and Starling-style challengers, not named account action.',commercial_problem='App-first models may still need credible pathways for vulnerable customers, cash-dependent moments or trust recovery without owning a branch estate.',plausible_intervention='Future distribution model provocation and monitoring, not proposal development.',recommendation_eligibility='monitor',recommended_next_action='Monitor for governed evidence of assisted-access programmes or partnership decisions.',stronger_actions_prohibited=['do not position a workshop as needed','do not infer enterprise exposure','do not propose branch strategy'],confidence='Low',confidence_explanation='Structural logic exists, but timing, programme and enterprise specificity are weak.',evidence_strength='Medium-Low',enterprise_specificity='Participant-type only',executive_specificity='Role-level inferred',unknowns=[_unknown('Challenger exposure to assisted-access demand is unknown','Participant-specific customer-outcome or programme evidence','active engagement')]+common_unknowns[:1],contradictions=[Contradiction(scope='Business model', effect='App-first economics may reduce relevance of physical access compared with incumbents.')],readiness='Candidate',lineage=base_lineage,classification=dict(enterprise_specificity='Low',timing='long_term',programme=False,roles=True,contradictions=True,eligibility='monitor',confidence='Low')),
        dict(opportunity_id='BK-OPP-004',status='Candidate',title='Prepare executive provocation on customer-outcome evidence for distribution change',summary='Consumer-outcome evidence can turn distribution decisions from cost takeout into an executive accountability issue.',enterprise_id='',enterprise_name='',participant_type='UK retail banking participant',primary_hypothesis_ids=['BRH-003'],supporting_observation_ids=['BK-OBS-014','BK-OBS-029','BK-OBS-047'],supporting_mechanism_ids=['BM-04','BM-15'],supporting_asset_ids=ASSETS,executive_roles=['Chief Customer Officer','Chief Risk Officer','Retail Banking Director'],why_now='Outcome evidence, inclusion and assisted access are active constraints on channel simplification.',why_this_enterprise='Supported at industry and participant-type level; enterprise naming requires governed outcome or programme evidence.',commercial_problem='Executives need to prove that channel changes improve or protect outcomes, not only reduce cost.',plausible_intervention='Customer-outcome evidence design and executive provocation.',recommendation_eligibility='prepare executive provocation',recommended_next_action='Build an evidence demand for customer outcomes and test it with an account team or executive.',stronger_actions_prohibited=['do not claim compliance failure','do not name an executive','do not imply proposal-readiness'],confidence='Medium',confidence_explanation='The role-level commercial problem is well supported; enterprise specificity remains incomplete.',evidence_strength='Medium',enterprise_specificity='Participant-type only',executive_specificity='Role-level only',unknowns=common_unknowns,contradictions=[],readiness='Ready for executive validation',lineage=base_lineage,classification=dict(enterprise_specificity='Medium',timing='current',programme=False,roles=True,contradictions=False,eligibility='prepare executive provocation',confidence='Medium')),
        dict(opportunity_id='BK-OPP-005',status='Candidate',title='Explore shared infrastructure as future distribution resilience',summary='Banking hubs and shared access may become structural trust infrastructure, but buying evidence is still early.',enterprise_id='',enterprise_name='',participant_type='Shared-access ecosystem participant',primary_hypothesis_ids=['BRH-003'],supporting_observation_ids=['BK-OBS-015','BK-OBS-016'],supporting_mechanism_ids=['BM-14','BM-04'],supporting_asset_ids=ASSETS,executive_roles=['Chief Operating Officer','Distribution leader','Strategy Director'],why_now='Shared access is visible now, but its durable economics and ownership model remain unresolved.',why_this_enterprise='Supported at ecosystem and participant-type level, not as a named bank opportunity.',commercial_problem='Participants may need to decide whether shared access is temporary mitigation or future operating infrastructure.',plausible_intervention='Thought leadership, future-enterprise modelling and monitoring.',recommendation_eligibility='learn',recommended_next_action='Develop a learning agenda for shared access economics and governance.',stronger_actions_prohibited=['do not sell transformation roadmap','do not assert near-term buying intent','do not name a bank'],confidence='Medium-Low',confidence_explanation='Governed mechanisms support the structural possibility, but timing and enterprise programme evidence are weak.',evidence_strength='Medium-Low',enterprise_specificity='Participant-type only',executive_specificity='Role-level only',unknowns=common_unknowns,contradictions=[Contradiction(scope='Time horizon', effect='Shared access may be transitional rather than structural.')],readiness='Candidate',lineage=base_lineage,classification=dict(enterprise_specificity='Low',timing='long_term',programme=False,roles=True,contradictions=True,eligibility='learn',confidence='Medium-Low')),
        dict(opportunity_id='BK-OPP-006',status='Deferred',title='Do not pursue unsupported named-bank physical access claims',summary='Some listed banks have insufficient governed account-level evidence for a commercial opportunity and should not be forced into the pipeline.',enterprise_id='',enterprise_name='',participant_type='Unsupported named-bank specificity',primary_hypothesis_ids=['BRH-003'],supporting_observation_ids=OBS[:2],supporting_mechanism_ids=['BM-04'],supporting_asset_ids=ASSETS,executive_roles=['Unknown role until account evidence is supplied'],why_now='There is industry change, but not enough evidence to support a named-enterprise claim.',why_this_enterprise='No governed Enterprise Twin or comparison coverage is sufficient for a specific claim in this runtime candidate.',commercial_problem='Fabricated specificity would create false precision and unsafe sales action.',plausible_intervention='Defer and gather governed enterprise evidence.',recommendation_eligibility='defer',recommended_next_action='Record the evidence demand; do not promote to an opportunity until account evidence exists.',stronger_actions_prohibited=['do not name a bank','do not infer executive ownership','do not shape a brief'],confidence='Low',confidence_explanation='Evidence is too weak for enterprise-level action.',evidence_strength='Low',enterprise_specificity='Unsupported',executive_specificity='Unsupported',unknowns=[_unknown('Enterprise exposure is unsupported','Authoritative Enterprise Twin evidence, programme evidence or labelled human knowledge','all commercial action')],contradictions=[Contradiction(scope='Safety', effect='Opportunity would require fabricated specificity.')],readiness='Deferred',lineage=base_lineage,classification=dict(enterprise_specificity='Low',timing='weak',programme=False,roles=False,contradictions=True,eligibility='defer',confidence='Low')),
    ]
    opps=[_opp(t, run_id, generated, mode) for t in templates]
    counts={'horizon_1_count':sum(o.horizon=='horizon_1' for o in opps),'horizon_2_count':sum(o.horizon=='horizon_2' for o in opps),'horizon_3_count':sum(o.horizon=='horizon_3' for o in opps),'not_actionable_count':sum(o.horizon=='not_actionable' for o in opps)}
    return OpportunityPipelineRun(pipeline_id='BK-OPP-PIPE-'+run_id, generated_at=generated.isoformat(timespec='seconds'), knowledge_snapshot=';'.join(ASSETS), reasoning_mode=mode, opportunities=opps, portfolio_summary=counts, global_unknowns=sorted({u.what for o in opps for u in o.unknowns}), global_contradictions=sorted({c.effect for o in opps for c in o.contradictions}))
