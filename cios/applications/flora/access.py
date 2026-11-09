"""Shared Flora product access checks."""
from __future__ import annotations

import re
from cios.applications.flora.security import verified_context, require_verified_human
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote_plus
from cios.applications.flora.pilot_import import (
    PILOT_BLUEPRINT_CAPABILITIES, PILOT_IMPORT_ACTOR, PILOT_IMPORT_WORKSPACE,
    pilot_import_bypass_enabled,
)

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
    context = verified_context(headers)
    return context.user_id if context else ""


def flora_authentication_source(headers: Any) -> str:
    return "verified_server_context" if verified_context(headers) else "none"


def financial_run_enterprise_id(run: dict[str, Any]) -> str:
    return str(run.get("enterprise_id") or (run.get("document") or {}).get("enterprise_id") or "bt-group-plc")


def canonical_enterprise_id(value: str) -> str:
    """Return the canonical comparison form for workspace and enterprise IDs."""
    return str(value or "").strip().casefold()


def _contains_id(values: set[str], candidate: str) -> bool:
    wanted = canonical_enterprise_id(candidate)
    return any(canonical_enterprise_id(value) == wanted for value in values)


def user_enterprise_access(headers: Any) -> set[str]:
    context = verified_context(headers)
    return set(context.enterprise_ids) if context else set()


def active_flora_workspace(headers: Any) -> str:
    context = verified_context(headers)
    return context.workspace if context else ""


def can_view_financial_intelligence_run(headers: Any, run: dict[str, Any]) -> bool:
    """Boolean form of the same persisted financial read boundary."""
    if not isinstance(run, dict) or not valid_financial_intelligence_run_id(str(run.get('run_id') or '')):
        return False
    try:
        require_financial_run_authority(headers, 'package.inspect', run)
        return True
    except (PermissionError, OSError, ValueError, TypeError):
        return False


BLUEPRINT_UPLOAD_PERMISSION = "package.upload"
BLUEPRINT_INSPECT_PERMISSION = "package.inspect"
BLUEPRINT_REVIEW_PERMISSION = "package.review"
BLUEPRINT_PROMOTE_PERMISSION = "candidate.promote"
BLUEPRINT_IMPORT_ADMIN_ROLE = "blueprint_import_admin"
CIOS_OWNER_ROLE = "cios_owner"
CANONICAL_OWNER_ROLES = frozenset({CIOS_OWNER_ROLE, "owner", "workspace.owner", "workspace_owner"})

BLUEPRINT_IMPORT_OWNER_PERMISSIONS = frozenset({
    BLUEPRINT_UPLOAD_PERMISSION,
    BLUEPRINT_INSPECT_PERMISSION,
    BLUEPRINT_REVIEW_PERMISSION,
    BLUEPRINT_PROMOTE_PERMISSION,
    BLUEPRINT_IMPORT_ADMIN_ROLE,
})
_BLUEPRINT_IMPORT_ROLES = {BLUEPRINT_IMPORT_ADMIN_ROLE, BLUEPRINT_UPLOAD_PERMISSION}

COMMERCIAL_CONTEXT_VIEW = "commercial_context.view"
COMMERCIAL_CONTEXT_EDIT = "commercial_context.edit"
PILOT_COMMERCIAL_CONTEXT_CAPABILITIES = frozenset({
    COMMERCIAL_CONTEXT_VIEW,
    COMMERCIAL_CONTEXT_EDIT,
})
PILOT_COMMERCIAL_CONTEXT_OWNER = PILOT_IMPORT_ACTOR
COMMERCIAL_CONTEXT_SCOPE_CLASS = "commercial-context"


@dataclass(frozen=True)
class CommercialContextAuthorisationDecision:
    actor_id: str
    context_scope: str
    required_capability: str
    decision: str
    failed_stage: str = ""
    denial_reason: str = ""
    effective_capabilities: tuple[str, ...] = ()
    scope_class: str = COMMERCIAL_CONTEXT_SCOPE_CLASS
    expected_scope_class: str = COMMERCIAL_CONTEXT_SCOPE_CLASS


