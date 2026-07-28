"""Declared Commercial Mission projection for the authenticated Flora user.

Mission data is operational user context, never Enterprise Intelligence.  The
file-backed configuration is intentionally separate from Twin and evidence
stores and may be replaced by an IAM/profile adapter later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Any

from cios.applications.flora.access import authenticated_flora_user

DEFAULT_CONFIG = Path(__file__).resolve().parents[3] / "config" / "flora" / "commercial_missions.json"


@dataclass(frozen=True)
class CommercialMission:
    user_id: str
    executive_role: str
    employer: str
    commercial_objective: str
    industries: tuple[str, ...] = ()
    enterprises: tuple[str, ...] = ()
    offer_portfolio: tuple[str, ...] = ()
    competitors: tuple[str, ...] = ()
    partners: tuple[str, ...] = ()
    geography: tuple[str, ...] = ()
    inspection_depth: str = "executive-to-evidence"
    authority_status: str = "human-supplied operational context"
    supplied_by: str = "configured user profile"

    @classmethod
    def from_dict(cls, user_id: str, value: dict[str, Any]) -> "CommercialMission":
        scalar = {k: str(value.get(k) or "") for k in ("executive_role", "employer", "commercial_objective")}
        lists = {k: tuple(str(v) for v in value.get(k, ()) if str(v).strip()) for k in
                 ("industries", "enterprises", "offer_portfolio", "competitors", "partners", "geography")}
        return cls(user_id=user_id, **scalar, **lists,
                   inspection_depth=str(value.get("inspection_depth") or "executive-to-evidence"),
                   authority_status=str(value.get("authority_status") or "human-supplied operational context"),
                   supplied_by=str(value.get("supplied_by") or "configured user profile"))


def resolve_commercial_mission(headers: Any) -> CommercialMission | None:
    """Resolve declared context for the authenticated principal; never infer it."""
    user_id = authenticated_flora_user(headers)
    if not user_id:
        return None
    path = Path(os.getenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(DEFAULT_CONFIG)))
    try:
        profiles = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    value = profiles.get(user_id)
    return CommercialMission.from_dict(user_id, value) if isinstance(value, dict) else None
