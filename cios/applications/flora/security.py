"""Verified, revocable server-stored authority; caller projections confer none."""
from __future__ import annotations
from typing import Any
from contextvars import ContextVar

_SERVICE_WRITE = ContextVar("flora_verified_service_write", default=())
from .verified_context_contract import VerifiedContext
from .public_routes import public_read_path, public_request_target, public_route_catalog

ACCESS_UNAVAILABLE = "Sign in and select an authorised workspace. Access is unavailable or your session has expired."


def verified_context(headers: Any = None) -> VerifiedContext | None:
    """Resolve only a server-stored opaque session; storage errors deny authority."""
    from .security_store import SecurityStore, cookie_token
    import sqlite3
    token = cookie_token(headers)
    if not token:
        return None
    try:
        return SecurityStore().resolve(token)
    except (OSError, sqlite3.Error, PermissionError, ValueError, KeyError, TypeError):
        return None


def require_verified_human(headers: Any = None) -> VerifiedContext:
    context = verified_context(headers)
    if context is None:
        raise PermissionError(ACCESS_UNAVAILABLE)
    return context


def require_service_capability(headers, capabilities):
    """Select an existing allowed capability through the canonical evaluator."""
    from .access import require_capability
    choices = (capabilities,) if isinstance(capabilities, str) else capabilities
    for capability in choices:
        try:
            return require_capability(headers, capability)
        except PermissionError:
            continue
    raise PermissionError('Required capability is unavailable')


def require_active_service_write(headers, capabilities):
    """Require the existing audited write envelope; supplies no new authority."""
    from .security_store import Context, SecurityStore, _ACTIVE
    context = require_service_capability(headers, capabilities)
    if isinstance(context, Context):
        active = _ACTIVE.get()
        if (not active or active[0] != SecurityStore().path or not active[1].in_transaction
                or context.session.session_ref not in _SERVICE_WRITE.get()):
            raise PermissionError('Verified service write transaction required')
    return context


def verified_service_write(capability: str | tuple[str, ...], *, denial_error=PermissionError, recent=False):
    """Serialize real authority changes with a whole consequential service call.

    The resolver is the only producer. Protocol shape is never used as proof.
    Existing explicit unit-test doubles remain unit tests, not session evidence.
    """
    from functools import wraps
    import inspect
    def decorate(function):
        signature = inspect.signature(function)
        @wraps(function)
        def guarded(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            headers = bound.arguments.get('headers')
            from .security_store import SecurityStore, Context, cookie_token, RECENT
            import time
            def authorize():
                try:
                    return require_service_capability(headers, capability)
                except PermissionError as exc:
                    if isinstance(exc, denial_error):
                        raise
                    raise denial_error(str(exc)) from exc
            context = authorize()
            def execute():
                current = authorize()
                if (recent or capability in {'candidate.promote','storage.recover'}) and isinstance(current, Context):
                    if time.time() - current.session.authenticated_at.timestamp() > RECENT:
                        raise denial_error('Recent authentication required')
                try:
                    return function(*args, **kwargs)
                except PermissionError as exc:
                    if isinstance(exc, denial_error):
                        raise
                    raise denial_error(str(exc)) from exc
            if isinstance(context, Context):
                with SecurityStore().transaction() as db:
                    current = authorize()
                    from .protected_storage import ProtectedJournal
                    ProtectedJournal(SecurityStore()).begin(db)
                    SecurityStore().audit(db,'service_authorized',operation=function.__qualname__,
                        user_id=current.user_id,workspace_id=current.workspace,
                        membership_id=current.membership.membership_id,membership_version=current.membership.version,
                        session_ref=current.session.session_ref)
                    scope = _SERVICE_WRITE.set(_SERVICE_WRITE.get() + (current.session.session_ref,))
                    try:
                        result = execute()
                        authorize()
                        SecurityStore().resolve(cookie_token(headers), touch=True)
                        return result
                    finally:
                        _SERVICE_WRITE.reset(scope)
            return execute()
        return guarded
    return decorate


def verified_service_read(capability: str | tuple[str, ...]):
    """Keep real authority/recovery and the entire resource render serialised."""
    from functools import wraps
    import inspect
    from contextlib import nullcontext
    def decorate(function):
        signature = inspect.signature(function)
        @wraps(function)
        def guarded(*args, **kwargs):
            from .security_store import Context, SecurityStore
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            headers = bound.arguments.get('headers')
            context = require_service_capability(headers, capability)
            with SecurityStore().transaction() if isinstance(context, Context) else nullcontext():
                require_service_capability(headers, capability)
                return function(*args, **kwargs)
        return guarded
    return decorate
