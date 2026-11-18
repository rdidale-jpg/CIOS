import json
from urllib.parse import parse_qs, urlsplit

import pytest

from cios.applications.flora import visual_streams as v
from cios.applications.flora.public_routes import owner_inspection_request_target, public_request_target
from tests.test_flora_eai2_integration import changed_release
from tests.test_flora_uxr1_650 import main, retained

BANKING = "/industries/banking"
LLOYDS = "/enterprises/lloyds"


def test_same_payment_subject_two_distinct_readings():
    query = {"stream": ["landscape"], "detail": ["payments"]}
    facts = main(v.render(BANKING, query))
    insight = main(v.render(BANKING, {**query, "reading": ["insight"]}))
    assert "Conceptual" in facts and "Initiate" in facts and "Service income" not in facts
    assert "Conceptual" in insight and "Service income" in insight and "Initiate" not in insight
    assert 'aria-current=page>Facts' in facts and 'aria-current=page>FLORA Insight' in insight
    assert "Pay.UK" not in facts + insight
    ctx = v.resolve(BANKING, {**query, "reading": ["insight"]})
    assert parse_qs(urlsplit(v.url(ctx, reading="insight")).query) == {**query, "reading": ["insight"]}
    assert "reading=" not in v.url(ctx, selected="nationwide", detail="")
    assert "reading=" not in v.stream_url(ctx, "forces")


@pytest.mark.parametrize("bad", ["", "unknown", "Insight"])
def test_unknown_reading_mode_fails_closed(bad):
    with pytest.raises(ValueError):
        v.resolve(BANKING, {"reading": [bad]})
    assert not public_request_target(BANKING + "?reading=" + bad)


def test_duplicate_modes_and_inspection_mix_rejected():
    with pytest.raises(ValueError):
        v.resolve(BANKING, {"reading": ["facts", "insight"]})
    assert not public_request_target(BANKING + "?reading=facts&reading=insight")
    assert not owner_inspection_request_target(BANKING + "?lens=inspection&reading=insight")
    assert not public_request_target(BANKING + "?lens=inspection&reading=insight")
    assert public_request_target(BANKING + "?detail=payments&reading=insight")


@pytest.mark.parametrize("mutation", ["rights", "private", "withdrawn", "source_host"])
def test_provider_evidence_gates_both_modes(mutation, tmp_path, monkeypatch):
    query = {"stream": ["forces"], "agenda": ["provider-oversight"]}
    assert "Google Cloud EMEA Limited" in main(v.render(BANKING, query))
    assert "services used" in main(v.render(BANKING, {**query, "reading": ["insight"]}))
    changed_release("provider", mutation, tmp_path, monkeypatch)
    assert "Google Cloud EMEA Limited" not in main(v.render(BANKING, query))
    assert "No supported FLORA Insight" in main(v.render(BANKING, {**query, "reading": ["insight"]}))


def test_nationwide_keeps_both_bases_and_withdrawal_gates_analysis(retained):
    query = {"selected": ["nationwide"]}
    facts = main(v.render(BANKING, query))
    insight = main(v.render(BANKING, {**query, "reading": ["insight"]}))
    assert "6,378 − 4,021 − 331 = 2,026" in facts + insight
    assert "2,026 + 1 − 138 − 399 = 1,490" in insight
    assert "Customer complaints · Society" in facts
    assert "100,886" not in insight
    package = json.loads(retained.read_text())
    package["sources"][1]["withdrawn"] = True
    retained.write_text(json.dumps(package))
    assert "6,378" not in main(v.render(BANKING, query))
    assert "No supported FLORA Insight" in main(v.render(BANKING, {**query, "reading": ["insight"]}))


def test_lloyds_operating_disclosure_and_implication_use_same_capability():
    query = {"stream": ["inside"], "detail": ["technology"]}
    facts = main(v.render(LLOYDS, query))
    insight = main(v.render(LLOYDS, {**query, "reading": ["insight"]}))
    assert "Conceptual · Group capability" in facts
    assert "data-semantic-type=\"insight\"" not in facts
    assert "monitoring part of the operating process" in insight
    assert "legal contracting entity remain unverified" in insight


@pytest.mark.parametrize("flag,value", [
    ("freshness", "superseded"),
    ("core_contradiction", True),
    ("owner_only", True),
])
def test_payment_insight_suppressed_when_its_model_is_restricted(monkeypatch, flag, value):
    ctx = v.Context("banking", "landscape", detail="payments")
    data = v.current_data(ctx)
    claim = next(claim for claim in data["claims"] if claim["id"] == "UK-VALUE")
    claim[flag] = value
    monkeypatch.setattr(v, "current_data", lambda ctx: data)
    query = {"detail": ["payments"]}
    assert "Initiate" in main(v.render(BANKING, query))
    html = v.render(BANKING, {**query, "reading": ["insight"]},
                    {"X-Flora-User": "owner", "X-Flora-Roles": "cios_owner"})
    assert "No supported FLORA Insight" in main(html)
    assert "Service income" not in main(html)
    assert "Guest" in html


@pytest.mark.parametrize("scope,stream", [
    (scope, stream)
    for scope, spec in v.SCOPES.items()
    for stream in spec["streams"]
])
def test_default_scene_has_no_authorial_insight(scope, stream):
    path = v.SCOPES[scope]["route"]
    facts = main(v.render(path, {"stream": [stream]}))
    assert 'aria-current=page>Facts' in facts
    assert 'data-semantic-type="insight"' not in facts
    assert "FLORA INSIGHT" not in facts
    analysis = main(v.render(path, {"stream": [stream], "reading": ["insight"]}))
    assert 'aria-current=page>FLORA Insight' in analysis


def test_lloyds_capability_map_respects_disclosure_lifecycle(monkeypatch):
    query = {"stream": ["inside"], "detail": ["technology"]}
    ctx = v.resolve(LLOYDS, query)
    data = v.current_data(ctx)
    claim = next(item for item in data["claims"] if item["id"] == "LBG-ENVOY-GOOGLE")
    claim["withdrawn"] = True
    monkeypatch.setattr(v, "current_data", lambda ctx: data)
    analysis = main(v.render(LLOYDS, {**query, "reading": ["insight"]}))
    assert "Envoy" in analysis and "Disclosed collaboration" not in analysis
    assert "Google Cloud EMEA Limited" not in analysis
