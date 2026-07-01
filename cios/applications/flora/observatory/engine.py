"""Deterministic Enterprise Transformation Observatory reasoning kernel."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any

from cios.applications.flora.live.aggregation import aggregate_live_evidence, unique_live_evidence
from cios.applications.flora.live.store import DEFAULT_PATH, read_jsonl
from cios.applications.flora.observatory.models import *

CRITIQUE_PATH = "docs/Enterprise_Transformation_Observatory_Architectural_Critique.md"

ORG_SEEDS = {
    "DWP": ("Public Sector", "legacy systems", "citizen service", "operational scale", "casework intelligence", "Board"),
    "National Grid": ("Energy", "grid connections", "energy transition", "asset planning", "grid forecasting", "Executive"),
    "BT": ("Telecommunications", "network estate", "enterprise productivity", "service assurance", "network intelligence", "Board"),
}

CASE_SECTIONS = ("Why Act?", "Why Now?", "Why AI?", "Why Cloud?", "Why Secure by Design?", "Why this Transformation?", "Cost of Waiting", "Commercial Risks", "Contradictory Evidence", "Unknowns")
COST_CATEGORIES = ("Operational cost/risk", "Technology debt", "Security exposure", "Citizen/customer experience", "Regulatory/reputational risk", "Competitive or policy risk", "Delivery complexity")
FACT_PATTERNS = (r"\b\d+(?:\.\d+)?\s*(?:million|billion|bn|m|%)\b", r"£\s*\d+(?:\.\d+)?\s*(?:million|billion|bn|m)?", r"\b20\d{2}\b")


def build_observatory() -> Observatory:
    live = unique_live_evidence(read_jsonl(DEFAULT_PATH))
    evidence = tuple(_live_evidence(live) or _seed_evidence())
    organisations = tuple(_organisation(org, sector, evidence, terms, live) for org, (sector, *terms) in ORG_SEEDS.items())
    return Observatory(CRITIQUE_PATH, evidence, organisations, _weather(evidence, live), _hypotheses(evidence), _graph_edges(evidence))


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


def _seed_evidence() -> list[ObservatoryEvidence]:
    rows: list[ObservatoryEvidence] = []
    for idx, (org, (sector, driver, theme, capability, ai_theme, _level)) in enumerate(ORG_SEEDS.items(), start=1):
        rows.extend([
            ObservatoryEvidence(f"ETO-EV-{idx}A", "SEEDED / SYNTHETIC / FALLBACK — Governed public signal", "Medium", "Current", org, sector, theme.title(), "Transformation Pressure", "Why now?", f"SEEDED / SYNTHETIC / FALLBACK: Public evidence indicates {driver} pressure is material for {org}.", "Seeded governed source register", "", 76, ("Current programme budget", "Named executive sponsor"), ("seed_data", "observatory_v0.1")),
            ObservatoryEvidence(f"ETO-EV-{idx}B", "SEEDED / SYNTHETIC / FALLBACK — Organisation announcement", "Medium", "Recent", org, sector, ai_theme.title(), "AI Readiness", "Why AI?", f"SEEDED / SYNTHETIC / FALLBACK: Observed transformation language suggests {ai_theme} could be plausible.", "Seeded governed source register", "", 72, ("Data quality", "Internal adoption capacity"), ("seed_data", "observatory_v0.1")),
            ObservatoryEvidence(f"ETO-EV-{idx}C", "SEEDED / SYNTHETIC / FALLBACK — Market/regulatory context", "Medium", "Recent", org, sector, capability.title(), "Mission Critical Systems", "What happens if we do nothing?", f"SEEDED / SYNTHETIC / FALLBACK: The operating environment makes {capability} resilience commercially significant for {org}.", "Seeded governed source register", "", 74, ("Supplier estate", "Operational constraints"), ("seed_data", "observatory_v0.1")),
        ])
    return rows


def _organisation(org: str, sector: str, evidence: tuple[ObservatoryEvidence, ...], terms: list[str], live_rows: list[dict[str, Any]]) -> OrganisationObservatory:
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
    case = _case(org, driver, theme, capability, ai_theme, level, org_ev, ev, conf)
    timeline = _timeline(org_ev)
    costs = _costs(org, org_ev, conf)
    counter = ("No contradictory evidence identified in the current evidence set. This does not mean contradiction does not exist.", "Possible counterarguments: existing transformation may already be underway; budget may be insufficient; current architecture may be more modern than public evidence suggests; an incumbent supplier may already be addressing the issue; executive sponsorship may not exist; the AI use case may not be mature enough.")
    return OrganisationObservatory(org, sector, genome, forces, forces[-1], TransformationWindow(org, "Next 6–18 months", "Building", conf, (theme, driver, capability), ("unknown delivery capacity", "unknown budget"), "Timeline evidence supports an engagement hypothesis, not a prediction."), StrategicConviction(tuple(f"{e.evidence_id}: {e.summary}" for e in org_ev), f"The commercial issue is uncertainty reduction around {theme} and {capability}, not technology adoption in isolation.", f"{org} may need a secure, data-enabled transformation conversation focused on {ai_theme}.", conf, ("Internal sponsorship", "Business case economics", "Incumbent supplier posture"), f"Open a {level.lower()}-level case-for-change discussion anchored in evidence, unknowns and cost of waiting.", ev), case, facts, strength, timeline, costs, counter)


def _case(org, driver, theme, capability, ai_theme, level, evs, ev, conf):
    prefix = "" if (evs and conf >= 65) else f"Current evidence is insufficient to support a strong AI transformation claim for {org}. The available snippets may include generic corporate language or single-source signals, but do not yet prove active AI-led network transformation.\n"
    lines = prefix + ("\n".join(f"Observed fact: {e.summary}\nSupporting evidence: {e.source_name} — {e.source_url} — {e.evidence_id} ({e.evidence_class}, confidence {e.confidence}).\nInterpretation: this receipt suggests {org} should test whether {driver}, {theme} or {capability} creates executive-level risk.\nHypothesis: a focused {ai_theme} transformation may be more defensible than generic digital change.\nUnknowns: {', '.join(e.unknowns)}.\nWhat would strengthen/weaken: named sponsor, budget, architecture detail, supplier posture and quantified outcomes." for e in evs[:3]) or "No live evidence available.")
    return CaseForChange(org, *(f"{label}\n{lines}" for label in CASE_SECTIONS[:7]), ("Delayed executive alignment", "Supplier lock-in", "Regulatory/customer trust deterioration"), ev, (), ("Quantified cost of waiting", "Confirmed transformation sponsor", "Current architecture"), conf, level, f"The conversation should move to {level} level because evidence concerns enterprise risk, timing and cross-functional trade-offs.")


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


def _graph_edges(evidence):
    edges = []
    for e in evidence:
        edges += [KnowledgeGraphEdge(e.organisation, "supported_by", e.evidence_id, (e.evidence_id,), False, "Observed evidence lineage.", e.confidence), KnowledgeGraphEdge(e.evidence_id, "supports_question", e.commercial_question_supported, (e.evidence_id,), False, "Evidence explicitly mapped to commercial question.", e.confidence), KnowledgeGraphEdge(e.organisation, "has_theme", e.transformation_theme, (e.evidence_id,), True, e.summary, e.confidence)]
    return tuple(edges)
