from cios.applications.flora.twin_inspection.contracts import InspectionAdapter, InspectionProfile, InspectionSection


def test_shell_renders_supported_contract_sections_and_unavailable_values(monkeypatch):
    profile = InspectionProfile(
        "Example Ltd", "Enterprise", "Unavailable", "Accepted", "v1", "2026-07-01",
        "2026-06-30", "Unavailable", "Accepted", "2 governed evidence link(s)",
        "2026-07-01", "medium", "1", "0", "1 Research Package(s) · 1 Import Run(s)",
    )
    sections = (
        InspectionSection("executive-intelligence", "Executive Intelligence", 10, lambda: "<section><h2>Executive Overview</h2></section>", "governed", True, True, "#evidence", "current", "2026-06-30"),
        InspectionSection("empty", "Empty section", 20, lambda: "<p>must not render</p>", "governed", False, True, "#empty", "current", "2026-06-30"),
        InspectionSection("research-lineage", "Research Lineage", 30, lambda: "<section id='lineage'>lineage</section>", "provenance", True, True, "#lineage", "current", "2026-06-30"),
    )
    monkeypatch.setattr("cios.applications.flora.twin_inspection.views.enterprise_inspection_adapter", lambda *_: InspectionAdapter("enterprise-canvas", profile, sections))
    from cios.applications.flora.twin_inspection.views import twin_inspection_page
    html, status = twin_inspection_page("example", {})
    assert status == 200
    assert html.index("Twin Intelligence Profile") < html.index("Executive Overview") < html.index("id='lineage'")
    assert "Canonical owner</dt><dd>Unavailable" in html
    assert "Empty section" not in html and "must not render" not in html
    assert "enterprise-canvas adapter" in html


def test_industry_adapter_uses_same_shell_and_exposes_challenge_and_evidence():
    from cios.applications.flora.twin_inspection.views import twin_inspection_page
    html, status = twin_inspection_page("uk-banking", {}, "industry")
    assert status == 200
    assert "industry-banking adapter" in html
    assert "Material conclusions" in html
    assert "Why should I believe this?" in html
    assert "What challenges it?" in html
    assert "What remains unknown?" in html
    assert "Inspect supporting Evidence" in html
    assert "Significant enterprises" in html
    assert "No universal trust score" in html


def test_market_participant_gap_is_explicit_and_does_not_fabricate_runtime():
    from cios.applications.flora.twin_inspection.views import twin_inspection_page
    html, status = twin_inspection_page("example-participant", {}, "market-participant")
    assert status == 404
    assert "no canonical governed Market Participant read runtime" in html
    assert "No capability has been fabricated" in html


def test_candidate_context_is_visually_distinct(monkeypatch):
    profile = InspectionProfile(
        "Proposed Twin", "Candidate Industry Twin", "Blueprint Import", "Candidate — not governed intelligence",
        "v1", "2026-07-27", "Not supplied", "Candidate", "Pre-acceptance", "1 candidate Evidence",
        "2026-07-27", "Validation only", "1", "1", "Package p · Import Run r",
    )
    conclusion = __import__("cios.applications.flora.twin_inspection.contracts", fromlist=["MaterialConclusion"]).MaterialConclusion(
        "candidate", "One mutation is proposed.", "candidate proposal", "Review required", "Validation supports it",
        "An Unknown challenges it", "/blueprint-import/r/inspect", "/blueprint-import/r/review",
    )
    adapter = InspectionAdapter("candidate-import", profile, (), (conclusion,), "candidate")
    monkeypatch.setattr("cios.applications.flora.twin_inspection.views.candidate_inspection_adapter", lambda *_: adapter)
    from cios.applications.flora.twin_inspection.views import twin_inspection_page
    html, status = twin_inspection_page("r", {}, "candidate")
    assert status == 200
    assert "Candidate intelligence — not accepted or governed" in html
    assert "Inspection cannot promote or mutate canonical state" in html
    assert "candidate proposal" in html
