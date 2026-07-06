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
from cios.applications.flora.financial_intelligence.normalisation import canonicalise_financial_claim, rounding_compatible
from cios.applications.flora.financial_intelligence.adapters import PdfFinancialTableAdapter, FinancialFactCandidate, ADAPTER_VERSION, StructuredFinancialAdapterResult
from cios.applications.flora.financial_intelligence.provider_guard import provider_call_guard
from cios.applications.flora.financial_intelligence.config import financial_intelligence_settings
from cios.applications.flora.financial_intelligence.schema import ExperimentDocument, FoundationFact
from cios.applications.flora.financial_intelligence.rapid import run_rapid_financial_intelligence
from cios.applications.flora.financial_intelligence.rapid_sources import RapidSourceAcquisitionError, acquire_rapid_financial_source
from cios.applications.flora.financial_intelligence.rapid_candidates import extract_rapid_financial_candidates
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.memory.views import enterprise_memory_panel
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.live.documents import fetch_document, parse_pdf_document
from cios.applications.flora.workspace.views import _page
from cios.applications.flora.access import valid_financial_intelligence_run_id

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
    'candidate_validation_failed': 'Financial sections were analysed, but extracted facts could not be validated.',
    'section_selection_failed': 'Flora could not identify the financial sections in this report.',
    'persistence_failed': 'Flora understood the report but could not save the results.',
    'deterministic_route_provider_violation': 'Deterministic financial refresh was blocked before any provider request was transmitted.',
    'structured_source_unavailable': 'Structured financial source unavailable',
    'structured_source_identity_failed': 'Structured financial source unavailable',
    'structured_source_retrieval_failed': 'Structured financial source unavailable',
    'structured_package_invalid': 'Structured financial source unavailable',
    'structured_filing_parse_failed': 'Structured financial source unavailable',
    'structured_entity_mismatch': 'Structured financial source unavailable',
    'structured_scope_ambiguous': 'Structured financial source unavailable',
    'structured_facts_unmapped': 'Structured financial source unavailable',
    'canonical_validation_failed': 'Structured financial source unavailable',
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
        'candidate_validation_failed': 'candidate_validation_failed',
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
    if category in {'source_retrieval_failed'}:
        base_message = 'Flora could not reach the approved BT financial source.'
    elif category in {'source_not_pdf', 'section_selection_failed'}:
        base_message = 'Flora reached the approved BT financial report but could not read it safely.'
    elif category in {'structured_source_identity_failed', 'structured_entity_mismatch', 'structured_scope_ambiguous'}:
        base_message = 'Flora reached a document but could not confirm it as the approved BT FY26 financial report.'
    elif category in {'candidate_validation_failed', 'provider_response_invalid', 'failed'}:
        base_message = 'Flora read the approved BT report but could not identify safe financial findings.'
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
    message = _redact_filesystem_paths(message)
    return message[:700]

_FILE_URL_RE = re.compile(r'file:///[^\s<>"\']+', re.I)
_WIN_PATH_RE = re.compile(r'(?<![A-Za-z0-9])(?:[A-Za-z]:\\|\\\\)[^\s<>"\']+')
_UNIX_PATH_RE = re.compile(r'(?<![A-Za-z0-9])/(?:tmp|var|home|workspace|Users|private/tmp|opt/render|mnt|data)(?:/[^\s<>"\']*)?', re.I)

def _redact_filesystem_paths(value: str) -> str:
    text = str(value or '')
    text = _FILE_URL_RE.sub('REDACTED_PATH', text)
    text = _WIN_PATH_RE.sub('REDACTED_PATH', text)
    text = _UNIX_PATH_RE.sub('REDACTED_PATH', text)
    return text

def _sanitize_diagnostic_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(_sanitize_diagnostic_payload(k)): _sanitize_diagnostic_payload(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_diagnostic_payload(v) for v in value]
    if isinstance(value, str):
        return _safe_message(value)
    return value

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


DEPLOYED_REVISION_ENV_VARS = (
    'RENDER_GIT_COMMIT', 'RENDER_COMMIT', 'RENDER_EXTERNAL_HOSTNAME_COMMIT',
    'GIT_COMMIT', 'SOURCE_VERSION', 'COMMIT_SHA', 'HEROKU_SLUG_COMMIT',
)

def deployed_revision() -> str:
    for key in DEPLOYED_REVISION_ENV_VARS:
        value = (os.getenv(key) or '').strip()
        if value:
            return value
    return 'unknown'

def _sanitize_url(value: Any) -> str:
    raw = str(value or '')
    if not raw:
        return 'unknown'
    if raw.lower().startswith('file:'):
        return 'REDACTED_PATH'
    try:
        from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
        parts = urlsplit(raw)
        netloc = parts.hostname or ''
        if parts.port:
            netloc += f':{parts.port}'
        sensitive = {'token','key','api_key','apikey','access_token','auth','authorization','signature','sig','password','secret','cookie'}
        query = urlencode([(k, 'REDACTED' if k.lower() in sensitive or any(x in k.lower() for x in ('token','key','secret','auth','password','cookie','sig')) else v) for k, v in parse_qsl(parts.query, keep_blank_values=True)])
        return _redact_filesystem_paths(urlunsplit((parts.scheme, netloc, parts.path, query, '')))
    except Exception:
        return _safe_message(raw)

def _not_reached(value: Any, default: str = 'not_reached') -> Any:
    return default if value in (None, '', [], (), {}) else value

def _diagnostic_user_message(stage: str) -> str:
    if stage == 'retrieval':
        return 'Flora could not reach the approved BT financial source.'
    if stage == 'parsing':
        return 'Flora reached the approved BT financial report but could not read it safely.'
    if stage == 'validation':
        return 'Flora reached a document but could not confirm it as the approved BT FY26 financial report.'
    if stage == 'extraction':
        return 'Flora read the approved BT report but could not identify safe financial findings.'
    return 'Financial Intelligence could not complete.'

def _run_diagnostic(run: dict[str, Any]) -> dict[str, Any]:
    coll = run.get('collection') or {}
    doc = run.get('document') or {}
    rapid = run.get('rapid_intelligence') or {}
    receipt = rapid.get('source_receipt') or {}
    diag = (run.get('diagnostics') or {}).get('rapid_support_diagnostics') or rapid.get('support_diagnostics') or run.get('support_diagnostics') or {}
    nav = run.get('pdf_navigation_diagnostics') or {}
    exceptions = run.get('exceptions') or run.get('candidate_exceptions') or []
    first_exc = exceptions[0] if exceptions else {}
    failure_stage = first_exc.get('failure_stage') or receipt.get('failure_stage') or run.get('failure_stage')
    status = str(run.get('status') or run.get('overall_status') or '')
    if not failure_stage:
        if status in {'source_retrieval_failed'} or receipt.get('failure_stage') == 'retrieval': failure_stage = 'retrieval'
        elif status in {'source_not_pdf','section_selection_failed'} or receipt.get('failure_code') == 'rapid_source_parse_failed': failure_stage = 'parsing'
        elif 'identity' in status or 'period' in status or receipt.get('identity_result') == 'mismatch' or receipt.get('period_result') == 'mismatch': failure_stage = 'validation'
        elif status in {'failed','completed_with_no_accepted_intelligence'} or rapid.get('extraction_status') == 'failed_extraction': failure_stage = 'extraction'
        elif status.startswith('completed'): failure_stage = 'none'
        else: failure_stage = 'unknown'
    candidate_count = rapid.get('candidate_count', rapid.get('candidate_fact_count', len(run.get('claims') or [])))
    canonical_write_count = (run.get('cost_summary') or {}).get('canonical_write_count', run.get('observations_created_or_strengthened', len(run.get('applied_results') or [])))
    requested = receipt.get('requested_url') or coll.get('active_source_url') or (run.get('governed_source') or {}).get('url') or doc.get('source_url')
    final_url = receipt.get('final_url') or coll.get('final_url') or doc.get('source_url')
    out = {
        'run_id': run.get('run_id','unknown'), 'support_reference': run.get('support_reference') or _support_reference(run), 'timestamp': run.get('completed_at') or run.get('updated_at') or run.get('created_at') or now_iso(),
        'deployed_revision': run.get('deployed_revision') or 'unknown', 'execution_mode': run.get('execution_mode') or run.get('extraction_mode') or 'unknown', 'source_configuration_key': receipt.get('configuration_key') or rapid.get('source_configuration_key') or (run.get('governed_source') or {}).get('source_id') or 'unknown',
        'request_attempted': bool(receipt.get('request_attempted', coll.get('retrieved') is not None or coll.get('http_status') is not None or coll.get('error') is not None or coll.get('active_source_url') is not None)), 'requested_url': _sanitize_url(requested), 'final_host': receipt.get('artifact_host') or ('unknown' if not final_url else __import__('urllib.parse').parse.urlsplit(str(final_url)).hostname or 'unknown'),
        'http_status': _not_reached(receipt.get('http_status', coll.get('http_status')), 'unknown' if bool(receipt.get('request_attempted', coll)) else 'not_reached'), 'content_type': _not_reached(receipt.get('content_type', coll.get('content_type')), 'not_reached'), 'bytes_downloaded': int(receipt.get('bytes_downloaded', coll.get('document_size') or 0) or 0), 'redirect_count': len(receipt.get('redirect_chain') or coll.get('redirect_chain') or []),
        'pdf_magic_result': receipt.get('pdf_magic_valid', 'not_reached' if not coll.get('retrieved') else bool(str(doc.get('media_type')).lower() == 'application/pdf')), 'parser_name': diag.get('parser_name') or receipt.get('parser_name') or nav.get('selected_parser') or doc.get('extraction_method') or 'not_reached', 'parser_version': diag.get('parser_version') or receipt.get('parser_version') or doc.get('extraction_version') or 'not_reached', 'page_count': receipt.get('page_count') or doc.get('page_count') or 'not_reached', 'pages_successfully_read': receipt.get('pages_successfully_read') or diag.get('pages_successfully_read') or ('not_reached' if not doc.get('page_count') else list(range(1, int(doc.get('page_count') or 0)+1))),
        'identity_result': receipt.get('identity_result') or 'not_reached', 'reporting_period_result': receipt.get('period_result') or 'not_reached', 'extraction_status': rapid.get('extraction_status') or ('completed' if run.get('claims') else ('not_reached' if failure_stage in {'retrieval','parsing','validation','unknown'} or status in {'queued','running','retrieving_source','reading_document','checking_document_quality','selecting_sections','preparing_packets','estimating_cost','analysing','validating','updating_memory'} else 'failed')), 'candidate_count': int(candidate_count or 0),
        'failure_stage': failure_stage, 'failure_code': first_exc.get('exception_type') or receipt.get('failure_code') or run.get('failure_category') or ('none' if status.startswith('completed') else 'unknown'), 'safe_failure_message': _safe_message(first_exc.get('user_message') or receipt.get('safe_failure_message') or _diagnostic_user_message(failure_stage)),
        'ai_call_count': int(run.get('ai_calls_made', run.get('openai_calls_made', (run.get('cost_summary') or {}).get('ai_call_count', 0))) or 0), 'canonical_write_count': int(canonical_write_count or 0), 'trusted_twin_changed': bool(run.get('trusted_twin_changed') or (run.get('canonical_update') or {}).get('enterprise_model_updated')),
    }
    return _sanitize_diagnostic_payload(out)

def attach_financial_run_diagnostic(run: dict[str, Any]) -> dict[str, Any]:
    run.setdefault('deployed_revision', deployed_revision())
    run.setdefault('support_reference', _support_reference(run))
    run['support_diagnostic'] = _run_diagnostic(run)
    return run

def financial_intelligence_support_diagnostic_payload(run_id: str) -> dict[str, Any]:
    run = load_run(run_id)
    return _sanitize_diagnostic_payload(run.get('support_diagnostic') or _run_diagnostic(run))



