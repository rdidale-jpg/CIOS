"""Deterministic live evidence extraction and interpretation."""
from __future__ import annotations

import hashlib
import html
import re
from datetime import UTC, date, datetime
from typing import Any

from cios.applications.flora.intelligence.evidence_engine import CommercialEvidence, EvidenceCategory, EvidenceReasoningDossier, EvidenceRichnessMetrics, EvidenceSourceAttribution
from cios.applications.flora.live.source_registry import SourceRecord
from cios.applications.flora.live.alignment import evidence_quality_band, source_tier, can_support_strategic_signal

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
STRONG_CONTEXT_TERMS = ("programme", "deployment", "investment", "budget", "supplier", "platform", "cloud", "cyber", "legacy", "operating model", "executive", "regulator", "capex", "service resilience", "network operations", "financial results", "procurement", "modernisation", "network", "managed services", "consulting", "partnership ecosystem", "delivery capability")

SPECIFICITY_PATTERNS = {
    "named_programme": r"\b(?:programme|program|initiative|strategy|transformation|rollout|project|scheme)\b",
    "named_executive_or_role": r"\b(?:chief|director|minister|secretary|ceo|cfo|cio|cto|coo|chair|executive|officer)\b",
    "quantified_value": r"\b(?:£|\$|€)?\d+(?:[.,]\d+)?\s?(?:m|bn|million|billion|%|per cent|employees|customers|citizens|homes|sites|km|capex|savings|investment)?\b",
    "date_specific": r"\b(?:20\d{2}|19\d{2}|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b",
    "procurement_reference": r"\b(?:contract|procurement|tender|award|framework|pipeline|find a tender|contracts finder)\b",
    "regulatory_report": r"\b(?:regulator|regulatory|report|finding|enforcement|consultation|nao|ofcom|ofwat|ofgem|fca)\b",
    "incident_resilience": r"\b(?:incident|outage|resilience|availability|reliability|service performance)\b",
    "financial_target": r"\b(?:revenue|profit|ebitda|capex|opex|savings|investment|target|financial results|annual report)\b",
    "technology_supplier": r"\b(?:platform|supplier|partnership|partner|cloud|cyber|ai|data|technology|microsoft|aws|google|oracle|salesforce|servicenow|nhs app)\b",
    "impact_metric": r"\b(?:customers|citizens|patients|users|claims|transactions|complaints|performance measure)\b",
}

CONTEXT_ONLY_SOURCE_TYPES = {"landing_page", "organisation_landing", "supplier_service_menu", "careers", "category_page", "strategy_page"}
PRIMARY_SOURCE_TYPES = {"annual_report", "annual_report_landing", "investor_results", "investor_presentations", "regulator_publications", "govuk_policy", "procurement", "contract_award", "official_guidance"}
SECONDARY_SOURCE_TYPES = {"official_newsroom", "company_newsroom", "news_item", "case_study", "technology_partner", "official_rss_or_feed", "investor_consensus"}

def source_classification(source: SourceRecord) -> str:
    st = source.source_type.casefold()
    name = f"{source.source_name} {source.url}".casefold()
    if "annual" in st or "annual" in name or "report" in st:
        return "annual_report" if "annual" in name else "report"
    if "regulator" in st or source.coverage_role == "regulator":
        return "regulator_report"
    if "procurement" in st or "contract" in st:
        return "procurement"
    if "news" in st or "newsroom" in st:
        return "news_item"
    if "case" in st:
        return "case_study"
    if "investor" in st or "results" in st:
        return "report"
    if source.coverage_role == "context" or "landing" in st or str(source.url).rstrip('/').count('/') <= 2:
        return "landing_page"
    return "focused_page"

def specificity_markers(snippet: str) -> list[str]:
    return [name for name, pattern in SPECIFICITY_PATTERNS.items() if re.search(pattern, snippet, re.IGNORECASE)]

def evidence_type_for(source: SourceRecord, snippet: str, markers: list[str], boilerplate: bool) -> str:
    st = source.source_type
    if boilerplate or st in CONTEXT_ONLY_SOURCE_TYPES or source.coverage_role == "context":
        return "Context Only"
    if st in PRIMARY_SOURCE_TYPES or source.coverage_role in {"regulator", "primary"} and any(m in markers for m in ("regulatory_report", "procurement_reference", "financial_target")):
        return "Primary Evidence"
    if st in SECONDARY_SOURCE_TYPES or any(m in markers for m in ("technology_supplier", "date_specific", "named_programme")):
        return "Secondary Evidence"
    return "Context Only"

