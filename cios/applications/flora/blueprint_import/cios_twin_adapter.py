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

MAPPING_VERSION = "mod-cdt-twin-spine-mapping-v1.3.3"


def _norm(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"^[0-9]+[a-z]?[_\-.\s]+", "", text)
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text


ID_COLUMNS = ("stable_id","external_id","id","source_id","evidence_id","observation_id","unknown_id","contradiction_id","entity_id","relationship_id","edge_id","human_knowledge_id","claim_id")
TEXT_COLUMNS = ("statement","atomic_statement","claim","question","name","label","title","summary","description","statement_a","statement_b","source","target")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _split_refs(value: Any) -> list[str]:
    text = _clean(value)
    if not text:
        return []
    return [_clean(part) for part in re.split(r"[,;|\t]\s*|\n+", text) if _clean(part)]


def _ref_key(value: Any) -> str:
    text = _clean(value).casefold()
    text = re.sub(r"^(source|src|evidence|ev)\s*[:#-]\s*", "", text)
    return re.sub(r"[^a-z0-9]+", "", text)


def _derive_identifier(enterprise_id: str, record_class: str, sheet: str, row: dict[str, Any], row_number: int, *, allow_row_fallback: bool = False) -> tuple[str, str]:
    natural = []
    for key in TEXT_COLUMNS + ("record_type", "type", "scope", "owner", "source_id", "evidence_id"):
        value = _clean(row.get(key))
        if value:
            natural.append(f"{key}={value}")
    if not natural:
        return "", ""
    basis = f"enterprise={enterprise_id}|class={record_class}|sheet={sheet}|" + "|".join(natural[:8])
    if allow_row_fallback:
        basis += f"|row={row_number}"
    digest = sha256_bytes(basis.casefold().encode("utf-8"))[:16]
    ent = _norm(enterprise_id) or "enterprise"
    return f"{ent}-{_norm(record_class) or 'record'}-{digest}", basis


def _is_formula_only(row_obj: dict[str, Any], vals: list[str]) -> bool:
    non_empty = [v for v in vals if _clean(v)]
    return bool(row_obj.get("formula_cells")) and len(non_empty) <= int(row_obj.get("formula_cells") or 0)

@dataclass(frozen=True)
class SheetMapping:
    aliases: tuple[str, ...]
    candidate_class: str
    disposition: str = "canonical_candidate"
    required_any: tuple[tuple[str, ...], ...] = (("stable_id", "external_id", "id"),)
    lineage_any: tuple[str, ...] = ("source_id", "evidence_id", "source", "source_title", "evidence", "provenance", "provenance_type", "citation", "url", "document")
    truth_default: str = "asserted"
    human_supplied: bool = False

