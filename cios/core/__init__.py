"""Core primitives for the CIOS SDK.

The core package owns foundational identifiers, common types, validation helpers,
and thin Pydantic data models. It must remain free of imports from other CIOS
packages to preserve the platform dependency model.
"""

from cios.core.identifiers import generate_identifier
from cios.core.models import Capability, Decision, Entity, Evidence, Observation, Opportunity, Recommendation, Relationship
from cios.core.types import ConfidenceLevel, DecisionStatus, EvidenceKind, RecommendationStatus
from cios.core.validation import utc_now

__all__ = [
    "Capability",
    "ConfidenceLevel",
    "Decision",
    "DecisionStatus",
    "Entity",
    "Evidence",
    "EvidenceKind",
    "Observation",
    "Opportunity",
    "Recommendation",
    "RecommendationStatus",
    "Relationship",
    "generate_identifier",
    "utc_now",
]
