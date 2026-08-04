#!/usr/bin/env python3
"""Explicitly refresh the governed schema after canonical contract review."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cios.contracts.flora_blueprint import BlueprintManifest

TARGET = ROOT / "knowledge-packs/researcher/package-contracts/flora-blueprint-import/blueprint_manifest.schema.json"
TARGET.write_text(json.dumps(BlueprintManifest.model_json_schema(), indent=2, sort_keys=True) + "\n")
print(TARGET.relative_to(ROOT))
