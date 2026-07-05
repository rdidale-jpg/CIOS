from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Any

SCALE_FACTORS = {
    'units': Decimal('1'), 'unit': Decimal('1'),
    'thousands': Decimal('1000'), 'thousand': Decimal('1000'), 'k': Decimal('1000'),
    'millions': Decimal('1000000'), 'million': Decimal('1000000'), 'm': Decimal('1000000'),
    'billions': Decimal('1000000000'), 'billion': Decimal('1000000000'), 'bn': Decimal('1000000000'),
}
CANONICAL_SCALE = {'unit':'units','units':'units','thousand':'thousands','thousands':'thousands','k':'thousands','million':'millions','millions':'millions','m':'millions','billion':'billions','billions':'billions','bn':'billions'}
FINANCIAL_CLAIM_TYPES = {'financial_metric_reported', 'financial_guidance_stated', 'financial_target_stated'}
FINANCIAL_MEASUREMENT_STATES = {'actual','guidance','target','forecast','prior_period_comparator'}
SUPPORTED_ACCOUNTING_BASES = {'statutory','adjusted','alternative_performance_measure','other_explicitly_reported_basis'}

@dataclass(frozen=True)
class CanonicalFinancialMetricFact:
    enterprise_id: str
    canonical_metric_id: str
    metric_label: str
    reported_amount: Any
    currency: str
    reported_scale: str
    normalised_amount: Any
    original_display_value: str
    precision: str
    rounding_status: str
    reporting_period: str
    period_start: str | None
    period_end: str | None
    scope: str
    financial_measurement_state: str
    accounting_basis: str
    source_identity: str
    source_locator: str
    supporting_evidence_lineage: tuple[str, ...]
    confidence: int
    freshness: str
    observed_date: str
    effective_date: str | None
    enterprise_model_attribute_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def canonical_metric(value: str | None) -> str:
    text = (value or 'metric').casefold().replace('&', 'and')
    text = text.replace('capex', 'capital expenditure').replace('ebitda', 'EBITDA'.casefold())
    # avoid deriving metric from full enterprise path
    if 'financial_performance.metrics.' in text:
        parts = text.split('.')
        try: return parts[parts.index('metrics') + 1]
        except Exception: pass
    return '_'.join(text.replace('-', ' ').split())

def accounting_basis(claim: dict[str, Any]) -> str | None:
    pred = str(claim.get('predicate') or claim.get('metric_identity') or claim.get('affected_attribute') or claim.get('original_statement') or '').casefold()
    if 'adjusted' in pred: return 'adjusted'
    if 'statutory' in pred: return 'statutory'
    if 'alternative performance' in pred or 'apm' in pred: return 'alternative_performance_measure'
    # annual-report reported metrics that are not explicitly adjusted are statutory by default only for standard IFRS-style metrics
    if any(m in pred for m in ('revenue','operating_profit','capital_expenditure','free_cash_flow','net_debt')):
        return 'statutory'
    return None

def measurement_state(claim: dict[str, Any]) -> str | None:
    raw = str(claim.get('state') or '').casefold()
    ctype = str(claim.get('claim_type') or '').casefold()
    text = ' '.join(str(claim.get(k) or '') for k in ('original_statement','source_excerpt','supporting_context')).casefold()
    if raw in {'guidance','target','forecast','prior_period_comparator'}: return raw
    if ctype == 'financial_guidance_stated' or 'guidance' in text or 'outlook' in text: return 'guidance'
    if ctype == 'financial_target_stated' or 'target' in text: return 'target'
    # `current` is freshness/provider vocabulary; annual-report reported results are actual only with reported-result context.
    if raw == 'actual' or (raw in {'current','historical'} and any(w in text for w in ('reported','annual report','results','financial highlights','for fy','year ended'))):
        return 'actual'
    return None

def normalise_scale(scale: str | None) -> str | None:
    if scale is None: return None
    return CANONICAL_SCALE.get(str(scale).strip().casefold())

def _scale_from_evidence(claim: dict[str, Any]) -> str | None:
    explicit = normalise_scale(claim.get('reported_scale') or claim.get('scale'))
    if explicit: return explicit
    text = ' '.join(str(claim.get(k) or '') for k in ('original_display_value','display_value','source_excerpt','supporting_context','original_statement'))
    low = text.casefold()
    if '£' in text or 'gbp' in low:
        # explicit suffix/word only; not magnitude inference
        import re
        if re.search(r'(?:£|gbp\s*)\s*[0-9][0-9,]*(?:\.[0-9]+)?\s*(bn|billion)\b', low): return 'billions'
        if re.search(r'(?:£|gbp\s*)\s*[0-9][0-9,]*(?:\.[0-9]+)?\s*(m|million)\b', low): return 'millions'
    if '£m' in low or 'gbp million' in low or 'in millions' in low: return 'millions'
    if '£bn' in low or 'gbp billion' in low or 'in billions' in low: return 'billions'
    return None

