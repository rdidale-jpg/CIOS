"""JSONL persistence for local Flora live evidence receipts."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path(".flora_pilot/live_evidence/live_evidence.jsonl")
DEFAULT_DIAGNOSTICS_PATH = Path(".flora_pilot/live_evidence/source_diagnostics.jsonl")


def _normalise(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def evidence_fingerprint(item: dict[str, Any]) -> str:
    """Return a stable fingerprint for a live evidence object.

    The fingerprint deliberately excludes volatile fields such as extraction timestamps
    and generated evidence IDs so repeated collection of unchanged source content does
    not create duplicate persisted evidence.
    """
    parts = [
        _normalise(item.get("organisation")),
        _normalise(item.get("source_id") or item.get("source_url")),
        _normalise(item.get("snippet")),
        _normalise(item.get("commercial_condition")),
        _normalise(item.get("likely_capability")),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def load_evidence_fingerprints(path: Path = DEFAULT_PATH) -> set[str]:
    return {evidence_fingerprint(item) for item in read_jsonl(path)}


def unique_evidence(items: list[dict[str, Any]], path: Path = DEFAULT_PATH) -> tuple[list[dict[str, Any]], int, set[str]]:
    """Filter out evidence already persisted at path or repeated in this batch."""
    fingerprints = load_evidence_fingerprints(path)
    new_items: list[dict[str, Any]] = []
    duplicate_count = 0
    for item in items:
        fingerprint = evidence_fingerprint(item)
        if fingerprint in fingerprints:
            duplicate_count += 1
            continue
        item.setdefault("evidence_fingerprint", fingerprint)
        fingerprints.add(fingerprint)
        new_items.append(item)
    return new_items, duplicate_count, fingerprints


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
