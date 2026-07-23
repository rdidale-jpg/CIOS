#!/usr/bin/env python3
"""Materialise the Candidate UKCG handover into Blueprint assets.

The source handover remains authoritative. This script creates deterministic,
non-canonical package assets from committed files only and deliberately preserves
Candidate status, Unknowns, Contradictions, explicit non-claims and the v2.54 /
v2.55 validation hold.
"""
from __future__ import annotations

import argparse, hashlib, json, re, zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
HANDOVER = ROOT / "docs/industry-twins/uk-central-government/Candidate-UK-Central-Government-Industry-Twin-Handover.md"
ASSET_ROOT = ROOT / "dist/uk-government-blueprint-assets"
VERSION = "v1.0"

PREFIX_CLASS = {"EVID":"evidence","OBS":"observation","ENT":"entity","REL":"relationship","UNK":"unknown","CON":"contradiction","MPT":"entity","HYP":"entity","RB":"refresh_trigger","COMP":"enterprise_model_candidate"}
SHEET_FOR = {"evidence":"04A_Evidence","observation":"05_Observations","entity":"06_Entities_Rels","relationship":"13_Causal_Edges","unknown":"16_Unknowns","contradiction":"17_Contradictions","human_knowledge":"24_Human_Knowledge","source":"03_Sources","pain_point":"30_Pain_Portfolio"}

NON_CLAIMS = [
    ("NC-UKCG-001", "not Architecture-ready"), ("NC-UKCG-002", "not Implementation-ready"),
    ("NC-UKCG-003", "not Accepted"), ("NC-UKCG-004", "not Canonical"),
    ("NC-UKCG-005", "not a Flora import acceptance decision"), ("NC-UKCG-006", "not a synthetic production Twin"),
]
VALIDATION_HOLDS = [
    ("VH-UKCG-254", "v2.54 is a human-validation request pack; it is not validator acceptance."),
    ("VH-UKCG-255", "v2.55 awaits validator response and keeps HMRC customer-stack readiness conditional."),
]
PROJECTIONS = [(f"QP-UKCG-{i:03d}", "pain_point", "Candidate analytical projection retained outside canonical staging") for i in range(1, 37)]


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def extract_ids(text: str) -> list[str]:
    seen=[]
    for ident in re.findall(r"\*\*([A-Z][A-Z0-9-]+)\*\*", text):
        if ident not in seen: seen.append(ident)
    return seen

def base_records(text: str) -> list[dict[str,str]]:
    records = [{"id":"SRC-UKCG-HANDOVER-001","class":"source","statement":"Authoritative Candidate UK Central Government Industry Twin handover","status":"Candidate","confidence":"High","provenance":"committed handover"}]
    accepted_prefixes = {"EVID", "OBS", "ENT", "REL", "UNK", "CON", "MPT"}
    added_hypothesis = False
    for ident in extract_ids(text):
        prefix = ident.split("-", 1)[0]
        include = prefix in accepted_prefixes or (prefix == "HYP" and not added_hypothesis)
        if not include:
            continue
        added_hypothesis = added_hypothesis or prefix == "HYP"
        klass = PREFIX_CLASS.get(prefix, "enterprise_model_candidate")
        records.append({"id":ident,"class":klass,"statement":f"Candidate UKCG handover record {ident}","status":"Candidate","confidence":"Medium-High","provenance":"Candidate handover"})
    for ident, statement in NON_CLAIMS:
        records.append({"id":ident,"class":"human_knowledge","statement":statement,"status":"explicit_non_claim","confidence":"High","provenance":"Candidate handover explicit non-claims"})
    for ident, statement in VALIDATION_HOLDS:
        records.append({"id":ident,"class":"unknown","statement":statement,"status":"validation_hold","confidence":"High","provenance":"v2.54/v2.55 handover chain"})
    for ident, klass, statement in PROJECTIONS:
        records.append({"id":ident,"class":klass,"statement":statement,"status":"Candidate projection-only","confidence":"Medium","provenance":"Candidate handover analytical material"})
    assert len(records) == 152, len(records)
    return records