def financial_intelligence_safe_support_report_payload(run_id: str) -> dict[str, Any]:
    """Return the persisted user-safe support report without rebuilding diagnostics.

    This download path is intentionally read-only: it loads the saved run record
    and returns only the sanitised diagnostic that was persisted with that run.
    Older runs created before support diagnostics existed receive a friendly
    unavailable payload rather than a reconstructed diagnostic.
    """
    run = load_run(run_id)
    support_reference = run.get('support_reference') or _support_reference(run)
    persisted = run.get('support_diagnostic')
    if not persisted:
        return _sanitize_diagnostic_payload({
            'run_id': run.get('run_id', run_id),
            'support_reference': support_reference,
            'report_available': False,
            'message': 'A support report is not available for this earlier run.',
        })
    payload = _sanitize_diagnostic_payload(persisted)
    if isinstance(payload, dict):
        payload.setdefault('run_id', run.get('run_id', run_id))
        payload.setdefault('support_reference', support_reference)
        payload.setdefault('report_available', True)
    return payload

def financial_intelligence_support_report_link(run_id: str) -> str:
    return (
        f"<p class='muted'>Provides a safe technical summary that can be shared with support.</p>"
        f"<p><a class='support-report-link' href='/financial-intelligence/{escape(str(run_id))}/support-report'>Download support report</a></p>"
    )

def financial_intelligence_support_diagnostic_page(run_id: str) -> str:
    payload = financial_intelligence_support_diagnostic_payload(run_id)
    rows = ''.join(f"<tr><th>{escape(str(k))}</th><td>{escape(json.dumps(v) if isinstance(v,(dict,list,tuple)) else str(v))}</td></tr>" for k,v in payload.items())
    body = f"""<section class='hero'><h1>Financial Intelligence support diagnostic</h1><p>Run {escape(run_id)} · Support reference {escape(str(payload.get('support_reference')))}</p><p><a href='/financial-intelligence/{escape(run_id)}/support-diagnostic/download'>Download diagnostic report</a></p></section><section class='card'><table>{rows}</table></section>"""
    return _page('Financial Intelligence support diagnostic', body)

DUAL_SPEED_FINANCIAL_INTELLIGENCE_MODE = 'dual_speed_financial_intelligence'

STRUCTURED_FINANCIAL_STATUSES = {
    'structured_source_unavailable',
    'structured_source_identity_failed',
    'structured_source_retrieval_failed',
    'structured_package_invalid',
    'structured_filing_parse_failed',
    'structured_entity_mismatch',
    'structured_scope_ambiguous',
    'structured_facts_unmapped',
    'canonical_validation_failed',
    'completed',
    'completed_with_exceptions',
    'completed_with_no_new_evidence',
}


class OfficialStructuredFinancialAdapter:
    """Governed structured filing adapter boundary for the hosted standard route.

    Live registry credentials/source discovery are intentionally not implemented
    here. In their absence the adapter returns no candidates and a structured
    source-unavailable exception so the caller can fail closed without falling
    back to PDF or AI workflows.
    """

    adapter_name = 'StructuredFinancialAdapter'
    adapter_version = 'structured-source-first-v1'
    source_family = 'governed_structured_filing'

    def discover_source(self, enterprise_id: str, reporting_period: str | None = None) -> dict[str, Any] | None:
        return None

    def extract(self, document: ExperimentDocument, **kwargs: Any) -> StructuredFinancialAdapterResult:
        source = self.discover_source(document.enterprise_id, kwargs.get('reporting_period'))
        if not source:
            return StructuredFinancialAdapterResult(
                self.adapter_name,
                self.adapter_version,
                document.checksum,
                (),
                ({'exception_type': 'structured_source_unavailable', 'failure_stage': 'structured_source_discovery', 'user_message': 'Structured financial source unavailable', 'rejection_reason': 'No governed structured filing source is configured or discoverable for this enterprise and reporting period.'},),
                ai_calls_made=0,
            )
        return StructuredFinancialAdapterResult(self.adapter_name, self.adapter_version, document.checksum, (), (), ai_calls_made=0)


def _trusted_state_snapshot(enterprise_id: str) -> dict[str, Any]:
    svc = ObservationMemoryService()
    canonical_id = canonical_enterprise_id(enterprise_id) or enterprise_id
    model = svc.models.get(canonical_id)
    active_observations = [o for o in svc.observations.list() if not getattr(o, 'retired_at', None) and getattr(o, 'lifecycle_state', 'active') not in {'retired', 'superseded'}]
    return {
        'canonical_enterprise_id': canonical_id,
        'observation_repository': type(svc.observations).__name__,
        'enterprise_model_repository': type(svc.models).__name__,
        'storage_mode': storage_mode().get('mode'),
        'active_observation_count': len(active_observations),
        'active_enterprise_model_attribute_count': len(model.attributes),
        'state_existed_before_run': bool(active_observations or model.attributes),
    }


def _structured_diagnostic(event: str, *, run_id: str, enterprise_id: str, acquisition_mode: str, adapter: Any, started: float, final_status: str = 'validating', candidate_count: int = 0, ai_call_count: int = 0, pdf_fallback_count: int = 0) -> dict[str, Any]:
    return {
        'event': event,
        'support_reference': 'FI-' + run_id.removeprefix('fi-'),
        'enterprise_id': enterprise_id,
        'acquisition_mode': acquisition_mode,
        'adapter_class': adapter.__class__.__name__,
        'adapter_name': getattr(adapter, 'adapter_name', adapter.__class__.__name__),
        'source_family': getattr(adapter, 'source_family', 'governed_structured_filing'),
        'candidate_count': candidate_count,
        'ai_call_count': ai_call_count,
        'pdf_fallback_count': pdf_fallback_count,
        'final_status': final_status,
        'elapsed_time': round(time.time() - started, 3),
        'pdf_section_selector_calls': 0,
        'pdf_candidate_extractor_calls': 0,
        'pdf_packet_calls': 0,
        'provider_calls': 0,
    }


def _refresh_structured_financial_intelligence(enterprise_id: str, run_id: str) -> dict[str, Any]:
    from cios.applications.flora.financial_intelligence.bt_structured import ingest_bt_fy26
    if enterprise_id == 'bt-group-plc' and OfficialStructuredFinancialAdapter.__name__ == 'OfficialStructuredFinancialAdapter':
        return ingest_bt_fy26(run_id)
    started = time.time()
    adapter = OfficialStructuredFinancialAdapter()
    document = ExperimentDocument(document_id=f'{enterprise_id}-structured-source', enterprise_id=enterprise_id, title='Governed structured financial filing', source_url='governed-structured-source', retrieval_timestamp=now_iso(), checksum='structured-source-unavailable', media_type='application/xbrl+xml', page_count=1, local_path=None)
    before = _trusted_state_snapshot(enterprise_id)
    diagnostics = [
        _structured_diagnostic('structured_refresh_started', run_id=run_id, enterprise_id=enterprise_id, acquisition_mode='structured_standard_financials', adapter=adapter, started=started),
        _structured_diagnostic('structured_adapter_selected', run_id=run_id, enterprise_id=enterprise_id, acquisition_mode='structured_standard_financials', adapter=adapter, started=started),
        _structured_diagnostic('structured_source_discovery_started', run_id=run_id, enterprise_id=enterprise_id, acquisition_mode='structured_standard_financials', adapter=adapter, started=started),
    ]
    result = adapter.extract(document)
    status = 'structured_source_unavailable' if not result.candidates else 'completed'
    diagnostics.append(_structured_diagnostic('structured_source_discovery_completed', run_id=run_id, enterprise_id=enterprise_id, acquisition_mode='structured_standard_financials', adapter=adapter, started=started, final_status=status, candidate_count=len(result.candidates), ai_call_count=result.ai_calls_made))
    if status == 'structured_source_unavailable':
        diagnostics.append(_structured_diagnostic('structured_source_unavailable', run_id=run_id, enterprise_id=enterprise_id, acquisition_mode='structured_standard_financials', adapter=adapter, started=started, final_status=status))
    after = _trusted_state_snapshot(enterprise_id)
    diagnostics.append(_structured_diagnostic('structured_refresh_completed', run_id=run_id, enterprise_id=enterprise_id, acquisition_mode='structured_standard_financials', adapter=adapter, started=started, final_status=status, candidate_count=len(result.candidates), ai_call_count=result.ai_calls_made))
    run = {'run_id': run_id, 'created_at': now_iso(), 'status': status, 'workflow': 'financial_intelligence', 'enterprise_id': enterprise_id, 'extraction_mode': 'structured_standard_financials', 'extraction_mode_label': 'Structured standard financials', 'adapter_class': adapter.__class__.__name__, 'adapter_name': adapter.adapter_name, 'source_family': adapter.source_family, 'collection': {'retrieved': False, 'retrieval_time': now_iso(), 'error': 'structured_source_unavailable'}, 'document': document.model_dump(), 'provider': 'not_executed', 'model': adapter.adapter_name, 'reasoning_effort': None, 'usage': {'openai_calls': 0}, 'estimated_cost_usd': 0, 'actual_cost_usd': 0, 'provider_status': 'not_executed', 'provider_errors': [], 'provider_diagnostics': diagnostics, 'structured_diagnostics': diagnostics, 'openai_invoked': False, 'openai_calls_made': 0, 'ai_calls_made': 0, 'pdf_fallback_calls_made': 0, 'prohibited_path_counters': {'pdf_section_selector_calls': 0, 'pdf_candidate_extractor_calls': 0, 'pdf_packet_calls': 0, 'provider_calls': 0}, 'claims': [], 'applied_results': [], 'candidate_exceptions': list(result.exceptions), 'exceptions': list(result.exceptions), 'candidate_pages_selected': [], 'page_packets_submitted': [], 'packet_count': 0, 'pdf_navigation_diagnostics': {}, 'visual_navigation': {}, 'visual_navigation_fallback_used': False, 'auto_accepted_count': 0, 'observations_created_or_strengthened': 0, 'enterprise_attributes_changed': [], 'candidate_lifecycle_counts': {'packet_candidates_extracted': 0, 'candidates_returned': 0, 'valid_candidates': 0, 'quarantined_candidates': 0, 'canonical_facts_accepted': 0, 'observations_created_or_strengthened': 0}, 'trusted_state_before': before, 'trusted_state_after': after, 'trusted_twin_changed': before['active_observation_count'] != after['active_observation_count'] or before['active_enterprise_model_attribute_count'] != after['active_enterprise_model_attribute_count'], 'ephemeral_state_absent_before_run': not before['state_existed_before_run'], 'no_new_evidence_message': 'Flora could not find or access a governed structured filing for this enterprise and reporting period. The existing trusted Financial Twin was not changed.', 'support_reference': 'FI-' + run_id.removeprefix('fi-'), 'terminal': True, 'progress_percent': 100, 'percent_complete': 100}
    for exc in run['exceptions']:
        exc.setdefault('support_reference', run['support_reference'])
    attach_financial_run_diagnostic(run)
    _write_json(_run_path(run_id), run)
    _write_cost_record(run)
    return run

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
    try:
        if path.parent == _run_dir() and isinstance(data, dict) and (str(data.get('run_id', '')).startswith('fi-') or data.get('workflow') == 'financial_intelligence'):
            attach_financial_run_diagnostic(data)
    except Exception:
        LOGGER.exception('Could not attach Financial Intelligence diagnostic before persistence path=%s', path)
    atomic_write_json(path, data)

def _run_path(run_id: str) -> Path:
    if not valid_financial_intelligence_run_id(run_id):
        raise FileNotFoundError(str(run_id))
    return _run_dir() / f'{run_id}.json'

