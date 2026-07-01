"""Configurable provider context for Flora reporting."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProviderContext(BaseModel):
    provider_name: str
    provider_type: str
    strategic_offerings: list[str] = Field(default_factory=list)
    key_competitors: list[str] = Field(default_factory=list)
    differentiators: list[str] = Field(default_factory=list)
    reference_strengths: list[str] = Field(default_factory=list)
    target_sectors: list[str] = Field(default_factory=list)
    reference_programmes: list[str] = Field(default_factory=list)
    sector_capability: list[str] = Field(default_factory=list)
    technology_partnerships: list[str] = Field(default_factory=list)
    delivery_capability: list[str] = Field(default_factory=list)
    opportunity_fit: list[str] = Field(default_factory=list)


def default_provider_context() -> ProviderContext:
    """Return cautious local provider context; no live data, LLMs or databases."""

    return ProviderContext(
        provider_name="IBM",
        provider_type="technology, consulting and managed services provider",
        strategic_offerings=[
            "AI transformation",
            "hybrid cloud modernisation",
            "consulting-led reinvention",
            "asset intelligence",
            "managed operations",
            "data and automation governance",
        ],
        key_competitors=["Accenture", "Capgemini", "Deloitte", "KPMG", "CGI", "TCS", "Infosys", "Cognizant", "Wipro", "Sopra Steria"],
        differentiators=[
            "hybrid cloud and AI platform heritage",
            "enterprise consulting and systems integration experience",
            "managed operations and resilient delivery credentials",
            "regulated-industry transformation patterns",
        ],
        reference_strengths=[
            "AI and automation delivery",
            "hybrid cloud architecture",
            "asset-intensive operations",
            "public-sector and regulated-industry modernisation",
        ],
        target_sectors=["Utilities", "Energy", "Telecommunications", "Media", "Sport", "Public Sector"],
        reference_programmes=["regulated-industry modernisation", "AI and automation delivery", "hybrid cloud transformation"],
        sector_capability=["Utilities", "Energy", "Telecommunications", "Public Sector"],
        technology_partnerships=["hybrid cloud ecosystem", "enterprise AI ecosystem", "automation ecosystem"],
        delivery_capability=["consulting", "systems integration", "managed operations", "secure delivery"],
        opportunity_fit=["AI Transformation", "Cloud Modernisation", "Cyber Resilience", "Operational Resilience", "Data Platform"],
    )


def provider_relevance_note(ctx: ProviderContext | None = None) -> str:
    provider = ctx or default_provider_context()
    offerings = ", ".join(provider.strategic_offerings[:5])
    return f"Because {provider.provider_name} is configured as the current provider, Flora highlights {offerings} angles where relevant."

# Milestone 4 provider profile aliases. These fields keep provider context
# configurable for EOSE without making the engine IBM-specific.
ProviderContext.model_rebuild()
