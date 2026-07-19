from __future__ import annotations

import re
import threading
from http.client import HTTPConnection

from cios.applications.flora.enterprise_intelligence.explain import (
    assemble_lloyds_context_package,
    claim_evidence_summaries,
    evidence_trust_view,
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


def test_every_rendered_evidence_item_has_complete_trust_lens() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert status == 200
    for label in [
        "Source authority", "Evidence role", "Scope", "Freshness", "Corroboration",
        "Evidence limitations", "Confidence contribution",
    ]:
        assert html.count(f"<dt>{label}</dt>") >= 6


def test_partial_dates_are_visibly_flagged() -> None:
    package = assemble_lloyds_context_package(); explanation = explain_lloyds_changes(package)
    trust = {t.evidence_id: t for t in evidence_trust_view(package, explanation)}
    assert trust["EV-LBG-005"].publication_date == "2026-XX-XX"
    assert trust["EV-LBG-005"].freshness_status == "temporally uncertain"
    assert "missing or partial publication date" in trust["EV-LBG-005"].data_quality_flags
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert "2026-XX-XX" in html
    assert "missing or partial publication date" in html


def test_company_reported_evidence_is_not_independently_validated_and_single_source() -> None:
    package = assemble_lloyds_context_package(); explanation = explain_lloyds_changes(package)
    trust = {t.evidence_id: t for t in evidence_trust_view(package, explanation)}
    assert trust["EV-LBG-003"].source_authority == "Lloyds investor reporting"
    assert trust["EV-LBG-003"].corroboration == "single-source"
    summaries = {s.change_id: s for s in claim_evidence_summaries(package, explanation)}
    assert summaries["CHG-LBG-002"].corroboration_status == "single-source"


def test_sector_context_is_not_presented_as_lloyds_specific_proof() -> None:
    package = assemble_lloyds_context_package(); explanation = explain_lloyds_changes(package)
    trust = {t.evidence_id: t for t in evidence_trust_view(package, explanation)}
    assert trust["EV-LBG-006"].scope == "cross-enterprise"
    assert trust["EV-LBG-006"].evidence_role == "contextual support"
    assert "not Lloyds-specific proof" in "; ".join(trust["EV-LBG-006"].data_quality_flags)


def test_direct_and_contextual_evidence_are_visibly_distinguished() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert status == 200
    assert "<dd>direct support</dd>" in html
    assert "<dd>contextual support</dd>" in html


def test_confidence_contribution_is_deterministic_bounded_and_non_numeric() -> None:
    package = assemble_lloyds_context_package(); explanation = explain_lloyds_changes(package)
    one = evidence_trust_view(package, explanation)
    two = evidence_trust_view(package, explanation)
    allowed = {"strong factual support", "moderate factual support", "contextual support only", "weak or incomplete support", "unavailable"}
    assert one == two
    assert {t.confidence_contribution for t in one} <= allowed
    assert not any(re.search(r"\d", t.confidence_contribution) for t in one)


def test_increment2_and_21_meaning_remains_unchanged_and_no_forbidden_capability() -> None:
    package = assemble_lloyds_context_package(); explanation = explain_lloyds_changes(package)
    presentation = executive_presentation_for_explanation(package, explanation)
    assert [c.change_id for c in explanation.changes] == ["CHG-LBG-001", "CHG-LBG-002", "CHG-LBG-003", "CHG-LBG-004"]
    assert presentation["headline"] == "What has changed at Lloyds?"
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert status == 200
    default_html = _strip_details(html).lower()
    for forbidden in ["recommendation", "opportunity score", "target executive"]:
        assert forbidden not in default_html
