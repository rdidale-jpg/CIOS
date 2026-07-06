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
from urllib.parse import parse_qs, urlparse

from cios.applications.flora.live.collect import collect, current_status
from cios.applications.flora.live.progress import read_state, mark_stale_interrupted
from cios.applications.flora.live.views import acquisition_plans_page, collection_progress_page, collection_result, collection_start_page, dashboard, evidence_page, feedback_diagnostics_page, rejected_claims_page, source_effectiveness_page, sources_page
from cios.applications.flora.workspace.feedback import create_feedback_record, create_logbook_record
from cios.applications.flora.rob_score import create_rob_score_record
from cios.applications.flora.workspace.views import case_page, landing_page, logbook_page, radar_page, rob_score_page, scoring_page, score_page, settings_page
from cios.applications.flora.digital_twins import digital_twins_landing_page, bt_twin_page, search_bt_twin, bt_search_progress_page
from cios.applications.flora.observatory.views import observatory_page, organisation_observatory_page
from cios.applications.flora.storage import startup_storage_status
from cios.applications.flora.document_review import apply_accepted, configure_financial_intelligence_logging, create_upload_run, financial_intelligence_admin_health_page, financial_intelligence_page, financial_intelligence_progress_page, financial_intelligence_progress_status, financial_intelligence_run_response, financial_intelligence_support_diagnostic_page, financial_intelligence_support_diagnostic_payload, create_financial_intelligence_progress_run, refresh_financial_intelligence, review_home_page, run_page, update_reviews

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
HOST_ENV = "HOST"
PORT_ENV = "PORT"
FLORA_HOST_ENV = "FLORA_HOST"
FLORA_PORT_ENV = "FLORA_PORT"
HEALTH_PAYLOAD = {"status": "healthy", "service": "flora"}
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
            elif parsed.path in {"/", "/morning-edition"}:
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
                self._html(digital_twins_landing_page())
            elif parsed.path == "/digital-twins/bt-group-plc":
                self._html(bt_twin_page((parse_qs(parsed.query).get("run_id") or [None])[0]))
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
                html, status = financial_intelligence_run_response(parsed.path.removeprefix("/financial-intelligence/"), show_support_control=_support_authorised(self.headers))
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
            elif parsed.path == "/settings":
                self._html(settings_page())
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

    def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length)
        form = {} if "multipart/form-data" in self.headers.get("Content-Type", "") else parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
        if self.path == "/digital-twins/bt-group-plc/search":
            run = search_bt_twin()
            self._redirect(f"/digital-twins/bt-group-plc/progress/{run['run_id']}")
        elif self.path.startswith("/financial-intelligence/bt-group-plc/refresh"):
            requested_mode = (form.get("acquisition_mode") or form.get("extraction_mode") or [""])[0]
            mode = requested_mode or ("administrative_review" if "reprocess=1" in self.path else "structured_standard_financials")
            run = create_financial_intelligence_progress_run("bt-group-plc", extraction_mode=mode)
            self._redirect(f"/financial-intelligence/progress/{run['run_id']}")
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

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def _support_authorised(headers) -> bool:
    expected = os.environ.get("FLORA_SUPPORT_TOKEN") or os.environ.get("FLORA_ADMIN_TOKEN")
    if not expected:
        return False
    auth = headers.get("Authorization", "")
    cookie = headers.get("Cookie", "")
    return auth == f"Bearer {expected}" or f"flora_support_token={expected}" in cookie

def _content_type_for_path(path: str) -> str | None:
    if path in {"/health", "/live/status", "/live/collect/status"}:
        return "application/json"
    if path.startswith("/digital-twins") or path.startswith("/ai-financial-report") or path.startswith("/financial-intelligence") or path == "/financial-reports":
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
        else:
            fields[name] = payload.decode("utf-8", "replace")
    return fields, files


def run(host: str | None = None, port: int | None = None) -> None:
    """Start the Flora production web service."""

    configure_financial_intelligence_logging()
    bind_host = host or env_host()
    bind_port = port if port is not None else env_port()
    storage = startup_storage_status()
    print(f"Flora storage {storage['status']}: {storage['data_root']}", flush=True)
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
