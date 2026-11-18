from cios.applications.flora import visual_streams as v
from tests.test_flora_eai2_integration import changed_release


def banking(stage, reading="facts"):
    return v.render("/industries/banking", {"detail": [stage], "reading": [reading]})


def test_customer_segments_and_ancillary_complaints():
    facts = banking("customers")
    assert 'class="banking-market"' in facts
    for label in ("Households", "Businesses", "Needs", "Products", "Channels"):
        assert label in facts
    assert "Barclays Bank UK PLC" in facts and "90,678" in facts
    insight = banking("customers", "insight")
    assert "90,678" not in insight
    assert "Acquisition" in insight and "Retention" in insight


def test_funding_reconciles_two_group_profit_bases():
    facts = banking("funding")
    assert 'class="banking-ledger"' in facts
    assert "FY ended 31 March 2026 · GBP millions" in facts
    assert "6,378 − 4,021 − 331 = 2,026" in facts
    assert "2,026 + 1 − 138 − 399 = 1,490" in facts
    assert facts.count("£127m") == 1 and "− 127" not in facts
    assert "Virgin Money contributes a full year" in banking("funding", "insight")


def test_payments_distinguish_processing_from_value_capture():
    facts = banking("payments")
    assert facts.index("Initiate") < facts.index("Clear</strong>") < facts.index("Settle</strong>")
    assert all(f"<dt>{label}</dt>" in facts for label in ("Scheme", "Operator", "Network"))
    insight = banking("payments", "insight")
    assert "Customer principal" in insight and "Service income" in insight
    assert "Pay.UK" not in facts + insight


def test_provider_oversight_and_brand_collaboration_stay_separate(tmp_path, monkeypatch):
    facts = banking("providers")
    assert "Google Cloud EMEA Limited" in facts
    assert "Lloyds Banking Group" in facts and "Envoy" in facts
    changed_release("provider", "withdrawn", tmp_path, monkeypatch)
    facts = banking("providers")
    insight = banking("providers", "insight")
    assert "Google Cloud EMEA Limited" not in facts + insight
    assert "Envoy" in facts and "workload unverified" in insight
    assert "Who operates each layer?" in facts and "Substitutability" in insight
