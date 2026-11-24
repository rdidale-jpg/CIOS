import pytest

from cios.applications.flora import easyjet_capabilities as easyjet
from cios.applications.flora import experience_composition as experience
from cios.applications.flora import visual_streams as v
from tests.test_flora_uxr1_650 import main


@pytest.mark.parametrize("path", ["/enterprises/lloyds", v.EASYJET_ROUTE])
def test_enterprise_roots_observe_three_different_questions(path):
    roots = {}
    for stream in ("landscape", "inside", "forces"):
        query = {"stream": [stream]}
        facts = main(v.render("/enterprises/lloyds/legacy" if path == "/enterprises/lloyds" else path, query))
        insight = main(v.render("/enterprises/lloyds/legacy" if path == "/enterprises/lloyds" else path, {**query, "reading": ["insight"]}))
        assert 'aria-label="Reading mode"' not in facts
        assert facts == insight
        if path == "/enterprises/lloyds":
            expected = {"inside": "Conceptual operating mechanism",
                        "landscape": "The balance alone does not show funding cost",
                        "forces": "If funding costs rise faster than asset yields"}
            assert expected[stream] in insight
            assert expected[stream] in facts
            if stream == 'landscape':
                assert 'data-semantic-type="insight"' in insight
        else:
            assert 'data-semantic-type="insight"' in insight
        assert "What's changing?" not in facts
        roots[stream] = facts
    assert "Durable capabilities" in roots["inside"]
    if path == v.EASYJET_ROUTE:
        assert roots["inside"].count('href="#ability-0"') == 2
        assert roots["inside"].count('id="ability-0"') == 1
    else:
        assert 'class="lv-matrix"' in roots["inside"]
        assert 'detail=technology-controls' in roots["inside"]
    assert "Durable capabilities" not in roots["landscape"] + roots["forces"]
    assert "Disclosed response" in roots["forces"]
    assert "118,762" not in roots["inside"]
    if path == "/enterprises/lloyds":
        assert 'agenda=service-recovery#agenda-insight' in roots["landscape"]
        assert "118,762" not in roots["landscape"]
        assert "Illustrative banking model" in roots["landscape"]
        assert 'data-semantic-type="reported"' in roots["landscape"]
        assert "£502.8bn" in roots["landscape"]
        assert "£502.8bn" not in roots["inside"]


@pytest.mark.parametrize("scope,keys", [("uk", experience.UK_DIMENSIONS), ("banking", experience.BANKING_FORCES)])
def test_force_lenses_retain_subject_and_reject_outside_scope(scope, keys):
    path = v.SCOPES[scope]["route"]
    for key in keys:
        query = {"stream": ["forces"], "detail": [key]}
        facts = main(v.render(path, query))
        insight = main(v.render(path, {**query, "reading": ["insight"]}))
        assert f'detail={key}' in facts
        assert 'reading=insight' not in facts
        assert 'class="experience-path"' in insight
        with pytest.raises(ValueError):
            v.resolve(path, {"stream": ["landscape"], "detail": [key]})


def test_airline_root_withdrawal_keeps_conceptual_map(monkeypatch):
    data = easyjet._data()
    next(s for s in data["sources"] if s["id"] == "SRC-AV-AR25")["withdrawn"] = True
    monkeypatch.setattr(easyjet, "_read_assessment", lambda: data)
    for mode in ("facts", "insight"):
        html = main(v.render(v.EASYJET_ROUTE, {"stream": ["inside"], "reading": [mode]}))
        assert "356 aircraft" not in html
        assert "Durable capabilities" in html
        assert 'data-semantic-type="insight"' not in html


@pytest.mark.parametrize("key", experience.BANKING_FORCES)
def test_competitive_comparisons_have_no_proxy_provenance(key):
    path = "/industries/banking"
    query = {"stream": ["forces"], "detail": [key]}
    facts = main(v.render(path, query))
    insight = main(v.render(path, {**query, "reading": ["insight"]}))
    assert "Conceptual competitive mechanism" in insight
    assert "Conceptual competitive mechanism" in facts and facts == insight
    for html in (facts, insight):
        assert 'data-semantic-type="insight"' not in html
        assert "4 November 2026" not in html
        assert "Google Cloud EMEA Limited" not in html


@pytest.mark.parametrize("mode", ["facts", "insight"])
def test_lloyds_envoy_withdrawal_leaves_independent_conceptual_workflow(monkeypatch, mode):
    path = "/enterprises/lloyds/legacy"
    root = {"stream": ["inside"], "reading": [mode]}
    dedicated = {**root, "detail": ["technology"]}
    data = v.current_data(v.resolve(path, dedicated))
    before = main(v.render(path, root))
    assert "Envoy" in before.split('class="lv-separate"')[1]
    assert "Envoy" not in before.split('class="lv-separate"')[0]
    assert "Envoy" in main(v.render(path, dedicated))
    next(item for item in data["claims"] if item["id"] == "LBG-ENVOY-CONTROLS")["withdrawn"] = True
    monkeypatch.setattr(v, "current_data", lambda ctx: data)
    assert "Durable capabilities" in main(v.render(path, root))
    assert "Envoy" not in main(v.render(path, root))
    assert "built-in Envoy controls" not in main(v.render(path, dedicated))
    assert "monitoring part of the operating process" not in main(v.render(path, dedicated))


