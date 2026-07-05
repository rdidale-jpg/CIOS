"""AI document-understanding review workflow for Flora financial reports."""
from __future__ import annotations

from cios.applications.flora.storage import PersistenceError, atomic_write_json, data_path, ensure_writable_dir, storage_mode

import hashlib, json, logging, os, re, shutil, sys, threading, time, uuid
from types import SimpleNamespace
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from cios.applications.flora.financial_intelligence.openai_provider import OpenAIDirectPDFProvider, openai_sdk_readiness
from cios.applications.flora.financial_intelligence.section_packets import SectionAwareOpenAIProvider
from cios.applications.flora.financial_intelligence.config import financial_intelligence_settings
from cios.applications.flora.financial_intelligence.schema import ExperimentDocument, FoundationFact
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.memory.views import enterprise_memory_panel
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.live.documents import fetch_document, parse_pdf_document
from cios.applications.flora.workspace.views import _page

def _review_dir() -> Path: return data_path('ai_financial_reports')
def _upload_dir() -> Path: return data_path('ai_financial_reports', 'uploads')
def _run_dir() -> Path: return data_path('ai_financial_reports', 'runs')

# Backwards-compatible module attributes; runtime code resolves dynamically through helpers.
REVIEW_DIR = _review_dir()
UPLOAD_DIR = _upload_dir()
RUN_DIR = _run_dir()
DEFAULT_MODEL = financial_intelligence_settings().model
BT_PROFILE = Path(__file__).resolve().parents[3] / 'config/flora/collection_profiles/bt-group-plc.json'
AUTO_ACCEPT_CONFIDENCE = int(os.getenv('FLORA_FINANCIAL_INTELLIGENCE_AUTO_ACCEPT_CONFIDENCE', '85'))
LOGGER = logging.getLogger('flora.financial_intelligence')

def configure_financial_intelligence_logging() -> logging.Logger:
    if not LOGGER.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
        LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.ERROR)
    LOGGER.propagate = False
    return LOGGER

configure_financial_intelligence_logging()

FAILURE_MESSAGES = {
    'source_retrieval_failed': 'Flora could not retrieve the financial report.',
    'source_not_pdf': 'Flora could not retrieve the financial report.',
    'provider_not_configured': 'Financial document understanding is temporarily unavailable.',
    'provider_sdk_unavailable': 'Financial document understanding is temporarily unavailable.',
    'provider_authentication_failed': 'Financial document understanding is temporarily unavailable.',
    'provider_request_failed': 'Financial document understanding could not complete.',
    'provider_quota_exceeded': 'Financial document understanding could not complete.',
    'request_exceeds_tpm_limit': 'Flora is dividing this large report into manageable financial sections.',
    'cost_limit_exceeded': 'Financial document understanding was blocked by the configured cost limit.',
    'cost_preflight_sdk_unavailable': 'Financial document understanding could not use SDK token preflight; bounded pilot controls apply.',
    'cost_preflight_request_failed': 'Financial document understanding could not safely complete token preflight.',
    'context_limit_exceeded': 'Financial document understanding could not complete because the report exceeds model context.',
    'provider_model_unavailable': 'Financial document understanding could not complete.',
    'provider_file_upload_failed': 'Financial document understanding could not complete.',
    'provider_request_invalid': 'Financial document understanding could not complete.',
    'provider_timeout': 'Financial document understanding could not complete.',
    'provider_response_invalid': 'Financial document understanding could not complete.',
    'section_selection_failed': 'Flora could not identify the financial sections in this report.',
    'persistence_failed': 'Flora understood the report but could not save the results.',
}

def _failure_message(category: str) -> str:
    return FAILURE_MESSAGES.get(category, 'Financial document understanding is temporarily unavailable.')

def _provider_failure_category(extraction) -> str:
    if not extraction:
        return 'provider_request_failed'
    errors = '; '.join(getattr(extraction, 'provider_errors', []) or [])
    status = getattr(extraction, 'status', '')
    diagnostics = getattr(extraction, 'diagnostics', []) or []
    diagnostic_types = {d.get('provider_error_type') for d in diagnostics if isinstance(d, dict)}
    if status == 'not_executed' and 'provider_sdk_unavailable' in diagnostic_types:
        return 'provider_sdk_unavailable'
    if status == 'not_executed' and 'OPENAI_API_KEY' in errors:
        return 'provider_not_configured'
    return {
        'authentication_failed': 'provider_authentication_failed',
        'quota_exceeded': 'provider_quota_exceeded',
        'provider_quota_exceeded': 'provider_quota_exceeded',
        'request_exceeds_tpm_limit': 'request_exceeds_tpm_limit',
        'cost_limit_exceeded': 'cost_limit_exceeded',
        'cost_preflight_sdk_unavailable': 'cost_preflight_sdk_unavailable',
        'cost_preflight_request_failed': 'cost_preflight_request_failed',
        'context_limit_exceeded': 'context_limit_exceeded',
        'model_unavailable': 'provider_model_unavailable',
        'file_upload_failed': 'provider_file_upload_failed',
        'invalid_request': 'provider_request_invalid',
        'provider_request_invalid': 'provider_request_invalid',
        'timeout': 'provider_timeout',
        'invalid_response': 'provider_response_invalid',
    }.get(status, 'provider_response_invalid' if getattr(extraction, 'schema_errors', None) else 'provider_request_failed')

def _support_reference(run: dict[str, Any]) -> str:
    diagnostics = run.get('provider_diagnostics') or []
    ref = next((d.get('support_reference') for d in diagnostics if isinstance(d, dict) and d.get('support_reference')), None)
    if ref:
        return str(ref)
    correlation = next((d.get('correlation_id') for d in reversed(diagnostics) if isinstance(d, dict) and d.get('correlation_id')), None) or run.get('run_id') or uuid.uuid4().hex[:12]
    support = 'FI-' + str(correlation).replace('fi-', '').replace('FI-', '')
    return support if support != 'FI-' else 'FI-' + uuid.uuid4().hex[:12]

