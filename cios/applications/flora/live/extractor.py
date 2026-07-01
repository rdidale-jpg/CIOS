"""Deterministic live evidence extraction and interpretation."""
from __future__ import annotations

import hashlib
import html
import re
from datetime import UTC, date, datetime
from typing import Any

from cios.applications.flora.intelligence.evidence_engine import CommercialEvidence, EvidenceCategory, EvidenceReasoningDossier, EvidenceRichnessMetrics, EvidenceSourceAttribution
from cios.applications.flora.live.source_registry import SourceRecord

KEYWORDS = ("AI", "automation", "digital transformation", "resilience", "customer service", "customer experience", "operational performance", "cost reduction", "efficiency", "data", "cloud", "regulation", "investment", "modernisation", "asset management", "network", "field operations", "legacy systems", "reform", "spending", "procurement", "service transformation", "cyber", "shared services", "legacy technology", "citizen experience", "AI readiness", "managed services", "consulting", "partnership", "delivery capability")


BOILERPLATE_TERMS = (
    "rewards & benefits", "rewards and benefits", "flexible working", "modern slavery",
    "child rights", "our locations", "search roles", "cookie", "privacy notice",
    "site map", "accessibility", "careers", "graduate", "jobs", "vacancies",
    "responsible business", "social value", "supplier code", "policy", "policies",
)
NAVIGATION_TERMS = ("menu", "home", "about us", "contact us", "investors", "newsroom", "search", "sign in", "subscribe", "locations", "roles")
ALIGNMENT_TERMS = {
    "AI Modernisation": ("ai", "artificial intelligence", "automation", "machine learning", "data platform", "analytics", "network operations", "customer operations", "technology", "deployment", "platform"),
    "AI Readiness": ("ai", "artificial intelligence", "data", "platform", "technology", "deployment", "readiness"),
    "Regulatory Pressure": ("regulator", "regulation", "regulatory", "compliance", "licence", "enforcement", "consultation", "obligation", "ofcom", "ofwat", "fca", "policy intervention"),
    "Network Resilience": ("network", "resilience", "outage", "service assurance", "infrastructure", "broadband", "connectivity", "availability", "reliability", "operational performance"),
    "Investment Pressure": ("investment", "capex", "financial results", "cost pressure", "productivity", "savings", "margin", "funding", "capital allocation", "programme value"),
    "Cost Pressure": ("cost", "savings", "productivity", "efficiency", "margin", "financial", "funding"),
}
STRONG_CONTEXT_TERMS = ("programme", "deployment", "investment", "budget", "supplier", "platform", "cloud", "cyber", "legacy", "operating model", "executive", "regulator", "capex", "service resilience", "network operations", "financial results", "procurement")


def _term_count(snippet: str, terms: tuple[str, ...]) -> int:
    text = snippet.casefold()
    return sum(1 for term in terms if term in text)


def _is_boilerplate(snippet: str) -> tuple[bool, str]:
    text = snippet.casefold()
    boilerplate_hits = [term for term in BOILERPLATE_TERMS if term in text]
    nav_hits = [term for term in NAVIGATION_TERMS if term in text]
    if len(nav_hits) >= 5:
        return True, "navigation-heavy page furniture"
    if len(boilerplate_hits) >= 2:
        return True, "generic corporate, careers, ESG or policy boilerplate"
    if any(term in text for term in ("search roles", "our locations", "modern slavery", "child rights", "flexible working", "rewards & benefits")):
        return True, "BT-style careers, social value or policy boilerplate"
    return False, ""


def _alignment_reason(condition: str, snippet: str) -> tuple[bool, str]:
    text = snippet.casefold()
    terms = ALIGNMENT_TERMS.get(condition)
    if not terms:
        return True, "condition does not require special alignment"
    if condition == "AI Modernisation" and "responsible ai" in text and _term_count(snippet, STRONG_CONTEXT_TERMS) == 0:
        return False, "generic Responsible AI reference lacks business transformation context"
    if any(term in text for term in terms):
        return True, "snippet aligns to claim-specific commercial context"
    return False, f"snippet lacks direct {condition} alignment terms"