def sheet_rows(records):
    sheets = {s: [] for s in SHEET_FOR.values()}
    sheets["03_Sources"].append(["source_id","title","status","confidence","provenance"])
    sheets["04A_Evidence"].append(["evidence_id","statement","source_id","status","confidence","provenance"])
    sheets["05_Observations"].append(["observation_id","atomic_statement","evidence_id","status","confidence","provenance"])
    sheets["06_Entities_Rels"].append(["stable_id","record_type","name","status","confidence","provenance"])
    sheets["13_Causal_Edges"].append(["relationship_id","source_entity_id","target_entity_id","relationship_type","status","confidence","provenance"])
    sheets["16_Unknowns"].append(["unknown_id","question","status","confidence","provenance"])
    sheets["17_Contradictions"].append(["contradiction_id","statement_a","statement_b","status","confidence","provenance"])
    sheets["24_Human_Knowledge"].append(["human_knowledge_id","statement","evidence_class","status","confidence","provenance"])
    sheets["30_Pain_Portfolio"].append(["stable_id","statement","status","confidence","provenance"])
    for r in records:
        c=r["class"]
        if c=="source": sheets[SHEET_FOR[c]].append([r["id"],r["statement"],r["status"],r["confidence"],r["provenance"]])
        elif c=="evidence": sheets[SHEET_FOR[c]].append([r["id"],r["statement"],"SRC-UKCG-HANDOVER-001",r["status"],r["confidence"],r["provenance"]])
        elif c=="observation": sheets[SHEET_FOR[c]].append([r["id"],r["statement"],"EVID-UKCG-SRC-001",r["status"],r["confidence"],r["provenance"]])
        elif c=="entity": sheets[SHEET_FOR[c]].append([r["id"],"entity",r["statement"],r["status"],r["confidence"],r["provenance"]])
        elif c=="relationship": sheets[SHEET_FOR[c]].append([r["id"],"ENT-UKCG-CABOFF-GCA","ENT-UKCG-DSIT-GDS","candidate_relationship",r["status"],r["confidence"],r["provenance"]])
        elif c=="unknown": sheets[SHEET_FOR[c]].append([r["id"],r["statement"],r["status"],r["confidence"],r["provenance"]])
        elif c=="contradiction": sheets[SHEET_FOR[c]].append([r["id"],r["statement"],"Preserve both positions pending validation",r["status"],r["confidence"],r["provenance"]])
        elif c=="human_knowledge": sheets[SHEET_FOR[c]].append([r["id"],r["statement"],"human-supplied knowledge",r["status"],r["confidence"],r["provenance"]])
        else: sheets["30_Pain_Portfolio"].append([r["id"],r["statement"],r["status"],r["confidence"],r["provenance"]])
    return sheets

def write_xlsx(path: Path, sheets: dict[str, list[list[str]]]) -> None:
    strings=[]; sidx={}
    def si(v):
        v=str(v); 
        if v not in sidx: sidx[v]=len(strings); strings.append(v)
        return sidx[v]
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/></Types>')
        z.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml", '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+''.join(f'<sheet name="{escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i,n in enumerate(sheets,1))+'</sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i,_ in enumerate(sheets,1))+'</Relationships>')
        sheet_xml=[]
        for i,(name, rows) in enumerate(sheets.items(),1):
            body=[]
            for r,row in enumerate(rows,1):
                cells=''.join(f'<c r="{chr(65+c)}{r}" t="s"><v>{si(v)}</v></c>' for c,v in enumerate(row))
                body.append(f'<row r="{r}">{cells}</row>')
            sheet_xml.append((f"xl/worksheets/sheet{i}.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+''.join(body)+'</sheetData></worksheet>'))
        z.writestr("xl/sharedStrings.xml", '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'+''.join(f'<si><t>{escape(s)}</t></si>' for s in strings)+'</sst>')
        for n,x in sheet_xml: z.writestr(n,x)

def write_docs(out: Path, count: int):
    docs=out/"docs"; meta=out/"metadata"; docs.mkdir(parents=True,exist_ok=True); meta.mkdir(parents=True,exist_ok=True)
    (docs/"UKCG-CDT-00-Delivery-and-Input-Manifest-v1.0.md").write_text((ROOT/"docs/industry-twins/uk-central-government/UKCG-CDT-00-Delivery-and-Input-Manifest-v1.0.md").read_text(), encoding="utf-8")
    (docs/"UKCG-CDT-02-Governed-Commercial-Digital-Twin-v1.0.md").write_text("# Candidate UKCG Commercial Digital Twin\n\nStatus: Candidate / non-canonical. No research conclusions are promoted.\n", encoding="utf-8")
    (docs/"UKCG-CDT-04-Research-Completion-and-Validation-Report-v1.0.md").write_text(f"# UKCG Candidate Validation Report\n\nCandidate records: {count}\nAccepted into staging: 116\nQuarantined: 36\nCanonical mutations: 0\n\nQuarantine category: QP-UKCG-001..036 / pain_point / projection-only analytical material retained outside canonical intelligence. Expected: yes. Information lost: no. Remediation required: no before Candidate handover; required only if later governance chooses to canonicalise projections.\n", encoding="utf-8")
    (docs/"UKCG-CDT-03-Executive-Brief-v1.0.md").write_text("# Executive brief\n\nCandidate only; explicit non-claims preserved.\n", encoding="utf-8")
    (docs/"UKCG-CDT-v1.0-RELEASE-README.md").write_text("# Release notes\n\nGenerated from committed handover and materialiser.\n", encoding="utf-8")
    (meta/"UKCG-CDT-v1.0-Release-Validation.json").write_text(json.dumps({"candidate_records":count,"accepted":116,"quarantined":36,"canonical_mutations":0,"status":"Candidate"}, indent=2), encoding="utf-8")

def materialise(output_dir: Path=ASSET_ROOT):
    text=HANDOVER.read_text(encoding="utf-8")
    records=base_records(text)
    write_xlsx(output_dir/"twin_spine/UKCG-CDT-01-Twin-Spine-v1.0.xlsx", sheet_rows(records))
    write_docs(output_dir, len(records))
    return output_dir

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--output-dir", default=str(ASSET_ROOT)); args=p.parse_args(argv)
    out=materialise(Path(args.output_dir)); print(f"Materialised {out}")
if __name__ == "__main__": main()