def clean_observation(snippet: str) -> str:
    text = re.sub(r"\s+", " ", html.unescape(snippet)).strip(" …")
    parts = re.split(r"(?<=[.!?])\s+", text)
    scored = []
    for part in parts or [text]:
        low = part.casefold()
        if len(part) < 35 or part.count("…") > 1 or _is_boilerplate(part)[0]:
            continue
        score = len(specificity_markers(part)) * 3 + (2 if re.search(r"\d", part) else 0) + len(part) / 200
        scored.append((score, part.strip(" …")))
    chosen = max(scored, default=(0, text[:260].strip(" …")))[1]
    return chosen[:420]


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
    markers = specificity_markers(snippet)
    reasons: list[str] = []
    if is_boilerplate:
        reasons.append(boilerplate_reason)
    if not markers:
        reasons.append("failed evidence specificity gate: no named programme, date, value, contract, regulator, incident, financial, technology or service metric")
    if not aligned:
        reasons.append(alignment_reason)
    source_kind = source_classification(source) if source else "focused_page"
    evidence_type = evidence_type_for(source, snippet, markers, is_boilerplate) if source else "Secondary Evidence"
    quant_count = len(re.findall(SPECIFICITY_PATTERNS["quantified_value"], snippet, re.IGNORECASE))
    strong_context = _term_count(snippet, STRONG_CONTEXT_TERMS)
    if is_boilerplate or not markers or evidence_type == "Context Only":
        level = "REJECT" if is_boilerplate or not markers else "LOW"
    elif not aligned:
        level = "LOW"
    elif source_kind == "landing_page" and not (quant_count and strong_context >= 2):
        level = "MEDIUM"
    elif quant_count or len(markers) >= 2 or evidence_type == "Primary Evidence":
        level = "HIGH"
    else:
        level = "MEDIUM"
    accepted = evidence_type != "Context Only" and (level == "HIGH" or (level == "MEDIUM" and aligned and (len(markers) >= 2 or strong_context >= 2)))
    if not reasons:
        reasons.append("specificity gate passed" if accepted else "downgraded to context; insufficient claim support")
    safer = "Treat as diagnostics/context only; do not use to support a transformation conclusion." if not accepted else "Use as governed commercial evidence with corroboration."
    return {"relevance_level": level, "accepted_for_claims": accepted, "rejection_reasons": reasons, "alignment_passed": aligned, "boilerplate_detected": is_boilerplate, "specificity_markers": markers, "evidence_type": evidence_type, "source_classification": source_kind, "supports_strategic_signals": accepted and evidence_type in {"Primary Evidence", "Secondary Evidence"} and (level == "HIGH" or (level == "MEDIUM" and len(markers) >= 2)), "safer_interpretation": safer}

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
        score -= 25
    if gate.get("evidence_type") == "Primary Evidence":
        score += 8
    elif gate.get("evidence_type") == "Context Only":
        score -= 30
    if gate.get("source_classification") == "landing_page":
        score -= 15
    if source.coverage_role not in {"regulator", "competitor", "primary"}:
        score -= 4
    if re.search(r"\b(?:£|\$|€)?\d", snippet):
        score += 8
    if _term_count(snippet, ("programme", "executive", "supplier", "budget", "platform", "regulator", "ofcom", "capex", "partnership")):
        score += 6
    if not gate.get("specificity_markers"):
        score -= 20
    cap = 72 if gate.get("source_classification") == "landing_page" else 95
    if gate.get("evidence_type") == "Context Only":
        cap = min(cap, 55)
    return max(5, min(cap, score))


def quality_scores(source: SourceRecord, snippet: str) -> dict[str, int]:
    reliability = 95 if source.evidence_tier.startswith("tier_1") else 75
    specificity = 92 if specificity_markers(snippet) else 35
    if source_classification(source) == "landing_page":
        specificity -= 20
    extraction = 88 if clean_observation(snippet) and len(clean_observation(snippet)) > 60 else 65
    overall = round((reliability + max(0, specificity) + extraction) / 3)
    return {"source_reliability": reliability, "source_specificity": max(0, specificity), "extraction_quality": extraction, "overall_evidence_quality": overall}


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
        tier = source_tier(source.source_type, source.source_name, str(source.url))
        item = {
            "evidence_id": evidence_id,
            "organisation": source.organisation,
            "source_id": source.source_id,
            "source_name": source.source_name,
            "source_type": source.source_type,
            "source_url": str(source.url),
            "sector": source.sector,
            "evidence_tier": source.evidence_tier,
            "source_tier": tier,
            **quality_scores(source, snippet),
            "keyword": keyword,
            "snippet": clean_observation(snippet),
            "cleaned_observation": clean_observation(snippet),
            "raw_snippet": snippet,
            "commercial_condition": condition,
            "likely_capability": capability,
            "ai_reinvention_relevance": relevance,
            "confidence": confidence,
            "evidence_dossier": evidence_dossier(source, keyword, snippet, condition, capability, confidence, extracted_at),
            "extraction_timestamp": extracted_at.isoformat(),
            "missing_evidence": ["named executive sponsor", "budget or procurement timing", "incumbent supplier position", "quantified AI outcome"],
            **gate,
            "attempted_classification": condition,
        }
        item["evidence_quality_band"] = evidence_quality_band(item)
        item["supports_strategic_signals"] = can_support_strategic_signal(item)
        found.append(item)
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
        title=f"Live evidence: {item['keyword']}", summary=item["ai_reinvention_relevance"], extracted_observation=item.get("cleaned_observation") or item["snippet"],
        confidence=item["confidence"], freshness=95, dossier=dossier, related_signals=[item["commercial_condition"]], related_patterns=["LIVE-EVIDENCE-v0.1"],
        related_playbooks=[f"CAPABILITY_PLAYBOOK_{item['likely_capability'].upper().replace(' ', '_')}"] , related_propositions=[f"AI Reinvention Discovery for {item['likely_capability'].title()}"],
        capability_tags=[item["likely_capability"]], executive_tags=["COO", "CIO"], sector_tags=[item["sector"]],
    )
