"""Reusable Researcher profile to canonical candidate-field adapter.

The adapter is driven by the versioned machine-readable Twin Object Profile
contract in :mod:`cios.contracts.twin_object_profiles` so Flora does not carry a
second prose-only semantic contract for Researcher packages.
"""
from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def _contract() -> dict[str, Any]:
    return json.loads(files("cios.contracts.twin_object_profiles").joinpath("researcher_v1.json").read_text())


CONTRACT = _contract()
_CLASS_ALIASES = {k: v["canonical_class"] for k, v in CONTRACT["profiles"].items() if "canonical_class" in v}


def adapt_researcher_payload(record_class: str, source: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Return the governed canonical owner class and a lossless payload."""
    canonical_class = _CLASS_ALIASES.get(record_class, record_class)
    profile = CONTRACT["profiles"].get(canonical_class, {})
    p = dict(source)
    p["source_payload"] = dict(source)
    p["transformation_adapter"] = CONTRACT["document_id"]

    aliases: dict[str, Any] = {}
    for target, selectors in CONTRACT["common_fields"].items():
        value = _first_value(source, selectors)
        if value not in (None, "", [], {}):
            aliases[target] = value
    for target, selectors in profile.get("fields", {}).items():
        value = _first_value(source, selectors)
        if value not in (None, "", [], {}):
            aliases[target] = value

    p.update(aliases)
    consumed = set(_flatten_selectors(CONTRACT["common_fields"].values())) | set(_flatten_selectors(profile.get("fields", {}).values()))
    p["mapping_diagnostics"] = {
        "contract_id": CONTRACT["document_id"],
        "contract_status": CONTRACT["status"],
        "source_fields": sorted(source),
        "mapped_fields": sorted(aliases),
        "unmapped_fields": sorted(set(source) - {field.split('.', 1)[0] for field in consumed if field != "$self"}),
    }
    return canonical_class, p


def _first_value(source: dict[str, Any], selectors: list[Any]) -> Any:
    for selector in selectors:
        if selector == "$self":
            return source
        if isinstance(selector, str):
            value = _path_value(source, selector)
        elif isinstance(selector, list):
            values = [_path_value(source, item) for item in selector]
            value = [item for item in values if item not in (None, "", [], {})]
        elif isinstance(selector, dict):
            value = {key: _path_value(source, path) for key, path in selector.items()}
            value = {key: item for key, item in value.items() if item not in (None, "", [], {})}
        else:
            value = None
        if value not in (None, "", [], {}):
            return value
    return None


def _path_value(source: dict[str, Any], path: str) -> Any:
    value: Any = source
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _flatten_selectors(groups) -> list[str]:
    out: list[str] = []
    for selectors in groups:
        for selector in selectors:
            if isinstance(selector, str):
                out.append(selector)
            elif isinstance(selector, list):
                out.extend(str(item) for item in selector)
            elif isinstance(selector, dict):
                out.extend(str(item) for item in selector.values())
    return out
