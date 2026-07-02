"""HTML views for Flora live evidence."""
from __future__ import annotations

from html import escape
from typing import Any

from cios.applications.flora.live.collect import current_status, source_coverage
from cios.applications.flora.live.progress import read_state
from collections import Counter
from cios.applications.flora.live.store import DEFAULT_PATH, load_evidence_fingerprints, read_jsonl
from cios.applications.flora.live.aggregation import aggregate_live_evidence, unique_live_evidence
from cios.applications.flora.portfolio import source_effectiveness_rows
from cios.applications.flora.url_utils import link_or_label


def live_banner_html() -> str:
    evidence = read_jsonl(DEFAULT_PATH)
    if evidence:
        sources = {item.get("source_id") or item.get("source_name") for item in evidence}
        unique_count = len(load_evidence_fingerprints(DEFAULT_PATH))
        return f"<section class='card action'><strong>LIVE EVIDENCE USED</strong> — {unique_count} unique evidence objects from {len(sources)} sources. <a href='/evidence'>Open evidence dashboard</a></section>"
    return "<section class='card action'><strong>NO LIVE EVIDENCE AVAILABLE</strong> — use <a href='/live/collect/start'>/live/collect/start</a> to attempt collection.</section>"


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{escape(title)}</title><style>body{{font-family:Inter,Arial,sans-serif;margin:2rem auto;max-width:1100px;line-height:1.5;color:#17211b}}a{{color:#185c4d}}.card{{border:1px solid #ded8ce;border-radius:14px;padding:18px;margin:14px 0}}.warn{{background:#fff7e6}}.ok{{background:#eef8f1}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #eee;padding:8px;text-align:left;vertical-align:top}}code{{background:#f4f4f4;padding:2px 4px}}.badge{{border-radius:999px;padding:3px 8px;font-weight:700;display:inline-block}}.green{{background:#dff3e6;color:#0c5f2e}}.amber{{background:#fff0c2;color:#7b5600}}.red{{background:#ffd9d5;color:#8a1f11}}.grey{{background:#e7e7e7;color:#555}}</style></head><body><nav><a href='/'>Home</a> · <a href='/live'>Live</a> · <a href='/live/collect/start'>Run collection</a> · <a href='/live/status'>Status JSON</a> · <a href='/live/sources'>Sources</a> · <a href='/live/evidence'>Evidence</a></nav>{body}</body></html>"""


def dashboard() -> str:
    status = current_status()
    metrics = aggregate_live_evidence(unique_live_evidence(read_jsonl(DEFAULT_PATH)))
    org_rows = "".join(f"<tr><td>{escape(org)}</td><td>{m.live_evidence_count}</td><td>{m.unique_source_count}</td><td>{escape(', '.join(m.strongest_conditions))}</td><td>{escape(', '.join(m.strongest_capabilities))}</td><td>{escape(m.evidence_freshness)}</td></tr>" for org, m in sorted(metrics.items(), key=lambda kv: kv[1].live_evidence_count, reverse=True))
    body = f"""<h1>Flora Evidence</h1><span hidden>Flora Live Evidence</span>{live_banner_html()}<section class='card'><h2>Status</h2><ul><li>Last collection time: {escape(str(status['last_collection_time'] or 'Never'))}</li><li>Sources attempted: {status['sources_attempted']}</li><li>Sources succeeded: {status['sources_succeeded']}</li><li>Sources failed: {status['sources_failed']}</li><li>Unique evidence objects: {status['total_unique_evidence_objects']}</li></ul><p><a href='/live/collect/start'>Run live collection now</a> · <a href='/live/sources'>Source coverage</a> · <a href='/live/evidence'>View evidence</a></p></section><section class='card'><h2>Live organisation aggregation</h2><table><thead><tr><th>Organisation</th><th>Evidence</th><th>Sources</th><th>Strongest conditions</th><th>Strongest capabilities</th><th>Freshness</th></tr></thead><tbody>{org_rows or '<tr><td colspan="6">No live aggregation available.</td></tr>'}</tbody></table></section><section class='card warn'><h2>Storage note</h2><p>Live evidence is stored in local JSONL. Render free-tier filesystems may be ephemeral and evidence may reset on redeploy; this is acceptable for pilot v0.2. Persistent storage is a later decision.</p></section>"""
    return _page("Flora Evidence", body)



def collection_progress_page() -> str:
    state = read_state()
    pct = int(state.get("percent_complete") or 0)
    body = f"""<h1>Live collection progress</h1><section class='card ok'><h2>Status: {escape(str(state.get('status')))}</h2><div style='background:#eee;border-radius:999px;overflow:hidden'><div style='width:{pct}%;background:#185c4d;color:white;padding:8px'>{pct}%</div></div><ul><li>Run ID: {escape(str(state.get('run_id')))}</li><li>Started: {escape(str(state.get('started_at')))}</li><li>Completed: {escape(str(state.get('completed_at')))}</li><li>Current source: {escape(str(state.get('current_source_name') or 'n/a'))}</li><li>Sources attempted / total: {state.get('sources_attempted', 0)} / {state.get('sources_total', 0)}</li><li>Succeeded: {state.get('sources_succeeded', 0)}</li><li>Failed: {state.get('sources_failed', 0)}</li><li>Evidence extracted: {state.get('evidence_extracted', 0)}</li><li>Latest message: {escape(str(state.get('latest_message')))}</li></ul><p class='muted'>This dependency-light deployment runs collection synchronously; percentage is updated in the state file during collection and is visible immediately after redirects complete. No Celery, Redis, database or external queue is used.</p><p><a href='/live/evidence'>View evidence</a> · <a href='/observatory'>Open Observatory</a> · <a href='/live/collect/start'>Run again</a></p></section><script>setTimeout(function(){{fetch('/live/collect/status').then(r=>r.json()).then(s=>{{if(s.status==='running') location.reload();}}).catch(()=>{{}})}},3000);</script>"""
    return _page("Flora Live Collection Progress", body)

def _diagnostic_rows(diagnostics: list[dict[str, Any]]) -> str:
    return "".join(f"<tr><td>{escape(d['source_id'])}</td><td>{escape(d['organisation'])}</td><td>{escape(d['source_name'])}</td><td>{escape(str(d.get('source_type','')))}</td><td><a href='{escape(str(d.get('url','')))}'>{escape(str(d.get('url','')))}</a></td><td>{escape(str(d.get('status') or ('succeeded' if d.get('success') else 'failed')))}</td><td>{escape(str(d.get('http_status') or d.get('error') or ''))}</td><td>{d.get('evidence_count',0)}</td><td>{escape(str(d.get('last_attempted') or d.get('attempted_at') or ''))}</td><td>{escape(str(d.get('failure_reason') or ''))}</td></tr>" for d in diagnostics)


def collection_result(result: dict[str, Any]) -> str:
    rows = _diagnostic_rows(result["diagnostics"])
    delta = result.get("observatory_delta") or {}
    delta_html = _observatory_delta_html(delta)
    return _page("Flora Live Collection Result", f"<h1>Live collection complete</h1><section class='card'><p>Attempted {result['sources_attempted']} sources; succeeded {result['sources_succeeded']}; failed {result['sources_failed']}; produced evidence from {result.get('sources_with_evidence', 0)} sources; extracted {result['evidence_objects_extracted']} evidence objects; added {result['new_evidence_added']} new; skipped {result['duplicate_evidence_skipped']} duplicates; total unique evidence objects: {result['total_unique_evidence_objects']}.</p><p><a href='/live/evidence'>View evidence</a> · <a href='/live/sources'>Source coverage</a> · <a href='/observatory'>Open Observatory</a></p></section>{delta_html}<table><thead><tr><th>Source ID</th><th>Organisation</th><th>Source</th><th>Type</th><th>URL</th><th>Status</th><th>HTTP/error</th><th>Evidence</th><th>Last attempted</th><th>Failure reason</th></tr></thead><tbody>{rows}</tbody></table>")


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
    rows = "".join(f"<tr><td>{escape(r['source_id'])}</td><td>{escape(r['organisation'])}</td><td>{escape(r['source_name'])}</td><td>{escape(r['source_type'])}</td><td>{link_or_label(r['url'])}<br><span class='muted'>status: {escape(str(r['last_status']))}</span></td><td>{'enabled' if r['enabled'] else 'disabled'}</td><td>{escape(r['evidence_tier'])}</td><td>{_status_badge(str(r['last_status']), int(r['evidence_count'] or 0))}</td><td>{r['evidence_count']}</td><td>{escape(r['recommended_action'])}</td></tr>" for r in coverage)
    return _page("Flora Live Source Coverage", f"<h1>Source Coverage</h1><span hidden>Live source coverage</span>{summary}<section class='card'><p>Governed source-specific collection only: no LLMs, no databases, and no broad crawling.</p></section><table><thead><tr><th>Source ID</th><th>Organisation</th><th>Source</th><th>Type</th><th>Canonical/display URL and status</th><th>Enabled</th><th>Evidence tier</th><th>Visual status</th><th>Evidence count</th><th>Recommended action</th></tr></thead><tbody>{rows}</tbody></table>")


def evidence_page() -> str:
    evidence = read_jsonl(DEFAULT_PATH)
    if not evidence:
        return _page("Flora Evidence Objects", "<h1>Evidence objects</h1><section class='card warn'><strong>No live evidence available.</strong><p>Use <a href='/live/collect'>/live/collect</a> to attempt governed collection. If sources fail, inspect <a href='/live/status'>/live/status</a>.</p></section>")
    rows = "".join(_evidence_row(e) for e in evidence[-100:])
    diagnostics = read_jsonl(__import__('cios.applications.flora.live.store', fromlist=['DEFAULT_DIAGNOSTICS_PATH']).DEFAULT_DIAGNOSTICS_PATH)
    accepted = len([e for e in evidence if e.get('accepted_for_claims', True)])
    rejected = sum(int(d.get('rejected_evidence_count') or 0) for d in diagnostics)
    downgraded = sum(int(d.get('downgraded_evidence_count') or 0) for d in diagnostics)
    unsupported = [u for d in diagnostics for u in d.get('unsupported_interpretations', [])]
    unsupported_rows = "".join(f"<tr><td>{escape(str(u.get('snippet','')))}</td><td>{escape(str(u.get('attempted_classification','')))}</td><td>{escape(str(u.get('rejection_reason','')))}</td><td>{escape(str(u.get('safer_interpretation','')))}</td></tr>" for u in unsupported[-50:])
    metrics = aggregate_live_evidence(unique_live_evidence(evidence))
    quality_rows = "".join(f"<tr><td>{escape(org)}</td><td>{m.accepted_evidence_count}</td><td>{m.rejected_evidence_count}</td><td>{m.downgraded_evidence_count}</td><td>{escape(str(m.top_receipts[:1]))}</td><td>{escape(str(m.weakest_receipts[:1]))}</td><td>{escape(', '.join(m.insufficient_claims) or 'None')}</td></tr>" for org, m in sorted(metrics.items()))
    return _page("Flora Evidence Objects", f"<h1>Evidence objects</h1><section class='card'><h2>Evidence quality gate</h2><ul><li>Evidence accepted: {accepted}</li><li>Evidence rejected: {rejected}</li><li>Evidence downgraded: {downgraded}</li></ul></section><section class='card'><h2>Organisation evidence quality</h2><table><thead><tr><th>Organisation</th><th>Accepted</th><th>Rejected</th><th>Downgraded</th><th>Strongest evidence</th><th>Weakest evidence</th><th>Claims with insufficient support</th></tr></thead><tbody>{quality_rows}</tbody></table></section><table><thead><tr><th>Organisation</th><th>Source</th><th>Source fetch URL</th><th>Source display URL</th><th>Type</th><th>Snippet</th><th>Condition</th><th>Capability</th><th>Relevance</th><th>Confidence</th><th>Quality</th><th>Extracted</th></tr></thead><tbody>{rows}</tbody></table><section class='card warn'><h2>Unsupported Interpretation diagnostics</h2><table><thead><tr><th>Snippet</th><th>Attempted classification</th><th>Rejection reasons</th><th>Safer interpretation</th></tr></thead><tbody>{unsupported_rows or '<tr><td colspan="4">None recorded.</td></tr>'}</tbody></table></section>")


def _evidence_row(e: dict[str, Any]) -> str:
    return f"<tr><td>{escape(str(e.get('organisation','')))}</td><td>{escape(str(e.get('source_name','')))}</td><td>{link_or_label(e.get('source_url'))}</td><td>{link_or_label(e.get('source_url'), 'display URL')}</td><td>{escape(str(e.get('source_type','')))}</td><td>{escape(str(e.get('snippet','')))}</td><td>{escape(str(e.get('commercial_condition','')))}</td><td>{escape(str(e.get('likely_capability','')))}</td><td>{escape(str(e.get('relevance_level','')))}</td><td>{escape(str(e.get('confidence','')))}</td><td>{escape(str(e.get('overall_evidence_quality','')))}</td><td>{escape(str(e.get('extraction_timestamp','')))}</td></tr>"


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
