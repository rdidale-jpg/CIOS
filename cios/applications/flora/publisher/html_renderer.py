"""HTML renderer for Flora executive publications."""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

CSS = """
:root { --flora-blue:#0b4f8a; --flora-navy:#102033; --muted:#64748b; --line:#dbe4ef; }
* { box-sizing: border-box; }
body { margin: 0; background: #f4f7fb; color: var(--flora-navy); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.45; }
.publication { max-width: 980px; margin: 0 auto; padding: 28px; }
.page { min-height: 920px; background: #fff; margin: 0 0 24px; padding: 54px 60px 44px; border: 1px solid var(--line); box-shadow: 0 12px 30px rgba(15,35,60,.08); position: relative; }
h1 { color: var(--flora-blue); font-size: 42px; letter-spacing: .08em; margin: 0 0 8px; }
h2 { color: var(--flora-blue); border-bottom: 2px solid var(--line); padding-bottom: 10px; margin: 0 0 22px; font-size: 25px; }
h3 { color: var(--flora-blue); margin: 20px 0 8px; font-size: 16px; }
.kicker { color: var(--muted); text-transform: uppercase; letter-spacing: .14em; font-size: 12px; font-weight: 700; }
.subtitle { font-size: 30px; margin: 10px 0 28px; }
.meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 42px; }
.meta, .card { border: 1px solid var(--line); border-left: 4px solid var(--flora-blue); padding: 14px 16px; border-radius: 8px; background: #fbfdff; }
.label { display:block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }
ul { padding-left: 20px; }
li { margin-bottom: 10px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #eaf2fb; color: var(--flora-blue); text-align: left; padding: 9px; border-bottom: 1px solid var(--line); }
td { padding: 9px; border-bottom: 1px solid var(--line); vertical-align: top; }
.footer { position:absolute; bottom: 18px; left:60px; right:60px; color: var(--muted); font-size: 11px; display:flex; justify-content:space-between; border-top: 1px solid var(--line); padding-top: 8px; }
.placeholder { color: var(--muted); font-style: italic; }
@media print { body { background:#fff; } .publication { padding:0; } .page { box-shadow:none; border:0; page-break-after:always; margin:0; } }
"""

def _e(value: Any) -> str:
    return escape(str(value))

def _footer(ctx: dict[str, Any], page: int) -> str:
    return f"<div class='footer'><span>Flora Pilot · Version {_e(ctx['version'])}</span><span>Generated {_e(ctx['generated_timestamp'])}</span><span>Page {page}</span></div>"

def render_html(ctx: dict[str, Any]) -> str:
    pages: list[str] = []
    pages.append(f"""<section class='page cover'><div class='kicker'>Confidential (Pilot)</div><h1>FLORA</h1><div class='subtitle'>Morning Edition</div><div class='meta-grid'><div class='meta'><span class='label'>Date</span>{_e(ctx['publication_date_label'])}</div><div class='meta'><span class='label'>Reading time</span>{ctx['reading_time']} minutes</div><div class='meta'><span class='label'>Version</span>{_e(ctx['version'])}</div><div class='meta'><span class='label'>Edition</span>Executive intelligence briefing</div></div>{_footer(ctx,1)}</section>""")
    pages.append(f"<section class='page'><h2>Executive Summary</h2><ul>{''.join(f'<li>{_e(b)}</li>' for b in ctx['executive_summary'])}</ul>{_footer(ctx,2)}</section>")
    po = ctx['priority_opportunity']
    pages.append(f"""<section class='page'><h2>Today's Priority Opportunity</h2>{''.join(f"<h3>{_e(k)}</h3><p>{_e(v)}</p>" for k,v in po.items())}{_footer(ctx,3)}</section>""")
    rows = ''.join(f"<tr><td>{_e(r['organisation'])}</td><td>{_e(r['sector'])}</td><td>{r['condition_strength']}</td><td>{r['ai_opportunity']}</td><td>{_e(r['movement'])}</td><td>{r['confidence']}</td></tr>" for r in ctx['top_organisations'])
    pages.append(f"<section class='page'><h2>Top Five Organisations</h2><table><thead><tr><th>Organisation</th><th>Sector</th><th>Condition Strength</th><th>AI Reinvention Opportunity</th><th>Movement</th><th>Confidence</th></tr></thead><tbody>{rows}</tbody></table>{_footer(ctx,4)}</section>")
    cond = ''.join(f"<div class='card'><h3>{_e(c['condition'])}</h3><p><b>Strength:</b> {c['strength']} · <b>Trend:</b> {_e(c['trend'])}</p><p><b>Affected Organisations:</b> {_e(', '.join(c['affected_organisations']))}</p><p><b>Primary Drivers:</b> {_e(c['primary_drivers'])}</p></div>" for c in ctx['conditions'])
    pages.append(f"<section class='page'><h2>Emerging Commercial Conditions</h2>{cond}{_footer(ctx,5)}</section>")
    moves = ''.join(f"<h3>{_e(s['title'])}</h3><ul>{''.join(f'<li>{_e(x)}</li>' for x in s['items'])}</ul>" for s in ctx['movements'])
    pages.append(f"<section class='page'><h2>Executive &amp; Market Movements</h2>{moves}{_footer(ctx,6)}</section>")
    comp = ''.join(f"<h3>{_e(k)}</h3><p>{_e(v)}</p>" for k,v in ctx['competitive_intelligence'].items())
    pages.append(f"<section class='page'><h2>Competitive Intelligence</h2>{comp}{_footer(ctx,7)}</section>")
    acts = ''.join(f"<div class='card'><h3>Priority {a['priority']} · {_e(a['organisation'])}</h3><p><b>Reason:</b> {_e(a['reason'])}</p><p><b>Expected Commercial Value:</b> {_e(a['expected_value'])}</p><p><b>Confidence:</b> {a['confidence']}</p><p><b>Evidence references:</b> {_e(', '.join(a['evidence_references']))}</p></div>" for a in ctx['recommended_actions'])
    pages.append(f"<section class='page'><h2>Recommended Actions</h2>{acts}{_footer(ctx,8)}</section>")
    teach = ''.join(f"<div class='card'><span class='label'>{_e(k)}</span><span class='placeholder'>{_e(v)}</span></div>" for k,v in ctx['teach_flora'].items())
    pages.append(f"<section class='page'><h2>Teach Flora</h2>{teach}{_footer(ctx,9)}</section>")
    return "<!doctype html><html><head><meta charset='utf-8'><title>Flora Morning Edition</title><link rel='stylesheet' href='assets/flora_publisher.css'></head><body><main class='publication'>" + ''.join(pages) + "</main></body></html>"

def write_html(ctx: dict[str, Any], output_path: Path) -> Path:
    (output_path.parent / "assets").mkdir(parents=True, exist_ok=True)
    (output_path.parent / "assets" / "flora_publisher.css").write_text(CSS, encoding="utf-8")
    output_path.write_text(render_html(ctx), encoding="utf-8")
    return output_path
