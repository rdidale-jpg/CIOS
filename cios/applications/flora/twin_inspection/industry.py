"""Industry adapter over the existing governed UK Banking presentation runtime."""
from __future__ import annotations
from html import escape

from cios.applications.flora.banking_portfolio import (
    BANKS, GENERATED_DATE, INDUSTRY_SIGNALS, PESTLE_FORCES,
    industry_outlook_html, pestle_view_html,
)
from .contracts import InspectionAdapter, InspectionProfile, InspectionSection, MaterialConclusion


def industry_inspection_adapter(industry_id: str, headers) -> InspectionAdapter:
    """Compose the implemented Banking read model; unsupported industries stay gaps."""
    if industry_id.casefold() not in {"uk-banking", "banking"}:
        raise LookupError(industry_id)
    conclusions = tuple(
        MaterialConclusion(
            f"industry-signal-{index}", title, "governed industry interpretation",
            implication, explanation,
            "Open Unknowns include the timing, affected-enterprise response and whether the pressure becomes funded demand.",
            f"/flora/banking/signals#signal-{index}", "/flora/banking/outlook#pestle",
            "High" if index == 1 else "Moderate", GENERATED_DATE,
        )
        for index, (title, explanation, implication, _banks, _href) in enumerate(INDUSTRY_SIGNALS[:3], 1)
    )
    profile = InspectionProfile(
        "UK Banking", "Industry", "Flora Banking governed runtime", "Governed",
        "Current Banking presentation", GENERATED_DATE, GENERATED_DATE,
        "Owner-backed runtime available", "Executive inspection available",
        "Governed Banking sources and enterprise evidence routes", GENERATED_DATE,
        "Owner-scoped qualifications shown per conclusion", "Material gaps retained per conclusion",
        "Competing pressures retained", "Banking runtime provenance",
    )
    sections = (
        InspectionSection("executive-intelligence", "Executive", 10, industry_outlook_html,
                          "governed industry presentation", True, True, "#material-conclusions", GENERATED_DATE, GENERATED_DATE),
        InspectionSection("market-dynamics", "Market dynamics", 20, pestle_view_html,
                          "governed industry presentation", bool(PESTLE_FORCES), True, "#pestle", GENERATED_DATE, GENERATED_DATE),
        InspectionSection("related-twins", "Related Twins", 40, _related_enterprises,
                          "governed Banking relationship presentation", bool(BANKS), True, "#related-twins", GENERATED_DATE, GENERATED_DATE),
        InspectionSection("supporting-research", "Supporting research", 50, _research,
                          "governed presentation provenance", True, True, "/flora/banking/signals", GENERATED_DATE, GENERATED_DATE),
    )
    return InspectionAdapter("industry-banking", profile, sections, conclusions)


def _related_enterprises() -> str:
    links = "".join(
        f"<li><a href='/flora/banking/{escape(bank.slug)}'>{escape(bank.name)}</a></li>"
        for bank in sorted(BANKS.values(), key=lambda item: item.priority_rank)
    )
    return f"<section class='card' id='related-twins'><h2>Significant enterprises</h2><p>Existing Banking runtime relationships; no inspection-shell graph is created.</p><ul>{links}</ul></section>"


def _research() -> str:
    return "<section class='card' id='supporting-research'><h2>Evidence and supporting research</h2><p>Inspect the existing signal and enterprise Evidence views; source ownership and lineage remain with the Banking runtime.</p><p><a href='/flora/banking/signals'>Inspect industry signals and provenance</a> · <a href='/flora/banking/outlook#pestle'>Inspect regulatory and market forces</a></p></section>"
