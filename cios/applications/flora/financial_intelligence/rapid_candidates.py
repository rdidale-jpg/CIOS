"""Deterministic Slice 2B-1 source-backed rapid financial candidate extraction.

Runtime-only candidate extraction: no AI calls, no provider calls after Slice 2A
acquisition, and no canonical Evidence/Observation/Enterprise Model writes.
Source locator page numbers are one-based PDF page numbers.
"""
from __future__ import annotations

import hashlib, json, re, time
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .adapters import FinancialFactCandidate
from .rapid_sources import AcquiredRapidSource, RapidSourceReceipt
from .page_aware_pdf import parse_page_aware_pdf

EXTRACTION_VERSION = "rapid-core-candidates-v1"
PROFILE_DIR = Path(__file__).resolve().parents[4] / "config" / "flora" / "rapid_extraction"
_EXCEPTION_CATEGORIES = {
    "source precondition failed", "metric label not found", "multiple metric rows matched", "period column not identified",
    "amount ambiguous", "scale missing", "scale contradictory", "currency missing", "scope ambiguous",
    "segment value rejected", "accounting basis ambiguous", "adjusted value rejected", "supporting excerpt unavailable",
    "source locator incomplete", "duplicate candidate", "parser failure",
}

@dataclass(frozen=True)
class CandidateExtractionException:
    metric_identity: str | None
    category: str
    page: int | None
    source_sha256: str | None
    explanation: str
    retry_with_same_source_useful: bool
    evidence_needed: str
    location: dict[str, Any] | None = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class RapidFinancialCandidateExtractionResult:
    extraction_status: str
    source_receipt_reference: dict[str, Any]
    source_sha256: str | None
    extraction_version: str
    candidate_count: int
    candidates: tuple[FinancialFactCandidate, ...]
    exception_count: int
    exceptions: tuple[CandidateExtractionException, ...]
    pages_examined: tuple[int, ...]
    table_or_section_matches: tuple[str, ...]
    elapsed_ms: int
    ai_call_count: int = 0
    provider_cost: float = 0.0
    canonical_write_count: int = 0
    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "candidates": [c.to_dict() for c in self.candidates], "exceptions": [e.to_dict() for e in self.exceptions]}

@dataclass(frozen=True)
class _Row:
    page:int; section:str; scale_context:str; headers:tuple[str,...]; label:str; values:tuple[str,...]; excerpt:str

def _exc(metric, category, receipt, explanation, page=None, location=None, retry=True, evidence="Clear source text resolving the extraction ambiguity"):
    assert category in _EXCEPTION_CATEGORIES
    return CandidateExtractionException(metric, category, page, receipt.sha256, explanation, retry, evidence, location)

def _preconditions(r: RapidSourceReceipt) -> list[str]:
    failed=[]
    if r.validation_result != "accepted": failed.append("validation result accepted")
    if not r.pdf_magic_valid: failed.append("PDF magic valid")
    if r.document_parse_result != "parsed": failed.append("parser validation successful")
    if r.identity_result != "matched": failed.append("issuer identity matched")
    if r.period_result != "matched": failed.append("reporting period matched")
    if not r.sha256: failed.append("actual-byte SHA-256 present")
    if r.bytes_downloaded <= 0: failed.append("bytes downloaded greater than zero")
    return failed

def load_rapid_extraction_profile(configuration_key: str, profile_dir: Path = PROFILE_DIR) -> dict[str, Any]:
    for p in sorted(profile_dir.glob("*.json")):
        data=json.loads(p.read_text())
        if data.get("configuration_key") == configuration_key:
            return data
    raise FileNotFoundError(configuration_key)

def _pdf_pages(path: Path) -> list[tuple[int,str]]:
    parsed = parse_page_aware_pdf(path)
    if parsed.status != "parsed":
        raise RuntimeError(f"parser failure: {parsed.failure_class or parsed.status}")
    return [(p.page_number, p.text) for p in parsed.pages if p.text.strip()]

def _scale(text: str, profile: dict[str,Any]) -> tuple[str|None,str|None,str|None]:
    found=[]
    for marker, scale in (profile.get("permitted_scale_markers") or {}).items():
        if re.search(r"\b"+re.escape(marker)+r"\b", text, re.I): found.append(("GBP", scale, marker))
    uniq={(c,s) for c,s,_ in found}
    if len(uniq)>1: return None, None, "contradictory"
    return found[0] if found else (None,None,None)