CANONICAL_MAPPINGS: tuple[SheetMapping, ...] = (
    SheetMapping(("03_Sources", "Sources", "Source"), "source", required_any=(("source_id","stable_id","id","external_id"),), lineage_any=(), truth_default="source_record"),
    SheetMapping(("04A_Evidence", "Evidence"), "evidence", required_any=(("evidence_id","stable_id","id","external_id"),), lineage_any=("source_id","source_title","source_locator","url","citation","document"), truth_default="evidence_record"),
    SheetMapping(("05_Observations", "Observations", "Observation"), "observation", required_any=(("observation_id","stable_id","id","external_id"),), lineage_any=("source_id","source_ids","evidence_id","evidence_ids","supporting_evidence_ids","source_ref","evidence_ref","source_reference","evidence_reference","supporting_source","supporting_evidence","citation_id","claim_id"), truth_default="observed"),
    SheetMapping(("06_Entities_Rels", "Entities Rels", "Entities and Relationships"), "enterprise_model_candidate", required_any=(("entity_id","relationship_id","stable_id","id","external_id"),), lineage_any=()),
    SheetMapping(("07_Executives_Rights",), "enterprise_model_candidate", lineage_any=()), SheetMapping(("08_Programmes",), "enterprise_model_candidate", lineage_any=()),
    SheetMapping(("09_Capabilities",), "enterprise_model_candidate", lineage_any=()), SheetMapping(("10_Systems_Data",), "enterprise_model_candidate", lineage_any=()),
    SheetMapping(("11_Suppliers_Contracts",), "enterprise_model_candidate", lineage_any=()), SheetMapping(("12_Measures_Resources",), "enterprise_model_candidate", lineage_any=()),
    SheetMapping(("13_Causal_Edges",), "relationship", required_any=(("edge_id","relationship_id","stable_id","id","external_id"),), lineage_any=()),
    SheetMapping(("16_Unknowns", "Unknowns", "Unknown"), "unknown", required_any=(("unknown_id","stable_id","id","external_id"),), lineage_any=(), truth_default="unknown"),
    SheetMapping(("17_Contradictions", "Contradictions", "Contradiction"), "contradiction", required_any=(("contradiction_id","stable_id","id","external_id"),), lineage_any=(), truth_default="contradiction"),
    SheetMapping(("21_Document_Refresh",), "refresh_trigger"), SheetMapping(("22_Provenance_Risk",), "unknown", lineage_any=(), truth_default="provenance_risk"),
    SheetMapping(("24_Human_Knowledge", "Human Supplied Knowledge", "Human Knowledge"), "human_knowledge", lineage_any=(), truth_default="human-supplied", human_supplied=True),
    SheetMapping(("04_Claims", "Claims"), "enterprise_model_candidate", truth_default="claim"),
    SheetMapping(("15_Theses", "Theses"), "enterprise_model_candidate", disposition="reasoning_artifact", truth_default="hypothesis"),
)
PROJECTION_MAPPINGS: tuple[SheetMapping, ...] = tuple(SheetMapping((name,), klass, "projection_only", truth_default="analytical_projection", lineage_any=()) for name, klass in {
    "30_Pain_Portfolio":"pain_point", "31_Pain_Evidence_Conseq":"pain_point", "32_Pain_Class_Select":"priority_disposition", "33_Pain_Disposition":"priority_disposition", "34_Pain_Stakeholders":"stakeholder_hot_button", "35_Pain_Response_Map":"solution_pattern", "36_Current_Responses":"current_response", "37_Response_Effect":"response_effectiveness", "38_Residual_Pain":"residual_pain", "39_Burning_Platform":"burning_platform", "40_Transform_Pressure":"transformation_pressure_view", "41_Pain_Solution_Map":"solution_pattern", "42_Future_Demand":"transformation_pressure_view", "43_Pain_Evidence_Demand":"pain_point", "61_v13_Pain_Selection":"priority_disposition", "62_v13_Flagship_Candidates":"solution_pattern", "92_v13_Shaping_Dossiers":"executive_publication", "93_v13_Buyer_Coalitions":"stakeholder_hot_button", "94_v13_Proof_Architecture":"executive_publication", "95_v13_Conversation_Packs":"executive_publication", "99_v13_Campaign_Sequence":"executive_publication", "106_v13_Sponsor_Map":"stakeholder_hot_button", "115_v13_Outreach_Targets":"stakeholder_hot_button", "Pain Points":"pain_point", "Current Responses":"current_response", "Burning Platforms":"burning_platform", "Transformation Pressures":"transformation_pressure_view", "Response Effectiveness":"response_effectiveness", "Residual Pains":"residual_pain", "Priority Selections":"priority_disposition", "Solution Patterns":"solution_pattern", "Executive Publications":"executive_publication"}.items())
