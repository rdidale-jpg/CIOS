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
DEFAULT_EMPLOYER_CONFIG = Path(__file__).resolve().parents[3] / "config" / "flora" / "employer_contexts.json"


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

    def employer_context(self) -> "EmployerContext":
        """Project employer data as a separate authority (never Twin intelligence)."""
        return EmployerContext(
            organisation=self.employer,
            offer_portfolio=self.offer_portfolio,
            capabilities=(),
            propositions=self.strategic_propositions,
            partners=self.partners,
            competitors=self.competitors,
            constraints=self.delivery_constraints,
        )

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
    if not all((mission.executive_role, mission.commercial_objective)):
        raise ValueError("Role and objective are required")
    profiles[user_id] = {name: list(getattr(mission, name)) for name in (
        "industries", "enterprises", "geography",
        "interests", "named_accounts", "campaigns", "target_customers", "priority_accounts",
        "excluded_accounts", "relevant_business_units", "objectives")}
    profiles[user_id].update({name: getattr(mission, name) for name in (
        "executive_role", "commercial_objective", "mission_name", "account_focus", "commercial_horizon",
        "opportunity_horizon", "required_opportunity_maturity", "minimum_evidence_state", "speculative_treatment",
        "show_unvalued_opportunities", "inspection_depth", "authority_status", "supplied_by")})
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(profiles, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)
    return mission


@dataclass(frozen=True)
class EmployerContext:
    """Declared supplier-side context, deliberately separate from the mission and Twin."""
    organisation: str = ""
    description: str = ""
    offer_portfolio: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    propositions: tuple[str, ...] = ()
    partners: tuple[str, ...] = ()
    competitors: tuple[str, ...] = ()
    credentials: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    target_sectors: tuple[str, ...] = ()
    excluded_offerings: tuple[str, ...] = ()
    authority_status: str = "human-supplied"
    field_statuses: dict[str, str] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        return bool(self.organisation and self.offer_portfolio and self.propositions)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "EmployerContext":
        list_fields = ("offer_portfolio", "capabilities", "propositions", "partners", "competitors",
                       "credentials", "constraints", "target_sectors", "excluded_offerings")
        data = {name: tuple(str(item) for item in value.get(name, ()) if str(item).strip()) for name in list_fields}
        data.update(organisation=str(value.get("organisation") or ""), description=str(value.get("description") or ""),
                    authority_status=str(value.get("authority_status") or "human-supplied"))
        statuses = value.get("field_statuses") if isinstance(value.get("field_statuses"), dict) else {}
        data["field_statuses"] = {name: str(statuses.get(name) or ("human-supplied" if data.get(name) else "unresolved"))
                                  for name in ("organisation", "description", *list_fields)}
        return cls(**data)


def resolve_employer_context(headers: Any) -> EmployerContext | None:
    """Resolve supplier-side configuration independently of mission and Twin stores."""
    user_id = authenticated_flora_user(headers)
    if not user_id:
        return None
    path = Path(os.getenv("FLORA_EMPLOYER_CONTEXTS_FILE", str(DEFAULT_EMPLOYER_CONFIG)))
    try:
        profiles = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    value = profiles.get(user_id)
    return EmployerContext.from_dict(value) if isinstance(value, dict) else None


def save_employer_context(headers: Any, value: dict[str, Any]) -> EmployerContext:
    """Atomically save explicitly supplied employer context in its own profile store."""
    user_id = authenticated_flora_user(headers)
    if not user_id:
        raise PermissionError("An authenticated Flora user is required")
    context = EmployerContext.from_dict(value)
    if not context.organisation:
        raise ValueError("Employer organisation is required")
    path = Path(os.getenv("FLORA_EMPLOYER_CONTEXTS_FILE", str(DEFAULT_EMPLOYER_CONFIG)))
    try:
        profiles = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        profiles = {}
    if not isinstance(profiles, dict):
        raise ValueError("Employer Context profile store must be an object")
    profiles[user_id] = {name: list(getattr(context, name)) for name in (
        "offer_portfolio", "capabilities", "propositions", "partners", "competitors", "credentials",
        "constraints", "target_sectors", "excluded_offerings")}
    profiles[user_id].update(organisation=context.organisation, description=context.description,
                             authority_status=context.authority_status, field_statuses=context.field_statuses)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(profiles, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)
    return context
