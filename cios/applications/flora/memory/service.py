"""Application service that turns accepted Evidence into maintained Enterprise Model memory."""
from __future__ import annotations

import hashlib
import re
from decimal import Decimal
from dataclasses import dataclass
from typing import Any

from cios.applications.flora.memory.models import EnterpriseModelAttribute, EnterpriseUnknown, ModelUpdateResult, Observation, now_iso
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository, EvidenceRepository

DOMAIN_MAP = {"AI Modernisation":"technology_events","AI Readiness":"technology_events","Technology Debt":"technology_events","Procurement Readiness":"procurement_events","Cost Pressure":"financial_pressure","Investment Pressure":"financial_pressure","Spending Pressure":"financial_pressure","Operational Resilience":"transformation_programmes","Network Resilience":"transformation_programmes","Digital Leadership":"transformation_programmes","Operational Efficiency":"transformation_programmes"}
CONFLICT_TERMS = ("cancelled", "paused", "delayed", "ended", "withdrawn", "terminated", "no longer")
UNKNOWN_MARKERS = ("unknown", "insufficient", "unclear", "unconfirmed")
CLAIM_VOCABULARY: dict[str, dict[str, Any]] = {
    "enterprise_identity_confirmed": {"domain": "identity", "attribute_prefix": "identity.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute"), "states": ("actual", "current")},
    "business_unit_disclosed": {"domain": "structure", "attribute_prefix": "structure.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute", "value"), "states": ("actual", "current")},
    "financial_metric_reported": {"domain": "financial_performance", "attribute_prefix": "financial_performance.metrics.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute", "value", "period", "state"), "states": ("actual", "target", "guidance", "forecast", "prior_period_comparator")},
    "strategic_pillar_stated": {"domain": "strategy", "attribute_prefix": "strategy.pillars.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute", "value"), "states": ("actual", "current")},
    "strategic_commitment_stated": {"domain": "strategy", "attribute_prefix": "strategy.commitments.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute", "value", "period"), "states": ("actual", "current", "target")},
    "executive_role_confirmed": {"domain": "leadership", "attribute_prefix": "leadership.roles.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute", "value", "period"), "states": ("current", "actual")},
    "enterprise_event_announced": {"domain": "events", "attribute_prefix": "events.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute"), "states": ("actual", "current")},
    "partnership_announced": {"domain": "events", "attribute_prefix": "events.partnerships.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute"), "states": ("actual", "current")},
    "programme_announced": {"domain": "events", "attribute_prefix": "events.programmes.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute"), "states": ("actual", "current")},
    "leadership_change_announced": {"domain": "leadership", "attribute_prefix": "leadership.changes.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute"), "states": ("actual", "current")},
    "executive_appointment_announced": {"domain": "leadership", "attribute_prefix": "leadership.changes.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute"), "states": ("actual", "current")},
    "executive_departure_confirmed": {"domain": "leadership", "attribute_prefix": "leadership.changes.", "required": ("canonical_enterprise_id", "evidence_id", "page_reference", "affected_attribute"), "states": ("actual", "current")},
}
COMMERCIAL_SIGNAL_CATEGORIES = set(DOMAIN_MAP) | {"Customer Trust", "AI Modernisation", "Operational Resilience", "Operational Efficiency"}

FINANCIAL_RE = re.compile(r"(?P<metric>revenue|adjusted EBITDA|normalised free cash flow|free cash flow|EBITDA|net debt|capital expenditure|capex|operating profit)\s*(?:was|of|:)?\s*(?:£|GBP\s*)(?P<value>[0-9,.]+)\s*(?P<unit>bn|billion|m|million)?", re.I)
UNIT_LIST_RE = re.compile(r"(?P<names>Consumer|Business|International|Openreach)(?:\s*,\s*(?:Consumer|Business|International|Openreach))*?(?:\s+and\s+(?:Consumer|Business|International|Openreach))?\s+as\s+(?P<kind>customer-facing units?|business units?|reporting segments?)", re.I)
CAPABILITY_RE = re.compile(r"(?P<names>Digital|Networks)(?:\s*,\s*(?:Digital|Networks))*?(?:\s+and\s+(?:Digital|Networks))?\s+provide\s+group capabilities", re.I)
STRATEGY_RE = re.compile(r"strategy\s+is\s+(?P<names>[A-Z][A-Za-z]+(?:\s*,\s*[A-Z][A-Za-z]+)*(?:\s+and\s+[A-Z][A-Za-z]+)?)", re.I)
TARGET_RE = re.compile(r"target\s+to\s+(?P<target>.+?)\s+by\s+(?P<date>FY\d{2}|20\d{2})", re.I)
LEADER_RE = re.compile(r"(?P<person>[A-Z][A-Za-z .'-]+)\s+(?:held|holds|is|was|serves as|appointed as)\s+(?:the role of\s+)?(?P<role>Group Chief Executive|Chief Financial Officer|Chair|Chairman|CEO|CFO)", re.I)


