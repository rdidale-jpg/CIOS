from __future__ import annotations
from typing import Any, Protocol
class ReasoningAdapter(Protocol):
    model_name: str; instruction_version: str
    def execute(self, task: str, context: dict[str, Any], output_schema: type) -> Any: ...
class DeterministicDevelopmentAdapter:
    model_name='deterministic-development-rules'; instruction_version='flora-banking-vslice-001'
    def execute(self, task: str, context: dict[str, Any], output_schema: type) -> Any:
        return context
