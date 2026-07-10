"""Adapter for CIOS Commercial Digital Twin package workbooks.

The adapter treats the original archive as immutable input, verifies workbook hashes
from the package manifest and stages spreadsheet rows as governed import
candidates. It never executes workbook contents and never treats narrative files as
canonical records.
"""
from __future__ import annotations

import json, re, zipfile
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit
from dataclasses import dataclass
from io import BytesIO
from typing import Any
from xml.etree import ElementTree as ET

from .archive import sha256_bytes
from .candidates import CandidateImportRecord, PROJECTION_ONLY_CLASSES, SUPPORTED_RECORD_CLASSES, ValidationFinding, candidate_id
from .ledger import utc_now

RESOLVER_FUNCTION_NAME = "cios.applications.flora.blueprint_import.cios_twin_adapter.resolve_ooxml_relationship_target"
ADAPTER_IMPLEMENTATION_ID = "cios-commercial-twin-adapter-v1"

def _target_classification(target: str, mode: str = "") -> str:
    if str(mode or "").casefold() == "external":
        return "external"
    target = str(target or "")
    if target.startswith("/"):
        return "package-rooted"
    if target == "xl" or target.startswith("xl/"):
        return "already prefixed"
    return "relative"

def _nearest_members(requested: str, names: set[str], limit: int = 5) -> list[str]:
    leaf = PurePosixPath(requested).name
    scored = []
    for name in names:
        if name.endswith("/"):
            continue
        score = 0
        if PurePosixPath(name).name == leaf:
            score += 100
        if name.endswith(leaf):
            score += 20
        if "worksheets/" in name and "worksheets/" in requested:
            score += 10
        if score:
            scored.append((-score, len(name), name))
    return [name for _, __, name in sorted(scored)[:limit]]

def _event(trace: list[dict[str, Any]] | None, step_id: int, component: str, action: str, safe_input: str, safe_output: str, status: str, correlation_id: str, failure_reason: str = "", **details: Any) -> None:
    if trace is None:
        return
    payload = {
        "timestamp": utc_now(),
        "step_id": step_id,
        "component": component,
        "action": action,
        "safe_input_summary": safe_input,
        "safe_output_summary": safe_output,
        "status": status,
        "failure_reason": failure_reason,
        "correlation_id": correlation_id,
    }
    payload.update({k: v for k, v in details.items() if v not in (None, "")})
    trace.append(payload)
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

def resolve_ooxml_relationship_target(source_part: str, target: str) -> str:
    """Resolve an OOXML relationship target to a safe package ZIP member path.

    Relationship targets are part-relative unless they are rooted with a
    leading slash.  Some producer workbooks incorrectly emit package-rooted
    paths without that slash (for example ``xl/worksheets/sheet1.xml``); those
    are preserved rather than being joined to ``xl/`` again.
    """

    original = target
    target = unquote(str(target or ""))
    if "\\" in target:
        raise ValueError(f"Malformed relationship target: {original}")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        raise ValueError(f"Malformed relationship target: {original}")
    target = parsed.path
    if not target or target.startswith("//"):
        raise ValueError(f"Malformed relationship target: {original}")
    if target.startswith("/"):
        candidate = PurePosixPath(target.lstrip("/"))
    else:
        source_dir = PurePosixPath(source_part).parent
        candidate = PurePosixPath(target) if target == "xl" or target.startswith("xl/") else source_dir / target
    parts: list[str] = []
    for part in candidate.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise ValueError(f"Relationship target escapes package: {original}")
            parts.pop()
            continue
        parts.append(part)
    if not parts or parts[0] == "..":
        raise ValueError(f"Malformed relationship target: {original}")
    return "/".join(parts)