@pytest.mark.parametrize("dimension,topic", [
    ("political", "Public procurement policy"),
    ("social", "Social commitments in public procurement"),
])
def test_two_partial_dimensions_disclose_common_policy_and_scope(dimension, topic):
    for mode in ("facts", "insight"):
        html = main(v.render("/", {"stream": ["forces"], "detail": [dimension], "reading": [mode]}))
        assert f"Partial coverage · {topic}" in html
        assert "same procurement policy" in html
        assert "central-government" in html and "2027-01-01" in html


def test_withdrawn_procurement_policy_suppresses_both_dimensions(monkeypatch):
    from copy import deepcopy

    original = v.visual_v2.insight

    def withdrawn(key):
        item = deepcopy(original(key))
        if key in {"political", "social"}:
            item["sources"][0]["withdrawn"] = True
        return item

    monkeypatch.setattr(v.visual_v2, "insight", withdrawn)
    for key in ("political", "social"):
        html = main(v.render("/", {"stream": ["forces"], "detail": [key], "reading": ["insight"]}))
        assert "Partial coverage" in html
        assert "2027-01-01" not in html
        assert 'data-semantic-type="insight"' not in html
    economic = main(v.render("/", {"stream": ["forces"], "detail": ["economic"]}))
    assert "0.7%" in economic


@pytest.mark.parametrize("mode", ["facts", "insight"])
def test_lloyds_capability_preserves_mode_and_selection(mode):
    path = "/enterprises/lloyds"
    selector = {"stream": ["inside"], "detail": ["servicing"], "reading": [mode]}
    html = main(v.render(path, selector))
    assert "<h2>Servicing</h2>" in html
    assert "Credit origination and servicing" in html
    assert "Customer support and service" in html
    assert 'detail=servicing' in html and 'aria-label="Reading mode"' not in html
    expected = 'detail=risk-assessment#lv-selection'
    assert expected in html
    assert "Lloyds’ thresholds" not in html
    with pytest.raises(ValueError):
        v.resolve(path, {**selector, "stream": ["forces"]})


def test_lloyds_withdrawn_rate_retains_only_conceptual_transmission(monkeypatch):
    path = "/enterprises/lloyds/legacy"
    query = {"stream": ["forces"], "reading": ["insight"]}
    data = v.current_data(v.resolve(path, query))
    claim = next(row for row in data["claims"] if row["id"] == "UK-RATE-NOV26")
    claim["owner_only"] = True
    monkeypatch.setattr(v, "current_data", lambda ctx: data)
    html = main(v.render(path, query))
    assert "Eligible policy observation unavailable" in html
    assert "If funding costs rise faster than asset yields" in html
    assert "No eligible evidence links a Lloyds response" in html
    assert "4 November 2026" not in html


@pytest.mark.parametrize("key,heading", [
    ("funding", "A foundation for lending"),
    ("lending-income", "Turning funding into income"),
    ("profit-costs", "What remains after costs"),
])
def test_lloyds_economic_selection_is_preserved_in_both_readings(key, heading):
    path = "/enterprises/lloyds"
    query = {"stream": ["landscape"], "detail": [key]}
    facts = main(v.render(path, query))
    insight = main(v.render(path, {**query, "reading": ["insight"]}))
    for html in (facts, insight):
        assert f'data-stage="{key}"' in html
        assert f'detail={key}#visual-content' in html
        assert heading in html
        assert "What to investigate" not in html
        assert 'data-identity="BK-ENT-001"' in html
        assert 'detail=economics' in html  # Existing financial presentation remains reachable.
    assert facts == insight
    with pytest.raises(ValueError):
        v.resolve(path, {**query, "stream": ["inside"]})
    with pytest.raises(ValueError):
        v.resolve(path, {**query, "agenda": ["service-recovery"]})


@pytest.mark.parametrize("key,claim,amount", [
    ("funding", "LBG-Q326-DEPOSITS", "£502.8bn"),
    ("lending-income", "LBG-Q326-PROFIT", "£6.6bn"),
    ("profit-costs", "LBG-Q326-PROFIT", "£6.6bn"),
])
def test_lloyds_withdrawn_economic_evidence_leaves_conceptual_structure(monkeypatch, key, claim, amount):
    path = "/enterprises/lloyds"
    query = {"stream": ["landscape"], "detail": [key]}
    data = v.current_data(v.resolve(path, query))
    next(row for row in data["claims"] if row["id"] == claim)["withdrawn"] = True
    monkeypatch.setattr(v, "current_data", lambda ctx: data)
    for mode in ("facts", "insight"):
        html = main(v.render(path, {**query, "reading": [mode]}))
        assert "Illustrative banking model" in html
        assert "No eligible reported measure" not in html  # Omit unavailable values, no admin placeholder.
        assert amount not in html
        if key == "funding":
            assert "£6.3bn" not in html
        assert "What to investigate" not in html
