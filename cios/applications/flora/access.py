"""Shared Flora product access checks."""
from __future__ import annotations

import re
from typing import Any

_RUN_ID_RE = re.compile(r"^fi-[A-Za-z0-9_-]+$")


def valid_financial_intelligence_run_id(run_id: str) -> bool:
    """Return True for bounded persisted Financial Intelligence run IDs."""
    return bool(_RUN_ID_RE.fullmatch(str(run_id or "")))


def cookie_value(headers: Any, name: str) -> str:
    for part in (headers.get("Cookie", "") or "").split(";"):
        if "=" not in part:
            continue
        key, value = part.strip().split("=", 1)
        if key == name:
            return value
    return ""


def authenticated_flora_user(headers: Any) -> str:
    return str(headers.get("X-Flora-User") or cookie_value(headers, "flora_user") or "").strip()


def financial_run_enterprise_id(run: dict[str, Any]) -> str:
    return str(run.get("enterprise_id") or (run.get("document") or {}).get("enterprise_id") or "bt-group-plc")


def user_enterprise_access(headers: Any) -> set[str]:
    allowed = headers.get("X-Flora-Enterprises") or cookie_value(headers, "flora_enterprises")
    return {item.strip() for item in str(allowed or "").replace("|", ",").split(",") if item.strip()}


def can_view_financial_intelligence_run(headers: Any, run: dict[str, Any]) -> bool:
    """Authoritative product-session rule for viewing FI runs and safe reports."""
    if not authenticated_flora_user(headers):
        return False
    allowed = user_enterprise_access(headers)
    if not allowed:
        return False
    enterprise_id = financial_run_enterprise_id(run)
    run_id = str(run.get("run_id") or "")
    return valid_financial_intelligence_run_id(run_id) and ("*" in allowed or enterprise_id in allowed)


_BLUEPRINT_IMPORT_ROLES = {"blueprint_import_admin", "package.upload"}


def can_receive_blueprint_package(headers: Any) -> bool:
    """Return True when the product session can receive Blueprint packages."""
    if not authenticated_flora_user(headers):
        return False
    raw_roles = headers.get("X-Flora-Roles") or cookie_value(headers, "flora_roles")
    roles = {item.strip() for item in str(raw_roles or "").replace("|", ",").split(",") if item.strip()}
    return bool(roles & _BLUEPRINT_IMPORT_ROLES)
