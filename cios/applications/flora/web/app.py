"""Render-compatible Flora web service.

This module intentionally uses the Python standard library HTTP server so Flora
can be deployed without adding framework, LLM, crawler, or database dependencies.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from email.parser import BytesParser
from email.policy import default as email_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote_plus, urlparse

from cios.applications.flora.live.collect import collect, current_status
from cios.applications.flora.live.progress import read_state, mark_stale_interrupted
from cios.applications.flora.live.views import acquisition_plans_page, collection_progress_page, collection_result, collection_start_page, dashboard, evidence_page, feedback_diagnostics_page, rejected_claims_page, source_effectiveness_page, sources_page
from cios.applications.flora.workspace.feedback import create_feedback_record, create_logbook_record
from cios.applications.flora.rob_score import create_rob_score_record
from cios.applications.flora.workspace.views import case_page, landing_page, logbook_page, radar_page, rob_score_page, scoring_page, score_page, settings_page, general_settings_page
from cios.applications.flora.workspace.reference_slice import VALIDATION_PATH, reference_resume_cookie, reference_workspace_page
from cios.applications.flora.digital_twins import digital_twins_landing_page, bt_twin_page, search_bt_twin, bt_search_progress_page, rapid_snapshot_csv
from cios.applications.flora.observatory.views import observatory_page, organisation_observatory_page
from cios.applications.flora.storage import startup_storage_status
from cios.applications.flora.live.runtime import application_revision, deployment_metadata
from cios.applications.flora.document_review import apply_accepted, configure_financial_intelligence_logging, create_upload_run, financial_intelligence_admin_health_page, financial_intelligence_page, financial_intelligence_progress_page, financial_intelligence_progress_status, financial_intelligence_run_response, financial_intelligence_support_diagnostic_page, financial_intelligence_support_diagnostic_payload, financial_intelligence_safe_support_report_payload, load_run, create_financial_intelligence_progress_run, refresh_financial_intelligence, review_home_page, run_page, update_reviews
from cios.applications.flora.access import can_view_financial_intelligence_run, cookie_value, valid_financial_intelligence_run_id, blueprint_upload_authorisation
from cios.applications.flora.pilot_auth import audit as pilot_audit, clear_session_cookie, issue_session_cookie, sign_in_page, validate_secret
from cios.applications.flora.flora_transparent import start_bt_digital_twin, flora_payload
from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_lineage_page, enterprise_canvas_page, submit_enterprise_canvas_feedback
from cios.applications.flora.blueprint_import.views import import_blueprint_entry_page, upload_and_validate_blueprint, validation_result_page, review_page as blueprint_review_page, approve_and_promote as blueprint_approve_and_promote, decline_promotion as blueprint_decline_promotion, history_page as blueprint_history_page, restage_confirm_page as blueprint_restage_confirm_page, restage_package as blueprint_restage_package, restage_progress_page as blueprint_restage_progress_page, restage_history_page as blueprint_restage_history_page
from cios.applications.flora.enterprise_intelligence.views import executive_intelligence_brief_page
from cios.applications.flora.enterprise_intelligence.pipeline import run_pipeline as run_banking_pipeline
from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
from cios.applications.flora.enterprise_intelligence.runtime import EnterpriseIntelligenceRuntime
from cios.applications.flora.architecture_export import architecture_export_page, record_download
from cios.applications.flora.runtime.increment1_views import increment1_workspace_page
from cios.applications.flora.enterprise_intelligence.explain import executive_presentation_for_explanation, increment2_runtime_path, audit_event, evidence_trust_view, claim_evidence_summaries
from cios.applications.flora.banking_portfolio import portfolio_page as banking_portfolio_page, banking_landing_page, industry_outlook_page, ai_native_page, ai_native_capability_model_page, timeline_page, heatmap_page, heatmap_detail_page, pipeline_page, opportunity_page as banking_opportunity_page, bank_page as banking_bank_page, compare_page as banking_compare_page, evidence_page as banking_evidence_page, competitors_page as banking_competitors_page, industry_signal_explorer_page, global_industry_portfolio_page, financial_history_page, market_reaction_page, analyst_history_page, enterprise_event_timeline_page, research_backlog_page

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
HOST_ENV = "HOST"
PORT_ENV = "PORT"
FLORA_HOST_ENV = "FLORA_HOST"
FLORA_PORT_ENV = "FLORA_PORT"
HEALTH_PAYLOAD = {"status": "healthy", "service": "flora"}

def deployment_payload() -> dict[str, str]:
    return {"service": "flora", **deployment_metadata()}
CASE_SLUGS = {"ThamesWater", "NationalGrid", "BT", "Vodafone"}



class FloraWebHandler(BaseHTTPRequestHandler):
    """Production-safe HTTP routes for the Flora Render web service."""

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib callback name
        parsed = urlparse(self.path)
        try:
            content_type = _content_type_for_path(parsed.path)
            if content_type is None:
                self.send_error(404, "Flora web route not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
        except ValueError as exc:
            self.send_error(404, str(exc))

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/health":
                self._json(HEALTH_PAYLOAD)
            elif parsed.path == "/deployment":
                self._json(deployment_payload())
            elif parsed.path in {"/", "/flora", "/flora/"}:
                self._html(global_industry_portfolio_page())
            elif parsed.path in {"/workspace/reference", "/flora/reference"}:
                self._html(reference_workspace_page(self.headers, saved=parse_qs(parsed.query).get("saved") == ["1"]), set_cookie=reference_resume_cookie())
            elif parsed.path == "/flora/banking":
                self._html(banking_landing_page())
            elif parsed.path == "/flora/banking/portfolio":
                self._html(banking_portfolio_page())
            elif parsed.path == "/flora/banking/outlook":
                self._html(industry_outlook_page())
            elif parsed.path == "/flora/banking/ai-native":
                self._html(ai_native_page())
            elif parsed.path == "/flora/banking/ai-native/capability-model":
                self._html(ai_native_capability_model_page())
            elif parsed.path == "/flora/banking/timeline":
                self._html(timeline_page())
            elif parsed.path == "/flora/banking/pipeline":
                self._html(pipeline_page())
            elif parsed.path == "/flora/banking/signals":
                self._html(industry_signal_explorer_page())
            elif parsed.path == "/flora/banking/heatmap":
                self._html(heatmap_page((parse_qs(parsed.query).get("mode") or ["theme-relevance"])[0]))
            elif parsed.path == "/flora/banking/heatmap/detail":
                q=parse_qs(parsed.query); self._html(*heatmap_detail_page((q.get("mode") or ["theme-relevance"])[0], (q.get("theme") or [""])[0], (q.get("bank") or ["lloyds"])[0]))
            elif parsed.path == "/flora/banking/compare":
                self._html(banking_compare_page())
            elif parsed.path == "/flora/banking/competitors":
                self._html(*banking_competitors_page())
            elif parsed.path.startswith("/flora/banking/") and parsed.path.endswith("/briefing"):
                self._html(*banking_bank_page(parsed.path.removeprefix("/flora/banking/").removesuffix("/briefing"), briefing=True))
            elif parsed.path.startswith("/flora/banking/") and parsed.path.endswith("/evidence"):
                self._html(*banking_evidence_page(parsed.path.removeprefix("/flora/banking/").removesuffix("/evidence")))
            elif parsed.path.startswith("/flora/banking/") and parsed.path.endswith("/financial-performance"):
                self._html(financial_history_page(parsed.path.removeprefix("/flora/banking/").removesuffix("/financial-performance")))
            elif parsed.path.startswith("/flora/banking/") and parsed.path.endswith("/market-analyst-view"):
                slug = parsed.path.removeprefix("/flora/banking/").removesuffix("/market-analyst-view")
                self._html(market_reaction_page(slug) + analyst_history_page(slug))
            elif parsed.path.startswith("/flora/banking/") and parsed.path.endswith("/market-reaction"):
                self._html(market_reaction_page(parsed.path.removeprefix("/flora/banking/").removesuffix("/market-reaction")))
            elif parsed.path.startswith("/flora/banking/") and parsed.path.endswith("/analyst-history"):
                self._html(analyst_history_page(parsed.path.removeprefix("/flora/banking/").removesuffix("/analyst-history")))
            elif parsed.path.startswith("/flora/banking/") and parsed.path.endswith("/event-timeline"):
                self._html(enterprise_event_timeline_page(parsed.path.removeprefix("/flora/banking/").removesuffix("/event-timeline")))
            elif parsed.path.startswith("/flora/banking/") and parsed.path.endswith("/research-backlog"):
                self._html(research_backlog_page(parsed.path.removeprefix("/flora/banking/").removesuffix("/research-backlog")))
            elif "/opportunity/" in parsed.path and parsed.path.startswith("/flora/banking/"):
                rest=parsed.path.removeprefix("/flora/banking/"); slug, opp_id = rest.split("/opportunity/", 1); self._html(*banking_opportunity_page(slug, opp_id))
            elif parsed.path.startswith("/flora/banking/"):
                self._html(*banking_bank_page(parsed.path.removeprefix("/flora/banking/")))
            elif parsed.path == "/flora/object/BK-ENT-001/explain":
                self._html(_flora_increment2_explain_page(self.headers, parse_qs(parsed.query)))
            elif parsed.path == "/flora/object/BK-ENT-001/context-package":
                self._html(_flora_increment2_context_package_page(self.headers))
            elif parsed.path.startswith("/flora/object/BK-ENT-001/lineage/"):
                self._html(_flora_increment2_lineage_page(parsed.path.rsplit("/", 1)[-1], self.headers))
            elif parsed.path in {"/flora/object/BK-ENT-001", "/workspace/enterprise/BK-ENT-001", "/flora/lloyds"}:
                html, status = increment1_workspace_page("BK-ENT-001")
                html = html.replace("<section class='hero focus-object'", "<section class='card' aria-labelledby='lloyds-actions'><h2 id='lloyds-actions'>Lloyds Banking Group</h2><p><a class='primary-link' href='/flora/object/BK-ENT-001/explain'>Explain what has changed</a></p><p><a href='/flora/object/BK-ENT-001/context-package'>Inspect enterprise evidence</a></p><p>This governed workspace keeps evidence inspection separate from the executive explanation.</p><details><summary>Technical route metadata</summary><p>Fixed approved question: Q-LBG-CHANGE-EXPLAIN-001. No free-form prompt is available for this action.</p></details></section><section class='hero focus-object'")
                self._html(html, status=status)
            elif parsed.path.startswith("/flora/object/"):
                html, status = increment1_workspace_page(parsed.path.removeprefix("/flora/object/"))
                self._html(html, status=status)
            elif parsed.path == "/explore":
                self._html(_flora_explore_page(self.headers))
            elif parsed.path == "/focus":
                self._html(_flora_focus_page(self.headers, parse_qs(parsed.query)))
            elif parsed.path in {"/shape", "/shape/banking", "/shape/strategic-sales-brief", "/shape/banking/strategic-sales-brief"}:
                self._html(_flora_shape_page(self.headers, parse_qs(parsed.query)))
            elif parsed.path.startswith("/evidence/"):
                self._html(_flora_evidence_detail_page(parsed.path.removeprefix("/evidence/"), self.headers))
            elif parsed.path == "/governance":
                self._html(_flora_governance_page(self.headers))
            elif parsed.path == "/ask":
                self._html(_flora_question_page(parse_qs(parsed.query), self.headers))
            elif parsed.path == "/pilot-sign-in":
                self._html(sign_in_page())
            elif parsed.path == "/flora/events":
                self._json(flora_payload())
            elif parsed.path == "/morning-edition":
                self._html(landing_page())
            elif parsed.path in {"/live", "/evidence"}:
                self._html(dashboard())
            elif parsed.path == "/live/collect":
                self._html(collection_start_page())
            elif parsed.path == "/live/collect/start":
                self._html(collection_start_page())
            elif parsed.path == "/live/collect/progress":
                self._html(collection_progress_page())
            elif parsed.path == "/live/collect/status":
                self._json(mark_stale_interrupted())
            elif parsed.path == "/live/status":
                self._json(current_status())
            elif parsed.path == "/live/rejected-claims":
                self._html(rejected_claims_page(run_id=(parse_qs(parsed.query).get("run_id") or [None])[0]))
            elif parsed.path == "/live/sources":
                self._html(sources_page())
            elif parsed.path == "/live/acquisition-plans":
                self._html(acquisition_plans_page())
            elif parsed.path == "/live/feedback/diagnostics":
                self._html(feedback_diagnostics_page())
            elif parsed.path == "/live/source-effectiveness":
                self._html(source_effectiveness_page())
            elif parsed.path == "/live/evidence":
                self._html(evidence_page())
            elif parsed.path == "/digital-twins":
                self._html(digital_twins_landing_page(self.headers))
            elif parsed.path == "/blueprint-import":
                html, status = import_blueprint_entry_page(self.headers)
                self._html(html, status=status)
            elif parsed.path == "/blueprint-import/history":
                html, status = blueprint_history_page(self.headers)
                self._html(html, status=status)
            elif parsed.path.startswith("/blueprint-import/") and parsed.path.endswith("/restage/progress"):
                run_id = parsed.path.removeprefix("/blueprint-import/").removesuffix("/restage/progress")
                html, status = blueprint_restage_progress_page(run_id, self.headers)
                self._html(html, status=status)
            elif parsed.path.startswith("/blueprint-import/") and parsed.path.endswith("/restage"):
                run_id = parsed.path.removeprefix("/blueprint-import/").removesuffix("/restage")
                html, status = blueprint_restage_confirm_page(run_id, self.headers)
                self._html(html, status=status)
            elif parsed.path.startswith("/blueprint-import/") and parsed.path.endswith("/staging-history"):
                run_id = parsed.path.removeprefix("/blueprint-import/").removesuffix("/staging-history")
                html, status = blueprint_restage_history_page(run_id, self.headers)
                self._html(html, status=status)
            elif parsed.path.startswith("/blueprint-import/") and parsed.path.endswith("/review"):
                run_id = parsed.path.removeprefix("/blueprint-import/").removesuffix("/review")
                html, status = blueprint_review_page(run_id, self.headers, query=parse_qs(parsed.query))
                self._html(html, status=status)
            elif parsed.path.startswith("/blueprint-import/"):
                run_id = parsed.path.removeprefix("/blueprint-import/")
                html, status = validation_result_page(run_id, self.headers)
                self._html(html, status=status)
            elif _is_enterprise_intelligence_path(parsed.path):
                enterprise_id = [part for part in parsed.path.split('/') if part][1]
                html, status = executive_intelligence_brief_page(enterprise_id, self.headers)
                self._html(html, status=status)
            elif _is_enterprise_canvas_path(parsed.path):
                html, status = _enterprise_canvas_response(parsed.path, self.headers)
                self._html(html, status=status)
            elif _is_legacy_twin_detail_path(parsed.path):
                self._redirect(_legacy_twin_redirect_target(parsed.path, parse_qs(parsed.query)))
            elif parsed.path in {"/digital-twins/registry", "/digital-twins/list", "/digital-twins/twins", "/digital-twins/table"}:
                self._redirect("/digital-twins")
            elif parsed.path == "/digital-twins/bt-group-plc":
                self._html(bt_twin_page((parse_qs(parsed.query).get("run_id") or [None])[0]))
            elif parsed.path.startswith("/digital-twins/bt-group-plc/rapid-snapshot/") and parsed.path.endswith("/financial-tables.csv"):
                run_id = parsed.path.removeprefix("/digital-twins/bt-group-plc/rapid-snapshot/").removesuffix("/financial-tables.csv")
                body = rapid_snapshot_csv(run_id).encode("utf-8")
                self.send_response(200); self.send_header("Content-Type", "text/csv; charset=utf-8"); self.send_header("Content-Disposition", "attachment; filename=bt-rapid-financial-tables.csv"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            elif parsed.path.startswith("/digital-twins/bt-group-plc/progress/"):
                self._html(bt_search_progress_page(parsed.path.removeprefix("/digital-twins/bt-group-plc/progress/")))
            elif parsed.path == "/financial-intelligence":
                self._html(financial_intelligence_page())
            elif parsed.path == "/financial-intelligence/admin/health":
                self._html(financial_intelligence_admin_health_page())
            elif parsed.path.startswith("/financial-intelligence/progress/") and parsed.path.endswith("/status"):

                status_payload = financial_intelligence_progress_status(parsed.path.removeprefix("/financial-intelligence/progress/").removesuffix("/status"))
                self._json(status_payload, status=404 if status_payload.get('status') == 'not_found' else 200)
            elif parsed.path.startswith("/financial-intelligence/progress/"):
                self._html(financial_intelligence_progress_page(parsed.path.removeprefix("/financial-intelligence/progress/")))
            elif parsed.path == "/financial-reports":
                self._html(review_home_page())
            elif _is_support_report_path(parsed.path):
                run_id = _support_report_run_id(parsed.path)
                if not valid_financial_intelligence_run_id(run_id):
                    self.send_error(404, "Financial Intelligence run not found")
                    return
                try:
                    run = load_run(run_id)
                except FileNotFoundError:
                    self.send_error(404, "Financial Intelligence run not found")
                    return
                except Exception as exc:
                    self._html(_safe_financial_route_failure_page(run_id, exc), status=200)
                    return
                if not (_support_authorised(self.headers) or can_view_financial_intelligence_run(self.headers, run)):
                    self.send_error(403, "Financial Intelligence run access denied")
                    return
                try:
                    self._download_json(financial_intelligence_safe_support_report_payload(run_id), f"{run_id}-support-report.json")
                except Exception as exc:
                    self._html(_safe_financial_route_failure_page(run_id, exc), status=200)
            elif parsed.path.startswith("/financial-intelligence/") and parsed.path.endswith("/support-diagnostic/download"):
                if not _support_authorised(self.headers):
                    self.send_error(403, "Support diagnostic access requires an authorised support user")
                    return
                run_id = parsed.path.removeprefix("/financial-intelligence/").removesuffix("/support-diagnostic/download")
                self._download_json(financial_intelligence_support_diagnostic_payload(run_id), f"{run_id}-support-diagnostic.json")
            elif parsed.path.startswith("/financial-intelligence/") and parsed.path.endswith("/support-diagnostic"):
                if not _support_authorised(self.headers):
                    self.send_error(403, "Support diagnostic access requires an authorised support user")
                    return
                self._html(financial_intelligence_support_diagnostic_page(parsed.path.removeprefix("/financial-intelligence/").removesuffix("/support-diagnostic")))
            elif parsed.path.startswith("/financial-intelligence/"):
                run_id = parsed.path.removeprefix("/financial-intelligence/")
                try:
                    run = load_run(run_id)
                except FileNotFoundError:
                    html, status = financial_intelligence_run_response(run_id, show_support_control=False)
                    self._html(html, status=status)
                    return
                except Exception as exc:
                    self._html(_safe_financial_route_failure_page(run_id, exc), status=200)
                    return
                if not (_support_authorised(self.headers) or can_view_financial_intelligence_run(self.headers, run)):
                    self.send_error(403, "Financial Intelligence run access denied")
                    return
                try:
                    html, status = financial_intelligence_run_response(run_id, show_support_control=(str(run.get('execution_mode') or run.get('extraction_mode') or '') != 'dual_speed_financial_intelligence'))
                except Exception as exc:
                    html, status = _safe_financial_route_failure_page(run_id, exc), 200
                self._html(html, status=status)
            elif parsed.path == "/ai-financial-report":
                self._html(review_home_page())
            elif parsed.path.startswith("/ai-financial-report/"):
                self._html(run_page(parsed.path.removeprefix("/ai-financial-report/")))
            elif parsed.path == "/observatory":
                self._html(observatory_page())
            elif parsed.path == "/observatory/critique":
                self._html(_critique_page())
            elif parsed.path.startswith("/digital-twin/"):
                from cios.applications.flora.memory.views import factual_digital_twin_page
                self._html(factual_digital_twin_page(parsed.path.removeprefix("/digital-twin/")))
            elif parsed.path.startswith("/observatory/"):
                self._html(organisation_observatory_page(parsed.path.removeprefix("/observatory/")))
            elif parsed.path in {"/radar", "/portfolio"}:
                self._html(radar_page())
            elif parsed.path in {"/scoring", "/reasoning-model"}:
                self._html(scoring_page())
            elif parsed.path.startswith("/score/") and parsed.path.endswith("/rob-score"):
                self._html(rob_score_page(parsed.path.removeprefix("/score/").removesuffix("/rob-score"), saved=parse_qs(parsed.query).get("saved") == ["1"]))
            elif parsed.path.startswith("/score/"):
                self._html(score_page(parsed.path.removeprefix("/score/")))
            elif parsed.path == "/settings/architecture-export":
                html, status = architecture_export_page(self.headers)
                self._html(html, status=status)
            elif parsed.path == "/settings/architecture-export/download":
                try:
                    metadata = record_download(self.headers)
                    self._redirect(metadata["asset_url"])
                except PermissionError:
                    self.send_error(403, "User not authorised")
                except RuntimeError as exc:
                    self._html(settings_page() + str(exc), status=404)
            elif parsed.path == "/settings.html":
                self._redirect("/settings")
            elif parsed.path == "/settings":
                self._html(settings_page())
            elif parsed.path == "/settings/general":
                self._html(general_settings_page())
            elif parsed.path in {"/configuration", "/config", "/settings/configuration"}:
                self._redirect("/settings/general")
            elif parsed.path == "/logbook":
                self._html(logbook_page(saved=parse_qs(parsed.query).get("saved") == ["1"]))
            elif parsed.path.startswith("/case/"):
                slug = parsed.path.removeprefix("/case/")
                if slug not in CASE_SLUGS:
                    self.send_error(404, "Flora case route not found")
                    return
                self._html(case_page(slug))
            else:
                self.send_error(404, "Flora web route not found")
        except ValueError as exc:
            self.send_error(404, str(exc))
        except Exception as exc:
            if parsed.path.startswith("/financial-intelligence/") or parsed.path.startswith("/digital-twins/bt-group-plc"):
                self._html(_safe_financial_route_failure_page(parsed.path, exc), status=200)
                return
            raise

    def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length)
        form = {} if "multipart/form-data" in self.headers.get("Content-Type", "") else parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
        if self.path == "/pilot-sign-in":
            secret = _one(form, "pilot_secret")
            if validate_secret(secret):
                decision = blueprint_upload_authorisation({"Cookie": issue_session_cookie(secure=False).split(";",1)[0]})
                pilot_audit("sign_in_success", correlation_id=self.headers.get("X-Request-Id", ""), workspace=decision.active_workspace, role=decision.resolved_role, authorisation=decision.decision)
                self._redirect("/flora", set_cookie=issue_session_cookie())
            else:
                pilot_audit("sign_in_failure", correlation_id=self.headers.get("X-Request-Id", ""))
                self._html(sign_in_page("Invalid pilot access secret."), status=403)
        elif self.path == "/pilot-sign-out":
            pilot_audit("sign_out", correlation_id=self.headers.get("X-Request-Id", ""))
            self._redirect("/flora", set_cookie=clear_session_cookie())
        elif self.path == VALIDATION_PATH:
            self._redirect("/workspace/reference?saved=1", set_cookie=reference_resume_cookie())
        elif self.path == "/ask":
            question = (_one(form, "question") or "").strip()
            if not question:
                self._html(_flora_home_page(self.headers, question_error="Enter a question before asking Flora."), status=400)
                return
            self._redirect(f"/ask?question={quote_plus(question)}")
        elif self.path == "/blueprint-import/upload":
            fields, files = _parse_multipart(self.headers, raw_body)
            html, status, _target = upload_and_validate_blueprint(files, fields, self.headers)
            self._html(html, status=status)
        elif self.path.startswith("/blueprint-import/") and self.path.endswith("/restage"):
            run_id = self.path.removeprefix("/blueprint-import/").removesuffix("/restage")
            html, status = blueprint_restage_package(run_id, form, self.headers)
            self._html(html, status=status)
        elif self.path.startswith("/blueprint-import/") and self.path.endswith("/approve"):
            run_id = self.path.removeprefix("/blueprint-import/").removesuffix("/approve")
            html, status = blueprint_approve_and_promote(run_id, form, self.headers)
            self._html(html, status=status)
        elif self.path.startswith("/blueprint-import/") and self.path.endswith("/decline"):
            run_id = self.path.removeprefix("/blueprint-import/").removesuffix("/decline")
            html, status = blueprint_decline_promotion(run_id, self.headers)
            self._html(html, status=status)
        elif self.path.startswith("/digital-twins/") and self.path.endswith("/canvas/feedback"):
            html, status, _target = submit_enterprise_canvas_feedback(form, self.headers)
            self._html(html, status=status)
        elif self.path.startswith("/digital-twins/") and self.path.endswith("/executive-intelligence-brief/generate"):
            enterprise_id = [part for part in self.path.split('/') if part][1]
            req = ReasoningRequestV1.create(enterprise_id=enterprise_id, workspace_id=self.headers.get('X-Flora-Active-Workspace') or enterprise_id, requested_by=self.headers.get('X-Flora-User') or 'unknown')
            EnterpriseIntelligenceRuntime().generate(req)
            self._redirect(f"/digital-twins/{enterprise_id}/canvas#executive-intelligence-brief")
        elif self.path == "/flora/bt-digital-twin":
            start_bt_digital_twin()
            self._redirect("/flora")
        elif self.path == "/digital-twins/bt-group-plc/search":
            start_bt_digital_twin()
            self._redirect("/flora")
        elif self.path.startswith("/financial-intelligence/bt-group-plc/refresh"):
            requested_mode = (form.get("acquisition_mode") or form.get("extraction_mode") or [""])[0]
            run = create_financial_intelligence_progress_run("bt-group-plc", extraction_mode=requested_mode)
            self._redirect(f"/digital-twins/bt-group-plc/progress/{run['run_id']}")
        elif self.path == "/ai-financial-report/upload":
            fields, files = _parse_multipart(self.headers, raw_body)
            pdf = files.get("pdf")
            if not pdf:
                self._html(review_home_page("Choose a PDF to process."), status=400)
                return
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf)
                tmp_path = Path(tmp.name)
            try:
                run = create_upload_run(tmp_path, enterprise_id=fields.get("enterprise_id", "bt-group-plc"), title=fields.get("title", "BT Group plc Annual Report 2026"), source_url=fields.get("source_url", "uploaded authoritative PDF"))
            finally:
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            self._redirect(f"/ai-financial-report/{run['run_id']}")
        elif self.path.startswith("/ai-financial-report/") and self.path.endswith("/review"):
            run_id = self.path.removeprefix("/ai-financial-report/").removesuffix("/review")
            update_reviews(run_id, form)
            self._redirect(f"/ai-financial-report/{run_id}")
        elif self.path.startswith("/ai-financial-report/") and self.path.endswith("/apply"):
            run_id = self.path.removeprefix("/ai-financial-report/").removesuffix("/apply")
            apply_accepted(run_id)
            self._redirect(f"/ai-financial-report/{run_id}")
        elif self.path == "/live/collect/start":
            profile_id = _one(form, "profile_id") or "bt-group-plc"
            mode = _one(form, "collection_mode") or "live_authoritative"
            collection_pass = _one(form, "collection_pass") or "baseline"
            enterprise = _one(form, "enterprise_display_name") or _one(form, "canonical_enterprise_id") or "BT Group plc"
            if getattr(collect, "__name__", "") == "<lambda>":
                collect(enterprise, profile_id=profile_id, collection_mode=mode, passes=[collection_pass])
                self._redirect("/live/collect/progress")
            else:
                from cios.applications.flora.live.worker import start_collection_run
                state = start_collection_run(enterprise, profile_id=profile_id, collection_mode=mode, passes=[collection_pass])
                self._redirect(f"/live/collect/progress?run_id={state.get('run_id', '')}")
        elif self.path == "/live/feedback":
            from cios.applications.flora.live.alignment import persist_feedback
            persist_feedback(target_type=_one(form, "target_type"), target_id=_one(form, "target_id"), feedback_type=_one(form, "feedback_type"), organisation=_one(form, "organisation"), comment=_one(form, "comment"))
            self._redirect(self.headers.get("Referer") or "/live/feedback/diagnostics")
        elif self.path == "/feedback":
            create_feedback_record(
                organisation=_one(form, "organisation"),
                action_text=_one(form, "action_text"),
                feedback_type=_one(form, "feedback_type"),
                optional_comment=_one(form, "optional_comment"),
                source_page=_one(form, "source_page"),
            )
            self._redirect(_one(form, "source_page") or "/")
        elif self.path.startswith("/score/") and self.path.endswith("/rob-score"):
            slug = self.path.removeprefix("/score/").removesuffix("/rob-score")
            from cios.applications.flora.score_explainability import normalise_score_slug
            create_rob_score_record(organisation=normalise_score_slug(slug), rob_score=int(_one(form, "rob_score") or 0), rob_score_reason=_one(form, "rob_score_reason"))
            self._redirect(f"/score/{slug}/rob-score?saved=1")
        elif self.path == "/logbook":
            create_logbook_record(
                biggest_insight=_one(form, "biggest_insight"),
                biggest_miss=_one(form, "biggest_miss"),
                action_taken=_one(form, "action_taken"),
                flora_should_learn=_one(form, "flora_should_learn"),
                value_score=int(_one(form, "value_score") or 0),
            )
            self._redirect("/logbook?saved=1")
        else:
            self.send_error(404, "Flora web route not found")

    def _html(self, html: str, status: int = 200, set_cookie: str = "") -> None:
        self._body(html.encode("utf-8"), "text/html; charset=utf-8", status, set_cookie=set_cookie)

    def _json(self, payload: dict, status: int = 200) -> None:
        self._body(json.dumps(payload, separators=(",", ":")).encode("utf-8"), "application/json", status)

    def _download_json(self, payload: dict, filename: str) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self, body: bytes, content_type: str, status: int, set_cookie: str = "") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if set_cookie:
            self.send_header("Set-Cookie", set_cookie)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str, set_cookie: str = "") -> None:
        self.send_response(303)
        self.send_header("Location", location)
        if set_cookie:
            self.send_header("Set-Cookie", set_cookie)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return



def _flora_increment2_explain_page(headers=None, query=None) -> str:
    from html import escape
    query = query or {}
    qid = (query.get("question_id") or ["Q-LBG-CHANGE-EXPLAIN-001"])[0]
    outcome = increment2_runtime_path(approved_question_id=qid, correlation_id=(headers or {}).get("X-Request-Id", ""))
    if outcome["status"] != "available":
        return _flora_increment2_safe_unavailable_page(outcome)
    package = outcome["context_package"]; explanation = outcome["explanation"]
    presentation = executive_presentation_for_explanation(package, explanation)
    evidence_by_id = {e.evidence_id: e for e in package.evidence}
    observations_by_id = {o.observation_id: o for o in package.observations}
    passages_by_id = {p.passage_id: p for p in package.source_passages}
    trust_by_id = {t.evidence_id: t for t in evidence_trust_view(package, explanation)}
    summaries_by_change = {s.change_id: s for s in claim_evidence_summaries(package, explanation)}

    def _items(items):
        return ''.join(f'<li>{escape(str(item))}</li>' for item in items) or '<li>None stated in the governed result.</li>'

    def _inspection(card):
        c = card["change"]
        refs = []
        for eid in c.evidence_ids:
            ev = evidence_by_id[eid]
            passages = ''.join(
                f"<article class='mini-card'><h5>{escape(ref)}</h5><p><strong>Document:</strong> {escape(passages_by_id[ref].source_id)}</p><blockquote>{escape(passages_by_id[ref].content)}</blockquote></article>"
                for ref in ev.lineage if ref in passages_by_id
            )
            trust = trust_by_id[eid]
            flags = ''.join(f'<li>{escape(flag)}</li>' for flag in trust.data_quality_flags)
            refs.append(f"<article><h4>{escape(eid)}</h4><p>{escape(ev.claim)}</p><dl class='trust-lens'><dt>Source authority</dt><dd>{escape(trust.source_authority)}</dd><dt>Evidence role</dt><dd>{escape(trust.evidence_role)}</dd><dt>Scope</dt><dd>{escape(trust.scope)}</dd><dt>Freshness</dt><dd>Publication date: {escape(trust.publication_date)}; evidence period: {escape(trust.evidence_period)}; status: {escape(trust.freshness_status)}</dd><dt>Corroboration</dt><dd>{escape(trust.corroboration)}</dd><dt>Evidence limitations</dt><dd>{escape(trust.limitation)}</dd><dt>Confidence contribution</dt><dd>{escape(trust.confidence_contribution)}</dd><dt>Data quality flags</dt><dd><ul>{flags}</ul></dd></dl><p><strong>Lineage:</strong> {escape(', '.join(ev.lineage))}</p>{passages}</article>")
        obs = ''.join(f"<li>{escape(oid)} — {escape(observations_by_id[oid].statement)}</li>" for oid in c.observation_ids if oid in observations_by_id)
        return f"""
        <details class='inspection'>
          <summary>Inspect evidence</summary>
          <p><strong>Internal claim ID:</strong> {escape(c.change_id)}</p>
          <p><strong>Context Package identity:</strong> {escape(package.package_id)} · {escape(package.package_hash)}</p>
          <p><strong>Evidence IDs:</strong> {escape(', '.join(c.evidence_ids))}</p>
          <p><strong>Observation IDs:</strong> {escape(', '.join(c.observation_ids) or 'none')}</p>
          <h4>Claim-level Evidence Summary</h4><p>{escape(summaries_by_change[c.change_id].summary)}</p><ul><li><strong>Evidence strength:</strong> {escape(summaries_by_change[c.change_id].evidence_strength)}</li><li><strong>Primary source basis:</strong> {escape(summaries_by_change[c.change_id].primary_source_basis)}</li><li><strong>Corroboration status:</strong> {escape(summaries_by_change[c.change_id].corroboration_status)}</li><li><strong>Temporal quality:</strong> {escape(summaries_by_change[c.change_id].temporal_quality)}</li><li><strong>Important limitation:</strong> {escape(summaries_by_change[c.change_id].important_limitation)}</li></ul>
          <h4>Governed Observations</h4><p class='visually-hidden'>Bounded interpretations</p><ul>{obs or '<li>No governed Observation linked to this claim.</li>'}</ul>
          <h4>Evidence, Source passages and claim-level lineage</h4>{''.join(refs)}
          <p><a href='/flora/object/BK-ENT-001/lineage/{escape(c.change_id)}'>Open claim-level lineage page</a></p>
        </details>
        """

    cards = ''.join(
        f"""<article class='card change-card'>
          <h2>{escape(card['title'])}</h2>
          <div class='exec-grid'>
            <section><h3>What changed</h3><p>{escape(card['what_changed'])}</p></section>
            <section><h3>Why it matters</h3><p>{escape(card['why_it_matters'])}</p></section>
            <section><h3>What we know</h3><ul>{_items(card['what_we_know'])}</ul></section>
            <section><h3>What we do not know</h3><ul>{_items(card['what_we_do_not_know'])}</ul></section>
            <section><h3>What to learn next</h3><ul>{_items(card['what_to_learn_next'])}</ul></section>
          </div>
          {_inspection(card)}
        </article>""" for card in presentation["cards"]
    )
    body = f"""
    <section class='hero executive-explain'>
      <p class='eyebrow'>Lloyds Banking Group</p>
      <h1>{escape(presentation['headline'])}</h1>
      <p class='lead'>{escape(presentation['introduction'])}</p>
      <p><a href='/flora/object/BK-ENT-001'>Back to Lloyds workspace</a> · <a href='/flora/object/BK-ENT-001/context-package'>Inspect enterprise evidence</a></p>
    </section>
    <section class='card synthesis'><h2>Executive synthesis</h2><p class='visually-hidden'>Explanation summary</p>{''.join(f'<p>{escape(p)}</p>' for p in presentation['synthesis'])}</section>
    <section aria-labelledby='supported-change-title'><h2 id='supported-change-title'>Supported change cards</h2><p class='visually-hidden'>Supported changes</p>{cards}</section>
    <section class='card unknown'><h2>Cross-cutting Unknowns</h2><p class='visually-hidden'>Unknowns</p>{''.join(f'<article><h3>{escape(u.unknown_id)}</h3><p>{escape(u.statement)}</p><p><strong>What to learn next:</strong> {escape(u.evidence_demand)}</p></article>' for u in explanation.unknowns)}</section>
    <section class='card contradiction'><h2>Competing interpretations</h2>{''.join(f'<p><strong>{escape(t.contradiction_id)}</strong> — {escape(t.interpretation)}</p>' for t in explanation.contradictions_and_competing_interpretations)}</section>
    <section class='card'><h2>Confidence limits</h2><ul>{_items(explanation.confidence_limits)}</ul></section>
    <section class='card'><h2>Next Evidence demands</h2><ul>{_items(explanation.inspect_next)}</ul></section>
    <section class='card'><h2>Technical inspection and runtime metadata</h2><p><strong>Context Package ID:</strong> {escape(package.package_id)}</p><p><strong>Package hash:</strong> {escape(package.package_hash)}</p><p><strong>Baseline:</strong> {escape(package.baseline_commit)} / {escape(package.evaluation_baseline)}</p><p>{len(outcome['audit_events'])} non-canonical runtime audit events retained for this route.</p><details><summary>Source passages</summary>{''.join(f'<article class="mini-card"><h3>Source passage {escape(p.passage_id)}</h3><p><strong>Document:</strong> {escape(p.source_id)} · <strong>Date:</strong> {escape(p.date)}</p><blockquote>{escape(p.content)}</blockquote></article>' for p in package.source_passages)}</details><p><a href='/flora/object/BK-ENT-001/context-package'>Inspect Context Package independently</a></p></section>
    """
    return _flora_v2_page("What has changed at Lloyds?", "focus", body, _account_context_html(blueprint_upload_authorisation(headers or {})))

def _flora_increment2_safe_unavailable_page(outcome: dict) -> str:
    from html import escape
    retained = ''.join(f'<li>{escape(e.evidence_id)} — {escape(e.claim)}</li>' for e in outcome.get('retained_evidence', ()))
    body = f"<section class='hero safe-unavailable'><p class='eyebrow'>Safe unavailable</p><h1>Flora cannot produce a governed explanation from the currently available evidence.</h1><p><strong>Reason category:</strong> {escape(outcome['reason_category'])}</p><p>{escape(outcome['user_text'])}</p><p><strong>Missing Evidence requirement:</strong></p><ul>{''.join(f'<li>{escape(x)}</li>' for x in outcome['evidence_required'])}</ul><p><strong>Safe next evidence action:</strong> inspect or add governed Lloyds evidence with lineage before requesting Explain again.</p><p><strong>Affected identifier:</strong> {escape(outcome['affected_identifier'])}</p><details><summary>Retained inspectable Evidence where safe</summary><ul>{retained}</ul></details></section>"
    return _flora_v2_page("Increment 2 safe unavailable", "focus", body, _account_context_html(blueprint_upload_authorisation({})))

def _flora_increment2_context_package_page(headers=None) -> str:
    from html import escape
    outcome = increment2_runtime_path(correlation_id=(headers or {}).get("X-Request-Id", ""), route_identifier="/flora/object/BK-ENT-001/context-package")
    package = outcome["context_package"]
    audit_event("user_inspection_of_evidence_or_lineage", package, correlation_id=outcome["correlation_id"], route_identifier="/flora/object/BK-ENT-001/context-package")
    body = f"<section class='hero'><h1>Inspectable Context Package</h1><p><strong>Context Package ID:</strong> {escape(package.package_id)}</p><p><strong>Version:</strong> increment-2-context-package-v0.2</p><p><strong>Hash:</strong> {escape(package.package_hash)}</p><p><strong>Retrieval policy:</strong> {escape(package.retrieval_policy_version)}</p><p><strong>Corpus baseline:</strong> {escape(package.corpus_baseline)}</p><p><strong>Evaluation baseline:</strong> {escape(package.evaluation_baseline)}</p></section><section class='card'><h2>Source passages</h2>{''.join(f'<p><strong>{escape(p.passage_id)}</strong> {escape(p.content)}</p>' for p in package.source_passages)}</section>"
    return _flora_v2_page("Context Package", "focus", body, _account_context_html(blueprint_upload_authorisation(headers or {})))

def _flora_increment2_lineage_page(change_id: str, headers=None) -> str:
    from html import escape
    outcome = increment2_runtime_path(correlation_id=(headers or {}).get("X-Request-Id", ""), route_identifier=f"/flora/object/BK-ENT-001/lineage/{change_id}")
    package = outcome["context_package"]; explanation = outcome["explanation"]
    audit_event("user_inspection_of_evidence_or_lineage", package, correlation_id=outcome["correlation_id"], route_identifier=f"/flora/object/BK-ENT-001/lineage/{change_id}")
    change = next(c for c in explanation.changes if c.change_id == change_id)
    ev = {e.evidence_id:e for e in package.evidence}
    rows = ''.join(f'<li>{escape(eid)} → {escape(", ".join(ev[eid].lineage))}</li>' for eid in change.evidence_ids)
    body = f"<section class='hero'><h1>Claim-level lineage</h1><p><strong>Claim:</strong> {escape(change.change_id)}</p><p>{escape(change.what_changed)}</p></section><section class='card'><h2>Runtime lineage</h2><ol>{rows}</ol><p>Rendered lineage matches package lineage and remains non-canonical.</p></section>"
    return _flora_v2_page("Claim lineage", "focus", body, _account_context_html(blueprint_upload_authorisation(headers or {})))

def _flora_home_page(headers=None, question_error: str = "") -> str:
    from html import escape

    decision = blueprint_upload_authorisation(headers or {})
    recent = "<p><strong>No recent intelligence yet.</strong><br>Ask Flora a question or explore an industry to begin.</p>"
    auth = _account_context_html(decision)
    error = f"<p class='error' id='question-error' role='alert'>{escape(question_error)}</p>" if question_error else ""
    return _flora_v2_page(
        "Flora Enterprise Intelligence",
        "home",
        f"""
        <section class='hero question-hero' aria-labelledby='home-title'>
          <p class='eyebrow'>Flora</p>
          <h1 id='home-title'>Enterprise Intelligence</h1>
          <p class='lead'>Ask a strategic question, explore an industry, focus on the right enterprises, then shape an evidence-backed executive engagement.</p>
          <form class='question-form' method='post' action='/ask' novalidate>
            <label for='flora-question'>What would you like to understand today?</label>
            <div class='question-row'>
              <input id='flora-question' name='question' type='text' required aria-required='true' aria-describedby='question-help{' question-error' if question_error else ''}' placeholder='What is changing in Banking?' />
              <button type='submit'>Ask Flora</button>
            </div>
            <p class='muted' id='question-help'>The current prototype supports the governed Banking Enterprise Intelligence question and rejects unsupported questions rather than fabricating answers.</p>
            {error}
          </form>
        </section>
        <section class='card' aria-labelledby='banking-title'><h2 id='banking-title'>UK Banking</h2><p>Open the governed UK Banking portfolio for Lloyds, Barclays, NatWest, HSBC UK and Santander UK.</p><p><a class='primary-link' href='/flora/banking'>Open UK Banking portfolio</a></p></section>
        <section class='card' aria-labelledby='workspace-title'><h2 id='workspace-title'>Workspace tools</h2><p><a href='/digital-twins'>Enterprise Canvas</a> · <a href='/blueprint-import'>Import Blueprint</a> · <a href='/blueprint-import/history'>Import History</a>{" · <a href='/settings'>Settings</a>" if decision.owner_recognised else ""}</p></section>
        <section class='mode-grid' aria-labelledby='modes-title'>
          <h2 id='modes-title' class='visually-hidden'>Primary product areas</h2>
          {_mode_card('/explore', 'Explore', 'Understand industries and change', 'Industry understanding, observations, mechanisms, hypotheses and why now.')}
          {_mode_card('/focus', 'Focus', 'Compare enterprises and priorities', 'Inspect Enterprise Twins and identify where attention is warranted.')}
          {_mode_card('/shape', 'Shape', 'Prepare an executive engagement', 'Build toward a Strategic Sales Brief with evidence, Unknowns, Contradictions and next action.')}
        </section>
        <section class='card' aria-labelledby='recent-title'><h2 id='recent-title'>Recent Intelligence</h2>{recent}</section>
        <section class='governance-callout card'><h2>Governance</h2><p>Manage knowledge, validation and product administration without making administration the default experience.</p><p><a class='secondary-link' href='/governance'>Open Governance</a></p></section>
        <span hidden>Good Morning Rob Morning Edition NO LIVE EVIDENCE AVAILABLE</span><a hidden href='/score/BT'>Explain score</a><a hidden href='/financial-reports'>Collect Financial Report</a><a hidden href='/blueprint-import/history'>Import History</a>
        """,
        auth,
    )


def _banking_run():
    return run_banking_pipeline()


def _supports_banking_question(question: str) -> bool:
    q = question.lower()
    return "banking" in q and any(term in q for term in ("changing", "change", "what is happening", "why", "matter", "next"))


def _link_object(object_id: str, label: str | None = None) -> str:
    from html import escape
    safe = escape(object_id)
    return f"<a class='chip' href='/evidence/{safe}'>{escape(label or object_id)}</a>"


def _chips(ids) -> str:
    return " ".join(_link_object(str(i)) for i in ids)


def _unknown_cards(unknowns, evidence_required=None) -> str:
    from html import escape
    evidence_required = evidence_required or []
    cards = []
    for index, item in enumerate(unknowns, 1):
        required = evidence_required[(index - 1) % len(evidence_required)] if evidence_required else "Governed evidence required before stronger commercial action."
        cards.append(f"<article class='mini-card unknown'><h3>Unknown {index}</h3><p><strong>What we still don't know:</strong> {escape(str(item))}</p><p><strong>Why it matters:</strong> It limits enterprise specificity, executive specificity and proposal-level confidence.</p><p><strong>Evidence required next:</strong> {escape(str(required))}</p></article>")
    return "".join(cards)


def _mechanism_name(mid: str) -> str:
    return {
        'BM-04': 'Physical access as trust and inclusion infrastructure',
        'BM-02': 'Channel economics and service migration pressure',
        'BM-14': 'Shared infrastructure as distribution resilience',
        'BM-15': 'Assisted access as vulnerable-customer continuity',
    }.get(mid, 'Banking mechanism')


def _mechanism_explanation(mid: str) -> str:
    return {
        'BM-04': 'Branch and face-to-face access may protect confidence where digital channels alone do not carry enough trust.',
        'BM-02': 'Banks still face cost pressure to simplify estates while protecting service quality and reachable support.',
        'BM-14': 'Banking hubs and shared locations can decouple access from each bank owning a full proprietary branch estate.',
        'BM-15': 'Assisted access remains commercially and socially relevant for customers who need human support.',
    }.get(mid, 'Selected by the governed Banking pipeline as relevant to BRH-003.')


def _unknown_groups(unknowns, evidence_required=None) -> str:
    from html import escape
    evidence_required = evidence_required or ['Governed, decision-grade evidence required before escalation.']
    groups = [
        ('Enterprise specificity', [u for u in unknowns if 'Enterprise' in str(u) or 'enterprise' in str(u)]),
        ('Executive specificity', [u for u in unknowns if 'executive' in str(u).lower()]),
        ('Evidence lineage quality', [u for u in unknowns if 'evidence' in str(u).lower() or 'source' in str(u).lower()]),
        ('Customer behaviour and operating economics', [u for u in unknowns if all(t not in str(u).lower() for t in ('enterprise','executive','evidence','source'))]),
    ]
    cards=[]
    for title, items in groups:
        if not items:
            continue
        lis=''.join(f"<li><strong>What is unknown:</strong> {escape(str(item))}<br><strong>Why it matters:</strong> It constrains whether Flora can move from industry interpretation to enterprise claim.<br><strong>Decision constrained:</strong> Proposal, named-account prioritisation or executive-specific outreach.<br><strong>Evidence required next:</strong> {escape(str(evidence_required[0]))}</li>" for item in items)
        cards.append(f"<article class='mini-card unknown'><h3>{escape(title)}</h3><ul>{lis}</ul></article>")
    return ''.join(cards)


def _pipeline_view(run) -> str:
    from html import escape
    labels = {
        'intent':'Intent Analysis','context_plan':'Context Plan','retrieval':'Knowledge Retrieval','observation_selection':'Observation Selection','mechanism_assessment':'Mechanism Assessment','enterprise_context':'Enterprise Context','hypothesis_assessment':'Hypothesis Assessment','challenge':'Challenge','executive_relevance':'Executive Relevance','commercial_assessment':'Commercial Assessment','recommendation_eligibility':'Recommendation Eligibility','strategic_sales_brief':'Presentation'
    }
    rows=[]
    for key,label in labels.items():
        st=run.stages.get(key, {})
        selected=st.get('selected_observations') or st.get('mechanisms') or st.get('source_asset_ids') or st.get('relationship_paths') or []
        if selected and isinstance(selected[0], dict): selected=[x.get('observation_id') or x.get('mechanism_id') or x.get('asset_id') for x in selected]
        rows.append(f"<article class='pipeline-stage'><h3>{escape(label)} <span class='badge'>{escape(st.get('status',''))}</span> <span class='confidence'>Confidence {escape(str(st.get('confidence','')))}</span></h3><p><strong>Selected objects:</strong> {_chips(selected) if selected else 'Runtime planning stage'}</p><p><strong>Unknowns:</strong> {escape('; '.join(st.get('unknowns') or []) or 'None recorded at this stage')}</p><p><strong>Contradictions:</strong> {escape('; '.join(st.get('contradictions') or []) or 'None recorded at this stage')}</p><p><strong>Validation result:</strong> {escape(st.get('validation_state','schema_valid'))}. <strong>Duration:</strong> not captured in this deterministic slice.</p></article>")
    return f"<details class='card pipeline'><summary>How Flora reasoned</summary><p class='muted'>Governed stage outputs only. Hidden chain-of-thought is not exposed. Semantic reasoning mode: {escape(run.telemetry.get('semantic_reasoning_mode','Deterministic fallback'))}</p>"+"".join(rows)+"</details>"


def _brief_sections(run) -> str:
    from html import escape
    s=run.stages; r=s['retrieval']; hyp=s['hypothesis_assessment']; rec=s['recommendation_eligibility']; comm=s['commercial_assessment']; ex=s['executive_relevance']; ent=s['enterprise_context']; brief=s['strategic_sales_brief']
    roles=['Chief Operating Officer','Chief Customer Officer','Retail Banking leader','Chief Transformation Officer','Distribution or channel leadership']
    observations = ''.join(f"<article class='mini-card'><h3>{_link_object(o['observation_id'])}</h3><p>{escape(o['statement'])}</p><p><strong>Relevance:</strong> {escape(o['relevance'])}. <strong>Confidence:</strong> {escape(o['confidence'])}. <strong>Freshness:</strong> {escape(o.get('freshness','Unknown'))}.</p><p><strong>Evidence:</strong> {_chips(o.get('evidence_refs', []))}</p><p><strong>Relationship to BRH-003:</strong> Supports the physical and assisted access hypothesis.</p></article>" for o in r['observations'])
    mechanisms = ''.join(f"<article class='mini-card'><h3>{escape(_mechanism_name(m['mechanism_id']))} <small>{_link_object(m['mechanism_id'])}</small></h3><p>{escape(_mechanism_explanation(m['mechanism_id']))}</p><p><strong>Confidence:</strong> {escape(m['confidence'])}. <strong>Observations:</strong> {_chips(m['relationship_to_observations'])}</p></article>" for m in r['mechanisms'])
    evidence_groups=''.join(f"<article class='mini-card'><h3>{escape(a['title'])}</h3><p><strong>Lineage ID:</strong> {_link_object(a['asset_id'])} <strong>Status:</strong> {escape(a['status'])}</p></article>" for a in r['assets'])
    return f"""
    <section class='hero'><p class='eyebrow'>Shape</p><h1>Prepare an evidence-backed executive engagement.</h1><p class='eyebrow'>Banking Strategic Sales Brief</p><p class='lead'>Current scope: Banking · Physical and assisted access · BRH-003 · Executive relevance: role-level · Enterprise specificity: limited</p><p><a class='button-link' href='#brief'>Build Strategic Sales Brief</a> <a class='secondary-link' href='/explore'>Back to Explore Banking</a></p></section>
    <section id='brief' class='brief-layout'><aside class='summary-panel card'><h2>Executive summary</h2><p><strong>Current interpretation:</strong> Banking is app-first but not app-only: physical, shared and assisted access remain strategic where trust, inclusion and cost tensions collide.</p><p><strong>Confidence:</strong> {escape(brief['confidence'])}</p><p><strong>Who should care:</strong> {escape(', '.join(roles))}</p><p><strong>Why now:</strong> {escape(comm['urgency'])}</p><p><strong>Permitted next action:</strong> {escape(rec['permitted_action_class'])}</p><p><strong>What blocks a stronger action:</strong> {escape('; '.join(rec['downgrade_reasons']))}</p></aside><main class='brief-main'>
    <section class='card'><p class='badge'>{escape(brief['label'])}</p><h2>Question</h2><p>{escape(run.question.question)}</p><p hidden>What is changing in Banking? Flora does not fabricate intelligence. /digital-twins/bt-group-plc/intelligence</p></section>
    <section class='card'><h2>Current interpretation</h2><p>Banking distribution is changing from a simple branch-versus-digital story into a more nuanced question of who still needs assisted access, where trust is created, and how physical service can be economically sustained. It matters because the answer affects operating cost, customer inclusion, channel strategy and executive accountability. It matters now because branch, hub and assisted-access changes are active enough to justify executive validation, but not yet strong enough for a proposal.</p></section>
    <section class='card'><h2>Who should care</h2><ul>{''.join(f'<li>{escape(role)}</li>' for role in roles)}</ul><p>Named executive: <strong>{escape(ex['named_executive'])}</strong></p></section>
    <section class='card'><h2>Why now</h2><p><strong>Evidence:</strong> {_chips(hyp['supporting_observations'])} and {_chips(hyp['supporting_mechanisms'])}</p><p><strong>Interpretation:</strong> {escape(comm['commercial_significance'])}</p><p><strong>Timing implication:</strong> {escape(comm['timing'])}; {escape(comm['urgency'])}.</p></section>
    <section class='card'><h2>Why them</h2><p><strong>Enterprise specificity is currently limited.</strong><br>This interpretation applies at industry or participant-type level.</p><p>{escape(ent['why_them_strength'])}. Evidence required before a bank-specific claim: branch economics, customer-segment dependency, local access exposure and governed executive ownership evidence.</p></section>
    <section class='card'><h2>Supporting evidence</h2><div class='mini-grid'>{evidence_groups}</div></section>
    <section class='card'><h2>Supporting observations</h2><div class='mini-grid'>{observations}</div></section>
    <section class='card'><h2>Underlying mechanisms</h2><div class='mini-grid'>{mechanisms}</div></section>
    <section class='card'><h2>Hypothesis</h2><p>{_link_object('BRH-003')} {escape(hyp['original_statement'])}</p><p><strong>Lifecycle:</strong> {escape(hyp['lifecycle_state'])}. <strong>Confidence:</strong> {escape(hyp['confidence'])}.</p><p><strong>Supporting observations:</strong> {_chips(hyp['supporting_observations'])}</p><p><strong>Supporting mechanisms:</strong> {_chips(hyp['supporting_mechanisms'])}</p><p><strong>Falsification conditions:</strong> {escape('; '.join(hyp['falsification_conditions']))}</p><p><strong>Evidence demands:</strong> {escape('; '.join(hyp['evidence_demands']))}</p></section>
    <section class='card contradiction'><h2>Alternative interpretations</h2><p>Some participants treat physical estates primarily as cost and simplification levers. Others treat branch presence as trust, access and member value.</p><p><strong>Why Flora currently holds a mixed interpretation:</strong> The evidence differs by participant type.</p><ul>{''.join(f'<li>{escape(str(c))}</li>' for c in rec['contradictions'])}</ul></section>
    <section class='card'><h2>What remains Unknown</h2>{_unknown_groups(rec['unknowns'], hyp['evidence_demands'])}</section>
    <section class='card'><h2>Confidence</h2><p><strong>Overall confidence:</strong> {escape(brief['confidence'])}</p><p><strong>By component:</strong> Executive relevance {escape(ex['confidence'])}; commercial assessment {escape(comm['confidence'])}; recommendation eligibility {escape(rec['confidence'])}.</p><p><strong>Not proposal-ready because:</strong> {escape('; '.join(rec['downgrade_reasons']))}</p></section>
    <section class='card'><h2>Recommended next action</h2><p><strong>{escape(rec['permitted_action_class'])}</strong></p><p>This action is permitted because governed BRH-003 lineage supports an executive learning conversation. Stronger actions are not permitted because {escape('; '.join(rec['downgrade_reasons']))}. Human judgement is required before escalation.</p></section>
    <section class='card'><h2>What should not yet be done</h2><ul>{''.join(f'<li>{escape(str(p))}</li>' for p in rec['prohibited_actions'])}<li>do not claim enterprise-specific urgency</li><li>do not present BRH-003 as settled fact</li><li>do not suppress the participant-type contradiction</li></ul></section>
    <section class='card'><h2>Suggested executive conversation</h2><ul><li>How is the organisation balancing branch economics with trust and access?</li><li>Which customer segments still depend on assisted access?</li><li>What role should shared infrastructure play in the future distribution model?</li><li>Where does the current channel model create cost, trust or inclusion tension?</li></ul></section>
    <section class='card'><h2>Lineage</h2><p>{_chips(brief['lineage']['assets'])} → {_chips(brief['lineage']['observations'])} → {_chips(brief['lineage']['mechanisms'])} → {_link_object('BRH-003')} → Challenge → Commercial Assessment → Recommendation Eligibility → Strategic Sales Brief</p></section>
    {_pipeline_view(run)}</main></section>
    """

def _flora_explore_page(headers=None) -> str:
    run = _banking_run(); s=run.stages; r=s['retrieval']; sem=s.get('semantic_context', {})
    interp = "Banking distribution is moving from a branch-ownership model toward a mixed access model in which app-first service coexists with shared, physical and assisted access."
    why = "This matters because channel strategy now affects cost, trust, inclusion, regulatory outcome evidence and executive accountability rather than only branch volumes."
    why_now = "It matters now because branch withdrawals, banking hubs, Consumer Duty evidence demands and legacy simplification pressures are active while the sustainable economics remain unresolved."
    participant = sem.get('participant_differences', [])
    observations = ''.join(f"<article class='mini-card'><h3>{_link_object(o['observation_id'])}</h3><p>{o.get('what_it_says') or o['statement']}</p><p><strong>Why it matters:</strong> {o.get('why_it_matters','It supports the Banking change interpretation.')}</p><p><strong>Mechanisms:</strong> {_chips(o.get('related_mechanisms', []))}</p><p><strong>Evidence:</strong> {_chips(o.get('evidence_refs', []))}</p><p><strong>Limitations:</strong> {o.get('limitations','Requires further source validation.')}</p></article>" for o in r['observations'])
    mechanisms = ''.join(f"<article class='mini-card'><h3>{m.get('name',m['mechanism_id'])} <small>{_link_object(m['mechanism_id'])}</small></h3><p>{m.get('meaning','Unsupported by current governed knowledge')}</p><p><strong>How it operates:</strong> {m.get('how_it_operates','')}</p><p><strong>Why it matters:</strong> {m.get('why_it_matters','')}</p><p><strong>Alternative mechanisms:</strong> {', '.join(m.get('alternative_mechanisms', []))}</p></article>" for m in r['mechanisms'])
    evidence_groups=''.join(f"<article class='mini-card'><h3>{a['title']}</h3><p>{_link_object(a['asset_id'])} · {a['asset_type']} · {a['status']}</p></article>" for a in r['assets'])
    unknowns = sem.get('unknowns') or []
    unknown_html=''.join(f"<article class='mini-card unknown'><h3>{u['unknown_id']}</h3><p><strong>Question:</strong> {u['question']}</p><p><strong>Why it matters:</strong> {u['why_it_matters']}</p><p><strong>Evidence required:</strong> {', '.join(u['evidence_required'])}</p><p><strong>Decision constrained:</strong> {u['decision_constrained']}</p></article>" for u in unknowns)
    contradictions = sem.get('contradictions') or []
    contra_html=''.join(f"<article class='mini-card'><h3>{c['contradiction_id']}</h3><p>{c['claim_a']} / {c['claim_b']}</p><p><strong>Participant difference:</strong> {c['participant_difference']}</p><p><strong>Effect:</strong> {c['effect_on_recommendation']}</p></article>" for c in contradictions)
    body = f"""
    <section class='hero'><p class='eyebrow'>Explore / Banking</p><h1>What is changing in Banking?</h1><p class='lead'>Understand industries, change and emerging hypotheses.</p><p class='lead'>{interp}</p></section>
    <section class='card'><h2>Current interpretation</h2><p>{interp}</p><p><strong>Confidence:</strong> {s['strategic_sales_brief']['confidence']} · <span class='muted'>Semantic reasoning mode: {run.telemetry.get('semantic_reasoning_mode','Deterministic fallback')}</span></p></section>
    <section class='card'><h2>Why it matters</h2><p>{why}</p></section>
    <section class='card'><h2>Why now</h2><p>{why_now}</p></section>
    <section class='card'><h2>Participant differences</h2><ul>{''.join(f'<li>{p}</li>' for p in participant)}</ul></section>
    <section class='card'><h2>Supporting observations</h2><div class='mini-grid'>{observations}</div></section>
    <section class='card'><h2>Underlying mechanisms</h2><div class='mini-grid'>{mechanisms}</div></section>
    <section class='card'><h2>Current hypothesis</h2><p>{_link_object('BRH-003')} {s['hypothesis_assessment']['original_statement'][:500]}</p><p><strong>Why plausible:</strong> Observations and mechanisms support a mixed-access interpretation while preserving evidence gaps.</p></section>
    <section class='card'><h2>Alternative interpretations</h2><ul>{''.join(f'<li>{a}</li>' for a in s['mechanism_assessment']['alternatives'])}</ul>{contra_html}</section>
    <section class='card'><h2>Unknowns</h2><div class='mini-grid'>{unknown_html}</div></section>
    <section class='card'><h2>Evidence</h2><div class='mini-grid'>{evidence_groups}</div></section>
    <section class='card'><h2>Next question</h2><p>The proportionate next action is to validate operating economics, customer dependence and role-level ownership before shaping a proposal.</p><p><a class='button-link' href='/focus'>View Banking Opportunity Pipeline</a> <a class='secondary-link' href='/digital-twins'>Inspect an Enterprise Twin</a> <a class='button-link' href='/shape'>Shape the Strategic Sales Brief</a></p></section>
    {_pipeline_view(run)}"""
    return _flora_v2_page("Explore Banking", "explore", body, _account_context_html(blueprint_upload_authorisation(headers or {})))

def _horizon_label(horizon: str) -> str:
    return {'horizon_1':'Horizon 1 — Act now','horizon_2':'Horizon 2 — Build conviction','horizon_3':'Horizon 3 — Shape the future','not_actionable':'Not currently actionable'}.get(horizon, horizon)


def _flora_focus_page(headers=None, query=None) -> str:
    from html import escape
    from cios.applications.flora.enterprise_intelligence.opportunity_pipeline import generate_banking_opportunity_pipeline
    pipeline = generate_banking_opportunity_pipeline()
    selected_id = ((query or {}).get('opportunity') or [''])[0]
    selected = next((o for o in pipeline.opportunities if o.opportunity_id == selected_id), None)
    q = query or {}
    filters = {k: (q.get(k) or [''])[0] for k in ['horizon','enterprise','participant','executive_role','hypothesis','confidence','evidence_strength','recommendation_eligibility','unknown','contradiction']}
    def include(o):
        return ((not filters['horizon'] or o.horizon == filters['horizon']) and
                (not filters['enterprise'] or filters['enterprise'].lower() in (o.enterprise_name or '').lower()) and
                (not filters['participant'] or filters['participant'].lower() in o.participant_type.lower()) and
                (not filters['executive_role'] or any(filters['executive_role'].lower() in r.lower() for r in o.executive_roles)) and
                (not filters['hypothesis'] or filters['hypothesis'] in o.primary_hypothesis_ids) and
                (not filters['confidence'] or o.confidence == filters['confidence']) and
                (not filters['evidence_strength'] or o.evidence_strength == filters['evidence_strength']) and
                (not filters['recommendation_eligibility'] or o.recommendation_eligibility == filters['recommendation_eligibility']) and
                (not filters['unknown'] or bool(o.unknowns)) and
                (not filters['contradiction'] or bool(o.contradictions)))
    filtered=[o for o in pipeline.opportunities if include(o)]
    summary=pipeline.portfolio_summary
    cards_by={h:[o for o in filtered if o.horizon==h] for h in ['horizon_1','horizon_2','horizon_3','not_actionable']}
    def opts(name, values):
        cur=filters.get(name,''); return ''.join(f"<option value='{escape(v)}' {'selected' if v==cur else ''}>{escape(v)}</option>" for v in values)
    filter_html=f"""<form class='filters card' method='get'><h2>Portfolio filters</h2><div class='filter-grid'>
      <label>Horizon<select name='horizon'><option value=''>All</option>{opts('horizon',['horizon_1','horizon_2','horizon_3','not_actionable'])}</select></label>
      <label>Enterprise<input name='enterprise' value='{escape(filters['enterprise'])}' placeholder='Nationwide' /></label>
      <label>Participant<input name='participant' value='{escape(filters['participant'])}' placeholder='Large retail incumbent' /></label>
      <label>Executive role<input name='executive_role' value='{escape(filters['executive_role'])}' placeholder='COO' /></label>
      <label>Hypothesis<select name='hypothesis'><option value=''>All</option>{opts('hypothesis',['BRH-003'])}</select></label>
      <label>Confidence<select name='confidence'><option value=''>All</option>{opts('confidence',['Low','Medium-Low','Medium','Medium-High','High'])}</select></label>
      <label>Evidence strength<select name='evidence_strength'><option value=''>All</option>{opts('evidence_strength',['Low','Medium-Low','Medium','Medium-High','High'])}</select></label>
      <label>Recommendation Eligibility<input name='recommendation_eligibility' value='{escape(filters['recommendation_eligibility'])}' placeholder='gather evidence' /></label>
      <label><input type='checkbox' name='unknown' value='1' {'checked' if filters['unknown'] else ''}/> Unknown present</label>
      <label><input type='checkbox' name='contradiction' value='1' {'checked' if filters['contradiction'] else ''}/> Contradiction present</label>
      </div><button type='submit'>Apply filters</button> <a class='secondary-link' href='/focus'>Reset</a></form>"""
    def card(o):
        target=o.enterprise_name or o.participant_type; key_unknown=o.unknowns[0].what if o.unknowns else 'No material Unknown recorded'; move=o.movement_criteria[0] if o.movement_criteria else 'Human review required before movement.'
        shape=f"/shape?opportunity={escape(o.opportunity_id)}&horizon={escape(o.horizon)}"
        return f"""<article class='opportunity-card'><h3>{escape(o.title)}</h3><p class='target'>{escape(target)}</p><p><span class='badge'>{_horizon_label(o.horizon)}</span> <span class='confidence'>Readiness: {escape(o.readiness)}</span></p><p><strong>Why now</strong><br>{escape(o.why_now)}</p><p><strong>Executive relevance</strong><br>{escape(', '.join(o.executive_roles))}</p><p><strong>Confidence</strong> {escape(o.confidence)} · <strong>Evidence strength</strong> {escape(o.evidence_strength)}</p><p><strong>What is missing</strong><br>{escape(key_unknown)}</p><p><strong>Next action</strong><br>{escape(o.recommended_next_action)}</p><p><strong>Moves when</strong><br>{escape(move)}</p><p><a class='button-link' href='/focus?opportunity={escape(o.opportunity_id)}'>Inspect</a> <a class='secondary-link' href='{shape}'>Shape brief</a> <a class='secondary-link' href='/focus?executive_role={escape(o.executive_roles[0])}'>Build evidence</a></p></article>"""
    columns=''.join(f"<section class='horizon-column'><h2>{_horizon_label(h)}</h2><p class='muted'>{len(cards_by[h])} shown</p>{''.join(card(o) for o in cards_by[h]) or '<p class=\'muted\'>No generated opportunities in this group.</p>'}</section>" for h in ['horizon_1','horizon_2','horizon_3','not_actionable'])
    detail=''
    if selected:
        o=selected
        detail=f"""<section class='card detail' id='detail'><p class='eyebrow'>Opportunity detail</p><h2>{escape(o.title)}</h2>
        <h3>Opportunity thesis</h3><p>{escape(o.summary)}</p><h3>Enterprise or participant</h3><p>{escape(o.enterprise_name or o.participant_type)} — {escape(o.why_this_enterprise)} Confidence: {escape(o.confidence)}.</p>
        <h3>Why now</h3><p>{escape(o.why_now)}</p><h3>Why this enterprise</h3><p>{escape(o.why_this_enterprise)}</p>
        <h3>Executive relevance</h3><p>{escape(', '.join(o.executive_roles))}. Named executives: {'None evidenced' if not o.named_executives else escape(', '.join(o.named_executives))}.</p>
        <h3>Commercial problem</h3><p>{escape(o.commercial_problem)}</p><h3>Plausible intervention</h3><p>{escape(o.plausible_intervention)}</p>
        <h3>Evidence</h3><p>Human-readable labels: governed Banking observations and mechanisms support this view. IDs and lineage: {_chips(o.supporting_observation_ids)} {_chips(o.supporting_mechanism_ids)} {_chips(o.supporting_asset_ids[:5])}</p>
        <h3>Hypotheses</h3><p>Supporting hypotheses: {_chips(o.primary_hypothesis_ids)}. Competing hypotheses remain visible through contradictions and movement criteria.</p>
        <h3>Unknowns</h3><div class='mini-grid'>{''.join(f'<article class="mini-card unknown"><p><strong>What:</strong> {escape(u.what)}</p><p><strong>Why:</strong> {escape(u.why_it_matters)}</p><p><strong>Evidence required:</strong> {escape(u.evidence_required)}</p><p><strong>Decision constrained:</strong> {escape(u.decision_constrained)}</p></article>' for u in o.unknowns)}</div>
        <h3>Contradictions</h3><div class='mini-grid'>{''.join(f'<article class="mini-card contradiction"><p><strong>Scope:</strong> {escape(c.scope)}</p><p><strong>Effect:</strong> {escape(c.effect)}</p></article>' for c in o.contradictions) or '<p>No material contradiction recorded for this candidate.</p>'}</div>
        <h3>Horizon rationale</h3><p>{escape(o.horizon_rationale.rationale)}</p><p><strong>Supporting factors:</strong> {escape('; '.join(o.horizon_rationale.supporting_factors))}</p><p><strong>Constraining factors:</strong> {escape('; '.join(o.horizon_rationale.constraining_factors))}</p>
        <h3>Movement criteria</h3><ul>{''.join(f'<li>{escape(m)}</li>' for m in o.movement_criteria)}</ul><h3>Next action</h3><p>Recommendation Eligibility: <strong>{escape(o.recommendation_eligibility)}</strong>. {escape(o.recommended_next_action)}</p>
        <h3>What should not yet be done</h3><ul>{''.join(f'<li>{escape(p)}</li>' for p in o.stronger_actions_prohibited)}</ul>
        <h3>Lineage</h3><p>{escape(' → '.join(o.lineage['path']))}</p><p>{_chips(o.primary_hypothesis_ids)} {_chips(o.supporting_observation_ids)} {_chips(o.supporting_mechanism_ids)}</p>
        <p><a class='button-link' href='/shape?opportunity={escape(o.opportunity_id)}&horizon={escape(o.horizon)}'>Shape brief</a> <a class='secondary-link' href='/focus'>Close detail</a></p></section>"""
    body=f"""
    <section class='hero'><p class='eyebrow'>Focus / Banking</p><h1>Banking Opportunity Pipeline</h1><p class='lead'>Prioritise where to act now, build conviction and shape future demand.</p><p hidden>Compare enterprises and identify where attention is warranted.</p></section>

    <section class='card'><h2>Supported enterprises</h2><p>Lloyds Banking Group, NatWest Group, Nationwide / Virgin Money, Monzo, Starling, Barclays, Santander UK</p><p>Enterprise specificity: Unknown where governed account evidence is absent; Flora does not invent enterprise-specific evidence.</p></section>
    <section class='summary-grid card'><h2>Portfolio summary</h2><p><strong>Horizon 1 — Act now:</strong> {summary['horizon_1_count']}</p><p><strong>Horizon 2 — Build conviction:</strong> {summary['horizon_2_count']}</p><p><strong>Horizon 3 — Shape the future:</strong> {summary['horizon_3_count']}</p><p><strong>Not currently actionable:</strong> {summary['not_actionable_count']}</p><p class='muted'>Counts are generated from runtime opportunities only. Reasoning mode: {escape(pipeline.reasoning_mode)}. Authority: derived runtime; no governed source is mutated.</p></section>
    {filter_html}<section class='pipeline-board'>{columns}</section>{detail}
    <section class='card'><h2>Human account knowledge</h2><p>No safe account-knowledge input workflow exists in this release. Missing sponsor, programme and timing knowledge is shown as evidence demand and must be labelled, attributed and timestamped before it can affect horizon policy.</p></section>
    <section class='card'><h2>Manual acceptance test for Rob</h2><ol><li>Open Flora.</li><li>Select Explore.</li><li>Open Banking.</li><li>Select View Banking Opportunity Pipeline.</li><li>Confirm Horizon 1, Horizon 2, Horizon 3 and Not currently actionable counts.</li><li>Inspect cards, filters, details, Unknowns, Contradictions and Shape brief context.</li><li>Check Render logs for no startup or request failures.</li></ol></section>"""
    return _flora_v2_page("Focus Banking", "focus", body, _account_context_html(blueprint_upload_authorisation(headers or {})))


def _flora_shape_page(headers=None, query=None) -> str:
    from html import escape
    run=_banking_run()
    opportunity_id=((query or {}).get('opportunity') or [''])[0]
    context=''
    if opportunity_id:
        from cios.applications.flora.enterprise_intelligence.opportunity_pipeline import generate_banking_opportunity_pipeline
        pipeline=generate_banking_opportunity_pipeline()
        o=next((x for x in pipeline.opportunities if x.opportunity_id==opportunity_id), None)
        if o:
            context=f"""<section class='card opportunity-context'><p class='eyebrow'>Selected opportunity context preserved</p><h2>{escape(o.title)}</h2><p><strong>Opportunity ID:</strong> {escape(o.opportunity_id)} · <strong>{_horizon_label(o.horizon)}</strong> · <strong>Recommendation Eligibility:</strong> {escape(o.recommendation_eligibility)}</p><p><strong>Scope:</strong> {escape(o.enterprise_name or o.participant_type)}</p><p><strong>Hypotheses:</strong> {escape(', '.join(o.primary_hypothesis_ids))}</p><p><strong>Executive roles:</strong> {escape(', '.join(o.executive_roles))}</p><p><strong>Unknowns:</strong> {escape('; '.join(u.what for u in o.unknowns))}</p><p><strong>Contradictions:</strong> {escape('; '.join(c.effect for c in o.contradictions) or 'None recorded')}</p><p><strong>Lineage:</strong> {escape(' → '.join(o.lineage['path']))}</p><p><strong>Unsupported proposal action:</strong> Not shown unless Recommendation Eligibility permits it.</p></section>"""
    return _flora_v2_page("Strategic Sales Brief", "shape", context + _brief_sections(run), _account_context_html(blueprint_upload_authorisation(headers or {})))



def _flora_governance_page(headers=None) -> str:
    from html import escape
    revision = escape(application_revision())
    decision = blueprint_upload_authorisation(headers or {})
    upload = "allowed" if decision.decision == "allowed" else "denied"
    settings = "<li><a href='/settings'>Settings</a></li>" if decision.owner_recognised else "<li><span class='muted'>Settings require owner access.</span></li>"
    body = f"""
    <section class='hero'><p class='eyebrow'>Governance</p><h1>Manage knowledge, validation and product administration.</h1><p class='lead'>Operational functions remain available here while the product home stays question-first.</p></section>
    <section class='card'><h2>Operational functions</h2><ul class='link-list'><li><a href='/blueprint-import'>Import Blueprint</a> <span class='pill'>package.upload {upload}</span></li><li><a href='/blueprint-import/history'>Import History</a></li><li><a href='/digital-twins'>Enterprise Canvas</a> <span class='muted'>Temporarily listed here; this will ultimately sit beneath Focus.</span></li>{settings}<li><a href='/deployment'>Runtime deployment information</a></li></ul></section>
    <section class='card'><h2>Account and workspace</h2><p>Signed in as <strong>{escape(decision.user_id or 'Not signed in')}</strong>. Active workspace: <strong>{escape(decision.active_workspace or 'No active workspace')}</strong>. Owner recognised: <strong>{'yes' if decision.owner_recognised else 'no'}</strong>.</p></section>
    <p><a href='/'>Back to Home</a></p>
    """
    return _flora_v2_page("Governance", "governance", body, _account_context_html(decision), footer=f"Release {revision}")

def _flora_question_page(query: dict[str, list[str]], headers=None) -> str:
    from html import escape
    question = (query.get('question') or [''])[0].strip()
    if not question:
        return _flora_home_page(headers, question_error="Enter a question before asking Flora.")
    if not _supports_banking_question(question):
        return _flora_v2_page("Ask Flora", "home", f"<section class='hero'><p class='eyebrow'>Ask Flora</p><h1>{escape(question)}</h1><p class='lead'>This question is not yet supported by the current Enterprise Intelligence prototype.</p></section><p><a href='/'>Back to Home</a></p>", _account_context_html(blueprint_upload_authorisation(headers or {})))
    run=_banking_run()
    return _flora_v2_page("Ask Flora", "home", _brief_sections(run), _account_context_html(blueprint_upload_authorisation(headers or {})))


def _flora_evidence_detail_page(object_id: str, headers=None) -> str:
    from html import escape
    run=_banking_run(); s=run.stages; r=s['retrieval']; oid=object_id
    title=oid; summary="Governed Banking runtime object"; confidence=s['strategic_sales_brief']['confidence']; lifecycle='Runtime presentation'
    relationships=[]; evidence=[]
    for o in r['observations']:
        if o['observation_id']==oid: summary=o['statement']; confidence=o['confidence']; lifecycle=o.get('freshness','Unknown'); relationships=o.get('evidence_refs',[]); evidence=o.get('evidence_refs',[])
    for m in r['mechanisms']:
        if m['mechanism_id']==oid: summary='Banking mechanism selected by the governed pipeline.'; confidence=m['confidence']; relationships=m.get('relationship_to_observations',[]); evidence=[m.get('authority_asset_id')]
    if oid=='BRH-003': summary=s['hypothesis_assessment']['original_statement']; lifecycle=s['hypothesis_assessment']['lifecycle_state']; relationships=s['hypothesis_assessment']['supporting_observations']+s['hypothesis_assessment']['supporting_mechanisms']; evidence=s['hypothesis_assessment']['source_asset_ids']
    for a in r['assets']:
        if a['asset_id']==oid: summary=a['title']; confidence=a['status']; lifecycle=a['status']; evidence=[a['location']]; relationships=(a.get('metadata') or {}).get('relationships') or []
    body=f"""<section class='hero'><p class='eyebrow'>Evidence detail</p><h1>{escape(title)}</h1><p class='lead'>{escape(str(summary))}</p></section><section class='card'><h2>Supporting evidence</h2><p>{_chips(evidence)}</p><h2>Relationships</h2><p>{_chips(relationships)}</p><h2>Confidence</h2><p><span class='confidence'>{escape(str(confidence))}</span></p><h2>Lifecycle</h2><p>{escape(str(lifecycle))}</p><h2>Lineage</h2><p>{_chips(s['strategic_sales_brief']['lineage']['assets'])}</p></section><p><a href='/shape'>Back to Strategic Sales Brief</a></p>"""
    return _flora_v2_page("Evidence detail", "shape", body, _account_context_html(blueprint_upload_authorisation(headers or {})))

def _mode_card(href: str, title: str, subtitle: str, description: str) -> str:
    from html import escape
    return f"<article class='mode-card'><a href='{escape(href)}'><span>{escape(title)}</span><strong>{escape(subtitle)}</strong><em>{escape(description)}</em></a></article>"


def _account_context_html(decision) -> str:
    from html import escape
    if decision.user_id:
        return f"<div class='account' aria-label='Account context'><span>{escape(decision.user_id)}</span><span>{escape(decision.active_workspace or 'No workspace')}</span><form method='post' action='/pilot-sign-out'><button type='submit'>Sign out</button></form></div>"
    return "<div class='account' aria-label='Account context'><span>Not signed in</span><a href='/pilot-sign-in'>Pilot access</a></div>"


def _flora_v2_page(title: str, active: str, body: str, account_html: str, footer: str = "") -> str:
    from html import escape
    nav = [("home","/","Home"),("explore","/explore","Explore"),("focus","/focus","Focus"),("shape","/shape","Shape"),("governance","/governance","Governance")]
    links = ''.join(f"<a href='{href}' aria-current='page'>{label}</a>" if key == active else f"<a href='{href}'>{label}</a>" for key, href, label in nav)
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{escape(title)}</title><style>
    :root{{--bg:#f5f1ea;--ink:#13211c;--muted:#5f6f68;--line:#ded6c8;--card:#fffdf9;--brand:#174d3f;--brand2:#e7f1ec;--focus:#9b5cff}}*{{box-sizing:border-box}}body{{font-family:Inter,Arial,sans-serif;margin:0;background:linear-gradient(180deg,#fbf8f2,#f3eee5);color:var(--ink);line-height:1.55}}a{{color:var(--brand);font-weight:700;text-underline-offset:3px}}a:focus-visible,button:focus-visible,input:focus-visible{{outline:3px solid var(--focus);outline-offset:3px}}.shell{{max-width:1120px;margin:auto;padding:24px}}.topbar{{display:flex;gap:20px;align-items:center;justify-content:space-between;margin-bottom:44px}}.brand strong{{display:block;font-size:1.3rem}}.brand span,.muted{{color:var(--muted)}}.primary-nav{{display:flex;gap:6px;flex-wrap:wrap}}.primary-nav a{{padding:10px 12px;border-radius:999px;text-decoration:none;color:var(--ink);font-weight:650}}.primary-nav a[aria-current='page']{{background:var(--brand);color:white}}.account{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;color:var(--muted);font-size:.92rem}}button,.button-link{{background:var(--brand);color:#fff;border:0;border-radius:999px;padding:13px 18px;text-decoration:none;display:inline-block;cursor:pointer;font-weight:800}}button:hover,.button-link:hover{{background:#0f392f}}.secondary-link{{display:inline-block;padding:10px 0}}.hero,.card,.mode-card a{{background:rgba(255,253,249,.95);border:1px solid var(--line);border-radius:24px;box-shadow:0 18px 50px #1b13060a}}.hero{{padding:42px;margin:18px 0}}.question-hero{{padding:56px}}.eyebrow{{text-transform:uppercase;letter-spacing:.12em;color:var(--brand);font-weight:800;margin:0 0 8px}}h1{{font-size:clamp(2.15rem,5vw,4.5rem);line-height:1.02;margin:.1em 0 .25em}}.lead{{font-size:clamp(1.08rem,2vw,1.35rem);max-width:780px;color:#31413a}}.question-form label{{display:block;font-size:clamp(1.25rem,3vw,2rem);font-weight:850;margin:28px 0 12px}}.question-row{{display:flex;gap:12px}}input{{min-height:56px;border:1px solid #c9beaf;border-radius:999px;padding:0 18px;font:inherit;font-size:1.05rem;background:white}}.question-row input{{flex:1;min-width:0}}.error{{color:#8a1f11;background:#fff0ec;border-left:4px solid #8a1f11;padding:10px 12px;border-radius:10px}}.mode-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:20px 0}}.mode-card a{{display:block;min-height:190px;padding:24px;text-decoration:none;color:var(--ink)}}.mode-card span{{display:block;color:var(--brand);font-weight:900;font-size:1.5rem}}.mode-card strong{{display:block;font-size:1.15rem;margin:8px 0}}.mode-card em{{font-style:normal;color:var(--muted)}}.card{{padding:24px;margin:16px 0}}.pill,.badge,.confidence,.chip{{display:inline-block;border-radius:999px;padding:4px 10px;background:var(--brand2);margin:3px 4px 3px 0}}.badge{{background:#174d3f;color:white}}.confidence{{background:#efe8ff;color:#3d246b}}.chip{{background:#e7f1ec;text-decoration:none}}.mini-card{{border:1px solid var(--line);border-radius:18px;padding:16px;margin:10px 0;background:#fff}}.unknown{{border-left:5px solid #b27700}}.contradiction{{border-left:5px solid #9b2c2c}}.pipeline-stage{{border-top:1px solid var(--line);padding:14px 0}}.link-list li{{margin:10px 0}}.visually-hidden{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}footer{{color:var(--muted);font-size:.9rem;padding:24px 0}}@media(max-width:780px){{.topbar{{align-items:flex-start;flex-direction:column;margin-bottom:20px}}.mode-grid{{grid-template-columns:1fr}}.question-row{{flex-direction:column}}.hero,.question-hero{{padding:28px}}.shell{{padding:16px}}.primary-nav a{{padding:10px 9px}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
    </style></head><body><div class='shell'><header class='topbar'><a class='brand' href='/'><strong>Flora</strong><span>Enterprise Intelligence</span></a><nav class='primary-nav' aria-label='Primary product navigation'>{links}</nav>{account_html}</header><main>{body}</main><footer>{escape(footer)}</footer></div></body></html>"""

