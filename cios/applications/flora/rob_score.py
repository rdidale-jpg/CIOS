"""Local Rob Score storage for Flora evidence-first scoring."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cios.applications.flora.live.store import read_jsonl
from cios.applications.flora.workspace.feedback import runtime_dir

ROB_SCORE_PATH = Path("rob_scores.jsonl")


@dataclass(frozen=True)
class RobScoreRecord:
    organisation: str
    rob_score: int = 0
    rob_score_reason: str = ""
    timestamp: str = ""


def rob_score_path() -> Path:
    return runtime_dir() / ROB_SCORE_PATH


def clamp_rob_score(value: int) -> int:
    return max(-20, min(20, int(value)))


def create_rob_score_record(*, organisation: str, rob_score: int, rob_score_reason: str) -> dict[str, Any]:
    record = {
        "rob_score_id": f"flora-rob-score-{uuid.uuid4().hex}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organisation": organisation,
        "rob_score": clamp_rob_score(rob_score),
        "rob_score_reason": rob_score_reason,
    }
    path = rob_score_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def latest_rob_score(organisation: str) -> RobScoreRecord:
    rows = [r for r in read_jsonl(rob_score_path()) if str(r.get("organisation")) == organisation]
    if not rows:
        return RobScoreRecord(organisation=organisation)
    latest = max(rows, key=lambda r: str(r.get("timestamp") or ""))
    return RobScoreRecord(
        organisation=organisation,
        rob_score=clamp_rob_score(int(latest.get("rob_score") or 0)),
        rob_score_reason=str(latest.get("rob_score_reason") or ""),
        timestamp=str(latest.get("timestamp") or ""),
    )