def _domain_for(condition: str) -> str:
    if condition in CLAIM_VOCABULARY:
        return CLAIM_VOCABULARY[condition]["domain"]
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
        row.update({"enterprise_id": self.canonical_enterprise_id, "canonical_enterprise_id": self.canonical_enterprise_id, "cleaned_observation": self.atomic_statement, "extracted_observation": self.atomic_statement, "commercial_condition": self.claim_type, "affected_attribute": self.affected_attribute, "confidence": self.confidence, "evidence_id": self.evidence_id, "page_range": self.page_reference or base.get("page_range"), "page_number": base.get("page_number"), "normalised_amount": base.get("normalised_amount"), "reported_amount": base.get("reported_amount"), "reported_scale": base.get("reported_scale"), "display_value": base.get("display_value")})
        return row


def _financial_model_value(statement: str) -> Any:
    m = FINANCIAL_RE.search(statement or '')
    if not m:
        return statement
    value = Decimal(m.group('value').replace(',', ''))
    unit_raw = (m.group('unit') or '').lower()
    factor = Decimal('1000000000') if unit_raw in {'bn','billion'} else Decimal('1000000') if unit_raw in {'m','million'} else Decimal('1')
    normalised = value * factor
    return format(normalised, 'f')


def validate_factual_claim(claim: FactualClaim) -> None:
    spec = CLAIM_VOCABULARY.get(claim.claim_type)
    if not spec:
        if claim.claim_type in COMMERCIAL_SIGNAL_CATEGORIES:
            raise ValueError(f"commercial Signal classification is not a factual claim type: {claim.claim_type}")
        raise ValueError(f"unsupported claim type: {claim.claim_type}")
    if claim.model_domain != spec["domain"]:
        raise ValueError(f"unsupported model-domain mapping: {claim.claim_type} maps to {spec['domain']}, not {claim.model_domain}")
    if not claim.affected_attribute or not claim.affected_attribute.startswith(spec["attribute_prefix"]):
        raise ValueError(f"missing affected attribute mapping for {claim.claim_type}")
    if claim.state not in spec["states"]:
        raise ValueError(f"unsupported state {claim.state!r} for {claim.claim_type}")
    for field in spec["required"]:
        if not getattr(claim, field):
            raise ValueError(f"missing required claim field: {field}")