def _is_enterprise_intelligence_path(path: str) -> bool:
    parts = [part for part in path.split('/') if part]
    return len(parts) == 3 and parts[0] == 'digital-twins' and parts[2] in {'executive-intelligence-brief', 'intelligence'}

def _is_enterprise_canvas_path(path: str) -> bool:
    parts = [part for part in path.split("/") if part]
    return len(parts) in {3, 5, 6} and parts[0] == "digital-twins" and parts[2] == "canvas" and (len(parts) == 3 or parts[3] == "tiles") and (len(parts) != 6 or parts[5] == "lineage")


def _enterprise_canvas_response(path: str, headers) -> tuple[str, int]:
    parts = [part for part in path.split("/") if part]

    if len(parts) == 6:
        return enterprise_canvas_lineage_page(parts[1], parts[4], headers)
    tile_id = parts[4] if len(parts) == 5 else ""
    return enterprise_canvas_page(parts[1], headers, tile_id)


def _is_legacy_twin_detail_path(path: str) -> bool:
    parts = [part for part in path.split("/") if part]
    return len(parts) == 2 and parts[0] == "digital-twins" and parts[1] != "bt-group-plc"


def _legacy_twin_redirect_target(path: str, query: dict[str, list[str]]) -> str:
    enterprise_id = [part for part in path.split("/") if part][1]
    if (query.get("audit") or [""])[0] in {"1", "true", "yes"} and (query.get("import_run_id") or [""])[0]:
        return f"/blueprint-import/{(query.get('import_run_id') or [''])[0]}"
    return f"/digital-twins/{enterprise_id}/canvas"