def _dedupe_exceptions(exceptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set(); out = []
    for e in exceptions or []:
        key = (e.get('failure_stage') or e.get('exception_type'), e.get('packet_id'), e.get('support_reference'))
        if key in seen:
            continue
        seen.add(key); out.append(e)
    return out

def _mark_failure(run: dict[str, Any], category: str, technical_reason: str) -> dict[str, Any]:
    run['status'] = category
    run['failure_category'] = category
    run['support_reference'] = _support_reference(run)
    base_message = _failure_message(category)
    if category.startswith('provider_') and category != 'provider_not_configured':
        base_message = 'Financial document understanding could not complete.'
    run['user_message'] = base_message
    run['user_message_display'] = f"{base_message} Support reference: {run['support_reference']}"
    new_exception = {'exception_type': category, 'failure_stage': category, 'support_reference': run['support_reference'], 'rejection_reason': technical_reason, 'user_message': run['user_message']}
    run['exceptions'] = [new_exception] if category == 'persistence_failed' else _dedupe_exceptions((run.get('exceptions') or []) + [new_exception])
    run['auto_accepted_count'] = 0; run['exception_count'] = len(run['exceptions']); run['observations_created_or_strengthened'] = 0; run['enterprise_attributes_changed'] = []
    return run


def now_iso() -> str: return datetime.now(UTC).isoformat(timespec='seconds')

def _safe_message(message: str) -> str:
    message = re.sub(r'sk-[A-Za-z0-9_\-]+', 'sk-REDACTED', message or '')
    message = re.sub(r'Bearer\s+[A-Za-z0-9._\-]+', 'Bearer REDACTED', message, flags=re.I)
    message = re.sub(r'(?i)(api[_-]?key|authorization|auth(?:entication)?)[=:]\s*[^\s,;]+', r'\1=REDACTED', message)
    return message[:700]

def _safe_provider_diagnostic(run_id: str, source: dict[str, Any], fetched: Any, model: str, started: float) -> dict[str, Any]:
    return {
        'correlation_id': run_id,
        'timestamp': now_iso(),
        'provider': 'openai',
        'requested_model': model,
        'request_stage': 'source_retrieval',
        'source_document_retrieval_result': bool(getattr(fetched, 'succeeded', False)),
        'source_content_type': getattr(fetched, 'media_type', None),
        'source_file_size': len(getattr(fetched, 'content', b'') or b''),
        'source_final_url': getattr(fetched, 'final_url', None) or getattr(fetched, 'url', None),
        'source_input_mode': None,
        'pdf_upload_succeeded': False,
        'http_status_code': getattr(fetched, 'status_code', None),
        'provider_error_type': 'source_retrieval_failed' if not getattr(fetched, 'succeeded', False) else None,
        'provider_error_code': None,
        'sanitised_provider_error_message': _safe_message(str(getattr(fetched, 'error', '') or '')),
        'retryable': not bool(getattr(fetched, 'succeeded', False)),
        'elapsed_time': round(time.time() - started, 3),
    }

def _record_provider_diagnostics(run: dict[str, Any]) -> None:
    for event in run.get('provider_diagnostics') or []:
        print('Flora provider diagnostic ' + json.dumps(event, sort_keys=True), flush=True)



def _log_financial_intelligence_failure(event: dict[str, Any]) -> None:
    payload = {
        'event': 'flora_financial_intelligence_provider_failure',
        'support_reference': 'FI-' + str(event.get('correlation_id', '')).replace('FI-', '').replace('fi-', ''),
        'failure_stage': event.get('request_stage'),
        'provider': event.get('provider'),
        'requested_model': event.get('requested_model'),
        'http_status_code': event.get('http_status_code'),
        'provider_error_type': event.get('provider_error_type'),
        'provider_error_code': event.get('provider_error_code'),
        'sanitised_provider_error_message': event.get('sanitised_provider_error_message'),
        'retryable': event.get('retryable'),
        'elapsed_time': event.get('elapsed_time'),
    }
    LOGGER.error(json.dumps(payload, sort_keys=True))

def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))

def _write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_json(path, data)

def _run_path(run_id: str) -> Path: return _run_dir() / f'{run_id}.json'

def _write_progress(run_id: str, status: str, **extra: Any) -> None:
    try:
        run = _read_json(_run_path(run_id)) if _run_path(run_id).is_file() else {'run_id': run_id, 'created_at': now_iso(), 'claims': [], 'applied_results': [], 'exceptions': []}
        run.update({'status': status, **extra})
        events = run.setdefault('progress_events', [])
        events.append({'status': status, 'at': now_iso()})
        _write_json(_run_path(run_id), run)
    except Exception:
        LOGGER.exception('Could not write Financial Intelligence progress for run_id=%s', run_id)

def _evidence_id(run_id: str, fact_id: str) -> str:
    return 'AI-EV-' + hashlib.sha256(f'{run_id}:{fact_id}'.encode()).hexdigest()[:16].upper()

def fact_to_review_claim(fact: FoundationFact, run_id: str) -> dict[str, Any]:
    statement = _statement(fact)
    return {
        'claim_id': fact.fact_id,
        'review_state': 'pending',
        'original_statement': statement,
        'amended_statement': statement,
        'claim_type': _memory_claim_type(str(fact.claim_type)),
        'canonical_enterprise_id': fact.canonical_enterprise_id,
        'affected_attribute': _affected_attribute(fact),
        'value': fact.value_number if fact.value_number is not None else fact.value_text,
        'unit': fact.scale or fact.unit,
        'currency': fact.currency,
        'business_unit': fact.business_unit or fact.subject_name,
        'period': fact.period_label,
        'state': str(fact.state),
        'confidence': int(round(fact.extraction_confidence * 100)),
        'page_reference': str(fact.source_page_start) if fact.source_page_start == fact.source_page_end else f'{fact.source_page_start}-{fact.source_page_end}',
        'source_excerpt': fact.source_excerpt,
        'extractor_provider': fact.extractor_provider,
        'extractor_model': fact.extractor_model,
        'evidence_id': _evidence_id(run_id, fact.fact_id),
    }

