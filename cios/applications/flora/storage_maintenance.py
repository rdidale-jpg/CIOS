"""Inode-focused inventory and narrowly bounded Flora storage recovery.

This module deliberately classifies names from their repository-owned paths.  It
never opens a persisted artefact while inventorying it and its destructive
boundary is one explicitly non-canonical restaging history directory.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from .storage import data_root, filesystem_context, startup_storage_status

TEMP_SUFFIXES = (".tmp", ".temp", ".part")
DISPOSABLE_HISTORY = Path("blueprint_import/staging_history")
KEEP_STAGING_VERSIONS = 2
RECOVERY_CONFIRMATION = "REMOVE SUPERSEDED STAGING HISTORY"

CANONICAL_REQUIRED = "canonical_required"
LIVE_CANDIDATE = "live_candidate_import"
DERIVED = "derived_regenerable"
DIAGNOSTIC = "diagnostic_operational"
TEMPORARY = "temporary"
SUPERSEDED = "superseded_abandoned"


def _iso(timestamp: float | None) -> str | None:
    return datetime.fromtimestamp(timestamp, UTC).isoformat() if timestamp is not None else None


def _walk(root: Path) -> Iterator[tuple[Path, os.stat_result, bool]]:
    """Yield descendants without following symlinks or reading file contents."""
    if not root.is_dir():
        return
    pending = [root]
    while pending:
        parent = pending.pop()
        try:
            entries = list(os.scandir(parent))
        except OSError:
            continue
        for entry in entries:
            path = Path(entry.path)
            try:
                stat = entry.stat(follow_symlinks=False)
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError:
                continue
            yield path, stat, is_dir
            if is_dir:
                pending.append(path)


def _is_temporary(path: Path) -> bool:
    name = path.name.casefold()
    return (name.startswith(".flora_write_probe") or name.endswith(TEMP_SUFFIXES)
            or (name.startswith(".") and ".tmp" in name))


def _classify(relative: Path, *, is_dir: bool) -> str:
    parts = relative.parts
    if not is_dir and _is_temporary(relative):
        return TEMPORARY
    if parts[:2] == ("blueprint_import", "staging_history"):
        return SUPERSEDED
    if parts[:2] in {
        ("blueprint_import", "staging"), ("blueprint_import", "runs"),
        ("blueprint_import", "reviews"), ("blueprint_import", "mappings"),
        ("blueprint_import", "plans"), ("blueprint_import", "restage_jobs"),
    }:
        return LIVE_CANDIDATE
    if parts[:2] in {
        ("blueprint_import", "packages"), ("blueprint_import", "archives"),
        ("blueprint_import", "audit"), ("blueprint_import", "lifecycle"),
        ("blueprint_import", "promotion"),
    } or parts[:1] in {("memory",), ("live_evidence",), ("commercial_context",)}:
        return CANONICAL_REQUIRED
    if any("diagnostic" in part.casefold() for part in parts) or parts[:2] in {
        ("ai_financial_reports", "runs"), ("blueprint_import", "jobs")
    }:
        return DIAGNOSTIC
    if parts[:1] in {("publications",), ("architecture_exports",), ("rapid_ai_twin_cache",)}:
        return DERIVED
    # Unrecognised storage is required by default. Unknown data is never made
    # eligible merely because its directory name is new to this release.
    return CANONICAL_REQUIRED


def _family(relative: Path) -> str:
    parts = relative.parts
    depth = 3 if parts[:1] == ("blueprint_import",) else 2
    return "/".join(parts[:depth])


def storage_inventory(root: Path | None = None, *, largest_limit: int = 20) -> dict[str, Any]:
    """Return inode-oriented name/metadata counts; never read artefact contents."""
    root = (root or data_root()).resolve(strict=False)
    by_top: Counter[str] = Counter()
    by_family: Counter[str] = Counter()
    by_dir: Counter[str] = Counter()
    by_class: Counter[str] = Counter()
    class_times: dict[str, list[float]] = {}
    files = directories = symlinks = 0
    diagnostic_files = candidate_history_files = temporary_files = 0
    for path, stat, is_dir in _walk(root):
        relative = path.relative_to(root)
        classification = _classify(relative, is_dir=is_dir)
        by_class[classification] += 1
        class_times.setdefault(classification, []).append(stat.st_mtime)
        by_top[relative.parts[0]] += 1
        by_family[_family(relative)] += 1
        if is_dir:
            directories += 1
        else:
            files += 1
            by_dir[str(relative.parent)] += 1
            temporary_files += int(_is_temporary(relative))
            diagnostic_files += int(any("diagnostic" in part.casefold() for part in relative.parts))
            candidate_history_files += int(relative.parts[:2] == ("blueprint_import", "staging_history"))
            if path.is_symlink():
                symlinks += 1
    total = files + directories
    primary, primary_count = by_family.most_common(1)[0] if by_family else ("none", 0)
    timestamps = {
        key: {"oldest": _iso(min(values)), "newest": _iso(max(values))}
        for key, values in sorted(class_times.items()) if values
    }
    return {
        "storage": filesystem_context(root, operation="inode_inventory"),
        "total_filesystem_entries": total, "total_file_count": files,
        "total_directory_count": directories, "total_symlink_count": symlinks,
        "entry_count_by_top_level_area": dict(sorted(by_top.items())),
        # Retain the old field while callers migrate to entry-oriented reporting.
        "file_count_by_top_level_area": dict(sorted(by_top.items())),
        "entry_count_by_record_family": dict(sorted(by_family.items())),
        "file_count_by_record_family": dict(sorted(by_family.items())),
        "entry_count_by_class": dict(sorted(by_class.items())),
        "largest_file_count_directories": [
            {"directory": key, "file_count": value} for key, value in by_dir.most_common(largest_limit)
        ],
        "temporary_file_count": temporary_files,
        "diagnostic_file_count": diagnostic_files,
        "import_staging_entry_count": by_class[LIVE_CANDIDATE],
        "candidate_history_entry_count": by_class[SUPERSEDED],
        "import_candidate_history_file_count": candidate_history_files,
        "canonical_persistent_entry_count": by_class[CANONICAL_REQUIRED],
        "derived_entry_count": by_class[DERIVED],
        "timestamps_by_class": timestamps,
        "oldest_artifact_timestamp": min((v["oldest"] for v in timestamps.values()), default=None),
        "newest_artifact_timestamp": max((v["newest"] for v in timestamps.values()), default=None),
        "primary_inode_consumer": primary, "primary_inode_consumer_entry_count": primary_count,
        "contents_inspected": False,
    }


def _eligible_versions(root: Path, keep_versions: int) -> list[Path]:
    history = (root / DISPOSABLE_HISTORY).resolve(strict=False)
    if history != root / DISPOSABLE_HISTORY or root not in history.parents:
        raise ValueError("Unsafe staging-history cleanup path")
    selected: list[Path] = []
    if history.is_dir():
        for run in (path for path in history.iterdir() if path.is_dir() and not path.is_symlink()):
            versions = sorted(
                (path for path in run.iterdir() if path.is_dir() and not path.is_symlink()),
                key=lambda path: path.stat().st_mtime, reverse=True,
            )
            selected.extend(versions[max(0, keep_versions):])
    return selected


def cleanup_superseded_staging_history(root: Path | None = None, *, keep_versions: int = KEEP_STAGING_VERSIONS,
                                       dry_run: bool = True) -> dict[str, Any]:
    """Remove only superseded snapshots outside the retained rollback window."""
    root = (root or data_root()).resolve(strict=False)
    versions = _eligible_versions(root, keep_versions)
    file_count = directory_count = 0
    for version in versions:
        entries = list(_walk(version))
        file_count += sum(not is_dir for _, _, is_dir in entries)
        # The selected version directory itself also consumes one inode.
        directory_count += 1 + sum(is_dir for _, _, is_dir in entries)
    before = filesystem_context(root, operation="storage_recovery_before")
    if not dry_run:
        for version in versions:
            shutil.rmtree(version)
    after = filesystem_context(root, operation="storage_recovery_after") if not dry_run else before
    return {
        "dry_run": dry_run, "scope": str(DISPOSABLE_HISTORY),
        "eligible_class": SUPERSEDED, "kept_versions_per_import": keep_versions,
        "versions_selected": len(versions), "files_selected": file_count,
        "directories_selected": directory_count,
        "estimated_inodes_recoverable": file_count + directory_count,
        "files_removed": file_count if not dry_run else 0,
        "inodes_before": before.get("available_inodes"),
        "inodes_after": after.get("available_inodes"),
        "canonical_areas_touched": False, "canonical_data_affected": "NO",
    }


def execute_storage_recovery(confirmation: str, root: Path | None = None) -> dict[str, Any]:
    """Execute confirmed cleanup and run the canonical admission/persistence probes."""
    if confirmation != RECOVERY_CONFIRMATION:
        raise ValueError("Explicit storage recovery confirmation did not match")
    result = cleanup_superseded_staging_history(root, dry_run=False)
    health = startup_storage_status()
    facts = health.get("diagnostics", {})
    total = int(facts.get("total_inodes") or 0)
    available = int(facts.get("available_inodes") or 0)
    result.update(
        available_inode_percentage=(available / total * 100) if total else None,
        inode_preflight="PASS" if health.get("ready") else "FAIL",
        write_probe="PASS" if facts.get("write_probe_succeeded") else "FAIL",
        blueprint_package_record_persistence=("PASS" if health.get("ready") else "FAIL"),
        health=health,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Flora persistent storage without reading contents")
    parser.add_argument("--cleanup-superseded-staging", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()
    result: dict[str, Any] = {"inventory": storage_inventory()}
    if args.cleanup_superseded_staging:
        result["cleanup"] = (execute_storage_recovery(args.confirm) if args.apply else
                             cleanup_superseded_staging_history())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
