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
    final_twin_spine_workbook: str | None = None
    files: list[BlueprintFile] = Field(default_factory=list)
    record_sets: list[BlueprintRecordSet] = Field(default_factory=list)

    @field_validator("package_id", "package_version", "enterprise_id", "profile_version")
    @classmethod
    def safe_identifier(cls, value: str) -> str:
        if value != value.strip() or not _ID_RE.fullmatch(value):
            raise ValueError("must be a safe 2-128 character identifier")
        return value

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
