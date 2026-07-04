from __future__ import annotations
from datetime import datetime, UTC
from enum import StrEnum
from typing import Any, Protocol
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class ClaimType(StrEnum):
    enterprise_identity_confirmed='enterprise_identity_confirmed'; business_unit_disclosed='business_unit_disclosed'; financial_metric_reported='financial_metric_reported'; financial_guidance_stated='financial_guidance_stated'; financial_target_stated='financial_target_stated'; strategic_pillar_stated='strategic_pillar_stated'; strategic_commitment_stated='strategic_commitment_stated'; executive_role_confirmed='executive_role_confirmed'; executive_appointment_announced='executive_appointment_announced'
class FactState(StrEnum):
    current='current'; historical='historical'; actual='actual'; target='target'; guidance='guidance'; announced='announced'; conditional='conditional'

class PageRange(BaseModel):
    model_config=ConfigDict(extra='forbid')
    start:int=Field(ge=1); end:int=Field(ge=1)
    @model_validator(mode='after')
    def ok(self):
        if self.end < self.start: raise ValueError('page range end must be >= start')
        return self
    def label(self)->str: return f"{self.start}-{self.end}" if self.start!=self.end else str(self.start)

class ExperimentDocument(BaseModel):
    model_config=ConfigDict(extra='forbid')
    document_id:str; enterprise_id:str; title:str; source_url:str; retrieval_timestamp:str; checksum:str; media_type:str; page_count:int=Field(ge=1); local_path:str|None=None

class FoundationFact(BaseModel):
    model_config=ConfigDict(extra='forbid')
    fact_id:str; canonical_enterprise_id:str; claim_type:ClaimType
    subject_type:str; subject_name:str; subject_id:str|None=None
    predicate:str; object_type:str
    value_text:str|None=None; value_number:float|None=None; scale:str|None=None; unit:str|None=None; currency:str|None=None
    business_unit:str|None=None
    period_label:str|None=None; period_start:str|None=None; period_end:str|None=None
    state:FactState
    source_document_id:str; source_page_start:int=Field(ge=1); source_page_end:int=Field(ge=1); source_excerpt:str=Field(min_length=1,max_length=420)
    extraction_confidence:float=Field(ge=0,le=1); explicit_in_source:bool
    extractor_provider:str; extractor_model:str; extractor_version:str
    @model_validator(mode='after')
    def validate_atomic(self):
        if self.source_page_end < self.source_page_start: raise ValueError('source page end must be >= start')
        metric_values=sum(v is not None for v in (self.value_text,self.value_number))
        if self.claim_type in {ClaimType.financial_metric_reported,ClaimType.financial_guidance_stated,ClaimType.financial_target_stated} and metric_values != 1:
            raise ValueError('financial facts must contain exactly one value')
        if self.claim_type not in {ClaimType.financial_metric_reported,ClaimType.financial_guidance_stated,ClaimType.financial_target_stated} and metric_values > 1:
            raise ValueError('one fact must contain one metric or relationship')
        if self.claim_type == ClaimType.financial_guidance_stated and self.state != FactState.guidance: raise ValueError('guidance claim must use guidance state')
        if self.claim_type == ClaimType.financial_target_stated and self.state != FactState.target: raise ValueError('target claim must use target state')
        return self

class FoundationFactSet(BaseModel):
    model_config=ConfigDict(extra='forbid')
    facts:list[FoundationFact]=Field(default_factory=list)

class ExtractionRun(BaseModel):
    model_config=ConfigDict(extra='forbid')
    run_id:str; route:str; provider:str; model:str; model_version:str|None=None; status:str
    request_id:str|None=None; started_at:str; completed_at:str; latency_seconds:float=Field(ge=0)
    usage:dict[str,Any]=Field(default_factory=dict); estimated_cost_usd:float|None=None; raw_response_location:str|None=None
    facts:list[FoundationFact]=Field(default_factory=list); schema_errors:list[str]=Field(default_factory=list); provider_errors:list[str]=Field(default_factory=list); verifier:dict[str,Any]=Field(default_factory=dict); diagnostics:list[dict[str,Any]]=Field(default_factory=list)

class DocumentUnderstandingProvider(Protocol):
    def extract_facts(self, document:ExperimentDocument, schema:type[FoundationFactSet], page_ranges:list[PageRange]|None=None)->ExtractionRun: ...

def now_iso(): return datetime.now(UTC).isoformat(timespec='seconds')
