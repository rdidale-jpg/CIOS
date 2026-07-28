"""Executive-first, read-only composition over an imported candidate package.

This module deliberately owns no intelligence.  It composes the package and
candidate staging read models and links back to their existing inspection and
governance owners.
"""
from __future__ import annotations

from collections import Counter
from html import escape
from typing import Any

from cios.applications.flora.access import can_access_enterprise
from cios.applications.flora.workspace.views import _page

from .registry import BlueprintPackageRegistry
from .twin_governance import project_twin_identity
from .validator import BlueprintPackageValidator, can_inspect_blueprint_package


THEMES = (
    ("market-condition", "Market condition", ("market", "industry", "sector", "economic")),
    ("financial-pressure", "Financial pressure", ("financial", "cost", "revenue", "margin", "funding", "investment")),
    ("regulation", "Regulation", ("regulat", "policy", "compliance", "mandate", "legislation")),
    ("technology", "Technology and infrastructure", ("technology", "digital", "data", "cloud", "ai ", "infrastructure", "network")),
    ("customer", "Customer and adoption", ("customer", "citizen", "adoption", "demand", "experience")),
    ("ecosystem", "Competitors and ecosystem", ("compet", "partner", "supplier", "ecosystem", "participant")),
)


def executive_workspace_page(import_run_id: str, headers: Any) -> tuple[str, int]:
    """Render provisional executive understanding without changing candidate state."""
    package = next((item for item in BlueprintPackageRegistry().list()
                    if item.import_run_id == import_run_id), None)
    if package is None:
        return _page("Executive Intelligence Workspace unavailable", "<section class='hero'><h1>Executive Intelligence Workspace unavailable</h1><p>The import record could not be found.</p></section>"), 404
    if (not can_access_enterprise(headers, package.identity.enterprise_id, package.workspace_id)
            or not can_inspect_blueprint_package(headers, package)):
        return _page("Executive Intelligence Workspace access denied", "<section class='hero'><h1>Access denied</h1><p>You do not have access to this imported Twin.</p></section>"), 403

    summary = BlueprintPackageValidator().staging_summary(import_run_id) or {}
    candidates = list(summary.get("candidates") or ())
    inspection = package.package_inspection or {}
    identity = project_twin_identity(package)
    title = str(inspection.get("twin_title") or inspection.get("package_title")
                or identity.primary_subject_name or package.identity.package_id)
    unresolved_scope = identity.status == "ambiguous" or not (
        identity.primary_subject_id and identity.governed_scope and identity.canonical_owner
    )
    mission = inspection.get("commercial_mission") or inspection.get("commercial_mission_context")

    body = _styles() + _hero(title, inspection, unresolved_scope, candidates)
    body += _narrative(candidates, inspection, mission)
    body += _themed_conclusions(candidates, import_run_id)
    body += _attention(candidates, import_run_id)
    body += _limitations(candidates, summary, inspection, mission, unresolved_scope)
    body += _progressive_navigation(import_run_id)
    return _page(f"Executive Intelligence — {title}", body), 200


def _hero(title: str, inspection: dict[str, Any], unresolved_scope: bool,
          candidates: list[dict[str, Any]]) -> str:
    twin_type = str(inspection.get("twin_type") or "proposed Twin").replace("_", " ").title()
    provisional = ("<p class='workspace-caveat'><strong>Executive understanding is provisional because "
                   "the Twin identity and governed scope have not yet been confirmed.</strong></p>"
                   if unresolved_scope else
                   "<p class='workspace-caveat'><strong>Executive understanding is provisional while this imported intelligence remains a candidate.</strong></p>")
    return f"""<nav class='executive-path' aria-label='Executive intelligence depth'><strong>Executive understanding</strong><span>Commercial relevance</span><span>Why now</span><span>Why believe it</span><a href='#evidence-inspection'>Evidence inspection</a><a href='#candidate-governance'>Candidate governance</a></nav>
    <header class='hero executive-workspace'><p class='eyebrow'>Executive Intelligence Workspace</p><h1>{escape(title)}</h1>
    <p>{escape(twin_type)} · {len(candidates)} staged intelligence records</p>{provisional}
    <div class='status-key'><span><b>Candidate intelligence</b> — imported, not governed</span><span><b>Provisional interpretation</b> — composed for understanding, not persisted</span></div></header>"""


