from __future__ import annotations

import hashlib
import re
import threading
from http.client import HTTPConnection
from urllib.parse import quote_plus

from cios.applications.flora.enterprise_intelligence.explain import (
    assemble_lloyds_context_package,
    executive_presentation_for_explanation,
    explain_lloyds_changes,
)
from cios.applications.flora.web.app import FloraWebHandler


def _get(path: str) -> tuple[int, str]:
    server = __import__("http.server").server.ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start(); conn = HTTPConnection("127.0.0.1", server.server_port)
    try:
        conn.request("GET", path)
        response = conn.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        conn.close(); server.shutdown(); server.server_close(); thread.join(timeout=2)


def _strip_details(html: str) -> str:
    return re.sub(r"<details.*?</details>", "", html, flags=re.S)


def test_lloyds_explain_action_is_near_top_and_evidence_is_secondary() -> None:
    status, html = _get("/flora/object/BK-ENT-001")
    assert status == 200
    explain_pos = html.index("Explain what has changed")
    first_relationship_pos = html.index("Governed relationships only")
    assert explain_pos < first_relationship_pos
    assert "Inspect enterprise evidence" in html
    assert "Open Lloyds Banking Group Increment 1 workspace" not in html


def test_executive_headline_titles_and_card_sections_render() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert status == 200
    assert "<h1>What has changed at Lloyds?</h1>" in html
    for title in [
        "Digital engagement has accelerated",
        "Deposit economics have become more commercially significant",
        "Technology transformation is visible, but outcome proof remains incomplete",
        "Halifax is moving toward a unified Lloyds customer experience",
    ]:
        assert f"<h2>{title}</h2>" in html
    assert html.count("<h3>What changed</h3>") == 4
    assert html.count("<h3>Why it matters</h3>") == 4
    assert html.count("<h3>What we know</h3>") == 4
    assert html.count("<h3>What we do not know</h3>") == 4
    assert html.count("<h3>What to learn next</h3>") == 4


def test_internal_ids_are_not_primary_headings_but_lineage_is_inspectable() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert status == 200
    primary_headings = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html)
    assert not any("CHG-LBG-" in heading for heading in primary_headings)
    assert "Internal claim ID:" in html
    assert "Evidence IDs:" in html
    assert "Observation IDs:" in html
    assert "claim-level lineage" in html
    assert "Context Package identity:" in html


def test_source_passages_are_collapsed_by_default_and_unknowns_remain_visible() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert status == 200
    default_html = _strip_details(html)
    assert "Source passage P01" not in default_html
    assert "Cross-cutting Unknowns" in default_html
    assert "Competing interpretations" in default_html
    assert "Confidence limits" in default_html
    assert "Next Evidence demands" in default_html


def test_safe_unavailable_fails_closed_with_executive_safe_text() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain?question_id=" + quote_plus("Q-UNSUPPORTED"))
    assert status == 200
    assert "Flora cannot produce a governed explanation from the currently available evidence." in html
    assert "Reason category:" in html
    assert "Missing Evidence requirement:" in html
    assert "Safe next evidence action:" in html
    assert "Digital engagement has accelerated" not in html


def test_same_context_package_produces_same_executive_presentation() -> None:
    package = assemble_lloyds_context_package()
    one = executive_presentation_for_explanation(package, explain_lloyds_changes(package))
    two = executive_presentation_for_explanation(package, explain_lloyds_changes(package))
    assert one == two
    assert hashlib.sha256(repr(one).encode()).hexdigest() == hashlib.sha256(repr(two).encode()).hexdigest()


def test_no_recommendation_score_target_or_unrestricted_prompt_in_executive_view() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert status == 200
    default_html = _strip_details(html).lower()
    forbidden = ["recommendation", "opportunity score", "target executive", "name='question'", "unrestricted prompt"]
    for phrase in forbidden:
        assert phrase not in default_html


def test_rendered_acceptance_journey_home_to_lloyds_to_explain() -> None:
    home_status, home = _get("/flora")
    workspace_status, workspace = _get("/flora/object/BK-ENT-001")
    explain_status, explain = _get("/flora/object/BK-ENT-001/explain")
    assert (home_status, workspace_status, explain_status) == (200, 200, 200)
    assert "Flora" in home
    assert "Lloyds Banking Group" in workspace
    assert workspace.index("Explain what has changed") < workspace.index("Governed relationships only")
    assert "What has changed at Lloyds?" in explain
    assert "Executive synthesis" in explain
    assert "Inspect evidence" in explain