def commercial_context_owner(headers: Any) -> str:
    return active_flora_workspace(headers)


def commercial_context_actor(headers: Any) -> str:
    return authenticated_flora_user(headers)


def commercial_context_authorisation(
    headers: Any, required_capability: str, context_scope: str,
) -> CommercialContextAuthorisationDecision:
    """Authorise only view/edit of the actor's commercial profile scope."""
    pilot = pilot_import_bypass_enabled()
    actor = commercial_context_actor(headers)
    scope = commercial_context_owner(headers)
    roles = raw_flora_roles(headers) if actor and not pilot else set()
    allowed_capability = required_capability in PILOT_COMMERCIAL_CONTEXT_CAPABILITIES
    owns_scope = bool(scope and context_scope and canonical_enterprise_id(scope) == canonical_enterprise_id(context_scope))
    capabilities = (set(PILOT_COMMERCIAL_CONTEXT_CAPABILITIES) if pilot else
                    set(PILOT_COMMERCIAL_CONTEXT_CAPABILITIES) if roles & CANONICAL_OWNER_ROLES else
                    roles & set(PILOT_COMMERCIAL_CONTEXT_CAPABILITIES))
    has_capability = required_capability in capabilities
    if not actor:
        stage, reason = "actor resolution", "missing authenticated Flora user"
    elif not scope or not context_scope:
        stage, reason = "scope resolution", "commercial-context scope is unavailable"
    elif not owns_scope:
        stage, reason = "scope isolation", "actor does not own the requested commercial-context scope"
    elif not allowed_capability or not has_capability:
        stage, reason = "capability check", f"missing {required_capability}"
    else:
        stage = reason = ""
    return CommercialContextAuthorisationDecision(
        actor, scope, required_capability, "allowed" if not stage else "denied", stage, reason,
        tuple(sorted(capabilities)),
    )


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
    context = verified_context(headers)
    return set(context.roles) if context else set()


def role_capabilities(roles) -> frozenset[str]:
    """Project the existing owner/admin policy; never establish membership.

    The same projection bounds server snapshots and service role evaluation.
    Blueprint administrators inherit Blueprint operations, not owner identity,
    commercial profile administration or the separate storage-recovery grant.
    """
    capabilities = set(roles)
    if capabilities & CANONICAL_OWNER_ROLES:
        capabilities |= BLUEPRINT_IMPORT_OWNER_PERMISSIONS | PILOT_COMMERCIAL_CONTEXT_CAPABILITIES
    elif BLUEPRINT_IMPORT_ADMIN_ROLE in capabilities:
        capabilities |= BLUEPRINT_IMPORT_OWNER_PERMISSIONS
    return frozenset(capabilities)


def flora_roles(headers: Any) -> set[str]:
    roles = raw_flora_roles(headers)
    if authenticated_flora_user(headers) and active_workspace_membership(headers):
        roles |= role_capabilities(roles)
        if roles & CANONICAL_OWNER_ROLES:
            roles.add(CIOS_OWNER_ROLE)
    return roles


def is_cios_owner(headers: Any) -> bool:
    return bool(authenticated_flora_user(headers) and active_flora_workspace(headers) and raw_flora_roles(headers) & CANONICAL_OWNER_ROLES)


def active_workspace_membership(headers: Any):
    """Consume a server-verified membership projection, never enterprise grants."""
    context = verified_context(headers)
    membership = getattr(context, "membership", None)
    if context is None or membership is None or not membership.active:
        return None
    if (membership.user_id != context.user_id or membership.workspace_id != context.workspace
            or context.workspace not in context.workspace_ids):
        return None
    return membership


