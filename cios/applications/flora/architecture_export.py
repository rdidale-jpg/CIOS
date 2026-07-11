"""Governed Flora architecture export integration.

Server-side only GitHub Actions dispatch/status helpers plus local validation
utilities mirrored by the packaging workflow. This module never exposes GitHub
credentials or package contents to the browser and does not mutate canonical
Twin data.
"""
from __future__ import annotations

import hashlib, json, os, re, time, urllib.error, urllib.request, uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from cios.applications.flora.access import authenticated_flora_user, active_flora_workspace, is_cios_owner
from cios.applications.flora.live.runtime import application_revision
from cios.applications.flora.storage import data_path
from cios.applications.flora.workspace.views import _page

WORKFLOW_FILE = "export-flora-architecture.yml"
WORKFLOW_NAME = "Export Flora Architecture"
DEFAULT_PROFILE = "architecture-reconciliation"
GENERATOR_VERSION = "flora-architecture-export-v1"
WORKFLOW_FILE_VERSION = "1.0"
REQUIRED_ROOT_FILES = [
    "FLORA_ARCHITECTURE_FILE_AUDIT.md",
    "FLORA_ARCHITECTURE_DOWNLOAD_LIST.txt",
    "FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json",
]
PROHIBITED_RE = re.compile(r"(^|/)(\.git|node_modules|\.venv|venv|__pycache__|\.cache|dist|build|coverage|\.idea|\.vscode|__MACOSX)(/|$)|(^|/)\.DS_Store$|(^|/)\.env(\..*)?$", re.I)
SECRET_RE = re.compile(r"(gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{16,}))", re.I)


@dataclass
class ExportAuditRecord:
    export_request_id: str
    requested_by: str
    workspace: str
    repository: str
    requested_ref: str
    resolved_commit: str = ""
    workflow_run_id: str = ""
    artifact_id: str = ""
    artifact_name: str = ""
    export_profile: str = DEFAULT_PROFILE
    status: str = "Requested"
    requested_at: str = ""
    completed_at: str = ""
    download_count: int = 0
    last_downloaded_at: str = ""
    checksum: str = ""
    failure_reason: str = ""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def configured_repository() -> str:
    return os.getenv("FLORA_ARCHITECTURE_REPOSITORY", os.getenv("GITHUB_REPOSITORY", "Rob/CIOS"))


def default_branch() -> str:
    return os.getenv("FLORA_ARCHITECTURE_DEFAULT_BRANCH", os.getenv("GITHUB_DEFAULT_BRANCH", "main"))


def production_commit() -> str:
    return os.getenv("FLORA_PRODUCTION_COMMIT", "")


def _store_path() -> Path:
    path = data_path("architecture_exports")
    path.mkdir(parents=True, exist_ok=True)
    return path / "audit_records.json"


def load_records() -> list[dict[str, Any]]:
    path = _store_path()
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_records(records: list[dict[str, Any]]) -> None:
    _store_path().write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")


def latest_record() -> dict[str, Any] | None:
    records = load_records()
    return records[-1] if records else None


def _github_token() -> str:
    return os.getenv("FLORA_GITHUB_TOKEN") or os.getenv("FLORA_GITHUB_APP_TOKEN") or ""


def github_configured() -> bool:
    return bool(configured_repository() and _github_token())


def _github(method: str, endpoint: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    token = _github_token()
    if not token:
        raise RuntimeError("GitHub integration not configured")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"https://api.github.com{endpoint}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data is not None: req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub API failed: {exc.code}") from exc



