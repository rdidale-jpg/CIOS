from cios.applications.flora.live.views import evidence_page
from cios.applications.flora.observatory.views import observatory_page, organisation_observatory_page
from cios.applications.flora.workspace.views import landing_page, radar_page, score_page


def test_executive_pages_open_with_judgement_not_mechanics():
    for html in [landing_page(), radar_page(), observatory_page(), organisation_observatory_page("BT")]:
        first = html[:3500].lower()
        assert "final score" not in first
        assert "base score" not in first
        assert "score contribution" not in first


def test_organisation_has_competing_hypotheses_and_reasoning_chain():
    html = organisation_observatory_page("BT")
    for text in ["Executive Intelligence Brief", "Flora’s View", "Recommended Next Conversation", "Commercial Priority Card", "Reasoning Chain", "Competing Hypotheses", "Primary Hypothesis", "Alternative Hypothesis", "Weakening / Contradictory Hypothesis", "Why Flora thinks this"]:
        assert text in html
    assert "Recommendation → Transformation Thesis → Competing Hypotheses → Strategic Signals → Evidence Cards" in html


def test_no_duplicate_why_now_or_truncated_fragments():
    html = organisation_observatory_page("BT")
    assert "Why now? Why Now?" not in html
    assert "This is a discovery thesi" not in html
    assert ">The<" not in html


def test_trace_and_raw_evidence_are_collapsed():
    html = organisation_observatory_page("BT")
    top = html.split("Layer 1 — 30-second briefing", 1)[1].split("Layer 3 — 30-minute investigation", 1)[0]
    assert "ETO-EV-" not in top
    assert "Raw/cleaned snippet" not in top
    score = score_page("BT")
    assert "Why Flora thinks this" in score.split("Analyst diagnostics", 1)[0]
    assert "Evidence-first score calculation audit" in score.split("Analyst diagnostics", 1)[1]


def test_seeded_fallback_not_presented_as_strong_live_evidence():
    html = observatory_page()
    assert "No strong live thesis yet — collect evidence first." in html
    assert "Seeded or insufficient-evidence cases remain learning targets" in html


def test_evidence_library_collapses_raw_scrape():
    html = evidence_page()
    assert "Evidence Library" in html
    assert "Executive-grade evidence" in html or "No live evidence available" in html
    if "Raw snippet" in html:
        assert "<details><summary>Raw snippet</summary>" in html
