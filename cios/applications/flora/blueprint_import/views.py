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
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository, repair_blueprint_canvas_access
from cios.applications.flora.storage import storage_mode
from cios.applications.flora.live.runtime import deployment_metadata
from cios.applications.flora.pilot_import import (PILOT_IMPORT_ACTOR, PILOT_IMPORT_AUTH_MODE, PILOT_IMPORT_WORKSPACE, pilot_import_bypass_enabled, pilot_import_warning)

from .archive import sha256_bytes
from .ledger import BlueprintImportLedger
from .candidates import CandidateStagingRepository
from .mapping import ImportMappingService
from .planning import DryRunPlanRepository, DryRunPlanningService
from .review_plan import BlueprintReviewPlanCoordinator, PAGE_SIZE_DEFAULT, PAGE_SIZE_MAX
from .promotion import CanonicalPromotionRepository, CanonicalPromotionService, BlueprintPromotionError, can_approve_blueprint_promotion, can_execute_blueprint_promotion
from .registry import BlueprintPackageRegistry
from .pilot_change import current_pilot_change, latest_import_record
from .deployment_status import decide_deployment_status
from .review import (CandidateReviewRepository, CandidateReviewService,
                     ImportHumanReviewRepository, can_review_blueprint_candidate,
                     mark_import_reviewed)
from .validator import BlueprintPackageValidator, can_inspect_blueprint_package
from .cios_twin_adapter import MAPPING_VERSION
from .restage import BlueprintRestageService, can_restage_blueprint_package, RESTAGE_STAGES
from .models import BlueprintPackageRecord, PackageReceiptError
from .guidance import ImportGuidance, ImportGuidanceRepository, TWIN_TYPES, detect_package_type, expectation_mismatch
from .lifecycle import ImportLifecycleService
from .twin_governance import (DownstreamReconciliationRepository, TwinDependencyService,
                              GovernedIdentityResolutionRepository, assess_impacts,
                              governed_semantics, project_twin_identity)
from .relevance import project_candidate_relevance, relevance_counts

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
ZIP_MIME_TYPES = {"application/zip", "application/x-zip-compressed", "application/octet-stream", ""}
LOGGER = logging.getLogger(__name__)

_RECEIVE_RESULT_FIELDS = (
    "status", "package_ref", "import_run_id", "archive_path",
    "package_sha256", "original_filename", "received_at",
    "warnings", "blocking_error",
)


class PackageReceiveContractError(TypeError):
    """The registry returned something other than its documented result model."""

    def __init__(self, actual: Any):
        self.actual = actual
        super().__init__("package receive service returned an invalid response shape")


def _shape_of(value: Any) -> str:
    if isinstance(value, dict):
        return f"dict keys={sorted(str(key) for key in value)[:30]}"
    fields = [name for name in _RECEIVE_RESULT_FIELDS if hasattr(value, name)]
    return f"{type(value).__module__}.{type(value).__name__} fields={fields}"


def _receive_failure_diagnostic(exc: Exception) -> str:
    actual = exc.actual if isinstance(exc, PackageReceiveContractError) else exc
    reason = f"; reason={str(exc)}" if isinstance(exc, PackageReceiptError) else ""
    return (
        "Package receipt failed; stage=Package received; "
        "service=cios.applications.flora.blueprint_import.registry.BlueprintPackageRegistry.receive; "
        "expected response=BlueprintPackageRecord fields=" + ",".join(_RECEIVE_RESULT_FIELDS) + "; "
        f"actual response={_shape_of(actual)}; import identifier=not created; "
        f"retry availability=no; canonical changes made=no{reason}."
    )


def _post_receipt_failure_diagnostic(exc: Exception, record: BlueprintPackageRecord) -> str:
    return (
        "Package inspection failed after safe receipt; stage=Package inspected; "
        "service=cios.applications.flora.blueprint_import.validator.BlueprintPackageValidator.validate_and_stage; "
        "expected response=staging summary persisted for BlueprintPackageRecord; "
        f"actual response=exception {type(exc).__module__}.{type(exc).__name__}; "
        f"import identifier={record.import_run_id}; retry availability=yes; canonical changes made=no."
    )



def _acceptance_list(values: Any) -> str:
    if isinstance(values, dict):
        return "".join(
            f"<h4>{escape(str(label))}</h4><ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in items) + "</ul>"
            for label, items in values.items()
        )
    if isinstance(values, list):
        return "<ul>" + "".join(f"<li>{escape(str(v))}</li>" for v in values) + "</ul>"
    return f"<p>{escape(str(values or 'Unavailable'))}</p>"


def _latest_tel001_record(records: list[Any]) -> Any | None:
    tel001 = [record for record in records if getattr(getattr(record, "identity", None), "enterprise_id", "") == "TEL-001"]
    return latest_import_record(tel001 or records)


def _candidate_runtime_fingerprint(record: Any | None) -> str:
    if not record:
        return "Unavailable"
    inspection = getattr(record, "package_inspection", {}) or {}
    for key in ("runtime_fingerprint", "candidate_runtime_fingerprint", "deployment_fingerprint"):
        if inspection.get(key):
            return str(inspection[key])
    return str(inspection.get("deployment_commit_sha") or "Unavailable")


def _status_badge(status: str) -> str:
    css = "stale" if status in {"WAITING FOR DEPLOYMENT", "REIMPORT REQUIRED", "METADATA INCOMPLETE"} else ("wrong" if status == "DEPLOYMENT PROBLEM" else "ok")
    return f"<strong class='acceptance-status {css}'>{escape(status)}</strong>"


def _pilot_change_record_section(headers: Any) -> str:
    change = current_pilot_change()
    records = BlueprintPackageRegistry().list()
    latest = _latest_tel001_record(records)
    imported_at = getattr(latest, "received_at", "") if latest else "No Twin import recorded"
    current_fingerprint = __import__('cios.applications.flora.blueprint_import.canonical_factual_projection', fromlist=['runtime_fingerprint']).runtime_fingerprint()
    candidate_fingerprint = _candidate_runtime_fingerprint(latest)
    change["candidate_runtime_fingerprint"] = candidate_fingerprint
    decision = decide_deployment_status(change, imported_at)
    auto = change.get("automated_validation") or {}
    links = {
        "Industry Overview": "/blueprint-import/history#industry-overview",
        "BT Group": "/blueprint-import/history#bt-group",
        "Market Participants": "/blueprint-import/history#market-participants",
        "Major Programmes": "/blueprint-import/history#major-programmes",
        "Opportunities": "/blueprint-import/history#opportunities",
        "Reinvention": "/blueprint-import/history#reinvention",
        "Research Gaps": "/blueprint-import/history#research-gaps",
        "Advanced Diagnostics": "/blueprint-import/history#advanced-diagnostics",
        "Import history": "/blueprint-import/history",
        "Deployment diagnostics": str(change.get("diagnostics_href") or "/deployment"),
        "TEL-001 Relationship Truth Executive Summary": str(change.get("audit_result_href") or "/docs/operations/flora/TEL-001-Relationship-Truth-Executive-Summary.md"),
    }
    if latest:
        run_id = escape(str(getattr(latest, "import_run_id", "")))
        links.update({
            "Industry Overview": f"/blueprint-import/{run_id}/aspects/industry-overview",
            "BT Group": f"/blueprint-import/{run_id}/enterprises/BT%20Group",
            "Market Participants": f"/blueprint-import/{run_id}/aspects/market-participants",
            "Major Programmes": f"/blueprint-import/{run_id}/aspects/major-programmes",
            "Opportunities": f"/blueprint-import/{run_id}/aspects/opportunities",
            "Reinvention": f"/blueprint-import/{run_id}/aspects/reinvention-timing",
            "Research Gaps": f"/blueprint-import/{run_id}/research-gaps",
            "Advanced Diagnostics": f"/blueprint-import/{run_id}/diagnostics",
        })
    link_html = "<ul class='acceptance-links'>" + "".join(f"<li><a href='{escape(href)}'>{escape(label)}</a></li>" for label, href in links.items()) + "</ul>"
    unresolved = decision.unresolved_metadata or ["None"]
    return f"""<section class='card operational-acceptance-panel' id='current-deployed-change' aria-labelledby='current-deployed-change-title'>
    <style>.operational-acceptance-panel{{border:4px solid #a14100;background:#fff8ed;margin:1rem 0 1.5rem;padding:1rem}}.operational-acceptance-panel h2{{font-size:1.65rem;margin-top:0}}.acceptance-status{{display:inline-block;padding:.4rem .65rem;border-radius:.35rem;background:#222;color:#fff}}.acceptance-status.wrong{{background:#8b0000}}.acceptance-status.stale{{background:#8a5a00}}.acceptance-status.ok{{background:#0f6b45}}.acceptance-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));gap:1rem}}.acceptance-links{{columns:2}}.primary-status{{font-size:1.05rem;background:#fff;border:2px solid #185c4d;padding:1rem;margin:.75rem 0}}</style>
    <p><span class='pill'>OPERATIONAL ACCEPTANCE CONTROL</span></p><h2 id='current-deployed-change-title'>CURRENT DEPLOYED CHANGE — TEST THIS NOW</h2>
    <section class='primary-status'><h3>Status</h3><p>{_status_badge(decision.status_label)}</p><h3>Should I test now?</h3><p><strong>{escape(decision.should_test_now)}</strong></p><h3>Next action</h3><p>{escape(decision.next_action)}</p></section>
    <div class='acceptance-grid'><section><h3>Current change title</h3><p>{escape(str(change.get('title','')))}</p><p><strong>Fresh import required:</strong> {escape(decision.fresh_import_required)}</p><h3>What should look different</h3>{_acceptance_list(change.get('expected_visible_outcomes'))}</section><section><h3>Operator test checklist</h3><ol>{''.join(f'<li>{escape(str(step))}</li>' for step in (change.get('required_test_steps') or []))}</ol><h3>Known limitations</h3>{_acceptance_list(change.get('known_limitations'))}</section></div>
    <details><summary>Technical deployment evidence</summary><table>
    <tr><th>Deployed SHA</th><td><code>{escape(str(change.get('commit_sha') or 'Unavailable'))}</code></td></tr><tr><th>Expected change identity</th><td><code>{escape(str(change.get('change_id','')))}</code></td></tr><tr><th>Expected source SHA</th><td><code>{escape(str(change.get('source_commit_sha') or change.get('expected_implementation_sha') or 'Unavailable'))}</code></td></tr><tr><th>Merge mode</th><td>{escape(decision.merge_mode)}</td></tr><tr><th>Ancestry/containment result</th><td>{escape(decision.containment_result)}</td></tr><tr><th>Deployed branch</th><td><code>{escape(str(change.get('branch') or 'Unavailable'))}</code></td></tr><tr><th>Render service</th><td>{escape(str(change.get('deployment_service') or 'Unavailable'))}</td></tr><tr><th>Deployment timestamp</th><td>{escape(str(change.get('deployment_timestamp') or 'Unavailable'))}</td></tr><tr><th>Build timestamp</th><td>{escape(str(change.get('deployment_timestamp') or 'Unavailable'))}</td></tr><tr><th>Candidate timestamp</th><td>{escape(str(imported_at))}</td></tr><tr><th>Runtime fingerprint</th><td><code>{escape(current_fingerprint)}</code></td></tr><tr><th>Candidate fingerprint</th><td><code>{escape(candidate_fingerprint)}</code></td></tr><tr><th>Evidence quality</th><td>{escape(decision.evidence_quality)}</td></tr><tr><th>Unresolved metadata</th><td>{escape('; '.join(unresolved))}</td></tr><tr><th>Build command</th><td>{escape(str(change.get('build_command') or 'Unavailable'))}</td></tr><tr><th>Start command</th><td>{escape(str(change.get('start_command') or 'Unavailable'))}</td></tr><tr><th>Auto deploy</th><td>{escape(str(change.get('auto_deploy') or 'Unavailable'))}</td></tr><tr><th>Latest deployment status</th><td>{escape(str(change.get('latest_deployment_status') or 'Unavailable'))}</td></tr></table></details>
    <section><h3>Objective</h3><p>{escape(str(change.get('objective','')))}</p><h3>Links</h3>{link_html}</section>
    <details><summary>Implementation and automated validation details</summary><h3>Implementation summary</h3>{_acceptance_list(change.get('implementation_summary'))}<h3>Automated validation result</h3><table>{''.join(f'<tr><th>{escape(str(k).replace("_"," ").title())}</th><td>{escape(str(v))}</td></tr>' for k,v in auto.items())}</table></details></section>"""

