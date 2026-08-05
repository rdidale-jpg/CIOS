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
    payload["deployed_change_marker"] = deployed.get("deployed_change_marker") or payload.get("deployed_change_marker") or "Unavailable"
    payload["deployment_service"] = deployed.get("render_service") or payload.get("deployment_service") or "Unavailable"
    payload["repository"] = deployed.get("repository") or payload.get("repository") or "Unavailable"
    payload["build_command"] = deployed.get("build_command") or payload.get("build_command") or "Unavailable"
    payload["start_command"] = deployed.get("start_command") or payload.get("start_command") or "Unavailable"
    payload["auto_deploy"] = deployed.get("auto_deploy") or payload.get("auto_deploy") or "Unavailable"
    payload["latest_deployment_status"] = deployed.get("latest_deployment_status") or payload.get("latest_deployment_status") or "Unavailable"
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
