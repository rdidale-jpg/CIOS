from cios.applications.flora.banking_portfolio import BANKS, THEMES, bank_page, compare_page, portfolio_page


def test_all_five_bank_focus_objects_are_available_and_rendered():
    assert [b["name"] for b in BANKS.values()] == ["Lloyds Banking Group", "Barclays", "NatWest Group", "HSBC UK", "Santander UK"]
    html = portfolio_page()
    for bank in BANKS.values():
        assert bank["name"] in html
        assert bank["id"] in html
        assert "Understand this bank" in html
        assert "Inspect evidence" in html


def test_each_bank_has_bounded_briefing_or_safe_unavailable_state():
    for slug, bank in BANKS.items():
        html, status = bank_page(slug, briefing=True)
        assert status == 200
        assert "Account preparation briefing" in html
        assert "Why this bank now?" in html
        assert "This is not a Recommendation" in html
        assert "Questions worth exploring" in html
        assert len(bank["questions"]) <= 7
    html, status = bank_page("unknown-bank")
    assert status == 200
    assert "Safe unavailable" in html
    assert "Missing evidence" in html


def test_common_themes_reused_and_sector_enterprise_scope_distinguished():
    assert len(THEMES) == 8
    html = compare_page()
    for theme in THEMES:
        assert theme in html
    assert "Specific to this bank" in html
    assert "Also visible across peers" not in html or "safe-unavailable" in html
    assert "Not enough evidence to compare" in html


def test_peer_comparison_does_not_rank_score_or_imply_absence():
    html = compare_page().lower()
    for prohibited in ["winner", "leader", "laggard", "best", "worst", "score", "ranking"]:
        assert prohibited not in html
    assert "this does not mean lack of activity" in html


def test_questions_originate_from_unknowns_or_tensions_and_lineage_is_visible():
    for slug, bank in BANKS.items():
        html, _ = bank_page(slug)
        assert "Originating Unknown or tension and Evidence" in html
        assert "Lineage" in html or "lineage" in html
        for question in bank["questions"]:
            assert question in html


def test_briefings_are_transient_evidence_diagnostics_collapsed_and_deterministic():
    first, _ = bank_page("lloyds", briefing=True)
    second, _ = bank_page("lloyds", briefing=True)
    assert first == second
    assert "Generated date: 2026-07-19" in first
    assert "transient" not in first.lower() or "canonical" not in first.lower()
    assert "Based mainly on recent company reporting" in first
    assert "Authority, freshness, corroboration" not in first


def test_no_unrestricted_prompt_recommendation_scores_or_targets():
    combined = portfolio_page() + compare_page() + "".join(bank_page(slug)[0] for slug in BANKS)
    lower = combined.lower()
    assert "name='question'" not in lower
    assert "opportunity score" not in lower
    assert "propensity" not in lower
    assert "contact a named executive" not in lower
    assert "sales play" not in lower
