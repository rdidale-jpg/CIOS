"""Deterministic Enterprise Transformation Observatory reasoning kernel."""
from __future__ import annotations

from cios.applications.flora.observatory.models import *

CRITIQUE_PATH = "docs/Enterprise_Transformation_Observatory_Architectural_Critique.md"

ORG_SEEDS = {
    "DWP": ("Public Sector", "legacy systems", "citizen service", "operational scale", "casework intelligence", "Board"),
    "National Grid": ("Energy", "grid connections", "energy transition", "asset planning", "grid forecasting", "Executive"),
    "BT": ("Telecommunications", "network estate", "enterprise productivity", "service assurance", "network intelligence", "Board"),
}


def build_observatory() -> Observatory:
    evidence = tuple(_evidence())
    organisations = tuple(_organisation(org, sector, evidence, terms) for org, (sector, *terms) in ORG_SEEDS.items())
    return Observatory(
        critique_path=CRITIQUE_PATH,
        evidence=evidence,
        organisations=organisations,
        weather=_weather(evidence),
        hypotheses=_hypotheses(),
        graph_edges=_graph_edges(evidence),
    )


def _evidence() -> list[ObservatoryEvidence]:
    rows: list[ObservatoryEvidence] = []
    for idx, (org, (sector, driver, theme, capability, ai_theme, _level)) in enumerate(ORG_SEEDS.items(), start=1):
        rows.extend([
            ObservatoryEvidence(f"ETO-EV-{idx}A", "Governed public signal", "Medium", "Current", org, sector, theme.title(), "Transformation Pressure", "Why now?", f"Public evidence indicates {driver} pressure is material for {org}.", "Seeded governed source register", "", 76, ("Current programme budget", "Named executive sponsor"), ("seed_data", "observatory_v0.1")),
            ObservatoryEvidence(f"ETO-EV-{idx}B", "Organisation announcement", "Medium", "Recent", org, sector, ai_theme.title(), "AI Readiness", "Why AI?", f"Observed transformation language suggests {ai_theme} could be a plausible AI-enabled intervention.", "Seeded governed source register", "", 72, ("Data quality", "Internal adoption capacity"), ("seed_data", "observatory_v0.1")),
            ObservatoryEvidence(f"ETO-EV-{idx}C", "Market/regulatory context", "Medium", "Recent", org, sector, capability.title(), "Mission Critical Systems", "What happens if we do nothing?", f"The operating environment makes {capability} resilience commercially significant for {org}.", "Seeded governed source register", "", 74, ("Supplier estate", "Operational constraints"), ("seed_data", "observatory_v0.1")),
        ])
    return rows


