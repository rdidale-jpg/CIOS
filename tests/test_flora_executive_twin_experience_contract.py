from cios.applications.flora.blueprint_import.executive_workspace import (
    _aspect_page, _dossier, _primary_nav, _source_item, _twin_map, twin_readiness,
)
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin
from cios.applications.flora.blueprint_import.review import ImportHumanReviewRepository, mark_import_reviewed


def _candidate(record_id, kind, **payload):
    return {"candidate_record_id": record_id, "original_source_id": record_id,
            "candidate_object_class": kind, "payload": payload}


def _twin():
    rows = _rows()
    return assemble_semantic_twin(rows)


def _rows():
    rows = [_candidate("e", "enterprise_twin", name="BBC", enterprise_id="bbc", domain="Media")]
    rows += [_candidate(f"p{i}", "market_participant_twin", name=f"Participant {i}", domain="Media") for i in range(10)]
    rows += [_candidate(f"o{i}", "opportunity_hypothesis", statement=f"Hypothesis {i}", affected_enterprises=["BBC"]) for i in range(9)]
    rows += [_candidate(f"m{i}", "transformation_programme", statement=f"Programme {i}", subject="BBC") for i in range(9)]
    rows += [_candidate("s", "evidence", title="Annual report", publisher="BBC", publication_date="2025")]
    return rows


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
    assert "9 programme records imported" in programmes and "Unnamed programme" not in programmes
    assert "9 opportunities available" in opportunities and "Hypothesis 1</h3>" in opportunities
    assert "10 market participant records imported" in participants


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
    headings = ["Organisation Overview", "Strategic Position and Ambition", "Financial Position", "Material Pressures", "Major Programmes", "Known Procurements", "Reinvention Timing", "Commercial Opportunities", "Evidence and Uncertainty", "Remaining Research Needs", "Advanced Inspection"]
    assert [html.index(f"<h2>{heading}</h2>") for heading in headings] == sorted(html.index(f"<h2>{heading}</h2>") for heading in headings)
    assert "Organisation description not supplied" in html
    assert html.count("Owned programme") == 9
    assert "Opportunity Hypothesis" not in html
    assert "governance review pending" not in html.casefold()


def test_subject_association_requires_explicit_canonical_field():
    twin = _twin()
    enterprise = twin.enterprises[0]
    unrelated = _candidate("x", "opportunity_hypothesis", statement="Unrelated", affected_enterprises=["Other Co"])
    combined = assemble_semantic_twin([*_rows(), unrelated])
    html = _dossier(next(e for e in combined.enterprises if e.name == enterprise.name), combined, "run", None)
    assert "Unrelated" not in html
    assert "Explicit enterprise relationship" in html


def test_human_review_is_persisted_without_promotion_or_truth_changes(monkeypatch, tmp_path):
    import cios.applications.flora.blueprint_import.review as review_module
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    package = type("Package", (), {"import_run_id": "run", "package_ref": "pkg",
                                   "workspace_id": "workspace",
                                   "identity": type("Identity", (), {"enterprise_id": "enterprise"})()})()
    monkeypatch.setattr(review_module.BlueprintPackageRegistry, "list", lambda self: [package])
    monkeypatch.setattr(review_module, "can_review_blueprint_candidate", lambda *args: True)
    monkeypatch.setattr(review_module, "authenticated_flora_user", lambda headers: "chief.architect")
    before = _twin()
    signature = [(o.record_id, o.statement, o.evidence_refs, o.kind) for o in before.objects]
    recorded = mark_import_reviewed("run", {}, "runtime-sha")
    saved = ImportHumanReviewRepository().get("run")
    after_signature = [(o.record_id, o.statement, o.evidence_refs, o.kind) for o in before.objects]
    assert saved and saved["reviewer_role"] == "Chief Architect"
    assert recorded.import_run_id == "run" and recorded.runtime_fingerprint == "runtime-sha"
    assert signature == after_signature
    assert not (tmp_path / "blueprint_import" / "lifecycle" / "run.json").exists()
