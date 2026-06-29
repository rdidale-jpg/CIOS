"""Seeded Flora v0.1 communications-sector data."""

from __future__ import annotations

from datetime import date

from cios.applications.flora.models import CommercialDNA, Priority, Signal, TargetAccount


def sample_commercial_dna() -> CommercialDNA:
    """Return sample commercial DNA for deterministic local execution."""

    return CommercialDNA(
        employer="Example AI Reinvention Consultancy",
        business_unit="Communications, Media, Energy and Utilities",
        sectors=["Utilities", "Energy", "Telecommunications", "Media", "Sport"],
        strategic_offerings=["AI operating model", "Customer operations automation", "Network intelligence", "Data platform modernisation"],
        competitors=["IBM", "Accenture", "Capgemini", "Deloitte", "KPMG", "CGI", "TCS", "Infosys", "Cognizant", "Wipro", "Sopra Steria"],
        differentiators=["sector-specific AI patterns", "explainable commercial reasoning", "rapid deterministic discovery"],
        reference_clients=["National Grid", "BBC", "SSE"],
        target_geographies=["United Kingdom", "Ireland", "Western Europe"],
    )


def sample_watchlist() -> list[TargetAccount]:
    """Return seeded target accounts for Flora v0.1."""

    return [
        TargetAccount(organisation_name="Thames Water", sector="Utilities", priority=Priority.HIGH, notes="Operational resilience and customer trust pressure.", known_incumbents=["Capgemini", "IBM"], known_competitors=["Accenture", "Deloitte", "CGI"]),
        TargetAccount(organisation_name="BT", sector="Telecommunications", priority=Priority.HIGH, notes="Network modernisation and enterprise productivity opportunity.", known_incumbents=["TCS", "IBM"], known_competitors=["Accenture", "Infosys", "Wipro"]),
        TargetAccount(organisation_name="National Grid", sector="Energy", priority=Priority.HIGH, notes="Grid resilience and energy transition complexity.", known_incumbents=["Deloitte", "IBM"], known_competitors=["Accenture", "Capgemini", "CGI"]),
        TargetAccount(organisation_name="Sky", sector="Media", priority=Priority.MEDIUM, notes="Customer retention and content operations opportunity.", known_incumbents=["Cognizant"], known_competitors=["Accenture", "TCS", "Infosys"]),
        TargetAccount(organisation_name="BBC", sector="Media", priority=Priority.MEDIUM, notes="Public service media transformation and productivity.", known_incumbents=["Deloitte"], known_competitors=["KPMG", "Capgemini", "Sopra Steria"]),
        TargetAccount(organisation_name="Vodafone", sector="Telecommunications", priority=Priority.HIGH, notes="Commercial simplification and network intelligence.", known_incumbents=["IBM", "Accenture"], known_competitors=["TCS", "Infosys", "Wipro"]),
        TargetAccount(organisation_name="SSE", sector="Energy", priority=Priority.MEDIUM, notes="Energy transition, field operations and customer service.", known_incumbents=["CGI"], known_competitors=["Accenture", "Deloitte", "Capgemini"]),
        TargetAccount(organisation_name="United Utilities", sector="Utilities", priority=Priority.MEDIUM, notes="Regulated utility performance and leakage reduction.", known_incumbents=["Sopra Steria"], known_competitors=["IBM", "CGI", "Capgemini"]),
    ]


def sample_signals() -> list[Signal]:
    """Return seeded intelligence signals; no live sources are called."""

    detected = date(2026, 6, 29)
    rows = [
        ("FLORA-SIG-001", "Seed briefing", "sample", "Thames Water", "Utilities", "Regulatory Pressure", "Regulatory scrutiny and resilience pressure remain high.", "Seeded sample evidence notes operational resilience, leakage, debt and customer trust pressure.", 82, 91, 88, ["asset intelligence", "customer trust analytics", "field operations automation"]),
        ("FLORA-SIG-002", "Seed briefing", "sample", "BT", "Telecommunications", "Network Intelligence", "Network automation and enterprise simplification are attractive AI areas.", "Seeded sample evidence notes large-scale network estate, service assurance and productivity potential.", 86, 87, 84, ["network intelligence", "service assurance", "workforce productivity"]),
        ("FLORA-SIG-003", "Seed briefing", "sample", "National Grid", "Energy", "Operational Resilience", "Grid transition complexity creates strong AI planning opportunity.", "Seeded sample evidence notes grid connections, forecasting, resilience and asset planning needs.", 88, 89, 82, ["grid forecasting", "asset intelligence", "planning optimisation"]),
        ("FLORA-SIG-004", "Seed briefing", "sample", "Sky", "Media", "Customer Experience", "Retention, personalisation and content operations create AI use cases.", "Seeded sample evidence notes competitive streaming pressure and customer experience differentiation.", 76, 78, 79, ["personalisation", "content intelligence", "customer operations automation"]),
        ("FLORA-SIG-005", "Seed briefing", "sample", "BBC", "Media", "Workforce Productivity", "Productivity and content metadata are likely reinvention themes.", "Seeded sample evidence notes public value, content archive operations and responsible AI constraints.", 78, 74, 76, ["content intelligence", "knowledge management", "responsible AI governance"]),
        ("FLORA-SIG-006", "Seed briefing", "sample", "Vodafone", "Telecommunications", "Competition", "Competitive pressure supports AI-enabled simplification.", "Seeded sample evidence notes pricing pressure, network operations and enterprise service differentiation.", 84, 86, 86, ["network intelligence", "sales operations automation", "customer operations automation"]),
        ("FLORA-SIG-007", "Seed briefing", "sample", "SSE", "Energy", "Digital Transformation", "Energy transition programmes indicate AI readiness.", "Seeded sample evidence notes capital delivery, field force optimisation and customer support demand.", 80, 77, 81, ["field operations automation", "asset intelligence", "customer operations automation"]),
        ("FLORA-SIG-008", "Seed briefing", "sample", "United Utilities", "Utilities", "Data Modernisation", "Regulated performance data can support targeted AI use cases.", "Seeded sample evidence notes leakage, customer service and operational analytics opportunities.", 79, 80, 78, ["leakage analytics", "asset intelligence", "customer trust analytics"]),
    ]
    return [Signal(signal_id=i, source=s, source_type=st, organisation=o, sector=sec, signal_category=cat, signal_summary=summary, evidence_text=ev, confidence=c, strength=strength, freshness=fresh, detected_date=detected, related_capabilities=caps) for i, s, st, o, sec, cat, summary, ev, c, strength, fresh, caps in rows]
