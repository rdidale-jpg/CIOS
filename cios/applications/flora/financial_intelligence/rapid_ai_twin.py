"""AI-first Rapid Commercial Digital Twin snapshot lane.

The snapshot is persisted inside the standard Financial Intelligence run record
as candidate, verification-pending intelligence.  This module performs no
canonical Evidence, Observation or Enterprise Model writes.
"""
from __future__ import annotations

import csv, hashlib, io, json, os, time, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from cios.applications.flora.storage import data_path, ensure_writable_dir, atomic_write_json
from .config import financial_intelligence_settings
from .openai_provider import OpenAIDirectPDFProvider
from .rapid_sources import AcquiredRapidSource
from .schema import ExperimentDocument, openai_strict_json_schema

EXTRACTION_SCHEMA_VERSION = "rapid-ai-twin-extraction-v1"
SYNTHESIS_SCHEMA_VERSION = "rapid-ai-twin-synthesis-v1"
EXTRACTION_PROMPT_VERSION = "rapid-ai-bt-extraction-prompt-v1"
SYNTHESIS_PROMPT_VERSION = "rapid-ai-bt-synthesis-prompt-v1"

class RapidAIExtraction(BaseModel):
    model_config = ConfigDict(extra='forbid')
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

class RapidAITwinProvider:
    """Thin adapter over the existing OpenAI direct-PDF provider."""
    def __init__(self, provider: OpenAIDirectPDFProvider | None = None):
        self.provider = provider or OpenAIDirectPDFProvider(max_retries=1)

    def extraction(self, acquired: AcquiredRapidSource, correlation_id: str) -> ProviderStageResult:
        receipt = acquired.receipt
        document = ExperimentDocument(document_id=receipt.source_id, enterprise_id=receipt.enterprise_id, title=receipt.document_title, source_url=receipt.final_url or receipt.requested_url, retrieval_timestamp=receipt.retrieved_at, checksum=receipt.sha256 or '', media_type='application/pdf', page_count=int(getattr(receipt, 'page_count', None) or 1), local_path=str(acquired.path))
        instructions = _stage1_prompt(receipt.to_dict())
        return _run_openai_stage(self.provider, document, RapidAIExtraction, instructions, 'stage_1_report_extraction', correlation_id)

    def synthesis(self, extraction: dict[str, Any], citation_index: list[dict[str, Any]], correlation_id: str) -> ProviderStageResult:
        return _run_openai_text_stage(self.provider, extraction, citation_index, correlation_id)

def _usage_record(meta: dict[str, Any]) -> dict[str, Any]:
    usage = meta.get('usage') or {}
    return {'model': meta.get('model'), 'input_tokens': int(usage.get('input_tokens') or 0), 'output_tokens': int(usage.get('output_tokens') or 0), 'estimated_or_actual_cost_usd': float(usage.get('approximate_cost_usd') or meta.get('actual_cost_usd') or 0)}

def _run_openai_stage(provider: OpenAIDirectPDFProvider, document: ExperimentDocument, schema: type[BaseModel], instructions: str, stage: str, correlation_id: str) -> ProviderStageResult:
    started=time.time(); source_path=Path(document.local_path) if document.local_path else None
    if not os.getenv('OPENAI_API_KEY'):
        return ProviderStageResult(None, {'stage':stage,'provider':'openai','model':provider.model,'status':'not_executed','usage':{},'estimated_or_actual_cost_usd':0,'schema_version':EXTRACTION_SCHEMA_VERSION}, 'OPENAI_API_KEY is not configured')
    original = provider._input_payload
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
            resp=provider._invoke(client, document, schema, mode, source_path)
        except Exception as exc:
            if getattr(exc, 'code', None) != 'invalid_file_url':
                raise
            mode='file_data'; resp=provider._invoke(client, document, schema, mode, source_path)
        raw=resp.model_dump(mode='json') if hasattr(resp,'model_dump') else (resp if isinstance(resp,dict) else {})
        meta=provider._response_metadata(resp, raw, input_tokens=input_tokens, estimated_cost=estimated)
        parsed_obj=getattr(resp,'output_parsed',None)
        if parsed_obj is None:
            text=getattr(resp,'output_text','') or raw.get('output_text','')
            parsed_obj=schema.model_validate_json(text) if text else None
        if parsed_obj is None:
            return ProviderStageResult(None, {'stage':stage,'provider':'openai','model':provider.model,'status':'empty_response','usage':meta.get('usage') or {},'estimated_or_actual_cost_usd':meta.get('actual_cost_usd') or estimated,'elapsed_ms':int((time.time()-started)*1000),'schema_version':EXTRACTION_SCHEMA_VERSION}, 'empty structured response')
        payload=parsed_obj.model_dump() if hasattr(parsed_obj,'model_dump') else dict(parsed_obj)
        return ProviderStageResult(payload, {'stage':stage,'provider':'openai','model':provider.model,'status':'completed','usage':meta.get('usage') or {},'estimated_or_actual_cost_usd':meta.get('actual_cost_usd') or estimated,'elapsed_ms':int((time.time()-started)*1000),'schema_version':EXTRACTION_SCHEMA_VERSION})
    except Exception as exc:
        return ProviderStageResult(None, {'stage':stage,'provider':'openai','model':provider.model,'status':'provider_request_failed','usage':{},'estimated_or_actual_cost_usd':0,'elapsed_ms':int((time.time()-started)*1000),'schema_version':EXTRACTION_SCHEMA_VERSION}, f'{type(exc).__name__}: {exc}')
    finally:
        provider._input_payload = original  # type: ignore[method-assign]

