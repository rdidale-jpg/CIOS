from __future__ import annotations
import json, os, time, urllib.request
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
    def __init__(self, reason='No enterprise intelligence LLM provider configured'): self.reason=reason
    def generate_structured(self, **kw): raise LLMProviderError(self.reason)

class StaticJSONProvider(LLMProvider):
    provider_name='static-json'
    def __init__(self, payload: dict[str,Any]|None=None, model='static-test'): self.payload=payload or {}; self.model=model
    def generate_structured(self, *, prompt, schema, timeout_s, token_budget):
        start=time.time()
        missing=[k for k in schema.get('required', []) if k not in self.payload]
        if missing: raise LLMProviderError('Structured output missing required fields: '+', '.join(missing))
        return LLMResult(self.payload, self.provider_name, self.model, {'prompt_tokens':len(prompt)//4,'completion_tokens':len(json.dumps(self.payload))//4}, int((time.time()-start)*1000))

class OpenAIResponsesProvider(LLMProvider):
    provider_name='openai'
    def __init__(self, api_key: str, model: str): self.api_key=api_key; self.model=model
    def generate_structured(self, *, prompt, schema, timeout_s, token_budget):
        start=time.time()
        body={'model':self.model,'input':prompt,'max_output_tokens':int(os.getenv('FLORA_REASONING_MAX_OUTPUT_TOKENS','2000')),'text':{'format':{'type':'json_schema','name':schema.get('name','ExecutiveCommercialBriefV1'),'schema':{'type':'object','additionalProperties':True, **{k:v for k,v in schema.items() if k in {'required'}}},'strict':True}}}
        req=urllib.request.Request('https://api.openai.com/v1/responses', data=json.dumps(body).encode(), headers={'Authorization':'Bearer '+self.api_key,'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp: data=json.loads(resp.read().decode())
        except Exception as exc:
            raise LLMProviderError(f'provider call failed: {type(exc).__name__}: {exc}') from exc
        text=data.get('output_text')
        if not text:
            parts=[]
            for out in data.get('output',[]) or []:
                for c in out.get('content',[]) or []:
                    if c.get('type') in {'output_text','text'}: parts.append(c.get('text',''))
            text=''.join(parts)
        try: payload=json.loads(text)
        except Exception as exc: raise LLMProviderError('provider did not return structured JSON') from exc
        return LLMResult(payload, self.provider_name, self.model, data.get('usage') or {}, int((time.time()-start)*1000))

def provider_diagnostics() -> dict[str,Any]:
    provider=os.getenv('FLORA_REASONING_PROVIDER') or os.getenv('FLORA_ENTERPRISE_INTELLIGENCE_PROVIDER') or ''
    model=os.getenv('FLORA_REASONING_MODEL') or os.getenv('FLORA_ENTERPRISE_INTELLIGENCE_MODEL') or ''
    key=bool(os.getenv('FLORA_REASONING_API_KEY') or os.getenv('OPENAI_API_KEY'))
    return {'provider':provider or 'not configured','model':model or 'not configured','api_key_available':key,'timeout_seconds':os.getenv('FLORA_REASONING_TIMEOUT_SECONDS','30'),'max_input_tokens':os.getenv('FLORA_REASONING_MAX_INPUT_TOKENS','24000'),'max_output_tokens':os.getenv('FLORA_REASONING_MAX_OUTPUT_TOKENS','2000')}

def provider_from_env() -> LLMProvider:
    if os.environ.get('FLORA_ENTERPRISE_INTELLIGENCE_STATIC_JSON'):
        return StaticJSONProvider(json.loads(os.environ['FLORA_ENTERPRISE_INTELLIGENCE_STATIC_JSON']), os.getenv('FLORA_REASONING_MODEL','static-test'))
    provider=(os.getenv('FLORA_REASONING_PROVIDER') or '').lower(); model=os.getenv('FLORA_REASONING_MODEL') or ''
    if not provider: return UnavailableProvider('FLORA_REASONING_PROVIDER is not configured')
    if not model: return UnavailableProvider('FLORA_REASONING_MODEL is not configured')
    key=os.getenv('FLORA_REASONING_API_KEY') or (os.getenv('OPENAI_API_KEY') if provider=='openai' else '')
    if not key: return UnavailableProvider('FLORA_REASONING_API_KEY is not configured')
    if provider=='openai': return OpenAIResponsesProvider(key, model)
    return UnavailableProvider(f'Unsupported FLORA_REASONING_PROVIDER {provider!r}')
