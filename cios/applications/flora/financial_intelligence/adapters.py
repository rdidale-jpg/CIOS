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

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        if isinstance(self.reported_amount, Decimal):
            row["reported_amount"] = format(self.reported_amount, "f")
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
_VALUE_RE = re.compile(r"(?P<currency>£|GBP)?\s*(?P<amount>\(?-?\d[\d,]*(?:\.\d+)?\)?)(?:\s*(?P<suffix>bn|billion|m|million))?\b", re.I)
_METRIC_WORDS = re.compile(r"revenue|adjusted\s+ebitda|operating\s+profit|profit\s+before\s+tax|capital\s+expenditure|capex|cash\s+flow\s+from\s+operating\s+activities|normalised\s+free\s+cash\s+flow|normalized\s+free\s+cash\s+flow|net\s+debt", re.I)


def _context(lines: list[str], idx: int) -> tuple[str | None, str | None, str | None]:
    window = " \n".join(lines[max(0, idx - 8): idx + 1])
    currency = scale = period = None
    for pat, cur, sc in _SCALE_PATTERNS:
        if pat.search(window):
            currency, scale = cur, sc
            break
    pmatches = list(_PERIOD_RE.finditer(window))
    if pmatches:
        period = pmatches[-1].group(0)
    return currency, scale, period


def _amount(text: str) -> tuple[str, Decimal | None, str | None, str | None]:
    matches = list(_VALUE_RE.finditer(text))
    if not matches:
        return "", None, None, None
    m = matches[-1]
    raw = m.group(0).strip()
    val = m.group("amount").replace(",", "")
    negative = val.startswith("(") and val.endswith(")")
    val = val.strip("()")
    amount = Decimal(val)
    if negative:
        amount = -amount
    suffix = (m.group("suffix") or "").casefold()
    scale = "billions" if suffix in {"bn", "billion"} else "millions" if suffix in {"m", "million"} else None
    currency = "GBP" if (m.group("currency") or "") else None
    return raw, amount, currency, scale


class PdfFinancialTableAdapter:
    adapter_name = "pdf_financial_table"
    adapter_version = ADAPTER_VERSION

    def extract(self, document: ExperimentDocument, *, embedded_pages: tuple[DocumentPage, ...] = ()) -> StructuredFinancialAdapterResult:
        canonical = load_canonical_pdf_document(document, embedded_pages)
        return self.extract_from_canonical(canonical)

    def extract_from_canonical(self, canonical: CanonicalPdfDocument) -> StructuredFinancialAdapterResult:
        candidates: list[FinancialFactCandidate] = []
        exceptions: list[dict[str, Any]] = []
        for page in canonical.pages:
            lines = [re.sub(r"\s+", " ", l).strip() for l in page.text.splitlines() if l.strip()]
            for idx, line in enumerate(lines):
                if not _METRIC_WORDS.search(line):
                    continue
                raw_value, amount, inline_currency, inline_scale = _amount(line)
                currency, scale, period = _context(lines, idx)
                currency = inline_currency or currency
                scale = inline_scale or scale
                label = _METRIC_WORDS.search(line).group(0) if _METRIC_WORDS.search(line) else line
                exception = None
                if amount is None: exception = "table_context_incomplete"
                elif not scale: exception = "financial_scale_ambiguous"
                elif not period: exception = "reporting_period_ambiguous"
                excerpt = " | ".join(lines[max(0, idx - 3): idx + 1])
                cid_material = f"{canonical.document.document_id}|{page.pdf_page_number}|{idx}|{line}|{period}|{scale}"
                candidate = FinancialFactCandidate(
                    "FFC-" + hashlib.sha256(cid_material.encode()).hexdigest()[:16].upper(),
                    canonical.document.enterprise_id,
                    canonical.document.document_id,
                    f"{canonical.document.document_id}#page={page.pdf_page_number}",
                    page.pdf_page_number,
                    page.extraction_method,
                    label,
                    raw_value,
                    amount,
                    currency,
                    scale,
                    period,
                    "group" if "group" in excerpt.casefold() or canonical.document.enterprise_id else None,
                    "adjusted" if "adjusted" in label.casefold() else ("statutory" if "income statement" in excerpt.casefold() else None),
                    "actual",
                    excerpt,
                    90 if not exception else 50,
                    canonical.document.checksum,
                    self.adapter_version,
                    exception,
                )
                candidates.append(candidate)
                if exception:
                    exceptions.append({"candidate_id": candidate.candidate_id, "exception_type": exception, "source_page": page.pdf_page_number})
        return StructuredFinancialAdapterResult(self.adapter_name, self.adapter_version, canonical.document.checksum, tuple(candidates), tuple(exceptions), 0)
