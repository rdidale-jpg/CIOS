"""CLI and shared service for governed Flora live evidence collection."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
from typing import Any

from cios.applications.flora.live.extractor import extract_evidence_with_diagnostics
from cios.applications.flora.live.fetcher import fetch_html
from cios.applications.flora.live.source_registry import SOURCES, canonical_organisation, enabled_sources
from cios.applications.flora.live.store import DEFAULT_DIAGNOSTICS_PATH, DEFAULT_PATH, load_evidence_fingerprints, read_jsonl, unique_evidence, write_jsonl
from cios.applications.flora.live.progress import complete_state, read_state, start_state, update_state

FAILURE_CATEGORIES = {"access_blocked", "timeout", "network_error", "non_html", "no_relevant_evidence", "parser_error", "unknown"}


def categorise_failure(*, succeeded: bool, http_status: int | None = None, error: str | None = None, evidence_count: int = 0) -> str | None:
    """Return the governed diagnostics category for a source attempt."""
    if succeeded and evidence_count > 0:
        return None
    if succeeded and evidence_count == 0:
        return "no_relevant_evidence"
    text = (error or "").lower()
    if http_status in {401, 403, 429} or "forbidden" in text or "blocked" in text or "captcha" in text:
        return "access_blocked"
    if "timed out" in text or "timeout" in text:
        return "timeout"
    if "non-html" in text or "content type" in text or "max_bytes" in text:
        return "non_html"
    if "parser" in text:
        return "parser_error"
    if "urlopen" in text or "name or service" in text or "connection" in text or "network" in text or "tunnel" in text:
        return "network_error"
    return "unknown"


def _status(succeeded: bool, evidence_count: int) -> str:
    if succeeded and evidence_count > 0:
        return "succeeded"
    if succeeded:
        return "no evidence"
    return "failed"


def source_improvement_recommendation(diag: dict[str, Any]) -> str:
    org = diag.get("organisation", "Source")
    kind = diag.get("source_classification") or diag.get("source_type") or "source"
    if diag.get("status") == "failed":
        return f"{org} {kind} failed; verify the governed URL or replace with a stable report, results, procurement or named news URL."
    if diag.get("accepted_evidence_count", 0) == 0 and diag.get("rejected_evidence_count", 0) > 0:
        if kind == "landing_page" or "govuk" in str(diag.get("source_type", "")).lower():
            return f"{org} GOV.UK or landing page produced only boilerplate; add annual report/accounts, latest documents and procurement pipeline sources."
        if "investor" in str(diag.get("source_type", "")).lower():
            return f"{org} investor landing page produced weak page furniture; add annual report PDF/HTML and FY results page."
        return f"{org} source produced noisy context; add case-study, press-release-specific, report or named programme URLs."
    if diag.get("context_only_count", 0) and not diag.get("primary_evidence_count", 0):
        return f"{org} evidence is context-heavy; add primary report, regulator, procurement or contract-award sources."
    return "Keep monitored; source produced usable governed evidence."

def _diagnostic(source: Any, attempted_at: str, result: Any, source_evidence: list[dict[str, Any]], rejected_evidence: list[dict[str, Any]] | None = None, error: str | None = None, succeeded: bool | None = None) -> dict[str, Any]:
    ok = result.succeeded if succeeded is None else succeeded
    evidence_count = len(source_evidence)
    failure_reason = categorise_failure(succeeded=ok, http_status=result.status_code, error=error if error is not None else result.error, evidence_count=evidence_count)
    source_kind = source_evidence[0].get("source_classification") if source_evidence else getattr(source, "source_classification", source.source_type)
    diag = {
        "source_id": source.source_id,
        "organisation": source.organisation,
        "source_name": source.source_name,
        "source_type": source.source_type,
        "source_classification": source_kind,
        "url": str(source.url),
        "status": _status(ok, evidence_count),
        "success": ok and evidence_count > 0,
        "http_status": result.status_code,
        "error": error if error is not None else result.error,
        "evidence_count": evidence_count,
        "last_attempted": attempted_at,
        "attempted_at": attempted_at,
        "failure_reason": failure_reason,
        "accepted_evidence_count": evidence_count,
        "rejected_evidence_count": len(rejected_evidence or []),
        "downgraded_evidence_count": len([e for e in (rejected_evidence or []) if e.get("relevance_level") == "LOW"]),
        "primary_evidence_count": len([e for e in source_evidence if e.get("evidence_type") == "Primary Evidence"]),
        "secondary_evidence_count": len([e for e in source_evidence if e.get("evidence_type") == "Secondary Evidence"]),
        "context_only_count": len([e for e in [*source_evidence, *(rejected_evidence or [])] if e.get("evidence_type") == "Context Only"]),
        "boilerplate_only": evidence_count == 0 and any(e.get("boilerplate_detected") for e in (rejected_evidence or [])),
        "unsupported_interpretations": [{
            "snippet": e.get("snippet", ""),
            "attempted_classification": e.get("attempted_classification") or e.get("commercial_condition", ""),
            "rejection_reason": "; ".join(e.get("rejection_reasons", [])),
            "safer_interpretation": e.get("safer_interpretation", "Treat as diagnostics only."),
            "relevance_level": e.get("relevance_level", "REJECT"),
        } for e in (rejected_evidence or [])[:8]],
    }
    diag["recommended_source_fix"] = source_improvement_recommendation(diag)
    return diag


def collect(organisation: str | None = None) -> dict[str, Any]:
    """Collect evidence from the governed source allow-list and write diagnostics."""
    from cios.applications.flora.observatory.engine import build_observatory, compare_observatory_snapshots, observatory_snapshot

    before_observatory = observatory_snapshot(build_observatory())
    sources = enabled_sources(organisation)
    start_state(len(sources))
    diagnostics: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    collection_started_at = datetime.now(UTC).isoformat()
    for source in sources:
        update_state(current_source_name=source.source_name, latest_message=f"Collecting {source.source_name}")
        attempted_at = collection_started_at
        result = fetch_html(str(source.url))
        source_evidence: list[dict[str, Any]] = []
        rejected_evidence: list[dict[str, Any]] = []
        parse_error: str | None = None
        succeeded = result.succeeded
        if result.succeeded:
            try:
                source_evidence, rejected_evidence = extract_evidence_with_diagnostics(source, result.html)
                evidence.extend(source_evidence)
            except Exception as exc:  # parser diagnostics must not stop other governed sources
                succeeded = False
                parse_error = f"parser_error: {exc}"
        diagnostics.append(_diagnostic(source, attempted_at, result, source_evidence, rejected_evidence, parse_error, succeeded))
        update_state(sources_attempted=len(diagnostics), sources_succeeded=len([d for d in diagnostics if d["status"] != "failed"]), sources_failed=len([d for d in diagnostics if d["status"] == "failed"]), evidence_extracted=len(evidence), latest_message=f"Finished {source.source_name}")
    new_evidence, duplicate_count, fingerprints = unique_evidence(evidence)
    output = write_jsonl(new_evidence) if new_evidence else DEFAULT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.touch(exist_ok=True)
    write_jsonl(diagnostics, DEFAULT_DIAGNOSTICS_PATH)
    after_observatory = observatory_snapshot(build_observatory())
    observatory_delta = compare_observatory_snapshots(
        before_observatory,
        after_observatory,
        tuple(str(item.get("evidence_id") or "") for item in new_evidence if item.get("evidence_id")),
    )
    failures = [d for d in diagnostics if d["status"] == "failed"]
    final_progress = complete_state("completed", "Collection completed.")
    return {
        "progress_state": final_progress,
        "last_collection_time": diagnostics[-1]["last_attempted"] if diagnostics else None,
        "sources_attempted": len(sources),
        "sources_succeeded": len([d for d in diagnostics if d["status"] != "failed"]),
        "sources_failed": len(failures),
        "sources_with_evidence": len([d for d in diagnostics if d["evidence_count"] > 0]),
        "evidence_objects_extracted": len(evidence),
        "evidence_objects_created": len(new_evidence),
        "new_evidence_added": len(new_evidence),
        "duplicate_evidence_skipped": duplicate_count,
        "total_unique_evidence_objects": len(fingerprints),
        "failures": failures,
        "accepted_evidence_count": len(evidence),
        "rejected_evidence_count": sum(int(d.get("rejected_evidence_count") or 0) for d in diagnostics),
        "downgraded_evidence_count": sum(int(d.get("downgraded_evidence_count") or 0) for d in diagnostics),
        "primary_evidence_count": sum(int(d.get("primary_evidence_count") or 0) for d in diagnostics),
        "secondary_evidence_count": sum(int(d.get("secondary_evidence_count") or 0) for d in diagnostics),
        "context_only_count": sum(int(d.get("context_only_count") or 0) for d in diagnostics),
        "source_improvement_recommendations": [d.get("recommended_source_fix") for d in diagnostics if d.get("recommended_source_fix")],
        "diagnostics": diagnostics,
        "observatory_delta": observatory_delta,
        "output_location": str(output),
        "diagnostics_location": str(DEFAULT_DIAGNOSTICS_PATH),
    }


def current_status() -> dict[str, Any]:
    diagnostics = read_jsonl(DEFAULT_DIAGNOSTICS_PATH)
    fingerprints = load_evidence_fingerprints(DEFAULT_PATH)
    latest_batch_time = diagnostics[-1].get("last_attempted") or diagnostics[-1].get("attempted_at") if diagnostics else None
    latest = [d for d in diagnostics if (d.get("last_attempted") or d.get("attempted_at")) == latest_batch_time] if latest_batch_time else []
    return {
        "last_collection_time": latest_batch_time,
        "sources_attempted": len(latest),
        "sources_succeeded": len([d for d in latest if d.get("status") != "failed" and (d.get("success") or d.get("status") == "no evidence")]),
        "sources_failed": len([d for d in latest if d.get("status") == "failed" or (not d.get("success") and d.get("status") != "no evidence")]),
        "sources_with_evidence": len([d for d in latest if d.get("evidence_count", 0) > 0]),
        "evidence_objects_collected": len(fingerprints),
        "total_unique_evidence_objects": len(fingerprints),
        "diagnostics": latest,
        "evidence_path": str(DEFAULT_PATH),
        "diagnostics_path": str(DEFAULT_DIAGNOSTICS_PATH),
        "progress_state": read_state(),
    }


def source_coverage() -> list[dict[str, Any]]:
    diagnostics = read_jsonl(DEFAULT_DIAGNOSTICS_PATH)
    latest_by_source = {d.get("source_id"): d for d in diagnostics}
    rows = []
    for source in SOURCES:
        latest = latest_by_source.get(source.source_id, {})
        status = latest.get("status", "not attempted")
        evidence_count = latest.get("evidence_count", 0)
        if not source.enabled:
            action = "Enable if this source is still governed and useful."
        elif status == "not attempted":
            action = "Run live collection."
        elif status == "failed":
            action = f"Review access or URL; category: {latest.get('failure_reason') or 'unknown'}."
        elif status == "no evidence":
            action = "Keep monitored; consider a more relevant stable page."
        else:
            action = "Keep monitored."
        rows.append({**source.model_dump(mode="json"), "last_status": status, "evidence_count": evidence_count, "recommended_action": action, "last_attempted": latest.get("last_attempted") or latest.get("attempted_at")})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect governed Flora live evidence for pilot organisations.")
    parser.add_argument("--organisation", help="Organisation to collect; matched against the governed registry aliases.")
    parser.add_argument("--all", action="store_true", help="Collect all pilot organisations.")
    args = parser.parse_args()
    org = None if args.all or not args.organisation else canonical_organisation(args.organisation)
    result = collect(org)
    print(f"sources attempted: {result['sources_attempted']}")
    print(f"sources succeeded: {result['sources_succeeded']}")
    print(f"sources failed: {result['sources_failed']}")
    print(f"evidence extracted: {result['evidence_objects_extracted']}")
    print(f"new evidence added: {result['new_evidence_added']}")
    print(f"duplicate evidence skipped: {result['duplicate_evidence_skipped']}")
    print(f"total unique evidence objects: {result['total_unique_evidence_objects']}")
    print("source diagnostics:")
    for diag in result["diagnostics"]:
        status = diag["http_status"] if diag["http_status"] is not None else diag["error"]
        print(f"- {diag['source_id']} | status={diag['status']} | status/error={status} | evidence={diag['evidence_count']} | category={diag.get('failure_reason')}")
    print(f"output location: {result['output_location']}")
    print(f"diagnostics location: {result['diagnostics_location']}")


if __name__ == "__main__":
    main()
