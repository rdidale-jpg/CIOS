"""Runtime storage configuration and safe persistence helpers for Flora."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

FLORA_DATA_DIR_ENV = "FLORA_DATA_DIR"
LEGACY_FLORA_PILOT_DIR_ENV = "FLORA_PILOT_DIR"
DEFAULT_DATA_DIR = Path(".flora_pilot")
REQUIRED_DIRS = (
    "ai_financial_reports/uploads",
    "ai_financial_reports/runs",
    "documents",
    "live_evidence",
    "collection_manifests",
    "memory",
    "memory/enterprise_models",
)

class PersistenceError(OSError):
    """Raised when Flora runtime state cannot be persisted safely."""


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
        raise PersistenceError(f"Flora storage directory is not writable: {path}: {exc}") from exc
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
        raise PersistenceError(f"Failed to persist Flora data at {path}: {exc}") from exc


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def storage_mode() -> dict[str, Any]:
    root = data_root()
    configured = bool(os.getenv(FLORA_DATA_DIR_ENV))
    durable = configured and str(root.resolve(strict=False)).startswith("/var/data")
    mode = "configured pilot storage" if configured else "ephemeral pilot storage"
    return {"mode": mode, "data_root": str(root.resolve(strict=False)), "configured": configured, "durable": durable, "ephemeral": not configured}


def startup_storage_status() -> dict[str, Any]:
    root = data_root()
    mode = storage_mode()
    durable = bool(mode["durable"])
    try:
        ensure_writable_dir(root)
        for rel in REQUIRED_DIRS:
            ensure_writable_dir(root / rel)
        status = "persistent storage ready" if durable else mode["mode"]
        ready = True
    except PersistenceError as exc:
        status = "storage unavailable"
        ready = False
        return {"ready": ready, "status": status, "data_root": mode["data_root"], "durable": durable, "ephemeral": mode["ephemeral"], "storage_mode": mode["mode"], "error": str(exc)}
    return {"ready": ready, "status": status, "data_root": mode["data_root"], "durable": durable, "ephemeral": mode["ephemeral"], "storage_mode": mode["mode"]}
