#!/usr/bin/env python3
"""Validate and deterministically render derived Researcher commissions.

Canonical Twin semantics remain in IT-001 and the pinned profiles.  This module only
composes governed profile and research-contract references with mission data.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "knowledge-packs/researcher"
MISSION = BASE / "research-missions"
MANDATORY_OUTPUTS = {"governed-records", "evidence-register", "unknown-register", "contradiction-register", "validation-report"}
OPPORTUNITY_MISSIONS = {"commercial-pipeline-qualification", "opportunity-pipeline-enrichment"}
OUTCOMES = {"CONTINUE", "EVIDENCE_EXHAUSTED", "COMPLETE"}
PROHIBITED_OUTCOMES = {"Accepted", "Architecture-ready", "Implementation-ready", "import-ready"}
TELECOM_TERMS = ("VodafoneThree", "Network Services 4", "Project Gigabit", "Openreach", "VMO2", "TalkTalk/PXC", "nexfibre", "Ofcom")

def load(path): return json.loads(Path(path).read_text())
def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def digest(value): return hashlib.sha256(canonical(value).encode()).hexdigest()

def registries():
    templates_doc = load(MISSION / "templates/templates-v1.json")
    contracts_doc = load(MISSION / "contracts/contracts-v1.json")
    return ({x["id"]: x for x in templates_doc["templates"]}, contracts_doc["modules"], load(BASE / "profile-versions.json")["profiles"])

def validate_templates(templates, contracts, profiles):
    if len(templates) != len(set(templates)): raise ValueError("duplicate mission-template ID")
    generic = canonical(list(templates.values()))
    for term in TELECOM_TERMS:
        if term.lower() in generic.lower(): raise ValueError(f"industry-specific value in generic template: {term}")
    for template in templates.values():
        if not re.fullmatch(r"\d+\.\d+\.\d+", template["version"]): raise ValueError("invalid template version")
        for key in ("purpose","profiles","modules","required_manifest_fields","required_outputs","outcome_states","validation","exclusions","compatibility","supersession","migration"):
            if not template.get(key): raise ValueError(f"template missing required property: {key}")
        unknown_profiles=set(template["profiles"])-set(profiles)
        unknown_modules=set(template["modules"])-set(contracts)
        if unknown_profiles: raise ValueError(f"template references missing profile: {sorted(unknown_profiles)[0]}")
        if unknown_modules: raise ValueError(f"template references missing contract module: {sorted(unknown_modules)[0]}")
        if not MANDATORY_OUTPUTS <= set(template["required_outputs"]): raise ValueError("template missing required output")
        if set(template["outcome_states"]) != OUTCOMES: raise ValueError("invalid template outcome states")
    owners={m["canonical_owner"] for m in contracts.values()}
    if len(contracts) != 20 or len(owners) != 20: raise ValueError("duplicate canonical research rule")

def validate_manifest(data, templates=None, profiles=None, contracts=None):
    schema=load(MISSION/"schema/research-mission-manifest-v1.schema.json")
    missing=set(schema["required"])-set(data)
    if missing: raise ValueError(f"manifest missing required fields: {sorted(missing)}")
    templates0, contracts0, profiles0=registries(); templates=templates or templates0; contracts=contracts or contracts0; profiles=profiles or profiles0
    validate_templates(templates, contracts, profiles)
    if data["schema_id"] != "CIOS-Research-Mission-Manifest" or data["schema_version"] != "1.1.0": raise ValueError("unsupported manifest version")
    template=templates.get(data["mission_template_id"])
    if not template or data["mission_type"] != template["id"]: raise ValueError("missing mission template")
    if not data.get("mission_template_version"): raise ValueError("missing mission-template version")
    if data["mission_template_version"] != template["version"]: raise ValueError("incompatible template version")
    if data["pack_version"] != BASE.joinpath("VERSION").read_text().strip(): raise ValueError("incompatible pack version")
    for field in template["required_manifest_fields"]:
        cursor=data
        for part in field.split("."): cursor=cursor.get(part) if isinstance(cursor,dict) else None
        if cursor in (None,"",[]): raise ValueError(f"template requires manifest field: {field}")
    for pid in template["profiles"]:
        if pid not in profiles: raise ValueError(f"template references missing profile: {pid}")
        if data["profile_pins"].get(pid)!=profiles[pid]: raise ValueError(f"incompatible profile and template versions: {pid}")
    if not data.get("baseline_release"): raise ValueError("missing baseline release")
    if not MANDATORY_OUTPUTS <= set(data["outputs"]["required_registers"]+data["outputs"]["required_object_classes"]): raise ValueError("mandatory outputs absent")
    if not set(template["required_outputs"]) <= set(data["outputs"]["required_registers"]+data["outputs"]["required_object_classes"]): raise ValueError("generated brief missing required output")
    if set(data["outcome_states"]) != OUTCOMES or set(data["outcome_states"]) & PROHIBITED_OUTCOMES: raise ValueError("invalid outcome state")
    policy=data["evidence_policy"]
    if data["mission_type"]=="targeted-evidence-closure" and not policy.get("evidence_exhaustion_policy"): raise ValueError("evidence-closure mission without exhaustion policy")
    if "analyst-estimate" in template["modules"] and not data["estimation_policy"].get("retain_underlying_unknown"): raise ValueError("analyst-estimate mission without Unknown retention")
    if data["mission_type"] in OPPORTUNITY_MISSIONS:
        commercial=data.get("commercial_pipeline_configuration",{})
        if set(commercial.get("horizon_boundaries",{}))!={"H1","H2","H3"}: raise ValueError("opportunity mission without Horizon configuration")
        if set(commercial.get("required_confidence_dimensions",[])) != {"customer/problem","programme linkage","buyer","procurement status","timing","value","competition","partner context"}: raise ValueError("opportunity mission missing confidence dimensions")
    return template

def render(data):
    template=validate_manifest(data); _,modules,_=registries()
    receipt={"baseline_release":data["baseline_release"],"contract_modules":{x:modules[x]["version"] for x in template["modules"]},"manifest_version":data["schema_version"],"pack_version":data["pack_version"],"profiles":{x:data["profile_pins"][x] for x in template["profiles"]},"template":f'{template["id"]}@{template["version"]}'}
    lines=[f"# {data['mission_id']} — Researcher Commission","","> Derived work order. Do not edit as a canonical source.","","## Version receipt",f"- Mission ID: {data['mission_id']}",f"- Mission type: {data['mission_type']}",f"- Mission-template version: {template['version']}",f"- Mission-manifest version: {data['schema_version']}",f"- Researcher Knowledge Pack version: {data['pack_version']}","- Twin Object Profile versions: "+"; ".join(f"{p} {data['profile_pins'][p]}" for p in template["profiles"]),f"- Contract-module versions: "+"; ".join(f"{m} {modules[m]['version']}" for m in template["modules"]),f"- Baseline Twin release: {data['baseline_release']}",f"- Generation date: {data['generated_date']}",f"- Version receipt SHA-256: {digest(receipt)}","","## Mission scope",f"- Name: {data['mission_name']}",f"- Parent Twin: {data['parent_twin_id']}",f"- Industry: {data['scope']['industry']}",f"- Geography: {'; '.join(data['scope']['geography'])}",f"- Research period: {data['scope']['research_period']}",f"- Evidence cut-off: {data['scope']['evidence_cut_off']}",f"- Included domains: {'; '.join(data['scope']['included_domains'])}",f"- Excluded domains: {'; '.join(data['scope']['excluded_domains']) or 'None configured'}","","## Research priorities",*[f"- {x}" for x in data["research_priorities"]["priority_outcomes"]]]
    for heading,key in (("Current governed gaps","current_governed_gaps"),("Current Unknowns","current_unknowns"),("Current Contradictions","current_contradictions"),("Monitoring targets","monitoring_targets")):
        lines += ["",f"## {heading}",*[f"- {x}" for x in data["research_priorities"].get(key,[]) or ["None supplied"]]]
    if data.get("commercial_pipeline_configuration"):
        c=data["commercial_pipeline_configuration"]; lines += ["","## Commercial pipeline configuration",f"- Commercial types: {', '.join(c['permitted_commercial_types'])}",f"- Value types (never aggregate as equivalent measures): {', '.join(c['permitted_value_types'])}",f"- Pipeline views: {', '.join(c['pipeline_views'])}",*[f"- {k}: {v}" for k,v in c["horizon_boundaries"].items()],f"- Confidence dimensions: {', '.join(c['required_confidence_dimensions'])}",f"- Aggregation rules: {c['aggregation_rules']}"]
    lines += ["","## Required outputs",*[f"- {x}" for x in data["outputs"]["required_object_classes"]+data["outputs"]["required_registers"]+data["outputs"]["required_reports"]],"","## Composed research contracts"]
    for mid in template["modules"]:
        m=modules[mid]; lines += [f"### {m['title']} ({mid}@{m['version']})",m["instruction"],f"- Validation: {'; '.join(m['validation_rules'])}",f"- Prohibited: {'; '.join(m['prohibited_behaviour'])}"]
    lines += ["","## Pre-delivery validation",*[f"- {x}" for x in template["validation"]],"","## Mission outcomes",*[f"- {x}" for x in data["outcome_states"]],"","## Generation receipt",f"- Manifest SHA-256: {digest(data)}",f"- Generator: tools/knowledge-packs/research_missions.py",f"- Derived output: {data['outputs']['required_package_name']}"]
    output="\n".join(lines)+"\n"
    if re.search(r"\{\{[^}]+\}\}|\$\{[^}]+\}",output): raise ValueError("unresolved template variable")
    return output

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("manifest"); p.add_argument("--output"); p.add_argument("--check",action="store_true"); args=p.parse_args(argv)
    data=load(args.manifest); result=render(data)
    if not args.output: print(result,end=""); return
    out=Path(args.output)
    if args.check:
        if not out.exists() or out.read_text()!=result: raise SystemExit(f"stale generated commission: {out}")
    else: out.parent.mkdir(parents=True,exist_ok=True); out.write_text(result)
if __name__=="__main__": main()
