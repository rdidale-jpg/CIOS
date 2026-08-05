"""Pilot change metadata for Flora operational transparency."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from cios.applications.flora.live.runtime import deployment_metadata

_METADATA_PATH = Path(__file__).resolve().parents[1] / "config" / "current_pilot_change.json"


def current_pilot_change() -> dict[str, Any]:
    payload = json.loads(_METADATA_PATH.read_text(encoding="utf-8"))
    deployed = deployment_metadata()
    payload["commit_sha"] = deployed.get("commit_sha") or payload.get("commit_sha") or "Unavailable"
    payload["branch"] = deployed.get("branch") or "Unavailable"
    payload["deployment_timestamp"] = deployed.get("build_timestamp") or "Unavailable"
    payload["deployment_version"] = deployed.get("deployment_version") or payload["commit_sha"]
    return payload


def latest_import_record(records: list[Any]) -> Any | None:
    return max(records, key=lambda r: getattr(r, "received_at", ""), default=None)


def import_predates_deployment(imported_at: str, deployed_at: str) -> bool | None:
    if not imported_at or not deployed_at or "Unavailable" in deployed_at:
        return None
    try:
        return datetime.fromisoformat(imported_at.replace("Z", "+00:00")) < datetime.fromisoformat(deployed_at.replace("Z", "+00:00"))
    except ValueError:
        return None
