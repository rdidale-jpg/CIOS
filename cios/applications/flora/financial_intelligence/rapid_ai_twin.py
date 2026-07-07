"""AI-first Rapid Commercial Digital Twin snapshot lane.

The snapshot is persisted inside the standard Financial Intelligence run record
as candidate, verification-pending intelligence.  This module performs no
canonical Evidence, Observation or Enterprise Model writes.
"""
from __future__ import annotations

import csv, hashlib, io, json, os, re, time, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from cios.applications.flora.storage import data_path, ensure_writable_dir, atomic_write_json
from .config import financial_intelligence_settings
from .openai_provider import OpenAIDirectPDFProvider
from .rapid_sources import AcquiredRapidSource
from .schema import ExperimentDocument, openai_strict_json_schema

ONE_CALL_SCHEMA_VERSION = "rapid-ai-twin-one-call-v2"
ONE_CALL_PROMPT_VERSION = "rapid-ai-bt-one-call-prompt-v2"
EXTRACTION_SCHEMA_VERSION = ONE_CALL_SCHEMA_VERSION
SYNTHESIS_SCHEMA_VERSION = ONE_CALL_SCHEMA_VERSION
EXTRACTION_PROMPT_VERSION = ONE_CALL_PROMPT_VERSION
SYNTHESIS_PROMPT_VERSION = ONE_CALL_PROMPT_VERSION
MAX_RAW_RESPONSE_BYTES = int(os.getenv("FLORA_RAPID_AI_TWIN_MAX_RAW_RESPONSE_BYTES", "200000"))

class RapidAIExtraction(BaseModel):
    model_config = ConfigDict(extra='allow')
    document_identity: dict[str, Any] = Field(default_factory=dict)
    financial_tables: list[dict[str, Any]] = Field(default_factory=list)
    reported_facts: list[dict[str, Any]] = Field(default_factory=list)
    management_commitments: list[dict[str, Any]] = Field(default_factory=list)
    strategic_priorities: list[dict[str, Any]] = Field(default_factory=list)
    transformation_programmes: list[dict[str, Any]] = Field(default_factory=list)
    risks_and_pressures: list[dict[str, Any]] = Field(default_factory=list)
    technology_digital_ai: list[dict[str, Any]] = Field(default_factory=list)
    leadership_and_governance: list[dict[str, Any]] = Field(default_factory=list)
    customer_market_and_regulation: list[dict[str, Any]] = Field(default_factory=list)
    unknowns: list[dict[str, Any] | str] = Field(default_factory=list)
    extraction_coverage: dict[str, Any] = Field(default_factory=dict)
    citation_index: list[dict[str, Any]] = Field(default_factory=list)

class RapidAISynthesis(BaseModel):
    model_config = ConfigDict(extra='forbid')
    executive_summary: list[dict[str, Any] | str] = Field(default_factory=list)
    what_changed: list[dict[str, Any] | str] = Field(default_factory=list)
    why_it_matters: list[dict[str, Any] | str] = Field(default_factory=list)
    financial_trajectory: list[dict[str, Any] | str] = Field(default_factory=list)
    enterprise_pressures: list[dict[str, Any] | str] = Field(default_factory=list)
    transformation_direction: list[dict[str, Any] | str] = Field(default_factory=list)
    management_execution_assessment: list[dict[str, Any] | str] = Field(default_factory=list)
    strategic_signals: list[dict[str, Any]] = Field(default_factory=list)
    hypotheses: list[dict[str, Any]] = Field(default_factory=list)
    commercial_themes: list[dict[str, Any]] = Field(default_factory=list)
    likely_executive_stakeholders: list[dict[str, Any] | str] = Field(default_factory=list)
    contradictions: list[dict[str, Any] | str] = Field(default_factory=list)
    unknowns: list[dict[str, Any] | str] = Field(default_factory=list)
    questions_to_investigate: list[dict[str, Any] | str] = Field(default_factory=list)
    what_not_to_claim: list[dict[str, Any] | str] = Field(default_factory=list)
    recommended_learning_actions: list[dict[str, Any] | str] = Field(default_factory=list)

@dataclass
class ProviderStageResult:
    payload: dict[str, Any] | None
    call_record: dict[str, Any]
    error: str | None = None
    raw_response: str | dict[str, Any] | None = None

class RapidAITwinProvider:
    """Thin adapter over the existing OpenAI direct-PDF provider."""
    def __init__(self, provider: OpenAIDirectPDFProvider | None = None):
        self.provider = provider or OpenAIDirectPDFProvider(max_retries=1)

    def extraction(self, acquired: AcquiredRapidSource, correlation_id: str) -> ProviderStageResult:
        receipt = acquired.receipt
        document = ExperimentDocument(document_id=receipt.source_id, enterprise_id=receipt.enterprise_id, title=receipt.document_title, source_url=receipt.final_url or receipt.requested_url, retrieval_timestamp=receipt.retrieved_at, checksum=receipt.sha256 or '', media_type='application/pdf', page_count=int(getattr(receipt, 'page_count', None) or 1), local_path=str(acquired.path))
        instructions = _stage1_prompt(receipt.to_dict())
        return _run_openai_stage(self.provider, document, RapidAIExtraction, instructions, 'stage_1_report_extraction', correlation_id)

    def analyse(self, acquired: AcquiredRapidSource, correlation_id: str) -> ProviderStageResult:
        receipt = acquired.receipt
        document = ExperimentDocument(document_id=receipt.source_id, enterprise_id=receipt.enterprise_id, title=receipt.document_title, source_url=receipt.final_url or receipt.requested_url, retrieval_timestamp=receipt.retrieved_at, checksum=receipt.sha256 or "", media_type="application/pdf", page_count=int(getattr(receipt, "page_count", None) or 1), local_path=str(acquired.path))
        return _run_openai_stage(self.provider, document, RapidAIExtraction, _one_call_prompt(receipt.to_dict()), "one_call_report_extraction_and_synthesis", correlation_id)

    def synthesis(self, extraction: dict[str, Any], citation_index: list[dict[str, Any]], correlation_id: str) -> ProviderStageResult:
        return ProviderStageResult({}, {"stage":"stage_2_twin_synthesis","status":"skipped","reason":"one_call_pilot_path"})

