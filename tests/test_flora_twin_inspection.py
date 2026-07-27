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
