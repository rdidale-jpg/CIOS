"""Governed package-contract detection at Flora's archive receipt boundary.

Detection is deliberately read-only.  Callers must run ``inspect_zip_inventory``
first and pass its result here; this keeps path validation and archive safety in
one place rather than growing a second ZIP safety implementation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from io import BytesIO
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
_GOVERNED_MANIFESTS = {"00_manifest.json", "promotion-manifest.json"}
_WORKSPACE_MARKERS = {"mission_state.json", "deterministic_restart_state.json", "workspace_manifest.json"}


class PackageContractDetector:
    """Detect a contract using exact, case-sensitive root member names only."""

    def detect(self, content: bytes, inventory: tuple[FileInventoryItem, ...]) -> PackageInspection:
        # Inventory is proof that the shared safe archive inspection has run.
        if not inventory:
            raise ValueError("A safely inspected archive inventory is required")
        paths = tuple(item.path for item in inventory)
        prefix = _single_root_prefix(paths)
        logical = {path: path[len(prefix):] if prefix and path.startswith(prefix) else path for path in paths}
        logical_paths = tuple(logical.values())
        roots = tuple(sorted(path for path in logical_paths if "/" not in path))
        root_set = set(roots)

        blueprint = _BLUEPRINT in root_set
        governed_manifests = [p for p in logical_paths if p.lower() == "00_manifest.json" or p.lower() == "flora/promotion-manifest.json"]
        deltas = [p for p in logical_paths if p.rsplit("/", 1)[-1].lower() in _DELTA_NAMES]
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
        details = _inspection_details(content, logical, manifest, deltas, logical_paths)
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
            _metadata_value(metadata, "package_id", "workspace_id", "delta_id", "mission_id"),
            _metadata_value(metadata, "package_version", "workspace_version", "delta_version", "version"),
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


def _inspection_details(content: bytes, logical: dict[str, str], manifest: str | None, deltas: list[str], paths: tuple[str, ...]) -> dict[str, Any]:
    def find(*terms: str) -> str | None:
        return next((p for p in paths if all(term in p.lower() for term in terms)), None)
    graph_validation = find("graph", "validation")
    status = None
    if graph_validation:
        physical = next(p for p, lp in logical.items() if lp == graph_validation)
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                report = json.loads(archive.read(physical))
            status = report.get("status") or report.get("validation_status") if isinstance(report, dict) else None
        except (KeyError, json.JSONDecodeError, UnicodeDecodeError, zipfile.BadZipFile):
            status = "unreadable"
    return {
        "manifest_location": manifest,
        "delta_location": deltas[0] if deltas else None,
        "graph_location": next((p for p in paths if "graph" in p.lower() and "validation" not in p.lower()), None),
        "graph_validation_location": graph_validation,
        "graph_validation_status": status,
        "evidence_register_location": find("evidence"),
        "unknown_register_location": find("unknown"),
        "contradiction_register_location": find("contradiction"),
        "package_inventory": list(sorted(logical)),
        "excluded_research_only_objects": [p for p in paths if any(t in p.lower() for t in ("restart", "checkpoint", "research_queue", "mission_state"))],
    }


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
