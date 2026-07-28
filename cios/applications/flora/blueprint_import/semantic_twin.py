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
    original_id: str = ""
    references: tuple[str, ...] = ()
    sufficiency: str = "unsupported claim"
    permitted_use: str = "not eligible for prominence"


@dataclass(frozen=True)
class SemanticEnterprise:
    identity_key: str
    name: str
    aliases: tuple[str, ...]
    records: tuple[SemanticObject, ...]
    ambiguous: bool = False
    unresolved_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class SemanticTwin:
    objects: tuple[SemanticObject, ...]
    enterprises: tuple[SemanticEnterprise, ...]
    unresolved_references: tuple[str, ...] = ()

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
        # Enterprise identity comes only from the authoritative enterprise
        # collection (or an explicit enterprise object in another package).
        if kind != "enterprise_twin" and not (kind == "entity" and payload.get("enterprise_id")):
            continue
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
    by_id = {o.original_id: o for o in objects if o.original_id}
    enterprises = []
    unresolved_all: set[str] = set()
    for key, seed in sorted(groups.items(), key=lambda item: names[item[0]].casefold()):
        # Subject-labelled observations are attached only after an explicit
        # enterprise identity has established the dossier owner.
        contextual = [o for o in objects if o not in seed and o.subject.casefold() == names[key].casefold()]
        refs = {ref for o in seed + contextual for ref in o.references}
        resolved = [by_id[ref] for ref in refs if ref in by_id]
        missing = sorted(ref for ref in refs if ref not in by_id)
        unresolved_all.update(missing)
        enterprises.append(SemanticEnterprise(key, names[key], tuple(sorted({names[key]})),
                            tuple(dict.fromkeys(seed + contextual + resolved)), key in ambiguous, tuple(missing)))
    return SemanticTwin(objects, tuple(enterprises), tuple(sorted(unresolved_all)))


def _object(candidate: dict[str, Any]) -> SemanticObject:
    p = candidate.get("payload") or {}
    statement = next((str(p[k]).strip() for k in ("statement", "summary", "description", "title") if p.get(k)), "")
    declared_kind = str(candidate.get("candidate_object_class") or "unclassified")
    if declared_kind == "capability_offer" and p.get("name"):
        statement = f"{p['name']} — {statement}" if statement else str(p["name"])
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
    original_id = str(candidate.get("original_source_id") or p.get("id") or "")
    reference_fields = ("evidence_refs", "unknowns", "contradictions", "transformations", "opportunities",
                        "procurement_routes", "buying_centres", "supplier_relationships", "buyer_ids",
                        "affected_objects", "owners", "relationships", "capabilities")
    refs: list[str] = []
    for field in reference_fields:
        value = p.get(field) or ()
        refs.extend([value] if isinstance(value, str) else [str(v) for v in value if not isinstance(v, dict)])
    truth = str(candidate.get("truth_class") or "").casefold()
    kind = declared_kind
    if kind == "unknown": sufficiency, permitted = "unknown", "investigation"
    elif kind == "contradiction": sufficiency, permitted = "unresolved contradiction", "investigation"
    elif "opportun" in kind: sufficiency, permitted = "Opportunity Hypothesis", "commercial hypothesis"
    elif evidence and truth in {"evidence_backed", "fact", "verified"}: sufficiency, permitted = "supported fact", "executive understanding"
    elif evidence: sufficiency, permitted = "supported interpretation", "executive understanding"
    else: sufficiency, permitted = "unsupported claim", "not eligible for prominence"
    return SemanticObject(
        str(candidate.get("candidate_record_id") or candidate.get("original_source_id") or "candidate"),
        str(candidate.get("candidate_object_class") or "unclassified"), statement,
        str(p.get("subject") or p.get("enterprise_name") or p.get("organisation_name") or "Twin scope"),
        tuple(map(str, evidence)), str(p.get("freshness") or p.get("observation_date") or "unknown"),
        str(p.get("confidence") or "bounded/unspecified"),
        "governed" if candidate.get("governance_status") in {"governed", "accepted"} else "candidate",
        str(candidate.get("source_file") or "Imported package"), str(candidate.get("source_location") or "not supplied"),
        eligible, reason, original_id, tuple(dict.fromkeys(refs)), sufficiency, permitted)
