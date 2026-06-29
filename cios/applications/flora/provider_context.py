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
    )


def provider_relevance_note(ctx: ProviderContext | None = None) -> str:
    provider = ctx or default_provider_context()
    offerings = ", ".join(provider.strategic_offerings[:5])
    return f"Because {provider.provider_name} is configured as the current provider, Flora highlights {offerings} angles where relevant."
