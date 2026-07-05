"""Section-aware, low-cost annual report packet extraction for Flora."""
from __future__ import annotations

import base64, hashlib, json, logging, re, time, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir
from cios.applications.flora.live.documents import DocumentPage
from .pdf_document_adapter import CanonicalPdfPage, load_canonical_pdf_document, useful_for_keyword_selection
from .instructions import EXTRACTION_INSTRUCTIONS
from .schema import ExperimentDocument, ExtractionRun, FoundationFactSet, ProviderFoundationFactSet, now_iso, openai_strict_json_schema
from .candidate_validation import parse_foundation_fact_candidates
from .config import financial_intelligence_settings

TARGET_INPUT_TOKENS = 50_000
ABSOLUTE_INPUT_TOKEN_CEILING = 75_000
MAX_BT_GOLDEN_CALLS = 4
PACKET_MAX_OUTPUT_TOKENS = 2_000
MATERIAL_FACT_LIMIT = 15

LOGGER = logging.getLogger('flora.financial_intelligence')

STRONG_HEADING_TERMS = (
    'financial highlights','group financial review','financial review','group income statement','income statement',
    'group balance sheet','balance sheet','cash flow statement','cash-flow statement','alternative performance measures',
    'segment performance','outlook','guidance','cost transformation','savings programme'
)
SECTION_TERMS = (
    'financial highlights','group income statement','group balance sheet','cash flow statement','cash-flow statement',
    'segment performance','revenue','adjusted ebitda','operating profit','capital expenditure','capex',
    'free cash flow','normalised free cash flow','net debt','outlook','guidance','cost transformation','cost savings','savings commitments',
    'financial performance','operating costs','cost reduction','cost-reduction','cost efficiencies','income statement','balance sheet','alternative performance measures','savings programme'
)
GENERIC_TERMS = ('annual report','company','performance','strategy')
COVER_ONLY_TERMS = ('annual report', 'strategic report', 'report 2026', 'bt group plc')

@dataclass(frozen=True)
class CanonicalPage:
    internal_index: int
    pdf_page_number: int
    printed_page_number: str | None
    text: str
    heading_candidates: tuple[str, ...]
    character_count: int
    source_document_id: str
    extraction_method: str = 'embedded_text'
    text_blocks: tuple[str, ...] = ()
    printable_character_ratio: float = 1.0
    alphanumeric_ratio: float = 0.5
    extraction_quality_score: float = 0.5

@dataclass(frozen=True)
class PageCandidate:
    page_number: int
    score: int
    matched_terms: tuple[str, ...]
    text: str
    matched_headings: tuple[str, ...] = ()
    reason: str = ''

@dataclass(frozen=True)
class PagePacket:
    packet_id: str
    page_numbers: tuple[int, ...]
    text: str
    packet_hash: str
    pdf_bytes: bytes = b''
    packet_page_to_original: dict[int, int] | None = None
    byte_size: int = 0
    page_count: int = 0
    input_mode: str = 'text_only'


def stable_document_hash(document: ExperimentDocument) -> str:
    return document.checksum or hashlib.sha256((document.source_url + document.document_id).encode()).hexdigest()


def _normalise_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def _heading_candidates(text: str) -> tuple[str, ...]:
    lines = [re.sub(r'\s+', ' ', line).strip() for line in (text or '').splitlines()]
    heads: list[str] = []
    for line in lines[:18]:
        if 4 <= len(line) <= 96 and not re.search(r'[.!?]$', line):
            heads.append(line)
    if not heads and text:
        heads.append(_normalise_text(text)[:96])
    return tuple(heads[:5])


def _printed_page_number(text: str) -> str | None:
    for pat in (r'\b(?:page|p\.)\s+(\d{1,3})\b', r'^\s*(\d{1,3})\s*$'):
        m = re.search(pat, text or '', re.I | re.M)
        if m:
            return m.group(1)
    return None


