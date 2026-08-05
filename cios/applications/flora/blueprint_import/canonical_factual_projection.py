"""Canonical factual projection runtime for imported Flora Twin Objects.

This module is the shared Layer-1 read model for candidate factual
intelligence.  It is intentionally read-only: governance, promotion, owner
assessment and Observation generation remain with their canonical owners.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .semantic_twin import SemanticEnterprise, SemanticObject, executive_record_view_model


@dataclass(frozen=True)
class FactualSection:
    label: str
    values: tuple[str, ...]

    @property
    def present(self) -> bool:
        return any(v.strip() for v in self.values)


@dataclass(frozen=True)
class CanonicalFactualProjection:
    object_id: str
    family: str
    title: str
    governance_label: str
    sections: tuple[FactualSection, ...]
    evidence_refs: tuple[str, ...]
    unknown_refs: tuple[str, ...]
    contradiction_refs: tuple[str, ...]
    observation_refs: tuple[str, ...]
    assessment_state: str = "Pending governance"

    @property
    def has_facts(self) -> bool:
        return any(section.present for section in self.sections)


def executive_value_lines(value: Any) -> tuple[str, ...]:
    """Return deterministic executive-safe text lines for canonical values.

    This is the single presentation formatter for imported Twin factual fields:
    pages and diagnostics consume these lines rather than exposing Python/JSON
    containers from source payloads.
    """
    if value in (None, "", [], {}, ()): return ()
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if item in (None, "", [], {}, ()): continue
            label = str(key).replace("_", " ").strip().title()
            rendered = "; ".join(executive_value_lines(item))
            if rendered: lines.append(f"{label}: {rendered}")
        return tuple(lines)
    if isinstance(value, (list, tuple, set)):
        lines = []
        for item in value:
            lines.extend(executive_value_lines(item))
        return tuple(line for line in lines if line.strip())
    return (str(value),)


def _text(value: Any) -> tuple[str, ...]:
    return executive_value_lines(value)


def _attrs(obj: SemanticObject) -> dict[str, Any]:
    return dict(obj.attributes or {})


def _first(attrs: dict[str, Any], *names: str) -> tuple[str, ...]:
    for name in names:
        values = _text(attrs.get(name))
        if values: return values
    return ()


def _refs(obj: SemanticObject, *names: str) -> tuple[str, ...]:
    attrs = _attrs(obj); values: list[str] = []
    for name in names:
        for value in _text(attrs.get(name)):
            values.append(value)
    return tuple(dict.fromkeys(values))


def factual_projection_for_object(obj: SemanticObject, family: str | None = None) -> CanonicalFactualProjection:
    """Project one semantic object into the canonical factual contract."""
    attrs = _attrs(obj); view = executive_record_view_model(obj)
    inferred = family or _family(obj.kind)
    title = view.title or obj.statement or obj.subject or obj.original_id or obj.record_id
    mapped = {label: _text(value) for label, value in view.fields}
    sections: list[FactualSection] = []
    def add(label: str, *fields: str, fallback: Iterable[str] = ()) -> None:
        values = tuple(mapped.get(label, ())) or _first(attrs, *fields) or tuple(fallback)
        sections.append(FactualSection(label, values))
    if inferred == "Industry Overview":
        add("Industry definition", "industry_definition", "definition", "description", "summary", fallback=(obj.statement,))
        add("Scope", "scope", "industry_scope")
        add("Subsectors", "subsectors", "segments")
        add("Value chain", "value_chain", "value_chain_position")
        add("Market structure", "market_structure", "structure")
        add("Economics", "economics", "economic_context", "financial_context")
        add("Regulation", "regulation", "regulatory_context")
        add("Technology change", "technology_change", "technology")
        add("Transformation themes", "transformation_themes", "themes")
        add("Qualified insights", "qualified_insights", "insights", fallback=(obj.consequence,))
    elif inferred == "Enterprise Dossier":
        add("Organisation summary", "organisation_summary", "description", "summary", "overview", fallback=(obj.statement,))
        add("Strategy", "strategy", "strategic_ambition", "market_position")
        add("Operating model", "operating_model", "operating_structure")
        add("Financial context", "financial_context", "financials")
        add("Technology", "technology")
        add("Ecosystem", "ecosystem")
        add("Programmes", "programmes", "transformation_programmes")
        add("Suppliers", "suppliers", "supplier_relationships")
        add("Transformation", "transformation", "transformation_posture", fallback=(obj.consequence,))
    elif inferred == "Opportunity":
        add("Customer", "customer", "affected_enterprises", fallback=(", ".join(obj.affected_organisations) or obj.subject,))
        add("Business unit", "business_unit")
        add("Commercial type", "commercial_type")
        add("Value type", "value_type")
        add("Timing", "timing", "procurement_timing", "expected_procurement_start")
        add("Confidence", "confidence", fallback=(obj.confidence,))
        add("Opportunity", "opportunity", "title", fallback=(obj.statement,))
    else:
        if title and title != obj.statement: sections.append(FactualSection("Title", (title,)))
        for label, value in view.fields: sections.append(FactualSection(label, _text(value)))
        if obj.statement: sections.insert(0, FactualSection("Summary", (obj.statement,)))
        if obj.consequence: sections.append(FactualSection("Qualified insights", (obj.consequence,)))
    return CanonicalFactualProjection(
        obj.record_id, inferred, title, "Candidate Intelligence — Pending governance" if obj.governance == "candidate" else "Governed factual intelligence",
        tuple(s for s in sections if s.present), tuple(dict.fromkeys(obj.evidence_refs)),
        _refs(obj, "unknown_refs", "unknowns"), _refs(obj, "contradiction_refs", "contradictions"),
        _refs(obj, "observation_refs", "observations"), "Pending governance" if obj.governance == "candidate" else "Owner governed",
    )


def factual_projection_for_enterprise(ent: SemanticEnterprise) -> CanonicalFactualProjection:
    identity = next((o for o in ent.records if o.kind in {"enterprise", "enterprise_twin", "entity"}), ent.records[0])
    base = factual_projection_for_object(identity, "Enterprise Dossier")
    evidence = tuple(dict.fromkeys(x for o in ent.records for x in o.evidence_refs))
    unknowns = tuple(dict.fromkeys(x for o in ent.records for x in _refs(o, "unknown_refs", "unknowns")))
    contradictions = tuple(dict.fromkeys(x for o in ent.records for x in _refs(o, "contradiction_refs", "contradictions")))
    return CanonicalFactualProjection(ent.identity_key, "Enterprise Dossier", ent.name, base.governance_label, base.sections, evidence, unknowns, contradictions, base.observation_refs, base.assessment_state)


def _family(kind: str) -> str:
    if kind in {"industry", "industry_twin", "industry_overview"}: return "Industry Overview"
    if kind in {"enterprise", "enterprise_twin", "enterprise_dossier", "entity"}: return "Enterprise Dossier"
    if "opportun" in kind: return "Opportunity"
    if kind in {"ai_reinvention_assessment", "reinvention_assessment"}: return "Reinvention Assessment"
    if kind == "transformation_programme": return "Programme"
    if "market_participant" in kind: return "Market Participant"
    return kind.replace("_", " ").title()
