from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal
import re
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
class MetricCatalogueEntry:
    canonical_metric_id: str
    canonical_label: str
    aliases: tuple[str, ...]
    permitted_accounting_bases: tuple[str, ...]
    expected_value_type: str = 'numeric'
    normalisation_rules: str = 'monetary_amount_with_explicit_currency_scale_period_scope_state_basis_and_source_locator'

METRIC_CATALOGUE: dict[str, MetricCatalogueEntry] = {
    'revenue': MetricCatalogueEntry('revenue', 'Revenue', ('revenue','reported revenue','reported revenue for fy26','group revenue'), ('statutory','other_explicitly_reported_basis')),
    'adjusted_ebitda': MetricCatalogueEntry('adjusted_ebitda', 'Adjusted EBITDA', ('adjusted ebitda','adjusteda ebitda','adjusted EBITDAa','reported adjusted ebitda','adjusteda ebitda for fy26'), ('adjusted','alternative_performance_measure')),
    'operating_profit': MetricCatalogueEntry('operating_profit', 'Operating profit', ('operating profit','reported operating profit'), ('statutory','adjusted','other_explicitly_reported_basis')),
    'profit_before_tax': MetricCatalogueEntry('profit_before_tax', 'Profit before tax', ('profit before tax','pbt'), ('statutory','adjusted','other_explicitly_reported_basis')),
    'capital_expenditure': MetricCatalogueEntry('capital_expenditure', 'Capital expenditure', ('capital expenditure','capex','capital expenditure for fy26','reported capital expenditure'), ('statutory','other_explicitly_reported_basis')),
    'cash_flow_from_operating_activities': MetricCatalogueEntry('cash_flow_from_operating_activities', 'Cash flow from operating activities', ('cash flow from operating activities','net cash inflow from operating activities'), ('statutory','other_explicitly_reported_basis')),
    'normalised_free_cash_flow': MetricCatalogueEntry('normalised_free_cash_flow', 'Normalised free cash flow', ('normalised free cash flow','normalized free cash flow','nfcf'), ('alternative_performance_measure','other_explicitly_reported_basis')),
    'net_debt': MetricCatalogueEntry('net_debt', 'Net debt', ('net debt','closing net debt'), ('alternative_performance_measure','other_explicitly_reported_basis')),
}
_ALIAS_INDEX: dict[str, str] = {}
_PERIOD_RE = re.compile(r'\b(?:fy\d{2}|20\d{2}|for the year|reported|actual|guidance|target|bt group|plc)\b', re.I)

