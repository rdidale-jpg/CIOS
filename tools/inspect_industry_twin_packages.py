"""Inspect local governed Industry Twin acceptance packages without promoting."""
from __future__ import annotations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))
from cios.applications.flora.blueprint_import.archive import inspect_zip_inventory
from cios.applications.flora.blueprint_import.package_contracts import PackageContractDetector

ROOT = Path(__file__).parents[1] / "tests/fixtures/industry_twin_packages"
NAMES = ("UKEU-001-final.zip", "TMS-001-final.zip", "DIST-001-final.zip")

def main() -> int:
    evidence = {}
    missing = []
    for name in NAMES:
        path = ROOT / name
        if not path.exists():
            missing.append(name)
            continue
        content = path.read_bytes()
        evidence[name] = PackageContractDetector().detect(content, inspect_zip_inventory(content)).to_dict()
    print(json.dumps({"inspections": evidence, "missing": missing}, indent=2, sort_keys=True))
    return 2 if missing else 0

if __name__ == "__main__":
    raise SystemExit(main())
