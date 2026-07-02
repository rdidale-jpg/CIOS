"""Deterministic executive intelligence helpers for Project Newton."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from cios.applications.flora.live.store import DEFAULT_PATH, read_jsonl

READINESS_FACTORS = (
    "Executive sponsor visibility", "Buying signal strength", "Procurement readiness",
    "Budget evidence", "Competitive intelligence", "Incumbent/supplier visibility",
    "AI transformation relevance", "Technology estate clarity", "Cost-of-waiting evidence", "Provider fit",
)
UNKNOWN = ("named sponsor", "budget", "procurement route", "current tooling", "incumbent supplier")

@dataclass(frozen=True)
class MomentumAssessment:
    label: str
    score: int
    explanation: str
    evidence_causing_momentum: tuple[str, ...]
    last_changed_timestamp: str

@dataclass(frozen=True)
class ConversationRecommendation:
    organisation: str
    target_executive_role: str
    business_function: str
    issue_to_discuss: str
    why_now: str
    supporting_thesis: str
    supporting_signals: tuple[str, ...]
    evidence_confidence: int
    commercial_attractiveness: int
    momentum: str
    key_unknown: str
    validation_questions: tuple[str, ...]
    what_not_to_overclaim: str
    recommended_action: str
    estimated_meeting_length: str
    trace: dict[str, tuple[str, ...]]

def _org_evidence(obs: Any, org: Any) -> list[Any]:
    return [e for e in obs.evidence if e.organisation == org.organisation]

def has_live_evidence(obs: Any, org: Any) -> bool:
    return any(e.is_live for e in _org_evidence(obs, org))

def commercial_attractiveness(org: Any) -> int:
    confidence = org.case_for_change.confidence
    thesis_bonus = 10 if org.transformation_theses else 0
    argument_bonus = 8 if org.commercial_arguments else 0
    evidence_penalty = 20 if not any(getattr(s, "supporting_evidence_ids", ()) for s in org.commercial_signals) else 0
    return max(0, min(100, round(confidence * 0.75 + thesis_bonus + argument_bonus - evidence_penalty)))

def temperature(obs: Any, org: Any | None = None) -> str:
    if org is None:
        vals = [temperature(obs, o) for o in obs.organisations]
        if vals.count("Hot") >= 1: return "Hot"
        if vals.count("Warming") >= 2: return "Warming"
        return "Stable" if vals else "Insufficient Evidence"
    if not has_live_evidence(obs, org) and org.case_for_change.confidence < 70:
        return "Insufficient Evidence"
    score = commercial_attractiveness(org)
    if score >= 78 and org.transformation_theses: return "Hot"
    if score >= 62: return "Warming"
    if score >= 45: return "Stable"
    return "Cooling"

def momentum(obs: Any, org: Any) -> MomentumAssessment:
    evs = _org_evidence(obs, org)
    live = [e for e in evs if e.is_live]
    if not live:
        return MomentumAssessment("Unknown", 0, "No live evidence has been collected; seeded fallback cannot create momentum.", (), "No live change recorded")
    diversity = len({e.source_name for e in live})
    quality = round(sum(e.confidence for e in live) / len(live))
    score = min(100, len(live) * 12 + len(org.commercial_signals) * 7 + diversity * 9 + max(0, quality - 55))
    if score >= 75: label = "Rising Fast"
    elif score >= 55: label = "Rising"
    elif score >= 30: label = "Stable"
    else: label = "Cooling"
    latest = max((e.extraction_timestamp for e in live if e.extraction_timestamp), default=datetime.now(UTC).isoformat(timespec="seconds"))
    ids = tuple(e.evidence_id for e in sorted(live, key=lambda e: e.confidence, reverse=True)[:3])
    return MomentumAssessment(label, score, f"{len(live)} live evidence item(s), {len(org.commercial_signals)} signal(s), {diversity} source(s), average confidence {quality}%.", ids, latest)

def readiness_index(obs: Any, org: Any) -> list[dict[str, str]]:
    texts = " ".join((e.summary + " " + e.evidence_class + " " + e.mapped_condition + " " + e.mapped_capability).lower() for e in _org_evidence(obs, org))
    out=[]
    for factor in READINESS_FACTORS:
        f=factor.lower(); level="Unknown"; rationale="No direct evidence yet."; missing="Validate with account discovery."
        if "buying" in f and org.commercial_signals:
            level="Medium"; rationale=f"{len(org.commercial_signals)} accepted signal(s) indicate a discovery-worthy issue."; missing="Confirm active initiative, owner and timing."
        elif "ai transformation" in f and ("ai" in texts or "automation" in texts):
            level="Medium"; rationale="Evidence references AI, automation or data-enabled operations."; missing="Validate data readiness and governed use case."
        elif "cost-of-waiting" in f or "cost" in f:
            if any(w in texts for w in ("cost", "capex", "savings", "risk", "regulatory")):
                level="Medium"; rationale="Public evidence indicates pressure or cost/risk language."; missing="Quantify financial impact and urgency."
        elif "technology" in f and any(w in texts for w in ("network", "legacy", "cloud", "cyber", "system")):
            level="Medium"; rationale="Technology estate signals are visible but incomplete."; missing="Map current tooling, architecture and constraints."
        elif "provider fit" in f and org.transformation_theses:
            level="Medium"; rationale="The thesis maps to evidence-led transformation discovery."; missing="Validate capability fit and buyer appetite."
        elif "sponsor" in f and any("owner" in o.lower() or "cio" in o.lower() or "coo" in o.lower() for t in org.transformation_theses for o in t.likely_executive_owners):
            level="Low"; rationale="Likely role is inferred from signal type, not named sponsorship."; missing="Identify named executive sponsor."
        out.append({"factor":factor,"level":level,"rationale":rationale,"missing_evidence":missing})
    return out

def key_unknown(org: Any) -> str:
    vals = list(dict.fromkeys([u for a in org.commercial_arguments for u in a.unknowns] + [u for t in org.transformation_theses for u in t.validation_required] + list(org.case_for_change.unknowns)))
    return vals[0] if vals else "Named sponsor, budget and procurement route."

def next_action(org: Any) -> str:
    if org.executive_recommendation: return org.executive_recommendation.recommendation
    return org.conviction.recommended_commercial_action

def executive_summary_cards(obs: Any, org: Any | None = None) -> list[tuple[str,str,str]]:
    if org is None:
        recs = recommendation_engine(obs)
        conf = round(sum(o.case_for_change.confidence for o in obs.organisations)/len(obs.organisations)) if obs.organisations else 0
        attr = max((commercial_attractiveness(o) for o in obs.organisations), default=0)
        mom = recs[0].momentum if recs else "Unknown"
        action = recs[0].recommended_action if recs else "Collect evidence before prioritising conversations."
        unknown = recs[0].key_unknown if recs else "No validated live evidence."
        return [("Transformation Temperature", temperature(obs), "What is heating up"),("Momentum", mom, "How fast the portfolio is moving"),("Evidence Confidence", f"{conf}%", "Evidence-backed confidence"),("Commercial Attractiveness", f"{attr}%", "Discovery attractiveness"),("Next Action", action, "Recommended learning conversation"),("Key Unknown", unknown, "Biggest missing proof point")]
    m=momentum(obs, org)
    return [("Transformation Temperature", temperature(obs, org), "Account heat"),("Momentum", m.label, m.explanation),("Evidence Confidence", f"{org.case_for_change.confidence}%", "Confidence in evidence-backed judgement"),("Commercial Attractiveness", f"{commercial_attractiveness(org)}%", "Discovery attractiveness"),("Next Action", next_action(org), "Recommended learning conversation"),("Key Unknown", key_unknown(org), "Biggest missing proof point")]

def recommendation_engine(obs: Any, limit:int=5) -> tuple[ConversationRecommendation,...]:
    recs=[]
    for org in obs.organisations:
        m=momentum(obs, org); thesis = org.transformation_theses[0] if org.transformation_theses else None; arg = org.commercial_arguments[0] if org.commercial_arguments else None
        if not thesis and org.case_for_change.confidence < 65: continue
        owners = thesis.likely_executive_owners if thesis else (org.case_for_change.conversation_level + " sponsor",)
        issue = (arg.claim if arg else org.case_for_change.why_act)[:220]
        signals = tuple(s.title for s in org.commercial_signals[:3])
        recs.append(ConversationRecommendation(org.organisation, owners[0], owners[0].split('/')[0].strip(), issue, org.case_for_change.why_now, thesis.what_appears_to_be_happening if thesis else "No strong thesis yet — evidence collection required.", signals, org.case_for_change.confidence, commercial_attractiveness(org), m.label, key_unknown(org), ("Who owns the issue?", "Is there budget or procurement timing?", "What tooling and incumbent supplier are in place?", "What evidence would disprove this thesis?"), "Do not overclaim enterprise-wide AI transformation, budget, sponsorship or procurement timing.", f"Request a 30-minute evidence-validation discussion with {owners[0]}.", "30 minutes", {"thesis": ((thesis.thesis_id,) if thesis else ()), "argument": ((arg.argument_id,) if arg else ()), "insight": tuple(i.insight_id for i in org.commercial_insights[:3]), "signal": tuple(s.signal_id for s in org.commercial_signals[:3]), "evidence": tuple(org.case_for_change.supporting_evidence_ids[:3])}))
    return tuple(sorted(recs, key=lambda r:(r.commercial_attractiveness, r.evidence_confidence, r.momentum=="Rising Fast"), reverse=True)[:limit])

def evidence_summary(ids: Iterable[str]) -> str:
    n=len(tuple(ids)); return f"{n} evidence item{'s' if n != 1 else ''}"

def strongest_evidence_items(obs: Any, ids: Iterable[str], limit:int=3) -> list[Any]:
    by={e.evidence_id:e for e in obs.evidence}; return sorted([by[i] for i in ids if i in by], key=lambda e:e.confidence, reverse=True)[:limit]
