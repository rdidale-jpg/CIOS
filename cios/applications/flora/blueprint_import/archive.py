"""Immutable archive and file-inventory handling for Blueprint packages."""
from __future__ import annotations

import hashlib
from io import BytesIO
import os
import re
import zipfile
from pathlib import PurePosixPath

from cios.applications.flora.storage import data_path, ensure_writable_dir

from .models import FileInventoryItem, PackageReceiptError

_PACKAGE_EXTENSIONS = {".zip"}
_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9._ -]+$")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def archive_root():
    return data_path("blueprint_import", "archives")


def _safe_original_filename(filename: str) -> str:
    raw = str(filename or "").strip()
    name = os.path.basename(raw)
    if raw != name:
        raise PackageReceiptError("Original filename must not contain path separators")
    if not name or not _SAFE_FILENAME_RE.fullmatch(name):
        raise PackageReceiptError("Original filename is required and must be a safe basename")
    if PurePosixPath(name).suffix.lower() not in _PACKAGE_EXTENSIONS:
        raise PackageReceiptError("Blueprint package receipt currently accepts .zip packages only")
    return name


def _validate_zip_member(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if not name or name.startswith("/") or "\\" in name:
        raise PackageReceiptError(f"Unsafe package member path: {name}")
    if any(part in ("", ".", "..") for part in path.parts):
        raise PackageReceiptError(f"Unsafe package member path: {name}")
    return path


def inspect_zip_inventory(content: bytes) -> tuple[FileInventoryItem, ...]:
    try:
        with zipfile.ZipFile(BytesIO(content)) as package:
            items: list[FileInventoryItem] = []
            for info in package.infolist():
                if info.is_dir():
                    continue
                path = _validate_zip_member(info.filename)
                file_bytes = package.read(info)
                items.append(
                    FileInventoryItem(
                        path=str(path),
                        size_bytes=len(file_bytes),
                        sha256=sha256_bytes(file_bytes),
                    )
                )
    except zipfile.BadZipFile as exc:
        raise PackageReceiptError("Blueprint package must be a valid ZIP archive") from exc
    if not items:
        raise PackageReceiptError("Blueprint package must contain at least one file")
    return tuple(sorted(items, key=lambda item: item.path))


def preserve_original_package(content: bytes, original_filename: str) -> tuple[str, int, str]:
    safe_name = _safe_original_filename(original_filename)
    checksum = sha256_bytes(content)
    root = ensure_writable_dir(archive_root() / checksum)
    destination = root / safe_name
    if destination.exists():
        existing = destination.read_bytes()
        if sha256_bytes(existing) != checksum:
            raise PackageReceiptError("Existing archive path contains different bytes")
    else:
        tmp = root / f".{safe_name}.{os.getpid()}.tmp"
        with tmp.open("wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, destination)
        os.chmod(destination, 0o444)
    return checksum, len(content), str(destination.relative_to(data_path()))
