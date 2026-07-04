"""AI document-understanding review workflow for Flora financial reports."""
from __future__ import annotations

import hashlib, json, os, shutil, uuid
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from experiments.document_understanding.providers import OpenAIDirectPDFProvider
from experiments.document_understanding.schema import ExperimentDocument, FoundationFact
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.memory.views import enterprise_memory_panel
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.workspace.views import _page

REVIEW_DIR = Path('.flora_pilot/ai_financial_reports')
UPLOAD_DIR = REVIEW_DIR / 'uploads'
RUN_DIR = REVIEW_DIR / 'runs'
DEFAULT_MODEL = os.getenv('FLORA_DOCUMENT_UNDERSTANDING_MODEL', 'gpt-5.5')


def now_iso() -> str: return datetime.now(UTC).isoformat(timespec='seconds')

def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))

def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f'.{path.name}.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)

def _run_path(run_id: str) -> Path: return RUN_DIR / f'{run_id}.json'

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

def create_upload_run(pdf_path: Path, *, enterprise_id: str = 'bt-group-plc', title: str = 'BT Group plc Annual Report 2026', source_url: str = 'uploaded authoritative PDF') -> dict[str, Any]:
    run_id = 'air-' + uuid.uuid4().hex[:12]
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    checksum = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    stored = UPLOAD_DIR / f'{checksum[:16]}.pdf'
    if pdf_path.resolve() != stored.resolve(): shutil.copyfile(pdf_path, stored)
    document = ExperimentDocument(document_id='DOC-' + checksum[:16].upper(), enterprise_id=canonical_enterprise_id(enterprise_id) or enterprise_id, title=title, source_url=source_url, retrieval_timestamp=now_iso(), checksum=checksum, media_type='application/pdf', page_count=1, local_path=str(stored))
    provider = OpenAIDirectPDFProvider(model=DEFAULT_MODEL)
    extraction = provider.extract_facts(document)
    claims = [fact_to_review_claim(f, run_id) for f in extraction.facts]
    run = {'run_id': run_id, 'created_at': now_iso(), 'status': 'ready_for_review' if claims else extraction.status, 'document': document.model_dump(), 'provider': extraction.provider, 'model': extraction.model, 'provider_status': extraction.status, 'provider_errors': extraction.provider_errors, 'raw_response_location': extraction.raw_response_location, 'claims': claims, 'applied_results': []}
    _write_json(_run_path(run_id), run)
    return run

def load_run(run_id: str) -> dict[str, Any]: return _read_json(_run_path(run_id))

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
    notice = f"<p class='pill'>{escape(message)}</p>" if message else ''
    body = f"""<section class='hero'><h1>AI Financial Report Review</h1><p>Upload an authoritative enterprise financial-report PDF. Flora sends the PDF to a genuine AI document-understanding model, returns strict page-grounded claims for review, and only accepted claims update Observation memory and the Commercial Digital Twin.</p>{notice}</section><section class='card action'><h2>Golden acceptance document</h2><p>Default enterprise: BT Group plc · expected document: BT Group Annual Report 2026.</p><form method='post' action='/ai-financial-report/upload' enctype='multipart/form-data'><label>Enterprise</label><input name='enterprise_id' value='bt-group-plc'><label>Report title</label><input name='title' value='BT Group plc Annual Report 2026'><label>Source URL or citation</label><input name='source_url' value='https://www.bt.com/about/annual-reports/2026summary/assets/files/BT-Annual-Report-2026.pdf'><label>PDF</label><input type='file' name='pdf' accept='application/pdf'><p><button>Process with AI document understanding</button></p></form></section>"""
    return _page('AI Financial Report Review', body)

def run_page(run_id: str) -> str:
    run = load_run(run_id)
    rows = ''.join(_claim_row(c) for c in run.get('claims', [])) or '<tr><td colspan="7">No claims returned. Check provider status and errors below.</td></tr>'
    applied = ''.join(f"<li>{escape(r.get('observation_id',''))} → {escape(r.get('affected_attribute',''))} ({escape(r.get('update_result',''))})</li>" for r in run.get('applied_results', []))
    body = f"""<section class='hero'><h1>Review extracted factual claims</h1><p>Run {escape(run_id)} · Provider {escape(run.get('provider',''))} · Model {escape(run.get('model',''))} · Status {escape(run.get('provider_status',''))}</p><p class='muted'>{escape('; '.join(run.get('provider_errors') or []))}</p></section><form method='post' action='/ai-financial-report/{escape(run_id)}/review'><section class='card'><table><thead><tr><th>Decision</th><th>Claim</th><th>Amendment</th><th>Type</th><th>Page</th><th>Excerpt</th><th>Confidence</th></tr></thead><tbody>{rows}</tbody></table><p><button>Save review decisions</button></p></section></form><section class='card action'><form method='post' action='/ai-financial-report/{escape(run_id)}/apply'><button>Apply accepted claims to Commercial Digital Twin</button></form><ul>{applied or '<li>No Observations applied yet.</li>'}</ul></section>{enterprise_memory_panel(run['document']['enterprise_id'])}"""
    return _page('Review AI claims', body)

def _claim_row(c: dict[str, Any]) -> str:
    cid = escape(c['claim_id']); state = c.get('review_state','pending')
    opts = ''.join(f"<option value='{v}' {'selected' if state==v else ''}>{label}</option>" for v,label in [('pending','Pending'),('accept','Accept'),('amend','Amend'),('reject','Reject')])
    return f"<tr><td><select name='action_{cid}'>{opts}</select></td><td>{escape(c['original_statement'])}</td><td><textarea name='amended_{cid}'>{escape(c.get('amended_statement',''))}</textarea></td><td>{escape(c['claim_type'])}</td><td>{escape(str(c.get('page_reference')))}</td><td>{escape(str(c.get('source_excerpt'))[:220])}</td><td>{c.get('confidence')}</td></tr>"
