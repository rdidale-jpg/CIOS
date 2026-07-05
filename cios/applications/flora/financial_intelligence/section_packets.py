"""Section-aware, low-cost annual report packet extraction for Flora."""
from __future__ import annotations

import hashlib, json, logging, re, time, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir
from cios.applications.flora.live.documents import DocumentPage
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

SECTION_TERMS = (
    'financial highlights','group income statement','group balance sheet','cash flow statement','cash-flow statement',
    'segment performance','revenue','adjusted ebitda','operating profit','capital expenditure','capex',
    'free cash flow','normalised free cash flow','net debt','outlook','guidance','cost transformation','cost savings','savings commitments',
    'financial performance','operating costs','cost reduction','cost-reduction','cost efficiencies'
)
COVER_ONLY_TERMS = ('annual report', 'strategic report', 'report 2026', 'bt group plc')

@dataclass(frozen=True)
class PageCandidate:
    page_number: int
    score: int
    matched_terms: tuple[str, ...]
    text: str

@dataclass(frozen=True)
class PagePacket:
    packet_id: str
    page_numbers: tuple[int, ...]
    text: str
    packet_hash: str


def stable_document_hash(document: ExperimentDocument) -> str:
    return document.checksum or hashlib.sha256((document.source_url + document.document_id).encode()).hexdigest()