def github_integration_status() -> dict[str, Any]:
    repo = configured_repository()
    credential = bool(_github_token())
    workflow_available = bool(WORKFLOW_FILE)
    workflow_found = (Path(WORKFLOW_FILE).exists() or Path(".github/workflows").joinpath(WORKFLOW_FILE).exists())
    manifest_found = Path("FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json").exists()
    reasons = []
    if not repo:
        reasons.append("GitHub repository not configured")
    if not credential:
        reasons.append("GitHub credential unavailable")
    if not workflow_found:
        reasons.append("Workflow file not found")
    if not manifest_found:
        reasons.append("Manifest not found")
    latest = latest_record() or {}
    if latest.get("status") in {"failed", "Failed", "failure"}:
        reasons.append("Latest workflow failed")
    if not latest:
        reasons.append("No export package generated")
    status = "Ready" if repo and credential and workflow_found and manifest_found else "Not configured"
    if latest.get("status") in {"failed", "Failed", "failure"}:
        status = "Error"
    return {
        "status": status,
        "repository_configured": bool(repo),
        "workflow_available": workflow_available,
        "token_available": credential,
        "workflow_file_found": workflow_found,
        "manifest_found": manifest_found,
        "reason": reasons[0] if reasons else "Ready",
    }

def dispatch_export(headers: Any, *, requested_ref: str = "", export_profile: str = DEFAULT_PROFILE, publish_mode: str = "artifact", include_audit_reports: bool = True, explicit_release_confirmation: bool = False) -> ExportAuditRecord:
    if not is_cios_owner(headers):
        raise PermissionError("User not authorised")
    if publish_mode == "release" and not explicit_release_confirmation:
        raise PermissionError("Release publishing requires explicit confirmation")
    if not github_configured():
        raise RuntimeError("GitHub integration not configured")
    ref = requested_ref or default_branch()
    record = ExportAuditRecord(str(uuid.uuid4()), authenticated_flora_user(headers), active_flora_workspace(headers), configured_repository(), ref, export_profile=export_profile, requested_at=_now())
    _github("POST", f"/repos/{configured_repository()}/actions/workflows/{WORKFLOW_FILE}/dispatches", {"ref": default_branch(), "inputs": {"git_ref": ref, "export_profile": export_profile, "publish_mode": publish_mode, "include_audit_reports": str(include_audit_reports).lower()}})
    # GitHub dispatch is async and does not return run id. Record request now; refresh resolves run/artifact metadata.
    records = load_records(); records.append(asdict(record)); save_records(records)
    return record


