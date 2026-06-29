"""HTML views for Flora live evidence."""
from __future__ import annotations

from html import escape
from typing import Any

from cios.applications.flora.live.collect import current_status, source_coverage
from collections import Counter
from cios.applications.flora.live.store import DEFAULT_PATH, load_evidence_fingerprints, read_jsonl
from cios.applications.flora.live.aggregation import aggregate_live_evidence, unique_live_evidence


def live_banner_html() -> str:
    evidence = read_jsonl(DEFAULT_PATH)
    if evidence:
        sources = {item.get("source_id") or item.get("source_name") for item in evidence}
        unique_count = len(load_evidence_fingerprints(DEFAULT_PATH))
        return f"<section class='card action'><strong>LIVE EVIDENCE USED</strong> — {unique_count} unique evidence objects from {len(sources)} sources. <a href='/live'>Open live dashboard</a></section>"
    return "<section class='card action'><strong>NO LIVE EVIDENCE AVAILABLE</strong> — use <a href='/live/collect'>/live/collect</a> to attempt collection.</section>"


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{escape(title)}</title><style>body{{font-family:Inter,Arial,sans-serif;margin:2rem auto;max-width:1100px;line-height:1.5;color:#17211b}}a{{color:#185c4d}}.card{{border:1px solid #ded8ce;border-radius:14px;padding:18px;margin:14px 0}}.warn{{background:#fff7e6}}.ok{{background:#eef8f1}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #eee;padding:8px;text-align:left;vertical-align:top}}code{{background:#f4f4f4;padding:2px 4px}}</style></head><body><nav><a href='/'>Home</a> · <a href='/live'>Live</a> · <a href='/live/collect'>Run collection</a> · <a href='/live/status'>Status JSON</a> · <a href='/live/sources'>Sources</a> · <a href='/live/evidence'>Evidence</a></nav>{body}</body></html>"""


def dashboard() -> str:
    status = current_status()
    metrics = aggregate_live_evidence(unique_live_evidence(read_jsonl(DEFAULT_PATH)))
    org_rows = "".join(f"<tr><td>{escape(org)}</td><td>{m.live_evidence_count}</td><td>{m.unique_source_count}</td><td>{escape(', '.join(m.strongest_conditions))}</td><td>{escape(', '.join(m.strongest_capabilities))}</td><td>{escape(m.evidence_freshness)}</td></tr>" for org, m in sorted(metrics.items(), key=lambda kv: kv[1].live_evidence_count, reverse=True))
    body = f"""<h1>Flora Live Evidence</h1>{live_banner_html()}<section class='card'><h2>Status</h2><ul><li>Last collection time: {escape(str(status['last_collection_time'] or 'Never'))}</li><li>Sources attempted: {status['sources_attempted']}</li><li>Sources succeeded: {status['sources_succeeded']}</li><li>Sources failed: {status['sources_failed']}</li><li>Unique evidence objects: {status['total_unique_evidence_objects']}</li></ul><p><a href='/live/collect'>Run live collection now</a> · <a href='/live/sources'>Source coverage</a> · <a href='/live/evidence'>View evidence</a></p></section><section class='card'><h2>Live organisation aggregation</h2><table><thead><tr><th>Organisation</th><th>Evidence</th><th>Sources</th><th>Strongest conditions</th><th>Strongest capabilities</th><th>Freshness</th></tr></thead><tbody>{org_rows or '<tr><td colspan="6">No live aggregation available.</td></tr>'}</tbody></table></section><section class='card warn'><h2>Storage note</h2><p>Live evidence is stored in local JSONL. Render free-tier filesystems may be ephemeral and evidence may reset on redeploy; this is acceptable for pilot v0.2. Persistent storage is a later decision.</p></section>"""
    return _page("Flora Live Evidence", body)


def _diagnostic_rows(diagnostics: list[dict[str, Any]]) -> str:
    return "".join(f"<tr><td>{escape(d['source_id'])}</td><td>{escape(d['organisation'])}</td><td>{escape(d['source_name'])}</td><td>{escape(str(d.get('source_type','')))}</td><td><a href='{escape(str(d.get('url','')))}'>{escape(str(d.get('url','')))}</a></td><td>{escape(str(d.get('status') or ('succeeded' if d.get('success') else 'failed')))}</td><td>{escape(str(d.get('http_status') or d.get('error') or ''))}</td><td>{d.get('evidence_count',0)}</td><td>{escape(str(d.get('last_attempted') or d.get('attempted_at') or ''))}</td><td>{escape(str(d.get('failure_reason') or ''))}</td></tr>" for d in diagnostics)


def collection_result(result: dict[str, Any]) -> str:
    rows = _diagnostic_rows(result["diagnostics"])
    return _page("Flora Live Collection Result", f"<h1>Live collection complete</h1><section class='card'><p>Attempted {result['sources_attempted']} sources; succeeded {result['sources_succeeded']}; failed {result['sources_failed']}; produced evidence from {result.get('sources_with_evidence', 0)} sources; extracted {result['evidence_objects_extracted']} evidence objects; added {result['new_evidence_added']} new; skipped {result['duplicate_evidence_skipped']} duplicates; total unique evidence objects: {result['total_unique_evidence_objects']}.</p><p><a href='/live/evidence'>View evidence</a> · <a href='/live/sources'>Source coverage</a></p></section><table><thead><tr><th>Source ID</th><th>Organisation</th><th>Source</th><th>Type</th><th>URL</th><th>Status</th><th>HTTP/error</th><th>Evidence</th><th>Last attempted</th><th>Failure reason</th></tr></thead><tbody>{rows}</tbody></table>")


def sources_page() -> str:
    coverage = source_coverage()
    orgs = {r["organisation"] for r in coverage}
    covered = {r["organisation"] for r in coverage if r["enabled"]}
    uncovered = sorted(orgs - covered)
    sector_counts = Counter(r["sector"] for r in coverage if r["enabled"])
    type_counts = Counter(r["source_type"] for r in coverage if r["enabled"])
    latest = current_status()
    summary = f"""<section class='card'><h2>Coverage summary</h2><ul><li>Total organisations configured: {len(orgs)}</li><li>Organisations with at least one enabled source: {len(covered)}</li><li>Organisations with no source coverage: {len(uncovered)}</li><li>Total sources: {len(coverage)}</li><li>Latest status: attempted {latest['sources_attempted']}, succeeded {latest['sources_succeeded']}, failed {latest['sources_failed']}</li></ul><h3>Sources by sector</h3><p>{escape(str(dict(sorted(sector_counts.items()))))}</p><h3>Sources by source_type</h3><p>{escape(str(dict(sorted(type_counts.items()))))}</p><h3>Organisations with no source coverage</h3><p>{escape(', '.join(uncovered) or 'None')}</p></section>"""
    rows = "".join(f"<tr><td>{escape(r['source_id'])}</td><td>{escape(r['organisation'])}</td><td>{escape(r['source_name'])}</td><td>{escape(r['source_type'])}</td><td><a href='{escape(str(r['url']))}'>{escape(str(r['url']))}</a></td><td>{'enabled' if r['enabled'] else 'disabled'}</td><td>{escape(r['evidence_tier'])}</td><td>{escape(str(r['last_status']))}</td><td>{r['evidence_count']}</td><td>{escape(r['recommended_action'])}</td></tr>" for r in coverage)
    return _page("Flora Live Source Coverage", f"<h1>Live source coverage</h1>{summary}<section class='card'><p>Governed source-specific collection only: no LLMs, no databases, and no broad crawling.</p></section><table><thead><tr><th>Source ID</th><th>Organisation</th><th>Source</th><th>Type</th><th>URL</th><th>Enabled</th><th>Evidence tier</th><th>Last status</th><th>Evidence count</th><th>Recommended action</th></tr></thead><tbody>{rows}</tbody></table>")


def evidence_page() -> str:
    evidence = read_jsonl(DEFAULT_PATH)
    if not evidence:
        return _page("Flora Live Evidence Objects", "<h1>Live evidence objects</h1><section class='card warn'><strong>No live evidence available.</strong><p>Use <a href='/live/collect'>/live/collect</a> to attempt governed collection. If sources fail, inspect <a href='/live/status'>/live/status</a>.</p></section>")
    rows = "".join(_evidence_row(e) for e in evidence[-100:])
    return _page("Flora Live Evidence Objects", f"<h1>Live evidence objects</h1><table><thead><tr><th>Organisation</th><th>Source</th><th>URL</th><th>Type</th><th>Snippet</th><th>Condition</th><th>Capability</th><th>Confidence</th><th>Quality</th><th>Extracted</th></tr></thead><tbody>{rows}</tbody></table>")


def _evidence_row(e: dict[str, Any]) -> str:
    return f"<tr><td>{escape(str(e.get('organisation','')))}</td><td>{escape(str(e.get('source_name','')))}</td><td><a href='{escape(str(e.get('source_url','')))}'>{escape(str(e.get('source_url','')))}</a></td><td>{escape(str(e.get('source_type','')))}</td><td>{escape(str(e.get('snippet','')))}</td><td>{escape(str(e.get('commercial_condition','')))}</td><td>{escape(str(e.get('likely_capability','')))}</td><td>{escape(str(e.get('confidence','')))}</td><td>{escape(str(e.get('overall_evidence_quality','')))}</td><td>{escape(str(e.get('extraction_timestamp','')))}</td></tr>"
