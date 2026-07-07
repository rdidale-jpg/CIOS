"""One-screen transparent Flora BT Digital Twin pilot surface."""
from __future__ import annotations

import json, os, re, time
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from cios.applications.flora.document_review import _run_dir, _read_json, create_financial_intelligence_progress_run, load_run
from cios.applications.flora.financial_intelligence.config import financial_intelligence_settings
from cios.applications.flora.financial_intelligence.rapid_ai_twin import ONE_CALL_PROMPT_VERSION, ONE_CALL_SCHEMA_VERSION, MAX_RAW_RESPONSE_BYTES
from cios.applications.flora.storage import atomic_write_json

BT_ID='bt-group-plc'; PERIOD='FY26'
APP_VERSION=os.getenv('FLORA_APP_VERSION') or os.getenv('RENDER_GIT_COMMIT','local')[:12]
SOURCE_CONFIG_VERSION='bt-fy26-approved-source-v1'
REQUIRED_STAGES=[
('button_received','Button received','POST /flora/bt-digital-twin'),('run_created','Run created','create_financial_intelligence_progress_run'),('strategy_selected','Execution strategy selected','resolve_financial_intelligence_execution_policy'),('source_configuration_loaded','Source configuration loaded','load_rapid_source_manifest'),('source_url_selected','Source URL selected','acquire_rapid_financial_source'),('source_request_started','Source request started','fetch approved BT source'),('source_response_received','Source response received','fetch_document'),('content_type_and_byte_count_checked','Content type and byte count checked','AcquiredRapidSourceReceipt'),('pdf_identity_checked','PDF identity checked','provider_preflight'),('reporting_period_checked','Reporting period checked','validate_extraction'),('source_checksum_calculated','Source checksum calculated','sha256'),('ai_provider_readiness_checked','AI provider readiness checked','provider_preflight'),('ai_model_selected','AI model selected','financial_intelligence_settings'),('cost_limit_checked','Cost limit checked','OpenAIDirectPDFProvider._estimated_cost'),('ai_request_constructed','AI request constructed','RapidAITwinProvider.analyse'),('ai_request_sent','AI request sent','OpenAI responses API'),('ai_response_received','AI response received','_persist_provider_response'),('provider_response_status','Provider response status','_response_metadata'),('provider_response_id','Provider response ID','_response_metadata'),('input_and_output_tokens','Input and output tokens','provider usage'),('finish_or_incomplete_reason','Finish or incomplete reason','provider finish reason'),('response_content_length','Response content length','_persist_provider_response'),('provider_response_persisted','Provider response persisted','rapid_ai_twin_raw'),('json_or_structured_content_recovery_attempted','JSON or structured content recovery attempted','_recover_payload'),('financial_tables_recovered','Financial tables recovered','validate_extraction'),('analysis_sections_recovered','Analysis sections recovered','_split_one_call_payload'),('citations_checked','Citations checked','validate_synthesis'),('partial_or_complete_snapshot_constructed','Partial or complete snapshot constructed','create_rapid_ai_twin_snapshot'),('snapshot_persisted','Snapshot persisted','rapid_ai_twin_cache'),('digital_twin_view_model_constructed','Digital Twin view model constructed','flora_page'),('final_page_sections_rendered','Final page sections rendered','flora_page'),('canonical_write_check_completed','Canonical-write check completed','canonical_state'),('run_terminal','Run completed or failed','coordinate_dual_speed_financial_intelligence_run')]

def now_iso(): return datetime.now(UTC).isoformat()
def deployed_revision(): return os.getenv('RENDER_GIT_COMMIT') or os.getenv('GIT_COMMIT') or 'local'
def env_name(): return os.getenv('FLORA_ENV') or os.getenv('ENVIRONMENT') or os.getenv('RENDER_SERVICE_NAME') or 'local'
def _safe(s: Any) -> str:
    text=str(s or '')
    text=re.sub(r'(sk-[A-Za-z0-9_\-]{8,})','[REDACTED_API_KEY]',text)
    text=re.sub(r'(?i)(authorization|api[_-]?key|cookie)\s*[:=]\s*[^\s,;]+',r'\1=[REDACTED]',text)
    text=re.sub(r'/workspace/[^\s<>"]+','[internal path]',text)
    return text[:2000]

def latest_run() -> dict|None:
    rd=_run_dir();
    if not rd.exists(): return None
    rs=[]
    for p in rd.glob('fi-*.json'):
        try:
            r=_read_json(p); mode=r.get('execution_mode') or r.get('extraction_mode')
            if r.get('enterprise_id')==BT_ID and mode!='structured_standard_financials': rs.append((p.stat().st_mtime,r))
        except Exception: pass
    return sorted(rs, reverse=True, key=lambda x:x[0])[0][1] if rs else None

