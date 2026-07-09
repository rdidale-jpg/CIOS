"""Append-only audit log for Blueprint import receipt events."""
from __future__ import annotations

import json
from datetime import UTC, datetime

from cios.applications.flora.storage import data_path, ensure_writable_dir


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class BlueprintImportLedger:
    def __init__(self):
        self.path = data_path("blueprint_import", "audit", "events.jsonl")

    def append(self, event_type: str, payload: dict) -> None:
        ensure_writable_dir(self.path.parent)
        row = {"schema_version": "1.0", "event_type": event_type, "recorded_at": utc_now(), "payload": payload}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()

    def list(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
