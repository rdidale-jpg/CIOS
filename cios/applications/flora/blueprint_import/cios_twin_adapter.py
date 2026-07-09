"""Adapter for CIOS Commercial Digital Twin package workbooks.

The adapter treats the original archive as immutable input, verifies workbook hashes
from the package manifest and stages spreadsheet rows as governed import
candidates. It never executes workbook contents and never treats narrative files as
canonical records.
"""
from __future__ import annotations

import json, re, zipfile
from dataclasses import dataclass
from io import BytesIO
from typing import Any
from xml.etree import ElementTree as ET

from .archive import sha256_bytes
from .candidates import CandidateImportRecord, PROJECTION_ONLY_CLASSES, SUPPORTED_RECORD_CLASSES, ValidationFinding, candidate_id
from .ledger import utc_now
from .models import BlueprintPackageRecord

_CANON = {
    "sources": "evidence", "source": "evidence", "evidence": "evidence", "observations": "observation", "observation": "observation",
    "unknowns": "unknown", "unknown": "unknown", "contradictions": "contradiction", "contradiction": "contradiction",
    "human supplied knowledge": "human_knowledge", "human-supplied knowledge": "human_knowledge", "human_knowledge": "human_knowledge",
    "enterprise facts": "enterprise_model_candidate", "enterprise model": "enterprise_model_candidate", "core facts": "enterprise_model_candidate",
}
_PROJ = {
    "pain points": "pain_point", "pain point": "pain_point", "burning platforms": "burning_platform", "burning platform": "burning_platform",
    "transformation pressures": "transformation_pressure_view", "current responses": "current_response", "response effectiveness": "response_effectiveness",
    "residual pains": "residual_pain", "priority selections": "priority_disposition", "solution patterns": "solution_pattern",
    "executive publications": "executive_publication",
}
_TRUTH = {"unknown": "unknown", "contradiction": "contradiction", "human-supplied knowledge": "human-supplied", "human supplied knowledge": "human-supplied"}

@dataclass(frozen=True)
class TwinWorkbookInspection:
    workbook_path: str
    worksheets: tuple[str, ...]
    candidates: tuple[CandidateImportRecord, ...]
    warnings: tuple[str, ...]
    errors: tuple[str, ...]