def blueprint_upload_authorisation(headers: Any) -> BlueprintAuthorisationDecision:
    user = authenticated_flora_user(headers)
    auth_source = flora_authentication_source(headers)
    context = verified_context(headers)
    workspaces = tuple(sorted(context.workspace_ids)) if context and user else ()
    active_workspace = active_flora_workspace(headers) if user else ""
    raw_roles = raw_flora_roles(headers) if user and active_workspace else set()
    roles = flora_roles(headers) if user and active_workspace else set()
    permissions = sorted(roles & BLUEPRINT_IMPORT_OWNER_PERMISSIONS)
    membership_resolved = bool(user and active_workspace and active_workspace_membership(headers))
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


def can_access_enterprise(headers: Any, enterprise_id: str, workspace_id: str = "") -> bool:
    if not authenticated_flora_user(headers):
        return False
    allowed = user_enterprise_access(headers)
    # A resource's explicit workspace boundary is checked before broad enterprise
    # grants. A wildcard does not select or authorise another workspace.
    if workspace_id and workspace_id != active_flora_workspace(headers):
        return False
    if "*" in allowed or _contains_id(allowed, enterprise_id):
        return True
    return False


def require_capability(headers: Any, capability: str, enterprise_id: str = "", workspace_id: str = ""):
    """Service-entry guard using the existing capability and resource policy."""
    context = require_verified_human(headers)
    if not context.verified_human or active_workspace_membership(headers) is None:
        raise PermissionError("Active workspace membership is unavailable")
    roles = flora_roles(headers)
    if (capability not in context.effective_capabilities
            or (capability not in roles and capability != "storage.recover" and not (capability == "package.review" and "blueprint_import_admin" in roles))):
        raise PermissionError("Required capability is unavailable")
    if enterprise_id and not can_access_enterprise(headers, enterprise_id, workspace_id):
        raise PermissionError("Resource unavailable")
    return context


def require_resource_scope(headers: Any, capability: str, enterprise_id: str,
                           workspace_id: str, *, require_acl: bool = True):
    """Intersect existing policy with authoritative resource scope and ACL.

    Identifiers here must come from a loaded server record, never a form. This
    helper supplies missing scope to the existing evaluator; it defines no roles
    or alternate permission policy. Unscoped historical records remain closed.
    """
    context = require_capability(headers, capability)
    membership = active_workspace_membership(headers)
    if (not context.verified_human or membership is None
            or not isinstance(workspace_id, str) or not workspace_id
            or workspace_id != workspace_id.strip() or workspace_id == '*'
            or workspace_id != context.workspace
            or not isinstance(enterprise_id, str) or not enterprise_id
            or enterprise_id != enterprise_id.strip() or enterprise_id == '*'):
        raise PermissionError('Resource unavailable')
    require_capability(headers, capability, enterprise_id, workspace_id)
    from .enterprise_canvas.access import EnterpriseCanvasAccessRepository, can_access_canvas_record
    record = EnterpriseCanvasAccessRepository().get(enterprise_id)
    if (require_acl or record is not None) and not can_access_canvas_record(headers, enterprise_id, workspace_id):
        raise PermissionError('Resource unavailable')
    return context


def require_financial_run_authority(headers: Any, capability: str, run: dict[str, Any]):
    """Require one unambiguous persisted workspace and Enterprise binding."""
    document = run.get('document', {})
    if not isinstance(document, dict):
        raise PermissionError('Resource unavailable')
    workspace = run.get('workspace_id')
    enterprises = [value for value in (run.get('enterprise_id'), document.get('enterprise_id')) if value is not None]
    if (not enterprises or any(not isinstance(v, str) or not v for v in enterprises)
            or len(set(enterprises)) != 1
            or ('workspace_id' in document and document['workspace_id'] != workspace)):
        raise PermissionError('Resource unavailable')
    claims = run.get('claims', [])
    if not isinstance(claims, list):
        raise PermissionError('Resource unavailable')
    for claim in claims:
        if (not isinstance(claim, dict)
                or ('workspace_id' in claim and claim['workspace_id'] != workspace)
                or any(key in claim and claim[key] != enterprises[0]
                       for key in ('enterprise_id', 'canonical_enterprise_id'))):
            raise PermissionError('Resource unavailable')
    return require_resource_scope(headers, capability, enterprises[0], workspace)
