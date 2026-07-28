"""Focused WP2-002 composition checks for the existing Import Review route."""
from tests.test_flora_blueprint_import_review_planning import HEADERS, stage


def _review(monkeypatch, tmp_path):
    records = [
        {"external_id": "ENT-1", "record_class": "enterprise", "truth_class": "human_supplied", "payload": {"display_name": "Example Bank", "role": "Industry enterprise", "commercial_significance": "Material participant", "evidence_status": "Evidence supplied"}},
        {"external_id": "MP-1", "record_class": "market_participant", "truth_class": "human_supplied", "payload": {"display_name": "Example Supplier", "participant_role": "Technology supplier"}},
        {"external_id": "OPP-1", "record_class": "opportunity", "truth_class": "hypothesis", "payload": {"description": "Modernise customer servicing", "classification_state": "Unclassified", "uncertainty": "Buyer timing is unknown"}},
        {"external_id": "OBS-1", "record_class": "observation", "truth_class": "evidence_backed", "payload": {"statement": "Service demand is moving to digital channels", "commercial_consequence": "Prioritise assisted digital service", "evidence_basis": "Owner-supplied observation"}},
        {"external_id": "UNK-1", "record_class": "unknown", "truth_class": "unknown", "payload": {"description": "Adoption timing is not known"}},
        {"external_id": "CON-1", "record_class": "contradiction", "truth_class": "human_supplied", "payload": {"description": "Branch demand remains material"}},
    ]
    run, _ = stage(monkeypatch, tmp_path, records)
    from cios.applications.flora.blueprint_import.views import review_page
    html, status = review_page(run.import_run_id, HEADERS)
    assert status == 200
    return html


def test_review_is_executive_first_and_technical_content_is_collapsed(monkeypatch, tmp_path):
    html = _review(monkeypatch, tmp_path)
    assert html.index("candidate-review-identity") < html.index("Executive intelligence summary") < html.index("Material proposed conclusions")
    assert html.index("Material proposed conclusions") < html.index("What acceptance would change") < html.index("Decisions required before promotion")
    assert "No canonical change has yet occurred" in html
    assert "Architect disclosure" in html and "Technical disclosure" in html
    assert html.index("Technical disclosure") < html.index("Review job ID")
    assert "Raw technical payload" in html and "Filters" in html


def test_review_preserves_trust_and_business_domain_paths(monkeypatch, tmp_path):
    html = _review(monkeypatch, tmp_path)
    assert "Why should I believe this?" in html
    assert "Inspect supporting Evidence" in html
    assert "What could make this wrong, incomplete or unsafe to rely upon?" in html
    assert "Adoption timing is not known" in html and "Branch demand remains material" in html
    assert "Return to Inspect with this candidate context" in html


def test_business_record_table_leads_with_owner_supplied_meaning():
    from cios.applications.flora.blueprint_import.views import _candidate_table
    candidates = [{"candidate_record_id": "c1", "original_source_id": "ENT-TECH-1", "candidate_object_class": "enterprise", "validation_status": "accepted", "payload": {"display_name": "Example Bank", "role": "Industry enterprise", "commercial_significance": "Material participant", "evidence_status": "Evidence supplied", "uncertainty": "Role needs confirmation"}}]
    html = _candidate_table("Enterprises detail", candidates, {"c1": {"effect_type": "create"}}, 1, 25)
    assert "Example Bank" in html and "Industry enterprise" in html and "Material participant" in html
    assert html.index("Business-readable name") < html.index("Proposed effect")
    assert "External ID" not in html and "Canonical class" not in html
    technical = _candidate_table("Enterprises detail", candidates, {}, 1, 25, technical=True)
    assert "External ID" in technical and "Canonical class" in technical and "Raw technical payload" in technical


def test_disclosures_use_native_keyboard_accessible_details(monkeypatch, tmp_path):
    html = _review(monkeypatch, tmp_path)
    assert "<details class='card analyst-depth'>" in html
    assert "<details class='card architect-depth'>" in html
    assert "<details class='card technical-depth'>" in html
    assert "architect-depth' open" not in html and "technical-depth' open" not in html
