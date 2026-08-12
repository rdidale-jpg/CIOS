"""Shared, governed vocabulary and rules for normal executive projections.

This contract changes presentation only.  It never establishes relationships,
changes candidate facts, or grants promotion/recommendation authority.
"""
from __future__ import annotations

ALLOWED_CONTENT_TYPES = (
    "facts", "evidence summaries", "unknowns", "contradictions", "relationships",
    "human review state", "promotion state", "assessment state", "recommendation state",
)
PROHIBITED_TECHNICAL_TERMS = (
    "runtime fingerprint", "adapter version", "semantic constructor", "python module",
    "confidence_model", "canonical read-model", "raw json",
)
FACT_STATES = (
    "Present and sufficient", "Present but incomplete", "Present but unsupported",
    "Known Unknown — further evidence required", "Contradicted", "Not supplied",
    "Assessment not yet performed", "Not applicable",
)
EMPTY_STATES = {
    "facts": "Not supplied",
    "unknown": "No explicit Unknown supplied",
    "contradiction": "No explicit Contradiction supplied",
    "assessment": "Assessment not yet performed",
}


def plural(count: int, singular: str, plural_form: str | None = None) -> str:
    return singular if count == 1 else (plural_form or singular + "s")


def review_label(review: dict | None) -> str:
    return "Reviewed by Chief Architect" if review else "Imported candidate — not yet reviewed"


def promotion_label(promoted: bool) -> str:
    return "Promoted" if promoted else "Not promoted"


def fact_state(*, present: bool, complete: bool = False, supported: bool = True,
               unknown: bool = False, contradicted: bool = False) -> str:
    if contradicted:
        return "Contradicted"
    if unknown:
        return "Known Unknown — further evidence required"
    if not present:
        return "Not supplied"
    if not supported:
        return "Present but unsupported"
    return "Present and sufficient" if complete else "Present but incomplete"

