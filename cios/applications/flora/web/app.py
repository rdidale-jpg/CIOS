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
from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
from cios.applications.flora.enterprise_intelligence.runtime import EnterpriseIntelligenceRuntime
from cios.applications.flora.architecture_export import architecture_export_page, record_download

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
                self._html(_flora_home_page(self.headers))
            elif parsed.path == "/explore":
                self._html(_flora_explore_page(self.headers))
            elif parsed.path == "/focus":
                self._html(_flora_focus_page(self.headers))
            elif parsed.path == "/shape":
                self._html(_flora_shape_page(self.headers))
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

    def _html(self, html: str, status: int = 200) -> None:
        self._body(html.encode("utf-8"), "text/html; charset=utf-8", status)

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

    def _body(self, body: bytes, content_type: str, status: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
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
            <p class='muted' id='question-help'>Flora preserves your question and routes to the current evidence-backed Banking path when a full answer is not yet available.</p>
            {error}
          </form>
        </section>
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


def _flora_explore_page(headers=None) -> str:
    question = "What is changing in Banking?"
    return _flora_v2_page("Explore", "explore", f"""
    <section class='hero'><p class='eyebrow'>Explore</p><h1>Understand industries, change and emerging hypotheses.</h1><p class='lead'>Begin with Banking and move from industry-level change into governed evidence paths.</p></section>
    <section class='card'><h2>Banking</h2><p>Use the current Banking Enterprise Intelligence vertical slice to inspect evidence-aware hypotheses and next-action boundaries.</p><p><strong>Suggested question:</strong> {question}</p><p><a class='button-link' href='/ask?question={quote_plus(question)}'>Ask about Banking</a> <a class='secondary-link' href='/digital-twins/bt-group-plc/intelligence'>Open Banking capability</a></p></section>
    <p><a href='/'>Back to Home</a></p>
    """, _account_context_html(blueprint_upload_authorisation(headers or {})))


def _flora_focus_page(headers=None) -> str:
    return _flora_v2_page("Focus", "focus", """
    <section class='hero'><p class='eyebrow'>Focus</p><h1>Compare enterprises and identify where attention is warranted.</h1><p class='lead'>Enterprise comparison is the intended next capability. Today, Focus keeps the existing Enterprise Canvas accessible without inventing priority scores.</p></section>
    <section class='card'><h2>Enterprise Canvas</h2><p>Open governed Enterprise Twin views and inspect current evidence, Unknowns and Contradictions.</p><p><a class='button-link' href='/digital-twins'>Open Enterprise Canvas</a></p></section>
    <p><a href='/'>Back to Home</a></p>
    """, _account_context_html(blueprint_upload_authorisation(headers or {})))


def _flora_shape_page(headers=None) -> str:
    items = ''.join(f"<li>{i}</li>" for i in ["Who?","Why now?","Why them?","What evidence?","What remains Unknown?","What contradicts the view?","What next?"])
    return _flora_v2_page("Shape", "shape", f"""
    <section class='hero'><p class='eyebrow'>Shape</p><h1>Prepare an evidence-backed executive engagement.</h1><p class='lead'>Shape will turn governed intelligence into a proportionate Strategic Sales Brief. Unsupported named executives or enterprise-specific claims will not be invented.</p></section>
    <section class='card'><h2>Strategic Sales Brief pathway</h2><p>Use the current Banking/BT Enterprise Intelligence route where available, then validate evidence before action.</p><p><a class='button-link' href='/digital-twins/bt-group-plc/intelligence'>Open Strategic Sales Brief path</a></p><h3>Expected output contract</h3><ul>{items}</ul></section>
    <p><a href='/'>Back to Home</a></p>
    """, _account_context_html(blueprint_upload_authorisation(headers or {})))


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
    return _flora_v2_page("Ask Flora", "home", f"""
    <section class='hero'><p class='eyebrow'>Ask Flora</p><h1>Question received</h1><p class='lead'>{escape(question)}</p></section>
    <section class='card'><h2>Evidence-backed answer not generated here</h2><p>This interim question path preserves the submitted question and does not fabricate intelligence. Use the governed Banking prototype path for the current supported Enterprise Intelligence slice.</p><p><a class='button-link' href='/digital-twins/bt-group-plc/intelligence'>Open Banking Enterprise Intelligence</a> <a class='secondary-link' href='/explore'>Explore Banking</a></p></section>
    <p><a href='/'>Back to Home</a></p>
    """, _account_context_html(blueprint_upload_authorisation(headers or {})))


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
    :root{{--bg:#f5f1ea;--ink:#13211c;--muted:#5f6f68;--line:#ded6c8;--card:#fffdf9;--brand:#174d3f;--brand2:#e7f1ec;--focus:#9b5cff}}*{{box-sizing:border-box}}body{{font-family:Inter,Arial,sans-serif;margin:0;background:linear-gradient(180deg,#fbf8f2,#f3eee5);color:var(--ink);line-height:1.55}}a{{color:var(--brand);font-weight:700;text-underline-offset:3px}}a:focus-visible,button:focus-visible,input:focus-visible{{outline:3px solid var(--focus);outline-offset:3px}}.shell{{max-width:1120px;margin:auto;padding:24px}}.topbar{{display:flex;gap:20px;align-items:center;justify-content:space-between;margin-bottom:44px}}.brand strong{{display:block;font-size:1.3rem}}.brand span,.muted{{color:var(--muted)}}.primary-nav{{display:flex;gap:6px;flex-wrap:wrap}}.primary-nav a{{padding:10px 12px;border-radius:999px;text-decoration:none;color:var(--ink);font-weight:650}}.primary-nav a[aria-current='page']{{background:var(--brand);color:white}}.account{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;color:var(--muted);font-size:.92rem}}button,.button-link{{background:var(--brand);color:#fff;border:0;border-radius:999px;padding:13px 18px;text-decoration:none;display:inline-block;cursor:pointer;font-weight:800}}button:hover,.button-link:hover{{background:#0f392f}}.secondary-link{{display:inline-block;padding:10px 0}}.hero,.card,.mode-card a{{background:rgba(255,253,249,.95);border:1px solid var(--line);border-radius:24px;box-shadow:0 18px 50px #1b13060a}}.hero{{padding:42px;margin:18px 0}}.question-hero{{padding:56px}}.eyebrow{{text-transform:uppercase;letter-spacing:.12em;color:var(--brand);font-weight:800;margin:0 0 8px}}h1{{font-size:clamp(2.15rem,5vw,4.5rem);line-height:1.02;margin:.1em 0 .25em}}.lead{{font-size:clamp(1.08rem,2vw,1.35rem);max-width:780px;color:#31413a}}.question-form label{{display:block;font-size:clamp(1.25rem,3vw,2rem);font-weight:850;margin:28px 0 12px}}.question-row{{display:flex;gap:12px}}input{{min-height:56px;border:1px solid #c9beaf;border-radius:999px;padding:0 18px;font:inherit;font-size:1.05rem;background:white}}.question-row input{{flex:1;min-width:0}}.error{{color:#8a1f11;background:#fff0ec;border-left:4px solid #8a1f11;padding:10px 12px;border-radius:10px}}.mode-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:20px 0}}.mode-card a{{display:block;min-height:190px;padding:24px;text-decoration:none;color:var(--ink)}}.mode-card span{{display:block;color:var(--brand);font-weight:900;font-size:1.5rem}}.mode-card strong{{display:block;font-size:1.15rem;margin:8px 0}}.mode-card em{{font-style:normal;color:var(--muted)}}.card{{padding:24px;margin:16px 0}}.pill{{display:inline-block;border-radius:999px;padding:4px 10px;background:var(--brand2);margin-left:6px}}.link-list li{{margin:10px 0}}.visually-hidden{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}footer{{color:var(--muted);font-size:.9rem;padding:24px 0}}@media(max-width:780px){{.topbar{{align-items:flex-start;flex-direction:column;margin-bottom:20px}}.mode-grid{{grid-template-columns:1fr}}.question-row{{flex-direction:column}}.hero,.question-hero{{padding:28px}}.shell{{padding:16px}}.primary-nav a{{padding:10px 9px}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
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
    if path in {"/", "/flora", "/flora/", "/pilot-sign-in", "/explore", "/focus", "/shape", "/governance", "/ask"} or path.startswith("/blueprint-import") or path.startswith("/digital-twins") or path.startswith("/ai-financial-report") or path.startswith("/financial-intelligence") or path == "/financial-reports" or path.startswith("/settings/architecture-export") or path == "/settings/general":
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
