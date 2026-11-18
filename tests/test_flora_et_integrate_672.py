import pytest

from cios.applications.flora import easyjet_capabilities as et
from cios.applications.flora import visual_streams as v
from cios.applications.flora.public_routes import public_request_target


@pytest.mark.parametrize("capability", et.CAPABILITIES)
@pytest.mark.parametrize("stream", ["landscape", "inside", "forces"])
@pytest.mark.parametrize("mode", ["facts", "insight"])
def test_easyjet_scene_keeps_exact_selection(capability, stream, mode):
    query = {"detail": [capability], "stream": [stream], "reading": [mode]}
    ctx = v.resolve(v.EASYJET_ROUTE, query)
    html = v.render(v.EASYJET_ROUTE, query)
    assert et.CAPABILITIES[capability] in html
    assert f'data-stream="{stream}"' in html
    assert f'detail={capability}' in v.stream_url(ctx, "forces")
    assert ("reading=insight" in v.stream_url(ctx, "forces")) == (mode == "insight")
    assert "reading=" not in v.url(ctx, detail="network-planning")
    assert "What's changing?" not in html and "AV-FLEET" not in html
    assert ('data-semantic-type="insight"' in html) == (mode == "insight")


@pytest.mark.parametrize("query", [
    {"stream": ["changing"]}, {"detail": ["private"]}, {"reading": ["draft"]},
    {"detail": ["fleet-operations", "customer-service"]}, {"workspace": ["private"]},
])
def test_invalid_context_fails_closed(query):
    with pytest.raises(ValueError):
        v.resolve(v.EASYJET_ROUTE, query)


@pytest.mark.parametrize("flag", ["withdrawn", "owner_only", "core_contradiction"])
def test_source_lifecycle_suppresses_both_modes(monkeypatch, flag):
    data = et._data()
    source = next(row for row in data["sources"] if row["id"] == "SRC-AV-AR25")
    source[flag] = True
    monkeypatch.setattr(et, "_read_assessment", lambda: data)
    query = {"stream": ["inside"], "detail": ["network-planning"]}
    facts = v.render(v.EASYJET_ROUTE, query)
    analysis = v.render(v.EASYJET_ROUTE, {**query, "reading": ["insight"]})
    assert "1,202 routes" not in facts + analysis
    assert "Conceptual · operating activities" in facts
    assert "No supported FLORA Insight" in analysis
    assert et.fact(data, "AV-MRO") is not None


def test_exact_public_route_and_image():
    assert public_request_target(v.EASYJET_ROUTE + "?detail=customer-service&reading=insight")
    assert not public_request_target(v.EASYJET_ROUTE + "?detail=customer-service&workspace=private")
    assert not public_request_target(v.EASYJET_ROUTE + "?reading=facts&reading=insight")
    assert v.asset(v.EASYJET_ART)[1] == "image/webp"
