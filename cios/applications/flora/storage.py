"""Runtime storage configuration and safe persistence helpers for Flora."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

FLORA_DATA_DIR_ENV = "FLORA_DATA_DIR"
LEGACY_FLORA_PILOT_DIR_ENV = "FLORA_PILOT_DIR"
DEFAULT_DATA_DIR = Path("/var/data/flora")
REQUIRED_DIRS = (
    "ai_financial_reports/uploads",
    "ai_financial_reports/runs",
    "documents",
    "live_evidence",
    "collection_manifests",
    "commercial_context",
    "memory",
    "memory/enterprise_models",
    "blueprint_import/archives",
    "blueprint_import/audit",
    "blueprint_import/packages",
    "blueprint_import/runs",
    "blueprint_import/lifecycle",
    "blueprint_import/staging",
    "blueprint_import/reviews",
    "blueprint_import/mappings",
    "blueprint_import/plans",
    "blueprint_import/promotion/approvals",
    "blueprint_import/promotion/executions",
)

class PersistenceError(OSError):
    """Raised when Flora runtime state cannot be persisted safely.

    ``context`` is deliberately made of operational filesystem facts.  It is
    safe to log and prevents an OSError's useful errno/path from being lost
    when storage adapters add application-level context.
    """

    def __init__(self, message: str, *, operation: str = "unknown", path: Path | str | None = None,
                 cause: BaseException | None = None, temp_path: Path | str | None = None):
        super().__init__(message)
        self.context = filesystem_context(path or data_root(), operation=operation, error=cause, temp_path=temp_path)


def filesystem_context(path: Path | str, *, operation: str = "inspect",
                       error: BaseException | None = None,
                       temp_path: Path | str | None = None) -> dict[str, Any]:
    """Return mount, capacity, inode and ownership facts for a target path."""
    target = Path(path).expanduser().resolve(strict=False)
    existing = target
    while not existing.exists() and existing != existing.parent:
        existing = existing.parent
    result: dict[str, Any] = {
        "operation": operation, "path": str(target), "parent_path": str(target.parent),
        "storage_root": str(data_root().expanduser().resolve(strict=False)),
        "is_mount": os.path.ismount(target), "existing_filesystem_path": str(existing),
        "existing_path_is_mount": os.path.ismount(existing), "uid": os.geteuid(), "gid": os.getegid(),
        "parent_writable": os.access(existing, os.W_OK),
        "temp_path": str(temp_path) if temp_path is not None else None,
    }
    try:
        stat = existing.stat()
        result.update(filesystem_device_id=stat.st_dev, directory_uid=stat.st_uid,
                      directory_gid=stat.st_gid, directory_mode=oct(stat.st_mode & 0o7777))
        fs = os.statvfs(existing)
        result.update(total_bytes=fs.f_blocks * fs.f_frsize, free_bytes=fs.f_bfree * fs.f_frsize,
                      available_bytes=fs.f_bavail * fs.f_frsize, total_inodes=fs.f_files,
                      free_inodes=fs.f_ffree, available_inodes=getattr(fs, "f_favail", fs.f_ffree))
    except OSError as stat_error:
        result["stat_error"] = {"type": type(stat_error).__name__, "errno": stat_error.errno,
                                "path": stat_error.filename}
    root = root_exception(error) if error is not None else None
    result.update(error_type=type(root).__name__ if root is not None else None,
                  errno=getattr(root, "errno", None), error_path=getattr(root, "filename", None))
    return result


def root_exception(exc: BaseException) -> BaseException:
    """Return the deepest explicitly chained exception without exposing it."""
    current = exc
    seen: set[int] = set()
    while current.__cause__ is not None and id(current) not in seen:
        seen.add(id(current))
        current = current.__cause__
    return current


def safe_exception_summary(exc: BaseException) -> str:
    """Describe a storage failure without copying exception text or parameters."""
    name = type(exc).__name__.lower()
    if "integrity" in name:
        return "Storage rejected the record because an integrity constraint was not satisfied."
    if "operational" in name or isinstance(exc, (ConnectionError, TimeoutError)):
        return "The storage backend was unavailable during the operation."
    if "programming" in name:
        return "The storage backend rejected the operation because its schema or statement was incompatible."
    if "serial" in name or isinstance(exc, (TypeError, ValueError)):
        return "The record could not be serialized for storage."
    if isinstance(exc, OSError):
        return "The filesystem storage operation failed."
    return "The storage operation failed; consult the correlated server log for details."


def data_root() -> Path:
    raw = os.getenv(FLORA_DATA_DIR_ENV) or os.getenv(LEGACY_FLORA_PILOT_DIR_ENV) or str(DEFAULT_DATA_DIR)
    return Path(raw).expanduser()


def data_path(*parts: str) -> Path:
    root = data_root()
    path = root.joinpath(*parts)
    resolved_root = root.resolve(strict=False)
    resolved_path = path.resolve(strict=False)
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise PersistenceError(f"Unsafe Flora data path outside {resolved_root}")
    return path


def ensure_writable_dir(path: Path) -> Path:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".flora_write_probe"
        with probe.open("w", encoding="utf-8") as handle:
            handle.write("ok")
            handle.flush()
            os.fsync(handle.fileno())
        probe.unlink(missing_ok=True)
    except OSError as exc:
        raise PersistenceError(f"Flora storage directory is not writable: {path}: {exc}",
                               operation="write_probe", path=path, cause=exc) from exc
    return path


def ensure_parent_writable(path: Path) -> Path:
    ensure_writable_dir(path.parent)
    return path


def atomic_write_text(path: Path, text: str) -> None:
    tmp: Path | None = None
    try:
        ensure_parent_writable(path)
        # A process id is not unique between concurrent requests in the same
        # web process.  A per-write name prevents one request's os.replace()
        # from consuming another request's temporary receipt file.
        tmp = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        try:
            dir_fd = os.open(str(path.parent), os.O_DIRECTORY)
            try: os.fsync(dir_fd)
            finally: os.close(dir_fd)
        except OSError:
            pass
    except OSError as exc:
        raise PersistenceError(f"Failed to persist Flora data at {path}: {exc}", operation="atomic_write",
                               path=path, cause=exc, temp_path=tmp) from exc
    finally:
        if tmp is not None:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def atomic_write_bytes(path: Path, content: bytes, *, mode: int | None = None) -> None:
    """Atomically write bytes using a unique temporary file on the target filesystem."""
    tmp: Path | None = None
    try:
        ensure_parent_writable(path)
        tmp = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
        with tmp.open("wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        if mode is not None:
            os.chmod(path, mode)
    except OSError as exc:
        raise PersistenceError(f"Failed to persist Flora binary data at {path}: {exc}",
                               operation="atomic_write_bytes", path=path, cause=exc,
                               temp_path=tmp) from exc
    finally:
        if tmp is not None:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass


def storage_mode() -> dict[str, Any]:
    root = data_root()
    configured = bool(os.getenv(FLORA_DATA_DIR_ENV) or os.getenv(LEGACY_FLORA_PILOT_DIR_ENV))
    resolved_root = root.resolve(strict=False)
    durable = str(resolved_root).startswith("/var/data")
    if durable:
        mode = "persistent pilot storage"
    elif configured:
        mode = "configured pilot storage"
    else:
        mode = "ephemeral pilot storage"
    return {"mode": mode, "data_root": str(resolved_root), "configured": configured, "durable": durable, "ephemeral": not durable}


def startup_storage_status() -> dict[str, Any]:
    root = data_root()
    mode = storage_mode()
    durable = bool(mode["durable"])
    diagnostics = filesystem_context(root, operation="startup_probe")
    diagnostics["configured_data_root"] = str(root)
    diagnostics["resolved_data_root"] = str(root.resolve(strict=False))
    diagnostics["write_probe_succeeded"] = False
    try:
        ensure_writable_dir(root)
        diagnostics = filesystem_context(root, operation="startup_probe") | {
            "configured_data_root": str(root), "resolved_data_root": str(root.resolve(strict=False)),
            "write_probe_succeeded": True,
        }
        for rel in REQUIRED_DIRS:
            ensure_writable_dir(root / rel)
        # Exercise the same JSON write/read/replace boundary used by
        # BlueprintPackageRecord before accepting uploads.
        receipt_root = root / "blueprint_import" / "packages"
        probe = receipt_root / f".blueprint-package-startup-{uuid4().hex}.json"
        try:
            atomic_write_json(probe, {"record_type": "BlueprintPackageRecord", "startup_probe": True})
            if json.loads(probe.read_text(encoding="utf-8")) != {
                "record_type": "BlueprintPackageRecord", "startup_probe": True
            }:
                raise PersistenceError("Flora Blueprint package storage probe could not be read back")
        finally:
            probe.unlink(missing_ok=True)
        status = mode["mode"]
        ready = True
    except PersistenceError as exc:
        status = "storage unavailable"
        ready = False
        diagnostics.update(exc.context)
        diagnostics["write_probe_succeeded"] = False
        return {"ready": ready, "status": status, "data_root": mode["data_root"], "durable": durable, "ephemeral": mode["ephemeral"], "storage_mode": mode["mode"], "error": str(exc), "diagnostics": diagnostics}
    return {"ready": ready, "status": status, "data_root": mode["data_root"], "durable": durable, "ephemeral": mode["ephemeral"], "storage_mode": mode["mode"], "diagnostics": diagnostics}
