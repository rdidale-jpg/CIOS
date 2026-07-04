from __future__ import annotations
import json, os, re, time, uuid
from pathlib import Path
from .instructions import EXTRACTION_INSTRUCTIONS
from pydantic import ValidationError
from .schema import ExperimentDocument, ExtractionRun, FoundationFactSet, PageRange, now_iso

RAW_DIR = Path('.document_understanding/raw_responses')
OPENAI_FILE_PURPOSE = 'user_data'
OPENAI_TIMEOUT_SECONDS = float(os.getenv('FLORA_OPENAI_TIMEOUT_SECONDS', '120'))


def _safe_message(message: str) -> str:
    message = re.sub(r'sk-[A-Za-z0-9_\-]+', 'sk-REDACTED', message or '')
    message = re.sub(r'Bearer\s+[A-Za-z0-9._\-]+', 'Bearer REDACTED', message, flags=re.I)
    return message[:700]


def _diagnostic(*, correlation_id: str, provider: str, model: str, stage: str, started: float | None = None,
                source_retrieved: bool | None = None, source_content_type: str | None = None,
                source_file_size: int | None = None, pdf_upload_succeeded: bool | None = None,
                http_status_code: int | None = None, provider_error_type: str | None = None,
                provider_error_code: str | None = None, provider_error_message: str | None = None,
                retryable: bool | None = None) -> dict:
    return {
        'correlation_id': correlation_id,
        'timestamp': now_iso(),
        'provider': provider,
        'requested_model': model,
        'request_stage': stage,
        'source_document_retrieval_result': source_retrieved,
        'source_content_type': source_content_type,
        'source_file_size': source_file_size,
        'pdf_upload_succeeded': pdf_upload_succeeded,
        'http_status_code': http_status_code,
        'provider_error_type': provider_error_type,
        'provider_error_code': provider_error_code,
        'sanitised_provider_error_message': _safe_message(provider_error_message or ''),
        'retryable': retryable,
        'elapsed_time': round(time.time() - started, 3) if started else 0,
    }


def _not_executed(route, provider, model, error, *, diagnostic=None):
    t = now_iso()
    return ExtractionRun(run_id=str(uuid.uuid4()), route=route, provider=provider, model=model, status='not_executed', started_at=t, completed_at=t, latency_seconds=0, provider_errors=[error], diagnostics=[diagnostic] if diagnostic else [])


