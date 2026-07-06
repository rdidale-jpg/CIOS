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
from .page_aware_pdf import parse_page_aware_pdf, ParsedPdfPage

EXTRACTION_VERSION = "rapid-core-candidates-v2-layout"
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
    diagnostics: dict[str, Any] | None = None
    ai_call_count: int = 0
    provider_cost: float = 0.0
    canonical_write_count: int = 0
    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "candidates": [c.to_dict() for c in self.candidates], "exceptions": [e.to_dict() for e in self.exceptions]}

@dataclass(frozen=True)
class _Row:
    page:int; section:str; scale_context:str; headers:tuple[str,...]; label:str; values:tuple[str,...]; excerpt:str; column_labels:tuple[str,...]=()

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

def _pdf_pages(path: Path) -> list[ParsedPdfPage]:
    parsed = parse_page_aware_pdf(path)
    if parsed.status != "parsed":
        raise RuntimeError(f"parser failure: {parsed.failure_class or parsed.status}")
    return [p for p in parsed.pages if p.text.strip()]

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

def _old_line_rows(pages: list[ParsedPdfPage], profile: dict[str,Any]) -> tuple[list[_Row], list[str]]:
    rows=[]; matches=[]; section_markers=[m.casefold() for m in profile.get("table_or_section_markers",())]
    for page in pages:
        lines=[re.sub(r"\s+", " ", l).strip() for l in page.text.splitlines() if l.strip()]
        section=""; headers=(); scale_context=""
        for line in lines:
            low=line.casefold()
            if any(m in low for m in section_markers): section=line; matches.append(line)
            if _scale(line, profile)[2]: scale_context=line
            if any(h.casefold() in low for h in profile.get("current_period_column_markers",())) and any(h.casefold() in low for h in profile.get("prior_period_column_markers",())):
                headers=tuple(re.split(r"\s{2,}|\|", line)) if "|" in line or re.search(r"\s{2,}", line) else tuple(line.split())
            if "|" in line:
                parts=[p.strip() for p in line.split("|")]
                if len(parts)>=3 and not any(h.casefold() in parts[0].casefold() for h in profile.get("current_period_column_markers",())):
                    rows.append(_Row(page.page_number, section, scale_context, headers, parts[0], tuple(parts[1:]), line, tuple(h.strip() for h in headers[1:])))
    return rows, tuple(dict.fromkeys(matches))

def _line_text(words): return " ".join(w.text for w in sorted(words, key=lambda w:(w.x0,w.word)))
def _mid_y(ws): return sum((w.y0+w.y1)/2 for w in ws)/len(ws)
def _y_bands(words, tolerance: float = 4.0):
    bands=[]
    for w in sorted(words, key=lambda w: ((w.y0+w.y1)/2, w.x0)):
        y=(w.y0+w.y1)/2
        for band in bands:
            if abs(band[0]-y) <= tolerance:
                band[1].append(w); band[0]=sum((x.y0+x.y1)/2 for x in band[1])/len(band[1]); break
        else:
            bands.append([y,[w]])
    return [(y, ws) for y, ws in bands]