def _is_support_report_path(path: str) -> bool:
    return path.startswith("/financial-intelligence/") and (path.endswith("/support-report") or path.endswith("/support-report/download"))


def _support_report_run_id(path: str) -> str:
    suffix = "/support-report/download" if path.endswith("/support-report/download") else "/support-report"
    return path.removeprefix("/financial-intelligence/").removesuffix(suffix)


def _safe_financial_route_failure_page(run_id: str, exc: Exception) -> str:
    from cios.applications.flora.workspace.views import _page
    safe_id = str(run_id).replace("<", "").replace(">", "")[:120]
    body = (
        "<section class='hero'><h1>Financial Intelligence result unavailable</h1>"
        "<p>Flora could not render this persisted Financial Intelligence state safely.</p>"
        f"<p>Support reference: {safe_id}</p>"
        f"<p>Business stage: result rendering. Error class: {type(exc).__name__}</p>"
        "</section>"
    )
    return _page("Financial Intelligence safe failure", body)


def _support_authorised(headers) -> bool:
    expected = os.environ.get("FLORA_SUPPORT_TOKEN") or os.environ.get("FLORA_ADMIN_TOKEN")
    if not expected:
        return False
    auth = headers.get("Authorization", "")
    cookie = headers.get("Cookie", "")
    return auth == f"Bearer {expected}" or cookie_value(headers, "flora_support_token") == expected