def _run_openai_text_stage(provider: OpenAIDirectPDFProvider, extraction: dict[str, Any], citation_index: list[dict[str, Any]], correlation_id: str) -> ProviderStageResult:
    started=time.time(); settings=financial_intelligence_settings()
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
            return ProviderStageResult(None, {'stage':'stage_2_twin_synthesis','provider':'openai','model':provider.model,'status':'empty_response','usage':meta.get('usage') or {},'estimated_or_actual_cost_usd':meta.get('actual_cost_usd') or estimated,'elapsed_ms':int((time.time()-started)*1000),'schema_version':SYNTHESIS_SCHEMA_VERSION}, 'empty structured response')
        return ProviderStageResult(parsed_obj.model_dump(), {'stage':'stage_2_twin_synthesis','provider':'openai','model':provider.model,'status':'completed','usage':meta.get('usage') or {},'estimated_or_actual_cost_usd':meta.get('actual_cost_usd') or estimated,'elapsed_ms':int((time.time()-started)*1000),'schema_version':SYNTHESIS_SCHEMA_VERSION})
    except Exception as exc:
        return ProviderStageResult(None, {'stage':'stage_2_twin_synthesis','provider':'openai','model':provider.model,'status':'provider_request_failed','usage':{},'estimated_or_actual_cost_usd':0,'elapsed_ms':int((time.time()-started)*1000),'schema_version':SYNTHESIS_SCHEMA_VERSION}, f'{type(exc).__name__}: {exc}')

def _stage2_prompt(extraction: dict[str, Any], citation_index: list[dict[str, Any]]) -> str:
    return 'Create Stage 2 Rapid AI Twin synthesis JSON. Use only this Stage 1 extraction and citation index. Distinguish reported facts, interpretation, Signals, Hypotheses, Unknowns and Contradictions. Every Signal and Hypothesis must reference valid Stage 1 fact or table-row IDs. Do not add uncited assumptions. Stage 1 extraction: ' + json.dumps({'extraction': extraction, 'citation_index': citation_index}, sort_keys=True, default=str)

def _cache_dir() -> Path: return data_path('ai_financial_reports', 'rapid_ai_twin_cache')
def cache_key(sha256: str | None, model: str) -> str:
    raw = '|'.join([sha256 or '', model, EXTRACTION_SCHEMA_VERSION, SYNTHESIS_SCHEMA_VERSION, EXTRACTION_PROMPT_VERSION, SYNTHESIS_PROMPT_VERSION])
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
    if 'bt' not in str(ident.get('enterprise_name') or '').casefold(): errors.append({'code':'enterprise_mismatch','message':'AI did not identify BT Group.'})
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

