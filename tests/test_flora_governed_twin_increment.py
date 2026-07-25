from cios.applications.flora.blueprint_import.guidance import (
    detect_package_type, expectation_mismatch, select_with_dependencies,
)
from cios.applications.flora.blueprint_import.maturity import assess_maturity
from cios.applications.flora.blueprint_import.projections import industry_portfolio, normalise_opportunity


def candidate(cid, external, twin_type, refs=()):
    return {"candidate_record_id": cid, "original_source_id": external,
            "candidate_object_class": "twin", "payload": {"twin_type": twin_type, "references": list(refs)}}


def test_detects_types_and_blocks_mismatch_without_relabelling():
    rows=[candidate("1","IND-1","industry"), candidate("2","ENT-1","enterprise")]
    assert detect_package_type(rows) == "mixed"
    assert expectation_mismatch("industry", "mixed")
    assert not expectation_mismatch("mixed", "mixed")
    assert rows[0]["payload"]["twin_type"] == "industry"


def test_selective_scope_closes_dependencies_and_reports_missing():
    rows=[candidate("1","OPP-1","opportunity",("BUYER-1","EVID-1")), candidate("2","BUYER-1","enterprise")]
    chosen, unresolved=select_with_dependencies(rows,{"OPP-1"})
    assert chosen == {"1","2"}
    assert unresolved == {"EVID-1"}


def test_maturity_is_deterministic_explainable_and_critical_inputs_cap_opportunity():
    signals={name:100 for name,_ in __import__("cios.applications.flora.blueprint_import.maturity",fromlist=["PROFILES"]).PROFILES["opportunity"]}
    signals["buyer_identity"]=0; signals.update(unknown_count=1, contradiction_count=1)
    first=assess_maturity("opportunity",signals,package_completeness=100)
    assert first == assess_maturity("opportunity",signals,package_completeness=100)
    assert first["overall_maturity"] <= 49
    assert first["package_completeness"] == 100
    assert first["decision_completeness"]["score"] != first["package_completeness"]
    assert first["caps"] and first["penalties"] and first["next_evidence"] == "buyer_identity"


def test_read_projections_preserve_unavailable_and_rank_only_comparable_inputs():
    weak=normalise_opportunity({"opportunity_id":"O1","title":"Modernise","industry":"Example"})
    assert weak["buyer"] == "Unknown buyer" and not weak["ranking"]["enabled"]
    scored=normalise_opportunity({"opportunity_id":"O2","title":"Assure","industry":"Example","urgency":80,"confidence":70,"investment_signal":60,"procurement_signal":50,"transformation_maturity":40,"addressability":90,"freshness":80})
    assert scored["ranking"]["enabled"] and scored["ranking"]["score"] == 71
    cards=industry_portfolio([{"industry_id":"I1","name":"Example","enterprises":["E1"]}], [{"industry_id":"I1"}])
    assert cards[0]["opportunity_count"] == 1 and cards[0]["enterprise_count"] == 1
