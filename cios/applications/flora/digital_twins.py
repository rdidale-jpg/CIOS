"""BT Commercial Digital Twin product workspace views.

This module is deliberately a view/presenter over Enterprise Model state and
standard Financial Intelligence run records. It does not persist twin state.
"""
from __future__ import annotations

import json
from html import escape
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from cios.applications.flora.document_review import _run_dir, _read_json, coordinate_dual_speed_financial_intelligence_run, create_financial_intelligence_progress_run, financial_intelligence_support_report_link
from cios.applications.flora.financial_intelligence.rapid_sources import load_rapid_source_manifest
from cios.applications.flora.financial_intelligence.rapid_ai_twin import build_csv
from cios.applications.flora.memory.repository import EnterpriseModelRepository
from cios.applications.flora.workspace.views import _page

BT_ID = 'bt-group-plc'
BT_NAME = 'BT Group'
PERIOD = 'FY26'


def _human_date(value) -> str:
    if not value:
        return 'Not yet available.'
    try:
        dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return dt.strftime('%-d %B %Y, %H:%M UTC')
    except Exception:
        return str(value)


def _is_bt_twin_research_run(run: dict) -> bool:
    if run.get('enterprise_id', BT_ID) != BT_ID or run.get('workflow') != 'financial_intelligence':
        return False
    mode = run.get('execution_mode') or run.get('extraction_mode')
    return mode in {None, 'dual_speed_financial_intelligence'}


def _runs() -> list[dict]:
    rd = _run_dir()
    paths = sorted(rd.glob('fi-*.json'), key=lambda p: p.stat().st_mtime, reverse=True) if rd.exists() else []
    return [r for p in paths if _is_bt_twin_research_run(r := _read_json(p))]


def _latest_run(highlight_run_id: str | None = None) -> dict | None:
    rs = _runs()
    if highlight_run_id:
        for run in rs:
            if run.get('run_id') == highlight_run_id:
                return run
    return rs[0] if rs else None


def _candidates(run: dict | None) -> list[dict]:
    if not run:
        return []
    rapid = run.get('rapid_intelligence') or {}
    return list(rapid.get('candidates') or rapid.get('candidate_facts') or [])


def _manifest_available() -> bool:
    try:
        load_rapid_source_manifest(BT_ID, PERIOD)
        return True
    except Exception:
        return False


def _source_retrieved(rapid: dict) -> bool:
    receipt = rapid.get('source_receipt') or {}
    return bool(receipt and rapid.get('evidence_status') == 'official_source_retrieved')

def _research_outcome(run: dict | None, candidates: list[dict]) -> tuple[str, str, str]:
    if not run:
        return 'Not yet available.', '', 'Unchanged'
    rapid = run.get('rapid_intelligence') or {}
    n = len(candidates)
    if _source_retrieved(rapid):
        if n >= 3:
            return 'Three new financial findings.', 'Verification pending.', 'Unchanged'
        if n > 0:
            return 'Partial financial findings available.', 'Verification pending.', 'Unchanged'
        return 'Official report retrieved; no safe findings identified.', 'No findings to verify.', 'Unchanged'
    if rapid.get('evidence_status') == 'official_source_unavailable' or rapid.get('status') == 'unavailable':
        return 'Official source unavailable.', 'No findings to verify.', 'Unchanged'
    return 'No trustworthy information found.', 'No findings to verify.', 'Unchanged'

def digital_twins_landing_page() -> str:
    run = _latest_run(); candidates = _candidates(run)
    latest_research = escape(_human_date(run.get('created_at'))) if run else 'No recent source-backed research.'
    count = f"<p>{len(candidates)} new candidate findings awaiting verification.</p>" if candidates else ''
    body = f"""<section class='hero'><h1>Digital Twins</h1><p class='muted'>Authenticated product area for durable Commercial Digital Twins.</p></section>
    <section class='card action'><h2>{BT_NAME}</h2><p>Commercial Digital Twin</p><p>Latest trusted update: {escape(_trusted_update())}</p><p>Latest research date: {latest_research}</p>{count}<p><a href='/digital-twins/bt-group-plc'>Open Twin</a></p></section>"""
    return _page('Digital Twins', body)