def create_rapid_ai_twin_snapshot(acquired: AcquiredRapidSource, *, provider_boundary: Any | None = None, correlation_id: str | None = None, force_reprocess: bool = False) -> dict[str, Any]:
    started=time.time(); correlation_id=correlation_id or ('rapid-ai-'+uuid.uuid4().hex[:8]); receipt=acquired.receipt.to_dict(); settings=financial_intelligence_settings(); model=settings.model
    key=cache_key(receipt.get('sha256'), model); cpath=_cache_path(key)
    if cpath.exists() and not force_reprocess:
        cached=json.loads(cpath.read_text()); cached['cache_state']='hit'; return cached
    provider_boundary = provider_boundary or RapidAITwinProvider()
    s1=provider_boundary.extraction(acquired, correlation_id)
    calls=[s1.call_record]
    if s1.error or not s1.payload:
        return _failure(receipt, calls, s1.error or 'stage_1_empty', started)
    extraction, extraction_errors = validate_extraction(s1.payload, receipt)
    if not extraction:
        return _failure(receipt, calls, 'stage_1_identity_or_period_rejected', started, extraction_errors)
    s2=provider_boundary.synthesis(extraction, extraction.get('citation_index') or [], correlation_id)
    calls.append(s2.call_record)
    synthesis_errors=[]; synthesis=s2.payload or {}
    if synthesis:
        synthesis, synthesis_errors = validate_synthesis(synthesis, extraction)
    snapshot={'version':'rapid-ai-twin-snapshot-v1','status':'ready' if synthesis else 'partial','verification_state':'verification_pending','canonical_state':{'trusted_twin_changed':False,'canonical_writes':0,'evidence_writes':0,'observation_writes':0,'enterprise_model_writes':0},'source_receipt':receipt,'extraction_result':extraction,'financial_tables':extraction.get('financial_tables') or [],'candidate_facts':extraction.get('reported_facts') or [],'commitments':extraction.get('management_commitments') or [],'programmes':extraction.get('transformation_programmes') or [],'report_analysis':synthesis,'signals':synthesis.get('strategic_signals') or [],'hypotheses':synthesis.get('hypotheses') or [],'unknowns':(extraction.get('unknowns') or []) + (synthesis.get('unknowns') or []),'contradictions':synthesis.get('contradictions') or [],'learning_actions':synthesis.get('recommended_learning_actions') or [],'citation_coverage':_coverage(extraction, synthesis),'model_and_cost_record':{'provider_calls':calls,'ai_call_count':len([c for c in calls if c.get('status') not in {'not_executed'}]),'model':model,'input_tokens':sum(int((c.get('usage') or {}).get('input_tokens') or 0) for c in calls),'output_tokens':sum(int((c.get('usage') or {}).get('output_tokens') or 0) for c in calls),'estimated_provider_cost_usd':sum(float(c.get('estimated_or_actual_cost_usd') or 0) for c in calls),'elapsed_ms':int((time.time()-started)*1000),'cache_key':key,'cache_state':'miss','schema_versions':{'extraction':EXTRACTION_SCHEMA_VERSION,'synthesis':SYNTHESIS_SCHEMA_VERSION},'prompt_versions':{'extraction':EXTRACTION_PROMPT_VERSION,'synthesis':SYNTHESIS_PROMPT_VERSION}},'validation':{'extraction_errors':extraction_errors,'synthesis_errors':synthesis_errors,'partial_result': bool(extraction_errors or s2.error)},'user_status':'AI-built snapshot — verification pending','user_explanation':'Flora reviewed the approved BT report and created this source-backed snapshot. It has not yet completed structured verification or canonical acceptance.'}
    ensure_writable_dir(_cache_dir()); atomic_write_json(cpath, snapshot)
    return snapshot

def _failure(receipt, calls, error, started, validation_errors=None):
    return {'version':'rapid-ai-twin-snapshot-v1','status':'unavailable','verification_state':'verification_pending','canonical_state':{'trusted_twin_changed':False,'canonical_writes':0},'source_receipt':receipt,'extraction_result':{},'financial_tables':[],'report_analysis':{},'signals':[],'hypotheses':[],'unknowns':['Flora retrieved the approved BT report but could not create a safe AI Twin Snapshot.'],'contradictions':[],'learning_actions':[],'model_and_cost_record':{'provider_calls':calls,'ai_call_count':len(calls),'elapsed_ms':int((time.time()-started)*1000)},'validation':{'error':error,'errors':validation_errors or []},'user_status':'AI-built snapshot unavailable','user_explanation':'Flora retrieved the approved BT report but could not create a safe AI Twin Snapshot.'}

def _coverage(extraction, synthesis):
    row_count=sum(len(t.get('rows') or []) for t in extraction.get('financial_tables') or [])
    cited_rows=sum(1 for t in extraction.get('financial_tables') or [] for r in t.get('rows') or [] if r.get('source_page'))
    facts=extraction.get('reported_facts') or []
    cited_facts=sum(1 for f in facts if f.get('source_page'))
    return {'financial_table_row_count':row_count,'financial_rows_with_page_citation':cited_rows,'reported_fact_count':len(facts),'reported_facts_with_page_citation':cited_facts,'signal_count':len(synthesis.get('strategic_signals') or []),'hypothesis_count':len(synthesis.get('hypotheses') or [])}

def _stage1_prompt(receipt: dict[str, Any]) -> str:
    return f"""Create Stage 1 Rapid AI Twin extraction JSON for BT Group FY26. Reproduce complete primary financial tables with all rows, current and comparator values, page citations and supporting excerpts. Extract report-wide facts, commitments, priorities, programmes, risks, technology/digital/AI themes, leadership, customer/market/regulation, unknowns and citation index. Confirm enterprise identity, document title, reporting period and page count. Source receipt: {json.dumps(receipt, sort_keys=True)}"""
