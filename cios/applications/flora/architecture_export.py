"""Owner-only Flora architecture export download integration.

Flora reads published, public architecture-export metadata and links the CIOS
owner directly to the latest GitHub release asset. It does not dispatch GitHub
workflows, poll Actions, store GitHub credentials, proxy ZIP contents, or mutate
canonical Twin data.
"""
from __future__ import annotations

import json, os, re, urllib.error, urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from cios.applications.flora.access import is_cios_owner
from cios.applications.flora.storage import data_path
from cios.applications.flora.workspace.views import _page

WORKFLOW_FILE = os.getenv("FLORA_ARCHITECTURE_WORKFLOW", "export-flora-architecture.yml")
DEFAULT_PROFILE = "architecture-reconciliation"
LATEST_RELEASE_TAG = "architecture-baseline-latest"
DEFAULT_REPOSITORY = "Rob/CIOS"
PROHIBITED_RE = re.compile(r"(^|/)(\.git|node_modules|\.venv|venv|__pycache__|\.cache|dist|build|coverage|\.idea|\.vscode|__MACOSX|logs?)(/|$)|(^|/)\.DS_Store$|(^|/)\.env(\..*)?$", re.I)
SECRET_RE = re.compile(r"(gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{16,}))", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def configured_repository() -> str:
    return os.getenv("FLORA_ARCHITECTURE_REPOSITORY", os.getenv("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))


def configured_workflow() -> str:
    return os.getenv("FLORA_ARCHITECTURE_WORKFLOW", WORKFLOW_FILE)


def github_actions_url() -> str:
    return f"https://github.com/{configured_repository()}/actions/workflows/{configured_workflow()}"


def github_releases_url() -> str:
    return f"https://github.com/{configured_repository()}/releases"


def default_metadata_url() -> str:
    return f"https://github.com/{configured_repository()}/releases/download/{LATEST_RELEASE_TAG}/architecture-export-latest.json"


def configured_metadata_url() -> str:
    return os.getenv("FLORA_ARCHITECTURE_EXPORT_METADATA_URL", default_metadata_url()).strip()


def configured_export_url() -> str:
    return os.getenv("FLORA_ARCHITECTURE_EXPORT_URL", "").strip()


def _download_log_path() -> Path:
    path = data_path("architecture_exports")
    path.mkdir(parents=True, exist_ok=True)
    return path / "download_log.jsonl"


def _fetch_json(url: str) -> dict[str, Any]:
    if not url.lower().startswith("https://"):
        raise RuntimeError("Architecture export metadata URL must be HTTPS")
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Flora architecture export metadata reader"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("No published architecture baseline was found.") from exc


def load_export_metadata() -> dict[str, Any] | None:
    metadata_url = configured_metadata_url()
    if not metadata_url:
        return None
    data = _fetch_json(metadata_url)
    if not isinstance(data, dict):
        raise RuntimeError("Architecture export metadata is invalid")
    return data


def validated_export_metadata() -> dict[str, Any] | None:
    data = load_export_metadata()
    if not data:
        return None
    required = ["package_name", "repository", "branch", "commit_sha", "generated_at", "release_tag", "release_url", "asset_url", "checksum", "file_count", "total_size", "export_profile", "workflow_run_id"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise RuntimeError("Architecture export metadata is invalid")
    asset_url = configured_export_url() or str(data["asset_url"])
    if not asset_url.lower().startswith("https://"):
        raise RuntimeError("Architecture export asset URL must be HTTPS")
    clean = dict(data)
    clean["asset_url"] = asset_url
    return clean


def validate_manifest(repo_root: Path, profile: str = DEFAULT_PROFILE) -> dict[str, Any]:
    manifest_path = repo_root / "FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json"
    if not manifest_path.exists():
        raise FileNotFoundError("Manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selected = manifest.get("export_profiles", {}).get(profile)
    if not isinstance(selected, dict) or not isinstance(selected.get("files"), list):
        raise ValueError("Manifest invalid")
    validated, missing_optional = [], []
    root_real = repo_root.resolve()
    for item in selected["files"]:
        path = item.get("path") if isinstance(item, dict) else str(item)
        required = bool(item.get("required", True)) if isinstance(item, dict) else True
        if not path or Path(path).is_absolute() or ".." in Path(path).parts or PROHIBITED_RE.search(path):
            raise ValueError("Repository path traversal is rejected")
        candidate = repo_root / path
        if not candidate.exists():
            if required: raise FileNotFoundError("Required file missing")
            missing_optional.append(path); continue
        real = candidate.resolve()
        if not str(real).startswith(str(root_real) + os.sep) and real != root_real:
            raise ValueError("Symbolic-link escape is rejected")
        if candidate.is_file() and candidate.stat().st_size < 1_000_000:
            raw = candidate.read_bytes()
            if b"\x00" not in raw and SECRET_RE.search(raw.decode("utf-8", "ignore")):
                raise ValueError("Sensitive content detected")
        validated.append(path)
    return {"manifest": manifest, "files": validated, "missing_optional_files": missing_optional, "included_bundles": selected.get("bundles", [])}


def github_integration_status() -> dict[str, Any]:
    try:
        metadata = validated_export_metadata()
        if not metadata:
            return {"status": "Architecture package unavailable", "reason": "No published architecture baseline was found.", "metadata": None}
        return {"status": "Ready", "reason": "Ready", "metadata": metadata}
    except RuntimeError as exc:
        return {"status": "Architecture package unavailable", "reason": str(exc), "metadata": None}


def record_download(headers: Any) -> dict[str, Any]:
    if not is_cios_owner(headers):
        raise PermissionError("User not authorised")
    metadata = validated_export_metadata()
    if not metadata:
        raise RuntimeError("No published architecture baseline was found.")
    entry = {"downloaded_at": _now(), "user": headers.get("X-Flora-User", "unknown") if hasattr(headers, "get") else "unknown", "package_name": metadata["package_name"], "commit_sha": metadata["commit_sha"], "asset_url": metadata["asset_url"]}
    with _download_log_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    return metadata


def architecture_export_page(headers: Any) -> tuple[str, int]:
    if not is_cios_owner(headers):
        return _page("User not authorised", "<section class='hero'><h1>User not authorised</h1><p>Architecture Export requires owner-level permission.</p></section>"), 403
    status = github_integration_status()
    metadata = status.get("metadata") or {}
    ready = status["status"] == "Ready"
    rows = [
        ("Package status", "Ready" if ready else "Architecture package unavailable"),
        ("Repository", metadata.get("repository") or configured_repository()),
        ("Commit SHA", metadata.get("commit_sha", "")),
        ("Generated date", metadata.get("generated_at", "")),
        ("Export profile", metadata.get("export_profile", DEFAULT_PROFILE)),
        ("File count", metadata.get("file_count", "")),
        ("Package size", metadata.get("total_size", "")),
        ("Checksum", metadata.get("checksum", "")),
    ]
    table = "".join(f"<tr><th>{escape(k)}</th><td>{escape(str(v))}</td></tr>" for k, v in rows)
    if ready:
        actions = f"<p><a role='button' href='/settings/architecture-export/download'>Download latest package</a></p><p><a href='{escape(str(metadata.get('release_url', github_releases_url())))}'>Open GitHub release</a></p>"
        unavailable = ""
    else:
        unavailable = "<section class='card action'><h2>Architecture package unavailable</h2><p><strong>Reason:</strong> No published architecture baseline was found.</p></section>"
        actions = f"<p><a href='{escape(github_actions_url())}'>Open GitHub Actions</a> · <a href='{escape(github_releases_url())}'>Open GitHub releases</a></p>"
    body = f"""<section class='hero'><h1>Architecture Export</h1><p>Download the latest governed architecture baseline package published from GitHub for the CIOS owner.</p></section><section class='card'><table>{table}</table></section>{unavailable}<section class='card action'>{actions}</section>"""
    return _page("Architecture Export", body), 200