def canonicalise_pages(pages: Iterable[DocumentPage], document: ExperimentDocument | None = None) -> list[CanonicalPage]:
    canonical: list[CanonicalPage] = []
    doc_id = document.document_id if document else 'unknown-document'
    for idx, page in enumerate(pages):
        raw = getattr(page, 'text', '') or getattr(page, 'content', '') or ''
        text = _normalise_text(raw)
        pdf_page = int(getattr(page, 'page_number', idx + 1) or idx + 1)
        canonical.append(CanonicalPage(idx, pdf_page, _printed_page_number(raw), text, _heading_candidates(raw), len(raw), doc_id, getattr(page, 'extraction_method', 'embedded_text'), ((text,) if text else ()), 1.0 if raw else 0.0, 0.5 if raw else 0.0, 0.5 if raw else 0.0))
    return canonical


def page_parse_diagnostics(pages: Iterable[DocumentPage], document: ExperimentDocument | None = None) -> dict[str, Any]:
    canonical = canonicalise_pages(pages, document)
    counts = [p.character_count for p in canonical]
    sorted_counts = sorted(counts)
    median = sorted_counts[len(sorted_counts)//2] if sorted_counts else 0
    printed_differs = any(p.printed_page_number and p.printed_page_number.isdigit() and int(p.printed_page_number) != p.pdf_page_number for p in canonical)
    toc = any('contents' in p.text.casefold() or 'table of contents' in p.text.casefold() for p in canonical)
    return {'total_pdf_page_count': document.page_count if document else len(canonical), 'parser_used': canonical[0].extraction_method if canonical else 'unknown', 'pages_with_extractable_text': sum(1 for p in canonical if p.text), 'total_extracted_character_count': sum(counts), 'min_characters_per_page': min(counts) if counts else 0, 'max_characters_per_page': max(counts) if counts else 0, 'median_characters_per_page': median, 'zero_character_pages': [p.pdf_page_number for p in canonical if not p.text], 'toc_or_bookmark_available': toc, 'first_five_non_empty_page_samples': [{'page_number': p.pdf_page_number, 'headings': list(p.heading_candidates[:2]), 'sample': p.text[:160]} for p in canonical if p.text][:5], 'printed_page_numbers_differ': printed_differs}


def _score_page(page: CanonicalPage) -> PageCandidate | None:
    if getattr(page, 'printable_character_ratio', 1.0) < .70 or getattr(page, 'alphanumeric_ratio', .5) < .18 or getattr(page, 'character_count', len(page.text)) < 30:
        return None
    lower = page.text.casefold()
    matched_terms = tuple(t for t in SECTION_TERMS if t in lower)
    matched_headings = tuple(h for h in page.heading_candidates if any(t in h.casefold() for t in STRONG_HEADING_TERMS))
    numeric = len(re.findall(r'(?:£|gbp|bn|m\b|%)', lower))
    toc_only = ('contents' in lower or 'table of contents' in lower) and numeric < 3 and not matched_headings
    generic_only = any(t in lower for t in GENERIC_TERMS) and not (matched_terms or matched_headings or numeric >= 3)
    if generic_only or toc_only:
        return None
    score = len(matched_terms) * 10 + len(matched_headings) * 25 + min(numeric, 12)
    if not (matched_terms or matched_headings or numeric >= 3) or score < 10:
        return None
    bits = []
    if matched_headings: bits.append('strong financial heading')
    if matched_terms: bits.append('matched financial terms: ' + ', '.join(matched_terms[:6]))
    if numeric >= 3: bits.append('numeric financial evidence')
    return PageCandidate(page.pdf_page_number, score, matched_terms, page.text, matched_headings, '; '.join(bits))


def _fallback_candidates(canonical: list[CanonicalPage], *, max_pages: int) -> list[PageCandidate]:
    starts: set[int] = set()
    for page in canonical:
        lower = page.text.casefold()
        if 'contents' in lower or 'table of contents' in lower:
            for m in re.finditer(r'(financial review|financial highlights|income statement|balance sheet|cash.?flow|outlook|guidance|alternative performance measures)', lower):
                starts.add(page.internal_index)
        if any(t in lower for t in STRONG_HEADING_TERMS):
            starts.add(page.internal_index)
    window = sorted({i for s in starts for i in range(max(0, s-1), min(len(canonical), s+4))})[:max_pages]
    out = [c for i in window if (c := _score_page(canonical[i]))]
    return sorted(out, key=lambda c: (-c.score, c.page_number))[:max_pages]


def select_candidate_pages(pages: Iterable[DocumentPage] | Iterable[CanonicalPage], *, max_pages: int = 24) -> list[PageCandidate]:
    raw = list(pages)
    canonical = raw if raw and isinstance(raw[0], CanonicalPage) else canonicalise_pages(raw)  # type: ignore[arg-type]
    candidates = [c for p in canonical if (c := _score_page(p))]
    candidates.sort(key=lambda c: (-c.score, c.page_number))
    if not candidates:
        candidates = _fallback_candidates(list(canonical), max_pages=max_pages)
    return sorted(candidates[:max_pages], key=lambda c: c.page_number)

def build_page_packets(candidates: list[PageCandidate], *, max_packets: int = MAX_BT_GOLDEN_CALLS) -> list[PagePacket]:
    if not candidates:
        return []
    buckets: list[list[PageCandidate]] = [[] for _ in range(min(max_packets, len(candidates)))]
    for idx, candidate in enumerate(candidates):
        buckets[idx % len(buckets)].append(candidate)
    packets: list[PagePacket] = []
    for idx, bucket in enumerate(buckets, 1):
        bucket = sorted(bucket, key=lambda c: c.page_number)
        text = '\n\n'.join(f"ORIGINAL PDF PAGE {c.page_number}\n{c.text}" for c in bucket)
        pages = tuple(c.page_number for c in bucket)
        digest = hashlib.sha256((json.dumps(pages) + text).encode()).hexdigest()
        packets.append(PagePacket(f'packet-{idx}', pages, text, digest))
    return packets




def _contiguous_ranges(candidates: list[PageCandidate], page_count: int, *, before: int = 0, after: int = 3, max_packets: int = MAX_BT_GOLDEN_CALLS) -> list[tuple[int, int]]:
    starts = sorted({max(1, min(page_count, c.page_number)) for c in candidates})[:max_packets]
    ranges: list[tuple[int, int]] = []
    for start in starts:
        lo, hi = max(1, start - before), min(page_count, start + after)
        if ranges and lo <= ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], hi))
        else:
            ranges.append((lo, hi))
    return ranges[:max_packets]

