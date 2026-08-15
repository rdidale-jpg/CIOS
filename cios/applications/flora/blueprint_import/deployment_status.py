"""Operational deployment-status decisions for the Import Twin panel."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

MATERIAL_COMPONENTS = {
    "import/validator",
    "adapter/profile",
    "semantic construction",
    "Canonical Factual Projection",
    "Observation runtime",
    "owner assessment",
    "Research Gap logic",
}


@dataclass(frozen=True)
class DeploymentDecision:
    status_code: str
    status_label: str
    should_test_now: str
    next_action: str
    fresh_import_required: str
    change_included: bool
    containment_result: str
    merge_mode: str
    evidence_quality: str
    unresolved_metadata: list[str]


def _unknown(value: Any) -> bool:
    return not value or "Unavailable" in str(value) or str(value).lower() == "unknown"


def _parse_time(value: Any) -> datetime | None:
    if _unknown(value):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


def _git_contains(deployed_sha: str, source_sha: str) -> str:
    if _unknown(deployed_sha) or _unknown(source_sha):
        return "unknown — SHA metadata unavailable"
    try:
        rc = subprocess.run(["git", "merge-base", "--is-ancestor", source_sha, deployed_sha], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    except Exception:
        return "unknown — repository history unavailable"
    return "contains expected source commit" if rc == 0 else "does not contain expected source commit"


def classify_candidate_freshness(change: dict[str, Any], imported_at: Any) -> tuple[str, list[str]]:
    impact = str(change.get("candidate_state_impact") or "").strip().lower()
    if impact in {"read-only", "read_only", "projection-only", "none"}:
        return "No", []
    if impact in {"regenerate", "persisted-state-change"}:
        cutoff = _parse_time(change.get("reimport_required_if_older_than_change"))
        imported = _parse_time(imported_at)
        if not cutoff or not imported:
            return "Cannot determine", ["candidate timestamp or regeneration cutoff unavailable"]
        return ("Yes" if imported < cutoff else "No"), []
    components = set(change.get("material_runtime_components_changed") or [])
    if not components:
        return "No", []
    if not components.intersection(MATERIAL_COMPONENTS):
        return "No", []
    cutoff = _parse_time(change.get("reimport_required_if_older_than_change")) or _parse_time(change.get("deployment_completed_at")) or _parse_time(change.get("deployment_timestamp"))
    imported = _parse_time(imported_at)
    if not cutoff or not imported:
        return "Cannot determine", ["candidate timestamp or material-change timestamp unavailable"]
    return ("Yes" if imported < cutoff else "No"), []


def decide_deployment_status(change: dict[str, Any], imported_at: Any = "") -> DeploymentDecision:
    deployed_sha = str(change.get("commit_sha") or "Unavailable")
    source_sha = str(change.get("source_commit_sha") or change.get("expected_implementation_sha") or "Unavailable")
    deployed_branch = str(change.get("branch") or "Unavailable")
    target_branch = str(change.get("target_branch") or "main")
    marker = str(change.get("deployed_change_marker") or "Unavailable")
    change_id = str(change.get("change_id") or "")
    completed = _parse_time(change.get("deployment_completed_at") or change.get("deployment_timestamp"))
    started = _parse_time(change.get("deployment_started_at"))
    window = int(change.get("expected_deployment_window_minutes") or 30)
    now = datetime.now(UTC)
    unresolved: list[str] = []

    marker_match = bool(change_id and marker == change_id)
    exact_sha = (not _unknown(deployed_sha) and not _unknown(source_sha) and deployed_sha.startswith(source_sha[:12]))
    containment = _git_contains(deployed_sha, source_sha)
    contains = containment.startswith("contains")
    included = marker_match or contains or exact_sha
    acceptance = change.get("automated_validation") or {}
    functional_pass = all(str(acceptance.get(key) or "").upper() == "PASS" for key in (
        "checksum_status", "end_to_end_test_status", "rendered_route_test_status",
        "diagnostics_reconciliation_status"))
    merge_mode = str(change.get("merge_mode") or ("squash/release marker" if marker_match and not contains else "git ancestry" if contains else "exact SHA" if exact_sha else "unverified"))

    status_text = str(change.get("latest_deployment_status") or "").lower()
    wrong_branch = (not _unknown(deployed_branch) and not _unknown(target_branch) and deployed_branch != target_branch)
    failed = "fail" in status_text
    fresh, fresh_gaps = classify_candidate_freshness(change, imported_at)
    unresolved.extend(fresh_gaps)
    for label, value in (("build timestamp", change.get("deployment_timestamp")), ("deployed change marker", marker), ("runtime fingerprint", change.get("deployment_version"))):
        if _unknown(value):
            unresolved.append(f"{label} unavailable")
    if containment.startswith("unknown") and not marker_match:
        unresolved.append("git ancestry unavailable")

    if wrong_branch or failed:
        return DeploymentDecision("DEPLOYMENT PROBLEM", "Deployment problem", "No", "Flora could not verify the latest approved change. This requires a Codex/Render deployment correction. No action is required from the Chief Architect.", fresh, included, containment, merge_mode, "authoritative deployment problem", unresolved)
    if not functional_pass:
        failed_checks = [key for key in ("checksum_status", "end_to_end_test_status",
                         "rendered_route_test_status", "diagnostics_reconciliation_status")
                         if str(acceptance.get(key) or "missing").upper() != "PASS"]
        reason = "Functional acceptance failed: " + ", ".join(failed_checks)
        return DeploymentDecision("FUNCTIONAL ACCEPTANCE FAILED", "Functional acceptance failed", "NO", reason, fresh, included, containment, merge_mode, "functional acceptance failure", unresolved)
    if included and fresh == "Yes":
        return DeploymentDecision("REIMPORT REQUIRED", "Reimport required", "Yes — after reimport", "The latest approved change is live. Import the unchanged TEL-001 package again, then follow the test checklist.", fresh, True, containment, merge_mode, "authoritative inclusion", unresolved)
    if included and fresh == "No" and not unresolved:
        return DeploymentDecision("READY FOR TESTING", "Ready for testing", "Yes", "The latest approved change is live. Test the pages below.", fresh, True, containment, merge_mode, "authoritative inclusion", unresolved)
    if included:
        return DeploymentDecision("READY FOR FUNCTIONAL TEST — DEPLOYMENT METADATA INCOMPLETE", "Ready for functional test — deployment metadata incomplete", "YES", "Proceed with functional testing. Known limitation: Deployment metadata incomplete.", fresh, True, containment, merge_mode, "functional acceptance passed; optional deployment metadata incomplete", unresolved)
    deadline = (started or completed) + timedelta(minutes=window) if (started or completed) else None
    if deadline and now <= deadline:
        return DeploymentDecision("WAITING FOR DEPLOYMENT", "Waiting for deployment", "No", "No action required. Flora is waiting for Render to publish the latest approved change. Refresh this page shortly.", fresh, False, containment, merge_mode, "deployment window open", unresolved)
    if deadline and now > deadline and not unresolved:
        return DeploymentDecision("DEPLOYMENT PROBLEM", "Deployment problem", "No", "Flora could not verify the latest approved change. This requires a Codex/Render deployment correction. No action is required from the Chief Architect.", fresh, False, containment, merge_mode, "deployment window elapsed", unresolved)
    if functional_pass:
        limitation = "; ".join(unresolved) or "deployment identity metadata incomplete"
        return DeploymentDecision("READY FOR FUNCTIONAL TEST — DEPLOYMENT METADATA INCOMPLETE", "Ready for functional test — deployment metadata incomplete", "YES", f"Proceed with functional testing. Known limitation: {limitation}", fresh, False, containment, merge_mode, "functional acceptance passed; optional deployment metadata incomplete", unresolved)
    return DeploymentDecision("METADATA INCOMPLETE", "Metadata incomplete", "No", "Flora cannot yet verify the deployed change because deployment metadata is incomplete. No technical action is required from the Chief Architect.", fresh, False, containment, merge_mode, "insufficient metadata", unresolved)