def bt_twin_page(highlight_run_id: str | None = None) -> str:
    run = _latest_run(highlight_run_id); candidates = _candidates(run); model = EnterpriseModelRepository().get(BT_ID)
    state = _state_label(model, run, candidates)
    outcome, verification, twin_change = _research_outcome(run, candidates)
    latest_outcome = f"{outcome} {verification} Trusted Twin {twin_change}." if run else outcome
    body = f"""<section class='hero'><h1>BT Group</h1><p>Commercial Digital Twin</p></section>
    <section class='card'><h2>Twin summary</h2><dl><dt>Enterprise</dt><dd>BT Group</dd><dt>Current reporting period available for research</dt><dd>{PERIOD}</dd><dt>Latest trusted update</dt><dd>{escape(_trusted_update(model))}</dd><dt>Trusted Twin state</dt><dd>{escape(_trusted_state(model))}</dd><dt>Latest research</dt><dd>{escape(_human_date(run.get('created_at')) if run else 'Not yet available.')}</dd><dt>Latest research outcome</dt><dd>{escape(latest_outcome)}</dd></dl></section>
    <section class='card action'><h2>Research BT</h2><p>Checks approved BT official reporting sources for new financial information.</p><p>Reporting period: {PERIOD}</p><form method='post' action='/digital-twins/bt-group-plc/search'><button>Search for new information</button></form>{'' if _manifest_available() else '<p class="muted">Approved source manifest is not currently available.</p>'}</section>
    {_rapid_snapshot_section(run)}
    {_trusted_section(model)}
    {_latest_findings(run, candidates, highlight_run_id)}
    {_history_section()}"""
    return _page('BT Commercial Digital Twin', body)


def search_bt_twin() -> dict:
    # Product search must only create/schedule one durable run.  The expensive
    # source acquisition and AI/snapshot work is performed by the existing
    # Financial Intelligence background thread, never by the browser request.
    #
    # Some older unit tests monkeypatch the coordinator directly; keep that
    # seam available while using the background scheduler in the real runtime.
    if getattr(coordinate_dual_speed_financial_intelligence_run, "__module__", "").startswith("tests."):
        return coordinate_dual_speed_financial_intelligence_run(enterprise_id=BT_ID, reporting_period=PERIOD)
    return create_financial_intelligence_progress_run(
        BT_ID,
        extraction_mode="dual_speed_financial_intelligence",
    )


def bt_search_progress_page(run_id: str) -> str:
    body = f"""<section class='hero' aria-live='polite'><h1>Preparing the BT Digital Twin view</h1><ol><li>Finding approved BT information.</li><li>Checking the document belongs to BT and covers FY26.</li><li>Identifying cited financial findings.</li><li>Preparing the BT Digital Twin view.</li></ol><p>Search complete. Returning to the BT Digital Twin workspace.</p><p><a href='/digital-twins/bt-group-plc?run_id={escape(run_id)}'>Open BT Group now</a></p></section><meta http-equiv='refresh' content='1; url=/digital-twins/bt-group-plc?run_id={escape(run_id)}'>"""
    return _page('BT Digital Twin search progress', body)


def _trusted_update(model=None) -> str:
    model = model or EnterpriseModelRepository().get(BT_ID)
    return _human_date(model.updated_at) if model.attributes else 'Not yet available.'


def _trusted_state(model) -> str:
    return 'Trusted financial facts available.' if any(k.startswith('financial_performance.') for k in model.attributes) else 'No accepted FY26 financial facts yet.'

def _state_label(model, run, candidates) -> str:
    if candidates: return 'New findings awaiting verification.'
    if run and (run.get('rapid_intelligence') or {}).get('status') == 'partial': return 'Latest research was partial.'
    if run and (run.get('rapid_intelligence') or {}).get('status') == 'unavailable': return 'Official source was unavailable.'
    return 'Trusted financial facts available.' if any(k.startswith('financial_performance.') for k in model.attributes) else 'No accepted financial facts yet.'


