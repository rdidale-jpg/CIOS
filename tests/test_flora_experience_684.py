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
        facts = main(v.render(path, query))
        insight = main(v.render(path, {**query, "reading": ["insight"]}))
        assert 'aria-current=page>Facts' in facts
        assert 'data-semantic-type="insight"' not in facts
        if path == "/enterprises/lloyds":
            expected = {"inside": "Conceptual operating mechanism",
                        "landscape": "What if the interest gap narrows?",
                        "forces": "If funding costs rise faster than asset yields"}
            assert expected[stream] in insight
            assert expected[stream] not in facts
            assert 'data-semantic-type="insight"' not in insight
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
        assert "Conceptual banking model" in roots["landscape"]
        assert "What Lloyds Group reported" in roots["landscape"]
        assert "£502.8bn" in roots["landscape"]
        assert "£502.8bn" not in roots["inside"]


@pytest.mark.parametrize("scope,keys", [("uk", experience.UK_DIMENSIONS), ("banking", experience.BANKING_FORCES)])
def test_force_lenses_retain_subject_and_reject_outside_scope(scope, keys):
    path = v.SCOPES[scope]["route"]
    for key in keys:
        query = {"stream": ["forces"], "detail": [key]}
        facts = main(v.render(path, query))
        insight = main(v.render(path, {**query, "reading": ["insight"]}))
        assert f'detail={key}&amp;reading=insight' in facts
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
    assert "Conceptual competitive mechanism" not in facts
    for html in (facts, insight):
        assert 'data-semantic-type="insight"' not in html
        assert "4 November 2026" not in html
        assert "Google Cloud EMEA Limited" not in html


@pytest.mark.parametrize("mode", ["facts", "insight"])
def test_lloyds_envoy_withdrawal_leaves_independent_conceptual_workflow(monkeypatch, mode):
    path = "/enterprises/lloyds"
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
    assert 'detail=servicing&amp;reading=insight#visual-content' in html
    expected = 'detail=risk-assessment&amp;reading=insight#lv-selection' if mode == "insight" else (
        'detail=risk-assessment#lv-selection'
    )
    assert expected in html
    assert "Lloyds’ thresholds" not in html
    with pytest.raises(ValueError):
        v.resolve(path, {**selector, "stream": ["forces"]})


def test_lloyds_withdrawn_rate_retains_only_conceptual_transmission(monkeypatch):
    path = "/enterprises/lloyds"
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