TERMINAL_RUN_STATES = {'completed','completed_with_exceptions','completed_with_no_accepted_intelligence','completed_with_no_new_evidence','structured_source_unavailable','structured_source_identity_failed','structured_source_retrieval_failed','structured_package_invalid','structured_filing_parse_failed','structured_entity_mismatch','structured_scope_ambiguous','structured_facts_unmapped','canonical_validation_failed','failed','candidate_validation_failed','provider_request_failed','provider_response_invalid','provider_response_incomplete','output_token_limit_reached','section_selection_failed','persistence_failed'}
PROGRESS_ORDER = {'queued':0,'retrieving_source':8,'reading_document':18,'checking_document_quality':18,'selecting_sections':30,'preparing_packets':42,'estimating_cost':52,'analysing':68,'validating':82,'updating_memory':92,'completed':100,'completed_with_exceptions':100,'completed_with_no_accepted_intelligence':100,'failed':100,'candidate_validation_failed':100,'provider_request_failed':100,'provider_response_incomplete':100,'output_token_limit_reached':100,'source_retrieval_failed':100,'source_not_pdf':100,'section_selection_failed':100,'structured_source_unavailable':100,'structured_source_identity_failed':100,'structured_source_retrieval_failed':100,'structured_package_invalid':100,'structured_filing_parse_failed':100,'structured_entity_mismatch':100,'structured_scope_ambiguous':100,'structured_facts_unmapped':100,'canonical_validation_failed':100,'completed_with_no_new_evidence':100,'persistence_failed':100}
ACTIVE_RUN_STATES = {'queued','running','retrieving_source','reading_document','checking_document_quality','selecting_sections','preparing_packets','estimating_cost','analysing','validating','updating_memory'}

def _normalise_terminal_status(status: str) -> str:
    return 'failed' if status in {'candidate_validation_failed','provider_request_failed','source_retrieval_failed','source_not_pdf','section_selection_failed','persistence_failed'} else status

def _write_progress(run_id: str, status: str, **extra: Any) -> None:
    try:
        path = _run_path(run_id)
        run = _read_json(path) if path.is_file() else {'run_id': run_id, 'created_at': now_iso(), 'claims': [], 'applied_results': [], 'exceptions': []}
        if run.get('status') in TERMINAL_RUN_STATES:
            return
        previous = int(run.get('progress_percent') or run.get('percent_complete') or 0)
        pct = max(previous, PROGRESS_ORDER.get(status, previous))
        state = _normalise_terminal_status(status)
        run.update({'status': state, 'state': state, 'current_stage': status, 'progress_percent': pct, 'percent_complete': pct, **extra})
        if state in TERMINAL_RUN_STATES:
            run['progress_percent'] = run['percent_complete'] = 100; run['terminal'] = True; run['completed_at'] = run.get('completed_at') or now_iso()
        else:
            run['terminal'] = False
        events = run.setdefault('progress_events', [])
        events.append({'status': state, 'stage': status, 'progress_percent': run['progress_percent'], 'at': now_iso()})
        _write_json(path, run)
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
        'metric_identity': (fact.predicate or fact.object_type or 'metric').casefold().replace(' ', '_'),
        'value': fact.value_number if fact.value_number is not None else fact.value_text,
        'reported_amount': fact.value_number if fact.value_number is not None else None,
        'original_display_value': None,
        'reported_scale': fact.scale,
        'unit': fact.unit,
        'currency': fact.currency,
        'accounting_basis': 'statutory' if str(fact.predicate).casefold().startswith('reported revenue') else None,
        'business_unit': fact.business_unit or fact.subject_name,
        'period': fact.period_label,
        'state': _financial_state_from_fact(fact),
        'period_start': fact.period_start,
        'period_end': fact.period_end,
        'confidence': int(round(fact.extraction_confidence * 100)),
        'page_reference': str(fact.source_page_start) if fact.source_page_start == fact.source_page_end else f'{fact.source_page_start}-{fact.source_page_end}',
        'source_excerpt': fact.source_excerpt,
        'supporting_context': fact.source_excerpt,
        'extractor_provider': fact.extractor_provider,
        'extractor_model': fact.extractor_model,
        'evidence_id': _evidence_id(run_id, fact.fact_id),
    }


def deterministic_candidate_to_review_claim(candidate: FinancialFactCandidate, run_id: str) -> dict[str, Any]:
    evidence_id = 'PDF-EV-' + hashlib.sha256(f'{candidate.source_hash}:{candidate.evidence_bundle_id or candidate.candidate_id}:{candidate.raw_value_text}'.encode()).hexdigest()[:16].upper()
    return {
        'claim_id': candidate.candidate_id,
        'review_state': 'pending',
        'original_statement': candidate.supporting_excerpt,
        'amended_statement': candidate.supporting_excerpt,
        'claim_type': 'financial_metric_reported',
        'canonical_enterprise_id': candidate.enterprise_id,
        'affected_attribute': '',
        'metric_identity': candidate.raw_metric_label,
        'value': str(candidate.reported_amount) if candidate.reported_amount is not None else None,
        'reported_amount': str(candidate.reported_amount) if candidate.reported_amount is not None else None,
        'raw_value_text': candidate.raw_value_text,
        'original_display_value': candidate.raw_value_text or None,
        'reported_scale': candidate.reported_scale,
        'currency': candidate.currency,
        'accounting_basis': candidate.accounting_basis_text,
        'business_unit': candidate.scope_text or 'group',
        'enterprise_scope': candidate.scope_text or 'group',
        'period': candidate.raw_period_text,
        'raw_period_text': candidate.raw_period_text,
        'state': candidate.measurement_state_text or 'actual',
        'confidence': candidate.extraction_confidence,
        'page_reference': str(candidate.source_page or ''),
        'source_page': candidate.source_page,
        'source_excerpt': candidate.supporting_excerpt,
        'supporting_context': candidate.supporting_excerpt,
        'extractor_provider': 'deterministic',
        'extractor_model': candidate.source_method,
        'extractor_version': candidate.extraction_version,
        'evidence_id': evidence_id,
        'candidate_exception': None if candidate.exception == 'four_digit_year_as_monetary_value' and candidate.reported_scale else candidate.exception,
        'evidence_bundle_id': candidate.evidence_bundle_id,
        'financial_table_evidence_bundle': candidate.evidence_bundle.to_dict() if candidate.evidence_bundle else None,
        'table_class': candidate.table_class,
        'source_locator': candidate.source_locator,
    }

def _memory_claim_type(claim_type: str) -> str:
    if claim_type in {'financial_guidance_stated', 'financial_target_stated'}:
        return 'financial_metric_reported'
    return claim_type


def _financial_state_from_fact(f: FoundationFact) -> str:
    text = f'{f.claim_type} {f.predicate} {f.source_excerpt} {f.period_label}'.casefold()
    if str(f.claim_type) == 'financial_guidance_stated' or 'guidance' in text or 'outlook' in text:
        return 'guidance'
    if str(f.claim_type) == 'financial_target_stated' or 'target' in text:
        return 'target'
    if str(f.state) == 'actual' or (str(f.state) in {'current','historical'} and any(w in text for w in ('reported','annual report','results','financial highlights','year ended','fy'))):
        return 'actual'
    return str(f.state)

def _affected_attribute(f: FoundationFact) -> str:
    ct = str(f.claim_type)
    period = (f.period_label or 'reported_period').replace(' ', '_')
    pred = hashlib.sha256(f'{f.subject_name}:{f.predicate}:{f.business_unit}:{f.value_text}:{f.value_number}'.encode()).hexdigest()[:10]
    if 'financial_' in ct:
        metric = (f.predicate or f.object_type or 'metric').casefold().replace(' ', '_')
        return f'financial_performance.metrics.{metric}.{period}.{_financial_state_from_fact(f)}'
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

def _canonical_financial_statement(claim: dict[str, Any]) -> str:
    if claim.get('claim_type') == 'financial_metric_reported' and claim.get('display_value') and claim.get('metric_identity') and claim.get('period'):
        metric = str(claim.get('metric_label') or claim.get('metric_identity')).replace('_', ' ')
        return f"BT Group plc reported {claim.get('period')} {metric} of {claim.get('display_value')}."
    return claim.get('amended_statement') or claim.get('original_statement') or ''

