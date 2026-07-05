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
    allowed = {'packet_page_number','original_pdf_page_number','fact_id','claim_type','predicate','object_type','value','value_kind','numeric_value','text_value','date_value','boolean_value','value_text','value_number','value_date','value_boolean','scale','unit','currency','business_unit','period_label','period_start','period_end','state','source_document_id','source_page_start','source_page_end','source_excerpt','extraction_confidence','explicit_in_source','extractor_provider','extractor_model','extractor_version','canonical_enterprise_id','subject_type','subject_name','subject_id'}
    return {k:v for k,v in candidate.items() if k in allowed}

def validation_exception(candidate: Any, exc: Exception, *, packet_id: str|None, candidate_index: int, provider: str, model: str, request_id: str|None=None, rule: str|None=None, repair_possible: bool=False) -> dict[str, Any]:
    cand = candidate if isinstance(candidate, dict) else {}
    structured_errors = []
    if isinstance(exc, ValidationError):
        for err in exc.errors():
            loc = [str(p) for p in err.get('loc', ())]
            value = err.get('input')
            structured_errors.append({
                'field_location': loc,
                'error_type': err.get('type'),
                'sanitised_message': str(err.get('msg') or '')[:300],
                'received_value_type': type(value).__name__,
                'candidate_id': cand.get('fact_id'),
                'packet_id': packet_id,
                'response_id': request_id,
            })
    return {
        'exception_type':'candidate_fact_validation_failed',
        'packet_id': packet_id,
        'returned_page_reference': cand.get('packet_page_number') or cand.get('source_page_start') or cand.get('page_reference'),
        'original_page_reference': cand.get('original_pdf_page_number') or cand.get('source_page_start') or cand.get('page_reference'),
        'candidate_index': candidate_index,
        'fact_id': cand.get('fact_id'),
        'support_reference': request_id or packet_id,
        'supporting_excerpt_length': len(cand.get('source_excerpt') or ''),
        'metric_type': cand.get('claim_type') or cand.get('predicate'),
        'value_kind': cand.get('value_kind') or ((cand.get('value') or {}).get('kind') if isinstance(cand.get('value'), dict) else None),
        'populated_value_fields': populated_value_fields(cand),
        'validation_failure_category':'candidate_fact_validation_failed',
        'validation_rule_failed': rule or str(exc).split('\n')[0][:180],
        'validation_error_code': (rule or type(exc).__name__),
        'deterministic_repair_possible': repair_possible,
        'safe_explanation': str(exc).split('\n')[0][:500],
        'validation_errors': structured_errors,
        'provider': provider,
        'model': model,
        'request_id': request_id,
        'machine_candidate': _safe_candidate(candidate),
    }

def _provider_candidate_with_runtime_context(candidate: dict[str, Any], *, provider: str, model: str) -> dict[str, Any]:
    """Attach runtime-owned provider provenance before the one provider DTO validation.

    Stored OpenAI responses from the regression window contain null model/version
    and sometimes a user_provided provider label after downstream enrichment.  The
    provider DTO is still the boundary contract, but provider/model/version are
    runtime facts rather than model-authored facts, so restore them deterministically
    before parsing once.
    """
    repaired = dict(candidate)
    if provider and provider != 'user_provided':
        repaired['extractor_provider'] = provider
    if model:
        repaired['extractor_model'] = model
        repaired['extractor_version'] = repaired.get('extractor_version') or model
    if not repaired.get('canonical_enterprise_id'):
        repaired['canonical_enterprise_id'] = 'bt-group-plc'
    if not repaired.get('subject_name'):
        repaired['subject_name'] = 'BT Group plc'
    if not repaired.get('subject_type'):
        repaired['subject_type'] = 'enterprise'
    if repaired.get('subject_id') in (None, '') and repaired.get('canonical_enterprise_id'):
        repaired['subject_id'] = repaired['canonical_enterprise_id']
    return repaired

def parse_foundation_fact_candidates(output: str, *, packet_id: str|None, provider: str, model: str, request_id: str|None=None, packet_page_map: dict[int, int] | None=None) -> tuple[FoundationFactSet, list[dict[str, Any]], str]:
    try:
        envelope = json.loads(output or '{}')
    except json.JSONDecodeError as exc:
        return FoundationFactSet(), [validation_exception({}, exc, packet_id=packet_id, candidate_index=-1, provider=provider, model=model, request_id=request_id)], 'provider_response_invalid'
    if '[EXTRACT NOT AVAILABLE:' in (output or ''):
        return FoundationFactSet(), [validation_exception({'source_excerpt': '[EXTRACT NOT AVAILABLE]'}, ValueError('packet_content_unavailable placeholder is not candidate evidence'), packet_id=packet_id, candidate_index=-1, provider=provider, model=model, request_id=request_id) | {'exception_type': 'packet_content_unavailable'}], 'packet_content_unavailable'
    if not isinstance(envelope, dict) or not isinstance(envelope.get('facts'), list):
        return FoundationFactSet(), [validation_exception(envelope, ValueError('response envelope must contain a facts array'), packet_id=packet_id, candidate_index=-1, provider=provider, model=model, request_id=request_id)], 'provider_response_invalid'
    valid=[]; exceptions=[]
    for idx, candidate in enumerate(envelope['facts']):
        try:
            if isinstance(candidate, dict) and packet_page_map:
                pkt = candidate.get('packet_page_number') or candidate.get('source_page_start')
                try: pkt_int = int(pkt)
                except Exception: pkt_int = 0
                if pkt_int in packet_page_map:
                    candidate = dict(candidate); candidate['packet_page_number'] = pkt_int; candidate['original_pdf_page_number'] = packet_page_map[pkt_int]; candidate['source_page_start'] = packet_page_map[pkt_int]; candidate['source_page_end'] = packet_page_map.get(int(candidate.get('source_page_end') or pkt_int), packet_page_map[pkt_int])
                else:
                    raise ValueError('packet_page_out_of_range')
            if isinstance(candidate, dict) and 'value_kind' in candidate:
                provider_dto = ProviderFoundationFact.model_validate(_provider_candidate_with_runtime_context(candidate, provider=provider, model=model))
                valid.append(provider_dto.to_canonical())
            else:
                valid.append(FoundationFact.model_validate(candidate))
        except ValidationError as exc:
            exceptions.append(validation_exception(candidate, exc, packet_id=packet_id, candidate_index=idx, provider=provider, model=model, request_id=request_id, rule=str(exc).split('\n')[0][:180], repair_possible=False))
        except ValueError as exc:
            exceptions.append(validation_exception(candidate, exc, packet_id=packet_id, candidate_index=idx, provider=provider, model=model, request_id=request_id, rule=str(exc).split('\n')[0][:180], repair_possible=False))
    status = 'completed_with_exceptions' if valid and exceptions else ('completed' if valid or not exceptions else ('candidate_validation_failed' if packet_page_map else 'provider_response_invalid'))
    return FoundationFactSet(facts=valid), exceptions, status
