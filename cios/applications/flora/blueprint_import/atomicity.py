"""Observation atomicity diagnostics and deterministic split helpers."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .archive import sha256_bytes

SEMICOLON_OR_COLON = re.compile(r"[;:]")
MULTI_FACT = re.compile(r"\b(and|while|but|because|therefore)\b", re.I)
SPECULATIVE = re.compile(r"\b(may|might|could|possibly|probably|likely|appears to|suggests|indicates|uncertain|contradicts|contradiction)\b", re.I)
RECOMMEND = re.compile(r"\b(should|recommend|recommended|next action|must engage|proposal|pitch|sell|pursue)\b", re.I)
BEFORE_AFTER = re.compile(r"\b(before|after|prior state|current state|from .+ to )\b", re.I)

@dataclass(frozen=True)
class AtomicityFinding:
    atomic: bool
    reason: str = ""
    deterministic_split_available: bool = False


def normalise_statement(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def validate_atomic_statement(statement: Any) -> AtomicityFinding:
    text = normalise_statement(statement)
    if not text:
        return AtomicityFinding(False, "missing atomic statement", False)
    if SPECULATIVE.search(text):
        return AtomicityFinding(False, "uncertainty or contradiction language belongs outside canonical Observation statements", False)
    if RECOMMEND.search(text):
        return AtomicityFinding(False, "recommendation language belongs outside canonical Observation statements", False)
    if BEFORE_AFTER.search(text):
        return AtomicityFinding(False, "before/after state is bundled into one statement", False)
    if SEMICOLON_OR_COLON.search(text):
        return AtomicityFinding(False, "semicolon- or colon-separated assertions are not atomic", _can_split(text))
    if MULTI_FACT.search(text) and len(re.findall(r"\b[A-Z][A-Za-z0-9-]+\b", text)) > 1:
        return AtomicityFinding(False, "multiple independent claims joined by conjunction or causal language", _can_split(text))
    return AtomicityFinding(True)


def _can_split(text: str) -> bool:
    return bool(split_atomic_statements(text))


def split_atomic_statements(statement: Any) -> tuple[str, ...]:
    text = normalise_statement(statement)
    if not text:
        return ()
    if SPECULATIVE.search(text) or RECOMMEND.search(text) or BEFORE_AFTER.search(text):
        return ()
    # Only split explicit assertion delimiters. Do not split causal/conjunction prose.
    if ";" not in text:
        return ()
    parts = [normalise_statement(p) for p in text.split(";")]
    parts = [p if p.endswith(".") else p + "." for p in parts if p]
    if len(parts) < 2:
        return ()
    return tuple(parts) if all(validate_atomic_statement(p).atomic for p in parts) else ()


def child_observation_id(parent_id: str, index: int, statement: str) -> str:
    return f"{parent_id}-CHILD-{index:02d}-{sha256_bytes(statement.encode())[:8].upper()}"
