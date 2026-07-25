"""Governed package-contract detection at Flora's archive receipt boundary.

Detection is deliberately read-only.  Callers must run ``inspect_zip_inventory``
first and pass its result here; this keeps path validation and archive safety in
one place rather than growing a second ZIP safety implementation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from io import BytesIO
from io import StringIO
import csv
import json
from types import MappingProxyType
from typing import Any, Mapping
import zipfile

from .models import FileInventoryItem


class PackageContract(str, Enum):
    BLUEPRINT = "Blueprint Package"
    GOVERNED_INDUSTRY_TWIN = "Governed Industry Twin Package"
    RESEARCH_WORKSPACE = "Research Workspace"
    INDUSTRY_TWIN_DELTA = "Industry Twin Delta"
    UNKNOWN = "Unknown Package"


@dataclass(frozen=True)
class ArchiveSummary:
    file_count: int
    total_uncompressed_bytes: int
    root_members: tuple[str, ...]


@dataclass(frozen=True)
class PromotableArtefact:
    artefact_type: str
    path: str
    promotable: bool
    reason: str


@dataclass(frozen=True)
class PackageInspection:
    contract_type: PackageContract
    confidence: str
    manifest_filename: str | None
    package_identifier: str | None
    package_version: str | None
    package_metadata: Mapping[str, Any]
    detected_assets: tuple[str, ...]
    promotable_artefacts: tuple[PromotableArtefact, ...]
    warnings: tuple[str, ...]
    blocking_errors: tuple[str, ...]
    archive_summary: ArchiveSummary
    inspection_details: Mapping[str, Any] = MappingProxyType({})

    @property
    def promotion_eligible(self) -> bool:
        return not self.blocking_errors and any(a.promotable for a in self.promotable_artefacts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_type": self.contract_type.value,
            "confidence": self.confidence,
            "manifest_filename": self.manifest_filename,
            "package_identifier": self.package_identifier,
            "package_version": self.package_version,
            "package_metadata": _thaw(self.package_metadata),
            "detected_assets": list(self.detected_assets),
            "promotable_artefacts": [asdict(item) for item in self.promotable_artefacts],
            "warnings": list(self.warnings),
            "blocking_errors": list(self.blocking_errors),
            "archive_summary": {
                "file_count": self.archive_summary.file_count,
                "total_uncompressed_bytes": self.archive_summary.total_uncompressed_bytes,
                "root_members": list(self.archive_summary.root_members),
            },
            **_thaw(self.inspection_details),
            "promotion_eligible": self.promotion_eligible,
        }


_BLUEPRINT = "blueprint_manifest.json"
_MISSION = "mission_state.json"
_RESTART = "deterministic_restart_state.json"
_DELTA = "industry_twin_delta_for_Flora.json"
_DELTA_NAMES = {_DELTA.lower(), "industry-twin-delta-for-flora.json"}
_WORKSPACE_MARKERS = {"mission_state.json", "deterministic_restart_state.json", "workspace_manifest.json"}


class PackageContractDetector:
    """Detect a contract using exact, case-sensitive root member names only."""

    def detect(self, content: bytes, inventory: tuple[FileInventoryItem, ...]) -> PackageInspection:
        # Inventory is proof that the shared safe archive inspection has run.
        if not inventory:
            raise ValueError("A safely inspected archive inventory is required")
        paths = tuple(item.path for item in inventory)
        prefix, root_error = _select_package_root(content, paths)
        logical = {path: path[len(prefix):] if prefix and path.startswith(prefix) else path for path in paths}
        logical_paths = tuple(logical.values())
        roots = tuple(sorted(path for path in logical_paths if "/" not in path))
        root_set = set(roots)

        blueprint = _BLUEPRINT in root_set
        governed_manifests = [p for p in logical_paths if _is_governed_manifest_path(p)]
        deltas = [p for p in logical_paths if _is_delta_path(p)]
        workspace = any(p.rsplit("/", 1)[-1].lower() in _WORKSPACE_MARKERS for p in logical_paths)
        governed = bool(governed_manifests)
        # Governed metadata outranks workspace mechanics commonly retained in a
        # final package; Blueprint plus governed metadata remains truly ambiguous.
        matches = [name for name, yes in (("Blueprint Package", blueprint), ("Governed Industry Twin Package", governed), ("Research Workspace", workspace and not governed)) if yes]
        if len(matches) > 1:
            contract, manifest = PackageContract.UNKNOWN, None
        elif blueprint:
            contract, manifest = PackageContract.BLUEPRINT, _BLUEPRINT
        elif governed:
            contract = PackageContract.GOVERNED_INDUSTRY_TWIN
            manifest = governed_manifests[0]
        elif workspace:
            contract = PackageContract.RESEARCH_WORKSPACE
            manifest = next(p for p in logical_paths if p.rsplit("/", 1)[-1].lower() in _WORKSPACE_MARKERS)
        elif deltas:
            contract, manifest = PackageContract.INDUSTRY_TWIN_DELTA, deltas[0]
        else:
            contract, manifest = PackageContract.UNKNOWN, None

        metadata: dict[str, Any] = {}
        warnings: list[str] = []
        errors: list[str] = []
        if manifest:
            try:
                with zipfile.ZipFile(BytesIO(content)) as archive:
                    physical_manifest = next((p for p, lp in logical.items() if lp == manifest), manifest)
                    parsed = json.loads(archive.read(physical_manifest).decode("utf-8"))
                if isinstance(parsed, dict):
                    metadata = parsed
                else:
                    errors.append(f"{manifest} must contain a JSON object.")
            except (KeyError, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile):
                errors.append(f"{manifest} is not valid JSON.")

        assets, artefacts = self._assets(root_set, logical_paths)
        if deltas and not any(a.artefact_type == "Industry Twin Delta" for a in artefacts):
            artefacts.append(PromotableArtefact("Industry Twin Delta", deltas[0], True, "Routes through the existing Blueprint candidate adapter"))
            assets.append("Industry Twin Delta")
        if len(matches) > 1:
            errors.append("Ambiguous package contract: " + ", ".join(matches) + ".")
        details, identity_errors, identity_warnings = _inspection_details(content, logical, governed_manifests, manifest, deltas, logical_paths, metadata)
        errors.extend(identity_errors)
        warnings.extend(identity_warnings)
        if root_error:
            errors.append(root_error)
        if contract in {PackageContract.GOVERNED_INDUSTRY_TWIN, PackageContract.RESEARCH_WORKSPACE}:
            for label, value in (("knowledge graph", details["graph_location"]), ("graph validation", details["graph_validation_location"]), ("evidence register", details["evidence_register_location"])):
                if not value:
                    warnings.append(f"Optional {label} artefact was not supplied.")
        if contract is PackageContract.GOVERNED_INDUSTRY_TWIN and not deltas:
            errors.append("Governed Industry Twin package is missing an Industry Twin Delta.")
        if contract is PackageContract.UNKNOWN:
            errors.append("Unknown package contract.")
            warnings.append("Package inspected. No canonical changes performed.")
        return PackageInspection(
            contract, "high" if manifest else "none", manifest,
            details.get("mission_identifier") or _metadata_value(metadata, "package_id", "workspace_id", "delta_id", "mission_id"),
            details.get("package_version") or _metadata_value(metadata, "package_version", "workspace_version", "delta_version", "version"),
            _freeze(metadata), tuple(assets), tuple(artefacts), tuple(warnings), tuple(errors),
            ArchiveSummary(len(inventory), sum(item.size_bytes for item in inventory), tuple(sorted(paths))), _freeze(details),
        )

    @staticmethod
    def _assets(root_set: set[str], paths: tuple[str, ...]) -> tuple[list[str], list[PromotableArtefact]]:
        assets: list[str] = []
        artefacts: list[PromotableArtefact] = []
        exact = {
            _DELTA: ("Industry Twin Delta", True, "Routes through the Blueprint candidate adapter"),
            "executive_intelligence.json": ("Executive Intelligence", True, "Supported promotable artefact"),
            "evidence.json": ("Evidence", True, "Supported promotable artefact"),
            "research_queue.json": ("Research Queue", False, "Research execution state is lineage only"),
            _RESTART: ("Restart State", False, "Research execution state is lineage only"),
            "checkpoint_metadata.json": ("Checkpoint Metadata", False, "Checkpoint metadata is lineage only"),
        }
        for path in paths:
            name = path.rsplit("/", 1)[-1]
            if name in exact:
                kind, promotable, reason = exact[name]
                if kind not in assets:
                    assets.append(kind)
                artefacts.append(PromotableArtefact(kind, path, promotable, reason))
        if _MISSION in root_set and "Research Workspace" not in assets:
            assets.insert(0, "Research Workspace")
        return assets, artefacts


def _single_root_prefix(paths: tuple[str, ...]) -> str:
    """Return a sole wrapper directory, but never collapse a modular root."""
    first = {p.split("/", 1)[0] for p in paths}
    return next(iter(first)) + "/" if len(first) == 1 and all("/" in p for p in paths) else ""


def _is_governed_manifest_path(path: str) -> bool:
    low = path.lower()
    name = low.rsplit("/", 1)[-1]
    return name in {"00_manifest.json", "manifest.json", "package_manifest.json", "package-manifest.json"} or (low.startswith("flora/") and name in {"promotion-manifest.json", "promotion_manifest.json"})


def _is_delta_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1].lower().removesuffix(".json")
    normalised = name.replace("-", "_")
    return normalised in {"industry_twin_delta", "industry_twin_delta_for_flora"}


def _select_package_root(content: bytes, paths: tuple[str, ...]) -> tuple[str, str | None]:
    """Select no wrapper or one nested wrapper; reject two plausible packages."""
    candidates: set[str] = set()
    for path in paths:
        parts = path.split("/")
        if _is_governed_manifest_path(path) or _is_delta_path(path):
            candidates.add(parts[0] + "/" if len(parts) > 1 and parts[0].lower() not in {"flora", "twins", "machine-inspectable", "registers", "workspace"} else "")
    if len(candidates) > 1:
        shown = ", ".join(repr(p or "archive root") for p in sorted(candidates))
        return "", f"Ambiguous nested package roots: {shown}."
    return (next(iter(candidates)) if candidates else _single_root_prefix(paths)), None


def _inspection_details(
    content: bytes,
    logical: dict[str, str],
    governed_manifests: list[str],
    manifest: str | None,
    deltas: list[str],
    paths: tuple[str, ...],
    metadata: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Resolve governed metadata without allowing lower-precedence sources to overwrite it."""
    def find(*terms: str) -> str | None:
        return next((p for p in paths if all(term in p.lower() for term in terms)), None)

    graph_validation = find("graph", "validation")
    locations = {
        "graph_location": next((p for p in paths if "graph" in p.lower() and "validation" not in p.lower()), None),
        "graph_validation_location": graph_validation,
        "evidence_register_location": find("evidence"),
        "unknown_register_location": find("unknown"),
        "contradiction_register_location": find("contradiction"),
        "restart_state_location": next((p for p in paths if "restart" in p.lower()), None),
    }
    promotion = next((p for p in governed_manifests if p.lower().endswith("promotion-manifest.json")), None)
    authoritative = [p for p in governed_manifests if p != promotion]
    # Contract precedence: promotion manifest, Delta, restart state.  Other
    # governed manifests are retained after the promotion manifest for legacy
    # producers that have no promotion metadata.
    ordered = ([promotion] if promotion else []) + authoritative + deltas + ([locations["restart_state_location"]] if locations["restart_state_location"] else [])
    documents: dict[str, Any] = {}
    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            for inspected_path in dict.fromkeys([p for p in ordered + list(locations.values()) if p]):
                physical = next((p for p, lp in logical.items() if lp == inspected_path), None)
                if not physical:
                    continue
                try:
                    documents[inspected_path] = json.loads(archive.read(physical).decode("utf-8"))
                except (KeyError, json.JSONDecodeError, UnicodeDecodeError):
                    documents[inspected_path] = None
            # Counts and collection discovery need all governed JSON documents,
            # not only identity documents.  Contents are never added to logs.
            for physical, inspected_path in logical.items():
                if inspected_path in documents or not inspected_path.casefold().endswith(".json"):
                    continue
                try:
                    documents[inspected_path] = json.loads(archive.read(physical).decode("utf-8"))
                except (KeyError, json.JSONDecodeError, UnicodeDecodeError):
                    documents[inspected_path] = None
            for physical, inspected_path in logical.items():
                if inspected_path.casefold().endswith(".csv"):
                    try:
                        documents[inspected_path] = list(csv.DictReader(StringIO(archive.read(physical).decode("utf-8-sig"))))
                    except (KeyError, UnicodeDecodeError, csv.Error):
                        documents[inspected_path] = None
    except zipfile.BadZipFile:
        pass

    fields = {
        "package_profile": ("package_profile", "profile", "profile_version", "schema_profile"),
        "mission_identifier": ("mission_id", "mission_identifier", "missionId", "package_id"),
        "twin_title": ("industry_twin_title", "twin_title", "industry_title", "package_title", "title", "industry", "name"),
        "twin_type": ("twin_type", "type"),
        "package_version": ("package_version", "version", "delta_version"),
        "research_state": ("research_state", "research_status", "mission_state", "state"),
        "decision_maturity": ("decision_maturity", "decision_readiness", "maturity"),
    }
    resolved: dict[str, Any] = {}
    sources: dict[str, str] = {}
    conflicts: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    for field, keys in fields.items():
        found: list[tuple[str, str]] = []
        for path in ordered:
            value = _deep_metadata_value(documents.get(path), *keys)
            if value not in (None, ""):
                found.append((str(value), path))
        if found:
            resolved[field], sources[field] = found[0]
            distinct = {v.strip().casefold() for v, _ in found}
            if len(distinct) > 1:
                item = {"field": field, "values": [{"value": v, "source_path": p} for v, p in found]}
                conflicts.append(item)
                errors.append(f"Conflicting {field.replace('_', ' ')}: " + "; ".join(f"{v!r} in {p}" for v, p in found) + ".")
    for field in fields:
        resolved.setdefault(field, None)
    if deltas and len(deltas) > 1:
        delta_ids = [(_deep_metadata_value(documents.get(p), "mission_id", "mission_identifier", "package_id"), p) for p in deltas]
        if len({str(v).casefold() for v, _ in delta_ids if v}) > 1:
            errors.append("Multiple Industry Twin Delta artefacts disagree.")
    required_refs = _referenced_paths(documents.get(manifest))
    unresolved = [ref for ref in required_refs if ref not in paths]
    if unresolved:
        errors.append("Required referenced files are missing: " + ", ".join(unresolved) + ".")
    if manifest and not resolved.get("mission_identifier"):
        warnings.append("Optional mission identifier metadata was not supplied.")
    profile = resolved.get("package_profile") or ("industry-twin-v1" if manifest and deltas else None)
    delta = documents.get(deltas[0]) if deltas else None
    records = delta.get("records") if isinstance(delta, dict) else None
    promotable_objects = [str(row.get("external_id")) for row in records or [] if isinstance(row, dict) and row.get("external_id")] if isinstance(records, list) else []
    counts = _asset_counts(documents, paths, locations)
    status_doc = documents.get(graph_validation)
    status = (status_doc.get("status") or status_doc.get("validation_status")) if isinstance(status_doc, dict) else ("unreadable" if graph_validation else None)
    details = {
        "package_contract": PackageContract.GOVERNED_INDUSTRY_TWIN.value if manifest and deltas else None,
        "package_profile": profile,
        **resolved,
        "industry_or_package_title": resolved.get("twin_title"),
        "selected_package_root": next((physical[:-len(lp)] for physical, lp in logical.items() if physical != lp), ""),
        "manifest_location": manifest, "delta_location": deltas[0] if deltas else None,
        **locations, "graph_validation_status": status,
        "unknown_count": counts.get("Unknowns"), "contradiction_count": counts.get("Contradictions"),
        "asset_counts": counts, "metadata_sources": sources, "metadata_conflicts": conflicts,
        "recognition_evidence": [p for p in (manifest, deltas[0] if deltas else None, locations["graph_location"]) if p],
        "files_used_for_identity": list(dict.fromkeys(sources.values())), "unresolved_references": unresolved,
        "promotable_objects": promotable_objects, "package_inventory": list(sorted(logical)),
        "excluded_research_only_objects": [p for p in paths if any(t in p.lower() for t in ("restart", "checkpoint", "research_queue", "mission_state"))],
    }
    return details, errors, warnings


