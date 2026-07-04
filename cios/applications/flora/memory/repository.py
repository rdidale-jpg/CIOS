"""JSONL/JSON repositories for durable Flora memory.

The Observation ledger is the authoritative intelligence history. It is a
single-writer JSONL file: every append writes one complete JSON record, flushes,
and fsyncs. Enterprise Model files are derived projections written via atomic
snapshot replacement and may be rebuilt from the ledger.
"""
from __future__ import annotations

from cios.applications.flora.storage import atomic_write_text, data_path, ensure_parent_writable

import json
import os
import re
from pathlib import Path
from typing import Iterable

from cios.applications.flora.memory.models import EnterpriseModel, Observation
from cios.applications.flora.live.source_registry import canonical_enterprise_id

OBSERVATION_LEDGER_PATH = data_path('memory','observations.jsonl')
ENTERPRISE_MODEL_DIR = data_path('memory','enterprise_models')
_SAFE_ID = re.compile(r"[^a-z0-9_-]+")


def _safe_enterprise_file_id(enterprise_id: str) -> str:
    raw = str(canonical_enterprise_id(enterprise_id) or enterprise_id or "unknown").strip()
    folded = raw.casefold()
    slug = _SAFE_ID.sub("_", folded).strip("._-") or "unknown"
    slug = slug[:48]
    digest = __import__("hashlib").sha256(raw.encode()).hexdigest()[:16]
    return f"{slug}-{digest}"


class ObservationRepository:
    def __init__(self, path: Path | None = None):
        self.path = path or data_path("memory", "observations.jsonl")

    def list(self) -> list[Observation]:
        if not self.path.exists():
            return []
        observations: list[Observation] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Malformed Observation JSONL record at {self.path}:{line_no}") from exc
                if not isinstance(row, dict):
                    raise ValueError(f"Malformed Observation JSONL record at {self.path}:{line_no}")
                observations.append(Observation.from_dict(row))
        return observations

    def get(self, observation_id: str) -> Observation | None:
        return next((o for o in self.list() if o.observation_id == observation_id), None)

    def get_by_fingerprint(self, fingerprint: str) -> Observation | None:
        return next((o for o in self.list() if o.observation_fingerprint == fingerprint), None)

    def save(self, observation: Observation) -> Observation:
        existing = self.get_by_fingerprint(observation.observation_fingerprint or "")
        if existing:
            evidence = tuple(dict.fromkeys([*existing.supporting_evidence_ids, *observation.supporting_evidence_ids]))
            history_changed = evidence != existing.supporting_evidence_ids or observation.confidence != existing.confidence
            if history_changed:
                existing.supporting_evidence_ids = evidence
                existing.confidence = max(existing.confidence, observation.confidence)
                existing.updated_at = observation.updated_at
                self._rewrite([existing if o.observation_id == existing.observation_id else o for o in self.list()])
            return existing
        self._append_record(observation.to_dict())
        return observation

    def _append_record(self, row: dict) -> None:
        ensure_parent_writable(self.path)
        encoded = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())

    def _rewrite(self, observations: Iterable[Observation]) -> None:
        data = "".join(json.dumps(observation.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for observation in observations)
        atomic_write_text(self.path, data)


class EnterpriseModelRepository:
    def __init__(self, directory: Path | None = None):
        self.directory = directory or data_path("memory", "enterprise_models")

    def path_for(self, enterprise_id: str) -> Path:
        path = self.directory / f"{_safe_enterprise_file_id(enterprise_id)}.json"
        resolved_dir = self.directory.resolve()
        resolved_path = path.resolve(strict=False)
        if resolved_dir not in resolved_path.parents:
            raise ValueError("Unsafe enterprise model path")
        return path

    def get(self, enterprise_id: str) -> EnterpriseModel:
        enterprise_id = canonical_enterprise_id(enterprise_id) or enterprise_id
        path = self.path_for(enterprise_id)
        if not path.exists():
            return EnterpriseModel(enterprise_id=enterprise_id)
        return EnterpriseModel.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def save(self, model: EnterpriseModel) -> EnterpriseModel:
        model.enterprise_id = canonical_enterprise_id(model.enterprise_id) or model.enterprise_id
        path = self.path_for(model.enterprise_id)
        data = json.dumps(model.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        atomic_write_text(path, data)
        return model
