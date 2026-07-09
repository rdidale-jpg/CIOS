"""HTML views for Flora's governed Blueprint Import workflow."""
from __future__ import annotations

from html import escape
from typing import Any

from cios.applications.flora.access import authenticated_flora_user, can_receive_blueprint_package
from cios.applications.flora.blueprint_import import (
    BlueprintPackageRegistry,
    BlueprintPackageValidator,
    CandidateReviewService,
    DryRunPlanningService,
    CanonicalPromotionService,
)
from cios.applications.flora.blueprint_import.models import PackageReceiptError
from cios.applications.flora.blueprint_import.promotion import BlueprintPromotionError
from cios.applications.flora.blueprint_import.review import BlueprintReviewError
from cios.applications.flora.workspace.views import _page


def blueprint_import_page(headers: Any, message: str = "") -> tuple[str, int]:
    """Render the upload entry point without performing canonical mutation."""
    if not can_receive_blueprint_package(headers):
        return access_denied_page("Import Blueprint requires an authorised Flora package-upload user.")
    notice = f"<p class='pill'>{escape(message)}</p>" if message else ""
    history = _history_list()
    body = f"""
    <section class='hero'><p><a href='/'>Flora Home</a></p><h1>Import Blueprint</h1><p>Upload a governed Blueprint ZIP, validate it, review staged changes, explicitly approve promotion, then open the Enterprise Canvas.</p>{notice}</section>
    <section class='card action'><h2>Choose Blueprint ZIP</h2><form method='post' action='/blueprint-import/upload' enctype='multipart/form-data'><label>Blueprint package ZIP <input type='file' name='blueprint_zip' accept='.zip' required></label><p><button type='submit'>Upload and validate</button></p></form></section>
    <section class='card'><h2>Import History</h2>{history}</section>
    <section class='card'><h2>Journey</h2><ol><li>Choose a ZIP from this computer.</li><li>Upload and validate.</li><li>Review the proposed changes.</li><li>Approve promotion explicitly.</li><li>Open the Enterprise Canvas.</li></ol></section>
    """
    return _page("Import Blueprint", body), 200


def import_history_page(headers: Any) -> tuple[str, int]:
    if not authenticated_flora_user(headers):
        return access_denied_page("Import History requires an authorised Flora user.")
    return _page("Import History", f"<section class='hero'><h1>Import History</h1><p><a href='/blueprint-import'>Import Blueprint</a></p></section><section class='card'>{_history_list()}</section>"), 200


def receive_blueprint_upload(headers: Any, filename: str, content: bytes) -> tuple[str, int]:
    if not can_receive_blueprint_package(headers):
        return access_denied_page("Import Blueprint requires an authorised Flora package-upload user.")
    actor = authenticated_flora_user(headers)
    try:
        record = BlueprintPackageRegistry().receive(content, filename, actor)
        result = BlueprintPackageValidator().validate_and_stage(record.package_ref, actor, headers)
    except (PackageReceiptError, PermissionError, ValueError) as exc:
        return _page("Blueprint Import failed", f"<section class='hero'><h1>Blueprint Import failed</h1><p>{escape(str(exc))}</p><p><a href='/blueprint-import'>Return to Import Blueprint</a></p></section>"), 400
    return blueprint_review_page(record.import_run_id, headers, f"Package uploaded and validated. Accepted candidates: {result.accepted_candidate_count}.")