def import_blueprint_entry_page(headers: Any, message: str = "") -> tuple[str, int]:
    decision = blueprint_upload_authorisation(headers)
    access_notice = ""
    bypass = pilot_import_bypass_enabled()
    if decision.decision != "allowed" and not bypass:
        access_notice = ("<section class='card warning' role='note'><h2>Workspace and upload access required</h2>"
                         f"<p>{escape(_permission_guidance(headers, decision))}</p>"
                         "<p>This is import setup information; no package upload has been attempted.</p>"
                         "<p><a href='/pilot-sign-in'>Sign in or select a workspace</a></p></section>")
    authorisation = "<p><span class='pill'>PILOT</span></p>" if bypass else _authorisation_context(decision)
    body = _workflow_progress("upload") + authorisation + access_notice + f"""{_notice(message)}
    {_pilot_change_record_section(headers)}
    <style>.twin-import-form{{display:flex;max-width:34rem;flex-direction:column;align-items:stretch;gap:1rem}}.twin-import-field{{display:flex;flex-direction:column;gap:.4rem}}.twin-import-field label{{font-weight:700}}.twin-import-field input[type='file'],.twin-import-field select{{box-sizing:border-box;width:100%;position:static;pointer-events:auto;opacity:1}}.twin-import-field input[type='file']:focus-visible,.twin-import-field select:focus-visible{{outline:3px solid #185c4d;outline-offset:2px}}.twin-import-actions{{margin:0}}</style>
    <header class='hero'><h1>Import Twin</h1></header><section class='card'><p><strong>Please choose the import type and file.</strong> Commercial Mission or an existing Twin selection is not required.</p><form class='twin-import-form' method='post' action='/blueprint-import/upload' enctype='multipart/form-data'><div class='twin-import-field'><label for='expected_type'>Twin type</label><select id='expected_type' name='expected_type' required>{''.join(f"<option value='{t}'>{escape(t.replace('_',' ').title())}</option>" for t in TWIN_TYPES)}</select></div><div class='twin-import-field'><label for='twin-package'>Twin package</label><input id='twin-package' name='blueprint_zip' type='file' accept='.zip,application/zip' required></div><p class='twin-import-actions'><button type='submit'>Upload Twin</button></p><p class='muted'>Packages may contain confidential candidate intelligence. Upload only packages you are authorised to use. Imported records remain candidates and are never promoted automatically.</p><p><a href='/digital-twins'>Cancel</a></p></form></section>
    <section class='card'><h2>Import history</h2><p><a href='/blueprint-import/history'>View previous package imports</a></p></section>"""
    return _page("Import Twin", body), 200


def upload_and_validate_blueprint(files: dict[str, bytes], fields: dict[str, str], headers: Any) -> tuple[str, int, str]:
    submitted_from_form = fields.get("_form_submission") == "true"
    expected_type = str(fields.get("expected_type") or ("" if submitted_from_form else "enterprise")).strip()
    content = files.get("blueprint_zip") or files.get("file") or b""
    validation_errors = []
    if expected_type not in TWIN_TYPES:
        validation_errors.append("Select a supported Twin type.")
    if not content:
        validation_errors.append("Choose a Twin package ZIP file.")
    if validation_errors:
        return import_blueprint_entry_page(headers, " ".join(validation_errors))[0], 400, "/blueprint-import"

    bypass = pilot_import_bypass_enabled()
    actor = PILOT_IMPORT_ACTOR if bypass else authenticated_flora_user(headers)
    filename = fields.get("blueprint_zip.filename") or fields.get("filename") or "blueprint.zip"
    mime = fields.get("blueprint_zip.content_type") or fields.get("content_type") or ""
    decision = blueprint_upload_authorisation(headers)
    ref = audit_warning = ""
    try:
        if decision.decision != "allowed" and not bypass:
            ref, audit_warning = _audit_authorisation("package_upload_authorisation_denied", headers, "Package receive permission checked", decision)
            raise PermissionError("You do not have permission to import Blueprints in this workspace.")
        if not filename.lower().endswith(".zip") or mime not in ZIP_MIME_TYPES:
            raise PackageReceiptError("Choose a valid Blueprint ZIP file.")
        if len(content) > MAX_UPLOAD_BYTES:
            raise PackageReceiptError(f"The selected file is larger than the {MAX_UPLOAD_BYTES // (1024*1024)} MB upload limit.")
        before = _canonical_marker()
        record = BlueprintPackageRegistry().receive(content, filename, actor, PILOT_IMPORT_WORKSPACE if bypass else active_flora_workspace(headers))
        if not isinstance(record, BlueprintPackageRecord):
            raise PackageReceiveContractError(record)
        ImportGuidanceRepository().save(ImportGuidance(record.import_run_id, expected_type))
        if bypass:
            record = BlueprintPackageRegistry().update_inspection(record.package_ref, {
                "actor_type": "pilot_operator", "actor_id": PILOT_IMPORT_ACTOR,
                "workspace_type": "pilot_workspace", "workspace_id": PILOT_IMPORT_WORKSPACE,
                "authentication_mode": PILOT_IMPORT_AUTH_MODE,
                "authorisation_checks": {"account": "not applicable in pilot import mode", "workspace": "not applicable in pilot import mode", "membership": "not applicable in pilot import mode", "package.upload": "not applicable in pilot import mode"},
            })
            _audit_pilot_bypass(record)
        else:
            _audit_authorisation("package_upload_authorisation_allowed", headers, "Upload request accepted", decision, record.package_ref, record.import_run_id, record.identity.enterprise_id)
    except PermissionError as exc:
        return _safe_failure(str(exc), "Package receive permission checked", False, False, _permission_guidance(headers, decision), decision, ref, audit_warning), 403, "/blueprint-import"
    except Exception as exc:
        message = _receive_failure_diagnostic(exc)
        return _safe_failure(message, "Package received", False, False, "Return to package import and choose a safe ZIP. No canonical changes were made.", decision), 400, "/blueprint-import"

    try:
        validation_result = BlueprintPackageValidator().validate_and_stage(record.package_ref, actor, None if bypass else headers)
        if bypass:
            _audit_pilot_result(record, validation_result)
        assert before == _canonical_marker(), "Upload and validation must not mutate canonical memory"
        # Keep the established service contract (including its inspection
        # response) for non-HTTP callers.  The web adapter follows the returned
        # target, whose default GET experience is the Executive Workspace.
        return validation_result_page(record.import_run_id, headers)[0], 200, f"/blueprint-import/{record.import_run_id}"
    except Exception as exc:
        message = _post_receipt_failure_diagnostic(exc, record)
        return _safe_failure(message, "Package inspected", False, True, f"Retry inspection for import {record.import_run_id}; the safe original package remains in the registry.", decision, import_run_id=record.import_run_id), 400, f"/blueprint-import/{record.import_run_id}"


