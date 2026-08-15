"""Rendered TEL-001 population and EI-002 relationship reconciliation."""
from __future__ import annotations
from collections import Counter
import hashlib, json, re
from pathlib import Path

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page, _semantic_candidates, _dossier
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, business_collections, business_object_id, enterprise_associations, query_subject_associations, resolve_relationships

FIXTURE = Path("docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip")
ORACLE = json.loads(Path("tests/fixtures/tel001_expected_truth.json").read_text())
EXPECTED_ASSOCIATIONS = {
    "ENT-BT": ({"PROG-BT-TRANSFORMATION"}, {"OPP-BT-AI-ENGINEERING", "OPP-BT-AIOPS", "OPP-BT-VERIZON-JV-INTEGRATION"}),
    "ENT-OPENREACH": ({"PROG-OPENREACH-FTTP"}, {"OPP-OPENREACH-FIBRE-AUTOMATION", "OPP-OPENREACH-CP-ENABLEMENT", "OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE"}),
    "ENT-VMO2": ({"PROG-VMO2-LUMI-AI", "PROG-VMO2-MOBILE-TRANSFORMATION"}, {"OPP-VMO2-AI-CX", "OPP-VMO2-MOBILE-RAN-AI-ASSURANCE", "OPP-VMO2-NEXFIBRE-MIGRATION"}),
    "ENT-VODAFONETHREE": ({"PROG-VT-5G-SA", "PROG-VT-INTEGRATION"}, {"OPP-VT-NETWORK-AI-OPS", "OPP-VT-ENTERPRISE-5G", "OPP-VT-WHOLESALE-REMEDY-ASSURANCE"}),
    "ENT-CITYFIBRE": ({"PROG-CITYFIBRE-WHOLESALE"}, {"OPP-CITYFIBRE-PROJECT-GIGABIT", "OPP-CITYFIBRE-WHOLESALE"}),
    "ENT-TALKTALK": ({"PROG-TALKTALK-PXC-DEMERGER"}, {"OPP-TALKTALK-COST", "OPP-PXC-PLATFORM-EFFICIENCY"}),
}


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
    package, _summary, twin = _runtime(monkeypatch, tmp_path)
    for enterprise in twin.enterprises:
        programme_evidence = query_subject_associations(twin, enterprise.identity_key, {"transformation_programme"})
        opportunity_evidence = query_subject_associations(twin, enterprise.identity_key, {"opportunity_hypothesis"})
        expected_programmes = {row.related_business_object_id for row in programme_evidence}
        expected_opportunities = {row.related_business_object_id for row in opportunity_evidence}
        html, route_status = executive_workspace_page(
            package.import_run_id, {}, view="enterprise", enterprise_id=enterprise.identity_key)
        assert route_status == 200
        actual_programmes = set(re.findall(r"<article data-business-object-id='([^']+)'", html))
        actual_opportunities = set(re.findall(r"<div data-business-object-id='([^']+)'", html))
        assert actual_programmes == expected_programmes
        assert actual_opportunities == expected_opportunities
        assert (expected_programmes, expected_opportunities) == EXPECTED_ASSOCIATIONS[enterprise.identity_key.upper()]
    bt = next(e for e in twin.enterprises if e.identity_key.casefold() == "ent-bt")
    programmes = enterprise_associations(twin, bt, {"transformation_programme"})
    opportunities = enterprise_associations(twin, bt, {"opportunity_hypothesis"})
    assert not any(business_object_id(row[0]) == "PROG-BT-VERIZON-JV" for row in programmes)
    assert not any("PROG-BT-VERIZON-JV" in {r.source_id, r.target_id} for r in resolve_relationships(twin))
    bt_programme = next(row for row in programmes if business_object_id(row[0]) == "PROG-BT-TRANSFORMATION")
    assert bt_programme[1:] == ("Enterprise owns Programme", "REL-W2-001")
    bt_ai = next(row for row in opportunities if business_object_id(row[0]) == "OPP-BT-AI-ENGINEERING")
    assert bt_ai[1:] == ("Opportunity targets Enterprise", "REL-W2-014")
    bt_opportunity = next(row for row in opportunities if business_object_id(row[0]) == "OPP-BT-VERIZON-JV-INTEGRATION")
    assert bt_opportunity[1:] == ("Opportunity targets Enterprise", "REL-W4-183")
    traces = {row.relationship_id: row for row in query_subject_associations(twin, "ENT-BT")}
    assert traces["REL-W2-001"].direction == "outgoing"
    assert traces["REL-W2-001"].subject_endpoint == "ENT-BT"
    assert traces["REL-W2-001"].related_endpoint == "PROG-BT-TRANSFORMATION"
    assert traces["REL-W2-014"].direction == "incoming"
    assert traces["REL-W2-014"].related_business_object_id == "OPP-BT-AI-ENGINEERING"
    assert all(row.resolution_state == "candidate relationship resolved" for row in traces.values())


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