def _organisation(org: str, sector: str, evidence: tuple[ObservatoryEvidence, ...], terms: list[str]) -> OrganisationObservatory:
    driver, theme, capability, ai_theme, level = terms
    ev = tuple(e.evidence_id for e in evidence if e.organisation == org)
    genome = (
        GenomeDimension("Technology", "Mission Critical Systems", f"{org} appears exposed to {capability} constraints.", 74, "Multiple evidence objects point to operationally important systems rather than optional innovation.", ev, ("Architecture inventory",), "Medium"),
        GenomeDimension("Technology", "AI Readiness", f"AI is plausible where {ai_theme} is tied to an operational problem.", 70, "The hypothesis is constrained by unknown data readiness and workforce adoption evidence.", ev[1:2], ("Data quality", "AI governance maturity"), "Medium"),
        GenomeDimension("Business", "Commercial Pressure", f"{theme.title()} pressure is commercially material.", 76, "Evidence links external pressure to executive questions about action and timing.", ev, ("Quantified value at stake",), "Medium"),
        GenomeDimension("Organisation", "Executive Resolve", "Resolve is plausible but not proven.", 58, "Public signals imply priority; they do not prove internal sponsorship.", ev[:1], ("Named sponsor", "Board minutes"), "Medium"),
        GenomeDimension("Transformation", "Transformation Inevitability Index (TII)", "Transformation looks increasingly difficult to defer, but this is a hypothesis not a prediction.", 73, "Pressure, mission-critical exposure and plausible AI/cloud levers align; inertia remains unknown.", ev, ("Funding capacity", "Delivery track record"), "Medium"),
    )
    forces = (
        ForceAssessment("Transformation Pressure", "Elevated", f"{driver.title()} pressure is visible in the evidence base.", ev[:1], 76),
        ForceAssessment("Organisational Inertia", "Unknown", "The Observatory has insufficient evidence on internal resistance or delivery constraints.", (), 35, ("Operating model evidence",)),
        ForceAssessment("Executive Resolve", "Plausible", "Public priority signals suggest attention but not commitment.", ev[:1], 58, ("Sponsor confirmation",)),
        ForceAssessment("Transformation Capability", "Unproven", "Capability cannot be inferred from external pressure alone.", ev[1:], 52, ("Delivery capacity", "Partner ecosystem")),
        ForceAssessment("Transformation Momentum", "Building", "Recent evidence clusters around a coherent transformation theme.", ev, 72),
        ForceAssessment("Transformation Window", "Open but time-bound", "Commercial pressure and technology constraints appear simultaneous.", ev, 70),
    )
    urgency = ForceAssessment("Strategic Urgency", "Increasing", f"Why now: {theme} pressure, {driver} constraints and {capability} exposure are converging.", ev, 74, ("Budget cycle", "Competing executive priorities"))
    window = TransformationWindow(org, "Next 6–18 months", "Building", 72, (theme, driver, capability), ("unknown delivery capacity", "unknown budget"), "This is an evidence-backed engagement hypothesis, not a prediction.")
    conviction = StrategicConviction(
        tuple(f"{e.evidence_id}: {e.summary}" for e in evidence if e.organisation == org),
        f"The commercial issue is not technology adoption in isolation; it is reducing uncertainty around {theme} and {capability}.",
        f"{org} may need a secure, data-enabled transformation conversation focused on {ai_theme}.",
        73,
        ("Internal sponsorship", "Business case economics", "Incumbent supplier posture"),
        f"Open a {level.lower()}-level case-for-change discussion anchored in evidence, unknowns and cost of waiting.",
        ev,
    )
    case = CaseForChange(org, f"Because {driver} pressure is material and current operating constraints appear commercially consequential.", f"Because evidence suggests pressure and transformation themes are converging now rather than remaining isolated signals.", f"Because AI may help only where tied to {ai_theme}; Flora does not infer AI readiness as fact.", "Because cloud modernisation may improve resilience and data access where legacy constraints are confirmed.", "Because transformation that increases dependency on data and platforms should reduce security risk by design, not after deployment.", f"A focused {ai_theme} transformation is more defensible than generic digital change.", "Waiting may increase remediation cost, stakeholder scrutiny and opportunity loss while evidence gaps remain unresolved.", ("Delayed executive alignment", "Supplier lock-in", "Regulatory or customer trust deterioration"), ev, (), ("Quantified cost of waiting", "Confirmed transformation sponsor", "Current architecture"), 73, level, f"The conversation should move to {level} level because the evidence concerns enterprise risk, timing and cross-functional trade-offs.")
    return OrganisationObservatory(org, sector, genome, forces, urgency, window, conviction, case)


def _weather(evidence: tuple[ObservatoryEvidence, ...]) -> EnterpriseWeather:
    return EnterpriseWeather("Elevated across monitored public sector, energy and telecoms organisations", "Building where pressure, legacy and AI themes cluster", ("Public Sector", "Energy", "Telecommunications"), ("secure AI-enabled operations", "legacy modernisation", "mission-critical resilience"), ("pressure plus unresolved data readiness", "security posture becoming a board constraint"), ("Transformation is most commercially useful when framed as uncertainty reduction, not technology substitution."), tuple(e.evidence_id for e in evidence[:5]))


def _hypotheses() -> tuple[ResearchHypothesis, ...]:
    return (ResearchHypothesis("ETO-HYP-001", "Legacy pressure plus public scrutiny elevates board-level transformation need", HypothesisStatus.STRENGTHENING, ("ETO-EV-1A", "ETO-EV-1C"), (), 74, "2026-07-01", "Lead with risk, resilience and cost-of-waiting rather than product capability."), ResearchHypothesis("ETO-HYP-002", "AI readiness is constrained more by data and operating model evidence than appetite", HypothesisStatus.NEEDS_MORE_EVIDENCE, ("ETO-EV-2B", "ETO-EV-3B"), (), 61, "2026-07-01", "Discovery should test data readiness before proposing AI scale-up."))


def _graph_edges(evidence: tuple[ObservatoryEvidence, ...]) -> tuple[KnowledgeGraphEdge, ...]:
    edges = []
    for e in evidence:
        edges.append(KnowledgeGraphEdge(e.organisation, "supported_by", e.evidence_id, (e.evidence_id,), False, "Observed evidence lineage." , e.confidence))
        edges.append(KnowledgeGraphEdge(e.evidence_id, "supports_question", e.commercial_question_supported, (e.evidence_id,), False, "Evidence explicitly mapped to commercial question.", e.confidence))
        edges.append(KnowledgeGraphEdge(e.organisation, "has_theme", e.transformation_theme, (e.evidence_id,), True, e.summary, e.confidence))
    return tuple(edges)