def select_candidate_pages(pages: Iterable[DocumentPage], *, max_pages: int = 24) -> list[PageCandidate]:
    candidates: list[PageCandidate] = []
    for page in pages:
        text = page.text or ''
        lower = text.casefold()
        matches = tuple(t for t in SECTION_TERMS if t in lower)
        numeric = len(re.findall(r'(?:£|gbp|bn|m\b|%)', lower))
        has_financial_evidence = bool(matches) or numeric >= 3
        cover_only = any(t in lower for t in COVER_ONLY_TERMS) and not has_financial_evidence
        toc_bonus = 0 if cover_only else (3 if 'contents' in lower and any(t in lower for t in ('financial', 'strategic report')) else 0)
        score = 0 if cover_only else len(matches) * 10 + min(numeric, 12) + toc_bonus
        if score and has_financial_evidence:
            candidates.append(PageCandidate(page.page_number, score, matches, text))
    candidates.sort(key=lambda c: (-c.score, c.page_number))
    chosen = sorted(candidates[:max_pages], key=lambda c: c.page_number)
    return chosen


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
    instructions = (EXTRACTION_INSTRUCTIONS + '\n\nReturn no more than 15 material, atomic facts across revenue, adjusted EBITDA, operating profit, capital expenditure, normalised free cash flow, net debt, cost savings, financial outlook, and material segment movement. Every fact must cite ORIGINAL PDF PAGE numbers present in the packet.').strip()
    return {
        'model': provider.model,
        'input': [{'role': 'user', 'content': [{'type': 'input_text', 'text': f"Document: {document.title}\nPacket pages: {', '.join(map(str, packet.page_numbers))}\n\n{packet.text}"}, {'type': 'input_text', 'text': instructions}]}],
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


class SectionAwareOpenAIProvider:
    def __init__(self, base_provider: Any):
        self.base_provider = base_provider
        self.model = base_provider.model
        self.reasoning_effort = 'none'
        self.max_output_tokens = min(int(getattr(base_provider, 'max_output_tokens', PACKET_MAX_OUTPUT_TOKENS)), PACKET_MAX_OUTPUT_TOKENS)
        self.settings = financial_intelligence_settings()

    def extract_packets(self, document: ExperimentDocument, pages: Iterable[DocumentPage], schema: type[ProviderFoundationFactSet] = ProviderFoundationFactSet, correlation_id: str | None = None) -> tuple[ExtractionRun, dict[str, Any]]:
        correlation_id = correlation_id or uuid.uuid4().hex
        candidates = select_candidate_pages(pages)
        page_reasons = {c.page_number: list(c.matched_terms) + ([f'numeric financial evidence'] if re.search(r'(?:£|gbp|bn|m\b|%)', c.text.casefold()) else []) for c in candidates}
        LOGGER.error('Flora selected financial pages ' + json.dumps({'support_reference': _support_reference(correlation_id), 'correlation_id': correlation_id, 'candidate_pages': [{'page_number': c.page_number, 'score': c.score, 'reasons': page_reasons.get(c.page_number, [])} for c in candidates]}, sort_keys=True))
        packets = build_page_packets(candidates)
        doc_hash = stable_document_hash(document)
        runs: list[ExtractionRun] = []; packet_records=[]; total_usage={'input_tokens':0,'output_tokens':0}; openai_calls=0; packet_failures=[]
        OpenAI = __import__('openai', fromlist=['OpenAI']).OpenAI
        client = OpenAI(timeout=getattr(self.base_provider, 'timeout_seconds', 120), max_retries=getattr(self.base_provider, 'max_retries', 0))
        queue = list(packets)
        while queue and openai_calls < MAX_BT_GOLDEN_CALLS:
            packet = queue.pop(0)
            cache_path = packet_cache_path(doc_hash, packet.packet_hash, self.model)
            if cache_path.is_file():
                run = ExtractionRun.model_validate(json.loads(cache_path.read_text()))
                runs.append(run); packet_records.append({'packet_id': packet.packet_id, 'page_numbers': packet.page_numbers, 'packet_hash': packet.packet_hash, 'cached': True, 'input_tokens': run.usage.get('input_tokens',0)})
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
                candidate_count = len(parsed.facts) + len(candidate_exceptions)
                diagnostics.append(_packet_event('packet_response_validation_completed', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started, provider_status=parse_status, candidate_count=candidate_count, valid_count=len(parsed.facts), quarantined_count=len(candidate_exceptions)))
                usage = raw.get('usage') or {}
                usage = usage | {'input_tokens': int(usage.get('input_tokens') or input_tokens), 'planned_output_allowance': self.max_output_tokens, 'tpm_reservation': input_tokens + self.max_output_tokens}
                total_usage['input_tokens'] += usage['input_tokens']; total_usage['output_tokens'] += int(usage.get('output_tokens') or 0)
                run = ExtractionRun(run_id=f'{correlation_id}-{packet.packet_id}', route='openai-responses-section-packet', provider='openai', model=self.model, model_version=self.model, status=parse_status, request_id=raw.get('id'), started_at=now_iso(), completed_at=now_iso(), latency_seconds=round(time.time()-started,3), usage=usage, facts=parsed.facts, candidate_exceptions=candidate_exceptions, diagnostics=diagnostics)
                ensure_writable_dir(cache_path.parent); atomic_write_json(cache_path, run.model_dump(mode='json'))
                runs.append(run); packet_records.append({'packet_id': packet.packet_id, 'page_numbers': packet.page_numbers, 'page_selection_reasons': {str(p): page_reasons.get(p, []) for p in packet.page_numbers}, 'packet_hash': packet.packet_hash, 'cached': False, 'input_tokens': input_tokens, 'status': parse_status, 'valid_facts': len(parsed.facts), 'quarantined_facts': len(candidate_exceptions)})
            except Exception as exc:
                LOGGER.exception('Unexpected Financial Intelligence packet exception support_reference=%s packet_id=%s', _support_reference(correlation_id), packet.packet_id)
                failure = _packet_event('packet_failed', correlation_id=correlation_id, packet=packet, reasons=page_reasons, input_tokens=input_tokens, model=self.model, started=started, provider_status='failed', provider_error=f'{type(exc).__name__}: {exc}')
                diagnostics.append(failure); packet_failures.append({'exception_type':'packet_failed','failure_stage': diagnostics[-2].get('event') if len(diagnostics)>1 else 'packet_selected','packet_id':packet.packet_id,'support_reference':_support_reference(correlation_id),'rejection_reason':failure['provider_error'],'user_message':'A financial section could not be analysed.'})
                run = ExtractionRun(run_id=f'{correlation_id}-{packet.packet_id}', route='openai-responses-section-packet', provider='openai', model=self.model, model_version=self.model, status='provider_request_failed', started_at=now_iso(), completed_at=now_iso(), latency_seconds=round(time.time()-started,3), usage={'input_tokens': input_tokens or 0}, facts=[], candidate_exceptions=[packet_failures[-1]], diagnostics=diagnostics)
                runs.append(run); packet_records.append({'packet_id': packet.packet_id, 'page_numbers': packet.page_numbers, 'page_selection_reasons': {str(p): page_reasons.get(p, []) for p in packet.page_numbers}, 'packet_hash': packet.packet_hash, 'cached': False, 'input_tokens': input_tokens, 'status': 'provider_request_failed', 'valid_facts': 0, 'quarantined_facts': 0})
                continue
        merged = merge_packet_facts(runs, document)
        final = ExtractionRun(run_id=correlation_id, route='openai-responses-section-packets', provider='openai', model=self.model, model_version=self.model, status=('completed_with_exceptions' if any(r.candidate_exceptions for r in runs) and merged.facts else ('provider_request_failed' if packet_failures and not merged.facts else ('provider_response_invalid' if runs and not merged.facts and any(r.candidate_exceptions for r in runs) else 'completed'))), started_at=now_iso(), completed_at=now_iso(), latency_seconds=0, usage=total_usage, facts=merged.facts, candidate_exceptions=[e for r in runs for e in r.candidate_exceptions], diagnostics=[d for r in runs for d in r.diagnostics])
        return final, {'candidate_pages': [{'page_number': c.page_number, 'score': c.score, 'reasons': page_reasons.get(c.page_number, [])} for c in candidates], 'packets': packet_records, 'packet_count': len(packet_records), 'openai_calls': openai_calls, 'document_hash': doc_hash}
