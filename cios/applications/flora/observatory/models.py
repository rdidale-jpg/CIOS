"""Explainable models for the Enterprise Transformation Observatory."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class HypothesisStatus(str, Enum):
    EMERGING = "Emerging"
    STRENGTHENING = "Strengthening"
    VALIDATED = "Validated"
    CONTRADICTED = "Contradicted"
    NEEDS_MORE_EVIDENCE = "Needs More Evidence"


@dataclass(frozen=True)
class ObservatoryEvidence:
    evidence_id: str
    evidence_class: str
    evidence_quality: str
    evidence_freshness: str
    organisation: str
    sector: str
    transformation_theme: str
    transformation_dimension: str
    commercial_question_supported: str
    summary: str
    source_name: str
    source_url: str
    confidence: int
    unknowns: tuple[str, ...]
    evidence_lineage: tuple[str, ...]


@dataclass(frozen=True)
class ForceAssessment:
    name: str
    state: str
    reasoning: str
    evidence_ids: tuple[str, ...]
    confidence: int
    unknowns: tuple[str, ...] = ()
    contradictory_evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class GenomeDimension:
    pillar: str
    name: str
    hypothesis: str
    confidence: int
    reasoning: str
    supporting_evidence_ids: tuple[str, ...]
    unknowns: tuple[str, ...]
    evidence_quality: str
    contradictory_evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategicConviction:
    observed_facts: tuple[str, ...]
    commercial_interpretation: str
    transformation_hypothesis: str
    confidence: int
    unknowns: tuple[str, ...]
    recommended_commercial_action: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class CaseForChange:
    organisation: str
    why_act: str
    why_now: str
    why_ai: str
    why_cloud: str
    why_secure_by_design: str
    why_this_transformation: str
    cost_of_waiting: str
    commercial_risks: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    contradictory_evidence_ids: tuple[str, ...]
    unknowns: tuple[str, ...]
    confidence: int
    conversation_level: str
    conversation_elevation_reason: str


@dataclass(frozen=True)
class TransformationWindow:
    organisation: str
    estimated_window: str
    momentum: str
    evidence_confidence: int
    primary_drivers: tuple[str, ...]
    primary_constraints: tuple[str, ...]
    reasoning: str


@dataclass(frozen=True)
class ResearchHypothesis:
    hypothesis_id: str
    title: str
    status: HypothesisStatus
    supporting_evidence_ids: tuple[str, ...]
    contradictory_evidence_ids: tuple[str, ...]
    confidence: int
    last_updated: str
    commercial_implications: str


@dataclass(frozen=True)
class KnowledgeGraphEdge:
    source: str
    relationship: str
    target: str
    evidence_ids: tuple[str, ...]
    inferred: bool = False
    reasoning: str = ""
    confidence: int = 0


@dataclass(frozen=True)
class OrganisationObservatory:
    organisation: str
    sector: str
    genome: tuple[GenomeDimension, ...]
    forces: tuple[ForceAssessment, ...]
    strategic_urgency: ForceAssessment
    transformation_window: TransformationWindow
    conviction: StrategicConviction
    case_for_change: CaseForChange


@dataclass(frozen=True)
class EnterpriseWeather:
    transformation_pressure: str
    transformation_momentum: str
    accelerating_sectors: tuple[str, ...]
    emerging_transformation_themes: tuple[str, ...]
    transformation_tipping_points: tuple[str, ...]
    cross_sector_observations: tuple[str, ...]
    most_significant_evidence_today: tuple[str, ...]


@dataclass(frozen=True)
class Observatory:
    critique_path: str
    evidence: tuple[ObservatoryEvidence, ...]
    organisations: tuple[OrganisationObservatory, ...]
    weather: EnterpriseWeather
    hypotheses: tuple[ResearchHypothesis, ...]
    graph_edges: tuple[KnowledgeGraphEdge, ...] = field(default_factory=tuple)