def _narrative(candidates: list[dict[str, Any]], inspection: dict[str, Any], mission: Any) -> str:
    counts = Counter(str(c.get("candidate_object_class") or "unclassified") for c in candidates)
    accepted = sum(c.get("validation_status") == "accepted" for c in candidates)
    organisations = sum(_semantic_text(c).find(word) >= 0 for c in candidates for word in ("enterprise", "participant") )
    timing = _find_named(candidates, ("reinvention timing", "transformation timing", "urgency"))
    opportunities = [c for c in candidates if "opportun" in _semantic_text(c)]
    timing_text = _statement(timing) if timing else "Reinvention Timing is not supported by the imported intelligence."
    opportunity_text = (f"{len(opportunities)} candidate record(s) refer to opportunities; inspect each before treating it as a hypothesis."
                        if opportunities else "No supported Opportunity Hypothesis is available in this package.")
    mission_text = ("Commercial Mission context is available and is used only to organise supplied intelligence."
                    if mission else "Personal commercial prioritisation is not yet applied because no Commercial Mission is available.")
    return f"""<section class='card' id='executive-understanding'><h2>Executive understanding</h2>
    <p>This package contributes <strong>{accepted} reviewable candidate records</strong>. It has not added governed intelligence. The brief below is a neutral, evidence-bounded reading of what the package contains.</p>
    <div class='grid executive-summary-grid'><article><h3>Current condition and material change</h3><p>Candidate conclusions are grouped below by executive theme rather than governance class.</p></article>
    <article id='commercial-relevance'><h3>Commercial relevance</h3><p>{escape(mission_text)}</p></article>
    <article id='why-now'><h3>Why now</h3><p>{escape(timing_text)}</p></article>
    <article><h3>Organisations deserving attention</h3><p>{organisations or counts.get('entity', 0)} organisation or participant signals are available for investigation; this is not a prospect score.</p></article>
    <article><h3>Opportunity Hypotheses</h3><p>{escape(opportunity_text)}</p></article></div></section>"""


def _themed_conclusions(candidates: list[dict[str, Any]], run_id: str) -> str:
    assigned: set[str] = set()
    sections: list[str] = []
    material = [c for c in candidates if c.get("candidate_object_class") in
                {"fact", "observation", "human_knowledge", "entity", "unknown", "contradiction"}]
    for key, label, terms in THEMES:
        matches = [c for c in material if any(term in _semantic_text(c) for term in terms)][:5]
        assigned.update(str(c.get("candidate_record_id")) for c in matches)
        if matches:
            sections.append(f"<section class='theme-group' id='{key}'><h3>{label}</h3>" +
                            "".join(_conclusion(c, run_id) for c in matches) + "</section>")
    other = [c for c in material if str(c.get("candidate_record_id")) not in assigned
             and c.get("candidate_object_class") not in {"unknown", "contradiction"}][:5]
    if other:
        sections.append("<section class='theme-group'><h3>Other material change</h3>" +
                        "".join(_conclusion(c, run_id) for c in other) + "</section>")
    if not sections:
        sections.append("<p>No material conclusions could be composed from the staged package. Inspect the package evidence and limitations rather than inferring a narrative.</p>")
    return "<section class='card' id='material-intelligence'><h2>Material candidate intelligence</h2><p>Each conclusion retains its candidate status and can be expanded to inspect support and provenance.</p>" + "".join(sections) + "</section>"


def _conclusion(candidate: dict[str, Any], run_id: str) -> str:
    statement = _statement(candidate)
    payload = candidate.get("payload") or {}
    evidence = payload.get("evidence_refs") or payload.get("source_refs") or payload.get("sources") or []
    if isinstance(evidence, str):
        evidence = [evidence]
    supported = bool(evidence) or candidate.get("candidate_object_class") == "evidence"
    support = ", ".join(map(str, evidence[:8])) if evidence else "No explicit Evidence reference was supplied; treat this conclusion as unsupported."
    status = str(candidate.get("validation_status") or "candidate")
    source = str(candidate.get("source_file") or "Imported package")
    location = candidate.get("source_location") or {}
    record_id = str(candidate.get("candidate_record_id") or candidate.get("original_source_id") or "candidate")
    return f"""<article class='executive-conclusion'><p class='pill'>Candidate intelligence · {escape(status)}</p><h4>{escape(statement)}</h4>
    <details><summary>Why believe it? Inspect provenance and governance status</summary><p><strong>Support:</strong> {escape(support)}</p>
    <p><strong>Evidence status:</strong> {'Referenced support in candidate package' if supported else 'Unsupported candidate conclusion'}.</p>
    <p><strong>Provenance:</strong> {escape(source)} · {escape(str(location) if location else 'location not supplied')} · <code>{escape(record_id)}</code></p>
    <p><strong>Governance status:</strong> Candidate only; not promoted to governed intelligence.</p>
    <p><a href='/blueprint-import/{escape(run_id)}/inspect#technical-diagnostics'>Inspect package evidence and lineage</a></p></details></article>"""


