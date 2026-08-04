"""Reusable Researcher profile to canonical candidate-field adapter.

The Researcher contract uses rich, nested owner documents.  Candidate staging
previously retained those documents verbatim, while the canonical read model
looked only for its stable field vocabulary.  This adapter adds that vocabulary
without replacing (or interpreting) the source document.
"""
from __future__ import annotations

from typing import Any


_CLASS_ALIASES = {
    "transformation_pressure_view": "ai_reinvention_assessment",
}


def adapt_researcher_payload(record_class: str, source: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Return the existing canonical owner class and a lossless payload.

    Values are copied only from declared source fields.  Nested structures stay
    intact and ``source_payload`` provides explicit field-level lineage.
    """
    canonical_class = _CLASS_ALIASES.get(record_class, record_class)
    p = dict(source)
    p["source_payload"] = dict(source)
    p["transformation_adapter"] = "researcher-profile-v1"

    aliases: dict[str, Any] = {}
    evidence = source.get("evidence") or source.get("sources") or source.get("sources_searched")
    if evidence:
        aliases["evidence_refs"] = evidence
    if source.get("unknowns"):
        aliases["unknown_refs"] = source["unknowns"]
    if source.get("contradictions"):
        aliases["contradiction_refs"] = source["contradictions"]

    if canonical_class == "industry_twin":
        aliases.update(description=source.get("executive_summary") or source.get("definition"),
                       industry_profile=source)
    elif canonical_class == "enterprise_twin":
        overview = source.get("executive_overview") or {}
        aliases.update(enterprise_id=source.get("id"), enterprise_name=source.get("name"),
                       description=overview.get("what") if isinstance(overview, dict) else overview,
                       strategy=source.get("corporate_strategy"), operating_structure=source.get("operating_model"),
                       financial_context=source.get("financial_intelligence"), technology=source.get("technology_landscape"),
                       ecosystem={"partners": source.get("partners", []), "suppliers": source.get("suppliers", []), "competitors": source.get("competitors", [])},
                       pressures=overview.get("pressures", []) if isinstance(overview, dict) else [],
                       programmes=source.get("transformation_portfolio"), transformation_posture=source.get("reinvention_assessment"))
    elif canonical_class == "market_participant_twin":
        aliases.update(organisation_name=source.get("name"), domain=source.get("classification"),
                       significance=source.get("commercial_significance") or source.get("market_significance"),
                       role=source.get("role"), capabilities=source.get("capabilities"),
                       relationships=source.get("relationships"), current_activity=source.get("current_activity"))
    elif canonical_class == "transformation_programme":
        aliases.update(title=source.get("programme_name"), owner=source.get("owning_enterprise"),
                       business_unit=source.get("owning_business_unit"), objective=source.get("strategic_objective"),
                       phase=source.get("phase"), timing=source.get("timeline"), investment=source.get("budget"))
    elif canonical_class == "opportunity_hypothesis":
        problem = source.get("client_problem")
        aliases.update(title=source.get("opportunity_title"),
                       client_problem=(problem.get("customer_problem") if isinstance(problem, dict) else problem),
                       affected_enterprises=[source.get("canonical_customer_twin_id") or source.get("customer_enterprise_twin_id") or source.get("named_customer")],
                       procurement_status=source.get("procurement_status_control") or source.get("procurement_stage"),
                       business_unit=source.get("business_unit"), buyer=source.get("buyer"),
                       commercial_type=source.get("commercial_type_wave5"), value_type=(source.get("wave5_pipeline_qualification") or {}).get("value_type_wave5"))
        timing = source.get("timing")
        if isinstance(timing, dict): aliases["procurement_timing"] = timing.get("estimated_procurement_window") or timing.get("estimated_contract_start")
        value = source.get("value")
        if isinstance(value, dict): aliases["value_range"] = value.get("estimated_contract_value_range")
    elif canonical_class == "ai_reinvention_assessment":
        aliases.update(title=source.get("scope"), summary=source.get("current_operating_model"),
                       affected_functions=source.get("business_functions_affected"), timing=source.get("timing"),
                       consequence=source.get("executive_implications"),
                       ai_disruption_mechanism=source.get("ai_disruption_mechanism"),
                       expected_tipping_point=source.get("expected_tipping_point"))
    elif canonical_class == "evidence":
        aliases.update(statement=source.get("supported_claim"), subject=source.get("supported_object"),
                       freshness=source.get("publication_date") or source.get("collection_date"))
    elif canonical_class == "unknown":
        aliases.update(statement=source.get("question"), subject=source.get("object"), consequence=source.get("commercial_impact"))
    elif canonical_class == "contradiction":
        aliases.update(statement=source.get("issue"), evidence_refs=source.get("sources"), consequence=source.get("commercial_impact"))
    elif canonical_class == "relationship":
        aliases.update(statement=source.get("rationale") or source.get("relationship_type"), references=[source.get("source"), source.get("target")],
                       relationship_source=source.get("source"), relationship_target=source.get("target"))
    elif canonical_class == "membership":
        aliases.update(statement=source.get("inclusion_rationale") or source.get("membership_role"), references=[source.get("parent_industry_twin"), source.get("child_identity")],
                       membership_parent=source.get("parent_industry_twin"), membership_child=source.get("child_identity"))

    p.update({key: value for key, value in aliases.items() if value not in (None, "", [], {})})
    p["mapping_diagnostics"] = {"source_fields": sorted(source), "mapped_fields": sorted(k for k in aliases if aliases[k] not in (None, "", [], {})), "unmapped_fields": sorted(set(source) - _consumed_source_fields(canonical_class))}
    return canonical_class, p


def _consumed_source_fields(kind: str) -> set[str]:
    common = {"evidence", "sources", "sources_searched", "unknowns", "contradictions"}
    specific = {
        "industry_twin": {"executive_summary", "definition"}, "enterprise_twin": {"id", "name", "executive_overview", "corporate_strategy", "operating_model", "financial_intelligence", "technology_landscape", "partners", "suppliers", "competitors", "transformation_portfolio", "reinvention_assessment"},
        "market_participant_twin": {"name", "classification", "commercial_significance", "market_significance", "role", "capabilities", "relationships", "current_activity"}, "transformation_programme": {"programme_name", "owning_enterprise", "owning_business_unit", "strategic_objective", "phase", "timeline", "budget"},
        "opportunity_hypothesis": {"opportunity_title", "client_problem", "canonical_customer_twin_id", "customer_enterprise_twin_id", "named_customer", "procurement_status_control", "procurement_stage", "business_unit", "buyer", "commercial_type_wave5", "wave5_pipeline_qualification", "timing", "value"},
        "ai_reinvention_assessment": {"scope", "current_operating_model", "business_functions_affected", "timing", "executive_implications", "ai_disruption_mechanism", "expected_tipping_point"},
        "evidence": {"supported_claim", "supported_object", "publication_date", "collection_date"}, "unknown": {"question", "object", "commercial_impact"}, "contradiction": {"issue", "commercial_impact"},
        "relationship": {"rationale", "relationship_type", "source", "target"}, "membership": {"inclusion_rationale", "membership_role", "parent_industry_twin", "child_identity"},
    }
    return common | specific.get(kind, set())