def validate_manifest(repo_root: Path, profile: str = DEFAULT_PROFILE) -> dict[str, Any]:
    manifest_path = repo_root / "FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json"
    if not manifest_path.exists():
        raise FileNotFoundError("Manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = manifest.get("export_profiles", {})
    selected = profiles.get(profile)
    if not isinstance(selected, dict):
        raise ValueError("Manifest invalid")
    files = selected.get("files", [])
    if not isinstance(files, list):
        raise ValueError("Manifest invalid")
    validated, missing_optional = [], []
    root_real = repo_root.resolve()
    for item in files:
        path = item.get("path") if isinstance(item, dict) else str(item)
        required = bool(item.get("required", True)) if isinstance(item, dict) else True
        if not path or Path(path).is_absolute() or ".." in Path(path).parts or PROHIBITED_RE.search(path):
            raise ValueError("Repository path traversal is rejected")
        candidate = (repo_root / path)
        if not candidate.exists():
            if required: raise FileNotFoundError("Required file missing")
            missing_optional.append(path); continue
        real = candidate.resolve()
        if not str(real).startswith(str(root_real) + os.sep) and real != root_real:
            raise ValueError("Symbolic-link escape is rejected")
        if candidate.is_symlink() and real != candidate.absolute():
            # Symlinks are allowed only if they resolve inside repo; already checked.
            pass
        if candidate.is_file() and candidate.stat().st_size < 1_000_000:
            text = candidate.read_bytes()
            if b"\x00" not in text:
                decoded = text.decode("utf-8", "ignore")
                if path == ".env.example" and SECRET_RE.search(decoded):
                    raise ValueError("Sensitive content detected")
                if SECRET_RE.search(decoded):
                    raise ValueError("Sensitive content detected")
        validated.append(path)
    return {"manifest": manifest, "files": validated, "missing_optional_files": missing_optional, "included_bundles": selected.get("bundles", [])}


def refresh_latest(headers: Any) -> dict[str, Any]:
    if not is_cios_owner(headers):
        raise PermissionError("User not authorised")
    record = latest_record()
    if not record:
        return {"status": "No export requested"}
    if not github_configured():
        record["status"] = "GitHub integration not configured"; return record
    # Conservative: only enrich when configured; tests can monkeypatch this boundary.
    return record


def record_download(headers: Any) -> dict[str, Any]:
    if not is_cios_owner(headers):
        raise PermissionError("User not authorised")
    records = load_records()
    if not records: raise FileNotFoundError("Artifact unavailable")
    rec = records[-1]
    if rec.get("status") not in {"Succeeded", "success", "completed"}:
        raise RuntimeError("Workflow failed")
    if rec.get("artifact_expired"):
        raise RuntimeError("Artifact expired")
    rec["download_count"] = int(rec.get("download_count") or 0) + 1
    rec["last_downloaded_at"] = _now()
    save_records(records)
    return rec


def architecture_export_page(headers: Any) -> tuple[str, int]:
    if not is_cios_owner(headers):
        return _page("User not authorised", "<section class='hero'><h1>User not authorised</h1><p>Architecture Export requires owner-level permission.</p></section>"), 403
    rec = latest_record() or {}
    integration = github_integration_status()
    status = rec.get("status") or ("GitHub integration not configured" if not github_configured() else "No export requested")
    artifact_expired = bool(rec.get("artifact_expired"))
    ready_to_generate = integration["status"] == "Ready"
    download = "<p><a role='button' href='/settings/architecture-export/download'>Download latest package</a></p>" if rec.get("status") in {"Succeeded", "success", "completed"} and not artifact_expired else ""
    generate = f"<form method='post' action='/settings/architecture-export/generate'><input name='export_profile' value='{DEFAULT_PROFILE}'><button>Generate architecture package</button></form>" if ready_to_generate else "<p class='muted'>Generate architecture package unavailable until the integration status is Ready.</p>"
    empty = "" if ready_to_generate else f"<section class='card action'><h2>Architecture Export unavailable</h2><p><strong>Reason:</strong> {escape(integration['reason'])}</p><p><a href='/settings/general'>View configuration</a> · <a href='/settings/architecture-export'>Retry status</a> · <a href='https://github.com/{escape(configured_repository())}/actions/workflows/{WORKFLOW_FILE}'>Open workflow run</a></p></section>"
    expired = "<p class='warn'>Architecture package expired</p><p><button>Generate a new package</button></p>" if artifact_expired else ""
    rows = [("Repository", configured_repository()), ("Branch", default_branch()), ("Current commit", application_revision()), ("Production commit, if known", production_commit() or "Unknown"), ("Export profile", rec.get("export_profile", DEFAULT_PROFILE)), ("Latest export status", status), ("Latest export date", rec.get("completed_at") or rec.get("requested_at", "")), ("Package checksum", rec.get("checksum", "")), ("GitHub integration status", integration["status"]), ("Repository configured", "yes" if integration["repository_configured"] else "no"), ("Workflow available", "yes" if integration["workflow_available"] else "no"), ("Token/app credential available", "yes" if integration["token_available"] else "no"), ("Workflow file found", "yes" if integration["workflow_file_found"] else "no"), ("Manifest found", "yes" if integration["manifest_found"] else "no"), ("Sensitive exclusions", ".env, credentials, keys, tokens, data, logs, caches, build outputs")]
    table = "".join(f"<tr><th>{escape(k)}</th><td>{escape(str(v))}</td></tr>" for k,v in rows)
    body = f"""<section class='hero'><h1>Architecture Export</h1><p>Generate and download a governed architecture baseline package from the configured GitHub repository.</p></section><section class='card'><table>{table}</table></section>{empty}<section class='card action'>{generate}<p><a href='/settings/architecture-export'>Retry status</a></p>{download}<p><a href='/settings/architecture-export/manifest'>View manifest</a> · <a href='/settings/architecture-export/exclusions'>View exclusions</a> · <a href='https://github.com/{escape(configured_repository())}/actions/workflows/{WORKFLOW_FILE}'>View workflow run</a></p>{expired}</section>"""
    return _page("Architecture Export", body), 200
