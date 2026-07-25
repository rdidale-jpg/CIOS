"""Guidance metadata and safe scope selection for the existing importer.

This module does not receive archives or write canonical state.  It records the
operator's expectation and filters the candidates produced by the governed
validator, retaining dependencies by their external identifiers.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any

from cios.applications.flora.storage import atomic_write_json, data_path

TWIN_TYPES = ("industry", "enterprise", "market_participant", "opportunity", "control_body", "mixed")


def normalise_twin_type(value: Any) -> str:
    return str(value or "").strip().casefold().replace(" ", "_").removesuffix("_twin").replace("mixed_twin_package", "mixed")


@dataclass(frozen=True)
class ImportGuidance:
    import_run_id: str
    expected_type: str
    selected_ids: tuple[str, ...] = ()
    include_dependencies: bool = True

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self); row["selected_ids"] = list(self.selected_ids); return row


class ImportGuidanceRepository:
    def path(self, import_run_id: str): return data_path("blueprint_import", "guidance", f"{import_run_id}.json")
    def save(self, guidance: ImportGuidance) -> ImportGuidance:
        if guidance.expected_type not in TWIN_TYPES: raise ValueError("Select a supported expected Twin type")
        atomic_write_json(self.path(guidance.import_run_id), guidance.to_dict()); return guidance
    def get(self, import_run_id: str) -> ImportGuidance | None:
        path = self.path(import_run_id)
        if not path.exists(): return None
        row=json.loads(path.read_text(encoding="utf-8")); row["selected_ids"]=tuple(row.get("selected_ids", ())); return ImportGuidance(**row)


def candidate_twin_type(candidate: dict[str, Any]) -> str:
    payload=candidate.get("payload") or {}
    declared=normalise_twin_type(payload.get("twin_type") or payload.get("type"))
    if declared in TWIN_TYPES[:-1]: return declared
    record_class=normalise_twin_type(candidate.get("candidate_object_class"))
    aliases={"enterprise":"enterprise", "opportunity":"opportunity", "market_participant":"market_participant", "control_body":"control_body"}
    return aliases.get(record_class, "")


def detect_package_type(candidates: list[dict[str, Any]]) -> str:
    found={candidate_twin_type(c) for c in candidates} - {""}
    return next(iter(found)) if len(found)==1 else ("mixed" if len(found)>1 else "unclear")


def expectation_mismatch(expected: str, detected: str) -> bool:
    return bool(expected and detected != "unclear" and expected != detected and expected != "mixed")


def select_with_dependencies(candidates: list[dict[str, Any]], selected_ids: set[str]) -> tuple[set[str], set[str]]:
    """Return selected candidate IDs and unresolved refs; dependencies close transitively."""
    if not selected_ids: return {str(c["candidate_record_id"]) for c in candidates}, set()
    by_external={str(c.get("original_source_id")):c for c in candidates}
    chosen={str(c["candidate_record_id"]) for c in candidates if str(c.get("original_source_id")) in selected_ids or str((c.get("payload") or {}).get("twin_id")) in selected_ids}
    unresolved=set(); changed=True
    while changed:
        changed=False
        for c in candidates:
            if str(c["candidate_record_id"]) not in chosen: continue
            refs=(c.get("payload") or {}).get("references", c.get("references", []))
            for ref in refs if isinstance(refs, list) else []:
                dep=by_external.get(str(ref))
                if dep and str(dep["candidate_record_id"]) not in chosen: chosen.add(str(dep["candidate_record_id"])); changed=True
                elif not dep: unresolved.add(str(ref))
    return chosen, unresolved
