"""Enterprise adapter over the existing Enterprise Canvas read runtime."""
from __future__ import annotations
from html import escape
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
from cios.applications.flora.enterprise_canvas.views import _executive_canvas, _has_successful_reasoning
from .contracts import InspectionAdapter, InspectionProfile, InspectionSection

UNAVAILABLE = "Unavailable"

def _known(value: object) -> str:
    text = str(value or "").strip()
    return UNAVAILABLE if not text or text.casefold() in {"unknown", "not established", "evidence incomplete"} else text

def enterprise_inspection_adapter(enterprise_id: str, headers) -> InspectionAdapter:
    """Resolve an Enterprise to its existing Canvas without copying its DTOs."""
    canvas = EnterpriseCanvasService().get_canvas(enterprise_id, headers)
    header = canvas.header
    access_record = EnterpriseCanvasAccessRepository().get(canvas.enterprise_id)
    lineage = tuple(ref for tile in canvas.tiles for ref in tile.lineage_references)
    package_refs = tuple(dict.fromkeys(ref.package_ref for ref in lineage if ref.package_ref))
    import_runs = tuple(dict.fromkeys(ref.import_run_id for ref in lineage if ref.import_run_id))
    unknown_count = sum(tile.unknown_indicator for tile in canvas.tiles)
    contradiction_count = sum(tile.contradiction_indicator for tile in canvas.tiles)
    stale_count = sum(tile.stale_evidence_indicator for tile in canvas.tiles)
    evidence_links = sum(len(ref.evidence_ids) for ref in lineage)
    confidence = tuple(dict.fromkeys(p.confidence_or_qualification for t in canvas.tiles for p in t.analytical_projections if p.confidence_or_qualification))
    profile = InspectionProfile(
        header.enterprise_name, "Enterprise", _known(access_record.owner_account if access_record else ""), _known(header.maturity_or_acceptance_state),
        _known(header.twin_version), _known(header.last_refreshed_date), _known(header.source_cut_off),
        UNAVAILABLE, _known(header.maturity_or_acceptance_state),
        f"{evidence_links} governed evidence link(s)" if evidence_links else UNAVAILABLE,
        f"{stale_count} area(s) flagged stale" if stale_count else _known(header.last_refreshed_date),
        "; ".join(confidence) if confidence else UNAVAILABLE, str(unknown_count), str(contradiction_count),
        f"{len(package_refs)} Research Package(s) · {len(import_runs)} Import Run(s)" if package_refs or import_runs else UNAVAILABLE,
    )
    # Generated intelligence is optional.  Without a successful governed brief,
    # the established deterministic Canvas overview is the executive opening.
    canvas_provider = lambda: _executive_canvas(canvas, headers, include_reasoning=_has_successful_reasoning(canvas), force_overview=True)
    metadata = (_known(header.last_refreshed_date), _known(header.effective_date))
    sections = (
        InspectionSection("executive-intelligence", "Executive Intelligence", 10, canvas_provider, "governed read model and labelled projections", True, True, "#evidence-and-lineage", *metadata),
        InspectionSection("commercial", "Commercial", 20, lambda: "", "governed Canvas projection", True, True, "#commercial-relevance", *metadata),
        InspectionSection("evidence", "Evidence", 30, lambda: "", "governed evidence", bool(lineage), True, "#evidence-and-lineage", *metadata),
        InspectionSection("unknowns", "Unknowns", 40, lambda: "", "canonical unknown", bool(unknown_count), True, "#unknowns-and-contradictions", *metadata),
        InspectionSection("contradictions", "Contradictions", 50, lambda: "", "governed contradiction", bool(contradiction_count), True, "#unknowns-and-contradictions", *metadata),
        InspectionSection("research-lineage", "Research Lineage", 60, lambda: _lineage(package_refs, import_runs), "governed provenance", bool(package_refs or import_runs), True, "#research-lineage", *metadata),
    )
    return InspectionAdapter("enterprise-canvas", profile, sections)

def _lineage(package_refs: tuple[str, ...], import_runs: tuple[str, ...]) -> str:
    packages = "".join(f"<li><code>{escape(v)}</code></li>" for v in package_refs) or "<li>Unavailable</li>"
    runs = "".join(f"<li><a href='/blueprint-import/{escape(v)}'><code>{escape(v)}</code></a></li>" for v in import_runs) or "<li>Unavailable</li>"
    histories = "".join(f"<li><a href='/blueprint-import/{escape(v)}'>Promotion and review record for <code>{escape(v)}</code></a></li>" for v in import_runs) or "<li>Unavailable</li>"
    return f"<section class='card' id='research-lineage'><h2>Research Lineage</h2><p>This provenance is distinct from the current governed Twin shown above.</p><h3>Research Package</h3><ul>{packages}</ul><h3>Import Run</h3><ul>{runs}</ul><h3>Promotion History</h3><ul>{histories}</ul><h3>Review History</h3><ul>{histories}</ul></section>"
