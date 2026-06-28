"""Console entry point for the Sprint 7A Opportunity Assistant."""

from __future__ import annotations

import argparse

from cios.applications.opportunity_assistant.pipeline import run_pipeline
from cios.applications.opportunity_assistant.reporting import render_console_report


def main() -> None:
    """Run the sample opportunity pipeline and print the selected report format."""

    parser = argparse.ArgumentParser(
        description="Run the deterministic CIOS Opportunity Assistant sample."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the full machine-readable pipeline result as JSON.",
    )
    args = parser.parse_args()

    result = run_pipeline()
    if args.json:
        print(result.model_dump_json(indent=2))
        return

    print(render_console_report(result))


if __name__ == "__main__":
    main()