def claim_to_evidence(run: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any]:
    claim, _ = canonicalise_financial_claim(claim)
    return {
        'evidence_id': claim['evidence_id'], 'enterprise_id': claim['canonical_enterprise_id'], 'canonical_enterprise_id': claim['canonical_enterprise_id'],
        'organisation': claim['canonical_enterprise_id'], 'source_id': run['document']['document_id'], 'source_name': run['document']['title'],
        'source_type': 'annual_report', 'source_url': run['document']['source_url'], 'evidence_tier': 'tier_1_company',
        'commercial_condition': claim['claim_type'], 'cleaned_observation': _canonical_financial_statement(claim),
        'extracted_observation': _canonical_financial_statement(claim), 'snippet': claim.get('source_excerpt') or '',
        'affected_attribute': claim['affected_attribute'], 'value': claim.get('display_value') or claim.get('value'), 'reported_amount': claim.get('reported_amount'), 'reported_scale': claim.get('reported_scale'), 'normalised_amount': claim.get('normalised_amount'), 'display_value': claim.get('display_value'), 'metric_identity': claim.get('metric_identity'), 'enterprise_scope': claim.get('enterprise_scope'), 'accounting_basis': claim.get('accounting_basis'), 'unit': claim.get('unit'), 'currency': claim.get('currency'),
        'period': claim.get('period'), 'state': claim.get('state', 'actual'), 'confidence': claim.get('confidence', 80),
        'page_range': claim.get('page_reference'), 'page_number': claim.get('page_reference'), 'publication_date': run['document'].get('publication_date'),
        'extraction_timestamp': now_iso(), 'provenance': 'evidence-backed', 'source_provenance': 'ai_document_understanding_reviewed',
        'extractor_name': 'OpenAIDirectPDFProvider', 'extractor_model': claim.get('extractor_model'), 'document_checksum': run['document']['checksum'],
        'source_excerpt': claim.get('source_excerpt'),
        'financial_table_evidence_bundle': claim.get('financial_table_evidence_bundle'),
        'evidence_bundle_id': claim.get('evidence_bundle_id'),
        'source_locator': claim.get('source_locator'),
        'supporting_evidence_ids': tuple(claim.get('supporting_evidence_ids') or (claim.get('evidence_id'),)),
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
        if (run.get('status') in {'completed', 'completed_with_exceptions'} and doc.get('checksum') == document.checksum and run.get('model') == model and run.get('schema_version') == settings.schema_version and run.get('prompt_version') == settings.prompt_version):
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
    if claim.get('extractor_provider') != 'deterministic' and int(claim.get('confidence') or 0) < AUTO_ACCEPT_CONFIDENCE:
        return False, 'confidence below governed acceptance threshold'
    claim, financial_reasons = canonicalise_financial_claim(claim)
    if financial_reasons:
        return False, 'financial_scale_ambiguous' if 'financial_scale_ambiguous' in financial_reasons else ', '.join(financial_reasons)
    required = ('value', 'currency', 'period', 'state', 'page_reference', 'affected_attribute', 'normalised_amount', 'reported_amount', 'reported_scale', 'source_excerpt', 'accounting_basis', 'enterprise_scope')
    missing = [field for field in required if claim.get(field) in (None, '')]
    if missing:
        return False, 'missing ' + ', '.join(missing)
    bundle = claim.get('financial_table_evidence_bundle')
    if claim.get('extractor_provider') == 'deterministic':
        if not isinstance(bundle, dict):
            return False, 'incomplete_financial_table_evidence_bundle'
        bundle_required = ('bundle_id','source_document_id','source_hash','original_pdf_page_number','table_id','table_title','table_unit_text','table_currency','table_scale','column_heading','column_period_text','row_label','raw_cell_text','parsed_amount','supporting_text_blocks','extraction_method','extraction_version','extraction_confidence')
        missing_bundle = [field for field in bundle_required if bundle.get(field) in (None, '', [])]
        if missing_bundle:
            return False, 'incomplete_financial_table_evidence_bundle'
        if str(bundle.get('raw_cell_text')).strip().casefold() in {'', '£', 'm', 'bn', '£m', '£bn'}:
            return False, 'unit_only_value'
        if claim.get('candidate_exception'):
            return False, str(claim.get('candidate_exception'))
    if not claim.get('business_unit') and 'bt group' not in claim.get('original_statement', '').casefold():
        return False, 'unclear group or segment scope'
    return True, 'governed source, table cell lineage, value, unit, currency, period, basis and confidence verified'

def _claim_packet_id(claim: dict[str, Any]) -> str | None:
    return claim.get('packet_id') or claim.get('provider_packet_id') or claim.get('source_packet_id')

def _candidate_disposition_row(claim: dict[str, Any], disposition: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        'candidate_id': claim.get('claim_id') or claim.get('candidate_id'),
        'packet_id': _claim_packet_id(claim),
        'provider_response_id': claim.get('provider_response_id') or claim.get('request_id') or claim.get('response_id'),
        'source_page': claim.get('page_reference') or claim.get('source_page'),
        'metric_identity': claim.get('metric_identity'),
        'reported_value': claim.get('original_display_value') or claim.get('display_value') or claim.get('value'),
        'normalised_value': claim.get('normalised_amount'),
        'accounting_basis': claim.get('accounting_basis'),
        'measurement_state': claim.get('financial_measurement_state') or claim.get('state'),
        'disposition': disposition,
        'disposition_reason': reason,
        'resulting_observation_id': extra.get('observation_id'),
        'resulting_enterprise_model_path': extra.get('enterprise_model_path') or claim.get('affected_attribute'),
    }

def _choose_canonical_claim(claims: list[dict[str, Any]]) -> dict[str, Any]:
    def precision_key(c: dict[str, Any]) -> tuple[int, int]:
        scale_rank = {'units': 3, 'thousands': 2, 'millions': 1, 'billions': 0}.get(str(c.get('reported_scale')), 0)
        amount = str(c.get('reported_amount') or '')
        decimals = len(amount.split('.', 1)[1]) if '.' in amount else 0
        return scale_rank, decimals
    chosen = max(claims, key=precision_key)
    merged = dict(chosen)
    merged['_canonical_source_candidate_id'] = chosen.get('claim_id') or chosen.get('candidate_id')
    evidence_ids = tuple(dict.fromkeys(str(c.get('evidence_id')) for c in claims if c.get('evidence_id')))
    merged['supporting_evidence_ids'] = evidence_ids
    merged['corroborating_candidates'] = [c.get('claim_id') for c in claims if c is not chosen]
    return merged

def _group_compatible_claims(claims: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for c in claims:
        buckets.setdefault(c.get('canonical_observation_identity') or c.get('claim_id'), []).append(c)
    groups: list[list[dict[str, Any]]] = []
    for bucket in buckets.values():
        remaining = list(bucket)
        while remaining:
            base = remaining.pop(0); group = [base]; rest = []
            for other in remaining:
                same = base.get('normalised_amount') == other.get('normalised_amount')
                compatible = same or rounding_compatible(base.get('reported_amount'), base.get('reported_scale'), other.get('normalised_amount')) or rounding_compatible(other.get('reported_amount'), other.get('reported_scale'), base.get('normalised_amount'))
                (group if compatible else rest).append(other)
            groups.append(group); remaining = rest
    return groups

def _read_after_write_ok(svc: ObservationMemoryService, result: Any, expected_evidence: tuple[str, ...]) -> tuple[bool, str]:
    observation = svc.observations.get(result.observation_id)
    if not observation:
        return False, 'persistence_failed: observation not readable after write'
    model = svc.models.get(result.enterprise_id)
    attr = model.attributes.get(result.affected_attribute)
    if not attr:
        return False, 'model_projection_failed: Enterprise Model path missing after write'
    if attr.current_value is None:
        return False, 'model_projection_failed: normalised value missing after write'
    if result.observation_id not in attr.observation_ids:
        return False, 'model_projection_failed: Observation lineage missing after write'
    if not set(expected_evidence).issubset(set(attr.evidence_ids)) or not set(expected_evidence).issubset(set(observation.supporting_evidence_ids)):
        return False, 'persistence_failed: Evidence lineage missing after write'
    return True, 'read-after-write validation passed'

def _apply_automatic_claims(run: dict[str, Any]) -> dict[str, Any]:
    svc = ObservationMemoryService(); results=[]; exceptions=[]; accepted=0; merges=0; dispositions=[]
    acceptable: list[dict[str, Any]] = []
    for i, raw in enumerate(run.get('claims', [])):
        claim, canon_reasons = canonicalise_financial_claim(raw)
        run['claims'][i] = claim
        ok, reason = _is_auto_acceptable(claim, run)
        for terminal in ('non_numeric_narrative','unsupported_metric','metric_identity_ambiguous','financial_scale_ambiguous','measurement_state_ambiguous','accounting_basis_ambiguous','invalid_lineage'):
            if canon_reasons and terminal in canon_reasons:
                reason = terminal; break
        claim['acceptance_reason'] = reason
        if ok:
            acceptable.append(claim)
        else:
            # Keep governed candidate-level exceptions only; do not add generic response-level duplicates.
            if 'range' in str(claim.get('source_excerpt') or claim.get('original_statement') or '').casefold() or ' to ' in str(claim.get('value') or '').casefold():
                reason = 'unsupported_financial_range'
            claim['review_state'] = 'needs_attention'; claim['disposition'] = reason; claim['exception_type'] = reason
            dispositions.append(_candidate_disposition_row(claim, reason, reason))
            exceptions.append(claim)
    for group in _group_compatible_claims(acceptable):
        canonical = _choose_canonical_claim(group)
        report = svc.process_evidence(claim_to_evidence(run, canonical))
        if report.results and not any(r.contradiction for r in report.results):
            result = report.results[0]
            ok, validation_reason = _read_after_write_ok(svc, result, tuple(canonical.get('supporting_evidence_ids') or (canonical.get('evidence_id'),)))
            if not ok:
                canonical['review_state'] = 'needs_attention'; canonical['disposition'] = validation_reason.split(':',1)[0]
                dispositions.append(_candidate_disposition_row(canonical, canonical['disposition'], validation_reason))
                exceptions.append(canonical); continue
            result_row = {**result.__dict__, 'update_result': result.action}
            results.append(result_row); accepted += 1
            for evidence_claim in group:
                ev = claim_to_evidence(run, evidence_claim)
                ev.update({'observation_id': result.observation_id, 'enterprise_model_path': result.affected_attribute, 'canonical_fact_id': canonical.get('canonical_fact_id') or canonical.get('canonical_observation_identity'), 'disposition': 'accepted' if evidence_claim is canonical else 'merged_as_corroborating_evidence'})
                svc.evidence.save(ev)
            canonical['review_state'] = 'auto_applied'; canonical['disposition'] = 'accepted'
            dispositions.append(_candidate_disposition_row(canonical, 'accepted', validation_reason, observation_id=result.observation_id, enterprise_model_path=result.affected_attribute))
            for c in group:
                if (c.get('claim_id') or c.get('candidate_id')) == canonical.get('_canonical_source_candidate_id'): continue
                c['review_state'] = 'merged'; c['disposition'] = 'merged_as_corroborating_evidence'
                dispositions.append(_candidate_disposition_row(c, 'merged_as_corroborating_evidence', 'rounding-compatible representation merged as corroborating Evidence', observation_id=result.observation_id, enterprise_model_path=result.affected_attribute))
                merges += 1
        else:
            reason = (report.rejected_claims[0].get('rejection_reason') if report.rejected_claims else 'contradiction or validation issue')
            for c in group:
                c['review_state'] = 'needs_attention'; c['disposition'] = 'quarantined'; c['exception_type'] = reason
                dispositions.append(_candidate_disposition_row(c, 'quarantined', reason)); exceptions.append(c)
            exceptions.extend(report.rejected_claims)
    for exc in run.get('candidate_exceptions', []):
        disp = exc.get('disposition') or exc.get('exception_type') or 'rejected'
        reason = exc.get('rejection_reason') or exc.get('safe_explanation') or exc.get('exception_type') or disp
        if 'range' in str(reason).casefold(): disp = 'unsupported_financial_range'
        dispositions.append({'candidate_id': exc.get('candidate_id') or exc.get('claim_id') or exc.get('packet_id'), 'packet_id': exc.get('packet_id'), 'provider_response_id': exc.get('provider_response_id') or exc.get('request_id'), 'source_page': exc.get('source_page') or exc.get('document_page') or exc.get('page'), 'metric_identity': exc.get('metric_identity'), 'reported_value': exc.get('value_text') or exc.get('reported_value'), 'normalised_value': None, 'accounting_basis': exc.get('accounting_basis'), 'measurement_state': exc.get('state'), 'disposition': disp, 'disposition_reason': reason, 'resulting_observation_id': None, 'resulting_enterprise_model_path': None})
    counts: dict[str, int] = {}
    for d in dispositions: counts[d['disposition']] = counts.get(d['disposition'], 0) + 1
    changed = [r for r in results if r.get('update_result') in {'created', 'updated'}]
    terminal_status = 'completed_with_no_accepted_intelligence' if accepted == 0 else ('completed_with_exceptions' if exceptions or run.get('candidate_exceptions') else 'completed')
    model = svc.models.get(canonical_enterprise_id(run.get('document', {}).get('enterprise_id') or 'bt-group-plc') or 'bt-group-plc')
    run.update({'status': terminal_status, 'applied_at': now_iso(), 'applied_results': results, 'exceptions': exceptions, 'auto_accepted_count': accepted, 'exception_count': len(exceptions), 'observations_created_or_strengthened': len(results), 'observations_created': len([r for r in results if r.get('update_result') == 'created']), 'observations_strengthened': len([r for r in results if r.get('update_result') == 'updated']), 'corroborating_evidence_merges': merges, 'deduplicated_count': merges, 'candidate_dispositions': dispositions, 'rejected_by_policy_count': len(exceptions), 'repository_diagnostics': {'observation_repository': type(svc.observations).__name__, 'enterprise_model_repository': type(svc.models).__name__, 'storage_mode': storage_mode().get('mode'), 'canonical_enterprise_id': model.enterprise_id, 'observation_count_after_write': len(svc.observations.list()), 'enterprise_model_attribute_count_after_projection': len(model.attributes)}, 'candidate_lifecycle_counts': {'packet_candidates_extracted': len(run.get('claims', [])) + len(run.get('candidate_exceptions', [])), 'candidates_returned': len(run.get('claims', [])) + len(run.get('candidate_exceptions', [])), 'valid_candidates': len(run.get('claims', [])), 'quarantined_candidates': len(run.get('candidate_exceptions', [])) + len([e for e in exceptions if e.get('review_state') == 'needs_attention']), 'canonical_facts_accepted': accepted, 'corroborating_evidence_merges': merges, 'automatically_accepted_candidates': accepted, 'deduplicated_candidates': merges, 'disposition_counts': counts, 'candidates_rejected_by_policy': len(exceptions), 'observations_created_or_strengthened': len(results), 'enterprise_model_attributes_created': len([r for r in changed if r.get('update_result') == 'created']), 'enterprise_model_attributes_updated': len([r for r in changed if r.get('update_result') == 'updated'])}, 'enterprise_attributes_changed': [r.get('affected_attribute') for r in changed]})
    return run



def _rapid_lane_from_fixture_result(rapid_result: dict[str, Any], elapsed_ms: int) -> dict[str, Any]:
    user_result = str(rapid_result.get('user_result') or '')
    facts = list(rapid_result.get('reported_financial_reality') or [])
    status = 'ready' if user_result and facts else ('partial' if user_result else 'unavailable')
    return {
        'status': status,
        'evidence_status': 'fixture_only',
        'source_receipts': list(rapid_result.get('sources') or []),
        'candidate_fact_count': int(rapid_result.get('candidate_fact_count') or len(facts)),
        'candidate_facts': facts,
        'management_commitments': list(rapid_result.get('management_commitments') or []),
        'hypotheses': list(rapid_result.get('transformation_hypotheses') or []),
        'unknowns': list(rapid_result.get('unknowns') or []),
        'contradictions': list(rapid_result.get('contradictions') or []),
        'user_result': user_result,
        'exceptions': list(rapid_result.get('verification_exceptions') or []),
        'elapsed_ms': elapsed_ms,
        'non_canonical': True,
        'fixture_only_warning': 'Fixture-only rapid intelligence: seeded candidate data for local orchestration proof; not verified official evidence and not production-ready.',
        'embedded_rapid_result': rapid_result,
    }


def _rapid_lane_from_source_receipt(receipt: Any, elapsed_ms: int, *, extraction: Any | None = None, temp_path_removed: bool | None = None) -> dict[str, Any]:
    receipt_dict = receipt.to_dict() if hasattr(receipt, 'to_dict') else dict(receipt or {})
    extraction_dict = extraction.to_dict() if extraction and hasattr(extraction, 'to_dict') else None
    candidates = list((extraction_dict or {}).get('candidates') or [])
    exceptions = list((extraction_dict or {}).get('exceptions') or [])
    status = 'ready' if extraction and extraction.extraction_status == 'completed' else ('partial' if extraction and extraction.candidate_count else 'unavailable')
    if extraction and extraction.extraction_status == 'failed_extraction':
        status = 'unavailable'
    return {
        'status': status,
        'evidence_status': 'official_source_retrieved' if receipt_dict.get('validation_result') == 'accepted' else 'official_source_unavailable',
        'source_receipt': receipt_dict,
        'source_receipts': [receipt_dict] if receipt_dict else [],
        'source_configuration_key': receipt_dict.get('configuration_key'),
        'source_validation_result': receipt_dict.get('validation_result'),
        'extraction_status': (extraction.extraction_status if extraction else 'not_run'),
        'candidate_count': len(candidates),
        'candidate_fact_count': len(candidates),
        'candidates': candidates,
        'candidate_facts': candidates,
        'exception_count': len(exceptions),
        'exceptions': exceptions,
        'source_call_count': int(receipt_dict.get('external_source_call_count') or 0),
        'ai_call_count': 0,
        'provider_cost': 0,
        'canonical_write_count': 0,
        'elapsed_ms': elapsed_ms,
        'pages_examined': list((extraction_dict or {}).get('pages_examined') or []),
        'extraction_version': (extraction_dict or {}).get('extraction_version'),
        'non_canonical': True,
        'source_temporary_file_removed': temp_path_removed,
        'support_diagnostics': {**(receipt_dict.get('support_diagnostics') or {k: receipt_dict.get(k) for k in ('parser_name','parser_version','page_count','pages_successfully_read','pages_with_extraction_errors','validation_marker_results','failure_code','failure_stage')}), 'extraction': (extraction_dict or {}).get('diagnostics') or {}},
        'user_result': 'Flora found an approved official BT FY26 financial document and identified three cited, unverified candidate facts.' if len(candidates) == 3 else '',
    }

def _rapid_lane_from_acquisition_error(exc: RapidSourceAcquisitionError, elapsed_ms: int) -> dict[str, Any]:
    receipt = exc.receipt.to_dict() if exc.receipt else {}
    return {
        'status': 'unavailable', 'evidence_status': 'official_source_unavailable',
        'source_receipt': receipt, 'source_receipts': [receipt] if receipt else [],
        'source_configuration_key': receipt.get('configuration_key'), 'source_validation_result': receipt.get('validation_result') or 'rejected',
        'extraction_status': 'not_run', 'candidate_count': 0, 'candidate_fact_count': 0, 'candidates': [], 'candidate_facts': [],
        'exception_count': 1, 'exceptions': [{'exception_type': exc.code, 'failure_stage': exc.stage, 'user_message': exc.safe_message, 'rejection_reason': exc.safe_message}],
        'source_call_count': int(receipt.get('external_source_call_count') or 0), 'ai_call_count': 0, 'provider_cost': 0, 'canonical_write_count': 0,
        'elapsed_ms': elapsed_ms, 'pages_examined': [], 'extraction_version': None, 'non_canonical': True, 'support_diagnostics': receipt.get('support_diagnostics') or {k: receipt.get(k) for k in ('parser_name','parser_version','page_count','pages_successfully_read','pages_with_extraction_errors','validation_marker_results','failure_code','failure_stage')}, 'user_result': '',
    }


def _verification_unavailable_lane(run_id: str, enterprise_id: str, started: float) -> dict[str, Any]:
    return {
        'status': 'unavailable',
        'source': 'structured_standard_financials',
        'adapter_handoff_attempted': False,
        'adapter_result': None,
        'facts_checked': 0,
        'facts_verified': 0,
        'facts_rejected': 0,
        'facts_contradicted': 0,
        'exceptions': [{
            'exception_type': 'structured_source_unavailable',
            'failure_stage': 'structured_verification_not_executed_in_slice_1',
            'support_reference': 'FI-' + run_id.removeprefix('fi-'),
            'user_message': 'Structured verification unavailable in Slice 1 fixture-only dual-speed mode.',
            'rejection_reason': 'Slice 1 does not retrieve live BT, FCA, ESEF or other external structured sources.',
        }],
        'diagnostics': [{
            'event': 'verification_unavailable',
            'enterprise_id': enterprise_id,
            'adapter_handoff_attempted': False,
            'no_adapter_result_before_handoff': True,
            'external_source_call_count': 0,
        }],
        'elapsed_ms': int((time.time() - started) * 1000),
    }


def _canonical_update_not_applicable() -> dict[str, Any]:
    return {
        'status': 'not_applicable',
        'evidence_ids': [],
        'observation_ids': [],
        'enterprise_model_updated': False,
        'attributes_updated': [],
        'transaction_result': 'not_started_fixture_only_rapid_candidates',
        'idempotency_result': 'not_applicable',
        'exceptions': [],
    }


def _dual_speed_completion_class(rapid: dict[str, Any], verification: dict[str, Any]) -> tuple[str, str]:
    rapid_status = rapid.get('status')
    verification_status = verification.get('status')
    has_rapid = bool(rapid.get('user_result')) and rapid_status in {'ready', 'partial'}
    if rapid_status == 'ready' and verification_status == 'verified':
        return 'completed', 'verified'
    if rapid_status == 'ready' and verification_status in {'unavailable', 'failed'}:
        return 'completed', 'unverified'
    if rapid_status == 'partial' and verification_status != 'verified':
        return 'completed', 'partial'
    if not has_rapid and verification_status == 'verified':
        return 'completed', 'verified'
    return 'failed', 'no_trustworthy_evidence'


def coordinate_dual_speed_financial_intelligence_run(enterprise_id: str = 'bt-group-plc', run_id: str | None = None, reporting_period: str = 'FY26', *, acquisition_boundary: Any = None, extraction_boundary: Any = None) -> dict[str, Any]:
    """Coordinate BT Financial Intelligence research in one standard run record."""
    acquisition_boundary = acquisition_boundary or acquire_rapid_financial_source
    extraction_boundary = extraction_boundary or extract_rapid_financial_candidates
    run_id = run_id or ('fi-' + uuid.uuid4().hex[:12])
    ensure_writable_dir(_run_dir())
    created_at = now_iso()
    support_reference = 'FI-' + run_id.removeprefix('fi-')
    result_url = f'/financial-intelligence/{run_id}'
    before = _trusted_state_snapshot(enterprise_id)
    run = {
        'run_id': run_id,
        'enterprise_id': enterprise_id,
        'reporting_period': reporting_period,
        'execution_mode': DUAL_SPEED_FINANCIAL_INTELLIGENCE_MODE,
        'extraction_mode': DUAL_SPEED_FINANCIAL_INTELLIGENCE_MODE,
        'extraction_mode_label': 'BT financial intelligence research',
        'overall_status': 'running',
        'completion_class': None,
        'status': 'running',
        'state': 'running',
        'workflow': 'financial_intelligence',
        'created_at': created_at,
        'updated_at': created_at,
        'support_reference': support_reference,
        'deployed_revision': deployed_revision(),
        'result_url': result_url,
        'rapid_intelligence': {'status': 'not_started'},
        'verification': {'status': 'not_started'},
        'canonical_update': _canonical_update_not_applicable(),
        'cost_summary': {'ai_call_count': 0, 'provider': 'none', 'model': None, 'input_tokens': 0, 'output_tokens': 0, 'estimated_provider_cost_usd': 0, 'cache_reused': False, 'external_source_call_count': 0},
        'diagnostics': {'slice': 'slice_1_fixture_orchestration_shell', 'production_ready': False, 'trusted_state_before': before},
        'claims': [], 'applied_results': [], 'exceptions': [],
        'terminal': False, 'progress_percent': 0, 'percent_complete': 0,
    }
    _write_json(_run_path(run_id), run)
    rapid_started = time.time()
    run['rapid_intelligence'] = {'status': 'running', 'ai_call_count': 0, 'canonical_write_count': 0}
    run['updated_at'] = now_iso(); run['progress_percent'] = run['percent_complete'] = 15
    _write_json(_run_path(run_id), run)
    try:
        temp_path = None
        with acquisition_boundary(enterprise_id, reporting_period) as acquired:
            temp_path = Path(acquired.path)
            extraction = extraction_boundary(acquired)
            rapid_lane = _rapid_lane_from_source_receipt(acquired.receipt, int((time.time() - rapid_started) * 1000), extraction=extraction, temp_path_removed=False)
        rapid_lane['source_temporary_file_removed'] = (not temp_path.exists()) if temp_path else None
    except RapidSourceAcquisitionError as exc:
        rapid_lane = _rapid_lane_from_acquisition_error(exc, int((time.time() - rapid_started) * 1000))
    run['rapid_intelligence'] = rapid_lane
    run['updated_at'] = now_iso(); run['progress_percent'] = run['percent_complete'] = 55
    run['cost_summary'].update({'ai_call_count': 0, 'estimated_provider_cost_usd': 0, 'external_source_call_count': rapid_lane.get('source_call_count', 0), 'canonical_write_count': 0})
    _write_json(_run_path(run_id), run)
    verification_started = time.time()
    verification_lane = _verification_unavailable_lane(run_id, enterprise_id, verification_started)
    run['verification'] = verification_lane
    run['canonical_update'] = _canonical_update_not_applicable()
    overall_status, completion_class = _dual_speed_completion_class(rapid_lane, verification_lane)
    after = _trusted_state_snapshot(enterprise_id)
    run.update({
        'overall_status': overall_status,
        'completion_class': completion_class,
        'status': overall_status,
        'state': overall_status,
        'current_stage': overall_status,
        'updated_at': now_iso(),
        'completed_at': now_iso(),
        'terminal': True,
        'progress_percent': 100,
        'percent_complete': 100,
        'user_message': rapid_lane.get('user_result') if rapid_lane.get('user_result') else 'No trustworthy Financial Intelligence outcome could be produced.',
        'exceptions': list(verification_lane.get('exceptions') or []),
        'ai_calls_made': 0,
        'openai_calls_made': 0,
        'estimated_cost_usd': 0,
        'actual_cost_usd': 0,
        'trusted_state_before': before,
        'trusted_state_after': after,
        'trusted_twin_changed': before['active_observation_count'] != after['active_observation_count'] or before['active_enterprise_model_attribute_count'] != after['active_enterprise_model_attribute_count'],
    })
    run['diagnostics'].update({'trusted_state_after': after, 'canonical_memory_changed': run['trusted_twin_changed'], 'rapid_support_diagnostics': rapid_lane.get('support_diagnostics')})
    attach_financial_run_diagnostic(run)
    _write_json(_run_path(run_id), run)
    return run

def refresh_financial_intelligence(enterprise_id: str = 'bt-group-plc', run_id: str | None = None, extraction_mode: str = 'structured_standard_financials') -> dict[str, Any]:
    run_id = run_id or ('fi-' + uuid.uuid4().hex[:12])
    acquisition_mode = extraction_mode or 'structured_standard_financials'
    if acquisition_mode == DUAL_SPEED_FINANCIAL_INTELLIGENCE_MODE:
        return coordinate_dual_speed_financial_intelligence_run(enterprise_id=enterprise_id, run_id=run_id)
    if acquisition_mode == 'structured_standard_financials':
        return _refresh_structured_financial_intelligence(enterprise_id, run_id)
    if acquisition_mode == 'rapid_financial_intelligence':
        return run_rapid_financial_intelligence(enterprise_id=enterprise_id, run_id=run_id)
    if acquisition_mode == 'pdf_supporting_evidence':
        extraction_mode = 'pdf_supporting_evidence'
    elif acquisition_mode == 'narrative_financial_interpretation':
        extraction_mode = 'narrative_financial_interpretation'
    elif acquisition_mode in {'administrative_review', 'administrative_ai_review'}:
        extraction_mode = 'administrative_review'
    else:
        raise ValueError(f'Unsupported financial intelligence acquisition mode: {acquisition_mode}')
    source = _bt_annual_report_source()
    correlation_id = run_id.removeprefix('fi-')
    ensure_writable_dir(_run_dir())
    retrieval_started = time.time()
    _write_progress(run_id, 'retrieving_source')
    fetched = fetch_document(source['url'])
    doc_parse = parse_pdf_document(fetched, _source_obj(source), canonical_enterprise_id='bt-group-plc')
    document = ExperimentDocument(document_id=doc_parse.document_id, enterprise_id='bt-group-plc', title=source['source_name'], source_url=(fetched.final_url or source['url']), retrieval_timestamp=doc_parse.retrieval_date, checksum=doc_parse.checksum, media_type=doc_parse.media_type or 'application/pdf', page_count=max(doc_parse.page_count, 1), local_path=doc_parse.local_path)
    settings = financial_intelligence_settings()
    provider = None if extraction_mode == 'pdf_supporting_evidence' else OpenAIDirectPDFProvider(model=settings.model, reasoning_effort=settings.reasoning_effort, max_output_tokens=settings.max_output_tokens, max_run_cost_usd=settings.max_run_cost_usd)

    _write_progress(run_id, 'checking_document_quality')
    _write_progress(run_id, 'selecting_sections', collection={'retrieved': fetched.succeeded, 'retrieval_time': fetched.retrieval_date, 'http_status': fetched.status_code, 'error': fetched.error})
    if extraction_mode == 'pdf_supporting_evidence':
        with provider_call_guard(extraction_mode, allowed_calls=0) as guard:
            _write_progress(run_id, 'validating')
            adapter_result = PdfFinancialTableAdapter().extract(document, embedded_pages=doc_parse.pages) if (fetched.succeeded and document.media_type == 'application/pdf' and doc_parse.pages) else None
            claims = [deterministic_candidate_to_review_claim(c, run_id) for c in (adapter_result.candidates if adapter_result else ())]
            run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'validating', 'workflow': 'financial_intelligence', 'deployed_revision': deployed_revision(), 'extraction_mode': 'pdf_supporting_evidence', 'extraction_mode_label': 'PDF supporting evidence', 'governed_source': source, 'collection': {'retrieved': fetched.succeeded, 'retrieval_time': fetched.retrieval_date, 'http_status': fetched.status_code, 'error': fetched.error, 'active_source_url': source['url'], 'document_size': len(fetched.content or b''), 'final_url': fetched.final_url or fetched.url, 'content_type': fetched.media_type, 'redirect_chain': list(fetched.redirect_chain), 'redirected': bool(fetched.redirect_chain)}, 'document': document.model_dump(), 'provider': 'deterministic', 'model': (adapter_result.adapter_name if adapter_result else 'pdf_financial_table'), 'reasoning_effort': None, 'schema_version': settings.schema_version, 'prompt_version': 'deterministic-financial-fact-capture-v2', 'document_hash': document.checksum, 'deterministic_cache_key': hashlib.sha256(f"{document.enterprise_id}:{document.checksum}:{document.source_url}:{ADAPTER_VERSION}:{settings.schema_version}:financial-metric-catalogue-v1".encode()).hexdigest(), 'deterministic_replay': 'fresh deterministic extraction', 'usage': {'openai_calls': 0}, 'estimated_cost_usd': 0, 'actual_cost_usd': 0, 'provider_status': 'not_executed', 'provider_errors': [], 'raw_response_location': None, 'provider_diagnostics': [], 'openai_invoked': False, 'openai_calls_made': 0, 'ai_calls_made': 0, 'claims': claims, 'applied_results': [], 'candidate_exceptions': list(adapter_result.exceptions if adapter_result else ()), 'candidate_pages_selected': sorted({c.source_page for c in (adapter_result.candidates if adapter_result else ()) if c.source_page}), 'page_packets_submitted': [], 'packet_count': 0, 'pdf_navigation_diagnostics': {'selected_parser': doc_parse.extraction_method, 'adapter': 'PdfFinancialTableAdapter', 'deterministic_candidates_extracted': len(claims), 'financial_tables_inspected': (adapter_result.exceptions[0].get('diagnostics', {}).get('approved_financial_tables') if adapter_result and adapter_result.exceptions and isinstance(adapter_result.exceptions[0], dict) else None)}, 'visual_navigation': {}, 'visual_navigation_fallback_used': False}
            if guard.attempted_calls:
                run = _mark_failure(run, 'deterministic_route_provider_violation', 'Provider request blocked before transmission')
            elif not fetched.succeeded:
                run = _mark_failure(run, 'source_retrieval_failed', fetched.error or 'governed source retrieval failed')
            elif document.media_type != 'application/pdf':
                run = _mark_failure(run, 'source_not_pdf', doc_parse.error or f"source returned {document.media_type}")
            elif not any(c.get('candidate_exception') is None for c in claims):
                run = _mark_failure(run, 'section_selection_failed', 'Deterministic extraction could not prove the required financial table context; no AI fallback occurred.')
            else:
                try:
                    _write_progress(run_id, 'updating_memory')
                    run = _apply_automatic_claims(run)
                    if run.get('observations_created_or_strengthened', 0) == 0 and run.get('auto_accepted_count', 0) == 0:
                        run['no_new_evidence_message'] = 'No new financial evidence was found. The trusted Financial Twin remains current.'
                except Exception as exc:
                    run = _mark_failure(run, 'persistence_failed', f'{type(exc).__name__}: {exc}')
            run['ai_calls_made'] = run['openai_calls_made'] = run.get('openai_calls_made', 0)
            run['support_reference'] = _support_reference(run)
            run['exceptions'] = _dedupe_exceptions(run.get('exceptions', []))
            run['terminal'] = True; run['progress_percent'] = run['percent_complete'] = 100
            _write_cost_record(run)
            try:
                attach_financial_run_diagnostic(run)
                _write_json(_run_path(run_id), run)
            except PersistenceError as exc:
                run = _mark_failure(run, 'persistence_failed', f'{type(exc).__name__}: {exc}')
            return run
    provider = provider or OpenAIDirectPDFProvider(model=settings.model, reasoning_effort=settings.reasoning_effort, max_output_tokens=settings.max_output_tokens, max_run_cost_usd=settings.max_run_cost_usd)
    cached = _successful_cached_run(document, provider.model) if fetched.succeeded else None
    if cached:
        run = dict(cached)
        run['run_id'] = run_id
        run['created_at'] = now_iso()
        run['cached_output_reused'] = True
        run['openai_invoked'] = False
        run = _apply_automatic_claims(run)
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
    run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'validating', 'workflow': 'financial_intelligence', 'deployed_revision': deployed_revision(), 'governed_source': source, 'collection': {'retrieved': fetched.succeeded, 'retrieval_time': fetched.retrieval_date, 'http_status': fetched.status_code, 'error': fetched.error, 'active_source_url': source['url'], 'document_size': len(fetched.content or b'')}, 'document': document.model_dump(), 'provider': (extraction.provider if extraction else 'openai'), 'model': (extraction.model if extraction else provider.model), 'reasoning_effort': getattr(provider, 'reasoning_effort', settings.reasoning_effort), 'schema_version': settings.schema_version, 'prompt_version': settings.prompt_version, 'document_hash': document.checksum, 'usage': (extraction.usage if extraction else {}), 'estimated_cost_usd': (extraction.estimated_cost_usd if extraction else None), 'actual_cost_usd': (getattr(extraction, 'verifier', {}) or {}).get('actual_cost_usd') if extraction else None, 'cost_breakdown': {'input_cost_usd': (getattr(extraction, 'verifier', {}) or {}).get('input_cost_usd'), 'output_cost_usd': (getattr(extraction, 'verifier', {}) or {}).get('output_cost_usd')} if extraction else {}, 'exact_preflight_available': (getattr(extraction, 'verifier', {}) or {}).get('exact_preflight_available') if extraction else None, 'provider_status': (extraction.status if extraction else 'not_executed'), 'provider_errors': (extraction.provider_errors if extraction else [fetched.error]), 'raw_response_location': (extraction.raw_response_location if extraction else None), 'provider_diagnostics': (getattr(extraction, 'diagnostics', []) if extraction else [_safe_provider_diagnostic(run_id, source, fetched, provider.model, retrieval_started)]), 'openai_invoked': bool(extraction and (not packet_plan or packet_plan.get('packet_count', 0))), 'claims': claims, 'applied_results': [], 'candidate_exceptions': candidate_exceptions, 'candidate_pages_selected': packet_plan.get('candidate_pages', []), 'page_packets_submitted': packet_plan.get('packets', []), 'packet_count': packet_plan.get('packet_count', 0), 'pdf_navigation_diagnostics': packet_plan.get('parse_diagnostics', {}), 'visual_navigation': packet_plan.get('visual_navigation', {}), 'visual_navigation_fallback_used': bool((packet_plan.get('visual_navigation') or {}).get('visual_fallback_used'))}
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
            if not run.get('claims') and not run.get('applied_results'):
                run = _mark_failure(run, 'failed', 'zero packets/facts/Observations cannot produce completed status')
            if candidate_exceptions:
                run['exceptions'] = run.get('exceptions', []) + candidate_exceptions
                run['exception_count'] = len(run.get('exceptions', []))
                if run.get('status') == 'completed':
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
    run['terminal'] = run.get('status') not in ACTIVE_RUN_STATES
    run['progress_percent'] = run['percent_complete'] = 100 if run['terminal'] else int(run.get('progress_percent') or 0)
    run['exception_count'] = len(run.get('exceptions', []))
    _record_provider_diagnostics(run)
    _write_cost_record(run)
    if fetched.succeeded:
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass
    try:
        attach_financial_run_diagnostic(run)
        _write_json(_run_path(run_id), run)
    except PersistenceError as exc:
        run = _mark_failure(run, 'persistence_failed', f'{type(exc).__name__}: {exc}')
    return run