def _usage_record(meta: dict[str, Any]) -> dict[str, Any]:
    usage = meta.get('usage') or {}
    return {'model': meta.get('model'), 'input_tokens': int(usage.get('input_tokens') or 0), 'output_tokens': int(usage.get('output_tokens') or 0), 'estimated_or_actual_cost_usd': float(usage.get('approximate_cost_usd') or meta.get('actual_cost_usd') or 0)}

def _run_openai_stage(provider: OpenAIDirectPDFProvider, document: ExperimentDocument, schema: type[BaseModel], instructions: str, stage: str, correlation_id: str) -> ProviderStageResult:
    started=time.monotonic(); source_path=Path(document.local_path) if document.local_path else None
    if not os.getenv('OPENAI_API_KEY'):
        return ProviderStageResult(None, {'stage':stage,'provider':'openai','model':provider.model,'status':'not_executed','usage':{},'estimated_or_actual_cost_usd':0,'schema_version':EXTRACTION_SCHEMA_VERSION}, 'OPENAI_API_KEY is not configured')
    original = provider._input_payload
    original_request_payload = provider._request_payload
    def json_mode_payload(current_mode: str) -> dict[str, Any]:
        return {
            'model': provider.model,
            'input': [{'role':'user','content':[provider._request_content(document, current_mode, source_path), {'type':'input_text','text':instructions}]}],
            'reasoning': {'effort': provider.reasoning_effort},
            'max_output_tokens': provider.max_output_tokens,
            'text': {'format': {'type': 'json_object'}},
        }
    provider._request_payload = lambda doc, sch, mode, sp: json_mode_payload(mode)  # type: ignore[method-assign]
    provider._input_payload = lambda doc, sch, mode, sp: [{'role':'user','content':[provider._request_content(doc, mode, sp), {'type':'input_text','text':instructions}]}]  # type: ignore[method-assign]
    try:
        OpenAI = __import__('openai', fromlist=['OpenAI']).OpenAI
        client = OpenAI(timeout=provider.timeout_seconds, max_retries=provider.max_retries)
        mode='file_url'; input_tokens=0; estimated=0.0
        try:
            input_tokens=provider._count_input_tokens(client, document, schema, mode, source_path)
            estimated=provider._estimated_cost(input_tokens)
            if estimated > provider.max_run_cost_usd:
                return ProviderStageResult(None, {'stage':stage,'provider':'openai','model':provider.model,'status':'cost_limit_exceeded','usage':{'input_tokens':input_tokens},'estimated_or_actual_cost_usd':estimated,'schema_version':EXTRACTION_SCHEMA_VERSION}, 'cost_limit_exceeded')
        except Exception as exc:
            # Keep bounded behaviour: if preflight is unavailable, do not improvise an unbounded call.
            return ProviderStageResult(None, {'stage':stage,'provider':'openai','model':provider.model,'status':'cost_preflight_unavailable','usage':{},'estimated_or_actual_cost_usd':0,'schema_version':EXTRACTION_SCHEMA_VERSION}, str(exc))
        try:
            resp=client.responses.create(**json_mode_payload(mode))
        except Exception as exc:
            if getattr(exc, 'code', None) != 'invalid_file_url':
                raise
            mode='file_data'; resp=client.responses.create(**json_mode_payload(mode))
        raw=resp.model_dump(mode='json') if hasattr(resp,'model_dump') else (resp if isinstance(resp,dict) else {})
        meta=provider._response_metadata(resp, raw, input_tokens=input_tokens, estimated_cost=estimated)
        text=getattr(resp,'output_text','') or raw.get('output_text','') or ''
        parsed_obj=getattr(resp,'output_parsed',None)
        if parsed_obj is None and text:
            parsed_obj=_extract_json_object(text)
        if parsed_obj is None:
            return ProviderStageResult(None, {'stage':stage,'provider':'openai','model':provider.model,'status':'empty_response','usage':meta.get('usage') or {},'estimated_or_actual_cost_usd':meta.get('actual_cost_usd') or estimated,'elapsed_ms':int((time.monotonic()-started)*1000),'schema_version':EXTRACTION_SCHEMA_VERSION}, 'empty structured response', raw_response=raw or text)
        payload=parsed_obj.model_dump() if hasattr(parsed_obj,'model_dump') else dict(parsed_obj)
        return ProviderStageResult(payload, {'stage':stage,'provider':'openai','model':provider.model,'status':'completed','provider_response_id':meta.get('response_id'),'provider_status':meta.get('response_status'),'finish_reason':meta.get('incomplete_details') or meta.get('response_status'),'usage':meta.get('usage') or {},'estimated_or_actual_cost_usd':meta.get('actual_cost_usd') or estimated,'elapsed_ms':int((time.monotonic()-started)*1000),'schema_version':ONE_CALL_SCHEMA_VERSION,'prompt_version':ONE_CALL_PROMPT_VERSION}, raw_response=raw)
    except Exception as exc:
        status_code = getattr(exc, 'status_code', None); code = getattr(exc, 'code', None) or getattr(getattr(exc, 'error', None), 'code', None)
        status = 'provider_request_invalid' if status_code == 400 else 'provider_request_failed'
        return ProviderStageResult(None, {'stage':stage,'provider':'openai','model':provider.model,'status':status,'http_status':status_code,'provider_error_code':code,'provider_error_type':type(exc).__name__,'safe_error_message':str(exc),'usage':{},'estimated_or_actual_cost_usd':0,'elapsed_ms':int((time.monotonic()-started)*1000),'schema_version':EXTRACTION_SCHEMA_VERSION}, f'{type(exc).__name__}: {exc}')
    finally:
        provider._input_payload = original  # type: ignore[method-assign]
        provider._request_payload = original_request_payload  # type: ignore[method-assign]

