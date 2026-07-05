"""Runtime-owned financial acquisition adapter boundary.

Adapters emit candidate data only. They do not create Observations or update the
Enterprise Model; canonicalisation and memory projection own those steps.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

from .pdf_document_adapter import CanonicalPdfDocument, load_canonical_pdf_document
from .schema import ExperimentDocument
from cios.applications.flora.live.documents import DocumentPage

ADAPTER_VERSION = "pdf-financial-table-v2"


@dataclass(frozen=True)
class FinancialTableEvidenceBundle:
    bundle_id: str
    source_document_id: str
    source_hash: str
    original_pdf_page_number: int
    table_id: str
    table_title: str
    table_bounding_box: tuple[float, float, float, float] | None
    table_unit_text: str
    table_currency: str | None
    table_scale: str | None
    column_heading: str
    column_period_text: str
    row_label: str
    row_bounding_box: tuple[float, float, float, float] | None
    raw_cell_text: str
    cell_bounding_box: tuple[float, float, float, float] | None
    parsed_amount: Decimal | None
    supporting_text_blocks: tuple[str, ...]
    extraction_method: str
    extraction_version: str
    extraction_confidence: int

    def is_complete(self) -> bool:
        return bool(
            self.source_document_id and self.source_hash and self.original_pdf_page_number
            and self.table_id and self.table_title and self.table_unit_text
            and self.table_currency and self.table_scale and self.column_heading
            and self.column_period_text and self.row_label and self.raw_cell_text
            and self.parsed_amount is not None and self.supporting_text_blocks
        )

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        if isinstance(self.parsed_amount, Decimal):
            row["parsed_amount"] = format(self.parsed_amount, "f")
        return row


@dataclass(frozen=True)
class FinancialFactCandidate:
    candidate_id: str
    enterprise_id: str
    source_id: str
    source_locator: str
    source_page: int | None
    source_method: str
    raw_metric_label: str
    raw_value_text: str
    reported_amount: Decimal | None
    currency: str | None
    reported_scale: str | None
    raw_period_text: str | None
    scope_text: str | None
    accounting_basis_text: str | None
    measurement_state_text: str | None
    supporting_excerpt: str
    extraction_confidence: int
    source_hash: str
    extraction_version: str
    exception: str | None = None
    evidence_bundle_id: str | None = None
    evidence_bundle: FinancialTableEvidenceBundle | None = None
    table_class: str | None = None

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        if isinstance(self.reported_amount, Decimal):
            row["reported_amount"] = format(self.reported_amount, "f")
        if self.evidence_bundle:
            row["evidence_bundle"] = self.evidence_bundle.to_dict()
        return row


@dataclass(frozen=True)
class StructuredFinancialAdapterResult:
    adapter_name: str
    adapter_version: str
    source_hash: str
    candidates: tuple[FinancialFactCandidate, ...]
    exceptions: tuple[dict[str, Any], ...] = ()
    ai_calls_made: int = 0


class StructuredFinancialAdapter(Protocol):
    adapter_name: str
    adapter_version: str

    def extract(self, document: ExperimentDocument, **kwargs: Any) -> StructuredFinancialAdapterResult: ...


class NarrativeFinancialAIAdapter:
    """Boundary wrapper for future narrative interpretation; not used for standard metrics."""
    adapter_name = "narrative_financial_ai"
    adapter_version = "deferred-v1"

    def extract(self, document: ExperimentDocument, **kwargs: Any) -> StructuredFinancialAdapterResult:
        return StructuredFinancialAdapterResult(self.adapter_name, self.adapter_version, document.checksum, (), (), ai_calls_made=0)


_SCALE_PATTERNS = (
    (re.compile(r"(?:£|gbp)\s*m\b|£m\b|\bgbp\s+millions\b|\bin\s+millions\b|\bmillion\b", re.I), "GBP", "millions"),
    (re.compile(r"(?:£|gbp)\s*bn\b|£bn\b|\bgbp\s+billions\b|\bin\s+billions\b|\bbillion\b", re.I), "GBP", "billions"),
)
_PERIOD_RE = re.compile(r"(?:year\s+ended\s+31\s+march\s+20\d{2}|fy\s*\d{2,4}|20\d{2})", re.I)
_VALUE_RE = re.compile(r"^(?P<currency>£|GBP)?\s*(?P<amount>\(?-?\d[\d,]*(?:\.\d+)?\)?)(?:\s*(?P<suffix>bn|billion|m|million))?$", re.I)
_UNIT_ONLY_RE = re.compile(r"^\s*(?:£|m|bn|£m|£bn|gbp|gbp\s+millions?|gbp\s+billions?)\s*$", re.I)
_APPROVED_TABLE_TITLE_RE = re.compile(r"financial highlights|group financial results|group results|income statement|cash[- ]?flow statement|balance sheet|alternative performance|net[- ]?debt|capital expenditure", re.I)
_GUIDANCE_RE = re.compile(r"guidance|outlook|target|ambition|forecast", re.I)
_ROW_ALIASES = {
    'revenue': ('revenue', 'group revenue'),
    'adjusted_ebitda': ('adjusted ebitda',),
    'operating_profit': ('operating profit',),
    'profit_before_tax': ('profit before tax', 'pbt'),
    'capital_expenditure': ('capital expenditure', 'capex'),
    'cash_flow_from_operating_activities': ('cash flow from operating activities', 'net cash inflow from operating activities', 'operating cash flow'),
    'normalised_free_cash_flow': ('normalised free cash flow', 'normalized free cash flow', 'nfcf'),
    'net_debt': ('net debt', 'closing net debt'),
}
_ALIAS_TO_LABEL = {alias: alias for aliases in _ROW_ALIASES.values() for alias in aliases}


def _scale_from_text(text: str) -> tuple[str | None, str | None]:
    for pat, cur, sc in _SCALE_PATTERNS:
        if pat.search(text or ''):
            return cur, sc
    return None, None


def _amount(text: str) -> tuple[str, Decimal | None, str | None, str | None, str | None]:
    cell = (text or '').strip()
    if not cell:
        return cell, None, None, None, 'empty_cell'
    if _UNIT_ONLY_RE.match(cell):
        return cell, None, None, None, 'unit_only_value'
    if '%' in cell:
        return cell, None, None, None, 'percentage_for_monetary_metric'
    m = _VALUE_RE.match(cell.replace(' ', '')) or _VALUE_RE.match(cell)
    if not m:
        return cell, None, None, None, 'malformed_amount'
    raw = m.group(0).strip()
    val = m.group('amount').replace(',', '')
    negative = val.startswith('(') and val.endswith(')')
    val = val.strip('()')
    amount = Decimal(val)
    if negative:
        amount = -amount
    if amount == amount.to_integral_value() and Decimal('1000') <= abs(amount) <= Decimal('2099') and not (m.group('currency') or m.group('suffix')):
        return raw, amount, None, None, 'four_digit_year_as_monetary_value'
    suffix = (m.group('suffix') or '').casefold()
    scale = 'billions' if suffix in {'bn', 'billion'} else 'millions' if suffix in {'m', 'million'} else None
    currency = 'GBP' if (m.group('currency') or '') else None
    return raw, amount, currency, scale, None


def _recognised_row(line: str) -> tuple[str | None, str | None, str | None]:
    cleaned = re.sub(r'[^a-z0-9 &-]+', ' ', (line or '').casefold()).replace('&', 'and')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    matches = []
    for metric, aliases in _ROW_ALIASES.items():
        for alias in aliases:
            if cleaned == alias or cleaned.startswith(alias + ' '):
                matches.append((metric, alias, cleaned[len(alias):].strip()))
    if len(matches) != 1:
        return None, None, 'unsupported_metric' if not matches else 'metric_identity_ambiguous'
    return matches[0]


def _period_from_heading(text: str) -> str | None:
    m = _PERIOD_RE.search(text or '')
    return m.group(0) if m else None


class PdfFinancialTableAdapter:
    adapter_name = "pdf_financial_table"
    adapter_version = ADAPTER_VERSION
    max_plausible_candidates = 96

    def extract(self, document: ExperimentDocument, *, embedded_pages: tuple[DocumentPage, ...] = ()) -> StructuredFinancialAdapterResult:
        canonical = load_canonical_pdf_document(document, embedded_pages)
        return self.extract_from_canonical(canonical)

    def extract_from_canonical(self, canonical: CanonicalPdfDocument) -> StructuredFinancialAdapterResult:
        candidates: list[FinancialFactCandidate] = []
        exceptions: list[dict[str, Any]] = []
        diagnostics = {"tables_detected": 0, "approved_financial_tables": 0, "rows_inspected": 0, "evidence_bundles_created": 0, "candidates_created": 0, "rejected_by_rule": {}}
        for page in canonical.pages:
            lines = [re.sub(r"\s+", " ", l).strip() for l in page.text.splitlines() if l.strip()]
            if not lines:
                continue
            title_idx = next((i for i, line in enumerate(lines) if _APPROVED_TABLE_TITLE_RE.search(line) and not _recognised_row(line)[0]), None)
            if title_idx is None:
                has_unit = any(_scale_from_text(line)[0] for line in lines[:4])
                has_period = any(_period_from_heading(line) for line in lines[:4])
                recognised_rows = sum(1 for line in lines if _recognised_row(line)[0])
                if not ((has_unit and has_period and recognised_rows >= 2) or (has_period and recognised_rows >= 1)):
                    continue
                title_idx = 0
                lines = ['Financial highlights', *lines]
            diagnostics["tables_detected"] += 1
            table_title = lines[title_idx]
            table_state = "guidance" if _GUIDANCE_RE.search(" ".join(lines[max(0, title_idx-1):title_idx+4])) else "reported_actual_results"
            if table_state != "reported_actual_results":
                continue
            unit_idx = None; currency = scale = None
            for i in range(title_idx, min(len(lines), title_idx + 8)):
                currency, scale = _scale_from_text(lines[i])
                if currency and scale:
                    unit_idx = i; break
            period_idx = None; period = None
            for i in range(title_idx, min(len(lines), title_idx + 10)):
                period = _period_from_heading(lines[i])
                if period:
                    period_idx = i; break
            if not period:
                continue
            if not (currency and scale):
                currency, scale = None, None
            diagnostics["approved_financial_tables"] += 1
            table_id = "TBL-" + hashlib.sha256(f"{canonical.document.document_id}|{page.pdf_page_number}|{table_title}|{period}".encode()).hexdigest()[:12].upper()
            used_cells: set[str] = set()
            for idx in range(max(unit_idx or title_idx, period_idx or title_idx) + 1, len(lines)):
                line = lines[idx]
                diagnostics["rows_inspected"] += 1
                metric_id, row_alias, row_reason = _recognised_row(line)
                if not metric_id:
                    continue
                raw_cell = line[len(row_alias or ''):].strip() if row_alias else ''
                raw_value, amount, inline_currency, inline_scale, amount_reason = _amount(raw_cell)
                bundle_id = "FTB-" + hashlib.sha256(f"{table_id}|{idx}|{row_alias}|{raw_cell}".encode()).hexdigest()[:16].upper()
                bundle = FinancialTableEvidenceBundle(
                    bundle_id=bundle_id,
                    source_document_id=canonical.document.document_id,
                    source_hash=canonical.document.checksum,
                    original_pdf_page_number=page.pdf_page_number,
                    table_id=table_id,
                    table_title=table_title,
                    table_bounding_box=None,
                    table_unit_text=lines[unit_idx or title_idx],
                    table_currency=inline_currency or currency,
                    table_scale=inline_scale or scale,
                    column_heading=lines[period_idx or title_idx],
                    column_period_text=period or '',
                    row_label=row_alias or line,
                    row_bounding_box=None,
                    raw_cell_text=raw_cell,
                    cell_bounding_box=None,
                    parsed_amount=amount,
                    supporting_text_blocks=tuple(lines[title_idx:min(len(lines), idx + 1)]),
                    extraction_method="pymupdf_table_or_geometric_text_strict" if page.extraction_method != 'embedded_text' else 'embedded_text_strict_table_lines',
                    extraction_version=self.adapter_version,
                    extraction_confidence=95,
                )
                diagnostics["evidence_bundles_created"] += 1
                exception = amount_reason
                if not exception and not bundle.table_scale:
                    exception = 'financial_scale_ambiguous'
                if not exception and not bundle.table_currency:
                    exception = 'financial_currency_missing'
                if not exception and not bundle.is_complete():
                    exception = "incomplete_financial_table_evidence_bundle"
                if not exception and raw_value in used_cells:
                    exception = "same_token_reused_for_multiple_rows"
                used_cells.add(raw_value)
                if exception:
                    diagnostics["rejected_by_rule"][exception] = diagnostics["rejected_by_rule"].get(exception, 0) + 1
                excerpt = " | ".join(bundle.supporting_text_blocks)
                cid_material = f"{bundle_id}|{metric_id}|{period}|{raw_value}"
                candidate = FinancialFactCandidate(
                    "FFC-" + hashlib.sha256(cid_material.encode()).hexdigest()[:16].upper(),
                    canonical.document.enterprise_id,
                    canonical.document.document_id,
                    f"{canonical.document.document_id}#page={page.pdf_page_number};table={table_id};row={idx};column={period}",
                    page.pdf_page_number,
                    bundle.extraction_method,
                    row_alias or metric_id,
                    raw_value,
                    amount,
                    bundle.table_currency,
                    bundle.table_scale,
                    period,
                    "group",
                    "adjusted" if metric_id == 'adjusted_ebitda' else ("alternative_performance_measure" if metric_id in {'normalised_free_cash_flow','net_debt'} else "statutory"),
                    "actual",
                    excerpt,
                    95 if exception is None else 40,
                    canonical.document.checksum,
                    self.adapter_version,
                    exception,
                    bundle_id,
                    bundle,
                    "financial_highlights" if "highlights" in table_title.casefold() else "approved_financial_table",
                )
                candidates.append(candidate)
                diagnostics["candidates_created"] += 1
                if exception:
                    exceptions.append({"candidate_id": candidate.candidate_id, "exception_type": exception, "source_page": page.pdf_page_number, "evidence_bundle_id": bundle_id})
        if len(candidates) > self.max_plausible_candidates:
            exceptions.append({"exception_type": "extraction_precision_failed", "rejection_reason": "implausible candidate volume", "candidate_count": len(candidates)})
            candidates = [c for c in candidates if c.exception is not None]
        diagnostics["accepted"] = len([c for c in candidates if c.exception is None])
        return StructuredFinancialAdapterResult(self.adapter_name, self.adapter_version, canonical.document.checksum, tuple(candidates), tuple(exceptions), 0)
