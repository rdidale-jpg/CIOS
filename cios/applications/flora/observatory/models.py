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
    source_type: str = "unknown"
    mapped_condition: str = "Unmapped"
    mapped_capability: str = "AI opportunity discovery"
    extraction_timestamp: str = ""
    is_live: bool = False


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
class CommercialSignal:
    signal_id: str
    organisation: str
    title: str
    observation: str
    evidence_quote: str
    commercial_meaning: str
    transformation_dimensions: tuple[str, ...]
    board_questions_supported: tuple[str, ...]
    supports: tuple[str, ...]
    does_not_support: tuple[str, ...]
    signal_type: str
    signal_quality_score: int
    signal_strength: str
    freshness: str
    missing_evidence: tuple[str, ...]
    classification: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    source_url: str
    confidence: int


@dataclass(frozen=True)
class CommercialInsight:
    insight_id: str
    organisation: str
    summary: str
    supporting_signal_ids: tuple[str, ...]
    contradictory_signal_ids: tuple[str, ...]
    unknowns: tuple[str, ...]
    confidence: int
    hypothesis_type: str = "multi-signal insight"


@dataclass(frozen=True)
class CommercialArgument:
    argument_id: str
    organisation: str
    question_answered: str
    claim: str
    supporting_insight_ids: tuple[str, ...]
    supporting_signal_ids: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    counterarguments: tuple[str, ...]
    unknowns: tuple[str, ...]
    confidence: int
    commercial_implication: str
    recommended_executive_audience: str


@dataclass(frozen=True)
class ExecutiveRecommendation:
    recommendation_id: str
    organisation: str
    recommendation: str
    supporting_argument_ids: tuple[str, ...]
    confidence: int


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
    key_facts: list[dict[str, str]] = field(default_factory=list)
    evidence_strength: dict[str, object] = field(default_factory=dict)
    transformation_timeline: list[dict[str, str]] = field(default_factory=list)
    cost_of_waiting_categories: list[dict[str, object]] = field(default_factory=list)
    counterarguments: tuple[str, ...] = ()
    commercial_signals: tuple[CommercialSignal, ...] = ()
    commercial_insights: tuple[CommercialInsight, ...] = ()
    commercial_arguments: tuple[CommercialArgument, ...] = ()
    executive_recommendation: ExecutiveRecommendation | None = None
    enterprise_profile: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EnterpriseWeather:
    transformation_pressure: str
    transformation_momentum: str
    accelerating_sectors: tuple[str, ...]
    emerging_transformation_themes: tuple[str, ...]
    transformation_tipping_points: tuple[str, ...]
    cross_sector_observations: tuple[str, ...]
    most_significant_evidence_today: tuple[str, ...]
    total_live_evidence_objects: int = 0
    total_organisations_covered: int = 0
    evidence_coverage_by_sector: dict[str, int] = field(default_factory=dict)
    evidence_coverage_by_class: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Observatory:
    critique_path: str
    evidence: tuple[ObservatoryEvidence, ...]
    organisations: tuple[OrganisationObservatory, ...]
    weather: EnterpriseWeather
    hypotheses: tuple[ResearchHypothesis, ...]
    graph_edges: tuple[KnowledgeGraphEdge, ...] = field(default_factory=tuple)
    commercial_signals: tuple[CommercialSignal, ...] = field(default_factory=tuple)
    commercial_insights: tuple[CommercialInsight, ...] = field(default_factory=tuple)
    commercial_arguments: tuple[CommercialArgument, ...] = field(default_factory=tuple)
    executive_recommendations: tuple[ExecutiveRecommendation, ...] = field(default_factory=tuple)
