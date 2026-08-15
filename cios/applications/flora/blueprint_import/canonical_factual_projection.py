"""Canonical factual projection runtime for imported Flora Twin Objects.

This module is the shared Layer-1 read model for candidate factual
intelligence.  It is intentionally read-only: governance, promotion, owner
assessment and Observation generation remain with their canonical owners.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from cios.applications.flora.live.runtime import deployment_metadata

from .cios_twin_adapter import MAPPING_VERSION
from .semantic_twin import SemanticEnterprise, SemanticObject, executive_record_view_model

CANONICAL_FACTUAL_PROJECTION_VERSION = "canonical-factual-projection-v4"
EXECUTIVE_PROJECTION_VERSION = "executive-factual-presentation-v4"
OWNER_ASSESSMENT_INPUT_VERSION = "owner-assessment-factual-input-v1"


def runtime_fingerprint() -> str:
    """Return the material factual-runtime fingerprint exposed to consumers."""
    deployed = deployment_metadata()
    parts = (
        f"commit={deployed.get('commit_sha') or 'Unavailable'}",
        f"adapter={MAPPING_VERSION}",
        "semantic=semantic-twin-constructor-v1",
        f"cfp={CANONICAL_FACTUAL_PROJECTION_VERSION}",
        "observation=imported-twin-observation-profile-v1",
        f"owner={OWNER_ASSESSMENT_INPUT_VERSION}",
        f"executive={EXECUTIVE_PROJECTION_VERSION}",
    )
    return " | ".join(parts)


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
    relationship_refs: tuple[str, ...] = ()
    membership_refs: tuple[str, ...] = ()
    source_lineage: tuple[str, ...] = ()
    candidate_state: str = "candidate"
    completeness_state: str = "owner_assessment_pending"
    projection_version: str = CANONICAL_FACTUAL_PROJECTION_VERSION
    runtime_fingerprint: str = ""
    assessment_state: str = "Assessment not yet performed"
    enterprise_synthesis: EnterpriseFactualSynthesis | None = None

    @property
    def has_facts(self) -> bool:
        return any(section.present for section in self.sections)


@dataclass(frozen=True)
class EnterpriseFactualDimension:
    """One governed Enterprise factual read contract shared by every surface."""
    key: str
    label: str
    values: tuple[str, ...]
    source_fields: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    unknown_refs: tuple[str, ...]
    contradiction_refs: tuple[str, ...]
    supported: bool = True

    @property
    def present(self) -> bool:
        return bool(self.values)

    @property
    def status(self) -> str:
        if not self.supported:
            return "UNSUPPORTED"
        return "PASS" if self.present else "EXPECTED ABSENCE"


@dataclass(frozen=True)
class EnterpriseFactualSynthesis:
    """Explainable composition of qualifying facts already held by the CFP."""
    status: str
    statement: str
    input_dimensions: tuple[str, ...]
    input_fact_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    confidence: str
    unknown_refs: tuple[str, ...]
    contradiction_refs: tuple[str, ...]
    source_object: str
    candidate_object: str
    assessment_required: bool = False


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
    candidate_state = obj.governance or "candidate"
    completeness_state = "owner_assessment_pending" if candidate_state == "candidate" else "owner_governed"
    return CanonicalFactualProjection(
        obj.record_id, inferred, title, "Imported candidate — not yet reviewed" if obj.governance == "candidate" else "Governed factual intelligence",
        tuple(s for s in sections if s.present), tuple(dict.fromkeys(obj.evidence_refs)),
        _refs(obj, "unknown_refs", "unknowns"), _refs(obj, "contradiction_refs", "contradictions"),
        _refs(obj, "observation_refs", "observations"),
        _refs(obj, "relationship_refs", "relationships", "related_records"), _refs(obj, "membership_refs", "memberships"),
        tuple(x for x in (obj.source_file, obj.source_location, obj.original_id) if x),
        candidate_state, completeness_state, CANONICAL_FACTUAL_PROJECTION_VERSION, runtime_fingerprint(),
        "Assessment not yet performed" if obj.governance == "candidate" else "Owner governed",
    )


def factual_projection_for_enterprise(ent: SemanticEnterprise) -> CanonicalFactualProjection:
    identity = next((o for o in ent.records if o.kind in {"enterprise", "enterprise_twin", "entity"}), ent.records[0])
    base = factual_projection_for_object(identity, "Enterprise Dossier")
    evidence = tuple(dict.fromkeys(x for o in ent.records for x in o.evidence_refs))
    unknowns = tuple(dict.fromkeys(x for o in ent.records for x in _refs(o, "unknown_refs", "unknowns")))
    contradictions = tuple(dict.fromkeys(x for o in ent.records for x in _refs(o, "contradiction_refs", "contradictions")))
    relationships = tuple(dict.fromkeys(x for o in ent.records for x in _refs(o, "relationship_refs", "relationships", "related_records")))
    memberships = tuple(dict.fromkeys(x for o in ent.records for x in _refs(o, "membership_refs", "memberships")))
    lineage = tuple(dict.fromkeys(x for o in ent.records for x in (o.source_file, o.source_location, o.original_id) if x))
    return CanonicalFactualProjection(
        ent.identity_key, "Enterprise Dossier", ent.name, base.governance_label,
        base.sections, evidence, unknowns, contradictions, base.observation_refs,
        relationships, memberships, lineage, base.candidate_state,
        base.completeness_state, base.projection_version,
        base.runtime_fingerprint, base.assessment_state,
        enterprise_factual_synthesis(ent),
    )


ENTERPRISE_FACTUAL_DIMENSIONS = (
    ("profile", "Organisation / Enterprise Profile", ("description", "organisation_description", "overview", "summary"), True),
    ("industry", "Industry / Domain", ("domains",), True),
    ("strategy", "Strategic Position and Ambition", ("strategy", "corporate_strategy", "strategic_ambition", "market_position", "current_position"), True),
    ("operating-model", "Operating Model", ("operating_model", "operating_structure", "business_units"), True),
    ("financial", "Financial Position", ("financial_context", "financial_intelligence", "financials"), True),
    ("economics", "Enterprise Economics", (), False),
    ("pressures", "Material Pressures", ("pressures",), True),
    ("leadership-governance", "Leadership / Governance", (), False),
    ("technology", "Technology / Platform Context", ("technology", "technology_landscape"), True),
    ("supplier-ecosystem", "Supplier / Ecosystem Context", ("ecosystem", "suppliers", "partners"), True),
    ("procurements", "Known Procurements", ("procurement_intelligence",), True),
    ("transformation", "Reinvention Timing", ("transformation_posture", "reinvention_assessment", "transformation_portfolio"), True),
)


def enterprise_factual_dimensions(ent: SemanticEnterprise) -> tuple[EnterpriseFactualDimension, ...]:
    """Project qualifying identity facts without invoking assessment or promotion."""
    identity = next((o for o in ent.records if o.kind in {"enterprise", "enterprise_twin", "entity"}), ent.records[0])
    attrs = _attrs(identity)
    evidence = tuple(dict.fromkeys(identity.evidence_refs))
    unknowns = _refs(identity, "unknown_refs", "unknowns")
    contradictions = _refs(identity, "contradiction_refs", "contradictions")
    result = []
    for key, label, fields, supported in ENTERPRISE_FACTUAL_DIMENSIONS:
        selected: list[str] = []
        source_fields: list[str] = []
        if key == "industry":
            selected.extend(d.title() for d in identity.domains if d)
            if selected: source_fields.append("semantic domains")
        else:
            for field in fields:
                values = executive_value_lines(attrs.get(field))
                if values:
                    source_fields.append(field)
                    selected.extend(values)
                    break  # aliases represent one canonical dimension, not additive facts
        result.append(EnterpriseFactualDimension(
            key, label, tuple(dict.fromkeys(selected)), tuple(source_fields), evidence,
            unknowns, contradictions, supported,
        ))
    return tuple(result)


def enterprise_factual_synthesis(ent: SemanticEnterprise) -> EnterpriseFactualSynthesis:
    """Compose qualifying CFP facts without inference, assessment or persistence."""
    identity = next((o for o in ent.records if o.kind in {"enterprise", "enterprise_twin", "entity"}), ent.records[0])
    dimensions = {d.key: d for d in enterprise_factual_dimensions(ent)}
    qualifying = [dimensions[key] for key in ("profile", "operating-model", "strategy") if dimensions[key].present]
    source = identity.original_id or identity.record_id
    unknowns = tuple(dict.fromkeys(x for d in qualifying for x in d.unknown_refs))
    contradictions = tuple(dict.fromkeys(x for d in qualifying for x in d.contradiction_refs))
    evidence = tuple(dict.fromkeys(x for d in qualifying for x in d.evidence_refs))
    if not dimensions["profile"].present or len(qualifying) < 2:
        return EnterpriseFactualSynthesis("INSUFFICIENT EVIDENCE", "", tuple(d.key for d in qualifying), (), evidence, identity.confidence or "Not supplied", unknowns, contradictions, source, identity.record_id)
    selected = [(d, d.values[0].strip()) for d in qualifying if d.values[0].strip()]
    statement = " ".join(value if value.endswith((".", "!", "?")) else value + "." for _, value in selected)
    return EnterpriseFactualSynthesis("GENERATED", statement, tuple(d.key for d, _ in selected), tuple(f"FACT-{source}-{d.key.upper()}" for d, _ in selected), evidence, identity.confidence or "Not supplied", unknowns, contradictions, source, identity.record_id)


def _family(kind: str) -> str:
    if kind in {"industry", "industry_twin", "industry_overview"}: return "Industry Overview"
    if kind in {"enterprise", "enterprise_twin", "enterprise_dossier", "entity"}: return "Enterprise Dossier"
    if "opportun" in kind: return "Opportunity"
    if kind in {"ai_reinvention_assessment", "reinvention_assessment"}: return "Reinvention Assessment"
    if kind == "transformation_programme": return "Programme"
    if "market_participant" in kind: return "Market Participant"
    return kind.replace("_", " ").title()
