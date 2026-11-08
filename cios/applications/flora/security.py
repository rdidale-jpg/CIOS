"""Closed authentication boundary for Security Repair 01A.

There is intentionally no identity/session issuer in this increment. Repair 01B
must supply verified, revocable, server-controlled membership before this seam
can resolve a principal. Cookies, headers, flags and caller objects never do so.
"""
from __future__ import annotations
from typing import Any

ACCESS_UNAVAILABLE = "Verified owner access is not available. Privileged operations are disabled pending Security Repair 01B."


def verified_context(headers: Any = None):
    """No verified authentication boundary is installed in Repair 01A."""
    return None


def require_verified_human(headers: Any = None):
    context = verified_context(headers)
    if context is None:
        raise PermissionError(ACCESS_UNAVAILABLE)
    return context


def public_read_path(path: str) -> bool:
    """Explicit source-curated public routes; protected routes default closed.

    Avoid prefix exemptions for user IDs, package IDs, files or arbitrary data.
    These Banking views project repository-curated context only.
    """
    if path.startswith(("/flora/banking/", "/evidence/", "/flora/object/BK-ENT-001/lineage/")):
        # These handlers read repository Banking source projections, never a
        # caller-selected import, Evidence repository or Enterprise Model.
        return True
    return path in {
        "/health", "/deployment", "/", "/flora", "/flora/", "/intelligence",
        "/digital-twins", "/blueprint-import", "/pilot-sign-in",
        "/opportunities", "/research", "/workspace/reference", "/flora/reference",
        "/flora/banking", "/flora/banking/", "/flora/banking/inspect",
        "/industries/uk-banking", "/explore", "/focus", "/shape", "/governance", "/ask",
        "/shape/banking", "/shape/strategic-sales-brief", "/shape/banking/strategic-sales-brief",
        "/flora/lloyds", "/flora/object/BK-ENT-001", "/flora/object/BK-ENT-001/explain",
        "/flora/object/BK-ENT-001/context-package", "/workspace/enterprise/BK-ENT-001",
    }