def _memory_claim_type(claim_type: str) -> str:
    if claim_type in {'financial_guidance_stated', 'financial_target_stated'}:
        return 'financial_metric_reported'
    return claim_type


def _affected_attribute(f: FoundationFact) -> str:
    ct = str(f.claim_type)
    period = (f.period_label or 'reported_period').replace(' ', '_')
    pred = hashlib.sha256(f'{f.subject_name}:{f.predicate}:{f.business_unit}:{f.value_text}:{f.value_number}'.encode()).hexdigest()[:10]
    if 'financial_' in ct:
        metric = (f.predicate or f.object_type or 'metric').casefold().replace(' ', '_')
        return f'financial_performance.metrics.{metric}.{period}.{f.state}'
    if ct == 'business_unit_disclosed': return f'structure.units.{f.subject_name}'
    if ct == 'strategic_pillar_stated': return f'strategy.pillars.{f.value_text or f.subject_name}'
    if ct == 'strategic_commitment_stated': return f'strategy.commitments.{pred}'
    if ct == 'executive_role_confirmed': return f'leadership.roles.{f.predicate or f.object_type}'
    if ct.startswith('executive_'): return f'leadership.changes.{pred}'
    return f'identity.{pred}'

def _statement(f: FoundationFact) -> str:
    value = f.value_text if f.value_text is not None else f.value_number
    value_part = f' {value}' if value is not None else ''
    scale = f' {f.scale}' if f.scale else ''
    curr = f' {f.currency}' if f.currency else ''
    period = f' for {f.period_label}' if f.period_label else ''
    bu = f' in {f.business_unit}' if f.business_unit else ''
    return f'{f.subject_name}{bu} {f.predicate}{value_part}{scale}{curr}{period}.'.replace('  ', ' ')

def claim_to_evidence(run: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any]:
    return {
        'evidence_id': claim['evidence_id'], 'enterprise_id': claim['canonical_enterprise_id'], 'canonical_enterprise_id': claim['canonical_enterprise_id'],
        'organisation': claim['canonical_enterprise_id'], 'source_id': run['document']['document_id'], 'source_name': run['document']['title'],
        'source_type': 'annual_report', 'source_url': run['document']['source_url'], 'evidence_tier': 'tier_1_company',
        'commercial_condition': claim['claim_type'], 'cleaned_observation': claim.get('amended_statement') or claim['original_statement'],
        'extracted_observation': claim.get('amended_statement') or claim['original_statement'], 'snippet': claim.get('source_excerpt') or '',
        'affected_attribute': claim['affected_attribute'], 'value': claim.get('value'), 'unit': claim.get('unit'), 'currency': claim.get('currency'),
        'period': claim.get('period'), 'state': claim.get('state', 'actual'), 'confidence': claim.get('confidence', 80),
        'page_range': claim.get('page_reference'), 'page_number': claim.get('page_reference'), 'publication_date': run['document'].get('publication_date'),
        'extraction_timestamp': now_iso(), 'provenance': 'evidence-backed', 'source_provenance': 'ai_document_understanding_reviewed',
        'extractor_name': 'OpenAIDirectPDFProvider', 'extractor_model': claim.get('extractor_model'), 'document_checksum': run['document']['checksum'],
        'source_excerpt': claim.get('source_excerpt'),
    }



def _successful_cached_run(document: ExperimentDocument, model: str) -> dict[str, Any] | None:
    settings = financial_intelligence_settings()
    if not document.checksum:
        return None
    run_dir = _run_dir()
    if not run_dir.exists():
        return None
    for path in sorted(run_dir.glob('fi-*.json'), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            run = _read_json(path)
        except Exception:
            continue
        doc = run.get('document') or {}
        if (run.get('status') == 'completed' and doc.get('checksum') == document.checksum and run.get('model') == model and run.get('schema_version') == settings.schema_version and run.get('prompt_version') == settings.prompt_version):
            return run
    return None

def _lock_path(document: ExperimentDocument, model: str) -> Path:
    key = hashlib.sha256(f"{document.checksum}:{model}:foundation-fact-set-v1:financial-material-facts-v1".encode()).hexdigest()[:24]
    return _run_dir() / f'.{key}.lock'

def _write_cost_record(run: dict[str, Any]) -> None:
    ensure_writable_dir(_run_dir())
    path = _run_dir() / 'cost_records.jsonl'
    usage = run.get('usage') or run.get('provider_usage') or {}
    record = {
        'enterprise': run.get('document', {}).get('enterprise_id'),
        'document_hash': run.get('document_hash') or run.get('document', {}).get('checksum'),
        'model': run.get('model'),
        'reasoning_effort': run.get('reasoning_effort'),
        'input_tokens': usage.get('input_tokens') or run.get('input_tokens'),
        'cached_input_tokens': usage.get('input_tokens_details', {}).get('cached_tokens') if isinstance(usage.get('input_tokens_details'), dict) else usage.get('cached_input_tokens'),
        'output_tokens': usage.get('output_tokens'),
        'reasoning_tokens': usage.get('output_tokens_details', {}).get('reasoning_tokens') if isinstance(usage.get('output_tokens_details'), dict) else usage.get('reasoning_tokens'),
        'input_cost': (run.get('cost_breakdown') or {}).get('input_cost_usd'),
        'output_cost': (run.get('cost_breakdown') or {}).get('output_cost_usd'),
        'estimated_cost': run.get('estimated_cost_usd'),
        'actual_calculated_cost': run.get('actual_cost_usd'),
        'exact_preflight_available': run.get('exact_preflight_available'),
        'timestamp': now_iso(),
        'success': run.get('status') == 'completed',
        'cached_output_reused': bool(run.get('cached_output_reused')),
    }
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, sort_keys=True) + '\n')

def _bt_annual_report_source() -> dict[str, Any]:
    profile = _read_json(BT_PROFILE)
    for source in profile.get('sources', []):
        if source.get('source_id') == 'bt-annual-report-2026':
            return source
    raise ValueError('BT governed annual-report source not found')

