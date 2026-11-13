from cios.applications.flora.banking_portfolio import (
    BANKS,
    PAGE_BUDGETS,
    REFERENCE_DOMAINS,
    banking_landing_page,
    industry_outlook_page,
    ai_native_page,
    ai_native_capability_model_page,
    portfolio_page,
    heatmap_page,
    bank_page,
    opportunity_page,
    evidence_page,
)


def _sections(html: str) -> int:
    return html.count("primary-section")


def test_landing_budget_conclusion_and_signals():
    html = banking_landing_page()
    assert _sections(html) <= 5
    assert html.index("UK banks are moving") < html.index("Three industry signals")
    assert "data-default-signal-count='3'" in html
    assert html.count("executive-insight-card") == 3
    assert "UK Banking PESTLE view" not in html


def test_pestle_only_outlook_not_landing_or_portfolio():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import PESTLE_FORCES
    outlook = Document(industry_outlook_page())
    assert 'Prioritised industry-force board' in outlook.headings
    for category, force in PESTLE_FORCES.items():
        assert category in outlook.text and force['force'] in outlook.text
    for html in (banking_landing_page(), portfolio_page()):
        doc = Document(html)
        assert 'Prioritised industry-force board' not in doc.headings
        assert '/flora/banking' in doc.hrefs
    assert any(h.split('#')[0] == '/flora/banking/outlook' for h in Document(banking_landing_page()).hrefs)


def test_ai_native_reference_model_collapsed_and_separate():
    from tests.flora_html_contract import Document
    top = Document(ai_native_page())
    assert '/flora/banking/ai-native/capability-model' in top.hrefs
    assert 'Today versus AI-native' in top.headings
    assert not all(domain['name'] in top.headings for domain in REFERENCE_DOMAINS)
    detail = Document(ai_native_capability_model_page())
    assert 'Explore all 12 capabilities' in detail.headings
    for domain in REFERENCE_DOMAINS:
        assert domain['name'] in detail.headings


def test_portfolio_excludes_full_industry_model_and_respects_card_budget():
    html = portfolio_page()
    assert html.count("portfolio-account") <= 5
    assert "Detailed inspection" not in html
    assert "UK Banking PESTLE view" not in html
    assert "Explore capability model" not in html


def test_heatmap_one_mode_and_cells_have_no_paragraphs():
    html = heatmap_page("opportunity-value")
    assert "Selected mode: Opportunity value" in html
    assert "Theme relevance, Reinvention pressure" not in html
    table = html.split("<tbody>",1)[1].split("</tbody>",1)[0]
    assert "<p>" not in table
    assert "heatmap-cell" in table


def test_account_default_opportunities_breadcrumbs_and_evidence_drilldown():
    from tests.flora_html_contract import Document
    html, status = bank_page('lloyds')
    doc = Document(html)
    assert status == 200 and html.count('primary-section') <= 7
    assert 'Top opportunities' in doc.headings
    opportunity_links = [h for h in doc.hrefs if h.startswith('/flora/banking/lloyds/opportunity/')]
    assert opportunity_links == [f'/flora/banking/lloyds/opportunity/{o.id}' for o in BANKS['lloyds'].opportunities[:3]]
    assert 'UK Banking' in doc.text
    assert '/flora/banking/lloyds/evidence' in doc.hrefs
    evidence, status = evidence_page('lloyds')
    assert status == 200 and 'Evidence, sources, lineage' in Document(evidence).text
    assert 'not accepted claim citations' in Document(evidence).text


def test_opportunity_detail_order_and_provenance():
    html, status = opportunity_page("lloyds", "COH-LBG-001")
    assert status == 200
    order = ["Opportunity", "Why now", "Estimated value", "Likely timing", "Customer problem", "Desired future state", "Current barrier", "Supplier landscape", "Competitive whitespace", "Recommended next action", "Why Flora believes this", "Provenance and evidence"]
    positions = [html.index(f"<h2>{name}</h2>") for name in order]
    assert positions == sorted(positions)
    assert "Annual report" in html


def _validate_narrative(text: str, bank: str = "Lloyds"):
    flags=[]
    lower=text.lower()
    words=lower.replace('.', ' ').split()
    for phrase in ("digital transformation", "customer centric", "operational excellence"):
        if lower.count(phrase) > 1:
            flags.append("duplicated phrases")
    for jargon in ("synergy", "omnichannel", "ecosystem"):
        if jargon in lower and "means" not in lower:
            flags.append("unexplained jargon")
    if "commercial implication" not in lower:
        flags.append("missing commercial implication")
    if bank.lower() not in lower and "bank" in lower:
        flags.append("generic sentence")
    return flags


def test_narrative_validator_rules():
    flags = _validate_narrative("Banks need digital transformation and digital transformation through omnichannel synergy.")
    assert "duplicated phrases" in flags
    assert "unexplained jargon" in flags
    assert "missing commercial implication" in flags
    good = _validate_narrative("Lloyds should fund migration because conduct and cost pressure are visible. Commercial implication: lead with measurable benefits.")
    assert good == []


def test_page_budgets_and_existing_intelligence_preserved():
    assert PAGE_BUDGETS["banking_landing"]["max_industry_signals"] == 3
    assert sum(o.value.midpoint for b in BANKS.values() for o in b.opportunities) == 910
    html = evidence_page("lloyds")[0] + ai_native_capability_model_page()
    assert "Lineage key" in html
    assert "Customer experience" in html and "Innovation and change delivery" in html

import pytest

# Domain tests use an explicit fixture identity provider, never HTTP trust.
pytestmark = pytest.mark.usefixtures("verified_flora_test_authority")
