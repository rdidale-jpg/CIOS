"""Minimal Blueprint package manifest validation for receipt metadata."""
from __future__ import annotations

import json
import zipfile
from io import BytesIO
from typing import Any

from pydantic import ValidationError
from .contract import BlueprintManifest
from .models import BlueprintPackageIdentity, PackageReceiptError

ROOT_MANIFEST = "blueprint_manifest.json"

MISSING_MANIFEST_MESSAGE = "Blueprint package is missing blueprint_manifest.json. Place blueprint_manifest.json at the root of the ZIP package."
NESTED_MANIFEST_MESSAGE = "blueprint_manifest.json was found inside a folder. Move it to the root of the ZIP package and try again."
DUPLICATE_MANIFEST_MESSAGE = "The package contains more than one blueprint_manifest.json. Keep one canonical manifest at the ZIP root."
INVALID_JSON_MESSAGE = "blueprint_manifest.json is not valid JSON."
INVALID_SCHEMA_MESSAGE = "blueprint_manifest.json does not match the required Blueprint manifest structure."


def _manifest_names(package: zipfile.ZipFile) -> tuple[list[str], list[str]]:
    root: list[str] = []
    nested: list[str] = []
    for info in package.infolist():
        if info.is_dir():
            continue
        name = info.filename.replace("\\", "/")
        if name == ROOT_MANIFEST:
            root.append(info.filename)
        elif name.endswith("/" + ROOT_MANIFEST):
            nested.append(info.filename)
    return root, nested


def read_root_manifest(package: zipfile.ZipFile) -> dict[str, Any]:
    root, nested = _manifest_names(package)
    if len(root) > 1 or (root and nested):
        raise PackageReceiptError(DUPLICATE_MANIFEST_MESSAGE)
    if not root and nested:
        raise PackageReceiptError(NESTED_MANIFEST_MESSAGE)
    if not root:
        raise PackageReceiptError(MISSING_MANIFEST_MESSAGE)
    try:
        manifest = json.loads(package.read(ROOT_MANIFEST).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageReceiptError(INVALID_JSON_MESSAGE) from exc
    if not isinstance(manifest, dict):
        raise PackageReceiptError(INVALID_SCHEMA_MESSAGE)
    return manifest


def parse_manifest(data: dict[str, Any]) -> BlueprintManifest:
    """Parse with the canonical contract while keeping Flora's safe diagnostic."""
    try:
        return BlueprintManifest.model_validate(data)
    except ValidationError as exc:
        raise PackageReceiptError(INVALID_SCHEMA_MESSAGE) from exc


def read_identity(content: bytes) -> BlueprintPackageIdentity:
    try:
        with zipfile.ZipFile(BytesIO(content)) as package:
            manifest = parse_manifest(read_root_manifest(package))
    except zipfile.BadZipFile as exc:
        raise PackageReceiptError("Blueprint package must be a valid ZIP archive") from exc
    return BlueprintPackageIdentity(
        package_id=manifest.package_id,
        package_version=manifest.package_version,
        enterprise_id=manifest.enterprise_id,
        profile_version=manifest.profile_version,
    )
