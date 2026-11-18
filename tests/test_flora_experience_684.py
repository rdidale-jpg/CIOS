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
        if path == "/enterprises/lloyds" and stream == "inside":
            assert "Conceptual operating mechanism" in insight
            assert 'data-semantic-type="insight"' not in insight
        else:
            assert 'data-semantic-type="insight"' in insight
        assert "What's changing?" not in facts
        roots[stream] = facts
    assert "Durable capabilities" in roots["inside"]
    assert roots["inside"].count('href="#ability-0"') == 2
    assert roots["inside"].count('id="ability-0"') == 1
    assert "Durable capabilities" not in roots["landscape"] + roots["forces"]
    assert "Disclosed response" in roots["forces"]
    assert "118,762" not in roots["inside"]
    if path == "/enterprises/lloyds":
        assert 'data-intelligence="service-recovery"' in roots["landscape"]
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
    assert "Envoy" not in before and "Separate Group technology example" in before
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