def _copy_pdf_pages(source_path: Path, page_numbers: tuple[int, ...]) -> tuple[bytes, dict[int, int]]:
    import fitz  # type: ignore
    if not source_path.is_file():
        raise FileNotFoundError('packet_content_unavailable: original PDF unavailable')
    with fitz.open(str(source_path)) as src:
        if src.page_count <= 0:
            raise ValueError('packet_content_unavailable: source PDF has zero pages')
        missing = [p for p in page_numbers if p < 1 or p > src.page_count]
        if missing:
            raise ValueError(f'packet_content_unavailable: selected original pages absent: {missing}')
        out = fitz.open()
        for pno in page_numbers:
            out.insert_pdf(src, from_page=pno - 1, to_page=pno - 1)
        data = out.tobytes(garbage=4, deflate=True)
        out.close()
    mapping = {i + 1: p for i, p in enumerate(page_numbers)}
    validate_packet_pdf_bytes(data, page_numbers)
    return data, mapping

def validate_packet_pdf_bytes(pdf_bytes: bytes, original_pages: tuple[int, ...]) -> None:
    if not pdf_bytes:
        raise ValueError('packet_content_unavailable: packet PDF byte size is zero')
    if not original_pages:
        raise ValueError('packet_content_unavailable: packet contains zero selected original pages')
    import fitz  # type: ignore
    with fitz.open(stream=pdf_bytes, filetype='pdf') as doc:
        if doc.page_count <= 0:
            raise ValueError('packet_content_unavailable: packet PDF page count is zero')
        if doc.page_count != len(original_pages):
            raise ValueError('packet_content_unavailable: packet page count does not match selected original pages')