def _run_openai_text_stage(provider: OpenAIDirectPDFProvider, extraction: dict[str, Any], citation_index: list[dict[str, Any]], correlation_id: str) -> ProviderStageResult:
    started=time.monotonic(); settings=financial_intelligence_settings()
    if not os.getenv('OPENAI_API_KEY'):
        return ProviderStageResult(None, {'stage':'stage_2_twin_synthesis','provider':'openai','model':settings.model,'status':'not_executed','usage':{},'estimated_or_actual_cost_usd':0,'schema_version':SYNTHESIS_SCHEMA_VERSION}, 'OPENAI_API_KEY is not configured')
    prompt = _stage2_prompt(extraction, citation_index)
    try:
        OpenAI = __import__('openai', fromlist=['OpenAI']).OpenAI
        client = OpenAI(timeout=provider.timeout_seconds, max_retries=provider.max_retries)
        payload = {'model': provider.model, 'input': [{'role':'user','content':[{'type':'input_text','text':prompt}]}], 'reasoning': {'effort': provider.reasoning_effort}, 'max_output_tokens': provider.max_output_tokens, 'text': {'format': {'type':'json_schema','name':'rapid_ai_synthesis','schema': openai_strict_json_schema(RapidAISynthesis),'strict': True}}}
        count_payload = dict(payload); count_payload.pop('max_output_tokens', None)
        counter = getattr(getattr(client, 'responses', None), 'input_tokens', None)
        if not counter:
            return ProviderStageResult(None, {'stage':'stage_2_twin_synthesis','provider':'openai','model':provider.model,'status':'cost_preflight_unavailable','usage':{},'estimated_or_actual_cost_usd':0,'schema_version':SYNTHESIS_SCHEMA_VERSION}, 'cost_preflight_sdk_unavailable')
        counted = counter.count(**count_payload) if hasattr(counter, 'count') else counter.create(**count_payload)
        input_tokens = int(getattr(counted, 'input_tokens', None) or getattr(counted, 'tokens', None) or (counted.get('input_tokens') if isinstance(counted, dict) else 0))
        estimated = provider._estimated_cost(input_tokens)
        if estimated > provider.max_run_cost_usd:
            return ProviderStageResult(None, {'stage':'stage_2_twin_synthesis','provider':'openai','model':provider.model,'status':'cost_limit_exceeded','usage':{'input_tokens':input_tokens},'estimated_or_actual_cost_usd':estimated,'schema_version':SYNTHESIS_SCHEMA_VERSION}, 'cost_limit_exceeded')
        parser = getattr(getattr(client, 'responses', None), 'parse', None)
        resp = parser(**payload) if parser else client.responses.create(**payload)
        raw=resp.model_dump(mode='json') if hasattr(resp,'model_dump') else (resp if isinstance(resp,dict) else {})
        meta=provider._response_metadata(resp, raw, input_tokens=input_tokens, estimated_cost=estimated)
        parsed_obj=getattr(resp,'output_parsed',None)
        if parsed_obj is None:
            text=getattr(resp,'output_text','') or raw.get('output_text','')
            parsed_obj=RapidAISynthesis.model_validate_json(text) if text else None
        if parsed_obj is None:
            return ProviderStageResult(None, {'stage':'stage_2_twin_synthesis','provider':'openai','model':provider.model,'status':'empty_response','usage':meta.get('usage') or {},'estimated_or_actual_cost_usd':meta.get('actual_cost_usd') or estimated,'elapsed_ms':int((time.monotonic()-started)*1000),'schema_version':SYNTHESIS_SCHEMA_VERSION}, 'empty structured response')
        return ProviderStageResult(parsed_obj.model_dump(), {'stage':'stage_2_twin_synthesis','provider':'openai','model':provider.model,'status':'completed','usage':meta.get('usage') or {},'estimated_or_actual_cost_usd':meta.get('actual_cost_usd') or estimated,'elapsed_ms':int((time.monotonic()-started)*1000),'schema_version':SYNTHESIS_SCHEMA_VERSION})
    except Exception as exc:
        return ProviderStageResult(None, {'stage':'stage_2_twin_synthesis','provider':'openai','model':provider.model,'status':'provider_request_failed','usage':{},'estimated_or_actual_cost_usd':0,'elapsed_ms':int((time.monotonic()-started)*1000),'schema_version':SYNTHESIS_SCHEMA_VERSION}, f'{type(exc).__name__}: {exc}')

def _stage2_prompt(extraction: dict[str, Any], citation_index: list[dict[str, Any]]) -> str:
    return 'Create Stage 2 Rapid AI Twin synthesis JSON. Use only this Stage 1 extraction and citation index. Distinguish reported facts, interpretation, Signals, Hypotheses, Unknowns and Contradictions. Every Signal and Hypothesis must reference valid Stage 1 fact or table-row IDs. Do not add uncited assumptions. Stage 1 extraction: ' + json.dumps({'extraction': extraction, 'citation_index': citation_index}, sort_keys=True, default=str)



def _provider_model(provider_boundary: Any, settings: Any) -> str:
    provider = getattr(provider_boundary, 'provider', provider_boundary)
    return str(getattr(provider, 'model', None) or settings.model or '')

