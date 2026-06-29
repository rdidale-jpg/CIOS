from __future__ import annotations

from cios.applications.flora.live.aggregation import aggregate_live_evidence, adjust_score, attention_organisations
from cios.applications.flora.pipeline import generate_daily_brief
from cios.applications.flora.publisher import morning_edition
from cios.applications.flora.seed_data import sample_watchlist


def _evidence(org: str = "BT", n: int = 2) -> list[dict[str, object]]:
    return [
        {
            "evidence_id": f"LIVE-{org}-{idx}",
            "organisation": org,
            "sector": "Telecommunications",
            "source_id": f"src-{idx % 2}",
            "source_name": f"Source {idx % 2}",
            "source_url": f"https://example.com/{idx}",
            "source_type": "official_newsroom" if idx % 2 else "investor_results",
            "snippet": f"{org} network AI operational efficiency update {idx}",
            "commercial_condition": "Network Intelligence" if idx % 2 else "Operational Efficiency",
            "likely_capability": "Network Operations AI" if idx % 2 else "Operational Efficiency Analytics",
            "evidence_tier": "tier_1_company",
            "confidence": 80,
            "extraction_timestamp": "2026-06-29T00:00:00+00:00",
        }
        for idx in range(n)
    ]


def test_increasing_live_evidence_changes_attention_counts() -> None:
    daily = generate_daily_brief()
    none = attention_organisations(daily.items, {}, sample_watchlist())
    live = attention_organisations(daily.items, aggregate_live_evidence(_evidence("BT", 3) + _evidence("Vodafone", 1)), sample_watchlist())
    assert len(live) != len(none)
    assert live[0] == "BT"


def test_new_evidence_count_reflects_actual_unique_live_count(monkeypatch) -> None:
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("BT", 4))
    ctx = morning_edition.build_publication_context()
    assert ctx["new_evidence_count"] == 4
    assert ctx["new_evidence_label"] == "live unique evidence objects"


def test_what_changed_changes_when_live_evidence_changes(monkeypatch) -> None:
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("BT", 1))
    bt_ctx = morning_edition.build_publication_context()
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("Vodafone", 3))
    vodafone_ctx = morning_edition.build_publication_context()
    assert bt_ctx["what_changed"]["strongest_movers"] != vodafone_ctx["what_changed"]["strongest_movers"]
    assert "Live evidence uplift" in vodafone_ctx["what_changed"]["strongest_movers"][0]["movement"]


def test_score_adjustment_changes_when_live_evidence_exists() -> None:
    metrics = aggregate_live_evidence(_evidence("BT", 2))["BT"]
    adjusted = adjust_score("BT", 70, metrics)
    assert adjusted.final_score > adjusted.base_score
    assert adjusted.live_evidence_bonus > 0


def test_why_this_matters_uses_live_conditions(monkeypatch) -> None:
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("BT", 2))
    ctx = morning_edition.build_publication_context()
    bt_action = next(a for a in ctx["recommended_actions"] if a["organisation"] == "BT")
    assert "Network Intelligence" in bt_action["why_this_matters_to_rob"] or "Operational Efficiency" in bt_action["why_this_matters_to_rob"]


def test_seeded_fallback_still_works_when_no_live_evidence(monkeypatch) -> None:
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: [])
    ctx = morning_edition.build_publication_context()
    assert ctx["new_evidence_count"] == 5
    assert ctx["new_evidence_label"] == "seeded fallback evidence items"
    assert "Seeded fallback" in ctx["what_changed"]["summary"]


def test_why_does_it_matter_changes_when_live_evidence_changes(monkeypatch) -> None:
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("BT", 2))
    bt = morning_edition.build_publication_context()["why_matters"]
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("DWP", 3))
    dwp = morning_edition.build_publication_context()["why_matters"]
    assert bt != dwp
    assert dwp[0]["organisation"] == "DWP"


def test_watchlist_ranking_changes_when_live_evidence_changes(monkeypatch) -> None:
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("BT", 1))
    bt_top = morning_edition.build_publication_context()["top_organisations"][0]["organisation"]
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("DWP", 4))
    dwp_ctx = morning_edition.build_publication_context()
    assert dwp_ctx["top_organisations"][0]["organisation"] != bt_top or dwp_ctx["top_organisations"][0]["live_uplift"] > 0
    assert {"base_score", "live_uplift", "final_score", "live_evidence_count", "unique_source_count"}.issubset(dwp_ctx["top_organisations"][0])