def build_real_page_packets(candidates: list[PageCandidate], document: ExperimentDocument, *, max_packets: int = MAX_BT_GOLDEN_CALLS) -> list[PagePacket]:
    if not candidates:
        return []
    source_path = Path(document.local_path) if document.local_path else Path()
    ranges = _contiguous_ranges(candidates, int(document.page_count or 0) or max(c.page_number for c in candidates), max_packets=max_packets)
    packets: list[PagePacket] = []
    for idx, (start, end) in enumerate(ranges, 1):
        pages = tuple(range(start, end + 1))
        pdf_bytes, mapping = _copy_pdf_pages(source_path, pages)
        text = f"Packet page to original PDF page map: {json.dumps(mapping, sort_keys=True)}"
        digest = hashlib.sha256(pdf_bytes + json.dumps(mapping, sort_keys=True).encode()).hexdigest()
        packets.append(PagePacket(f'packet-{idx}', pages, text, digest, pdf_bytes, mapping, len(pdf_bytes), len(pages), 'file_data'))
    return packets

def _support_reference(correlation_id: str) -> str:
    ref = 'FI-' + str(correlation_id or uuid.uuid4().hex).replace('FI-', '').replace('fi-', '')
    return ref if ref != 'FI-' else 'FI-' + uuid.uuid4().hex[:12]


def _packet_event(event: str, *, correlation_id: str, packet: PagePacket, reasons: dict[int, list[str]], input_tokens: int | None, model: str, started: float, provider_status: str | None = None, provider_error: str | None = None, candidate_count: int = 0, valid_count: int = 0, quarantined_count: int = 0) -> dict[str, Any]:
    payload = {
        'event': event,
        'request_stage': event,
        'support_reference': _support_reference(correlation_id),
        'correlation_id': correlation_id,
        'packet_id': packet.packet_id,
        'page_numbers': list(packet.page_numbers),
        'page_selection_reasons': {str(p): reasons.get(p, []) for p in packet.page_numbers},
        'input_tokens': input_tokens,
        'model': model,
        'requested_model': model,
        'elapsed_time': round(time.time() - started, 3),
        'provider_status': provider_status,
        'provider_error': provider_error,
        'candidate_facts_returned': candidate_count,
        'valid_facts': valid_count,
        'quarantined_facts': quarantined_count,
    }
    LOGGER.error('Flora packet diagnostic ' + json.dumps(payload, sort_keys=True))
    return payload

def packet_cache_path(document_hash: str, packet_hash: str, model: str) -> Path:
    return data_path('ai_financial_reports', 'packet_cache', document_hash, f'{model}-{packet_hash}.json')


def _packet_payload(provider: Any, document: ExperimentDocument, packet: PagePacket, schema: type[FoundationFactSet]) -> dict[str, Any]:
    if not packet.pdf_bytes or packet.page_count <= 0 or packet.input_mode != 'file_data':
        raise ValueError('packet_content_unavailable: packet has no PDF bytes; refusing text-only placeholder')
    mapping = packet.packet_page_to_original or {i + 1: p for i, p in enumerate(packet.page_numbers)}
    encoded = base64.b64encode(packet.pdf_bytes).decode('ascii')
    instructions = (
        EXTRACTION_INSTRUCTIONS
        + '\n\nReturn no more than 15 material, atomic facts across revenue, adjusted EBITDA, operating profit, capital expenditure, normalised free cash flow, net debt, cost savings, financial outlook, and material segment movement. Every fact must cite ORIGINAL PDF PAGE numbers present in this packet map. Packet page to original PDF page map: '
        + json.dumps(mapping, sort_keys=True)
    ).strip()
    return {
        'model': provider.model,
        'input': [{'role': 'user', 'content': [
            {'type': 'input_file', 'filename': f'{packet.packet_id}.pdf', 'file_data': f'data:application/pdf;base64,{encoded}'},
            {'type': 'input_text', 'text': f"Document: {document.title}\nOriginal PDF pages in packet: {', '.join(map(str, packet.page_numbers))}\nPacket hash: {packet.packet_hash}"},
            {'type': 'input_text', 'text': instructions},
        ]}],
        'reasoning': {'effort': provider.reasoning_effort},
        'text': {'format': {'type': 'json_schema', 'name': 'foundation_fact_set', 'schema': openai_strict_json_schema(schema), 'strict': True}},
    }

def count_packet_input_tokens(client: Any, provider: Any, document: ExperimentDocument, packet: PagePacket, schema: type[FoundationFactSet]) -> int:
    payload = _packet_payload(provider, document, packet, schema)
    counter = getattr(getattr(client, 'responses', None), 'input_tokens', None)
    result = counter.count(**payload)
    return int(getattr(result, 'input_tokens', None) or getattr(result, 'tokens', None) or (result.get('input_tokens') if isinstance(result, dict) else 0))


