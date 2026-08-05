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
CHANGE_MARKER_ENV_NAMES = ("FLORA_DEPLOYED_CHANGE_MARKER", "FLORA_CHANGE_ID", "DEPLOYED_CHANGE_MARKER")
SERVICE_ENV_NAMES = ("RENDER_SERVICE_NAME", "FLORA_RENDER_SERVICE", "APPLICATION_SERVICE")
REPOSITORY_ENV_NAMES = ("RENDER_GIT_REPO_SLUG", "RENDER_REPOSITORY", "GITHUB_REPOSITORY")
BUILD_COMMAND_ENV_NAMES = ("RENDER_BUILD_COMMAND", "FLORA_BUILD_COMMAND")
START_COMMAND_ENV_NAMES = ("RENDER_START_COMMAND", "FLORA_START_COMMAND")
AUTO_DEPLOY_ENV_NAMES = ("RENDER_AUTO_DEPLOY", "FLORA_AUTO_DEPLOY")
DEPLOYMENT_STATUS_ENV_NAMES = ("RENDER_DEPLOY_STATUS", "FLORA_DEPLOYMENT_STATUS")

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
        return "Unavailable — deployment metadata not configured"


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
        return subprocess.check_output(["git", "branch", "--show-current"], text=True, stderr=subprocess.DEVNULL).strip()[:128] or "Unavailable — deployment metadata not configured"
    except Exception:
        return "Unavailable — deployment metadata not configured"


def build_timestamp() -> str:
    """Return a bounded non-secret build timestamp when the platform exposes one."""
    value = _first_env(BUILD_TIMESTAMP_ENV_NAMES)
    if value and value.isdigit():
        try:
            return datetime.fromtimestamp(int(value), UTC).isoformat()
        except (OverflowError, ValueError, OSError):
            return value
    return value or "Unavailable — deployment metadata not configured"


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
        "deployed_change_marker": _first_env(CHANGE_MARKER_ENV_NAMES) or "Unavailable — deployment metadata not configured",
        "render_service": _first_env(SERVICE_ENV_NAMES) or "Unavailable — deployment metadata not configured",
        "repository": _first_env(REPOSITORY_ENV_NAMES) or "Unavailable — deployment metadata not configured",
        "build_command": _first_env(BUILD_COMMAND_ENV_NAMES) or "Unavailable — deployment metadata not configured",
        "start_command": _first_env(START_COMMAND_ENV_NAMES) or "Unavailable — deployment metadata not configured",
        "auto_deploy": _first_env(AUTO_DEPLOY_ENV_NAMES) or "Unavailable — deployment metadata not configured",
        "latest_deployment_status": _first_env(DEPLOYMENT_STATUS_ENV_NAMES) or "Unavailable — deployment metadata not configured",
    }
