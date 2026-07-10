from __future__ import annotations
import json, os, time
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class LLMResult:
    payload: dict[str,Any]; provider: str; model: str; token_usage: dict[str,int]; duration_ms: int; fallback: bool=False

class LLMProviderError(RuntimeError): pass
class LLMProvider:
    provider_name='abstract'
    def generate_structured(self, *, prompt: str, schema: dict[str,Any], timeout_s: int, token_budget: int) -> LLMResult: raise NotImplementedError

class UnavailableProvider(LLMProvider):
    provider_name='unavailable'
    def generate_structured(self, **kw): raise LLMProviderError('No enterprise intelligence LLM provider configured')

class StaticJSONProvider(LLMProvider):
    provider_name='static-json'
    def __init__(self, payload: dict[str,Any]|None=None): self.payload=payload or {}
    def generate_structured(self, *, prompt, schema, timeout_s, token_budget):
        start=time.time(); return LLMResult(self.payload, self.provider_name, 'static-test', {'prompt_tokens':len(prompt)//4,'completion_tokens':len(json.dumps(self.payload))//4}, int((time.time()-start)*1000))

def provider_from_env() -> LLMProvider:
    if os.environ.get('FLORA_ENTERPRISE_INTELLIGENCE_DISABLE_LLM','').lower() in {'1','true','yes'}: return UnavailableProvider()
    if os.environ.get('FLORA_ENTERPRISE_INTELLIGENCE_STATIC_JSON'):
        return StaticJSONProvider(json.loads(os.environ['FLORA_ENTERPRISE_INTELLIGENCE_STATIC_JSON']))
    return UnavailableProvider()
