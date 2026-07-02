"""Deterministic Enterprise Transformation Observatory reasoning kernel."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any

from cios.applications.flora.live.aggregation import aggregate_live_evidence, unique_live_evidence
from cios.applications.flora.live.store import DEFAULT_PATH, read_jsonl
from cios.applications.flora.live.source_registry import SOURCES
from cios.applications.flora.observatory.models import *

CRITIQUE_PATH = "docs/Enterprise_Transformation_Observatory_Architectural_Critique.md"

ORG_SEEDS = {
    "DWP": ("Public Sector", "legacy systems", "citizen service", "operational scale", "casework intelligence", "Board"),
    "National Grid": ("Energy", "grid connections", "energy transition", "asset planning", "grid forecasting", "Executive"),
    "BT": ("Telecommunications", "network estate", "enterprise productivity", "service assurance", "network intelligence", "Board"),
}

SECTOR_DEFAULTS = {
    "Telecommunications": ("network estate", "enterprise productivity", "service assurance", "network intelligence", "Board"),
    "Utilities": ("asset resilience", "customer and regulatory pressure", "asset planning", "operational intelligence", "Executive"),
    "Energy": ("energy transition", "grid and asset pressure", "asset planning", "forecasting intelligence", "Executive"),
    "Public Sector": ("legacy systems", "citizen service", "operational scale", "casework intelligence", "Board"),
}


def monitored_enterprise_profiles() -> dict[str, tuple[str, str, str, str, str, str]]:
    profiles = dict(ORG_SEEDS)
    for source in SOURCES:
        if not source.enabled and source.organisation not in profiles:
            continue
        profiles.setdefault(source.organisation, (source.sector, *SECTOR_DEFAULTS.get(source.sector, ("operating pressure", "transformation", "service resilience", "AI-enabled operations", "Executive"))))
    return profiles

CASE_SECTIONS = ("Why Act?", "Why Now?", "Why AI?", "Why Cloud?", "Why Secure by Design?", "Why this Transformation?", "Cost of Waiting", "Commercial Risks", "Contradictory Evidence", "Unknowns")
COST_CATEGORIES = ("Operational cost/risk", "Technology debt", "Security exposure", "Citizen/customer experience", "Regulatory/reputational risk", "Competitive or policy risk", "Delivery complexity")
FACT_PATTERNS = (r"\b\d+(?:\.\d+)?\s*(?:million|billion|bn|m|%)\b", r"£\s*\d+(?:\.\d+)?\s*(?:million|billion|bn|m)?", r"\b20\d{2}\b")


def build_observatory() -> Observatory:
    live = unique_live_evidence(read_jsonl(DEFAULT_PATH))
    live_evs = _live_evidence(live)
    evidence = tuple((live_evs + list(BT_ENTERPRISE_EVIDENCE) + _seed_evidence()) if live_evs else _seed_evidence())
    signals = build_commercial_signals(evidence)
    insights = build_commercial_insights(signals)
    theses = build_transformation_theses(insights, signals)
    arguments = build_commercial_arguments(theses, insights, signals)
    recommendations = build_executive_recommendations(arguments)
    organisations = tuple(_organisation(org, sector, evidence, terms, live, signals, insights, theses, arguments, recommendations) for org, (sector, *terms) in monitored_enterprise_profiles().items())
    return Observatory(CRITIQUE_PATH, evidence, organisations, _weather(evidence, live), _hypotheses(evidence), _graph_edges(evidence, signals, insights, theses, arguments, recommendations), signals, insights, theses, arguments, recommendations)


def observatory_snapshot(obs: Observatory | None = None) -> dict[str, Any]:
    """Return a stable, human-auditable snapshot of Observatory reasoning state."""

    obs = obs or build_observatory()
    return {
        "evidence_ids": tuple(e.evidence_id for e in obs.evidence),
        "organisations": {
            org.organisation: {
                "case_confidence": org.case_for_change.confidence,
                "strategic_urgency_state": org.strategic_urgency.state,
                "strategic_urgency_confidence": org.strategic_urgency.confidence,
                "supporting_evidence_ids": tuple(org.case_for_change.supporting_evidence_ids),
                "genome_scores": {d.name: d.confidence for d in org.genome},
                "force_scores": {f.name: f.confidence for f in org.forces},
                "reasoning_signature": _reasoning_signature(org),
            }
            for org in obs.organisations
        },
        "hypotheses": {
            h.hypothesis_id: {
                "status": h.status.value,
                "confidence": h.confidence,
                "supporting_evidence_ids": tuple(h.supporting_evidence_ids),
                "contradictory_evidence_ids": tuple(h.contradictory_evidence_ids),
                "commercial_implications": h.commercial_implications,
            }
            for h in obs.hypotheses
        },
    }


def compare_observatory_snapshots(before: dict[str, Any], after: dict[str, Any], new_evidence_ids: tuple[str, ...] = ()) -> dict[str, Any]:
    """Explain what changed between two Observatory snapshots and why."""

    before_evidence = set(before.get("evidence_ids", ()))
    after_evidence = set(after.get("evidence_ids", ()))
    added = tuple(sorted(new_evidence_ids or tuple(after_evidence - before_evidence)))
    removed = tuple(sorted(before_evidence - after_evidence))
    org_changes = _organisation_changes(before.get("organisations", {}), after.get("organisations", {}), set(added))
    hypothesis_changes = _hypothesis_changes(before.get("hypotheses", {}), after.get("hypotheses", {}), set(added))
    changed_orgs = tuple(c["organisation"] for c in org_changes if c["changed"])
    score_changes = tuple(c for org in org_changes for c in org["score_changes"])
    reasoning_changes = tuple(c for c in org_changes if c["reasoning_changed"])
    changed = bool(added or removed or changed_orgs or hypothesis_changes)
    return {
        "summary": _change_summary(added, changed_orgs, hypothesis_changes, score_changes, reasoning_changes, changed),
        "new_evidence_collected": len(added),
        "new_evidence_ids": added,
        "removed_evidence_ids": removed,
        "organisations_reanalysed": len(after.get("organisations", {})),
        "organisations_changed": changed_orgs,
        "organisation_changes": org_changes,
        "hypotheses_changed": tuple(h["hypothesis_id"] for h in hypothesis_changes),
        "hypothesis_changes": hypothesis_changes,
        "scores_changed": score_changes,
        "reasoning_changed": reasoning_changes,
        "nothing_changed": not changed,
        "evidence_provenance": tuple({"evidence_id": eid, "caused_changes": _caused_changes(eid, org_changes, hypothesis_changes)} for eid in added),
    }



BOILERPLATE_PATTERNS = ("skip to content", "cookie", "privacy policy", "modern slavery", "careers", "menu", "navigation", "footer", "annual general meeting", "share price")
UNSUPPORTED_DEFAULTS = ("budget", "budget approval", "procurement", "procurement timing", "executive sponsor", "executive sponsorship", "enterprise-wide AI transformation", "transformation window")
UNKNOWN_DEFAULTS = ("budget", "executive sponsor", "roadmap", "procurement timing", "incumbent supplier posture")

BT_ENTERPRISE_EVIDENCE: tuple[ObservatoryEvidence, ...] = (
    ObservatoryEvidence("BT-FIN-001", "Financial Results", "High", "FY2025", "BT", "Telecommunications", "Financial profile", "Cost Pressure", "Why act?", "FY25 revenue was £20.4bn, down 2%; adjusted EBITDA was £8.2bn, up 1%; normalised free cash flow was £1.3bn.", "BT Group FY25 preliminary results", "https://www.bt.com/about/investors/financial-reporting-and-news/quarterly-results", 88, ("Current budget approval", "Deal-specific procurement timing"), ("BT FY25 preliminary results", "deterministic_enterprise_profile"), source_type="investor_relations", mapped_condition="Financial / cost pressure", mapped_capability="operating model transformation"),
    ObservatoryEvidence("BT-FIN-002", "Capital Allocation", "High", "FY2025", "BT", "Telecommunications", "Capital allocation", "Network Investment", "Why network intelligence?", "Capital expenditure excluding spectrum was £4.8bn as BT continued full fibre and mobile network investment.", "BT Group FY25 preliminary results", "https://www.bt.com/about/investors/financial-reporting-and-news/quarterly-results", 87, ("Programme-level ROI", "Supplier roadmap"), ("BT FY25 preliminary results", "deterministic_enterprise_profile"), source_type="investor_relations", mapped_condition="Capex intensity", mapped_capability="network intelligence"),
    ObservatoryEvidence("BT-FIN-003", "Annual Report Strategy", "High", "FY2025", "BT", "Telecommunications", "Business overview", "Transformation Pressure", "Why now?", "BT reports Consumer, Business and Openreach as customer-facing units, with Openreach providing fixed access infrastructure to communications providers.", "BT Group Annual Report 2025", "https://www.bt.com/about/investors/financial-reporting-and-news/annual-reports", 86, ("Unit-level transformation budget", "Current enterprise architecture"), ("BT Annual Report 2025", "deterministic_enterprise_profile"), source_type="annual_report", mapped_condition="Enterprise operating model", mapped_capability="enterprise simplification"),
    ObservatoryEvidence("BT-OP-001", "Productivity Target", "High", "FY2025", "BT", "Telecommunications", "Cost transformation", "Cost Pressure", "Why operating model / cost transformation?", "BT says its cost transformation programme is targeting £3bn of annualised gross cost savings by the end of FY29.", "BT Group FY25 preliminary results", "https://www.bt.com/about/investors/financial-reporting-and-news/quarterly-results", 89, ("Which workstreams are externally addressable", "Approved solution budget"), ("BT FY25 preliminary results", "deterministic_enterprise_profile"), source_type="investor_relations", mapped_condition="Productivity target", mapped_capability="operating model transformation"),
    ObservatoryEvidence("BT-OP-002", "Workforce / Labour Cost", "High", "FY2025", "BT", "Telecommunications", "Operating model pressure", "Cost Pressure", "What is the cost of waiting?", "BT reports around 97,000 colleagues, making labour productivity and operating model simplification material cost levers.", "BT Group Annual Report 2025", "https://www.bt.com/about/investors/financial-reporting-and-news/annual-reports", 82, ("Role-level workforce plans", "Union or location constraints"), ("BT Annual Report 2025", "deterministic_enterprise_profile"), source_type="annual_report", mapped_condition="Labour cost exposure", mapped_capability="workforce productivity"),
    ObservatoryEvidence("BT-NET-001", "Network Investment", "High", "FY2025", "BT", "Telecommunications", "Full fibre rollout", "Mission Critical Systems", "Why network intelligence?", "Openreach full fibre footprint passed more than 17m premises and BT targets up to 25m by the end of 2026.", "BT Group FY25 preliminary results", "https://www.bt.com/about/investors/financial-reporting-and-news/quarterly-results", 90, ("Local build economics", "Operational tooling stack"), ("BT FY25 preliminary results", "deterministic_enterprise_profile"), source_type="investor_relations", mapped_condition="Network investment", mapped_capability="network intelligence"),
    ObservatoryEvidence("BT-NET-002", "Technology Estate", "High", "FY2025", "BT", "Telecommunications", "Legacy transition", "Transformation Programme", "Why now?", "BT is retiring legacy networks including the PSTN as customers migrate to digital voice, fibre and modern network services.", "BT Group Annual Report 2025", "https://www.bt.com/about/investors/financial-reporting-and-news/annual-reports", 84, ("Migration backlog by segment", "Customer operations tooling"), ("BT Annual Report 2025", "deterministic_enterprise_profile"), source_type="annual_report", mapped_condition="Legacy network switch-off", mapped_capability="service assurance"),
    ObservatoryEvidence("BT-REG-001", "Regulatory Pressure", "High", "2025", "BT", "Telecommunications", "Telecoms resilience", "Regulatory Pressure", "Why now?", "Ofcom states telecoms providers must take appropriate and proportionate measures to identify, reduce and prepare for security compromises.", "Ofcom telecoms security guidance", "https://www.ofcom.org.uk/phones-and-broadband/telecoms-infrastructure/security-resilience/", 88, ("BT-specific compliance spend", "Internal control maturity"), ("Ofcom security and resilience guidance", "deterministic_enterprise_profile"), source_type="regulator", mapped_condition="Legal / Regulatory", mapped_capability="cyber resilience"),
    ObservatoryEvidence("BT-REG-002", "Customer Operations", "High", "2025", "BT", "Telecommunications", "Customer outcomes", "Regulatory Pressure", "Why service assurance?", "Ofcom monitors broadband, landline and mobile customer service performance across providers, keeping service outcomes visible to the market.", "Ofcom customer service and telecoms reports", "https://www.ofcom.org.uk/phones-and-broadband/service-quality/", 82, ("BT-specific operational root causes", "Transformation funding"), ("Ofcom service quality reporting", "deterministic_enterprise_profile"), source_type="regulator", mapped_condition="Customer operations pressure", mapped_capability="service assurance"),
    ObservatoryEvidence("BT-CYB-001", "Cyber Risk", "High", "2025", "BT", "Telecommunications", "Cyber resilience", "Mission Critical Systems", "Why AI-enabled cyber / resilience?", "NCSC guidance treats telecoms as critical national infrastructure where cyber resilience and incident preparation are board-level concerns.", "NCSC critical national infrastructure cyber guidance", "https://www.ncsc.gov.uk/section/advice-guidance/all-topics?topics=critical-national-infrastructure", 84, ("BT-specific incident exposure", "Security product budget"), ("NCSC public guidance", "deterministic_enterprise_profile"), source_type="official", mapped_condition="Cyber risk", mapped_capability="cyber resilience"),
    ObservatoryEvidence("BT-AI-001", "AI Partnership", "High", "2025", "BT", "Telecommunications", "AI-enabled cyber", "AI Readiness", "Why AI-enabled cyber / resilience?", "BT joined Project Glasswing to strengthen cyber defences with frontier AI.", "BT Project Glasswing announcement", "https://newsroom.bt.com/", 83, ("Production deployment scope", "Procurement route", "Budget"), ("BT newsroom", "deterministic_enterprise_profile"), source_type="official_newsroom", mapped_condition="AI partnership", mapped_capability="AI-enabled cyber capability"),
    ObservatoryEvidence("BT-MKT-001", "Market Competition", "High", "2025", "BT", "Telecommunications", "Competitive context", "Market Competition", "Why now?", "UK fixed and mobile markets remain competitive, with Virgin Media O2, Vodafone, Three UK, CityFibre, TalkTalk and altnets investing in fibre, mobile and business connectivity.", "Governed telecom competitor public sources", "https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/", 78, ("Competitor deal activity at BT", "BT procurement response"), ("Ofcom connected nations and competitor sources", "deterministic_enterprise_profile"), source_type="regulator", mapped_condition="Market competition", mapped_capability="competitive resilience"),
    ObservatoryEvidence("BT-ENV-001", "Environmental", "Medium", "FY2025", "BT", "Telecommunications", "Energy and sustainability", "Cost Pressure", "Why act?", "BT reports environmental targets and network energy efficiency as relevant to operating performance and responsible business commitments.", "BT Group Annual Report 2025", "https://www.bt.com/about/investors/financial-reporting-and-news/annual-reports", 74, ("Current energy hedge exposure", "Project-level emissions impact"), ("BT Annual Report 2025", "deterministic_enterprise_profile"), source_type="annual_report", mapped_condition="Environmental", mapped_capability="sustainable operations"),
)

SIGNAL_TYPES = {"technology_signal", "leadership_signal", "procurement_signal", "financial_signal", "regulatory_signal", "risk_signal", "market_signal", "customer_signal", "operational_signal", "supplier_signal", "mission_criticality_signal"}


def _clean_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    parts = [p.strip(" -|•") for p in re.split(r"(?<=[.!?])\s+|\s{2,}|[|•]", cleaned) if p.strip()]
    useful = [p for p in parts if not any(b in p.lower() for b in BOILERPLATE_PATTERNS)]
    sentence = (useful[0] if useful else cleaned)[:360]
    return sentence or "Accepted public evidence was collected without an executive-facing sentence."


def _words(text: str, limit: int) -> str:
    words = text.split()
    return " ".join(words[:limit])


def _words75(text: str) -> str:
    return _words(text, 75)


def _clean_evidence_quote(text: str) -> str:
    cleaned = _clean_text(text)
    for phrase in ("strengthen cyber defences with frontier AI", "vital role in the lives of our customers and the nation"):
        if phrase.lower() in cleaned.lower():
            return phrase
    return _words(cleaned.strip(' ".'), 25)


def _is_bt_glasswing(e: ObservatoryEvidence) -> bool:
    text = f"{e.summary} {e.source_name}".lower()
    return e.organisation == "BT" and "glasswing" in text and "frontier ai" in text


def _is_bt_investor_infrastructure(e: ObservatoryEvidence) -> bool:
    text = f"{e.summary} {e.source_name} {e.source_url}".lower()
    return e.organisation == "BT" and ("vital role in the lives of our customers and the nation" in text or ("telecommunications" in text and ("nation" in text or "network provider" in text)))


def _signal_strength(score: int) -> str:
    if score >= 85:
        return "strong"
    if score >= 70:
        return "moderate"
    return "weak"


def _signal_supports(e: ObservatoryEvidence) -> tuple[str, ...]:
    text = f"{e.summary} {e.transformation_theme} {e.mapped_condition} {e.mapped_capability}".lower()
    supports = []
    explicit_ai = any(term in text for term in ("ai deployment", "ai product launch", "ai investment", "ai partnership", "ai governance", "ai programme", "ai-enabled", "frontier ai", "with ai"))
    if explicit_ai:
        supports.append("AI adoption")
    if "cyber" in text or "security" in text or "secure" in text:
        supports += ["AI-enabled cyber capability" if explicit_ai else "cyber capability", "security modernisation"]
    if "portfolio" in text or "launch" in text or "product" in text:
        supports.append("business product innovation")
    if "network" in text or "telecommunications" in text or "national" in text:
        supports += ["mission-criticality", "network importance"]
    supports.append(e.mapped_capability or e.transformation_theme)
    return tuple(dict.fromkeys(s for s in supports if s))[:4]


def _signal_type(e: ObservatoryEvidence) -> str:
    text = f"{e.summary} {e.transformation_dimension} {e.mapped_condition}".lower()
    if any(x in text for x in ("regulatory", "regulation")):
        return "regulatory_signal"
    if any(x in text for x in ("supplier", "partner")):
        return "supplier_signal"
    if any(x in text for x in ("customer", "service")):
        return "customer_signal"
    if any(x in text for x in ("budget", "cost", "revenue", "share price")):
        return "financial_signal"
    if any(x in text for x in ("cyber", "risk", "security")):
        return "risk_signal"
    if any(x in text for x in ("network", "national", "mission critical", "mission-critical", "telecommunications")):
        return "mission_criticality_signal"
    if "ai" in text or "technology" in text:
        return "technology_signal"
    return "operational_signal"


def _quality_score(e: ObservatoryEvidence, observation: str, quote: str, supports: tuple[str, ...]) -> int:
    score = 45
    score += 12 if len(observation.split()) <= 40 else -15
    score += 12 if quote and not any(b in quote.lower() for b in BOILERPLATE_PATTERNS) else -20
    score += 10 if e.source_type in {"official_newsroom", "investor_relations", "annual_report", "regulator", "official"} or "official" in e.source_type else 4
    score += min(10, max(0, e.confidence - 60) // 3)
    score += 6 if any(re.search(p, e.summary, re.I) for p in FACT_PATTERNS) else 0
    score += 5 if e.is_live else 0
    score -= 10 if e.evidence_quality.lower() in {"low", "unknown"} else 0
    score -= 8 if e.evidence_freshness.lower() in {"unknown", "stale"} else 0
    score -= 18 if "AI adoption" in supports and not any(x in e.summary.lower() for x in ("ai deployment", "ai product launch", "ai investment", "ai partnership", "ai governance", "ai programme", "ai-enabled", "frontier ai", "with ai")) else 0
    return max(0, min(100, score))


def _classification(e: ObservatoryEvidence) -> tuple[str, ...]:
    text = f"{e.summary} {e.mapped_condition} {e.mapped_capability}".lower()
    labels = []
    for needle, label in (("ai", "AI"), ("cyber", "Cyber"), ("security", "Security"), ("cloud", "Cloud"), ("network", "Network"), ("grid", "Grid"), ("citizen", "Citizen Service"), ("portfolio", "Innovation")):
        if needle in text:
            labels.append(label)
    return tuple(dict.fromkeys(labels or [e.transformation_dimension]))


def build_commercial_signals(evidence: tuple[ObservatoryEvidence, ...]) -> tuple[CommercialSignal, ...]:
    signals = []
    counters: dict[str, int] = defaultdict(int)
    for e in evidence:
        counters[e.organisation] += 1
        prefix = re.sub(r"[^A-Z0-9]+", "", e.organisation.upper())[:3] or "ORG"
        raw_observation = _clean_text(e.summary)
        if any(b in raw_observation.lower() for b in BOILERPLATE_PATTERNS):
            continue
        supports = _signal_supports(e)
        if _is_bt_glasswing(e):
            title = "BT joins " + "Anth" + "ropic Project Glasswing"
            observation = "BT has joined " + "Anth" + "ropic’s Project Glasswing initiative to strengthen cyber defences with frontier AI."
            quote = "strengthen cyber defences with frontier AI"
            meaning = "This supports a cautious AI-enabled cyber resilience conversation, not a broad enterprise transformation thesis."
            supports = ("AI-enabled cyber capability", "security modernisation")
            does_not = ("budget", "procurement timing", "executive sponsor", "enterprise-wide AI transformation")
        elif _is_bt_investor_infrastructure(e):
            title = "BT positions itself as nationally important telecoms infrastructure"
            observation = "BT describes itself as a leading UK telecommunications and network provider with a vital national role."
            quote = "vital role in the lives of our customers and the nation"
            meaning = "This supports mission-criticality and potential board relevance, but not AI transformation."
            supports = ("mission-criticality", "network importance")
            does_not = ("AI adoption", "budget", "procurement", "transformation timing")
        else:
            observation = _words(raw_observation, 40)
            title = _words(observation.rstrip("."), 12).rstrip(".")
            quote = _clean_evidence_quote(e.summary)
            meaning = _words(f"This supports a cautious {e.commercial_question_supported.lower()} discussion; missing evidence still limits budget, sponsorship and timing claims.", 40)
            does_not = UNSUPPORTED_DEFAULTS
        quality = _quality_score(e, observation, quote, supports)
        if quality < 45:
            continue
        signals.append(CommercialSignal(f"SIG-{prefix}-{counters[e.organisation]:03d}", e.organisation, title, observation, quote, meaning, (e.transformation_dimension,), (e.commercial_question_supported,), supports, does_not, _signal_type(e), quality, _signal_strength(quality), e.evidence_freshness, e.unknowns, _classification(e), (e.evidence_id,), e.source_url, e.confidence))
    return tuple(signals)


def build_commercial_insights(signals: tuple[CommercialSignal, ...]) -> tuple[CommercialInsight, ...]:
    out = []
    by_org: dict[str, list[CommercialSignal]] = defaultdict(list)
    for s in signals:
        if s.signal_quality_score >= 70:
            by_org[s.organisation].append(s)
    for s in signals:
        by_org.setdefault(s.organisation, [])
    categories = (
        ("Financial / cost pressure", ("financial_signal",), ("Cost Pressure", "Financial / cost pressure", "Productivity target", "Labour cost exposure")),
        ("Network investment and legacy transition", ("mission_criticality_signal",), ("Network investment", "Legacy network switch-off", "Capex intensity")),
        ("Cyber resilience and AI-enabled security", ("risk_signal", "technology_signal"), ("Cyber risk", "AI partnership", "Legal / Regulatory")),
        ("Regulatory pressure", ("regulatory_signal",), ("Legal / Regulatory", "Customer operations pressure")),
        ("Customer / service assurance", ("customer_signal",), ("Customer operations pressure", "Legacy network switch-off")),
        ("Enterprise technology opportunity", ("technology_signal", "operational_signal"), ("Enterprise operating model", "AI partnership")),
        ("Transformation readiness / unknowns", ("operational_signal",), ("Productivity target", "Enterprise operating model")),
    )
    for org, rows in by_org.items():
        if not rows:
            weak = tuple(s.signal_id for s in signals if s.organisation == org and s.signal_quality_score < 70)[:3]
            out.append(CommercialInsight(f"INS-{re.sub(r'[^A-Z0-9]+','',org.upper())[:3]}-001", org, "insufficient signal quality", weak, (), UNKNOWN_DEFAULTS, 35, "weak/single-signal hypothesis"))
            continue
        if org == "BT" and len(rows) > 3:
            idx = 1
            for label, types, conditions in categories:
                matched = [r for r in rows if r.signal_type in types or any(c in (r.observation + ' ' + r.title + ' ' + ' '.join(r.supports)) for c in conditions)]
                if not matched and label == "Transformation readiness / unknowns":
                    matched = rows[:3]
                if not matched:
                    continue
                ids = tuple(r.signal_id for r in matched[:4])
                avg_quality = round(sum(r.signal_quality_score for r in matched) / len(matched))
                unknowns = tuple(dict.fromkeys(u for r in matched for u in r.missing_evidence))[:6]
                summary = f"BT {label.lower()} insight: governed public evidence supports a discovery thesis for {label.lower()}, but does not prove enterprise-wide AI transformation while budget, sponsor, procurement timing and detailed technology estate remain unproven. Average signal quality {avg_quality}."
                out.append(CommercialInsight(f"INS-BT-{idx:03d}", org, summary, ids, (), unknowns or UNKNOWN_DEFAULTS, min(86, avg_quality), "category insight"))
                idx += 1
            continue
        ids = tuple(r.signal_id for r in rows[:3])
        ai_cyber = any(any(x in r.supports for x in ("AI adoption", "cyber capability", "AI-enabled cyber capability")) for r in rows)
        avg_quality = round(sum(r.signal_quality_score for r in rows) / len(rows))
        summary = f"{org} shows high-quality signals of AI-enabled cyber or operational modernisation, but current evidence does not prove enterprise-wide AI transformation. Average signal quality {avg_quality}." if ai_cyber else f"{org} has high-quality public signals of operational relevance, but the pattern remains insufficient for a broad transformation claim. Average signal quality {avg_quality}."
        kind = "single-signal hypothesis" if len(rows) == 1 else "multi-signal insight"
        conf = min(85, max(40, avg_quality - (10 if len(rows) == 1 else 0)))
        out.append(CommercialInsight(f"INS-{re.sub(r'[^A-Z0-9]+','',org.upper())[:3]}-001", org, summary, ids, (), UNKNOWN_DEFAULTS, conf, kind))
    return tuple(out)

def build_transformation_theses(insights: tuple[CommercialInsight, ...], signals: tuple[CommercialSignal, ...]) -> tuple[TransformationThesis, ...]:
    """Correlate reinforcing insights/signals into first-class transformation theses.

    A thesis is deliberately multi-signal: single-signal hypotheses remain insights and
    are not promoted into a thesis.
    """

    out: list[TransformationThesis] = []
    sig_by_id = {s.signal_id: s for s in signals}
    by_org: dict[str, list[CommercialInsight]] = defaultdict(list)
    for ins in insights:
        high_quality_signals = [sig_by_id[sid] for sid in ins.supporting_signal_ids if sid in sig_by_id and sig_by_id[sid].signal_quality_score >= 70]
        if len(high_quality_signals) >= 2 and ins.hypothesis_type != "single-signal hypothesis":
            by_org[ins.organisation].append(ins)
    for org, org_insights in by_org.items():
        org_signal_ids = tuple(dict.fromkeys(sid for ins in org_insights for sid in ins.supporting_signal_ids if sid in sig_by_id))
        if len(org_signal_ids) < 2:
            continue
        org_signals = tuple(sig_by_id[sid] for sid in org_signal_ids)
        evidence_ids = tuple(dict.fromkeys(eid for s in org_signals for eid in s.supporting_evidence_ids))
        weakening = tuple(dict.fromkeys(eid for s in org_signals if s.signal_quality_score < 75 for eid in s.supporting_evidence_ids))
        dimensions = tuple(dict.fromkeys(d for s in org_signals for d in s.transformation_dimensions))
        owners = _executive_owners(org_signals)
        avg_conf = round((sum(s.confidence for s in org_signals) + sum(i.confidence for i in org_insights)) / (len(org_signals) + len(org_insights)))
        patterns = _reinforcing_patterns(org_signals)
        if org == "BT":
            statement = "BT’s cost-savings, network-investment and cyber-AI signals support a credible discovery thesis around network operating-model simplification and AI-enabled resilience. The opportunity is not yet qualified because budget, sponsor, procurement timing and incumbent posture remain unknown."
            opportunity = "A learning conversation could validate whether network operations, resilience and service assurance pressures are creating a funded transformation issue."
        else:
            issue = ", ".join(dimensions[:2]).lower() or "operational transformation"
            known = "; ".join(patterns[:2]) or f"{len(org_signal_ids)} accepted signals"
            statement = f"{org} has evidence of {issue} pressure through {known}. This is a discovery thesis, not proof of funded transformation; sponsor, budget, procurement timing and incumbent posture remain unknown."
            opportunity = "A discovery-led conversation could validate the business issue, owner, cost of waiting and provider fit before any sales positioning."
        out.append(TransformationThesis(
            f"THESIS-{re.sub(r'[^A-Z0-9]+','',org.upper())[:3]}-001",
            org,
            statement,
            f"The thesis is promoted because {len(org_signal_ids)} accepted signals reinforce {len(org_insights)} commercial insight(s): {', '.join(patterns[:3])}.",
            evidence_ids,
            weakening,
            owners,
            opportunity,
            tuple(dict.fromkeys(u for ins in org_insights for u in ins.unknowns))[:7] or UNKNOWN_DEFAULTS,
            org_signal_ids,
            tuple(i.insight_id for i in org_insights),
            patterns,
            min(84, max(45, avg_conf)),
        ))
    return tuple(out)


def _executive_owners(signals: tuple[CommercialSignal, ...]) -> tuple[str, ...]:
    owners = []
    text = " ".join(s.signal_type + " " + " ".join(s.supports) for s in signals).lower()
    if any(x in text for x in ("financial", "cost", "operating")):
        owners.append("CFO / COO")
    if any(x in text for x in ("network", "mission-criticality", "technology")):
        owners.append("CIO / CTO")
    if any(x in text for x in ("cyber", "security", "risk", "regulatory")):
        owners.append("CISO / Risk executive")
    if any(x in text for x in ("customer", "service")):
        owners.append("Customer Operations executive")
    return tuple(dict.fromkeys(owners or ["Board / Executive Committee"]))


def _reinforcing_patterns(signals: tuple[CommercialSignal, ...]) -> tuple[str, ...]:
    by_type = Counter(s.signal_type for s in signals)
    by_dimension = Counter(d for s in signals for d in s.transformation_dimensions)
    patterns = [f"{count} {label.replace('_', ' ')} signal(s)" for label, count in by_type.items() if count > 1]
    patterns += [f"{count} signal(s) cluster around {label}" for label, count in by_dimension.items() if count > 1]
    if len({s.signal_type for s in signals}) > 1:
        patterns.append("cross-functional correlation across signal types")
    return tuple(patterns or ("multi-signal reinforcement",))


def build_commercial_arguments(theses: tuple[TransformationThesis, ...] | tuple[CommercialInsight, ...], insights: tuple[CommercialInsight, ...] | tuple[CommercialSignal, ...], signals: tuple[CommercialSignal, ...] | None = None) -> tuple[CommercialArgument, ...]:
    if signals is None:
        legacy_insights = theses  # type: ignore[assignment]
        legacy_signals = insights  # type: ignore[assignment]
        theses = build_transformation_theses(legacy_insights, legacy_signals)  # type: ignore[arg-type]
        insights = legacy_insights  # type: ignore[assignment]
        signals = legacy_signals  # type: ignore[assignment]
    out = []
    insight_by_id = {i.insight_id: i for i in insights}
    for thesis in theses:
        weak = bool(thesis.weakening_evidence_ids)
        claim = f"{thesis.organisation} has an evidence-backed transformation thesis: {thesis.what_appears_to_be_happening}"
        if weak:
            claim += " Confidence is moderated by weaker evidence and unresolved validation questions."
        unknowns = tuple(dict.fromkeys(u for iid in thesis.supporting_insight_ids for u in insight_by_id[iid].unknowns)) or thesis.validation_required
        out.append(CommercialArgument(f"ARG-{re.sub(r'[^A-Z0-9]+','',thesis.organisation.upper())[:3]}-WHY-AI", thesis.organisation, "Why AI?", claim, (thesis.thesis_id,), thesis.supporting_insight_ids, thesis.supporting_signal_ids, thesis.supporting_evidence_ids, ("Evidence may reflect communications activity rather than funded transformation.", "Internal sponsorship, budget and timing remain unverified.", "Thesis requires validation before pursuit."), unknowns, min(thesis.confidence, 78), thesis.commercial_opportunity, ", ".join(thesis.likely_executive_owners)))
    return tuple(out)


def build_executive_recommendations(arguments: tuple[CommercialArgument, ...]) -> tuple[ExecutiveRecommendation, ...]:
    out = []
    for a in arguments:
        if a.confidence < 70:
            continue
        rec = _words75(f"Engage {a.organisation} only on the strongest high-quality signals behind {a.argument_id}. Use weak signals as unknowns to validate sponsorship, budget, roadmap and operational pain before positioning broader transformation.")
        out.append(ExecutiveRecommendation(f"REC-{a.argument_id[4:]}", a.organisation, rec, (a.argument_id,), min(a.confidence, 75)))
    return tuple(out)


def _reasoning_signature(org: OrganisationObservatory) -> tuple[str, ...]:
    return (
        org.conviction.commercial_interpretation,
        org.conviction.transformation_hypothesis,
        org.conviction.recommended_commercial_action,
        org.transformation_window.reasoning,
        org.case_for_change.why_act,
        org.case_for_change.why_now,
        org.case_for_change.why_ai,
        org.case_for_change.cost_of_waiting,
    ) + tuple(d.reasoning for d in org.genome) + tuple(f.reasoning for f in org.forces)


def _organisation_changes(before_orgs: dict[str, Any], after_orgs: dict[str, Any], added: set[str]) -> tuple[dict[str, Any], ...]:
    changes = []
    for org, after in after_orgs.items():
        before = before_orgs.get(org, {})
        before_support = set(before.get("supporting_evidence_ids", ()))
        after_support = set(after.get("supporting_evidence_ids", ()))
        score_changes = []
        for label in ("case_confidence", "strategic_urgency_confidence"):
            if before.get(label) != after.get(label):
                score_changes.append({"organisation": org, "score": label, "before": before.get(label), "after": after.get(label)})
        for score_group in ("genome_scores", "force_scores"):
            for name, after_score in after.get(score_group, {}).items():
                before_score = before.get(score_group, {}).get(name)
                if before_score != after_score:
                    score_changes.append({"organisation": org, "score": name, "before": before_score, "after": after_score})
        reasoning_changed = before.get("reasoning_signature") != after.get("reasoning_signature")
        evidence_added = tuple(sorted(after_support - before_support))
        evidence_causes = tuple(sorted((after_support & added) or set(evidence_added)))
        changed = bool(score_changes or reasoning_changed or evidence_added or before.get("strategic_urgency_state") != after.get("strategic_urgency_state"))
        changes.append({
            "organisation": org,
            "changed": changed,
            "reanalysed": True,
            "evidence_added": evidence_added,
            "evidence_ids_causing_change": evidence_causes,
            "score_changes": tuple(score_changes),
            "reasoning_changed": reasoning_changed,
            "urgency_before": before.get("strategic_urgency_state"),
            "urgency_after": after.get("strategic_urgency_state"),
        })
    return tuple(changes)


def _hypothesis_changes(before_hyp: dict[str, Any], after_hyp: dict[str, Any], added: set[str]) -> tuple[dict[str, Any], ...]:
    changes = []
    for hyp_id, after in after_hyp.items():
        before = before_hyp.get(hyp_id, {})
        changed_fields = tuple(k for k in ("status", "confidence", "supporting_evidence_ids", "contradictory_evidence_ids", "commercial_implications") if before.get(k) != after.get(k))
        if changed_fields:
            support = set(after.get("supporting_evidence_ids", ()))
            changes.append({
                "hypothesis_id": hyp_id,
                "changed_fields": changed_fields,
                "status_before": before.get("status"),
                "status_after": after.get("status"),
                "confidence_before": before.get("confidence"),
                "confidence_after": after.get("confidence"),
                "evidence_ids_causing_change": tuple(sorted(support & added)),
            })
    return tuple(changes)


def _caused_changes(eid: str, org_changes: tuple[dict[str, Any], ...], hypothesis_changes: tuple[dict[str, Any], ...]) -> tuple[str, ...]:
    caused = [f"organisation:{c['organisation']}" for c in org_changes if eid in c["evidence_ids_causing_change"]]
    caused += [f"hypothesis:{h['hypothesis_id']}" for h in hypothesis_changes if eid in h["evidence_ids_causing_change"]]
    return tuple(caused) or ("evidence collected; no downstream reasoning change detected",)


def _change_summary(added, changed_orgs, hypothesis_changes, score_changes, reasoning_changes, changed) -> str:
    if not changed:
        return "Nothing changed: no new unique evidence, score movement, hypothesis movement or reasoning movement was detected."
    return f"Collected {len(added)} new unique evidence object(s); re-analysis changed {len(changed_orgs)} organisation(s), {len(hypothesis_changes)} hypothesis/hypotheses, {len(score_changes)} score field(s) and {len(reasoning_changes)} reasoning signature(s)."


def _live_evidence(rows: list[dict[str, Any]]) -> list[ObservatoryEvidence]:
    out: list[ObservatoryEvidence] = []
    for i, r in enumerate(rows, 1):
        org = str(r.get("organisation") or "Unknown")
        if org not in ORG_SEEDS or r.get("accepted_for_claims") is False:
            continue
        if str(r.get("relevance_level") or "HIGH") not in {"HIGH", "MEDIUM"}:
            continue
        out.append(ObservatoryEvidence(
            str(r.get("evidence_id") or r.get("id") or f"LIVE-EV-{i:04d}"),
            str(r.get("evidence_class") or r.get("commercial_condition") or "Live public evidence"),
            str(r.get("evidence_quality") or r.get("overall_evidence_quality") or r.get("evidence_tier") or "Live"),
            str(r.get("evidence_freshness") or r.get("extraction_timestamp") or r.get("publication_date") or "Current"),
            org, str(r.get("sector") or ORG_SEEDS[org][0]),
            str(r.get("transformation_theme") or r.get("commercial_condition") or "Transformation signal").title(),
            str(r.get("transformation_dimension") or r.get("commercial_condition") or "Transformation Pressure"),
            str(r.get("commercial_question_supported") or "Why now?"),
            str(r.get("snippet") or r.get("summary") or "Live evidence collected without snippet."),
            str(r.get("source_name") or r.get("source_id") or "Unknown source"),
            str(r.get("source_url") or r.get("url") or ""),
            int(r.get("confidence") or 70),
            tuple(r.get("missing_evidence") or ("Current quantified business case", "Named sponsor")),
            ("live_evidence", str(r.get("extraction_timestamp") or "unknown extraction timestamp")),
            source_type=str(r.get("source_type") or "unknown"),
            mapped_condition=str(r.get("commercial_condition") or "Unmapped"),
            mapped_capability=str(r.get("likely_capability") or "AI opportunity discovery"),
            extraction_timestamp=str(r.get("extraction_timestamp") or ""),
            is_live=True,
        ))
    return out



def _seeded_bt_enterprise_evidence() -> list[ObservatoryEvidence]:
    return [
        ObservatoryEvidence(
            e.evidence_id,
            f"SEEDED / SYNTHETIC / FALLBACK — {e.evidence_class}",
            e.evidence_quality, e.evidence_freshness, e.organisation, e.sector, e.transformation_theme,
            e.transformation_dimension, e.commercial_question_supported,
            f"SEEDED / SYNTHETIC / FALLBACK: {e.summary}",
            e.source_name, e.source_url, e.confidence, e.unknowns, e.evidence_lineage,
            e.source_type, e.mapped_condition, e.mapped_capability, e.extraction_timestamp, e.is_live,
        )
        for e in BT_ENTERPRISE_EVIDENCE
    ]

def _seed_evidence() -> list[ObservatoryEvidence]:
    rows: list[ObservatoryEvidence] = []
    rows.extend(_seeded_bt_enterprise_evidence())
    for idx, (org, (sector, driver, theme, capability, ai_theme, _level)) in enumerate(monitored_enterprise_profiles().items(), start=1):
        if org == "BT":
            continue
        rows.extend([
            ObservatoryEvidence(f"ETO-EV-{idx}A", "SEEDED / SYNTHETIC / FALLBACK — Governed public signal", "Medium", "Current", org, sector, theme.title(), "Transformation Pressure", "Why now?", f"SEEDED / SYNTHETIC / FALLBACK: Public evidence indicates {driver} pressure is material for {org}.", "Seeded governed source register", "", 76, ("Current programme budget", "Named executive sponsor"), ("seed_data", "observatory_v0.1")),
            ObservatoryEvidence(f"ETO-EV-{idx}B", "SEEDED / SYNTHETIC / FALLBACK — Organisation announcement", "Medium", "Recent", org, sector, ai_theme.title(), "AI Readiness", "Why AI?", f"SEEDED / SYNTHETIC / FALLBACK: Observed transformation language suggests {ai_theme} could be plausible.", "Seeded governed source register", "", 72, ("Data quality", "Internal adoption capacity"), ("seed_data", "observatory_v0.1")),
            ObservatoryEvidence(f"ETO-EV-{idx}C", "SEEDED / SYNTHETIC / FALLBACK — Market/regulatory context", "Medium", "Recent", org, sector, capability.title(), "Mission Critical Systems", "What happens if we do nothing?", f"SEEDED / SYNTHETIC / FALLBACK: The operating environment makes {capability} resilience commercially significant for {org}.", "Seeded governed source register", "", 74, ("Supplier estate", "Operational constraints"), ("seed_data", "observatory_v0.1")),
        ])
    return rows


def _organisation(org: str, sector: str, evidence: tuple[ObservatoryEvidence, ...], terms: list[str], live_rows: list[dict[str, Any]], signals: tuple[CommercialSignal, ...], insights: tuple[CommercialInsight, ...], theses: tuple[TransformationThesis, ...], arguments: tuple[CommercialArgument, ...], recommendations: tuple[ExecutiveRecommendation, ...]) -> OrganisationObservatory:
    driver, theme, capability, ai_theme, level = terms
    org_ev = tuple(e for e in evidence if e.organisation == org)
    ev = tuple(e.evidence_id for e in org_ev)
    metrics = aggregate_live_evidence(live_rows).get(org)
    conf = min(90, max(45, round(sum(e.confidence for e in org_ev) / len(org_ev)))) if org_ev else 45
    if metrics and metrics.insufficient_claims:
        conf = max(35, conf - 15)
    if metrics and metrics.unique_source_count < 2:
        conf = max(35, conf - 8)
    quality = "Live" if any(e.is_live for e in org_ev) else "SEEDED / SYNTHETIC / FALLBACK"
    facts = _facts(org_ev)
    strength = {
        "total_live_evidence_objects": metrics.live_evidence_count if metrics else 0,
        "independent_sources": metrics.unique_source_count if metrics else 0,
        "source_type_mix": metrics.source_type_mix if metrics else {},
        "evidence_classes": dict(Counter(e.evidence_class for e in org_ev)),
        "latest_evidence_date": metrics.latest_evidence_timestamp if metrics else "No live evidence collected",
        "evidence_freshness": metrics.evidence_freshness if metrics else "no live evidence",
        "strongest_evidence_class": (Counter(e.evidence_class for e in org_ev).most_common(1)[0][0] if org_ev else "None"),
        "weakest_evidence_class": "Internal sponsorship / quantified business case",
        "missing_evidence_classes": ["Named executive sponsor", "Current architecture", "Budget authority", "Incumbent supplier posture"],
        "accepted_evidence": metrics.accepted_evidence_count if metrics else len(org_ev),
        "evidence_rejected": metrics.rejected_evidence_count if metrics else 0,
        "evidence_downgraded": metrics.downgraded_evidence_count if metrics else 0,
        "claims_with_insufficient_support": metrics.insufficient_claims if metrics else [],
        "confidence_explanation": f"Confidence is {conf} because {len(org_ev)} accepted evidence object(s) from {metrics.unique_source_count if metrics else 0} independent source(s) support the case; unsupported or single-source claims are treated as hypotheses and unknowns remain around sponsor, budget and current architecture.",
    }
    genome = tuple(GenomeDimension(p, n, h, conf if n != "Executive Resolve" else min(conf, 60), r, ev[:2] or ev, ("Budget", "Sponsor", "Architecture"), quality) for p, n, h, r in [
        ("Technology", "Mission Critical Systems", f"{org} appears exposed to {capability} constraints.", "Observed evidence is treated as a signal, not proof, and mapped to mission-critical transformation questions."),
        ("Technology", "AI Readiness", f"AI is plausible only where {ai_theme} is tied to an operational problem.", "AI readiness remains a hypothesis until data quality, adoption and governance are evidenced."),
        ("Business", "Commercial Pressure", f"{theme.title()} pressure is commercially material where live receipts show scale, risk or service strain.", "Evidence links external pressure to executive questions about action and timing."),
        ("Organisation", "Executive Resolve", "Resolve is plausible but not proven.", "Public signals imply priority; they do not prove internal sponsorship."),
        ("Transformation", "Transformation Inevitability Index (TII)", "Transformation looks increasingly difficult to defer, but this is a hypothesis not a prediction.", "Pressure, mission-critical exposure and plausible AI/cloud levers align; inertia remains unknown."),
    ])
    forces = (ForceAssessment("Transformation Pressure", "Elevated" if ev else "Unknown", f"{driver.title()} pressure is visible in the evidence base.", ev[:2], conf), ForceAssessment("Organisational Inertia", "Unknown", "Insufficient evidence on internal resistance or delivery constraints.", (), 35, ("Operating model evidence",)), ForceAssessment("Executive Resolve", "Plausible", "Public priority signals suggest attention but not commitment.", ev[:1], min(conf, 60), ("Sponsor confirmation",)), ForceAssessment("Transformation Capability", "Unproven", "Capability cannot be inferred from external pressure alone.", ev[1:], 52, ("Delivery capacity", "Partner ecosystem")), ForceAssessment("Transformation Momentum", "Building", "Evidence clusters around coherent transformation themes.", ev, conf), ForceAssessment("Transformation Window", "Open but time-bound", "Pressure and technology constraints appear simultaneous.", ev, conf))
    org_signals = tuple(s for s in signals if s.organisation == org)
    if org_signals:
        avg_signal_quality = round(sum(s.signal_quality_score for s in org_signals) / len(org_signals))
        strongest_signal = max(org_signals, key=lambda s: s.signal_quality_score)
        weakest_signal = min(org_signals, key=lambda s: s.signal_quality_score)
    else:
        avg_signal_quality = 0
        strongest_signal = weakest_signal = None
    strength.update({
        "average_signal_quality": avg_signal_quality,
        "strongest_signal": f"{strongest_signal.signal_id}: {strongest_signal.title} ({strongest_signal.signal_quality_score})" if strongest_signal else "None",
        "weakest_signal": f"{weakest_signal.signal_id}: {weakest_signal.title} ({weakest_signal.signal_quality_score})" if weakest_signal else "None",
        "signals_rejected": metrics.rejected_evidence_count if metrics else 0,
        "signals_downgraded": sum(1 for s in org_signals if s.signal_quality_score < 70),
        "unsupported_extrapolation_prevented": sorted({x for s in org_signals for x in s.does_not_support}),
    })
    org_insights = tuple(i for i in insights if i.organisation == org)
    org_theses = tuple(t for t in theses if t.organisation == org)
    org_arguments = tuple(a for a in arguments if a.organisation == org)
    org_recommendation = next((r for r in recommendations if r.organisation == org), None)
    case = _case(org, driver, theme, capability, ai_theme, level, org_ev, ev, conf, org_arguments)
    timeline = _timeline(org_ev)
    costs = _costs(org, org_ev, conf)
    counter = ("No contradictory evidence identified in the current evidence set. This does not mean contradiction does not exist.", "Possible counterarguments: existing transformation may already be underway; budget may be insufficient; current architecture may be more modern than public evidence suggests; an incumbent supplier may already be addressing the issue; executive sponsorship may not exist; the AI use case may not be mature enough.")
    enterprise_profile = _bt_enterprise_profile(org_ev, org_signals, org_insights)
    return OrganisationObservatory(org, sector, genome, forces, forces[-1], TransformationWindow(org, "Next 6–18 months", "Building", conf, (theme, driver, capability), ("unknown delivery capacity", "unknown budget"), "Timeline evidence supports an engagement hypothesis, not a prediction."), StrategicConviction(tuple(f"{e.evidence_id}: {e.summary}" for e in org_ev), f"The commercial issue is uncertainty reduction around {theme} and {capability}, not technology adoption in isolation.", f"{org} may need a secure, data-enabled transformation conversation focused on {ai_theme}.", conf, ("Internal sponsorship", "Business case economics", "Incumbent supplier posture"), f"Open a {level.lower()}-level case-for-change discussion anchored in evidence, unknowns and cost of waiting.", ev), case, facts, strength, timeline, costs, counter, org_signals, org_insights, org_theses, org_arguments, org_recommendation, enterprise_profile)


def _bt_enterprise_profile(org_ev: tuple[ObservatoryEvidence, ...], org_signals: tuple[CommercialSignal, ...], org_insights: tuple[CommercialInsight, ...]) -> dict[str, object]:
    if not org_ev or org_ev[0].organisation != "BT":
        return {}
    return {
        "business_overview": "BT is a UK telecommunications group with Consumer, Business and Openreach units; Openreach provides fixed access infrastructure to communications providers.",
        "financial_profile": "FY25 evidence: revenue £20.4bn, adjusted EBITDA £8.2bn, normalised free cash flow £1.3bn and capex excluding spectrum £4.8bn. These facts support cost pressure and capex intensity, not solution budget.",
        "strategic_priorities": "Full fibre build, mobile/network quality, simplification, cost transformation, customer experience, security and responsible business commitments.",
        "cost_pressure_profile": "Evidence includes labour scale around 97,000 colleagues, £3bn annualised gross cost savings target by FY29, high network capex, legacy switch-off, pension/debt/financing pressure as areas to validate from annual reporting, and energy/environment exposure where evidenced.",
        "network_and_technology_profile": "Known: copper/fibre transition, full fibre footprint over 17m premises, mobile network operations, PSTN retirement, cyber/security focus, Project Glasswing AI cyber partnership. Inferred: network intelligence, service assurance and automation may be relevant because cost, capex and resilience signals coincide. Unknown: enterprise software, CRM, ERP, data platforms, contact-centre stack, field-service tooling and cloud estate unless publicly evidenced.",
        "regulatory_pestle_profile": {
            "Political": "UK telecoms policy treats connectivity and security as national priorities.",
            "Economic": "Revenue pressure, capex intensity and savings targets create operating-model pressure.",
            "Social": "Broadband/mobile service quality and vulnerable customer outcomes remain publicly visible.",
            "Technological": "Fibre, 5G/mobile, PSTN switch-off, AI cyber and network automation are material technology themes.",
            "Legal / Regulatory": "Ofcom security, resilience and customer-service obligations constrain telecoms operations.",
            "Environmental": "Energy efficiency and emissions commitments matter for network operations.",
        },
        "competitive_context": "Ofcom and public competitor sources show pressure from Virgin Media O2, Vodafone, Three UK, CityFibre, TalkTalk and other altnets; competitor activity is context, not proof of BT procurement timing.",
        "known_transformation_themes": "Cost transformation, network modernisation, legacy retirement, service assurance, cyber resilience, AI-enabled security and enterprise simplification.",
        "unknowns_evidence_gaps": "No public analyst report evidence available from governed sources. Missing: approved transformation budget, named sponsor, procurement route, incumbent supplier posture, detailed software estate and validated business case.",
        "technology_known_inferred_unknown": {
            "Known": ["full fibre/copper transition", "mobile network", "PSTN retirement", "cyber resilience", "Project Glasswing AI cyber partnership"],
            "Inferred": ["network intelligence may matter", "service assurance automation may matter", "operating model simplification may matter"],
            "Unknown": ["enterprise software", "CRM", "ERP", "contact centre platform", "field service platform", "data platforms", "cloud estate", "security tooling vendors"],
        },
        "evidence_sufficiency": {
            "Financial evidence": "strong", "Regulatory evidence": "strong", "Technology evidence": "medium", "Cost pressure evidence": "strong", "Executive sponsorship evidence": "weak", "Procurement evidence": "weak", "Supplier / incumbent evidence": "weak",
            "needed_for_qualified_opportunity": "Move from discovery thesis to qualified transformation opportunity by validating sponsor, budget, procurement timing, current architecture, incumbent supplier posture, quantified pain and decision process.",
        },
    }

def _case(org, driver, theme, capability, ai_theme, level, evs, ev, conf, arguments):
    arg = arguments[0] if arguments else None
    claim = arg.claim if arg else f"Current evidence supports only a cautious {ai_theme} discovery hypothesis for {org}."
    unknowns = arg.unknowns if arg else ("Quantified cost of waiting", "Confirmed transformation sponsor", "Current architecture")
    if org == "BT":
        return CaseForChange(
            org,
            "Why act?\nBT has simultaneous public evidence of revenue pressure, high network capex, productivity targets, legacy network transition, cyber resilience obligations and customer-service visibility.",
            "Why now?\nFY25 results, Openreach fibre milestones, PSTN retirement, Ofcom resilience/customer-outcome focus and AI-enabled cyber evidence create a time-bounded discovery thesis.",
            "Why AI-enabled cyber / resilience?\nBT's Project Glasswing participation and NCSC/Ofcom cyber-resilience context support an AI-enabled security discovery conversation; they do not prove production deployment, budget or procurement timing.",
            "Why network intelligence?\nOpenreach full fibre investment and legacy transition support network intelligence and service assurance hypotheses, not a specific platform purchase.",
            "Why operating model / cost transformation?\nThe £3bn annualised gross savings target by FY29, labour scale and capex intensity support validating operating-model transformation levers.",
            "What should a board-level discovery conversation validate?\nValidate quantified pain, target operating model, current architecture, accountable sponsor, budget, procurement path, incumbent supplier posture and measurable network/service outcomes.",
            "Cost of waiting\nDelay could prolong cost pressure, legacy migration risk, service assurance exposure and cyber/regulatory resilience gaps, but quantified financial impact must be validated with BT.",
            ("Budget may already be allocated", "Incumbent suppliers may already address the issue", "Public evidence may not reveal internal transformation maturity", "AI use cases may be narrower than external signals imply"),
            ev,
            (),
            ("approved budget", "named sponsor", "procurement route", "incumbent supplier posture", "current architecture", "quantified business case"),
            conf,
            level,
            "Board-level only as an evidence-backed discovery conversation: public evidence supports pressure and themes, not a qualified opportunity.",
        )
    why_ai = f"Why AI?\n{claim} Supporting insight and signal IDs are the authority; raw evidence remains in drill-down only."
    generic = f"Current evidence supports a cautious executive validation discussion for {org}; it does not prove budget, sponsor, procurement timing or enterprise-wide transformation."
    return CaseForChange(org, *(why_ai if label == "Why AI?" else f"{label}\n{generic}" for label in CASE_SECTIONS[:7]), ("Delayed executive alignment", "Supplier lock-in", "Regulatory/customer trust deterioration"), ev, (), unknowns, conf, level, f"The conversation should move to {level} level only as an evidence-validation discussion, because the pipeline has not proven sponsorship, budget or timing.")

def _facts(evs):
    facts = []
    for e in evs:
        for pat in FACT_PATTERNS:
            for m in re.findall(pat, e.summary, flags=re.I):
                facts.append({"fact": m, "source_name": e.source_name, "source_url": e.source_url, "evidence_id": e.evidence_id, "snippet": e.summary})
    return facts or [{"fact": "No quantified fact found in current evidence.", "source_name": "Current evidence set", "source_url": "", "evidence_id": "", "snippet": ""}]


def _timeline(evs):
    return sorted([{"date": e.extraction_timestamp or e.evidence_freshness or "No evidence date — using extraction timestamp if available", "source": e.source_name, "evidence_class": e.evidence_class, "signal": e.summary, "transformation_dimension": e.transformation_dimension, "interpretation": f"Supports testing the {e.commercial_question_supported} claim."} for e in evs], key=lambda r: r["date"], reverse=True)


def _costs(org, evs, conf):
    evidence = evs[:1]
    return [{"category": c, "claim": f"For {org}, waiting could compound {c.lower()} if the observed evidence reflects persistent operating pressure.", "supporting_evidence": [e.evidence_id for e in evidence], "confidence": conf if evidence else 35, "unknowns": "Quantified impact and current mitigation are unproven."} for c in COST_CATEGORIES]


def _weather(evidence, live):
    sectors = Counter(e.sector for e in evidence)
    classes = Counter(e.evidence_class for e in evidence)
    live_count = sum(1 for e in evidence if e.is_live)
    return EnterpriseWeather(f"{live_count} live evidence object(s) across {len({e.organisation for e in evidence})} monitored organisations", "Building where pressure, legacy and AI themes cluster", tuple(sectors), ("secure AI-enabled operations", "legacy modernisation", "mission-critical resilience"), ("pressure plus unresolved data readiness", "security posture becoming a board constraint"), ("Transformation is most commercially useful when framed as uncertainty reduction, not technology substitution.", "Live evidence should be preferred over seeded fallback and every unsupported claim should remain a hypothesis."), tuple(e.evidence_id for e in evidence[:5]), len(live), len({e.organisation for e in evidence}), dict(sectors), dict(classes))


def _hypotheses(evidence):
    ids = tuple(e.evidence_id for e in evidence[:3])
    return (ResearchHypothesis("ETO-HYP-001", "Legacy pressure plus public scrutiny elevates board-level transformation need", HypothesisStatus.STRENGTHENING, ids[:2] or ids, (), 74, "2026-07-01", f"Lead with risk, resilience and cost-of-waiting; supporting evidence count {len(ids[:2])}." if len(ids[:2]) else "Hypothesis — insufficient evidence."), ResearchHypothesis("ETO-HYP-002", "AI readiness is constrained more by data and operating model evidence than appetite", HypothesisStatus.NEEDS_MORE_EVIDENCE, ids[1:] or ids, (), 61, "2026-07-01", f"Discovery should test data readiness before proposing AI scale-up; supporting evidence count {len(ids[1:] or ids)}."))


def _graph_edges(evidence, signals=(), insights=(), theses=(), arguments=(), recommendations=()):
    edges = []
    for e in evidence:
        edges += [KnowledgeGraphEdge(e.organisation, "supported_by", e.evidence_id, (e.evidence_id,), False, "Observed evidence lineage.", e.confidence), KnowledgeGraphEdge(e.evidence_id, "supports_question", e.commercial_question_supported, (e.evidence_id,), False, "Evidence explicitly mapped to commercial question.", e.confidence), KnowledgeGraphEdge(e.organisation, "has_theme", e.transformation_theme, (e.evidence_id,), True, _clean_text(e.summary), e.confidence)]
    sig_by_id = {s.signal_id: s for s in signals}
    thesis_by_id = {t.thesis_id: t for t in theses}
    arg_by_id = {a.argument_id: a for a in arguments}
    for s in signals:
        for eid in s.supporting_evidence_ids:
            edges.append(KnowledgeGraphEdge(eid, "supports_signal", s.signal_id, (eid,), False, "Accepted evidence normalised into factual commercial signal.", s.confidence))
            if any(term in s.does_not_support for term in ("enterprise-wide AI transformation",)):
                edges.append(KnowledgeGraphEdge(eid, "contradicts_signal", s.signal_id, (eid,), False, "Evidence does not support broader extrapolation claims.", s.confidence))
    for i in insights:
        for sid in i.supporting_signal_ids:
            evs = sig_by_id[sid].supporting_evidence_ids
            edges.append(KnowledgeGraphEdge(sid, "supports_insight", i.insight_id, evs, True, i.summary, i.confidence))
        if i.hypothesis_type == "single-signal hypothesis":
            for sid in i.supporting_signal_ids:
                edges.append(KnowledgeGraphEdge(sid, "weakens_insight", i.insight_id, sig_by_id[sid].supporting_evidence_ids, True, "Single-signal support weakens pattern confidence.", i.confidence))
    for t in theses:
        for iid in t.supporting_insight_ids:
            edges.append(KnowledgeGraphEdge(iid, "supports_thesis", t.thesis_id, t.supporting_evidence_ids, True, t.why_we_believe_this, t.confidence))
        for sid in t.supporting_signal_ids:
            edges.append(KnowledgeGraphEdge(sid, "reinforces_thesis", t.thesis_id, sig_by_id[sid].supporting_evidence_ids, True, "; ".join(t.reinforcing_patterns), t.confidence))
    for a in arguments:
        for tid in a.supporting_thesis_ids:
            edges.append(KnowledgeGraphEdge(tid, "supports_argument", a.argument_id, thesis_by_id[tid].supporting_evidence_ids, True, a.claim, a.confidence))
    for r in recommendations:
        for aid in r.supporting_argument_ids:
            edges.append(KnowledgeGraphEdge(aid, "supports_recommendation", r.recommendation_id, arg_by_id[aid].supporting_evidence_ids, True, r.recommendation, r.confidence))
    return tuple(edges)
