#!/usr/bin/env python3
"""Build a Flora Blueprint ZIP for the UK Central Government twin.

This exporter intentionally uses the existing Flora Blueprint package profile
(`blueprint_manifest.json` plus a declared final Twin Spine workbook). It does
not create a Researcher Knowledge Pack and does not define a new package type.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGE_ID = "UKCG-CDT-Blueprint"
DEFAULT_ENTERPRISE_ID = "UK-Central-Government"
DEFAULT_VERSION = "v1.0"
REQUIRED_ASSETS = (
    ("twin_spine/UKCG-CDT-01-Twin-Spine-v1.0.xlsx", "final_twin_spine_workbook", True),
    ("docs/UKCG-CDT-00-Delivery-and-Input-Manifest-v1.0.md", "delivery_input_manifest", True),
    ("docs/UKCG-CDT-02-Governed-Commercial-Digital-Twin-v1.0.md", "governed_twin_publication", True),
    ("docs/UKCG-CDT-04-Research-Completion-and-Validation-Report-v1.0.md", "completion_validation_report", True),
)
OPTIONAL_ASSETS = (
    ("docs/UKCG-CDT-03-Executive-Brief-v1.0.md", "executive_brief", False),
    ("metadata/UKCG-CDT-v1.0-Release-Validation.json", "release_validation", False),
    ("docs/UKCG-CDT-v1.0-RELEASE-README.md", "release_notes", False),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative(path: str) -> str:
    rel = PurePosixPath(path)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise SystemExit(f"Unsafe package path: {path}")
    return rel.as_posix()


def build(input_dir: Path, output_dir: Path, package_version: str = DEFAULT_VERSION) -> Path:
    input_dir = input_dir.resolve()
    files = []
    missing = []
    for rel, role, required in REQUIRED_ASSETS + OPTIONAL_ASSETS:
        rel = safe_relative(rel)
        src = (input_dir / rel).resolve()
        if input_dir not in src.parents and src != input_dir:
            raise SystemExit(f"Asset escapes input directory: {rel}")
        if not src.exists():
            if required:
                missing.append(rel)
            continue
        if not src.is_file():
            raise SystemExit(f"Asset is not a file: {rel}")
        files.append({"path": rel, "role": role, "required": required, "sha256": sha256(src)})
    if missing:
        raise SystemExit("Missing required UK Government Blueprint assets: " + ", ".join(missing))

    twin_spine = REQUIRED_ASSETS[0][0]
    manifest = {
        "package_id": DEFAULT_PACKAGE_ID,
        "package_version": package_version,
        "enterprise_id": DEFAULT_ENTERPRISE_ID,
        "profile_version": "0.1",
        "final_twin_spine_workbook": twin_spine,
        "files": files,
        "record_sets": [],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"UKCG-CDT-Flora-Blueprint-{package_version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("blueprint_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        for entry in files:
            zf.write(input_dir / entry["path"], entry["path"])
    return zip_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build a Flora-importable UK Central Government Blueprint ZIP using the existing Blueprint profile.")
    parser.add_argument("--input-dir", default="dist/uk-government-blueprint-assets", help="Directory containing the completed UK Government Blueprint assets.")
    parser.add_argument("--output-dir", default="dist", help="Directory for the generated ZIP.")
    parser.add_argument("--package-version", default=DEFAULT_VERSION)
    args = parser.parse_args(argv)
    zip_path = build(Path(args.input_dir), Path(args.output_dir), args.package_version)
    print(f"Built {zip_path.relative_to(ROOT) if zip_path.is_relative_to(ROOT) else zip_path} sha256={sha256(zip_path)}")


if __name__ == "__main__":
    main()
