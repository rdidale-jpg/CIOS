"""Runtime provider-call guard for governed Financial Intelligence modes."""
from __future__ import annotations

import inspect
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Iterator


class ProviderCallViolation(RuntimeError):
    """Raised before an LLM provider request is transmitted in a zero-call mode."""


@dataclass
class ProviderCallGuard:
    mode: str
    allowed_calls: int = 0
    attempted_calls: int = 0
    violations: list[dict] = field(default_factory=list)

    def before_provider_call(self, provider: str, call_path: str) -> None:
        self.attempted_calls += 1
        if self.attempted_calls > self.allowed_calls:
            frame = next((f for f in inspect.stack()[1:] if 'provider_guard.py' not in f.filename), None)
            location = f"{frame.filename}:{frame.lineno}" if frame else call_path
            event = {"failure_category": "deterministic_route_provider_violation", "provider": provider, "call_path": call_path, "stack_location": location}
            self.violations.append(event)
            raise ProviderCallViolation("deterministic_route_provider_violation")

_CURRENT_GUARD: ContextVar[ProviderCallGuard | None] = ContextVar("flora_provider_call_guard", default=None)

@contextmanager
def provider_call_guard(mode: str, allowed_calls: int = 0) -> Iterator[ProviderCallGuard]:
    guard = ProviderCallGuard(mode=mode, allowed_calls=allowed_calls)
    token = _CURRENT_GUARD.set(guard)
    try:
        yield guard
    finally:
        _CURRENT_GUARD.reset(token)

def enforce_provider_call_allowed(provider: str, call_path: str) -> None:
    guard = _CURRENT_GUARD.get()
    if guard is not None:
        guard.before_provider_call(provider, call_path)
