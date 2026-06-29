"""Deterministic live evidence extraction and interpretation."""
from __future__ import annotations

import hashlib
import html
import re
from datetime import UTC, date, datetime
from typing import Any

from cios.applications.flora.intelligence.evidence_engine import CommercialEvidence, EvidenceCategory
from cios.applications.flora.live.source_registry import SourceRecord

KEYWORDS = ("AI", "automation", "digital transformation", "resilience", "customer service", "customer experience", "operational performance", "cost reduction", "efficiency", "data", "cloud", "regulation", "investment", "modernisation", "asset management", "network", "field operations", "legacy systems", "reform", "spending", "procurement", "service transformation", "cyber", "shared services", "legacy technology", "citizen experience", "AI readiness", "managed services", "consulting", "partnership", "delivery capability")

CONDITION_MAP = {
    "regulation": ("Regulatory Pressure", "governed performance reporting"),
    "resilience": ("Operational Resilience", "asset intelligence"),
    "operational performance": ("Operational Resilience", "performance analytics"),
    "customer service": ("Customer Trust", "customer operations automation"),
    "customer experience": ("Customer Trust", "customer experience intelligence"),
    "cost reduction": ("Cost Pressure", "efficiency automation"),
    "efficiency": ("Operational Efficiency", "process automation"),
    "automation": ("Operational Efficiency", "workflow automation"),
    "AI": ("AI Modernisation", "AI use-case discovery"),
    "data": ("AI Modernisation", "data platform modernisation"),
    "cloud": ("Technology Debt", "cloud modernisation"),
    "digital transformation": ("Digital Leadership", "digital operating model"),
    "modernisation": ("Technology Debt", "platform modernisation"),
    "investment": ("Investment Pressure", "portfolio prioritisation"),
    "asset management": ("Operational Resilience", "asset management intelligence"),
    "network": ("Network Resilience", "network intelligence"),
    "field operations": ("Operational Efficiency", "field operations optimisation"),
    "legacy systems": ("Legacy Technology", "legacy modernisation"),
    "reform": ("Service Transformation", "service reform discovery"),
    "spending": ("Spending Pressure", "spend optimisation"),
    "procurement": ("Procurement Readiness", "procurement route validation"),
    "service transformation": ("Citizen Experience", "citizen service transformation"),
    "cyber": ("Cyber Resilience", "cyber resilience modernisation"),
    "shared services": ("Shared Services", "shared services automation"),
    "legacy technology": ("Legacy Technology", "legacy modernisation"),
    "citizen experience": ("Citizen Experience", "citizen experience improvement"),
    "AI readiness": ("AI Readiness", "AI readiness assessment"),
    "managed services": ("Managed Services", "managed service transformation"),
    "consulting": ("Consulting Growth", "consulting-led transformation"),
    "partnership": ("Partnership Ecosystem", "partner ecosystem activation"),
    "delivery capability": ("Delivery Capability", "delivery assurance"),
}


def html_to_text(page: str) -> str:
    page = re.sub(r"(?is)<(script|style).*?</\1>", " ", page)
    page = re.sub(r"(?s)<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(page)).strip()


def _snippet(text: str, start: int, end: int, radius: int = 170) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    prefix = "…" if left else ""
    suffix = "…" if right < len(text) else ""
    return prefix + text[left:right].strip() + suffix


def interpret_keyword(keyword: str) -> tuple[str, str, str, int]:
    condition, capability = CONDITION_MAP[keyword]
    relevance = f"Evidence mentioning {keyword} may indicate a practical AI reinvention conversation around {capability}."
    confidence = 74 if keyword in {"AI", "automation", "operational performance", "regulation", "investment"} else 68
    return condition, capability, relevance, confidence


def quality_scores(source: SourceRecord, snippet: str) -> dict[str, int]:
    reliability = 95 if source.evidence_tier.startswith("tier_1") else 75
    specificity = 90 if source.coverage_role in {"primary", "regulator", "competitor"} else 65
    extraction = 85 if len(snippet) > 80 else 70
    overall = round((reliability + specificity + extraction) / 3)
    return {"source_reliability": reliability, "source_specificity": specificity, "extraction_quality": extraction, "overall_evidence_quality": overall}


def extract_evidence(source: SourceRecord, page: str, extracted_at: datetime | None = None, max_items: int = 4) -> list[dict[str, Any]]:
    extracted_at = extracted_at or datetime.now(UTC)
    text = html_to_text(page)
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for keyword in KEYWORDS:
        match = re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE)
        if not match:
            continue
        snippet = _snippet(text, match.start(), match.end())
        dedupe = snippet.lower()
        if dedupe in seen:
            continue
        seen.add(dedupe)
        condition, capability, relevance, confidence = interpret_keyword(keyword)
        evidence_id = "LIVE-" + hashlib.sha1(f"{source.source_id}|{keyword}|{snippet}".encode()).hexdigest()[:12].upper()
        found.append({
            "evidence_id": evidence_id,
            "organisation": source.organisation,
            "source_id": source.source_id,
            "source_name": source.source_name,
            "source_type": source.source_type,
            "source_url": str(source.url),
            "sector": source.sector,
            "evidence_tier": source.evidence_tier,
            **quality_scores(source, snippet),
            "keyword": keyword,
            "snippet": snippet,
            "commercial_condition": condition,
            "likely_capability": capability,
            "ai_reinvention_relevance": relevance,
            "confidence": confidence,
            "extraction_timestamp": extracted_at.isoformat(),
            "missing_evidence": ["named executive sponsor", "budget or procurement timing", "incumbent supplier position", "quantified AI outcome"],
        })
        if len(found) >= max_items:
            break
    return found


def to_commercial_evidence(item: dict[str, Any]) -> CommercialEvidence:
    category = EvidenceCategory.REGULATORY_PUBLICATION if item["source_type"] in {"regulator", "regulator_publications"} else EvidenceCategory.COMPANY_NEWS
    if item["source_type"] in {"company_investor", "investor_results", "annual_report_landing"}:
        category = EvidenceCategory.INVESTOR_PRESENTATION
    return CommercialEvidence(
        evidence_id=item["evidence_id"], organisation=item["organisation"], evidence_type="Live public HTML evidence", evidence_category=category,
        source_name=item["source_name"], source_type=item["source_type"], publication_date=date.fromisoformat(item["extraction_timestamp"][:10]),
        title=f"Live evidence: {item['keyword']}", summary=item["ai_reinvention_relevance"], extracted_observation=item["snippet"],
        confidence=item["confidence"], freshness=95, related_signals=[item["commercial_condition"]], related_patterns=["LIVE-EVIDENCE-v0.1"],
        related_playbooks=[f"CAPABILITY_PLAYBOOK_{item['likely_capability'].upper().replace(' ', '_')}"] , related_propositions=[f"AI Reinvention Discovery for {item['likely_capability'].title()}"],
        capability_tags=[item["likely_capability"]], executive_tags=["COO", "CIO"], sector_tags=[item["sector"]],
    )