def split_oversized_packet(packet: PagePacket) -> list[PagePacket]:
    if len(packet.page_numbers) <= 1:
        return [packet]
    mid = len(packet.page_numbers) // 2
    pages_a = set(packet.page_numbers[:mid]); pages_b = set(packet.page_numbers[mid:])
    def part(pages: set[int], suffix: str) -> PagePacket:
        chunks = re.split(r'(?=ORIGINAL PDF PAGE \d+)', packet.text)
        text = '\n'.join(c for c in chunks if any(c.startswith(f'ORIGINAL PDF PAGE {p}') for p in pages))
        digest = hashlib.sha256((json.dumps(sorted(pages)) + text).encode()).hexdigest()
        return PagePacket(packet.packet_id + suffix, tuple(sorted(pages)), text, digest)
    return [part(pages_a, 'a'), part(pages_b, 'b')]



def _quarantine_ungrounded_facts(facts: list[Any], exceptions: list[dict[str, Any]], packet: PagePacket) -> list[Any]:
    allowed = set(packet.page_numbers)
    valid: list[Any] = []
    for idx, fact in enumerate(facts):
        excerpt = (getattr(fact, 'source_excerpt', '') or '').strip()
        start = int(getattr(fact, 'source_page_start', 0) or 0)
        end = int(getattr(fact, 'source_page_end', start) or start)
        if not excerpt or start not in allowed or end not in allowed:
            exceptions.append({'exception_type':'candidate_fact_validation_failed','packet_id':packet.packet_id,'candidate_index':idx,'original_page_reference':start,'validation_failure_category':'evidence_grounding_failed','safe_explanation':'Returned fact page is outside the packet map or lacks supporting excerpt/context.','machine_candidate': fact.model_dump(mode='json') if hasattr(fact, 'model_dump') else {}})
        else:
            valid.append(fact)
    return valid

def merge_packet_facts(runs: list[ExtractionRun], document: ExperimentDocument) -> FoundationFactSet:
    seen: set[tuple[Any, ...]] = set(); facts = []
    for run in runs:
        for fact in run.facts:
            if fact.source_page_start < 1 or fact.source_page_end > document.page_count:
                continue
            key = (str(fact.claim_type), fact.predicate.casefold(), fact.business_unit or fact.subject_name, fact.period_label, fact.value_number, fact.value_text, fact.unit, fact.currency, str(fact.state))
            if key in seen:
                continue
            seen.add(key); facts.append(fact)
            if len(facts) >= MATERIAL_FACT_LIMIT:
                return FoundationFactSet(facts=facts)
    return FoundationFactSet(facts=facts)


