"""Calibration utilities for scoped Flora Enterprise Model runs."""
from __future__ import annotations

from cios.applications.flora.storage import data_path

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository


def inspection_rows(enterprise: str, observations: ObservationRepository | None = None, models: EnterpriseModelRepository | None = None) -> list[dict]:
    cid = canonical_enterprise_id(enterprise) or enterprise
    observations = observations or ObservationRepository()
    models = models or EnterpriseModelRepository()
    model = models.get(cid)
    rows = []
    for obs in observations.list():
        if obs.enterprise_id != cid:
            continue
        attr = model.attributes.get(obs.affected_attribute)
        rows.append({
            "observation_id": obs.observation_id,
            "atomic_statement": obs.atomic_statement,
            "evidence_ids": list(obs.supporting_evidence_ids),
            "enterprise_id": obs.enterprise_id,
            "affected_model_domain": obs.affected_attribute.split(".", 1)[0],
            "affected_attribute": obs.affected_attribute,
            "update_result": "projected" if attr and obs.observation_id in attr.observation_ids else "not_projected",
            "confidence": obs.confidence,
            "freshness": obs.freshness,
            "rejection_reason": None if obs.lifecycle_state == "accepted" else obs.lifecycle_state,
        })
    return rows


def archive_and_reset_enterprise(enterprise: str, *, confirm: str, observations: ObservationRepository | None = None, models: EnterpriseModelRepository | None = None, archive_root: Path | None = None) -> dict:
    cid = canonical_enterprise_id(enterprise) or enterprise
    if confirm != f"reset {cid}":
        raise ValueError(f"Explicit confirmation required: reset {cid}")
    observations = observations or ObservationRepository()
    models = models or EnterpriseModelRepository()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    archive_dir = archive_root / cid / stamp
    archive_dir.mkdir(parents=True, exist_ok=True)
    model_path = models.path_for(cid)
    if model_path.exists():
        shutil.copy2(model_path, archive_dir / model_path.name)
        model_path.unlink()
    all_obs = observations.list()
    kept = [o for o in all_obs if o.enterprise_id != cid]
    archived = [o for o in all_obs if o.enterprise_id == cid]
    (archive_dir / "observations.jsonl").write_text("".join(json.dumps(o.to_dict(), sort_keys=True) + "\n" for o in archived), encoding="utf-8")
    observations._rewrite(kept)
    audit = {"enterprise_id": cid, "archived_observations": len(archived), "archive_dir": str(archive_dir), "reset_at": datetime.now(UTC).isoformat(), "other_enterprise_observations_preserved": len(kept)}
    (archive_dir / "reset_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")
    return audit
