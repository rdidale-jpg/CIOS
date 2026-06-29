"""Governed source registry for Flora live evidence v0.1."""
from __future__ import annotations

from pydantic import BaseModel, HttpUrl


class SourceRecord(BaseModel):
    source_id: str
    organisation: str
    source_name: str
    source_type: str
    url: HttpUrl
    sector: str
    evidence_tier: str
    expected_signal_types: list[str]
    enabled: bool = True


SOURCES: tuple[SourceRecord, ...] = (
    SourceRecord(source_id="thames-water-investors", organisation="Thames Water", source_name="Thames Water investors", source_type="company_investor", url="https://www.thameswater.co.uk/about-us/investors", sector="Utilities", evidence_tier="tier_1_company", expected_signal_types=["investment", "operational performance", "resilience", "customer service"]),
    SourceRecord(source_id="thames-water-news", organisation="Thames Water", source_name="Thames Water news", source_type="company_newsroom", url="https://www.thameswater.co.uk/news", sector="Utilities", evidence_tier="tier_1_company", expected_signal_types=["customer service", "investment", "resilience", "network"]),
    SourceRecord(source_id="thames-water-ofwat", organisation="Thames Water", source_name="Ofwat Thames Water search", source_type="regulator", url="https://www.ofwat.gov.uk/?s=Thames+Water", sector="Utilities", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "operational performance", "customer service"]),
    SourceRecord(source_id="national-grid-investors", organisation="National Grid", source_name="National Grid investors", source_type="company_investor", url="https://www.nationalgrid.com/investors", sector="Energy", evidence_tier="tier_1_company", expected_signal_types=["investment", "network", "resilience", "asset management"]),
    SourceRecord(source_id="national-grid-news", organisation="National Grid", source_name="National Grid news", source_type="company_newsroom", url="https://www.nationalgrid.com/media-centre/press-releases", sector="Energy", evidence_tier="tier_1_company", expected_signal_types=["investment", "network", "modernisation", "resilience"]),
    SourceRecord(source_id="national-grid-ofgem", organisation="National Grid", source_name="Ofgem National Grid search", source_type="regulator", url="https://www.ofgem.gov.uk/search?keywords=National%20Grid", sector="Energy", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "network", "investment"]),
    SourceRecord(source_id="bt-investors", organisation="BT", source_name="BT investors", source_type="company_investor", url="https://www.bt.com/about/investors", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["digital transformation", "cost reduction", "network", "customer experience"]),
    SourceRecord(source_id="bt-news", organisation="BT", source_name="BT newsroom", source_type="company_newsroom", url="https://newsroom.bt.com/", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["AI", "network", "customer experience", "cloud"]),
    SourceRecord(source_id="bt-ofcom", organisation="BT", source_name="Ofcom BT search", source_type="regulator", url="https://www.ofcom.org.uk/search/?q=BT", sector="Telecommunications", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "customer service", "network"]),
    SourceRecord(source_id="vodafone-investors", organisation="Vodafone", source_name="Vodafone investors", source_type="company_investor", url="https://investors.vodafone.com/", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["efficiency", "cost reduction", "network", "customer experience"]),
    SourceRecord(source_id="vodafone-news", organisation="Vodafone", source_name="Vodafone news", source_type="company_newsroom", url="https://www.vodafone.com/news", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["AI", "network", "data", "customer experience"]),
    SourceRecord(source_id="vodafone-ofcom", organisation="Vodafone", source_name="Ofcom Vodafone search", source_type="regulator", url="https://www.ofcom.org.uk/search/?q=Vodafone", sector="Telecommunications", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "customer service", "network"]),
)

ALIASES = {"thameswater": "Thames Water", "nationalgrid": "National Grid", "bt": "BT", "vodafone": "Vodafone"}


def canonical_organisation(value: str) -> str:
    return ALIASES.get(value.replace(" ", "").replace("_", "").replace("-", "").lower(), value)


def enabled_sources(organisation: str | None = None) -> list[SourceRecord]:
    org = canonical_organisation(organisation) if organisation else None
    return [s for s in SOURCES if s.enabled and (org is None or s.organisation == org)]
