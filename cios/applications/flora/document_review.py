"""AI document-understanding review workflow for Flora financial reports."""
from __future__ import annotations

from cios.applications.flora.storage import PersistenceError, atomic_write_json, data_path, ensure_writable_dir, storage_mode

import hashlib, json, os, shutil, time, uuid
from types import SimpleNamespace
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from experiments.document_understanding.providers import OpenAIDirectPDFProvider
from experiments.document_understanding.schema import ExperimentDocument, FoundationFact
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
DEFAULT_MODEL = os.getenv('FLORA_DOCUMENT_UNDERSTANDING_MODEL', 'gpt-5.5')
BT_PROFILE = Path(__file__).resolve().parents[3] / 'config/flora/collection_profiles/bt-group-plc.json'
AUTO_ACCEPT_CONFIDENCE = int(os.getenv('FLORA_FINANCIAL_INTELLIGENCE_AUTO_ACCEPT_CONFIDENCE', '85'))

FAILURE_MESSAGES = {
    'source_retrieval_failed': 'Flora could not retrieve the financial report.',
    'source_not_pdf': 'Flora could not retrieve the financial report.',
    'provider_not_configured': 'Financial document understanding is temporarily unavailable.',
    'provider_authentication_failed': 'Financial document understanding is temporarily unavailable.',
    'provider_request_failed': 'Financial document understanding could not complete.',
    'provider_quota_exceeded': 'Financial document understanding could not complete.',
    'provider_model_unavailable': 'Financial document understanding could not complete.',
    'provider_file_upload_failed': 'Financial document understanding could not complete.',
    'provider_request_invalid': 'Financial document understanding could not complete.',
    'provider_timeout': 'Financial document understanding could not complete.',
    'provider_response_invalid': 'Financial document understanding could not complete.',
    'persistence_failed': 'Flora understood the report but could not save the results.',
}

def _failure_message(category: str) -> str:
    return FAILURE_MESSAGES.get(category, 'Financial document understanding is temporarily unavailable.')

def _provider_failure_category(extraction) -> str:
    if not extraction:
        return 'provider_request_failed'
    errors = '; '.join(getattr(extraction, 'provider_errors', []) or [])
    status = getattr(extraction, 'status', '')
    if status == 'not_executed' and 'OPENAI_API_KEY' in errors:
        return 'provider_not_configured'
    return {
        'authentication_failed': 'provider_authentication_failed',
        'quota_exceeded': 'provider_quota_exceeded',
        'model_unavailable': 'provider_model_unavailable',
        'file_upload_failed': 'provider_file_upload_failed',
        'invalid_request': 'provider_request_invalid',
        'timeout': 'provider_timeout',
        'invalid_response': 'provider_response_invalid',
    }.get(status, 'provider_response_invalid' if getattr(extraction, 'schema_errors', None) else 'provider_request_failed')

def _support_reference(run: dict[str, Any]) -> str:
    diagnostics = run.get('provider_diagnostics') or []
    correlation = diagnostics[-1].get('correlation_id') if diagnostics else run.get('run_id', '')
    return 'FI-' + str(correlation).replace('fi-', '').replace('FI-', '')

def _mark_failure(run: dict[str, Any], category: str, technical_reason: str) -> dict[str, Any]:
    run['status'] = category
    run['failure_category'] = category
    run['support_reference'] = _support_reference(run)
    base_message = _failure_message(category)
    if category.startswith('provider_') and category != 'provider_not_configured':
        base_message = 'Financial document understanding could not complete.'
    run['user_message'] = base_message
    run['user_message_display'] = f"{base_message} Support reference: {run['support_reference']}"
    run['exceptions'] = [{'exception_type': category, 'rejection_reason': technical_reason, 'user_message': run['user_message']}]
    run['auto_accepted_count'] = 0; run['exception_count'] = len(run['exceptions']); run['observations_created_or_strengthened'] = 0; run['enterprise_attributes_changed'] = []
    return run