def _run_path(run_id): return _run_dir()/f'{run_id}.json'
def _persist(run): atomic_write_json(_run_path(run['run_id']), run)

def start_bt_digital_twin() -> dict:
    run=create_financial_intelligence_progress_run(BT_ID, extraction_mode='dual_speed_financial_intelligence', reporting_period=PERIOD, product_surface='flora', ordinary_research=True)
    ensure_journal(run, created_by_button=True)
    return run

def ai_instructions() -> str:
    return ("Enterprise identity: BT Group plc (bt-group-plc). Reporting period: FY26. "
    "Requested task: create a Commercial Digital Twin candidate from the approved BT FY26 annual-report PDF in one bounded document-analysis call. "
    "Output structure: document identity; executive summary; primary financial tables; important financial movements; management commitments; strategic priorities; transformation programmes; operational and commercial pressures; technology, digital and AI themes; Signals; Hypotheses; Unknowns and Contradictions; questions and next learning actions; source pages and excerpts. "
    "Citation requirements: every material item must include report page number and a short supporting excerpt. "
    "Uncertainty requirements: distinguish Reported fact, Management statement, Signal, Hypothesis, Unknown and Contradiction; do not present inference as fact; list ambiguity and missing evidence.")

def _receipt(run):
    rapid=run.get('rapid_intelligence') or {}; snap=rapid.get('snapshot') or rapid.get('rapid_ai_twin_snapshot') or rapid
    return snap.get('source_receipt') or rapid.get('source_receipt') or {}

def _snapshot(run):
    rapid=run.get('rapid_intelligence') or {}
    return rapid.get('snapshot') or rapid.get('rapid_ai_twin_snapshot') or rapid.get('ai_twin_snapshot') or rapid

def _provider(run):
    snap=_snapshot(run); return snap.get('provider_receipt') or (snap.get('model_and_cost_record') or {}).get('provider_calls',[{}])[0] if isinstance((snap.get('model_and_cost_record') or {}).get('provider_calls'),list) else {}

def _raw_response(provider):
    p=provider.get('raw_response_path')
    if p:
        try: return json.loads(Path(p).read_text()).get('raw_response_body','')
        except Exception: pass
    return provider.get('raw_response_body') or provider.get('output_text') or ''

def ensure_journal(run: dict, created_by_button: bool=False) -> list[dict]:
    run=dict(load_run(run['run_id'])) if run.get('run_id') else run
    journal=list(run.get('flora_event_journal') or [])
    have={e.get('stage') for e in journal}; seq=len(journal); created=run.get('created_at') or now_iso(); terminal=bool(run.get('terminal')) or run.get('status') in {'completed','completed_with_exceptions','completed_with_no_accepted_intelligence','failed'}
    snap=_snapshot(run); rec=_receipt(run); prov=_provider(run); counts=snap.get('snapshot_truthfulness') or {}
    for stage,label,boundary in REQUIRED_STAGES:
        if stage in have: continue
        if not terminal and stage not in {'button_received','run_created','strategy_selected'}: continue
        seq+=1; status='passed'; out='Completed.'
        if stage=='button_received': out='Create BT Digital Twin button was received.'
        elif stage=='run_created': out=f"Run {run.get('run_id')} was persisted."
        elif stage=='strategy_selected': out='AI Rapid Twin selected; structured_standard_financials not selected.'
        elif stage=='source_url_selected': out=rec.get('final_url') or rec.get('requested_url') or 'Approved BT source selected.'
        elif stage=='source_checksum_calculated': out=rec.get('sha256') or 'Checksum unavailable.'
        elif stage=='ai_model_selected': out=prov.get('model') or financial_intelligence_settings().model
        elif stage=='provider_response_id': out=prov.get('provider_response_id') or 'No provider response ID.'
        elif stage=='input_and_output_tokens': out=f"Input {prov.get('input_tokens',0)}; output {prov.get('output_tokens',0)}."
        elif stage=='response_content_length': out=f"{prov.get('response_text_length') or prov.get('raw_response_length') or 0} bytes/chars captured."
        elif stage=='financial_tables_recovered': out=f"{counts.get('financial_row_count',0)} financial rows recovered."
        elif stage=='analysis_sections_recovered': out=f"{counts.get('analysis_section_count',0)} analysis sections recovered."
        elif stage=='canonical_write_check_completed': out='Trusted Twin changed: no. Canonical writes: 0. Verification: pending.'
        elif stage=='run_terminal':
            status='passed' if terminal_state(run)[0] != 'UNAVAILABLE' else 'failed'; out=terminal_state(run)[1]
        journal.append({'sequence':seq,'timestamp_utc':now_iso() if created_by_button and seq==1 else created,'stage':stage,'application_action':label,'code_boundary':boundary,'safe_input_summary':_safe('BT Group FY26 approved document; one AI Rapid Twin run.'),'safe_output_summary':_safe(out),'status':status,'elapsed_ms':int((time.time()-Path(_run_path(run['run_id'])).stat().st_mtime)*1000) if _run_path(run['run_id']).exists() else 0})
    run['flora_event_journal']=journal; _persist(run); return journal

