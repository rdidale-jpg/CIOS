"""Durable Enterprise Canvas access records for Blueprint-created canvases."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from cios.applications.flora.access import active_flora_workspace, authenticated_flora_user, can_access_enterprise, canonical_enterprise_id
from cios.applications.flora.blueprint_import.ledger import utc_now
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.storage import atomic_write_json, data_path


@dataclass(frozen=True)
class EnterpriseCanvasAccessRecord:
    schema_version: str
    canvas_id: str
    enterprise_id: str
    workspace_id: str
    owner_account: str
    import_run_ids: tuple[str, ...] = ()
    workspace_members: tuple[str, ...] = ()
    enterprise_members: tuple[str, ...] = ()
    acl: tuple[dict[str, str], ...] = field(default_factory=tuple)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("import_run_ids", "workspace_members", "enterprise_members"):
            data[key] = list(data[key])
        data["acl"] = [dict(item) for item in self.acl]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnterpriseCanvasAccessRecord":
        return cls(
            schema_version=str(data.get("schema_version") or "1.0"),
            canvas_id=str(data["canvas_id"]),
            enterprise_id=str(data["enterprise_id"]),
            workspace_id=str(data.get("workspace_id") or ""),
            owner_account=str(data.get("owner_account") or ""),
            import_run_ids=tuple(data.get("import_run_ids") or ()),
            workspace_members=tuple(data.get("workspace_members") or ()),
            enterprise_members=tuple(data.get("enterprise_members") or ()),
            acl=tuple(dict(item) for item in data.get("acl") or ()),
            created_at=str(data.get("created_at") or ""),
            updated_at=str(data.get("updated_at") or ""),
        )


class EnterpriseCanvasAccessRepository:
    def __init__(self):
        self.path = data_path("enterprise_canvas", "access.json")

    def list(self) -> list[EnterpriseCanvasAccessRecord]:
        if not self.path.exists():
            return []
        return [EnterpriseCanvasAccessRecord.from_dict(item) for item in json.loads(self.path.read_text(encoding="utf-8") or "[]")]

    def get(self, enterprise_id: str) -> EnterpriseCanvasAccessRecord | None:
        wanted = canonical_enterprise_id(enterprise_id)
        return next((r for r in self.list() if canonical_enterprise_id(r.enterprise_id) == wanted), None)

    def save(self, record: EnterpriseCanvasAccessRecord) -> EnterpriseCanvasAccessRecord:
        records = self.list()
        wanted = canonical_enterprise_id(record.enterprise_id)
        replaced = False
        out = []
        for existing in records:
            if canonical_enterprise_id(existing.enterprise_id) == wanted:
                out.append(record); replaced = True
            else:
                out.append(existing)
        if not replaced:
            out.append(record)
        atomic_write_json(self.path, {"records": [r.to_dict() for r in out]})
        return record


def _read_records(repo: EnterpriseCanvasAccessRepository) -> list[EnterpriseCanvasAccessRecord]:
    if not repo.path.exists():
        return []
    raw = json.loads(repo.path.read_text(encoding="utf-8") or "{}")
    rows = raw.get("records", raw if isinstance(raw, list) else [])
    return [EnterpriseCanvasAccessRecord.from_dict(item) for item in rows]

EnterpriseCanvasAccessRepository.list = _read_records  # preserve list compatibility after envelope migration


def repair_blueprint_canvas_access(import_run_id: str, headers: Any, repo: EnterpriseCanvasAccessRepository | None = None) -> EnterpriseCanvasAccessRecord | None:
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    if not package:
        return None
    owner = authenticated_flora_user(headers) or package.received_by
    workspace = package.workspace_id or active_flora_workspace(headers)
    return repair_enterprise_canvas_access(package.identity.enterprise_id, workspace, owner, import_run_id, repo)


def repair_enterprise_canvas_access(enterprise_id: str, workspace_id: str, owner_account: str, import_run_id: str = "", repo: EnterpriseCanvasAccessRepository | None = None) -> EnterpriseCanvasAccessRecord:
    repo = repo or EnterpriseCanvasAccessRepository()
    existing = repo.get(enterprise_id)
    now = utc_now()
    canvas_id = existing.canvas_id if existing else f"canvas-{canonical_enterprise_id(enterprise_id)}"
    imports = tuple(dict.fromkeys((existing.import_run_ids if existing else ()) + ((import_run_id,) if import_run_id else ())))
    workspace_members = tuple(dict.fromkeys((existing.workspace_members if existing else ()) + ((owner_account,) if owner_account else ())))
    enterprise_members = tuple(dict.fromkeys((existing.enterprise_members if existing else ()) + ((owner_account,) if owner_account else ())))
    acl_by_principal = {item.get("principal_id", ""): dict(item) for item in (existing.acl if existing else ())}
    if owner_account:
        acl_by_principal[owner_account] = {"principal_id": owner_account, "role": "owner", "grant_source": "blueprint_promotion_owner"}
    return repo.save(EnterpriseCanvasAccessRecord("1.0", canvas_id, enterprise_id, workspace_id or (existing.workspace_id if existing else ""), owner_account or (existing.owner_account if existing else ""), imports, workspace_members, enterprise_members, tuple(acl_by_principal.values()), existing.created_at if existing else now, now))


def can_access_canvas_record(headers: Any, enterprise_id: str, workspace_id: str = "") -> bool:
    user = authenticated_flora_user(headers)
    if not user:
        return False
    record = EnterpriseCanvasAccessRepository().get(enterprise_id)
    effective_workspace = workspace_id or (record.workspace_id if record else "")
    if not can_access_enterprise(headers, enterprise_id, effective_workspace):
        return False
    if not record:
        return True
    principals = {item.get("principal_id") for item in record.acl}
    return user in principals or user in record.enterprise_members or user in record.workspace_members
