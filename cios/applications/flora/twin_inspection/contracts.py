"""Presentation-only contracts for the Twin Inspection Shell."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class MaterialConclusion:
    """Presentation reference to an owner-backed conclusion, never a stored claim."""
    conclusion_id: str
    statement: str
    truth_class: str
    commercial_consequence: str
    support_summary: str
    challenge_summary: str
    evidence_target: str
    lineage_target: str
    confidence: str = "Not supplied"
    freshness: str = "Not supplied"

@dataclass(frozen=True)
class InspectionSection:
    key: str
    label: str
    order: int
    provider: Callable[[], str]
    truth_class: str
    availability: bool
    authorization: bool
    lineage_target: str
    freshness: str
    effective_date: str

@dataclass(frozen=True)
class InspectionProfile:
    identity: str
    twin_type: str
    canonical_owner: str
    status: str
    version: str
    last_refresh: str
    source_cut_off: str
    research_maturity: str
    commercial_maturity: str
    evidence_coverage: str
    evidence_freshness: str
    confidence: str
    unknowns: str
    contradictions: str
    package_lineage: str

@dataclass(frozen=True)
class InspectionAdapter:
    adapter_key: str
    profile: InspectionProfile
    sections: tuple[InspectionSection, ...]
    conclusions: tuple[MaterialConclusion, ...] = ()
    context: str = "governed"
