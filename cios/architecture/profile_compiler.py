"""Registry-backed architecture profile compiler.

This module implements the first AP-001/AP-002 compiler: a deterministic,
read-only compiler that turns the Architecture Authority Registry into an
inspectable profile record. It packages metadata only; it never mutates source
architecture or production export manifests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

COMPILER_VERSION = "0.1.0"
REGISTRY_PATH = Path("architecture/reference-architecture/Architecture-Authority-Registry.md")
ARCHITECTURE_VERSION = "CIOS Architecture v2.0"
SUPPORTED_PROFILES = {"architecture-authority", "researcher-pack", "reviewer-pack", "review-context"}
ACCEPTED_STATUS = "Accepted"


@dataclass(frozen=True)
class RegistryDocument:
    """Single document authority row parsed from the Architecture Authority Registry."""

    document_id: str
    title: str
    path: str
    status: str
    authority_classification: str
    release_profile_membership: tuple[str, ...]
    dependencies: tuple[str, ...]
    validation_trigger: str

    @property
    def is_accepted(self) -> bool:
        return self.status.casefold() == ACCEPTED_STATUS.casefold()

    @property
    def is_authoritative(self) -> bool:
        classification = self.authority_classification.casefold()
        return self.is_accepted and "not authoritative" not in classification


@dataclass(frozen=True)
class ProfileCompilation:
    """Inspectable result of compiling a named architecture profile."""

    compilation_profile: str
    source_registry_path: str
    registry_last_updated: str | None
    included_documents: tuple[RegistryDocument, ...]
    excluded_documents: tuple[RegistryDocument, ...]
    dependencies: tuple[str, ...]
    outstanding_validation_triggers: tuple[str, ...]
    architecture_version: str = ARCHITECTURE_VERSION
    registry_version: str | None = None
    compiler_version: str = COMPILER_VERSION
    compilation_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    non_promotion_statement: str = "Compilation packages documents only; it does not promote document status."

    def to_dict(self) -> dict[str, object]:
        return {
            "compilation_profile": self.compilation_profile,
            "source_registry_path": self.source_registry_path,
            "registry_last_updated": self.registry_last_updated,
            "included_documents": [_document_to_dict(doc) for doc in self.included_documents],
            "excluded_documents": [_document_to_dict(doc) for doc in self.excluded_documents],
            "dependencies": list(self.dependencies),
            "outstanding_validation_triggers": list(self.outstanding_validation_triggers),
            "non_promotion_statement": self.non_promotion_statement,
            "architecture_version": self.architecture_version,
            "registry_version": self.registry_version,
            "compiler_version": self.compiler_version,
            "compilation_timestamp": self.compilation_timestamp,
        }


def compile_architecture_profile(profile: str, root: str | Path = ".") -> ProfileCompilation:
    """Compile a named architecture profile from the Authority Registry.

    The registry is the control plane. Production profiles include only accepted,
    authoritative rows with explicit registry membership. ``review-context`` is a
    bounded review compilation and can include non-accepted rows while preserving
    their registry status in the output.
    """

    if profile not in SUPPORTED_PROFILES:
        supported = ", ".join(sorted(SUPPORTED_PROFILES))
        raise ValueError(f"Unsupported architecture profile {profile!r}; expected one of: {supported}")

    root_path = Path(root)
    registry_path = root_path / REGISTRY_PATH
    registry_text = registry_path.read_text(encoding="utf-8")
    documents = parse_authority_registry(registry_text)

    included = tuple(doc for doc in documents if _include_document(doc, profile))
    excluded = tuple(doc for doc in documents if doc not in included)
    dependencies = _unique(dep for doc in included for dep in doc.dependencies if dep)
    outstanding = _unique(
        f"{doc.document_id}: {doc.validation_trigger}"
        for doc in included
        if doc.validation_trigger and doc.validation_trigger.strip().lower() not in {"none", "n/a"}
    )

    return ProfileCompilation(
        compilation_profile=profile,
        source_registry_path=REGISTRY_PATH.as_posix(),
        registry_last_updated=_metadata_value(registry_text, "Last updated"),
        registry_version=_metadata_value(registry_text, "Last updated"),
        included_documents=included,
        excluded_documents=excluded,
        dependencies=dependencies,
        outstanding_validation_triggers=outstanding,
    )


def parse_authority_registry(text: str) -> tuple[RegistryDocument, ...]:
    rows: list[RegistryDocument] = []
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "| ID | Title | Path |" in line:
            continue
        cells = [_clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8 or cells[0] in {"Profile", "Status"}:
            continue
        doc_id, title, path, status, authority, membership, dependencies, trigger = cells
        if not doc_id or path == "Meaning":
            continue
        rows.append(
            RegistryDocument(
                document_id=doc_id,
                title=title,
                path=path.strip("`"),
                status=status,
                authority_classification=authority,
                release_profile_membership=_parse_profiles(membership),
                dependencies=tuple(part.strip() for part in dependencies.split(";") if part.strip()),
                validation_trigger=trigger,
            )
        )
    return tuple(rows)


def _include_document(doc: RegistryDocument, profile: str) -> bool:
    if profile == "review-context":
        return doc.status in {"Review", "Proposed"} or "review-context" in doc.release_profile_membership
    return profile in doc.release_profile_membership and doc.is_authoritative


def _parse_profiles(value: str) -> tuple[str, ...]:
    found = [profile for profile in (*SUPPORTED_PROFILES, "none") if profile in value]
    return tuple(dict.fromkeys(found))


def _clean_cell(value: str) -> str:
    return " ".join(value.replace("<br>", "; ").strip().split())


def _metadata_value(text: str, label: str) -> str | None:
    prefix = f"**{label}:**"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return None


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _document_to_dict(doc: RegistryDocument) -> dict[str, object]:
    return {
        "id": doc.document_id,
        "title": doc.title,
        "path": doc.path,
        "status": doc.status,
        "authority_classification": doc.authority_classification,
        "release_profile_membership": list(doc.release_profile_membership),
        "dependencies": list(doc.dependencies),
        "validation_trigger": doc.validation_trigger,
    }
