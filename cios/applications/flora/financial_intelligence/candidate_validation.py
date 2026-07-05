from __future__ import annotations
import json
from typing import Any
from pydantic import ValidationError
from .schema import FoundationFact, FoundationFactSet, ProviderFoundationFact

LEGACY_VALUE_FIELDS = ('value_text','value_number','value_date','value_boolean')
PROVIDER_VALUE_FIELDS = ('numeric_value','text_value','date_value','boolean_value')

def populated_value_fields(candidate: dict[str, Any]) -> list[str]:
    fields=[]
    if candidate.get('value') is not None: fields.append('value')
    fields += [k for k in LEGACY_VALUE_FIELDS + PROVIDER_VALUE_FIELDS if k in candidate and candidate.get(k) is not None]
    return fields

def _safe_candidate(candidate: Any) -> Any:
    if not isinstance(candidate, dict): return candidate
    allowed = {'fact_id','claim_type','predicate','object_type','value','value_kind','numeric_value','text_value','date_value','boolean_value','value_text','value_number','value_date','value_boolean','scale','unit','currency','business_unit','period_label','period_start','period_end','state','source_document_id','source_page_start','source_page_end','source_excerpt','extraction_confidence','explicit_in_source','extractor_provider','extractor_model','extractor_version','canonical_enterprise_id','subject_type','subject_name','subject_id'}
    return {k:v for k,v in candidate.items() if k in allowed}

def validation_exception(candidate: Any, exc: Exception, *, packet_id: str|None, candidate_index: int, provider: str, model: str, request_id: str|None=None) -> dict[str, Any]:
    cand = candidate if isinstance(candidate, dict) else {}
    return {
        'exception_type':'candidate_fact_validation_failed',
        'packet_id': packet_id,
        'original_page_reference': cand.get('source_page_start') or cand.get('page_reference'),
        'candidate_index': candidate_index,
        'fact_id': cand.get('fact_id'),
        'support_reference': cand.get('source_excerpt'),
        'populated_value_fields': populated_value_fields(cand),
        'validation_failure_category':'candidate_fact_validation_failed',
        'safe_explanation': str(exc).split('\n')[0][:500],
        'provider': provider,
        'model': model,
        'request_id': request_id,
        'machine_candidate': _safe_candidate(candidate),
    }

def parse_foundation_fact_candidates(output: str, *, packet_id: str|None, provider: str, model: str, request_id: str|None=None) -> tuple[FoundationFactSet, list[dict[str, Any]], str]:
    try:
        envelope = json.loads(output or '{}')
    except json.JSONDecodeError as exc:
        return FoundationFactSet(), [validation_exception({}, exc, packet_id=packet_id, candidate_index=-1, provider=provider, model=model, request_id=request_id)], 'provider_response_invalid'
    if not isinstance(envelope, dict) or not isinstance(envelope.get('facts'), list):
        return FoundationFactSet(), [validation_exception(envelope, ValueError('response envelope must contain a facts array'), packet_id=packet_id, candidate_index=-1, provider=provider, model=model, request_id=request_id)], 'provider_response_invalid'
    valid=[]; exceptions=[]
    for idx, candidate in enumerate(envelope['facts']):
        try:
            if isinstance(candidate, dict) and 'value_kind' in candidate:
                valid.append(ProviderFoundationFact.model_validate(candidate).to_canonical())
            else:
                valid.append(FoundationFact.model_validate(candidate))
        except ValidationError as exc:
            exceptions.append(validation_exception(candidate, exc, packet_id=packet_id, candidate_index=idx, provider=provider, model=model, request_id=request_id))
        except ValueError as exc:
            exceptions.append(validation_exception(candidate, exc, packet_id=packet_id, candidate_index=idx, provider=provider, model=model, request_id=request_id))
    status = 'completed_with_exceptions' if valid and exceptions else ('completed' if valid or not exceptions else 'provider_response_invalid')
    return FoundationFactSet(facts=valid), exceptions, status
