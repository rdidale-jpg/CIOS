"""Section-aware, low-cost annual report packet extraction for Flora."""
from __future__ import annotations

import hashlib, json, re, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir
from cios.applications.flora.live.documents import DocumentPage
from .instructions import EXTRACTION_INSTRUCTIONS
from .schema import ExperimentDocument, ExtractionRun, FoundationFactSet, now_iso, openai_strict_json_schema
from .candidate_validation import parse_foundation_fact_candidates
from .config import financial_intelligence_settings

TARGET_INPUT_TOKENS = 50_000
ABSOLUTE_INPUT_TOKEN_CEILING = 75_000
MAX_BT_GOLDEN_CALLS = 4
PACKET_MAX_OUTPUT_TOKENS = 2_000
MATERIAL_FACT_LIMIT = 15

SECTION_TERMS = (
    'financial highlights','group income statement','group balance sheet','cash flow statement','cash-flow statement',
    'segment performance','revenue','adjusted ebitda','operating profit','capital expenditure','capex',
    'free cash flow','normalised free cash flow','net debt','outlook','guidance','cost transformation','cost savings','savings commitments'
)

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
        toc_bonus = 3 if 'contents' in lower and any(t in lower for t in ('financial', 'strategic report')) else 0
        score = len(matches) * 10 + min(numeric, 12) + toc_bonus
        if score:
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

    def extract_packets(self, document: ExperimentDocument, pages: Iterable[DocumentPage], schema: type[FoundationFactSet] = FoundationFactSet, correlation_id: str | None = None) -> tuple[ExtractionRun, dict[str, Any]]:
        correlation_id = correlation_id or uuid.uuid4().hex
        candidates = select_candidate_pages(pages)
        packets = build_page_packets(candidates)
        doc_hash = stable_document_hash(document)
        runs: list[ExtractionRun] = []; packet_records=[]; total_usage={'input_tokens':0,'output_tokens':0}; openai_calls=0
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
            input_tokens = count_packet_input_tokens(client, self, document, packet, schema)
            if input_tokens > ABSOLUTE_INPUT_TOKEN_CEILING:
                queue = split_oversized_packet(packet) + queue
                continue
            payload = _packet_payload(self, document, packet, schema) | {'max_output_tokens': self.max_output_tokens}
            resp = client.responses.create(**payload); openai_calls += 1
            raw = resp.model_dump(mode='json') if hasattr(resp, 'model_dump') else resp
            parsed, candidate_exceptions, parse_status = parse_foundation_fact_candidates(getattr(resp, 'output_text', '') or raw.get('output_text', '{}'), packet_id=packet.packet_id, provider='openai', model=self.model, request_id=raw.get('id'))
            usage = raw.get('usage') or {}
            usage = usage | {'input_tokens': int(usage.get('input_tokens') or input_tokens), 'planned_output_allowance': self.max_output_tokens, 'tpm_reservation': input_tokens + self.max_output_tokens}
            total_usage['input_tokens'] += usage['input_tokens']; total_usage['output_tokens'] += int(usage.get('output_tokens') or 0)
            run = ExtractionRun(run_id=f'{correlation_id}-{packet.packet_id}', route='openai-responses-section-packet', provider='openai', model=self.model, model_version=self.model, status=parse_status, request_id=raw.get('id'), started_at=now_iso(), completed_at=now_iso(), latency_seconds=0, usage=usage, facts=parsed.facts, candidate_exceptions=candidate_exceptions, diagnostics=[{'request_stage':'token_preflight','packet_id':packet.packet_id,'page_numbers':list(packet.page_numbers),'input_tokens':input_tokens,'planned_output_allowance':self.max_output_tokens,'tpm_reservation':input_tokens+self.max_output_tokens,'absolute_input_token_ceiling':ABSOLUTE_INPUT_TOKEN_CEILING}])
            ensure_writable_dir(cache_path.parent); atomic_write_json(cache_path, run.model_dump(mode='json'))
            runs.append(run); packet_records.append({'packet_id': packet.packet_id, 'page_numbers': packet.page_numbers, 'packet_hash': packet.packet_hash, 'cached': False, 'input_tokens': input_tokens})
        merged = merge_packet_facts(runs, document)
        final = ExtractionRun(run_id=correlation_id, route='openai-responses-section-packets', provider='openai', model=self.model, model_version=self.model, status=('completed_with_exceptions' if any(r.candidate_exceptions for r in runs) and merged.facts else ('provider_response_invalid' if runs and not merged.facts and any(r.candidate_exceptions for r in runs) else 'completed')), started_at=now_iso(), completed_at=now_iso(), latency_seconds=0, usage=total_usage, facts=merged.facts, candidate_exceptions=[e for r in runs for e in r.candidate_exceptions], diagnostics=[d for r in runs for d in r.diagnostics])
        return final, {'candidate_pages': [c.page_number for c in candidates], 'packets': packet_records, 'packet_count': len(packet_records), 'openai_calls': openai_calls, 'document_hash': doc_hash}
