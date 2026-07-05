from __future__ import annotations
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
SUPPORTED_ACCOUNTING_BASES = {'actual','statutory','adjusted','guidance','target'}

def canonical_metric(value: str | None) -> str:
    text = (value or 'metric').casefold().replace('&', 'and')
    text = text.replace('capex', 'capital expenditure').replace('ebitda', 'EBITDA'.casefold())
    return '_'.join(text.replace('-', ' ').split())

def accounting_basis(claim: dict[str, Any]) -> str | None:
    state = str(claim.get('state') or '').casefold()
    pred = str(claim.get('predicate') or claim.get('affected_attribute') or claim.get('original_statement') or '').casefold()
    if 'adjusted' in pred: return 'adjusted'
    if 'statutory' in pred: return 'statutory'
    if state in {'guidance','target'}: return state
    if state in {'actual','current','historical'}: return 'actual'
    return None

def normalise_scale(scale: str | None) -> str | None:
    if scale is None: return None
    return CANONICAL_SCALE.get(str(scale).strip().casefold())

def normalise_amount(amount: Any, scale: str | None) -> Decimal | None:
    canonical = normalise_scale(scale)
    if canonical is None or amount is None: return None
    return Decimal(str(amount)) * SCALE_FACTORS[canonical]

def display_amount(amount: Any, currency: str | None, scale: str | None) -> str:
    symbol = '£' if (currency or '').upper() == 'GBP' else ((currency or '') + ' ' if currency else '')
    suffix = {'units':'','thousands':'k','millions':'m','billions':'bn'}.get(normalise_scale(scale) or '', '')
    text = format(Decimal(str(amount)).normalize(), 'f') if amount is not None else ''
    return f'{symbol}{text}{suffix}'

def canonicalise_financial_claim(claim: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    claim = dict(claim); reasons: list[str] = []
    if claim.get('claim_type') not in FINANCIAL_CLAIM_TYPES and claim.get('claim_type') != 'financial_metric_reported':
        return claim, reasons
    scale = normalise_scale(claim.get('reported_scale') or claim.get('scale') or claim.get('unit'))
    amount = claim.get('reported_amount', claim.get('value'))
    currency = claim.get('currency')
    normalised = normalise_amount(amount, scale)
    if not scale: reasons.append('financial_scale_ambiguous')
    if not currency: reasons.append('financial_currency_missing')
    if normalised is None: reasons.append('financial_value_not_reconstructable')
    basis = claim.get('accounting_basis') or accounting_basis(claim)
    if not basis: reasons.append('financial_accounting_basis_missing')
    scope = claim.get('enterprise_scope') or ('segment' if claim.get('business_unit') and 'bt group' not in str(claim.get('business_unit')).casefold() else 'group')
    metric = canonical_metric(claim.get('metric_identity') or claim.get('predicate') or claim.get('affected_attribute'))
    period = claim.get('period')
    if not period: reasons.append('financial_period_missing')
    if not claim.get('source_excerpt'): reasons.append('financial_supporting_context_missing')
    claim.update({
        'reported_amount': amount, 'reported_scale': scale, 'normalised_amount': int(normalised) if normalised is not None and normalised == normalised.to_integral_value() else (str(normalised) if normalised is not None else None),
        'display_value': claim.get('display_value') or display_amount(amount, currency, scale), 'metric_identity': metric,
        'enterprise_scope': scope, 'accounting_basis': basis, 'original_pdf_page': claim.get('page_reference'),
    })
    claim['affected_attribute'] = f"financial_performance.metrics.{metric}.{period}.{scope}.{basis}".replace(' ', '_')
    claim['canonical_observation_identity'] = '|'.join(map(str, [claim.get('canonical_enterprise_id'), metric, period, scope, basis]))
    return claim, list(dict.fromkeys(reasons))
