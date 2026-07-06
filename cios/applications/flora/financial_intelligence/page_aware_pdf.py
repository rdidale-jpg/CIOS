"""Page-aware PDF text parsing boundary for rapid Financial Intelligence."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ParsedPdfPage:
    page_number: int
    text: str
    error: str | None = None


@dataclass(frozen=True)
class PageAwarePdfParseResult:
    parser_name: str
    parser_version: str
    page_count: int
    pages: tuple[ParsedPdfPage, ...]
    page_errors: tuple[dict[str, Any], ...]
    status: str
    failure_class: str | None = None

    @property
    def pages_successfully_read(self) -> tuple[int, ...]:
        return tuple(p.page_number for p in self.pages if p.text.strip() and not p.error)

    def diagnostics(self) -> dict[str, Any]:
        return {
            "parser_name": self.parser_name,
            "parser_version": self.parser_version,
            "page_count": self.page_count,
            "pages_successfully_read": list(self.pages_successfully_read),
            "pages_with_extraction_errors": [e.get("page_number") for e in self.page_errors],
            "document_parse_status": self.status,
            "failure_class": self.failure_class,
        }


def parser_version() -> str:
    try:
        return version("PyMuPDF")
    except PackageNotFoundError:
        return "unavailable"


def parse_page_aware_pdf(path: Path) -> PageAwarePdfParseResult:
    name = "pymupdf"
    ver = parser_version()
    try:
        import fitz  # type: ignore
    except Exception:
        return PageAwarePdfParseResult(name, ver, 0, (), (), "failed", "missing_production_dependency")
    pages: list[ParsedPdfPage] = []
    errors: list[dict[str, Any]] = []
    try:
        with fitz.open(str(path)) as doc:
            page_count = int(doc.page_count)
            if page_count <= 0:
                return PageAwarePdfParseResult(name, ver, 0, (), (), "failed", "no_pages")
            for idx in range(page_count):
                page_no = idx + 1
                try:
                    text = doc[idx].get_text("text") or ""
                    pages.append(ParsedPdfPage(page_no, text))
                    if not text.strip():
                        errors.append({"page_number": page_no, "failure_class": "no_meaningful_text"})
                except Exception as exc:  # bounded page-level diagnostic only
                    pages.append(ParsedPdfPage(page_no, "", type(exc).__name__))
                    errors.append({"page_number": page_no, "failure_class": type(exc).__name__})
    except Exception as exc:
        return PageAwarePdfParseResult(name, ver, 0, (), (), "failed", type(exc).__name__)
    meaningful = [p for p in pages if p.text.strip()]
    status = "parsed" if meaningful else "failed"
    return PageAwarePdfParseResult(name, ver, page_count, tuple(pages), tuple(errors), status, None if meaningful else "no_meaningful_text")