def now_iso() -> str: return datetime.now(UTC).isoformat(timespec='seconds')

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
        'sanitised_provider_error_message': str(getattr(fetched, 'error', '') or '')[:700],
        'retryable': not bool(getattr(fetched, 'succeeded', False)),
        'elapsed_time': round(time.time() - started, 3),
    }

def _record_provider_diagnostics(run: dict[str, Any]) -> None:
    for event in run.get('provider_diagnostics') or []:
        print('Flora provider diagnostic ' + json.dumps(event, sort_keys=True))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))

def _write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_json(path, data)

def _run_path(run_id: str) -> Path: return _run_dir() / f'{run_id}.json'

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

def refresh_financial_intelligence(enterprise_id: str = 'bt-group-plc') -> dict[str, Any]:
    source = _bt_annual_report_source()
    run_id = 'fi-' + uuid.uuid4().hex[:12]
    ensure_writable_dir(_run_dir())
    retrieval_started = time.time()
    fetched = fetch_document(source['url'])
    doc_parse = parse_pdf_document(fetched, _source_obj(source), canonical_enterprise_id='bt-group-plc')
    document = ExperimentDocument(document_id=doc_parse.document_id, enterprise_id='bt-group-plc', title=source['source_name'], source_url=(fetched.final_url or source['url']), retrieval_timestamp=doc_parse.retrieval_date, checksum=doc_parse.checksum, media_type=doc_parse.media_type or 'application/pdf', page_count=max(doc_parse.page_count, 1), local_path=doc_parse.local_path)
    provider = OpenAIDirectPDFProvider(model=DEFAULT_MODEL)
    extraction = provider.extract_facts(document) if fetched.succeeded else None
    claims = [fact_to_review_claim(f, run_id) for f in (extraction.facts if extraction else [])]
    run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'processing', 'workflow': 'financial_intelligence', 'governed_source': source, 'collection': {'retrieved': fetched.succeeded, 'retrieval_time': fetched.retrieval_date, 'http_status': fetched.status_code, 'error': fetched.error, 'active_source_url': source['url'], 'document_size': len(fetched.content or b'')}, 'document': document.model_dump(), 'provider': (extraction.provider if extraction else 'openai'), 'model': (extraction.model if extraction else DEFAULT_MODEL), 'provider_status': (extraction.status if extraction else 'not_executed'), 'provider_errors': (extraction.provider_errors if extraction else [fetched.error]), 'raw_response_location': (extraction.raw_response_location if extraction else None), 'provider_diagnostics': (getattr(extraction, 'diagnostics', []) if extraction else [_safe_provider_diagnostic(run_id, source, fetched, DEFAULT_MODEL, retrieval_started)]), 'openai_invoked': bool(extraction), 'claims': claims, 'applied_results': []}
    run['collection'].update({'final_url': fetched.final_url or fetched.url, 'content_type': fetched.media_type, 'redirect_chain': list(fetched.redirect_chain), 'redirected': bool(fetched.redirect_chain)})
    if extraction:
        run['provider_diagnostics'] = [_safe_provider_diagnostic(run_id, source, fetched, DEFAULT_MODEL, retrieval_started)] + run.get('provider_diagnostics', [])
    if not fetched.succeeded:
        run = _mark_failure(run, 'source_retrieval_failed', fetched.error or 'governed source retrieval failed')
    elif document.media_type != 'application/pdf':
        run = _mark_failure(run, 'source_not_pdf', doc_parse.error or f"source returned {document.media_type}")
    elif extraction and extraction.status == 'completed':
        try:
            run = _apply_automatic_claims(run)
        except Exception as exc:
            run = _mark_failure(run, 'persistence_failed', f'{type(exc).__name__}: {exc}')
    else:
        run = _mark_failure(run, _provider_failure_category(extraction), '; '.join(run.get('provider_errors') or ['provider did not complete']))
    _record_provider_diagnostics(run)
    try:
        _write_json(_run_path(run_id), run)
    except PersistenceError as exc:
        run = _mark_failure(run, 'persistence_failed', f'{type(exc).__name__}: {exc}')
    return run

