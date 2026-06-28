"""Console entry point for the Sprint 7A Opportunity Assistant."""

from __future__ import annotations

import argparse
import json

from cios.applications.opportunity_assistant.agent_adapter import (
    OpportunityAssessmentAgent,
)
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
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Include passive OpportunityAssessmentAgent output.",
    )
    args = parser.parse_args()

    result = run_pipeline()
    agent_output = OpportunityAssessmentAgent().assess(result) if args.agent else None

    if args.json:
        if agent_output is None:
            print(result.model_dump_json(indent=2))
            return

        payload = result.model_dump(mode="json")
        payload["agent_output"] = agent_output.model_dump(mode="json")
        print(json.dumps(payload, indent=2))
        return

    print(render_console_report(result, agent_output=agent_output))


if __name__ == "__main__":
    main()
