"""Observation-backed Enterprise Model persistence for the Flora pilot.

The file-backed repositories intentionally support a single writer per memory
store. The Observation ledger is the durable history; Enterprise Model snapshots
are derived projections that can be rebuilt later from stored observations and
projection rules.
"""
from __future__ import annotations

import hashlib, json, os, re, tempfile
from dataclasses import dataclass, field, asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

OBSERVATION_SCHEMA_VERSION = 1
ENTERPRISE_MODEL_SCHEMA_VERSION = 1
FINGERPRINT_SCHEMA_VERSION = 1
SUPPORTED_SCHEMA_VERSIONS = {1}
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,119}$")


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def normalise(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def safe_enterprise_id(value: str) -> str:
    raw = value.strip()
    if "/" in raw or "\\" in raw or ".." in raw:
        raise ValueError("enterprise_id must be a stable safe internal identifier")
    normalised = normalise(value).replace(" ", "-")
    cleaned = re.sub(r"[^a-z0-9_-]", "-", normalised)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-_")
    if not cleaned or not _SAFE_ID.fullmatch(cleaned) or ".." in cleaned:
        raise ValueError("enterprise_id must be a stable safe internal identifier")
    return cleaned


def observation_fingerprint(*, enterprise_id: str, domain: str, attribute: str, value: str, effective_date: str | None) -> str:
    payload = {
        "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
        "enterprise_id": safe_enterprise_id(enterprise_id),
        "domain": normalise(domain),
        "attribute": normalise(attribute),
        "value": normalise(value),
        "effective_date": (effective_date or "").strip(),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:32]
    return f"obs-v{FINGERPRINT_SCHEMA_VERSION}-{digest}"


@dataclass
class EnterpriseObservation:
    enterprise_id: str
    domain: str
    attribute: str
    value: str
    effective_date: str | None
    evidence_ids: list[str]
    confidence: float
    observed_at: str = field(default_factory=utc_now)
    schema_version: int = OBSERVATION_SCHEMA_VERSION
    fingerprint_schema_version: int = FINGERPRINT_SCHEMA_VERSION
    observation_id: str = ""
    status: Literal["active", "contradictory"] = "active"
    confidence_history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.enterprise_id = safe_enterprise_id(self.enterprise_id)
        if not self.observation_id:
            self.observation_id = observation_fingerprint(
                enterprise_id=self.enterprise_id, domain=self.domain, attribute=self.attribute,
                value=self.value, effective_date=self.effective_date,
            )
        if not self.confidence_history:
            self.confidence_history.append({"at": self.observed_at, "confidence": self.confidence, "reason": "created"})

    @classmethod
    def from_record(cls, data: dict[str, Any]) -> "EnterpriseObservation":
        if data.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(f"unsupported Observation schema_version: {data.get('schema_version')}")
        return cls(**data)

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EnterpriseUnknown:
    unknown_id: str
    enterprise_id: str
    question: str
    domain: str
    status: Literal["open", "resolved", "superseded", "no_longer_material"] = "open"
    created_at: str = field(default_factory=utc_now)
    review_at: str | None = None
    related_observation_ids: list[str] = field(default_factory=list)


@dataclass
class EnterpriseModel:
    enterprise_id: str
    attributes: dict[str, dict[str, Any]] = field(default_factory=dict)
    contradictions: dict[str, list[str]] = field(default_factory=dict)
    unknowns: list[EnterpriseUnknown] = field(default_factory=list)
    source_observation_ids: list[str] = field(default_factory=list)
    schema_version: int = ENTERPRISE_MODEL_SCHEMA_VERSION
    projection_version: int = 1
    generated_at: str = field(default_factory=utc_now)

    @classmethod
    def from_record(cls, data: dict[str, Any]) -> "EnterpriseModel":
        if data.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(f"unsupported EnterpriseModel schema_version: {data.get('schema_version')}")
        data = dict(data)
        data["unknowns"] = [u if isinstance(u, EnterpriseUnknown) else EnterpriseUnknown(**u) for u in data.get("unknowns", [])]
        return cls(**data)

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


class JsonlObservationLedger:
    """Append-only JSONL Observation ledger; single writer per memory store."""
    def __init__(self, root: Path | str):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "observations.jsonl"

    def append(self, observation: EnterpriseObservation) -> None:
        line = json.dumps(observation.to_record(), sort_keys=True) + "\n"
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line); fh.flush(); os.fsync(fh.fileno())

    def list(self) -> list[EnterpriseObservation]:
        if not self.path.exists(): return []
        rows=[]
        with self.path.open(encoding="utf-8") as fh:
            for number,line in enumerate(fh,1):
                if not line.endswith("\n"):
                    raise ValueError(f"malformed trailing Observation record at line {number}")
                try: data=json.loads(line)
                except json.JSONDecodeError as exc: raise ValueError(f"malformed Observation record at line {number}") from exc
                rows.append(EnterpriseObservation.from_record(data))
        return rows


