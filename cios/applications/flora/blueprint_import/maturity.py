"""Deterministic, explainable Twin-type maturity read assessment."""
from __future__ import annotations
from typing import Any

PROFILES={
 "industry": (("identity_scope",10),("structure_value_chains",7),("jurisdictions_controls",7),("enterprise_coverage",7),("participant_coverage",5),("relationships",6),("economics_investment",6),("transformations",7),("pressures_risks_dependencies",9),("opportunity_reasoning",8),("ai_reinvention",5),("executive_intelligence",6),("commercial_activation",5),("evidence_confidence",5),("freshness",4),("unknowns_contradictions",3)),
 "enterprise": (("identity",8),("ownership_governance",6),("financial_facts",7),("operational_facts",7),("strategy",6),("pressures_risks",8),("transformations",6),("technology_data_ot",7),("relationships_partners",7),("opportunities",7),("executive_intelligence",6),("evidence_confidence",7),("freshness",5),("unknowns_contradictions",3)),
 "market_participant": (("identity_scale",10),("offerings_capabilities",12),("markets_customers",9),("delivery_evidence_outcomes",12),("partnerships_procurement",9),("strengths_constraints",8),("operating_evidence",8),("opportunity_relevance",8),("evidence_confidence",8),("freshness",5),("unknowns_contradictions",3)),
 "opportunity": (("buyer_identity",10),("buyer_pressure",9),("target_outcome",9),("strategic_relevance",5),("evidence_lineage",10),("investment_procurement",8),("addressability",9),("capabilities_dependencies",7),("delivery_competition",5),("value_horizon_action",6),("confidence_freshness",7),("unknowns_contradictions",5)),
 "control_body": (("mandate_jurisdiction",15),("authority_governance",12),("policy_decision_rights",12),("funding_mechanisms",8),("relationships_obligations",10),("enforcement",8),("active_programmes",8),("evidence_confidence",12),("freshness",10),("unknowns_contradictions",5)),
}
CRITICAL={"opportunity":("buyer_identity","buyer_pressure","target_outcome","addressability","evidence_lineage")}

def assess_maturity(twin_type: str, signals: dict[str, Any], *, package_completeness: int=100, decision: str="opportunity prioritisation") -> dict[str, Any]:
    profile=PROFILES.get(twin_type, PROFILES["enterprise"]); dimensions=[]
    for name,weight in profile:
        raw=signals.get(name)
        score=max(0,min(100,int(raw))) if isinstance(raw,(int,float)) else 0
        dimensions.append({"name":name,"score":score,"weight":weight,"available":raw is not None})
    weighted=round(sum(x["score"]*x["weight"] for x in dimensions)/sum(x["weight"] for x in dimensions))
    gaps=[x["name"] for x in dimensions if x["score"]<50]
    critical=[n for n in CRITICAL.get(twin_type,()) if next(x["score"] for x in dimensions if x["name"]==n)<50]
    cap=49 if critical else 100
    unknowns=int(signals.get("unknown_count",0)); contradictions=int(signals.get("contradiction_count",0)); stale=int(signals.get("stale_evidence_count",0))
    penalty=min(30, unknowns*2+contradictions*5+stale*3); overall=max(0,min(cap,weighted-penalty))
    decision_score=max(0,min(overall, round((overall+(100 if not critical else 0))/2)))
    return {"twin_type":twin_type,"package_completeness":package_completeness,"overall_maturity":overall,"decision_completeness":{"decision":decision,"score":decision_score},"dimensions":dimensions,"weights_total":sum(x["weight"] for x in dimensions),"caps":[{"value":cap,"reason":"critical opportunity inputs absent"}] if critical else [],"penalties":[{"value":penalty,"reason":"unknown, contradiction and stale-evidence constraints"}] if penalty else [],"critical_gaps":critical,"material_gaps":gaps,"stale_evidence":stale,"unresolved_unknowns":unknowns,"unresolved_contradictions":contradictions,"next_evidence":critical[0] if critical else (gaps[0] if gaps else "No material gap identified")}