def classify_relevance(snippet: str, condition: str, source: SourceRecord | None = None) -> dict[str, Any]:
    is_boilerplate, boilerplate_reason = _is_boilerplate(snippet)
    aligned, alignment_reason = _alignment_reason(condition, snippet)
    reasons: list[str] = []
    if is_boilerplate:
        reasons.append(boilerplate_reason)
    if not aligned:
        reasons.append(alignment_reason)
    quant_count = len(re.findall(r"\b(?:£|\$|€)?\d+(?:[.,]\d+)?\s?(?:m|bn|million|billion|%|per cent|employees|customers|homes|sites|MW|GW|km)?\b", snippet, re.IGNORECASE))
    strong_context = _term_count(snippet, STRONG_CONTEXT_TERMS)
    if is_boilerplate and not strong_context:
        level = "REJECT"
    elif not aligned:
        level = "LOW"
    elif strong_context >= 2 or quant_count or (source and source.coverage_role in {"regulator", "primary"} and strong_context):
        level = "HIGH"
    elif strong_context == 1 or aligned:
        level = "MEDIUM"
    else:
        level = "LOW"
    accepted = level == "HIGH" or (level == "MEDIUM" and aligned and not is_boilerplate)
    if not reasons:
        reasons.append("accepted as specific commercial evidence" if accepted else "insufficient commercial specificity")
    safer = "Treat as page context only; do not use to support a transformation conclusion." if not accepted else "Use cautiously as commercial evidence."
    return {"relevance_level": level, "accepted_for_claims": accepted, "rejection_reasons": reasons, "alignment_passed": aligned, "boilerplate_detected": is_boilerplate, "safer_interpretation": safer}

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
    relevance = f"Evidence mentioning {keyword} may indicate a possible AI reinvention transformation conversation around {capability}; it must pass relevance and alignment gates before supporting conclusions."
    confidence = 74 if keyword in {"AI", "automation", "operational performance", "regulation", "investment"} else 68
    return condition, capability, relevance, confidence


def recalibrated_confidence(base: int, gate: dict[str, Any], source: SourceRecord, snippet: str) -> int:
    score = base
    if gate["relevance_level"] == "HIGH":
        score += 8
    elif gate["relevance_level"] == "MEDIUM":
        score -= 8
    elif gate["relevance_level"] == "LOW":
        score -= 25
    else:
        score -= 40
    if gate.get("boilerplate_detected"):
        score -= 20
    if source.coverage_role not in {"regulator", "competitor"}:
        score -= 4
    if re.search(r"\b(?:£|\$|€)?\d", snippet):
        score += 8
    if _term_count(snippet, ("programme", "executive", "supplier", "budget", "platform", "regulator", "ofcom", "capex")):
        score += 6
    return max(5, min(95, score))


def quality_scores(source: SourceRecord, snippet: str) -> dict[str, int]:
    reliability = 95 if source.evidence_tier.startswith("tier_1") else 75
    specificity = 90 if source.coverage_role in {"primary", "regulator", "competitor"} else 65
    extraction = 85 if len(snippet) > 80 else 70
    overall = round((reliability + specificity + extraction) / 3)
    return {"source_reliability": reliability, "source_specificity": specificity, "extraction_quality": extraction, "overall_evidence_quality": overall}


