"""Registry-backed architecture profile compiler.

This module implements the first AP-001/AP-002 compiler: a deterministic,
read-only compiler that turns the Architecture Authority Registry into an
inspectable profile record. It packages metadata only; it never mutates source
architecture or production export manifests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Iterable
import zipfile

COMPILER_VERSION = "0.1.0"
REGISTRY_PATH = Path("architecture/reference-architecture/Architecture-Authority-Registry.md")
ARCHITECTURE_VERSION = "CIOS Architecture v2.0"
SUPPORTED_PROFILES = {"architecture-authority", "researcher-pack", "reviewer-pack", "review-context"}
ACCEPTED_STATUS = "Accepted"
DETERMINISTIC_ZIP_TIMESTAMP = (2026, 7, 12, 0, 0, 0)

STANDALONE_RESEARCHER_DOCUMENT_IDS = (
    "AP-001",
    "AP-002",
    "RP-001",
    "DD-001",
    "RA-001",
    "EI-001",
    "EI-012",
    "EI-002",
    "EI-003",
    "FP-009",
    "GL-001",
)

ADR_RUNTIME_PACKS = (
    ("ADR Foundation Pack", ("ADR-001", "ADR-002", "ADR-003")),
    ("ADR Governance Pack", ("ADR-004", "ADR-005", "ADR-009")),
    ("ADR Evidence Acquisition Pack", ("ADR-010",)),
    ("ADR Financial Intelligence Pack", ("ADR-011",)),
    ("ADR Blueprint and Canvas Pack", ("ADR-012", "ADR-013")),
    ("ADR Reasoning and Exchange Pack", ("ADR-014", "ADR-016")),
)


@dataclass(frozen=True)
class RuntimeUploadFile:
    """One deterministic upload file for a compiled runtime package."""

    name: str
    content: str
    source_paths: tuple[str, ...]
    generated: bool = False


@dataclass(frozen=True)
class ResearcherRuntimePackage:
    """Compiled Researcher GPT runtime upload package."""

    upload_files: tuple[RuntimeUploadFile, ...]
    source_profile: ProfileCompilation

    @property
    def upload_file_count(self) -> int:
        return len(self.upload_files)

    def to_zip_bytes(self) -> bytes:
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for upload_file in sorted(self.upload_files, key=lambda file: file.name):
                info = zipfile.ZipInfo(upload_file.name, DETERMINISTIC_ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, upload_file.content.encode("utf-8"))
        return buffer.getvalue()

    def validate_zip(self) -> bool:
        zip_bytes = self.to_zip_bytes()
        expected_names = sorted(file.name for file in self.upload_files)
        with zipfile.ZipFile(BytesIO(zip_bytes), "r") as archive:
            return archive.testzip() is None and sorted(archive.namelist()) == expected_names


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


def compile_researcher_runtime_package(root: str | Path = ".") -> ResearcherRuntimePackage:
    """Compile the Researcher GPT runtime package into exactly 17 upload files.

    The canonical architecture documents remain unchanged. The eleven non-ADR
    authorities are emitted standalone, while accepted ADRs in the Researcher
    profile are copied into six generated compilation artefacts that retain each
    ADR's ID, title, status and source path.
    """

    root_path = Path(root)
    profile = compile_architecture_profile("researcher-pack", root_path)
    by_id = {document.document_id: document for document in profile.included_documents}

    upload_files: list[RuntimeUploadFile] = []
    for document_id in STANDALONE_RESEARCHER_DOCUMENT_IDS:
        document = by_id[document_id]
        content = (root_path / document.path).read_text(encoding="utf-8")
        upload_files.append(
            RuntimeUploadFile(
                name=Path(document.path).name,
                content=content,
                source_paths=(document.path,),
            )
        )

    for pack_title, adr_ids in ADR_RUNTIME_PACKS:
        documents = tuple(by_id[adr_id] for adr_id in adr_ids)
        upload_files.append(_compile_adr_pack(pack_title, documents, root_path))

    return ResearcherRuntimePackage(upload_files=tuple(upload_files), source_profile=profile)


def _compile_adr_pack(pack_title: str, documents: tuple[RegistryDocument, ...], root: Path) -> RuntimeUploadFile:
    slug = pack_title.replace(" — ", "-").replace(" ", "-")
    lines = [
        f"# {pack_title}",
        "",
        "**Document class:** Generated Researcher GPT runtime artefact",
        "**Canonical status:** Not canonical architecture; compiled from canonical ADR source documents",
        "**Compilation rule:** Preserves each ADR verbatim below its traceability heading",
        "",
        "## Source traceability",
        "",
        "| ADR ID | Title | Status | Canonical source |",
        "| --- | --- | --- | --- |",
    ]
    for document in documents:
        lines.append(f"| {document.document_id} | {document.title} | {document.status} | `{document.path}` |")
    lines.extend(["", "## Compiled ADR content", ""])

    for document in documents:
        source_text = (root / document.path).read_text(encoding="utf-8").rstrip()
        lines.extend(
            [
                f"## {document.document_id} — {document.title}",
                "",
                f"**Original ADR ID:** {document.document_id}",
                f"**Original title:** {document.title}",
                f"**Original status:** {document.status}",
                f"**Canonical source:** `{document.path}`",
                "",
                source_text,
                "",
            ]
        )

    return RuntimeUploadFile(
        name=f"{slug}.md",
        content="\n".join(lines).rstrip() + "\n",
        source_paths=tuple(document.path for document in documents),
        generated=True,
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
