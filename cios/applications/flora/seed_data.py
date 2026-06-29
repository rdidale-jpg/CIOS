"""Seeded Flora v0.1 communications-sector data."""

from __future__ import annotations

from datetime import date

from cios.applications.flora.models import CommercialDNA, Priority, Signal, TargetAccount


def sample_commercial_dna() -> CommercialDNA:
    """Return sample commercial DNA for deterministic local execution."""

    return CommercialDNA(
        employer="Example AI Reinvention Consultancy",
        business_unit="Communications, Media, Energy and Utilities",
        sectors=["Utilities", "Energy", "Telecommunications", "Media", "Sport", "Public Sector"],
        strategic_offerings=["AI operating model", "Customer operations automation", "Network intelligence", "Data platform modernisation", "Public sector service transformation"],
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
        TargetAccount(organisation_name="Ministry of Defence", sector="Public Sector", priority=Priority.HIGH, notes="Defence digital modernisation, cyber resilience and operational reform.", known_incumbents=["CGI", "Sopra Steria"], known_competitors=["Accenture", "Deloitte", "IBM"]),
        TargetAccount(organisation_name="DWP", sector="Public Sector", priority=Priority.HIGH, notes="Citizen service transformation, legacy systems and operational efficiency pressure.", known_incumbents=["IBM", "TCS"], known_competitors=["Accenture", "Deloitte", "Capgemini"]),
        TargetAccount(organisation_name="Ministry of Justice", sector="Public Sector", priority=Priority.MEDIUM, notes="Justice service reform, digital casework and legacy technology pressure.", known_incumbents=["Sopra Steria", "CGI"], known_competitors=["Accenture", "Deloitte", "KPMG"]),
        TargetAccount(organisation_name="Severn Trent", sector="Utilities", priority=Priority.MEDIUM, notes="Water resilience, customer service and regulated performance pressure.", known_competitors=["Accenture", "Capgemini", "CGI"]),
        TargetAccount(organisation_name="Southern Water", sector="Utilities", priority=Priority.MEDIUM, notes="Operational improvement, environmental performance and customer trust pressure.", known_competitors=["Accenture", "Deloitte", "CGI"]),
        TargetAccount(organisation_name="Yorkshire Water", sector="Utilities", priority=Priority.MEDIUM, notes="Asset resilience, leakage reduction and customer operations opportunity.", known_competitors=["IBM", "Capgemini", "CGI"]),
        TargetAccount(organisation_name="Anglian Water", sector="Utilities", priority=Priority.MEDIUM, notes="Water scarcity, capital delivery and operational intelligence opportunity.", known_competitors=["Accenture", "Capgemini", "Deloitte"]),
        TargetAccount(organisation_name="Northumbrian Water", sector="Utilities", priority=Priority.MEDIUM, notes="Customer experience, leakage and field operations transformation opportunity.", known_competitors=["IBM", "CGI", "Sopra Steria"]),
        TargetAccount(organisation_name="Centrica", sector="Energy", priority=Priority.MEDIUM, notes="Retail energy, services and operational efficiency opportunity.", known_competitors=["Accenture", "Deloitte", "Capgemini"]),
        TargetAccount(organisation_name="EDF Energy UK", sector="Energy", priority=Priority.MEDIUM, notes="Low-carbon generation, customer operations and asset programmes.", known_competitors=["IBM", "Accenture", "Capgemini"]),
        TargetAccount(organisation_name="Octopus Energy", sector="Energy", priority=Priority.MEDIUM, notes="Digital energy retail and platform-led customer operations.", known_competitors=["Accenture", "Deloitte", "TCS"]),
        TargetAccount(organisation_name="ScottishPower", sector="Energy", priority=Priority.MEDIUM, notes="Grid investment, renewables and customer transformation pressure.", known_competitors=["IBM", "CGI", "Capgemini"]),
        TargetAccount(organisation_name="E.ON UK", sector="Energy", priority=Priority.MEDIUM, notes="Customer energy transition and managed operations opportunity.", known_competitors=["Accenture", "Infosys", "Wipro"]),
        TargetAccount(organisation_name="Virgin Media O2", sector="Telecommunications", priority=Priority.MEDIUM, notes="Network investment, customer experience and integration complexity.", known_competitors=["Accenture", "IBM", "TCS"]),
        TargetAccount(organisation_name="TalkTalk", sector="Telecommunications", priority=Priority.MEDIUM, notes="Connectivity, service and cost transformation opportunity.", known_competitors=["Accenture", "Infosys", "Wipro"]),
        TargetAccount(organisation_name="Three UK", sector="Telecommunications", priority=Priority.MEDIUM, notes="Mobile network, customer operations and merger-readiness pressure.", known_competitors=["IBM", "Accenture", "TCS"]),
        TargetAccount(organisation_name="Openreach", sector="Telecommunications", priority=Priority.MEDIUM, notes="Fibre rollout, service assurance and field operations scale.", known_competitors=["Accenture", "Capgemini", "CGI"]),
        TargetAccount(organisation_name="ITV", sector="Media", priority=Priority.MEDIUM, notes="Streaming, advertising and content operations transformation.", known_competitors=["Accenture", "Deloitte", "Cognizant"]),
        TargetAccount(organisation_name="Channel 4", sector="Media", priority=Priority.MEDIUM, notes="Digital commissioning, ad technology and productivity opportunity.", known_competitors=["Accenture", "KPMG", "Capgemini"]),
        TargetAccount(organisation_name="Channel 5 / Paramount UK", sector="Media", priority=Priority.MEDIUM, notes="Streaming, content operations and audience analytics opportunity.", known_competitors=["Accenture", "TCS", "Infosys"]),
        TargetAccount(organisation_name="The Guardian", sector="Media", priority=Priority.MEDIUM, notes="Reader revenue, publishing operations and responsible AI opportunity.", known_competitors=["Accenture", "Deloitte", "Cognizant"]),
        TargetAccount(organisation_name="News UK", sector="Media", priority=Priority.MEDIUM, notes="Subscriptions, advertising and newsroom operations transformation.", known_competitors=["Accenture", "Infosys", "TCS"]),
        TargetAccount(organisation_name="Premier League", sector="Sport", priority=Priority.MEDIUM, notes="Fan engagement, media operations and data platform opportunity.", known_competitors=["Accenture", "Deloitte", "IBM"]),
        TargetAccount(organisation_name="The Football Association", sector="Sport", priority=Priority.MEDIUM, notes="Grassroots services, competition operations and data modernisation.", known_competitors=["Accenture", "Deloitte", "Capgemini"]),
        TargetAccount(organisation_name="England and Wales Cricket Board", sector="Sport", priority=Priority.MEDIUM, notes="Fan, participant and operations transformation opportunity.", known_competitors=["IBM", "Accenture", "Deloitte"]),
        TargetAccount(organisation_name="Rugby Football Union", sector="Sport", priority=Priority.MEDIUM, notes="Participation, fan engagement and operational resilience opportunity.", known_competitors=["Accenture", "Capgemini", "CGI"]),
        TargetAccount(organisation_name="Wimbledon / AELTC", sector="Sport", priority=Priority.MEDIUM, notes="Premium event operations, fan experience and asset intelligence.", known_competitors=["IBM", "Accenture", "Deloitte"]),
        TargetAccount(organisation_name="HMRC", sector="Public Sector", priority=Priority.HIGH, notes="Tax service transformation, compliance operations and legacy modernisation.", known_competitors=["Accenture", "Deloitte", "IBM"]),
        TargetAccount(organisation_name="DEFRA", sector="Public Sector", priority=Priority.HIGH, notes="Environmental services, data platforms and operational reform.", known_competitors=["Accenture", "KPMG", "Capgemini"]),
        TargetAccount(organisation_name="Department of Health and Social Care", sector="Public Sector", priority=Priority.HIGH, notes="Health policy, data and service transformation pressure.", known_competitors=["IBM", "Accenture", "Deloitte"]),
        TargetAccount(organisation_name="NHS England", sector="Public Sector", priority=Priority.HIGH, notes="Health service transformation, data, cloud and operational productivity.", known_competitors=["Accenture", "Deloitte", "IBM"]),
        TargetAccount(organisation_name="Home Office", sector="Public Sector", priority=Priority.HIGH, notes="Public safety services, casework and legacy technology pressure.", known_competitors=["IBM", "CGI", "Sopra Steria"]),
        TargetAccount(organisation_name="Cabinet Office", sector="Public Sector", priority=Priority.HIGH, notes="Cross-government reform, shared services and digital standards.", known_competitors=["Accenture", "Deloitte", "KPMG"]),
        TargetAccount(organisation_name="Department for Education", sector="Public Sector", priority=Priority.MEDIUM, notes="Education services, data and operational transformation.", known_competitors=["Accenture", "Capgemini", "CGI"]),
        TargetAccount(organisation_name="Department for Transport", sector="Public Sector", priority=Priority.MEDIUM, notes="Transport services, infrastructure data and operational reform.", known_competitors=["IBM", "Accenture", "Deloitte"]),
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
        ("FLORA-SIG-009", "Seed briefing", "sample", "Ministry of Defence", "Public Sector", "Cyber Resilience", "Defence reform and digital programmes indicate cyber-resilient modernisation demand.", "Seeded sample evidence notes defence digital, cyber resilience, cloud and operational reform.", 82, 84, 80, ["cyber resilience", "cloud modernisation", "operational intelligence"]),
        ("FLORA-SIG-010", "Seed briefing", "sample", "DWP", "Public Sector", "Service Transformation", "Citizen services and operational scale create automation and AI readiness pressure.", "Seeded sample evidence notes citizen experience, legacy systems, automation and operational efficiency.", 88, 90, 86, ["citizen service automation", "legacy modernisation", "casework intelligence"]),
        ("FLORA-SIG-011", "Seed briefing", "sample", "Ministry of Justice", "Public Sector", "Legacy Technology", "Justice reform depends on digital casework and legacy technology reduction.", "Seeded sample evidence notes justice service reform, digital modernisation and case management pressure.", 78, 80, 79, ["casework automation", "digital service transformation", "data platform modernisation"]),
    ]
    return [Signal(signal_id=i, source=s, source_type=st, organisation=o, sector=sec, signal_category=cat, signal_summary=summary, evidence_text=ev, confidence=c, strength=strength, freshness=fresh, detected_date=detected, related_capabilities=caps) for i, s, st, o, sec, cat, summary, ev, c, strength, fresh, caps in rows]
