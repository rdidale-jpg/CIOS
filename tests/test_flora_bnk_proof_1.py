import copy

import pytest

from cios.applications.flora import banking_value_system as proof
from cios.applications.flora import visual_streams as streams
from tests.test_flora_eai2_integration import changed_release
from tests.test_flora_f1_642 import authority, permitted

BANKING = "/industries/banking"
LLOYDS = "/enterprises/lloyds"


@pytest.mark.parametrize("stage", proof.STAGES)
def test_banking_value_system_selects_finite_editorial_stage(stage):
    page = streams.render(BANKING, {"selected": [stage]})
    assert f'<h1>{proof.escape(proof.STAGES[stage][0])}</h1>' in page
    assert "Nationwide Group earnings" in page
    assert "IND-PART-LLOYDS" not in page


@pytest.mark.parametrize("query", [
    {"selected": ["garbage"]},
    {"selected": ["funding", "funding"]},
])
def test_unknown_or_duplicate_selected_role_is_rejected(query):
    with pytest.raises(ValueError):
        streams.resolve(BANKING, query)
    with pytest.raises(ValueError):
        streams.resolve(LLOYDS, {"selected": ["funding"]})


@pytest.mark.parametrize("mutation", ["rights", "private", "withdrawn", "source_host"])
def test_ctp_pulse_follows_existing_lifecycle(mutation, tmp_path, monkeypatch):
    assert 'id="banking-change"' in streams.render(BANKING, {"stream": ["forces"]})
    changed_release("provider", mutation, tmp_path, monkeypatch)
    assert 'id="banking-change"' not in streams.render(BANKING, {"stream": ["forces"]})
    assert "Deposits &amp; lending" in streams.render(BANKING, {})


@pytest.mark.parametrize("field,value", [
    ("entity_scope", "Lloyds Bank plc"),
    ("statement", "Changed issuer statement"),
    ("superseded", True),
])
def test_envoy_claim_changes_suppress_dependent_relationship(field, value):
    ctx = streams.Context("lloyds", "landscape", detail="technology")
    data = copy.deepcopy(streams.current_data(ctx))
    assert "Envoy collaborator" in proof.lloyds_scope(data)
    claim = next(claim for claim in data["claims"] if claim["id"] == "LBG-ENVOY-GOOGLE")
    claim[field] = value
    assert proof.lloyds_scope(data) == ""


def test_positive_relationship_is_owner_inspection_only(permitted):
    from cios.applications.flora import visual_panels
    from cios.applications.flora.security_store import canonical

    store, headers, _ = permitted
    query = {"lens": ["inspection"], "selected": ["clearing"]}
    proof_id = "IND-PART-LLOYDS"
    assert proof_id in visual_panels.research_inspection(BANKING, query, headers)
    assert proof_id not in streams.render(BANKING, {"selected": ["clearing"]}, headers)
    with store.transaction() as db:
        db.execute("UPDATE memberships SET roles=?", (canonical(["package.inspect"]),))
    with pytest.raises(PermissionError):
        visual_panels.research_inspection(BANKING, query, headers)
