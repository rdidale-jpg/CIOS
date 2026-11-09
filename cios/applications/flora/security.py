"""Closed authentication boundary for Security Repair 01A.

There is intentionally no identity/session issuer in this increment. Repair 01B
must supply verified, revocable, server-controlled membership before this seam
can resolve a principal. Cookies, headers, flags and caller objects never do so.
"""
from __future__ import annotations
from typing import Any
from .verified_context_contract import VerifiedContext
from .public_routes import public_read_path, public_request_target, public_route_catalog

ACCESS_UNAVAILABLE = "Verified owner access is not available. Privileged operations are disabled pending Security Repair 01B."


def verified_context(headers: Any = None) -> VerifiedContext | None:
    """No verified authentication boundary is installed in Repair 01A."""
    return None


def require_verified_human(headers: Any = None) -> VerifiedContext:
    context = verified_context(headers)
    if context is None:
        raise PermissionError(ACCESS_UNAVAILABLE)
    return context
