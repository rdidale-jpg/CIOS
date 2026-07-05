"""Canonical, quality-gated PDF document adapter for Financial Intelligence."""
from __future__ import annotations

import re, statistics, string
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from cios.applications.flora.live.documents import DocumentPage
from .schema import ExperimentDocument

QUALITY_USABLE = 'text_extraction_usable'
QUALITY_PARTIAL = 'text_extraction_partial'
QUALITY_CORRUPT = 'text_extraction_corrupt'
QUALITY_UNAVAILABLE = 'text_extraction_unavailable'

FINANCIAL_NAV_TERMS = (
    'financial highlights','group financial review','financial review','revenue','adjusted ebitda',
    'operating profit','capital expenditure','free cash flow','net debt','outlook','guidance',
    'segment results','segment performance','financial statements','cost transformation','savings',
    'income statement','balance sheet','cash flow statement'
)

@dataclass(frozen=True)
class CanonicalPdfPage:
    internal_index: int
    pdf_page_number: int
    printed_page_number: str | None
    text: str
    text_blocks: tuple[str, ...]
    heading_candidates: tuple[str, ...]
    character_count: int
    printable_character_ratio: float
    alphanumeric_ratio: float
    extraction_quality_score: float
    source_document_id: str
    extraction_method: str
    width: float = 0.0
    height: float = 0.0
    renderable: bool = False

@dataclass(frozen=True)
class ParserAttempt:
    parser: str
    status: str
    page_count: int
    pages_with_useful_text: int
    total_characters: int
    median_characters_per_non_empty_page: int
    printable_character_ratio: float
    alphanumeric_ratio: float
    control_character_ratio: float
    repeated_glyph_indicator: bool
    heading_or_sentence_structure: bool
    quality_state: str
    quality_score: float
    error: str = ''

@dataclass(frozen=True)
class CanonicalPdfDocument:
    document: ExperimentDocument
    pages: tuple[CanonicalPdfPage, ...]
    parser_attempts: tuple[ParserAttempt, ...]
    selected_parser: str
    quality_state: str
    quality_metrics: dict[str, Any]


def _normalise(text: str) -> str:
    return re.sub(r'[ \t]+', ' ', re.sub(r'\n{3,}', '\n\n', text or '')).strip()

def _ratios(text: str) -> tuple[float, float, float]:
    if not text: return 0.0, 0.0, 0.0
    printable = sum(1 for c in text if c in string.printable or c.isprintable()) / len(text)
    alnum = sum(1 for c in text if c.isalnum()) / len(text)
    control = sum(1 for c in text if (ord(c) < 32 and c not in '\n\r\t')) / len(text)
    return printable, alnum, control

def _headings(text: str) -> tuple[str, ...]:
    heads=[]
    for line in (text or '').splitlines()[:40]:
        line = re.sub(r'\s+', ' ', line).strip()
        if 4 <= len(line) <= 110 and (line.isupper() or not re.search(r'[.!?]$', line)):
            heads.append(line)
    if not heads and text: heads.append(re.sub(r'\s+', ' ', text)[:96])
    return tuple(heads[:8])

def _printed(text: str) -> str | None:
    for pat in (r'\b(?:page|p\.)\s+(\d{1,3})\b', r'^\s*(\d{1,3})\s*$'):
        m=re.search(pat, text or '', re.I|re.M)
        if m: return m.group(1)
    return None

def _repeated_glyph(text: str) -> bool:
    compact = re.sub(r'\s+', '', text or '')
    if len(compact) < 40: return False
    return bool(re.search(r'(.)\1{12,}', compact)) or (len(set(compact)) <= 6 and len(compact) > 80)