def _active_refresh_run() -> dict[str, Any] | None:
    if not _run_dir().exists(): return None
    for path in sorted(_run_dir().glob('fi-*.json'), key=lambda p: p.stat().st_mtime, reverse=True):
        run = _read_json(path)
        if run.get('status') in ACTIVE_RUN_STATES:
            return run
    return None

def create_financial_intelligence_progress_run(enterprise_id: str = 'bt-group-plc', extraction_mode: str = 'structured_standard_financials') -> dict[str, Any]:
    active = _active_refresh_run()
    if active: return active
    run_id = 'fi-' + uuid.uuid4().hex[:12]
    run = {'run_id': run_id, 'created_at': now_iso(), 'deployed_revision': deployed_revision(), 'status': 'queued', 'state': 'queued', 'terminal': False, 'progress_percent': 0, 'workflow': 'financial_intelligence', 'enterprise_id': enterprise_id, 'extraction_mode': extraction_mode, 'support_reference': 'FI-' + run_id.removeprefix('fi-'), 'claims': [], 'applied_results': [], 'exceptions': []}
    _write_json(_run_path(run_id), run)
    threading.Thread(target=_background_refresh, args=(enterprise_id, run_id, extraction_mode), daemon=True).start()
    return run

def _background_refresh(enterprise_id: str, run_id: str, extraction_mode: str = 'structured_standard_financials') -> None:
    try:
        refresh_financial_intelligence(enterprise_id=enterprise_id, run_id=run_id, extraction_mode=extraction_mode)
    except Exception as exc:
        LOGGER.exception('Financial Intelligence background refresh failed support_reference=%s', 'FI-' + run_id.removeprefix('fi-'))
        run = {'run_id': run_id, 'created_at': now_iso(), 'deployed_revision': deployed_revision(), 'status': 'failed', 'failure_category': 'failed', 'support_reference': 'FI-' + run_id.removeprefix('fi-'), 'exceptions': [{'exception_type': 'failed', 'failure_stage': 'failed', 'support_reference': 'FI-' + run_id.removeprefix('fi-'), 'user_message': 'Financial Intelligence refresh failed safely.', 'rejection_reason': f'{type(exc).__name__}: {exc}'}], 'claims': [], 'applied_results': []}
        attach_financial_run_diagnostic(run)
        _write_json(_run_path(run_id), run)