def test_relationship_resolution_retains_unresolved_endpoint_truth():
    def row(identifier, kind, **payload):
        return {"candidate_record_id": identifier, "original_source_id": identifier, "candidate_object_class": kind, "validation_status": "accepted", "payload": payload}
    twin = assemble_semantic_twin([
        row("ENT-A", "enterprise_twin", enterprise_id="ENT-A", name="A"),
        row("OPP-X", "opportunity_hypothesis", title="X"),
        row("REL-OK", "relationship", source="OPP-X", target="ENT-A", relationship_type="Opportunity targets Enterprise"),
        row("REL-BAD", "relationship", source="OPP-MISSING", target="ENT-A", relationship_type="Opportunity targets Enterprise"),
    ])
    rows = resolve_relationships(twin)
    assert [(r.relationship.original_id, r.resolved) for r in rows] == [("REL-OK", True), ("REL-BAD", False)]
    assert rows[1].source is None and rows[1].target is not None
    assert rows[0].status == "candidate relationship resolved"
    assert rows[0].reason == "candidate endpoints resolved in import scope"
    assert rows[1].status == "candidate relationship unresolved"
    assert rows[1].reason == "endpoint missing"


def test_candidate_resolution_is_read_only_and_import_scoped():
    def row(identifier, kind, **payload):
        return {"candidate_record_id": identifier, "original_source_id": identifier,
                "candidate_object_class": kind, "validation_status": "accepted",
                "governance_state": "candidate", "payload": payload}

    first = assemble_semantic_twin([
        row("ENT-A", "enterprise_twin", enterprise_id="ENT-A", name="A"),
        row("PROG-P", "transformation_programme", title="P"),
        row("REL-R", "relationship", source="ENT-A", target="PROG-P",
            relationship_type="Enterprise owns Programme"),
    ])
    second = assemble_semantic_twin([
        row("ENT-A", "enterprise_twin", enterprise_id="ENT-A", name="Other A"),
        row("PROG-OTHER", "transformation_programme", title="Other"),
    ])
    assert resolve_relationships(first)[0].resolved
    assert [business_object_id(item[0]) for item in enterprise_associations(
        first, first.enterprises[0], {"transformation_programme"})] == ["PROG-P"]
    assert not resolve_relationships(second)
    assert all(obj.governance == "candidate" for obj in first.objects)
    assert all(obj.validation_status == "accepted" for obj in first.objects)


def test_colliding_candidate_import_ids_cannot_cross_link():
    def row(identifier, kind, **payload):
        return {"candidate_record_id": identifier, "original_source_id": identifier,
                "candidate_object_class": kind, "validation_status": "accepted", "payload": payload}
    first = assemble_semantic_twin([
        row("ENT-A", "enterprise_twin", enterprise_id="ENT-A", name="A"),
        row("REL-R", "relationship", source="ENT-A", target="PROG-COLLISION",
            relationship_type="Enterprise owns Programme"),
    ])
    second = assemble_semantic_twin([
        row("ENT-A", "enterprise_twin", enterprise_id="ENT-A", name="Other A"),
        row("PROG-COLLISION", "transformation_programme", title="Other import programme"),
    ])
    assert not resolve_relationships(first)[0].resolved
    assert query_subject_associations(first, "ENT-A") == ()
    assert query_subject_associations(second, "ENT-A") == ()