def _geometric_rows(pages: list[ParsedPdfPage], profile: dict[str,Any]) -> tuple[list[_Row], list[str], dict[str,Any]]:
    rows=[]; matches=[]; diag={"layout_strategy":"word_geometry","pages_examined":[],"table_regions_found":[],"period_columns_found":[],"scale_markers_found":[],"normalized_labels_encountered":[],"metric_aliases_attempted":[],"statutory_adjusted_context_decisions":[],"rows_rejected":[]}
    markers=[m.casefold() for m in profile.get("table_or_section_markers",())]
    current=[m.casefold() for m in profile.get("current_period_column_markers",())]; prior=[m.casefold() for m in profile.get("prior_period_column_markers",())]
    aliases_for_diag=tuple(dict.fromkeys(a for m in profile.get("metric_definitions",()) for a in m.get("accepted_source_labels",())))
    diag["metric_aliases_attempted"] = list(aliases_for_diag)
    for page in pages:
        diag["pages_examined"].append(page.page_number)
        by_line={}
        for w in page.words: by_line.setdefault((w.block,w.line),[]).append(w)
        # Keep native lines for titles/scale, but reconstruct data rows from page-wide y-bands so labels split across spans/blocks are joined.
        lines=sorted(by_line.values(), key=lambda ws:(min(w.y0 for w in ws), min(w.x0 for w in ws)))
        section=""; scale_context=""; header_ws=None
        for ws in lines:
            txt=_line_text(ws); low=txt.casefold()
            if any(m in low for m in markers): section=txt; matches.append(txt); diag["table_regions_found"].append({"page":page.page_number,"title":txt[:120]})
            if _scale(txt, profile)[2]: scale_context=txt; diag["scale_markers_found"].append({"page":page.page_number,"marker":txt[:80]})
            if any(c in low for c in current) and any(p in low for p in prior): header_ws=ws
        if not header_ws:
            header_candidates=[w for w in page.words if w.text.casefold() in set(current+prior)]
            if header_candidates:
                ys=[round(((w.y0+w.y1)/2)/3)*3 for w in header_candidates]
                best=max(set(ys), key=ys.count)
                header_ws=[w for w,y in zip(header_candidates,ys) if y==best]
        if not header_ws: continue
        header_y=_mid_y(header_ws); cols=[]
        for w in sorted(header_ws, key=lambda w:w.x0):
            wt=w.text.casefold()
            if wt in current or wt in prior: cols.append((wt, (w.x0+w.x1)/2))
        if not any(c[0] in current for c in cols): continue
        diag["period_columns_found"].append({"page":page.page_number,"columns":[c[0] for c in cols]})
        left_edge=min(w.x0 for w in header_ws)
        label_words=[w for w in page.words if w.y0>header_y+2 and w.x0 < left_edge-10]
        val_words=[w for w in page.words if w.y0>header_y+2 and w.x0 >= left_edge-10]
        for y,lws in _y_bands(label_words):
            label=_line_text(lws); nlabel=_norm(label)
            is_known=any(_norm(a) in nlabel or nlabel in _norm(a) for m in profile.get("metric_definitions",()) for a in m.get("accepted_source_labels",()))
            is_rejected_decoy=label.casefold().startswith(("adjusted","segment"))
            if not label or not (is_known or is_rejected_decoy): continue
            vals=[]
            for col_label,cx in cols:
                aligned=[w for w in val_words if abs(((w.y0+w.y1)/2)-y)<=5 and abs(((w.x0+w.x1)/2)-cx)<=35]
                vals.append(_line_text(aligned))
            if any(vals):
                excerpt=(label+" | "+" | ".join(vals)).strip()
                diag["normalized_labels_encountered"].append({"page":page.page_number,"label":_norm(label)[:80]})
                diag["statutory_adjusted_context_decisions"].append({"page":page.page_number,"row":label[:80],"decision":"reject_adjusted_or_segment" if is_rejected_decoy else "candidate_statutory_group_row"})
                rows.append(_Row(page.page_number, section, scale_context, tuple(c[0] for c in cols), label, tuple(vals), excerpt, tuple(c[0] for c in cols)))
    return rows, tuple(dict.fromkeys(matches)), diag

def _extract_rows(pages: list[ParsedPdfPage], profile: dict[str,Any]) -> tuple[list[_Row], list[CandidateExtractionException], list[str], dict[str,Any]]:
    old_rows, old_matches = _old_line_rows(pages, profile)
    geo_rows, geo_matches, diag = _geometric_rows(pages, profile)
    diag["old_line_row_count"]=len(old_rows); diag["geometric_row_count"]=len(geo_rows)
    return old_rows + [r for r in geo_rows if (r.page,_norm(r.label)) not in {(o.page,_norm(o.label)) for o in old_rows}], [], tuple(dict.fromkeys(tuple(old_matches)+tuple(geo_matches))), diag

def _candidate_id(material: dict[str,Any]) -> str:
    return "RFC-"+hashlib.sha256(json.dumps(material, sort_keys=True, default=str).encode()).hexdigest()[:20].upper()