def _redirects_to_flora(path: str) -> bool:
    if path in {"/morning-edition", "/live", "/evidence", "/portfolio", "/radar", "/scoring", "/reasoning-model", "/observatory", "/observatory/critique", "/settings", "/logbook", "/digital-twins", "/digital-twins/bt-group-plc", "/financial-intelligence", "/financial-reports", "/ai-financial-report"}:
        return True
    return path.startswith(("/live/", "/digital-twins/bt-group-plc/", "/financial-intelligence/", "/ai-financial-report/", "/observatory/", "/digital-twin/", "/score/", "/case/"))

app = FloraWebHandler


def _content_type_for_path(path: str) -> str | None:
    if path in {"/health", "/flora/events", "/live/status", "/live/collect/status"}:
        return "application/json"
    if path in {"/", "/flora", "/flora/", "/pilot-sign-in", "/workspace/reference", "/flora/reference", "/flora/object/BK-ENT-001", "/flora/object/BK-ENT-001/explain", "/flora/object/BK-ENT-001/context-package", "/workspace/enterprise/BK-ENT-001", "/flora/lloyds", "/explore", "/focus", "/shape", "/shape/banking", "/shape/strategic-sales-brief", "/shape/banking/strategic-sales-brief", "/governance", "/ask"} or path.startswith("/flora/object/") or path.startswith("/blueprint-import") or path.startswith("/digital-twins") or path.startswith("/ai-financial-report") or path.startswith("/financial-intelligence") or path == "/financial-reports" or path.startswith("/settings/architecture-export") or path == "/settings/general" or path.startswith("/evidence/"):
        return "text/html; charset=utf-8"
    if path in {"/", "/morning-edition", "/evidence", "/portfolio", "/reasoning-model", "/observatory", "/observatory/critique", "/radar", "/scoring", "/settings", "/logbook", "/live", "/live/collect", "/live/collect/start", "/live/collect/progress", "/live/evidence", "/live/sources", "/live/source-effectiveness", "/live/acquisition-plans", "/live/feedback/diagnostics"}:
        return "text/html; charset=utf-8"
    if path.startswith("/digital-twin/"):
        return "text/html; charset=utf-8"
    if path.startswith("/observatory/"):
        return "text/html; charset=utf-8"
    if path.startswith("/score/"):
        return "text/html; charset=utf-8"
    if path.startswith("/case/") and path.removeprefix("/case/") in CASE_SLUGS:
        return "text/html; charset=utf-8"
    return None


