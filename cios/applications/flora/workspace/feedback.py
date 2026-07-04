"""Local JSONL feedback and pilot logbook storage for Flora."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cios.applications.flora.storage import data_root, ensure_parent_writable


def runtime_dir() -> Path:
    return data_root()


def _append_jsonl(filename: str, record: dict[str, Any]) -> dict[str, Any]:
    path = runtime_dir() / filename
    ensure_parent_writable(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def create_feedback_record(*, organisation: str, action_text: str, feedback_type: str, optional_comment: str = "", source_page: str = "") -> dict[str, Any]:
    record = {
        "feedback_id": f"flora-feedback-{uuid.uuid4().hex}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organisation": organisation,
        "recommendation_id": action_text[:120],
        "action_text": action_text,
        "feedback_type": feedback_type,
        "optional_comment": optional_comment,
        "source_page": source_page,
    }
    return _append_jsonl("feedback.jsonl", record)


def create_logbook_record(*, biggest_insight: str, biggest_miss: str, action_taken: str, flora_should_learn: str, value_score: int) -> dict[str, Any]:
    score = max(0, min(5, int(value_score)))
    record = {
        "logbook_id": f"flora-logbook-{uuid.uuid4().hex}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "biggest_insight": biggest_insight,
        "biggest_miss": biggest_miss,
        "action_taken": action_taken,
        "flora_should_learn": flora_should_learn,
        "flora_value_score": score,
    }
    return _append_jsonl("logbook.jsonl", record)
