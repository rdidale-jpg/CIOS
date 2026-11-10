"""Read-only Research Intelligence Diagnostic regression tests."""
import html

from cios.applications.flora.public_routes import public_request_target
from cios.applications.flora.research_intelligence.diagnostic import assess, render
from cios.applications.flora.research_intelligence.model import load_assessment


def test_diagnostic_available_for_exact_registered_enterprises_only():
    for slug in ("lloyds", "easyjet"):
        assert public_request_target(f"/enterprises/{slug}/research-diagnostic")
        assert not public_request_target(f"/enterprises/{slug}/research-diagnostic?lens=opportunities")
    assert not public_request_target("/enterprises/unknown/research-diagnostic")
    assert not public_request_target("/enterprises/lloyds/research-diagnostic/secret")


def test_banking_and_aviation_report_evidence_not_fake_maturity_scores():
    for domain in ("banking", "aviation"):
        data = load_assessment(domain)
        report = assess(data)
        assert report["source_count"] == len(data["sources"])
        assert report["claim_count"] == len(data["claims"])
        assert report["relationship_count"] == len(data["relationships"])
        assert report["candidate_count"] == len(data["candidates"])
        assert report["supported_claim_count"] + report["unverified_claim_count"] == len(data["claims"])
        assert (report["verified_relationship_count"] +
                report["interpretive_relationship_count"]) == len(data["relationships"])
        assert report["invalid_source_refs"] == []
        assert "Not assessed" in report["maturity"]
        assert report["authority"] == "candidate_intelligence"
        assert "Research Intelligence Diagnostic" in render(data)
        assert "not an IT-001 maturity score" in render(data)


def test_gap_order_and_html_safety():
    data = load_assessment("aviation")
    extra = dict(data)
    extra["gaps"] = [
        {"id": "low", "title": "<script>alert(1)</script>", "status": "open",
         "priority": "Low", "required_evidence": "<unsafe>"},
        {"id": "high", "title": "Important", "status": "open",
         "priority": "High", "required_evidence": "Verify"},
        {"id": "done", "title": "Closed", "status": "resolved",
         "priority": "High"},
    ]
    result = assess(extra)
    assert [g["id"] for g in result["active_gaps"]] == ["high", "low"]
    markup = render(extra)
    assert markup.index("Important") < markup.index("&lt;script&gt;")
    assert "<script>" not in markup
    assert "&lt;unsafe&gt;" in markup


def test_diagnostic_does_not_mutate_research_overlay():
    data = load_assessment("banking")
    from copy import deepcopy
    before = deepcopy(data)
    assess(data)
    render(data)
    assert data == before