IGNORED_SHEET_PATTERNS = ("control", "dashboard", "calculation", "gate", "release", "acceptance", "workflow", "session_charter", "charter", "handoff", "routing", "return_form", "technical_reconciliation", "summary", "register_dictionary", "plan", "document_refresh_control", "reconciliation")
SHEET_REGISTRY = { _norm(alias): m for m in CANONICAL_MAPPINGS + PROJECTION_MAPPINGS for alias in m.aliases }
_TRUTH = {"unknown": "unknown", "contradiction": "contradiction", "human_supplied_knowledge": "human-supplied", "human_knowledge": "human-supplied"}
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
        actual = sha256_bytes(data)
        hash_matches = (not expected) or actual == expected
        _event(trace, 3, __name__, "Hash selected workbook", workbook_path, "hash match" if hash_matches else "hash mismatch", "Passed" if hash_matches else "Failed", correlation_id, workbook_sha256=actual, workbook_sha256_expected=expected or "not declared", workbook_sha256_actual=actual, workbook_sha256_matches=hash_matches, workbook_adapter_module=__name__, workbook_adapter_implementation_identifier=ADAPTER_IMPLEMENTATION_ID, manifest_workbook_path=workbook_path, resolved_zip_member_path=workbook_path)
        if expected and actual != expected:
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
                seen_ids: set[tuple[str, str]] = set()
                ref_index: dict[str, str] = {}
                claim_lineage: dict[str, list[dict[str, str]]] = {}
                for sheet_name, sheet_file in sheet_map:
                    sheet_names.append(sheet_name)
                    rows=self._rows(wb, sheet_file, shared)
                    out.extend(self._candidates(package, workbook_path, sheet_name, rows, seen_ids, ref_index, claim_lineage))
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
        names=set(wb.namelist())
        _event(trace, 4, __name__, "Open workbook part", "xl/workbook.xml", "Opening workbook sheet list", "Started", correlation_id, source_ooxml_part="xl/workbook.xml", workbook_adapter_module=__name__, workbook_adapter_implementation_identifier=ADAPTER_IMPLEMENTATION_ID, archive_member_count=len(names))
        book=ET.fromstring(wb.read("xl/workbook.xml"))
        sheet_rids: dict[str, str] = {}
        for sheet in book.findall(".//x:sheet", ns):
            sheet_name=sheet.attrib.get("name", "Sheet")
            rid=sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', "")
            if rid:
                sheet_rids[rid]=sheet_name
        _event(trace, 4, __name__, "Open workbook relationships", "xl/_rels/workbook.xml.rels", "Opening workbook relationships", "Started", correlation_id, source_ooxml_part="xl/workbook.xml", relationship_file="xl/_rels/workbook.xml.rels", archive_member_count=len(names))
        rels=ET.fromstring(wb.read("xl/_rels/workbook.xml.rels"))
        targets={}; seen_relationship_ids=set()
        _event(trace, 4, __name__, "Read workbook sheet list", "xl/workbook.xml", "Workbook relationships loaded", "Passed", correlation_id, source_ooxml_part="xl/workbook.xml", relationship_file="xl/_rels/workbook.xml.rels", workbook_adapter_module=__name__, workbook_adapter_implementation_identifier=ADAPTER_IMPLEMENTATION_ID, archive_member_count=len(names))
        for rel in rels:
            rid=str(rel.attrib.get("Id") or "")
            target=str(rel.attrib.get("Target") or "")
            mode=str(rel.attrib.get("TargetMode") or "")
            sheet_name=sheet_rids.get(rid, "")
            if not rid: continue
            if rid in seen_relationship_ids: raise ValueError(f"Duplicate workbook relationship ID: {rid}")
            seen_relationship_ids.add(rid)
            if mode.casefold() == "external":
                _event(trace, 5, __name__, "Skip external worksheet relationship", rid, "External relationship ignored", "Passed", correlation_id, sheet_name=sheet_name, source_ooxml_part="xl/workbook.xml", relationship_file="xl/_rels/workbook.xml.rels", relationship_id=rid, original_relationship_target=target, target_mode=mode, target_classification=_target_classification(target, mode))
                continue
            _event(trace, 5, __name__, "Resolve worksheet relationship target", target, "Resolver entered before ZIP lookup", "Started", correlation_id, resolver_function_name=RESOLVER_FUNCTION_NAME, sheet_name=sheet_name, source_ooxml_part="xl/workbook.xml", relationship_file="xl/_rels/workbook.xml.rels", relationship_id=rid, original_relationship_target=target, target_mode=mode, target_classification=_target_classification(target, mode))
            resolved=self._resolve_part_target("xl/workbook.xml", target)
            exists = resolved in names
            _event(trace, 5, __name__, "Read and normalize worksheet relationship", rid, f"Target: {target}; resolved: {resolved}; exists: {'yes' if exists else 'no'}", "Passed" if exists else "Failed", correlation_id, failure_reason="ZIP member not found" if not exists else "", resolver_function_name=RESOLVER_FUNCTION_NAME, sheet_name=sheet_name, source_ooxml_part="xl/workbook.xml", relationship_file="xl/_rels/workbook.xml.rels", relationship_id=rid, original_relationship_target=target, target_mode=mode, target_classification=_target_classification(target, mode), normalized_target=resolved, final_zip_lookup_path=resolved, zip_member_exists=exists, nearest_matching_zip_members=_nearest_members(resolved, names), archive_member_count=len(names))
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
            exists = resolved in names
            _event(trace, 6, __name__, "Check workbook archive", resolved, "File found; worksheet ready for parsing" if exists else "File not found; processing stopped before candidate staging", "Passed" if exists else "Failed", correlation_id, sheet_name=sheet_name, relationship_id=rid, requested_member_path=resolved, final_zip_lookup_path=resolved, zip_member_exists=exists, nearest_matching_zip_members=_nearest_members(resolved, names), archive_member_count=len(names), current_stage="worksheet_parsing" if exists else "workbook_processing", previous_completed_stage="workbook_relationship_parsing", next_intended_stage="candidate_staging", processing_stopped=not exists, stop_reason="" if exists else "workbook inspection failed", canonical_changes_made=False, promotion_enabled=exists)
            if not exists:
                missing.append(f"Worksheet relationship could not be resolved: sheet={sheet_name}; relationship_id={rid}; target={self._relationship_target(rels, rid)}; resolved={resolved}; missing={resolved}")
                continue
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
            vals=[]; last_col=0; formula_cells=0
            for c in row.findall("x:c", ns):
                ref=str(c.attrib.get("r") or "")
                if ref:
                    letters="".join(ch for ch in ref if ch.isalpha())
                    col=0
                    for ch in letters: col = col*26 + (ord(ch.upper())-64)
                    while last_col and col > last_col + 1: vals.append(""); last_col += 1
                    last_col = col or last_col + 1
                else:
                    last_col += 1
                if c.find("x:f", ns) is not None: formula_cells += 1
                v=c.find("x:v", ns); text="" if v is None or v.text is None else v.text
                vals.append(shared[int(text)] if c.attrib.get("t")=="s" and text.isdigit() and int(text)<len(shared) else text)
            rows.append({"values": vals, "formula_cells": formula_cells, "row_number": int(row.attrib.get("r") or len(rows)+1)})
        return rows

    def _header_index(self, rows):
        for pos, row in enumerate(rows[:10]):
            vals=row["values"]
            normalized=[_norm(v) for v in vals]
            non_empty=[h for h in normalized if h]
            has_human_knowledge_header = (
                any("knowledge_id" in h for h in non_empty)
                and "statement" in non_empty
                and "evidence_class" in non_empty
            )
            if has_human_knowledge_header:
                return pos, normalized
            if len(non_empty) >= 2 and any(h in set(ID_COLUMNS) | {"record_class","item_id","item_type","contradiction_id_preserve_both_positions"} for h in non_empty):
                return pos, normalized
        return (0, [_norm(v) for v in rows[0]["values"]]) if rows else (0, [])

    def _apply_v13_aliases(self, row: dict[str, Any]) -> None:
        aliases = {
            "contradiction_id_preserve_both_positions": ("contradiction_id",),
            "item_id": ("stable_id",),
            "item_type": ("record_type",),
            "entity_class": ("entity_type",),
            "parent_source_entity": ("source_entity_id",),
            "target_entity": ("target_entity_id",),
            "from_entity_state": ("source_entity_id",),
            "to_entity_state": ("target_entity_id",),
            "relationship": ("relationship_type",),
            "mechanism_summary": ("statement",),
            "supporting_observation_ids": ("observation_ids",),
            "supporting_evidence_ids": ("evidence_ids", "supporting_evidence_ids"),
            "status_evidenced_hypothesised": ("status",),
            "knowledge_id_hsk_only_not_mod_evidence": ("human_knowledge_id", "stable_id"),
            "contributor": ("provider",),
            "linked_entities_theses": ("references",),
            "validation_need": ("validation_need",),
            "treatment": ("caveat",),
            "why_material": ("significance",),
            "affected_thesis_mechanism": ("affected_thesis_mechanism",),
            "current_evidence_boundary": ("evidence_boundary",),
            "best_validation_route": ("validation_route",),
            "owner_validator_sought": ("owner",),
            "class": ("contradiction_class",),
            "evidence_needed": ("evidence_needed",),
            "affected_outputs": ("affected_outputs",),
            "current_judgement": ("current_judgement",),
        }
        for source, targets in aliases.items():
            value = row.get(source)
            if not _clean(value):
                continue
            for target in targets:
                row.setdefault(target, value)

    def _is_section_header(self, row: dict[str, str], vals: list[str]) -> bool:
        non=[str(v).strip() for v in vals if str(v).strip()]
        if len(non) == 1 and len(non[0]) < 120: return True
        marker=" ".join(non[:2]).casefold()
        return marker.startswith(("section", "guidance", "instructions", "notes"))

    def _mapping_for_sheet(self, sheet: str) -> SheetMapping | None:
        key=_norm(sheet)
        return SHEET_REGISTRY.get(key)

    def _is_control_sheet(self, sheet: str) -> bool:
        key=_norm(sheet)
        return any(p in key for p in IGNORED_SHEET_PATTERNS) or key.startswith(("00_", "01_", "02_", "20_"))

    def _candidates(self, package, workbook_path, sheet, rows, seen_ids: set[tuple[str, str]] | None = None, ref_index: dict[str, str] | None = None, claim_lineage: dict[str, list[dict[str, str]]] | None = None):
        if len(rows)<1: return []
        seen_ids = seen_ids if seen_ids is not None else set()
        ref_index = ref_index if ref_index is not None else {}
        claim_lineage = claim_lineage if claim_lineage is not None else {}
        header_pos, headers = self._header_index(rows); out=[]
        mapping=self._mapping_for_sheet(sheet)
        control_sheet=self._is_control_sheet(sheet)
        for row_obj in rows[header_pos+1:]:
            idx=row_obj["row_number"]; vals=row_obj["values"]
            non_blank = any(_clean(v) for v in vals)
            row={headers[i] or f"column_{i+1}": vals[i] if i < len(vals) else "" for i in range(len(headers))}
            ignore_reason = ""
            normalized_vals=[_norm(v) for v in vals]
            if not non_blank:
                ignore_reason = "ignored_blank_row"
            elif normalized_vals[:len(headers)] == headers[:len(normalized_vals)] and sum(1 for v in normalized_vals if v) >= 2:
                ignore_reason = "ignored_repeated_header"
            elif _is_formula_only(row_obj, vals):
                ignore_reason = "ignored_formula_only"
            elif self._is_section_header(row, vals):
                ignore_reason = "ignored_section_header"
            elif control_sheet:
                key = _norm(sheet)
                ignore_reason = "ignored_dashboard_row" if "dashboard" in key else "ignored_workflow_row" if "workflow" in key else "ignored_release_control" if "release" in key else "ignored_control_row"
            if ignore_reason:
                ext=f"{_norm(sheet)}-{idx}-{ignore_reason}"
                payload={"mapping_version": MAPPING_VERSION, "mapping_disposition": "ignored", "ignore_reason": ignore_reason, "source_worksheet": sheet, "source_row": idx, "header_row": header_pos+1}
                loc={"workbook": workbook_path, "sheet": sheet, "row": idx, "stable_id": ext, "mapping_version": MAPPING_VERSION, "header_row": header_pos+1}
                out.append(CandidateImportRecord("1.0", candidate_id(package.package_ref, workbook_path, ext, "ignored_row"), package.package_ref, package.package_sha256, workbook_path, sheet, loc, ext, "ignored_row", "ignored", payload, "ignored", (), sha256_bytes(json.dumps(payload, sort_keys=True).encode()), utc_now(), package.import_run_id, 0))
                continue
            self._apply_v13_aliases(row)
            row["__has_evidence_class"] = "evidence_class" in row
            findings=[]
            if not mapping:
                rc=str(row.get("record_class") or "unsupported_twin_spine_row"); status="quarantined"; truth="unknown"
                findings=[ValidationFinding("warning","quarantined_unsupported_schema",f"Unsupported Twin Spine worksheet: {sheet}",f"{workbook_path}:{sheet}!{idx}")]
            else:
                rc=str(row.get("record_class") or mapping.candidate_class)
                row_type=str(row.get("record_type") or row.get("type") or row.get("class") or row.get("relationship_type") or row.get("entity_type") or "").casefold()
                if mapping.candidate_class == "enterprise_model_candidate" and ("relationship" in row_type or (_clean(row.get("source_entity_id") or row.get("source")) and _clean(row.get("target_entity_id") or row.get("target")))): rc="relationship"
                elif mapping.candidate_class == "enterprise_model_candidate" and ("entity" in row_type or _clean(row.get("name")) or _clean(row.get("label"))): rc="entity"
                truth=str(row.get("truth_class") or row.get("truth") or _TRUTH.get(_norm(sheet)) or mapping.truth_default)
                status="accepted" if rc in SUPPORTED_RECORD_CLASSES and rc not in PROJECTION_ONLY_CLASSES else "quarantined"
                if mapping.disposition in {"projection_only", "reasoning_artifact"} or rc in PROJECTION_ONLY_CLASSES:
                    status = "accepted" if rc in SUPPORTED_RECORD_CLASSES and rc not in PROJECTION_ONLY_CLASSES and mapping.disposition == "reasoning_artifact" else "quarantined"
                    findings.append(ValidationFinding("warning","projection_only","Projection-only/reasoning class retained outside canonical intelligence",f"{workbook_path}:{sheet}!{idx}"))
                if rc not in SUPPORTED_RECORD_CLASSES:
                    status="quarantined"; findings.append(ValidationFinding("warning","quarantined_unsupported_schema",f"Unsupported record class in mapped sheet: {rc}",f"{workbook_path}:{sheet}!{idx}"))
                missing=[]
                for group in mapping.required_any:
                    if not any(_clean(row.get(_norm(c))) for c in group): missing.append("/".join(group))
                ext_supplied = any(_clean(row.get(k)) for k in ID_COLUMNS)
                if missing:
                    derived, basis = _derive_identifier(package.identity.enterprise_id, rc, sheet, row, idx)
                    if derived:
                        row["stable_id"] = derived; row["identifier_derivation"] = {"derived": True, "basis": basis, "strategy": "sha256-natural-key-v1", "source_supplied": False}
                        missing=[]
                    else:
                        status="quarantined"; findings.append(ValidationFinding("error","quarantined_missing_identifier",f"Missing required identifier column value: {', '.join(missing)}",f"{workbook_path}:{sheet}!{idx}"))
                lineage_values=[]
                for c in mapping.lineage_any:
                    lineage_values.extend(_split_refs(row.get(_norm(c))))
                lineage_values=list(dict.fromkeys(lineage_values))
                resolutions=[]; resolved_any=False
                for ref in lineage_values:
                    rk=_ref_key(ref); resolved=ref_index.get(rk, "")
                    if not resolved and _ref_key(ref).startswith("claim") and row.get("claim_id"):
                        inherited = claim_lineage.get(rk, [])
                        resolved = ";".join(x.get("resolved_staged_candidate", "") for x in inherited if x.get("resolved_staged_candidate"))
                    resolved_any = resolved_any or bool(resolved)
                    resolutions.append({"original_reference": ref, "normalized_reference": rk, "resolved_staged_candidate": resolved, "unresolved_reason": "" if resolved else "reference_not_found_in_staged_sources_or_evidence"})
                if rc == "observation" and (_norm(sheet) == "05_observations") and not resolved_any:
                    status="quarantined"; findings.append(ValidationFinding("error","quarantined_missing_lineage" if not lineage_values else "quarantined_invalid_reference",f"Missing resolved evidence/source lineage for {rc}",f"{workbook_path}:{sheet}!{idx}"))
                elif rc not in PROJECTION_ONLY_CLASSES and re.match(r"^[0-9]", str(sheet)) and mapping.lineage_any and not lineage_values:
                    status="quarantined"; findings.append(ValidationFinding("error","quarantined_missing_lineage",f"Missing required evidence/source lineage for {rc}",f"{workbook_path}:{sheet}!{idx}"))
                if resolutions:
                    row["lineage_resolution"] = resolutions
            ext=""
            preferred_ids = {"source": ("source_id","stable_id","external_id","id"), "evidence": ("evidence_id","stable_id","external_id","id"), "observation": ("observation_id","stable_id","external_id","id"), "unknown": ("unknown_id","stable_id","external_id","id"), "contradiction": ("contradiction_id","stable_id","external_id","id"), "entity": ("entity_id","stable_id","external_id","id"), "relationship": ("relationship_id","edge_id","stable_id","external_id","id"), "human_knowledge": ("human_knowledge_id","stable_id","external_id","id")}.get(rc, ID_COLUMNS)
            for key in preferred_ids:
                if _clean(row.get(key)): ext=_clean(row.get(key)); break
            ext=ext or f"{_norm(sheet)}-{idx}"
            key=(rc, ext)
            if key in seen_ids:
                suffix=sha256_bytes(json.dumps(row, sort_keys=True).encode())[:8]
                ext=f"{ext}-{suffix}"
                row.setdefault("identifier_collision_resolution", {"collision_checked": True, "collision_suffix": suffix})
            seen_ids.add((rc, ext))
            if rc == "relationship":
                row.setdefault("source_entity_id", _clean(row.get("source_entity_id") or row.get("from") or row.get("source")))
                row.setdefault("target_entity_id", _clean(row.get("target_entity_id") or row.get("to") or row.get("target")))
                row.setdefault("relationship_type", _norm(row.get("relationship_type") or row.get("type") or row.get("record_type")))
                if not (_clean(row.get("source_entity_id")) and _clean(row.get("target_entity_id")) and _clean(row.get("relationship_type"))):
                    status="quarantined"; findings.append(ValidationFinding("error","quarantined_ambiguous_row_type","Relationship rows require source endpoint, target endpoint and relationship type",f"{workbook_path}:{sheet}!{idx}"))
            if rc == "entity":
                row.setdefault("entity_name", _clean(row.get("entity_name") or row.get("name") or row.get("label") or row.get("title")))
                row.setdefault("entity_type", _norm(row.get("entity_type") or row.get("type") or row.get("record_type") or sheet))
                if not (_clean(row.get("stable_id") or row.get("entity_id") or row.get("id")) and _clean(row.get("entity_name")) and _clean(row.get("entity_type"))):
                    status="quarantined"; findings.append(ValidationFinding("error","quarantined_ambiguous_row_type","Entity rows require clear identity and type",f"{workbook_path}:{sheet}!{idx}"))
            if rc == "human_knowledge":
                evidence_class = _clean(row.get("evidence_class")).casefold()
                marker_ok = ("human" in evidence_class and ("supplied" in evidence_class or "knowledge" in evidence_class)) or not row.get("__has_evidence_class")
                if not (_clean(row.get("human_knowledge_id") or row.get("stable_id")) and _clean(row.get("statement")) and marker_ok):
                    status="quarantined"; findings.append(ValidationFinding("error","quarantined_human_knowledge_requirements","Human Knowledge rows require HSK ID, statement and human-supplied evidence class",f"{workbook_path}:{sheet}!{idx}"))
            payload={k:v for k,v in row.items() if v not in ("", None) and not str(k).startswith("__")}
            payload.setdefault("twin_version", package.identity.package_version)
            payload["mapping_version"] = MAPPING_VERSION
            payload["mapping_disposition"] = "unsupported" if not mapping else mapping.disposition
            payload["source_worksheet"] = sheet; payload["source_row"] = idx
            payload.setdefault("identifier_metadata", {"source_supplied": bool('ext_supplied' in locals() and ext_supplied), "derived": bool(isinstance(payload.get("identifier_derivation"), dict))})
            if mapping and mapping.human_supplied: payload["human_supplied"] = True; payload.setdefault("truth_class", "human-supplied")
            loc={"workbook": workbook_path, "sheet": sheet, "row": idx, "stable_id": ext, "mapping_version": MAPPING_VERSION, "header_row": header_pos+1}
            cand = CandidateImportRecord("1.0", candidate_id(package.package_ref, workbook_path, ext, rc), package.package_ref, package.package_sha256, workbook_path, sheet, loc, ext, rc, truth, payload, status, tuple(findings), sha256_bytes(json.dumps(payload, sort_keys=True).encode()), utc_now(), package.import_run_id, 0)
            out.append(cand)
            if status == "accepted" and rc in {"source", "evidence"}:
                ref_index[_ref_key(ext)] = cand.candidate_record_id
                for k in preferred_ids:
                    if _clean(row.get(k)): ref_index[_ref_key(row.get(k))] = cand.candidate_record_id
            if rc == "enterprise_model_candidate" and _clean(row.get("claim_id")) and payload.get("lineage_resolution"):
                claim_lineage[_ref_key(row.get("claim_id"))] = payload.get("lineage_resolution") or []
        return out
