"""Console entry point for the Sprint 7A Opportunity Assistant."""

from __future__ import annotations

from cios.applications.opportunity_assistant.pipeline import render_console_report, run_pipeline


def main() -> None:
    """Run the sample opportunity pipeline and print the report."""

    print(render_console_report(run_pipeline()))


if __name__ == "__main__":
    main()
