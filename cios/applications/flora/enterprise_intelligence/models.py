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

# Compatibility contract for the Flora Enterprise Intelligence reasoning runtime.
# The Banking vertical-slice models above are runtime objects used by the CLI
# pipeline.  The deployed web service still serves the executive reasoning
# route, whose importer expects these bounded request/evidence contracts.
SCHEMA_VERSION = 'enterprise_intelligence_v1'
PROFILE_ID = 'strategic_sales_director_v1'

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def stable_hash(value: Any) -> str:
    import hashlib, json
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode('utf-8')).hexdigest()

class ReasoningRequestV1(BaseModel):
    model_config = ConfigDict(extra='forbid')
    request_id: str
    enterprise_id: str
    workspace_id: str
    requested_by: str
    twin_version: str = 'accepted'
    evidence_cut_off: str = ''
    maximum_evidence_volume: int = 12000
    prompt_version_ref: str = 'executive_commercial_brief_prompt_v1'
    reasoning_profile: str = PROFILE_ID
    schema_version: str = SCHEMA_VERSION
    created_at: str = Field(default_factory=now_iso)

    @classmethod
    def create(
        cls,
        enterprise_id: str,
        workspace_id: str,
        requested_by: str,
        *,
        evidence_cut_off: str = '',
        maximum_evidence_volume: int = 12000,
        twin_version: str = 'accepted',
        prompt_version_ref: str = 'executive_commercial_brief_prompt_v1',
        reasoning_profile: str = PROFILE_ID,
    ) -> 'ReasoningRequestV1':
        return cls(
            request_id='rr-' + stable_hash({'enterprise_id': enterprise_id, 'workspace_id': workspace_id, 'requested_by': requested_by, 'created_at': now_iso()})[:16],
            enterprise_id=enterprise_id,
            workspace_id=workspace_id,
            requested_by=requested_by,
            evidence_cut_off=evidence_cut_off,
            maximum_evidence_volume=maximum_evidence_volume,
            twin_version=twin_version,
            prompt_version_ref=prompt_version_ref,
            reasoning_profile=reasoning_profile,
        )

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

class EvidencePackageItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    stable_id: str
    object_class: str
    statement: str
    truth_status: str
    confidence: Any = ''
    freshness: str = ''
    lineage: tuple[str, ...] = ()
    linked_objects: tuple[str, ...] = ()
    source_location: str = ''
    enterprise_id: str = ''

    def __init__(self, stable_id: str, object_class: str, statement: str, truth_status: str, confidence: Any = '', freshness: str = '', lineage: tuple[str, ...] = (), linked_objects: tuple[str, ...] = (), source_location: str = '', enterprise_id: str = ''):
        super().__init__(stable_id=stable_id, object_class=object_class, statement=statement, truth_status=truth_status, confidence=confidence, freshness=freshness, lineage=tuple(lineage), linked_objects=tuple(linked_objects), source_location=source_location, enterprise_id=enterprise_id)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

class EvidencePackageV1(BaseModel):
    model_config = ConfigDict(extra='forbid')
    package_id: str
    enterprise_id: str
    enterprise_context: dict[str, Any]
    twin_version: str
    evidence_cut_off: str
    source_scope: str
    selected_observations: tuple[EvidencePackageItem, ...] = ()
    selected_entities_and_relationships: tuple[EvidencePackageItem, ...] = ()
    selected_programmes_and_initiatives: tuple[EvidencePackageItem, ...] = ()
    selected_unknowns: tuple[EvidencePackageItem, ...] = ()
    selected_contradictions: tuple[EvidencePackageItem, ...] = ()
    selected_human_supplied_knowledge: tuple[EvidencePackageItem, ...] = ()
    selected_projections: tuple[EvidencePackageItem, ...] = ()
    lineage_manifest: tuple[str, ...] = ()
    freshness: str = 'current'
    retrieval_strategy: str = 'bounded'
    retrieval_notes: tuple[str, ...] = ()

    def __init__(self, package_id: str, enterprise_id: str, enterprise_context: dict[str, Any], twin_version: str, evidence_cut_off: str, source_scope: str, selected_observations: tuple[EvidencePackageItem, ...] = (), selected_entities_and_relationships: tuple[EvidencePackageItem, ...] = (), selected_programmes_and_initiatives: tuple[EvidencePackageItem, ...] = (), selected_unknowns: tuple[EvidencePackageItem, ...] = (), selected_contradictions: tuple[EvidencePackageItem, ...] = (), selected_human_supplied_knowledge: tuple[EvidencePackageItem, ...] = (), selected_projections: tuple[EvidencePackageItem, ...] = (), lineage_manifest: tuple[str, ...] = (), freshness: str = 'current', retrieval_strategy: str = 'bounded', retrieval_notes: tuple[str, ...] = ()):
        super().__init__(package_id=package_id, enterprise_id=enterprise_id, enterprise_context=enterprise_context, twin_version=twin_version, evidence_cut_off=evidence_cut_off, source_scope=source_scope, selected_observations=tuple(selected_observations), selected_entities_and_relationships=tuple(selected_entities_and_relationships), selected_programmes_and_initiatives=tuple(selected_programmes_and_initiatives), selected_unknowns=tuple(selected_unknowns), selected_contradictions=tuple(selected_contradictions), selected_human_supplied_knowledge=tuple(selected_human_supplied_knowledge), selected_projections=tuple(selected_projections), lineage_manifest=tuple(lineage_manifest), freshness=freshness, retrieval_strategy=retrieval_strategy, retrieval_notes=tuple(retrieval_notes))

    def all_items(self) -> list[EvidencePackageItem]:
        return [*self.selected_observations, *self.selected_entities_and_relationships, *self.selected_programmes_and_initiatives, *self.selected_unknowns, *self.selected_contradictions, *self.selected_human_supplied_knowledge, *self.selected_projections]

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
