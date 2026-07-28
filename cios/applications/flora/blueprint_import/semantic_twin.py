"""Typed, read-only semantic projection over staged import candidates."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import re


@dataclass(frozen=True)
class SemanticObject:
    record_id: str
    kind: str
    statement: str
    subject: str
    evidence_refs: tuple[str, ...]
    freshness: str
    confidence: str
    governance: str
    source_file: str
    source_location: str
    eligible_conclusion: bool
    exclusion_reason: str = ""


@dataclass(frozen=True)
class SemanticEnterprise:
    identity_key: str
    name: str
    aliases: tuple[str, ...]
    records: tuple[SemanticObject, ...]
    ambiguous: bool = False


@dataclass(frozen=True)
class SemanticTwin:
    objects: tuple[SemanticObject, ...]
    enterprises: tuple[SemanticEnterprise, ...]

    def of_kind(self, kind: str) -> tuple[SemanticObject, ...]:
        return tuple(o for o in self.objects if o.kind == kind)


def assemble_semantic_twin(candidates: list[dict[str, Any]]) -> SemanticTwin:
    objects = tuple(_object(c) for c in candidates)
    groups: dict[str, list[SemanticObject]] = {}
    names: dict[str, str] = {}
    ambiguous: set[str] = set()
    for candidate, obj in zip(candidates, objects):
        payload = candidate.get("payload") or {}
        kind = obj.kind.casefold()
        name = str(payload.get("enterprise_name") or payload.get("organisation_name") or
                   (payload.get("name") if any(x in kind for x in ("entity", "enterprise", "participant")) else "") or "").strip()
        subject = str(payload.get("subject") or "").strip()
        if not name and subject and any(x in kind for x in ("observation", "fact", "hypothesis", "opportun")):
            name = subject
        if not name:
            continue
        supplied_id = str(payload.get("enterprise_id") or payload.get("canonical_id") or "").strip()
        key = supplied_id.casefold() or re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
        if payload.get("identity_status") in {"ambiguous", "unresolved"}:
            key = f"{key}:{obj.record_id}"
            ambiguous.add(key)
        groups.setdefault(key, []).append(obj); names.setdefault(key, name)
    enterprises = tuple(SemanticEnterprise(k, names[k], tuple(sorted({names[k]})), tuple(v), k in ambiguous)
                        for k, v in sorted(groups.items(), key=lambda item: names[item[0]].casefold()))
    return SemanticTwin(objects, enterprises)


def _object(candidate: dict[str, Any]) -> SemanticObject:
    p = candidate.get("payload") or {}
    statement = next((str(p[k]).strip() for k in ("statement", "summary", "description", "title") if p.get(k)), "")
    raw_value = p.get("value")
    metric_complete = raw_value is not None and all(p.get(k) not in (None, "") for k in
        ("metric", "unit", "period", "subject", "source")) and bool(p.get("business_significance") or statement)
    isolated = (not statement and raw_value is not None) or bool(statement and re.fullmatch(r"[\d.,%]+", statement))
    label_only = not statement and bool(p.get("name") or p.get("display_name"))
    evidence = p.get("evidence_refs") or p.get("source_refs") or p.get("sources") or ()
    if isinstance(evidence, str): evidence = (evidence,)
    eligible = bool(statement) and not isolated and not label_only and (raw_value is None or metric_complete)
    reason = ""
    if isolated or (raw_value is not None and not metric_complete): reason = "Metric meaning, unit, period, subject, source or significance is incomplete"
    elif label_only: reason = "Identity or label is not an executive conclusion"
    elif not statement: reason = "No interpretable observation or claim was supplied"
    return SemanticObject(
        str(candidate.get("candidate_record_id") or candidate.get("original_source_id") or "candidate"),
        str(candidate.get("candidate_object_class") or "unclassified"), statement,
        str(p.get("subject") or p.get("enterprise_name") or p.get("organisation_name") or "Twin scope"),
        tuple(map(str, evidence)), str(p.get("freshness") or p.get("observation_date") or "unknown"),
        str(p.get("confidence") or "bounded/unspecified"),
        "governed" if candidate.get("governance_status") in {"governed", "accepted"} else "candidate",
        str(candidate.get("source_file") or "Imported package"), str(candidate.get("source_location") or "not supplied"),
        eligible, reason)
