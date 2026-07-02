from pathlib import Path

from cios.applications.flora.live.progress import default_state, percent_complete, write_state, read_state
from cios.applications.flora.observatory.engine import build_observatory
from cios.applications.flora.observatory.newton import momentum, recommendation_engine
from cios.applications.flora.observatory.views import observatory_page, organisation_observatory_page
from cios.applications.flora.workspace.views import landing_page, radar_page


def test_executive_summary_cards_major_pages():
    assert "Executive Summary Cards" in landing_page()
    assert "Executive Summary Cards" in radar_page()
    assert "Executive Summary Cards" in observatory_page()
    assert "Executive Summary Cards" in organisation_observatory_page("BT")


def test_organisation_three_layer_and_diagnostics_reframe():
    html = organisation_observatory_page("BT")
    assert "Layer 1 — 30-second briefing" in html
    assert "Layer 2 — 3-minute briefing" in html
    assert "Layer 3 — 30-minute investigation" in html
    snapshot = html.split("<h2>Executive Snapshot</h2>", 1)[1].split("</section>", 1)[0]
    assert "Accepted evidence count" not in snapshot
    assert "Reasoning Diagnostics" in html


def test_commercial_readiness_recommendations_and_momentum():
    obs = build_observatory()
    recs = recommendation_engine(obs)
    assert len(recs) == 5
    assert all(r.trace["evidence"] for r in recs)
    assert "Commercial Readiness Index" in radar_page()
    assert "Unknown" in organisation_observatory_page("BT")
    seeded = next(o for o in obs.organisations if not any(e.is_live and e.organisation == o.organisation for e in obs.evidence))
    assert momentum(obs, seeded).label == "Unknown"


def test_no_generic_seeded_thesis_and_evidence_id_noise_suppressed():
    assert "Multiple public signals suggest BT may be entering" not in organisation_observatory_page("BT")
    assert "No strong thesis yet — evidence collection required." in observatory_page()
    top = organisation_observatory_page("BT").split("Layer 1 — 30-second briefing", 1)[1].split("Layer 3 — 30-minute investigation", 1)[0]
    assert "ETO-EV-" not in top


def test_live_collection_status_fields_and_percent(tmp_path, monkeypatch):
    from cios.applications.flora.live import progress
    monkeypatch.setattr(progress, "STATE_DIR", tmp_path)
    monkeypatch.setattr(progress, "STATE_PATH", tmp_path / "collection_run_state.json")
    state = default_state() | {"run_id": "run", "sources_total": 4, "sources_attempted": 1}
    write_state(state)
    loaded = read_state()
    assert set(default_state()) <= set(loaded)
    assert percent_complete(1, 4) == 25
    assert percent_complete(5, 4) == 100


def test_no_llm_database_broad_crawling_imports_newton_files():
    text = "\n".join(Path(p).read_text(encoding="utf-8") for p in [
        "cios/applications/flora/observatory/newton.py",
        "cios/applications/flora/live/progress.py",
    ])
    forbidden = ["openai", "anthropic", "langchain", "sqlalchemy", "sqlite3", "psycopg", "scrapy"]
    assert not any(word in text.lower() for word in forbidden)
