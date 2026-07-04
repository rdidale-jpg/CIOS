"""Pilot in-process worker for file-backed Flora collection runs."""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any

from cios.applications.flora.live.progress import TERMINAL_STATES, mark_stale_interrupted, read_state, start_state, update_state
from cios.applications.flora.live.source_registry import collection_scope, enabled_sources, load_collection_profile

_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="flora-collection")
_LOCK = Lock()
_FUTURE: Future | None = None
STALE_AFTER = timedelta(minutes=30)


def start_collection_run(organisation: str, *, profile_id: str | None, collection_mode: str | None, passes: list[str] | None) -> dict[str, Any]:
    """Create durable run state and submit exactly one writer to the pilot worker."""
    global _FUTURE
    mark_stale_interrupted()
    with _LOCK:
        current = read_state()
        if current.get("status") not in TERMINAL_STATES and current.get("run_id") not in {None, "none", ""}:
            return {**current, "duplicate_blocked": True}
        scope = collection_scope(profile_id, mode=collection_mode, passes=passes) if profile_id else None
        selected_passes = passes or (load_collection_profile(profile_id).get("default_passes", []) if profile_id else [])
        sources = enabled_sources(organisation, profile_id=profile_id, passes=passes) if profile_id or passes else enabled_sources(organisation)
        run_id = f"flora-run-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{__import__('uuid').uuid4().hex[:8]}"
        state = start_state(len(sources), run_id=run_id, canonical_enterprise_id=scope.canonical_enterprise_id if scope else "", enterprise_display_name=scope.display_name if scope else organisation, profile_id=profile_id, collection_mode=collection_mode or (scope.collection_mode if scope else "live_plus_seeded"), collection_pass=",".join(selected_passes), status="queued")
        _FUTURE = _EXECUTOR.submit(_run, organisation, profile_id, collection_mode, run_id, selected_passes)
        return state


def _run(organisation: str, profile_id: str | None, collection_mode: str | None, run_id: str, passes: list[str] | None) -> None:
    from cios.applications.flora.live.collect import collect
    try:
        update_state(status="starting", latest_message="Collection worker started.")
        collect(organisation, profile_id=profile_id, collection_mode=collection_mode, run_id=run_id, passes=passes)
    except Exception as exc:  # surfaced to status endpoint
        update_state(status="failed", completed_at=datetime.now(UTC).isoformat(timespec="seconds"), latest_message="Collection failed.", errors=[{"message": str(exc)}])
