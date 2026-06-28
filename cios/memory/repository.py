"""Passive memory repository interfaces and in-memory implementation.

Sprint 7E introduces storage adapter contracts for memory records while keeping
memory passive. Repositories save and retrieve records only; they must not call
reasoning, scoring, decision engines, agents, applications, LLMs, databases,
external services, or persistence frameworks.
"""

from __future__ import annotations

from typing import Protocol

from cios.memory.models import MemoryRecord


class MemoryRepository(Protocol):
    """Protocol for passive memory record storage adapters."""

    def save(self, record: MemoryRecord) -> MemoryRecord:
        """Store a memory record and return the stored record."""

    def get(self, record_id: str) -> MemoryRecord | None:
        """Return a memory record by ID, or None when it is unknown."""

    def list(self) -> list[MemoryRecord]:
        """Return all stored memory records."""

    def find_by_record_type(self, record_type: str) -> list[MemoryRecord]:
        """Return stored memory records with the requested record type."""


class InMemoryRepository:
    """Simple process-local repository for passive memory records.

    This implementation is intentionally ephemeral and exists only as a safe
    foundation for future adapters. It does not perform file persistence,
    database access, network calls, orchestration, scoring, or decisions.
    """

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}

    def save(self, record: MemoryRecord) -> MemoryRecord:
        """Store a memory record by its ID and return the same record."""

        self._records[record.id] = record
        return record

    def get(self, record_id: str) -> MemoryRecord | None:
        """Return a memory record by ID, or None when it is unknown."""

        return self._records.get(record_id)

    def list(self) -> list[MemoryRecord]:
        """Return all stored memory records in insertion order."""

        return list(self._records.values())

    def find_by_record_type(self, record_type: str) -> list[MemoryRecord]:
        """Return stored records whose record_type exactly matches record_type."""

        return [record for record in self._records.values() if record.record_type == record_type]
