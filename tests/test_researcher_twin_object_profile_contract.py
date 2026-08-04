import json
import zipfile

from cios.applications.flora.blueprint_import.researcher_profile_adapter import CONTRACT, adapt_researcher_payload

TEL001 = "docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip"


def _first(path):
    with zipfile.ZipFile(TEL001) as archive:
        data = json.loads(archive.read(path))
    return data[0] if isinstance(data, list) else data


def test_flora_adapter_is_driven_by_governed_profile_contract():
    assert CONTRACT["document_id"] == "TOP-RESEARCHER-PORTABLE-OBJECTS-v1"
    assert "opportunity_hypothesis" in CONTRACT["profiles"]


def test_tel001_opportunity_shape_projects_required_owner_fields():
    _, payload = adapt_researcher_payload("opportunity_hypothesis", _first("content/source/opportunity_objects_wave5.json"))
    assert payload["client_problem"]
    assert payload["procurement_timing"]
    assert payload["value_range"]
    assert payload["affected_enterprises"]
    assert payload["mapping_diagnostics"]["contract_id"] == CONTRACT["document_id"]


def test_tel001_supported_object_families_share_profile_contract():
    cases = {
        "industry_twin": "content/source/industry_overview_wave5.json",
        "enterprise_twin": "content/source/enterprise_dossiers_wave5.json",
        "market_participant_twin": "content/source/market_participant_profiles_wave5.json",
        "transformation_programme": "content/source/programme_objects_wave5.json",
        "opportunity_hypothesis": "content/source/opportunity_objects_wave5.json",
        "ai_reinvention_assessment": "content/source/reinvention_assessments_wave5.json",
    }
    for record_class, path in cases.items():
        canonical_class, payload = adapt_researcher_payload(record_class, _first(path))
        assert canonical_class in CONTRACT["profiles"]
        assert payload["mapping_diagnostics"]["mapped_fields"], record_class
