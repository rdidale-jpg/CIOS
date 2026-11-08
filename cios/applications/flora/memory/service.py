"""Application service that turns accepted Evidence into maintained Enterprise Model memory."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
import re
from decimal import Decimal
from dataclasses import dataclass
from typing import Any

from cios.applications.flora.memory.models import EnterpriseModelAttribute, EnterpriseUnknown, ModelUpdateResult, Observation, MaterialPressure, now_iso
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

FINANCIAL_RE = re.compile(r"(?P<metric>revenue|adjusted EBITDA|normalised free cash flow|free cash flow|EBITDA|net debt|capital expenditure|capex|operating profit|profit before tax)\s*(?:was|of|:)?\s*(?:£|GBP\s*)(?P<value>[0-9,.]+)\s*(?P<unit>bn|billion|m|million)?", re.I)
UNIT_LIST_RE = re.compile(r"(?P<names>Consumer|Business|International|Openreach)(?:\s*,\s*(?:Consumer|Business|International|Openreach))*?(?:\s+and\s+(?:Consumer|Business|International|Openreach))?\s+as\s+(?P<kind>customer-facing units?|business units?|reporting segments?)", re.I)
CAPABILITY_RE = re.compile(r"(?P<names>Digital|Networks)(?:\s*,\s*(?:Digital|Networks))*?(?:\s+and\s+(?:Digital|Networks))?\s+provide\s+group capabilities", re.I)
STRATEGY_RE = re.compile(r"strategy\s+is\s+(?P<names>[A-Z][A-Za-z]+(?:\s*,\s*[A-Z][A-Za-z]+)*(?:\s+and\s+[A-Z][A-Za-z]+)?)", re.I)
TARGET_RE = re.compile(r"target\s+to\s+(?P<target>.+?)\s+by\s+(?P<date>FY\d{2}|20\d{2})", re.I)
LEADER_RE = re.compile(r"(?P<person>[A-Z][A-Za-z .'-]+)\s+(?:held|holds|is|was|serves as|appointed as)\s+(?:the role of\s+)?(?P<role>Group Chief Executive|Chief Financial Officer|Chair|Chairman|CEO|CFO)", re.I)


def _domain_for(condition: str) -> str:
    if condition in CLAIM_VOCABULARY:
        return CLAIM_VOCABULARY[condition]["domain"]
    return DOMAIN_MAP.get(condition or "", "enterprise_identity")


def _effective_period(observation: Observation) -> str:
    """Use supplied period/scope metadata, never collection time, for conflicts."""
    supplied = observation.human_provenance.get('effective_period') or observation.human_provenance.get('effective_date')
    periods = re.findall(r'\b(?:FY\d{2,4}|Q[1-4](?:\s+20\d{2})?)\b', observation.atomic_statement, re.I)
    period = str(supplied).casefold() if supplied else '|'.join(p.casefold() for p in periods)
    if re.fullmatch(r'q[1-4]', period):
        period += '|' + observation.observation_date[:4]
    return period or observation.observation_date


def _assertions_conflict(left: Observation, right: Observation) -> bool:
    """Recognise explicit opposing assertions, not general semantic disagreement."""
    a, b = left.atomic_statement.casefold(), right.atomic_statement.casefold()
    if a == b:
        return False
    negative = lambda text: any(re.search(r'\b' + re.escape(t) + r'\b', text) for t in CONFLICT_TERMS)
    if negative(a) != negative(b):
        return True
    movement = r'\b(increased?|increasing|rose|risen|up|grew|decreased?|decreasing|fell|fallen|down|declined?)\b\s*(?:by\s+)?([+-]?\d+(?:\.\d+)?)\s*(%|percent|per cent)'
    ma, mb = re.search(movement, a), re.search(movement, b)
    if ma and mb:
        direction = lambda word: -1 if word.startswith(('decreas', 'declin', 'fell', 'fallen', 'down')) else 1
        return direction(ma[1]) * Decimal(ma[2]) != direction(mb[1]) * Decimal(mb[2])
    # Same assertion with different reported numbers (including financial facts).
    # Keep the surrounding words/units to avoid comparing unrelated quantities.
    number = r'[+-]?\d+(?:[.,]\d+)*'
    shape = lambda text: re.sub(number, '#', text.replace(' percent', '%').replace(' per cent', '%'))
    return shape(a) == shape(b) and re.findall(number, a) != re.findall(number, b)


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
        obs.human_provenance.update(dict(item.get('human_provenance') or {}))
        obs.human_provenance.update({k: item[k] for k in ('effective_date', 'effective_period', 'source_date', 'scope') if item.get(k)})
        if item.get('period'):
            obs.human_provenance['effective_period'] = item['period']
        obs.supersedes_observation_id = item.get('supersedes_observation_id')
        obs.retired_at = item.get('retired_at')
        obs.lifecycle_state = str(item.get('lifecycle_state') or obs.lifecycle_state)
        obs.last_confirmed_date = str(item.get('last_confirmed_date') or obs.last_confirmed_date)
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
        result=self._apply_observation(observation)
        # No descriptor means no new pressure. Only previously maintained,
        # dependent pressures are reassessed after a supporting fact changes.
        if observation.human_provenance.get('material_pressure'):
            self.assess_material_pressure(observation.observation_id)
        model=self.models.get(observation.enterprise_id)
        for pressure in tuple(model.material_pressures.values()):
            if pressure.source_input_id==observation.observation_id: continue
            supports=[self.observations.get(ref) for ref in pressure.observation_refs]
            if any(obs and obs.affected_attribute==observation.affected_attribute for obs in supports):
                self.assess_material_pressure(pressure.source_input_id,pressure.source_input_type)
        return result

    def assess_material_pressure(self, canonical_input_id: str, source_type: str='observation'):
        """Maintain ADR-026 state inside the existing Enterprise Model owner."""
        from cios.applications.flora.blueprint_import.material_pressure import candidate_from_source,qualify_candidates,MaterialPressureQualification
        from cios.applications.flora.blueprint_import.promotion import CanonicalJsonlRepository
        source=self.observations.get(canonical_input_id) if source_type=='observation' else CanonicalJsonlRepository('fact').get(canonical_input_id)
        if source is None: raise ValueError('Canonical pressure source is unavailable')
        provenance=(source.human_provenance if isinstance(source,Observation) else source)
        if not provenance.get('material_pressure'): return MaterialPressureQualification(())
        candidate=candidate_from_source(source,source_type)
        model=self.models.get(candidate.enterprise_id)
        result=qualify_candidates((candidate,),observations=self.observations,evidence=self.evidence,model=model)
        changed=False
        normalise=lambda value:json.loads(json.dumps(value,sort_keys=True))
        for assessment in result.assessments:
            c=assessment.candidate
            key=source_type+':'+canonical_input_id
            diagnostic=normalise(asdict(assessment))
            if model.pressure_assessments.get(key)!=diagnostic:
                model.pressure_assessments[key]=diagnostic; changed=True
            previous=model.material_pressures.get(assessment.identity)
            if previous is None:
                previous=next((p for p in model.material_pressures.values() if p.source_input_id==canonical_input_id and p.source_input_type==source_type),None)
            if not assessment.qualified and previous is None: continue
            if previous and (previous.superseded_by or (previous.resolved_at and not c.resolved_at and not assessment.qualified)):
                # A replaced object's history cannot silently become current
                # merely because its old source is replayed or reassessed.
                continue
            if previous is not None:
                known_inputs={previous.source_input_id,*(row.get('source_input_id') for row in previous.history)}
                if canonical_input_id in known_inputs and canonical_input_id!=previous.source_input_id:
                    # An old source replay may corroborate history, never undo a
                    # more recent accepted assessment or resolution.
                    refs=tuple(dict.fromkeys((*previous.evidence_refs,*c.evidence_refs)))
                    if refs!=previous.evidence_refs:
                        previous.evidence_refs=refs; previous.updated_at=now_iso();changed=True
                    continue
            qualification=assessment.qualification if assessment.qualification!='REJECTED' else 'NOT_QUALIFIED'
            values=dict(pressure_id=previous.pressure_id if previous else assessment.identity,
                enterprise_id=c.enterprise_id,condition_concept=previous.condition_concept if previous and not assessment.qualified else c.condition_concept,
                condition=c.condition or (previous.condition if previous else ''),affected_domain=previous.affected_domain if previous and not assessment.qualified else c.affected_domain,
                scope=previous.scope if previous and not assessment.qualified else c.scope,time_context=previous.time_context if previous and not assessment.qualified else c.time_context,
                mechanism=c.mechanism,consequence=c.consequence,consequence_domain=c.consequence_domain,
                qualification=qualification,source_input_id=canonical_input_id,source_input_type=source_type,
                observation_refs=tuple(dict.fromkeys((*(previous.observation_refs if previous else ()),*c.observation_refs))),
                evidence_refs=tuple(dict.fromkeys((*(previous.evidence_refs if previous else ()),*c.evidence_refs))),
                current_evidence_refs=c.evidence_refs,counter_evidence_refs=tuple(dict.fromkeys((*(previous.counter_evidence_refs if previous else ()),*assessment.counter_evidence_refs))),
                unknown_refs=tuple(dict.fromkeys((*(previous.unknown_refs if previous else ()),*c.unknown_refs))),contradiction_refs=tuple(dict.fromkeys((*(previous.contradiction_refs if previous else ()),*c.contradiction_refs))),
                confidence=c.confidence,observed_at=c.observed_at,effective_at=c.effective_at,
                resolved_at=c.resolved_at,resolution_evidence_refs=tuple(dict.fromkeys((*(previous.resolution_evidence_refs if previous else ()),*c.resolution_evidence_refs))),
                supersedes_pressure_id=c.supersedes_pressure_id,superseded_at='',identity_rationale=c.identity_rationale,assessment_reason=assessment.reason)
            before=asdict(previous) if previous else {}
            comparison={k:v for k,v in before.items() if k not in {'updated_at','last_change','history','superseded_by'}}
            if previous and normalise(comparison)==normalise(values): continue
            change='qualified' if previous is None else ('resolved' if c.resolved_at else
                'weakened' if isinstance(c.confidence,(int,float)) and isinstance(previous.confidence,(int,float)) and c.confidence<previous.confidence else
                'strengthened' if isinstance(c.confidence,(int,float)) and isinstance(previous.confidence,(int,float)) and c.confidence>previous.confidence else
                'qualification changed' if previous.qualification!=qualification else 'lineage or condition updated')
            snapshot={k:v for k,v in before.items() if k!='history'}
            history=(*previous.history,normalise(snapshot)) if previous else ()
            pressure=MaterialPressure(**values,history=history,last_change=change)
            model.material_pressures[pressure.pressure_id]=pressure;changed=True
            if assessment.qualified and c.supersedes_pressure_id:
                old=model.material_pressures[c.supersedes_pressure_id]
                if old.superseded_by==pressure.pressure_id: continue
                old.history=(*old.history,normalise({k:v for k,v in asdict(old).items() if k!='history'}))
                old.qualification='NOT_QUALIFIED';old.superseded_by=pressure.pressure_id
                old.superseded_at=c.effective_at or c.observed_at
                old.last_change='superseded through governed Evidence';old.updated_at=now_iso()
        if changed:
            model.updated_at=now_iso();self.models.save(model)
        return result

    def _apply_observation(self, observation: Observation) -> ModelUpdateResult:
        oid = observation.observation_id or ''
        key = observation.affected_attribute
        inactive=(observation.lifecycle_state.casefold() in {'retired','superseded'}
                  or bool(observation.retired_at) or 'expired' in observation.freshness.casefold())
        if inactive:
            model=self.models.get(observation.enterprise_id)
            current=model.attributes.get(key)
            state='superseded' if observation.lifecycle_state.casefold()=='superseded' else 'retired'
            old_value=_financial_model_value(observation.atomic_statement) if observation.observation_type=='financial_metric_reported' else observation.atomic_statement
            if (current and oid in current.observation_ids
                    and str(current.current_value)==str(old_value)
                    and current.last_observed_date in {observation.observation_date,observation.last_confirmed_date}):
                if current.trust_state==state: return ModelUpdateResult(observation.enterprise_id,oid,key,'unchanged')
                # Preserve the value and all its lineage/history, but remove
                # its authority as current support. Do not invent a replacement.
                current.trust_state=state
                current.freshness=observation.freshness if 'expired' in observation.freshness.casefold() else state
                current.updated_at=model.updated_at=now_iso()
                self.models.save(model)
                return ModelUpdateResult(observation.enterprise_id,oid,key,state)
            return ModelUpdateResult(observation.enterprise_id,oid,key,'ignored')
        if observation.lifecycle_state not in {"accepted", "Validated"}:
            return ModelUpdateResult(observation.enterprise_id, oid, key, "ignored")
        model = self.models.get(observation.enterprise_id)
        domain = key.split(".", 1)[0]
        lower = observation.atomic_statement.casefold()
        if any(marker in lower for marker in UNKNOWN_MARKERS):
            unknown_id = f"UNK-{hashlib.sha256((observation.enterprise_id + key).encode()).hexdigest()[:12].upper()}"; existing = model.unknowns.get(unknown_id); related = tuple(dict.fromkeys([*(existing.related_observation_ids if existing else ()), oid]))
            if existing and related == existing.related_observation_ids:
                return ModelUpdateResult(observation.enterprise_id, oid, key, 'unchanged')
            model.unknowns[unknown_id] = EnterpriseUnknown(unknown_id, observation.enterprise_id, f"Unknown model state for {key}", domain, "medium", ("accepted corroborating evidence",), "open", related, review_at=observation.last_confirmed_date); model.updated_at = now_iso(); self.models.save(model)
            return ModelUpdateResult(observation.enterprise_id, oid, key, "unknown_created", unknown_created=True)
        existing = model.attributes.get(key)
        if existing and oid in existing.observation_ids:
            # Replays and corroboration may extend lineage, never restore an old
            # value or append the same confidence assessment again.
            evidence = tuple(dict.fromkeys((*existing.evidence_ids, *observation.supporting_evidence_ids)))
            confidence = max(existing.confidence, observation.confidence)
            if evidence == existing.evidence_ids and confidence == existing.confidence:
                return ModelUpdateResult(observation.enterprise_id, oid, key, 'unchanged', contradiction=existing.contradiction_state != 'none')
            existing.evidence_ids = evidence
            if confidence != existing.confidence:
                existing.confidence = confidence
                existing.confidence_history = (*existing.confidence_history, {'observation_id': oid, 'confidence': observation.confidence, 'recorded_at': now_iso()})
            existing.updated_at = model.updated_at = now_iso()
            self.models.save(model)
            return ModelUpdateResult(observation.enterprise_id, oid, key, 'updated', contradiction=existing.contradiction_state != 'none')

        rows = self.observations.list()
        superseded = {o.supersedes_observation_id for o in rows if o.supersedes_observation_id
                      and o.lifecycle_state in {'accepted', 'Validated'}
                      and o.enterprise_id == observation.enterprise_id and o.affected_attribute == key}
        conflicts = [o for o in rows if o.observation_id != oid
                     and o.observation_id not in superseded
                     and o.lifecycle_state in {'accepted', 'Validated'}
                     and o.enterprise_id == observation.enterprise_id and o.affected_attribute == key
                     and o.human_provenance.get('scope') == observation.human_provenance.get('scope')
                     and _effective_period(o) == _effective_period(observation)
                     and _assertions_conflict(o, observation)]
        if conflicts:
            self.observations.record_conflict([oid, *(o.observation_id for o in conflicts)])
        contradiction = bool(conflicts)
        recorded_at = now_iso()
        is_older = bool(existing and observation.observation_date < existing.last_observed_date)
        value = getattr(observation, 'normalised_amount', None)
        if value is None:
            value = _financial_model_value(observation.atomic_statement) if observation.observation_type == 'financial_metric_reported' else observation.atomic_statement
        if existing:
            prior = tuple(existing.prior_values)
            if existing.current_value != value and not contradiction:
                prior = (*prior, {'value': value if is_older else existing.current_value,
                                 'confidence': observation.confidence if is_older else existing.confidence,
                                 'effective_date': observation.observation_date if is_older else existing.last_observed_date,
                                 'superseded_at': recorded_at, 'observation_ids': (oid,) if is_older else existing.observation_ids})
            observation_ids = tuple(dict.fromkeys((*existing.observation_ids, oid)))
            evidence_ids = tuple(dict.fromkeys((*existing.evidence_ids, *observation.supporting_evidence_ids)))
            if contradiction or is_older:
                value = existing.current_value
            conflict_ids = tuple(dict.fromkeys((*existing.conflicting_observation_ids, *(o.observation_id for o in conflicts), oid))) if contradiction else (() if not is_older else existing.conflicting_observation_ids)
            state = 'contradicted' if contradiction else (existing.contradiction_state if is_older else observation.contradiction_state)
        else:
            prior = (); observation_ids = (oid,); evidence_ids = observation.supporting_evidence_ids
            conflict_ids = (); state = observation.contradiction_state
        confidence = max(observation.confidence, existing.confidence if existing else 0)
        history = (*(existing.confidence_history if existing else ()), {'observation_id': oid, 'confidence': observation.confidence, 'recorded_at': recorded_at})
        last_date = existing.last_observed_date if is_older else observation.last_confirmed_date or observation.observation_date
        model.attributes[key] = EnterpriseModelAttribute(domain, key, value, confidence, last_date, existing.freshness if is_older else observation.freshness, observation_ids, evidence_ids, observation.provenance_type, 'trusted', state, conflict_ids, prior, history)
        model.updated_at = recorded_at
        self.models.save(model)
        return ModelUpdateResult(observation.enterprise_id, oid, key, 'contradiction_recorded' if contradiction else ('updated' if existing else 'created'), contradiction=contradiction)

    def rebuild_from_ledger(self) -> list[ModelUpdateResult]:
        return [self.apply_observation(obs) for obs in self.observations.list()]
