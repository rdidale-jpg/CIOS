"""Read-only inventory and narrowly bounded disposable-state maintenance."""
from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .storage import data_root, filesystem_context

TEMP_SUFFIXES = (".tmp", ".temp", ".part")
DISPOSABLE_HISTORY = Path("blueprint_import/staging_history")


def _iso(timestamp: float | None) -> str | None:
    return datetime.fromtimestamp(timestamp, UTC).isoformat() if timestamp is not None else None


def storage_inventory(root: Path | None = None, *, largest_limit: int = 20) -> dict[str, Any]:
    """Count names and timestamps only; never read persisted file contents."""
    root = (root or data_root()).resolve(strict=False)
    by_top: Counter[str] = Counter(); by_family: Counter[str] = Counter(); by_dir: Counter[str] = Counter()
    temporary = diagnostic = candidate_history = 0
    oldest: float | None = None; newest: float | None = None
    for path in root.rglob("*") if root.exists() else ():
        if not path.is_file():
            continue
        relative = path.relative_to(root); parts = relative.parts
        by_top[parts[0]] += 1
        family = "/".join(parts[:3] if parts[:1] == ("blueprint_import",) else parts[:2])
        by_family[family] += 1; by_dir[str(relative.parent)] += 1
        name = path.name.casefold()
        if name.startswith(".flora_write_probe") or name.endswith(TEMP_SUFFIXES) or (name.startswith(".") and ".tmp" in name): temporary += 1
        if any(part.casefold().startswith("diagnostic") for part in parts): diagnostic += 1
        if parts[:2] == ("blueprint_import", "staging_history"): candidate_history += 1
        try: modified = path.stat().st_mtime
        except OSError: continue
        oldest = modified if oldest is None else min(oldest, modified)
        newest = modified if newest is None else max(newest, modified)
    return {
        "storage": filesystem_context(root, operation="file_count_inventory"),
        "total_file_count": sum(by_top.values()), "file_count_by_top_level_area": dict(sorted(by_top.items())),
        "file_count_by_record_family": dict(sorted(by_family.items())),
        "largest_file_count_directories": [{"directory": k, "file_count": v} for k, v in by_dir.most_common(largest_limit)],
        "temporary_file_count": temporary, "diagnostic_file_count": diagnostic,
        "import_candidate_history_file_count": candidate_history,
        "oldest_artifact_timestamp": _iso(oldest), "newest_artifact_timestamp": _iso(newest),
        "contents_inspected": False,
    }


def cleanup_superseded_staging_history(root: Path | None = None, *, keep_versions: int = 2, dry_run: bool = True) -> dict[str, Any]:
    """Remove only old, non-canonical restage snapshots; active staging is unreachable."""
    root = (root or data_root()).resolve(strict=False)
    history = (root / DISPOSABLE_HISTORY).resolve(strict=False)
    if history != root / DISPOSABLE_HISTORY or root not in history.parents:
        raise ValueError("Unsafe staging-history cleanup path")
    removed_versions = removed_files = 0
    if history.exists():
        for run in (p for p in history.iterdir() if p.is_dir()):
            versions = sorted((p for p in run.iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
            for version in versions[max(0, keep_versions):]:
                count = sum(1 for p in version.rglob("*") if p.is_file())
                if not dry_run: shutil.rmtree(version)
                removed_versions += 1; removed_files += count
    return {"dry_run": dry_run, "scope": str(DISPOSABLE_HISTORY), "kept_versions_per_import": keep_versions,
            "versions_selected": removed_versions, "files_selected": removed_files,
            "canonical_areas_touched": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Flora persistent storage without reading confidential contents")
    parser.add_argument("--cleanup-superseded-staging", action="store_true")
    parser.add_argument("--apply", action="store_true", help="apply the narrowly scoped cleanup (default is dry-run)")
    parser.add_argument("--keep-versions", type=int, default=2)
    args = parser.parse_args()
    result: dict[str, Any] = {"inventory": storage_inventory()}
    if args.cleanup_superseded_staging:
        result["cleanup"] = cleanup_superseded_staging_history(keep_versions=max(0, args.keep_versions), dry_run=not args.apply)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