def evidence_dossier(source: SourceRecord, keyword: str, snippet: str, condition: str, capability: str, confidence: int, extracted_at: datetime) -> dict[str, Any]:
    quant_count = len(re.findall(r"\b(?:£|\$|€)?\d+(?:[.,]\d+)?\s?(?:m|bn|million|billion|%|per cent|employees|customers|homes|sites|MW|GW|km)?\b", snippet, re.IGNORECASE))
    quote_count = snippet.count("“") + snippet.count('"') // 2
    richness = EvidenceRichnessMetrics(
        source_count=1,
        independent_source_count=1,
        quantitative_fact_count=quant_count,
        quote_count=quote_count,
        competitor_comparison_count=1 if source.coverage_role == "competitor" else 0,
        benchmark_count=1 if source.coverage_role in {"regulator", "competitor"} else 0,
        timeline_event_count=1,
        freshness_score=95,
        corroboration_score=35,
        traceability_score=90,
    )
    return EvidenceReasoningDossier(
        observed_facts=[snippet],
        quantitative_facts=[f"{quant_count} quantitative figure(s) detected in the extracted snippet."] if quant_count else ["No quantitative figure detected in this snippet."],
        named_sources=[EvidenceSourceAttribution(source_name=source.source_name, source_type=source.source_type, source_url=str(source.url), publication_date=extracted_at.date(), freshness_note="Collected during live public-source run.")],
        strategic_messages=[f"Public source mentions {keyword} in a way mapped to {condition}."],
        competitor_comparisons=[f"Competitor/market context source for {source.organisation}; compare against incumbent and challenger announcements."] if source.coverage_role == "competitor" else [],
        sector_benchmarks=[f"Benchmark against {source.sector} pressure themes and regulator/company disclosures."],
        transformation_timeline=[f"{extracted_at.date().isoformat()}: live evidence collected from {source.source_name}."],
        interpretation=[f"Evidence mentioning {keyword} may indicate a practical AI reinvention conversation around {capability}."],
        hypotheses=["The public signal may reflect transformation pressure; sponsor, budget, timing and supplier position remain unproven."],
        implications=[f"Potential entry point: {capability}; requires independent corroboration before treating as demand."],
        recommended_actions=["Find a second named source, extract quantitative facts and validate executive ownership before outreach."],
        evidence_freshness="Collected today during live evidence extraction.",
        expected_update_frequency="Refresh on each live collection run; re-check before account planning or external use.",
        independent_corroboration="Single live source; needs independent corroboration.",
        calibrated_confidence=confidence,
        richness=richness,
    ).model_dump(mode="json")


def _candidate_items(source: SourceRecord, page: str, extracted_at: datetime | None = None, max_items: int | None = None) -> list[dict[str, Any]]:
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
        gate = classify_relevance(snippet, condition, source)
        confidence = recalibrated_confidence(confidence, gate, source, snippet)
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
            "evidence_dossier": evidence_dossier(source, keyword, snippet, condition, capability, confidence, extracted_at),
            "extraction_timestamp": extracted_at.isoformat(),
            "missing_evidence": ["named executive sponsor", "budget or procurement timing", "incumbent supplier position", "quantified AI outcome"],
            **gate,
            "attempted_classification": condition,
        })
        if max_items is not None and len([item for item in found if item["accepted_for_claims"]]) >= max_items:
            break
    return found


def extract_evidence(source: SourceRecord, page: str, extracted_at: datetime | None = None, max_items: int = 4) -> list[dict[str, Any]]:
    return [item for item in _candidate_items(source, page, extracted_at, max_items) if item["accepted_for_claims"]][:max_items]


def extract_evidence_with_diagnostics(source: SourceRecord, page: str, extracted_at: datetime | None = None, max_items: int = 4) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = _candidate_items(source, page, extracted_at, None)
    accepted = [item for item in candidates if item["accepted_for_claims"]][:max_items]
    accepted_ids = {item["evidence_id"] for item in accepted}
    rejected = [item for item in candidates if item["evidence_id"] not in accepted_ids]
    return accepted, rejected

def to_commercial_evidence(item: dict[str, Any]) -> CommercialEvidence:
    category = EvidenceCategory.REGULATORY_PUBLICATION if item["source_type"] in {"regulator", "regulator_publications"} else EvidenceCategory.COMPANY_NEWS
    if item["source_type"] in {"company_investor", "investor_results", "annual_report_landing"}:
        category = EvidenceCategory.INVESTOR_PRESENTATION
    dossier = EvidenceReasoningDossier.model_validate(item["evidence_dossier"]) if item.get("evidence_dossier") else None
    return CommercialEvidence(
        evidence_id=item["evidence_id"], organisation=item["organisation"], evidence_type="Live public HTML evidence", evidence_category=category,
        source_name=item["source_name"], source_type=item["source_type"], publication_date=date.fromisoformat(item["extraction_timestamp"][:10]),
        title=f"Live evidence: {item['keyword']}", summary=item["ai_reinvention_relevance"], extracted_observation=item["snippet"],
        confidence=item["confidence"], freshness=95, dossier=dossier, related_signals=[item["commercial_condition"]], related_patterns=["LIVE-EVIDENCE-v0.1"],
        related_playbooks=[f"CAPABILITY_PLAYBOOK_{item['likely_capability'].upper().replace(' ', '_')}"] , related_propositions=[f"AI Reinvention Discovery for {item['likely_capability'].title()}"],
        capability_tags=[item["likely_capability"]], executive_tags=["COO", "CIO"], sector_tags=[item["sector"]],
    )
