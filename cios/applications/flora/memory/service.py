"""Application service that turns accepted Evidence into maintained Enterprise Model memory."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from cios.applications.flora.memory.models import EnterpriseModelAttribute, EnterpriseUnknown, ModelUpdateResult, Observation, now_iso
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository

DOMAIN_MAP = {"AI Modernisation":"technology_events","AI Readiness":"technology_events","Technology Debt":"technology_events","Procurement Readiness":"procurement_events","Cost Pressure":"financial_pressure","Investment Pressure":"financial_pressure","Spending Pressure":"financial_pressure","Operational Resilience":"transformation_programmes","Network Resilience":"transformation_programmes","Digital Leadership":"transformation_programmes"}
CONFLICT_TERMS = ("cancelled", "paused", "delayed", "ended", "withdrawn", "terminated", "no longer")
UNKNOWN_MARKERS = ("unknown", "insufficient", "unclear", "unconfirmed")

FINANCIAL_RE = re.compile(r"(?P<metric>revenue|adjusted EBITDA|normalised free cash flow|free cash flow|EBITDA|net debt|capital expenditure|capex|operating profit)\s*(?:was|of|:)?\s*£(?P<value>[0-9,.]+)\s*(?P<unit>bn|billion|m|million)?", re.I)
UNIT_LIST_RE = re.compile(r"(?P<names>Consumer|Business|International|Openreach)(?:\s*,\s*(?:Consumer|Business|International|Openreach))*?(?:\s+and\s+(?:Consumer|Business|International|Openreach))?\s+as\s+(?P<kind>customer-facing units?|business units?|reporting segments?)", re.I)
CAPABILITY_RE = re.compile(r"(?P<names>Digital|Networks)(?:\s*,\s*(?:Digital|Networks))*?(?:\s+and\s+(?:Digital|Networks))?\s+provide\s+group capabilities", re.I)
STRATEGY_RE = re.compile(r"strategy\s+is\s+(?P<names>[A-Z][A-Za-z]+(?:\s*,\s*[A-Z][A-Za-z]+)*(?:\s+and\s+[A-Z][A-Za-z]+)?)", re.I)
TARGET_RE = re.compile(r"target\s+to\s+(?P<target>.+?)\s+by\s+(?P<date>FY\d{2}|20\d{2})", re.I)
LEADER_RE = re.compile(r"(?P<person>[A-Z][A-Za-z .'-]+)\s+(?:held|holds|is|was|serves as|appointed as)\s+(?:the role of\s+)?(?P<role>Group Chief Executive|Chief Financial Officer|Chair|Chairman|CEO|CFO)", re.I)


def _domain_for(condition: str) -> str:
    return DOMAIN_MAP.get(condition or "", "enterprise_identity")


def _evidence_id(item: dict[str, Any]) -> str:
    return str(item.get("evidence_id") or item.get("id") or item.get("evidence_fingerprint") or hashlib.sha256(str(item).encode()).hexdigest()[:16])


def _names(text: str) -> list[str]:
    return re.findall(r"\b(?:Consumer|Business|International|Openreach|Digital|Networks|Build|Connect|Accelerate)\b", text)


def _metric_key(metric: str) -> str:
    return metric.casefold().replace(" ", "_").replace("ebitda", "ebitda").replace("capex", "capital_expenditure")


@dataclass(frozen=True)
class FactualClaim:
    canonical_enterprise_id: str
    claim_type: str
    atomic_statement: str
    model_domain: str
    affected_attribute: str
    value: float | str | None = None
    unit: str | None = None
    currency: str | None = None
    period: str | None = None
    state: str = "actual"
    evidence_id: str = ""
    page_reference: str | None = None
    confidence: int = 50
    candidate_id: str = ""

    def to_evidence(self, base: dict[str, Any]) -> dict[str, Any]:
        row = dict(base)
        row.update({"enterprise_id": self.canonical_enterprise_id, "canonical_enterprise_id": self.canonical_enterprise_id, "cleaned_observation": self.atomic_statement, "extracted_observation": self.atomic_statement, "commercial_condition": self.claim_type, "affected_attribute": self.affected_attribute, "confidence": self.confidence, "evidence_id": self.evidence_id, "page_range": self.page_reference or base.get("page_range"), "page_number": base.get("page_number")})
        return row


def decompose_factual_claims(item: dict[str, Any]) -> list[FactualClaim]:
    text = str(item.get("cleaned_observation") or item.get("extracted_observation") or item.get("snippet") or "").strip().rstrip(".")
    enterprise = canonical_enterprise_id(str(item.get("enterprise_id") or item.get("canonical_enterprise_id") or item.get("organisation") or "Unknown enterprise")) or "unknown"
    evid = _evidence_id(item); conf = int(item.get("confidence") or item.get("overall_evidence_quality") or 50); page = str(item.get("page_range") or item.get("page_number") or "") or None
    period = str(item.get("period") or ("FY25" if re.search(r"FY25|2025", text) else "FY26" if re.search(r"FY26|2026", text) else "reported period"))
    claims: list[FactualClaim] = []
    financial_matches = list(FINANCIAL_RE.finditer(text))
    for i, m in enumerate(financial_matches, 1):
        metric = _metric_key(m.group("metric")); unit_raw = (m.group("unit") or "").lower(); unit = "billion" if unit_raw in {"bn", "billion"} else "million" if unit_raw in {"m", "million"} else None
        value = float(m.group("value").replace(",", "")); state = "target" if re.search(r"target|guidance|by FY", text, re.I) else "actual"
        stmt = text + "." if len(financial_matches) == 1 and item.get("affected_attribute") else f"{enterprise} reported {period} {metric.replace('_',' ')} of GBP {value:g}{(' '+unit) if unit else ''}."
        attr = str(item.get("affected_attribute")) if len(financial_matches) == 1 and item.get("affected_attribute") else f"financial_performance.metrics.{metric}.{period}.{state}"
        claims.append(FactualClaim(enterprise, "reported_financial_metric", stmt, "financial_performance", attr, value, unit, "GBP", period, state, evid, page, conf, f"{evid}:financial:{i}"))
    if re.search(r"customer-facing units?|business units?|reporting segments?", text, re.I):
        for name in [n for n in ("Consumer", "Business", "International", "Openreach") if re.search(rf"\b{n}\b", text)]:
            stmt = f"{name} is a disclosed BT customer-facing business unit."
            claims.append(FactualClaim(enterprise, "business_unit_disclosed", stmt, "structure", f"structure.units.{name}", name, None, None, None, "actual", evid, page, conf, f"{evid}:unit:{name}"))
    if re.search(r"group capabilities|internal capabilit", text, re.I):
        for name in [n for n in ("Digital", "Networks") if re.search(rf"\b{n}\b", text)]:
            stmt = f"{name} is a disclosed internal BT capability."
            claims.append(FactualClaim(enterprise, "business_unit_disclosed", stmt, "structure", f"structure.capabilities.{name}", name, None, None, None, "actual", evid, page, conf, f"{evid}:capability:{name}"))
    sm = STRATEGY_RE.search(text)
    if sm:
        for name in _names(sm.group("names")):
            claims.append(FactualClaim(enterprise, "strategic_commitment_stated", f"{name} is a stated BT strategic pillar.", "strategy", f"strategy.pillars.{name}", name, None, None, None, "actual", evid, page, conf, f"{evid}:pillar:{name}"))
    tm = TARGET_RE.search(text)
    if tm:
        target = tm.group("target").strip(); date = tm.group("date")
        claims.append(FactualClaim(enterprise, "strategic_target_stated", f"BT stated a strategic target to {target}.", "strategy", "strategy.targets.target", target, None, None, None, "target", evid, page, conf, f"{evid}:target"))
        claims.append(FactualClaim(enterprise, "strategic_target_date_stated", f"BT stated the strategic target date as {date}.", "strategy", "strategy.targets.date", date, None, None, date, "target", evid, page, conf, f"{evid}:target_date"))
    for i, m in enumerate(LEADER_RE.finditer(text), 1):
        role = m.group("role").replace("CEO", "Group Chief Executive").replace("CFO", "Chief Financial Officer").replace("Chairman", "Chair")
        person = m.group("person").strip()
        claims.append(FactualClaim(enterprise, "executive_role_confirmed", f"{person} held the role of {role} at BT.", "leadership", f"leadership.roles.{role}", person, None, None, str(item.get("effective_date") or item.get("publication_date") or "reported date"), "current", evid, page, conf, f"{evid}:leader:{i}"))
    if claims:
        return claims
    return [FactualClaim(enterprise, str(item.get("commercial_condition") or item.get("mapped_condition") or "enterprise identity"), text + ".", _domain_for(str(item.get("commercial_condition") or "")), str(item.get("affected_attribute") or f"{_domain_for(str(item.get('commercial_condition') or ''))}.{str(item.get('commercial_condition') or 'enterprise identity')}"), None, None, None, None, "actual", evid, page, conf, f"{evid}:original")]


@dataclass
class EvidenceProcessingReport:
    results: list[ModelUpdateResult]
    rejected_claims: list[dict[str, Any]]
    factual_claims_extracted: int = 0
    factual_claims_accepted: int = 0
    factual_claims_rejected: int = 0
    factual_claims_duplicate: int = 0
    factual_claims_corroborated: int = 0


class ObservationMemoryService:
    def __init__(self, observations: ObservationRepository | None = None, models: EnterpriseModelRepository | None = None):
        self.observations = observations or ObservationRepository(); self.models = models or EnterpriseModelRepository()

    def observation_from_evidence(self, item: dict[str, Any]) -> Observation:
        statement = str(item.get("cleaned_observation") or item.get("extracted_observation") or item.get("snippet") or "").strip()
        condition = str(item.get("commercial_condition") or item.get("mapped_condition") or "enterprise identity")
        collected = str(item.get("extraction_timestamp") or item.get("collection_date") or now_iso()); observed = str(item.get("observation_date") or collected[:10])
        publication = item.get("publication_date") or item.get("evidence_publication_date")
        enterprise = canonical_enterprise_id(str(item.get("enterprise_id") or item.get("canonical_enterprise_id") or item.get("organisation") or "Unknown enterprise")) or "unknown"
        return Observation(enterprise, condition, statement, observed, collected, str(item.get("affected_attribute") or f"{_domain_for(condition)}.{condition}"), int(item.get("confidence") or item.get("overall_evidence_quality") or 50), (_evidence_id(item),), evidence_publication_date=str(publication) if publication else None, provenance_type="evidence-backed", freshness=str(item.get("evidence_freshness") or "current"), importance=int(item["importance"]) if item.get("importance") is not None else None, commercial_value=int(item["commercial_value"]) if item.get("commercial_value") is not None else None)

    def accept_evidence(self, item: dict[str, Any]) -> ModelUpdateResult:
        report = self.process_evidence(item)
        if report.results:
            return report.results[0]
        reason = report.rejected_claims[0]["rejection_reason"] if report.rejected_claims else "No factual claims extracted"
        raise ValueError(reason)

    def process_evidence(self, item: dict[str, Any]) -> EvidenceProcessingReport:
        report = EvidenceProcessingReport([], [])
        claims = decompose_factual_claims(item); report.factual_claims_extracted = len(claims)
        for claim in claims:
            try:
                before = self.observations.get_by_fingerprint(Observation(**self.observation_from_evidence(claim.to_evidence(item)).to_dict()).observation_fingerprint or "")
                observation = self.observations.save(self.observation_from_evidence(claim.to_evidence(item)))
                result = self.apply_observation(observation); report.results.append(result)
                report.factual_claims_accepted += 1
                if before: report.factual_claims_corroborated += 1
            except ValueError as exc:
                report.factual_claims_rejected += 1
                report.rejected_claims.append({"claim_text": claim.atomic_statement, "source_evidence_id": claim.evidence_id, "page": claim.page_reference, "rejection_reason": str(exc), "model_domain": claim.model_domain, "candidate_id": claim.candidate_id})
        return report

    def apply_observation(self, observation: Observation) -> ModelUpdateResult:
        if observation.lifecycle_state != "accepted": return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", observation.affected_attribute, "ignored")
        model = self.models.get(observation.enterprise_id); key = observation.affected_attribute; domain = key.split(".", 1)[0]; lower = observation.atomic_statement.casefold()
        if any(marker in lower for marker in UNKNOWN_MARKERS):
            unknown_id = f"UNK-{hashlib.sha256((observation.enterprise_id + key).encode()).hexdigest()[:12].upper()}"; existing = model.unknowns.get(unknown_id); related = tuple(dict.fromkeys([*(existing.related_observation_ids if existing else ()), observation.observation_id or ""]))
            model.unknowns[unknown_id] = EnterpriseUnknown(unknown_id, observation.enterprise_id, f"Unknown model state for {key}", domain, "medium", ("accepted corroborating evidence",), "open", related, review_at=observation.last_confirmed_date); model.updated_at = now_iso(); self.models.save(model)
            return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", key, "unknown_created", unknown_created=True)
        existing = model.attributes.get(key); contradiction = bool(existing and existing.current_value and existing.current_value != observation.atomic_statement and any(t in lower or t in existing.current_value.casefold() for t in CONFLICT_TERMS))
        if existing:
            prior = tuple(existing.prior_values)
            if existing.current_value != observation.atomic_statement and not contradiction: prior = (*prior, {"value": existing.current_value, "confidence": existing.confidence, "superseded_at": now_iso(), "observation_ids": existing.observation_ids})
            observation_ids = tuple(dict.fromkeys([*existing.observation_ids, observation.observation_id or ""])); evidence_ids = tuple(dict.fromkeys([*existing.evidence_ids, *observation.supporting_evidence_ids])); value = existing.current_value if contradiction else observation.atomic_statement; conflicts = tuple(dict.fromkeys([*existing.conflicting_observation_ids, observation.observation_id or ""])) if contradiction else existing.conflicting_observation_ids; state = "contradicted" if contradiction else observation.contradiction_state
        else:
            prior = (); observation_ids = (observation.observation_id or "",); evidence_ids = observation.supporting_evidence_ids; value = observation.atomic_statement; conflicts = (); state = observation.contradiction_state
        confidence = max(observation.confidence, existing.confidence if existing else 0); confidence_history = (*(existing.confidence_history if existing else ()), {"observation_id": observation.observation_id or "", "confidence": observation.confidence, "recorded_at": now_iso()})
        model.attributes[key] = EnterpriseModelAttribute(domain, key, value, confidence, observation.last_confirmed_date or observation.observation_date, observation.freshness, observation_ids, evidence_ids, observation.provenance_type, state, conflicts, prior, confidence_history); model.updated_at = now_iso(); self.models.save(model)
        return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", key, "contradiction_recorded" if contradiction else ("updated" if existing else "created"), contradiction=contradiction)

    def rebuild_from_ledger(self) -> list[ModelUpdateResult]:
        return [self.apply_observation(obs) for obs in self.observations.list()]
