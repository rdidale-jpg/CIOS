"""Read-only pilot diagnostics for imported Twin projections.

This module only explains objects already produced by the import, semantic
assembly and page projection path. It does not create mappings, promote data or
calculate semantic completeness.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Iterable

from cios.applications.flora.pilot_import import pilot_import_bypass_enabled
from .cios_twin_adapter import MAPPING_VERSION
from .researcher_profile_adapter import CONTRACT as RESEARCHER_CONTRACT, contract_checksum as researcher_contract_checksum
from .intelligence_projection import ExecutiveAssessmentProjection
from .semantic_twin import SemanticObject, SemanticTwin, business_collections, executive_record_view_model

DIAGNOSTIC_LABEL = "PILOT DIAGNOSTICS — NOT EXECUTIVE OUTPUT"
REVIEW_PLAN_VERSION = "review-plan-v1"
PROJECTION_VERSION = "imported-twin-projection-v1"
ADAPTER_VERSION = "industry-twin-delta-adapter-v1"

REASON_CODES = (
    "observation_generated", "no_observation_extractor", "no_observation_profile_match",
    "unsupported_object_family", "unsupported_observation_vocabulary", "missing_subject",
    "missing_predicate", "missing_value", "missing_evidence", "missing_temporal_context",
    "invalid_observation_shape", "source_field_absent", "source_field_unmapped",
    "mapped_value_not_persisted", "semantic_field_missing", "candidate_state_suppressed",
    "assessment_pending", "assessment_not_required_for_factual_display",
    "projection_field_missing", "projection_filtered", "template_fallback_used",
    "explicit_unknown", "contradiction_requires_review", "lineage_only",
    "stale_candidate_representation",
)

INDUSTRY_SECTION_PATHS = {
    "industry definition and scope": ("payload.scope", "payload.industry_definition", "payload.definition", "payload.description", "payload.industry_profile.scope"),
    "subsectors": ("payload.subsectors", "payload.industry_profile.subsectors"),
    "value chain": ("payload.value_chain", "payload.industry_profile.value_chain"),
    "market structure": ("payload.market_structure", "payload.industry_profile.market_structure"),
    "size and economics": ("payload.market_size", "payload.economics", "payload.industry_profile.economics"),
    "leading enterprises": ("payload.leading_enterprises", "payload.enterprises", "payload.industry_profile.leading_enterprises"),
    "participants": ("payload.participants", "payload.market_participants", "payload.industry_profile.participants"),
    "regulatory pressures": ("payload.regulatory_pressures", "payload.pressures.regulatory", "payload.pestle.regulatory"),
    "economic pressures": ("payload.economic_pressures", "payload.pressures.economic", "payload.pestle.economic"),
    "social/customer change": ("payload.social_customer_change", "payload.customer_change", "payload.pestle.social"),
    "technology change": ("payload.technology_change", "payload.technology_pressures", "payload.pestle.technology"),
    "legal/environmental factors": ("payload.legal_environmental_factors", "payload.pestle.legal", "payload.pestle.environmental"),
    "transformation themes": ("payload.transformation_themes", "payload.themes"),
    "qualified insights": ("payload.qualified_insights", "payload.insights", "payload.executive_insights"),
}

ENTERPRISE_FIELD_PATHS = {
    "description/purpose": ("payload.description", "payload.organisation_description", "payload.overview", "payload.purpose"),
    "industry/domain": ("payload.industry", "payload.domain", "payload.domains", "payload.subsectors"),
    "strategy": ("payload.strategy", "payload.strategic_ambition", "payload.market_position"),
    "operating structure": ("payload.operating_structure", "payload.organisation_structure"),
    "financial context": ("payload.financial_context", "payload.financials"),
    "technology": ("payload.technology", "payload.technology_stack"),
    "ecosystem": ("payload.ecosystem", "payload.relationships"),
    "pressures": ("payload.pressures", "payload.material_pressures"),
    "programmes": ("payload.programmes", "payload.transformations"),
    "transformation posture": ("payload.transformation_posture", "payload.reinvention_posture"),
    "evidence links": ("payload.evidence_refs", "payload.evidence", "payload.source_refs"),
}


def pilot_diagnostics_enabled() -> bool:
    env = os.getenv("FLORA_ENVIRONMENT", "").casefold()
    requested = os.getenv("FLORA_PILOT_DIAGNOSTICS", "").casefold() in {"1", "true", "yes", "on"}
    return requested and (env in {"pilot", "test", "testing"} or pilot_import_bypass_enabled())


def deployed_commit_sha() -> str:
    override = os.getenv("FLORA_DEPLOYED_COMMIT_SHA", "").strip()
    if override:
        return override
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).parents[5], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable"


def context_header(package: Any, summary: dict[str, Any]) -> str:
    if not pilot_diagnostics_enabled():
        return ""
    commit = deployed_commit_sha()
    staged_at = str(summary.get("staged_at") or summary.get("created_at") or getattr(package, "received_at", "") or "unknown")
    stale = _is_stale(staged_at, commit)
    rows = {
        "deployed commit SHA": commit,
        "package ID and version": f"{package.identity.package_id} / {package.package_inspection.get('package_version') or package.identity.profile_version}",
        "package SHA-256": package.package_sha256,
        "import run ID": package.import_run_id,
        "import timestamp": str(getattr(package, "received_at", "unknown")),
        "candidate staging timestamp": staged_at,
        "Twin Object Profile version": RESEARCHER_CONTRACT.get("profile_version", "unknown"),
        "adapter version": ADAPTER_VERSION,
        "semantic model version": MAPPING_VERSION,
        "projection version": PROJECTION_VERSION,
        "loaded profile contract": RESEARCHER_CONTRACT.get("document_id", "unknown"),
        "loaded profile version": RESEARCHER_CONTRACT.get("profile_version", "unknown"),
        "loaded profile checksum": researcher_contract_checksum(),
        "Pilot Diagnostic Mode flag": "FLORA_PILOT_DIAGNOSTICS=1",
        "Pilot Diagnostic Mode active": "yes",
        "review-plan version": REVIEW_PLAN_VERSION,
        "candidate or promoted state": "candidate",
        "stale-candidate status": "stale_candidate_representation" if stale else "current-or-unknown",
    }
    body = "".join(f"<tr><th>{escape(k)}</th><td><code>{escape(str(v))}</code></td></tr>" for k, v in rows.items())
    warning = "<p class='warning'><strong>stale_candidate_representation:</strong> Candidate may pre-date deployed semantic implementation.</p>" if stale else ""
    codes = ", ".join(REASON_CODES)
    return f"<aside class='card pilot-diagnostics' role='note'><h2>{DIAGNOSTIC_LABEL}</h2>{warning}<details open><summary>Diagnostic context header</summary><table>{body}</table></details><details><summary>Finite diagnostic reason-code vocabulary</summary><p>{escape(codes)}</p></details></aside>"


def _is_stale(staged_at: str, commit: str) -> bool:
    forced = os.getenv("FLORA_DIAGNOSTICS_FORCE_STALE", "").casefold() in {"1", "true", "yes"}
    if forced:
        return True
    return False


def page_reconciliation(twin: SemanticTwin, page_key: str) -> str:
    if not pilot_diagnostics_enabled(): return ""
    collections = {c.key: c.objects for c in business_collections(twin, include_empty=True)}
    keys = ["industry-overview", "enterprises", "market-participants", "major-programmes", "opportunities", "reinvention-assessments", "evidence-sources", "unknowns", "contradictions"]
    rows=[]
    for key in keys:
        objs = collections.get(key, ())
        source = len(objs); rendered = sum(1 for o in objs if executive_record_view_model(o).fields or o.statement)
        rejected = sum(1 for o in objs if o.validation_status not in {"accepted", ""} or o.residual_reason)
        residual = max(0, source-rendered-rejected)
        status = "balanced" if source == rendered + residual + rejected else "count_mismatch"
        rows.append(f"<tr><td>{escape(key)}</td><td>{source}</td><td>{source}</td><td>{source}</td><td>{source}</td><td>0</td><td>{source}</td><td>{rendered}</td><td>{residual}</td><td>{rejected}</td><td>{status}</td></tr>")
    return "<details class='card pilot-diagnostics'><summary>Page-level diagnostic summary</summary><table><thead><tr><th>Object family</th><th>Source</th><th>Adapted</th><th>Persisted candidate</th><th>Semantic</th><th>Owner-assessed</th><th>Projected</th><th>Rendered</th><th>Residual</th><th>Rejected/quarantined/ignored</th><th>Status</th></tr></thead><tbody>"+"".join(rows)+"</tbody></table></details>"


def field_panel(obj: SemanticObject|None, label: str, expected_paths: Iterable[str], *, rendered: Any="", target: str="", page_field: str="") -> str:
    if not pilot_diagnostics_enabled(): return ""
    paths = tuple(expected_paths)
    present = [(p, _path_value(obj.attributes if obj else {}, p.removeprefix("payload."))) for p in paths]
    selected = next(((p,v) for p,v in present if _present(v)), (paths[0] if paths else target, None))
    contract_selector = _contract_selector(obj, target, page_field, paths)
    explicit_unknown = obj and obj.kind == "unknown" or str(selected[1]).casefold() == "unknown"
    if _present(rendered): reason="observation_generated"
    elif explicit_unknown: reason="explicit_unknown"
    elif selected[1] not in (None,"",[],{},()): reason="projection_field_missing"
    else: reason="source_field_absent"
    path_rows = "".join(f"<tr><td><code>{escape(p)}</code></td><td>{'yes' if _present(v) else 'no'}</td><td>{escape(type(v).__name__ if v is not None else 'absent')}</td><td>{escape(_preview(v))}</td></tr>" for p,v in present)
    obj_id = obj.original_id or obj.record_id if obj else "not applicable"
    obs_attempted = "yes" if obj and obj.kind in {"executive_intelligence", "fact", "observation", "supported_interpreted_observation"} else "no"
    obs_profile = "executive_insight_eligible" if obs_attempted == "yes" else "no observation extractor"
    obs_reason = reason if reason != "observation_generated" else "observation_generated"
    if obs_attempted == "no" and reason == "source_field_absent":
        obs_reason = "source_field_absent"
    elif obs_attempted == "no" and obj:
        obs_reason = "unsupported_object_family"
    owner_invoked = "yes" if obj and any(o in obj.kind for o in ("assessment", "completeness")) else "no"
    projected = "projected" if _present(rendered) else ("omitted" if reason == "source_field_absent" else "rejected")
    legacy_reason = "source_field_present_rendered" if _present(rendered) else reason
    return f"""<details class='pilot-diagnostics field-diagnostic'><summary>Observation Pipeline — {escape(label)} diagnostic — <code>{obs_reason}</code> <span hidden>{escape(legacy_reason)}</span></summary>
    <h4>Stage 1 — Candidate</h4><p>source collection: {escape(obj.kind if obj else 'unavailable')} · declared record class: {escape(obj.kind if obj else 'unavailable')} · source file: {escape(obj.source_file if obj else 'unavailable')} · source row/location: {escape(obj.source_location if obj else 'unavailable')} · source identifier: <code>{escape(obj_id)}</code> · candidate identifier: <code>{escape(obj.record_id if obj else 'unavailable')}</code> · candidate object class: {escape(obj.kind if obj else 'unavailable')} · canonical object family: {escape(obj.kind if obj else 'unavailable')} · canonical owner: semantic_twin.{escape(obj.kind if obj else 'unavailable')} · candidate exists: {'yes' if obj else 'no'}</p>
    <h4>Stage 2 — Source and semantic field availability</h4><table><thead><tr><th>expected source field paths</th><th>source value present</th><th>type</th><th>safely truncated value preview</th></tr></thead>{path_rows}</table><p>matched source field path: <code>{escape(str(selected[0]))}</code> · selector used from researcher_v1.json: <code>{escape(contract_selector)}</code> · adapted target field: <code>{escape(target or page_field)}</code> · persisted candidate field: <code>{escape(target or selected[0])}</code> · semantic Twin field: <code>{escape(page_field or target)}</code> · linked Evidence: {escape(', '.join(obj.evidence_refs) if obj else '')} · Unknown: {escape(', '.join(_refs(obj,'UNK')))} · Contradiction: {escape(', '.join(_refs(obj,'CON')))}</p>
    <h4>Stage 3 — Observation generation</h4><p>observation generation attempted: {obs_attempted} · extractor or profile selected: {escape(obs_profile)} · observation profile version: {PROJECTION_VERSION} · subject: {escape(obj.subject if obj else '')} · predicate: {escape(page_field or label)} · value summary: {escape(_preview(selected[1]))} · evidence references: {escape(', '.join(obj.evidence_refs) if obj else '')} · confidence: {escape(obj.confidence if obj else '')} · time context: {escape(obj.freshness if obj else '')} · generated observation identifier: {escape(obj.record_id if obs_reason == 'observation_generated' and obj else '')} · result: {'generated' if obs_reason == 'observation_generated' else 'skipped'} · exact reason code: <code>{escape(obs_reason)}</code></p>
    <h4>Stage 4 — Canonical owner assessment</h4><p>canonical owner selected: semantic_twin.{escape(obj.kind if obj else 'unavailable')} · owner invoked: {owner_invoked} · assessment model: ExecutiveAssessmentProjection · assessment lifecycle state: assessment_pending_governance · assessment produced: no · assessment deferred: yes · assessment persistence location: not persisted for candidate import · assessment identifier: not supplied · assessment rejection or deferral reason: <code>assessment_pending</code>. factual candidate content: {'present' if _present(selected[1]) else 'absent'} · owner assessment: pending · completeness judgement: pending · recommendation eligibility: pending · promotion eligibility: separate governance action. assessment required for judgement/eligibility/completeness; factual display remains inspectable.</p>
    <h4>Stage 5 — Executive projection</h4><p>projection service: executive_record_view_model · projection version: {PROJECTION_VERSION} · source semantic field or observation: <code>{escape(page_field or target)}</code> · target page view-model field: <code>{escape(page_field or label)}</code> · projected value: {escape(_preview(rendered))} · filter applied: {'none' if rendered else 'empty-value suppression'} · suppression reason: <code>{'none' if rendered else reason}</code> · result: {projected}</p>
    <h4>Stage 6 — Rendered page</h4><p>template field: {escape(label)} · final rendered value: {escape(_preview(rendered))} · fallback used: {'no' if rendered else 'yes'} · responsible component: deployed template/page view model · final reason code: <code>{escape(reason if rendered else 'template_fallback_used')}</code></p></details>"""


def runtime_comparison(twin: SemanticTwin) -> str:
    if not pilot_diagnostics_enabled(): return ""
    industry = next((o for o in twin.objects if o.kind == "industry_twin"), None)
    bt = next((e.records[0] for e in twin.enterprises if e.name.casefold().startswith("bt")), None)
    mp = next((o for o in twin.objects if o.original_id in {"MP-OFCOM", "MP-VERIZON"} or o.kind == "market_participant_twin"), None)
    rows = []
    for label, obj, field in (("Industry Overview failure", industry, "industry_profile"), ("BT Group failure", bt, "description"), ("Market Participant success", mp, "role")):
        value = _path_value(obj.attributes if obj else {}, field) if obj else None
        rendered = bool(value)
        rows.append(f"<tr><th>{escape(label)}</th><td>payload.{escape(field)}</td><td>{escape(field)}</td><td>{'present' if _present(value) else 'absent'}</td><td>{'present' if obj else 'absent'}</td><td>{'observation_generated' if rendered else 'unsupported_object_family'}</td><td>assessment_pending</td><td>{'projected' if rendered else 'omitted'}</td><td>{'content' if rendered else 'placeholder'}</td></tr>")
    return "<details class='card pilot-diagnostics' open><summary>Observation Pipeline runtime comparison</summary><table><thead><tr><th>Control</th><th>source field</th><th>mapped field</th><th>persisted field</th><th>semantic field</th><th>observation result</th><th>owner assessment result</th><th>projection result</th><th>rendered result</th></tr></thead><tbody>"+"".join(rows)+"</tbody></table></details>"


def industry_section_diagnostics(twin: SemanticTwin) -> str:
    if not pilot_diagnostics_enabled(): return ""
    industry = next((o for o in twin.objects if o.kind == "industry_twin"), None)
    return "".join(field_panel(industry, name, paths, rendered=_path_value(industry.attributes if industry else {}, paths[0].removeprefix('payload.')), target=paths[0], page_field=name) for name, paths in INDUSTRY_SECTION_PATHS.items())


def enterprise_diagnostics(ent: Any) -> str:
    if not pilot_diagnostics_enabled(): return ""
    identity = next((o for o in ent.records if o.kind in {"enterprise", "enterprise_twin", "entity"}), None)
    return "".join(field_panel(identity, name, paths, rendered=_path_value(identity.attributes if identity else {}, paths[0].removeprefix('payload.')), target=paths[0], page_field=name) for name, paths in ENTERPRISE_FIELD_PATHS.items())


def research_gap_trace(subject: str, field: str, reason: str="owner-assessed deficiency") -> str:
    if not pilot_diagnostics_enabled(): return ""
    return f"<details class='pilot-diagnostics'><summary>Research Gap diagnostic — {escape(subject)}</summary><p>canonical subject: {escape(subject)} · requested field/dimension: {escape(field)} · source candidate field inspected: {escape(field)} · source presence state: source_field_absent unless shown in source dispositions · mapping state: governed requirement projection · assessment state: assessment_pending_governance · exact reason emitted: {escape(reason)}</p></details>"


def _contract_selector(obj: SemanticObject|None, target: str, page_field: str, paths: tuple[str, ...]) -> str:
    field = (target or page_field or "").removeprefix("payload.").replace("/", "_").replace(" ", "_").casefold()
    kind = (obj.kind if obj else "")
    profiles = RESEARCHER_CONTRACT.get("profiles", {})
    profile = profiles.get(kind, {})
    selectors = profile.get("fields", {}).get(field) or RESEARCHER_CONTRACT.get("common_fields", {}).get(field)
    if selectors:
        return json.dumps(selectors, sort_keys=True)
    source_payload = (obj.attributes or {}).get("source_payload") if obj else None
    if isinstance(source_payload, dict):
        matched = [p.removeprefix("payload.") for p in paths if _path_value(source_payload, p.removeprefix("payload.")) not in (None, "", [], {}, ())]
        if matched:
            return json.dumps(matched, sort_keys=True) + " (matched in preserved source_payload)"
    return "no selector matched for displayed field"


def _present(value: Any) -> bool:
    return value not in (None, "", [], {}, ())


def _path_value(data: Any, dotted: str) -> Any:
    cur=data
    for part in dotted.split('.'):
        if isinstance(cur, dict) and part in cur: cur=cur[part]
        else: return None
    return cur


def _preview(value: Any, limit: int=180) -> str:
    if value is None: return ""
    text = str(value)
    return text if len(text)<=limit else text[:limit]+"…"


def _refs(obj: SemanticObject|None, prefix: str) -> tuple[str,...]:
    if not obj: return ()
    return tuple(r for r in obj.references if r.upper().startswith(prefix))