def provider_preflight(acquired: AcquiredRapidSource, provider_boundary: Any, settings: Any) -> dict[str, Any]:
    """Validate the explicit provider boundary before Stage 1.

    Test doubles are accepted as configured providers so unit tests can prove the
    lifecycle without real credentials.  The production OpenAI adapter still
    requires OPENAI_API_KEY and a bounded max-run cost before any provider call.
    """
    receipt = acquired.receipt.to_dict()
    provider = getattr(provider_boundary, 'provider', provider_boundary)
    is_openai_adapter = isinstance(provider_boundary, RapidAITwinProvider) or isinstance(provider, OpenAIDirectPDFProvider)
    source_path = Path(acquired.path)
    size = source_path.stat().st_size if source_path.exists() else 0
    max_bytes = int(receipt.get('maximum_bytes') or 25000000)
    checks = {
        'ai_feature_enabled': os.getenv('FLORA_RAPID_AI_TWIN_ENABLED', '1').lower() not in {'0', 'false', 'no'},
        'provider_configured': bool(provider_boundary),
        'model_configured': bool(_provider_model(provider_boundary, settings)),
        'credential_present': bool(os.getenv('OPENAI_API_KEY')) if is_openai_adapter else True,
        'source_pdf_available': source_path.exists() and size > 0 and source_path.read_bytes()[:4] == b'%PDF',
        'source_size_supported': 0 < size <= max_bytes,
        'maximum_run_cost_configured': float(getattr(settings, 'max_run_cost_usd', 0) or 0) > 0,
    }
    failed = [name for name, ok in checks.items() if not ok]
    return {
        'status': 'passed' if not failed else 'failed',
        'checks': checks,
        'failed_checks': failed,
        'provider': 'openai' if is_openai_adapter else provider_boundary.__class__.__name__,
        'model': _provider_model(provider_boundary, settings),
        'source_bytes': size,
        'maximum_source_bytes': max_bytes,
    }


def provider_runtime_readiness(provider_boundary: Any | None = None, settings: Any | None = None) -> dict[str, Any]:
    """Shared BT Rapid AI Twin provider readiness gate.

    This intentionally uses only configuration checks so product pages and search
    requests can decide readiness before creating a run or retrieving a source.
    The source-specific `provider_preflight` below remains the final Stage 1
    guard once the approved PDF has been acquired.
    """
    settings = settings or financial_intelligence_settings()
    provider_boundary = provider_boundary or RapidAITwinProvider()
    provider = getattr(provider_boundary, 'provider', provider_boundary)
    is_openai_adapter = isinstance(provider_boundary, RapidAITwinProvider) or isinstance(provider, OpenAIDirectPDFProvider)
    enabled = os.getenv('FLORA_RAPID_AI_TWIN_ENABLED', '1').lower() not in {'0', 'false', 'no'}
    checks = {
        'feature_enabled': enabled,
        'provider_available': bool(provider_boundary),
        'credential_present': bool(os.getenv('OPENAI_API_KEY')) if is_openai_adapter else True,
        'model_configured': bool(_provider_model(provider_boundary, settings)),
        'maximum_cost_configured': float(getattr(settings, 'max_run_cost_usd', 0) or 0) > 0,
    }
    failed = [name for name, ok in checks.items() if not ok]
    return {
        'status': 'passed' if not failed else 'failed',
        'checks': checks,
        'failed_checks': failed,
        'provider': 'openai' if is_openai_adapter else provider_boundary.__class__.__name__,
        'model': _provider_model(provider_boundary, settings),
        'maximum_run_cost_usd': float(getattr(settings, 'max_run_cost_usd', 0) or 0),
        'user_status': 'ready' if not failed else 'AI research is not configured for this deployment.',
        'owner_state': 'Rapid AI Twin provider is configured.' if not failed else 'Set OPENAI_API_KEY on the deployed web service and keep FLORA_RAPID_AI_TWIN_ENABLED=true.',
    }

def _cache_dir() -> Path: return data_path('ai_financial_reports', 'rapid_ai_twin_cache')
def cache_key(sha256: str | None, model: str) -> str:
    raw = '|'.join([sha256 or '', model, ONE_CALL_PROMPT_VERSION, ONE_CALL_SCHEMA_VERSION])
    return hashlib.sha256(raw.encode()).hexdigest()

def _cache_path(key: str) -> Path: return _cache_dir() / f'{key}.json'

def _ids_from_extraction(extraction: dict[str, Any]) -> set[str]:
    ids=set()
    for t in extraction.get('financial_tables') or []:
        if t.get('table_id'): ids.add(str(t['table_id']))
        for r in t.get('rows') or []:
            if r.get('row_id'): ids.add(str(r['row_id']))
    for f in extraction.get('reported_facts') or []:
        if f.get('fact_id'): ids.add(str(f['fact_id']))
    return ids

def _page(v: Any) -> int | None:
    try: return int(v)
    except Exception: return None

