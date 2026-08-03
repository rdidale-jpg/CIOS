#!/usr/bin/env python3
"""Validate and deterministically render Research Missions from existing owners."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "knowledge-packs/researcher"
MISSION = BASE / "research-missions"
MANDATORY_OUTPUTS = {"governed-records", "evidence-register", "unknown-register", "contradiction-register", "validation-report"}

def load(path): return json.loads(Path(path).read_text())

def validate_manifest(data, templates=None, profiles=None):
    schema = load(MISSION / "schema/research-mission-manifest-v1.schema.json")
    missing = set(schema["required"]) - set(data)
    if missing: raise ValueError(f"manifest missing required fields: {sorted(missing)}")
    if set(data) - set(schema["properties"]): raise ValueError("manifest contains unknown fields")
    if data["manifest_version"] != "1.0.0": raise ValueError("unsupported manifest version")
    templates = templates or {x["id"]: x for x in load(MISSION / "templates/templates-v1.json")["templates"]}
    profiles = profiles or load(BASE / "profile-versions.json")["profiles"]
    template = templates.get(data["mission_type"])
    if not template: raise ValueError("missing mission template")
    for pid in template["profiles"]:
        if pid not in profiles: raise ValueError(f"template references missing profile: {pid}")
        if data["profile_versions"].get(pid) != profiles[pid]: raise ValueError(f"required profile version absent or stale: {pid}")
    if not MANDATORY_OUTPUTS <= set(data["required_outputs"]): raise ValueError("generated brief would omit mandatory outputs")
    if data["mission_type"] == "opportunity-pipeline-enrichment" and not data.get("horizon_definitions"):
        raise ValueError("opportunity mission omits Horizon rules")
    if data["mission_type"] == "targeted-evidence-closure":
        if "analyst-estimates" not in template["modules"] or "evidence-closure" not in template["modules"] or "EVIDENCE EXHAUSTED" not in data["outcome_states"]:
            raise ValueError("evidence-closure mission omits estimate and exhaustion rules")
    return template

def render(data):
    template = validate_manifest(data)
    contracts = load(MISSION / "contracts/contracts-v1.json")
    lines = [f"# {data['mission_id']} — Researcher Commission", "",
      "## Version provenance", f"- Researcher Knowledge Pack version: {data['pack_version']}",
      f"- Mission-template version: {template['version']}", f"- Mission-manifest version: {data['manifest_version']}",
      "- Twin Object Profile versions: " + "; ".join(f"{p} {data['profile_versions'][p]}" for p in template['profiles']),
      f"- Baseline Twin release: {data['baseline_release']}", f"- Generation timestamp: {data['generated_date']}", "",
      "## Commission", f"- Parent Twin: {data['parent_twin_id']}", f"- Mission type: {data['mission_type']}",
      f"- Industry: {data['industry']}", f"- Geography: {'; '.join(data['geography'])}",
      "- Scope: `" + json.dumps(data['scope'], sort_keys=True, separators=(',', ':')) + "`", "",
      "## Research priorities", *[f"- {x}" for x in data['research_priorities']]]
    if data.get("current_gaps"): lines += ["", "## Current gaps supplied by Flora", *[f"- {x}" for x in data["current_gaps"]]]
    if data.get("subject_ids"): lines += ["", "## Subject register supplied by Flora", *[f"- {x}" for x in data["subject_ids"]]]
    if data.get("horizon_definitions"): lines += ["", "## Manifest horizon definitions", *[f"- {k}: {v}" for k,v in data["horizon_definitions"].items()]]
    lines += ["", "## Required outputs", *[f"- {x}" for x in data['required_outputs']], "", "## Composed research contract"]
    for mid in template["modules"]: lines += [f"### {mid}", contracts["modules"][mid]]
    lines += ["", "## Mission controls", f"- Evidence-closure policy: {data['evidence_closure_policy']}",
      f"- Permitted estimate types: {', '.join(data['permitted_estimate_types'])}", f"- Outcome states: {', '.join(data['outcome_states'])}"]
    output = "\n".join(lines) + "\n"
    if re.search(r"\{\{[^}]+\}\}|\$\{[^}]+\}", output): raise ValueError("template contains unresolved variables")
    return output

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("manifest"); p.add_argument("--output"); p.add_argument("--check", action="store_true")
    args=p.parse_args(argv); data=load(args.manifest); result=render(data)
    if args.output:
        out=Path(args.output)
        if args.check:
            if not out.exists() or out.read_text()!=result: raise SystemExit(f"generated file differs: {out}")
        else: out.parent.mkdir(parents=True,exist_ok=True); out.write_text(result)
    else: print(result,end="")
if __name__ == "__main__": main()