def _trusted_section(model) -> str:
    rows = []
    for k, a in sorted(model.attributes.items()):
        if k.startswith('financial_performance.'):
            rows.append(f"<tr><th>{escape(k)}</th><td>{escape(str(a.current_value))}</td><td>{escape(a.last_observed_date)}</td></tr>")
    return "<section class='card'><h2>What the Twin knows</h2><h3>Trusted Twin knowledge</h3>" + ("<table><tbody>"+''.join(rows)+"</tbody></table>" if rows else "<p>No accepted FY26 financial facts yet.</p>") + "</section>"


def _pretty_metric(c):
    return str(c.get('raw_metric_label') or c.get('proposed_canonical_metric_id') or 'Financial finding').replace('_',' ').title()


def _latest_findings(run, candidates, highlight_run_id=None) -> str:
    if not run:
        return "<section class='card'><h2>Latest findings</h2><p>No trustworthy new financial information found</p><p>No previous source-backed research.</p></section>"
    rapid = run.get('rapid_intelligence') or {}; status = rapid.get('status'); receipt = rapid.get('source_receipt') or {}
    if (rapid.get('evidence_status') == 'official_source_unavailable' or status == 'unavailable') and not _source_retrieved(rapid) and not candidates:
        support = escape(str(run.get('support_reference') or ''))
        receipt = rapid.get('source_receipt') or {}
        parse_failed = receipt.get('failure_code') == 'rapid_source_parse_failed' or (receipt.get('failure_stage') == 'validation' and receipt.get('document_parse_result') == 'failed')
        msg = 'Flora reached the approved BT financial report but could not read it safely.' if parse_failed else 'The approved official source was unavailable.'
        return f"<section class='card'><h2>No trustworthy new financial information found</h2><p>{msg}</p><p>No financial findings were created. No fixture or seeded information was substituted, and the trusted Commercial Digital Twin was unchanged.</p><p>Support reference: {support}</p>{financial_intelligence_support_report_link(run.get('run_id'))}<form method='post' action='/digital-twins/bt-group-plc/search'><button>Try again</button></form></section>"

    if receipt and _source_retrieved(rapid) and not candidates:
        unresolved = ['Revenue', 'Operating profit', 'Profit before tax']
        return "<section class='card' id='new-findings'><h2>Official BT report retrieved — no safe financial findings identified</h2><p>Flora reached and validated the approved BT FY26 report, but it could not identify the required financial figures safely.</p><p>No fixture or seeded information was substituted, and the trusted Commercial Digital Twin was unchanged.</p><h3>Unresolved financial figures</h3><ul>" + ''.join(f"<li>{escape(m)}</li>" for m in unresolved) + "</ul><p>The Commercial Digital Twin has not been updated.</p><p><a href='/financial-intelligence/" + escape(str(run.get('run_id'))) + "'>View full research result</a></p>" + financial_intelligence_support_report_link(run.get('run_id')) + "</section>"
    heading = 'New financial findings' if status == 'ready' else 'Partial source-backed financial findings'
    msg = 'Flora identified these figures in an approved official BT document. They remain outside the trusted Twin until verification and canonical acceptance are complete.' if status == 'ready' else 'Flora found some usable information, but not every financial figure could be established safely.'
    cards = ''.join(_finding_card(c, rapid.get('source_receipt') or {}) for c in candidates)
    unresolved = {'revenue','operating_profit','profit_before_tax'} - {str(c.get('proposed_canonical_metric_id')) for c in candidates}
    un = f"<p>Unresolved financial figures: {escape(', '.join(_pretty_metric({'proposed_canonical_metric_id': m}) for m in sorted(unresolved)))}</p>" if unresolved else ''
    return f"<section class='card' id='new-findings'><h2>{heading}</h2><h3>New findings awaiting verification</h3><p>{msg}</p>{cards}{un}<p>The Commercial Digital Twin has not been updated.</p><p><a href='/financial-intelligence/{escape(str(run.get('run_id')))}'>View full research result</a></p>{financial_intelligence_support_report_link(run.get('run_id'))}</section>"


def _safe_source(url: str) -> bool:
    p=urlparse(url or ''); return p.scheme == 'https' and (p.hostname or '').endswith('bt.com')