def normalise_amount(amount: Any, scale: str | None) -> Decimal | None:
    canonical = normalise_scale(scale)
    if canonical is None or amount is None: return None
    return Decimal(str(amount).replace(',', '')) * SCALE_FACTORS[canonical]

def display_amount(amount: Any, currency: str | None, scale: str | None) -> str:
    symbol = '£' if (currency or '').upper() == 'GBP' else ((currency or '') + ' ' if currency else '')
    suffix = {'units':'','thousands':'k','millions':'m','billions':'bn'}.get(normalise_scale(scale) or '', '')
    text = format(Decimal(str(amount).replace(',', '')).normalize(), 'f') if amount is not None else ''
    return f'{symbol}{text}{suffix}'

def _precision(amount: Any) -> str:
    text = str(amount)
    return f"{len(text.split('.',1)[1])}dp" if '.' in text else 'integer'

def canonicalise_financial_claim(claim: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    claim = dict(claim); reasons: list[str] = []
    if claim.get('claim_type') not in FINANCIAL_CLAIM_TYPES and claim.get('claim_type') != 'financial_metric_reported':
        return claim, reasons
    scale = _scale_from_evidence(claim)
    amount = claim.get('reported_amount', claim.get('value'))
    currency = claim.get('currency') or ('GBP' if '£' in str(claim.get('source_excerpt') or claim.get('original_statement') or '') else None)
    normalised = normalise_amount(amount, scale)
    if not scale: reasons.append('financial_scale_ambiguous')
    if not currency: reasons.append('financial_currency_missing')
    if normalised is None: reasons.append('financial_value_not_reconstructable')
    basis = claim.get('accounting_basis') or accounting_basis(claim)
    if basis not in SUPPORTED_ACCOUNTING_BASES: reasons.append('accounting_basis_ambiguous')
    state = measurement_state(claim)
    if state not in FINANCIAL_MEASUREMENT_STATES: reasons.append('measurement_state_ambiguous')
    scope = claim.get('enterprise_scope') or ('segment' if claim.get('business_unit') and 'bt group' not in str(claim.get('business_unit')).casefold() else 'group')
    metric = canonical_metric(claim.get('predicate') or claim.get('metric_identity') or claim.get('affected_attribute'))
    period = claim.get('period')
    if not period: reasons.append('financial_period_missing')
    if not claim.get('source_excerpt'): reasons.append('invalid_lineage')
    normalised_value = int(normalised) if normalised is not None and normalised == normalised.to_integral_value() else (str(normalised) if normalised is not None else None)
    path = f"financial_performance.metrics.{metric}.{period}.{state}".replace(' ', '_') if period and state else claim.get('affected_attribute')
    evidence = tuple(e for e in (claim.get('evidence_id'), claim.get('source_identity'), claim.get('source_locator')) if e)
    canonical_fact = None
    if not reasons:
        canonical_fact = CanonicalFinancialMetricFact(
            enterprise_id=claim.get('canonical_enterprise_id') or claim.get('enterprise_id'), canonical_metric_id=metric,
            metric_label=str(claim.get('metric_label') or metric.replace('_',' ').title()), reported_amount=amount, currency=currency,
            reported_scale=scale, normalised_amount=normalised_value, original_display_value=claim.get('original_display_value') or claim.get('display_value') or display_amount(amount, currency, scale),
            precision=claim.get('precision') or _precision(amount), rounding_status=claim.get('rounding_status') or ('reported_rounded' if scale in {'billions','millions'} and '.' in str(amount) else 'unknown_rounding'),
            reporting_period=period, period_start=claim.get('period_start'), period_end=claim.get('period_end'), scope=scope,
            financial_measurement_state=state, accounting_basis=basis, source_identity=str(claim.get('source_identity') or claim.get('source_id') or ''),
            source_locator=str(claim.get('source_locator') or claim.get('page_reference') or claim.get('page_range') or ''), supporting_evidence_lineage=evidence,
            confidence=int(claim.get('confidence') or 0), freshness=str(claim.get('freshness') or claim.get('evidence_freshness') or 'current'), observed_date=str(claim.get('observed_date') or claim.get('extraction_timestamp') or '')[:10], effective_date=claim.get('effective_date') or claim.get('period_end'), enterprise_model_attribute_path=path)
    claim.update({'reported_amount': amount, 'reported_scale': scale, 'normalised_amount': normalised_value, 'display_value': claim.get('display_value') or display_amount(amount, currency, scale), 'original_display_value': claim.get('original_display_value') or claim.get('display_value') or display_amount(amount, currency, scale), 'metric_identity': metric, 'enterprise_scope': scope, 'accounting_basis': basis, 'financial_measurement_state': state, 'state': state or claim.get('state'), 'original_pdf_page': claim.get('page_reference'), 'affected_attribute': path, 'canonical_financial_fact': canonical_fact.to_dict() if canonical_fact else None})
    claim['canonical_observation_identity'] = '|'.join(map(str, [claim.get('canonical_enterprise_id'), metric, period, scope, basis, state]))
    return claim, list(dict.fromkeys(reasons))
