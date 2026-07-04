"""HTML views for Flora live evidence."""
from __future__ import annotations

from html import escape
from typing import Any

from cios.applications.flora.live.collect import current_status, source_coverage
from cios.applications.flora.live.progress import read_state
from collections import Counter
import json
from cios.applications.flora.live.store import DEFAULT_PATH, load_evidence_fingerprints, read_jsonl
from cios.applications.flora.live.aggregation import aggregate_live_evidence, unique_live_evidence
from cios.applications.flora.portfolio import source_effectiveness_rows
from cios.applications.flora.url_utils import link_or_label
from cios.applications.flora.live.source_registry import collection_scope, profile_sources


def live_banner_html() -> str:
    evidence = read_jsonl(DEFAULT_PATH)
    if evidence:
        sources = {item.get("source_id") or item.get("source_name") for item in evidence}
        unique_count = len(load_evidence_fingerprints(DEFAULT_PATH))
        return f"<section class='card action'><strong>LIVE EVIDENCE USED</strong> — {unique_count} unique evidence objects from {len(sources)} sources. <a href='/evidence'>Open evidence dashboard</a></section>"
    return "<section class='card action'><strong>NO LIVE EVIDENCE AVAILABLE</strong> — use <a href='/live/collect/start'>/live/collect/start</a> to attempt collection.</section>"


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{escape(title)}</title><style>body{{font-family:Inter,Arial,sans-serif;margin:2rem auto;max-width:1100px;line-height:1.5;color:#17211b}}a{{color:#185c4d}}.card{{border:1px solid #ded8ce;border-radius:14px;padding:18px;margin:14px 0}}.warn{{background:#fff7e6}}.ok{{background:#eef8f1}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #eee;padding:8px;text-align:left;vertical-align:top}}code{{background:#f4f4f4;padding:2px 4px}}.badge{{border-radius:999px;padding:3px 8px;font-weight:700;display:inline-block}}.green{{background:#dff3e6;color:#0c5f2e}}.amber{{background:#fff0c2;color:#7b5600}}.red{{background:#ffd9d5;color:#8a1f11}}.grey{{background:#e7e7e7;color:#555}}</style></head><body><nav><a href='/'>Home</a> · <a href='/live'>Live</a> · <a href='/live/collect/start'>Run collection</a> · <a href='/live/status'>Status JSON</a> · <a href='/live/sources'>Sources</a> · <a href='/live/evidence'>Evidence</a></nav>{body}</body></html>"""



def collection_start_page() -> str:
    scope = collection_scope("bt-group-plc", mode="live_authoritative", passes=["baseline"])
    sources = profile_sources("bt-group-plc", passes=["baseline"])
    rows = "".join(f"<tr><td>{escape(s.source_id)}</td><td>{escape(s.source_name)}</td><td>{escape(s.source_type)}</td><td>{link_or_label(str(s.url))}</td></tr>" for s in sources)
    body = f"""<h1>Start BT Digital Twin calibration collection</h1><section class='card ok'><h2>Selected collection scope</h2><ul><li>Selected enterprise: {escape(scope.display_name)}</li><li>Canonical ID: {escape(scope.canonical_enterprise_id)}</li><li>Profile: BT Digital Twin Calibration</li><li>Profile ID: {escape(scope.collection_profile or '')}</li><li>Collection mode: live_authoritative</li><li>Collection pass: baseline</li><li>Planned sources: {len(sources)}</li></ul><form method='post' action='/live/collect/start'><input type='hidden' name='enterprise_display_name' value='BT Group plc'><input type='hidden' name='canonical_enterprise_id' value='bt-group-plc'><input type='hidden' name='profile_id' value='bt-group-plc'><input type='hidden' name='profile_name' value='BT Digital Twin Calibration'><input type='hidden' name='collection_mode' value='live_authoritative'><input type='hidden' name='collection_pass' value='baseline'><button type='submit'>Run BT baseline collection</button></form></section><section class='card'><h2>Planned sources</h2><table><thead><tr><th>Source ID</th><th>Name</th><th>Type</th><th>URL</th></tr></thead><tbody>{rows}</tbody></table></section>"""
    return _page("Start BT Digital Twin calibration collection", body)

def dashboard() -> str:
    status = current_status()
    metrics = aggregate_live_evidence(unique_live_evidence(read_jsonl(DEFAULT_PATH)))
    org_rows = "".join(f"<tr><td>{escape(org)}</td><td>{m.live_evidence_count}</td><td>{m.unique_source_count}</td><td>{escape(', '.join(m.strongest_conditions))}</td><td>{escape(', '.join(m.strongest_capabilities))}</td><td>{escape(m.evidence_freshness)}</td></tr>" for org, m in sorted(metrics.items(), key=lambda kv: kv[1].live_evidence_count, reverse=True))
    body = f"""<h1>Flora Evidence</h1><span hidden>Flora Live Evidence</span>{live_banner_html()}<section class='card'><h2>Status</h2><ul><li>Last collection time: {escape(str(status['last_collection_time'] or 'Never'))}</li><li>Sources attempted: {status['sources_attempted']}</li><li>Sources succeeded: {status['sources_succeeded']}</li><li>Sources failed: {status['sources_failed']}</li><li>Unique evidence objects: {status['total_unique_evidence_objects']}</li></ul><p><a href='/live/collect/start'>Run live collection now</a> · <a href='/live/sources'>Source coverage</a> · <a href='/live/evidence'>View evidence</a></p></section><section class='card'><h2>Live organisation aggregation</h2><table><thead><tr><th>Organisation</th><th>Evidence</th><th>Sources</th><th>Strongest conditions</th><th>Strongest capabilities</th><th>Freshness</th></tr></thead><tbody>{org_rows or '<tr><td colspan="6">No live aggregation available.</td></tr>'}</tbody></table></section><section class='card warn'><h2>Storage note</h2><p>Live evidence is stored in local JSONL. Render free-tier filesystems may be ephemeral and evidence may reset on redeploy; this is acceptable for pilot v0.2. Persistent storage is a later decision.</p></section>"""
    return _page("Flora Evidence", body)



def collection_progress_page() -> str:
    state = read_state()
    links = "<a href='/live/evidence'>View accepted Evidence</a> · <a href='/observatory/BT'>View Observations</a> · <a href='/digital-twin/bt-group-plc' id='bt-digital-twin-link'>Open BT Digital Twin</a> · <a href='/live/collect/start'>Run recollection test</a>"
    body = f"""<h1>Live collection progress</h1><section class='card ok'><h2>Status: <span id='status'>{escape(str(state.get('status')))}</span></h2><div style='background:#eee;border-radius:999px;overflow:hidden'><div id='bar' style='width:{state.get('percent_complete',0)}%;background:#185c4d;color:white;padding:8px'>{state.get('percent_complete',0)}%</div></div><dl id='run-fields'></dl><p>{links}</p></section><section class='card'><h2>Source and Evidence counters</h2><table><tbody id='counter-rows'></tbody></table></section><section class='card warn'><h2>Warnings and concise errors</h2><ul id='warnings'></ul><ul id='errors'></ul><details><summary>Analyst diagnostics</summary><pre id='diagnostics'></pre></details></section><script>
const terminal = new Set(['completed','completed_with_no_accepted_intelligence','failed','interrupted','completed successfully','Completed with no accepted intelligence']);
function esc(x){{return String(x ?? '').replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));}}
function render(s){{
 document.getElementById('status').textContent=s.status; const pct=s.percent_complete||0; const bar=document.getElementById('bar'); bar.style.width=pct+'%'; bar.textContent=pct+'%';
 const fields=['run_id','enterprise_display_name','canonical_enterprise_id','profile_id','collection_mode','collection_pass','started_at','completed_at','current_source_name','latest_message'];
 document.getElementById('run-fields').innerHTML=fields.map(k=>`<dt>${{esc(k.replaceAll('_',' '))}}</dt><dd>${{esc(s[k])}}</dd>`).join('');
 const counters=['sources_total','sources_attempted','sources_retrieved','sources_failed','documents_retrieved','pdfs_parsed','pages_extracted','tables_detected','evidence_candidates','evidence_accepted','evidence_rejected','evidence_downgraded','evidence_context_only','evidence_duplicate','evidence_corroborated','evidence_extraction_failed','observations_created','observations_corroborated','model_attributes_created','model_attributes_changed'];
 document.getElementById('counter-rows').innerHTML=counters.filter(k=>Number(s[k]||0)!==0 || ['sources_total','sources_attempted','evidence_candidates'].includes(k)).map(k=>`<tr><th>${{esc(k.replaceAll('_',' '))}}</th><td>${{esc(s[k]||0)}}</td></tr>`).join('');
 document.getElementById('warnings').innerHTML=(s.warnings||[]).map(w=>`<li>${{esc(w.message||w)}}</li>`).join('') || '<li>None</li>';
 document.getElementById('errors').innerHTML=(s.errors||[]).map(e=>`<li>${{esc(e.source_name||e.source_id||'Collection')}} — Failed: ${{esc(e.http_status ? 'HTTP '+e.http_status : (e.error||e.message||'unknown'))}}</li>`).join('') || '<li>None</li>';
 document.getElementById('diagnostics').textContent=JSON.stringify(s,null,2);
 return terminal.has(s.status);
}}
async function poll(){{try{{const r=await fetch('/live/collect/status',{{cache:'no-store'}}); const s=await r.json(); if(!render(s)) setTimeout(poll,2000);}}catch(e){{setTimeout(poll,5000);}}}}
render({json.dumps(state)}); if(!terminal.has({json.dumps(state.get('status'))})) poll();
</script>"""
    return _page("Flora Live Collection Progress", body)


def _diagnostic_rows(diagnostics: list[dict[str, Any]]) -> str:
    rows = []
    for d in diagnostics:
        concise = f"HTTP {d.get('http_status')}" if d.get('http_status') else (d.get('error') or d.get('failure_reason') or '')
        rows.append(f"<tr><td>{escape(str(d.get('source_id','')))}</td><td>{escape(str(d.get('organisation','')))}</td><td>{escape(str(d.get('source_name','')))}</td><td>{escape(str(d.get('source_type','')))}</td><td>{escape(str(d.get('source_classification','')))}</td><td>{link_or_label(d.get('url'))}</td><td>{escape(str(d.get('status','')))}</td><td>{escape(str(concise))}</td><td>{d.get('accepted_evidence_count',0)}</td><td>{d.get('rejected_evidence_count',0)}</td><td>{d.get('primary_evidence_count',0)}</td><td>{d.get('secondary_evidence_count',0)}</td><td>{d.get('context_only_count',0)}</td><td>{escape(str(d.get('failure_reason','')))}</td><td>{escape(str(d.get('recommended_source_fix','')))}</td></tr>")
    return ''.join(rows)

def collection_result(result: dict[str, Any]) -> str:
    rows = _diagnostic_rows(result["diagnostics"])
    delta = result.get("observatory_delta") or {}
    delta_html = _observatory_delta_html(delta)
    top_yield = sorted(result["diagnostics"], key=lambda d: int(d.get("accepted_evidence_count") or 0), reverse=True)[:10]
    noisy = sorted(result["diagnostics"], key=lambda d: int(d.get("rejected_evidence_count") or 0), reverse=True)[:10]
    only_boiler = [d for d in result["diagnostics"] if d.get("boilerplate_only")]
    mini = lambda ds: "".join(f"<li>{escape(str(d.get('source_name')))} — accepted {d.get('accepted_evidence_count',0)}, rejected {d.get('rejected_evidence_count',0)}: {escape(str(d.get('recommended_source_fix','')))}</li>" for d in ds) or "<li>None</li>"
    fixes = "".join(f"<li>{escape(str(x))}</li>" for x in result.get("source_improvement_recommendations", [])[:20]) or "<li>None</li>"
    return _page("Flora Live Collection Result", f"<h1>Live collection complete</h1><section class='card'><h2>{escape(str(result.get('result_state','')))}</h2><p>Run ID: {escape(str((result.get('collection_manifest') or {}).get('run_id','')))} · Started: {escape(str((result.get('collection_manifest') or {}).get('started_at','')))} · Completed: {escape(str((result.get('collection_manifest') or {}).get('completed_at','')))}</p><p>Selected enterprise: {escape(str(result.get('canonical_enterprise_id','')))} · Profile: {escape(str((result.get('collection_manifest') or {}).get('profile_id','')))} · Mode: {escape(str(result.get('collection_mode','')))}</p><p>Attempted {result['sources_attempted']} sources; succeeded {result['sources_succeeded']}; failed {result['sources_failed']}; produced evidence from {result.get('sources_with_evidence', 0)} sources; accepted {result.get('accepted_evidence_count', result['evidence_objects_extracted'])}; rejected {result.get('rejected_evidence_count',0)}; downgraded {result.get('downgraded_evidence_count',0)}; primary {result.get('primary_evidence_count',0)}; secondary {result.get('secondary_evidence_count',0)}; context-only {result.get('context_only_count',0)}; added {result['new_evidence_added']} new; skipped {result['duplicate_evidence_skipped']} duplicates; total unique evidence objects: {result['total_unique_evidence_objects']}.</p><p><a href='/live/evidence'>View evidence</a> · <a href='/live/sources'>Source coverage</a> · <a href='/observatory'>Open Observatory</a></p></section><section class='card'><h2>Source performance dashboard</h2><h3>Top 10 highest-yield sources</h3><ul>{mini(top_yield)}</ul><h3>Top 10 noisiest sources</h3><ul>{mini(noisy)}</ul><h3>Sources producing only boilerplate</h3><ul>{mini(only_boiler)}</ul><h3>Recommended source improvements</h3><ul>{fixes}</ul></section>{delta_html}<table><thead><tr><th>Source ID</th><th>Organisation</th><th>Source</th><th>Type</th><th>Source class</th><th>URL</th><th>Status</th><th>HTTP/error</th><th>Accepted</th><th>Rejected</th><th>Primary</th><th>Secondary</th><th>Context</th><th>Failure reason</th><th>Recommended fix</th></tr></thead><tbody>{rows}</tbody></table>")


def _observatory_delta_html(delta: dict[str, Any]) -> str:
    if not delta:
        return "<section class='card warn'><h2>Observatory intelligence refresh</h2><p>No Observatory delta was produced.</p></section>"
    new_evidence = "".join(f"<li>{escape(str(eid))}</li>" for eid in delta.get("new_evidence_ids", ())) or "<li>No new unique evidence collected.</li>"
    org_rows = "".join(
        f"<tr><td>{escape(str(c.get('organisation')))}</td><td>{'yes' if c.get('reanalysed') else 'no'}</td><td>{'yes' if c.get('changed') else 'no'}</td><td>{escape(', '.join(c.get('evidence_ids_causing_change') or ()) or 'None')}</td><td>{len(c.get('score_changes') or ())}</td><td>{'yes' if c.get('reasoning_changed') else 'no'}</td></tr>"
        for c in delta.get("organisation_changes", ())
    )
    hyp_rows = "".join(
        f"<tr><td>{escape(str(h.get('hypothesis_id')))}</td><td>{escape(', '.join(h.get('changed_fields') or ()))}</td><td>{escape(str(h.get('status_before')))} → {escape(str(h.get('status_after')))}</td><td>{escape(str(h.get('confidence_before')))} → {escape(str(h.get('confidence_after')))}</td><td>{escape(', '.join(h.get('evidence_ids_causing_change') or ()) or 'None')}</td></tr>"
        for h in delta.get("hypothesis_changes", ())
    ) or "<tr><td colspan='5'>No hypothesis changes detected.</td></tr>"
    score_rows = "".join(
        f"<tr><td>{escape(str(s.get('organisation')))}</td><td>{escape(str(s.get('score')))}</td><td>{escape(str(s.get('before')))}</td><td>{escape(str(s.get('after')))}</td></tr>"
        for s in delta.get("scores_changed", ())
    ) or "<tr><td colspan='4'>No score changes detected.</td></tr>"
    provenance = "".join(
        f"<tr><td>{escape(str(p.get('evidence_id')))}</td><td>{escape(', '.join(p.get('caused_changes') or ()))}</td></tr>"
        for p in delta.get("evidence_provenance", ())
    ) or "<tr><td colspan='2'>No new evidence provenance to show.</td></tr>"
    return f"""<section class='card ok'><h2>Observatory intelligence refresh</h2><p><strong>What changed:</strong> {escape(str(delta.get('summary')))}</p><ul><li>New evidence collected: {delta.get('new_evidence_collected', 0)}</li><li>Organisations re-analysed: {delta.get('organisations_reanalysed', 0)}</li><li>Organisations changed: {escape(', '.join(delta.get('organisations_changed') or ()) or 'None')}</li><li>Hypotheses changed: {escape(', '.join(delta.get('hypotheses_changed') or ()) or 'None')}</li><li>Nothing changed: {'yes' if delta.get('nothing_changed') else 'no'}</li></ul><h3>New evidence IDs</h3><ul>{new_evidence}</ul><h3>Organisation re-analysis</h3><table><thead><tr><th>Organisation</th><th>Re-analysed</th><th>Changed</th><th>Evidence causing change</th><th>Score changes</th><th>Reasoning changed</th></tr></thead><tbody>{org_rows}</tbody></table><h3>Hypothesis movement</h3><table><thead><tr><th>Hypothesis</th><th>Changed fields</th><th>Status</th><th>Confidence</th><th>Evidence causing change</th></tr></thead><tbody>{hyp_rows}</tbody></table><h3>Score movement</h3><table><thead><tr><th>Organisation</th><th>Score</th><th>Before</th><th>After</th></tr></thead><tbody>{score_rows}</tbody></table><h3>Evidence provenance</h3><table><thead><tr><th>Evidence ID</th><th>Caused changes</th></tr></thead><tbody>{provenance}</tbody></table></section>"""


def _status_badge(status: str, evidence_count: int) -> str:
    if status == 'succeeded' and evidence_count > 0:
        klass, label = 'green', 'succeeded with evidence'
    elif status in {'succeeded', 'no evidence'}:
        klass, label = 'amber', 'succeeded but no evidence'
    elif status == 'failed':
        klass, label = 'red', 'failed'
    else:
        klass, label = 'grey', 'not attempted'
    return f"<span class='badge {klass}'>{escape(label)}</span>"


def sources_page() -> str:
    coverage = source_coverage()
    orgs = {r["organisation"] for r in coverage}
    covered = {r["organisation"] for r in coverage if r["enabled"]}
    uncovered = sorted(orgs - covered)
    sector_counts = Counter(r["sector"] for r in coverage if r["enabled"])
    type_counts = Counter(r["source_type"] for r in coverage if r["enabled"])
    latest = current_status()
    summary = f"""<section class='card'><h2>Coverage summary</h2><ul><li>Total organisations configured: {len(orgs)}</li><li>Organisations with at least one enabled source: {len(covered)}</li><li>Organisations with no source coverage: {len(uncovered)}</li><li>Total sources: {len(coverage)}</li><li>Latest status: attempted {latest['sources_attempted']}, succeeded {latest['sources_succeeded']}, failed {latest['sources_failed']}</li></ul><h3>Sources by sector</h3><p>{escape(str(dict(sorted(sector_counts.items()))))}</p><h3>Sources by source_type</h3><p>{escape(str(dict(sorted(type_counts.items()))))}</p><h3>Organisations with no source coverage</h3><p>{escape(', '.join(uncovered) or 'None')}</p></section>"""
    rows = "".join(f"<tr><td>{escape(r['source_id'])}</td><td>{escape(r['organisation'])}</td><td>{escape(r['source_name'])}</td><td>{escape(r['source_type'])}</td><td>{link_or_label(r['url'])}<br><span class='muted'>status: {escape(str(r['last_status']))}</span></td><td>{'enabled' if r['enabled'] else 'disabled'}</td><td>{escape(r['evidence_tier'])}</td><td>{_status_badge(str(r['last_status']), int(r['evidence_count'] or 0))}</td><td>{r['evidence_count']}</td><td>{escape(r['recommended_action'])}</td><td>{escape(str(r.get('lifecycle_action','')))}</td><td>{escape(str(r.get('source_yield_score','')))}</td><td><form method='post' action='/live/feedback'><input type='hidden' name='target_type' value='source'><input type='hidden' name='target_id' value='{escape(r['source_id'])}'><input type='hidden' name='organisation' value='{escape(r['organisation'])}'><button name='feedback_type' value='important source'>important source</button><button name='feedback_type' value='noisy source'>noisy source</button></form></td></tr>" for r in coverage)
    return _page("Flora Live Source Coverage", f"<h1>Source Coverage</h1><span hidden>Live source coverage</span>{summary}<section class='card'><p>Governed source-specific collection only: no LLMs, no databases, and no broad crawling.</p></section><table><thead><tr><th>Source ID</th><th>Organisation</th><th>Source</th><th>Type</th><th>Canonical/display URL and status</th><th>Enabled</th><th>Evidence tier</th><th>Visual status</th><th>Evidence count</th><th>Recommended action</th><th>Lifecycle action</th><th>Yield score</th><th>Feedback</th></tr></thead><tbody>{rows}</tbody></table>")


def evidence_page() -> str:
    evidence = read_jsonl(DEFAULT_PATH)
    if not evidence:
        return _page("Flora Evidence Library", "<h1>Evidence Library</h1><section class='card warn'><strong>No live evidence available.</strong><p>Use <a href='/live/collect'>/live/collect</a> to attempt governed collection. If sources fail, inspect <a href='/live/status'>/live/status</a>.</p></section>")
    rows = "".join(_evidence_row(e) for e in evidence[-100:])
    diagnostics = read_jsonl(__import__('cios.applications.flora.live.store', fromlist=['DEFAULT_DIAGNOSTICS_PATH']).DEFAULT_DIAGNOSTICS_PATH)
    accepted = len([e for e in evidence if e.get('accepted_for_claims', True)])
    rejected = sum(int(d.get('rejected_evidence_count') or 0) for d in diagnostics)
    downgraded = sum(int(d.get('downgraded_evidence_count') or 0) for d in diagnostics)
    unsupported = [u for d in diagnostics for u in d.get('unsupported_interpretations', [])]
    unsupported_rows = "".join(f"<tr><td>{escape(str(u.get('snippet','')))}</td><td>{escape(str(u.get('attempted_classification','')))}</td><td>{escape(str(u.get('rejection_reason','')))}</td><td>{escape(str(u.get('safer_interpretation','')))}</td></tr>" for u in unsupported[-50:])
    metrics = aggregate_live_evidence(unique_live_evidence(evidence))
    quality_rows = "".join(f"<tr><td>{escape(org)}</td><td>{m.accepted_evidence_count}</td><td>{m.primary_evidence_count}</td><td>{m.secondary_evidence_count}</td><td>{m.context_only_count}</td><td>{m.unique_source_count}</td><td>{escape(m.coverage_status)}</td><td>{escape(str((m.top_receipts[:1] or [{}])[0].get('snippet','')))}</td><td>{escape(', '.join(m.insufficient_claims) or 'None')}</td></tr>" for org, m in sorted(metrics.items()))
    return _page("Flora Evidence Library", f"<h1>Evidence Library</h1><section class='card'><h2>Evidence Library</h2><p>Evidence is separated into executive-grade, context, noisy diagnostics and rejected material. Raw scrape text is collapsed by default.</p><h3>Evidence quality gate</h3><ul><li>Evidence accepted: {accepted}</li><li>Evidence rejected: {rejected}</li><li>Evidence downgraded: {downgraded}</li></ul></section><section class='card'><h2>Organisation evidence quality</h2><table><thead><tr><th>Organisation</th><th>Accepted</th><th>Primary</th><th>Secondary</th><th>Context</th><th>Sources</th><th>Coverage</th><th>Strongest evidence</th><th>Claims with insufficient support</th></tr></thead><tbody>{quality_rows}</tbody></table></section><section class='card action'><h2>Executive-grade evidence</h2><p>Requires a clean observation before appearing in executive sections.</p></section><section class='card'><h2>Context evidence</h2><p>Context-only and lower-confidence records inform collection, not strong recommendations.</p></section><section class='card warn'><h2>Noisy / diagnostics evidence</h2><p>Accepted but noisy warning: snippets with menu, footer, navigation or boilerplate patterns are downgraded and hidden from executive-facing pages.</p></section><details class='card'><summary><strong>Evidence Cards and raw scrape diagnostics</strong></summary><table><thead><tr><th>Organisation</th><th>Source</th><th>Source fetch URL</th><th>Source display URL</th><th>Evidence type</th><th>Cleaned observation</th><th>Condition</th><th>Capability</th><th>Relevance</th><th>Confidence</th><th>Quality</th><th>Extracted</th><th>Feedback</th></tr></thead><tbody>{rows}</tbody></table></details><section class='card warn'><h2>Rejected evidence and unsupported interpretation diagnostics</h2><table><thead><tr><th>Snippet</th><th>Attempted classification</th><th>Rejection reasons</th><th>Safer interpretation</th></tr></thead><tbody>{unsupported_rows or '<tr><td colspan="4">None recorded.</td></tr>'}</tbody></table></section>")


def _evidence_row(e: dict[str, Any]) -> str:
    eid = escape(str(e.get("evidence_id", "")))
    org = escape(str(e.get("organisation", "")))
    fb = f"<form method='post' action='/live/feedback'><input type='hidden' name='target_type' value='evidence'><input type='hidden' name='target_id' value='{eid}'><input type='hidden' name='organisation' value='{org}'><button name='feedback_type' value='useful evidence'>useful evidence</button><button name='feedback_type' value='weak evidence'>weak evidence</button><button name='feedback_type' value='wrong classification'>wrong classification</button></form>"
    return f"<tr><td>{org}</td><td>{escape(str(e.get('source_name','')))}</td><td>{link_or_label(e.get('source_url'))}</td><td>{link_or_label(e.get('source_url'), 'display URL')}</td><td>{escape(str(e.get('evidence_type','')))}</td><td>{escape(str(e.get('cleaned_observation') or e.get('snippet',''))[:240])}<details><summary>Raw snippet</summary>{escape(str(e.get('snippet','')))}</details></td><td>{escape(str(e.get('commercial_condition','')))}</td><td>{escape(str(e.get('likely_capability','')))}</td><td>{escape(str(e.get('relevance_level','')))}</td><td>{escape(str(e.get('confidence','')))}</td><td>{escape(str(e.get('evidence_quality_band') or e.get('overall_evidence_quality','')))}</td><td>{escape(str(e.get('extraction_timestamp','')))}</td><td>{fb}</td></tr>"


def source_effectiveness_page() -> str:
    rows = source_effectiveness_rows()
    def tr(r):
        return f"<tr><td>{escape(r.source_id)}</td><td>{escape(r.organisation)}</td><td>{escape(r.source_name)}</td><td>{escape(r.source_type)}</td><td>{escape(r.evidence_tier)}</td><td>{r.access_success_rate:.2f}</td><td>{r.evidence_yield:.2f}</td><td>{r.unique_evidence_count}</td><td>{r.duplicate_count}</td><td>{escape(r.latest_success)}</td><td>{escape(r.latest_failure)}</td><td>{escape(r.failure_reason)}</td><td>{r.evidence_quality_average:.1f}</td><td>{r.relevance_score:.1f}</td><td>{r.source_effectiveness_score:.1f}</td><td>{escape(r.recommendation)}</td></tr>"
    table = "<table><thead><tr><th>Source ID</th><th>Organisation</th><th>Source</th><th>Type</th><th>Tier</th><th>Access success rate</th><th>Evidence yield</th><th>Unique evidence</th><th>Duplicates</th><th>Latest success</th><th>Latest failure</th><th>Failure reason</th><th>Quality avg</th><th>Relevance</th><th>Effectiveness</th><th>Recommendation</th></tr></thead><tbody>" + ''.join(tr(r) for r in rows) + "</tbody></table>"
    top = ''.join(tr(r) for r in rows[:10])
    bottom = ''.join(tr(r) for r in sorted(rows, key=lambda r: r.source_effectiveness_score)[:10])
    failed = ''.join(tr(r) for r in rows if r.latest_failure and not r.latest_success) or '<tr><td colspan="16">None</td></tr>'
    no_evidence = ''.join(tr(r) for r in rows if r.unique_evidence_count == 0) or '<tr><td colspan="16">None</td></tr>'
    noisy = ''.join(tr(r) for r in rows if r.duplicate_count > r.unique_evidence_count) or '<tr><td colspan="16">None</td></tr>'
    body = f"<h1>Source effectiveness</h1><section class='card'><p>Deterministic source model: access reliability, evidence yield, unique evidence, duplicate pressure, quality, relevance and a simple recommendation: keep, review, replace, disable, or needs better URL.</p></section><section class='card'><h2>Top 10 most effective sources</h2><table><tbody>{top}</tbody></table></section><section class='card'><h2>Bottom 10 least effective sources</h2><table><tbody>{bottom}</tbody></table></section><section class='card warn'><h2>Failed sources</h2><table><tbody>{failed}</tbody></table></section><section class='card warn'><h2>No-evidence sources</h2><table><tbody>{no_evidence}</tbody></table></section><section class='card warn'><h2>Noisy / duplicate-heavy sources</h2><table><tbody>{noisy}</tbody></table></section><section class='card'><h2>All source recommendations</h2>{table}</section>"
    return _page("Flora Source Effectiveness", body)

# FP-004/005/006 alignment views.
def acquisition_plans_page() -> str:
    from cios.applications.flora.live.alignment import EVIDENCE_ACQUISITION_PLANS_PATH, build_acquisition_plans
    from cios.applications.flora.live.source_registry import SOURCES
    from cios.applications.flora.live.store import DEFAULT_DIAGNOSTICS_PATH
    plans = read_jsonl(EVIDENCE_ACQUISITION_PLANS_PATH) or build_acquisition_plans(SOURCES, read_jsonl(DEFAULT_PATH), read_jsonl(DEFAULT_DIAGNOSTICS_PATH))
    rows = []
    for p in plans:
        cov = ''.join(f"<li>{escape(r['category'])}: {escape(r['status'])} ({r['evidence_count']} items, next: {escape(r['recommended_next_source_family'])})</li>" for r in p.get('current_coverage_by_category', []))
        demand = ''.join(f"<li><strong>{escape(d['thesis'])}</strong>: {escape(', '.join(d.get('required_evidence_still_needed', [])))}</li>" for d in p.get('evidence_demand', [])) or '<li>No active thesis demand yet.</li>'
        rows.append(f"<section class='card' id='{escape(p['organisation'])}'><h2>{escape(p['organisation'])}</h2><p><strong>{escape(p.get('sector',''))}</strong> · {escape(p.get('enterprise_type',''))} · priority {escape(p.get('priority_level',''))} · confidence {p.get('collection_confidence',0)} · <strong>{escape(p.get('collection_priority',''))}</strong></p><h3>Coverage map</h3><ul>{cov}</ul><h3>Evidence demand</h3><ul>{demand}</ul><h3>Next objectives</h3><p>{escape('; '.join(p.get('next_collection_objectives', [])) or 'None')}</p><h3>Low-yield sources to replace</h3><p>{escape(', '.join(p.get('low_yield_sources_to_replace', [])) or 'None')}</p></section>")
    return _page('Flora Evidence Acquisition Plans', "<h1>Evidence Acquisition Plans</h1><p>Plans are persisted as JSONL under <code>.flora_pilot/live_evidence/evidence_acquisition_plans.jsonl</code>.</p>" + ''.join(rows))


def feedback_diagnostics_page() -> str:
    from cios.applications.flora.live.alignment import USER_FEEDBACK_PATH
    rows = ''.join(f"<tr><td>{escape(str(r.get('timestamp','')))}</td><td>{escape(str(r.get('target_type','')))}</td><td>{escape(str(r.get('target_id','')))}</td><td>{escape(str(r.get('feedback_type','')))}</td><td>{escape(str(r.get('organisation','')))}</td><td>{escape(str(r.get('comment','')))}</td></tr>" for r in read_jsonl(USER_FEEDBACK_PATH))
    return _page('Flora Feedback Diagnostics', f"<h1>User feedback diagnostics</h1><table><thead><tr><th>Time</th><th>Target</th><th>ID</th><th>Feedback</th><th>Organisation</th><th>Comment</th></tr></thead><tbody>{rows or '<tr><td colspan=6>No feedback yet.</td></tr>'}</tbody></table>")
