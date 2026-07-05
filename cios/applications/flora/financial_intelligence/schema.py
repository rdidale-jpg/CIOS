from __future__ import annotations
from datetime import datetime, UTC
from enum import StrEnum
from copy import deepcopy
from decimal import Decimal
from typing import Annotated, Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator


def openai_strict_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    if model is FoundationFactSet:
        model = ProviderFoundationFactSet
    schema = deepcopy(model.model_json_schema())
    _require_all_object_properties(schema)
    assert_openai_structured_outputs_schema(schema)
    return schema

UNSUPPORTED_OPENAI_SCHEMA_KEYWORDS = {'oneOf','allOf','not','if','then','else'}

def assert_openai_structured_outputs_schema(schema: dict[str, Any]) -> None:
    """CI/runtime guard for the OpenAI Structured Outputs subset used by Flora."""
    errors: list[str] = []
    def walk(node: Any, path: str = '$') -> None:
        if isinstance(node, dict):
            for keyword in UNSUPPORTED_OPENAI_SCHEMA_KEYWORDS:
                if keyword in node:
                    errors.append(f'{path} contains unsupported keyword {keyword}')
            properties = node.get('properties')
            if isinstance(properties, dict):
                if node.get('additionalProperties') is not False:
                    errors.append(f'{path} object missing additionalProperties:false')
                required = set(node.get('required') or [])
                missing = set(properties) - required
                if missing:
                    errors.append(f'{path} required omits {sorted(missing)}')
            for key, value in node.items():
                walk(value, f'{path}.{key}')
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                walk(item, f'{path}[{idx}]')
    walk(schema)
    if errors:
        raise ValueError('; '.join(errors))



def _require_all_object_properties(node: Any) -> None:
    if isinstance(node, dict):
        properties = node.get('properties')
        if isinstance(properties, dict):
            node['required'] = list(properties.keys())
            node['additionalProperties'] = False
        for value in node.values():
            _require_all_object_properties(value)
    elif isinstance(node, list):
        for item in node:
            _require_all_object_properties(item)

class ClaimType(StrEnum):
    enterprise_identity_confirmed='enterprise_identity_confirmed'; business_unit_disclosed='business_unit_disclosed'; financial_metric_reported='financial_metric_reported'; financial_guidance_stated='financial_guidance_stated'; financial_target_stated='financial_target_stated'; strategic_pillar_stated='strategic_pillar_stated'; strategic_commitment_stated='strategic_commitment_stated'; executive_role_confirmed='executive_role_confirmed'; executive_appointment_announced='executive_appointment_announced'
class FactState(StrEnum):
    current='current'; historical='historical'; actual='actual'; target='target'; guidance='guidance'; announced='announced'; conditional='conditional'

class NumericFactValue(BaseModel):
    model_config=ConfigDict(extra='forbid')
    kind: Literal['numeric']='numeric'; amount: Decimal; scale: str|None=None; unit: str|None=None; currency: str|None=None
class TextFactValue(BaseModel):
    model_config=ConfigDict(extra='forbid')
    kind: Literal['text']='text'; text: str
class DateFactValue(BaseModel):
    model_config=ConfigDict(extra='forbid')
    kind: Literal['date']='date'; date: str
class BooleanFactValue(BaseModel):
    model_config=ConfigDict(extra='forbid')
    kind: Literal['boolean']='boolean'; value: bool
FactValue = Annotated[NumericFactValue | TextFactValue | DateFactValue | BooleanFactValue, Field(discriminator='kind')]
FactValueAdapter = TypeAdapter(FactValue)

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
    predicate:str; object_type:str; value: FactValue
    business_unit:str|None=None
    period_label:str|None=None; period_start:str|None=None; period_end:str|None=None
    state:FactState
    source_document_id:str; source_page_start:int=Field(ge=1); source_page_end:int=Field(ge=1); source_excerpt:str=Field(min_length=1,max_length=420)
    packet_page_number:int|None=None; original_pdf_page_number:int|None=None
    extraction_confidence:float=Field(ge=0,le=1); explicit_in_source:bool
    extractor_provider:str; extractor_model:str; extractor_version:str

    @model_validator(mode='before')
    @classmethod
    def reject_or_upgrade_legacy_values(cls, data: Any) -> Any:
        if not isinstance(data, dict): return data
        legacy = ['value_text','value_number','value_date','value_boolean']
        populated = [k for k in legacy if k in data and data.get(k) is not None]
        if 'value' in data:
            if populated: raise ValueError('fact must use explicit value and not legacy value fields')
            return data
        if len(populated) != 1: raise ValueError('financial facts must contain exactly one value')
        copy = dict(data); k = populated[0]
        if k == 'value_number':
            copy['value'] = {'kind':'numeric','amount': copy.pop(k), 'scale': copy.pop('scale', None), 'unit': copy.pop('unit', None), 'currency': copy.pop('currency', None)}
        elif k == 'value_text': copy['value'] = {'kind':'text','text': copy.pop(k)}
        elif k == 'value_date': copy['value'] = {'kind':'date','date': copy.pop(k)}
        else: copy['value'] = {'kind':'boolean','value': copy.pop(k)}
        for extra in legacy:
            copy.pop(extra, None)
        return copy

    @model_validator(mode='after')
    def validate_atomic(self):
        if self.source_page_end < self.source_page_start: raise ValueError('source page end must be >= start')
        if self.claim_type in {ClaimType.financial_metric_reported,ClaimType.financial_guidance_stated,ClaimType.financial_target_stated} and self.value.kind not in {'numeric','text'}:
            raise ValueError('financial facts must use numeric or text values')
        if self.claim_type == ClaimType.financial_guidance_stated and self.state != FactState.guidance: raise ValueError('guidance claim must use guidance state')
        if self.claim_type == ClaimType.financial_target_stated and self.state != FactState.target: raise ValueError('target claim must use target state')
        return self

    @property
    def value_number(self) -> float|None: return float(self.value.amount) if isinstance(self.value, NumericFactValue) else None
    @property
    def value_text(self) -> str|None: return self.value.text if isinstance(self.value, TextFactValue) else None
    @property
    def scale(self) -> str|None: return self.value.scale if isinstance(self.value, NumericFactValue) else None
    @property
    def unit(self) -> str|None: return self.value.unit if isinstance(self.value, NumericFactValue) else None
    @property
    def currency(self) -> str|None: return self.value.currency if isinstance(self.value, NumericFactValue) else None