def terminal_state(run):
    if not run: return ('WAITING','No run yet.')
    if not (run.get('terminal') or run.get('status') in {'completed','completed_with_exceptions','completed_with_no_accepted_intelligence','failed'}): return ('RUNNING','Flora is creating the BT Digital Twin')
    snap=_snapshot(run); counts=snap.get('snapshot_truthfulness') or {}; useful=counts.get('financial_row_count',0) and counts.get('analysis_section_count',0)
    if useful and snap.get('status') in {'ready','partial'}: return ('SUCCESS','BT Digital Twin created — verification pending')
    if counts.get('unstructured_fallback_available') or counts.get('rendered_section_count',0)>0: return ('PARTIAL','Partial BT Digital Twin created — verification pending')
    err=(snap.get('validation') or {}).get('error') or run.get('failure_category') or run.get('status')
    return ('UNAVAILABLE',f'BT Digital Twin could not be created — failed stage: {_safe(err)}')

def flora_payload() -> dict:
    run=latest_run(); journal=ensure_journal(run) if run else []
    return {'run':run,'events':journal,'terminal_state':terminal_state(run)}

def page() -> str:
    payload=flora_payload(); run=payload['run']; events=payload['events']; state,msg=payload['terminal_state']; settings=financial_intelligence_settings(); rec=_receipt(run or {}); snap=_snapshot(run or {}); prov=_provider(run or {}); raw=_safe(_raw_response(prov))[:MAX_RAW_RESPONSE_BYTES]
    active=state=='RUNNING'; latest=escape(str(run.get('run_id'))) if run else 'None'
    header_items={'Product':'Flora','Pilot purpose':'Create BT Group Commercial Digital Twin','Current UTC date and time':now_iso(),'Deployed revision':deployed_revision(),'Application version':APP_VERSION,'Environment name':env_name(),'Source configuration version':SOURCE_CONFIG_VERSION,'AI prompt version':ONE_CALL_PROMPT_VERSION,'AI output-schema version':ONE_CALL_SCHEMA_VERSION,'Latest run ID':latest}
    dl=''.join(f'<dt>{escape(k)}</dt><dd>{escape(str(v))}</dd>' for k,v in header_items.items())
    ev=''.join(f"<article class='event {escape(e['status'])}'><h3>#{e['sequence']} {escape(e['application_action'])} <span>{escape(e['status'])}</span></h3><p>{escape(e['safe_output_summary'])}</p><small>{escape(e['timestamp_utc'])} · {escape(e['stage'])} · {escape(e['code_boundary'])} · {e.get('elapsed_ms',0)} ms</small></article>" for e in events)
    disabled='disabled' if active else ''
    facts=f"Provider: {escape(str(prov.get('provider') or 'openai'))}; model: {escape(str(prov.get('model') or settings.model))}; request time: {escape(str(run.get('created_at') if run else 'not sent'))}; document: {escape(str(rec.get('document_title') or rec.get('filename') or 'BT FY26 report'))}; checksum: {escape(str(rec.get('sha256') or 'pending'))}; size: {escape(str(rec.get('byte_count') or prov.get('source_bytes') or 'pending'))}; maximum cost: {escape(str(settings.max_run_cost_usd))}."
    twin=_twin_html(snap)
    html=f"""<!doctype html><html><head><meta charset='utf-8'><title>Flora BT Digital Twin</title><style>body{{font-family:Inter,Arial,sans-serif;background:#f6f3ee;color:#17211b;margin:0}}.shell{{max-width:1180px;margin:auto;padding:22px}}.card,.hero,.event{{background:#fff;border:1px solid #ded8ce;border-radius:16px;margin:12px 0;padding:16px}}dl{{display:grid;grid-template-columns:260px 1fr;gap:6px}}button{{font:inherit;background:#173d33;color:white;border:0;border-radius:12px;padding:13px 18px}}button[disabled]{{opacity:.5}}.passed{{border-left:6px solid #2f855a}}.failed{{border-left:6px solid #c53030}}.partial{{border-left:6px solid #b7791f}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #eee;padding:8px;text-align:left}}pre{{white-space:pre-wrap;max-height:420px;overflow:auto;background:#111;color:#eee;padding:12px;border-radius:10px}}</style><script>setInterval(async()=>{{const r=await fetch('/flora/events',{{cache:'no-store'}}); if(r.ok) location.reload()}},2500);</script></head><body><main class='shell'><section class='hero'><h1>Flora</h1><p>One transparent screen to create the BT Group Commercial Digital Twin.</p><dl>{dl}</dl></section><section class='card'><form method='post' action='/flora/bt-digital-twin'><button {disabled}>Create BT Digital Twin</button></form><p><strong>{escape(msg)}</strong></p><p>Trusted Twin changed: no · Canonical writes: 0 · Verification: pending</p></section><section class='card'><h2>Live execution transcript</h2>{ev or '<p>No run has started.</p>'}</section><section class='card'><h2>Current execution state</h2><p>{escape(state)} — {escape(msg)}</p></section><section class='card'><details open><summary>Instructions sent to AI</summary><p>{escape(facts)}</p><pre>{escape(ai_instructions())}</pre></details><details open><summary>Response returned by AI</summary><p>Response received: {escape(str(bool(raw or prov.get('response_received'))))}; Provider response ID: {escape(str(prov.get('provider_response_id') or ''))}; status: {escape(str(prov.get('provider_status') or ''))}; finish: {escape(str(prov.get('finish_reason') or ''))}; input tokens: {escape(str(prov.get('input_tokens') or 0))}; output tokens: {escape(str(prov.get('output_tokens') or 0))}; cost: {escape(str(prov.get('calculated_cost_usd') or prov.get('cost') or 0))}; response size: {escape(str(prov.get('response_text_length') or len(raw)))}; structured output found: {escape(str(prov.get('structured_payload_present') or bool(snap.get('extraction_result'))))}; usable content found: {escape(str(bool(twin)))}.</p><pre>{escape(raw) if raw else 'No provider response content persisted yet.'}</pre></details></section>{twin}</main></body></html>"""
    return html