def missing_run_status(run_id: str) -> dict[str, Any]:
    return {
        'run_id': run_id,
        'requested_run_id': run_id,
        'status': 'not_found',
        'state': 'not_found',
        'terminal': True,
        'progress_percent': 100,
        'current_stage': 'not_found',
        'message': 'This financial intelligence run is no longer available. Please start a new run.',
        'final_result_url': None,
    }

def financial_intelligence_progress_status(run_id: str) -> dict[str, Any]:
    try:
        run = load_run(run_id)
    except FileNotFoundError:
        print(f"Flora Financial Intelligence requested missing progress run {run_id}; storage mode={storage_mode()['mode']}")
        return missing_run_status(run_id)
    status = run.get('status') or 'queued'
    terminal = status in TERMINAL_RUN_STATES or bool(run.get('terminal'))
    created = run.get('created_at') or now_iso()
    try: elapsed = int((datetime.now(UTC) - datetime.fromisoformat(created)).total_seconds())
    except Exception: elapsed = 0
    pct = int(run.get('progress_percent') or run.get('percent_complete') or (100 if terminal else 0))
    return {'run_id': run_id, 'state': status, 'terminal': terminal, 'progress_percent': 100 if terminal else pct, 'current_stage': run.get('current_stage') or status, 'elapsed_time': elapsed, 'packet_count': run.get('packet_count',0), 'packets_completed': len([p for p in run.get('page_packets_submitted',[]) if p.get('status')]), 'facts_valid': len(run.get('claims',[])), 'facts_quarantined': len(run.get('candidate_exceptions') or run.get('exceptions') or []), 'final_result_url': f'/financial-intelligence/{run_id}' if terminal else None}

