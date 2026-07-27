"""Candidate adapter over the existing Blueprint Import read owners."""
from __future__ import annotations
from collections import Counter
from html import escape

from cios.applications.flora.access import can_access_enterprise
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.validator import BlueprintPackageValidator, can_inspect_blueprint_package
from .contracts import InspectionAdapter, InspectionProfile, InspectionSection, MaterialConclusion


def candidate_inspection_adapter(import_run_id: str, headers) -> InspectionAdapter:
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    if package is None:
        raise LookupError(import_run_id)
    if (not can_access_enterprise(headers, package.identity.enterprise_id, package.workspace_id)
            or not can_inspect_blueprint_package(headers, package)):
        raise PermissionError(import_run_id)
    summary = BlueprintPackageValidator().staging_summary(import_run_id) or {}
    candidates = tuple(summary.get("candidates") or ())
    inspection = package.package_inspection or {}
    counts = Counter(str(item.get("candidate_object_class") or "unclassified") for item in candidates)
    errors = tuple(summary.get("errors") or ())
    warnings = tuple(summary.get("warnings") or ())
    proposed = sum(1 for item in candidates if item.get("validation_status") == "accepted")
    rejected = len(candidates) - proposed
    conclusion = MaterialConclusion(
        "candidate-promotion-decision",
        f"{proposed} candidate record(s) are proposed for governed review; no canonical mutation has occurred.",
        "candidate proposal", "Determines whether this package should proceed to governed review.",
        f"Validation inspected {len(candidates)} staged candidate record(s).",
        f"{len(errors)} blocking error(s), {len(warnings)} warning(s), and {rejected} non-accepted candidate(s) challenge promotion.",
        f"/blueprint-import/{escape(import_run_id)}/inspect", f"/blueprint-import/{escape(import_run_id)}/review",
        "Candidate validation only", package.received_at,
    )
    profile = InspectionProfile(
        str(inspection.get("twin_title") or package.identity.package_id),
        f"Candidate {str(inspection.get('twin_type') or 'Twin').replace('_', ' ').title()}",
        "Blueprint Import (candidate owner)", "Candidate — not governed intelligence",
        package.identity.package_version, package.received_at,
        str(inspection.get("evidence_cut_off") or "Not supplied"),
        str(inspection.get("research_state") or "Not supplied"),
        str(inspection.get("decision_maturity") or "Pre-acceptance"),
        f"{counts.get('evidence', 0)} candidate Evidence record(s)", package.received_at,
        "Validation state; not a governed trust score", str(counts.get("unknown", 0)),
        str(counts.get("contradiction", 0)), f"Package {package.package_ref} · Import Run {import_run_id}",
    )
    sections = (
        InspectionSection("candidate-impact", "Promotion impact", 20,
                          lambda: _candidate_summary(import_run_id, counts, proposed, errors, warnings),
                          "candidate staging projection", True, True, f"/blueprint-import/{import_run_id}/review", package.received_at, package.received_at),
        InspectionSection("candidate-review", "Import Review", 30,
                          lambda: _review_links(import_run_id), "candidate workflow links", True, True,
                          f"/blueprint-import/{import_run_id}/review", package.received_at, package.received_at),
    )
    return InspectionAdapter("candidate-import", profile, sections, (conclusion,), "candidate")


def _candidate_summary(run_id, counts, proposed, errors, warnings) -> str:
    rows = "".join(f"<tr><th>{escape(key.replace('_', ' ').title())}</th><td>{value}</td></tr>" for key, value in sorted(counts.items()))
    return f"<section class='card candidate-state' id='candidate-impact'><h2>Proposed intelligence and promotion impact</h2><p><strong>Candidate state:</strong> proposed intelligence only. Nothing on this page is accepted Enterprise Intelligence.</p><p>{proposed} record(s) may proceed to review; {len(errors)} blocking error(s) and {len(warnings)} warning(s) remain.</p><table>{rows}</table><p><a href='/blueprint-import/{escape(run_id)}/inspect'>Open existing Import Inspect</a></p></section>"


def _review_links(run_id: str) -> str:
    run = escape(run_id)
    return f"<section class='card' id='candidate-review'><h2>Validation and proposed mutations</h2><p>The existing Import Review remains the owner of review decisions and proposed mutations.</p><p><a href='/blueprint-import/{run}/review'>Open Import Review</a> · <a href='/blueprint-import/{run}'>Open import history</a></p></section>"