def _amount(cell: str) -> Decimal:
    raw=cell.strip().replace(" ", "")
    m=re.fullmatch(r"\(?-?\d[\d,]*(?:\.\d+)?\)?", raw)
    if not m: raise InvalidOperation(cell)
    neg=raw.startswith("(") and raw.endswith(")")
    val=Decimal(raw.strip("()").replace(",", ""))
    return -val if neg else val

def _norm(s: str) -> str: return re.sub(r"[^a-z0-9]+", " ", s.casefold()).strip()

def _extract_rows(pages: list[tuple[int,str]], profile: dict[str,Any]) -> tuple[list[_Row], list[CandidateExtractionException], list[str]]:
    rows=[]; exceptions=[]; matches=[]
    section_markers=[m.casefold() for m in profile.get("table_or_section_markers",())]
    for page_no,text in pages:
        lines=[re.sub(r"\s+", " ", l).strip() for l in text.splitlines() if l.strip()]
        section=""; headers=(); scale_context=""
        for i,line in enumerate(lines):
            low=line.casefold()
            if any(m in low for m in section_markers): section=line; matches.append(line)
            cur,sc,marker=_scale(line, profile)
            if marker: scale_context=line
            if any(h.casefold() in low for h in profile.get("current_period_column_markers",())) and any(h.casefold() in low for h in profile.get("prior_period_column_markers",())):
                headers=tuple(re.split(r"\s{2,}|\|", line)) if "|" in line or re.search(r"\s{2,}", line) else tuple(line.split())
            # pipe-delimited fixture row: label | FY26 | FY25 | basis | scope
            if "|" in line:
                parts=[p.strip() for p in line.split("|")]
                if len(parts)>=3 and not any(h.casefold() in parts[0].casefold() for h in profile.get("current_period_column_markers",())):
                    rows.append(_Row(page_no, section, scale_context, headers, parts[0], tuple(parts[1:]), line))
    return rows, exceptions, tuple(dict.fromkeys(matches))

def _candidate_id(material: dict[str,Any]) -> str:
    return "RFC-"+hashlib.sha256(json.dumps(material, sort_keys=True, default=str).encode()).hexdigest()[:20].upper()

