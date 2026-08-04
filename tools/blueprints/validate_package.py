#!/usr/bin/env python3
"""Run a producer ZIP through Flora's real receipt and inspection path."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator


def validate(path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="flora-blueprint-conformance-") as data_dir:
        previous = os.environ.get("FLORA_DATA_DIR")
        os.environ["FLORA_DATA_DIR"] = data_dir
        try:
            receipt = BlueprintPackageRegistry().receive(path.read_bytes(), path.name, "researcher-conformance")
            result = BlueprintPackageValidator().validate_and_stage(receipt.package_ref, "researcher-conformance")
        finally:
            if previous is None:
                os.environ.pop("FLORA_DATA_DIR", None)
            else:
                os.environ["FLORA_DATA_DIR"] = previous
    if result.errors:
        raise SystemExit("Blueprint package failed Flora inspection: " + "; ".join(result.errors))
    print(f"PASS: {path} received={receipt.package_ref} files_inspected={len(result.files_inspected)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    validate(args.package)


if __name__ == "__main__":
    main()
