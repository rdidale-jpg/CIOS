"""Validation helpers for CIOS core data models.

The helpers in this module intentionally stay small and reusable. They express
cross-model validation rules without creating service abstractions or importing
from non-core CIOS modules.
"""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""

    return datetime.now(UTC)


def require_non_empty(value: str, field_name: str) -> str:
    """Validate that a string field contains non-whitespace content.

    Args:
        value: The string value to validate.
        field_name: Human-readable field name for error messages.

    Returns:
        The stripped string value.

    Raises:
        ValueError: If ``value`` is empty after trimming whitespace.
    """

    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(f"{field_name} must not be empty")
    return normalized_value