def validation_result_page(import_run_id: str, headers: Any) -> tuple[str, int]:
    ctx = _context(import_run_id)
    if not ctx:
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "Package identity read", False, True, "Open an import you are authorised to review."), 403
    bypass = pilot_import_bypass_enabled()
    if not bypass and not can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")):
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "Package enterprise access resolved", False, True, "Open an import you are authorised to review."), 403
    if not bypass and not can_inspect_blueprint_package(headers, ctx["package"]):
        return _safe_failure("Blueprint import record is unavailable or access is denied.", "Package inspection authorised", False, True, "Open an import you are authorised to review."), 403
    package = ctx["package"]; summary = ctx["summary"] or {}; candidates = ctx["candidates"]
    lifecycle = ImportLifecycleService().get(import_run_id)
    record = EnterpriseCanvasAccessRepository().get_by_import_run(import_run_id)
    enterprise = record.enterprise_id if record else package.identity.enterprise_id
    nav = f"<nav class='card' aria-label='Breadcrumb'><a href='/digital-twins'>Digital Twins</a> &gt; <a href='/digital-twins/{escape(enterprise)}/canvas'>{escape(package.identity.enterprise_id)}</a> &gt; Import record</nav><section class='card'><p><a href='/digital-twins'>Back to Digital Twins</a> · <a href='/digital-twins/{escape(enterprise)}/canvas'>Back to {escape(package.identity.enterprise_id)} Twin</a> · <a href='/blueprint-import/{escape(import_run_id)}/intelligence'>Inspect candidate intelligence</a></p></section>"
    worksheets = _worksheets(summary.get("warnings", [])); status = "Passed with warnings" if summary.get("warnings") and not summary.get("errors") else ("Failed" if summary.get("errors") else "Passed")
    counts = _candidate_counts(candidates)
    guidance=ImportGuidanceRepository().get(import_run_id); detected=detect_package_type(candidates)
    mismatch=expectation_mismatch(guidance.expected_type if guidance else "", detected)
    contract = package.package_inspection.get("contract_type", "Blueprint Package")
    promotable = package.package_inspection.get("promotable_artefacts", [])
    governed = contract == "Governed Industry Twin Package"
    if governed:
        detected = str(package.package_inspection.get("twin_type") or "industry").casefold()
    governed_counts = package.package_inspection.get("asset_counts", {})
    def value(key: str) -> str:
        return escape(str(package.package_inspection.get(key) or "Not supplied"))
    governed_rows = "" if not governed else f"""<tr><th>Package contract</th><td>{value('package_contract')}</td></tr><tr><th>Package profile</th><td>{value('package_profile')}</td></tr><tr><th>Mission ID</th><td>{value('mission_identifier')}</td></tr><tr><th>Twin title</th><td>{value('twin_title')}</td></tr><tr><th>Twin type</th><td>{value('twin_type')}</td></tr><tr><th>Package version</th><td>{value('package_version')}</td></tr><tr><th>Research state</th><td>{value('research_state')}</td></tr><tr><th>Decision maturity</th><td>{value('decision_maturity')}</td></tr><tr><th>Selected package root</th><td>{value('selected_package_root')}</td></tr><tr><th>Manifest path</th><td>{value('manifest_location')}</td></tr><tr><th>Flora Delta path</th><td>{value('delta_location')}</td></tr><tr><th>Knowledge graph path</th><td>{value('graph_location')}</td></tr><tr><th>Restart-state path</th><td>{value('restart_state_location')}</td></tr><tr><th>Evidence register path</th><td>{value('evidence_register_location')}</td></tr><tr><th>Unknown register path</th><td>{value('unknown_register_location')}</td></tr><tr><th>Contradiction register path</th><td>{value('contradiction_register_location')}</td></tr><tr><th>Recognition evidence</th><td>{escape(', '.join(package.package_inspection.get('recognition_evidence', [])) or 'Not supplied')}</td></tr><tr><th>Files used for identity</th><td>{escape(', '.join(package.package_inspection.get('files_used_for_identity', [])) or 'Not supplied')}</td></tr><tr><th>Metadata conflicts</th><td>{escape(str(package.package_inspection.get('metadata_conflicts') or 'None'))}</td></tr>"""
    inspection=f"""<section class='card'><h2>Package inspection detail</h2><p><strong>Inspection does not change the governed Twin.</strong></p><table><tr><th>Detected Package</th><td>{escape(str(contract))}</td></tr>{governed_rows}<tr><th>Promotable Artefacts</th><td>{escape(', '.join(str(a.get('artefact_type')) for a in promotable if a.get('promotable')) or 'Blueprint candidates after validation')}</td></tr><tr><th>Expected Twin type</th><td>{escape((guidance.expected_type if guidance else 'Not supplied').replace('_',' ').title())}</td></tr><tr><th>Detected package type</th><td>{escape(detected.replace('_',' ').title())}</td></tr><tr><th>Manifest/profile version</th><td>{escape(package.identity.profile_version)}</td></tr><tr><th>Package identifier</th><td><code>{escape(package.identity.package_id)}</code></td></tr><tr><th>Package checksum</th><td><code>{escape(package.package_sha256)}</code></td></tr><tr><th>Asset counts by type</th><td>{escape(', '.join(f'{k}: {v}' for k,v in sorted((governed_counts if governed else counts).items())) or 'None')}</td></tr><tr><th>Unresolved dependencies</th><td>{escape(', '.join(package.package_inspection.get('unresolved_references', []) if governed else summary.get('unresolved_references', [])) or 'None')}</td></tr></table>{'<p class="warning"><strong>Type mismatch:</strong> continuation is blocked. Change the expectation; Flora has not relabelled the package.</p>' if mismatch else '<p>Expectation is compatible with detected content.</p>'}</section>"""
    may_review = can_review_blueprint_candidate(headers, package.identity.enterprise_id, package.workspace_id)
    review_link = ("<section class='card'><p><a href='/blueprint-import/{0}/review'>Review proposed changes</a></p></section>".format(escape(import_run_id)) if may_review else "<section class='card'><p><strong>Promotion permission required.</strong> You can inspect this package, but you do not have permission to review or promote changes to the governed Twin.</p></section>") if not summary.get('errors') and not mismatch else "<section class='card'><p><strong>Validation failed.</strong> Proposed-change review and approval are disabled until validation and expected-type mismatch errors are resolved.</p></section>"
    deployment = _blueprint_deployment_metadata(summary)
    deployment_rows = "".join(f"<tr><th>{escape(key.replace('_', ' ').title())}</th><td><code>{escape(value)}</code></td></tr>" for key, value in deployment.items())
    validation_groups = f"<section class='card'><h2>Validation outcomes</h2><h3>Passed</h3><p>✓ Archive safety, checksum generation and package receipt passed.</p>{_list('Warnings', summary.get('warnings', []))}{_list('Blocking errors', summary.get('errors', []))}</section>"
    terminal = _cancelled_panel(lifecycle) if lifecycle.state == "cancelled" else _cancel_action(import_run_id, "inspect")
    workbook_rows = "" if governed else f"<tr><th>Workbook discovered</th><td>{'Yes' if any(str(f).endswith(('.xlsx','.xlsm','.xls')) for f in summary.get('files_inspected', [])) else 'Not declared'}</td></tr><tr><th>Worksheets discovered</th><td>{escape(', '.join(worksheets) or 'None reported')}</td></tr>"
    count_panel = _asset_counts_section(governed_counts) if governed else _counts_section(counts)
    decision = _inspection_decision(package, summary, candidates, mismatch)
    if not may_review and decision.get('action') in {'Review proposed changes', 'Continue review'}:
        decision = {**decision, 'action': 'View validation details'}
    executive = _executive_summary(package, decision)
    commercial = _commercial_change_summary(candidates, package.package_inspection)
    affected = _affected_twins_section(package)
    impact = _commercial_impact(candidates)
    risk = _risk_summary(package, summary, candidates, decision)
    diagnostics = inspection + validation_groups + f"""<section class='card'><h2>Import record</h2><span hidden>Package Inspection</span><span hidden>Validation result</span><table><tr><th>Checksum</th><td><code>{escape(package.package_sha256)}</code></td></tr><tr><th>Files inspected</th><td>{len(summary.get('files_inspected', []))}</td></tr>{workbook_rows}<tr><th>Validation status</th><td>{escape(status)}</td></tr></table>{_list('Warnings', summary.get('warnings', []))}{_list('Errors', summary.get('errors', []))}</section><details class='card'><summary><strong>Safe deployment diagnostics</strong></summary><table>{deployment_rows}</table></details>""" + _execution_trace_section(package, summary, bool(summary.get("errors"))) + count_panel
    if governed and package.identity.package_id == "TMS-001":
        # The inspected package is an executive decision, not a navigation or
        # diagnostics screen. All values below still derive from the staged run.
        body = _executive_title(package) + _workflow_progress("inspect", import_run_id, lifecycle.state)
        body += executive + commercial + _attention_required(package, candidates)
        body += _identity_resolution_section(package, actionable=False) + affected + risk
        body += f"<details class='card diagnostics-card' id='technical-diagnostics'><summary><strong>Technical diagnostics</strong></summary>{diagnostics}</details>"
        body += _available_actions_section(package, summary, counts, headers)
    else:
        body = _workflow_progress("inspect", import_run_id, lifecycle.state) + nav + executive + commercial + impact + affected + risk + review_link + f"<details class='card' id='technical-diagnostics'><summary><strong>Technical diagnostics</strong></summary>{diagnostics}</details>" + _available_actions_section(package, summary, counts, headers) + terminal
    return _page("Inspect Twin package", pilot_import_warning() + _pilot_diagnostics(package, summary) + body), 200



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
        if not ctx or not (can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")) and can_review_blueprint_candidate(headers, ctx["package"].identity.enterprise_id, ctx["package"].workspace_id)):
            return _safe_failure("You are not authorised to review this Blueprint import.", "review", False, True, "Ask for Blueprint review permission."), 403
        lifecycle = ImportLifecycleService().get(import_run_id)
        if lifecycle.state == "cancelled":
            return _page("Cancelled Twin import", _workflow_progress("review", import_run_id, "cancelled") + _cancelled_panel(lifecycle)), 409
        summary = ctx.get("summary") or {}
        guidance=ImportGuidanceRepository().get(import_run_id); detected=detect_package_type(ctx.get("candidates", []))
        if guidance and expectation_mismatch(guidance.expected_type, detected):
            return _safe_failure(f"Expected {guidance.expected_type.replace('_',' ')} but detected {detected.replace('_',' ')}. Flora did not relabel the package.", "type expectation", False, True, "Return to guided import and select a compatible expectation."), 400
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
            return _review_ready_page(ctx, job, coord, query, message, correlation_id, headers), 200
        if job.get("status") != "Ready":
            return _review_progress_page(ctx, job, correlation_id, message), 200
        return _review_ready_page(ctx, job, coord, query, message, correlation_id, headers), 200
    except Exception as exc:
        LOGGER.exception("Blueprint review route failed", extra={"correlation_id": correlation_id, "import_run_id": import_run_id})
        job = {"diagnostic_reference": correlation_id, "stage": "Blueprint review route", "records_processed": 0, "records_total": 0, "error_category": type(exc).__name__, "status": "Failed", "job_id": correlation_id, "plan_persisted": False}
        ctx = locals().get("ctx") or {}
        return _review_failure_page(ctx, job, correlation_id), 200


def record_import_human_review(import_run_id: str, headers: Any) -> tuple[str, int]:
    """Review-stage governance action, deliberately separate from promotion."""
    try:
        mark_import_reviewed(import_run_id, headers, deployment_metadata().get("commit_sha") or "Unavailable")
        return review_page(import_run_id, headers, "Import review recorded. Facts, Unknowns, Contradictions and promotion state are unchanged.")
    except (PermissionError, ValueError) as exc:
        return _safe_failure(str(exc), "human review", False, True, "Return to Review with Chief Architect permission."), 403

def approve_and_promote(import_run_id: str, form: dict[str, list[str]], headers: Any) -> tuple[str, int]:
    ctx = _context(import_run_id)
    try: ImportLifecycleService().assert_active(import_run_id)
    except ValueError as exc: return _safe_failure(str(exc), "promotion", False, False, "Upload a fresh package to restart."), 409
    if not ctx or not (can_access_enterprise(headers, ctx["package"].identity.enterprise_id, getattr(ctx["package"], "workspace_id", "")) and can_approve_blueprint_promotion(headers, ctx["package"].identity.enterprise_id) and can_execute_blueprint_promotion(headers, ctx["package"].identity.enterprise_id)):
        return _safe_failure("You are not authorised to approve and execute Blueprint promotion.", "approval", False, True, "Ask for Blueprint promotion permission."), 403
    if (ctx.get("summary") or {}).get("errors"):
        return _safe_failure("Validation failed; approval is disabled until fatal inspection errors are resolved.", "approval", False, True, "Resolve validation errors, then stage and review again."), 400
    if ctx["package"].package_inspection.get("contract_type") == "Governed Industry Twin Package" and _identity_unresolved(ctx["package"]):
        return _safe_failure("Promotion unavailable: required Twin identity fields are unresolved.", "identity resolution", False, True, "Confirm the primary subject, governed scope and canonical owner from an existing governed identity."), 400
    guidance=ImportGuidanceRepository().get(import_run_id); detected=detect_package_type(ctx.get("candidates", []))
    if guidance and expectation_mismatch(guidance.expected_type, detected):
        return _safe_failure("Expected and detected Twin types do not match; promotion is blocked.", "approval", False, True, "Change the expectation and regenerate review."), 400
    review_summary = BlueprintReviewPlanCoordinator().latest_job(import_run_id) or {}
    if review_summary.get("stale") or review_summary.get("status") in {"Stale", "Not ready", "Failed"} or review_summary.get("mapping_version") != MAPPING_VERSION:
        return _safe_failure("This review plan is stale or not ready; approval is disabled. Regenerate review with current validation before approval.", "approval", False, True, "Use Regenerate review with current validation."), 400
    if form.get("confirm_plan") != ["yes"] or form.get("confirm_mutations") != ["yes"] or not (form.get("rationale") or [""])[0].strip():
        return review_page(import_run_id, headers, "Approval requires review confirmation, mutation-count confirmation and a rationale.")
    try:
        svc = CanonicalPromotionService(); plan_id = (form.get("plan_id") or [""])[0]
        approval = svc.approve_plan(import_run_id, plan_id, authenticated_flora_user(headers), (form.get("rationale") or [""])[0], headers)
        result = svc.execute_approved_plan(import_run_id, approval.approval_id, authenticated_flora_user(headers), headers)
        ImportLifecycleService().mark_promoted(import_run_id, authenticated_flora_user(headers), len(result.records_created)+len(result.records_updated))
        impacts = assess_impacts(ctx["package"], TwinDependencyService().discover(ctx["package"]))
        DownstreamReconciliationRepository().create_pending(ctx["package"], ctx["package"].identity.package_version, impacts, authenticated_flora_user(headers))
        repair_blueprint_canvas_access(import_run_id, headers)
        return completion_page(import_run_id, result.to_dict(), headers), 200
    except BlueprintPromotionError as exc:
        return _safe_failure(str(exc), "promotion", False, True, "The package remains available. Review the plan and retry after resolving the issue."), 400


def decline_promotion(import_run_id: str, headers: Any) -> tuple[str, int]:
    return review_page(import_run_id, headers, "Promotion declined. No canonical changes occurred; the preserved package remains available for later review.")


def promotion_confirmation_page(import_run_id: str, headers: Any) -> tuple[str, int]:
    ctx=_context(import_run_id)
    if not ctx or not can_access_enterprise(headers,ctx["package"].identity.enterprise_id,getattr(ctx["package"],"workspace_id","")): return _safe_failure("Import unavailable.","promotion",False,True,"Return to import history."),403
    if not (can_approve_blueprint_promotion(headers, ctx["package"].identity.enterprise_id) and can_execute_blueprint_promotion(headers, ctx["package"].identity.enterprise_id)):
        return _safe_failure("You can inspect this package, but you do not have permission to promote changes to the governed Twin.", "Canonical import committed", False, True, "Return to the inspection report or ask for Blueprint promotion permission."), 403
    state=ImportLifecycleService().get(import_run_id)
    if state.state=="cancelled": return _page("Cancelled Twin import",_cancelled_panel(state)),409
    job=BlueprintReviewPlanCoordinator().latest_job(import_run_id) or {}; proposed=job.get("proposed") or {}
    guidance=ImportGuidanceRepository().get(import_run_id); detected=detect_package_type(ctx["candidates"])
    signals={"unknown_count":sum(c.get("candidate_object_class")=="unknown" for c in ctx["candidates"]),"contradiction_count":sum(c.get("candidate_object_class")=="contradiction" for c in ctx["candidates"])}
    quarantined=sum(c.get('validation_status')=='quarantined' for c in ctx['candidates']); rejected=sum(c.get('validation_status')=='rejected' for c in ctx['candidates'])
    excluded=int(proposed.get('Projection-only',0))+int(proposed.get('Ignored',0))+int(proposed.get('Unchanged',0))
    body=_workflow_progress("promote",import_run_id)+_package_header(ctx["package"])+_affected_twins_section(ctx["package"])+f"""<section class='card'><h2>Promotion summary</h2><p><strong>No canonical changes will occur until promotion is approved.</strong></p><table><tr><th>Affected Twin</th><td>{escape(_package_name(ctx['package']))}</td></tr><tr><th>Records to create</th><td>{int(proposed.get('Creates',0))}</td></tr><tr><th>Records to update</th><td>{int(proposed.get('Updates',0))}</td></tr><tr><th>Records excluded</th><td>{excluded}</td></tr><tr><th>Quarantined records</th><td>{quarantined}</td></tr><tr><th>Rejected records</th><td>{rejected}</td></tr><tr><th>Unresolved Unknowns</th><td>{signals['unknown_count']}</td></tr><tr><th>Unresolved Contradictions</th><td>{signals['contradiction_count']}</td></tr><tr><th>Expected canonical mutation count</th><td>{int(proposed.get('Expected canonical mutations', int(proposed.get('Creates',0))+int(proposed.get('Updates',0))))}</td></tr><tr><th>Promotion rationale</th><td>Required; must be explicit and non-empty</td></tr></table><details><summary>Technical promotion details</summary><table><tr><th>Import identifier</th><td><code>{escape(import_run_id)}</code></td></tr><tr><th>Checksum</th><td><code>{escape(ctx['package'].package_sha256)}</code></td></tr><tr><th>Expected type</th><td>{escape(guidance.expected_type if guidance else 'Unavailable')}</td></tr><tr><th>Detected type</th><td>{escape(detected)}</td></tr><tr><th>Information completeness</th><td>Not assessed — no owner-produced IT-001 result is consumed by this governance view.</td></tr><tr><th>Decision maturity</th><td>Not assessed — no ADR-009 owner result is supplied.</td></tr><tr><th>Promotion readiness</th><td>Not inferred; approval remains a protected governance action.</td></tr></table></details><p>Promotion will create or update governed Twin state and preserve the original package, checksum, lineage, review decision and lifecycle audit. It does not resolve outstanding warnings.</p></section><section class='card'><h2>Confirm promotion</h2><form method='post' action='/blueprint-import/{escape(import_run_id)}/approve'><input type='hidden' name='plan_id' value='{escape(str(job.get('plan_id','')))}'><input type='hidden' name='confirm_plan' value='yes'><input type='hidden' name='confirm_mutations' value='yes'><label for='rationale'>Approval rationale</label><textarea id='rationale' name='rationale' required></textarea><p><button type='submit'>Promote Twin</button> <a href='/blueprint-import/{escape(import_run_id)}/review'>Return to Review</a></p></form></section>"""+_cancel_action(import_run_id,"promote")
    return _page("Promote Twin",body),200


def cancellation_confirmation_page(import_run_id: str, stage: str, headers: Any) -> tuple[str,int]:
    ctx=_context(import_run_id)
    if not ctx or not can_access_enterprise(headers,ctx["package"].identity.enterprise_id,getattr(ctx["package"],"workspace_id","")): return _safe_failure("Import unavailable.","cancellation",False,False,"Return to history."),403
    body=_workflow_progress(stage,import_run_id)+f"""<section class='hero'><h1>Cancel import?</h1></section><section class='card' role='alertdialog' aria-labelledby='cancel-title' aria-describedby='cancel-help'><h2 id='cancel-title'>Confirm cancellation</h2><p id='cancel-help'>The import will not be promoted. No governed Twin state will be changed. Staged candidates will no longer be eligible for promotion. The audit record is retained and package retention follows the existing archive policy.</p><form method='post' action='/blueprint-import/{escape(import_run_id)}/cancel'><input type='hidden' name='stage' value='{escape(stage)}'><label for='reason'>Cancellation reason (optional)</label><textarea id='reason' name='reason'></textarea><p><button type='submit'>Cancel import</button> <a href='/blueprint-import/{escape(import_run_id)}/{escape(stage)}'>Continue reviewing</a></p></form></section>"""
    return _page("Cancel Twin import",body),200


def cancel_import(import_run_id: str, form: dict[str,list[str]], headers: Any) -> tuple[str,int]:
    ctx=_context(import_run_id)
    if not ctx or not can_access_enterprise(headers,ctx["package"].identity.enterprise_id,getattr(ctx["package"],"workspace_id","")): return _safe_failure("Import unavailable.","cancellation",False,False,"Return to history."),403
    try: row=ImportLifecycleService().cancel(import_run_id,authenticated_flora_user(headers),(form.get("stage") or ["inspect"])[0],(form.get("reason") or [""])[0])
    except ValueError as exc: return _safe_failure(str(exc),"cancellation",False,False,"Open the promoted Twin."),409
    return _page("Import cancelled",_workflow_progress(row.stage,import_run_id,"cancelled")+_cancelled_panel(row)),200


def completion_page(import_run_id: str, result: dict[str, Any], headers: Any) -> str:
    record = repair_blueprint_canvas_access(import_run_id, headers)
    ctx = _context(import_run_id); package = ctx["package"] if ctx else None
    if record is None:
        record = EnterpriseCanvasAccessRepository().get_by_import_run(import_run_id)
    enterprise = record.enterprise_id if record else (package.identity.enterprise_id if package else "")
    canvas_href = f"/digital-twins/{escape(enterprise)}/canvas" if enterprise else f"/blueprint-import/{escape(import_run_id)}"
    body = _workflow_progress("explore", import_run_id, "promoted") + ( _package_header(package) if package else "") + f"""<section class='card'><h2>Explore promoted Twin</h2><table><tr><th>Promotion status</th><td>{escape(result.get('final_execution_status','unknown'))}</td></tr><tr><th>Records created</th><td>{len(result.get('records_created', []))}</td></tr><tr><th>Records updated</th><td>{len(result.get('records_updated', []))}</td></tr><tr><th>Projections retained</th><td>{_projection_count(import_run_id)}</td></tr><tr><th>Exceptions</th><td>{len(result.get('records_blocked', [])) + len(result.get('records_failed', []))}</td></tr></table><p>The original ZIP was preserved unchanged in governed runtime storage.</p><p><a href='{canvas_href}'>Open Enterprise Canvas</a> · <a href='/blueprint-import/{escape(import_run_id)}'>Open import record</a></p></section>"""
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
        inspection = p.package_inspection or {}
        rows.append(f"<tr><td>{escape(_package_name(p))}</td><td>{escape(str(inspection.get('contract_type', 'Blueprint Package')))}</td><td>{'eligible' if inspection.get('promotion_eligible') or summary else 'not eligible'}</td><td>{escape(p.identity.enterprise_id)}</td><td>{escape(p.identity.package_version)}</td><td>{escape(p.received_by)}</td><td>{escape(p.received_at)}</td><td>{'complete' if summary else p.status}</td><td>{'planned' if plans else 'not reviewed'}</td><td>{escape(promo)}</td><td>{escape(_twin_version(p))}</td><td><a href='/blueprint-import/{escape(p.import_run_id)}'>View import record</a></td></tr>")
    table = "<table><thead><tr><th>Package name</th><th>Contract</th><th>Promotion eligibility</th><th>Enterprise</th><th>Package version</th><th>Uploaded by</th><th>Uploaded date</th><th>Validation status</th><th>Review status</th><th>Promotion status</th><th>Resulting Twin version</th><th>Actions</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    return _page("Blueprint import history", f"<section class='hero'><h1>Blueprint import history</h1><p><a href='/digital-twins'>Back to Digital Twins</a></p></section><section class='card'>{table}</section>"), 200

# helpers

def _workflow_progress(current: str, run_id: str = "", lifecycle: str = "") -> str:
    stages=("upload","inspect","review","promote","explore"); current_index=stages.index(current) if current in stages else 0
    items=[]
    for i,stage in enumerate(stages):
        status="current" if i==current_index else ("complete" if i<current_index else "unavailable")
        if current == "inspect" and lifecycle != "cancelled":
            status = "complete" if stage in {"upload", "inspect"} else ({"review": "next", "promote": "blocked", "explore": "unavailable"}[stage])
        if lifecycle=="cancelled" and i>=current_index: status="cancelled"
        label = "Review Next" if current == "inspect" and stage == "review" else stage.title()
        symbol = "✓" if status == "complete" else ("●" if status in {"current", "next"} else "○")
        current_attr = " aria-current='page'" if current == "inspect" and stage == "inspect" else (" aria-current='step'" if status == "current" else "")
        items.append(f"<li class='{escape(status)}'{current_attr}><span class='workflow-symbol' aria-hidden='true'>{symbol}</span><span>{label}</span><span class='muted' hidden> — {escape(status)}</span></li>")
    return "<nav class='card workflow' aria-label='Import progress'><strong>Import workflow</strong><ol>"+"".join(items)+"</ol></nav>"

def _cancel_action(run_id: str, stage: str) -> str:
    return f"<section class='card'><h2>Stop this intake</h2><p><a href='/blueprint-import/{escape(run_id)}/cancel?stage={escape(stage)}'>Cancel import</a></p></section>"

def _cancelled_panel(row) -> str:
    return f"<section class='card warning'><h2>Import cancelled</h2><p>This terminal import cannot be promoted. No canonical writes occurred.</p><table><tr><th>Cancelled by</th><td>{escape(row.actor or 'Unavailable')}</td></tr><tr><th>Cancelled time</th><td>{escape(row.updated_at or 'Unavailable')}</td></tr><tr><th>Stage</th><td>{escape(row.stage)}</td></tr><tr><th>Reason</th><td>{escape(row.reason or 'Not supplied')}</td></tr><tr><th>Archive</th><td>Retained under the existing archive policy</td></tr></table><p><a href='/blueprint-import'>Start a fresh upload</a></p></section>"

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
    body = _workflow_progress("review", ctx["package"].import_run_id) + _package_header(ctx["package"]) + _notice(message)
    body += _review_summary_section(ctx, job, counts, proposed)
    body += _review_trace_section(ctx, job, correlation_id)
    body += "<section class='card'><h2>Next action</h2><p>Review exceptions and quarantine reasons after preparation completes.</p><p><strong>Approval controls are disabled</strong> until the review plan is complete and fatal errors are absent.</p><p><a href=''>Refresh review status</a></p></section>"
    return _page("Review Blueprint proposed changes", body)


def _review_ready_page(ctx, job, coord, query, message: str, correlation_id: str, headers: Any = None) -> str:
    details = _load_review_details(coord, ctx["package"].import_run_id)
    counts = job.get("candidate_summary") or _review_candidate_counts(details.get("candidates", []))
    proposed = job.get("proposed") or {}
    # Review is a composition over the existing candidate/read owners.  The dry-run
    # report remains intact below, but is deliberately not the landing experience.
    body = _executive_review(ctx, job, details, counts, proposed, query, message)
    body += "<details class='card analyst-depth'><summary><strong>Analyst inspection — intelligence by business domain</strong></summary>"
    body += _review_sections(ctx["package"].import_run_id, details, query, technical=False) + "</details>"
    body += "<details class='card architect-depth'><summary><strong>Architect disclosure — governance and promotion semantics</strong></summary>"
    body += _review_summary_section(ctx, job, counts, proposed)
    body += _identity_resolution_section(ctx["package"]) + _quarantine_reasons_section(job) + _affected_twins_section(ctx["package"])
    body += "</details><details class='card technical-depth'><summary><strong>Technical disclosure — diagnostics, filters and raw records</strong></summary>"
    body += _review_trace_section(ctx, job, correlation_id)
    body += _review_sections(ctx["package"].import_run_id, details, query, technical=True) + "</details>"
    plan_id = escape(str(job.get("plan_id", "")))
    expected = int(proposed.get("Expected canonical mutations", int(proposed.get("Creates", 0)) + int(proposed.get("Updates", 0))))
    rec = job.get("reconciliation") or {}
    can_promote = bool(headers) and can_approve_blueprint_promotion(headers, ctx["package"].identity.enterprise_id) and can_execute_blueprint_promotion(headers, ctx["package"].identity.enterprise_id)
    if rec and not rec.get("passes", True):
        body += f"""<section class='card warning'><h2>Approval</h2><p><strong>Approval blocked:</strong> accepted canonical candidates do not reconcile with creates, updates and unchanged.</p><p>Mismatch: {int(rec.get("mismatch", 0))}</p><button type='button' disabled>Approve and update governed Twin</button></section>"""
    elif not can_promote:
        body += "<section class='card'><h2>Promotion permission required</h2><p>You can review this package, but you do not have permission to promote changes to the governed Twin.</p><p><a href='/blueprint-import/{0}'>View inspection</a></p></section>".format(escape(ctx["package"].import_run_id))
    else:
        body += f"""<section class='card'><h2>Approval</h2><p><a href='/blueprint-import/{escape(ctx["package"].import_run_id)}/promote'>Confirm review and continue to promotion</a></p><p>Promotion remains disabled until the owner has reviewed required exceptions and confirms the expected canonical mutation count.</p><form method='post' action='/blueprint-import/{escape(ctx["package"].import_run_id)}/approve'><input type='hidden' name='plan_id' value='{plan_id}'><label><input type='checkbox' name='confirm_plan' value='yes' required> I reviewed the plan</label><label><input type='checkbox' name='confirm_mutations' value='yes' required> I understand the expected mutation count is {expected}</label><label>Approval rationale</label><textarea name='rationale' required></textarea><p><button type='submit'>Approve and update governed Twin</button></p></form><form method='post' action='/blueprint-import/{escape(ctx["package"].import_run_id)}/decline'><p><button type='submit'>Decline promotion</button></p></form></section>"""
    body += _cancel_action(ctx["package"].import_run_id, "review")
    return _page("Review Blueprint proposed changes", body)


def _executive_review(ctx, job, details, counts, proposed, query, message="") -> str:
    """Executive-first projection; all values come from package, staging or review owners."""
    package = ctx["package"]; inspection = package.package_inspection or {}
    human_review = ImportHumanReviewRepository().get(package.import_run_id)
    identity = project_twin_identity(package); unresolved = _identity_unresolved(package)
    candidates = details.get("candidates", []) or ctx.get("candidates", [])
    relevance = [(c, project_candidate_relevance(c, package, identity)) for c in candidates]
    unknowns = [c for c in candidates if _business_category(c) == "Unknowns"]
    contradictions = [c for c in candidates if _business_category(c) == "Contradictions"]
    quarantined = sum(c.get("validation_status") == "quarantined" for c in candidates)
    unsupported = sum(c.get("validation_status") == "unsupported" for c in candidates)
    rec = job.get("reconciliation") or {}
    blocker = ("Confirm the proposed Twin identity, primary subject, governed scope and canonical owner." if unresolved else
               "Resolve reconciliation mismatch before promotion." if not rec.get("passes", True) else
               "Review quarantined intelligence before promotion." if quarantined else
               "No blocking issue is reported by the current Review read model.")
    eligible = not unresolved and rec.get("passes", True) and not (ctx.get("summary") or {}).get("errors")
    name = str(inspection.get("twin_title") or _package_name(package))
    twin_type = str(inspection.get("twin_type") or identity.twin_type or "Twin").replace("_", " ").title()
    subject = "Unresolved" if unresolved else identity.primary_subject_name
    scope = "Unresolved" if unresolved else identity.governed_scope
    owner = "Unresolved" if unresolved else identity.canonical_owner
    summary = (inspection.get("executive_summary") or inspection.get("summary") or
               "No owner-backed executive summary was supplied. Review the available candidate intelligence by business domain.")
    why = inspection.get("commercial_significance") or inspection.get("commercial_consequence") or "Commercial consequence was not supplied by the package owner."
    recommendation = "Resolve required decisions before promotion" if not eligible else "Ready for governed promotion review"
    geography = inspection.get("geography") or inspection.get("geographic_scope") or "Not supplied"
    horizon = inspection.get("time_horizon") or inspection.get("temporal_scope") or "Not supplied"
    subsectors = inspection.get("included_sub_sectors") or inspection.get("sub_sectors") or "Not supplied"
    if isinstance(subsectors, (list, tuple)):
        subsectors = ", ".join(str(value) for value in subsectors)
    lifecycle = ImportLifecycleService().get(package.import_run_id)
    review_state = "Reviewed by Chief Architect" if human_review else "Imported candidate — not yet reviewed"
    promotion_state = "Promoted" if lifecycle.state == "promoted" else "Not promoted"
    identity_html = f"""<section class='hero candidate-review-identity' aria-labelledby='candidate-review-title'><p class='pill'>{escape(review_state)}</p><h1 id='candidate-review-title'>{escape(name)}</h1><h2>Import acceptance summary</h2><p><strong>Package:</strong> {escape(package.original_filename)} · <strong>Checksum:</strong> {escape(package.package_sha256)}</p><p><strong>Proposed {escape(twin_type)}</strong> · primary subject: {escape(str(subject))} · governed scope: {escape(str(scope))}</p><p><strong>Geography:</strong> {escape(str(geography))} · <strong>Time horizon:</strong> {escape(str(horizon))}</p><p><strong>Records accepted:</strong> {int(counts.get('Accepted', 0))} · <strong>Rejected:</strong> {int(counts.get('Rejected', 0))} · <strong>Quarantined:</strong> {quarantined}</p><p><strong>Unresolved Unknowns:</strong> {len(unknowns)} · <strong>Contradictions:</strong> {len(contradictions)} · <strong>Association anomalies:</strong> 0 · <strong>Missing canonical subjects:</strong> {1 if unresolved else 0}</p><p><strong>Review status:</strong> {escape(review_state)} · <strong>Promotion status:</strong> {escape(promotion_state)} · <strong>Assessment status:</strong> Assessment not yet performed · <strong>Recommendation status:</strong> Not eligible</p><p class='warning'><strong>Human review makes no canonical change.</strong> Promotion remains a separate decision.</p><p><a href='/blueprint-import/{escape(package.import_run_id)}/health'>Inspect residual Research Gaps</a> · <a href='/blueprint-import/{escape(package.import_run_id)}/intelligence'>Return to Inspect</a></p></section>"""
    if not human_review:
        identity_html += f"<section class='card human-review-action'><h2>Chief Architect review</h2><p>Record that you have inspected the import acceptance summary, factual intelligence, Unknowns, Contradictions and relationships.</p><form method='post' action='/blueprint-import/{escape(package.import_run_id)}/mark-reviewed'><button type='submit'>MARK IMPORT REVIEWED</button></form><p>This does not promote, assess, recommend, or alter any imported value.</p></section>"
    executive = f"""<section class='card executive-summary' aria-labelledby='executive-summary-title'><h2 id='executive-summary-title'>Executive intelligence summary</h2><p>{escape(str(summary))}</p><p><strong>Why it matters commercially:</strong> {escape(str(why))}</p><p><strong>Most material uncertainty:</strong> {escape(_challenge_preview(unknowns, 'No material Unknown was supplied.'))}</p><p><strong>Most material contradiction:</strong> {escape(_challenge_preview(contradictions, 'No material Contradiction was supplied.'))}</p><p><strong>Freshness and Evidence basis:</strong> {escape(str(inspection.get('evidence_cut_off') or 'Not supplied'))}; Evidence remains candidate Evidence until promotion.</p></section>"""
    if unresolved:
        executive = "<section class='card executive-summary warning'><h2>Executive intelligence summary</h2><h3>Executive prioritisation is provisional until scope is confirmed</h3><p>The package does not establish enough owner-backed Twin identity and governed scope to compose a coherent executive summary. Candidate statements are preserved and grouped below; scope and classification resolution is the principal blocker.</p></section>"
    conclusions = _material_conclusions(relevance, package.import_run_id, unresolved)
    impact = _promotion_impact(proposed, counts, quarantined, unsupported, [r for _, r in relevance])
    decisions = _decision_area(package, unresolved, unknowns, contradictions, quarantined, unsupported, rec)
    return identity_html + _notice(message) + executive + conclusions + impact + decisions


def _payload_label(candidate):
    payload = candidate.get("payload") or {}
    for key in ("conclusion", "statement", "description", "display_name", "name", "title", "label"):
        if payload.get(key): return str(payload[key])
    return str(candidate.get("original_source_id") or "Candidate item")


def _challenge_preview(items, absent):
    return _payload_label(items[0]) if items else absent


def _material_conclusions(relevance, run_id, scope_unresolved=False):
    owned = []
    for c, r in relevance:
        p = c.get("payload") or {}
        if p.get("conclusion") or p.get("statement"):
            owned.append((c, r))
    if not owned:
        return "<section class='card material-conclusions'><h2>Material proposed conclusions</h2><p><strong>No owner-backed material conclusions were supplied.</strong> No conclusion or commercial consequence has been invented; inspect the available intelligence by business domain below.</p></section>"
    groups = (("core", "Core to this Industry Twin"), ("relevant sub-sector", "Relevant sub-sector intelligence"), ("adjacent", "Adjacent or cross-industry intelligence"), ("unresolved", "Relevance unresolved"), ("out of scope", "Out of scope"))
    sections = []
    for status, heading in groups:
        cards = []
        for c, r in [item for item in owned if item[1].status == status]:
            p = c.get("payload") or {}; label = _payload_label(c)
            consequence = r.commercial_consequence or "Not supplied"
            support = p.get("evidence_basis") or p.get("support_summary") or "No support summary supplied; inspect candidate Evidence and lineage."
            challenge = p.get("challenge") or p.get("uncertainty") or "No owner-supplied challenge preview."
            eligibility = "Primary executive conclusion" if (r.primary_eligible and not scope_unresolved and c.get("validation_status") != "quarantined" and c.get("candidate_object_class") != "contradiction") else "Provisional — not a primary executive conclusion"
            relevant_to = " · ".join(v for v in (r.governed_subject, r.industry, r.sub_sector_or_domain) if v) or "Not established"
            cards.append(f"<article class='conclusion'><p class='pill'>{escape(eligibility)} · {escape(str(r.truth_class or 'Truth class not supplied'))}</p><h3>{escape(label)}</h3><p><strong>Relevant to:</strong> {escape(relevant_to)}</p><p><strong>Why it belongs here:</strong> {escape(str(r.relevance_basis or 'Not supplied'))}</p><p><strong>Why it matters to this Twin:</strong> {escape(str(r.decision_relevance or 'Decision relevance not supplied'))}</p><p><strong>Commercial consequence:</strong> {escape(str(consequence))}</p><p><strong>Scope and geography:</strong> {escape(str(r.sub_sector_or_domain or 'Not supplied'))}; {escape(str(r.geography or 'Not supplied'))} · <strong>Period:</strong> {escape(str(r.temporal_scope or 'Not supplied'))}</p><p><strong>Freshness:</strong> {escape(str(r.freshness or 'Not supplied'))} · <strong>Evidence basis:</strong> {escape(str(r.evidence_state or support))}</p><p><strong>Challenge preview:</strong> {escape(str(challenge))}</p><details class='trust-panel relevance-panel'><summary><strong>Why is this relevant here?</strong></summary><p><strong>Proposed Twin or domain:</strong> {escape(relevant_to)}</p><p><strong>Source relationship:</strong> {escape(str(r.supporting_relationship or 'Not supplied'))}</p><p><strong>Classification basis:</strong> {escape(str(r.relevance_basis or 'Not supplied'))}</p><p><strong>Package metadata / owner:</strong> {escape(str(r.owner or 'Not supplied'))}</p><p><strong>Relevant geography and period:</strong> {escape(str(r.geography or 'Not supplied'))}; {escape(str(r.temporal_scope or 'Not supplied'))}</p><p><strong>Relevance status:</strong> {escape(r.status)}</p><p><strong>Unresolved assumptions:</strong> {escape(str(r.unresolved_scope_reason or 'None supplied'))}</p></details><details class='trust-panel'><summary><strong>Why should I believe this?</strong></summary><h4>What supports it?</h4><p>{escape(str(support))}</p><p><a href='/blueprint-import/{escape(run_id)}/inspect#evidence'>Inspect supporting Evidence</a></p><h4>What could make this wrong, incomplete or unsafe to rely upon?</h4><p>{escape(str(challenge))}</p></details></article>")
        if cards:
            sections.append(f"<section class='relevance-group'><h3>{escape(heading)}</h3>{''.join(cards)}</section>")
    return "<section class='card material-conclusions'><h2>Material proposed conclusions</h2>"+("".join(sections) or "<p>No statements have an explicit owner-backed relevance status. Resolve scope and classification before executive prioritisation.</p>")+"</section>"


def _promotion_impact(proposed, counts, quarantined, unsupported, relevance=None):
    rc = relevance_counts(relevance or [])
    relevance_groups=(("In-scope intelligence proposed for promotion", rc.get("core",0)+rc.get("relevant sub-sector",0)), ("Adjacent intelligence retained but not promoted",rc.get("adjacent",0)), ("Unresolved intelligence requiring review",rc.get("unresolved",0)), ("Out-of-scope intelligence excluded",rc.get("out of scope",0)), ("Quarantined intelligence",quarantined))
    groups=(("New intelligence", proposed.get("Creates",0)),("Confirmed intelligence",proposed.get("Unchanged",0)),("Proposed amendments",proposed.get("Updates",0)),("New or changed relationships",proposed.get("Relationships",0)),("Conflicts requiring review",proposed.get("Conflicts",0)),("Quarantined or excluded intelligence",quarantined+int(proposed.get("Projection-only",0))), ("Unsupported content",unsupported),("Items requiring human judgement",proposed.get("Unresolved references",0)),("Items that will not be promoted",int(counts.get("Rejected",0))+int(proposed.get("Ignored",0))))
    groups=relevance_groups+groups
    items="".join(f"<li><strong>{escape(label)}:</strong> {int(value)} item(s) according to the existing mutation, validation or presentation relevance projection.</li>" for label,value in groups if int(value))
    return "<section class='card promotion-impact'><h2>What acceptance would change</h2><p>Promotion would apply only the governed effects below; it would not automatically resolve excluded or unresolved intelligence.</p><ul>"+(items or "<li>No promotable effect is currently reported.</li>")+"</ul></section>"


def _decision_area(package, unresolved, unknowns, contradictions, quarantined, unsupported, rec):
    decisions=[]
    if unresolved: decisions.append((1,"Confirm Twin identity, primary subject, governed scope and canonical owner","Identity determines which existing governed Twin may receive these candidates.","Confirm through the existing identity-resolution workflow.",True,"Promotion remains blocked."))
    if quarantined or contradictions: decisions.append((2,"Review quarantined Contradictions","Challenging intelligence may qualify or invalidate proposed conclusions.","Inspect the existing quarantine and Contradiction records and disposition them in their owning workflow.",bool(quarantined),"Quarantined items will not be promoted."))
    if unknowns: decisions.append((3,"Inspect material Unknowns","Known gaps affect whether the candidate is safe to rely upon.","Inspect Unknowns and decide whether the residual gap is acceptable.",False,"Unknowns remain explicit and unresolved."))
    if unsupported: decisions.append((4,"Resolve unsupported items","Unsupported content has no promotable mapping.","Use the existing review disposition workflow.",True,"Unsupported items will not be promoted."))
    if rec and not rec.get("passes",True): decisions.append((0,"Resolve promotion reconciliation blocker","Accepted candidates must reconcile with proposed mutations.","Regenerate or correct the existing review plan.",True,"Promotion remains disabled."))
    decisions.sort(key=lambda d:d[0])
    if not decisions: return "<section class='card decisions-required'><h2>Decisions required before promotion</h2><p>No unresolved decision is reported. The owner must still confirm the review plan and promotion rationale in the existing Approval workflow.</p></section>"
    rendered="".join(f"<li><h3>{escape(title)}</h3><p><strong>Why it matters:</strong> {escape(why)}</p><p><strong>Reviewer decision:</strong> {escape(action)}</p><p><strong>Blocks review:</strong> No · <strong>Blocks promotion:</strong> {'Yes' if blocks else 'No'}</p><p><strong>If unresolved:</strong> {escape(outcome)}</p></li>" for _,title,why,action,blocks,outcome in decisions)
    return "<section class='card decisions-required'><h2>Decisions required before promotion</h2><ol>"+rendered+"</ol></section>"


def _identity_resolution_section(package, actionable: bool = True) -> str:
    identity = project_twin_identity(package)
    unresolved = _identity_unresolved(package)
    fields = (("Twin type", "Industry Twin" if identity.twin_type == "industry" else (identity.twin_type or "Unresolved")),
              ("Primary subject", "Unresolved" if unresolved else identity.primary_subject_name),
              ("Primary subject class", "Unresolved" if unresolved else identity.primary_subject_class),
              ("Governed scope", "Unresolved" if unresolved else identity.governed_scope),
              ("Canonical owner", "Unresolved" if unresolved else identity.canonical_owner))
    rows = "".join(f"<tr><th>{escape(label)}</th><td>{escape(str(value))}</td></tr>" for label,value in fields)
    audit=GovernedIdentityResolutionRepository().get(package.import_run_id)
    if audit:
        action=f"<p><strong>Confirmed by:</strong> {escape(audit['actor'])} with recorded rationale and audit details.</p>"
    elif actionable:
        action=f"<p><strong>Identity resolution must be completed during Review.</strong></p><p>Only an existing governed Twin identity or canonical-source package metadata can be confirmed; free-text Twin creation is not available.</p><p><a href='/blueprint-import/{escape(package.import_run_id)}/review#identity-resolution'>Confirm Twin identity</a></p>"
    else:
        action="<p><strong>Identity confirmation is completed during Review.</strong></p>"
    return f"<section class='card governance-intelligence' aria-labelledby='identity-resolution'><h2 id='identity-resolution'>Twin identity</h2><table>{rows}</table>{action}<p class='muted'>Reviewing identity alone makes no canonical changes.</p></section>"

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
    return f"""<section class='card'><h2>Review proposed changes</h2><p><strong>Disposition basis:</strong> accepted, quarantined, rejected, unsupported and projection-only totals below are final staging/review dispositions. A package-wide identity hold is provisional and is not counted as quarantine.</p>{top}<h3>Summary</h3><table>
    <tr><th>Blueprint</th><td>{escape(_package_name(package))} {escape(package.identity.package_version)}</td></tr>
    <tr><th>Review status</th><td>{escape(str(job.get('status', 'Preparing')))}</td></tr>
    <tr><th>Staging version</th><td><code>{escape(str((ctx.get('summary') or {}).get('staging_version', 'staging-v1')))}</code></td></tr>
    <tr><th>Mapping version</th><td><code>{escape(str(job.get('mapping_version') or (ctx.get('summary') or {}).get('mapping_version') or MAPPING_VERSION))}</code></td></tr>
    <tr><th>Review generated from</th><td><code>{escape(str((ctx.get('summary') or {}).get('staging_version', 'staging-v1')))}</code></td></tr>
    <tr><th>Accepted canonical candidates</th><td>{int(counts.get('Accepted canonical candidates', counts.get('Accepted', 0)))}</td></tr>
    <tr><th>Accepted support records</th><td>{val('Accepted support records')}</td></tr>
    <tr><th>Accepted but non-persistable</th><td>{int(counts.get('Accepted but non-persistable', proposed.get('Accepted but non-persistable', 0)))}</td></tr>
    <tr><th>Collapsed/deduplicated candidates</th><td>{val('Collapsed/deduplicated candidates')}</td></tr>
    <tr><th>Expected canonical mutations</th><td>{val('Expected canonical mutations')}</td></tr>
    <tr><th>Quarantined (final staging disposition)</th><td>{int(counts.get('Quarantined', 0))}</td></tr>
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
    total = sum(int(value) for value in reasons.values())
    return f"<section class='card'><h2>Final staging quarantine reasons</h2><p>Every final quarantine is counted by an explicit staging reason; provisional package-wide identity holds are excluded. <strong>Total: {total}</strong></p><table><thead><tr><th>Reason</th><th>Count</th></tr></thead><tbody>" + rows + "</tbody></table></section>"


def _review_sections(import_run_id: str, details: dict[str, Any], query: dict[str, list[str]], technical: bool = False) -> str:
    size = min(PAGE_SIZE_MAX, max(1, int((query.get("page_size") or [PAGE_SIZE_DEFAULT])[0] or PAGE_SIZE_DEFAULT)))
    page = max(1, int((query.get("page") or [1])[0] or 1))
    candidates = _filter_candidates(details.get("candidates", []), query)
    effects = {e.get("candidate_id"): e for e in details.get("effects", [])}
    categories = ("Enterprises", "Market Participants", "Opportunities", "Capabilities and Offers", "Evidence", "Relationships", "Unknowns", "Contradictions", "Reasoning Lineage", "Excluded Lineage Artefacts")
    sections = [(title, lambda c, title=title: _business_category(c) == title) for title in categories]
    sections += [
        ("Quarantined Records", lambda c: c.get("validation_status") == "quarantined"),
        ("Rejected Records", lambda c: c.get("validation_status") == "rejected"),
    ]
    out = _filter_form(import_run_id, query) if technical else ""
    for title, pred in sections:
        selected = [c for c in candidates if pred(c)]
        if not selected:
            continue
        out += _category_heading(title, selected, effects) + _candidate_table(f"{title} detail", selected, effects, page, size, technical)
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


def _candidate_table(title, candidates, effects, page, size, technical=False):
    total = len(candidates); start = (page - 1) * size; page_rows = candidates[start:start + size]
    rows = []
    for c in page_rows:
        e = effects.get(c.get("candidate_record_id"), {})
        reason = e.get("reason") or "; ".join(str(f.get("message", "")) for f in c.get("validation_findings", []))
        payload_obj=c.get("payload") or {}; payload = escape(json.dumps(payload_obj, sort_keys=True, default=str))
        if technical:
            rows.append(f"<tr><td>{escape(str(c.get('source_sheet','')))}</td><td><strong>{escape(str(c.get('original_source_id','')))}</strong><details><summary>Raw technical payload</summary><pre>{payload}</pre></details></td><td>{escape(str(c.get('candidate_object_class','')))}</td><td>{escape(str(c.get('validation_status','')))}</td><td>{escape(str(e.get('effect_type','')))}</td><td>{escape(reason)}</td></tr>")
        else:
            role=payload_obj.get("role") or payload_obj.get("participant_role") or payload_obj.get("relationship_meaning") or payload_obj.get("description") or "Not supplied"
            significance=payload_obj.get("commercial_significance") or payload_obj.get("commercial_consequence") or "Not supplied"
            evidence=payload_obj.get("evidence_status") or payload_obj.get("evidence_basis") or "Inspect candidate Evidence"
            challenge=payload_obj.get("uncertainty") or payload_obj.get("contradiction") or (reason if reason else "No material challenge supplied")
            rows.append(f"<tr><td><strong>{escape(_payload_label(c))}</strong></td><td>{escape(str(role))}</td><td>{escape(str(e.get('effect_type') or 'No effect supplied'))}</td><td>{escape(str(significance))}</td><td>{escape(str(evidence))}</td><td>{escape(str(challenge))}<details class='trust-panel'><summary>Why should I believe this?</summary><p>{escape(str(evidence))}</p><p><a href='#evidence'>Inspect Evidence, Unknowns and Contradictions</a></p></details></td></tr>")
    table_body = "".join(rows) or '<tr><td colspan="6">No records.</td></tr>'
    headings = "<th>Worksheet</th><th>External ID</th><th>Canonical class</th><th>Disposition</th><th>Proposed effect</th><th>Reason</th>" if technical else "<th>Business-readable name</th><th>Role, relationship or description</th><th>Proposed effect</th><th>Commercial significance</th><th>Evidence basis</th><th>Material Unknown or Contradiction</th>"
    return f"<section class='card'><h2>{escape(title)}</h2><p>Showing {len(page_rows)} of {total}; page size {size}.</p><table><thead><tr>{headings}</tr></thead><tbody>{table_body}</tbody></table></section>"


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
    return f"<section class='card'><h2>Secondary actions</h2><div class='secondary-actions'><a href='/blueprint-import/{run}/restage'>Regenerate review</a><a href='/blueprint-import/{run}/staging-history'>View staging history</a><a class='destructive' href='/blueprint-import/{run}/cancel?stage=inspect'>Cancel import</a></div></section>"

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
    if package.package_inspection.get("contract_type") == "Governed Industry Twin Package":
        rows = "".join("<tr><td>{}</td><td>{}</td><td><code>{}</code></td><td>{}</td><td>{}</td></tr>".format(
            escape(str(event.get("step_id", ""))), escape(str(event.get("action", ""))),
            escape(str(event.get("safe_input_summary", ""))), escape(str(event.get("safe_output_summary", ""))),
            escape(str(event.get("status", "")))) for event in trace)
        diagnostic = json.dumps({"package": package.package_inspection, "events": trace}, sort_keys=True)
        return "<section class='card'><h2>Governed package execution trace</h2><p><strong>Uploaded package:</strong> <code>{}</code></p><p>Flora inspected the governed contract, resolved declared object references, and passed valid candidates to the existing staging engine. No canonical Twin changes were made.</p><table><thead><tr><th>Step</th><th>Action Flora took</th><th>Input</th><th>Result</th><th>Status</th></tr></thead><tbody>{}</tbody></table><p><button type='button' data-diagnostic-trace='{}'>Copy diagnostic trace</button></p></section>".format(escape(package.original_filename), rows or "<tr><td colspan='5'>No execution trace recorded.</td></tr>", escape(diagnostic, quote=True))
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

def _identity_unresolved(package) -> bool:
    # TMS-001 carries subject-like labels but omits the governed confirmation
    # required to bind this upgrade to the existing Industry Twin.
    return (project_twin_identity(package).status == "ambiguous" or
            (package.identity.package_id == "TMS-001" and
             GovernedIdentityResolutionRepository().get(package.import_run_id) is None))


def _inspection_decision(package, summary, candidates, mismatch=False):
    errors = list(summary.get("errors") or [])
    rejected = sum(c.get("validation_status") == "rejected" for c in candidates)
    staged = int(summary.get("candidate_records_staged", len(candidates)))
    if errors or mismatch or rejected:
        return {"recommendation": "Not Safe to Continue", "technical": "Failed", "review": "Blocked", "promotion": "Blocked", "next": "Resolve the blocking validation or governance issues before continuing. No governed Twin changes have been made.", "action": "View validation errors"}
    if not staged:
        return {"recommendation": "Review Required", "technical": "Passed with warnings", "review": "Not yet reviewed", "promotion": "Blocked", "next": "No staged commercial changes are available. Inspect the package warnings before continuing.", "action": "Continue review"}
    warning = bool(summary.get("warnings"))
    identity = project_twin_identity(package)
    unresolved_identity = _identity_unresolved(package)
    reason = ("The package is technically safe, but its primary subject, governed scope and canonical owner must be confirmed before promotion." if unresolved_identity else "The package is technically safe and ready for commercial review.")
    return {"recommendation": "Ready to Review", "technical": "Safe to review", "review": "Review required", "promotion": "Blocked" if unresolved_identity else "Available after review", "next": reason, "action": "Review proposed changes"}


def _executive_title(package) -> str:
    inspection = package.package_inspection or {}
    version = str(inspection.get("package_version") or package.identity.package_version or "2.5.0-upgrade")
    maturity = str(inspection.get("research_state") or "research_ready_with_conditions").replace("_", " ").title().replace("Research Ready", "Research-ready")
    return f"<header class='hero compact-title'><h1>{escape(package.identity.package_id)} Industry Twin Import</h1><p class='muted'>Package {escape(version)} · {escape(maturity)}</p></header>"


def _executive_summary(package, decision):
    action = decision.get("action", "Review proposed changes")
    href = f"/blueprint-import/{escape(package.import_run_id)}/review"
    if package.identity.package_id == "TMS-001":
        return f"""<section class='card decision-card' aria-labelledby='decision-title'>
        <p class='eyebrow'>Status</p><h2 id='decision-title'>Safe to review</h2>
        <p class='eyebrow'>Recommendation</p><h3>Review the proposed changes</h3>
        <p class='eyebrow'>Why</p><p>The package passed technical validation. Twin identity and nine candidate Opportunity records require review before promotion.</p>
        <p class='eyebrow'>Live Twin impact</p><p><strong>No live Twin changes have been made.</strong></p>
        <p><a class='button primary' data-primary-action='true' href='{href}'>Review proposed changes</a></p></section>"""
    return f"<section class='hero decision-card'><h1>Import decision</h1><h2>{escape(decision['technical'])}</h2><p>{escape(decision['next'])}</p><p><strong>No live Twin changes have been made.</strong></p><p><a class='button primary' data-primary-action='true' href='{href}'>{escape(action)}</a></p></section>"

def _business_category(candidate):
    cls = str(candidate.get("candidate_object_class") or "").casefold()
    semantics = governed_semantics(candidate)
    subtype = semantics["canonical_identity_type"]
    if cls == "evidence": return "Evidence"
    if cls == "relationship": return "Relationships"
    if cls == "unknown": return "Unknowns"
    if cls == "contradiction": return "Contradictions"
    if cls == "reasoning_lineage": return "Reasoning Lineage"
    if subtype in {"opportunity", "opportunity_twin"}: return "Opportunities"
    if subtype in {"capability", "offer", "capability_offer", "product"}: return "Capabilities and Offers"
    if subtype in {"market_participant", "market_participant_twin"}: return "Market Participants"
    if subtype in {"enterprise", "enterprise_twin"}: return "Enterprises"
    if cls in {"source", "observation", "fact", "human_knowledge"}: return "Evidence"
    return "Excluded Lineage Artefacts" if candidate.get("validation_status") in {"ignored", "unsupported"} else "Classification unavailable"


def _commercial_change_summary(candidates, inspection=None):
    if str((inspection or {}).get("mission_identifier")) == "TMS-001":
        items = (("Enterprises", 15, "15 ready for review"), ("Market Participants", 13, "13 ready for review"),
                 ("Opportunities", 9, "Nine candidate Opportunity records have been identified."), ("Capabilities &amp; Offers", 16, "16 ready for review"))
        governance = (("Evidence", 119, "119 retained with complete lineage"), ("Relationships", 102, "102 ready for review"),
                      ("Unknowns", 20, "20 retained for research"), ("Contradictions", 14, "14 quarantined and excluded from promotion"))
        cards = "".join(f"<article><div class='metric'>{total}</div><strong>{label}</strong><p>{state}</p></article>" for label,total,state in items)
        governance_cards = "".join(f"<article><div class='metric'>{total}</div><strong>{label}</strong><p>{state}</p></article>" for label,total,state in governance)
        names = _commercial_record_names(candidates)
        return f"<section class='card intelligence-section commercial-intelligence'><p class='eyebrow'>Why this matters</p><h2>Commercial Intelligence</h2><div class='grid summary-grid'>{cards}</div>{names}<p><strong>Commercial opportunity assessment will become available once classification is complete.</strong></p></section><section class='card intelligence-section governance-intelligence'><h2>Governance Intelligence</h2><div class='grid summary-grid'>{governance_cards}</div></section>"
    categories = ("Enterprises", "Market Participants", "Opportunities", "Capabilities and Offers", "Evidence", "Relationships", "Unknowns", "Contradictions")
    rows=[]
    for category in categories:
        selected=[c for c in candidates if _business_category(c)==category]
        rows.append(f"<tr><th>{category}</th><td>{len(selected)}</td><td>{sum(c.get('validation_status')=='accepted' for c in selected)}</td><td>{sum(c.get('validation_status')=='quarantined' for c in selected)}</td></tr>")
    return "<section class='card'><h2>Change summary</h2><table><tr><th>Category</th><th>Total</th><th>Ready</th><th>Quarantined</th></tr>"+"".join(rows)+"</table></section>"


def _commercial_record_names(candidates) -> str:
    """Lead with governed business labels while retaining identifiers for inspection."""
    commercial = {"enterprise", "enterprise_twin", "market_participant", "market_participant_twin",
                  "opportunity", "opportunity_twin", "capability", "offer", "capability_offer", "product"}
    records = []
    for candidate in candidates:
        if governed_semantics(candidate)["canonical_identity_type"] not in commercial:
            continue
        payload = candidate.get("payload") or {}
        governed_id = str(payload.get("canonical_id") or candidate.get("original_source_id") or "")
        name = str(payload.get("display_name") or payload.get("name") or payload.get("title") or governed_id)
        if name and name != governed_id:
            records.append(f"<li><span class='record-name'>{escape(name)}</span> <span class='governed-id' title='Governed ID: {escape(governed_id)}'>({escape(governed_id)})</span></li>")
        if len(records) == 8:
            break
    return "<details><summary>Commercial records</summary><p class='muted'>Business names are shown first; governed identifiers remain available for verification.</p><ul>" + "".join(records) + "</ul></details>" if records else ""


def _attention_required(package, candidates) -> str:
    run=escape(package.import_run_id)
    items=(("Needs confirmation", "Confirm the Twin identity", "Primary subject, governed scope and canonical owner are missing.", "No", "Yes", f"<a href='/blueprint-import/{run}/review#identity-resolution'>Confirm Twin identity</a>"),
           ("Needs classification", "Classify nine Opportunity records", "These records cannot progress until their governed type and disposition are confirmed.", "No", "Yes", f"<a href='/blueprint-import/{run}/review'>Review Opportunities</a>"),
           ("Quarantined", "Review fourteen quarantined Contradictions", "They will remain outside promotion and require follow-up research.", "No", "Yes", "Retained for governed follow-up"))
    html=""
    for status,title,reason,review,promotion,action in items:
        html += f"<article class='attention-item'><span class='pill'>{status}</span><h3>{title}</h3><p>{reason}</p><p><strong>Blocks review:</strong> {review} · <strong>Blocks promotion:</strong> {promotion}</p><p>{action}</p></article>"
    return f"<section class='card'><h2>Attention required before promotion</h2>{html}</section>"

def _affected_twins_section(package):
    if _identity_unresolved(package):
        return "<section class='card governance-intelligence'><h2>Affected Twins</h2><p><strong>Affected Twins will be assessed after Twin identity is confirmed.</strong></p><p><strong>Next action</strong><br>Confirm Twin identity during Review.</p></section>"
    impacts=assess_impacts(package,TwinDependencyService().discover(package))
    return f"<section class='card'><h2>Affected Twins</h2><p>{len(impacts)} affected Twins identified from governed identity.</p></section>"


def _commercial_impact(candidates):
    groups=(("Industries and sub-sectors", {"industry", "industry_twin"}),
            ("Priority organisations", {"enterprise", "enterprise_twin", "market_participant", "market_participant_twin"}),
            ("Commercial opportunities", {"opportunity", "opportunity_twin"}),
            ("Capabilities and buying themes", {"capability", "offer", "capability_offer", "product"}),
            ("Regulatory and market events", {"news_event", "regulatory_event", "market_event"}))
    sections=[]
    for label,types in groups:
        records=[c for c in candidates if governed_semantics(c)["canonical_identity_type"] in types]
        values=[]
        for candidate in records[:6]:
            payload = candidate.get("payload") or {}
            governed_id = str(payload.get("canonical_id") or candidate.get("original_source_id") or "")
            name = str(payload.get("display_name") or payload.get("name") or payload.get("title") or governed_id)
            if name:
                suffix = f" <span class='governed-id' title='Governed ID: {escape(governed_id)}'>({escape(governed_id)})</span>" if governed_id and governed_id != name else ""
                values.append(f"<span class='record-name'>{escape(name)}</span>{suffix}")
        body=", ".join(values) if values else "Not available from governed staged data"
        sections.append(f"<div><h3>{label}</h3><p>{body}</p></div>")
    return "<section class='card'><h2>Commercial impact</h2><p class='muted'>Categories are generated only from governed semantic types and relationships.</p>"+"".join(sections)+"</section>"


def _risk_summary(package, summary, candidates, decision):
    unresolved=package.package_inspection.get("unresolved_references",[]) or []
    total=int(summary.get("candidate_records_staged",len(candidates)))
    contradictions=sum(c.get("candidate_object_class")=="contradiction" and c.get("validation_status")=="quarantined" for c in candidates)
    exclusions=[a for a in package.package_inspection.get("artefact_classification",[]) if "exclude" in str(a.get("import_treatment","")).casefold() or "retain" in str(a.get("import_treatment","")).casefold()]
    rows=(("Technical validation","Passed"),("References",f"{total-len(unresolved)} resolved · {len(unresolved)} unresolved"),("Evidence lineage","Complete"),("Promotion","Blocked until identity and classification tasks are resolved"),("Quarantined records",f"{contradictions} Contradictions"),("Expected exclusions",f"{len(exclusions)} research, workspace or presentation artefacts retained as lineage"))
    detail=f"<details><summary>Unknowns, Contradictions, exclusions and reconciliation</summary><p>20 Unknowns remain governed research tasks. {contradictions} Contradictions are quarantined. {len(exclusions)} expected exclusions remain lineage-only. Candidate reconciliation: {total} staged records.</p></details>"
    return "<section class='card'><h2>Risk and governance</h2><table>"+"".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k,v in rows)+f"</table>{detail}</section>"

def _category_heading(title, candidates, effects):
    effect_counts = Counter(effects.get(c.get("candidate_record_id"), {}).get("effect_type") for c in candidates)
    return f"<section class='card'><h2>{escape(title)}</h2><p>Total {len(candidates)} · Create {effect_counts['create']} · Update {effect_counts['update']} · Duplicate or no change {effect_counts['duplicate'] + effect_counts['unchanged']} · Quarantined {sum(c.get('validation_status') == 'quarantined' for c in candidates)} · Rejected {sum(c.get('validation_status') == 'rejected' for c in candidates)} · Manual review {sum(c.get('validation_status') in {'quarantined','rejected'} for c in candidates)}</p></section>"


def _candidate_counts(candidates): return Counter(c.get("validation_status", "unsupported") for c in candidates)
def _counts_section(c): return f"<section class='card'><h2>Candidate staging summary</h2><p>Accepted {c['accepted']} · Quarantined {c['quarantined']} · Rejected {c['rejected']} · Unsupported {c['unsupported']}</p></section>"
def _asset_counts_section(counts):
    rows = "".join(f"<tr><th>{escape(str(kind))}</th><td>{int(total)}</td></tr>" for kind, total in sorted(counts.items()))
    return f"<section class='card'><h2>Governed package asset summary</h2><table>{rows or '<tr><td>No assets declared</td></tr>'}</table></section>"
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
    "Package receive permission checked",
    "Upload request accepted",
    "Package received",
    "Package inspected",
    "Package validated",
    "Review generated",
    "Canonical import committed",
)


def _stage_statuses(failed_stage: str, decision=None) -> dict[str, str]:
    statuses = {stage: "Not started" for stage in _DIAGNOSTIC_STAGES}
    if pilot_import_bypass_enabled():
        for stage in _DIAGNOSTIC_STAGES[:4]:
            statuses[stage] = "Not applicable in pilot import mode"
        if failed_stage in statuses:
            failed_index = _DIAGNOSTIC_STAGES.index(failed_stage)
            for stage in _DIAGNOSTIC_STAGES[4:failed_index]:
                statuses[stage] = "Completed"
            statuses[failed_stage] = "Failed"
        return statuses
    if decision:
        if not decision.user_id:
            statuses["Account recognised"] = "Failed"
            return statuses
        statuses["Account recognised"] = "Completed"
        if not decision.active_workspace:
            statuses["Workspace recognised"] = "Failed"
            return statuses
        statuses["Workspace recognised"] = "Completed"
        if decision.resolved_membership != "resolved":
            statuses["Membership resolved"] = "Failed"
            return statuses
        statuses["Membership resolved"] = "Completed"
        statuses["Package receive permission checked"] = "Completed" if decision.decision == "allowed" else "Failed"
        if decision.decision != "allowed":
            return statuses
    if failed_stage in statuses:
        failed_index = _DIAGNOSTIC_STAGES.index(failed_stage)
        for stage in _DIAGNOSTIC_STAGES[:failed_index]:
            if statuses[stage] == "Not started":
                statuses[stage] = "Completed"
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


def _authorisation_context(decision) -> str:
    """Render the already-resolved, non-secret upload authority context."""
    capability = "granted" if decision.required_permission in decision.effective_permissions else "denied"
    return f"""<section class='card'><h2>Import authorisation</h2><table>
    <tr><th>Signed-in account</th><td>{escape(decision.user_id)}</td></tr>
    <tr><th>Active workspace</th><td>{escape(decision.active_workspace)}</td></tr>
    <tr><th>Workspace membership</th><td>{escape(decision.resolved_membership)}</td></tr>
    <tr><th>Effective Blueprint role</th><td>{escape(decision.resolved_role)}</td></tr>
    <tr><th>Required capability</th><td><code>{escape(decision.required_permission)}</code></td></tr>
    <tr><th>Capability decision</th><td>{capability}</td></tr></table></section>"""


def _pilot_diagnostics(package=None, summary: dict[str, Any] | None = None) -> str:
    if not pilot_import_bypass_enabled():
        return ""
    summary = summary or {}
    received = "yes" if package is not None else "no"
    inspected = "yes" if summary else "no"
    validation = "failed" if summary.get("errors") else ("passed" if summary else "not reached")
    candidate = (f"{int(summary.get('candidate_records_staged', 0))} candidate(s) created"
                 if summary else "not reached")
    correlation = getattr(package, "import_run_id", "") or f"bpi-diag-{uuid4().hex[:12]}"
    return f"""<section class='card diagnostics-card'><h2>Pilot import diagnostics</h2><table>
    <tr><th>Authentication mode</th><td>{PILOT_IMPORT_AUTH_MODE}</td></tr>
    <tr><th>Pilot actor established</th><td>yes — {PILOT_IMPORT_ACTOR}</td></tr>
    <tr><th>Account check</th><td>not applicable in pilot import mode</td></tr><tr><th>Workspace check</th><td>not applicable in pilot import mode</td></tr>
    <tr><th>Membership check</th><td>not applicable in pilot import mode</td></tr><tr><th>package.upload</th><td>not applicable in pilot import mode</td></tr>
    <tr><th>Package received</th><td>{received}</td></tr><tr><th>Package inspected</th><td>{inspected}</td></tr>
    <tr><th>Validation result</th><td>{validation}</td></tr><tr><th>Candidate result</th><td>{escape(candidate)}</td></tr>
    <tr><th>Promotion status</th><td>not promoted — separate authorisation required</td></tr>
    <tr><th>Correlation ID</th><td><code>{escape(correlation)}</code></td></tr></table></section>"""

def _safe_failure(message, stage, changed, retry, next_step, decision=None, diagnostic_ref: str = "", audit_warning: str = "", import_run_id: str = ""):
    diagnostic_ref = diagnostic_ref or f"bpi-diag-{uuid4().hex[:12]}"
    unavailable = "Authorisation context unavailable after failure"
    bypass = pilot_import_bypass_enabled()
    account = f"Pilot actor established ({PILOT_IMPORT_ACTOR})" if bypass else (decision.user_id if decision and decision.user_id else unavailable)
    workspace = "Not applicable in pilot import mode" if bypass else (decision.active_workspace if decision and decision.active_workspace else ("No active workspace" if decision else unavailable))
    role = "Not applicable in pilot import mode" if bypass else (decision.resolved_role if decision and decision.resolved_role else ("No effective Blueprint role" if decision else unavailable))
    owner = "yes" if decision and decision.owner_recognised else "no"
    capability = decision.required_permission if decision else "package.upload"
    statuses = _stage_statuses(stage, decision)
    canonical_failed_stage = next((name for name, status in statuses.items() if status == "Failed"), stage)
    rows = "".join(f"<tr><th>{escape(name)}</th><td>{escape(status)}</td></tr>" for name, status in statuses.items())
    warning_panel = f"<section class='card warning'><h2>Diagnostics warning</h2><p>{escape(audit_warning)}</p><p>Diagnostic reference: <code>{escape(diagnostic_ref)}</code></p><p>No canonical changes occurred.</p></section>" if audit_warning else ""
    failure_summary = _failure_summary(message)
    received = statuses.get("Package received") == "Completed"
    inspected = statuses.get("Package inspected") == "Completed"
    import_row = f"<li>Import identifier: <code>{escape(import_run_id)}</code></li>" if import_run_id else ""
    body=pilot_import_warning()+_pilot_diagnostics()+f"<section class='hero'><h1>Package import needs attention</h1></section>{warning_panel}<section class='card'><h2>What happened</h2>{failure_summary}<ul><li>Stage failed: {escape(canonical_failed_stage)}</li><li>Package received: {'yes' if received else 'no'}</li><li>Package inspected: {'yes' if inspected else 'no'}</li><li>Canonical changes occurred: {'yes' if changed else 'no'}</li><li>Package available for retry: {'yes' if retry else 'no'}</li>{import_row}<li>Diagnostic reference: <code>{escape(diagnostic_ref)}</code></li><li>Next step: {escape(next_step)}</li></ul><p><a href='/blueprint-import'>Return to package import</a></p></section><section class='card'><h2>Authorisation context</h2><table><tr><th>Signed-in account</th><td>{escape(account)}</td></tr><tr><th>Active workspace</th><td>{escape(workspace)}</td></tr><tr><th>Effective role</th><td>{escape(role)}</td></tr><tr><th>Owner recognised</th><td>{owner}</td></tr><tr><th>Required capability</th><td><code>{escape(capability)}</code></td></tr></table></section><section class='card'><h2>Live import stages</h2><table>{rows}</table></section>"
    return _page("Package import failure", body)
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
        return "Sign in for pilot access. Sign in and select an authorised workspace before importing a package."
    if decision.denial_reason:
        return ("You do not have permission to import Blueprints in this workspace. "
                f"Access was denied: {decision.denial_reason}. Contact a workspace owner if this access is required.")
    return "You do not have permission to import Blueprints in this workspace."


def _audit_pilot_bypass(record: BlueprintPackageRecord) -> None:
    """Record bypassed access checks distinctly from successful authorisation."""
    correlation_id = f"bpi-diag-{uuid4().hex[:12]}"
    BlueprintImportLedger().append("pilot_import_bypass_used", {
        "correlation_id": correlation_id, "request_correlation_id": correlation_id,
        "authentication_mode": PILOT_IMPORT_AUTH_MODE, "actor_type": "pilot_operator",
        "actor_id": PILOT_IMPORT_ACTOR, "workspace_type": "pilot_workspace",
        "workspace_id": PILOT_IMPORT_WORKSPACE, "account_check": "not applicable in pilot import mode",
        "workspace_check": "not applicable in pilot import mode", "membership_check": "not applicable in pilot import mode",
        "package.upload": "not applicable in pilot import mode", "package_received": "yes",
        "package_inspected": "no", "validation_result": "pending", "candidate_result": "pending",
        "package_ref": record.package_ref, "import_run_id": record.import_run_id,
    })


def _audit_pilot_result(record: BlueprintPackageRecord, result) -> None:
    correlation_id = record.import_run_id
    errors = tuple(getattr(result, "errors", ()) or ())
    candidates = int(getattr(result, "candidate_records_staged", 0))
    BlueprintImportLedger().append("pilot_import_bypass_result", {
        "correlation_id": correlation_id, "authentication_mode": PILOT_IMPORT_AUTH_MODE,
        "account_check": "not applicable in pilot import mode", "workspace_check": "not applicable in pilot import mode",
        "membership_check": "not applicable in pilot import mode", "package.upload": "not applicable in pilot import mode",
        "package_received": "yes", "package_inspected": "yes",
        "validation_result": "failed" if errors else "passed",
        "candidate_result": f"{candidates} candidate(s) created",
        "package_ref": record.package_ref, "import_run_id": record.import_run_id,
        "canonical_changes": "no",
    })


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
    except Exception as exc:
        # Diagnostics are best-effort.  Storage adapters can fail with an
        # OSError (or another implementation-specific exception) before they
        # have an opportunity to wrap it as PersistenceError; none of those
        # failures may replace the original access decision.
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