def validate_extraction(extraction: dict[str, Any], receipt: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    errors=[]; ident=extraction.get('document_identity') or {}
    enterprise_name = ident.get('enterprise_name') or ident.get('enterprise') or ident.get('legal_name')
    if 'bt' not in str(enterprise_name or '').casefold(): errors.append({'code':'enterprise_mismatch','message':'AI did not identify BT Group.'})
    if str(receipt.get('reporting_period') or '') and str(receipt.get('reporting_period')) not in str(ident.get('reporting_period') or ''): errors.append({'code':'period_mismatch','message':'AI reporting period did not match source receipt.'})
    page_count = int(ident.get('document_page_count') or 10**9)
    valid_tables=[]
    for ti,t in enumerate(extraction.get('financial_tables') or []):
        rows=[]; seen=set()
        for ri,r in enumerate(t.get('rows') or []):
            rid=str(r.get('row_id') or f"{t.get('table_id','table')}-row-{ri+1}")
            p=_page(r.get('source_page') or r.get('page') or t.get('page'))
            if not p or p < 1 or p > page_count:
                errors.append({'code':'row_page_invalid','row_id':rid,'partial':True}); continue
            if rid in seen: errors.append({'code':'duplicate_row','row_id':rid,'partial':True}); continue
            seen.add(rid); r['row_id']=rid; r['source_page']=p
            if not r.get('supporting_excerpt'): r['ambiguity'] = (str(r.get('ambiguity') or '') + ' supporting excerpt unavailable').strip()
            rows.append(r)
        if rows:
            t['rows']=rows; valid_tables.append(t)
    extraction['financial_tables']=valid_tables
    if errors and any(e.get('code') in {'enterprise_mismatch','period_mismatch'} for e in errors): return None, errors
    return extraction, errors

def validate_synthesis(synthesis: dict[str, Any], extraction: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors=[]; valid_ids=_ids_from_extraction(extraction)
    def refs(item):
        vals=[]
        for k in ('supporting_fact_ids','supporting Evidence/fact IDs','supporting_evidence_fact_ids','supporting_ids','lineage_ids','fact_ids'):
            v=item.get(k) if isinstance(item,dict) else None
            if isinstance(v,list): vals += [str(x) for x in v]
        return vals
    for sec in ('strategic_signals','hypotheses'):
        kept=[]
        for item in synthesis.get(sec) or []:
            r=refs(item)
            if not r or any(x not in valid_ids for x in r):
                errors.append({'code':'invalid_lineage','section':sec,'item':item.get('signal_id') or item.get('hypothesis_id')}); continue
            kept.append(item)
        synthesis[sec]=kept
    return synthesis, errors

def build_csv(snapshot: dict[str, Any]) -> str:
    out=io.StringIO(); w=csv.writer(out)
    w.writerow(['table_id','table_title','row_order','row_id','reported_label','current_period_display_value','comparator_display_value','unit','scale','scope','accounting_basis','financial_measurement_state','source_page','supporting_excerpt','confidence','ambiguity','proposed_canonical_metric_id'])
    for t in ((snapshot.get('extraction_result') or {}).get('financial_tables') or []):
        for i,r in enumerate(t.get('rows') or [], start=1):
            w.writerow([t.get('table_id'),t.get('title'),r.get('row_order',i),r.get('row_id'),r.get('reported_label'),r.get('current_period_display_value'),r.get('comparator_display_value') or r.get('comparator_display_values'),r.get('unit'),r.get('scale'),r.get('scope'),r.get('accounting_basis'),r.get('financial_measurement_state'),r.get('source_page'),r.get('supporting_excerpt'),r.get('confidence'),r.get('ambiguity'),r.get('proposed_canonical_metric_id')])
    return out.getvalue()

def _raw_dir() -> Path:
    return data_path('ai_financial_reports', 'rapid_ai_twin_raw')

def _raw_text(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        return str(value)

def _response_text_candidates(value: Any) -> list[str]:
    """Return likely provider-visible text bodies without exposing secrets.

    OpenAI SDK objects and test doubles do not always expose `output_text` in
    the same place.  The previous pilot path treated a raw response dictionary
    itself as the candidate JSON object, which could hide useful JSON nested in
    `output_text` or `output[].content[].text`.
    """
    candidates: list[str] = []
    def add(v: Any) -> None:
        if isinstance(v, str) and v.strip():
            candidates.append(v)
    if isinstance(value, str):
        add(value); return candidates
    if isinstance(value, dict):
        for key in ('output_text', 'text', 'content'):
            add(value.get(key))
        for item in value.get('output') or []:
            if isinstance(item, dict):
                for content in item.get('content') or []:
                    if isinstance(content, dict):
                        add(content.get('text') or content.get('output_text'))
        if not candidates:
            add(_raw_text(value))
        return candidates
    add(getattr(value, 'output_text', None))
    return candidates or [_raw_text(value)]

def _persist_provider_response(correlation_id: str, call: dict[str, Any], raw_response: Any, started: float) -> dict[str, Any]:
    raw = _raw_text(raw_response if raw_response is not None else call.get('raw_response') or call.get('raw_body') or call.get('output_text') or '')
    bounded = raw[:MAX_RAW_RESPONSE_BYTES]
    ensure_writable_dir(_raw_dir())
    raw_path = _raw_dir() / f'{correlation_id}-{uuid.uuid4().hex[:10]}.json'
    atomic_write_json(raw_path, {'raw_response_body': bounded, 'truncated_for_storage': len(raw) > len(bounded)})
    usage = call.get('usage') or {}
    response_received = raw_response is not None or bool(raw) or call.get('http_status') is not None or call.get('provider_response_id') or call.get('response_id') or call.get('id')
    receipt = {
        'request_attempted': call.get('status') not in {'not_executed', 'skipped'},
        'response_received': bool(response_received),
        'http_status': call.get('http_status') or call.get('http_status_code'),
        'provider_response_id': call.get('provider_response_id') or call.get('response_id') or call.get('id'),
        'provider_status': call.get('provider_status') or call.get('response_status') or call.get('status'),
        'provider_error_type': call.get('provider_error_type') or call.get('error_type'),
        'provider_error_safe_message': call.get('sanitised_provider_error_message') or call.get('safe_error_message') or call.get('error_message') or call.get('error'),
        'model': call.get('model'),
        'finish_reason': call.get('finish_reason') or call.get('incomplete_details') or call.get('response_status') or call.get('status'),
        'input_tokens': int(usage.get('input_tokens') or 0),
        'output_tokens': int(usage.get('output_tokens') or 0),
        'token_usage': usage,
        'calculated_cost_usd': float(call.get('estimated_or_actual_cost_usd') or usage.get('approximate_cost_usd') or call.get('actual_cost_usd') or 0),
        'cost': call.get('estimated_or_actual_cost_usd') or usage.get('approximate_cost_usd') or call.get('actual_cost_usd') or 0,
        'elapsed_ms': call.get('elapsed_ms') or int((time.time() - started) * 1000),
        'response_text_length': len(raw),
        'raw_response_length': len(raw),
        'structured_payload_present': isinstance(raw_response, dict) or isinstance(call.get('output_parsed'), dict) or bool(call.get('structured_payload_present')),
        'raw_response_type': type(raw_response).__name__,
        'raw_response_path': str(raw_path),
        'prompt_version': call.get('prompt_version') or ONE_CALL_PROMPT_VERSION,
        'schema_version': call.get('schema_version') or ONE_CALL_SCHEMA_VERSION,
    }
    call['provider_receipt'] = receipt
    return receipt

def _extract_json_object(text: str) -> dict[str, Any] | None:
    if not text.strip():
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S | re.I)
    candidates = [fenced.group(1)] if fenced else []
    start = text.find('{')
    if start >= 0:
        depth = 0
        in_str = False
        esc = False
        for i, ch in enumerate(text[start:], start):
            if in_str:
                esc = (ch == '\\' and not esc)
                if ch == '"' and not esc:
                    in_str = False
                elif ch != '\\':
                    esc = False
                continue
            if ch == '"':
                in_str = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    candidates.append(text[start:i + 1])
                    break
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
            return obj if isinstance(obj, dict) else None
        except Exception:
            continue
    return None

def _recover_payload(result: ProviderStageResult) -> tuple[dict[str, Any] | None, str | None]:
    if isinstance(result.payload, dict) and result.payload:
        return result.payload, None
    raw_value = result.raw_response or result.call_record.get('raw_response') or result.call_record.get('raw_body') or result.call_record.get('output_text')
    first_text: str | None = None
    for text in _response_text_candidates(raw_value):
        first_text = first_text or text.strip()
        parsed = _extract_json_object(text)
        if parsed:
            # If the parsed object is the provider envelope, recurse into common
            # body fields rather than accepting an empty wrapper as the result.
            if not any(k in parsed for k in ('document_identity', 'financial_tables', 'executive_summary', 'signals', 'hypotheses')):
                for nested in _response_text_candidates(parsed):
                    nested_parsed = _extract_json_object(nested)
                    if nested_parsed and any(k in nested_parsed for k in ('document_identity', 'financial_tables', 'executive_summary', 'signals', 'hypotheses')):
                        return nested_parsed, None
            return parsed, None
    return None, first_text or None

def _split_one_call_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    extraction_keys = {'document_identity','financial_tables','reported_facts','management_commitments','strategic_priorities','transformation_programmes','risks_and_pressures','technology_digital_ai','leadership_and_governance','customer_market_and_regulation','unknowns','extraction_coverage','citation_index'}
    synthesis_map = {
        'signals': 'strategic_signals',
        'key_changes': 'what_changed',
        'pressures_and_risks': 'enterprise_pressures',
        'questions_and_next_actions': 'questions_to_investigate',
        'unknowns_and_contradictions': 'unknowns',
    }
    extraction = {k: payload.get(k) for k in extraction_keys if k in payload}
    synthesis = {k: payload.get(k) for k in RapidAISynthesis.model_fields if k in payload}
    for src, dst in synthesis_map.items():
        if src in payload and dst not in synthesis:
            synthesis[dst] = payload.get(src)
    if 'executive_summary' in payload and 'executive_summary' not in synthesis:
        synthesis['executive_summary'] = payload.get('executive_summary')
    if 'commercial_themes' in payload:
        synthesis['commercial_themes'] = payload.get('commercial_themes')
    return extraction, synthesis


def _usable_counts(snapshot: dict[str, Any]) -> dict[str, int | bool]:
    analysis = snapshot.get('report_analysis') or {}
    analysis_sections = sum(1 for v in analysis.values() if isinstance(v, list) and v)
    financial_tables = snapshot.get('financial_tables') or ((snapshot.get('extraction_result') or {}).get('financial_tables') or [])
    financial_rows = sum(len(t.get('rows') or []) for t in financial_tables if isinstance(t, dict))
    rendered = sum(1 for v in [analysis.get('executive_summary'), financial_tables, analysis.get('what_changed'), snapshot.get('commitments'), snapshot.get('programmes'), analysis.get('enterprise_pressures'), snapshot.get('signals'), snapshot.get('hypotheses'), analysis.get('commercial_themes'), snapshot.get('unknowns'), snapshot.get('contradictions'), analysis.get('questions_to_investigate'), snapshot.get('learning_actions'), [snapshot.get('unstructured_ai_report')] if snapshot.get('unstructured_ai_report') else []] if v)
    return {'usable_structured_sections': int(bool(financial_rows)) + analysis_sections, 'financial_table_count': len(financial_tables), 'financial_row_count': financial_rows, 'analysis_section_count': analysis_sections, 'unstructured_fallback_available': bool(snapshot.get('unstructured_ai_report')), 'rendered_section_count': rendered}

def _safe_provider_failure(error: str | None, call: dict[str, Any], receipt: dict[str, Any] | None = None) -> tuple[str, str]:
    status = str(call.get('status') or call.get('provider_status') or '')
    error_text = str(error or call.get('error') or '').strip()
    if status == 'timeout' or 'timeout' in error_text.lower():
        return 'provider_timed_out', 'AI response unavailable — the provider timed out before returning usable content.'
    if status == 'cost_limit_exceeded':
        return 'cost_limit_exceeded', 'AI response unavailable — the configured cost limit prevented completion.'
    if status in {'provider_request_invalid', 'request_failed', 'provider_request_failed'} or error_text:
        return 'provider_rejected_request', 'Provider rejected Flora’s AI request because its requested output format was invalid.'
    if receipt and receipt.get('response_received') and not receipt.get('response_text_length'):
        return 'provider_empty_response', 'AI response unavailable — the provider returned an empty response.'
    return 'provider_empty_response', 'AI response unavailable — the provider returned no usable response content.'

def create_rapid_ai_twin_snapshot(acquired: AcquiredRapidSource, *, provider_boundary: Any | None = None, correlation_id: str | None = None, force_reprocess: bool = False) -> dict[str, Any]:
    started=time.monotonic(); correlation_id=correlation_id or ('rapid-ai-'+uuid.uuid4().hex[:8]); receipt=acquired.receipt.to_dict(); settings=financial_intelligence_settings(); model=settings.model
    key=cache_key(receipt.get('sha256'), model); cpath=_cache_path(key)
    if cpath.exists() and not force_reprocess:
        cached=json.loads(cpath.read_text()); cached['cache_state']='hit'; return cached
    provider_boundary = provider_boundary or RapidAITwinProvider()
    preflight = provider_preflight(acquired, provider_boundary, settings)
    if preflight['status'] != 'passed':
        return _failure(receipt, [], 'provider_preflight_failed', started, [{'code':'provider_preflight_failed','failed_checks':preflight['failed_checks']}], preflight=preflight)
    call_method = getattr(provider_boundary, 'analyse', None) or getattr(provider_boundary, 'extraction')
    s1=call_method(acquired, correlation_id)
    calls=[s1.call_record]
    provider_receipt = _persist_provider_response(correlation_id, s1.call_record, s1.raw_response or s1.payload, started)
    if s1.error and not (s1.payload or s1.raw_response or s1.call_record.get('raw_body') or s1.call_record.get('output_text')):
        return _failure(receipt, calls, s1.error or 'provider_empty', started, provider_receipt=provider_receipt, preflight=preflight)
    payload, unstructured = _recover_payload(s1)
    if not payload:
        if unstructured:
            snapshot=_partial_unstructured(receipt, calls, unstructured, started, provider_receipt, key, preflight)
            ensure_writable_dir(_cache_dir()); atomic_write_json(cpath, snapshot)
            return snapshot
        return _failure(receipt, calls, s1.error or 'provider_empty', started, provider_receipt=provider_receipt, preflight=preflight)
    extraction_payload, synthesis = _split_one_call_payload(payload)
    extraction, extraction_errors = validate_extraction(extraction_payload, receipt)
    if not extraction:
        if payload:
            extraction = extraction_payload | {'financial_tables': extraction_payload.get('financial_tables') or []}
            extraction_errors = extraction_errors + [{'code':'identity_or_period_partial','partial':True}]
        else:
            return _failure(receipt, calls, 'stage_1_identity_or_period_rejected', started, extraction_errors)
    synthesis_errors=[]
    if synthesis:
        synthesis, synthesis_errors = validate_synthesis(synthesis, extraction)
    has_content = bool((extraction.get('financial_tables') or []) or synthesis or (extraction.get('reported_facts') or []))
    truncated = str((s1.call_record.get('finish_reason') or s1.call_record.get('provider_status') or '')).lower() in {'length','max_output_tokens','incomplete'} or bool(s1.call_record.get('incomplete_details'))
    status = 'ready' if synthesis and has_content and not (extraction_errors or synthesis_errors or truncated) else 'partial'
    user_status = 'AI-built snapshot — verification pending' if status == 'ready' else 'Partial AI Twin Snapshot — verification pending'
    user_explanation = 'Flora reviewed the approved BT report in one bounded AI call and created this source-backed snapshot. It has not yet completed structured verification or canonical acceptance.' if status == 'ready' else 'Flora retained the largest useful provider response subset from one bounded AI call. Some extraction or synthesis fields are partial; verification and canonical acceptance have not completed.'
    snapshot={'version':'rapid-ai-twin-snapshot-v2','status':status,'verification_state':'verification_pending','canonical_state':{'trusted_twin_changed':False,'canonical_writes':0,'evidence_writes':0,'observation_writes':0,'enterprise_model_writes':0},'source_receipt':receipt,'provider_receipt':provider_receipt,'extraction_result':extraction,'financial_tables':extraction.get('financial_tables') or [],'candidate_facts':extraction.get('reported_facts') or [],'commitments':extraction.get('management_commitments') or [],'programmes':extraction.get('transformation_programmes') or [],'report_analysis':synthesis,'signals':synthesis.get('strategic_signals') or synthesis.get('signals') or [],'hypotheses':synthesis.get('hypotheses') or [],'unknowns':(extraction.get('unknowns') or []) + (synthesis.get('unknowns') or []),'contradictions':synthesis.get('contradictions') or [],'learning_actions':synthesis.get('recommended_learning_actions') or synthesis.get('questions_to_investigate') or [],'citation_coverage':_coverage(extraction, synthesis),'model_and_cost_record':{'provider_calls':calls,'ai_call_count':len([c for c in calls if c.get('status') not in {'not_executed','skipped'}]),'model':model,'input_tokens':sum(int((c.get('usage') or {}).get('input_tokens') or 0) for c in calls),'output_tokens':sum(int((c.get('usage') or {}).get('output_tokens') or 0) for c in calls),'estimated_provider_cost_usd':sum(float(c.get('estimated_or_actual_cost_usd') or 0) for c in calls),'elapsed_ms':int((time.monotonic()-started)*1000),'cache_key':key,'cache_state':'miss','schema_versions':{'one_call':ONE_CALL_SCHEMA_VERSION},'prompt_versions':{'one_call':ONE_CALL_PROMPT_VERSION}},'provider_preflight':preflight,'validation':{'extraction_errors':extraction_errors,'synthesis_errors':synthesis_errors,'partial_result': bool(extraction_errors or synthesis_errors or truncated),'truncated':truncated},'user_status':user_status,'user_explanation':user_explanation}
    snapshot['snapshot_truthfulness'] = {'snapshot_record_persisted': True, 'provider_response_persisted': bool(provider_receipt), **_usable_counts(snapshot)}
    ensure_writable_dir(_cache_dir()); atomic_write_json(cpath, snapshot)
    return snapshot

def _failure(receipt, calls, error, started, validation_errors=None, preflight=None, provider_receipt=None):
    last_call = calls[-1] if calls else {}
    failure_code, message = _safe_provider_failure(error, last_call, provider_receipt)
    snapshot = {'version':'rapid-ai-twin-snapshot-v2','status':'unavailable','verification_state':'no_provider_content','canonical_state':{'trusted_twin_changed':False,'canonical_writes':0,'evidence_writes':0,'observation_writes':0,'enterprise_model_writes':0},'source_receipt':receipt,'provider_receipt':provider_receipt or {},'extraction_result':{},'financial_tables':[],'report_analysis':{},'signals':[],'hypotheses':[],'unknowns':[],'contradictions':[],'learning_actions':[],'provider_preflight':preflight or {},'model_and_cost_record':{'provider_calls':calls,'ai_call_count':len([c for c in calls if c.get('status') not in {'not_executed','skipped'}]),'input_tokens':sum(int((c.get('usage') or {}).get('input_tokens') or 0) for c in calls),'output_tokens':sum(int((c.get('usage') or {}).get('output_tokens') or 0) for c in calls),'estimated_provider_cost_usd':sum(float(c.get('estimated_or_actual_cost_usd') or 0) for c in calls),'elapsed_ms':int((time.monotonic()-started)*1000)},'validation':{'error':error,'safe_failure_code':failure_code,'errors':validation_errors or []},'user_status':'AI response unavailable','user_explanation':message}
    snapshot['snapshot_truthfulness'] = {'snapshot_record_persisted': False, 'provider_response_persisted': bool(provider_receipt), **_usable_counts(snapshot)}
    return snapshot

def _partial_unstructured(receipt, calls, report_text, started, provider_receipt, key, preflight):
    snapshot = {'version':'rapid-ai-twin-snapshot-v2','status':'partial','verification_state':'verification_pending','canonical_state':{'trusted_twin_changed':False,'canonical_writes':0,'evidence_writes':0,'observation_writes':0,'enterprise_model_writes':0},'source_receipt':receipt,'provider_receipt':provider_receipt,'extraction_result':{},'financial_tables':[],'candidate_facts':[],'report_analysis':{},'unstructured_ai_report':report_text[:MAX_RAW_RESPONSE_BYTES],'signals':[],'hypotheses':[],'unknowns':[],'contradictions':[],'learning_actions':[],'citation_coverage':{'financial_table_row_count':0,'reported_fact_count':0,'signal_count':0,'hypothesis_count':0},'provider_preflight':preflight,'model_and_cost_record':{'provider_calls':calls,'ai_call_count':len([c for c in calls if c.get('status') not in {'not_executed','skipped'}]),'input_tokens':sum(int((c.get('usage') or {}).get('input_tokens') or 0) for c in calls),'output_tokens':sum(int((c.get('usage') or {}).get('output_tokens') or 0) for c in calls),'estimated_provider_cost_usd':sum(float(c.get('estimated_or_actual_cost_usd') or 0) for c in calls),'elapsed_ms':int((time.monotonic()-started)*1000),'cache_key':key,'cache_state':'miss','schema_versions':{'one_call':ONE_CALL_SCHEMA_VERSION},'prompt_versions':{'one_call':ONE_CALL_PROMPT_VERSION}},'validation':{'partial_result':True,'unstructured':True},'user_status':'Partial AI Twin Snapshot — report available','user_explanation':'Flora received and persisted a non-empty provider report, but no recoverable JSON object was available. The report is shown for review and remains outside trusted Twin state.'}
    snapshot['snapshot_truthfulness'] = {'snapshot_record_persisted': True, 'provider_response_persisted': bool(provider_receipt), **_usable_counts(snapshot)}
    return snapshot

def _coverage(extraction, synthesis):
    row_count=sum(len(t.get('rows') or []) for t in extraction.get('financial_tables') or [])
    cited_rows=sum(1 for t in extraction.get('financial_tables') or [] for r in t.get('rows') or [] if r.get('source_page'))
    facts=extraction.get('reported_facts') or []
    cited_facts=sum(1 for f in facts if f.get('source_page'))
    return {'financial_table_row_count':row_count,'financial_rows_with_page_citation':cited_rows,'reported_fact_count':len(facts),'reported_facts_with_page_citation':cited_facts,'signal_count':len(synthesis.get('strategic_signals') or []),'hypothesis_count':len(synthesis.get('hypotheses') or [])}

def _stage1_prompt(receipt: dict[str, Any]) -> str:
    return f"""Create Stage 1 Rapid AI Twin extraction JSON for BT Group FY26. Reproduce complete primary financial tables with all rows, current and comparator values, page citations and supporting excerpts. Extract report-wide facts, commitments, priorities, programmes, risks, technology/digital/AI themes, leadership, customer/market/regulation, unknowns and citation index. Confirm enterprise identity, document title, reporting period and page count. Source receipt: {json.dumps(receipt, sort_keys=True)}"""

def _one_call_prompt(receipt: dict[str, Any]) -> str:
    return (
        "Return exactly one JSON object and no prose, markdown or code fence. "
        "Create one compact JSON object for the BT Rapid AI Twin pilot. "
        "Use only the supplied BT FY26 report and source receipt. Perform both report extraction and executive synthesis in this single call. "
        "Include document_identity, executive_summary, financial_tables, key_changes, management_commitments, strategic_priorities, transformation_programmes, pressures_and_risks, technology_digital_ai, signals, hypotheses, commercial_themes, unknowns_and_contradictions, questions_and_next_actions. "
        "Financial tables must include the primary Group results table in full where practical; keep displayed values even where they do not map to canonical metrics. "
        "Every material finding, Signal and Hypothesis must have page references or cited table/report facts. "
        "Do not write trusted/canonical state. Source receipt: " + json.dumps(receipt, sort_keys=True)
    )
