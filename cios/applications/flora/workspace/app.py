"""Run the local Flora Pilot Workspace web server."""
from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from cios.applications.flora.workspace.feedback import create_feedback_record, create_logbook_record
from cios.applications.flora.workspace.views import case_page, landing_page, logbook_page, settings_page

HOST = "127.0.0.1"
PORT = 8000
HOST_ENV = "FLORA_HOST"
PORT_ENV = "FLORA_PORT"
PREVIEW_URL_ENV = "FLORA_PREVIEW_URL"


class FloraWorkspaceHandler(BaseHTTPRequestHandler):
    """Small standard-library HTTP handler for local pilot use."""

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib callback name
        parsed = urlparse(self.path)
        try:
            if parsed.path in {"/", "/logbook", "/settings"} or parsed.path.startswith("/case/"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
            else:
                self.send_error(404, "Flora workspace route not found")
        except ValueError as exc:
            self.send_error(404, str(exc))

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                self._html(landing_page())
            elif parsed.path.startswith("/case/"):
                self._html(case_page(parsed.path.removeprefix("/case/")))
            elif parsed.path == "/logbook":
                self._html(logbook_page(saved=parse_qs(parsed.query).get("saved") == ["1"]))
            elif parsed.path == "/settings":
                self._html(settings_page())
            else:
                self.send_error(404, "Flora workspace route not found")
        except ValueError as exc:
            self.send_error(404, str(exc))

    def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
        if self.path == "/feedback":
            create_feedback_record(
                organisation=_one(form, "organisation"),
                action_text=_one(form, "action_text"),
                feedback_type=_one(form, "feedback_type"),
                optional_comment=_one(form, "optional_comment"),
                source_page=_one(form, "source_page"),
            )
            self._redirect(_one(form, "source_page") or "/")
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
            self.send_error(404, "Flora workspace route not found")

    def _html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def _one(form: dict[str, list[str]], key: str) -> str:
    return form.get(key, [""])[0]


def _env_host() -> str:
    return os.environ.get(HOST_ENV, HOST)


def _env_port() -> int:
    raw_port = os.environ.get(PORT_ENV)
    if raw_port is None:
        return PORT
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError(f"{PORT_ENV} must be an integer; got {raw_port!r}") from exc
    if not 1 <= port <= 65535:
        raise ValueError(f"{PORT_ENV} must be between 1 and 65535; got {port}")
    return port


def _display_urls(host: str, port: int) -> list[str]:
    preview_url = os.environ.get(PREVIEW_URL_ENV)
    if preview_url:
        return [preview_url]
    if host in {"0.0.0.0", "::"}:
        return [f"http://localhost:{port}", f"http://127.0.0.1:{port}"]
    return [f"http://{host}:{port}"]


def _print_startup_message(host: str, port: int) -> None:
    print("Flora Pilot Workspace is running.")
    print(f"Listening on: {host}:{port}")
    print("Open in your browser:")
    for url in _display_urls(host, port):
        print(f"  {url}")
    print(f"Local-safe default: {HOST_ENV} defaults to {HOST}.")
    print(f"Hosted preview: set {HOST_ENV}=0.0.0.0 and {PORT_ENV}=8000, then use your workspace preview URL.")
    print(f"If your platform provides a public preview URL, set {PREVIEW_URL_ENV} to print it here.")
    print("Press Ctrl+C to stop.")


def run(host: str | None = None, port: int | None = None) -> None:
    host = host or _env_host()
    port = port if port is not None else _env_port()
    server = ThreadingHTTPServer((host, port), FloraWorkspaceHandler)
    _print_startup_message(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Flora Pilot Workspace.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
