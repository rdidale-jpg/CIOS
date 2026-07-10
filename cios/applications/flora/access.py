"""Shared Flora product access checks."""
from __future__ import annotations

import os
import re
from cios.applications.flora.pilot_auth import resolve_pilot_session
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


def _trusted_proxy_headers_enabled() -> bool:
    return os.environ.get("FLORA_TRUST_PROXY_HEADERS", "0").strip().lower() in {"1", "true", "yes", "on"}


def _trusted_header(headers: Any, name: str) -> str:
    if not _trusted_proxy_headers_enabled():
        return ""
    return str(headers.get(name) or "").strip()


def authenticated_flora_user(headers: Any) -> str:
    """Resolve the canonical Flora principal from the product session.

    Live browser requests are cookie/session based.  Trusted proxy headers remain
    available for the existing in-process tests and for deployments that
    explicitly choose to map an upstream identity provider into Flora headers.
    """
    session = resolve_pilot_session(headers)
    if session:
        return session.user_id
    return str(_trusted_header(headers, "X-Flora-User") or cookie_value(headers, "flora_user") or "").strip()


def flora_authentication_source(headers: Any) -> str:
    if resolve_pilot_session(headers):
        return "pilot_session_cookie"
    if _trusted_header(headers, "X-Flora-User"):
        return "trusted_proxy_header"
    if cookie_value(headers, "flora_user"):
        return "flora_session_cookie"
    return "none"


def financial_run_enterprise_id(run: dict[str, Any]) -> str:
    return str(run.get("enterprise_id") or (run.get("document") or {}).get("enterprise_id") or "bt-group-plc")


def user_enterprise_access(headers: Any) -> set[str]:
    session = resolve_pilot_session(headers)
    if session:
        return {session.workspace}
    allowed = _trusted_header(headers, "X-Flora-Enterprises") or cookie_value(headers, "flora_enterprises")
    return {item.strip() for item in str(allowed or "").replace("|", ",").split(",") if item.strip()}


def active_flora_workspace(headers: Any) -> str:
    """Resolve Flora's active workspace from the canonical session state."""
    session = resolve_pilot_session(headers)
    if session:
        return session.workspace
    selected = _trusted_header(headers, "X-Flora-Active-Workspace") or cookie_value(headers, "flora_active_workspace")
    allowed = user_enterprise_access(headers)
    if selected and ("*" in allowed or selected in allowed):
        return selected
    concrete = sorted(w for w in allowed if w != "*")
    return concrete[0] if len(concrete) == 1 else ""


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
    owner_recognised: bool
    active_workspace: str
    resolved_membership: str
    resolved_role: str
    policy_name: str
    policy_source: str
    decision: str
    denial_reason: str = ""
    authentication_source: str = "none"


def raw_flora_roles(headers: Any) -> set[str]:
    session = resolve_pilot_session(headers)
    if session:
        return {session.role}
    raw_roles = _trusted_header(headers, "X-Flora-Roles") or cookie_value(headers, "flora_roles")
    return {item.strip() for item in str(raw_roles or "").replace("|", ",").split(",") if item.strip()}


def flora_roles(headers: Any) -> set[str]:
    roles = raw_flora_roles(headers)
    if authenticated_flora_user(headers) and active_flora_workspace(headers) and roles & CANONICAL_OWNER_ROLES:
        roles |= BLUEPRINT_IMPORT_OWNER_PERMISSIONS | {CIOS_OWNER_ROLE}
    return roles


def is_cios_owner(headers: Any) -> bool:
    return bool(authenticated_flora_user(headers) and active_flora_workspace(headers) and raw_flora_roles(headers) & CANONICAL_OWNER_ROLES)


def blueprint_upload_authorisation(headers: Any) -> BlueprintAuthorisationDecision:
    user = authenticated_flora_user(headers)
    auth_source = flora_authentication_source(headers)
    workspaces = tuple(sorted(user_enterprise_access(headers))) if user else ()
    active_workspace = active_flora_workspace(headers) if user else ""
    raw_roles = raw_flora_roles(headers) if user and active_workspace else set()
    roles = flora_roles(headers) if user and active_workspace else set()
    permissions = sorted(roles & (BLUEPRINT_IMPORT_OWNER_PERMISSIONS | {BLUEPRINT_UPLOAD_PERMISSION}))
    membership_resolved = bool(user and active_workspace and ("*" in workspaces or active_workspace in workspaces))
    owner_recognised = bool(membership_resolved and raw_roles & CANONICAL_OWNER_ROLES)
    allowed = membership_resolved and bool(roles & _BLUEPRINT_IMPORT_ROLES)
    if allowed:
        reason = ""
    elif not user:
        reason = "missing authenticated Flora user"
    elif not active_workspace:
        reason = "no active workspace in product session"
    elif not membership_resolved:
        reason = "workspace membership could not be resolved from the authenticated account"
    elif owner_recognised and BLUEPRINT_UPLOAD_PERMISSION not in permissions:
        reason = "Blueprint upload capability is missing from the owner role"
    else:
        reason = "missing package.upload or owner-inherited authority"
    return BlueprintAuthorisationDecision(
        user_id=user,
        workspace_ids=workspaces,
        raw_roles=tuple(sorted(raw_roles)),
        effective_roles=tuple(sorted(roles)),
        effective_permissions=tuple(permissions),
        required_permission=BLUEPRINT_UPLOAD_PERMISSION,
        owner_recognised=owner_recognised,
        active_workspace=active_workspace,
        resolved_membership="resolved" if membership_resolved else "unresolved",
        resolved_role=next((role for role in (CIOS_OWNER_ROLE, BLUEPRINT_IMPORT_ADMIN_ROLE, BLUEPRINT_UPLOAD_PERMISSION) if role in roles), sorted(roles)[0] if roles else ""),
        policy_name="can_receive_blueprint_package",
        policy_source="canonical Flora product session",
        decision="allowed" if allowed else "denied",
        denial_reason=reason,
        authentication_source=auth_source,
    )


def can_receive_blueprint_package(headers: Any) -> bool:
    """Return True when the product session can receive Blueprint packages."""
    return blueprint_upload_authorisation(headers).decision == "allowed"


def can_access_enterprise(headers: Any, enterprise_id: str) -> bool:
    if not authenticated_flora_user(headers):
        return False
    allowed = user_enterprise_access(headers)
    return "*" in allowed or enterprise_id in allowed
