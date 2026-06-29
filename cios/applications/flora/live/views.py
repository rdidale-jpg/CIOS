"""HTML views for Flora live evidence."""
from __future__ import annotations

from html import escape
from typing import Any

from cios.applications.flora.live.collect import current_status
from cios.applications.flora.live.store import DEFAULT_PATH, read_jsonl


def live_banner_html() -> str:
    evidence = read_jsonl(DEFAULT_PATH)
    if evidence:
        sources = {item.get("source_id") or item.get("source_name") for item in evidence}
        return f"<section class='card action'><strong>LIVE EVIDENCE USED</strong> — {len(evidence)} evidence objects from {len(sources)} sources. <a href='/live'>Open live dashboard</a></section>"
    return "<section class='card action'><strong>NO LIVE EVIDENCE AVAILABLE</strong> — use <a href='/live/collect'>/live/collect</a> to attempt collection.</section>"


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{escape(title)}</title><style>body{{font-family:Inter,Arial,sans-serif;margin:2rem auto;max-width:1100px;line-height:1.5;color:#17211b}}a{{color:#185c4d}}.card{{border:1px solid #ded8ce;border-radius:14px;padding:18px;margin:14px 0}}.warn{{background:#fff7e6}}.ok{{background:#eef8f1}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #eee;padding:8px;text-align:left;vertical-align:top}}code{{background:#f4f4f4;padding:2px 4px}}</style></head><body><nav><a href='/'>Home</a> · <a href='/live'>Live</a> · <a href='/live/collect'>Run collection</a> · <a href='/live/status'>Status JSON</a> · <a href='/live/evidence'>Evidence</a></nav>{body}</body></html>"""


def dashboard() -> str:
    status = current_status()
    body = f"""<h1>Flora Live Evidence</h1>{live_banner_html()}<section class='card'><h2>Status</h2><ul><li>Last collection time: {escape(str(status['last_collection_time'] or 'Never'))}</li><li>Sources attempted: {status['sources_attempted']}</li><li>Sources succeeded: {status['sources_succeeded']}</li><li>Sources failed: {status['sources_failed']}</li><li>Evidence objects collected: {status['evidence_objects_collected']}</li></ul><p><a href='/live/collect'>Run live collection now</a> · <a href='/live/evidence'>View evidence</a></p></section><section class='card warn'><h2>Storage note</h2><p>Live evidence is stored in local JSONL. Render free-tier filesystems may be ephemeral and evidence may reset on redeploy; this is acceptable for pilot v0.2. Persistent storage is a later decision.</p></section>"""
    return _page("Flora Live Evidence", body)


def collection_result(result: dict[str, Any]) -> str:
    rows = "".join(f"<tr><td>{escape(d['source_id'])}</td><td>{escape(d['organisation'])}</td><td>{escape(d['source_name'])}</td><td>{escape(str(d['success']))}</td><td>{escape(str(d.get('http_status') or d.get('error') or ''))}</td><td>{d['evidence_count']}</td><td>{escape(d['attempted_at'])}</td></tr>" for d in result["diagnostics"])
    return _page("Flora Live Collection Result", f"<h1>Live collection complete</h1><section class='card'><p>Attempted {result['sources_attempted']} sources; succeeded {result['sources_succeeded']}; failed {result['sources_failed']}; created {result['evidence_objects_created']} evidence objects.</p><p><a href='/live/evidence'>View evidence</a></p></section><table><thead><tr><th>Source ID</th><th>Organisation</th><th>Source</th><th>Success</th><th>Status/error</th><th>Evidence</th><th>Attempted</th></tr></thead><tbody>{rows}</tbody></table>")


def evidence_page() -> str:
    evidence = read_jsonl(DEFAULT_PATH)
    if not evidence:
        return _page("Flora Live Evidence Objects", "<h1>Live evidence objects</h1><section class='card warn'><strong>No live evidence available.</strong><p>Use <a href='/live/collect'>/live/collect</a> to attempt governed collection. If sources fail, inspect <a href='/live/status'>/live/status</a>.</p></section>")
    rows = "".join(_evidence_row(e) for e in evidence[-100:])
    return _page("Flora Live Evidence Objects", f"<h1>Live evidence objects</h1><table><thead><tr><th>Organisation</th><th>Source</th><th>URL</th><th>Type</th><th>Snippet</th><th>Condition</th><th>Capability</th><th>Confidence</th><th>Extracted</th></tr></thead><tbody>{rows}</tbody></table>")


def _evidence_row(e: dict[str, Any]) -> str:
    return f"<tr><td>{escape(str(e.get('organisation','')))}</td><td>{escape(str(e.get('source_name','')))}</td><td><a href='{escape(str(e.get('source_url','')))}'>{escape(str(e.get('source_url','')))}</a></td><td>{escape(str(e.get('source_type','')))}</td><td>{escape(str(e.get('snippet','')))}</td><td>{escape(str(e.get('commercial_condition','')))}</td><td>{escape(str(e.get('likely_capability','')))}</td><td>{escape(str(e.get('confidence','')))}</td><td>{escape(str(e.get('extraction_timestamp','')))}</td></tr>"