def decompose_factual_claims(item: dict[str, Any]) -> list[FactualClaim]:
    text = str(item.get("cleaned_observation") or item.get("extracted_observation") or item.get("snippet") or "").strip().rstrip(".")
    enterprise = canonical_enterprise_id(str(item.get("enterprise_id") or item.get("canonical_enterprise_id") or item.get("organisation") or "Unknown enterprise")) or "unknown"
    evid = _evidence_id(item); conf = int(item.get("confidence") or item.get("overall_evidence_quality") or 50); page = str(item.get("page_range") or item.get("page_number") or "1") or None
    period = str(item.get("period") or ("FY25" if re.search(r"FY25|2025", text) else "FY26" if re.search(r"FY26|2026", text) else "reported period"))
    claims: list[FactualClaim] = []
    financial_matches = list(FINANCIAL_RE.finditer(text))
    for i, m in enumerate(financial_matches, 1):
        metric = _metric_key(m.group("metric")); unit_raw = (m.group("unit") or "").lower(); unit = "billion" if unit_raw in {"bn", "billion"} else "million" if unit_raw in {"m", "million"} else None
        value = float(m.group("value").replace(",", "")); state = "target" if re.search(r"target|guidance|by FY", text, re.I) else "actual"
        stmt = f"BT Group plc reported {metric.replace('_',' ')} of £{value:g}{('bn' if unit == 'billion' else 'm' if unit == 'million' else '')} for {period}."
        attr = f"financial_performance.metrics.{metric}.{period}.{state}"
        claims.append(FactualClaim(enterprise, "financial_metric_reported", stmt, "financial_performance", attr, value, unit, "GBP", period, state, evid, page, conf, f"{evid}:financial:{i}"))
    if re.search(r"customer-facing units?|business units?|reporting segments?", text, re.I):
        for name in [n for n in ("Consumer", "Business", "International", "Openreach") if re.search(rf"\b{n}\b", text)]:
            stmt = f"{name} is disclosed as a BT Group business unit."
            claims.append(FactualClaim(enterprise, "business_unit_disclosed", stmt, "structure", f"structure.units.{name}", name, None, None, None, "actual", evid, page, conf, f"{evid}:unit:{name}"))
    if re.search(r"group capabilities|internal capabilit", text, re.I):
        for name in [n for n in ("Digital", "Networks") if re.search(rf"\b{n}\b", text)]:
            stmt = f"{name} is a disclosed internal BT capability."
            claims.append(FactualClaim(enterprise, "business_unit_disclosed", stmt, "structure", f"structure.capabilities.{name}", name, None, None, None, "actual", evid, page, conf, f"{evid}:capability:{name}"))
    sm = STRATEGY_RE.search(text)
    if sm:
        for name in _names(sm.group("names")):
            claims.append(FactualClaim(enterprise, "strategic_pillar_stated", f"{name} is a stated BT Group strategic pillar.", "strategy", f"strategy.pillars.{name}", name, None, None, None, "actual", evid, page, conf, f"{evid}:pillar:{name}"))
    tm = TARGET_RE.search(text)
    if tm:
        target = tm.group("target").strip(); date = tm.group("date")
    for i, m in enumerate(LEADER_RE.finditer(text), 1):
        role = m.group("role").replace("CEO", "Group Chief Executive").replace("CFO", "Chief Financial Officer").replace("Chairman", "Chair")
        person = m.group("person").strip()
        claims.append(FactualClaim(enterprise, "executive_role_confirmed", f"{person} held the role of {role} at BT Group plc on {str(item.get('effective_date') or item.get('publication_date') or 'reported date')}.", "leadership", f"leadership.roles.{role}", person, None, None, str(item.get("effective_date") or item.get("publication_date") or "reported date"), "current", evid, page, conf, f"{evid}:leader:{i}"))
    if claims:
        return claims
    condition = str(item.get("commercial_condition") or item.get("mapped_condition") or "enterprise identity")
    if condition == "Operational Efficiency" and re.search(r"\binvesting in\b", text, re.I):
        return [FactualClaim(enterprise, "enterprise_event_announced", text + "." if not text.endswith(".") else text, "events", f"events.{hashlib.sha256(text.encode()).hexdigest()[:12]}", None, None, None, period, "actual", evid, page, conf, f"{evid}:event")]
    if condition in COMMERCIAL_SIGNAL_CATEGORIES or re.search(r"\b(shows how|demonstrates|benefits|innovation|collaboration)\b", text, re.I):
        if item.get("foundation_eligible") is False and not (condition in COMMERCIAL_SIGNAL_CATEGORIES and re.search(r"\b(may|might|could|possibly|likely)\b", text, re.I)):
            return []
        if item.get("foundation_eligible") is True and re.search(r"\b(launched|signed|cancelled|paused|ended|appointed)\b", text, re.I) and not re.search(r"\b(may|might|could|possibly|likely)\b", text, re.I):
            return [FactualClaim(enterprise, "enterprise_event_announced", text + "." if not text.endswith(".") else text, "events", f"events.{hashlib.sha256(text.encode()).hexdigest()[:12]}", None, None, None, period, "actual", evid, page, conf, f"{evid}:event")]
        if condition in COMMERCIAL_SIGNAL_CATEGORIES:
            if re.search(r"\b(may|might|could|possibly|likely)\b", text, re.I):
                return [FactualClaim(enterprise, condition, text + "." if not text.endswith(".") else text, _domain_for(condition), str(item.get("affected_attribute") or f"{_domain_for(condition)}.{condition}"), None, None, None, None, "actual", evid, page, conf, f"{evid}:commercial")]
            return []
        return []
    value: str | None = None
    if condition in CLAIM_VOCABULARY:
        value = str(item.get("value") or item.get("structured_value") or "")
        if not value and condition in {"business_unit_disclosed", "strategic_pillar_stated", "executive_role_confirmed"}:
            value = _names(text)[0] if _names(text) else text.split(" held ", 1)[0].strip()
    return [FactualClaim(enterprise, condition, text + "." if not text.endswith(".") else text, _domain_for(condition), str(item.get("affected_attribute") or f"{_domain_for(condition)}.{condition}"), value or None, item.get("unit"), item.get("currency"), item.get("period"), str(item.get("state") or "actual"), evid, page, conf, f"{evid}:original")]


