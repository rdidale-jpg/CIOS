"""Runtime storage configuration and safe persistence helpers for Flora."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

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

    ``diagnostic`` is deliberately limited to operational metadata.  It gives
    the web/runtime diagnostics the original OS error without leaking data or
    configuration values.
    """

    def __init__(self, message: str, *, operation: str = "unknown", record_type: str = "unknown", cause: BaseException | None = None):
        super().__init__(message)
        self.diagnostic = {
            "exception_class": type(cause).__name__ if cause else type(self).__name__,
            "category": _error_category(cause),
            "operation": operation,
            "record_type": record_type,
            "transaction_state": "rolled back" if operation == "registry transaction" else "not committed",
            "connection_available": True,  # the canonical adapter is filesystem-backed
            "schema_alignment": "unknown",
            "safe_error": str(cause or message),
        }


def _error_category(exc: BaseException | None) -> str:
    if isinstance(exc, OSError):
        return {
            2: "missing path", 13: "permission/constraint", 17: "path conflict",
            28: "capacity/quota", 30: "read-only storage",
        }.get(exc.errno, "filesystem I/O")
    return "storage"


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
        raise PersistenceError(f"Flora storage directory is not writable: {path}: {exc}", operation="write probe", record_type="directory", cause=exc) from exc
    return path


def ensure_parent_writable(path: Path) -> Path:
    ensure_writable_dir(path.parent)
    return path


def atomic_write_text(path: Path, text: str) -> None:
    try:
        ensure_parent_writable(path)
        tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
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
        raise PersistenceError(f"Failed to persist Flora data at {path}: {exc}", operation="atomic file replace", record_type="JSON record", cause=exc) from exc


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


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
    try:
        ensure_writable_dir(root)
        for rel in REQUIRED_DIRS:
            ensure_writable_dir(root / rel)
        status = mode["mode"]
        ready = True
    except PersistenceError as exc:
        status = "storage unavailable"
        ready = False
        from cios.applications.flora.blueprint_import.registry import blueprint_registry_storage_status
        return {"ready": ready, "status": status, "data_root": mode["data_root"], "durable": durable, "ephemeral": mode["ephemeral"], "storage_mode": mode["mode"], "error": str(exc), "blueprint_package_registry": blueprint_registry_storage_status()}
    result = {"ready": ready, "status": status, "data_root": mode["data_root"], "durable": durable, "ephemeral": mode["ephemeral"], "storage_mode": mode["mode"]}
    # Extend the established startup diagnostic rather than introducing a
    # second operator-facing health system.
    from cios.applications.flora.blueprint_import.registry import blueprint_registry_storage_status
    result["blueprint_package_registry"] = blueprint_registry_storage_status()
    return result