def financial_intelligence_progress_page(run_id: str) -> str:
    try:
        run = load_run(run_id)
    except FileNotFoundError:
        return missing_run_page(run_id)
    labels = {'queued': 'Queued', 'retrieving_source': 'Retrieving the financial report', 'selecting_sections': 'Reading the report structure / Finding relevant financial sections', 'estimating_cost': 'Estimating processing cost', 'analysing': 'Analysing financial sections', 'validating': 'Validating financial facts', 'updating_memory': 'Updating the Commercial Digital Twin', 'completed': 'Complete', 'completed_with_exceptions': 'Needs attention', 'completed_with_no_accepted_intelligence': 'No accepted intelligence', 'checking_document_quality': 'Checking document quality', 'document_parsing_failed': 'Checking document quality — Failed', 'section_selection_failed': 'Finding financial sections — Needs attention', 'provider_response_invalid': 'Needs attention', 'provider_request_failed': 'Failed', 'failed': 'Failed'}
    created = run.get('created_at') or now_iso()
    try: elapsed = int((datetime.now(UTC) - datetime.fromisoformat(created)).total_seconds())
    except Exception: elapsed = 0
    label = labels.get(run.get('status'), 'Failed' if run.get('status') not in {'queued','retrieving_source','selecting_sections','estimating_cost','analysing','validating','updating_memory'} else 'Working')
    terminal = run.get('status') in TERMINAL_RUN_STATES or bool(run.get('terminal'))
    pct = int(run.get('progress_percent') or run.get('percent_complete') or (100 if terminal else 0))
    body = f"""<section class='hero'><h1>Financial Intelligence refresh</h1><p>{escape(label)}</p><div style='background:#eee;border-radius:999px;overflow:hidden'><div id='bar' style='width:{pct}%;background:#185c4d;color:white;padding:8px'>{pct}%</div></div><p>Elapsed time: {elapsed} seconds. Large reports may take several minutes.</p></section>{_outcome_summary(run) if terminal else ''}<script>let polling={str(not terminal).lower()};let timer=null;async function poll(){{if(!polling)return;const r=await fetch('/financial-intelligence/progress/{escape(run_id)}/status',{{cache:'no-store'}});const s=await r.json();document.getElementById('bar').style.width=s.progress_percent+'%';document.getElementById('bar').textContent=s.progress_percent+'%';if(s.terminal){{polling=false;if(timer)clearTimeout(timer);if(s.final_result_url){{location.href=s.final_result_url}}else{{document.querySelector('.hero p').textContent=s.message||'This financial intelligence run is no longer available. Please start a new run.'}}return}}timer=setTimeout(poll,2000)}}if(polling)poll();</script>"""
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
        results.extend(({**r.__dict__, 'update_result': r.action}) for r in report.results)
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

def _business_change_label(run: dict[str, Any], result: dict[str, Any]) -> str:
    attr = str(result.get('affected_attribute') or '')
    claim = next((c for c in run.get('claims', []) if c.get('affected_attribute') == attr), None)
    if claim and claim.get('display_value'):
        metric = str(claim.get('metric_identity') or attr.rsplit('.', 4)[0].rsplit('.', 1)[-1]).replace('_', ' ').title().replace('Ebitda', 'EBITDA')
        return f"{metric}: {claim.get('display_value')} — strengthened by {len(claim.get('supporting_evidence_ids') or (claim.get('evidence_id'),))} Evidence records"
    return attr