def _source_obj(source: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(source_id=source['source_id'], source_name=source['source_name'], url=source['url'], source_type=source.get('source_type', 'annual_report'), evidence_tier=source.get('authority_tier', 'tier_1_company_authoritative'), authority_tier=source.get('authority_tier', 'tier_1_company_authoritative'), organisation=source.get('publisher', 'BT Group plc'))

def _is_auto_acceptable(claim: dict[str, Any], run: dict[str, Any]) -> tuple[bool, str]:
    if not run.get('governed_source') or not run.get('document', {}).get('checksum'):
        return False, 'source lineage is not governed and complete'
    if claim.get('claim_type') != 'financial_metric_reported':
        return False, 'unsupported fact type for automatic financial acceptance'
    if int(claim.get('confidence') or 0) < AUTO_ACCEPT_CONFIDENCE:
        return False, 'confidence below governed acceptance threshold'
    required = ('value', 'unit', 'currency', 'period', 'state', 'page_reference', 'affected_attribute')
    missing = [field for field in required if not claim.get(field)]
    if missing:
        return False, 'missing ' + ', '.join(missing)
    if not claim.get('business_unit') and 'bt group' not in claim.get('original_statement', '').casefold():
        return False, 'unclear group or segment scope'
    return True, 'governed source, page lineage, value, unit, currency, period, basis and confidence verified'

def _apply_automatic_claims(run: dict[str, Any]) -> dict[str, Any]:
    svc = ObservationMemoryService(); results=[]; exceptions=[]; accepted=0
    for claim in run.get('claims', []):
        ok, reason = _is_auto_acceptable(claim, run)
        claim['acceptance_reason'] = reason
        if not ok:
            claim['review_state'] = 'needs_attention'
            claim['exception_type'] = reason
            exceptions.append(claim)
            continue
        report = svc.process_evidence(claim_to_evidence(run, claim))
        results.extend(r.__dict__ for r in report.results)
        if report.results and not any(r.contradiction for r in report.results):
            claim['review_state'] = 'auto_applied'
            accepted += 1
        else:
            claim['review_state'] = 'needs_attention'
            claim['exception_type'] = 'contradiction or validation issue'
            exceptions.append(claim)
        exceptions.extend(report.rejected_claims)
    changed = [r for r in results if r.get('update_result') in {'created', 'updated'}]
    run.update({'status': 'completed', 'applied_at': now_iso(), 'applied_results': results, 'exceptions': exceptions, 'auto_accepted_count': accepted, 'exception_count': len(exceptions), 'observations_created_or_strengthened': len(results), 'enterprise_attributes_changed': [r.get('affected_attribute') for r in changed]})
    return run

def refresh_financial_intelligence(enterprise_id: str = 'bt-group-plc', run_id: str | None = None) -> dict[str, Any]:
    source = _bt_annual_report_source()
    run_id = run_id or ('fi-' + uuid.uuid4().hex[:12])
    correlation_id = run_id.removeprefix('fi-')
    ensure_writable_dir(_run_dir())
    retrieval_started = time.time()
    _write_progress(run_id, 'retrieving_source')
    fetched = fetch_document(source['url'])
    doc_parse = parse_pdf_document(fetched, _source_obj(source), canonical_enterprise_id='bt-group-plc')
    document = ExperimentDocument(document_id=doc_parse.document_id, enterprise_id='bt-group-plc', title=source['source_name'], source_url=(fetched.final_url or source['url']), retrieval_timestamp=doc_parse.retrieval_date, checksum=doc_parse.checksum, media_type=doc_parse.media_type or 'application/pdf', page_count=max(doc_parse.page_count, 1), local_path=doc_parse.local_path)
    settings = financial_intelligence_settings()
    provider = OpenAIDirectPDFProvider(model=settings.model, reasoning_effort=settings.reasoning_effort, max_output_tokens=settings.max_output_tokens, max_run_cost_usd=settings.max_run_cost_usd)

    _write_progress(run_id, 'selecting_sections', collection={'retrieved': fetched.succeeded, 'retrieval_time': fetched.retrieval_date, 'http_status': fetched.status_code, 'error': fetched.error})
    cached = _successful_cached_run(document, provider.model) if fetched.succeeded else None
    if cached:
        run = dict(cached)
        run['run_id'] = run_id
        run['created_at'] = now_iso()
        run['cached_output_reused'] = True
        run['openai_invoked'] = False
        _write_json(_run_path(run_id), run)
        _write_cost_record(run)
        return run

    lock_path = _lock_path(document, provider.model)
    if fetched.succeeded:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except FileExistsError:
            run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'provider_request_failed', 'workflow': 'financial_intelligence', 'document': document.model_dump(), 'model': provider.model, 'reasoning_effort': provider.reasoning_effort, 'document_hash': document.checksum, 'cached_output_reused': False, 'openai_invoked': False, 'exceptions': [{'exception_type': 'duplicate_in_progress', 'user_message': 'Financial Intelligence refresh is already running for this document.'}], 'claims': [], 'applied_results': []}
            _write_json(_run_path(run_id), run)
            return run

    if fetched.succeeded:
        try:
            _write_progress(run_id, 'estimating_cost')
            if os.getenv('OPENAI_API_KEY') and doc_parse.pages:
                _write_progress(run_id, 'analysing')
                extraction, packet_plan = SectionAwareOpenAIProvider(provider).extract_packets(document, doc_parse.pages, correlation_id=correlation_id)
            else:
                extraction = provider.extract_facts(document, correlation_id=correlation_id)
                packet_plan = {}
        except TypeError as exc:
            if 'correlation_id' not in str(exc):
                raise
            extraction = provider.extract_facts(document)
            packet_plan = {}
    else:
        extraction = None
    packet_plan = locals().get('packet_plan', {})
    _write_progress(run_id, 'validating')
    claims = [fact_to_review_claim(f, run_id) for f in (extraction.facts if extraction else [])]
    candidate_exceptions = list(getattr(extraction, 'candidate_exceptions', []) if extraction else [])
    run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'validating', 'workflow': 'financial_intelligence', 'governed_source': source, 'collection': {'retrieved': fetched.succeeded, 'retrieval_time': fetched.retrieval_date, 'http_status': fetched.status_code, 'error': fetched.error, 'active_source_url': source['url'], 'document_size': len(fetched.content or b'')}, 'document': document.model_dump(), 'provider': (extraction.provider if extraction else 'openai'), 'model': (extraction.model if extraction else provider.model), 'reasoning_effort': getattr(provider, 'reasoning_effort', settings.reasoning_effort), 'schema_version': settings.schema_version, 'prompt_version': settings.prompt_version, 'document_hash': document.checksum, 'usage': (extraction.usage if extraction else {}), 'estimated_cost_usd': (extraction.estimated_cost_usd if extraction else None), 'actual_cost_usd': (getattr(extraction, 'verifier', {}) or {}).get('actual_cost_usd') if extraction else None, 'cost_breakdown': {'input_cost_usd': (getattr(extraction, 'verifier', {}) or {}).get('input_cost_usd'), 'output_cost_usd': (getattr(extraction, 'verifier', {}) or {}).get('output_cost_usd')} if extraction else {}, 'exact_preflight_available': (getattr(extraction, 'verifier', {}) or {}).get('exact_preflight_available') if extraction else None, 'provider_status': (extraction.status if extraction else 'not_executed'), 'provider_errors': (extraction.provider_errors if extraction else [fetched.error]), 'raw_response_location': (extraction.raw_response_location if extraction else None), 'provider_diagnostics': (getattr(extraction, 'diagnostics', []) if extraction else [_safe_provider_diagnostic(run_id, source, fetched, provider.model, retrieval_started)]), 'openai_invoked': bool(extraction and (not packet_plan or packet_plan.get('packet_count', 0))), 'claims': claims, 'applied_results': [], 'candidate_exceptions': candidate_exceptions, 'candidate_pages_selected': packet_plan.get('candidate_pages', []), 'page_packets_submitted': packet_plan.get('packets', []), 'packet_count': packet_plan.get('packet_count', 0)}
    run['collection'].update({'final_url': fetched.final_url or fetched.url, 'content_type': fetched.media_type, 'redirect_chain': list(fetched.redirect_chain), 'redirected': bool(fetched.redirect_chain)})
    if extraction:
        run['provider_diagnostics'] = [_safe_provider_diagnostic(run_id, source, fetched, provider.model, retrieval_started)] + run.get('provider_diagnostics', [])
    if not fetched.succeeded:
        _log_financial_intelligence_failure(run['provider_diagnostics'][-1])
        run = _mark_failure(run, 'source_retrieval_failed', fetched.error or 'governed source retrieval failed')
    elif document.media_type != 'application/pdf':
        _log_financial_intelligence_failure(run['provider_diagnostics'][-1])
        run = _mark_failure(run, 'source_not_pdf', doc_parse.error or f"source returned {document.media_type}")
    elif extraction and extraction.status in {'completed', 'completed_with_exceptions'}:
        try:
            _write_progress(run_id, 'updating_memory')
            run = _apply_automatic_claims(run)
            if candidate_exceptions:
                run['exceptions'] = run.get('exceptions', []) + candidate_exceptions
                run['exception_count'] = len(run.get('exceptions', []))
                run['status'] = 'completed_with_exceptions'
        except Exception as exc:
            run = _mark_failure(run, 'persistence_failed', f'{type(exc).__name__}: {exc}')
    else:
        run = _mark_failure(run, _provider_failure_category(extraction), '; '.join(run.get('provider_errors') or ['provider did not complete']))
        if candidate_exceptions:
            run['exceptions'] = run.get('exceptions', []) + candidate_exceptions
            run['exception_count'] = len(run.get('exceptions', []))
    run['support_reference'] = _support_reference(run)
    run['exceptions'] = _dedupe_exceptions(run.get('exceptions', []))
    run['exception_count'] = len(run.get('exceptions', []))
    _record_provider_diagnostics(run)
    _write_cost_record(run)
    if fetched.succeeded:
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass
    try:
        _write_json(_run_path(run_id), run)
    except PersistenceError as exc:
        run = _mark_failure(run, 'persistence_failed', f'{type(exc).__name__}: {exc}')
    return run


