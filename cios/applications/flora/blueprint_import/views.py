"""Plain-language Flora Blueprint Import web experience."""
from __future__ import annotations

from collections import Counter
import json
import logging
import os
from html import escape
from typing import Any
from uuid import uuid4

from cios.applications.flora.access import authenticated_flora_user, active_flora_workspace, blueprint_upload_authorisation, can_access_enterprise, flora_roles, is_cios_owner, user_enterprise_access
from cios.applications.flora.workspace.views import _page
from cios.applications.flora.storage import PersistenceError, storage_mode
from cios.applications.flora.live.runtime import deployment_metadata

from .archive import sha256_bytes
from .ledger import BlueprintImportLedger
from .candidates import CandidateStagingRepository
from .mapping import ImportMappingService
from .planning import DryRunPlanRepository, DryRunPlanningService
from .review_plan import BlueprintReviewPlanCoordinator, PAGE_SIZE_DEFAULT, PAGE_SIZE_MAX
from .promotion import CanonicalPromotionRepository, CanonicalPromotionService, BlueprintPromotionError, can_approve_blueprint_promotion, can_execute_blueprint_promotion
from .registry import BlueprintPackageRegistry
from .review import CandidateReviewRepository, CandidateReviewService, can_review_blueprint_candidate
from .validator import BlueprintPackageValidator, BlueprintValidationError, can_inspect_blueprint_package
from .cios_twin_adapter import MAPPING_VERSION
from .restage import BlueprintRestageService, can_restage_blueprint_package, RESTAGE_STAGES
from .models import PackageReceiptError

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
ZIP_MIME_TYPES = {"application/zip", "application/x-zip-compressed", "application/octet-stream", ""}
LOGGER = logging.getLogger(__name__)


def import_blueprint_entry_page(headers: Any, message: str = "") -> tuple[str, int]:
    decision = blueprint_upload_authorisation(headers)
    if decision.decision != "allowed":
        ref, audit_warning = _audit_authorisation("package_upload_authorisation_denied", headers, "Blueprint upload capability resolved", decision)
        return _safe_failure("Blueprint import access denied", "Blueprint upload capability resolved", False, False, _permission_guidance(headers, decision), decision, ref, audit_warning), 403
    body = f"""<section class='hero'><h1>Import Blueprint</h1><p>Select a Commercial Digital Twin Blueprint ZIP from your computer.</p>{_notice(message)}</section>
    <section class='card'><h2>Upload package</h2><p><strong>Supported format:</strong> .zip Blueprint package. <strong>Maximum size:</strong> {MAX_UPLOAD_BYTES // (1024*1024)} MB.</p><p class='muted'>Blueprint packages may contain confidential enterprise intelligence. Upload only packages you are authorised to use.</p><p><strong>Uploading a Blueprint does not change the governed Twin. Flora will validate and stage the package for review first.</strong></p><form method='post' action='/blueprint-import/upload' enctype='multipart/form-data'><label for='blueprint_zip'>Blueprint ZIP file</label><input id='blueprint_zip' name='blueprint_zip' type='file' accept='.zip,application/zip' required><p><button type='submit'>Upload and validate</button></p></form></section>
    <section class='card'><h2>Import history</h2><p><a href='/blueprint-import/history'>View previous Blueprint imports</a></p></section>"""
    return _page("Import Blueprint", body), 200


def upload_and_validate_blueprint(files: dict[str, bytes], fields: dict[str, str], headers: Any) -> tuple[str, int, str]:
    actor = authenticated_flora_user(headers)
    filename = fields.get("blueprint_zip.filename") or fields.get("filename") or "blueprint.zip"
    mime = fields.get("blueprint_zip.content_type") or fields.get("content_type") or ""
    try:
        decision = blueprint_upload_authorisation(headers)
        if decision.decision != "allowed":
            ref, audit_warning = _audit_authorisation("package_upload_authorisation_denied", headers, "Blueprint upload capability resolved", decision)
            raise PermissionError("You do not have permission to import Blueprints in this workspace.")
        content = files.get("blueprint_zip") or files.get("file") or b""
        if not filename.lower().endswith(".zip") or mime not in ZIP_MIME_TYPES:
            raise PackageReceiptError("Choose a valid Blueprint ZIP file.")
        if len(content) > MAX_UPLOAD_BYTES:
            raise PackageReceiptError(f"The selected file is larger than the {MAX_UPLOAD_BYTES // (1024*1024)} MB upload limit.")
        before = _canonical_marker()
        record = BlueprintPackageRegistry().receive(content, filename, actor, active_flora_workspace(headers))
        _audit_authorisation("package_upload_authorisation_allowed", headers, "Upload request accepted", decision, record.package_ref, record.import_run_id, record.identity.enterprise_id)
        result = BlueprintPackageValidator().validate_and_stage(record.package_ref, actor, headers)
        assert before == _canonical_marker(), "Upload and validation must not mutate canonical memory"
        return validation_result_page(record.import_run_id, headers)[0], 200, f"/blueprint-import/{record.import_run_id}"
    except PermissionError as exc:
        return _safe_failure(str(exc), "Blueprint upload capability resolved", False, False, _permission_guidance(headers, decision), decision, ref, audit_warning), 403, "/blueprint-import"
    except Exception as exc:
        failed_stage = "Package inspection authorised" if isinstance(exc, BlueprintValidationError) else "Package received"
        return _safe_failure(str(exc), failed_stage, False, False, "Choose a safe Blueprint ZIP and try again. No governed Twin changes occurred.", decision), 400, "/blueprint-import"


def validation_result_page(import_run_id: str, headers: Any) -> tuple[str, int]:
    ctx = _context(import_run_id)
    if not ctx:
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "Package identity read", False, True, "Open an import you are authorised to review."), 403
    if not can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")):
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "Package enterprise access resolved", False, True, "Open an import you are authorised to review."), 403
    if not can_inspect_blueprint_package(headers, ctx["package"]):
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "Package inspection authorised", False, True, "Open an import you are authorised to review."), 403
    package = ctx["package"]; summary = ctx["summary"] or {}; candidates = ctx["candidates"]
    worksheets = _worksheets(summary.get("warnings", [])); status = "Passed with warnings" if summary.get("warnings") and not summary.get("errors") else ("Failed" if summary.get("errors") else "Passed")
    counts = _candidate_counts(candidates)
    review_link = "<section class='card'><p><a href='/blueprint-import/{0}/review'>Review proposed changes</a></p></section>".format(escape(import_run_id)) if not summary.get('errors') else "<section class='card'><p><strong>Validation failed.</strong> Proposed-change review and approval are disabled until fatal validation errors are resolved.</p></section>"
    deployment = _blueprint_deployment_metadata(summary)
    deployment_rows = "".join(f"<tr><th>{escape(key.replace('_', ' ').title())}</th><td><code>{escape(value)}</code></td></tr>" for key, value in deployment.items())
    body = _package_header(package) + f"""<section class='card'><h2>Validation result</h2><table><tr><th>Checksum</th><td><code>{escape(package.package_sha256)}</code></td></tr><tr><th>Files inspected</th><td>{len(summary.get('files_inspected', []))}</td></tr><tr><th>Workbook discovered</th><td>{'Yes' if any(str(f).endswith(('.xlsx','.xlsm','.xls')) for f in summary.get('files_inspected', [])) else 'Not declared'}</td></tr><tr><th>Worksheets discovered</th><td>{escape(', '.join(worksheets) or 'None reported')}</td></tr><tr><th>Validation status</th><td>{escape(status)}</td></tr></table>{_list('Warnings', summary.get('warnings', []))}{_list('Errors', summary.get('errors', []))}</section><details class='card'><summary><strong>Safe deployment diagnostics</strong></summary><table>{deployment_rows}</table></details>""" + _execution_trace_section(package, summary, bool(summary.get("errors"))) + _counts_section(counts) + _available_actions_section(package, summary, counts, headers) + review_link
    return _page("Blueprint validation result", body), 200