def visual_navigation_plan(document: ExperimentDocument, canonical_doc: Any) -> dict[str, Any]:
    """Bounded visual-navigation boundary used only when text extraction is unusable.

    Production deployments may replace this deterministic conservative plan with a
    low-resolution thumbnail call to the configured low-cost model. The returned
    ranges always use original one-based PDF page numbers.
    """
    page_count = max(int(document.page_count or len(getattr(canonical_doc, 'pages', ()) or []) or 1), 1)
    # Bounded, generic annual-report navigation windows; not company-specific and
    # capped so packet extraction remains limited.
    anchors = sorted({max(1, min(page_count, p)) for p in (8, max(1, page_count//3), max(1, page_count//2), max(1, int(page_count*.72)))})[:MAX_BT_GOLDEN_CALLS]
    types = ['contents_or_highlights', 'financial_review', 'financial_statements', 'outlook_guidance']
    ranges=[]
    for i, page in enumerate(anchors):
        ranges.append({'section_title': types[min(i, len(types)-1)].replace('_',' ').title(), 'section_type': types[min(i, len(types)-1)], 'start_pdf_page': page, 'end_pdf_page': min(page_count, page+2), 'confidence': 55, 'visual_evidence_page': min(page, 20)})
    return {'visual_fallback_used': True, 'model': financial_intelligence_settings().model, 'stage_a_pages': list(range(1, min(page_count, 20)+1)), 'contents_pages_found': [], 'selected_ranges': ranges, 'model_calls': 0}


class SectionAwareOpenAIProvider:
    def __init__(self, base_provider: Any):
        self.base_provider = base_provider
        self.model = base_provider.model
        self.reasoning_effort = 'none'
        self.max_output_tokens = min(int(getattr(base_provider, 'max_output_tokens', PACKET_MAX_OUTPUT_TOKENS)), PACKET_MAX_OUTPUT_TOKENS)
        self.settings = financial_intelligence_settings()

    def extract_packets(self, document: ExperimentDocument, pages: Iterable[DocumentPage], schema: type[ProviderFoundationFactSet] = ProviderFoundationFactSet, correlation_id: str | None = None) -> tuple[ExtractionRun, dict[str, Any]]:
        correlation_id = correlation_id or uuid.uuid4().hex
        page_list = list(pages)
        canonical_doc = load_canonical_pdf_document(document, page_list)
        parse_diag = canonical_doc.quality_metrics
        LOGGER.error('Flora PDF parse diagnostics ' + json.dumps({'support_reference': _support_reference(correlation_id), 'correlation_id': correlation_id, **parse_diag}, sort_keys=True))
        canonical_pages = list(canonical_doc.pages)
        if not useful_for_keyword_selection(canonical_doc) and int(document.page_count or 0) >= 20:
            visual_plan = visual_navigation_plan(document, canonical_doc)
            candidates = [PageCandidate(int(r['start_pdf_page']), int(r.get('confidence', 50)), (str(r.get('section_type','financial')),), f"Visual navigation selected {r.get('section_title','financial section')} on original PDF page {r['start_pdf_page']}", (str(r.get('section_title','financial section')),), 'visual navigation fallback; original PDF page number preserved') for r in visual_plan.get('selected_ranges', [])]
        else:
            visual_plan = {'visual_fallback_used': False, 'selected_ranges': []}
            candidates = select_candidate_pages(canonical_pages)
        page_reasons = {c.page_number: ([c.reason] if c.reason else list(c.matched_terms)) + ([f'numeric financial evidence'] if re.search(r'(?:£|gbp|bn|m\b|%)', c.text.casefold()) else []) for c in candidates}
        LOGGER.error('Flora selected financial pages ' + json.dumps({'support_reference': _support_reference(correlation_id), 'correlation_id': correlation_id, 'candidate_pages': [{'page_number': c.page_number, 'score': c.score, 'matched_headings': list(c.matched_headings), 'matched_financial_terms': list(c.matched_terms), 'selection_reason': c.reason, 'reasons': page_reasons.get(c.page_number, [])} for c in candidates]}, sort_keys=True))
        try:
            packets = build_real_page_packets(candidates, document)
        except Exception as exc:
            LOGGER.exception('Financial Intelligence packet construction failed support_reference=%s', _support_reference(correlation_id))
            exc_payload = {'exception_type':'packet_content_unavailable','failure_stage':'preparing_packets','support_reference':_support_reference(correlation_id),'rejection_reason':f'{type(exc).__name__}: {exc}','user_message':'Flora could not prepare the selected PDF pages for analysis.'}
            final = ExtractionRun(run_id=correlation_id, route='openai-responses-section-packets', provider='openai', model=self.model, model_version=self.model, status='packet_content_unavailable', started_at=now_iso(), completed_at=now_iso(), latency_seconds=0, usage={'input_tokens':0,'output_tokens':0}, facts=[], candidate_exceptions=[exc_payload], diagnostics=[exc_payload | {'openai_invoked':False}])
            return final, {'candidate_pages': [], 'packets': [], 'packet_count': 0, 'openai_calls': 0, 'document_hash': stable_document_hash(document), 'parse_diagnostics': parse_diag, 'fallback_used': True, 'visual_navigation': locals().get('visual_plan', {'visual_fallback_used': False})}

        doc_hash = stable_document_hash(document)
        runs: list[ExtractionRun] = []; packet_records=[]; total_usage={'input_tokens':0,'output_tokens':0}; openai_calls=0; packet_failures=[]
        if not packets:
            exc = {'exception_type':'section_selection_failed','failure_stage':'selecting_sections','support_reference':_support_reference(correlation_id),'user_message':'Flora could not identify the financial sections in this report.','rejection_reason':'No relevant financial pages selected; no paid model request occurred.'}
            final = ExtractionRun(run_id=correlation_id, route='openai-responses-section-packets', provider='openai', model=self.model, model_version=self.model, status='section_selection_failed', started_at=now_iso(), completed_at=now_iso(), latency_seconds=0, usage={'input_tokens':0,'output_tokens':0}, facts=[], candidate_exceptions=[exc], diagnostics=[{'event':'section_selection_failed','request_stage':'selecting_sections','support_reference':_support_reference(correlation_id),'correlation_id':correlation_id,'openai_invoked':False,'no_paid_model_request':True}])
            return final, {'candidate_pages': [], 'packets': [], 'packet_count': 0, 'openai_calls': 0, 'document_hash': stable_document_hash(document), 'parse_diagnostics': parse_diag, 'fallback_used': True, 'visual_navigation': locals().get('visual_plan', {'visual_fallback_used': False})}
        OpenAI = __import__('openai', fromlist=['OpenAI']).OpenAI
        client = OpenAI(timeout=getattr(self.base_provider, 'timeout_seconds', 120), max_retries=getattr(self.base_provider, 'max_retries', 0))
        queue = list(packets)
        while queue and openai_calls < MAX_BT_GOLDEN_CALLS:
            packet = queue.pop(0)
            cache_path = packet_cache_path(doc_hash, packet.packet_hash, self.model)
            if cache_path.is_file():
                run = ExtractionRun.model_validate(json.loads(cache_path.read_text()))
                runs.append(run); packet_records.append({'packet_id': packet.packet_id, 'page_numbers': packet.page_numbers, 'packet_hash': packet.packet_hash, 'cached': True, 'input_tokens': run.usage.get('input_tokens',0), 'packet_byte_size': packet.byte_size, 'packet_page_count': packet.page_count, 'input_mode': packet.input_mode})
                continue
            started = time.time(); diagnostics=[]; input_tokens = None
            diagnostics.append(_packet_event('packet_selected', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started))
            try:
                diagnostics.append(_packet_event('packet_preflight_started', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started))
                input_tokens = count_packet_input_tokens(client, self, document, packet, schema)
                diagnostics.append(_packet_event('packet_preflight_completed', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started, provider_status='completed'))
                if input_tokens > ABSOLUTE_INPUT_TOKEN_CEILING:
                    queue = split_oversized_packet(packet) + queue
                    continue
                payload = _packet_payload(self, document, packet, schema) | {'max_output_tokens': self.max_output_tokens}
                diagnostics.append(_packet_event('packet_model_request_started', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started))
                resp = client.responses.create(**payload); openai_calls += 1
                raw = resp.model_dump(mode='json') if hasattr(resp, 'model_dump') else resp
                diagnostics.append(_packet_event('packet_model_request_completed', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started, provider_status='completed'))
                diagnostics.append(_packet_event('packet_response_validation_started', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started))
                parsed, candidate_exceptions, parse_status = parse_foundation_fact_candidates(getattr(resp, 'output_text', '') or raw.get('output_text', '{}'), packet_id=packet.packet_id, provider='openai', model=self.model, request_id=raw.get('id'))
                parsed_facts = _quarantine_ungrounded_facts(list(parsed.facts), candidate_exceptions, packet)
                parsed = FoundationFactSet(facts=parsed_facts)
                if parsed.facts and candidate_exceptions:
                    parse_status = 'completed_with_exceptions'
                elif candidate_exceptions and not parsed.facts:
                    parse_status = 'provider_response_invalid'
                candidate_count = len(parsed.facts) + len(candidate_exceptions)
                diagnostics.append(_packet_event('packet_response_validation_completed', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started, provider_status=parse_status, candidate_count=candidate_count, valid_count=len(parsed.facts), quarantined_count=len(candidate_exceptions)))
                usage = raw.get('usage') or {}
                usage = usage | {'input_tokens': int(usage.get('input_tokens') or input_tokens), 'planned_output_allowance': self.max_output_tokens, 'tpm_reservation': input_tokens + self.max_output_tokens}
                total_usage['input_tokens'] += usage['input_tokens']; total_usage['output_tokens'] += int(usage.get('output_tokens') or 0)
                run = ExtractionRun(run_id=f'{correlation_id}-{packet.packet_id}', route='openai-responses-section-packet', provider='openai', model=self.model, model_version=self.model, status=parse_status, request_id=raw.get('id'), started_at=now_iso(), completed_at=now_iso(), latency_seconds=round(time.time()-started,3), usage=usage, facts=parsed.facts, candidate_exceptions=candidate_exceptions, diagnostics=diagnostics)
                ensure_writable_dir(cache_path.parent); atomic_write_json(cache_path, run.model_dump(mode='json'))
                runs.append(run); packet_records.append({'packet_id': packet.packet_id, 'page_numbers': packet.page_numbers, 'page_selection_reasons': {str(p): page_reasons.get(p, []) for p in packet.page_numbers}, 'packet_hash': packet.packet_hash, 'cached': False, 'input_tokens': input_tokens, 'packet_byte_size': packet.byte_size, 'packet_page_count': packet.page_count, 'input_mode': packet.input_mode, 'packet_page_to_original': packet.packet_page_to_original, 'status': parse_status, 'valid_facts': len(parsed.facts), 'quarantined_facts': len(candidate_exceptions)})
            except Exception as exc:
                LOGGER.exception('Unexpected Financial Intelligence packet exception support_reference=%s packet_id=%s', _support_reference(correlation_id), packet.packet_id)
                failure = _packet_event('packet_failed', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started, provider_status='failed', provider_error=f'{type(exc).__name__}: {exc}')
                diagnostics.append(failure); packet_failures.append({'exception_type':'packet_failed','failure_stage': diagnostics[-2].get('event') if len(diagnostics)>1 else 'packet_selected','packet_id':packet.packet_id,'support_reference':_support_reference(correlation_id),'rejection_reason':failure['provider_error'],'user_message':'A financial section could not be analysed.'})
                run = ExtractionRun(run_id=f'{correlation_id}-{packet.packet_id}', route='openai-responses-section-packet', provider='openai', model=self.model, model_version=self.model, status='provider_request_failed', started_at=now_iso(), completed_at=now_iso(), latency_seconds=round(time.time()-started,3), usage={'input_tokens': input_tokens or 0}, facts=[], candidate_exceptions=[packet_failures[-1]], diagnostics=diagnostics)
                runs.append(run); packet_records.append({'packet_id': packet.packet_id, 'page_numbers': packet.page_numbers, 'page_selection_reasons': {str(p): page_reasons.get(p, []) for p in packet.page_numbers}, 'packet_hash': packet.packet_hash, 'cached': False, 'input_tokens': input_tokens, 'packet_byte_size': packet.byte_size, 'packet_page_count': packet.page_count, 'input_mode': packet.input_mode, 'packet_page_to_original': packet.packet_page_to_original, 'status': 'provider_request_failed', 'valid_facts': 0, 'quarantined_facts': 0})
                continue
        merged = merge_packet_facts(runs, document)
        if any(r.candidate_exceptions for r in runs) and merged.facts:
            final_status = 'completed_with_exceptions'
        elif packet_failures and not merged.facts:
            final_status = 'provider_request_failed'
        elif runs and not merged.facts and any(r.candidate_exceptions for r in runs):
            final_status = 'provider_response_invalid'
        else:
            final_status = 'completed'
        final = ExtractionRun(run_id=correlation_id, route='openai-responses-section-packets', provider='openai', model=self.model, model_version=self.model, status=final_status, started_at=now_iso(), completed_at=now_iso(), latency_seconds=0, usage=total_usage, facts=merged.facts, candidate_exceptions=[e for r in runs for e in r.candidate_exceptions], diagnostics=[d for r in runs for d in r.diagnostics])
        return final, {'candidate_pages': [{'page_number': c.page_number, 'score': c.score, 'matched_headings': list(c.matched_headings), 'matched_financial_terms': list(c.matched_terms), 'selection_reason': c.reason, 'reasons': page_reasons.get(c.page_number, [])} for c in candidates], 'packets': packet_records, 'packet_count': len(packet_records), 'openai_calls': openai_calls, 'document_hash': doc_hash, 'parse_diagnostics': parse_diag, 'fallback_used': False, 'visual_navigation': visual_plan}
