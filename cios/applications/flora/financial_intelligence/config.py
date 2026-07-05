from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_TESTING_MODEL = 'gpt-5.4-nano'
DEFAULT_REASONING_EFFORT = 'none'
DEFAULT_MAX_OUTPUT_TOKENS = 4000
DEFAULT_MAX_RUN_COST_USD = 0.25
DEFAULT_MAX_FACTS = 15
PROMPT_VERSION = 'financial-material-facts-v1'
EXTRACTION_SCHEMA_VERSION = 'foundation-fact-set-v1'

# Conservative per-token prices. Override with env vars when provider pricing changes.
DEFAULT_INPUT_COST_PER_1M = 0.05
DEFAULT_OUTPUT_COST_PER_1M = 0.40

@dataclass(frozen=True)
class FinancialIntelligenceSettings:
    model: str = DEFAULT_TESTING_MODEL
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    max_run_cost_usd: float = DEFAULT_MAX_RUN_COST_USD
    max_facts: int = DEFAULT_MAX_FACTS
    input_cost_per_1m: float = DEFAULT_INPUT_COST_PER_1M
    output_cost_per_1m: float = DEFAULT_OUTPUT_COST_PER_1M
    prompt_version: str = PROMPT_VERSION
    schema_version: str = EXTRACTION_SCHEMA_VERSION


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def financial_intelligence_settings() -> FinancialIntelligenceSettings:
    model = os.getenv('FLORA_FINANCIAL_INTELLIGENCE_MODEL') or os.getenv('FLORA_DOCUMENT_UNDERSTANDING_MODEL') or DEFAULT_TESTING_MODEL
    return FinancialIntelligenceSettings(
        model=model,
        reasoning_effort=os.getenv('FLORA_FINANCIAL_INTELLIGENCE_REASONING', DEFAULT_REASONING_EFFORT),
        max_output_tokens=_int_env('FLORA_FINANCIAL_INTELLIGENCE_MAX_OUTPUT_TOKENS', DEFAULT_MAX_OUTPUT_TOKENS),
        max_run_cost_usd=_float_env('FLORA_FINANCIAL_INTELLIGENCE_MAX_RUN_COST_USD', DEFAULT_MAX_RUN_COST_USD),
        max_facts=_int_env('FLORA_FINANCIAL_INTELLIGENCE_MAX_FACTS', DEFAULT_MAX_FACTS),
        input_cost_per_1m=_float_env('FLORA_FINANCIAL_INTELLIGENCE_INPUT_COST_PER_1M', DEFAULT_INPUT_COST_PER_1M),
        output_cost_per_1m=_float_env('FLORA_FINANCIAL_INTELLIGENCE_OUTPUT_COST_PER_1M', DEFAULT_OUTPUT_COST_PER_1M),
    )
