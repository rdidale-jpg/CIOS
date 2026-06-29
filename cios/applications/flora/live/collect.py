"""CLI for governed Flora live evidence collection."""
from __future__ import annotations

import argparse
from typing import Any

from cios.applications.flora.live.extractor import extract_evidence
from cios.applications.flora.live.fetcher import fetch_html
from cios.applications.flora.live.source_registry import canonical_organisation, enabled_sources
from cios.applications.flora.live.store import DEFAULT_PATH, write_jsonl


def collect(organisation: str | None = None) -> dict[str, Any]:
    sources = enabled_sources(organisation)
    failures: list[dict[str, str]] = []
    evidence: list[dict[str, Any]] = []
    succeeded = 0
    for source in sources:
        result = fetch_html(str(source.url))
        if not result.succeeded:
            failures.append({"source_id": source.source_id, "source_name": source.source_name, "url": str(source.url), "error": result.error})
            continue
        succeeded += 1
        evidence.extend(extract_evidence(source, result.html))
    output = write_jsonl(evidence) if evidence else DEFAULT_PATH
    if not evidence:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.touch(exist_ok=True)
    return {"sources_attempted": len(sources), "sources_succeeded": succeeded, "evidence_objects_created": len(evidence), "failures": failures, "output_location": str(output)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect governed Flora live evidence for pilot organisations.")
    parser.add_argument("--organisation", choices=["ThamesWater", "NationalGrid", "BT", "Vodafone"], help="Pilot organisation to collect.")
    parser.add_argument("--all", action="store_true", help="Collect all pilot organisations.")
    args = parser.parse_args()
    org = None if args.all or not args.organisation else canonical_organisation(args.organisation)
    result = collect(org)
    print(f"sources attempted: {result['sources_attempted']}")
    print(f"sources succeeded: {result['sources_succeeded']}")
    print(f"evidence objects created: {result['evidence_objects_created']}")
    print("failures:")
    for failure in result["failures"]:
        print(f"- {failure['source_name']} ({failure['url']}): {failure['error']}")
    if not result["failures"]:
        print("- none")
    print(f"output location: {result['output_location']}")


if __name__ == "__main__":
    main()
