"""Plain-language Flora Blueprint Import web experience."""
from __future__ import annotations

from collections import Counter
import json
import logging
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
from .promotion import CanonicalPromotionRepository, CanonicalPromotionService, BlueprintPromotionError, can_approve_blueprint_promotion, can_execute_blueprint_promotion
from .registry import BlueprintPackageRegistry
from .review import CandidateReviewRepository, CandidateReviewService, can_review_blueprint_candidate
from .validator import BlueprintPackageValidator, BlueprintValidationError, can_inspect_blueprint_package
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
    deployment = deployment_metadata()
    deployment_rows = "".join(f"<tr><th>{escape(key.replace('_', ' ').title())}</th><td><code>{escape(value)}</code></td></tr>" for key, value in deployment.items())
    body = _package_header(package) + f"""<section class='card'><h2>Validation result</h2><table><tr><th>Checksum</th><td><code>{escape(package.package_sha256)}</code></td></tr><tr><th>Files inspected</th><td>{len(summary.get('files_inspected', []))}</td></tr><tr><th>Workbook discovered</th><td>{'Yes' if any(str(f).endswith(('.xlsx','.xlsm','.xls')) for f in summary.get('files_inspected', [])) else 'Not declared'}</td></tr><tr><th>Worksheets discovered</th><td>{escape(', '.join(worksheets) or 'None reported')}</td></tr><tr><th>Validation status</th><td>{escape(status)}</td></tr></table>{_list('Warnings', summary.get('warnings', []))}{_list('Errors', summary.get('errors', []))}</section><details class='card'><summary><strong>Safe deployment diagnostics</strong></summary><table>{deployment_rows}</table></details>""" + _counts_section(counts) + review_link
    return _page("Blueprint validation result", body), 200


