"""Read-only assembly service for the Flora Enterprise Canvas."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from cios.applications.flora.access import authenticated_flora_user, user_enterprise_access
from cios.applications.flora.blueprint_import.archive import sha256_bytes
from cios.applications.flora.blueprint_import.candidates import PROJECTION_ONLY_CLASSES, CandidateStagingRepository
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.memory.models import EnterpriseModelAttribute, EnterpriseUnknown
from cios.applications.flora.memory.repository import EnterpriseModelRepository, EvidenceRepository, ObservationRepository

from .models import CANVAS_SCHEMA_VERSION, CanvasAnalyticalProjection, CanvasLineageReference, EnterpriseCanvas, EnterpriseCanvasHeader, EnterpriseCanvasTile


class EnterpriseCanvasAccessError(PermissionError):
    """Raised when a product session cannot view an Enterprise Canvas."""


def can_view_enterprise_canvas(headers: Any, enterprise_id: str) -> bool:
    if not authenticated_flora_user(headers):
        return False
    allowed = user_enterprise_access(headers)
    return "*" in allowed or enterprise_id in allowed


class EnterpriseCanvasService:
    """Assemble governed Canvas DTOs without writing canonical state."""

    def __init__(self, models=None, observations=None, evidence=None, staging=None, registry=None):
        self.models = models or EnterpriseModelRepository()
        self.observations = observations or ObservationRepository()
        self.evidence = evidence or EvidenceRepository()
        self.staging = staging or CandidateStagingRepository()
        self.registry = registry or BlueprintPackageRegistry()

    def get_canvas(self, enterprise_id: str, headers: Any, lens: str = "organisation") -> EnterpriseCanvas:
        enterprise_id = canonical_enterprise_id(enterprise_id) or enterprise_id
        if lens != "organisation":
            raise ValueError("Only the organisation lens is supported in this bounded read model")
        if not can_view_enterprise_canvas(headers, enterprise_id):
            raise EnterpriseCanvasAccessError("Actor is not authorised to view this Enterprise Canvas")
        model = self.models.get(enterprise_id)
        attributes = dict(sorted(model.attributes.items()))
        unknowns = tuple(model.unknowns.values())
        evidence_rows = {str(e.get("evidence_id")): e for e in self.evidence.list()}
        projections = self._accepted_projections(enterprise_id)
        header = self._header(enterprise_id, attributes, unknowns, projections)
        tiles = tuple(self._tiles(enterprise_id, attributes, unknowns, evidence_rows, projections))
        return EnterpriseCanvas(CANVAS_SCHEMA_VERSION, enterprise_id, lens, header, tiles, True)

    def _header(self, enterprise_id, attrs, unknowns, projections):
        def attr(name, default="Unknown"):
            return (attrs.get(name) or attrs.get(f"enterprise.{name}") or EnterpriseModelAttribute("", "", default, 0, "", "unknown", (), (), "unknown")).current_value or default
        latest_dates = [a.last_observed_date for a in attrs.values() if a.last_observed_date]
        stale = [a.attribute for a in attrs.values() if a.freshness == "stale"]
        pressures = [p.display_label for p in projections if p.projection_type in {"pain_point", "burning_platform", "transformation_pressure_view"}]
        return EnterpriseCanvasHeader(
            enterprise_name=attr("name", enterprise_id),
            enterprise_purpose=attr("purpose"),
            twin_version=attr("twin_version", "Not established"),
            effective_date=max(latest_dates) if latest_dates else "Unknown",
            source_cut_off=attr("source_cut_off", max(latest_dates) if latest_dates else "Unknown"),
            maturity_or_acceptance_state=attr("acceptance_state", "Accepted Evidence-backed state" if attrs else "Incomplete"),
            latest_material_change=attr("latest_material_change", "Unknown"),
            governing_thesis=attr("governing_thesis", "Unknown"),
            current_material_pressures=tuple(pressures[:5]),
            freshness_warning=("Some evidence is stale" if stale else ""),
            last_refreshed_date=attr("last_refreshed_date", max(latest_dates) if latest_dates else "Unknown"),
        )

    def _tiles(self, enterprise_id, attrs, unknowns, evidence_rows, projections):
        groups: dict[str, list[EnterpriseModelAttribute]] = defaultdict(list)
        for attr in attrs.values():
            if attr.domain.startswith("organisation") or attr.domain in {"unit", "domain", "programme"}:
                key = attr.attribute.split(".")[0]
                groups[key].append(attr)
        if not groups and attrs:
            groups["enterprise"].extend(attrs.values())
        for order, (key, facts) in enumerate(sorted(groups.items()), start=1):
            ref = f"{enterprise_id}:{key}"
            projections_for_tile = tuple(p for p in projections if key.casefold() in " ".join([p.display_label, *p.supporting_record_refs]).casefold() or p.projection_type in {"pain_point", "burning_platform", "transformation_pressure_view"})[:8]
            lineage = tuple(self._lineage_for_attribute(f, evidence_rows) for f in facts)
            unknown = any(u.affected_domain in {key, "organisation", "enterprise"} and u.status == "open" for u in unknowns) or any(f.current_value in (None, "") for f in facts)
            contradiction = any(f.contradiction_state != "none" or f.trust_state == "contradicted" for f in facts)
            stale = any(f.freshness == "stale" for f in facts)
            yield EnterpriseCanvasTile(
                tile_view_id="canvas-tile-" + sha256_bytes(f"{enterprise_id}\norganisation\n{ref}".encode())[:20],
                lens="organisation",
                sort_order=order,
                underlying_reference=ref,
                display_name=self._first(facts, ["display_name", "name"], key.replace("_", " ").title()),
                plain_english_role=self._first(facts, ["role", "purpose", "what_it_does"], "This part of the enterprise has an accepted role, but details are incomplete."),
                accountable_role=self._first(facts, ["accountable_role", "owner"], "Unknown"),
                current_state=self._first(facts, ["current_state", "state"], "Unknown"),
                principal_pain_or_pressure=(projections_for_tile[0].display_label if projections_for_tile else "Unknown"),
                material_change=self._first(facts, ["material_change", "latest_material_change"], "Unknown"),
                what_has_been_done_so_far=self._projection_label(projections, {"current_response", "response_effectiveness"}),
                what_remains_unresolved=self._projection_label(projections, {"residual_pain"}),
                unknown_indicator=unknown,
                contradiction_indicator=contradiction,
                stale_evidence_indicator=stale,
                nested_twin_available=self._first(facts, ["nested_twin_available"], "false").lower() == "true",
                effective_date=max((f.last_observed_date for f in facts if f.last_observed_date), default="Unknown"),
                source_cut_off=max((f.last_observed_date for f in facts if f.last_observed_date), default="Unknown"),
                last_refreshed_date=max((f.updated_at for f in facts if f.updated_at), default="Unknown"),
                core_facts=tuple(f"{f.attribute.replace('_',' ')}: {f.current_value or 'Unknown'}" for f in facts),
                analytical_projections=projections_for_tile,
                lineage_references=lineage + tuple(l for p in projections_for_tile for l in p.lineage),
                inspection={"underlying_attributes": [f.attribute for f in facts]},
            )

    def _first(self, facts, names, default):
        for name in names:
            for f in facts:
                leaf = f.attribute.rsplit(".", 1)[-1]
                if leaf == name and f.current_value:
                    return str(f.current_value)
        return default

    def _projection_label(self, projections, types):
        return next((p.display_label for p in projections if p.projection_type in types), "Unknown")

    def _lineage_for_attribute(self, attr, evidence_rows):
        sources = tuple(str(evidence_rows.get(eid, {}).get("source_id") or evidence_rows.get(eid, {}).get("source") or "") for eid in attr.evidence_ids)
        return CanvasLineageReference(attr.current_value or attr.attribute, "canonical_attribute", attr.attribute, attr.observation_ids, attr.evidence_ids, tuple(s for s in sources if s))

    def _accepted_projections(self, enterprise_id):
        out = []
        for package in self.registry.list():
            if package.identity.enterprise_id != enterprise_id:
                continue
            for c in self.staging.list_candidates(package.import_run_id):
                if c.get("candidate_object_class") not in PROJECTION_ONLY_CLASSES or c.get("validation_status") == "rejected":
                    continue
                payload = c.get("payload") or {}
                label = str(payload.get("display_label") or payload.get("statement") or payload.get("name") or c.get("original_source_id"))
                lineage = CanvasLineageReference(label, "analytical_projection", c["candidate_record_id"], tuple(payload.get("observation_ids") or ()), tuple(payload.get("evidence_ids") or ()), tuple(payload.get("source_ids") or ()), package.package_ref, package.import_run_id, str(c.get("source_location") or c.get("source_file") or ""))
                out.append(CanvasAnalyticalProjection(label, c["candidate_object_class"], str(payload.get("twin_version") or package.identity.package_version), tuple(payload.get("supporting_record_refs") or (c["candidate_record_id"],)), str(payload.get("effective_date") or ""), str(payload.get("confidence") or payload.get("qualification") or ""), str(payload.get("status") or "accepted projection"), (lineage,)))
        return tuple(sorted(out, key=lambda p: (p.projection_type, p.display_label)))