def _deep_metadata_value(document: Any, *keys: str) -> Any:
    if not isinstance(document, dict):
        return None
    for key in keys:
        if document.get(key) not in (None, ""):
            return document[key]
    for container in ("metadata", "package", "identity", "industry_twin", "twin", "mission", "delta"):
        value = document.get(container)
        found = _deep_metadata_value(value, *keys)
        if found not in (None, ""):
            return found
    # Governed producers may add a named envelope.  Search remaining mappings
    # in document order while preserving the source-document precedence above.
    for value in document.values():
        if isinstance(value, dict):
            found = _deep_metadata_value(value, *keys)
            if found not in (None, ""):
                return found
    return None


def _referenced_paths(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return []
    result: list[str] = []
    for key, value in document.items():
        low = str(key).lower()
        if ("path" in low or low in {"files", "artefacts", "artifacts"}) and isinstance(value, str):
            result.append(value.lstrip("./"))
        elif isinstance(value, list) and ("file" in low or "artefact" in low or "artifact" in low):
            result.extend(str(v).lstrip("./") for v in value if isinstance(v, str))
    return result


def _asset_counts(documents: dict[str, Any], paths: tuple[str, ...], locations: dict[str, str | None]) -> dict[str, int]:
    aliases = {"industry": "Industry Twins", "enterprise": "Enterprise Twins", "market_participant": "Market Participant Twins", "flow": "Flow Twins", "opportunity": "Opportunity Twins", "control_body": "Control Bodies", "procurement_route": "Procurement Routes", "transformation_programme": "Transformation Programmes", "evidence": "Evidence records", "unknown": "Unknowns", "contradiction": "Contradictions"}
    counts: dict[str, int] = {}
    seen: set[tuple[str, str]] = set()
    category_labels = {"industry_twins": "Industry Twins", "enterprise_twins": "Enterprise Twins", "market_participant_twins": "Market Participant Twins", "opportunity_twins": "Opportunity Twins", "flow_twins": "Flow Twins"}
    for path, doc in documents.items():
        primary = doc.get("primary_objects") if isinstance(doc, dict) else None
        if not isinstance(primary, dict) and isinstance(doc, dict) and isinstance(doc.get("delta"), dict):
            primary = doc["delta"].get("primary_objects")
        if isinstance(primary, dict):
            for category, declaration in primary.items():
                values = declaration
                if isinstance(declaration, dict):
                    values = next((declaration[key] for key in ("ids", "identifiers", "references", "objects", "items") if key in declaration), [])
                if isinstance(values, list) and category in category_labels:
                    counts[category_labels[category]] = max(counts.get(category_labels[category], 0), len(values))
        rows = doc if isinstance(doc, list) else next((doc.get(k) for k in ("records", "items", "nodes", "entries", "unknowns", "contradictions", "enterprise_twins", "market_participant_twins", "opportunity_twins", "flow_twins") if isinstance(doc, dict) and isinstance(doc.get(k), list)), None)
        if not isinstance(rows, list):
            continue
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            kind = str(row.get("twin_type") or row.get("object_type") or row.get("record_class") or "").lower().replace(" ", "_").replace("-", "_")
            label = aliases.get(kind)
            if label and (path, str(row.get("id") or row.get("external_id") or i)) not in seen:
                counts[label] = counts.get(label, 0) + 1
                seen.add((path, str(row.get("id") or row.get("external_id") or i)))
        name = path.lower()
        normal_name = name.replace("-", "_")
        for token, label in (("enterprise_twin", "Enterprise Twins"), ("market_participant_twin", "Market Participant Twins"), ("opportunity_twin", "Opportunity Twins"), ("flow_twin", "Flow Twins")):
            if token in normal_name:
                counts[label] = max(counts.get(label, 0), len(rows))
        if "unknown" in name:
            counts["Unknowns"] = len(rows)
        if "contradiction" in name:
            counts["Contradictions"] = len(rows)
        if "evidence" in name:
            counts["Evidence records"] = len(rows)
        if path == locations.get("graph_location"):
            if isinstance(doc, dict) and isinstance(doc.get("nodes"), list):
                counts["graph nodes"] = len(doc["nodes"])
            if isinstance(doc, dict) and isinstance(doc.get("edges"), list):
                counts["graph edges"] = len(doc["edges"])
    return counts

def _register_count(document: Any) -> int | None:
    """Count common register shapes without inventing producer-specific semantics."""
    if isinstance(document, list):
        return len(document)
    if isinstance(document, dict):
        for key in ("records", "items", "unknowns", "contradictions", "entries"):
            if isinstance(document.get(key), list):
                return len(document[key])
    return None


def _metadata_value(metadata: dict[str, Any], *keys: str) -> str | None:
    return next((str(metadata[k]) for k in keys if metadata.get(k) not in (None, "")), None)


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_thaw(v) for v in value]
    return value
