"""Canonical, read-only semantic classification of imported Evidence.

Evidence remains owned by the import-scoped ``SemanticObject``.  This module
interprets its surviving governed metadata once so financial and dossier
projections cannot introduce incompatible report taxonomies.
"""
from __future__ import annotations

from dataclasses import dataclass

from .semantic_twin import SemanticObject


@dataclass(frozen=True)
class EvidenceSemantics:
    report_family: str
    is_company_financial_reporting: bool
    is_external_research: bool
    rationale: str


def _text(obj: SemanticObject, *names: str) -> str:
    attrs = obj.attributes or {}
    return " ".join(str(attrs.get(name) or "") for name in names).casefold()


def classify_evidence(obj: SemanticObject) -> EvidenceSemantics:
    """Classify from supplied Evidence meaning, never from fixture identity."""
    if obj.kind != "evidence":
        return EvidenceSemantics("", False, False, "Object is not Evidence.")
    source = _text(obj, "title", "evidence_type", "category", "source_type",
                   "evidence_quality", "publisher")
    external_terms = ("analyst report", "analyst research", "broker research",
                      "equity research", "market research", "market analysis")
    if any(term in source for term in external_terms):
        return EvidenceSemantics("external_research", False, True,
                                 "Supplied Evidence metadata identifies external research.")
    report_terms = ("annual report", "annual results", "financial report",
                    "financial results", "results release", "quarterly results",
                    "quarterly report", "trading update", "earnings release")
    company_terms = ("primary", "company", "filing", "investor relations")
    if any(term in source for term in report_terms) and any(term in source for term in company_terms):
        return EvidenceSemantics("company_financial_reporting", True, False,
                                 "Supplied report meaning and company-primary provenance agree.")
    return EvidenceSemantics("", False, False,
                             "Supplied Evidence metadata does not establish a governed report family.")