def restage_confirm_page(import_run_id: str, headers: Any) -> tuple[str, int]:
    ctx = _context(import_run_id)
    if not ctx or not can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")):
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "restage", False, True, "Open an import you are authorised to restage."), 403
    if not can_restage_blueprint_package(headers, ctx["package"]):
        return _safe_failure("You are not authorised to restage this Blueprint package.", "restage", False, True, "Ask for Blueprint staging capability."), 403
    summary = ctx.get("summary") or {}; counts = _candidate_counts(ctx.get("candidates", []))
    body = _package_header(ctx["package"]) + _restage_intro(ctx["package"], summary, counts)
    return _page("Restage Blueprint package", body), 200


def restage_history_page(import_run_id: str, headers: Any) -> tuple[str, int]:
    ctx = _context(import_run_id)
    if not ctx or not can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")):
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "staging history", False, True, "Open an import you are authorised to view."), 403
    hist = BlueprintRestageService().history(import_run_id)
    rows = ''.join(f"<tr><td><code>{escape(str(h.get('staging_version','')))}</code></td><td><code>{escape(str(h.get('mapping_version','')))}</code></td><td>{escape(str(h.get('created_at','')))}</td><td><code>{escape(str(h.get('package_checksum','')))}</code></td><td>{escape(str(h.get('records_accepted_into_staging',0)))}</td></tr>" for h in hist) or "<tr><td colspan='5'>No prior staging history recorded.</td></tr>"
    body = _package_header(ctx["package"]) + f"<section class='card'><h2>Prior staging history</h2><table><thead><tr><th>Staging version</th><th>Mapping version</th><th>Created</th><th>Package checksum</th><th>Accepted</th></tr></thead><tbody>{rows}</tbody></table></section>"
    return _page("Blueprint staging history", body), 200


def restage_package(import_run_id: str, form: dict[str, list[str]], headers: Any) -> tuple[str, int]:
    ctx = _context(import_run_id)
    if not ctx or not can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")):
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "restage", False, True, "Open an import you are authorised to restage."), 403
    if form.get("confirm_restage") != ["yes"]:
        return restage_confirm_page(import_run_id, headers)
    before = _canonical_marker()
    try:
        job = BlueprintRestageService().ensure_restage(import_run_id, authenticated_flora_user(headers), headers)
        assert before == _canonical_marker(), "Restaging must not mutate canonical memory"
        return restage_progress_page(import_run_id, headers, job), 200
    except PermissionError as exc:
        return _safe_failure(str(exc), "restage", False, True, "Ask for Blueprint staging capability."), 403


def restage_progress_page(import_run_id: str, headers: Any, job: dict[str, Any] | None = None) -> tuple[str, int] | str:
    direct_render = job is not None
    ctx = _context(import_run_id)
    if not ctx:
        html = _safe_failure("Blueprint import record is unavailable or access is denied.", "restage progress", False, True, "Open an import you are authorised to restage.")
        return html if direct_render else (html, 403)
    job = job or (BlueprintRestageService()._jobs(import_run_id)[-1] if BlueprintRestageService()._jobs(import_run_id) else {})
    if job.get("already_completed"):
        body = _package_header(ctx["package"]) + f"<section class='card'><h2>Already restaged</h2><p>This package has already been restaged with mapping version <code>{escape(str(job.get('mapping_version')))}</code>.</p><p><a href='/blueprint-import/{escape(import_run_id)}/review'>View latest review</a></p></section>"
        html = _page("Blueprint restage already complete", body)
        return html if direct_render else (html, 200)
    if job.get("status") == "Failed":
        body = _package_header(ctx["package"]) + f"<section class='card warning'><h2>Restaging failed</h2><table><tr><th>Diagnostic reference</th><td><code>{escape(str(job.get('diagnostic_reference','')))}</code></td></tr><tr><th>Package reference</th><td><code>{escape(str(job.get('package_ref','')))}</code></td></tr><tr><th>Mapping version</th><td><code>{escape(str(job.get('mapping_version','')))}</code></td></tr><tr><th>Stage failed</th><td>{escape(str(job.get('stage','')))}</td></tr><tr><th>Records processed</th><td>{escape(str(job.get('records_processed',0)))}</td></tr><tr><th>Canonical changes made</th><td>No</td></tr><tr><th>Prior active staging remains available</th><td>{escape(str(job.get('prior_active_staging_available','yes')))}</td></tr><tr><th>Next action</th><td>Retry restaging after support inspects the diagnostic reference.</td></tr></table></section>"
        html = _page("Blueprint restage failed", body); return html if direct_render else (html, 200)
    done = set(RESTAGE_STAGES[:RESTAGE_STAGES.index(job.get('stage','package located'))+1]) if job.get('stage') in RESTAGE_STAGES else set()
    items = ''.join(f"<li>{'✓' if s in done else '…'} {escape(s)}</li>" for s in RESTAGE_STAGES)
    cs = job.get('candidate_summary') or {}
    body = _package_header(ctx["package"]) + f"<section class='card'><h2>Regenerate review with current validation</h2><p>Status: <strong>{escape(str(job.get('status','Not started')))}</strong></p><ul>{items}</ul><table><tr><th>Staging version</th><td><code>{escape(str(job.get('staging_version','')))}</code></td></tr><tr><th>Mapping version</th><td><code>{escape(str(job.get('mapping_version', MAPPING_VERSION)))}</code></td></tr><tr><th>Canonical changes made</th><td>No</td></tr><tr><th>Accepted</th><td>{int(cs.get('Accepted',0))}</td></tr><tr><th>Quarantined</th><td>{int(cs.get('Quarantined',0))}</td></tr><tr><th>Rejected</th><td>{int(cs.get('Rejected',0))}</td></tr><tr><th>Projection-only</th><td>{int(cs.get('Projection-only',0))}</td></tr></table><p><a href='/blueprint-import/{escape(import_run_id)}/review'>View latest review</a> · <a href='/blueprint-import/{escape(import_run_id)}/staging-history'>View prior staging history</a></p></section>"
    html = _page("Blueprint restage progress", body); return html if direct_render else (html, 200)