def extract_rapid_financial_candidates(acquired: AcquiredRapidSource, *, profile: dict[str,Any] | None=None, profile_path: Path | None=None) -> RapidFinancialCandidateExtractionResult:
    start=time.monotonic(); r=acquired.receipt; receipt_ref=r.to_dict(); profile=profile or json.loads((profile_path or (PROFILE_DIR / f"{r.enterprise_id.lower()}-{r.reporting_period.lower()}.json")).read_text())
    pre=_preconditions(r)
    if pre:
        ex=(_exc(None,"source precondition failed",r,"Rapid source receipt failed preconditions: "+", ".join(pre), retry=False, evidence="Accepted Slice 2A receipt with valid PDF parsing, identity, period, SHA-256 and bytes"),)
        return RapidFinancialCandidateExtractionResult("failed_precondition", receipt_ref, r.sha256, EXTRACTION_VERSION, 0, (), len(ex), ex, (), (), int((time.monotonic()-start)*1000))
    if r.sha256 and hashlib.sha256(acquired.path.read_bytes()).hexdigest()!=r.sha256:
        ex=(_exc(None,"source precondition failed",r,"Source receipt SHA-256 does not match acquired PDF bytes.", retry=False, evidence="Matching actual-byte receipt and acquired temporary source"),)
        return RapidFinancialCandidateExtractionResult("failed_precondition", receipt_ref, r.sha256, EXTRACTION_VERSION, 0, (), len(ex), ex, (), (), int((time.monotonic()-start)*1000))
    try: pages=_pdf_pages(acquired.path)
    except RuntimeError as e:
        ex=(_exc(None,"parser failure",r,str(e), retry=True, evidence="Parser-readable PDF text"),)
        return RapidFinancialCandidateExtractionResult("failed_extraction", receipt_ref, r.sha256, EXTRACTION_VERSION, 0, (), len(ex), ex, (), (), int((time.monotonic()-start)*1000))
    rows, exceptions, matches = _extract_rows(pages, profile)
    candidates=[]; seen=set()
    current_markers=[m.casefold() for m in profile.get("current_period_column_markers",())]
    for metric in profile.get("metric_definitions",()):
        mid=metric["proposed_canonical_metric_id"]; aliases=[_norm(a) for a in metric.get("accepted_source_labels",())]
        matched=[row for row in rows if _norm(row.label) in aliases]
        adjusted=[row for row in rows if _norm(row.label).startswith("adjusted ") and any(a in _norm(row.label) for a in aliases)]
        segment=[row for row in rows if "segment" in row.excerpt.casefold() and any(a in _norm(row.label) for a in aliases)]
        for row in adjusted: exceptions.append(_exc(mid,"adjusted value rejected",r,"Adjusted row is outside statutory Slice 2B-1 scope.",row.page,{"row":row.label},False,"Statutory row for the metric"))
        for row in segment: exceptions.append(_exc(mid,"segment value rejected",r,"Segment row is outside Group scope.",row.page,{"row":row.label},False,"Group consolidated row for the metric"))
        matched=[m for m in matched if "segment" not in m.excerpt.casefold()]
        if not matched:
            exceptions.append(_exc(mid,"metric label not found",r,f"No statutory Group row matched {mid}.", evidence="A statutory Group row with accepted metric label")); continue
        if len(matched)>1:
            exceptions.append(_exc(mid,"multiple metric rows matched",r,f"Multiple statutory Group rows matched {mid}.", matched[0].page, retry=True, evidence="Unambiguous single metric row")); continue
        row=matched[0]
        cur,sc,marker=_scale(row.scale_context or row.excerpt, profile)
        if marker == "contradictory": exceptions.append(_exc(mid,"scale contradictory",r,"Contradictory scale markers found.",row.page)); continue
        if not sc: exceptions.append(_exc(mid,"scale missing",r,"No explicit permitted scale marker found in table context.",row.page)); continue
        if not cur: exceptions.append(_exc(mid,"currency missing",r,"No explicit permitted currency marker found in table context.",row.page)); continue
        if not row.section: exceptions.append(_exc(mid,"supporting excerpt unavailable",r,"No section/table context marker found.",row.page)); continue
        if not any(m in " ".join(row.headers).casefold() for m in current_markers): exceptions.append(_exc(mid,"period column not identified",r,"FY26/current-period column marker not identified.",row.page)); continue
        value=row.values[0]
        try: amount=_amount(value)
        except Exception: exceptions.append(_exc(mid,"amount ambiguous",r,f"Could not parse amount {value!r} safely.",row.page)); continue
        locator={"page":row.page,"section":row.section,"table":row.section,"row":row.label,"column":profile["reporting_period"],"scale_context":row.scale_context,"source_sha256":r.sha256}
        material={"enterprise_id":r.enterprise_id,"metric":mid,"period":r.reporting_period,"scope":profile["expected_scope"],"basis":metric["required_accounting_basis"],"state":metric["required_measurement_state"],"source_sha256":r.sha256,"source_locator":locator,"reported_amount":str(amount),"reported_scale":sc}
        cid=_candidate_id(material)
        if cid in seen: exceptions.append(_exc(mid,"duplicate candidate",r,"Duplicate deterministic candidate fingerprint.",row.page,locator)); continue
        seen.add(cid)
        candidates.append(FinancialFactCandidate(candidate_id=cid, enterprise_id=r.enterprise_id, source_id=r.source_id, source_locator=json.dumps(locator, sort_keys=True), source_page=row.page, source_method="deterministic_official_issuer_results_pdf", raw_metric_label=row.label, raw_value_text=value, reported_amount=amount, currency=cur, reported_scale=sc, raw_period_text=r.reporting_period, scope_text=profile["expected_scope"], accounting_basis_text=metric["required_accounting_basis"], measurement_state_text=metric["required_measurement_state"], supporting_excerpt=row.excerpt, extraction_confidence=95, source_hash=r.sha256 or "", extraction_version=EXTRACTION_VERSION, proposed_canonical_metric_id=mid, original_displayed_value=value, period_start=profile["period_start"], period_end=profile["period_end"], verification_status="candidate_unverified"))
    status="completed" if len(candidates)==3 else ("partial" if candidates else "failed_extraction")
    return RapidFinancialCandidateExtractionResult(status, receipt_ref, r.sha256, EXTRACTION_VERSION, len(candidates), tuple(candidates), len(exceptions), tuple(exceptions), tuple(p for p,_ in pages), matches, int((time.monotonic()-start)*1000))
