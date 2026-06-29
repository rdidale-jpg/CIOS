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
    confidence: int = Field(ge=0, le=100)
    freshness: int = Field(ge=0, le=100)
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


def _ev(org: str, idx: int, category: EvidenceCategory, month: int, title: str, summary: str, observation: str, caps: list[str], execs: list[str], sector: str, patterns: list[str]) -> CommercialEvidence:
    slug = org.upper().replace(" ", "-")
    return CommercialEvidence(
        evidence_id=f"EV-{slug}-{idx:03d}", organisation=org, evidence_type="Seeded public-domain theme", evidence_category=category,
        source_name=f"Seeded {category.value}", source_type="seed", publication_date=date(2026, month, min(28, 10 + idx)),
        title=title, summary=summary, extracted_observation=observation, confidence=78 + (idx % 12), freshness=85 - idx,
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
