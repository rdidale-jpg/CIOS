"""Rendered TEL-001 population and EI-002 relationship reconciliation."""
from __future__ import annotations
from collections import Counter
import hashlib, json, re
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page, _semantic_candidates, _dossier
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, business_collections, business_object_id, enterprise_associations

FIXTURE = Path("docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip")
ORACLE = json.loads(Path("tests/fixtures/tel001_expected_truth.json").read_text())


def _runtime(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    package = BlueprintPackageRegistry().receive(FIXTURE.read_bytes(), FIXTURE.name, "population-auditor")
    BlueprintPackageValidator().validate_and_stage(package.package_ref, "population-auditor")
    summary = BlueprintPackageValidator().staging_summary(package.import_run_id)
    twin = assemble_semantic_twin(_semantic_candidates(package, summary["candidates"]))
    return package, summary, twin


def test_real_routes_reconcile_business_object_population(monkeypatch, tmp_path):
    package, summary, twin = _runtime(monkeypatch, tmp_path)
    assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == ORACLE["fixture_sha256"]
    assert Counter(c["candidate_object_class"] for c in summary["candidates"] if c["validation_status"] == "accepted")["opportunity_hypothesis"] == 17
    collections = {c.key: c.objects for c in business_collections(twin, include_empty=True)}
    assert len({business_object_id(o) for o in collections["opportunities"]}) == 17
    assert len({business_object_id(o) for o in twin.objects if o.kind == "transformation_programme"}) == 13

    opportunities, status = executive_workspace_page(package.import_run_id, {}, view="aspect", collection="opportunities")
    programmes, programme_status = executive_workspace_page(package.import_run_id, {}, view="aspect", collection="major-programmes")
    assert status == programme_status == 200
    opportunity_ids = re.findall(r"data-business-object-family='Opportunity' data-business-object-id='([^']+)'", opportunities)
    programme_ids = re.findall(r"data-business-object-family='Programme' data-business-object-id='([^']+)'", programmes)
    expected_opportunities = {business_object_id(o) for o in collections["opportunities"]}
    expected_programmes = {business_object_id(o) for o in twin.objects if o.kind == "transformation_programme"}
    assert len(opportunity_ids) == len(set(opportunity_ids)) == 17
    assert len(programme_ids) == len(set(programme_ids)) == 13
    assert set(opportunity_ids) == expected_opportunities
    assert set(programme_ids) == expected_programmes
    assert "17 opportunities available" in opportunities
    assert not any(c["candidate_object_class"] == "opportunity_qualification_scorecard" and c["original_source_id"] in opportunities for c in summary["candidates"])


def test_all_enterprise_rendered_associations_equal_canonical_relationship_sets(monkeypatch, tmp_path):
    _package, _summary, twin = _runtime(monkeypatch, tmp_path)
    for enterprise in twin.enterprises:
        expected_programmes = {business_object_id(row[0]) for row in enterprise_associations(twin, enterprise, {"transformation_programme"})}
        expected_opportunities = {business_object_id(row[0]) for row in enterprise_associations(twin, enterprise, {"opportunity_hypothesis"})}
        html = _dossier(enterprise, twin, "run", None)
        actual_programmes = set(re.findall(r"<article data-business-object-id='([^']+)'", html))
        actual_opportunities = set(re.findall(r"<div data-business-object-id='([^']+)'", html))
        assert actual_programmes == expected_programmes
        assert actual_opportunities == expected_opportunities
    bt = next(e for e in twin.enterprises if e.identity_key.casefold() == "ent-bt")
    assert enterprise_associations(twin, bt, {"transformation_programme"})
    assert enterprise_associations(twin, bt, {"opportunity_hypothesis"})


def test_unrelated_and_reverse_relationship_contract():
    def row(identifier, kind, **payload):
        return {"candidate_record_id": identifier, "original_source_id": identifier, "candidate_object_class": kind, "validation_status": "accepted", "payload": payload}
    twin = assemble_semantic_twin([
        row("ENT-A", "enterprise_twin", enterprise_id="ENT-A", name="A"),
        row("OPP-X", "opportunity_hypothesis", title="X"), row("OPP-Y", "opportunity_hypothesis", title="Y"),
        row("REL-X", "relationship", source="OPP-X", target="ENT-A", relationship_type="Opportunity targets Enterprise"),
    ])
    enterprise = twin.enterprises[0]
    assert [(business_object_id(o), kind, rid) for o, kind, rid in enterprise_associations(twin, enterprise, {"opportunity_hypothesis"})] == [("OPP-X", "Opportunity targets Enterprise", "REL-X")]
    assert "OPP-Y" not in _dossier(enterprise, twin, "run", None)


def test_diagnostics_use_same_population_and_association_owner(monkeypatch, tmp_path):
    package, _summary, _twin = _runtime(monkeypatch, tmp_path)
    html, status = executive_workspace_page(package.import_run_id, {}, view="diagnostics")
    assert status == 200
    assert "Business Object Population Reconciliation" in html
    assert re.search(r"<td>Opportunities</td><td>17</td><td>17</td><td>17</td><td>17</td><td>0</td><td>0</td><td>PASS</td>", html)
    assert re.search(r"<td>Programmes</td><td>13</td><td>13</td><td>13</td><td>13</td><td>0</td><td>0</td><td>PASS</td>", html)
    assert "Enterprise Association Reconciliation" in html