def _active_refresh_run() -> dict[str, Any] | None:
    if not _run_dir().exists(): return None
    for path in sorted(_run_dir().glob('fi-*.json'), key=lambda p: p.stat().st_mtime, reverse=True):
        run = _read_json(path)
        if run.get('status') in {'queued','retrieving_source','selecting_sections','estimating_cost','analysing','validating','updating_memory'}:
            return run
    return None

def create_financial_intelligence_progress_run(enterprise_id: str = 'bt-group-plc') -> dict[str, Any]:
    active = _active_refresh_run()
    if active: return active
    run_id = 'fi-' + uuid.uuid4().hex[:12]
    run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'queued', 'workflow': 'financial_intelligence', 'enterprise_id': enterprise_id, 'support_reference': 'FI-' + run_id.removeprefix('fi-'), 'claims': [], 'applied_results': [], 'exceptions': []}
    _write_json(_run_path(run_id), run)
    threading.Thread(target=_background_refresh, args=(enterprise_id, run_id), daemon=True).start()
    return run

def _background_refresh(enterprise_id: str, run_id: str) -> None:
    try:
        refresh_financial_intelligence(enterprise_id=enterprise_id, run_id=run_id)
    except Exception as exc:
        LOGGER.exception('Financial Intelligence background refresh failed support_reference=%s', 'FI-' + run_id.removeprefix('fi-'))
        run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'failed', 'failure_category': 'failed', 'support_reference': 'FI-' + run_id.removeprefix('fi-'), 'exceptions': [{'exception_type': 'failed', 'failure_stage': 'failed', 'support_reference': 'FI-' + run_id.removeprefix('fi-'), 'user_message': 'Financial Intelligence refresh failed safely.', 'rejection_reason': f'{type(exc).__name__}: {exc}'}], 'claims': [], 'applied_results': []}
        _write_json(_run_path(run_id), run)