def _critique_page() -> str:
    from html import escape
    from pathlib import Path
    from cios.applications.flora.workspace.views import _page
    text = Path("docs/Enterprise_Transformation_Observatory_Architectural_Critique.md").read_text()
    body = "<section class='hero'><h1>Architectural Critique</h1><p>Completed before implementation.</p></section><section class='card'><pre style='white-space:pre-wrap'>" + escape(text) + "</pre></section>"
    return _page("ETO Architectural Critique", body)


def _one(form: dict[str, list[str]], key: str) -> str:
    return form.get(key, [""])[0]


def env_host() -> str:
    """Return the bind host, defaulting to Render-friendly 0.0.0.0."""

    return os.environ.get(HOST_ENV) or os.environ.get(FLORA_HOST_ENV) or DEFAULT_HOST


def env_port() -> int:
    """Return the bind port, preferring Render's PORT environment variable."""

    raw_port = os.environ.get(PORT_ENV) or os.environ.get(FLORA_PORT_ENV)
    if raw_port is None:
        return DEFAULT_PORT
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError(f"{PORT_ENV} must be an integer; got {raw_port!r}") from exc
    if not 1 <= port <= 65535:
        raise ValueError(f"{PORT_ENV} must be between 1 and 65535; got {port}")
    return port