def _quality(pages: list[CanonicalPdfPage], parser: str, error: str = '') -> ParserAttempt:
    counts=[p.character_count for p in pages if p.text.strip()]
    total=sum(p.character_count for p in pages)
    text='\n'.join(p.text for p in pages)
    pr, ar, cr = _ratios(text)
    useful=sum(1 for p in pages if p.character_count >= 30 and p.printable_character_ratio >= .85 and p.alphanumeric_ratio >= .25)
    med=int(statistics.median(counts)) if counts else 0
    structure=bool(re.search(r'\b[A-Z][a-z]{2,}\s+[a-z]{2,}.*[.!?]', text)) or any(any(t in h.casefold() for t in FINANCIAL_NAV_TERMS) for p in pages for h in p.heading_candidates)
    repeated=_repeated_glyph(text)
    coverage = useful / max(len(pages), 1)
    score = round((coverage * .45) + (min(med, 1200)/1200*.25) + (pr*.15) + (ar*.10) + ((0 if repeated else .05)) + ((.05) if structure else 0), 4)
    if not pages or total == 0: state=QUALITY_UNAVAILABLE
    elif total < 200 or pr < .70 or ar < .18 or cr > .05 or repeated: state=QUALITY_CORRUPT
    elif coverage >= .35 and med >= 250 and pr >= .90 and ar >= .35 and structure: state=QUALITY_USABLE
    elif coverage >= .10 and med >= 30 and pr >= .85 and ar >= .25: state=QUALITY_PARTIAL
    else: state=QUALITY_CORRUPT
    return ParserAttempt(parser, 'parsed' if pages else 'failed', len(pages), useful, total, med, pr, ar, cr, repeated, structure, state, score, error)

def _mk_page(idx:int, text:str, doc_id:str, method:str, blocks:Iterable[str]=(), width: float = 0.0, height: float = 0.0, renderable: bool = False) -> CanonicalPdfPage:
    text=_normalise(text); pr, ar, _ = _ratios(text)
    score = round((min(len(text),1000)/1000*.4) + (pr*.3) + (ar*.2) + ((0 if _repeated_glyph(text) else .1)), 4)
    return CanonicalPdfPage(idx, idx+1, _printed(text), text, tuple(blocks) or ((text,) if text else ()), _headings(text), len(text), pr, ar, score, doc_id, method, float(width or 0), float(height or 0), bool(renderable))

def _from_document_pages(pages: Iterable[DocumentPage], document: ExperimentDocument) -> list[CanonicalPdfPage]:
    return [_mk_page(i, getattr(p,'text','') or '', document.document_id, getattr(p,'extraction_method','embedded_text')) for i,p in enumerate(pages)]

def _fitz_pages(path: Path, document: ExperimentDocument) -> list[CanonicalPdfPage]:
    import fitz  # type: ignore
    out=[]
    with fitz.open(str(path)) as doc:
        for i,page in enumerate(doc):
            blocks=[]
            try: blocks=[str(b[4]) for b in page.get_text('blocks') if len(b)>4 and str(b[4]).strip()]
            except Exception: blocks=[]
            rect = page.rect
            renderable = False
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(0.05, 0.05), alpha=False)
                renderable = bool(pix.width and pix.height)
            except Exception:
                renderable = False
            out.append(_mk_page(i, page.get_text('text') or '\n'.join(blocks), document.document_id, 'pymupdf', blocks, rect.width, rect.height, renderable))
    return out

def load_canonical_pdf_document(document: ExperimentDocument, embedded_pages: Iterable[DocumentPage] = ()) -> CanonicalPdfDocument:
    attempts=[]; candidates=[]
    embedded=_from_document_pages(embedded_pages, document)
    attempts.append(_quality(embedded, 'embedded_text'))
    candidates.append(('embedded_text', embedded, attempts[-1]))
    path=Path(document.local_path) if document.local_path else None
    name, fn = 'pymupdf', _fitz_pages
    if not path or not path.is_file():
        attempts.append(ParserAttempt(name,'not_available',0,0,0,0,0,0,0,False,False,QUALITY_UNAVAILABLE,0,'local PDF unavailable'))
    else:
        try:
            pages=fn(path, document); att=_quality(pages, name); attempts.append(att); candidates.append((name,pages,att))
        except Exception as exc:
            attempts.append(ParserAttempt(name,'failed',0,0,0,0,0,0,0,False,False,QUALITY_UNAVAILABLE,0,f'{type(exc).__name__}: {exc}'))
    best_name,best_pages,best=max(candidates, key=lambda x: x[2].quality_score)
    metrics=best.__dict__ | {'parser_attempts':[a.__dict__ for a in attempts]}
    return CanonicalPdfDocument(document, tuple(best_pages), tuple(attempts), best_name, best.quality_state, metrics)


def useful_for_keyword_selection(canonical: CanonicalPdfDocument) -> bool:
    return canonical.quality_state in {QUALITY_USABLE, QUALITY_PARTIAL}
