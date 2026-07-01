"""Enterprise Opportunity Shaping Engine (EOSE).

The engine is deliberately enterprise-generic: organisation-specific outputs are
computed from enterprise metadata, sector characteristics, transformation themes,
role structures and evidence chains rather than from bespoke account rules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean

from cios.applications.flora.models import EvidenceItem, Signal, TargetAccount
from cios.applications.flora.provider_context import ProviderContext, default_provider_context

UNIVERSAL_SOURCES = ["Annual Reports", "Investor Relations", "News", "Press Releases", "Executive Speeches", "Careers", "Financial Results", "Regulatory Filings", "Procurement", "Technology Partnerships"]
SECTOR_SOURCES = {
    "Government": ["GOV.UK", "NAO", "IPA", "Contracts Finder", "Find a Tender", "Parliamentary Committees"],
    "Public Sector": ["GOV.UK", "NAO", "IPA", "Contracts Finder", "Find a Tender", "Parliamentary Committees"],
    "Utilities": ["Ofwat", "Ofgem", "Environment Agency"],
    "Telecommunications": ["Ofcom", "Connected Nations", "Telecom Security publications"],
    "Healthcare": ["NHS England", "CQC", "MHRA"],
    "Banking": ["FCA", "PRA"],
    "Energy": ["DESNZ", "Ofgem", "NESO"],
}

THEME_KEYWORDS = {
    "AI Transformation": ("ai", "automation", "intelligence", "productivity"),
    "Cyber Resilience": ("cyber", "secure", "security", "resilience"),
    "Cloud Modernisation": ("cloud",),
    "Legacy Replacement": ("legacy", "modernisation", "modernization", "debt"),
    "Enterprise Platforms": ("platform",),
    "ERP Modernisation": ("erp", "shared services"),
    "Customer Experience": ("customer", "citizen", "retention", "trust"),
    "Operational Resilience": ("resilience", "operational", "reliability"),
    "Service Transformation": ("service", "casework", "citizen"),
    "Workforce Transformation": ("workforce", "field force", "productivity"),
    "Network Modernisation": ("network", "fibre", "connectivity"),
    "Data Platform": ("data", "analytics", "forecasting"),
    "Digital Channels": ("digital", "channels"),
    "Cost Transformation": ("cost", "efficiency", "simplification"),
    "Shared Services": ("shared services",),
    "Secure by Design": ("secure", "security"),
    "Automation": ("automation", "automate"),
    "Observability": ("observability", "assurance", "monitoring"),
    "Digital Operations": ("operations", "operational", "field"),
    "Enterprise Integration": ("integration",),
}

OWNERSHIP = {
    "Cyber Resilience": ("Chief Information Security Officer", "Chief Information Officer", "Chief Financial Officer", "Chief Technology Officer", "Chief Operating Officer"),
    "Network Modernisation": ("Chief Technology Officer", "Chief Operating Officer", "Chief Financial Officer", "Network Operations Director", "Chief Information Officer"),
    "Operational Resilience": ("Chief Operating Officer", "Chief Information Officer", "Chief Financial Officer", "Operations Director", "Risk Director"),
    "Customer Experience": ("Chief Customer Officer", "Chief Digital Officer", "Chief Financial Officer", "Head of Customer Operations", "Chief Operating Officer"),
    "Service Transformation": ("Chief Digital and Information Officer", "Chief Operating Officer", "Chief Financial Officer", "Service Director", "Commercial Director"),
    "Legacy Replacement": ("Chief Information Officer", "Chief Digital Officer", "Chief Financial Officer", "Enterprise Architect", "Chief Operating Officer"),
    "Data Platform": ("Chief Data Officer", "Chief Information Officer", "Chief Financial Officer", "Data Platform Director", "Chief Operating Officer"),
}
DEFAULT_OWNERSHIP = ("Chief Information Officer", "Chief Operating Officer", "Chief Financial Officer", "Chief Technology Officer", "Transformation Director")

@dataclass(frozen=True)
class EnterpriseDNA:
    sector: str
    business_model: str
    mission_criticality: str
    technology_intensity: str
    operational_complexity: str
    regulatory_intensity: str
    customer_criticality: str
    security_criticality: str
    transformation_pressure: str
    transformation_capability: str
    executive_structure: list[str] = field(default_factory=list)
    supplier_ecosystem: list[str] = field(default_factory=list)
    buying_behaviour: str = "evidence-led, procurement-governed"
    commercial_maturity: str = "unknown"
    digital_maturity: str = "unknown"
    cloud_maturity: str = "unknown"
    ai_maturity: str = "unknown"

@dataclass(frozen=True)
class TransformationTheme:
    name: str
    matched_terms: list[str]
    supporting_signal_ids: list[str]

@dataclass(frozen=True)
class EvidenceTrace:
    commercial_argument: str
    commercial_insight: str
    strategic_signal_id: str
    raw_evidence: str
    source: str

@dataclass(frozen=True)
class OpportunityHypothesis:
    target_executive_role: str
    business_function: str
    transformation_theme: str
    strategic_issue: str
    why_this_role_owns_the_issue: str
    supporting_strategic_signals: list[str]
    supporting_commercial_insights: list[str]
    supporting_commercial_arguments: list[str]
    evidence_strength: str
    commercial_importance: str
    opportunity_description: str
    why_now: str
    discovery_questions: list[str]
    likely_counterarguments: list[str]
    missing_evidence: list[str]
    evidence_required: list[str]
    recommended_conversation: str
    provider_positioning: str
    confidence: int
    issue_qualification_ladder: dict[str, str | list[str]]
    evidence_trace: list[EvidenceTrace]

@dataclass(frozen=True)
class ConversationPlan:
    primary_conversation: str
    secondary_conversation: str
    conversations_to_avoid: list[str]
    executive_escalation_path: list[str]
    board_readiness: str
    conversation_objective: str
    success_criteria: list[str]
    supporting_evidence: list[str]

@dataclass(frozen=True)
class EnterpriseOpportunityReport:
    enterprise_name: str
    enterprise_dna: EnterpriseDNA
    source_profile: list[str]
    themes: list[TransformationTheme]
    hypotheses: list[OpportunityHypothesis]
    conversation_plan: ConversationPlan
    role_issue_opportunity_map: list[dict[str, object]]
    learning_hooks: list[str]


def infer_enterprise_dna(account: TargetAccount, signals: list[Signal]) -> EnterpriseDNA:
    text = " ".join([account.notes, account.sector, *(s.signal_summary + " " + s.evidence_text for s in signals)]).lower()
    sector = account.sector
    is_public = sector in {"Public Sector", "Government"}
    roles = ["Chief Information Officer", "Chief Operating Officer", "Chief Financial Officer", "Chief Procurement Officer", "Transformation Director"]
    if is_public:
        roles += ["Permanent Secretary", "Chief Digital and Information Officer", "Commercial Director"]
    if sector == "Telecommunications":
        roles += ["Chief Technology Officer", "Network Operations Director", "Service Assurance Director"]
    if sector in {"Utilities", "Energy"}:
        roles += ["Asset Operations Director", "Regulatory Director", "Director of Asset Management"]
    return EnterpriseDNA(
        sector=sector,
        business_model="public-service delivery" if is_public else "regulated infrastructure and services" if sector in {"Utilities", "Energy", "Telecommunications"} else "commercial services",
        mission_criticality="high" if any(w in text for w in ["citizen", "grid", "network", "water", "defence", "resilience"]) else "medium",
        technology_intensity="high" if any(w in text for w in ["digital", "network", "cloud", "data", "ai", "platform"]) else "medium",
        operational_complexity="high" if any(w in text for w in ["field", "casework", "asset", "network", "operations", "scale"]) else "medium",
        regulatory_intensity="high" if is_public or sector in {"Utilities", "Energy", "Telecommunications", "Banking", "Healthcare"} else "medium",
        customer_criticality="high" if any(w in text for w in ["customer", "citizen", "service", "trust"]) else "medium",
        security_criticality="high" if any(w in text for w in ["cyber", "defence", "security", "critical"]) else "medium",
        transformation_pressure="high" if signals or any(w in text for w in ["pressure", "legacy", "modernisation", "efficiency", "resilience"]) else "unknown",
        transformation_capability="unproven from public evidence",
        executive_structure=roles,
        supplier_ecosystem=account.known_incumbents + account.known_competitors,
    )


def select_source_profile(dna: EnterpriseDNA) -> list[str]:
    return UNIVERSAL_SOURCES + SECTOR_SOURCES.get(dna.sector, [])


def detect_themes(signals: list[Signal], account: TargetAccount) -> list[TransformationTheme]:
    haystacks = {s.signal_id: " ".join([s.signal_category, s.signal_summary, s.evidence_text, *s.related_capabilities]).lower() for s in signals}
    if not haystacks:
        haystacks = {"account-notes": account.notes.lower()}
    ranked = []
    for name, keywords in THEME_KEYWORDS.items():
        supporting = [sid for sid, text in haystacks.items() if any(k in text for k in keywords)]
        if supporting:
            matched = [k for k in keywords if any(k in t for t in haystacks.values())]
            # Prefer the most specific enterprise theme over broad AI language so
            # outputs diverge by evidence and sector rather than by account name.
            specificity = len(matched) + (0 if name == "AI Transformation" else 2)
            ranked.append((specificity, TransformationTheme(name, matched, supporting)))
    themes = [theme for _, theme in sorted(ranked, key=lambda item: item[0], reverse=True)]
    return themes[:5] or [TransformationTheme("AI Transformation", ["discovery"], ["account-notes"])]


def map_role(theme: str, dna: EnterpriseDNA) -> tuple[str, str, str, str, str]:
    typical = OWNERSHIP.get(theme, DEFAULT_OWNERSHIP)
    def pick(candidates: tuple[str, ...]) -> str:
        for role in dna.executive_structure:
            if any(token in role.lower() for c in candidates for token in c.lower().replace("and", " ").split() if len(token) > 3):
                return role
        return candidates[0]
    primary = pick((typical[0],))
    return primary, typical[1], typical[2], typical[3], typical[4]


def discovery_questions(theme: str, issue: str) -> list[str]:
    return [
        f"Which executive is accountable for resolving the {issue.lower()} now, and who would sponsor a change if the evidence is strong enough?",
        "What budget line, programme or mandatory outcome would this need to attach to before it becomes real?",
        "What timing window matters most: current-year delivery, next budget cycle, regulatory milestone or operational incident risk?",
        "How is success measured today, and which metric would have to move for the board to care?",
        "Which suppliers or internal teams already influence this theme, and where are they not meeting the need?",
        "What evidence would make you stop exploring this opportunity?",
    ]


def build_opportunity_report(account: TargetAccount, signals: list[Signal], provider: ProviderContext | None = None) -> EnterpriseOpportunityReport:
    provider = provider or default_provider_context()
    dna = infer_enterprise_dna(account, signals)
    themes = detect_themes(signals, account)
    evidence = [EvidenceItem(source_name=s.source, source_type=s.source_type, publication_date=s.detected_date, evidence_summary=s.evidence_text, related_signal=s.signal_id, confidence=s.confidence) for s in signals]
    hypotheses = []
    for theme in themes[:5]:
        primary, supporting, budget, technical, business = map_role(theme.name, dna)
        linked = [s for s in signals if s.signal_id in theme.supporting_signal_ids] or signals[:1]
        strength_num = round(mean([s.confidence for s in linked])) if linked else 35
        issue = linked[0].signal_summary if linked else account.notes
        traces = [EvidenceTrace(
            commercial_argument=f"{theme.name} may justify an executive learning conversation because evidence indicates {issue.lower()}.",
            commercial_insight=f"{account.organisation_name} shows a {theme.name.lower()} pressure pattern in {dna.sector}.",
            strategic_signal_id=s.signal_id,
            raw_evidence=s.evidence_text,
            source=s.source,
        ) for s in linked]
        missing = ["named executive sponsor", "budget ownership", "programme maturity", "procurement timing", "incumbent supplier posture"]
        args = [t.commercial_argument for t in traces]
        hypotheses.append(OpportunityHypothesis(
            target_executive_role=primary,
            business_function=business,
            transformation_theme=theme.name,
            strategic_issue=issue,
            why_this_role_owns_the_issue=f"The generic ownership model maps {theme.name} to {primary}, with {supporting} as supporting executive, {budget} as budget owner and {technical} as technical decision maker.",
            supporting_strategic_signals=[s.signal_id for s in linked],
            supporting_commercial_insights=[t.commercial_insight for t in traces],
            supporting_commercial_arguments=args,
            evidence_strength="strong" if strength_num >= 80 else "moderate" if strength_num >= 60 else "weak",
            commercial_importance="high" if dna.mission_criticality == "high" or dna.regulatory_intensity == "high" else "medium",
            opportunity_description=f"A plausible learning opportunity exists to test whether {theme.name.lower()} can improve {issue.lower()} without assuming a sale.",
            why_now=f"Transformation pressure is {dna.transformation_pressure}; current evidence includes {', '.join(s.signal_category for s in linked) or 'account notes'}.",
            discovery_questions=discovery_questions(theme.name, issue),
            likely_counterarguments=["Priority is known but already funded internally.", "Existing suppliers may already cover the issue.", "Evidence may indicate pressure but not willingness to change."],
            missing_evidence=missing,
            evidence_required=["public programme or procurement evidence", "named accountable role", "budget or business case signal", "delivery timetable", "supplier landscape evidence"],
            recommended_conversation=f"Ask {primary} or their office for a learning conversation about whether the evidence-backed {theme.name.lower()} issue is material, funded and time-bound.",
            provider_positioning=f"Position {provider.provider_name} only where configured strengths match: {', '.join(provider.strategic_offerings[:3])}. Keep the conversation diagnostic, not sales-led.",
            confidence=max(20, min(95, strength_num - 5 if missing else strength_num)),
            issue_qualification_ladder={"evidence_backed_issue": issue, "plausible_opportunity": f"{theme.name} learning conversation", "unproven_assumption": missing, "validation_required": ["sponsor", "budget", "timing", "supplier gap"], "disqualifiers": ["no executive owner", "no measurable pain", "no timing", "incumbent fully satisfies need"]},
            evidence_trace=traces,
        ))
    primary = hypotheses[0]
    plan = ConversationPlan(
        primary_conversation=primary.recommended_conversation,
        secondary_conversation=f"Validate technical and delivery feasibility with {map_role(primary.transformation_theme, dna)[3]}.",
        conversations_to_avoid=["generic AI pitch", "provider-first sales presentation", "conversation that bypasses evidence gaps"],
        executive_escalation_path=[primary.target_executive_role, map_role(primary.transformation_theme, dna)[1], map_role(primary.transformation_theme, dna)[2]],
        board_readiness="not board-ready until sponsor, business case, risk and timing evidence are validated",
        conversation_objective="increase commercial intelligence by validating ownership, pain, timing, budget and disqualifiers",
        success_criteria=["confirmed owner", "confirmed issue materiality", "next evidence source identified", "clear disqualifier or next learning step"],
        supporting_evidence=primary.supporting_strategic_signals,
    )
    rows = [{"Executive Role": h.target_executive_role, "Business Function": h.business_function, "Transformation Theme": h.transformation_theme, "Strategic Issue": h.strategic_issue, "Supporting Signals": h.supporting_strategic_signals, "Commercial Importance": h.commercial_importance, "Evidence Strength": h.evidence_strength, "Opportunity Hypothesis": h.opportunity_description, "Discovery Questions": h.discovery_questions, "Confidence": h.confidence, "Recommended Action": h.recommended_conversation} for h in hypotheses]
    return EnterpriseOpportunityReport(account.organisation_name, dna, select_source_profile(dna), themes, hypotheses, plan, rows, ["won pursuit feedback", "lost pursuit feedback", "executive feedback", "proposal outcomes", "commercial results"])
