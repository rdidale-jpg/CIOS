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
            "promotion_eligible": self.promotion_eligible,
        }


_BLUEPRINT = "blueprint_manifest.json"
_MISSION = "mission_state.json"
_RESTART = "deterministic_restart_state.json"
_DELTA = "industry_twin_delta_for_Flora.json"


class PackageContractDetector:
    """Detect a contract using exact, case-sensitive root member names only."""

    def detect(self, content: bytes, inventory: tuple[FileInventoryItem, ...]) -> PackageInspection:
        # Inventory is proof that the shared safe archive inspection has run.
        if not inventory:
            raise ValueError("A safely inspected archive inventory is required")
        paths = tuple(item.path for item in inventory)
        roots = tuple(sorted(path for path in paths if "/" not in path))
        root_set = set(roots)

        if _BLUEPRINT in root_set:
            contract, manifest = PackageContract.BLUEPRINT, _BLUEPRINT
        elif _MISSION in root_set or _RESTART in root_set:
            contract = PackageContract.RESEARCH_WORKSPACE
            manifest = _MISSION if _MISSION in root_set else _RESTART
        elif _DELTA in root_set:
            contract, manifest = PackageContract.INDUSTRY_TWIN_DELTA, _DELTA
        else:
            contract, manifest = PackageContract.UNKNOWN, None

        metadata: dict[str, Any] = {}
        warnings: list[str] = []
        errors: list[str] = []
        if manifest:
            try:
                with zipfile.ZipFile(BytesIO(content)) as archive:
                    parsed = json.loads(archive.read(manifest).decode("utf-8"))
                if isinstance(parsed, dict):
                    metadata = parsed
                else:
                    errors.append(f"{manifest} must contain a JSON object.")
            except (KeyError, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile):
                errors.append(f"{manifest} is not valid JSON.")

        assets, artefacts = self._assets(root_set, paths)
        if contract is PackageContract.UNKNOWN:
            errors.append("Unknown package contract.")
            warnings.append("Package inspected. No canonical changes performed.")
        return PackageInspection(
            contract, "high" if manifest else "none", manifest,
            _metadata_value(metadata, "package_id", "workspace_id", "delta_id", "mission_id"),
            _metadata_value(metadata, "package_version", "workspace_version", "delta_version", "version"),
            _freeze(metadata), tuple(assets), tuple(artefacts), tuple(warnings), tuple(errors),
            ArchiveSummary(len(inventory), sum(item.size_bytes for item in inventory), roots),
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