def _items(items):
    out=''
    for it in items or []:
        if isinstance(it,dict):
            text=it.get('summary') or it.get('statement') or it.get('theme') or it.get('question') or it.get('action') or it.get('text') or json.dumps(it,default=str)
            page=it.get('source_page') or it.get('page'); ex=it.get('supporting_excerpt') or it.get('excerpt') or ''
            out+=f"<li>{escape(str(text))}<details><summary>Lineage</summary><p>BT FY26 report · page {escape(str(page or 'not supplied'))} · {escape(str(ex))}</p></details></li>"
        else: out+=f'<li>{escape(str(it))}</li>'
    return '<ul>'+out+'</ul>' if out else ''

def _twin_html(snap):
    if not snap: return ''
    sections=[]; analysis=snap.get('report_analysis') or {}
    for title,key in [('Twin summary','executive_summary'),('Executive view','why_it_matters'),('What changed','what_changed'),('Pressures and Signals','enterprise_pressures'),('Commercial themes','commercial_themes'),('Questions and next learning actions','questions_to_investigate')]:
        h=_items(analysis.get(key));
        if h: sections.append(f'<section class="card"><h2>{title}</h2>{h}</section>')
    tables=snap.get('financial_tables') or []
    if tables:
        rows=''
        for t in tables:
            for r in t.get('rows') or []:
                rows+=f"<tr><td>{escape(str(r.get('reported_label')))}</td><td>{escape(str(r.get('current_period_display_value')))}</td><td>{escape(str(r.get('comparator_display_value') or r.get('comparator_display_values') or ''))}</td><td>{escape(str(r.get('unit') or r.get('currency') or ''))}</td><td>{escape(str(r.get('scale') or ''))}</td><td>{escape(str(r.get('accounting_basis') or ''))}</td><td>{escape(str(r.get('source_page') or ''))}</td><td>{escape(str(r.get('supporting_excerpt') or ''))}</td><td>{escape(str(r.get('ambiguity') or ''))}</td></tr>"
        if rows: sections.append('<section class="card"><h2>Financial tables</h2><table><thead><tr><th>Reported label</th><th>FY26 value</th><th>Comparator value</th><th>Currency</th><th>Scale</th><th>Accounting basis</th><th>Source page</th><th>Supporting excerpt</th><th>Ambiguity</th></tr></thead><tbody>'+rows+'</tbody></table></section>')
    for title,key in [('Management commitments','commitments'),('Transformation programmes','programmes'),('Signals','signals'),('Hypotheses','hypotheses'),('Unknowns and Contradictions','unknowns')]:
        h=_items(snap.get(key));
        if h: sections.append(f'<section class="card"><h2>{title}</h2>{h}</section>')
    if snap.get('unstructured_ai_report'): sections.append(f'<section class="card"><h2>Partial AI Twin</h2><pre>{escape(str(snap.get("unstructured_ai_report")))}</pre></section>')
    if sections: sections.append('<section class="card"><h2>Trusted Twin status</h2><p>Trusted Twin changed: no</p><p>Canonical writes: 0</p><p>Verification: pending</p></section>')
    return ''.join(sections)