def test_query_preserves_duplicate_evidence_while_executive_set_deduplicates():
    def row(identifier, kind, **payload):
        return {"candidate_record_id": identifier, "original_source_id": identifier,
                "candidate_object_class": kind, "validation_status": "accepted", "payload": payload}
    twin = assemble_semantic_twin([
        row("ENT-A", "enterprise_twin", enterprise_id="ENT-A", name="A"),
        row("PROG-P", "transformation_programme", title="P"),
        row("REL-1", "relationship", source="ENT-A", target="PROG-P", relationship_type="Enterprise owns Programme"),
        row("REL-2", "relationship", source="ENT-A", target="PROG-P", relationship_type="Enterprise owns Programme"),
    ])
    assert [item.relationship_id for item in query_subject_associations(twin, "ENT-A")] == ["REL-1", "REL-2"]
    assert [business_object_id(item[0]) for item in enterprise_associations(
        twin, twin.enterprises[0], {"transformation_programme"})] == ["PROG-P"]
    assert _dossier(twin.enterprises[0], twin, "run", None).count("data-business-object-id='PROG-P'") == 1


def test_truthful_zero_associations_pass_all_three_stages():
    candidate = {"candidate_record_id": "ENT-Z", "original_source_id": "ENT-Z",
                 "candidate_object_class": "enterprise_twin", "validation_status": "accepted",
                 "payload": {"enterprise_id": "ENT-Z", "name": "Zero"}}
    twin = assemble_semantic_twin([candidate])
    assert query_subject_associations(twin, "ENT-Z") == ()
    assert enterprise_associations(twin, twin.enterprises[0], {"transformation_programme"}) == ()
    html = _dossier(twin.enterprises[0], twin, "run", None)
    assert "data-business-object-id=" not in html


def test_dimension_missing_does_not_repeat_operating_model():
    def row(identifier, kind, **payload):
        return {"candidate_record_id": identifier, "original_source_id": identifier, "candidate_object_class": kind, "validation_status": "accepted", "payload": payload}
    twin = assemble_semantic_twin([row("ENT-A", "enterprise_twin", enterprise_id="ENT-A", name="A", operating_model="Federated operating model")])
    html = _dossier(twin.enterprises[0], twin, "run", None)
    financial = html.split("<h2>Financial Position</h2>", 1)[1].split("</section>", 1)[0]
    assert "Federated operating model" not in financial
    assert "No complete financial measure is supplied" in financial
    assert "Not supplied" in financial


def test_diagnostics_use_same_population_and_association_owner(monkeypatch, tmp_path):
    package, _summary, _twin = _runtime(monkeypatch, tmp_path)
    html, status = executive_workspace_page(package.import_run_id, {}, view="diagnostics")
    assert status == 200
    assert "Business Object Population Reconciliation" in html
    assert re.search(r"<td>Opportunities</td><td>17</td><td>17</td><td>17</td><td>17</td><td>0</td><td>0</td><td>PASS</td>", html)
    assert re.search(r"<td>Programmes</td><td>13</td><td>13</td><td>13</td><td>13</td><td>0</td><td>0</td><td>PASS</td>", html)
    assert "Enterprise Association Reconciliation" in html
    for enterprise_id, (programmes, opportunities) in EXPECTED_ASSOCIATIONS.items():
        assert enterprise_id in html
        assert all(identifier in html for identifier in programmes | opportunities)
    assert "Duplicates collapsed" in html
    assert "Source expected Programmes" in html and "Query-resolved Programmes" in html
    assert "Source expected Opportunities" in html and "Query-resolved Opportunities" in html
    assert "Missing at query" in html and "Missing at render" in html
    assert "Relationship Resolution Reconciliation" in html
    assert "Executive Dimension Reconciliation" in html
    assert "Candidate-resolved Relationships" in html
    assert re.search(r"<td>308</td><td>308</td><td>252</td><td>56</td><td>0</td><td>56</td><td>0</td><td>0</td><td>0</td><td>0</td>", html)