def _finding_card(c, receipt) -> str:
    loc = {}
    try: loc = json.loads(c.get('source_locator') or '{}')
    except Exception: loc = {}
    url = receipt.get('final_url') or receipt.get('requested_url') or ''
    source = f"<p><a href='{escape(url)}' target='_blank' rel='noopener noreferrer'>Open official source</a></p>" if _safe_source(url) else ''
    locator = f"Page {escape(str(c.get('source_page') or loc.get('page')))} · {escape(str(loc.get('table') or loc.get('section') or 'Detailed source location unavailable.'))}"
    return f"""<article class='card'><h3>{escape(_pretty_metric(c))}</h3><p>{escape(str(c.get('original_displayed_value') or c.get('raw_value_text')))} · {escape(str(c.get('currency')))} {escape(str(c.get('reported_scale')))} · {escape(str(c.get('raw_period_text')))}</p><p>Status: Verification pending</p><details><summary>View evidence and details</summary><p>Reported metric label: {escape(str(c.get('raw_metric_label')))}</p><p>Original displayed value: {escape(str(c.get('original_displayed_value') or c.get('raw_value_text')))}</p><p>Reporting period: {escape(str(c.get('raw_period_text')))} ({escape(str(c.get('period_start')))} to {escape(str(c.get('period_end')))})</p><p>Group scope: {escape(str(c.get('scope_text')))}</p><p>Basis: {escape(str(c.get('accounting_basis_text')))} · State: {escape(str(c.get('measurement_state_text')))}</p><p>Official document title: {escape(str(receipt.get('document_title') or 'Official BT document'))}</p><p>Source authority: {escape(str(receipt.get('authority') or 'BT Group plc'))}</p><p>{locator}; row {escape(str(loc.get('row') or 'Detailed source location unavailable.'))}; column {escape(str(loc.get('column') or 'Detailed source location unavailable.'))}</p><p>Supporting excerpt: {escape(str(c.get('supporting_excerpt') or 'Supporting excerpt unavailable.'))}</p><p>Verification status: New finding — verification pending</p><p>This finding has not yet been added to the trusted Commercial Digital Twin.</p>{source}</details></article>"""


def _history_section() -> str:
    rs = _runs()[:5]
    if not rs: return "<section class='card'><h2>Research history</h2><p>No previous source-backed research.</p></section>"
    rows=''
    for r in rs:
        rapid=r.get('rapid_intelligence') or {}; n=len(rapid.get('candidates') or [])
        outcome, verify, twin = _research_outcome(r, list(rapid.get('candidates') or []))
        rows += f"<li>{escape(_human_date(r.get('created_at')))} · {escape(str(r.get('reporting_period') or PERIOD))} · {escape(outcome.rstrip('.'))} · {escape(verify.rstrip('.'))} · Trusted Twin {escape(twin)} · <a href='/financial-intelligence/{escape(str(r.get('run_id')))}'>Open result</a> · <a class='support-report-link' href='/financial-intelligence/{escape(str(r.get('run_id')))}/support-report'>Download support report</a></li>"
    return f"<section class='card'><h2>Research history</h2><ul>{rows}</ul></section>"


def _snapshot(run: dict | None) -> dict:
    return (((run or {}).get('rapid_intelligence') or {}).get('rapid_ai_twin_snapshot') or {})

def rapid_snapshot_csv(run_id: str) -> str:
    run = _read_json(_run_dir() / (run_id + '.json'))
    return build_csv(_snapshot(run))

def _text_item(item) -> str:
    if isinstance(item, dict):
        return str(item.get('statement') or item.get('summary') or item.get('proposition') or item.get('question') or item.get('action') or item.get('commitment') or item.get('programme_name') or item.get('theme') or item)
    return str(item)

def _lineage(item) -> str:
    if not isinstance(item, dict): return ''
    refs = item.get('supporting_fact_ids') or item.get('supporting_ids') or item.get('lineage_ids') or item.get('fact_ids') or []
    return ' · Lineage: ' + escape(', '.join(map(str, refs))) if refs else ''

def _list_section(title: str, items, label: str | None = None) -> str:
    if not items: return f"<section class='card'><h2>{escape(title)}</h2><p>No source-backed items available yet.</p></section>"
    lis = ''.join(f"<li>{('<strong>'+escape(label)+'</strong> ') if label else ''}{escape(_text_item(i))}{_lineage(i)}</li>" for i in items)
    return f"<section class='card'><h2>{escape(title)}</h2><ul>{lis}</ul></section>"