def _clean_metric_text(value: str | None) -> str:
    text = (value or '').casefold().replace('&', 'and').replace('-', ' ')
    if 'financial_performance.metrics.' in text:
        parts = text.split('.')
        try: text = parts[parts.index('metrics') + 1]
        except Exception: pass
    text = text.replace('adjusteda', 'adjusted').replace('ebitdaa', 'ebitda')
    text = _PERIOD_RE.sub(' ', text)
    text = re.sub(r'[^a-z0-9 ]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

for entry in METRIC_CATALOGUE.values():
    for alias in (entry.canonical_metric_id.replace('_',' '), entry.canonical_label, *entry.aliases):
        _ALIAS_INDEX[_clean_metric_text(alias)] = entry.canonical_metric_id

def resolve_metric(value: str | None) -> tuple[MetricCatalogueEntry | None, str | None]:
    cleaned = _clean_metric_text(value)
    if not cleaned:
        return None, 'metric_identity_ambiguous'
    if cleaned in _ALIAS_INDEX:
        return METRIC_CATALOGUE[_ALIAS_INDEX[cleaned]], None
    matches = [entry for key, mid in _ALIAS_INDEX.items() if key and (key in cleaned or cleaned in key) for entry in [METRIC_CATALOGUE[mid]]]
    uniq = {m.canonical_metric_id: m for m in matches}
    if len(uniq) == 1:
        return next(iter(uniq.values())), None
    return None, 'metric_identity_ambiguous' if matches else 'unsupported_metric'

def canonical_metric(value: str | None) -> str:
    entry, reason = resolve_metric(value)
    return entry.canonical_metric_id if entry else (reason or 'unsupported_metric')

@dataclass(frozen=True)
class CanonicalFinancialMetricFact:
    enterprise_id: str; canonical_metric_id: str; metric_label: str; reported_amount: Any; currency: str; reported_scale: str; normalised_amount: Any; original_display_value: str; precision: str; rounding_status: str; reporting_period: str; period_start: str | None; period_end: str | None; scope: str; financial_measurement_state: str; accounting_basis: str; source_identity: str; source_locator: str; supporting_evidence_lineage: tuple[str, ...]; confidence: int; freshness: str; observed_date: str; effective_date: str | None; enterprise_model_attribute_path: str
    def to_dict(self) -> dict[str, Any]: return asdict(self)

def accounting_basis(claim: dict[str, Any]) -> str | None:
    explicit = claim.get('accounting_basis')
    if explicit in SUPPORTED_ACCOUNTING_BASES: return explicit
    text = ' '.join(str(claim.get(k) or '') for k in ('predicate','metric_identity','original_statement','source_excerpt','supporting_context')).casefold()
    if 'adjusted' in text: return 'adjusted'
    if 'statutory' in text: return 'statutory'
    if 'alternative performance' in text or re.search(r'\bapm\b', text): return 'alternative_performance_measure'
    if 'basis' in text and any(w in text for w in ('reported basis','constant currency')): return 'other_explicitly_reported_basis'
    metric_entry, _ = resolve_metric(claim.get('predicate') or claim.get('metric_identity') or claim.get('affected_attribute'))
    if metric_entry and len(metric_entry.permitted_accounting_bases) == 1:
        return metric_entry.permitted_accounting_bases[0]
    if metric_entry and metric_entry.canonical_metric_id in {'capital_expenditure', 'cash_flow_from_operating_activities'} and not re.search(r'\badjusted\b|\bapm\b|alternative performance|normalised|normalized', text):
        return 'statutory'
    # Legacy hosted/report fixtures use provider text such as 'Revenue was £19.7bn' with no separate basis field.
    # Keep this narrow to revenue so non-revenue metrics still surface accounting_basis_ambiguous.
    if re.search(r'\brevenue\b', text) and not re.search(r'\badjusted\b|\bapm\b|alternative performance', text): return 'statutory'
    return None

def measurement_state(claim: dict[str, Any]) -> str | None:
    raw = str(claim.get('state') or '').casefold(); ctype = str(claim.get('claim_type') or '').casefold()
    text = ' '.join(str(claim.get(k) or '') for k in ('original_statement','source_excerpt','supporting_context')).casefold()
    if raw in {'guidance','target','forecast','prior_period_comparator'}: return raw
    if ctype == 'financial_guidance_stated' or 'guidance' in text or 'outlook' in text: return 'guidance'
    if ctype == 'financial_target_stated' or 'target' in text: return 'target'
    if raw == 'actual' or (raw in {'current','historical'} and any(w in text for w in ('reported','annual report','results','financial highlights','for fy','year ended'))): return 'actual'
    return None

def normalise_scale(scale: str | None) -> str | None:
    return None if scale is None else CANONICAL_SCALE.get(str(scale).strip().casefold())

def _scale_from_evidence(claim: dict[str, Any]) -> str | None:
    explicit = normalise_scale(claim.get('reported_scale') or claim.get('scale'))
    if explicit: return explicit
    text = ' '.join(str(claim.get(k) or '') for k in ('original_display_value','display_value','source_excerpt','supporting_context','original_statement'))
    low = text.casefold()
    if re.search(r'(?:£|gbp\s*)\s*[0-9][0-9,]*(?:\.[0-9]+)?\s*(bn|billion)\b', low): return 'billions'
    if re.search(r'(?:£|gbp\s*)\s*[0-9][0-9,]*(?:\.[0-9]+)?\s*(m|million)\b', low): return 'millions'
    if '£m' in low or 'gbp million' in low or 'in millions' in low: return 'millions'
    if '£bn' in low or 'gbp billion' in low or 'in billions' in low: return 'billions'
    return None

def normalise_amount(amount: Any, scale: str | None) -> Decimal | None:
    canonical = normalise_scale(scale)
    if canonical is None or amount is None: return None
    return Decimal(str(amount).replace(',', '')) * SCALE_FACTORS[canonical]


def rounding_interval(amount: Any, scale: str | None) -> tuple[Decimal, Decimal] | None:
    """Return the base-unit half-open interval implied by reported decimal precision."""
    canonical = normalise_scale(scale)
    if canonical is None or amount is None:
        return None
    text = str(amount).replace(',', '').strip()
    decimals = len(text.split('.', 1)[1]) if '.' in text else 0
    quantum = (Decimal('1').scaleb(-decimals)) * SCALE_FACTORS[canonical]
    centre = Decimal(text) * SCALE_FACTORS[canonical]
    half = quantum / Decimal('2')
    return centre - half, centre + half

def rounding_compatible(rounded_amount: Any, rounded_scale: str | None, precise_normalised: Any) -> bool:
    interval = rounding_interval(rounded_amount, rounded_scale)
    if interval is None or precise_normalised is None:
        return False
    value = Decimal(str(precise_normalised).replace(',', ''))
    return interval[0] <= value < interval[1]

def display_amount(amount: Any, currency: str | None, scale: str | None) -> str:
    symbol = '£' if (currency or '').upper() == 'GBP' else ((currency or '') + ' ' if currency else '')
    suffix = {'units':'','thousands':'k','millions':'m','billions':'bn'}.get(normalise_scale(scale) or '', '')
    text = format(Decimal(str(amount).replace(',', '')).normalize(), 'f') if amount is not None else ''
    return f'{symbol}{text}{suffix}'

def _precision(amount: Any) -> str:
    text = str(amount); return f"{len(text.split('.',1)[1])}dp" if '.' in text else 'integer'

def _is_non_numeric_narrative(claim: dict[str, Any]) -> bool:
    if claim.get('reported_amount', claim.get('value')) is None: return True
    text = ' '.join(str(claim.get(k) or '') for k in ('predicate','original_statement','source_excerpt','supporting_context')).casefold()
    return bool(re.search(r'cash flow inflection|expectation|expects|reiterated|narrative', text)) and not re.search(r'(?:£|gbp\s*)\s*[0-9][0-9,]*(?:\.[0-9]+)?\s*(?:bn|billion|m|million)\b', text)

def canonicalise_financial_claim(claim: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    claim = dict(claim); reasons: list[str] = []
    if claim.get('claim_type') not in FINANCIAL_CLAIM_TYPES and claim.get('claim_type') != 'financial_metric_reported': return claim, reasons
    if _is_non_numeric_narrative(claim): reasons.append('non_numeric_narrative')
    metric_entry, metric_reason = resolve_metric(claim.get('predicate') or claim.get('metric_identity') or claim.get('affected_attribute'))
    if metric_reason: reasons.append(metric_reason)
    metric = metric_entry.canonical_metric_id if metric_entry else (metric_reason or 'unsupported_metric')
    scale = _scale_from_evidence(claim); amount = claim.get('reported_amount', claim.get('value'))
    currency = claim.get('currency') or ('GBP' if '£' in str(claim.get('source_excerpt') or claim.get('original_statement') or claim.get('display_value') or '') else None)
    normalised = normalise_amount(amount, scale)
    if not scale: reasons.append('financial_scale_ambiguous')
    if not currency: reasons.append('financial_currency_missing')
    if normalised is None: reasons.append('financial_value_not_reconstructable')
    basis = accounting_basis(claim)
    if basis not in SUPPORTED_ACCOUNTING_BASES: reasons.append('accounting_basis_ambiguous')
    state = measurement_state(claim)
    if state not in FINANCIAL_MEASUREMENT_STATES: reasons.append('measurement_state_ambiguous')
    metric_path = metric
    metric_label = metric_entry.canonical_label if metric_entry else metric
    text_for_variant = ' '.join(str(claim.get(k) or '') for k in ('predicate','metric_identity','original_statement','source_excerpt','supporting_context')).casefold()
    if metric == 'operating_profit' and basis in {'statutory', 'adjusted'} and basis in text_for_variant:
        metric_path = f'operating_profit_{basis}'
        metric_label = f"Operating profit ({basis})"
    scope = claim.get('enterprise_scope') or ('segment' if claim.get('business_unit') and 'bt group' not in str(claim.get('business_unit')).casefold() else 'group')
    period = claim.get('period')
    if not period: reasons.append('financial_period_missing')
    if not claim.get('source_excerpt'): reasons.append('invalid_lineage')
    normalised_value = int(normalised) if normalised is not None and normalised == normalised.to_integral_value() else (str(normalised) if normalised is not None else None)
    path = f"financial_performance.metrics.{metric_path}.{period}.{state}" if period and state and not metric_reason else claim.get('affected_attribute')
    evidence = tuple(e for e in (claim.get('evidence_id'), claim.get('source_identity'), claim.get('source_locator')) if e)
    canonical_fact = None
    display = claim.get('original_display_value') or claim.get('display_value') or display_amount(amount, currency, scale)
    if not reasons:
        canonical_fact = CanonicalFinancialMetricFact(claim.get('canonical_enterprise_id') or claim.get('enterprise_id'), metric_path, metric_label, amount, currency, scale, normalised_value, display, claim.get('precision') or _precision(amount), claim.get('rounding_status') or ('reported_rounded' if scale in {'billions','millions'} and '.' in str(amount) else 'unknown_rounding'), period, claim.get('period_start'), claim.get('period_end'), scope, state, basis, str(claim.get('source_identity') or claim.get('source_id') or ''), str(claim.get('source_locator') or claim.get('page_reference') or claim.get('page_range') or ''), evidence, int(claim.get('confidence') or 0), str(claim.get('freshness') or claim.get('evidence_freshness') or 'current'), str(claim.get('observed_date') or claim.get('extraction_timestamp') or '')[:10], claim.get('effective_date') or claim.get('period_end'), path)
    claim.update({'reported_amount': amount, 'reported_scale': scale, 'normalised_amount': normalised_value, 'value': normalised_value if normalised_value is not None else claim.get('value'), 'display_value': display, 'original_display_value': display, 'metric_identity': metric_path, 'metric_label': metric_label, 'enterprise_scope': scope, 'accounting_basis': basis, 'financial_measurement_state': state, 'state': state or claim.get('state'), 'original_pdf_page': claim.get('page_reference'), 'affected_attribute': path, 'canonical_financial_fact': canonical_fact.to_dict() if canonical_fact else None})
    claim['canonical_observation_identity'] = '|'.join(map(str, [claim.get('canonical_enterprise_id'), metric_path, period, scope, basis, state]))
    return claim, list(dict.fromkeys(reasons))