def extract_rapid_financial_candidates(acquired: AcquiredRapidSource, *, profile: dict[str,Any] | None=None, profile_path: Path | None=None) -> RapidFinancialCandidateExtractionResult:
    start=time.monotonic(); r=acquired.receipt; receipt_ref=r.to_dict(); profile=profile or json.loads((profile_path or (PROFILE_DIR / f"{r.enterprise_id.lower()}-{r.reporting_period.lower()}.json")).read_text())
    pre=_preconditions(r)
    if pre:
        ex=(_exc(None,"source precondition failed",r,"Rapid source receipt failed preconditions: "+", ".join(pre), retry=False, evidence="Accepted Slice 2A receipt with valid PDF parsing, identity, period, SHA-256 and bytes"),)
        return RapidFinancialCandidateExtractionResult("failed_precondition", receipt_ref, r.sha256, EXTRACTION_VERSION, 0, (), len(ex), ex, (), (), int((time.monotonic()-start)*1000), {})
    if r.sha256 and hashlib.sha256(acquired.path.read_bytes()).hexdigest()!=r.sha256:
        ex=(_exc(None,"source precondition failed",r,"Source receipt SHA-256 does not match acquired PDF bytes.", retry=False, evidence="Matching actual-byte receipt and acquired temporary source"),)
        return RapidFinancialCandidateExtractionResult("failed_precondition", receipt_ref, r.sha256, EXTRACTION_VERSION, 0, (), len(ex), ex, (), (), int((time.monotonic()-start)*1000), {})
    try: pages=_pdf_pages(acquired.path)
    except RuntimeError as e:
        ex=(_exc(None,"parser failure",r,str(e), retry=True, evidence="Parser-readable PDF text"),)
        return RapidFinancialCandidateExtractionResult("failed_extraction", receipt_ref, r.sha256, EXTRACTION_VERSION, 0, (), len(ex), ex, (), (), int((time.monotonic()-start)*1000), {})
    rows, exceptions, matches, diagnostics = _extract_rows(pages, profile)
    candidates=[]; seen=set()
    current_markers=[m.casefold() for m in profile.get("current_period_column_markers",())]
    for metric in profile.get("metric_definitions",()):
        mid=metric["proposed_canonical_metric_id"]; aliases=[_norm(a) for a in metric.get("accepted_source_labels",())]
        matched=[row for row in rows if _norm(row.label) in aliases]
        adjusted=[row for row in rows if _norm(row.label).startswith("adjusted ") and any(a in _norm(row.label) for a in aliases)]
        segment=[row for row in rows if "segment" in row.excerpt.casefold() and any(a in _norm(row.label) for a in aliases)]
        for row in adjusted:
            exceptions.append(_exc(mid,"adjusted value rejected",r,"Adjusted row is outside statutory Slice 2B-1 scope.",row.page,{"row":row.label},False,"Statutory row for the metric"))
            diagnostics.setdefault("rows_rejected", []).append({"metric":mid,"page":row.page,"row":row.label,"reason":"adjusted value rejected"})
        for row in segment:
            exceptions.append(_exc(mid,"segment value rejected",r,"Segment row is outside Group scope.",row.page,{"row":row.label},False,"Group consolidated row for the metric"))
            diagnostics.setdefault("rows_rejected", []).append({"metric":mid,"page":row.page,"row":row.label,"reason":"segment value rejected"})
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
        try:
            idx = [h.casefold() for h in (row.column_labels or row.headers)].index(profile["reporting_period"].casefold())
        except ValueError:
            idx = 0
        value=row.values[idx] if idx < len(row.values) else ""
        try: amount=_amount(value)
        except Exception: exceptions.append(_exc(mid,"amount ambiguous",r,f"Could not parse amount {value!r} safely.",row.page)); continue
        locator={"page":row.page,"section":row.section,"table":row.section,"row":row.label,"column":(row.column_labels[idx] if idx < len(row.column_labels) else profile["reporting_period"]),"scale_context":row.scale_context,"source_sha256":r.sha256}
        material={"enterprise_id":r.enterprise_id,"metric":mid,"period":r.reporting_period,"scope":profile["expected_scope"],"basis":metric["required_accounting_basis"],"state":metric["required_measurement_state"],"source_sha256":r.sha256,"source_locator":locator,"reported_amount":str(amount),"reported_scale":sc}
        cid=_candidate_id(material)
        if cid in seen: exceptions.append(_exc(mid,"duplicate candidate",r,"Duplicate deterministic candidate fingerprint.",row.page,locator)); continue
        seen.add(cid)
        candidates.append(FinancialFactCandidate(candidate_id=cid, enterprise_id=r.enterprise_id, source_id=r.source_id, source_locator=json.dumps(locator, sort_keys=True), source_page=row.page, source_method="deterministic_official_issuer_results_pdf", raw_metric_label=row.label, raw_value_text=value, reported_amount=amount, currency=cur, reported_scale=sc, raw_period_text=r.reporting_period, scope_text=profile["expected_scope"], accounting_basis_text=metric["required_accounting_basis"], measurement_state_text=metric["required_measurement_state"], supporting_excerpt=row.excerpt, extraction_confidence=95, source_hash=r.sha256 or "", extraction_version=EXTRACTION_VERSION, proposed_canonical_metric_id=mid, original_displayed_value=value, period_start=profile["period_start"], period_end=profile["period_end"], verification_status="candidate_unverified"))
    status="completed" if len(candidates)==3 else ("partial" if candidates else "failed_extraction")
    # Bound support diagnostics and consolidate duplicate row/reason entries.
    dedup=[]; keys=set()
    for item in diagnostics.get("rows_rejected", []):
        key=(item.get("metric"), item.get("page"), item.get("row"), item.get("reason"))
        if key not in keys: keys.add(key); dedup.append(item)
    diagnostics["rows_rejected"] = dedup
    diagnostics["candidate_count"] = len(candidates)
    diagnostics["extraction_status"] = status
    return RapidFinancialCandidateExtractionResult(status, receipt_ref, r.sha256, EXTRACTION_VERSION, len(candidates), tuple(candidates), len(exceptions), tuple(exceptions), tuple(p.page_number for p in pages), matches, int((time.monotonic()-start)*1000), diagnostics)
