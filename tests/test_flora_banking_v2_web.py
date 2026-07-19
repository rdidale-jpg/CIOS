from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from urllib.parse import quote_plus

from cios.applications.flora.web.app import FloraWebHandler


def _get(path: str) -> tuple[int, str]:
    server = __import__("http.server").server.ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    conn = HTTPConnection("127.0.0.1", server.server_port)
    try:
        conn.request("GET", path)
        response = conn.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        conn.close(); server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_ask_flora_executes_banking_pipeline() -> None:
    status, html = _get("/ask?question=" + quote_plus("What is changing in Banking?"))
    assert status == 200
    assert "Banking Strategic Sales Brief" in html
    assert "BRH-003" in html
    assert "Recommendation Eligibility" in html


def test_unsupported_ask_rejects_without_fabricating() -> None:
    status, html = _get("/ask?question=" + quote_plus("Who should I call at a supermarket?"))
    assert status == 200
    assert "This question is not yet supported by the current Enterprise Intelligence prototype." in html
    assert "named executive" not in html.lower()


def test_explore_displays_governed_observations_unknowns_and_contradictions() -> None:
    status, html = _get("/explore")
    assert status == 200
    assert "Explore / Banking" in html
    assert "BK-OBS-014" in html
    assert "Unknowns" in html
    assert "Contradictions" in html


def test_focus_displays_governed_enterprise_context_without_unsupported_claims() -> None:
    status, html = _get("/focus")
    assert status == 200
    assert "Supported enterprises" in html
    assert "Lloyds Banking Group" in html
    assert "Enterprise specificity: Unknown" in html
    assert "does not invent enterprise-specific evidence" in html


def test_shape_renders_strategic_sales_brief_pipeline_and_recommendation_gate() -> None:
    status, html = _get("/shape")
    assert status == 200
    assert "Banking Strategic Sales Brief" in html
    assert "How Flora reasoned" in html
    assert "Recommendation Eligibility" in html
    assert "validate with executive" in html
    assert "proposal" in html


def test_evidence_navigation_renders_observation_mechanism_and_hypothesis_detail() -> None:
    for object_id in ("BK-OBS-014", "BM-04", "BRH-003"):
        status, html = _get(f"/evidence/{object_id}")
        assert status == 200
        assert object_id in html
        assert "Supporting evidence" in html
        assert "Relationships" in html
        assert "Lifecycle" in html


def test_health_endpoint_still_passes() -> None:
    server = __import__("http.server").server.ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start(); conn = HTTPConnection("127.0.0.1", server.server_port)
    try:
        conn.request("GET", "/health")
        response = conn.getresponse()
        assert response.status == 200
        assert json.loads(response.read().decode("utf-8"))["status"] == "healthy"
    finally:
        conn.close(); server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_shape_banking_routes_and_explore_link_work() -> None:
    for path in ("/shape", "/shape/banking", "/shape/strategic-sales-brief", "/shape/banking/strategic-sales-brief"):
        status, html = _get(path)
        assert status == 200
        assert "Prepare an evidence-backed executive engagement." in html
        assert "Build Strategic Sales Brief" in html
    status, html = _get("/explore")
    assert status == 200
    assert "Shape the Strategic Sales Brief" in html
    assert "href='/shape'" in html


def test_strategic_sales_brief_required_sections_and_safety() -> None:
    status, html = _get("/shape/banking/strategic-sales-brief")
    assert status == 200
    for text in [
        "Derived runtime view — not authoritative Enterprise Knowledge",
        "Current interpretation",
        "Who should care",
        "Why now",
        "Why them",
        "Supporting evidence",
        "Supporting observations",
        "Underlying mechanisms",
        "BRH-003",
        "What remains Unknown",
        "Alternative interpretations",
        "Confidence",
        "Recommended next action",
        "What should not yet be done",
        "Lineage",
    ]:
        assert text in html
    assert "Named executive: <strong>Unknown</strong>" in html
    assert "Enterprise specificity is currently limited" in html
    assert "validate with executive" in html
    assert "approved recommendation" in html
    assert "do not claim enterprise-specific urgency" in html


