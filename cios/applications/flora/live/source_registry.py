"""Governed source registry for Flora live evidence v0.3."""
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
    SourceRecord(source_id="thames-water-investors", organisation="Thames Water", source_name="Thames Water investors", source_type="investor_results", url="https://www.thameswater.co.uk/about-us/investors", sector="Utilities", evidence_tier="tier_1_company", expected_signal_types=["investment", "operational performance", "resilience", "customer service"]),
    SourceRecord(source_id="thames-water-news", organisation="Thames Water", source_name="Thames Water news", source_type="official_newsroom", url="https://www.thameswater.co.uk/news", sector="Utilities", evidence_tier="tier_1_company", expected_signal_types=["customer service", "investment", "resilience", "network"]),
    SourceRecord(source_id="thames-water-ofwat", organisation="Thames Water", source_name="Ofwat Thames Water search", source_type="regulator_publications", url="https://www.ofwat.gov.uk/?s=Thames+Water", sector="Utilities", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "operational performance", "customer service"]),
    SourceRecord(source_id="national-grid-investors", organisation="National Grid", source_name="National Grid investors", source_type="investor_results", url="https://www.nationalgrid.com/investors", sector="Energy", evidence_tier="tier_1_company", expected_signal_types=["investment", "network", "resilience", "asset management"]),
    SourceRecord(source_id="national-grid-news", organisation="National Grid", source_name="National Grid news", source_type="official_newsroom", url="https://www.nationalgrid.com/media-centre/press-releases", sector="Energy", evidence_tier="tier_1_company", expected_signal_types=["investment", "network", "modernisation", "resilience"]),
    SourceRecord(source_id="national-grid-ofgem", organisation="National Grid", source_name="Ofgem National Grid search", source_type="regulator_publications", url="https://www.ofgem.gov.uk/search?keywords=National%20Grid", sector="Energy", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "network", "investment"]),
    SourceRecord(source_id="bt-investors", organisation="BT", source_name="BT investors", source_type="investor_results", url="https://www.bt.com/about/investors", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["digital transformation", "cost reduction", "network", "customer experience"]),
    SourceRecord(source_id="bt-news", organisation="BT", source_name="BT newsroom", source_type="official_newsroom", url="https://newsroom.bt.com/", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["AI", "network", "customer experience", "cloud"]),
    SourceRecord(source_id="bt-ofcom", organisation="BT", source_name="Ofcom BT search", source_type="regulator_publications", url="https://www.ofcom.org.uk/search/?q=BT", sector="Telecommunications", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "customer service", "network"]),
    SourceRecord(source_id="vodafone-investors", organisation="Vodafone", source_name="Vodafone investors", source_type="investor_results", url="https://investors.vodafone.com/", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["efficiency", "cost reduction", "network", "customer experience"]),
    SourceRecord(source_id="vodafone-news", organisation="Vodafone", source_name="Vodafone news", source_type="official_newsroom", url="https://www.vodafone.com/news", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["AI", "network", "data", "customer experience"]),
    SourceRecord(source_id="vodafone-ofcom", organisation="Vodafone", source_name="Ofcom Vodafone search", source_type="regulator_publications", url="https://www.ofcom.org.uk/search/?q=Vodafone", sector="Telecommunications", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "customer service", "network"]),

    SourceRecord(source_id="united-utilities-results", organisation="United Utilities", source_name="United Utilities results centre", source_type="investor_results", url="https://www.unitedutilities.com/corporate/investors/results-centre/", sector="Utilities", evidence_tier="tier_1_company", expected_signal_types=["investment", "operational performance", "resilience", "customer service"]),
    SourceRecord(source_id="united-utilities-news", organisation="United Utilities", source_name="United Utilities news", source_type="official_newsroom", url="https://www.unitedutilities.com/corporate/newsroom/", sector="Utilities", evidence_tier="tier_1_company", expected_signal_types=["customer service", "investment", "resilience", "network"]),
    SourceRecord(source_id="united-utilities-ofwat", organisation="United Utilities", source_name="Ofwat United Utilities search", source_type="regulator_publications", url="https://www.ofwat.gov.uk/?s=United+Utilities", sector="Utilities", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "operational performance", "customer service"]),
    SourceRecord(source_id="sse-results", organisation="SSE", source_name="SSE results and reports", source_type="investor_results", url="https://www.sse.com/investors/results-and-reports/", sector="Energy", evidence_tier="tier_1_company", expected_signal_types=["investment", "network", "resilience", "asset management"]),
    SourceRecord(source_id="sse-news", organisation="SSE", source_name="SSE news", source_type="official_newsroom", url="https://www.sse.com/news-and-views/", sector="Energy", evidence_tier="tier_1_company", expected_signal_types=["investment", "network", "modernisation", "resilience"]),
    SourceRecord(source_id="sse-ofgem", organisation="SSE", source_name="Ofgem SSE search", source_type="regulator_publications", url="https://www.ofgem.gov.uk/search?keywords=SSE", sector="Energy", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "network", "investment"]),
    SourceRecord(source_id="sky-results", organisation="Sky", source_name="Comcast Sky results", source_type="investor_results", url="https://www.cmcsa.com/financials/quarterly-results", sector="Media", evidence_tier="tier_1_company", expected_signal_types=["customer experience", "data", "cloud", "efficiency"]),
    SourceRecord(source_id="sky-news", organisation="Sky", source_name="Sky corporate news", source_type="official_newsroom", url="https://www.skygroup.sky/media-centre/", sector="Media", evidence_tier="tier_1_company", expected_signal_types=["AI", "customer experience", "data", "cloud"]),
    SourceRecord(source_id="sky-ofcom", organisation="Sky", source_name="Ofcom Sky search", source_type="regulator_publications", url="https://www.ofcom.org.uk/search/?q=Sky", sector="Media", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "customer service", "network"]),
    SourceRecord(source_id="bbc-annual-report", organisation="BBC", source_name="BBC annual reports", source_type="annual_report_landing", url="https://www.bbc.com/aboutthebbc/reports/annualreport", sector="Media", evidence_tier="tier_1_public_body", expected_signal_types=["digital transformation", "efficiency", "customer experience"]),
    SourceRecord(source_id="bbc-news", organisation="BBC", source_name="BBC media centre", source_type="official_newsroom", url="https://www.bbc.co.uk/mediacentre/", sector="Media", evidence_tier="tier_1_public_body", expected_signal_types=["AI", "digital transformation", "data", "customer experience"]),
    SourceRecord(source_id="bbc-ofcom", organisation="BBC", source_name="Ofcom BBC search", source_type="regulator_publications", url="https://www.ofcom.org.uk/search/?q=BBC", sector="Media", evidence_tier="tier_1_regulator", expected_signal_types=["regulation", "customer service"]),

    SourceRecord(source_id="mod-govuk-org", organisation="Ministry of Defence", source_name="GOV.UK Ministry of Defence", source_type="govuk_organisation", url="https://www.gov.uk/government/organisations/ministry-of-defence", sector="Public Sector", evidence_tier="tier_1_public_body", expected_signal_types=["digital transformation", "AI", "automation", "legacy systems", "operational performance", "reform", "spending", "procurement", "service transformation", "data", "cloud", "cyber", "shared services"]),
    SourceRecord(source_id="mod-govuk-news", organisation="Ministry of Defence", source_name="GOV.UK Ministry of Defence news", source_type="govuk_news", url="https://www.gov.uk/search/news-and-communications?organisations%5B%5D=ministry-of-defence", sector="Public Sector", evidence_tier="tier_1_public_body", expected_signal_types=["digital transformation", "AI", "automation", "operational performance", "reform", "spending", "procurement", "data", "cloud", "cyber"]),
    SourceRecord(source_id="dwp-govuk-org", organisation="DWP", source_name="GOV.UK DWP", source_type="govuk_organisation", url="https://www.gov.uk/government/organisations/department-for-work-pensions", sector="Public Sector", evidence_tier="tier_1_public_body", expected_signal_types=["digital transformation", "AI", "automation", "legacy systems", "operational performance", "reform", "spending", "procurement", "service transformation", "data", "cloud", "cyber", "shared services"]),
    SourceRecord(source_id="dwp-govuk-publications", organisation="DWP", source_name="GOV.UK DWP publications", source_type="govuk_publications", url="https://www.gov.uk/search/all?organisations%5B%5D=department-for-work-pensions&content_store_document_type=publication", sector="Public Sector", evidence_tier="tier_1_public_body", expected_signal_types=["service transformation", "automation", "legacy systems", "operational performance", "spending", "data", "shared services"]),
    SourceRecord(source_id="moj-govuk-org", organisation="Ministry of Justice", source_name="GOV.UK Ministry of Justice", source_type="govuk_organisation", url="https://www.gov.uk/government/organisations/ministry-of-justice", sector="Public Sector", evidence_tier="tier_1_public_body", expected_signal_types=["digital transformation", "AI", "automation", "legacy systems", "operational performance", "reform", "spending", "procurement", "service transformation", "data", "cloud", "cyber", "shared services"]),
    SourceRecord(source_id="moj-govuk-news", organisation="Ministry of Justice", source_name="GOV.UK Ministry of Justice news", source_type="govuk_news", url="https://www.gov.uk/search/news-and-communications?organisations%5B%5D=ministry-of-justice", sector="Public Sector", evidence_tier="tier_1_public_body", expected_signal_types=["service transformation", "reform", "operational performance", "digital transformation", "data", "cyber"]),
    SourceRecord(source_id="bt-strategy", organisation="BT", source_name="BT strategy overview", source_type="strategy_page", url="https://www.bt.com/about/strategy", sector="Telecommunications", evidence_tier="tier_1_company", expected_signal_types=["digital transformation", "customer experience", "network"], enabled=False),
    SourceRecord(source_id="bbc-rss", organisation="BBC", source_name="BBC press office feed", source_type="official_rss_or_feed", url="https://feeds.bbci.co.uk/news/rss.xml", sector="Media", evidence_tier="tier_2_feed", expected_signal_types=["customer experience", "data"], enabled=False),
)

ALIASES = {"thameswater": "Thames Water", "nationalgrid": "National Grid", "bt": "BT", "vodafone": "Vodafone", "unitedutilities": "United Utilities", "sse": "SSE", "sky": "Sky", "bbc": "BBC", "mod": "Ministry of Defence", "ministryofdefence": "Ministry of Defence", "dwp": "DWP", "departmentforworkandpensions": "DWP", "moj": "Ministry of Justice", "ministryofjustice": "Ministry of Justice"}


def canonical_organisation(value: str) -> str:
    return ALIASES.get(value.replace(" ", "").replace("_", "").replace("-", "").lower(), value)


def enabled_sources(organisation: str | None = None) -> list[SourceRecord]:
    org = canonical_organisation(organisation) if organisation else None
    return [s for s in SOURCES if s.enabled and (org is None or s.organisation == org)]