class CiosCommercialTwinAdapter:
    """Read a final Twin Spine workbook from an accepted package manifest."""

    def inspect(self, package: BlueprintPackageRecord, outer_zip: zipfile.ZipFile, manifest: dict[str, Any], trace: list[dict[str, Any]] | None = None) -> TwinWorkbookInspection | None:
        correlation_id = package.import_run_id
        _event(trace, 1, __name__, "Read Blueprint manifest", "blueprint_manifest.json", f"Package {package.identity.package_id} {package.identity.package_version} identified", "Passed", correlation_id, package_id=package.identity.package_id, package_version=package.identity.package_version, enterprise_id=package.identity.enterprise_id, package_checksum=package.package_sha256)
        workbook_path = self._workbook_path(manifest)
        if not workbook_path:
            return None
        warnings: list[str] = [] ; errors: list[str] = []
        _event(trace, 2, __name__, "Select final Twin workbook", workbook_path, "Workbook found" if workbook_path in outer_zip.namelist() else "Workbook missing", "Passed" if workbook_path in outer_zip.namelist() else "Failed", correlation_id, workbook_path_selected=workbook_path)
        if workbook_path not in outer_zip.namelist():
            return TwinWorkbookInspection(workbook_path, (), (), (), (f"Declared final Twin Spine workbook missing: {workbook_path}",))
        expected = self._declared_hash(manifest, workbook_path)
        data = outer_zip.read(workbook_path)
        _event(trace, 3, __name__, "Hash selected workbook", workbook_path, sha256_bytes(data), "Passed", correlation_id, workbook_sha256=sha256_bytes(data))
        if expected and sha256_bytes(data) != expected:
            return TwinWorkbookInspection(workbook_path, (), (), (), (f"Workbook hash mismatch: {workbook_path}",))
        candidates, sheets = self._read_workbook(package, workbook_path, data, warnings, errors, trace, correlation_id)
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

    def _read_workbook(self, package, workbook_path: str, data: bytes, warnings: list[str], errors: list[str], trace: list[dict[str, Any]] | None = None, correlation_id: str = ""):
        out=[]; sheet_names=[]
        try:
            with zipfile.ZipFile(BytesIO(data)) as wb:
                names=set(wb.namelist())
                if any(n.endswith("vbaProject.bin") or n.startswith("xl/externalLinks/") for n in names):
                    warnings.append("Workbook macros, scripts or external links were ignored")
                shared=self._shared(wb)
                sheet_map=self._sheets(wb, trace, correlation_id)
                for sheet_name, sheet_file in sheet_map:
                    sheet_names.append(sheet_name)
                    rows=self._rows(wb, sheet_file, shared)
                    out.extend(self._candidates(package, workbook_path, sheet_name, rows))
        except (zipfile.BadZipFile, ET.ParseError, KeyError, ValueError) as exc:
            errors.append(f"Workbook could not be inspected safely: {exc}")
        _event(trace, 7, __name__, "Candidate staging", str(len(out)), "Candidates staged" if not errors else "Stopped because workbook inspection failed", "Passed" if not errors else "Not started", correlation_id, current_stage="candidate_staging" if not errors else "validation_stop", previous_completed_stage="worksheet_parsing" if not errors else "workbook_relationship_parsing", next_intended_stage="proposed_change_review", processing_stopped=bool(errors), stop_reason="; ".join(errors), canonical_changes_made=False, promotion_enabled=not bool(errors))
        return out, sheet_names

    def _shared(self, wb):
        if "xl/sharedStrings.xml" not in wb.namelist(): return []
        root=ET.fromstring(wb.read("xl/sharedStrings.xml")); ns={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        return ["".join(t.text or "" for t in si.findall(".//x:t", ns)) for si in root.findall("x:si", ns)]

    def _sheets(self, wb, trace: list[dict[str, Any]] | None = None, correlation_id: str = ""):
        ns={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
        book=ET.fromstring(wb.read("xl/workbook.xml")); rels=ET.fromstring(wb.read("xl/_rels/workbook.xml.rels"))
        names=set(wb.namelist()); targets={}; seen_relationship_ids=set()
        _event(trace, 4, __name__, "Read workbook sheet list", "xl/workbook.xml", "Workbook relationships loaded", "Passed", correlation_id, source_ooxml_part="xl/workbook.xml", relationship_file="xl/_rels/workbook.xml.rels", workbook_adapter_module=__name__, workbook_adapter_implementation_identifier=ADAPTER_IMPLEMENTATION_ID)
        for rel in rels:
            rid=str(rel.attrib.get("Id") or "")
            target=str(rel.attrib.get("Target") or "")
            if not rid: continue
            if rid in seen_relationship_ids: raise ValueError(f"Duplicate workbook relationship ID: {rid}")
            seen_relationship_ids.add(rid)
            if str(rel.attrib.get("TargetMode") or "").casefold() == "external":
                continue
            resolved=self._resolve_part_target("xl/workbook.xml", target)
            exists = resolved in names
            _event(trace, 5, __name__, "Read and normalize worksheet relationship", rid, f"Target: {target}; resolved: {resolved}; exists: {'yes' if exists else 'no'}", "Passed" if exists else "Failed", correlation_id, failure_reason="ZIP member not found" if not exists else "", resolver_function_name=RESOLVER_FUNCTION_NAME, source_ooxml_part="xl/workbook.xml", relationship_file="xl/_rels/workbook.xml.rels", relationship_id=rid, original_relationship_target=target, target_classification=_target_classification(target, rel.attrib.get("TargetMode", "")), normalized_target=resolved, final_zip_lookup_path=resolved, zip_member_exists=exists, nearest_matching_zip_members=_nearest_members(resolved, names))
            targets[rid]=resolved
        sheets=[]; missing=[]
        for sheet in book.findall(".//x:sheet", ns):
            sheet_name=sheet.attrib.get("name", "Sheet")
            rid=sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', "")
            resolved=targets.get(rid, "")
            if not resolved:
                _event(trace, 6, __name__, "Resolve worksheet for parsing", sheet_name, "Relationship missing", "Failed", correlation_id, sheet_name=sheet_name, relationship_id=rid, current_stage="workbook_processing", previous_completed_stage="workbook_relationship_parsing", next_intended_stage="candidate_staging", processing_stopped=True, stop_reason="worksheet relationship missing", canonical_changes_made=False, promotion_enabled=False)
                missing.append(f"Worksheet relationship could not be resolved: sheet={sheet_name}; relationship_id={rid}; target=; resolved=; missing=")
                continue
            if resolved not in names:
                _event(trace, 6, __name__, "Check workbook archive", resolved, "File not found; processing stopped before candidate staging", "Failed", correlation_id, sheet_name=sheet_name, relationship_id=rid, final_zip_lookup_path=resolved, zip_member_exists=False, nearest_matching_zip_members=_nearest_members(resolved, names), current_stage="workbook_processing", previous_completed_stage="workbook_relationship_parsing", next_intended_stage="candidate_staging", processing_stopped=True, stop_reason="workbook inspection failed", canonical_changes_made=False, promotion_enabled=False)
                missing.append(f"Worksheet relationship could not be resolved: sheet={sheet_name}; relationship_id={rid}; target={self._relationship_target(rels, rid)}; resolved={resolved}; missing={resolved}")
                continue
            _event(trace, 6, __name__, "Check workbook archive", resolved, "File found; worksheet ready for parsing", "Passed", correlation_id, sheet_name=sheet_name, relationship_id=rid, final_zip_lookup_path=resolved, zip_member_exists=True)
            sheets.append((sheet_name, resolved))
        if missing: raise ValueError("; ".join(missing))
        return sheets

    def _relationship_target(self, rels, rid: str) -> str:
        for rel in rels:
            if rel.attrib.get("Id") == rid: return str(rel.attrib.get("Target") or "")
        return ""

    def _resolve_part_target(self, source_part: str, target: str) -> str:
        return resolve_ooxml_relationship_target(source_part, target)

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
