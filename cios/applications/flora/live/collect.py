"""CLI and shared service for governed Flora live evidence collection."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
from typing import Any

from cios.applications.flora.live.extractor import extract_evidence_with_diagnostics
from cios.applications.flora.live.fetcher import fetch_html
from cios.applications.flora.live.documents import fetch_document, parse_pdf_document
from cios.applications.flora.memory.factual_twin import extract_factual_evidence
from cios.applications.flora.live.source_registry import SOURCES, canonical_organisation, canonical_enterprise_id, collection_scope, enabled_sources, load_collection_profile, source_canonical_enterprise_id
from cios.applications.flora.live.store import DEFAULT_DIAGNOSTICS_PATH, DEFAULT_PATH, load_evidence_fingerprints, read_jsonl, unique_evidence, write_jsonl
from pathlib import Path
import json, os, uuid
from cios.applications.flora.live.progress import complete_state, read_state, start_state, update_state
from cios.applications.flora.live.alignment import build_acquisition_plans, lifecycle_action
from cios.applications.flora.memory.service import ObservationMemoryService

FAILURE_CATEGORIES = {"access_blocked", "timeout", "network_error", "non_html", "unsupported_media_type", "pdf_extraction_failure", "table_extraction_failure", "no_relevant_evidence", "parser_error", "unknown"}


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
    if "unsupported media type" in text:
        return "unsupported_media_type"
    if "non-html" in text or "content type" in text or "max_bytes" in text:
        return "non_html"
    if "pdf" in text or "embedded text" in text or "encryption" in text:
        return "pdf_extraction_failure"
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
    diag.update(lifecycle_action(diag))
    diag["recommended_source_fix"] = source_improvement_recommendation(diag)
    return diag


def collect(organisation: str | None = None, *, profile_id: str | None = None, collection_mode: str | None = None, run_id: str | None = None, passes: list[str] | None = None) -> dict[str, Any]:
    """Collect evidence from the governed source allow-list and write diagnostics."""
    from cios.applications.flora.observatory.engine import build_observatory, compare_observatory_snapshots, observatory_snapshot

    before_observatory = observatory_snapshot(build_observatory())
    run_id = run_id or f"flora-run-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    scope = collection_scope(profile_id, run_id=run_id, mode=collection_mode, passes=passes) if profile_id else None
    mode = collection_mode or (scope.collection_mode if scope else "live_plus_seeded")
    sources = enabled_sources(organisation, profile_id=profile_id, passes=passes) if profile_id or passes else enabled_sources(organisation)
    scoped_enterprise_id = scope.canonical_enterprise_id if scope else canonical_enterprise_id(organisation)
    scoped_display_name = scope.display_name if scope else (canonical_organisation(organisation) if organisation else "All configured enterprises")
    selected_passes = passes or (load_collection_profile(profile_id).get("default_passes", []) if profile_id else [])
    if scope:
        permitted = set(scope.permitted_source_ids)
        out_of_scope = [s.source_id for s in sources if s.source_id not in permitted or source_canonical_enterprise_id(s) != scope.canonical_enterprise_id]
        if out_of_scope:
            raise ValueError(f"Collection scope violation for {scope.collection_profile}: {', '.join(out_of_scope)}")
    collection_started_at = datetime.now(UTC).isoformat()
    if read_state().get("run_id") != run_id:
        start_state(len(sources), run_id=run_id, canonical_enterprise_id=scoped_enterprise_id, enterprise_display_name=scoped_display_name, profile_id=profile_id, collection_mode=mode, collection_pass=",".join(selected_passes), status="starting")
    else:
        update_state(status="collecting", latest_message="Collection started.")
    diagnostics: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    for source in sources:
        update_state(status="collecting", current_source_name=source.source_name, latest_message=f"Collecting {source.source_name}")
        attempted_at = collection_started_at
        result = fetch_html(str(source.url))
        source_evidence: list[dict[str, Any]] = []
        rejected_evidence: list[dict[str, Any]] = []
        parse_error: str | None = None
        succeeded = result.succeeded
        if (not result.succeeded) and (str(source.url).lower().endswith(".pdf") or "non-html content type" in result.error.lower()):
            update_state(status="parsing", latest_message=f"Parsing document for {source.source_name}")
            doc_fetch = fetch_document(str(source.url))
            doc = parse_pdf_document(doc_fetch, source, canonical_enterprise_id=source_canonical_enterprise_id(source))
            succeeded = doc_fetch.succeeded
            result = type(result)(url=result.url, succeeded=succeeded, status_code=doc_fetch.status_code, html="", error=doc.error)
            if doc.parser_status == "parsed":
                update_state(status="extracting_evidence", latest_message=f"Extracting factual Evidence from {source.source_name}")
                source_evidence, rejected_evidence = extract_factual_evidence(doc)
                parse_error = None
            else:
                parse_error = doc.error or "PDF extraction failed"
            for item in source_evidence:
                item["collection_mode"] = mode
            diagnostics_extra = {"documents_retrieved": 1 if doc_fetch.succeeded else 0, "pdfs_parsed": 1 if doc.parser_status == "parsed" else 0, "pages_extracted": doc.page_count if doc.parser_status == "parsed" else 0, "tables_detected": len([e for e in source_evidence if e.get("origin") == "table"]), "document_id": doc.document_id, "document_checksum": doc.checksum, "parser_status": doc.parser_status, "extraction_warnings": list(doc.warnings)}
        elif result.succeeded:
            try:
                update_state(status="extracting_evidence", latest_message=f"Extracting Evidence from {source.source_name}")
                source_evidence, rejected_evidence = extract_evidence_with_diagnostics(source, result.html)
                for item in source_evidence:
                    item["enterprise_id"] = source_canonical_enterprise_id(source)
                    item["canonical_enterprise_id"] = source_canonical_enterprise_id(source)
                    item["organisation"] = source_canonical_enterprise_id(source)
                    item["collection_mode"] = mode
                    item["source_provenance"] = "live"
                if mode == "live_authoritative":
                    source_evidence = [e for e in source_evidence if e.get("source_provenance") == "live" and "seed" not in str(e.get("source_type", "")).lower() and "synthetic" not in str(e.get("source_type", "")).lower()]
                evidence.extend(source_evidence)
                diagnostics_extra = {"documents_retrieved": 0, "pdfs_parsed": 0, "pages_extracted": 0, "tables_detected": 0}
            except Exception as exc:  # parser diagnostics must not stop other governed sources
                succeeded = False
                parse_error = f"parser_error: {exc}"
                diagnostics_extra = {"documents_retrieved": 0, "pdfs_parsed": 0, "pages_extracted": 0, "tables_detected": 0}
        else:
            diagnostics_extra = {"documents_retrieved": 0, "pdfs_parsed": 0, "pages_extracted": 0, "tables_detected": 0}
        evidence.extend([e for e in source_evidence if e not in evidence])
        diag = _diagnostic(source, attempted_at, result, source_evidence, rejected_evidence, parse_error, succeeded)
        diag.update(diagnostics_extra)
        diagnostics.append(diag)
        evidence_rejected_running = sum(int(d.get("rejected_evidence_count") or 0) for d in diagnostics)
        evidence_downgraded_running = sum(int(d.get("downgraded_evidence_count") or 0) for d in diagnostics)
        evidence_context_running = sum(int(d.get("context_only_count") or 0) for d in diagnostics)
        evidence_candidates = len(evidence) + evidence_rejected_running + evidence_downgraded_running
        update_state(sources_attempted=len(diagnostics), sources_succeeded=len([d for d in diagnostics if d["status"] != "failed"]), sources_retrieved=len([d for d in diagnostics if d["status"] != "failed"]), sources_failed=len([d for d in diagnostics if d["status"] == "failed"]), evidence_extracted=len(evidence), evidence_candidates=evidence_candidates, evidence_accepted=len(evidence), evidence_rejected=evidence_rejected_running, evidence_downgraded=evidence_downgraded_running, evidence_context_only=evidence_context_running, documents_retrieved=sum(int(d.get("documents_retrieved") or 0) for d in diagnostics), pdfs_parsed=sum(int(d.get("pdfs_parsed") or 0) for d in diagnostics), pages_extracted=sum(int(d.get("pages_extracted") or 0) for d in diagnostics), tables_detected=sum(int(d.get("tables_detected") or 0) for d in diagnostics), latest_message=f"Finished {source.source_name}")
    update_state(status="accepting_evidence", latest_message="Applying Evidence acceptance and duplicate checks.")
    new_evidence, duplicate_count, fingerprints = unique_evidence(evidence)
    output = write_jsonl(new_evidence) if new_evidence else DEFAULT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.touch(exist_ok=True)
    update_state(status="creating_observations", latest_message="Creating Observations from accepted Evidence.")
    memory_results = [ObservationMemoryService().accept_evidence(item) for item in new_evidence]
    update_state(status="updating_model", latest_message="Updating Enterprise Model projection.")
    write_jsonl(diagnostics, DEFAULT_DIAGNOSTICS_PATH)
    after_observatory = observatory_snapshot(build_observatory())
    observatory_delta = compare_observatory_snapshots(
        before_observatory,
        after_observatory,
        tuple(str(item.get("evidence_id") or "") for item in new_evidence if item.get("evidence_id")),
    )
    failures = [d for d in diagnostics if d["status"] == "failed"]
    plans = build_acquisition_plans(SOURCES, read_jsonl(DEFAULT_PATH) + new_evidence, diagnostics)
    insufficient = [p["organisation"] for p in plans if p.get("collection_confidence", 0) < 60]
    urgent = [p for p in plans if p.get("collection_priority") == "collect urgently"]
    completed_at = datetime.now(UTC).isoformat()
    obs_created = len([r for r in memory_results if r.action == "created"])
    obs_corroborated = len([r for r in memory_results if r.action == "updated"])
    attrs_created = len([r for r in memory_results if r.action == "created"])
    unknowns_created = len([r for r in memory_results if r.unknown_created])
    contradictions_created = len([r for r in memory_results if r.contradiction])
    evidence_rejected = sum(int(d.get("rejected_evidence_count") or 0) for d in diagnostics)
    evidence_downgraded = sum(int(d.get("downgraded_evidence_count") or 0) for d in diagnostics)
    evidence_candidates = len(evidence) + evidence_rejected + evidence_downgraded
    source_failures = [d for d in diagnostics if d["status"] == "failed"]
    result_state = "completed" if diagnostics and len([d for d in diagnostics if d["status"] != "failed"]) >= 1 and len(new_evidence) >= 1 and (obs_created + obs_corroborated) >= 1 and (attrs_created + obs_corroborated) >= 1 else "completed_with_no_accepted_intelligence"
    manifest = {"run_id": run_id, "canonical_enterprise_id": scoped_enterprise_id, "enterprise_display_name": scoped_display_name, "profile_id": profile_id, "started_at": collection_started_at, "completed_at": completed_at, "collection_mode": mode, "passes": selected_passes, "sources_planned": [s.source_id for s in sources], "sources_attempted": [d["source_id"] for d in diagnostics], "sources_retrieved": [d["source_id"] for d in diagnostics if d["status"] != "failed"], "sources_failed": [d["source_id"] for d in source_failures], "evidence_candidates": evidence_candidates, "evidence_accepted": len(new_evidence), "evidence_rejected": evidence_rejected, "evidence_downgraded": evidence_downgraded, "evidence_context_only": sum(int(d.get("context_only_count") or 0) for d in diagnostics), "evidence_duplicate": duplicate_count, "evidence_corroborated": obs_corroborated, "evidence_extraction_failed": 0, "documents_retrieved": sum(int(d.get("documents_retrieved") or 0) for d in diagnostics), "pdfs_parsed": sum(int(d.get("pdfs_parsed") or 0) for d in diagnostics), "pages_extracted": sum(int(d.get("pages_extracted") or 0) for d in diagnostics), "tables_detected": sum(int(d.get("tables_detected") or 0) for d in diagnostics), "observations_created": obs_created, "observations_corroborated": obs_corroborated, "observations_rejected": 0, "model_attributes_created": attrs_created, "model_attributes_changed": len([r for r in memory_results if r.action == "updated"]), "model_attributes_reconfirmed": obs_corroborated, "unknowns_created": unknowns_created, "contradictions_created": contradictions_created, "result_state": result_state, "errors": [d for d in diagnostics if d.get("status") == "failed"], "warnings": []}
    if len(manifest["sources_attempted"]) != len(manifest["sources_retrieved"]) + len(manifest["sources_failed"]):
        raise ValueError("Source counters do not reconcile")
    if manifest["evidence_candidates"] != manifest["evidence_accepted"] + manifest["evidence_rejected"] + manifest["evidence_downgraded"] + manifest["evidence_duplicate"]:
        raise ValueError("Evidence candidate dispositions do not reconcile")
    mpath = Path(".flora_pilot/collection_manifests") / f"{run_id}.json"
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    final_progress = complete_state(result_state, f"Collection complete\nSources: {len(manifest['sources_retrieved'])}/{len(sources)} retrieved\nEvidence: {manifest['evidence_accepted']} accepted, {manifest['evidence_rejected']} rejected\nObservations: {obs_created} created, {obs_corroborated} corroborated\nModel: {attrs_created} attributes created, {unknowns_created} Unknowns", sources_attempted=len(manifest["sources_attempted"]), sources_succeeded=len(manifest["sources_retrieved"]), sources_retrieved=len(manifest["sources_retrieved"]), sources_failed=len(manifest["sources_failed"]), evidence_candidates=evidence_candidates, evidence_accepted=len(new_evidence), evidence_rejected=evidence_rejected, evidence_downgraded=evidence_downgraded, evidence_context_only=manifest["evidence_context_only"], evidence_duplicate=duplicate_count, evidence_corroborated=obs_corroborated, evidence_extraction_failed=0, documents_retrieved=manifest["documents_retrieved"], pdfs_parsed=manifest["pdfs_parsed"], pages_extracted=manifest["pages_extracted"], tables_detected=manifest["tables_detected"], observations_created=obs_created, observations_corroborated=obs_corroborated, observations_rejected=0, model_attributes_created=attrs_created, model_attributes_changed=manifest["model_attributes_changed"], model_attributes_reconfirmed=obs_corroborated, unknowns_created=unknowns_created, contradictions_created=contradictions_created, warnings=manifest["warnings"], errors=manifest["errors"])
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
        "accepted_evidence_count": len(new_evidence),
        "documents_retrieved": manifest.get("documents_retrieved", 0),
        "pdfs_parsed": manifest.get("pdfs_parsed", 0),
        "pages_extracted": manifest.get("pages_extracted", 0),
        "tables_detected": manifest.get("tables_detected", 0),
        "evidence_candidates": evidence_candidates,
        "result_state": result_state,
        "rejected_evidence_count": sum(int(d.get("rejected_evidence_count") or 0) for d in diagnostics),
        "downgraded_evidence_count": sum(int(d.get("downgraded_evidence_count") or 0) for d in diagnostics),
        "primary_evidence_count": sum(int(d.get("primary_evidence_count") or 0) for d in diagnostics),
        "secondary_evidence_count": sum(int(d.get("secondary_evidence_count") or 0) for d in diagnostics),
        "context_only_count": sum(int(d.get("context_only_count") or 0) for d in diagnostics),
        "diagnostics_only_count": len([d for d in diagnostics if d.get("lifecycle_action") == "diagnostics only"]),
        "organisations_with_insufficient_coverage": insufficient,
        "recommended_next_collection_actions": [f"{p['organisation']}: {', '.join(p.get('next_collection_objectives', [])[:2])}" for p in urgent[:10]],
        "source_improvement_recommendations": [d.get("recommended_source_fix") for d in diagnostics if d.get("recommended_source_fix")],
        "diagnostics": diagnostics,
        "collection_manifest": manifest,
        "collection_manifest_location": str(mpath),
        "collection_mode": mode,
        "canonical_enterprise_id": scoped_enterprise_id,
        "observations_updated": len(memory_results),
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
        rows.append({**source.model_dump(mode="json"), **lifecycle_action(latest or {"source_type": source.source_type, "source_name": source.source_name, "url": str(source.url), "evidence_count": evidence_count}), "last_status": status, "evidence_count": evidence_count, "recommended_action": action, "last_attempted": latest.get("last_attempted") or latest.get("attempted_at")})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect governed Flora live evidence for pilot organisations.")
    parser.add_argument("--organisation", help="Organisation to collect; matched against the governed registry aliases.")
    parser.add_argument("--all", action="store_true", help="Collect all pilot organisations.")
    parser.add_argument("--profile", help="Collection profile ID, for example bt-group-plc.")
    parser.add_argument("--mode", choices=["live_authoritative", "live_plus_seeded", "test_fixture"], help="Collection mode.")
    parser.add_argument("--pass", dest="passes", action="append", help="Profile pass to run: baseline, change_event or recollection.")
    args = parser.parse_args()
    org = None if args.all or not args.organisation else canonical_organisation(args.organisation)
    result = collect(org, profile_id=args.profile, collection_mode=args.mode, passes=args.passes)
    print(result.get("progress_state", {}).get("latest_message", "Collection complete"))
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