class FileEnterpriseModelRepository:
    """Atomic file-backed Enterprise Model projection repository; single writer."""
    def __init__(self, root: Path | str):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, enterprise_id: str) -> Path:
        enterprise_id = safe_enterprise_id(enterprise_id)
        path = (self.root / f"{enterprise_id}.json").resolve()
        if self.root.resolve() not in path.parents:
            raise ValueError("enterprise path escapes memory directory")
        return path

    def save(self, model: EnterpriseModel) -> None:
        path = self.path_for(model.enterprise_id)
        payload = json.dumps(model.to_record(), indent=2, sort_keys=True)
        fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(payload); fh.flush(); os.fsync(fh.fileno())
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def load(self, enterprise_id: str) -> EnterpriseModel | None:
        path = self.path_for(enterprise_id)
        if not path.exists(): return None
        return EnterpriseModel.from_record(json.loads(path.read_text(encoding="utf-8")))


class EnterpriseMemoryService:
    def __init__(self, ledger: JsonlObservationLedger, models: FileEnterpriseModelRepository):
        self.ledger=ledger; self.models=models

    def process_evidence(self, *, enterprise_id: str, evidence_id: str, domain: str, attribute: str, value: str, effective_date: str | None, confidence: float) -> EnterpriseObservation:
        new = EnterpriseObservation(enterprise_id, domain, attribute, value, effective_date, [evidence_id], confidence)
        observations = self.ledger.list()
        existing = next((o for o in observations if o.observation_id == new.observation_id), None)
        if existing:
            changed = False
            if evidence_id not in existing.evidence_ids:
                existing.evidence_ids.append(evidence_id); changed = True
            if confidence != existing.confidence:
                existing.confidence_history.append({"at": utc_now(), "confidence": confidence, "reason": f"corroborated by {evidence_id}"})
                existing.confidence = max(existing.confidence, confidence); changed = True
            if changed:
                self._rewrite(observations)
            self._project(existing.enterprise_id)
            return existing
        self.ledger.append(new); self._project(new.enterprise_id); return new

    def _rewrite(self, observations: list[EnterpriseObservation]) -> None:
        fd,tmp=tempfile.mkstemp(prefix=".observations.", suffix=".tmp", dir=self.ledger.root)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as fh:
                for o in observations: fh.write(json.dumps(o.to_record(), sort_keys=True)+"\n")
                fh.flush(); os.fsync(fh.fileno())
            os.replace(tmp,self.ledger.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def _project(self, enterprise_id: str) -> EnterpriseModel:
        obs=[o for o in self.ledger.list() if o.enterprise_id==safe_enterprise_id(enterprise_id)]
        model=EnterpriseModel(enterprise_id=safe_enterprise_id(enterprise_id), source_observation_ids=[o.observation_id for o in obs])
        by_key: dict[str, list[EnterpriseObservation]]={}
        for o in obs: by_key.setdefault(f"{normalise(o.domain)}.{normalise(o.attribute)}", []).append(o)
        for key, items in by_key.items():
            values={normalise(i.value) for i in items}
            if len(values)>1:
                model.contradictions[key]=[i.observation_id for i in items]
                for i in items: i.status="contradictory"
            chosen=max(items, key=lambda i: i.confidence)
            model.attributes[key]={"value": chosen.value, "confidence": chosen.confidence, "observation_ids": [i.observation_id for i in items], "contradiction_state": "contradicted" if len(values)>1 else "none"}
        if any(o.status == "contradictory" for o in obs):
            all_observations = self.ledger.list()
            by_id = {o.observation_id: o for o in obs}
            self._rewrite([by_id.get(o.observation_id, o) for o in all_observations])
        self.models.save(model); return model

    def load_model(self, enterprise_id: str) -> EnterpriseModel | None:
        return self.models.load(enterprise_id)


def render_memory_panel(model: EnterpriseModel) -> str:
    rows = []
    for key, attr in sorted(model.attributes.items()):
        rows.append(f"<li>{key}: {attr['value']} ({attr['contradiction_state']})</li>")
    return "<section id='enterprise-memory'><h2>Enterprise Memory</h2><ul>" + "".join(rows) + "</ul></section>"
