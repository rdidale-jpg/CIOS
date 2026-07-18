from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

Authority = Literal['governed_source','derived_runtime_assessment','candidate_intelligence','transient_presentation']
Status = Literal['PASS','PARTIAL','DOWNGRADED','FAIL']

def now(): return datetime.now(timezone.utc)

class RuntimeObject(BaseModel):
    model_config = ConfigDict(extra='forbid')
    object_id: str
    object_type: str
    run_id: str
    status: Status = 'PASS'
    authority: Authority
    created_at: datetime = Field(default_factory=now)
    created_by: str = 'flora-banking-prototype'
    source_asset_ids: list[str] = Field(default_factory=list)
    relationship_paths: list[str] = Field(default_factory=list)
    confidence: str = 'Medium'
    unknowns: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    validation_state: str = 'schema_valid'
    persistence_class: str = 'transient_runtime'

class QuestionObject(RuntimeObject):
    object_type: Literal['question']='question'; authority: Authority='derived_runtime_assessment'
    question: str; user_role: str; industry_scope: list[str]; mode: str; required_output: str
class IntentObject(RuntimeObject):
    object_type: Literal['intent']='intent'; authority: Authority='derived_runtime_assessment'
    interpretations: list[str]; progression: str; prohibited_claims: list[str]
class ContextPlan(RuntimeObject):
    object_type: Literal['context_plan']='context_plan'; authority: Authority='derived_runtime_assessment'
    required_asset_classes: list[str]; hypothesis_id: str; observation_ids: list[str]; mechanism_ids: list[str]; manifest_asset_ids: list[str]; required_stages: list[str]; required_output: str
class GovernedAsset(BaseModel):
    asset_id: str; title: str; asset_type: str; status: str; location: str; content_sha256: str; authority: Authority='governed_source'; metadata: dict[str, Any]=Field(default_factory=dict)
class RetrievalSet(RuntimeObject):
    object_type: Literal['retrieval_set']='retrieval_set'; authority: Authority='derived_runtime_assessment'
    assets: list[GovernedAsset]; hypothesis: dict[str, Any]; observations: list[dict[str, Any]]; mechanisms: list[dict[str, Any]]
class ObservationSelection(RuntimeObject):
    object_type: Literal['observation_selection']='observation_selection'; authority: Authority='derived_runtime_assessment'
    selected_observations: list[dict[str, Any]]; missing_evidence: list[str]
class MechanismAssessment(RuntimeObject):
    object_type: Literal['mechanism_assessment']='mechanism_assessment'; authority: Authority='derived_runtime_assessment'
    mechanisms: list[dict[str, Any]]; alternatives: list[str]; applicability_constraints: list[str]
class EnterpriseContextAssessment(RuntimeObject):
    object_type: Literal['enterprise_context_assessment']='enterprise_context_assessment'; authority: Authority='derived_runtime_assessment'
    participant_scope: str; enterprise_specificity: str; why_them_strength: str
class HypothesisAssessment(RuntimeObject):
    object_type: Literal['hypothesis_assessment']='hypothesis_assessment'; authority: Authority='derived_runtime_assessment'
    hypothesis_id: str; original_statement: str; lifecycle_state: str; supporting_observations: list[str]; supporting_mechanisms: list[str]; evidence_demands: list[str]; falsification_conditions: list[str]; competing_explanations: list[str]
class ChallengeReport(RuntimeObject):
    object_type: Literal['challenge_report']='challenge_report'; authority: Authority='derived_runtime_assessment'
    contradictory_evidence: list[str]; unresolved_unknowns: list[str]; competing_explanations: list[str]; weak_lineage: list[str]; proposed_confidence_downgrade: str; evidence_required_next: list[str]
class ExecutiveRelevanceAssessment(RuntimeObject):
    object_type: Literal['executive_relevance_assessment']='executive_relevance_assessment'; authority: Authority='derived_runtime_assessment'
    likely_decision_owner: str; likely_sponsor: str; likely_affected_executive: str; named_executive: str; why_matters: str; evidence_strength: str
class CommercialAssessment(RuntimeObject):
    object_type: Literal['commercial_assessment']='commercial_assessment'; authority: Authority='derived_runtime_assessment'
    commercial_significance: str; urgency: str; enterprise_exposure: str; timing: str; evidence_completeness: str; executive_ownership_confidence: str; transformation_appetite: str; permitted_action_range: list[str]
class RecommendationEligibilityResult(RuntimeObject):
    object_type: Literal['recommendation_eligibility']='recommendation_eligibility'; authority: Authority='derived_runtime_assessment'
    permitted_action_class: str; downgrade_reasons: list[str]; prohibited_actions: list[str]
class StrategicSalesBrief(RuntimeObject):
    object_type: Literal['strategic_sales_brief']='strategic_sales_brief'; authority: Authority='transient_presentation'
    label: str; markdown: str; lineage: dict[str, Any]
class LearningCaptureDecision(RuntimeObject):
    object_type: Literal['learning_capture_decision']='learning_capture_decision'; authority: Authority='candidate_intelligence'
    decision: str; evidence_demands: list[str]; repository_mutation_allowed: bool
class AuditEvent(BaseModel):
    stage: str; status: Status; message: str; object_id: str; created_at: datetime=Field(default_factory=now)
class PipelineValidationResult(RuntimeObject):
    object_type: Literal['pipeline_validation']='pipeline_validation'; authority: Authority='derived_runtime_assessment'
    passed: bool; gates: list[dict[str, str]]; governed_knowledge_mutated: bool
class PipelineRun(BaseModel):
    model_config=ConfigDict(extra='forbid')
    run_id: str; question: QuestionObject; stages: dict[str, Any]; audit_events: list[AuditEvent]; validation: PipelineValidationResult; telemetry: dict[str, Any]
