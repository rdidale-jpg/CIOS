"""JSONL/JSON repositories for durable Flora memory.

Flora remains dependency-light in this runtime: no database drivers are introduced.
The migration for this sprint creates file-backed ledgers under .flora_pilot/memory.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from cios.applications.flora.live.store import read_jsonl, write_jsonl
from cios.applications.flora.memory.models import EnterpriseModel, Observation

OBSERVATION_LEDGER_PATH = Path(".flora_pilot/memory/observations.jsonl")
ENTERPRISE_MODEL_DIR = Path(".flora_pilot/memory/enterprise_models")


class ObservationRepository:
    def __init__(self, path: Path = OBSERVATION_LEDGER_PATH):
        self.path = path

    def list(self) -> list[Observation]:
        return [Observation.from_dict(row) for row in read_jsonl(self.path)]

    def get(self, observation_id: str) -> Observation | None:
        return next((o for o in self.list() if o.observation_id == observation_id), None)

    def get_by_fingerprint(self, fingerprint: str) -> Observation | None:
        return next((o for o in self.list() if o.observation_fingerprint == fingerprint), None)

    def save(self, observation: Observation) -> Observation:
        existing = self.get_by_fingerprint(observation.observation_fingerprint or "")
        if existing:
            evidence = tuple(dict.fromkeys([*existing.supporting_evidence_ids, *observation.supporting_evidence_ids]))
            if evidence != existing.supporting_evidence_ids:
                existing.supporting_evidence_ids = evidence
                existing.confidence = max(existing.confidence, observation.confidence)
                existing.updated_at = observation.updated_at
                self._rewrite([existing if o.observation_id == existing.observation_id else o for o in self.list()])
            return existing
        write_jsonl([observation.to_dict()], self.path)
        return observation

    def _rewrite(self, observations: Iterable[Observation]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")
        write_jsonl([o.to_dict() for o in observations], self.path)


class EnterpriseModelRepository:
    def __init__(self, directory: Path = ENTERPRISE_MODEL_DIR):
        self.directory = directory

    def path_for(self, enterprise_id: str) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in enterprise_id.strip()) or "unknown"
        return self.directory / f"{safe}.json"

    def get(self, enterprise_id: str) -> EnterpriseModel:
        path = self.path_for(enterprise_id)
        if not path.exists():
            return EnterpriseModel(enterprise_id=enterprise_id)
        return EnterpriseModel.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def save(self, model: EnterpriseModel) -> EnterpriseModel:
        path = self.path_for(model.enterprise_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(model.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return model