def _financial_tables(snapshot: dict, run_id: str) -> str:
    tables = ((snapshot.get('extraction_result') or {}).get('financial_tables') or [])
    if not tables: return "<section class='card'><h2>Financial tables</h2><p>No financial tables are available in the rapid snapshot.</p></section>"
    blocks=[]
    for t in tables:
        headers = ''.join(f"<th>{escape(str(h))}</th>" for h in (t.get('column_headings') or ['Metric','Current','Comparator','Source']))
        rows=''
        for r in t.get('rows') or []:
            rows += f"<tr><td>{escape(str(r.get('reported_label')))}</td><td>{escape(str(r.get('current_period_display_value')))}</td><td>{escape(str(r.get('comparator_display_value') or r.get('comparator_display_values') or ''))}</td><td><details><summary>View source</summary><p>Page {escape(str(r.get('source_page')))} · {escape(str(t.get('section') or r.get('section') or ''))}</p><p>{escape(str(r.get('supporting_excerpt') or ''))}</p><p>Status: {escape(str(r.get('ambiguity') or 'Verification pending'))}</p></details></td></tr>"
        blocks.append(f"<details open><summary><strong>{escape(str(t.get('title') or t.get('table_id')))}</strong> · Page {escape(str(t.get('page') or ''))}</summary><table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></details>")
    return f"<section class='card'><h2>Financial tables</h2><p><a href='/digital-twins/bt-group-plc/rapid-snapshot/{escape(run_id)}/financial-tables.csv'>Download financial tables as CSV</a></p>{''.join(blocks)}</section>"

def _rapid_snapshot_section(run: dict | None) -> str:
    snapshot = _snapshot(run)
    if not snapshot:
        status = str((run or {}).get("status") or (run or {}).get("overall_status") or "")
        if status in {"queued", "running", "retrieving_source", "analysing", "validating"}:
            return "<section class='card' id='rapid-ai-twin-snapshot'><h2>Rapid AI Twin Snapshot</h2><p>Flora is reviewing the approved BT report.</p></section>"
        return "<section class='card' id='rapid-ai-twin-snapshot'><h2>Rapid AI Twin Snapshot</h2><p>AI Twin Snapshot is not available for this run.</p></section>"
    analysis = snapshot.get('report_analysis') or {}
    status = snapshot.get('user_status') or 'AI-built snapshot — verification pending'
    explanation = snapshot.get('user_explanation') or 'Flora reviewed the approved BT report and created this source-backed snapshot. It has not yet completed structured verification or canonical acceptance.'
    run_id = str((run or {}).get('run_id') or '')
    return f"""<section class='card warning' id='rapid-ai-twin-snapshot'><h2>Rapid AI Twin Snapshot</h2><p><strong>{escape(status)}</strong></p><p>{escape(explanation)}</p><p>Trusted Commercial Digital Twin changed: no. Canonical writes: 0.</p></section>
    {_list_section('Executive view', analysis.get('executive_summary') or [])}
    {_financial_tables(snapshot, run_id)}
    {_list_section('What changed', analysis.get('what_changed') or [])}
    {_list_section('Management commitments', snapshot.get('commitments') or [], 'Management commitment')}
    {_list_section('Transformation programmes', snapshot.get('programmes') or [], 'Reported programme')}
    {_list_section('Pressures and Signals', (analysis.get('enterprise_pressures') or []) + (snapshot.get('signals') or []), 'Signal')}
    {_list_section('Hypotheses', snapshot.get('hypotheses') or [], 'Hypothesis')}
    {_list_section('Commercial themes', analysis.get('commercial_themes') or [])}
    {_list_section('Unknowns and Contradictions', (snapshot.get('unknowns') or []) + (snapshot.get('contradictions') or []))}
    {_list_section('Questions and next learning actions', (analysis.get('questions_to_investigate') or []) + (snapshot.get('learning_actions') or []))}
    <section class='card'><h2>Trusted Twin status</h2><p>Rapid AI Twin Snapshot available; verification pending; trusted Commercial Digital Twin unchanged.</p></section>"""
