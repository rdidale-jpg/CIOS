"""Canonical Flora Blueprint package manifest contract.

This module deliberately lives outside ``cios.applications.flora`` so contract
producers can export its schema without executing the Flora application package.
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BLUEPRINT_MANIFEST_SCHEMA_VERSION = "1.0"
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{1,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _safe_package_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or value.startswith(("/", "\\")) or "\\" in value or ".." in path.parts or path.as_posix() != value:
        raise ValueError("must be a normalized, relative POSIX archive path")
    return value


class BlueprintFile(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    path: str
    role: str | None = None
    required: bool = False
    sha256: str | None = None
    _path = field_validator("path")(_safe_package_path)

    @field_validator("sha256")
    @classmethod
    def valid_checksum(cls, value: str | None) -> str | None:
        if value is not None and not _SHA256_RE.fullmatch(value):
            raise ValueError("must be a lowercase SHA-256 digest")
        return value


class BlueprintRecordSet(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    record_class: str
    path: str
    count: int = Field(ge=0)
    required: bool = False
    _path = field_validator("path")(_safe_package_path)


class BlueprintManifest(BaseModel):
    """Implemented Blueprint manifest profile; unknown fields fail closed."""

    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["1.0"] = BLUEPRINT_MANIFEST_SCHEMA_VERSION
    package_id: str
    package_version: str
    enterprise_id: str
    profile_version: str
    # Optional governed linkage.  ``enterprise_id`` is the access boundary for
    # the package; it is not, by itself, proof of the Twin that owns its
    # contents.  Producers that want identity to resolve without a registry
    # confirmation must therefore supply this complete, explicit set.
    twin_id: str | None = None
    twin_type: Literal["industry", "enterprise", "market_participant", "opportunity"] | None = None
    primary_subject_id: str | None = None
    primary_subject_name: str | None = None
    primary_subject_class: Literal["industry", "enterprise", "market_participant", "opportunity"] | None = None
    governed_scope: str | None = None
    canonical_owner: str | None = None
    geography: str | None = None
    time_horizon: str | None = None
    included_sub_sectors: list[str] | None = None
    final_twin_spine_workbook: str | None = None
    files: list[BlueprintFile] = Field(default_factory=list)
    record_sets: list[BlueprintRecordSet] = Field(default_factory=list)

    @field_validator("package_id", "package_version", "enterprise_id", "profile_version", "twin_id", "primary_subject_id", "canonical_owner")
    @classmethod
    def safe_identifier(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value != value.strip() or not _ID_RE.fullmatch(value):
            raise ValueError("must be a safe 2-128 character identifier")
        return value

    @model_validator(mode="after")
    def complete_governed_identity(self):
        governed = (self.twin_id, self.twin_type, self.primary_subject_id,
                    self.primary_subject_name, self.primary_subject_class,
                    self.governed_scope, self.canonical_owner)
        if any(value not in (None, "") for value in governed) and not all(
                value not in (None, "") for value in governed):
            raise ValueError("governed Twin identity must supply twin_id, twin_type, primary subject, governed_scope and canonical_owner together")
        return self

    @field_validator("final_twin_spine_workbook")
    @classmethod
    def safe_workbook_path(cls, value: str | None) -> str | None:
        return _safe_package_path(value) if value is not None else None

    @model_validator(mode="after")
    def unique_paths_and_references(self):
        file_paths = [item.path for item in self.files]
        record_paths = [item.path for item in self.record_sets]
        if len(file_paths) != len(set(file_paths)) or len(record_paths) != len(set(record_paths)):
            raise ValueError("declared file paths must be unique")
        if self.final_twin_spine_workbook and self.final_twin_spine_workbook not in set(file_paths):
            raise ValueError("final_twin_spine_workbook must reference a declared file")
        return self


def build_manifest(**values) -> dict:
    """Validate and serialize a producer manifest deterministically."""
    return BlueprintManifest.model_validate(values).model_dump(mode="json", exclude_none=True)
