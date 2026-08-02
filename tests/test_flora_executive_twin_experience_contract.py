from cios.applications.flora.blueprint_import.executive_workspace import (
    _aspect_page, _dossier, _primary_nav, _source_item, _twin_map, twin_readiness,
)
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin


def _candidate(record_id, kind, **payload):
    return {"candidate_record_id": record_id, "original_source_id": record_id,
            "candidate_object_class": kind, "payload": payload}


def _twin():
    rows = [_candidate("e", "enterprise_twin", name="BBC", enterprise_id="bbc", domain="Media")]
    rows += [_candidate(f"p{i}", "market_participant_twin", name=f"Participant {i}", domain="Media") for i in range(10)]
    rows += [_candidate(f"o{i}", "opportunity_hypothesis", statement=f"Hypothesis {i}", affected_enterprises=["BBC"]) for i in range(9)]
    rows += [_candidate(f"m{i}", "transformation_programme", statement=f"Programme {i}", subject="BBC") for i in range(9)]
    rows += [_candidate("s", "evidence", title="Annual report", publisher="BBC", publication_date="2025")]
    return assemble_semantic_twin(rows)


def test_canonical_counts_are_not_inflated_and_readiness_is_honest():
    aspects = {a.key: a for a in twin_readiness(_twin())}
    assert aspects["opportunities"].present[0] == "9 opportunity hypothesis record(s)"
    assert aspects["market-participants"].present[0] == "10 represented participant(s)"
    assert aspects["market-participants"].state == "legacy_unassessed"
    assert aspects["major-programmes"].present[0] == "9 programme hypothesis record(s)"
    assert aspects["reinvention-timing"].state == "legacy_unassessed"
    assert aspects["reinvention-timing"].missing


def test_primary_pages_consolidate_incomplete_records():
    twin = _twin()
    programmes = _aspect_page(twin, "run", "Twin", "major-programmes", "all", None)
    opportunities = _aspect_page(twin, "run", "Twin", "opportunities", "all", None)
    participants = _aspect_page(twin, "run", "Twin", "market-participants", "all", None)
    assert "9 programme hypotheses identified" in programmes and "Unnamed programme" not in programmes
    assert "9 hypotheses require further research" in opportunities and "Hypothesis 1</h3>" not in opportunities
    assert "10 participants identified" in participants and "0 sufficiently classified" in participants


def test_navigation_and_sources_use_final_contract():
    nav = _primary_nav("run", "map")
    assert all(label in nav for label in ("Twin Map", "Research Gaps", "Advanced Inspection"))
    assert "Browse Full Twin" not in nav and "Key Insights" not in nav and "Governance" not in nav
    source = next(o for o in _twin().objects if o.kind == "evidence")
    html = _source_item(source)
    assert "Direct source link not supplied" in html and "Claim support not mapped" in html


def test_bbc_dossier_has_ordered_honest_consolidated_sections():
    twin = _twin()
    html = _dossier(twin.enterprises[0], twin, "run", None)
    headings = ["Organisation Overview", "Strategic Position and Ambition", "Financial Position", "Material Pressures", "Major Programmes", "Known Procurements", "Reinvention Timing", "Opportunities", "Key Sources", "Research Gaps", "Advanced Inspection"]
    assert [html.index(f"<h2>{heading}</h2>") for heading in headings] == sorted(html.index(f"<h2>{heading}</h2>") for heading in headings)
    assert "Organisation overview incomplete" in html
    assert "9 hypothesis record(s)" in html
    assert "Opportunity Hypothesis" not in html
