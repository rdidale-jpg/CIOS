"""CLI entry point for Flora v0.2."""

from __future__ import annotations

import argparse

from cios.applications.flora.pipeline import generate_daily_brief, generate_weekly_brief
from cios.applications.flora.reporting import render_daily_brief, render_weekly_brief
from cios.applications.flora.intelligence.case_file import generate_case_file
from cios.applications.flora.intelligence.case_reporting import render_case_file


def main() -> None:
    """Print the Flora intelligence brief as text or JSON."""

    parser = argparse.ArgumentParser(description="Run deterministic Flora v0.2 intelligence briefs.")
    parser.add_argument("--weekly", action="store_true", help="Emit the Weekly Intelligence Brief instead of the daily assessment brief.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON for the selected briefing.")
    parser.add_argument("--case", dest="case_name", help="Emit a Living Commercial Case File for a seeded organisation.")
    args = parser.parse_args()
    if args.case_name:
        case_file = generate_case_file(args.case_name)
        print(case_file.model_dump_json(indent=2) if args.json else render_case_file(case_file))
        return
    brief = generate_weekly_brief() if args.weekly else generate_daily_brief()
    renderer = render_weekly_brief if args.weekly else render_daily_brief
    print(brief.model_dump_json(indent=2) if args.json else renderer(brief))


if __name__ == "__main__":
    main()
