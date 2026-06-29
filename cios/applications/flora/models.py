"""Pydantic models for Flora AI Reinvention Intelligence v0.1."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Watchlist priority bands."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CommercialDNA(BaseModel):
    """Commercial configuration describing the user's market position."""

    employer: str
    business_unit: str
    sectors: list[str] = Field(default_factory=list)
    strategic_offerings: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    differentiators: list[str] = Field(default_factory=list)
    reference_clients: list[str] = Field(default_factory=list)
    target_geographies: list[str] = Field(default_factory=list)


class TargetAccount(BaseModel):
    """A target organisation to monitor for AI reinvention signals."""

    organisation_name: str
    sector: str
    priority: Priority
    notes: str
    known_incumbents: list[str] = Field(default_factory=list)
    known_competitors: list[str] = Field(default_factory=list)


class Signal(BaseModel):
    """A seeded intelligence signal used by Flora v0.1 scoring."""

    signal_id: str
    source: str
    source_type: str
    organisation: str
    sector: str
    signal_category: str
    signal_summary: str
    evidence_text: str
    confidence: int = Field(ge=0, le=100)
    strength: int = Field(ge=0, le=100)
    freshness: int = Field(ge=0, le=100)
    detected_date: date
    related_capabilities: list[str] = Field(default_factory=list)


class ReinventionScores(BaseModel):
    """Deterministic AI reinvention indices for one organisation."""

    commercial_pressure_index: int = Field(ge=0, le=100)
    ai_suitability_index: int = Field(ge=0, le=100)
    organisational_readiness_index: int = Field(ge=0, le=100)
    commercial_attractiveness_index: int = Field(ge=0, le=100)
    influence_potential_index: int = Field(ge=0, le=100)
    ai_reinvention_opportunity_score: int = Field(ge=0, le=100)


class BriefingItem(BaseModel):
    """A ranked organisation entry in the Flora Daily Intelligence Brief."""

    rank: int
    organisation: str
    sector: str
    scores: ReinventionScores
    why_interesting: str
    strongest_detected_signals: list[str] = Field(default_factory=list)
    likely_capability_areas: list[str] = Field(default_factory=list)
    main_competitors_to_watch: list[str] = Field(default_factory=list)
    recommended_next_action: str


class DailyBrief(BaseModel):
    """The complete Flora Daily Intelligence Brief."""

    title: str = "Flora Daily Intelligence Brief"
    version: Literal["0.1"] = "0.1"
    generated_for: str
    business_unit: str
    target_geographies: list[str] = Field(default_factory=list)
    items: list[BriefingItem] = Field(default_factory=list)