def review_page(import_run_id: str, headers: Any, message: str = "") -> tuple[str, int]:
    ctx = _context(import_run_id)
    if not ctx or not (can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")) and can_review_blueprint_candidate(headers, ctx["package"].identity.enterprise_id)):
        return _safe_failure("You are not authorised to review this Blueprint import.", "review", False, True, "Ask for Blueprint review permission."), 403
    summary = ctx.get("summary") or {}
    if summary.get("errors"):
        body = _package_header(ctx["package"]) + _notice(message) + "<section class='card'><h2>Review proposed changes</h2><p><strong>Validation failed.</strong> Proposed-change planning is disabled because workbook or package inspection did not complete safely.</p>{}</section>".format(_list('Errors', summary.get('errors', [])))
        body += "<section class='card'><h2>Approval</h2><p>Approval controls are disabled until fatal validation errors are resolved.</p><button type='button' disabled>Approve and update governed Twin</button></section>"
        return _page("Review Blueprint proposed changes", body), 200
    _ensure_reviews_and_mappings(ctx, headers)
    plan = DryRunPlanningService().create_plan(import_run_id, authenticated_flora_user(headers), headers)
    totals = Counter(e.effect_type for e in plan.effects)
    exceptions = [e for e in plan.effects if e.effect_type in {"conflict", "unresolved", "quarantine", "unsupported", "reject", "defer", "projection"}]
    rows = "".join(f"<tr><th>{escape(k.replace('_',' '))}</th><td>{v}</td></tr>" for k,v in {
        "records to create": totals["create"], "records to update": totals["update"], "records mapped without change": totals["mapped"] + totals["unchanged"], "duplicates": totals["duplicate"], "conflicts": totals["conflict"], "unresolved references": totals["unresolved"], "analytical projections retained outside canonical memory": totals["projection"]}.items())
    body = _package_header(ctx["package"]) + _notice(message) + f"<section class='card'><h2>Review proposed changes</h2><table>{rows}</table><p><strong>Expected governed Twin mutation count:</strong> {plan.expected_canonical_mutation_count}</p>{_exceptions(exceptions)}</section>"
    body += f"""<section class='card'><h2>Approval</h2><p>Approve only if you have reviewed the plan, expected mutation count and unresolved warnings.</p><form method='post' action='/blueprint-import/{escape(import_run_id)}/approve'><input type='hidden' name='plan_id' value='{escape(plan.plan_id)}'><label><input type='checkbox' name='confirm_plan' value='yes' required> I reviewed the plan</label><label><input type='checkbox' name='confirm_mutations' value='yes' required> I understand the expected mutation count is {plan.expected_canonical_mutation_count}</label><label>Approval rationale</label><textarea name='rationale' required></textarea><p><button type='submit'>Approve and update governed Twin</button></p></form><form method='post' action='/blueprint-import/{escape(import_run_id)}/decline'><p><button type='submit'>Decline promotion</button></p></form></section>"""
    return _page("Review Blueprint proposed changes", body), 200


def approve_and_promote(import_run_id: str, form: dict[str, list[str]], headers: Any) -> tuple[str, int]:
    ctx = _context(import_run_id)
    if not ctx or not (can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")) and can_approve_blueprint_promotion(headers, ctx["package"].identity.enterprise_id) and can_execute_blueprint_promotion(headers, ctx["package"].identity.enterprise_id)):
        return _safe_failure("You are not authorised to approve and execute Blueprint promotion.", "approval", False, True, "Ask for Blueprint promotion permission."), 403
    if (ctx.get("summary") or {}).get("errors"):
        return _safe_failure("Validation failed; approval is disabled until fatal inspection errors are resolved.", "approval", False, True, "Resolve validation errors, then stage and review again."), 400
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
        if cid not in reviews:
            decision = "approve" if c.get("validation_status") == "accepted" else ("unsupported" if c.get("validation_status") == "quarantined" else "reject")
            reviewer_svc.record_decision(cid, decision, reviewer, "UI default review summary for staged package", headers)
        if c.get("validation_status") == "accepted" and c.get("candidate_object_class") in {"evidence", "observation"} and not c.get("payload", {}).get("proposed_effect"):
            mapper.record_mapping(c, "propose_create", reviewer, headers, c.get("candidate_object_class", "").title())

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


def _safe_failure(message, stage, changed, retry, next_step, decision=None, diagnostic_ref: str = "", audit_warning: str = ""):
    diagnostic_ref = diagnostic_ref or f"bpi-diag-{uuid4().hex[:12]}"
    account = decision.user_id if decision and decision.user_id else "Not signed in"
    workspace = decision.active_workspace if decision and decision.active_workspace else "No active workspace"
    role = decision.resolved_role if decision and decision.resolved_role else "No effective Blueprint role"
    owner = "yes" if decision and decision.owner_recognised else "no"
    capability = decision.required_permission if decision else "package.upload"
    rows = "".join(f"<tr><th>{escape(name)}</th><td>{escape(status)}</td></tr>" for name, status in _stage_statuses(stage, decision).items())
    warning_panel = f"<section class='card warning'><h2>Diagnostics warning</h2><p>{escape(audit_warning)}</p><p>Diagnostic reference: <code>{escape(diagnostic_ref)}</code></p><p>No canonical changes occurred.</p></section>" if audit_warning else ""
    body=f"<section class='hero'><h1>Blueprint import needs attention</h1></section>{warning_panel}<section class='card'><h2>What happened</h2><p>{escape(message)}</p><ul><li>Stage failed: {escape(stage)}</li><li>Canonical changes occurred: {'yes' if changed else 'no'}</li><li>Package available for retry: {'yes' if retry else 'no'}</li><li>Diagnostic reference: <code>{escape(diagnostic_ref)}</code></li><li>Next step: {escape(next_step)}</li></ul></section><section class='card'><h2>Authorisation context</h2><table><tr><th>Signed-in account</th><td>{escape(account)}</td></tr><tr><th>Active workspace</th><td>{escape(workspace)}</td></tr><tr><th>Effective role</th><td>{escape(role)}</td></tr><tr><th>Owner recognised</th><td>{owner}</td></tr><tr><th>Required Blueprint capability</th><td><code>{escape(capability)}</code></td></tr></table></section><section class='card'><h2>Live import stages</h2><table>{rows}</table></section>"
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
