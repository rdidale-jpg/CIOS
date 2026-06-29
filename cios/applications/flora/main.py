"""CLI entry point for Flora v0.1."""

from __future__ import annotations

import argparse

from cios.applications.flora.pipeline import generate_daily_brief
from cios.applications.flora.reporting import render_daily_brief


def main() -> None:
    """Print the Flora Daily Brief as text or JSON."""

    parser = argparse.ArgumentParser(description="Run the deterministic Flora v0.1 Daily Intelligence Brief.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON for the briefing.")
    args = parser.parse_args()
    brief = generate_daily_brief()
    print(brief.model_dump_json(indent=2) if args.json else render_daily_brief(brief))


if __name__ == "__main__":
    main()