def test_what_should_i_do_changes_when_live_evidence_changes(monkeypatch) -> None:
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("BT", 2))
    bt_actions = morning_edition.build_publication_context()["recommended_actions"]
    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("DWP", 3))
    dwp_actions = morning_edition.build_publication_context()["recommended_actions"]
    assert bt_actions != dwp_actions
    assert dwp_actions[0]["organisation"] == "DWP"
    assert dwp_actions[0]["time_required"]
    assert dwp_actions[0]["target_executive_or_function"]
    assert dwp_actions[0]["proposition"]
    assert dwp_actions[0]["live_evidence_receipt"]
    assert dwp_actions[0]["missing_evidence"]


def test_public_sector_organisations_exist_in_watchlist_and_registry() -> None:
    from cios.applications.flora.live.source_registry import enabled_sources

    watchlist = {account.organisation_name for account in sample_watchlist()}
    assert {"Ministry of Defence", "DWP", "Ministry of Justice"}.issubset(watchlist)
    assert enabled_sources("Ministry of Defence")
    assert enabled_sources("DWP")
    assert enabled_sources("Ministry of Justice")


def test_public_sector_evidence_maps_to_public_sector_conditions() -> None:
    from cios.applications.flora.live.extractor import interpret_keyword

    assert interpret_keyword("legacy systems")[0] == "Legacy Technology"
    assert interpret_keyword("service transformation")[0] == "Citizen Experience"
    assert interpret_keyword("cyber")[0] == "Cyber Resilience"
    assert interpret_keyword("procurement")[0] == "Procurement Readiness"


def test_watchlist_displays_live_uplift_and_provider_context(monkeypatch, tmp_path) -> None:
    from cios.applications.flora.publisher import morning_edition
    from cios.applications.flora.publisher.morning_edition import render_markdown
    from cios.applications.flora.workspace import views as workspace_views
    from cios.applications.flora.workspace.views import landing_page, settings_page

    monkeypatch.setattr(morning_edition, "read_jsonl", lambda *args, **kwargs: _evidence("BT", 2))
    ctx = morning_edition.build_publication_context()
    monkeypatch.setattr(workspace_views, "build_publication_context", lambda: ctx)
    html = landing_page()
    settings = settings_page()
    markdown = render_markdown(ctx)

    assert ctx["provider_context"]["provider_name"] == "IBM"
    assert any(row["organisation"] == "BT" and row["live_uplift"] > 0 for row in ctx["top_organisations"])
    assert "Live uplift +" in html
    assert "Provider Context" in html
    assert "Current provider:</strong> IBM" in html
    assert "provider_name" in settings and "IBM" in settings
    assert "Provider Context" in markdown


def test_expanded_target_organisations_and_public_sector_sources_exist() -> None:
    from cios.applications.flora.live.source_registry import enabled_sources
    from cios.applications.flora.seed_data import sample_watchlist

    watchlist = {account.organisation_name for account in sample_watchlist()}
    expected = {
        "Severn Trent", "Southern Water", "Yorkshire Water", "Anglian Water", "Northumbrian Water",
        "Centrica", "EDF Energy UK", "Octopus Energy", "ScottishPower", "E.ON UK",
        "Virgin Media O2", "TalkTalk", "Three UK", "Openreach",
        "ITV", "Channel 4", "Channel 5 / Paramount UK", "The Guardian", "News UK",
        "Premier League", "The Football Association", "England and Wales Cricket Board", "Rugby Football Union", "Wimbledon / AELTC",
        "HMRC", "DEFRA", "Department of Health and Social Care", "NHS England", "Home Office", "Cabinet Office", "Department for Education", "Department for Transport",
    }
    assert expected.issubset(watchlist)
    assert {"HMRC", "DEFRA", "Department of Health and Social Care"}.issubset(watchlist)
    sources = {source.organisation for source in enabled_sources()}
    assert expected.issubset(sources)