def _rapid_exception_business_summaries(exceptions: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> list[str]:
    seen_categories: dict[str, set[str]] = {}
    for e in exceptions or []:
        metric = str(e.get('metric_identity') or '')
        if metric in {'revenue','operating_profit','profit_before_tax'}:
            seen_categories.setdefault(metric, set()).add(str(e.get('category') or e.get('exception_type') or ''))
    messages = {
        'revenue': 'Revenue: Flora found adjusted measures but could not establish the required statutory Group figure.',
        'operating_profit': 'Operating profit: the required statutory Group row could not be identified safely.',
        'profit_before_tax': 'Profit before tax: the amount was found, but its reported scale could not be established safely.',
    }
    out=[]
    for metric in ('revenue','operating_profit','profit_before_tax'):
        cats=seen_categories.get(metric,set())
        if not cats: continue
        if metric == 'revenue' and 'adjusted value rejected' in cats: out.append(messages[metric])
        elif metric == 'profit_before_tax' and 'scale missing' in cats: out.append(messages[metric])
        elif metric == 'operating_profit': out.append(messages[metric])
        else: out.append(f"{_display_metric(metric)}: the required statutory Group figure could not be identified safely.")
    return out

def _display_metric(mid: str) -> str:
    return {"revenue":"Revenue","operating_profit":"Operating profit","profit_before_tax":"Profit before tax"}.get(str(mid), str(mid).replace('_',' ').title())

def _display_enum(value: str) -> str:
    return {
        'official_source_retrieved': 'Official source retrieved',
        'no_trustworthy_evidence': 'No trustworthy findings',
        'not_applicable': 'No canonical update required',
        'candidate_unverified': 'Verification pending',
        'not_started': 'Not started',
    }.get(str(value), str(value).replace('_',' ').title())

def _render_dual_speed_outcome(run: dict[str, Any], show_support_control: bool = False) -> str:
    support_report_link = financial_intelligence_support_report_link(run.get('run_id')) if show_support_control else ''
    rapid = run.get('rapid_intelligence') or {}
    verification = run.get('verification') or {}
    canonical = run.get('canonical_update') or {}
    cost = run.get('cost_summary') or {}
    receipt = rapid.get('source_receipt') or {}
    candidates = rapid.get('candidates') or rapid.get('candidate_facts') or []
    canonical_status = escape(_display_enum(str(canonical.get('status') or 'not_started')))
    canonical_changed = 'yes' if canonical.get('enterprise_model_updated') else 'no'
    if receipt and rapid.get('evidence_status') == 'official_source_retrieved':
        unresolved = {'revenue', 'operating_profit', 'profit_before_tax'} - {str(c.get('proposed_canonical_metric_id')) for c in candidates}
        unresolved_html = '<ul>' + ''.join(f"<li>{escape(_display_metric(m))}</li>" for m in sorted(unresolved)) + '</ul>' if unresolved else ''
        business_items = ''.join(f"<li>{escape(m)}</li>" for m in _rapid_exception_business_summaries(rapid.get('exceptions') or [])) or '<li>The required statutory Group figures could not be identified safely.</li>'
        if not candidates:
            return f"""<section class='card warning'><h2>Official BT report retrieved — no safe financial findings identified</h2><p>Flora reached and validated the approved BT FY26 report, but it could not identify the required financial figures safely.</p><p>No fixture or seeded information was substituted, and the trusted Commercial Digital Twin was unchanged.</p><h3>Unresolved financial figures</h3>{unresolved_html}<ul>{business_items}</ul><p><strong>{escape(str(receipt.get('document_title')))}</strong> · Authority: {escape(str(receipt.get('authority')))} · Reporting period: {escape(str(receipt.get('reporting_period')))} · Source retrieval status: Official source retrieved</p></section><section class='card'><h2>Canonical update summary</h2><p>Status: No canonical update required · Enterprise Model updated: {canonical_changed}</p></section><section class='card'><h2>Run outcome</h2><p>Overall status: {escape(_display_enum(str(run.get('overall_status'))))} · Completion class: {escape(_display_enum(str(run.get('completion_class'))))} · Result URL: {escape(str(run.get('result_url')))} · Support reference: {escape(str(run.get('support_reference')))}</p><p>AI calls: {escape(str(cost.get('ai_call_count', 0)))} · Provider cost: {escape(str(cost.get('estimated_provider_cost_usd', 0)))} USD · Live source calls: {escape(str(cost.get('external_source_call_count', 0)))}</p>{support_report_link}</section>"""
        rows = ''.join(
            f"<tr><td>{escape(str(c.get('raw_metric_label') or _display_metric(c.get('proposed_canonical_metric_id'))))}</td>"
            f"<td>{escape(str(c.get('original_displayed_value') or c.get('raw_value_text')))}</td>"
            f"<td>{escape(str(c.get('reported_amount')))} {escape(str(c.get('currency')))} {escape(str(c.get('reported_scale')))}</td>"
            f"<td>Page {escape(str(c.get('source_page')))} · {escape(str(c.get('source_locator')))}</td>"
            f"<td>{escape(_display_enum(str(c.get('verification_status') or 'candidate_unverified')))}</td></tr>"
            for c in candidates
        )
        heading = 'Official-source candidate facts' if not unresolved else 'Partial source-backed financial findings'
        msg = 'These figures were extracted from an approved official document but have not yet completed structured verification or canonical acceptance.' if not unresolved else 'Flora identified some source-backed financial findings, but not every required figure could be established safely.'
        unresolved_block = f"<h3>Unresolved financial figures</h3>{unresolved_html}" if unresolved else ''
        return f"""<section class='card warning'><h2>{heading}</h2><p>{msg}</p><p><strong>{escape(str(receipt.get('document_title')))}</strong> · Authority: {escape(str(receipt.get('authority')))} · Reporting period: {escape(str(receipt.get('reporting_period')))} · Source retrieval status: Official source retrieved</p><table><thead><tr><th>Metric</th><th>Displayed value</th><th>Reported amount</th><th>Page/table citation</th><th>Verification</th></tr></thead><tbody>{rows}</tbody></table>{unresolved_block}<p>Canonical memory has not been updated. Evidence IDs: {escape(str(len(canonical.get('evidence_ids') or [])))} · Observation IDs: {escape(str(len(canonical.get('observation_ids') or [])))} · Enterprise Model updated: {canonical_changed}</p><ul>{business_items}</ul></section><section class='card'><h2>Verification summary</h2><p>Status: {escape(_display_enum(str(verification.get('status') or 'not_started')))} · Facts verified: {escape(str(verification.get('facts_verified', 0)))}</p></section><section class='card'><h2>Canonical update summary</h2><p>Status: {canonical_status} · Enterprise Model updated: {canonical_changed}</p></section><section class='card'><h2>Run outcome</h2><p>Overall status: {escape(_display_enum(str(run.get('overall_status'))))} · Completion class: {escape(_display_enum(str(run.get('completion_class'))))} · Result URL: {escape(str(run.get('result_url')))} · Support reference: {escape(str(run.get('support_reference')))}</p><p>AI calls: {escape(str(cost.get('ai_call_count', 0)))} · Provider cost: {escape(str(cost.get('estimated_provider_cost_usd', 0)))} USD · Live source calls: {escape(str(cost.get('external_source_call_count', 0)))}</p>{support_report_link}</section>"""
    if rapid.get('evidence_status') == 'official_source_unavailable':
        exc = (rapid.get('exceptions') or [{}])[0]
        return f"""<section class='card warning'><h2>Official source unavailable</h2><p>Flora reached the approved BT financial report but could not read it safely.</p><p>Stage: {escape(str(exc.get('failure_stage') or receipt.get('failure_stage') or 'unknown'))} · Cause: {escape(str(exc.get('user_message') or receipt.get('safe_failure_message') or 'Source unavailable'))}</p><p>No financial findings were created. No fixture or seeded information was substituted, and the trusted Commercial Digital Twin was unchanged.</p></section>"""
    rapid_result = escape(str(rapid.get('user_result') or 'No rapid outlook is available.'))
    return f"""<section class='card warning'><h2>Fixture-only evidence warning</h2><p>This legacy result uses seeded rapid fixture data for local orchestration proof only. It is not verified official evidence and has not updated canonical Evidence, Observations or the Enterprise Model.</p></section><section class='card'><h2>Rapid Financial Pressure and Transformation Outlook</h2><p>Rapid lane status: {escape(_display_enum(str(rapid.get('status'))))} · Evidence status: {escape(_display_enum(str(rapid.get('evidence_status'))))} · Candidate facts: {escape(str(rapid.get('candidate_fact_count', 0)))}</p><pre>{rapid_result}</pre></section>"""

def _outcome_summary(run: dict[str, Any] | None, show_support_control: bool = False) -> str:
    support_report_link = financial_intelligence_support_report_link(run.get('run_id')) if (run and show_support_control) else ''
    if not run: return ''
    if run.get('execution_mode') == DUAL_SPEED_FINANCIAL_INTELLIGENCE_MODE:
        return _render_dual_speed_outcome(run, show_support_control=show_support_control)
    if run.get('extraction_mode') == 'structured_standard_financials' and run.get('status') == 'structured_source_unavailable':
        support = run.get('support_reference') or _support_reference(run)
        counts = run.get('candidate_lifecycle_counts') or {}
        return f"""<section class='card'><h2>Structured financial source unavailable</h2><p>Flora could not find or access a governed structured filing for this enterprise and reporting period. The existing trusted Financial Twin was not changed.</p><p>Extraction mode: {escape(str(run.get('extraction_mode_label') or 'Structured standard financials'))} · AI calls made: {escape(str(run.get('ai_calls_made', 0)))} · PDF fallback calls made: {escape(str(run.get('pdf_fallback_calls_made', 0)))}</p><p>Candidate facts extracted: {escape(str(counts.get('packet_candidates_extracted', len(run.get('claims', [])))))} · Canonical facts accepted: {escape(str(run.get('auto_accepted_count', 0)))} · Trusted twin changed: {'yes' if run.get('trusted_twin_changed') else 'no'} · Support reference: {escape(str(support))}</p><p><a href='/settings'>Configure governed structured financial source</a></p>{support_report_link}</section><section id='evidence' class='card'><h2>Evidence</h2><p>No structured financial evidence was returned.</p></section>{enterprise_memory_panel('bt-group-plc')}"""
    no_accept = run.get('status') == 'completed_with_no_accepted_intelligence'
    changes = ''.join(f"<li>{escape(_business_change_label(run, r))} — {escape(str(r.get('update_result')))}</li>" for r in run.get('applied_results', [])[:20]) or ('<li>Financial intelligence was updated. Some extracted facts require attention.</li>' if run.get('status') == 'completed_with_exceptions' else ('<li>Flora analysed the financial report, but no facts passed the governed acceptance rules.</li>' if no_accept else '<li>No financial intelligence was added because processing did not complete.</li>'))
    exceptions = _dedupe_exceptions(run.get('exceptions', []))
    if exceptions:
        specific = [e for e in exceptions if e.get('exception_type') not in {'provider_response_invalid','candidate_validation_failed'} or e.get('packet_id') or e.get('candidate_id') or e.get('claim_id')]
        if specific:
            exceptions = specific
    support = run.get('support_reference') or _support_reference(run)
    needs = ''.join(f"<li>{escape(str(e.get('user_message') or e.get('acceptance_reason') or e.get('rejection_reason') or 'Needs attention'))} Support reference: {escape(str(e.get('support_reference') or support))} — section {escape(str(e.get('packet_id') or 'n/a'))}</li>" for e in exceptions[:20]) or '<li>No exceptions requiring review.</li>'
    evidence = ''.join(f"<details><summary>{escape(str(c.get('metric_label') or c.get('metric_identity') or c.get('original_statement','')))} — {escape(str(c.get('original_display_value') or c.get('display_value') or c.get('value') or ''))} — {escape(str(c.get('period') or ''))} {escape(str(c.get('state') or ''))} — {escape(str(c.get('business_unit') or c.get('enterprise_scope') or ''))} — {escape(str(c.get('accounting_basis') or 'basis not resolved'))} — source page {escape(str(c.get('page_reference')))}</summary><p>Page {escape(str(c.get('page_reference')))} · Confidence {escape(str(c.get('confidence')))} · Evidence {escape(c.get('evidence_id',''))} · Normalised {escape(str(c.get('normalised_amount') or ''))}</p><p>{escape(str(c.get('source_excerpt') or ''))}</p></details>" for c in run.get('claims', [])[:20]) or '<p>No page-grounded claims returned.</p>'
    status = run.get('status','')
    headline = 'Complete' if status == 'completed' else ('Needs attention' if status == 'completed_with_exceptions' else ('No accepted intelligence' if status == 'completed_with_no_accepted_intelligence' else ('In progress' if status in {'queued','retrieving_source','selecting_sections','estimating_cost','analysing','validating','updating_memory'} else 'Failed')))
    cost_value = run.get('actual_cost_usd') if run.get('actual_cost_usd') is not None else run.get('estimated_cost_usd')
    cost_text = f" · Run cost: {escape(str(cost_value))} USD" if cost_value is not None else ''
    outcome = 'Financial intelligence was updated. Some extracted facts require attention.' if status == 'completed_with_exceptions' else ('Flora analysed the financial report, but no facts passed the governed acceptance rules.' if status == 'completed_with_no_accepted_intelligence' else ('maintained Enterprise Model financial attributes changed or strengthened; use this as a prompt for account planning, not as a standalone commercial conclusion.' if run.get('enterprise_attributes_changed') else 'No financial intelligence was added because processing did not complete.'))
    accepted_periods = [c.get('period') for c in run.get('claims', []) if c.get('disposition') == 'accepted' and c.get('period')]
    candidate_periods = [c.get('period') for c in run.get('claims', []) if c.get('period')]
    period_text = 'inferred from accepted facts' if accepted_periods else (f"detected from candidates ({escape(str(candidate_periods[0]))})" if candidate_periods else 'not established')
    support_link = f" · <a class='support-report-link' href='/financial-intelligence/{escape(run['run_id'])}/support-report'>Download support report</a>" if show_support_control else ''
    return f"""<section class='card'><h2>Refresh outcome</h2><p>Extraction mode: {escape(str(run.get('extraction_mode_label') or run.get('extraction_mode') or 'AI financial report review'))} · AI calls made: {escape(str(run.get('ai_calls_made', run.get('openai_calls_made', 0))))}</p><p>{headline}{cost_text} · Candidate facts extracted: {(run.get('candidate_lifecycle_counts') or {}).get('packet_candidates_extracted', len(run.get('claims', [])))} · Reporting period: {period_text} · Collection status: {escape(status)} · Collected: {escape(run.get('collection',{}).get('retrieval_time',''))}</p><div class='grid'><div><div class='metric'>{run.get('auto_accepted_count',0)}</div><p>Canonical facts accepted</p></div><div><div class='metric'>{run.get('observations_created_or_strengthened',0)}</div><p>New or strengthened Observations</p></div><div><div class='metric'>{len([r for r in run.get('applied_results',[]) if r.get('contradiction')])}</div><p>Contradictions</p></div><div><div class='metric'>{len(exceptions)}</div><p>Needs Attention</p></div></div><p><a href='/financial-intelligence/{escape(run['run_id'])}'>View financial changes</a> · <a href='/financial-intelligence/{escape(run['run_id'])}#evidence'>View supporting evidence</a> · <a href='/financial-intelligence/{escape(run['run_id'])}#attention'>Review exceptions</a>{support_link}</p></section><section class='card'><h2>What changed</h2><ul>{changes}</ul></section><section class='card'><h2>Why it matters</h2><p><strong>Outcome:</strong> {escape(str(run.get('no_new_evidence_message') or outcome))}</p>{("<p><a href='/digital-twin/bt-group-plc'>View updated twin</a> · <a href='#attention'>Review exception</a> · <a href='#evidence'>View evidence</a></p>" if status == 'completed_with_exceptions' and run.get('enterprise_attributes_changed') else "<form method='post' action='/financial-intelligence/bt-group-plc/refresh'><button>Retry</button></form>")}</section><section id='attention' class='card'><h2>What needs attention</h2><ul>{needs}</ul></section><section id='evidence' class='card'><h2>Evidence</h2>{evidence}</section>{enterprise_memory_panel('bt-group-plc')}"""

def missing_run_page(run_id: str) -> str:
    body = f"""<section class='hero'><h1>Financial Intelligence</h1><p>This previous refresh result is no longer available.</p><p>Start a new refresh to collect the latest financial intelligence.</p><form method='post' action='/financial-intelligence/bt-group-plc/refresh'><button>Start new refresh</button></form><p><a href='/financial-intelligence'>Return to Financial Intelligence</a></p></section>"""
    return _page('Financial Intelligence result unavailable', body)

def financial_intelligence_run_page(run_id: str) -> str:
    try:
        return _page('Financial Intelligence outcome', _outcome_summary(load_run(run_id)))
    except FileNotFoundError:
        print(f"Flora Financial Intelligence requested missing run {run_id}; storage mode={storage_mode()['mode']}")
        return missing_run_page(run_id)

def financial_intelligence_run_response(run_id: str, show_support_control: bool = True) -> tuple[str, int]:
    try:
        return _page('Financial Intelligence outcome', _outcome_summary(load_run(run_id), show_support_control=show_support_control)), 200
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
