"""Minimal Blueprint package manifest validation for receipt metadata."""
from __future__ import annotations

import json
import re
import zipfile
from io import BytesIO
from typing import Any

from .models import BlueprintPackageIdentity, PackageReceiptError

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{1,127}$")


def _require_safe_id(data: dict[str, Any], key: str) -> str:
    value = str(data.get(key) or "").strip()
    if not _ID_RE.fullmatch(value):
        raise PackageReceiptError(f"Manifest field {key} is required and must be a safe identifier")
    return value


def read_identity(content: bytes) -> BlueprintPackageIdentity:
    try:
        with zipfile.ZipFile(BytesIO(content)) as package:
            try:
                raw = package.read("blueprint_manifest.json")
            except KeyError as exc:
                raise PackageReceiptError("Blueprint package must contain blueprint_manifest.json") from exc
    except zipfile.BadZipFile as exc:
        raise PackageReceiptError("Blueprint package must be a valid ZIP archive") from exc
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageReceiptError("blueprint_manifest.json must be valid UTF-8 JSON") from exc
    if not isinstance(manifest, dict):
        raise PackageReceiptError("blueprint_manifest.json must contain an object")
    return BlueprintPackageIdentity(
        package_id=_require_safe_id(manifest, "package_id"),
        package_version=_require_safe_id(manifest, "package_version"),
        enterprise_id=_require_safe_id(manifest, "enterprise_id"),
        profile_version=_require_safe_id(manifest, "profile_version"),
    )