class CiosCommercialTwinAdapter:
    """Read a final Twin Spine workbook from an accepted package manifest."""

    def inspect(self, package: BlueprintPackageRecord, outer_zip: zipfile.ZipFile, manifest: dict[str, Any]) -> TwinWorkbookInspection | None:
        workbook_path = self._workbook_path(manifest)
        if not workbook_path:
            return None
        warnings: list[str] = [] ; errors: list[str] = []
        if workbook_path not in outer_zip.namelist():
            return TwinWorkbookInspection(workbook_path, (), (), (), (f"Declared final Twin Spine workbook missing: {workbook_path}",))
        expected = self._declared_hash(manifest, workbook_path)
        data = outer_zip.read(workbook_path)
        if expected and sha256_bytes(data) != expected:
            return TwinWorkbookInspection(workbook_path, (), (), (), (f"Workbook hash mismatch: {workbook_path}",))
        candidates, sheets = self._read_workbook(package, workbook_path, data, warnings, errors)
        return TwinWorkbookInspection(workbook_path, tuple(sheets), tuple(candidates), tuple(warnings), tuple(errors))

    def _workbook_path(self, manifest: dict[str, Any]) -> str:
        for f in manifest.get("files", []):
            if not isinstance(f, dict): continue
            role = str(f.get("role") or f.get("kind") or f.get("file_role") or "").casefold()
            path = str(f.get("path") or "")
            if path.endswith((".xlsx", ".xlsm")) and ("final_twin_spine" in role or "twin_spine" in role or f.get("final") is True):
                return path
        return str(manifest.get("final_twin_spine_workbook") or manifest.get("twin_spine_workbook") or "")

    def _declared_hash(self, manifest: dict[str, Any], path: str) -> str:
        for f in manifest.get("files", []):
            if isinstance(f, dict) and f.get("path") == path:
                return str(f.get("sha256") or f.get("hash") or "")
        return ""

    def _read_workbook(self, package, workbook_path: str, data: bytes, warnings: list[str], errors: list[str]):
        out=[]; sheet_names=[]
        try:
            with zipfile.ZipFile(BytesIO(data)) as wb:
                names=set(wb.namelist())
                if any(n.endswith("vbaProject.bin") or n.startswith("xl/externalLinks/") for n in names):
                    warnings.append("Workbook macros, scripts or external links were ignored")
                shared=self._shared(wb)
                sheet_map=self._sheets(wb)
                for sheet_name, sheet_file in sheet_map:
                    sheet_names.append(sheet_name)
                    rows=self._rows(wb, sheet_file, shared)
                    out.extend(self._candidates(package, workbook_path, sheet_name, rows))
        except (zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
            errors.append(f"Workbook could not be inspected safely: {exc}")
        return out, sheet_names

    def _shared(self, wb):
        if "xl/sharedStrings.xml" not in wb.namelist(): return []
        root=ET.fromstring(wb.read("xl/sharedStrings.xml")); ns={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        return ["".join(t.text or "" for t in si.findall(".//x:t", ns)) for si in root.findall("x:si", ns)]

    def _sheets(self, wb):
        ns={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
        book=ET.fromstring(wb.read("xl/workbook.xml")); rels=ET.fromstring(wb.read("xl/_rels/workbook.xml.rels"))
        targets={r.attrib["Id"]: "xl/"+r.attrib["Target"].lstrip("/") for r in rels}
        return [(s.attrib.get("name", "Sheet"), targets.get(s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'), "")) for s in book.findall(".//x:sheet", ns)]

    def _rows(self, wb, sheet_file, shared):
        ns={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}; root=ET.fromstring(wb.read(sheet_file)); rows=[]
        for row in root.findall(".//x:sheetData/x:row", ns):
            vals=[]
            for c in row.findall("x:c", ns):
                v=c.find("x:v", ns); text="" if v is None or v.text is None else v.text
                vals.append(shared[int(text)] if c.attrib.get("t")=="s" and text.isdigit() and int(text)<len(shared) else text)
            rows.append(vals)
        return rows

    def _candidates(self, package, workbook_path, sheet, rows):
        if len(rows)<2: return []
        headers=[str(h).strip().casefold().replace(" ", "_") for h in rows[0]]; out=[]
        klass=_CANON.get(sheet.casefold()) or _PROJ.get(sheet.casefold())
        for idx, vals in enumerate(rows[1:], start=2):
            row={headers[i]: vals[i] if i < len(vals) else "" for i in range(len(headers))}
            rc=str(row.get("record_class") or klass or "unsupported_twin_spine_row")
            truth=str(row.get("truth_class") or _TRUTH.get(sheet.casefold()) or ("analytical_projection" if rc in PROJECTION_ONLY_CLASSES else "asserted"))
            ext=str(row.get("stable_id") or row.get("external_id") or row.get("id") or f"{sheet}-{idx}")
            payload={k:v for k,v in row.items() if v != ""}
            payload.setdefault("twin_version", package.identity.package_version)
            status="accepted" if rc in SUPPORTED_RECORD_CLASSES and rc not in PROJECTION_ONLY_CLASSES else "quarantined"
            findings=[] if rc in SUPPORTED_RECORD_CLASSES else [ValidationFinding("warning","unsupported_twin_spine_row",f"Unsupported Twin Spine row class: {rc}",f"{workbook_path}:{sheet}!{idx}")]
            loc={"workbook": workbook_path, "sheet": sheet, "row": idx, "stable_id": ext}
            out.append(CandidateImportRecord("1.0", candidate_id(package.package_ref, workbook_path, ext, rc), package.package_ref, package.package_sha256, workbook_path, sheet, loc, ext, rc, truth, payload, status, tuple(findings), sha256_bytes(json.dumps(payload, sort_keys=True).encode()), utc_now(), package.import_run_id, 0))
        return out
