"""Shared Flora product access checks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote_plus

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
            return unquote_plus(value.strip())
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


BLUEPRINT_UPLOAD_PERMISSION = "package.upload"
BLUEPRINT_REVIEW_PERMISSION = "package.review"
BLUEPRINT_PROMOTE_PERMISSION = "candidate.promote"
BLUEPRINT_IMPORT_ADMIN_ROLE = "blueprint_import_admin"
CIOS_OWNER_ROLE = "cios_owner"
CANONICAL_OWNER_ROLES = frozenset({CIOS_OWNER_ROLE, "owner", "workspace.owner", "workspace_owner"})

BLUEPRINT_IMPORT_OWNER_PERMISSIONS = frozenset({
    BLUEPRINT_UPLOAD_PERMISSION,
    BLUEPRINT_REVIEW_PERMISSION,
    BLUEPRINT_PROMOTE_PERMISSION,
    BLUEPRINT_IMPORT_ADMIN_ROLE,
})
_BLUEPRINT_IMPORT_ROLES = {BLUEPRINT_IMPORT_ADMIN_ROLE, BLUEPRINT_UPLOAD_PERMISSION}


@dataclass(frozen=True)
class BlueprintAuthorisationDecision:
    user_id: str
    workspace_ids: tuple[str, ...]
    raw_roles: tuple[str, ...]
    effective_roles: tuple[str, ...]
    effective_permissions: tuple[str, ...]
    required_permission: str
    policy_name: str
    policy_source: str
    decision: str
    denial_reason: str = ""


def raw_flora_roles(headers: Any) -> set[str]:
    raw_roles = headers.get("X-Flora-Roles") or cookie_value(headers, "flora_roles")
    return {item.strip() for item in str(raw_roles or "").replace("|", ",").split(",") if item.strip()}


def flora_roles(headers: Any) -> set[str]:
    roles = raw_flora_roles(headers)
    if roles & CANONICAL_OWNER_ROLES:
        roles |= BLUEPRINT_IMPORT_OWNER_PERMISSIONS | {CIOS_OWNER_ROLE}
    return roles


def is_cios_owner(headers: Any) -> bool:
    return bool(raw_flora_roles(headers) & CANONICAL_OWNER_ROLES)


def blueprint_upload_authorisation(headers: Any) -> BlueprintAuthorisationDecision:
    user = authenticated_flora_user(headers)
    raw_roles = raw_flora_roles(headers)
    roles = flora_roles(headers)
    permissions = sorted(roles & (BLUEPRINT_IMPORT_OWNER_PERMISSIONS | {BLUEPRINT_UPLOAD_PERMISSION}))
    allowed = bool(user) and bool(roles & _BLUEPRINT_IMPORT_ROLES)
    if allowed:
        reason = ""
    elif not user:
        reason = "missing authenticated Flora user"
    else:
        reason = "missing package.upload or owner-inherited authority"
    return BlueprintAuthorisationDecision(
        user_id=user,
        workspace_ids=tuple(sorted(user_enterprise_access(headers))),
        raw_roles=tuple(sorted(raw_roles)),
        effective_roles=tuple(sorted(roles)),
        effective_permissions=tuple(permissions),
        required_permission=BLUEPRINT_UPLOAD_PERMISSION,
        policy_name="can_receive_blueprint_package",
        policy_source="product-session header/cookie role policy",
        decision="allowed" if allowed else "denied",
        denial_reason=reason,
    )


def can_receive_blueprint_package(headers: Any) -> bool:
    """Return True when the product session can receive Blueprint packages."""
    return blueprint_upload_authorisation(headers).decision == "allowed"


def can_access_enterprise(headers: Any, enterprise_id: str) -> bool:
    if not authenticated_flora_user(headers):
        return False
    allowed = user_enterprise_access(headers)
    return "*" in allowed or enterprise_id in allowed