def create_upload_run(pdf_path: Path, *, enterprise_id: str = 'bt-group-plc', title: str = 'BT Group plc Annual Report 2026', source_url: str = 'uploaded authoritative PDF') -> dict[str, Any]:
    run_id = 'air-' + uuid.uuid4().hex[:12]
    ensure_writable_dir(_upload_dir())
    checksum = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    stored = _upload_dir() / f'{checksum[:16]}.pdf'
    if pdf_path.resolve() != stored.resolve(): shutil.copyfile(pdf_path, stored)
    document = ExperimentDocument(document_id='DOC-' + checksum[:16].upper(), enterprise_id=canonical_enterprise_id(enterprise_id) or enterprise_id, title=title, source_url=source_url, retrieval_timestamp=now_iso(), checksum=checksum, media_type='application/pdf', page_count=1, local_path=str(stored))
    provider = OpenAIDirectPDFProvider(model=DEFAULT_MODEL)
    extraction = provider.extract_facts(document)
    claims = [fact_to_review_claim(f, run_id) for f in extraction.facts]
    run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'ready_for_review' if claims else extraction.status, 'document': document.model_dump(), 'provider': extraction.provider, 'model': extraction.model, 'provider_status': extraction.status, 'provider_errors': extraction.provider_errors, 'raw_response_location': extraction.raw_response_location, 'provider_diagnostics': getattr(extraction, 'diagnostics', []), 'claims': claims, 'applied_results': []}
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
    provider_ready = bool(os.getenv('OPENAI_API_KEY'))
    provider_state = 'Available: OpenAI document-understanding credentials are configured.' if provider_ready else 'Unavailable until configured: OPENAI_API_KEY is not set. You can still open this workflow, select an enterprise and prepare the report; processing will show a clear provider configuration error instead of hiding the product capability.'
    notice = f"<p class='pill'>{escape(message)}</p>" if message else ''
    body = f"""<section class='hero'><h1>AI Financial Report Review</h1><p>Upload an authoritative enterprise financial-report PDF. Flora sends the PDF to a genuine AI document-understanding model, returns strict page-grounded claims for review, and only accepted claims update Observation memory and the Commercial Digital Twin.</p>{notice}</section><section class='card'><h2>Provider status</h2><p>{escape(provider_state)}</p><p class='muted'>Provider route: OpenAI direct PDF · Model: {escape(DEFAULT_MODEL)} · The original PDF is sent to the model as a PDF input file when credentials are present.</p></section><section class='card action'><h2>Collect Financial Report</h2><p>Select an enterprise, add the governed annual report PDF, process it, then accept, amend or reject page-grounded candidate facts before they update Observations and the Commercial Digital Twin.</p><p>Default enterprise: BT Group plc · expected document: BT Group Annual Report 2026.</p><form method='post' action='/ai-financial-report/upload' enctype='multipart/form-data'><label>Enterprise</label><select name='enterprise_id'><option value='bt-group-plc'>BT Group plc</option></select><label>Report title</label><input name='title' value='BT Group plc Annual Report 2026'><label>Source URL or citation</label><input name='source_url' value='https://www.bt.com/about/annual-reports/2026summary/assets/files/BT-Annual-Report-2026.pdf'><label>PDF</label><input type='file' name='pdf' accept='application/pdf'><p><button>Process document</button></p></form></section>"""
    return _page('AI Financial Report Review', body)

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
    body = f"""<section class='hero'><h1>Financial Intelligence</h1><p>BT Commercial Digital Twin outcome view. Flora collects the governed annual report, understands the financial facts, updates Observations and the Enterprise Model, then shows what changed and what needs attention.</p>{notice}<p class='pill'>{escape(state)}</p></section><section class='card action'><h2>Active governed source</h2><p><strong>{escape(source['source_name'])}</strong></p><p><a href='{escape(source['url'])}'>{escape(source['url'])}</a></p><p class='muted'>Source is registered in the BT collection profile and collected server-side; no download or upload is required.</p><form method='post' action='/financial-intelligence/bt-group-plc/refresh'><button>Refresh Financial Intelligence</button></form></section>{summary}<details class='card'><summary><strong>Administrative fallback only</strong></summary><p>Use only when governed automatic collection cannot retrieve a replacement report. This is not the BT sales-user workflow.</p><form method='post' action='/ai-financial-report/upload' enctype='multipart/form-data'><input type='hidden' name='enterprise_id' value='bt-group-plc'><input type='hidden' name='title' value='BT Group plc Annual Report 2026'><input type='hidden' name='source_url' value='{escape(source['url'])}'><input type='file' name='pdf' accept='application/pdf'><button>Admin fallback upload</button></form></details>"""
    return _page('Financial Intelligence', body)

