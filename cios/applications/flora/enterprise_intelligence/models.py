from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import UTC, datetime
from typing import Any
import hashlib, json, uuid

PROFILE_ID='strategic_sales_director_v1'
PROMPT_VERSION='executive_commercial_brief_prompt_v1'
SCHEMA_VERSION='ExecutiveCommercialBriefV1'

def now_iso(): return datetime.now(UTC).isoformat(timespec='seconds')
def stable_hash(data: Any) -> str: return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()

@dataclass(frozen=True)
class ReasoningRequestV1:
    request_id: str
    enterprise_id: str
    workspace_id: str
    twin_version: str
    reasoning_profile: str
    user_role: str
    purpose: str
    requested_sections: tuple[str,...]
    evidence_cut_off: str
    maximum_evidence_volume: int
    model_configuration_ref: str
    prompt_version_ref: str
    created_at: str
    requested_by: str
    include_projections: bool = True
    version: str = 'ReasoningRequestV1'
    @classmethod
    def create(cls, enterprise_id, workspace_id, requested_by, twin_version='accepted', evidence_cut_off='', maximum_evidence_volume=24000, user_role='strategic_sales_director'):
        return cls('rr-'+uuid.uuid4().hex[:16], enterprise_id, workspace_id, twin_version, PROFILE_ID, user_role,
            'Understand the enterprise, identify evidence-backed reinvention pressures, assess commercial relevance, and define the next learning or engagement moves.',
            ('executive_summary','material_changes','material_pressures','operating_model_summary','change_portfolio','stakeholders','commercial_relevance','unknowns','contradictions','recommended_next_moves','evidence_lineage'),
            evidence_cut_off, maximum_evidence_volume, 'env:FLORA_ENTERPRISE_INTELLIGENCE_MODEL', PROMPT_VERSION, now_iso(), requested_by)
    def to_dict(self):
        d=asdict(self); d['requested_sections']=list(self.requested_sections); return d

@dataclass(frozen=True)
class EvidencePackageItem:
    stable_id: str; object_class: str; statement: str; truth_status: str; confidence: int|str; freshness: str; lineage: tuple[str,...]=(); linked_objects: tuple[str,...]=(); source_location: str=''; enterprise_id: str=''
    def to_dict(self):
        d=asdict(self); d['lineage']=list(self.lineage); d['linked_objects']=list(self.linked_objects); return d

@dataclass(frozen=True)
class EvidencePackageV1:
    package_id: str; enterprise_id: str; enterprise_metadata: dict[str,Any]; accepted_twin_version: str; source_cut_off: str; progressive_assurance_status: str; selected_observations: tuple[EvidencePackageItem,...]; selected_entities_and_relationships: tuple[EvidencePackageItem,...]; selected_programmes_and_initiatives: tuple[EvidencePackageItem,...]; selected_unknowns: tuple[EvidencePackageItem,...]; selected_contradictions: tuple[EvidencePackageItem,...]; selected_human_supplied_knowledge: tuple[EvidencePackageItem,...]; selected_projections: tuple[EvidencePackageItem,...]; lineage_references: tuple[str,...]; freshness: str; confidence: str; retrieval_rationale: tuple[str,...]
    def all_items(self):
        return tuple(x for group in (self.selected_observations,self.selected_entities_and_relationships,self.selected_programmes_and_initiatives,self.selected_unknowns,self.selected_contradictions,self.selected_human_supplied_knowledge,self.selected_projections) for x in group)
    def to_dict(self):
        d=asdict(self)
        for k in ('selected_observations','selected_entities_and_relationships','selected_programmes_and_initiatives','selected_unknowns','selected_contradictions','selected_human_supplied_knowledge','selected_projections'):
            d[k]=[i.to_dict() for i in getattr(self,k)]
        d['lineage_references']=list(self.lineage_references); d['retrieval_rationale']=list(self.retrieval_rationale); return d