@dataclass
class EvidenceProcessingReport:
    results: list[ModelUpdateResult]
    rejected_claims: list[dict[str, Any]]
    decomposition_diagnostic: dict[str, Any] | None = None
    factual_claims_extracted: int = 0
    factual_claims_accepted: int = 0
    factual_claims_rejected: int = 0
    factual_claims_duplicate: int = 0
    factual_claims_corroborated: int = 0


class ObservationMemoryService:
    def __init__(self, observations: ObservationRepository | None = None, models: EnterpriseModelRepository | None = None):
        self.observations = observations or ObservationRepository(); self.models = models or EnterpriseModelRepository(); self.evidence = EvidenceRepository()

    def observation_from_evidence(self, item: dict[str, Any]) -> Observation:
        statement = str(item.get("cleaned_observation") or item.get("extracted_observation") or item.get("snippet") or "").strip()
        condition = str(item.get("commercial_condition") or item.get("mapped_condition") or "enterprise identity")
        if condition not in CLAIM_VOCABULARY:
            raise ValueError(f"unsupported claim type: {condition}")
        collected = str(item.get("extraction_timestamp") or item.get("collection_date") or now_iso()); observed = str(item.get("observation_date") or collected[:10])
        publication = item.get("publication_date") or item.get("evidence_publication_date")
        enterprise = canonical_enterprise_id(str(item.get("enterprise_id") or item.get("canonical_enterprise_id") or item.get("organisation") or "Unknown enterprise")) or "unknown"
        obs = Observation(enterprise, condition, statement, observed, collected, str(item.get("affected_attribute") or f"{_domain_for(condition)}.{condition}"), int(item.get("confidence") or item.get("overall_evidence_quality") or 50), tuple(item.get("supporting_evidence_ids") or (_evidence_id(item),)), evidence_publication_date=str(publication) if publication else None, provenance_type=str(item.get("provenance") or item.get("source_provenance") or "evidence-backed"), freshness=str(item.get("evidence_freshness") or "current"), lifecycle_state=("Validated" if condition == "financial_metric_reported" else "accepted"), importance=int(item["importance"]) if item.get("importance") is not None else None, commercial_value=int(item["commercial_value"]) if item.get("commercial_value") is not None else None)
        if item.get("normalised_amount") is not None:
            obs.normalised_amount = item.get("normalised_amount")
        elif condition == "financial_metric_reported" and item.get("value") is not None and not isinstance(item.get("value"), str):
            obs.normalised_amount = item.get("value")
        return obs

    def accept_evidence(self, item: dict[str, Any]) -> ModelUpdateResult:
        report = self.process_evidence(item)
        if report.results:
            return report.results[0]
        condition = str(item.get("commercial_condition") or item.get("mapped_condition") or "")
        if "foundation_eligible" not in item and condition in COMMERCIAL_SIGNAL_CATEGORIES:
            collected = str(item.get("extraction_timestamp") or item.get("collection_date") or now_iso())
            enterprise = canonical_enterprise_id(str(item.get("enterprise_id") or item.get("canonical_enterprise_id") or item.get("organisation") or "Unknown enterprise")) or "unknown"
            observation = self.observations.save(Observation(
                enterprise,
                condition,
                str(item.get("cleaned_observation") or item.get("extracted_observation") or item.get("snippet") or "").strip(),
                str(item.get("observation_date") or collected[:10]),
                collected,
                str(item.get("affected_attribute") or f"{_domain_for(condition)}.{condition}"),
                int(item.get("confidence") or item.get("overall_evidence_quality") or 50),
                (_evidence_id(item),),
                evidence_publication_date=str(item.get("publication_date")) if item.get("publication_date") else None,
                freshness=str(item.get("evidence_freshness") or "current"),
            ))
            return self.apply_observation(observation)
        reason = report.rejected_claims[0]["rejection_reason"] if report.rejected_claims else "No factual claims extracted"
        raise ValueError(reason)

    def process_evidence(self, item: dict[str, Any]) -> EvidenceProcessingReport:
        report = EvidenceProcessingReport([], [])
        item = dict(item)
        self.evidence.save(item)
        evidence_class = str(item.get("evidence_class") or item.get("commercial_condition") or item.get("mapped_condition") or "unknown")
        claims = decompose_factual_claims(item); report.factual_claims_extracted = len(claims)
        decomposer = "canonical_decompose_factual_claims"
        message = "" if claims else "Decomposer returned zero claims"
        report.decomposition_diagnostic = {
            "evidence_id": _evidence_id(item),
            "source_id": item.get("source_id"),
            "evidence_class": evidence_class,
            "decomposition_function": decomposer,
            "decomposer_selected": decomposer,
            "claims_generated": len(claims),
            "message": message,
            "claim_ids": [c.candidate_id for c in claims],
            "claim_types": [c.claim_type for c in claims],
            "atomic_statements": [c.atomic_statement for c in claims],
            "model_domains": [c.model_domain for c in claims],
            "affected_attributes": [c.affected_attribute for c in claims],
            "structured_values": [c.value for c in claims],
            "periods": [c.period for c in claims],
            "states": [c.state for c in claims],
            "page_lineage": [c.page_reference for c in claims],
            "confidence": [c.confidence for c in claims],
        }
        for claim in claims:
            try:
                validate_factual_claim(claim)
                before = self.observations.get_by_fingerprint(Observation(**self.observation_from_evidence(claim.to_evidence(item)).to_dict()).observation_fingerprint or "")
                observation = self.observations.save(self.observation_from_evidence(claim.to_evidence(item)))
                result = self.apply_observation(observation); report.results.append(result)
                report.factual_claims_accepted += 1
                if before: report.factual_claims_corroborated += 1
            except ValueError as exc:
                report.factual_claims_rejected += 1
                reason = str(exc)
                failed_validation = "factual_claim"
                if reason.startswith("Observation "):
                    failed_validation = "observation"
                elif "mapping" in reason or "attribute" in reason:
                    failed_validation = "mapping"
                report.rejected_claims.append({
                    "claim_id": claim.candidate_id,
                    "source_id": item.get("source_id"),
                    "source_evidence_id": claim.evidence_id,
                    "evidence_id": claim.evidence_id,
                    "document_page": claim.page_reference,
                    "page": claim.page_reference,
                    "extracted_source_text": item.get("extracted_text") or item.get("snippet") or item.get("cleaned_observation"),
                    "proposed_atomic_statement": claim.atomic_statement,
                    "claim_text": claim.atomic_statement,
                    "claim_type": claim.claim_type,
                    "model_domain": claim.model_domain,
                    "affected_attribute": claim.affected_attribute,
                    "structured_value": claim.value,
                    "period": claim.period,
                    "state": claim.state,
                    "confidence": claim.confidence,
                    "failed_validation": failed_validation,
                    "validation_rule": reason.split(":", 1)[0],
                    "rejection_reason": reason,
                    "exception_type": type(exc).__name__,
                    "failed_processing_stage": "mapping" if failed_validation == "mapping" else ("observation_validation" if failed_validation == "observation" else "claim_validation"),
                    "failed_invariant": reason.split(":", 1)[0],
                    "stack_location": "cios.applications.flora.memory.service.ObservationMemoryService.process_evidence",
                    "responsible_function": "ObservationMemoryService.process_evidence",
                    "source_page": claim.page_reference,
                    "source_excerpt": str(item.get("extracted_text") or item.get("snippet") or item.get("cleaned_observation") or "")[:500],
                    "domain": claim.model_domain,
                    "proposed_observation_statement": claim.atomic_statement,
                    "problem_stage": "mapping" if failed_validation == "mapping" else ("validation" if failed_validation == "observation" else "extraction"),
                    "intended_domain": claim.model_domain,
                })
        return report

    def apply_observation(self, observation: Observation) -> ModelUpdateResult:
        if observation.lifecycle_state not in {"accepted", "Validated"}: return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", observation.affected_attribute, "ignored")
        model = self.models.get(observation.enterprise_id); key = observation.affected_attribute; domain = key.split(".", 1)[0]; lower = observation.atomic_statement.casefold()
        if any(marker in lower for marker in UNKNOWN_MARKERS):
            unknown_id = f"UNK-{hashlib.sha256((observation.enterprise_id + key).encode()).hexdigest()[:12].upper()}"; existing = model.unknowns.get(unknown_id); related = tuple(dict.fromkeys([*(existing.related_observation_ids if existing else ()), observation.observation_id or ""]))
            model.unknowns[unknown_id] = EnterpriseUnknown(unknown_id, observation.enterprise_id, f"Unknown model state for {key}", domain, "medium", ("accepted corroborating evidence",), "open", related, review_at=observation.last_confirmed_date); model.updated_at = now_iso(); self.models.save(model)
            return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", key, "unknown_created", unknown_created=True)
        existing = model.attributes.get(key); contradiction = bool(existing and existing.current_value and existing.current_value != observation.atomic_statement and any(t in lower or t in str(existing.current_value).casefold() for t in CONFLICT_TERMS))
        if existing:
            prior = tuple(existing.prior_values)
            if existing.current_value != observation.atomic_statement and not contradiction: prior = (*prior, {"value": existing.current_value, "confidence": existing.confidence, "superseded_at": now_iso(), "observation_ids": existing.observation_ids})
            observation_ids = tuple(dict.fromkeys([*existing.observation_ids, observation.observation_id or ""])); evidence_ids = tuple(dict.fromkeys([*existing.evidence_ids, *observation.supporting_evidence_ids])); domain_value = getattr(observation, "normalised_amount", None) or (existing.current_value if existing and observation.observation_type == 'financial_metric_reported' else (_financial_model_value(observation.atomic_statement) if observation.observation_type == 'financial_metric_reported' else observation.atomic_statement)); value = existing.current_value if contradiction else domain_value; conflicts = tuple(dict.fromkeys([*existing.conflicting_observation_ids, observation.observation_id or ""])) if contradiction else existing.conflicting_observation_ids; state = "contradicted" if contradiction else observation.contradiction_state
        else:
            prior = (); observation_ids = (observation.observation_id or "",); evidence_ids = observation.supporting_evidence_ids; value = getattr(observation, "normalised_amount", None) or (_financial_model_value(observation.atomic_statement) if observation.observation_type == 'financial_metric_reported' else observation.atomic_statement); conflicts = (); state = observation.contradiction_state
        confidence = max(observation.confidence, existing.confidence if existing else 0); confidence_history = (*(existing.confidence_history if existing else ()), {"observation_id": observation.observation_id or "", "confidence": observation.confidence, "recorded_at": now_iso()})
        model.attributes[key] = EnterpriseModelAttribute(domain, key, value, confidence, observation.last_confirmed_date or observation.observation_date, observation.freshness, observation_ids, evidence_ids, observation.provenance_type, "trusted", state, conflicts, prior, confidence_history); model.updated_at = now_iso(); self.models.save(model)
        return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", key, "contradiction_recorded" if contradiction else ("updated" if existing else "created"), contradiction=contradiction)

    def rebuild_from_ledger(self) -> list[ModelUpdateResult]:
        return [self.apply_observation(obs) for obs in self.observations.list()]
