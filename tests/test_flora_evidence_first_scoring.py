from cios.applications.flora.live.aggregation import adjust_score, aggregate_live_evidence
from cios.applications.flora.portfolio import build_radar_rows
from cios.applications.flora.rob_score import create_rob_score_record
from cios.applications.flora.score_explainability import score_detail
from cios.applications.flora.workspace.views import landing_page, score_page, rob_score_page


def _live(org="BT"):
    return [{"source_id":"s1","organisation":org,"source_name":"Official","source_type":"official_newsroom","source_url":"https://example.com","snippet":"Sponsor and budget confirm AI network operations timing with incumbent supplier and competitor engagement by operations director pain owner.","commercial_condition":"AI Modernisation","likely_capability":"network intelligence","confidence":90,"overall_evidence_quality":90,"evidence_tier":"tier_1_company","extraction_timestamp":"2026-06-30T00:00:00+00:00"}]


def test_seeded_score_not_used_when_live_evidence_exists(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    metrics = aggregate_live_evidence(_live())["BT"]
    score = adjust_score("BT", 5, metrics)
    assert score.scoring_mode == "LIVE EVIDENCE"
    assert score.seeded_fallback_score is None
    assert score.final_score == score.live_evidence_score - score.missing_evidence_penalty


def test_seeded_fallback_only_without_live_or_learned(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    score = adjust_score("BT", 73, None)
    assert score.scoring_mode == "SEEDED FALLBACK"
    assert score.seeded_fallback_score == 73
    assert score.final_score == 73


def test_rob_score_adjusts_final_score(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    create_rob_score_record(organisation="BT", rob_score=12, rob_score_reason="Rob validated urgency")
    metrics = aggregate_live_evidence(_live())["BT"]
    score = adjust_score("BT", 5, metrics)
    assert score.rob_score_adjustment == 12
    assert score.final_score == min(100, score.live_evidence_score + 12 - score.missing_evidence_penalty)


def test_rob_score_route_renders(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    html = rob_score_page("BT")
    assert "Rob score" in html
    assert "Score adjustment" in html


def test_radar_and_watchlist_use_evidence_first(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    monkeypatch.setattr("cios.applications.flora.portfolio.read_jsonl", lambda path=None: _live("BT"))
    rows = build_radar_rows()
    bt = next(r for r in rows if r.organisation == "BT")
    assert bt.live_evidence_score > 0
    assert "evidence-first" in bt.rank_change_reason.lower() or "live evidence" in bt.rank_change_reason.lower()


def test_score_explanation_shows_evidence_first_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    monkeypatch.setattr("cios.applications.flora.score_explainability.read_jsonl", lambda path=None: _live("BT"))
    monkeypatch.setattr("cios.applications.flora.portfolio.read_jsonl", lambda path=None: _live("BT"))
    html = score_page("BT")
    assert "LIVE EVIDENCE" in html
    assert "live evidence score" in html
    assert "seeded fallback score" in html
