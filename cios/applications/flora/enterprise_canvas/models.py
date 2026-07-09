"""Plain-language read models for Flora's Enterprise Canvas.

These dataclasses are DTOs only. They are assembled from governed canonical
memory and accepted analytical projections, and are never written back as
canonical enterprise intelligence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

CANVAS_SCHEMA_VERSION = "flora-enterprise-canvas-v1"


@dataclass(frozen=True)
class CanvasLineageReference:
    displayed_judgement: str
    reference_type: str
    reference_id: str
    observation_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    package_ref: str = ""
    import_run_id: str = ""
    package_location: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("observation_ids", "evidence_ids", "source_ids"):
            data[key] = list(data[key])
        return data


@dataclass(frozen=True)
class CanvasAnalyticalProjection:
    display_label: str
    projection_type: str
    package_or_twin_version: str
    supporting_record_refs: tuple[str, ...] = ()
    effective_date: str = ""
    confidence_or_qualification: str = ""
    status: str = ""
    lineage: tuple[CanvasLineageReference, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["supporting_record_refs"] = list(self.supporting_record_refs)
        data["lineage"] = [item.to_dict() for item in self.lineage]
        return data


@dataclass(frozen=True)
class EnterpriseCanvasHeader:
    enterprise_name: str
    enterprise_purpose: str
    twin_version: str
    effective_date: str
    source_cut_off: str
    maturity_or_acceptance_state: str
    latest_material_change: str = ""
    governing_thesis: str = ""
    current_material_pressures: tuple[str, ...] = ()
    freshness_warning: str = ""
    last_refreshed_date: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["current_material_pressures"] = list(self.current_material_pressures)
        return data


@dataclass(frozen=True)
class EnterpriseCanvasTile:
    tile_view_id: str
    lens: str
    sort_order: int
    underlying_reference: str
    display_name: str
    plain_english_role: str
    accountable_role: str = "Unknown"
    current_state: str = "Unknown"
    principal_pain_or_pressure: str = "Unknown"
    material_change: str = "Unknown"
    what_has_been_done_so_far: str = "Unknown"
    what_remains_unresolved: str = "Unknown"
    unknown_indicator: bool = False
    contradiction_indicator: bool = False
    stale_evidence_indicator: bool = False
    nested_twin_available: bool = False
    effective_date: str = ""
    source_cut_off: str = ""
    last_refreshed_date: str = ""
    core_facts: tuple[str, ...] = ()
    analytical_projections: tuple[CanvasAnalyticalProjection, ...] = ()
    lineage_references: tuple[CanvasLineageReference, ...] = ()
    inspection: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["core_facts"] = list(self.core_facts)
        data["analytical_projections"] = [item.to_dict() for item in self.analytical_projections]
        data["lineage_references"] = [item.to_dict() for item in self.lineage_references]
        return data


@dataclass(frozen=True)
class EnterpriseCanvas:
    schema_version: str
    enterprise_id: str
    lens: str
    header: EnterpriseCanvasHeader
    tiles: tuple[EnterpriseCanvasTile, ...]
    read_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "enterprise_id": self.enterprise_id,
            "lens": self.lens,
            "header": self.header.to_dict(),
            "tiles": [tile.to_dict() for tile in self.tiles],
            "read_only": self.read_only,
        }
