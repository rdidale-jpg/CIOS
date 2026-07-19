from __future__ import annotations
import json, os, time
from typing import Any, Protocol

class ReasoningAdapter(Protocol):
    model_name: str; instruction_version: str; mode_label: str
    def execute(self, task: str, context: dict[str, Any], output_schema: type) -> Any: ...

class DeterministicDevelopmentAdapter:
    model_name='deterministic-development-rules'; instruction_version='flora-banking-semantic-001'; mode_label='Deterministic fallback'
    def execute(self, task: str, context: dict[str, Any], output_schema: type) -> Any:
        return context

class ModelBackedReasoningAdapter:
    """Provider-neutral core boundary for structured semantic tasks.

    The adapter records provider/model metadata but returns only validated JSON-like
    structures to the runtime. If provider dependencies, secrets, timeout or JSON
    validation fail, callers can use the deterministic fallback.
    """
    instruction_version='flora-banking-semantic-001'; mode_label='Model-backed'
    def __init__(self, provider: str='openai', model_name: str|None=None, timeout_s: float|None=None, retry_limit: int|None=None):
        self.provider=provider; self.model_name=model_name or os.getenv('FLORA_REASONING_MODEL','gpt-4.1-mini')
        self.timeout_s=float(timeout_s or os.getenv('FLORA_REASONING_TIMEOUT_SECONDS','20'))
        self.retry_limit=int(retry_limit if retry_limit is not None else os.getenv('FLORA_REASONING_RETRY_LIMIT','1'))
    def execute(self, task: str, context: dict[str, Any], output_schema: type) -> Any:
        permitted=set(context.get('permitted_source_ids') or [])
        prompt={'task':task,'instruction_version':self.instruction_version,'rules':['Return JSON only','Cite only permitted_source_ids','Do not include hidden chain of thought','Convert unsupported claims to Unknown'],'permitted_source_ids':sorted(permitted),'context':context}
        last_error=None
        for _ in range(self.retry_limit+1):
            start=time.time()
            try:
                if self.provider!='openai': raise RuntimeError('unsupported provider')
                import importlib
                client=importlib.import_module('openai').OpenAI(timeout=self.timeout_s)
                resp=client.chat.completions.create(model=self.model_name,response_format={'type':'json_object'},messages=[{'role':'system','content':'You are Flora semantic reasoning. Produce grounded enterprise intelligence as JSON only.'},{'role':'user','content':json.dumps(prompt,default=str)}])
                if time.time()-start > self.timeout_s: raise TimeoutError('reasoning timeout')
                data=json.loads(resp.choices[0].message.content or '{}')
                _reject_unsupported_ids(data, permitted)
                if hasattr(output_schema,'model_validate'): return output_schema.model_validate(data)
                return data
            except Exception as exc: last_error=exc
        raise RuntimeError(f'model reasoning failed safely: {last_error}')

def _reject_unsupported_ids(value: Any, permitted: set[str]) -> None:
    if isinstance(value, dict):
        for k,v in value.items():
            if k.endswith('_ids') or k in {'source_ids','supporting_asset_ids'}:
                for item in v or []:
                    if isinstance(item,str) and item not in permitted: raise ValueError(f'unsupported source id: {item}')
            _reject_unsupported_ids(v, permitted)
    elif isinstance(value, list):
        for v in value: _reject_unsupported_ids(v, permitted)

def configured_reasoning_adapter() -> ReasoningAdapter:
    if os.getenv('FLORA_REASONING_PROVIDER') and os.getenv('OPENAI_API_KEY'):
        return ModelBackedReasoningAdapter(provider=os.getenv('FLORA_REASONING_PROVIDER','openai'))
    return DeterministicDevelopmentAdapter()