def financial_intelligence_progress_page(run_id: str) -> str:
    run = load_run(run_id)
    labels = {'queued': 'Queued', 'retrieving_source': 'Retrieving the financial report', 'selecting_sections': 'Reading the report structure / Finding relevant financial sections', 'estimating_cost': 'Estimating processing cost', 'analysing': 'Analysing financial sections', 'validating': 'Validating financial facts', 'updating_memory': 'Updating the Commercial Digital Twin', 'completed': 'Complete', 'completed_with_exceptions': 'Needs attention', 'section_selection_failed': 'Finding relevant financial sections — Needs attention', 'failed': 'Failed'}
    created = run.get('created_at') or now_iso()
    try: elapsed = int((datetime.now(UTC) - datetime.fromisoformat(created)).total_seconds())
    except Exception: elapsed = 0
    label = labels.get(run.get('status'), 'Working')
    body = f"""<section class='hero'><h1>Financial Intelligence refresh</h1><p>{escape(label)}</p><p>Elapsed time: {elapsed} seconds. Large reports may take several minutes.</p><meta http-equiv='refresh' content='5'></section>{_outcome_summary(run) if run.get('status') not in {'queued','retrieving_source','selecting_sections','estimating_cost','analysing','validating','updating_memory'} else ''}"""
    return _page('Financial Intelligence progress', body)

def create_upload_run(pdf_path: Path, *, enterprise_id: str = 'bt-group-plc', title: str = 'BT Group plc Annual Report 2026', source_url: str = 'uploaded authoritative PDF') -> dict[str, Any]:
    run_id = 'air-' + uuid.uuid4().hex[:12]
    ensure_writable_dir(_upload_dir())
    checksum = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    stored = _upload_dir() / f'{checksum[:16]}.pdf'
    if pdf_path.resolve() != stored.resolve(): shutil.copyfile(pdf_path, stored)
    document = ExperimentDocument(document_id='DOC-' + checksum[:16].upper(), enterprise_id=canonical_enterprise_id(enterprise_id) or enterprise_id, title=title, source_url=source_url, retrieval_timestamp=now_iso(), checksum=checksum, media_type='application/pdf', page_count=1, local_path=str(stored))
    settings = financial_intelligence_settings(); provider = OpenAIDirectPDFProvider(model=settings.model, reasoning_effort=settings.reasoning_effort, max_output_tokens=settings.max_output_tokens, max_run_cost_usd=settings.max_run_cost_usd)
    extraction = provider.extract_facts(document)
    _write_progress(run_id, 'validating')
    claims = [fact_to_review_claim(f, run_id) for f in extraction.facts]
    run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'ready_for_review' if claims else extraction.status, 'document': document.model_dump(), 'provider': extraction.provider, 'model': extraction.model, 'reasoning_effort': provider.reasoning_effort, 'schema_version': settings.schema_version, 'prompt_version': settings.prompt_version, 'document_hash': checksum, 'usage': extraction.usage, 'estimated_cost_usd': extraction.estimated_cost_usd, 'actual_cost_usd': (getattr(extraction, 'verifier', {}) or {}).get('actual_cost_usd'), 'provider_status': extraction.status, 'provider_errors': extraction.provider_errors, 'raw_response_location': extraction.raw_response_location, 'provider_diagnostics': getattr(extraction, 'diagnostics', []), 'claims': claims, 'applied_results': []}
    _write_json(_run_path(run_id), run)
    return run

def load_run(run_id: str) -> dict[str, Any]: return _read_json(_run_path(run_id))

def run_exists(run_id: str) -> bool: return _run_path(run_id).is_file()

def update_reviews(run_id: str, form: dict[str, list[str]]) -> dict[str, Any]:
    run = load_run(run_id)
    for claim in run['claims']:
        cid = claim['claim_id']; action = (form.get(f'action_{cid}', ['pending'])[0] or 'pending')
        claim['review_state'] = action
        amended = form.get(f'amended_{cid}', [claim['amended_statement']])[0]
        claim['amended_statement'] = amended.strip() or claim['original_statement']
    run['status'] = 'reviewed'
    _write_json(_run_path(run_id), run)
    return run

def apply_accepted(run_id: str) -> dict[str, Any]:
    run = load_run(run_id); svc = ObservationMemoryService(); results=[]; rejected=[]
    for claim in run['claims']:
        if claim.get('review_state') not in {'accept', 'amend'}: continue
        report = svc.process_evidence(claim_to_evidence(run, claim))
        results.extend(r.__dict__ for r in report.results)
        rejected.extend(report.rejected_claims)
    run['status'] = 'applied'; run['applied_at'] = now_iso(); run['applied_results'] = results; run['rejected_on_apply'] = rejected
    _write_json(_run_path(run_id), run)
    return run

def review_home_page(message: str = '') -> str:
    sdk_ready = openai_sdk_readiness()
    provider_ready = bool(os.getenv('OPENAI_API_KEY')) and sdk_ready['available']
    if not sdk_ready['available']:
        provider_state = 'Unavailable: OpenAI Python SDK is not installed in this runtime. OPENAI_API_KEY also must be configured before provider execution.'
    else:
        provider_state = 'Available: OpenAI document-understanding credentials are configured.' if provider_ready else 'Unavailable until configured: OPENAI_API_KEY is not set. You can still open this workflow, select an enterprise and prepare the report; processing will show a clear provider configuration error instead of hiding the product capability.'
    notice = f"<p class='pill'>{escape(message)}</p>" if message else ''
    body = f"""<section class='hero'><h1>AI Financial Report Review</h1><p>Upload an authoritative enterprise financial-report PDF. Flora sends the PDF to a genuine AI document-understanding model, returns strict page-grounded claims for review, and only accepted claims update Observation memory and the Commercial Digital Twin.</p>{notice}</section><section class='card'><h2>Provider status</h2><p>{escape(provider_state)}</p><p class='muted'>Provider route: OpenAI direct PDF · Model: {escape(financial_intelligence_settings().model)} · The original PDF is sent to the model as a PDF input file when credentials are present.</p></section><section class='card action'><h2>Collect Financial Report</h2><p>Select an enterprise, add the governed annual report PDF, process it, then accept, amend or reject page-grounded candidate facts before they update Observations and the Commercial Digital Twin.</p><p>Default enterprise: BT Group plc · expected document: BT Group Annual Report 2026.</p><form method='post' action='/ai-financial-report/upload' enctype='multipart/form-data'><label>Enterprise</label><select name='enterprise_id'><option value='bt-group-plc'>BT Group plc</option></select><label>Report title</label><input name='title' value='BT Group plc Annual Report 2026'><label>Source URL or citation</label><input name='source_url' value='https://www.bt.com/about/annual-reports/2026summary/assets/files/BT-Annual-Report-2026.pdf'><label>PDF</label><input type='file' name='pdf' accept='application/pdf'><p><button>Process document</button></p></form></section>"""
    return _page('AI Financial Report Review', body)

