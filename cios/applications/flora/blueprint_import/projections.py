"""Read-only multi-industry and opportunity projections over accepted state."""
from __future__ import annotations
from typing import Any

def unavailable(value: Any, reason: str="Unavailable") -> Any: return value if value not in (None,"") else reason

def normalise_opportunity(row: dict[str, Any]) -> dict[str, Any]:
    lineage=row.get("blueprint_import_lineage") or row.get("lineage")
    kind=row.get("opportunity_type") or "market"
    comparable=all(row.get(k) is not None for k in ("urgency","confidence","addressability","freshness"))
    components={k:row.get(k) for k in ("urgency","confidence","investment_signal","procurement_signal","transformation_maturity","addressability","freshness")}
    weights={"urgency":20,"confidence":20,"investment_signal":10,"procurement_signal":10,"transformation_maturity":10,"addressability":20,"freshness":10}
    score=round(sum(float(components[k])*w for k,w in weights.items())/sum(weights.values())) if comparable and all(isinstance(components[k],(int,float)) for k in weights) else None
    return {"opportunity_id":row.get("opportunity_id") or row.get("canonical_id"),"opportunity_type":kind,"industry":unavailable(row.get("industry")),"buyer":unavailable(row.get("buyer"),"Unknown buyer"),"title":unavailable(row.get("title")),"theme":unavailable(row.get("theme")),"buyer_pressure":unavailable(row.get("buyer_pressure"),"Insufficient evidence"),"target_outcome":unavailable(row.get("target_outcome")),"horizon":unavailable(row.get("horizon")),"required_capabilities":row.get("required_capabilities") or [],"confidence":unavailable(row.get("confidence")),"freshness":unavailable(row.get("freshness")),"unknowns":row.get("unknowns") or [],"contradictions":row.get("contradictions") or [],"lineage":unavailable(lineage,"Insufficient evidence"),"ranking":{"enabled":score is not None,"score":score,"components":components,"weights":weights,"missing_inputs":[k for k,v in components.items() if v is None],"explanation":"Weighted deterministic read projection; no probability or financial value is inferred."}}

def industry_portfolio(industries: list[dict[str, Any]], opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive cards without persisting or copying canonical Twin state."""
    result=[]
    for twin in industries:
        iid=twin.get("industry_id") or twin.get("canonical_id"); related=[o for o in opportunities if o.get("industry_id")==iid or o.get("industry")==twin.get("name")]
        result.append({"industry_id":iid,"name":unavailable(twin.get("name")),"scope":unavailable(twin.get("scope")),"lifecycle_state":unavailable(twin.get("lifecycle_state")),"maturity":twin.get("maturity"),"decision_completeness":twin.get("decision_completeness"),"freshness":unavailable(twin.get("freshness")),"confidence":unavailable(twin.get("confidence")),"enterprise_count":len(twin.get("enterprises") or []),"market_participant_count":len(twin.get("market_participants") or []),"opportunity_count":len(related),"pressures":twin.get("pressures") or [],"transformation_themes":twin.get("transformation_themes") or [],"unknowns":twin.get("unknowns") or [],"contradictions":twin.get("contradictions") or [],"lineage":unavailable(twin.get("blueprint_import_lineage") or twin.get("lineage"),"Insufficient evidence")})
    return result
