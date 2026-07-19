"""Read-only Flora Runtime Increment 1 workspace slice.

This module deliberately projects frozen fixture contracts only. It does not create
canonical objects, invoke AI, infer relationships, score opportunities, or write
Enterprise Knowledge.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = ROOT / "schemas" / "flora-runtime" / "v0.1"
FIXTURE_DIR = ROOT / "fixtures" / "flora-runtime" / "increment-1" / "uk-banking"
SUPPORTED_OBJECT_ID = "BK-ENT-001"
SUPPORTED_ENTERPRISE_ID = "lloyds"

CONTRACT_BY_FIXTURE = {
    "focus-object-lloyds.json": "focus-object-projection-v0.1.schema.json",
    "focus-object-incomplete-freshness.json": "focus-object-projection-v0.1.schema.json",
    "relationship-governed.json": "relationship-projection-v0.1.schema.json",
    "relationship-unresolved-target.json": "relationship-projection-v0.1.schema.json",
    "evidence-observation-availability.json": "evidence-observation-availability-v0.1.schema.json",
    "unknown.json": "unknown-response-v0.1.schema.json",
    "contradiction.json": "contradiction-response-v0.1.schema.json",
    "lineage-complete.json": "lineage-response-v0.1.schema.json",
    "lineage-partial.json": "lineage-response-v0.1.schema.json",
    "lineage-access-redacted.json": "lineage-response-v0.1.schema.json",
    "workspace-state.json": "workspace-state-v0.1.schema.json",
    "ingestion-success.json": "ingestion-report-v0.1.schema.json",
    "ingestion-identifier-collision.json": "ingestion-report-v0.1.schema.json",
    "missing-authority-metadata.json": "safe-unavailable-response-v0.1.schema.json",
    "unresolved-identity.json": "safe-unavailable-response-v0.1.schema.json",
    "focus-object-missing-authority.json": "focus-object-projection-v0.1.schema.json",
}

class ContractValidationError(ValueError):
    """Raised when a payload violates the frozen Increment 1 contract."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_ref(ref: str) -> dict[str, Any]:
    if ref.startswith("common-definitions.schema.json#/$defs/"):
        name = ref.rsplit("/", 1)[-1]
        return read_json(SCHEMA_DIR / "common-definitions.schema.json")["$defs"][name]
    raise ContractValidationError(f"unsupported schema ref {ref}")


def validate_contract(payload: Any, schema_name: str, path: str = "$", schema: dict[str, Any] | None = None) -> None:
    """Small schema validator covering the frozen contracts used by Increment 1."""
    schema = schema or read_json(SCHEMA_DIR / schema_name)
    if "$ref" in schema:
        return validate_contract(payload, schema_name, path, _schema_ref(schema["$ref"]))
    if "const" in schema and payload != schema["const"]:
        raise ContractValidationError(f"{path} must equal {schema['const']!r}")
    if "enum" in schema and payload not in schema["enum"]:
        raise ContractValidationError(f"{path} must be one of {schema['enum']!r}")
    types = schema.get("type")
    if types:
        allowed = set(types if isinstance(types, list) else [types])
        ok = (("object" in allowed and isinstance(payload, dict)) or ("array" in allowed and isinstance(payload, list)) or
              ("string" in allowed and isinstance(payload, str)) or ("boolean" in allowed and isinstance(payload, bool)) or
              ("integer" in allowed and isinstance(payload, int) and not isinstance(payload, bool)) or ("number" in allowed and isinstance(payload, (int, float)) and not isinstance(payload, bool)) or
              ("null" in allowed and payload is None))
        if not ok:
            raise ContractValidationError(f"{path} must be {types!r}")
    if isinstance(payload, dict):
        for key in schema.get("required", []):
            if key not in payload:
                raise ContractValidationError(f"{path}.{key} is required")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(payload) - set(props)
            if extra:
                raise ContractValidationError(f"{path} has unsupported properties {sorted(extra)!r}")
        for key, value in payload.items():
            if key in props:
                validate_contract(value, schema_name, f"{path}.{key}", props[key])
    if isinstance(payload, list) and "items" in schema:
        for idx, value in enumerate(payload):
            validate_contract(value, schema_name, f"{path}[{idx}]", schema["items"])


def load_fixture(area: str, name: str) -> dict[str, Any]:
    payload = read_json(FIXTURE_DIR / area / name)
    validate_contract(payload, CONTRACT_BY_FIXTURE[name])
    return payload


def safe_unavailable(reason: str) -> dict[str, Any]:
    name = "unresolved-identity.json" if reason == "identifier_unresolved" else "missing-authority-metadata.json"
    return load_fixture("safe-unavailable", name)


@dataclass(frozen=True)
class RuntimeWorkspace:
    """Composable read-only projection for the single supported Lloyds object."""
    focus_object: dict[str, Any]
    relationships: list[dict[str, Any]]
    evidence_observation_availability: dict[str, Any]
    unknowns: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    lineage: dict[str, Any]
    workspace_state: dict[str, Any]
    safe_unavailable_notices: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "focus_object": self.focus_object,
            "relationships": self.relationships,
            "evidence_observation_availability": self.evidence_observation_availability,
            "unknowns": self.unknowns,
            "contradictions": self.contradictions,
            "lineage": self.lineage,
            "workspace_state": self.workspace_state,
            "safe_unavailable_notices": self.safe_unavailable_notices,
        }


def open_focus_object(object_id: str = SUPPORTED_OBJECT_ID) -> RuntimeWorkspace | dict[str, Any]:
    if object_id not in {SUPPORTED_OBJECT_ID, SUPPORTED_ENTERPRISE_ID}:
        return safe_unavailable("identifier_unresolved")
    notices: list[dict[str, Any]] = []
    def section(area: str, name: str, default: Any) -> Any:
        try:
            return load_fixture(area, name)
        except (OSError, json.JSONDecodeError, ContractValidationError) as exc:
            notices.append({"reason_code": "section_unavailable", "message": f"{name} unavailable: {exc}", "correlation_id": "corr-runtime-section"})
            return default
    return RuntimeWorkspace(
        focus_object=section("valid", "focus-object-lloyds.json", safe_unavailable("missing_authority_metadata")),
        relationships=[section("valid", "relationship-governed.json", {})],
        evidence_observation_availability=section("valid", "evidence-observation-availability.json", {"status": "safe_unavailable"}),
        unknowns=[section("valid", "unknown.json", {})],
        contradictions=[section("valid", "contradiction.json", {})],
        lineage=section("valid", "lineage-complete.json", {"status": "safe_unavailable"}),
        workspace_state=section("valid", "workspace-state.json", {}),
        safe_unavailable_notices=notices,
    )


def validate_fixture_corpus() -> dict[str, list[str]]:
    passed: list[str] = []
    failed: list[str] = []
    for path in sorted(FIXTURE_DIR.glob("*/*.json")):
        try:
            validate_contract(read_json(path), CONTRACT_BY_FIXTURE[path.name])
            passed.append(str(path.relative_to(ROOT)))
        except ContractValidationError:
            failed.append(str(path.relative_to(ROOT)))
    return {"passed": passed, "failed": failed}
