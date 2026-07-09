"""Governed Blueprint Import views for Flora.

The import journey is deliberately staged: upload, validate, review/map,
dry-run, approve promotion, and view the result. Uploading alone records an
import draft/history item only; it never mutates canonical Flora data.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Mapping, Sequence

from cios.applications.flora.workspace.views import _page

IMPORT_TOKEN_ENV = "FLORA_BLUEPRINT_IMPORT_TOKEN"
IMPORT_DATA_DIR_ENV = "FLORA_BLUEPRINT_IMPORT_DIR"
DEFAULT_IMPORT_DIR = Path("data/flora/blueprint_import")
MAX_UPLOAD_BYTES = 512 * 1024
REQUIRED_BLUEPRINT_FIELDS = ("name", "version")


@dataclass(frozen=True)
class BlueprintImportRecord:
    import_id: str
    filename: str
    uploaded_at: str
    sha256: str
    status: str
    validation_errors: tuple[str, ...]
    canonical_mutation: bool = False
    promoted_at: str | None = None
    approved_by: str | None = None


def import_directory() -> Path:
    return Path(os.environ.get(IMPORT_DATA_DIR_ENV, DEFAULT_IMPORT_DIR))


def history_path() -> Path:
    return import_directory() / "history.jsonl"


def _authorised(headers: Mapping[str, str] | None = None, form: Mapping[str, Sequence[str]] | None = None) -> bool:
    token = os.environ.get(IMPORT_TOKEN_ENV)
    if not token:
        return False
    supplied = ""
    if headers:
        supplied = headers.get("X-Flora-Import-Token") or headers.get("Authorization", "").removeprefix("Bearer ")
    if not supplied and form:
        values = form.get("access_token") or form.get("token") or [""]
        supplied = values[0] if values else ""
    return supplied == token


def access_denied_page() -> str:
    return _page("Blueprint Import access denied", "<section class='hero'><h1>Access denied</h1><p>Blueprint Import requires server-side authorisation.</p></section>")


def require_authorised(headers: Mapping[str, str] | None = None, form: Mapping[str, Sequence[str]] | None = None) -> None:
    if not _authorised(headers, form):
        raise PermissionError("Blueprint Import requires authorisation")


def validate_blueprint_payload(payload: bytes) -> tuple[dict, tuple[str, ...]]:
    if len(payload) > MAX_UPLOAD_BYTES:
        return {}, ("Upload exceeds the governed size limit.",)
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, (f"Blueprint must be valid UTF-8 JSON: {exc}",)
    if not isinstance(data, dict):
        return {}, ("Blueprint root must be a JSON object.",)
    errors = tuple(f"Missing required field: {field}" for field in REQUIRED_BLUEPRINT_FIELDS if not data.get(field))
    return data, errors


def create_upload_record(filename: str, payload: bytes) -> BlueprintImportRecord:
    _data, errors = validate_blueprint_payload(payload)
    digest = hashlib.sha256(payload).hexdigest()
    import_id = digest[:16]
    record = BlueprintImportRecord(
        import_id=import_id,
        filename=Path(filename or "blueprint.json").name,
        uploaded_at=datetime.now(timezone.utc).isoformat(),
        sha256=digest,
        status="validation_failed" if errors else "uploaded",
        validation_errors=errors,
        canonical_mutation=False,
    )
    save_record(record)
    (import_directory() / f"{import_id}.json").write_bytes(payload)
    return record


def save_record(record: BlueprintImportRecord) -> None:
    import_directory().mkdir(parents=True, exist_ok=True)
    with history_path().open("a", encoding="utf-8") as handle:
        payload = asdict(record)
        payload["validation_errors"] = list(record.validation_errors)
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def import_history() -> list[BlueprintImportRecord]:
    path = history_path()
    if not path.exists():
        return []
    records: list[BlueprintImportRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        item["validation_errors"] = tuple(item.get("validation_errors", ()))
        records.append(BlueprintImportRecord(**item))
    return records


def get_record(import_id: str) -> BlueprintImportRecord | None:
    for record in reversed(import_history()):
        if record.import_id == import_id:
            return record
    return None


def promotion_dry_run(import_id: str) -> dict[str, object]:
    record = get_record(import_id)
    if record is None:
        raise ValueError("Unknown blueprint import")
    return {"import_id": import_id, "canonical_mutation": False, "effects": ["Validate blueprint schema", "Map blueprint to Enterprise Canvas", "Prepare promotion approval"]}


def approve_promotion(import_id: str, approved_by: str = "authorised-user") -> BlueprintImportRecord:
    record = get_record(import_id)
    if record is None:
        raise ValueError("Unknown blueprint import")
    if record.validation_errors:
        raise ValueError("Cannot promote an invalid blueprint")
    promoted = BlueprintImportRecord(**{**asdict(record), "status": "promoted", "promoted_at": datetime.now(timezone.utc).isoformat(), "approved_by": approved_by, "canonical_mutation": True})
    save_record(promoted)
    return promoted


def upload_page(message: str = "") -> str:
    notice = f"<p class='pill'>{escape(message)}</p>" if message else ""
    body = f"""<section class='hero'><h1>Import Blueprint</h1><p>Governed Blueprint Import keeps upload, validation, review, dry-run and explicit promotion approval separate.</p>{notice}</section>
    <section class='card'><form method='post' action='/flora/blueprint-import'><label>Access token</label><input name='access_token' type='password'><label>Blueprint JSON</label><textarea name='blueprint_json' placeholder='{{&quot;name&quot;:&quot;Example&quot;,&quot;version&quot;:&quot;1.0&quot;}}'></textarea><p><button>Upload for validation</button></p></form></section>
    <section class='card'><p><a href='/flora/blueprint-import/history'>Import History</a> · <a href='/flora/enterprise-canvas'>Enterprise Canvas</a></p></section>"""
    return _page("Import Blueprint", body)


def validation_result_page(record: BlueprintImportRecord) -> str:
    errors = "".join(f"<li>{escape(e)}</li>" for e in record.validation_errors) or "<li>No validation errors.</li>"
    body = f"<section class='hero'><h1>Validation Result</h1><p>Import {escape(record.import_id)} status: {escape(record.status)}</p></section><section class='card'><ul>{errors}</ul><p><a href='/flora/blueprint-import/{escape(record.import_id)}/review'>Review and mapping</a></p></section>"
    return _page("Validation Result", body)


def history_page() -> str:
    rows = "".join(f"<tr><td>{escape(r.import_id)}</td><td>{escape(r.filename)}</td><td>{escape(r.status)}</td><td>{'yes' if r.canonical_mutation else 'no'}</td><td><a href='/flora/blueprint-import/{escape(r.import_id)}/review'>Review</a></td></tr>" for r in import_history()) or "<tr><td colspan='5'>No imports yet.</td></tr>"
    return _page("Import History", f"<section class='hero'><h1>Import History</h1></section><section class='card'><table><thead><tr><th>Import</th><th>File</th><th>Status</th><th>Canonical mutation</th><th>Review</th></tr></thead><tbody>{rows}</tbody></table></section>")


def review_page(import_id: str) -> str:
    record = get_record(import_id)
    if record is None:
        raise ValueError("Unknown blueprint import")
    dry = promotion_dry_run(import_id)
    effects = "".join(f"<li>{escape(str(e))}</li>" for e in dry["effects"])
    return _page("Review and Mapping", f"<section class='hero'><h1>Review and Mapping</h1><p>Import {escape(import_id)}</p></section><section class='card'><h2>Dry-run effects</h2><ul>{effects}</ul><form method='post' action='/flora/blueprint-import/{escape(import_id)}/promote'><label>Access token</label><input name='access_token' type='password'><label>Approved by</label><input name='approved_by' value='authorised-user'><p><button>Approve promotion</button></p></form></section>")


def promotion_result_page(record: BlueprintImportRecord) -> str:
    return _page("Promotion Result", f"<section class='hero'><h1>Promotion Result</h1><p>Import {escape(record.import_id)} promoted by {escape(record.approved_by or '')}.</p></section><section class='card'><p>Canonical mutation: {'yes' if record.canonical_mutation else 'no'}</p><p><a href='/flora/enterprise-canvas'>Enterprise Canvas</a></p></section>")
