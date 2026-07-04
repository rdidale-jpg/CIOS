"""Lightweight file-backed live collection progress state."""
from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATE_DIR = Path(".flora_pilot/live_evidence")
STATE_PATH = STATE_DIR / "collection_run_state.json"
TERMINAL_STATES = {"completed", "completed_with_no_accepted_intelligence", "failed", "interrupted", "completed successfully", "Completed with no accepted intelligence"}
IN_PROGRESS_STATES = {"queued", "starting", "collecting", "parsing", "extracting_evidence", "accepting_evidence", "creating_observations", "updating_model", "running"}

def percent_complete(attempted: int, total: int) -> int:
    if total <= 0:
        return 100
    return max(0, min(100, round((attempted / total) * 100)))

def default_state() -> dict[str, Any]:
    return {"run_id":"none","started_at":None,"completed_at":None,"status":"queued","canonical_enterprise_id":"","enterprise_display_name":"","profile_id":"","collection_mode":"","collection_pass":"","sources_total":0,"sources_attempted":0,"sources_succeeded":0,"sources_failed":0,"sources_retrieved":0,"evidence_candidates":0,"evidence_accepted":0,"evidence_rejected":0,"evidence_downgraded":0,"evidence_context_only":0,"evidence_duplicate":0,"evidence_corroborated":0,"evidence_extraction_failed":0,"documents_retrieved":0,"pdfs_parsed":0,"pages_extracted":0,"tables_detected":0,"observations_created":0,"observations_corroborated":0,"observations_rejected":0,"model_attributes_created":0,"model_attributes_changed":0,"model_attributes_reconfirmed":0,"unknowns_created":0,"contradictions_created":0,"evidence_extracted":0,"current_source_name":"","percent_complete":0,"latest_message":"No collection has started.","warnings":[],"errors":[]}

def write_state(state: dict[str, Any]) -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return state

def mark_stale_interrupted(max_age_seconds: int = 1800) -> dict[str, Any]:
    state = read_state(raw=True)
    if state.get("status") in IN_PROGRESS_STATES and state.get("started_at"):
        try:
            started = datetime.fromisoformat(str(state["started_at"]).replace("Z", "+00:00"))
            if (datetime.now(UTC) - started).total_seconds() > max_age_seconds:
                return write_state({**state, "status":"interrupted", "completed_at":datetime.now(UTC).isoformat(timespec="seconds"), "latest_message":"Collection interrupted or stale after application restart.", "percent_complete":100})
        except ValueError:
            pass
    return state

def read_state(raw: bool = False) -> dict[str, Any]:
    if not STATE_PATH.exists():
        return default_state()
    try:
        return {**default_state(), **json.loads(STATE_PATH.read_text(encoding="utf-8"))}
    except json.JSONDecodeError:
        return {**default_state(), "status":"failed", "latest_message":"Progress state file is unreadable."}

def start_state(total: int, *, run_id: str | None = None, canonical_enterprise_id: str | None = None, enterprise_display_name: str | None = None, profile_id: str | None = None, collection_mode: str | None = None, collection_pass: str | None = None, status: str = "starting") -> dict[str, Any]:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    return write_state({**default_state(), "run_id": run_id or uuid.uuid4().hex[:12], "started_at": now, "status":status, "canonical_enterprise_id": canonical_enterprise_id or "", "enterprise_display_name": enterprise_display_name or "", "profile_id": profile_id or "", "collection_mode": collection_mode or "", "collection_pass": collection_pass or "", "sources_total": total, "latest_message":"Collection started."})

def update_state(**updates: Any) -> dict[str, Any]:
    state = {**read_state(), **updates}
    state["percent_complete"] = percent_complete(int(state.get("sources_attempted") or 0), int(state.get("sources_total") or 0))
    return write_state(state)

def complete_state(status: str = "completed", message: str = "Collection completed.", **updates: Any) -> dict[str, Any]:
    return update_state(status=status, completed_at=datetime.now(UTC).isoformat(timespec="seconds"), percent_complete=100, latest_message=message, **updates)
