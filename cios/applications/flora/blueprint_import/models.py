"""Models for governed Blueprint package receipt state.

These records deliberately model package acceptance only. They are not Evidence,
Observations, Enterprise Model attributes, candidates, staging decisions, or
canonical intelligence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

PackageStatus = Literal["received"]
ImportRunStatus = Literal["received", "failed"]


class PackageReceiptError(ValueError):
    """Raised when a Blueprint package cannot be safely received."""


@dataclass(frozen=True)
class FileInventoryItem:
    path: str
    size_bytes: int
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BlueprintPackageIdentity:
    package_id: str
    package_version: str
    enterprise_id: str
    profile_version: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BlueprintPackageRecord:
    schema_version: str
    package_ref: str
    identity: BlueprintPackageIdentity
    package_sha256: str
    byte_count: int
    original_filename: str
    archive_path: str
    inventory: tuple[FileInventoryItem, ...]
    status: PackageStatus
    received_at: str
    received_by: str
    import_run_id: str
    workspace_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["identity"] = self.identity.to_dict()
        data["inventory"] = [item.to_dict() for item in self.inventory]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BlueprintPackageRecord":
        return cls(
            schema_version=str(data["schema_version"]),
            package_ref=str(data["package_ref"]),
            identity=BlueprintPackageIdentity(**data["identity"]),
            package_sha256=str(data["package_sha256"]),
            byte_count=int(data["byte_count"]),
            original_filename=str(data["original_filename"]),
            archive_path=str(data["archive_path"]),
            inventory=tuple(FileInventoryItem(**item) for item in data.get("inventory", [])),
            status=data["status"],
            received_at=str(data["received_at"]),
            received_by=str(data["received_by"]),
            import_run_id=str(data["import_run_id"]),
            workspace_id=str(data.get("workspace_id") or ""),
        )


@dataclass(frozen=True)
class ImportRunRecord:
    schema_version: str
    import_run_id: str
    package_ref: str
    package_sha256: str
    status: ImportRunStatus
    actor: str
    created_at: str
    updated_at: str
    error: str = ""
    canonical_mutation_count: int = 0
    deferred_capabilities: tuple[str, ...] = field(
        default=("parsing", "staging", "promotion", "enterprise_canvas")
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["deferred_capabilities"] = list(self.deferred_capabilities)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImportRunRecord":
        return cls(
            schema_version=str(data["schema_version"]),
            import_run_id=str(data["import_run_id"]),
            package_ref=str(data["package_ref"]),
            package_sha256=str(data["package_sha256"]),
            status=data["status"],
            actor=str(data["actor"]),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
            error=str(data.get("error", "")),
            canonical_mutation_count=int(data.get("canonical_mutation_count", 0)),
            deferred_capabilities=tuple(data.get("deferred_capabilities", [])),
        )
