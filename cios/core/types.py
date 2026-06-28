"""Common type definitions for CIOS core models.

This module contains small, stable enumerations shared by Sprint 1 data models.
It has no dependencies on other CIOS modules, preserving ``cios.core`` as the
bottom layer of the SDK dependency graph.
"""

from __future__ import annotations

from enum import StrEnum


class ConfidenceLevel(StrEnum):
    """Qualitative confidence assigned to evidence, observations, or outputs."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceKind(StrEnum):
    """Supported categories of source material for Sprint 1 evidence records."""

    DOCUMENT = "document"
    URL = "url"
    NOTE = "note"
    DATA = "data"


class RecommendationStatus(StrEnum):
    """Lifecycle status for a proposed recommendation."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class DecisionStatus(StrEnum):
    """Lifecycle status for a decision record."""

    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