class ProviderFoundationFact(BaseModel):
    """OpenAI Structured Outputs-compatible DTO; mapped into canonical FoundationFact after receipt."""
    model_config=ConfigDict(extra='forbid')
    fact_id:str; canonical_enterprise_id:str; claim_type:ClaimType
    subject_type:str; subject_name:str; subject_id:str|None=None
    predicate:str; object_type:str
    value_kind: Literal['numeric','text','date','boolean']
    numeric_value: Decimal|None=None
    text_value: str|None=None
    date_value: str|None=None
    boolean_value: bool|None=None
    currency:str|None=None; unit:str|None=None; scale:str|None=None
    business_unit:str|None=None
    period_label:str|None=None; period_start:str|None=None; period_end:str|None=None
    state:FactState
    source_document_id:str; source_page_start:int=Field(ge=1); source_page_end:int=Field(ge=1); source_excerpt:str=Field(min_length=1,max_length=420)
    packet_page_number:int|None=None; original_pdf_page_number:int|None=None
    extraction_confidence:float=Field(ge=0,le=1); explicit_in_source:bool
    extractor_provider:str; extractor_model:str; extractor_version:str

    def to_canonical(self) -> FoundationFact:
        populated = {
            'numeric': self.numeric_value,
            'text': self.text_value,
            'date': self.date_value,
            'boolean': self.boolean_value,
        }
        non_null = [kind for kind, value in populated.items() if value is not None]
        if non_null != [self.value_kind]:
            raise ValueError('value_kind must match exactly one populated value field and all other value fields must be null')
        if self.value_kind == 'numeric':
            value = {'kind':'numeric','amount': self.numeric_value, 'scale': self.scale, 'unit': self.unit, 'currency': self.currency}
        elif self.value_kind == 'text':
            if self.currency is not None or self.unit is not None or self.scale is not None:
                raise ValueError('text values must not include numeric unit, currency, or scale')
            value = {'kind':'text','text': self.text_value}
        elif self.value_kind == 'date':
            if self.currency is not None or self.unit is not None or self.scale is not None:
                raise ValueError('date values must not include numeric unit, currency, or scale')
            value = {'kind':'date','date': self.date_value}
        else:
            if self.currency is not None or self.unit is not None or self.scale is not None:
                raise ValueError('boolean values must not include numeric unit, currency, or scale')
            value = {'kind':'boolean','value': self.boolean_value}
        data = self.model_dump()
        for key in ('value_kind','numeric_value','text_value','date_value','boolean_value','currency','unit','scale'):
            data.pop(key, None)
        data['value'] = value
        return FoundationFact.model_validate(data)

class ProviderFoundationFactSet(BaseModel):
    model_config=ConfigDict(extra='forbid')
    facts:list[ProviderFoundationFact]=Field(default_factory=list)

class FoundationFactSet(BaseModel):
    model_config=ConfigDict(extra='forbid')
    facts:list[FoundationFact]=Field(default_factory=list)

class ExtractionRun(BaseModel):
    model_config=ConfigDict(extra='forbid')
    run_id:str; route:str; provider:str; model:str; model_version:str|None=None; status:str
    request_id:str|None=None; started_at:str; completed_at:str; latency_seconds:float=Field(ge=0)
    usage:dict[str,Any]=Field(default_factory=dict); estimated_cost_usd:float|None=None; raw_response_location:str|None=None
    facts:list[FoundationFact]=Field(default_factory=list); schema_errors:list[str]=Field(default_factory=list); provider_errors:list[str]=Field(default_factory=list); verifier:dict[str,Any]=Field(default_factory=dict); diagnostics:list[dict[str,Any]]=Field(default_factory=list); candidate_exceptions:list[dict[str,Any]]=Field(default_factory=list)

class DocumentUnderstandingProvider(Protocol):
    def extract_facts(self, document:ExperimentDocument, schema:type[FoundationFactSet], page_ranges:list[PageRange]|None=None)->ExtractionRun: ...

def now_iso(): return datetime.now(UTC).isoformat(timespec='seconds')
