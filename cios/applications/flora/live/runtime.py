"""Runtime build identification helpers for Flora live collection."""
from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from functools import lru_cache

REVISION_ENV_NAMES = ("RENDER_GIT_COMMIT", "APPLICATION_REVISION", "APP_REVISION", "GIT_COMMIT", "SOURCE_VERSION")
BRANCH_ENV_NAMES = ("RENDER_GIT_BRANCH", "APPLICATION_BRANCH", "APP_BRANCH", "GIT_BRANCH", "SOURCE_BRANCH")
BUILD_TIMESTAMP_ENV_NAMES = ("RENDER_BUILD_TIMESTAMP", "FLORA_BUILD_TIMESTAMP", "BUILD_TIMESTAMP", "SOURCE_DATE_EPOCH")
VERSION_ENV_NAMES = ("FLORA_DEPLOYMENT_VERSION", "RENDER_SERVICE_NAME", "APPLICATION_VERSION", "APP_VERSION")

@lru_cache(maxsize=1)
def application_revision() -> str:
    """Return a bounded non-secret application revision identifier."""
    for name in REVISION_ENV_NAMES:
        value = os.environ.get(name, "").strip()
        if value:
            return value[:64]
    try:
        return subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def _first_env(names: tuple[str, ...]) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value[:128]
    return ""


def application_branch() -> str:
    """Return a bounded non-secret source branch identifier."""
    value = _first_env(BRANCH_ENV_NAMES)
    if value:
        return value
    try:
        return subprocess.check_output(["git", "branch", "--show-current"], text=True, stderr=subprocess.DEVNULL).strip()[:128] or "unknown"
    except Exception:
        return "unknown"


def build_timestamp() -> str:
    """Return a bounded non-secret build timestamp when the platform exposes one."""
    value = _first_env(BUILD_TIMESTAMP_ENV_NAMES)
    if value and value.isdigit():
        try:
            return datetime.fromtimestamp(int(value), UTC).isoformat()
        except (OverflowError, ValueError, OSError):
            return value
    return value or "unknown"


def deployment_version() -> str:
    """Return a bounded non-secret deployment version identifier."""
    return _first_env(VERSION_ENV_NAMES) or application_revision()


def deployment_metadata() -> dict[str, str]:
    """Return safe deployment metadata for logs and diagnostics."""
    return {
        "deployment_version": deployment_version(),
        "commit_sha": application_revision(),
        "branch": application_branch(),
        "build_timestamp": build_timestamp(),
    }
