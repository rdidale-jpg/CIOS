"""Identifier helpers for CIOS core models.

Sprint 1 uses opaque, prefixed UUID-based string identifiers. Keeping identifier
creation in this module avoids model-level duplication while remaining simple,
deterministic in shape, and independent of external services.
"""

from __future__ import annotations

from uuid import uuid4

_IDENTIFIER_SEPARATOR = "_"


def generate_identifier(prefix: str) -> str:
    """Return a globally unique identifier with a human-readable prefix.

    Args:
        prefix: Short model or concept prefix, such as ``"entity"``.

    Returns:
        A string in the form ``"<prefix>_<uuid4-hex>"``.

    Raises:
        ValueError: If ``prefix`` is blank or contains non-alphanumeric
            characters other than underscores and hyphens.
    """

    normalized_prefix = prefix.strip().lower()
    if not normalized_prefix:
        raise ValueError("identifier prefix must not be blank")
    if not all(character.isalnum() or character in {"_", "-"} for character in normalized_prefix):
        raise ValueError("identifier prefix may contain only letters, numbers, underscores, or hyphens")
    return f"{normalized_prefix}{_IDENTIFIER_SEPARATOR}{uuid4().hex}"
