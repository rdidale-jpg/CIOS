"""Domain objects for Flora's minimal durable Enterprise Intelligence memory."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from datetime import UTC, datetime
from typing import Any

_SPECULATIVE = re.compile(r"\b(may|might|could|possibly|probably|likely|appears to|suggests|indicates|opportunity|hypothesis)\b", re.I)
_RECOMMEND = re.compile(r"\b(should|recommend|recommended|next action|must engage|proposal|pitch|sell|pursue)\b", re.I)
_MULTI_FACT = re.compile(r"\b(and|while|but|because|therefore)\b", re.I)


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def normalise(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def stable_observation_fingerprint(enterprise_id: str, observation_type: str, statement: str, attribute: str) -> str:
    return hashlib.sha256("|".join([normalise(enterprise_id), normalise(observation_type), normalise(statement), normalise(attribute)]).encode()).hexdigest()


def stable_observation_id(fingerprint: str) -> str:
    return f"OBS-{fingerprint[:16].upper()}"


@dataclass
class Observation:
    enterprise_id: str
    observation_type: str
    atomic_statement: str
    observation_date: str
    collection_date: str
    affected_attribute: str
    confidence: int
    supporting_evidence_ids: tuple[str, ...] = ()
    evidence_publication_date: str | None = None
    provenance_type: str = "evidence-backed"
    freshness: str = "current"
    last_confirmed_date: str | None = None
    lifecycle_state: str = "accepted"
    importance: int | None = None
    commercial_value: int | None = None
    contradiction_state: str = "none"
    contradicted_by_observation_ids: tuple[str, ...] = ()
    supersedes_observation_id: str | None = None
    retired_at: str | None = None
    human_provenance: dict[str, Any] = field(default_factory=dict)
    observation_id: str | None = None
    observation_fingerprint: str | None = None
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    def __post_init__(self) -> None:
        self.supporting_evidence_ids = tuple(dict.fromkeys(str(e) for e in self.supporting_evidence_ids if e))
        self.contradicted_by_observation_ids = tuple(dict.fromkeys(str(o) for o in self.contradicted_by_observation_ids if o))
        self.confidence = max(0, min(100, int(self.confidence)))
        if self.provenance_type == "evidence-backed" and not self.supporting_evidence_ids:
            raise ValueError("Evidence-backed Observations require at least one accepted Evidence ID.")
        if self.provenance_type == "human-supplied" and not self.human_provenance:
            raise ValueError("Human-supplied Observations require explicit human provenance metadata.")
        if _SPECULATIVE.search(self.atomic_statement):
            raise ValueError("Observation contains speculative language that belongs in a Hypothesis.")
        if _RECOMMEND.search(self.atomic_statement):
            raise ValueError("Observation contains Recommendation or action language.")
        if len(re.findall(r"[;:]", self.atomic_statement)) > 0 or (_MULTI_FACT.search(self.atomic_statement) and len(re.findall(r"\b[A-Z][A-Za-z0-9-]+\b", self.atomic_statement)) > 1):
            raise ValueError("Observation statement is not atomic.")
        self.last_confirmed_date = self.last_confirmed_date or self.observation_date
        self.observation_fingerprint = self.observation_fingerprint or stable_observation_fingerprint(self.enterprise_id, self.observation_type, self.atomic_statement, self.affected_attribute)
        self.observation_id = self.observation_id or stable_observation_id(self.observation_fingerprint)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Observation":
        row = dict(row)
        for key in ("supporting_evidence_ids", "contradicted_by_observation_ids"):
            row[key] = tuple(row.get(key) or ())
        return cls(**row)


@dataclass
class EnterpriseModelAttribute:
    domain: str
    attribute: str
    current_value: str | None
    confidence: int
    last_observed_date: str
    freshness: str
    observation_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    provenance_type: str
    contradiction_state: str = "none"
    conflicting_observation_ids: tuple[str, ...] = ()
    prior_values: tuple[dict[str, Any], ...] = ()
    updated_at: str = field(default_factory=now_iso)


@dataclass
class EnterpriseUnknown:
    unknown_id: str
    enterprise_id: str
    question: str
    affected_domain: str
    priority: str = "medium"
    evidence_required: tuple[str, ...] = ()
    status: str = "open"
    related_observation_ids: tuple[str, ...] = ()
    review_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnterpriseModel:
    enterprise_id: str
    attributes: dict[str, EnterpriseModelAttribute] = field(default_factory=dict)
    unknowns: dict[str, EnterpriseUnknown] = field(default_factory=dict)
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {"enterprise_id": self.enterprise_id, "created_at": self.created_at, "updated_at": self.updated_at, "attributes": {k: asdict(v) for k, v in self.attributes.items()}, "unknowns": {k: asdict(v) for k, v in self.unknowns.items()}}

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "EnterpriseModel":
        return cls(row["enterprise_id"], {k: EnterpriseModelAttribute(**v) for k, v in row.get("attributes", {}).items()}, {k: EnterpriseUnknown(**v) for k, v in row.get("unknowns", {}).items()}, row.get("created_at", now_iso()), row.get("updated_at", now_iso()))


@dataclass(frozen=True)
class ModelUpdateResult:
    enterprise_id: str
    observation_id: str
    affected_attribute: str
    action: str
    contradiction: bool = False
    unknown_created: bool = False