def _outcome_summary(run: dict[str, Any] | None) -> str:
    if not run: return ''
    changes = ''.join(f"<li>{escape(str(r.get('affected_attribute')))} — {escape(str(r.get('update_result')))}</li>" for r in run.get('applied_results', [])[:20]) or '<li>No financial intelligence was added because processing did not complete.</li>'
    needs = ''.join(f"<li>{escape(str(run.get('user_message_display') or e.get('user_message') or e.get('acceptance_reason') or e.get('rejection_reason')))} — page {escape(str(e.get('page_reference') or e.get('page') or e.get('document_page') or 'n/a'))}</li>" for e in run.get('exceptions', [])[:20]) or '<li>No exceptions requiring review.</li>'
    evidence = ''.join(f"<details><summary>{escape(c.get('original_statement',''))}</summary><p>Page {escape(str(c.get('page_reference')))} · Confidence {escape(str(c.get('confidence')))} · Evidence {escape(c.get('evidence_id',''))}</p><p>{escape(str(c.get('source_excerpt') or ''))}</p></details>" for c in run.get('claims', [])[:20]) or '<p>No page-grounded claims returned.</p>'
    return f"""<section class='card'><h2>Refresh outcome</h2><p>Reporting period: inferred from accepted facts · Collection status: {escape(run.get('status',''))} · Collected: {escape(run.get('collection',{}).get('retrieval_time',''))}</p><div class='grid'><div><div class='metric'>{run.get('auto_accepted_count',0)}</div><p>Automatically accepted facts</p></div><div><div class='metric'>{run.get('observations_created_or_strengthened',0)}</div><p>New or strengthened Observations</p></div><div><div class='metric'>{len([r for r in run.get('applied_results',[]) if r.get('contradiction')])}</div><p>Contradictions</p></div><div><div class='metric'>{run.get('exception_count',0)}</div><p>Needs Attention</p></div></div><p><a href='/financial-intelligence/{escape(run['run_id'])}'>View financial changes</a> · <a href='/financial-intelligence/{escape(run['run_id'])}#evidence'>View supporting evidence</a> · <a href='/financial-intelligence/{escape(run['run_id'])}#attention'>Review exceptions</a></p></section><section class='card'><h2>What changed</h2><ul>{changes}</ul></section><section class='card'><h2>Why it matters</h2><p><strong>Outcome:</strong> {'maintained Enterprise Model financial attributes changed or strengthened; use this as a prompt for account planning, not as a standalone commercial conclusion.' if run.get('enterprise_attributes_changed') else 'No financial intelligence was added because processing did not complete.'}</p><form method='post' action='/financial-intelligence/bt-group-plc/refresh'><button>Retry</button></form></section><section id='attention' class='card'><h2>What needs attention</h2><ul>{needs}</ul></section><section id='evidence' class='card'><h2>Evidence</h2>{evidence}</section>{enterprise_memory_panel('bt-group-plc')}"""

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
