"""Declared Commercial Mission projection for the authenticated Flora user.

Mission data is operational user context, never Enterprise Intelligence.  The
file-backed configuration is intentionally separate from Twin and evidence
stores and may be replaced by an IAM/profile adapter later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import tempfile
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
    interests: tuple[str, ...] = ()
    named_accounts: tuple[str, ...] = ()
    campaigns: tuple[str, ...] = ()
    mission_name: str = ""
    target_customers: tuple[str, ...] = ()
    priority_accounts: tuple[str, ...] = ()
    excluded_accounts: tuple[str, ...] = ()
    relevant_business_units: tuple[str, ...] = ()
    account_focus: str = ""
    commercial_horizon: str = ""
    objectives: tuple[str, ...] = ()
    strategic_propositions: tuple[str, ...] = ()
    delivery_constraints: tuple[str, ...] = ()
    opportunity_horizon: str = ""
    required_opportunity_maturity: str = ""
    minimum_evidence_state: str = ""
    speculative_treatment: str = ""
    show_unvalued_opportunities: bool = False
    inspection_depth: str = "executive-to-evidence"
    authority_status: str = "human-supplied operational context"
    supplied_by: str = "configured user profile"

    @classmethod
    def from_dict(cls, user_id: str, value: dict[str, Any]) -> "CommercialMission":
        scalar = {k: str(value.get(k) or "") for k in ("executive_role", "employer", "commercial_objective")}
        lists = {k: tuple(str(v) for v in value.get(k, ()) if str(v).strip()) for k in
                 ("industries", "enterprises", "offer_portfolio", "competitors", "partners", "geography",
                  "interests", "named_accounts", "campaigns", "target_customers", "priority_accounts",
                  "excluded_accounts", "relevant_business_units", "objectives", "strategic_propositions",
                  "delivery_constraints")}
        return cls(user_id=user_id, **scalar, **lists,
                   **{k: str(value.get(k) or "") for k in ("mission_name", "account_focus", "commercial_horizon",
                      "opportunity_horizon", "required_opportunity_maturity", "minimum_evidence_state", "speculative_treatment")},
                   show_unvalued_opportunities=bool(value.get("show_unvalued_opportunities", False)),
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


def save_commercial_mission(headers: Any, value: dict[str, Any]) -> CommercialMission:
    """Atomically persist declared mission context against the existing user ID."""
    user_id = authenticated_flora_user(headers)
    if not user_id:
        raise PermissionError("An authenticated Flora user is required")
    path = Path(os.getenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(DEFAULT_CONFIG)))
    try:
        profiles = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        profiles = {}
    if not isinstance(profiles, dict):
        raise ValueError("Commercial Mission profile store must be an object")
    mission = CommercialMission.from_dict(user_id, value)
    if not all((mission.executive_role, mission.employer, mission.commercial_objective)):
        raise ValueError("Role, employer and objective are required")
    profiles[user_id] = {name: list(getattr(mission, name)) for name in (
        "industries", "enterprises", "offer_portfolio", "competitors", "partners", "geography",
        "interests", "named_accounts", "campaigns", "target_customers", "priority_accounts",
        "excluded_accounts", "relevant_business_units", "objectives", "strategic_propositions", "delivery_constraints")}
    profiles[user_id].update({name: getattr(mission, name) for name in (
        "executive_role", "employer", "commercial_objective", "mission_name", "account_focus", "commercial_horizon",
        "opportunity_horizon", "required_opportunity_maturity", "minimum_evidence_state", "speculative_treatment",
        "show_unvalued_opportunities", "inspection_depth", "authority_status", "supplied_by")})
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(profiles, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)
    return mission
