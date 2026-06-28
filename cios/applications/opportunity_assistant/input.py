"""Input loading and evidence mapping for the Opportunity Assistant."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cios.core import ConfidenceLevel, Evidence, EvidenceKind

SAMPLE_PATH = Path(__file__).with_name("sample_opportunity.json")


def load_sample_opportunity(path: Path = SAMPLE_PATH) -> dict[str, Any]:
    """Load the structured sample opportunity JSON."""

    return json.loads(path.read_text(encoding="utf-8"))


def create_evidence(source: dict[str, Any]) -> list[Evidence]:
    """Map structured opportunity source evidence into core evidence records."""

    return [
        Evidence(
            title=item["title"],
            kind=EvidenceKind.DATA,
            source=item["source"],
            summary=item.get("summary"),
            confidence=ConfidenceLevel.HIGH,
        )
        for item in source.get("evidence", [])
    ]