def blueprint_review_page(import_run_id: str, headers: Any, message: str = "") -> tuple[str, int]:
    summary = BlueprintPackageValidator().staging_summary(import_run_id)
    if not summary:
        return _page("Blueprint review unavailable", "<section class='hero'><h1>Review unavailable</h1><p>No staged Blueprint candidates were found for this import run.</p></section>"), 404
    package = BlueprintPackageRegistry().get(str(summary["package_ref"]))
    if not package:
        return access_denied_page("Blueprint package metadata is unavailable.")
    # Re-use validation's server-side inspection rule without altering staged state.
    try:
        BlueprintPackageValidator().validate_and_stage(package.package_ref, authenticated_flora_user(headers), headers)
    except Exception:
        return access_denied_page("You are not authorised to review this Blueprint import.")
    notice = f"<p class='pill'>{escape(message)}</p>" if message else ""
    rows = "".join(_candidate_row(c) for c in summary.get("candidates", []))
    body = f"""
    <section class='hero'><h1>Review proposed changes</h1><p>Import run {escape(import_run_id)} · Package {escape(str(summary['package_ref']))}</p>{notice}</section>
    <section class='card'><h2>Staged candidates</h2><table><thead><tr><th>Class</th><th>External ID</th><th>Status</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table></section>
    <section class='card action'><h2>Approve promotion</h2><p>This explicit step records review decisions, creates a dry-run plan, approves that plan, and executes only the approved canonical effects. Navigation alone does not mutate canonical data.</p><form method='post' action='/blueprint-import/{escape(import_run_id)}/approve'><label>Approval rationale <input name='rationale' value='Approved through Flora Blueprint Import review'></label><p><button type='submit'>Approve promotion</button></p></form></section>
    <section class='card'><p><a href='/digital-twins/{escape(package.identity.enterprise_id)}/canvas'>Open Enterprise Canvas</a></p></section>
    """
    return _page("Review Blueprint Import", body), 200


def approve_blueprint_import(import_run_id: str, headers: Any, rationale: str) -> tuple[str, int]:
    actor = authenticated_flora_user(headers)
    try:
        summary = BlueprintPackageValidator().staging_summary(import_run_id)
        if not summary:
            raise BlueprintReviewError("No staged candidates for import run")
        for c in summary.get("candidates", []):
            decision = "approve" if c.get("validation_status") == "accepted" else "quarantine"
            CandidateReviewService().record_decision(c["candidate_record_id"], decision, actor, rationale or "Blueprint Import reviewed", headers)
        plan = DryRunPlanningService().create_plan(import_run_id, actor, headers)
        approval = CanonicalPromotionService().approve_plan(import_run_id, plan.plan_id, actor, rationale or "Approved", headers)
        result = CanonicalPromotionService().execute_approved_plan(import_run_id, approval.approval_id, actor, headers)
        package = BlueprintPackageRegistry().get(str(summary["package_ref"]))
    except (BlueprintReviewError, BlueprintPromotionError, PermissionError, ValueError) as exc:
        return access_denied_page(str(exc))
    canvas = f"/digital-twins/{escape(package.identity.enterprise_id if package else 'bt-group-plc')}/canvas"
    body = f"<section class='hero'><h1>Promotion approved</h1><p>Promotion status: {escape(result.final_execution_status)}. Canonical mutations applied: {result.actual_mutation_count}.</p><p><a class='button' href='{canvas}'>Open Enterprise Canvas</a></p></section>"
    return _page("Blueprint Import promoted", body), 200


def access_denied_page(reason: str) -> tuple[str, int]:
    return _page("Access denied", f"<section class='hero'><h1>Access denied</h1><p>{escape(reason)}</p><p><a href='/'>Return to Flora Home</a></p></section>"), 403


def _candidate_row(c: dict[str, Any]) -> str:
    return f"<tr><td>{escape(str(c.get('candidate_object_class','')))}</td><td>{escape(str(c.get('original_source_id','')))}</td><td>{escape(str(c.get('validation_status','')))}</td><td>{escape(str(c.get('source_file','')))}</td></tr>"


def _history_list() -> str:
    records = BlueprintPackageRegistry().list()
    if not records:
        return "<p>No Blueprint imports have been received yet.</p>"
    items = "".join(f"<li><a href='/blueprint-import/{escape(r.import_run_id)}/review'>{escape(r.identity.enterprise_name)}</a> — {escape(r.status)} · {escape(r.received_at)} · {escape(r.original_filename)}</li>" for r in records)
    return f"<ul>{items}</ul>"