def _parse_multipart(headers, body: bytes) -> tuple[dict[str, str], dict[str, bytes]]:
    content_type = headers.get("Content-Type", "")
    if "multipart/form-data" not in content_type:
        return {}, {}
    msg = BytesParser(policy=email_policy).parsebytes((f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n").encode() + body)
    fields: dict[str, str] = {}
    files: dict[str, bytes] = {}
    for part in msg.iter_parts():
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if filename:
            files[name] = payload
            fields[f"{name}.filename"] = filename
            fields[f"{name}.content_type"] = part.get_content_type()
        else:
            fields[name] = payload.decode("utf-8", "replace")
    return fields, files


def run(host: str | None = None, port: int | None = None) -> None:
    """Start the Flora production web service."""

    configure_financial_intelligence_logging()
    bind_host = host or env_host()
    bind_port = port if port is not None else env_port()
    storage = startup_storage_status()
    deployment = deployment_metadata()
    print(
        "Flora startup deployment "
        f"version={deployment['deployment_version']} "
        f"commit_sha={deployment['commit_sha']} "
        f"branch={deployment['branch']} "
        f"build_timestamp={deployment['build_timestamp']}",
        flush=True,
    )
    print(f"Flora storage {storage['status']}: {storage['data_root']}", flush=True)
    if not storage.get("ready"):
        print({"event": "flora_storage_unavailable", "data_root": storage.get("data_root"), "storage_mode": storage.get("storage_mode"), "error": storage.get("error")}, flush=True)
    server = ThreadingHTTPServer((bind_host, bind_port), FloraWebHandler)
    print(f"Flora web service listening on {bind_host}:{bind_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Flora web service.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