def financial_intelligence_admin_health_page() -> str:
    run_dir = _run_dir()
    runs = sorted(run_dir.glob('fi-*.json'), key=lambda p: p.stat().st_mtime, reverse=True) if run_dir.exists() else []
    last = _read_json(runs[0]) if runs else {}
    diag = (last.get('provider_diagnostics') or [{}])[-1]
    mode = storage_mode()
    rows = [
        ('OpenAI SDK import ready', 'yes' if openai_sdk_readiness()['available'] else 'no'),
        ('OpenAI configuration detected', 'yes' if os.getenv('OPENAI_API_KEY') else 'no'),
        ('Configured model', financial_intelligence_settings().model),
        ('Reasoning effort', financial_intelligence_settings().reasoning_effort),
        ('Last Financial Intelligence run time', last.get('created_at', 'none')),
        ('Last support reference', last.get('support_reference', 'none')),
        ('Last failure stage', diag.get('request_stage') or last.get('failure_category') or 'none'),
        ('Last provider status/code', f"{last.get('provider_status') or 'none'} / {diag.get('http_status_code') or diag.get('provider_error_code') or 'none'}"),
        ('Storage mode', mode.get('mode', 'unknown')),
    ]
    html_rows = ''.join(f"<tr><th>{escape(k)}</th><td>{escape(str(v))}</td></tr>" for k, v in rows)
    return _page('Financial Intelligence system health', f"<section class='hero'><h1>Financial Intelligence system health</h1><p>Administrator diagnostics only. Secrets and provider messages are not displayed.</p></section><section class='card'><table>{html_rows}</table></section>")

def financial_intelligence_page(message: str = '') -> str:
    source = _bt_annual_report_source()
    run_dir = _run_dir()
    runs = sorted(run_dir.glob('fi-*.json'), key=lambda p: p.stat().st_mtime, reverse=True) if run_dir.exists() else []
    last = _read_json(runs[0]) if runs else None
    ready = bool(os.getenv('OPENAI_API_KEY'))
    state = 'Financial intelligence ready' if ready else 'Financial intelligence is temporarily unavailable'
    notice = f"<p class='pill'>{escape(message)}</p>" if message else ''
    summary = _outcome_summary(last) if last else '<p>No Financial Intelligence refresh has run yet.</p>'
    mode = storage_mode()
    print(f"Flora Financial Intelligence storage mode: {mode['mode']} at {mode['data_root']}")
    body = f"""<section class='hero'><h1>Financial Intelligence</h1><p>BT Commercial Digital Twin outcome view. Flora collects the governed annual report, understands the financial facts, updates Observations and the Enterprise Model, then shows what changed and what needs attention.</p>{notice}<p class='pill'>{escape(state)}</p></section><section class='card action'><h2>Active governed source</h2><p><strong>{escape(source['source_name'])}</strong></p><p><a href='{escape(source['url'])}'>{escape(source['url'])}</a></p><p class='muted'>Source is registered in the BT collection profile and collected server-side; no download or upload is required.</p><form method='post' action='/financial-intelligence/bt-group-plc/refresh'><button>Refresh Financial Intelligence</button></form><form method='post' action='/financial-intelligence/bt-group-plc/refresh?reprocess=1'><button>Administrative Reprocess</button></form></section>{summary}<details class='card'><summary><strong>Administrative fallback only</strong></summary><p>Use only when governed automatic collection cannot retrieve a replacement report. This is not the BT sales-user workflow.</p><form method='post' action='/ai-financial-report/upload' enctype='multipart/form-data'><input type='hidden' name='enterprise_id' value='bt-group-plc'><input type='hidden' name='title' value='BT Group plc Annual Report 2026'><input type='hidden' name='source_url' value='{escape(source['url'])}'><input type='file' name='pdf' accept='application/pdf'><button>Admin fallback upload</button></form></details>"""
    return _page('Financial Intelligence', body)