def _attention(candidates: list[dict[str, Any]], run_id: str) -> str:
    unknowns = [c for c in candidates if c.get("candidate_object_class") == "unknown"]
    contradictions = [c for c in candidates if c.get("candidate_object_class") == "contradiction"]
    items = unknowns[:4] + contradictions[:4]
    cards = "".join(_conclusion(c, run_id) for c in items)
    if not cards:
        cards = "<p>No explicit Unknown or Contradiction records were supplied. This does not establish completeness.</p>"
    return f"<section class='card' id='recommended-investigation'><h2>Principal unknowns and recommended investigation</h2><p>Investigate the following gaps or challenges before relying on candidate conclusions for action.</p>{cards}</section>"


def _limitations(candidates: list[dict[str, Any]], summary: dict[str, Any], inspection: dict[str, Any],
                 mission: Any, unresolved_scope: bool) -> str:
    counts = Counter(str(c.get("candidate_object_class") or "unclassified") for c in candidates)
    unsupported = sum(not ((c.get("payload") or {}).get("evidence_refs") or
                           (c.get("payload") or {}).get("source_refs"))
                      for c in candidates if c.get("candidate_object_class") in {"fact", "observation", "human_knowledge"})
    limitations = []
    if unresolved_scope: limitations.append("Twin identity and governed scope are not confirmed")
    if not mission: limitations.append("Commercial Mission is unavailable; personal prioritisation is not applied")
    if not _find_named(candidates, ("reinvention timing", "transformation timing")): limitations.append("Reinvention Timing is not supported")
    if unsupported: limitations.append(f"{unsupported} candidate conclusion(s) have no explicit Evidence reference")
    if summary.get("warnings"): limitations.append(f"{len(summary['warnings'])} import warning(s) require inspection")
    if summary.get("errors"): limitations.append(f"{len(summary['errors'])} blocking import error(s) limit this brief")
    limitations.append("Candidate intelligence has not been promoted to governed intelligence")
    detail = "".join(f"<li>{escape(item)}</li>" for item in limitations)
    return f"""<section class='card' id='coverage-limitations'><h2>Coverage and Limitations</h2>
    <p><strong>Coverage:</strong> {len(candidates)} candidate records · {counts.get('evidence', 0)} Evidence · {counts.get('unknown', 0)} Unknowns · {counts.get('contradiction', 0)} Contradictions · 0 newly governed records.</p>
    <ul>{detail}</ul><details><summary>Inspect all import warnings and missing metadata</summary><p>Detailed package fields, validation warnings and technical diagnostics remain in Import Inspect. Missing values are aggregated here so they do not overwhelm executive understanding.</p></details></section>"""


def _progressive_navigation(run_id: str) -> str:
    run = escape(run_id)
    return f"""<section class='card' id='evidence-inspection'><h2>Continue investigation</h2>
    <p><a class='button primary' href='/blueprint-import/{run}/inspect#technical-diagnostics'>Inspect evidence and import decisions</a></p></section>
    <section class='card' id='candidate-governance'><h2>Candidate governance</h2><p>When executive understanding is sufficient, continue to the existing workflow to resolve scope, review dispositions and decide whether anything should become governed.</p>
    <p><a href='/blueprint-import/{run}/review'>Review candidate governance</a> · <a href='/blueprint-import/{run}/review#identity-resolution'>Resolve Twin scope</a> · <a href='/blueprint-import/{run}/inspect'>Inspect import decisions</a></p></section>"""


def _semantic_text(candidate: dict[str, Any]) -> str:
    return (str(candidate.get("candidate_object_class") or "") + " " +
            str(candidate.get("original_source_id") or "") + " " +
            " ".join(f"{key} {value}" for key, value in (candidate.get("payload") or {}).items())).casefold()


def _statement(candidate: dict[str, Any] | None) -> str:
    if not candidate:
        return ""
    payload = candidate.get("payload") or {}
    for key in ("statement", "summary", "title", "display_name", "name", "description", "value"):
        if payload.get(key):
            return str(payload[key])
    return str(candidate.get("original_source_id") or "Candidate conclusion")


def _find_named(candidates: list[dict[str, Any]], terms: tuple[str, ...]) -> dict[str, Any] | None:
    return next((candidate for candidate in candidates if any(term in _semantic_text(candidate) for term in terms)), None)


def _styles() -> str:
    return """<style>.executive-path{display:flex;gap:.65rem;flex-wrap:wrap;align-items:center;margin:0 0 1rem}.executive-path span,.executive-path a,.executive-path strong{padding:.45rem .7rem;border-radius:1rem;background:#eef5f2}.workspace-caveat{border-left:4px solid #b46b00;padding:.75rem;background:#fff8e8}.status-key{display:flex;gap:1rem;flex-wrap:wrap}.executive-summary-grid article{border-top:3px solid #185c4d}.theme-group{margin:1.5rem 0}.executive-conclusion{border-left:4px solid #c98b2e;padding:1rem;margin:.75rem 0;background:#fffdf8}.executive-conclusion h4{margin:.3rem 0}.executive-conclusion details{margin-top:.75rem}</style>"""
