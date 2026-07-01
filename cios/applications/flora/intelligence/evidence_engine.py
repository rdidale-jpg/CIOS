"""Governed seeded commercial evidence for Flora case files.

No live collection, external APIs, databases or LLM reasoning are used here.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Protocol

from pydantic import BaseModel, Field


class EvidenceCategory(str, Enum):
    ANNUAL_REPORT = "Annual Report"
    INVESTOR_PRESENTATION = "Investor Presentation"
    RESULTS_ANNOUNCEMENT = "Results Announcement"
    REGULATORY_PUBLICATION = "Regulatory Publication"
    EXECUTIVE_APPOINTMENT = "Executive Appointment"
    STRATEGY_UPDATE = "Strategy Update"
    COMPANY_NEWS = "Company News"
    INDUSTRY_NEWS = "Industry News"
    HIRING_SIGNAL = "Hiring Signal"
    TECHNOLOGY_INVESTMENT = "Technology Investment"
    CUSTOMER_SIGNAL = "Customer Signal"


class EvidenceSourceAttribution(BaseModel):
    """Named source attribution retained with every evidence claim."""

    source_name: str
    source_type: str
    source_url: str | None = None
    publication_date: date | None = None
    freshness_note: str = "Publication date recorded; refresh cadence not yet verified."


class EvidenceRichnessMetrics(BaseModel):
    """Evidence-depth metrics that complement calibrated confidence."""

    source_count: int = Field(default=1, ge=0)
    independent_source_count: int = Field(default=1, ge=0)
    quantitative_fact_count: int = Field(default=0, ge=0)
    quote_count: int = Field(default=0, ge=0)
    competitor_comparison_count: int = Field(default=0, ge=0)
    benchmark_count: int = Field(default=0, ge=0)
    timeline_event_count: int = Field(default=1, ge=0)
    freshness_score: int = Field(default=70, ge=0, le=100)
    corroboration_score: int = Field(default=35, ge=0, le=100)
    traceability_score: int = Field(default=80, ge=0, le=100)

    @property
    def evidence_richness_score(self) -> int:
        breadth = min(25, self.source_count * 8 + self.independent_source_count * 5)
        substance = min(30, self.quantitative_fact_count * 6 + self.quote_count * 4)
        context = min(20, self.competitor_comparison_count * 7 + self.benchmark_count * 6 + self.timeline_event_count * 2)
        governance = round((self.freshness_score + self.corroboration_score + self.traceability_score) / 12)
        return min(100, breadth + substance + context + governance)


class EvidenceReasoningDossier(BaseModel):
    """Structured dossier separating facts, interpretation, hypotheses, implications and actions."""

    observed_facts: list[str] = Field(default_factory=list)
    quantitative_facts: list[str] = Field(default_factory=list)
    named_sources: list[EvidenceSourceAttribution] = Field(default_factory=list)
    executive_quotes: list[str] = Field(default_factory=list)
    strategic_messages: list[str] = Field(default_factory=list)
    competitor_comparisons: list[str] = Field(default_factory=list)
    sector_benchmarks: list[str] = Field(default_factory=list)
    transformation_timeline: list[str] = Field(default_factory=list)
    interpretation: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    implications: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    evidence_freshness: str = "Publication date captured; monitor for newer filings, news and regulator updates."
    expected_update_frequency: str = "Refresh during daily live collection and before customer-facing use."
    independent_corroboration: str = "Single-source until supported by another named source."
    calibrated_confidence: int = Field(default=70, ge=0, le=100)
    richness: EvidenceRichnessMetrics = Field(default_factory=EvidenceRichnessMetrics)


class CommercialEvidence(BaseModel):
    evidence_id: str
    organisation: str
    evidence_type: str
    evidence_category: EvidenceCategory
    source_name: str
    source_type: str
    publication_date: date
    title: str
    summary: str
    extracted_observation: str
    confidence: int = Field(ge=0, le=100, description="Calibrated confidence, not a substitute for evidence richness.")
    freshness: int = Field(ge=0, le=100)
    dossier: EvidenceReasoningDossier | None = Field(default=None, description="Structured evidence dossier for depth, traceability and reasoning separation.")
    related_signals: list[str] = Field(default_factory=list)
    related_patterns: list[str] = Field(default_factory=list)
    related_playbooks: list[str] = Field(default_factory=list)
    related_propositions: list[str] = Field(default_factory=list)
    capability_tags: list[str] = Field(default_factory=list)
    executive_tags: list[str] = Field(default_factory=list)
    sector_tags: list[str] = Field(default_factory=list)


class EvidenceConnector(Protocol):
    """Future dependency-injection contract for live evidence providers."""

    connector_name: str

    def collect(self, organisation: str) -> list[CommercialEvidence]:
        """Return governed evidence for one organisation."""


class AnnualReportConnector(EvidenceConnector, Protocol):
    pass


class InvestorPresentationConnector(EvidenceConnector, Protocol):
    pass


class RegulatorConnector(EvidenceConnector, Protocol):
    pass


class CompanyNewsConnector(EvidenceConnector, Protocol):
    pass


class HiringSignalConnector(EvidenceConnector, Protocol):
    pass


def _seed_dossier(org: str, category: EvidenceCategory, title: str, summary: str, observation: str, caps: list[str], sector: str, confidence: int, freshness: int) -> EvidenceReasoningDossier:
    richness = EvidenceRichnessMetrics(source_count=1, independent_source_count=1, timeline_event_count=1, freshness_score=freshness, corroboration_score=35, traceability_score=85)
    return EvidenceReasoningDossier(
        observed_facts=[f"{org}: {summary}", observation],
        quantitative_facts=["No public quantitative value captured in seeded evidence; quantify budget, capex, customers, employees, deadlines or programme size during live research."],
        named_sources=[EvidenceSourceAttribution(source_name=f"Seeded {category.value}", source_type="seed", publication_date=date(2026, 1, 1), freshness_note="Seeded public-domain theme; replace with live named source before external use.")],
        strategic_messages=[title],
        competitor_comparisons=["Competitor and incumbent comparison not yet evidenced; validate against awards, partner announcements and procurement notices."],
        sector_benchmarks=[f"Compare against {sector} playbook pressures for resilience, cost, customer and regulatory performance."],
        transformation_timeline=[f"2026 seeded {category.value}: {title}"],
        interpretation=[f"The evidence points to {', '.join(caps[:2]) if caps else 'AI transformation'} as a plausible discussion theme."],
        hypotheses=["Transformation pressure may be increasing, but buying intent is unproven without sponsor, funding and timing evidence."],
        implications=["Use as preparation context rather than proof of active demand."],
        recommended_actions=["Find independently corroborating named sources and quantify the business pressure before outreach."],
        calibrated_confidence=confidence,
        richness=richness,
    )


def _ev(org: str, idx: int, category: EvidenceCategory, month: int, title: str, summary: str, observation: str, caps: list[str], execs: list[str], sector: str, patterns: list[str]) -> CommercialEvidence:
    slug = org.upper().replace(" ", "-")
    confidence = 78 + (idx % 12)
    freshness = 85 - idx
    return CommercialEvidence(
        evidence_id=f"EV-{slug}-{idx:03d}", organisation=org, evidence_type="Seeded public-domain theme", evidence_category=category,
        source_name=f"Seeded {category.value}", source_type="seed", publication_date=date(2026, month, min(28, 10 + idx)),
        title=title, summary=summary, extracted_observation=observation, confidence=confidence, freshness=freshness,
        dossier=_seed_dossier(org, category, title, summary, observation, caps, sector, confidence, freshness),
        related_signals=[f"FLORA-SIG-{idx:03d}"], related_patterns=patterns,
        related_playbooks=[f"SECTOR_PLAYBOOK_{sector.upper().replace(' ', '_')}"] + [f"CAPABILITY_PLAYBOOK_{c.upper().replace(' ', '_')}" for c in caps[:1]],
        related_propositions=[f"AI Reinvention Discovery for {caps[0].title()}" if caps else "AI Reinvention Discovery"],
        capability_tags=caps, executive_tags=execs, sector_tags=[sector],
    )


ORG_META = {
    "Thames Water": ("Utilities", ["asset management", "customer operations", "field operations"], ["COO", "CIO", "CDO"]),
    "National Grid": ("Energy", ["asset management", "grid forecasting", "field operations"], ["COO", "CIO"]),
    "BT": ("Telecommunications", ["network intelligence", "customer operations", "workforce productivity"], ["COO", "CIO", "CDO"]),
    "Vodafone": ("Telecommunications", ["network intelligence", "sales operations", "customer operations"], ["COO", "CDO"]),
    "Sky": ("Media", ["customer operations", "content intelligence", "personalisation"], ["CDO", "CIO"]),
    "BBC": ("Media", ["content intelligence", "knowledge management", "responsible AI governance"], ["CIO", "CDO"]),
    "SSE": ("Energy", ["field operations", "asset management", "customer operations"], ["COO", "CIO"]),
    "United Utilities": ("Utilities", ["leakage analytics", "asset management", "customer operations"], ["COO", "CDO"]),
}


def get_seed_evidence() -> list[CommercialEvidence]:
    """Return deterministic seeded commercial evidence for Sprint 3."""
    items: list[CommercialEvidence] = []
    for org, (sector, caps, execs) in ORG_META.items():
        items.extend([
            _ev(org, 1, EvidenceCategory.ANNUAL_REPORT, 3, f"{org} annual report themes", "Annual themes emphasise resilience, cost discipline and service performance.", "Board language links operational pressure to transformation need.", caps, execs, sector, ["PAT-001", "PAT-002"]),
            _ev(org, 2, EvidenceCategory.INVESTOR_PRESENTATION, 4, f"{org} investor priorities", "Investor themes reference efficiency, digital enablement and capital discipline.", "Efficiency commitments create a quantified automation conversation.", caps, execs, sector, ["PAT-002", "PAT-007"]),
            _ev(org, 3, EvidenceCategory.REGULATORY_PUBLICATION, 5, f"{org} regulatory context", "Regulatory pressure highlights performance, transparency or resilience obligations.", "Regulation increases urgency for auditable operating data.", caps, execs, sector, ["PAT-001"]),
            _ev(org, 4, EvidenceCategory.EXECUTIVE_APPOINTMENT, 5, f"{org} leadership signal", "Executive focus includes digital, operations, customer or transformation outcomes.", "Leadership change may reopen the transformation agenda.", caps, execs, sector, ["PAT-003"]),
            _ev(org, 5, EvidenceCategory.TECHNOLOGY_INVESTMENT, 6, f"{org} technology investment", "Technology announcements point to data, automation or platform modernisation.", "Technology spend improves readiness for governed AI use cases.", caps, execs, sector, ["PAT-004", "PAT-007"]),
            _ev(org, 6, EvidenceCategory.CUSTOMER_SIGNAL, 6, f"{org} customer and service signal", "Customer, reliability or service indicators create pressure for measurable reinvention.", "Customer operations is a plausible AI reinvention candidate.", caps, execs, sector, ["PAT-005", "PAT-006"]),
        ])
    return items


def evidence_for_organisation(organisation: str) -> list[CommercialEvidence]:
    key = organisation.replace("_", " ").replace("-", " ").lower()
    return [e for e in get_seed_evidence() if e.organisation.lower().replace(" ", "") == key.replace(" ", "")]