def _outcome_summary(run: dict[str, Any] | None) -> str:
    if not run: return ''
    changes = ''.join(f"<li>{escape(str(r.get('affected_attribute')))} — {escape(str(r.get('update_result')))}</li>" for r in run.get('applied_results', [])[:20]) or '<li>No financial intelligence was added because processing did not complete.</li>'
    exceptions = _dedupe_exceptions(run.get('exceptions', []))
    support = run.get('support_reference') or _support_reference(run)
    needs = ''.join(f"<li>{escape(str(e.get('user_message') or e.get('acceptance_reason') or e.get('rejection_reason') or 'Needs attention'))} Support reference: {escape(str(e.get('support_reference') or support))} — section {escape(str(e.get('packet_id') or 'n/a'))}</li>" for e in exceptions[:20]) or '<li>No exceptions requiring review.</li>'
    evidence = ''.join(f"<details><summary>{escape(c.get('original_statement',''))}</summary><p>Page {escape(str(c.get('page_reference')))} · Confidence {escape(str(c.get('confidence')))} · Evidence {escape(c.get('evidence_id',''))}</p><p>{escape(str(c.get('source_excerpt') or ''))}</p></details>" for c in run.get('claims', [])[:20]) or '<p>No page-grounded claims returned.</p>'
    status = run.get('status','')
    headline = 'Complete' if status == 'completed' else ('Needs attention' if status == 'completed_with_exceptions' else ('In progress' if status in {'queued','retrieving_source','selecting_sections','estimating_cost','analysing','validating','updating_memory'} else 'Failed'))
    cost_value = run.get('actual_cost_usd') if run.get('actual_cost_usd') is not None else run.get('estimated_cost_usd')
    cost_text = f" · Run cost: {escape(str(cost_value))} USD" if cost_value is not None else ''
    outcome = 'maintained Enterprise Model financial attributes changed or strengthened; use this as a prompt for account planning, not as a standalone commercial conclusion.' if run.get('enterprise_attributes_changed') else 'No financial intelligence was added because processing did not complete.'
    return f"""<section class='card'><h2>Refresh outcome</h2><p>{headline}{cost_text} · Facts added: {len(run.get('claims', []))} · Reporting period: inferred from accepted facts · Collection status: {escape(status)} · Collected: {escape(run.get('collection',{}).get('retrieval_time',''))}</p><div class='grid'><div><div class='metric'>{run.get('auto_accepted_count',0)}</div><p>Automatically accepted facts</p></div><div><div class='metric'>{run.get('observations_created_or_strengthened',0)}</div><p>New or strengthened Observations</p></div><div><div class='metric'>{len([r for r in run.get('applied_results',[]) if r.get('contradiction')])}</div><p>Contradictions</p></div><div><div class='metric'>{len(exceptions)}</div><p>Needs Attention</p></div></div><p><a href='/financial-intelligence/{escape(run['run_id'])}'>View financial changes</a> · <a href='/financial-intelligence/{escape(run['run_id'])}#evidence'>View supporting evidence</a> · <a href='/financial-intelligence/{escape(run['run_id'])}#attention'>Review exceptions</a></p></section><section class='card'><h2>What changed</h2><ul>{changes}</ul></section><section class='card'><h2>Why it matters</h2><p><strong>Outcome:</strong> {outcome}</p><form method='post' action='/financial-intelligence/bt-group-plc/refresh'><button>Retry</button></form></section><section id='attention' class='card'><h2>What needs attention</h2><ul>{needs}</ul></section><section id='evidence' class='card'><h2>Evidence</h2>{evidence}</section>{enterprise_memory_panel('bt-group-plc')}"""

def missing_run_page(run_id: str) -> str:
    body = f"""<section class='hero'><h1>Financial Intelligence</h1><p>This previous refresh result is no longer available.</p><p>Start a new refresh to collect the latest financial intelligence.</p><form method='post' action='/financial-intelligence/bt-group-plc/refresh'><button>Start new refresh</button></form><p><a href='/financial-intelligence'>Return to Financial Intelligence</a></p></section>"""
    return _page('Financial Intelligence result unavailable', body)

def financial_intelligence_run_page(run_id: str) -> str:
    try:
        return _page('Financial Intelligence outcome', _outcome_summary(load_run(run_id)))
    except FileNotFoundError:
        print(f"Flora Financial Intelligence requested missing run {run_id}; storage mode={storage_mode()['mode']}")
        return missing_run_page(run_id)

def financial_intelligence_run_response(run_id: str) -> tuple[str, int]:
    try:
        return _page('Financial Intelligence outcome', _outcome_summary(load_run(run_id))), 200
    except FileNotFoundError:
        print(f"Flora Financial Intelligence requested missing run {run_id}; storage mode={storage_mode()['mode']}")
        return missing_run_page(run_id), 410

def run_page(run_id: str) -> str:
    run = load_run(run_id)
    rows = ''.join(_claim_row(c) for c in run.get('claims', [])) or '<tr><td colspan="7">No claims returned. Check provider status and errors below.</td></tr>'
    applied = ''.join(f"<li>{escape(r.get('observation_id',''))} → {escape(r.get('affected_attribute',''))} ({escape(r.get('update_result',''))})</li>" for r in run.get('applied_results', []))
    body = f"""<section class='hero'><h1>Review extracted factual claims</h1><p>Run {escape(run_id)} · Provider {escape(run.get('provider',''))} · Model {escape(run.get('model',''))} · Status {escape(run.get('provider_status',''))}</p><p class='muted'>{escape('; '.join(run.get('provider_errors') or []))}</p></section><form method='post' action='/ai-financial-report/{escape(run_id)}/review'><section class='card'><table><thead><tr><th>Decision</th><th>Claim</th><th>Amendment</th><th>Type</th><th>Page</th><th>Excerpt</th><th>Confidence</th></tr></thead><tbody>{rows}</tbody></table><p><button>Save review decisions</button></p></section></form><section class='card action'><form method='post' action='/ai-financial-report/{escape(run_id)}/apply'><button>Apply accepted claims to Commercial Digital Twin</button></form><ul>{applied or '<li>No Observations applied yet.</li>'}</ul><p><a href='/digital-twin/bt-group-plc'>Open Commercial Digital Twin</a></p></section>{enterprise_memory_panel(run['document']['enterprise_id'])}"""
    return _page('Review AI claims', body)

def _claim_row(c: dict[str, Any]) -> str:
    cid = escape(c['claim_id']); state = c.get('review_state','pending')
    opts = ''.join(f"<option value='{v}' {'selected' if state==v else ''}>{label}</option>" for v,label in [('pending','Pending'),('accept','Accept'),('amend','Amend'),('reject','Reject')])
    return f"<tr><td><select name='action_{cid}'>{opts}</select></td><td>{escape(c['original_statement'])}</td><td><textarea name='amended_{cid}'>{escape(c.get('amended_statement',''))}</textarea></td><td>{escape(c['claim_type'])}</td><td>{escape(str(c.get('page_reference')))}</td><td>{escape(str(c.get('source_excerpt'))[:220])}</td><td>{c.get('confidence')}</td></tr>"
