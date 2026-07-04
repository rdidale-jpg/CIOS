"""Static HTML export for the Flora Pilot Workspace."""
from __future__ import annotations

from pathlib import Path

from cios.applications.flora.workspace.feedback import runtime_dir
from cios.applications.flora.workspace.views import case_page, landing_page, logbook_page, settings_page

EXPORT_DIRNAME = "export"
CASE_SLUGS = [
    "ThamesWater",
    "BT",
    "NationalGrid",
    "Vodafone",
    "Sky",
    "BBC",
    "SSE",
    "UnitedUtilities",
    "MinistryofDefence",
    "DWP",
    "MinistryofJustice",
]


def export_dir() -> Path:
    """Return the Flora static export directory."""
    return runtime_dir() / EXPORT_DIRNAME


def _staticize_root_page(html: str) -> str:
    html = (
        html.replace("href='/'", "href='index.html'")
        .replace("href='/logbook'", "href='logbook.html'")
        .replace("href='/settings'", "href='settings.html'")
        .replace("href='/financial-reports'", "href='#financial-reports'")
        .replace("href='/observatory/critique'", "href='#research'")
        .replace("href='/observatory'", "href='#observatory'")
        .replace("href='/radar'", "href='#radar'")
        .replace("href='/scoring'", "href='#scoring'")
        .replace("href='/live/collect/start'", "href='#live-collect'")
        .replace("href='/live/collect'", "href='#live-collect'")
        .replace("href='/live/evidence'", "href='#live-evidence'")
        .replace("href='/live'", "href='#live'")
        .replace("action='/logbook'", "action='#logbook'")
    )
    return _replace_score_links(_replace_case_links(html, "case/"), "#score-")


def _staticize_case_page(html: str) -> str:
    html = (
        html.replace("href='/'", "href='../index.html'")
        .replace("href='/logbook'", "href='../logbook.html'")
        .replace("href='/settings'", "href='../settings.html'")
        .replace("href='/financial-reports'", "href='../index.html#financial-reports'")
        .replace("href='/digital-twin/bt-group-plc'", "href='../index.html#digital-twin'")
        .replace("href='/observatory/critique'", "href='../index.html#research'")
        .replace("href='/observatory'", "href='../index.html#observatory'")
        .replace("href='/radar'", "href='../index.html#radar'")
        .replace("href='/scoring'", "href='../index.html#scoring'")
        .replace("href='/live/collect/start'", "href='#live-collect'")
        .replace("href='/live/collect'", "href='#live-collect'")
        .replace("href='/live/evidence'", "href='#live-evidence'")
        .replace("href='/live'", "href='#live'")
        .replace("action='/feedback'", "action='#feedback'")
    )
    return _replace_score_links(_replace_case_links(html, ""), "../index.html#score-")


def _replace_case_links(html: str, prefix: str) -> str:
    for slug in CASE_SLUGS:
        html = html.replace(f"href='/case/{slug}'", f"href='{prefix}{slug}.html'")
    return html


def _replace_score_links(html: str, prefix: str) -> str:
    for slug in CASE_SLUGS:
        html = html.replace(f"href='/score/{slug}'", f"href='{prefix}{slug}'")
    return html


def generate_export(destination: Path | None = None) -> Path:
    """Generate static Flora workspace files and return the index path."""
    destination = destination or export_dir()
    case_destination = destination / "case"
    case_destination.mkdir(parents=True, exist_ok=True)

    (destination / "index.html").write_text(_staticize_root_page(landing_page()), encoding="utf-8")
    (destination / "settings.html").write_text(_staticize_root_page(settings_page()), encoding="utf-8")
    (destination / "logbook.html").write_text(_staticize_root_page(logbook_page()), encoding="utf-8")

    for slug in CASE_SLUGS:
        (case_destination / f"{slug}.html").write_text(_staticize_case_page(case_page(slug)), encoding="utf-8")

    return destination / "index.html"


def main() -> None:
    """CLI entry point for static export generation."""
    print(generate_export().resolve())


if __name__ == "__main__":
    main()
