"""JSONL persistence for local Flora live evidence receipts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path(".flora_pilot/live_evidence/live_evidence.jsonl")
DEFAULT_DIAGNOSTICS_PATH = Path(".flora_pilot/live_evidence/source_diagnostics.jsonl")


def write_jsonl(items: list[dict[str, Any]], path: Path = DEFAULT_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def read_jsonl(path: Path = DEFAULT_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