def test_lineage_and_evidence_references_resolve() -> None:
    status, html = _get("/shape")
    assert status == 200
    for object_id in ("BRH-003", "BK-OBS-014", "BK-OBS-015", "BK-OBS-016", "BK-OBS-029", "BK-OBS-047", "BM-04", "BM-02", "BM-14", "BM-15", "BK-IND-001"):
        assert object_id in html
        detail_status, detail_html = _get(f"/evidence/{object_id}")
        assert detail_status == 200
        assert object_id in detail_html
        assert "Lineage" in detail_html


def test_reference_workspace_completes_required_journey() -> None:
    status, html = _get("/workspace/reference")
    assert status == 200
    for text in [
        "What Changed",
        "UK Banking",
        "APP Fraud",
        "Lloyds Banking Group",
        "Explainability panel",
        "Evidence panel",
        "Unknowns panel",
        "Contradictions panel",
        "Opportunity panel",
        "Enterprise Need",
        "Provider Fit",
        "Commercial Accessibility",
        "Commercial Conviction",
        "Validation Action creation",
        "No duplicate enterprise objects are introduced",
    ]:
        assert text in html
    assert "Not inferred" in html
    assert "Architecture-safe placeholder" in html


def test_reference_workspace_validation_action_preserves_resume_state() -> None:
    server = __import__("http.server").server.ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start(); conn = HTTPConnection("127.0.0.1", server.server_port)
    try:
        body = "action=validate&journey=uk-banking-app-fraud-lloyds"
        conn.request("POST", "/workspace/reference/validation-action", body=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
        response = conn.getresponse()
        response.read()
        assert response.status == 303
        cookie = response.getheader("Set-Cookie") or ""
        assert "flora_reference_investigation=uk-banking-app-fraud-lloyds" in cookie
    finally:
        conn.close(); server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_increment43_ai_native_reference_model_and_timelines_exist() -> None:
    status, html = _get("/flora/banking")
    assert status == 200
    for text in [
        "What the AI-native bank will look like",
        "Customer experience",
        "Sales and relationship management",
        "Innovation and change delivery",
        "Industry reinvention timeline",
        "Now",
        "1–2 years",
        "3–5 years",
        "6–10 years",
        "Inspectable assumptions",
    ]:
        assert text in html
    for bank in ["Lloyds Banking Group", "Barclays", "NatWest Group", "HSBC UK", "Santander UK"]:
        assert bank in html
    assert "2–3 years" in html
    assert "6–9 years" in html


def test_increment43_account_pages_are_plain_language_and_do_not_duplicate_full_pestle() -> None:
    status, html = _get("/flora/banking/lloyds")
    assert status == 200
    for text in [
        "Where this bank sits on the reinvention journey",
        "What an AI-native version of this bank would look like",
        "What must change next",
        "Reinvention gap view",
        "Customer primacy</strong> means whether customers treat this bank as their main financial relationship",
        "Control evidence</strong> means proof that processes are operating safely",
        "Title provenance:",
        "Customer Experience Transformation and Outsourcing was supplied by the user",
        "Pressure → required change → capability gap → commercial scope → opportunity title",
    ]:
        assert text in html
    assert "<h2>PESTLE analysis</h2>" not in html
    assert "Independently derived title?</strong> No" in html


def test_increment43_competitor_page_ranks_suppliers_without_win_probability() -> None:
    status, html = _get("/flora/banking/competitors")
    assert status == 200
    for text in [
        "Competitor capability landscape",
        "Customer experience",
        "Data and AI",
        "Accenture",
        "Microsoft",
        "Ranking basis is inspectable and non-canonical",
        "does not imply likelihood of winning a specific opportunity",
        "Competitor-to-opportunity mapping",
        "This is a competitive hypothesis, not a confirmed procurement view",
    ]:
        assert text in html


def test_increment43_simplified_heatmap_keeps_expandable_detail_and_pipeline_values() -> None:
    status, html = _get("/flora/banking/compare")
    assert status == 200
    for text in [
        "Simplified executive heatmap",
        "Default cells are materially shorter",
        "<strong>Stage:</strong>",
        "<strong>Pressure:</strong>",
        "<strong>Value:</strong>",
        "<strong>Top supplier:</strong>",
        "<strong>Top gap:</strong>",
        "Technical detail remains available",
        "Opportunity-value summary",
        "not a win probability",
    ]:
        assert text in html
    assert "Flora working estimate" in html
