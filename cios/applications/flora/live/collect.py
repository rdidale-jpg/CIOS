"""CLI and shared service for governed Flora live evidence collection."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
from typing import Any

from cios.applications.flora.live.extractor import extract_evidence
from cios.applications.flora.live.fetcher import fetch_html
from cios.applications.flora.live.source_registry import canonical_organisation, enabled_sources
from cios.applications.flora.live.store import DEFAULT_DIAGNOSTICS_PATH, DEFAULT_PATH, read_jsonl, write_jsonl


def collect(organisation: str | None = None) -> dict[str, Any]:
    """Collect evidence from the governed source allow-list and write diagnostics."""
    sources = enabled_sources(organisation)
    diagnostics: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    collection_started_at = datetime.now(UTC).isoformat()
    for source in sources:
        attempted_at = collection_started_at
        result = fetch_html(str(source.url))
        source_evidence: list[dict[str, Any]] = []
        if result.succeeded:
            source_evidence = extract_evidence(source, result.html)
            evidence.extend(source_evidence)
        diagnostics.append({
            "source_id": source.source_id,
            "organisation": source.organisation,
            "source_name": source.source_name,
            "url": str(source.url),
            "success": result.succeeded,
            "http_status": result.status_code,
            "error": result.error,
            "evidence_count": len(source_evidence),
            "attempted_at": attempted_at,
        })
    output = write_jsonl(evidence) if evidence else DEFAULT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.touch(exist_ok=True)
    write_jsonl(diagnostics, DEFAULT_DIAGNOSTICS_PATH)
    failures = [d for d in diagnostics if not d["success"]]
    return {
        "last_collection_time": diagnostics[-1]["attempted_at"] if diagnostics else None,
        "sources_attempted": len(sources),
        "sources_succeeded": len([d for d in diagnostics if d["success"]]),
        "sources_failed": len(failures),
        "evidence_objects_created": len(evidence),
        "failures": failures,
        "diagnostics": diagnostics,
        "output_location": str(output),
        "diagnostics_location": str(DEFAULT_DIAGNOSTICS_PATH),
    }


def current_status() -> dict[str, Any]:
    diagnostics = read_jsonl(DEFAULT_DIAGNOSTICS_PATH)
    evidence = read_jsonl(DEFAULT_PATH)
    latest_batch_time = diagnostics[-1]["attempted_at"] if diagnostics else None
    latest = [d for d in diagnostics if d.get("attempted_at") == latest_batch_time] if latest_batch_time else []
    return {
        "last_collection_time": latest_batch_time,
        "sources_attempted": len(latest),
        "sources_succeeded": len([d for d in latest if d.get("success")]),
        "sources_failed": len([d for d in latest if not d.get("success")]),
        "evidence_objects_collected": len(evidence),
        "diagnostics": latest,
        "evidence_path": str(DEFAULT_PATH),
        "diagnostics_path": str(DEFAULT_DIAGNOSTICS_PATH),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect governed Flora live evidence for pilot organisations.")
    parser.add_argument("--organisation", choices=["ThamesWater", "NationalGrid", "BT", "Vodafone"], help="Pilot organisation to collect.")
    parser.add_argument("--all", action="store_true", help="Collect all pilot organisations.")
    args = parser.parse_args()
    org = None if args.all or not args.organisation else canonical_organisation(args.organisation)
    result = collect(org)
    print(f"sources attempted: {result['sources_attempted']}")
    print(f"sources succeeded: {result['sources_succeeded']}")
    print(f"sources failed: {result['sources_failed']}")
    print(f"evidence objects created: {result['evidence_objects_created']}")
    print("source diagnostics:")
    for diag in result["diagnostics"]:
        status = diag["http_status"] if diag["http_status"] is not None else diag["error"]
        print(f"- {diag['source_id']} | success={diag['success']} | status/error={status} | evidence={diag['evidence_count']}")
    print(f"output location: {result['output_location']}")
    print(f"diagnostics location: {result['diagnostics_location']}")


if __name__ == "__main__":
    main()
