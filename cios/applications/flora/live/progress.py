"""Lightweight file-backed live collection progress state."""
from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATE_DIR = Path(".flora_pilot/live_evidence")
STATE_PATH = STATE_DIR / "collection_run_state.json"

def percent_complete(attempted: int, total: int) -> int:
    if total <= 0:
        return 100
    return max(0, min(100, round((attempted / total) * 100)))

def default_state() -> dict[str, Any]:
    return {"run_id":"none","started_at":None,"completed_at":None,"status":"queued","sources_total":0,"sources_attempted":0,"sources_succeeded":0,"sources_failed":0,"evidence_extracted":0,"current_source_name":"","percent_complete":0,"latest_message":"No collection has started."}

def write_state(state: dict[str, Any]) -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return state

def read_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return default_state()
    try:
        return {**default_state(), **json.loads(STATE_PATH.read_text(encoding="utf-8"))}
    except json.JSONDecodeError:
        return {**default_state(), "status":"failed", "latest_message":"Progress state file is unreadable."}

def start_state(total: int) -> dict[str, Any]:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    return write_state({**default_state(), "run_id": uuid.uuid4().hex[:12], "started_at": now, "status":"running", "sources_total": total, "latest_message":"Collection started."})

def update_state(**updates: Any) -> dict[str, Any]:
    state = {**read_state(), **updates}
    state["percent_complete"] = percent_complete(int(state.get("sources_attempted") or 0), int(state.get("sources_total") or 0))
    return write_state(state)

def complete_state(status: str = "completed", message: str = "Collection completed.") -> dict[str, Any]:
    return update_state(status=status, completed_at=datetime.now(UTC).isoformat(timespec="seconds"), percent_complete=100, latest_message=message, sources_attempted=read_state().get("sources_total", 0))