def review_page(import_run_id: str, headers: Any, message: str = "", query: dict[str, list[str]] | None = None) -> tuple[str, int]:
    correlation_id = f"bpi-review-{uuid4().hex[:12]}"
    try:
        query = query or {}
        ctx = _context(import_run_id)
        if not ctx or not (can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")) and can_review_blueprint_candidate(headers, ctx["package"].identity.enterprise_id)):
            return _safe_failure("You are not authorised to review this Blueprint import.", "review", False, True, "Ask for Blueprint review permission."), 403
        summary = ctx.get("summary") or {}
        if summary.get("errors"):
            body = _package_header(ctx["package"]) + _notice(message) + "<section class='card'><h2>Review proposed changes</h2><p><strong>Validation failed.</strong> Proposed-change planning is disabled because workbook or package inspection did not complete safely.</p>{}</section>".format(_list('Errors', summary.get('errors', []))) + _execution_trace_section(ctx["package"], summary, True)
            body += "<section class='card'><h2>Approval</h2><p>Approval controls are disabled until fatal validation errors are resolved.</p><button type='button' disabled>Approve and update governed Twin</button></section>"
            return _page("Review Blueprint proposed changes", body), 200
        coord = BlueprintReviewPlanCoordinator()
        def defaults(): _ensure_reviews_and_mappings(ctx, headers)
        job = coord.ensure_job(import_run_id, authenticated_flora_user(headers), headers, defaults)
        LOGGER.info("Blueprint review preparation trace", extra={"correlation_id": correlation_id, "review_job_id": job.get("job_id"), "import_run_id": import_run_id, "stage": job.get("stage"), "records_processed": job.get("records_processed", 0)})
        if job.get("status") == "Failed":
            return _review_failure_page(ctx, job, correlation_id), 200
        if job.get("status") == "Stale":
            body = _package_header(ctx["package"]) + _stale_review_section(ctx["package"], job)
            return _page("Review Blueprint proposed changes", body), 200
        if job.get("status") == "Not ready":
            return _review_ready_page(ctx, job, coord, query, message, correlation_id), 200
        if job.get("status") != "Ready":
            return _review_progress_page(ctx, job, correlation_id, message), 200
        return _review_ready_page(ctx, job, coord, query, message, correlation_id), 200
    except Exception as exc:
        LOGGER.exception("Blueprint review route failed", extra={"correlation_id": correlation_id, "import_run_id": import_run_id})
        job = {"diagnostic_reference": correlation_id, "stage": "Blueprint review route", "records_processed": 0, "records_total": 0, "error_category": type(exc).__name__, "status": "Failed", "job_id": correlation_id, "plan_persisted": False}
        ctx = locals().get("ctx") or {}
        return _review_failure_page(ctx, job, correlation_id), 200

def approve_and_promote(import_run_id: str, form: dict[str, list[str]], headers: Any) -> tuple[str, int]:
    ctx = _context(import_run_id)
    if not ctx or not (can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")) and can_approve_blueprint_promotion(headers, ctx["package"].identity.enterprise_id) and can_execute_blueprint_promotion(headers, ctx["package"].identity.enterprise_id)):
        return _safe_failure("You are not authorised to approve and execute Blueprint promotion.", "approval", False, True, "Ask for Blueprint promotion permission."), 403
    if (ctx.get("summary") or {}).get("errors"):
        return _safe_failure("Validation failed; approval is disabled until fatal inspection errors are resolved.", "approval", False, True, "Resolve validation errors, then stage and review again."), 400
    review_summary = BlueprintReviewPlanCoordinator().latest_job(import_run_id) or {}
    if review_summary.get("stale") or review_summary.get("status") in {"Stale", "Not ready", "Failed"} or review_summary.get("mapping_version") != MAPPING_VERSION:
        return _safe_failure("This review plan is stale or not ready; approval is disabled. Regenerate review with current validation before approval.", "approval", False, True, "Use Regenerate review with current validation."), 400
    if form.get("confirm_plan") != ["yes"] or form.get("confirm_mutations") != ["yes"] or not (form.get("rationale") or [""])[0].strip():
        return review_page(import_run_id, headers, "Approval requires review confirmation, mutation-count confirmation and a rationale.")
    try:
        svc = CanonicalPromotionService(); plan_id = (form.get("plan_id") or [""])[0]
        approval = svc.approve_plan(import_run_id, plan_id, authenticated_flora_user(headers), (form.get("rationale") or [""])[0], headers)
        result = svc.execute_approved_plan(import_run_id, approval.approval_id, authenticated_flora_user(headers), headers)
        return completion_page(import_run_id, result.to_dict(), headers), 200
    except BlueprintPromotionError as exc:
        return _safe_failure(str(exc), "promotion", False, True, "The package remains available. Review the plan and retry after resolving the issue."), 400


def decline_promotion(import_run_id: str, headers: Any) -> tuple[str, int]:
    return review_page(import_run_id, headers, "Promotion declined. No canonical changes occurred; the preserved package remains available for later review.")


def completion_page(import_run_id: str, result: dict[str, Any], headers: Any) -> str:
    ctx = _context(import_run_id); package = ctx["package"] if ctx else None; enterprise = package.identity.enterprise_id if package else ""
    body = ( _package_header(package) if package else "") + f"""<section class='card'><h2>Completion</h2><table><tr><th>Promotion status</th><td>{escape(result.get('final_execution_status','unknown'))}</td></tr><tr><th>Records created</th><td>{len(result.get('records_created', []))}</td></tr><tr><th>Records updated</th><td>{len(result.get('records_updated', []))}</td></tr><tr><th>Projections retained</th><td>{_projection_count(import_run_id)}</td></tr><tr><th>Exceptions</th><td>{len(result.get('records_blocked', [])) + len(result.get('records_failed', []))}</td></tr></table><p>The original ZIP was preserved unchanged in governed runtime storage.</p><p><a href='/digital-twins/{escape(enterprise)}/canvas'>Open Enterprise Canvas</a> · <a href='/blueprint-import/{escape(import_run_id)}'>Open import record</a></p></section>"""
    return _page("Blueprint import complete", body)


def history_page(headers: Any) -> tuple[str, int]:
    if not authenticated_flora_user(headers):
        return _safe_failure("Sign in to view Blueprint import history.", "history", False, True, "Sign in and try again."), 403
    rows = []
    allowed = user_enterprise_access(headers)
    for p in BlueprintPackageRegistry().list():
        if not can_access_enterprise(headers, p.identity.enterprise_id, getattr(p, "workspace_id", "")): continue
        summary = BlueprintPackageValidator().staging_summary(p.import_run_id) or {}
        plans = DryRunPlanRepository().list(p.import_run_id)
        promo = _latest_promotion_status(p.import_run_id)
        rows.append(f"<tr><td>{escape(_package_name(p))}</td><td>{escape(p.identity.enterprise_id)}</td><td>{escape(p.identity.package_version)}</td><td>{escape(p.received_by)}</td><td>{escape(p.received_at)}</td><td>{'complete' if summary else p.status}</td><td>{'planned' if plans else 'not reviewed'}</td><td>{escape(promo)}</td><td>{escape(_twin_version(p))}</td><td><a href='/blueprint-import/{escape(p.import_run_id)}'>details</a></td></tr>")
    table = "<table><thead><tr><th>Package name</th><th>Enterprise</th><th>Package version</th><th>Uploaded by</th><th>Uploaded date</th><th>Validation status</th><th>Review status</th><th>Promotion status</th><th>Resulting Twin version</th><th>Details</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    return _page("Blueprint import history", f"<section class='hero'><h1>Blueprint import history</h1></section><section class='card'>{table}</section>"), 200

# helpers

def _context(import_run_id):
    for p in BlueprintPackageRegistry().list():
        if p.import_run_id == import_run_id:
            s = BlueprintPackageValidator().staging_summary(import_run_id)
            return {"package": p, "summary": s, "candidates": (s or {}).get("candidates", [])}
    return None

def _ensure_reviews_and_mappings(ctx, headers):
    reviewer = authenticated_flora_user(headers); reviews = CandidateReviewRepository().latest_by_candidate(ctx["package"].import_run_id); mapper = ImportMappingService(); reviewer_svc = CandidateReviewService()
    for c in ctx["candidates"]:
        cid = c["candidate_record_id"]
        if cid not in reviews and c.get("validation_status") == "accepted":
            decision = "approve" if c.get("validation_status") == "accepted" else ("unsupported" if c.get("validation_status") == "quarantined" else "reject")
            reviewer_svc.record_decision(cid, decision, reviewer, "UI default review summary for staged package", headers)
        if c.get("validation_status") == "accepted" and c.get("candidate_object_class") in {"evidence", "observation"} and not c.get("payload", {}).get("proposed_effect"):
            mapper.record_mapping(c, "propose_create", reviewer, headers, c.get("candidate_object_class", "").title())


def _stale_review_section(package, job) -> str:
    run = escape(package.import_run_id)
    why = escape(str(job.get("stale_reason") or "Constructor validation rules, canonical constructors, mapping version or promotion contract changed since this review was generated."))
    return f"""<section class='card warning'><h2>Review plan is stale</h2><p>{why}</p><p><strong>Approval blocked:</strong> stale review plans cannot be retried.</p><form method='post' action='/blueprint-import/{run}/restage'><input type='hidden' name='confirm_restage' value='yes'><p><button type='submit'>Regenerate review with current validation</button></p></form><p><a href='/blueprint-import/{run}'>Return to Blueprint</a></p></section>"""

def _review_progress_page(ctx, job, correlation_id: str, message: str = "") -> str:
    counts = job.get("candidate_summary") or _review_candidate_counts(ctx.get("candidates", []))
    proposed = job.get("proposed") or {}
    body = _package_header(ctx["package"]) + _notice(message)
    body += _review_summary_section(ctx, job, counts, proposed)
    body += _review_trace_section(ctx, job, correlation_id)
    body += "<section class='card'><h2>Next action</h2><p>Review exceptions and quarantine reasons after preparation completes.</p><p><strong>Approval controls are disabled</strong> until the review plan is complete and fatal errors are absent.</p><p><a href=''>Refresh review status</a></p></section>"
    return _page("Review Blueprint proposed changes", body)


def _review_ready_page(ctx, job, coord, query, message: str, correlation_id: str) -> str:
    details = _load_review_details(coord, ctx["package"].import_run_id)
    counts = job.get("candidate_summary") or _review_candidate_counts(details.get("candidates", []))
    proposed = job.get("proposed") or {}
    body = _package_header(ctx["package"]) + _notice(message)
    body += _review_summary_section(ctx, job, counts, proposed)
    body += _review_trace_section(ctx, job, correlation_id)
    body += _quarantine_reasons_section(job)
    body += _review_sections(ctx["package"].import_run_id, details, query)
    plan_id = escape(str(job.get("plan_id", "")))
    expected = int(proposed.get("Creates", 0)) + int(proposed.get("Updates", 0))
    rec = job.get("reconciliation") or {}
    if rec and not rec.get("passes", True):
        body += f"""<section class='card warning'><h2>Approval</h2><p><strong>Approval blocked:</strong> accepted canonical candidates do not reconcile with creates, updates and unchanged.</p><p>Mismatch: {int(rec.get("mismatch", 0))}</p><button type='button' disabled>Approve and update governed Twin</button></section>"""
    else:
        body += f"""<section class='card'><h2>Approval</h2><p>Promotion remains disabled until the owner has reviewed required exceptions and confirms the expected canonical mutation count.</p><form method='post' action='/blueprint-import/{escape(ctx["package"].import_run_id)}/approve'><input type='hidden' name='plan_id' value='{plan_id}'><label><input type='checkbox' name='confirm_plan' value='yes' required> I reviewed the plan</label><label><input type='checkbox' name='confirm_mutations' value='yes' required> I understand the expected mutation count is {expected}</label><label>Approval rationale</label><textarea name='rationale' required></textarea><p><button type='submit'>Approve and update governed Twin</button></p></form><form method='post' action='/blueprint-import/{escape(ctx["package"].import_run_id)}/decline'><p><button type='submit'>Decline promotion</button></p></form></section>"""
    return _page("Review Blueprint proposed changes", body)


def _review_failure_page(ctx, job, correlation_id: str) -> str:
    header = _package_header(ctx["package"]) if ctx and ctx.get("package") else "<section class='hero'><h1>Blueprint review</h1></section>"
    body = header + f"""<section class='card warning'><h2>Blueprint review could not be prepared.</h2><table>
    <tr><th>Diagnostic reference</th><td><code>{escape(str(job.get('diagnostic_reference') or correlation_id))}</code></td></tr>
    <tr><th>Current review stage</th><td>{escape(str(job.get('stage', 'unknown')))}</td></tr>
    <tr><th>Records processed</th><td>{escape(str(job.get('records_processed', 0)))}</td></tr>
    <tr><th>Records remaining</th><td>{max(0, int(job.get('records_total', 0)) - int(job.get('records_processed', 0)))}</td></tr>
    <tr><th>Exception category</th><td>{escape(str(job.get('error_category', 'BlueprintReviewError')))}</td></tr>
    <tr><th>Canonical changes made</th><td>No</td></tr>
    <tr><th>Next action</th><td>Retry review after support inspects the diagnostic reference.</td></tr>
    </table></section>"""
    if ctx and ctx.get("package"):
        body += _stale_review_section(ctx["package"], job)
    body += _review_trace_section(ctx or {}, job, correlation_id)
    return _page("Blueprint review could not be prepared", body)


def _review_summary_section(ctx, job, counts, proposed) -> str:
    package = ctx["package"]
    def val(name): return int(proposed.get(name, 0))
    mq = job.get("mapping_quality") or {}
    def rows(title, data):
        body = "".join(f"<tr><td>{escape(str(k))}</td><td>{int(v)}</td></tr>" for k, v in sorted((data or {}).items(), key=lambda kv: str(kv[0]))) or "<tr><td colspan='2'>None</td></tr>"
        return f"<h3>{escape(title)}</h3><table><tbody>{body}</tbody></table>"
    completeness = "".join(f"<tr><td>{escape(str(k))}</td><td>{'Yes' if v else 'No'}</td></tr>" for k, v in (mq.get("twin_completeness_indicators") or {}).items())
    top = rows("Accepted by class", mq.get("accepted_by_class")) + rows("Projection-only by class", mq.get("projection_only_by_class")) + rows("Ignored by reason", job.get("ignored_reasons")) + rows("Quarantined by reason", job.get("quarantine_reasons")) + f"<h3>Derived IDs</h3><table><tr><th>Source-supplied IDs</th><td>{int(mq.get('source_supplied_id_count',0))}</td></tr><tr><th>Derived IDs</th><td>{int(mq.get('derived_id_count',0))}</td></tr><tr><th>Derived-ID collisions</th><td>{int(mq.get('derived_id_collisions',0))}</td></tr><tr><th>Derived-ID failures</th><td>{int(mq.get('derived_id_failures',0))}</td></tr></table><h3>Twin completeness indicators</h3><table>{completeness}</table>"
    return f"""<section class='card'><h2>Review proposed changes</h2>{top}<h3>Summary</h3><table>
    <tr><th>Blueprint</th><td>{escape(_package_name(package))} {escape(package.identity.package_version)}</td></tr>
    <tr><th>Review status</th><td>{escape(str(job.get('status', 'Preparing')))}</td></tr>
    <tr><th>Staging version</th><td><code>{escape(str((ctx.get('summary') or {}).get('staging_version', 'staging-v1')))}</code></td></tr>
    <tr><th>Mapping version</th><td><code>{escape(str(job.get('mapping_version') or (ctx.get('summary') or {}).get('mapping_version') or MAPPING_VERSION))}</code></td></tr>
    <tr><th>Review generated from</th><td><code>{escape(str((ctx.get('summary') or {}).get('staging_version', 'staging-v1')))}</code></td></tr>
    <tr><th>Accepted canonical candidates</th><td>{int(counts.get('Accepted canonical candidates', counts.get('Accepted', 0)))}</td></tr>
    <tr><th>Accepted but non-persistable</th><td>{int(counts.get('Accepted but non-persistable', proposed.get('Accepted but non-persistable', 0)))}</td></tr>
    <tr><th>Quarantined</th><td>{int(counts.get('Quarantined', 0))}</td></tr>
    <tr><th>Rejected</th><td>{int(counts.get('Rejected', 0))}</td></tr>
    <tr><th>Unsupported</th><td>{int(counts.get('Unsupported', 0))}</td></tr>
    <tr><th>Creates</th><td>{val('Creates')}</td></tr>
    <tr><th>Updates</th><td>{val('Updates')}</td></tr>
    <tr><th>Unchanged</th><td>{val('Unchanged')}</td></tr>
    <tr><th>Reconciliation check</th><td>{'Passed' if (job.get('reconciliation') or {}).get('passes', True) else 'Failed'}</td></tr>
    <tr><th>Conflicts</th><td>{val('Conflicts')}</td></tr>
    <tr><th>Unresolved references</th><td>{val('Unresolved references')}</td></tr>
    <tr><th>Projection-only</th><td>{val('Projection-only')} analytical projections retained outside canonical memory</td></tr>
    <tr><th>Constructor validation failures</th><td>{int(job.get('constructor_validation_failures', 0))}</td></tr>
    <tr><th>Non-atomic observations</th><td>{int(job.get('non_atomic_observations', 0))}</td></tr>
    <tr><th>Canonical changes made</th><td>No</td></tr>
    <tr><th>Next action</th><td>Review exceptions and quarantine reasons</td></tr>
    </table></section>"""


def _review_trace_section(ctx, job, correlation_id: str) -> str:
    elapsed = max(0, int((job.get("completed_at") or __import__("time").time()) - (job.get("started_at") or __import__("time").time())))
    package = ctx.get("package") if isinstance(ctx, dict) else None
    rows = {
        "Review job ID": job.get("job_id", ""),
        "Package reference": job.get("package_ref", getattr(package, "package_ref", "")),
        "Staged candidate count": job.get("records_total", job.get("candidate_count", 0)),
        "Current stage": job.get("stage", ""),
        "Records processed": job.get("records_processed", 0),
        "Elapsed time": f"{elapsed}s",
        "Memory-safe batching enabled": "yes",
        "Pagination enabled": "yes",
        "Plan persisted": "yes" if job.get("plan_persisted") else "no",
        "Deployed commit SHA": job.get("deployment_commit_sha") or deployment_metadata().get("commit_sha") or "Unavailable",
        "Correlation ID": correlation_id,
    }
    return "<section class='card'><h2>Review preparation trace</h2><table>" + "".join(f"<tr><th>{escape(k)}</th><td><code>{escape(str(v))}</code></td></tr>" for k, v in rows.items()) + "</table></section>"


def _quarantine_reasons_section(job) -> str:
    reasons = job.get("quarantine_reasons") or {}
    rows = "".join(f"<tr><td>{escape(str(k))}</td><td>{int(v)}</td></tr>" for k, v in sorted(reasons.items(), key=lambda kv: str(kv[0]))) or "<tr><td colspan='2'>No quarantined records.</td></tr>"
    return "<section class='card'><h2>Quarantine reasons</h2><table><thead><tr><th>Reason</th><th>Count</th></tr></thead><tbody>" + rows + "</tbody></table></section>"


def _review_sections(import_run_id: str, details: dict[str, Any], query: dict[str, list[str]]) -> str:
    size = min(PAGE_SIZE_MAX, max(1, int((query.get("page_size") or [PAGE_SIZE_DEFAULT])[0] or PAGE_SIZE_DEFAULT)))
    page = max(1, int((query.get("page") or [1])[0] or 1))
    candidates = _filter_candidates(details.get("candidates", []), query)
    effects = {e.get("candidate_id"): e for e in details.get("effects", [])}
    sections = [
        ("Records ready for canonical acceptance", lambda c: effects.get(c.get("candidate_record_id"), {}).get("effect_type") in {"create","update","unchanged","mapped"}),
        ("Quarantined records", lambda c: c.get("validation_status") == "quarantined"),
        ("Rejected records", lambda c: c.get("validation_status") == "rejected"),
        ("Conflicts", lambda c: effects.get(c.get("candidate_record_id"), {}).get("effect_type") == "conflict"),
        ("Unresolved references", lambda c: effects.get(c.get("candidate_record_id"), {}).get("effect_type") == "unresolved"),
        ("Projection-only records", lambda c: effects.get(c.get("candidate_record_id"), {}).get("effect_type") == "projection"),
        ("Sheet-by-sheet breakdown", lambda c: True),
    ]
    out = _filter_form(import_run_id, query)
    for title, pred in sections:
        out += _candidate_table(title, [c for c in candidates if pred(c)], effects, page, size)
    return out


def _filter_form(import_run_id, query):
    fields = ["source worksheet", "record class", "disposition", "quarantine reason", "rejection reason", "canonical/projection-only", "external ID"]
    inputs = "".join(f"<label>{escape(f.title())}<input name='{escape(f.replace(' ', '_').replace('/', '_'))}' value='{escape((query.get(f.replace(' ', '_').replace('/', '_')) or [''])[0])}'></label>" for f in fields)
    return f"<section class='card'><h2>Filters</h2><form method='get' action='/blueprint-import/{escape(import_run_id)}/review'>{inputs}<label>Page size<input name='page_size' value='{PAGE_SIZE_DEFAULT}'></label><p><button>Apply filters</button></p></form></section>"


def _filter_candidates(candidates, query):
    def q(name): return ((query.get(name) or [""])[0] or "").lower()
    out = []
    for c in candidates:
        if q("source_worksheet") and q("source_worksheet") not in str(c.get("source_sheet","")).lower(): continue
        if q("record_class") and q("record_class") not in str(c.get("candidate_object_class","")).lower(): continue
        if q("disposition") and q("disposition") not in str(c.get("validation_status","")).lower(): continue
        if q("external_ID".lower()) and q("external_ID".lower()) not in str(c.get("original_source_id","")).lower(): continue
        out.append(c)
    return out


def _candidate_table(title, candidates, effects, page, size):
    total = len(candidates); start = (page - 1) * size; page_rows = candidates[start:start + size]
    rows = []
    for c in page_rows:
        e = effects.get(c.get("candidate_record_id"), {})
        reason = e.get("reason") or "; ".join(str(f.get("message", "")) for f in c.get("validation_findings", []))
        rows.append(f"<tr><td>{escape(str(c.get('source_sheet','')))}</td><td>{escape(str(c.get('original_source_id','')))}</td><td>{escape(str(c.get('candidate_object_class','')))}</td><td>{escape(str(c.get('validation_status','')))}</td><td>{escape(str(e.get('effect_type','')))}</td><td>{escape(reason)}</td></tr>")
    return f"<section class='card'><h2>{escape(title)}</h2><p>Showing {len(page_rows)} of {total}; page size {size}.</p><table><thead><tr><th>Worksheet</th><th>External ID</th><th>Class</th><th>Disposition</th><th>Proposed effect</th><th>Reason</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan=\"6\">No records.</td></tr>'}</tbody></table></section>"


def _load_review_details(coord, import_run_id):
    path = coord.detail_path(import_run_id)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"effects": [], "candidates": []}


def _review_candidate_counts(candidates):
    c = Counter(x.get("validation_status") for x in candidates)
    return {"Accepted": c["accepted"], "Accepted canonical candidates": c["accepted"], "Accepted but non-persistable": 0, "Quarantined": c["quarantined"], "Rejected": c["rejected"], "Unsupported": c["unsupported"]}



def _available_actions_section(package, summary, counts, headers) -> str:
    if not can_restage_blueprint_package(headers, package):
        return ""
    run = escape(package.import_run_id)
    return f"<section class='card'><h2>Available actions</h2><ul><li><a href='/blueprint-import/{run}/restage'>Regenerate review with current validation</a></li><li><a href='/blueprint-import/{run}/review'>View current proposed changes</a></li><li><a href='/blueprint-import/{run}/staging-history'>View prior staging history</a></li></ul></section>"

def _restage_intro(package, summary, counts) -> str:
    run=escape(package.import_run_id)
    projection = sum(1 for c in (summary.get('candidates') or []) if c.get('candidate_object_class') in __import__('cios.applications.flora.blueprint_import.candidates', fromlist=['PROJECTION_ONLY_CLASSES']).PROJECTION_ONLY_CLASSES)
    return f"""<section class='card'><h2>Regenerate review with current validation</h2><p><strong>Current mapping version:</strong> <code>{escape(MAPPING_VERSION)}</code></p><h3>Current staged result</h3><table><tr><th>Accepted</th><td>{counts['accepted']}</td></tr><tr><th>Quarantined</th><td>{counts['quarantined']}</td></tr><tr><th>Rejected</th><td>{counts['rejected']}</td></tr><tr><th>Projection-only</th><td>{projection}</td></tr></table><h3>Regeneration will:</h3><ul><li>reuse the preserved package;</li><li>rerun workbook mapping and constructor validation;</li><li>apply current atomicity rules and quarantine non-promotable observations;</li><li>create a new staging version;</li><li>invalidate the previous review plan;</li><li>generate a new review plan;</li><li>make no canonical changes.</li></ul><form method='post' action='/blueprint-import/{run}/restage'><label><input type='checkbox' name='confirm_restage' value='yes' required> I understand this will replace the active staging result but preserve prior history.</label><p><button type='submit'>Regenerate review with current validation</button></p></form></section>"""

def _blueprint_deployment_metadata(summary: dict[str, Any]) -> dict[str, str]:
    meta = deployment_metadata()
    unavailable = "Unavailable — deployment metadata not configured"
    trace = summary.get("execution_trace") or []
    adapter_id = ""
    adapter_module = ""
    for event in trace:
        adapter_id = adapter_id or str(event.get("workbook_adapter_implementation_identifier") or "")
        adapter_module = adapter_module or str(event.get("workbook_adapter_module") or "")
    return {
        "Git commit SHA": meta.get("commit_sha") or unavailable,
        "Git branch": meta.get("branch") or unavailable,
        "Render service name": os.getenv("RENDER_SERVICE_NAME", "").strip() or unavailable,
        "Build timestamp": meta.get("build_timestamp") or unavailable,
        "Deployment version": meta.get("deployment_version") or unavailable,
        "Service environment": os.getenv("RENDER_ENVIRONMENT", "").strip() or os.getenv("FLORA_ENVIRONMENT", "").strip() or unavailable,
        "Code module version": adapter_module or unavailable,
        "Workbook adapter implementation identifier": adapter_id or unavailable,
    }

def _trace_latest(trace: list[dict[str, Any]], key: str, default: str = "Not recorded") -> str:
    for event in reversed(trace):
        if key in event and event.get(key) not in (None, "", []):
            value = event.get(key)
            if isinstance(value, bool):
                return "yes" if value else "no"
            if isinstance(value, list):
                return ", ".join(str(v) for v in value) or default
            return str(value)
    return default

def _execution_trace_section(package, summary: dict[str, Any], fatal: bool) -> str:
    trace = list(summary.get("execution_trace") or [])
    deployment = _blueprint_deployment_metadata(summary)
    rows = []
    for event in trace:
        rows.append("<tr><td>{}</td><td>{}</td><td><code>{}</code></td><td>{}</td><td>{}</td></tr>".format(
            escape(str(event.get("step_id", ""))),
            escape(str(event.get("action", ""))),
            escape(str(event.get("safe_input_summary", ""))),
            escape(str(event.get("safe_output_summary", ""))),
            escape(str(event.get("status", ""))),
        ))
    trace_table = "<table><thead><tr><th>Step</th><th>Action Flora took</th><th>Input</th><th>Result</th><th>Status</th></tr></thead><tbody>{}</tbody></table>".format("".join(rows) or "<tr><td colspan='5'>No execution trace recorded.</td></tr>")
    pkg_rows = {
        "Package ID": package.identity.package_id,
        "Package version": package.identity.package_version,
        "Enterprise ID": package.identity.enterprise_id,
        "Package checksum": package.package_sha256,
        "Uploaded filename": getattr(package, "original_filename", "") or getattr(package, "filename", "") or "Unavailable — deployment metadata not configured",
        "Workbook path selected": _trace_latest(trace, "workbook_path_selected"),
        "Workbook SHA-256 result": _trace_latest(trace, "workbook_sha256"),
        "Workbook SHA-256 expected": _trace_latest(trace, "workbook_sha256_expected"),
        "Workbook SHA-256 actual": _trace_latest(trace, "workbook_sha256_actual"),
        "Workbook hash matches": _trace_latest(trace, "workbook_sha256_matches"),
        "Resolved workbook ZIP member": _trace_latest(trace, "resolved_zip_member_path"),
    }
    workbook_rows = {
        "Workbook adapter module": _trace_latest(trace, "workbook_adapter_module"),
        "Resolver function name": _trace_latest(trace, "resolver_function_name"),
        "Source OOXML part": _trace_latest(trace, "source_ooxml_part"),
        "Relationship file": _trace_latest(trace, "relationship_file"),
        "Sheet name": _trace_latest(trace, "sheet_name"),
        "Relationship ID": _trace_latest(trace, "relationship_id"),
        "Original relationship target": _trace_latest(trace, "original_relationship_target"),
        "Target classification": _trace_latest(trace, "target_classification"),
        "Normalized target": _trace_latest(trace, "normalized_target"),
        "Final ZIP lookup path": _trace_latest(trace, "final_zip_lookup_path"),
        "ZIP member exists": _trace_latest(trace, "zip_member_exists"),
        "Nearest matching ZIP members": _trace_latest(trace, "nearest_matching_zip_members"),
    }
    flow_rows = {
        "Current stage": _trace_latest(trace, "current_stage", "validation_result"),
        "Previous completed stage": _trace_latest(trace, "previous_completed_stage"),
        "Next intended stage": _trace_latest(trace, "next_intended_stage"),
        "Processing stopped": _trace_latest(trace, "processing_stopped", "yes" if fatal else "no"),
        "Stop reason": _trace_latest(trace, "stop_reason", "; ".join(summary.get("errors", [])) or "None"),
        "Canonical changes made": _trace_latest(trace, "canonical_changes_made", "no"),
        "Promotion enabled": "no" if fatal else _trace_latest(trace, "promotion_enabled", "yes"),
    }
    def table(title, values):
        return "<h3>{}</h3><table>{}</table>".format(escape(title), "".join(f"<tr><th>{escape(k)}</th><td><code>{escape(str(v))}</code></td></tr>" for k,v in values.items()))
    requested = _trace_latest(trace, "final_zip_lookup_path")
    expected = _trace_latest(trace, "nearest_matching_zip_members")
    guidance = "Flora found the workbook but generated an invalid internal worksheet path. The Blueprint package should remain unchanged. A Flora workbook-adapter fix is required." if fatal and requested != "Not recorded" else ("Review the proposed changes when validation passes." if not fatal else "Keep the package unchanged and share this diagnostic trace with support.")
    plain = f"<p><strong>Plain-English explanation:</strong> Flora read worksheet relationship target <code>{escape(_trace_latest(trace, 'original_relationship_target'))}</code>, normalized it to <code>{escape(_trace_latest(trace, 'normalized_target'))}</code>, checked <code>{escape(requested)}</code>, and found ZIP member exists: <strong>{escape(_trace_latest(trace, 'zip_member_exists'))}</strong>. Processing stopped before candidate staging: <strong>{'yes' if fatal else 'no'}</strong>. No canonical Twin changes were made.</p>"
    copy = json.dumps({"deployment": deployment, "package": pkg_rows, "workbook_processing": workbook_rows, "validation_flow": flow_rows, "events": trace}, sort_keys=True)
    return "<section class='card'><h2>Blueprint import execution trace</h2>{plain}{trace_table}{deployment}{package}{workbook}{flow}<h3>Owner next action</h3><p>{guidance}</p><p><button type='button' data-diagnostic-trace='{copy}'>Copy diagnostic trace</button> <a download='blueprint-import-trace.json' href='data:application/json,{copy}'>Download diagnostic trace as JSON</a></p></section>".format(plain=plain, trace_table=trace_table, deployment=table("Deployment", deployment), package=table("Package", pkg_rows), workbook=table("Workbook processing", workbook_rows), flow=table("Validation flow", flow_rows), guidance=escape(guidance), copy=escape(copy, quote=True))

def _candidate_counts(candidates): return Counter(c.get("validation_status", "unsupported") for c in candidates)
def _counts_section(c): return f"<section class='card'><h2>Candidate staging summary</h2><p>Accepted {c['accepted']} · Quarantined {c['quarantined']} · Rejected {c['rejected']} · Unsupported {c['unsupported']}</p></section>"
def _package_name(p): return getattr(p.identity, "package_name", "") or p.identity.package_id
def _twin_version(p): return getattr(p.identity, "twin_version", "") or p.identity.package_version
def _package_header(p): return f"<section class='hero'><h1>{escape(_package_name(p))}</h1><p>Version {escape(p.identity.package_version)} · Enterprise {escape(p.identity.enterprise_id)}</p></section>"
def _notice(m): return f"<p class='pill'>{escape(m)}</p>" if m else ""
def _list(t, xs): return f"<h3>{escape(t)}</h3><ul>{''.join(f'<li>{escape(str(x))}</li>' for x in xs) or '<li>None</li>'}</ul>"
def _worksheets(warnings):
    for w in warnings:
        if str(w).startswith("Worksheets discovered:"): return [x.strip() for x in str(w).split(":",1)[1].split(",") if x.strip()]
    return []
def _exceptions(effects): return "<details><summary>Important exceptions</summary><ul>" + "".join(f"<li>{escape(e.external_id)} — {escape(e.effect_type)}: {escape(e.reason)}</li>" for e in effects) + "</ul></details>"
def _projection_count(import_run_id): return sum(1 for p in DryRunPlanRepository().list(import_run_id) for e in p.get("effects",[]) if e.get("effect_type") == "projection")
def _latest_promotion_status(import_run_id):
    import json
    from cios.applications.flora.storage import data_path
    root=data_path("blueprint_import","promotion","executions",import_run_id)
    if not root.exists(): return "not promoted"
    vals=[json.loads(p.read_text()).get("final_execution_status", "unknown") for p in root.glob("*.json")]
    return vals[-1] if vals else "not promoted"
_DIAGNOSTIC_STAGES = (
    "Account recognised",
    "Workspace recognised",
    "Membership resolved",
    "Owner status resolved",
    "Blueprint upload capability resolved",
    "Upload request accepted",
    "Package received",
    "Package identity read",
    "Package enterprise access resolved",
    "Package inspection authorised",
    "Package stored",
    "Package validated",
    "Import preview generated",
    "Canonical import committed",
)


def _stage_statuses(failed_stage: str, decision=None) -> dict[str, str]:
    statuses = {stage: "Not started" for stage in _DIAGNOSTIC_STAGES}
    if decision:
        if not decision.user_id:
            statuses["Account recognised"] = "Failed"
            return statuses
        statuses["Account recognised"] = "Passed"
        if not decision.active_workspace:
            statuses["Workspace recognised"] = "Failed"
            return statuses
        statuses["Workspace recognised"] = "Passed"
        if decision.resolved_membership != "resolved":
            statuses["Membership resolved"] = "Failed"
            return statuses
        statuses["Membership resolved"] = "Passed"
        if not decision.resolved_role:
            statuses["Owner status resolved"] = "Failed"
            return statuses
        statuses["Owner status resolved"] = "Passed"
        statuses["Blueprint upload capability resolved"] = "Passed" if decision.decision == "allowed" else "Failed"
        if decision.decision != "allowed":
            return statuses
        passed_after_upload = {
            "Upload request accepted": ["Upload request accepted", "Package received", "Package identity read", "Package enterprise access resolved", "Package inspection authorised", "Package stored", "Package validated", "Import preview generated", "Canonical import committed"],
            "Package received": ["Package received", "Package identity read", "Package enterprise access resolved", "Package inspection authorised", "Package stored", "Package validated", "Import preview generated", "Canonical import committed"],
            "Package identity read": ["Package identity read", "Package enterprise access resolved", "Package inspection authorised", "Package stored", "Package validated", "Import preview generated", "Canonical import committed"],
            "Package enterprise access resolved": ["Package enterprise access resolved", "Package inspection authorised", "Package stored", "Package validated", "Import preview generated", "Canonical import committed"],
            "Package inspection authorised": ["Package inspection authorised", "Package stored", "Package validated", "Import preview generated", "Canonical import committed"],
            "Package stored": ["Package stored", "Package validated", "Import preview generated", "Canonical import committed"],
            "Package validated": ["Package validated", "Import preview generated", "Canonical import committed"],
        }
        for stage in _DIAGNOSTIC_STAGES:
            if stage in {"Account recognised", "Workspace recognised", "Membership resolved", "Owner status resolved", "Blueprint upload capability resolved"}:
                continue
            if failed_stage in passed_after_upload and stage not in passed_after_upload[failed_stage]:
                statuses[stage] = "Passed"
        if failed_stage in statuses:
            statuses[failed_stage] = "Failed"
        return statuses
    if failed_stage in statuses:
        statuses[failed_stage] = "Failed"
    return statuses


def _failure_summary(message: str) -> str:
    import re
    parts = [p.strip() for p in re.split(r"[;\n]+", str(message or "")) if p.strip()]
    if len(parts) <= 3 and len(str(message)) <= 500:
        return f"<p>{escape(str(message))}</p>"
    grouped = Counter(p.split(":", 1)[0].strip() for p in parts)
    examples = "".join(f"<li>{escape(p)}</li>" for p in parts[:5])
    groups = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>" for k, v in grouped.most_common())
    details = escape(str(message), quote=True)
    return f"<p>{len(parts)} validation failure details were reported. First affected items:</p><ul>{examples}</ul><h3>Grouped failure reasons</h3><table><tbody>{groups}</tbody></table><details><summary>Expandable failure details</summary><pre>{details}</pre></details><p><a download='blueprint-failure-details.txt' href='data:text/plain,{details}'>Download details</a></p>"

def _safe_failure(message, stage, changed, retry, next_step, decision=None, diagnostic_ref: str = "", audit_warning: str = ""):
    diagnostic_ref = diagnostic_ref or f"bpi-diag-{uuid4().hex[:12]}"
    unavailable = "Authorisation context unavailable after failure"
    account = decision.user_id if decision and decision.user_id else unavailable
    workspace = decision.active_workspace if decision and decision.active_workspace else ("No active workspace" if decision else unavailable)
    role = decision.resolved_role if decision and decision.resolved_role else ("No effective Blueprint role" if decision else unavailable)
    owner = "yes" if decision and decision.owner_recognised else "no"
    capability = decision.required_permission if decision else "package.upload"
    rows = "".join(f"<tr><th>{escape(name)}</th><td>{escape(status)}</td></tr>" for name, status in _stage_statuses(stage, decision).items())
    warning_panel = f"<section class='card warning'><h2>Diagnostics warning</h2><p>{escape(audit_warning)}</p><p>Diagnostic reference: <code>{escape(diagnostic_ref)}</code></p><p>No canonical changes occurred.</p></section>" if audit_warning else ""
    failure_summary = _failure_summary(message)
    body=f"<section class='hero'><h1>Blueprint import needs attention</h1></section>{warning_panel}<section class='card'><h2>What happened</h2>{failure_summary}<ul><li>Stage failed: {escape(stage)}</li><li>Canonical changes occurred: {'yes' if changed else 'no'}</li><li>Package available for retry: {'yes' if retry else 'no'}</li><li>Diagnostic reference: <code>{escape(diagnostic_ref)}</code></li><li>Next step: {escape(next_step)}</li></ul><p><a href='/blueprint-import'>Return to Blueprint</a></p></section><section class='card'><h2>Authorisation context</h2><table><tr><th>Signed-in account</th><td>{escape(account)}</td></tr><tr><th>Active workspace</th><td>{escape(workspace)}</td></tr><tr><th>Effective role</th><td>{escape(role)}</td></tr><tr><th>Owner recognised</th><td>{owner}</td></tr><tr><th>Required Blueprint capability</th><td><code>{escape(capability)}</code></td></tr></table></section><section class='card'><h2>Live import stages</h2><table>{rows}</table></section>"
    return _page("Blueprint import failure", body)
def _canonical_marker():
    from cios.applications.flora.storage import data_path
    files=[]
    for rel in [("memory","evidence.jsonl"),("memory","observations.jsonl")]:
        p=data_path(*rel); files.append(sha256_bytes(p.read_bytes()) if p.exists() else "missing")
    return tuple(files)


def _permission_guidance(headers: Any, decision=None) -> str:
    decision = decision or blueprint_upload_authorisation(headers)
    if is_cios_owner(headers):
        if not decision.workspace_ids:
            return "Switch to the owning workspace."
        if decision.denial_reason == "Blueprint upload capability is missing from the owner role":
            return "Blueprint upload capability is missing from the owner role."
        return "Sign out and sign back in to refresh owner permissions. If it still fails, contact support with the diagnostic reference."
    if not authenticated_flora_user(headers):
        return "Sign in for pilot access to import Blueprints in this workspace."
    return "You do not have permission to import Blueprints in this workspace."


def _audit_authorisation(event_type: str, headers: Any, stage: str, decision, package_ref: str = "", import_run_id: str = "", enterprise_id: str = "") -> tuple[str, str]:
    diagnostic_ref = f"bpi-diag-{uuid4().hex[:12]}"
    payload = {
        "diagnostic_reference": diagnostic_ref,
        "request_correlation_id": diagnostic_ref,
        "actor": decision.user_id,
        "user_id": decision.user_id,
        "workspace_ids": list(decision.workspace_ids),
        "workspace_id": enterprise_id or decision.active_workspace,
        "enterprise_id": enterprise_id or (decision.workspace_ids[0] if len(decision.workspace_ids) == 1 else ""),
        "resolved_membership": decision.resolved_membership,
        "resolved_role": decision.resolved_role,
        "owner_status": "recognised" if decision.owner_recognised else "not recognised",
        "raw_roles": list(decision.raw_roles),
        "roles": list(decision.effective_roles),
        "effective_permissions": list(decision.effective_permissions),
        "required_permission": decision.required_permission,
        "permission_source": decision.policy_source,
        "policy_name": decision.policy_name,
        "policy_source": decision.policy_source,
        "permission_decision": decision.decision,
        "decision": decision.decision,
        "denial_reason": decision.denial_reason,
        "authenticated": "yes" if decision.user_id else "no",
        "authentication_source": getattr(decision, "authentication_source", "none"),
        "workspace_resolved": "yes" if decision.active_workspace else "no",
        "membership_resolved": "yes" if decision.resolved_membership == "resolved" else "no",
        "owner_recognised": "yes" if decision.owner_recognised else "no",
        "request_route": "blueprint_import",
        "deployment_version": __import__("os").environ.get("FLORA_DEPLOYMENT_VERSION", "unknown"),
        "migration_version": "2026-07-10-blueprint-session-context",
        "blueprint_package_ref": package_ref,
        "import_run_id": import_run_id,
        "stage": stage,
        "result": "failed" if decision.decision == "denied" else "allowed",
        "failure_reason": decision.denial_reason,
        "import_job_id": "",
    }
    try:
        BlueprintImportLedger().append(event_type, payload)
    except PersistenceError as exc:
        path = str(BlueprintImportLedger().path.parent)
        warning = {
            "message": "Blueprint diagnostics could not be persisted.",
            "diagnostic_reference": diagnostic_ref,
            "request_correlation_id": diagnostic_ref,
            "event_type": event_type,
            "storage_path": path,
            "exception_type": type(exc).__name__,
            "exception_summary": str(exc),
            "deployment_version": __import__("os").environ.get("FLORA_DEPLOYMENT_VERSION", "unknown"),
            "storage_mode": storage_mode().get("mode"),
        }
        LOGGER.warning("blueprint_audit_persistence_failed %s", json.dumps(warning, sort_keys=True), extra={"flora_event": warning})
        return diagnostic_ref, "Blueprint diagnostics could not be persisted."
    LOGGER.info("blueprint_authorisation_audit_recorded", extra={"flora_event": {"diagnostic_reference": diagnostic_ref, "event_type": event_type}})
    return diagnostic_ref, ""