class OpenAIDirectPDFProvider:
    def __init__(self, model='gpt-5.5', max_retries=2, timeout_seconds: float = OPENAI_TIMEOUT_SECONDS):
        self.model = model
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    def extract_facts(self, document: ExperimentDocument, schema: type[FoundationFactSet] = FoundationFactSet, page_ranges: list[PageRange] | None = None) -> ExtractionRun:
        correlation_id = str(uuid.uuid4())
        started = time.time()
        source_path = Path(document.local_path) if document.local_path else None
        source_size = source_path.stat().st_size if source_path and source_path.is_file() else None
        base_diag = dict(correlation_id=correlation_id, provider='openai', model=self.model, started=started,
                         source_retrieved=bool(source_path and source_path.is_file()), source_content_type=document.media_type,
                         source_file_size=source_size)
        if not os.getenv('OPENAI_API_KEY'):
            diag = _diagnostic(**base_diag, stage='configuration', provider_error_type='provider_not_configured', provider_error_message='OPENAI_API_KEY is not configured', retryable=False)
            return _not_executed('openai-direct', 'openai', self.model, 'OPENAI_API_KEY is not configured', diagnostic=diag)
        if not source_path or not source_path.is_file():
            diag = _diagnostic(**base_diag, stage='source_validation', provider_error_type='source_unavailable', provider_error_message='local PDF is unavailable', retryable=True)
            return _not_executed('openai-direct', 'openai', self.model, 'local PDF is unavailable', diagnostic=diag)
        start_iso = now_iso(); RAW_DIR.mkdir(parents=True, exist_ok=True); diagnostics = []
        uploaded_file = None
        try:
            from openai import OpenAI
            client = OpenAI(timeout=self.timeout_seconds, max_retries=self.max_retries)
            with source_path.open('rb') as pdf:
                uploaded_file = client.files.create(file=pdf, purpose=OPENAI_FILE_PURPOSE)
            diagnostics.append(_diagnostic(**base_diag, stage='file_upload', pdf_upload_succeeded=True))
            resp = client.responses.create(
                model=self.model,
                input=[{'role': 'user', 'content': [
                    {'type': 'input_file', 'file_id': uploaded_file.id},
                    {'type': 'input_text', 'text': EXTRACTION_INSTRUCTIONS},
                ]}],
                text={'format': {'type': 'json_schema', 'name': 'foundation_fact_set', 'schema': schema.model_json_schema(), 'strict': True}},
            )
            diagnostics.append(_diagnostic(**base_diag, stage='model_invocation', pdf_upload_succeeded=True, http_status_code=200, retryable=False))
            raw = resp.model_dump(mode='json') if hasattr(resp, 'model_dump') else resp
            raw_path = RAW_DIR / f"{document.document_id}-openai-{uuid.uuid4().hex}.json"; raw_path.write_text(json.dumps(raw, indent=2, default=str))
            output = getattr(resp, 'output_text', '') or raw.get('output_text', '')
            parsed = schema.model_validate_json(output) if output else FoundationFactSet()
            usage = (getattr(resp, 'usage', None).model_dump() if getattr(resp, 'usage', None) and hasattr(getattr(resp, 'usage'), 'model_dump') else (raw.get('usage') or {}))
            return ExtractionRun(run_id=correlation_id, route='openai-direct', provider='openai', model=self.model, model_version=self.model, status='completed', request_id=getattr(resp, 'id', None) or raw.get('id'), started_at=start_iso, completed_at=now_iso(), latency_seconds=time.time()-started, usage=usage, raw_response_location=str(raw_path), facts=parsed.facts, diagnostics=diagnostics)
        except ValidationError as exc:
            diagnostics.append(_diagnostic(**base_diag, stage='response_parse', pdf_upload_succeeded=bool(uploaded_file), provider_error_type='ValidationError', provider_error_message=str(exc), retryable=False))
            return ExtractionRun(run_id=correlation_id, route='openai-direct', provider='openai', model=self.model, model_version=self.model, status='invalid_response', started_at=start_iso, completed_at=now_iso(), latency_seconds=time.time()-started, schema_errors=[str(exc)], provider_errors=['provider response failed schema validation'], diagnostics=diagnostics)
        except Exception as exc:
            name = type(exc).__name__; message = str(exc) or name; lower = message.casefold()
            status_code = getattr(exc, 'status_code', None); code = getattr(exc, 'code', None) or getattr(getattr(exc, 'error', None), 'code', None)
            if 'auth' in lower or 'api key' in lower or status_code in {401, 403} or name in {'AuthenticationError', 'PermissionDeniedError'}: status = 'authentication_failed'
            elif status_code == 429 or 'quota' in lower or 'rate limit' in lower: status = 'quota_exceeded'
            elif status_code == 404 or code in {'model_not_found', 'model_not_available'} or 'model' in lower and 'not' in lower and 'found' in lower: status = 'model_unavailable'
            elif name in {'APITimeoutError', 'TimeoutError'} or 'timeout' in lower: status = 'timeout'
            elif not uploaded_file: status = 'file_upload_failed'
            elif status_code == 400: status = 'invalid_request'
            else: status = 'failed'
            diagnostics.append(_diagnostic(**base_diag, stage='file_upload' if not uploaded_file else 'model_invocation', pdf_upload_succeeded=bool(uploaded_file), http_status_code=status_code, provider_error_type=name, provider_error_code=code, provider_error_message=message, retryable=status in {'timeout','quota_exceeded'} or (status_code and status_code >= 500)))
            return ExtractionRun(run_id=correlation_id, route='openai-direct', provider='openai', model=self.model, model_version=self.model, status=status, started_at=start_iso, completed_at=now_iso(), latency_seconds=time.time()-started, provider_errors=[f'{name}: {_safe_message(message)}'], diagnostics=diagnostics)
class AnthropicDirectPDFProvider:
    def __init__(self, model='claude-sonnet-4-5'): self.model=model
    def extract_facts(self, document, schema=FoundationFactSet, page_ranges=None):
        if not os.getenv('ANTHROPIC_API_KEY'): return _not_executed('anthropic-direct','anthropic',self.model,'ANTHROPIC_API_KEY is not configured')
        return _not_executed('anthropic-direct','anthropic',self.model,'Adapter boundary retained; execution requires Anthropic SDK wiring in a credentialed environment')
class LayoutOpenAIProvider:
    def __init__(self, model='gpt-5.5'): self.model=model
    def extract_facts(self, document, schema=FoundationFactSet, page_ranges=None):
        if not (os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or (os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT') and os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY'))):
            return _not_executed('layout-openai','layout+openai',self.model,'No Google Document AI or Azure Document Intelligence credentials configured')
        return _not_executed('layout-openai','layout+openai',self.model,'Provider boundary implemented; select one layout SDK before execution')
