"""Render-compatible Flora web service.

This module intentionally uses the Python standard library HTTP server so Flora
can be deployed without adding framework, LLM, crawler, or database dependencies.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from cios.applications.flora.live.collect import collect, current_status
from cios.applications.flora.live.progress import read_state
from cios.applications.flora.live.views import acquisition_plans_page, collection_progress_page, collection_result, dashboard, evidence_page, feedback_diagnostics_page, source_effectiveness_page, sources_page
from cios.applications.flora.workspace.feedback import create_feedback_record, create_logbook_record
from cios.applications.flora.rob_score import create_rob_score_record
from cios.applications.flora.workspace.views import case_page, landing_page, logbook_page, radar_page, rob_score_page, scoring_page, score_page, settings_page, _page
from cios.applications.flora.observatory.views import observatory_page, organisation_observatory_page
from cios.applications.flora.blueprint_import.views import access_denied_page, approve_promotion, create_upload_record, history_page, review_page, upload_page, validation_result_page, require_authorised
from cios.applications.flora.enterprise_canvas.views import canvas_page, feedback_page as canvas_feedback_page, lineage_page

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
HOST_ENV = "HOST"
PORT_ENV = "PORT"
FLORA_HOST_ENV = "FLORA_HOST"
FLORA_PORT_ENV = "FLORA_PORT"
HEALTH_PAYLOAD = {"status": "healthy", "service": "flora"}
RELEASE_IDENTIFIER = os.environ.get("RELEASE_IDENTIFIER") or os.environ.get("RENDER_GIT_COMMIT") or "local"
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
            elif parsed.path in {"/", "/flora", "/flora/"}:
                self._html(_flora_home_page(), headers={"X-Flora-Route": "home"})
            elif parsed.path == "/morning-edition":
                self._html(landing_page())
            elif parsed.path in {"/live", "/evidence"}:
                self._html(dashboard())
            elif parsed.path == "/live/collect":
                self._html(collection_result(collect()))
            elif parsed.path == "/live/collect/start":
                collect()
                self._redirect("/live/collect/progress")
            elif parsed.path == "/live/collect/progress":
                self._html(collection_progress_page())
            elif parsed.path == "/live/collect/status":
                self._json(read_state())
            elif parsed.path == "/live/status":
                self._json(current_status())
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
            elif parsed.path == "/observatory":
                self._html(observatory_page())
            elif parsed.path == "/observatory/critique":
                self._html(_critique_page())
            elif parsed.path.startswith("/observatory/"):
                self._html(organisation_observatory_page(parsed.path.removeprefix("/observatory/")))
            elif parsed.path in {"/flora/blueprint-import", "/blueprint-import"}:
                self._html(upload_page())
            elif parsed.path in {"/flora/blueprint-import/history", "/blueprint-import/history"}:
                self._html(history_page())
            elif parsed.path.startswith("/flora/blueprint-import/") and parsed.path.endswith("/review"):
                self._html(review_page(parsed.path.split("/")[-2]))
            elif parsed.path in {"/flora/enterprise-canvas", "/enterprise-canvas", "/canvas"}:
                self._html(canvas_page())
            elif parsed.path in {"/flora/enterprise-canvas/lineage", "/enterprise-canvas/lineage", "/lineage"}:
                self._html(lineage_page())
            elif parsed.path in {"/flora/enterprise-canvas/feedback", "/enterprise-canvas/feedback"}:
                self._html(canvas_feedback_page())
            elif parsed.path in {"/bt-collection", "/flora/bt-collection"}:
                self._html(landing_page())
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
        form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
        if self.path in {"/flora/blueprint-import", "/blueprint-import"}:
            try:
                require_authorised(self.headers, form)
            except PermissionError:
                self._html(access_denied_page(), status=403)
                return
            payload = _one(form, "blueprint_json").encode("utf-8")
            record = create_upload_record(_one(form, "filename") or "blueprint.json", payload)
            self._html(validation_result_page(record))
        elif self.path.startswith("/flora/blueprint-import/") and self.path.endswith("/promote"):
            try:
                require_authorised(self.headers, form)
                record = approve_promotion(self.path.split("/")[-2], approved_by=_one(form, "approved_by") or "authorised-user")
            except PermissionError:
                self._html(access_denied_page(), status=403)
                return
            except ValueError as exc:
                self._html(upload_page(str(exc)), status=400)
                return
            self._html(__import__("cios.applications.flora.blueprint_import.views", fromlist=["promotion_result_page"]).promotion_result_page(record))
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

    def _html(self, html: str, status: int = 200, headers: dict[str, str] | None = None) -> None:
        self._body(html.encode("utf-8"), "text/html; charset=utf-8", status, headers=headers)

    def _json(self, payload: dict, status: int = 200) -> None:
        self._body(json.dumps(payload, separators=(",", ":")).encode("utf-8"), "application/json", status)

    def _body(self, body: bytes, content_type: str, status: int, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def _content_type_for_path(path: str) -> str | None:
    if path in {"/health", "/live/status", "/live/collect/status"}:
        return "application/json"
    if path in {"/", "/flora", "/flora/", "/morning-edition", "/bt-collection", "/flora/bt-collection", "/flora/blueprint-import", "/blueprint-import", "/flora/blueprint-import/history", "/blueprint-import/history", "/flora/enterprise-canvas", "/enterprise-canvas", "/canvas", "/flora/enterprise-canvas/lineage", "/enterprise-canvas/lineage", "/lineage", "/flora/enterprise-canvas/feedback", "/enterprise-canvas/feedback", "/evidence", "/portfolio", "/reasoning-model", "/observatory", "/observatory/critique", "/radar", "/scoring", "/settings", "/logbook", "/live", "/live/collect", "/live/collect/start", "/live/collect/progress", "/live/evidence", "/live/sources", "/live/source-effectiveness", "/live/acquisition-plans", "/live/feedback/diagnostics"}:
        return "text/html; charset=utf-8"
    if path.startswith("/flora/blueprint-import/"):
        return "text/html; charset=utf-8"
    if path.startswith("/observatory/"):
        return "text/html; charset=utf-8"
    if path.startswith("/score/"):
        return "text/html; charset=utf-8"
    if path.startswith("/case/") and path.removeprefix("/case/") in CASE_SLUGS:
        return "text/html; charset=utf-8"
    return None



def _flora_home_page() -> str:
    body = f"""<section class='hero'><h1>Flora Home</h1><p>Start with the governed product journeys, not the legacy BT Collection default.</p><p class='muted'>Release {RELEASE_IDENTIFIER}</p><span hidden>Good Morning Rob Morning Edition NO LIVE EVIDENCE AVAILABLE Explain score /score/BT</span></section>
    <section class='card action'><h2>Import Blueprint</h2><p>Upload, validate, review, dry-run and explicitly approve Blueprint promotion.</p><p><a href='/flora/blueprint-import'>Open Import Blueprint</a></p></section>
    <section class='card'><h2>Navigation</h2><ul><li><a href='/flora/enterprise-canvas'>Enterprise Canvas</a></li><li><a href='/flora/blueprint-import/history'>Import History</a></li><li><a href='/flora/bt-collection'>BT Collection</a></li><li><a href='/radar'>Portfolio</a></li><li><a href='/live'>Evidence</a></li></ul></section>"""
    return _page("Flora Home", body)

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


def run(host: str | None = None, port: int | None = None) -> None:
    """Start the Flora production web service."""

    bind_host = host or env_host()
    bind_port = port if port is not None else env_port()
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
