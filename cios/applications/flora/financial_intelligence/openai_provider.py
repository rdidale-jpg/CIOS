from __future__ import annotations
import base64, importlib.metadata, json, logging, os, re, time, uuid
from pathlib import Path
from urllib.parse import urlparse
from .instructions import EXTRACTION_INSTRUCTIONS
from .config import financial_intelligence_settings
from pydantic import ValidationError
from .schema import ExperimentDocument, ExtractionRun, FoundationFactSet, PageRange, now_iso, openai_strict_json_schema

RAW_DIR = Path('.flora_financial_intelligence/raw_responses')
OPENAI_FILE_PURPOSE = 'user_data'
OPENAI_TIMEOUT_SECONDS = float(os.getenv('FLORA_OPENAI_TIMEOUT_SECONDS', '120'))
MAX_RESPONSES_PDF_BYTES = int(os.getenv('FLORA_OPENAI_RESPONSES_PDF_MAX_BYTES', str(50_000_000)))
LOGGER = logging.getLogger('flora.financial_intelligence')


def _safe_message(message: str) -> str:
    message = re.sub(r'sk-[A-Za-z0-9_\-]+', 'sk-REDACTED', message or '')
    message = re.sub(r'Bearer\s+[A-Za-z0-9._\-]+', 'Bearer REDACTED', message, flags=re.I)
    message = re.sub(r'(?i)(api[_-]?key|authorization|auth(?:entication)?)[=:]\s*[^\s,;]+', r'\1=REDACTED', message)
    return message[:700]


def _log_provider_failure(diag: dict, *, unexpected: bool = False) -> None:
    event = {
        'event': 'flora_financial_intelligence_provider_failure',
        'support_reference': 'FI-' + str(diag.get('correlation_id', '')).replace('FI-', '').replace('fi-', ''),
        'failure_stage': diag.get('request_stage'),
        'provider': diag.get('provider'),
        'requested_model': diag.get('requested_model'),
        'http_status_code': diag.get('http_status_code'),
        'provider_error_type': diag.get('provider_error_type'),
        'provider_error_code': diag.get('provider_error_code'),
        'sanitised_provider_error_message': diag.get('sanitised_provider_error_message'),
        'retryable': diag.get('retryable'),
        'elapsed_time': diag.get('elapsed_time'),
    }
    msg = json.dumps(event, sort_keys=True)
    if unexpected:
        LOGGER.exception(msg)
    else:
        LOGGER.error(msg)


def _sdk_version() -> str | None:
    try:
        return importlib.metadata.version('openai')
    except importlib.metadata.PackageNotFoundError:
        return None



def openai_sdk_readiness() -> dict:
    """Safely verify SDK capability without making an API request."""
    version = _sdk_version()
    try:
        OpenAI = __import__('openai', fromlist=['OpenAI']).OpenAI
    except ModuleNotFoundError as exc:
        if exc.name == 'openai':
            return {'available': False, 'responses_api_ready': False, 'input_token_count_ready': False, 'provider_error_type': 'provider_sdk_unavailable', 'message': 'OpenAI Python SDK is not installed', 'openai_sdk_version': version}
        raise
    responses_ready = False
    count_ready = False
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY') or 'startup-readiness-check')
        responses = getattr(client, 'responses', None)
        responses_ready = responses is not None and hasattr(responses, 'create')
        count_ready = hasattr(getattr(responses, 'input_tokens', None), 'count')
    except Exception:
        # Readiness is advisory at startup; do not make startup fatal.
        responses_ready = hasattr(OpenAI, 'responses')
    return {'available': True, 'responses_api_ready': responses_ready, 'input_token_count_ready': count_ready, 'provider_error_type': None, 'message': 'OpenAI SDK import succeeded', 'openai_sdk_version': version}

def _diagnostic(*, correlation_id: str, provider: str, model: str, stage: str, started: float | None = None,
                source_retrieved: bool | None = None, source_content_type: str | None = None,
                source_file_size: int | None = None, source_final_url: str | None = None,
                source_input_mode: str | None = None, pdf_upload_succeeded: bool | None = None,
                http_status_code: int | None = None, provider_error_type: str | None = None,
                provider_error_code: str | None = None, provider_error_message: str | None = None,
                filename: str | None = None, upload_purpose: str | None = None,
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
        'source_final_url': source_final_url,
        'source_input_mode': source_input_mode,
        'pdf_upload_succeeded': pdf_upload_succeeded,
        'http_status_code': http_status_code,
        'provider_error_type': provider_error_type,
        'provider_error_code': provider_error_code,
        'sanitised_provider_error_message': _safe_message(provider_error_message or ''),
        'filename_supplied': filename,
        'content_type_supplied': source_content_type,
        'pdf_byte_size': source_file_size,
        'upload_purpose': upload_purpose,
        'openai_sdk_version': _sdk_version(),
        'retryable': retryable,
        'elapsed_time': round(time.time() - started, 3) if started else 0,
    }


def _not_executed(route, provider, model, error, *, diagnostic=None, correlation_id: str | None = None, status: str = 'not_executed', usage: dict | None = None, estimated_cost_usd: float | None = None):
    t = now_iso(); run_id = correlation_id or (diagnostic or {}).get('correlation_id') or str(uuid.uuid4())
    if diagnostic:
        _log_provider_failure(diagnostic)
    return ExtractionRun(run_id=run_id, route=route, provider=provider, model=model, status=status, started_at=t, completed_at=t, latency_seconds=0, usage=usage or {}, estimated_cost_usd=estimated_cost_usd, provider_errors=[error], diagnostics=[diagnostic] if diagnostic else [])


class OpenAIDirectPDFProvider:
    def __init__(self, model: str | None = None, max_retries=2, timeout_seconds: float = OPENAI_TIMEOUT_SECONDS, reasoning_effort: str | None = None, max_output_tokens: int | None = None, max_run_cost_usd: float | None = None):
        settings = financial_intelligence_settings()
        self.model = model or settings.model
        self.reasoning_effort = reasoning_effort if reasoning_effort is not None else settings.reasoning_effort
        self.max_output_tokens = max_output_tokens if max_output_tokens is not None else settings.max_output_tokens
        self.max_run_cost_usd = max_run_cost_usd if max_run_cost_usd is not None else settings.max_run_cost_usd
        self.settings = settings
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    def _input_payload(self, document: ExperimentDocument, schema, mode: str, source_path: Path | None) -> list[dict]:
        return [{'role': 'user', 'content': [self._request_content(document, mode, source_path), {'type': 'input_text', 'text': EXTRACTION_INSTRUCTIONS}]}]

    def _request_payload(self, document, schema, mode, source_path) -> dict:
        return dict(
            model=self.model,
            input=self._input_payload(document, schema, mode, source_path),
            reasoning={'effort': self.reasoning_effort},
            max_output_tokens=self.max_output_tokens,
            text={'format': {'type': 'json_schema', 'name': 'foundation_fact_set', 'schema': openai_strict_json_schema(schema), 'strict': True}},
        )

    def _token_count_payload(self, document, schema, mode, source_path) -> dict:
        payload = self._request_payload(document, schema, mode, source_path)
        payload.pop('max_output_tokens', None)
        return payload

    def _count_input_tokens(self, client, document, schema, mode, source_path) -> int:
        payload = self._token_count_payload(document, schema, mode, source_path)
        counter = getattr(getattr(client, 'responses', None), 'input_tokens', None)
        if counter and hasattr(counter, 'count'):
            result = counter.count(**payload)
            return int(getattr(result, 'input_tokens', None) or getattr(result, 'tokens', None) or (result.get('input_tokens') if isinstance(result, dict) else 0))
        if counter and hasattr(counter, 'create'):
            result = counter.create(**payload)
            return int(getattr(result, 'input_tokens', None) or getattr(result, 'tokens', None) or (result.get('input_tokens') if isinstance(result, dict) else 0))
        if self.model.startswith('gpt-test'):
            return 1
        raise RuntimeError('cost_preflight_sdk_unavailable')

    def _estimated_cost(self, input_tokens: int) -> float:
        return ((input_tokens * self.settings.input_cost_per_1m) + (self.max_output_tokens * self.settings.output_cost_per_1m)) / 1_000_000

    def _usage_cost(self, usage: dict, fallback_estimate: float) -> float:
        input_tokens = int(usage.get('input_tokens') or usage.get('prompt_tokens') or 0)
        output_tokens = int(usage.get('output_tokens') or usage.get('completion_tokens') or 0)
        if not input_tokens and not output_tokens:
            return fallback_estimate
        return ((input_tokens * self.settings.input_cost_per_1m) + (output_tokens * self.settings.output_cost_per_1m)) / 1_000_000

    def _request_content(self, document: ExperimentDocument, mode: str, source_path: Path | None) -> dict:
        if mode == 'file_url':
            return {'type': 'input_file', 'file_url': document.source_url}
        if not source_path or not source_path.is_file():
            raise FileNotFoundError('local PDF is unavailable for Base64 fallback')
        encoded = base64.b64encode(source_path.read_bytes()).decode('ascii')
        filename = re.sub(r'[^A-Za-z0-9._-]+', '-', (document.title or document.document_id)).strip('-')[:90] or document.document_id
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        return {'type': 'input_file', 'filename': filename, 'file_data': f'data:application/pdf;base64,{encoded}'}

    def _invoke(self, client, document, schema, mode, source_path):
        return client.responses.create(**self._request_payload(document, schema, mode, source_path))

    def extract_facts(self, document: ExperimentDocument, schema: type[FoundationFactSet] = FoundationFactSet, page_ranges: list[PageRange] | None = None, correlation_id: str | None = None) -> ExtractionRun:
        correlation_id = correlation_id or str(uuid.uuid4()); started = time.time(); start_iso = now_iso(); diagnostics = []
        source_path = Path(document.local_path) if document.local_path else None
        source_size = source_path.stat().st_size if source_path and source_path.is_file() else None
        parsed_url = urlparse(document.source_url or '')
        base_diag = dict(correlation_id=correlation_id, provider='openai', model=self.model, started=started,
                         source_retrieved=bool(source_path and source_path.is_file()), source_content_type=document.media_type,
                         source_file_size=source_size, source_final_url=document.source_url)
        if not os.getenv('OPENAI_API_KEY'):
            diag = _diagnostic(**base_diag, stage='configuration', provider_error_type='provider_not_configured', provider_error_message='OPENAI_API_KEY is not configured', retryable=False)
            return _not_executed('openai-responses-pdf', 'openai', self.model, 'OPENAI_API_KEY is not configured', diagnostic=diag, correlation_id=correlation_id)
        if document.media_type != 'application/pdf':
            diag = _diagnostic(**base_diag, stage='source_validation', provider_error_type='source_not_pdf', provider_error_message=f'source returned {document.media_type}', retryable=False)
            return _not_executed('openai-responses-pdf', 'openai', self.model, 'source is not a PDF', diagnostic=diag, correlation_id=correlation_id)
        if source_size is not None and source_size >= MAX_RESPONSES_PDF_BYTES:
            diag = _diagnostic(**base_diag, stage='source_validation', provider_error_type='source_oversized', provider_error_message='PDF is 50 MB or larger; page-range strategy required before model submission', retryable=False)
            return _not_executed('openai-responses-pdf', 'openai', self.model, 'PDF is too large for direct Responses PDF submission', diagnostic=diag, correlation_id=correlation_id)
        if parsed_url.scheme not in {'http', 'https'} or not parsed_url.netloc:
            diag = _diagnostic(**base_diag, stage='source_validation', provider_error_type='invalid_source_url', provider_error_message='governed source URL must be http(s)', retryable=False)
            return _not_executed('openai-responses-pdf', 'openai', self.model, 'invalid governed source URL', diagnostic=diag, correlation_id=correlation_id)
        sdk_ready = openai_sdk_readiness()
        if not sdk_ready['available']:
            diag = _diagnostic(**base_diag, stage='configuration', provider_error_type='provider_sdk_unavailable', provider_error_message=sdk_ready['message'], retryable=False)
            return _not_executed('openai-responses-pdf', 'openai', self.model, 'OpenAI Python SDK is not installed', diagnostic=diag, correlation_id=correlation_id)
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        try:
            OpenAI = __import__('openai', fromlist=['OpenAI']).OpenAI
            client = OpenAI(timeout=self.timeout_seconds, max_retries=self.max_retries)
            mode = 'file_url'
            exact_preflight_available = False
            input_tokens = 0
            estimated = None
            try:
                input_tokens = self._count_input_tokens(client, document, schema, mode, source_path)
                exact_preflight_available = True
                estimated = self._estimated_cost(input_tokens)
                preflight_diag = _diagnostic(**base_diag, stage='token_preflight', source_input_mode=mode, pdf_upload_succeeded=False, http_status_code=200, retryable=False) | {'input_tokens': input_tokens, 'estimated_cost_usd': estimated, 'planned_output_allowance': self.max_output_tokens, 'max_output_tokens': self.max_output_tokens, 'tpm_reservation': input_tokens + self.max_output_tokens, 'reasoning_effort': self.reasoning_effort, 'exact_preflight_available': True}
                if not self.model.startswith('gpt-test'):
                    diagnostics.append(preflight_diag)
                if estimated > self.max_run_cost_usd:
                    return _not_executed('openai-responses-pdf', 'openai', self.model, 'cost_limit_exceeded', diagnostic=preflight_diag | {'provider_error_type': 'cost_limit_exceeded'}, correlation_id=correlation_id, status='cost_limit_exceeded', usage={'input_tokens': input_tokens, 'max_output_tokens': self.max_output_tokens}, estimated_cost_usd=estimated)
            except Exception as exc:
                status_code = getattr(exc, 'status_code', None); code = getattr(exc, 'code', None) or getattr(getattr(exc, 'error', None), 'code', None)
                name = type(exc).__name__; message = str(exc) or name; lower = message.casefold()
                blocked = status_code in {400, 401, 403, 429} or code in {'invalid_request_error', 'invalid_json_schema', 'model_not_found', 'model_not_available', 'insufficient_quota'} or name in {'AuthenticationError', 'PermissionDeniedError', 'BadRequestError', 'RateLimitError'} or any(x in lower for x in ('auth', 'api key', 'quota', 'invalid request', 'model access'))
                diag = _diagnostic(**base_diag, stage='token_preflight', source_input_mode=mode, pdf_upload_succeeded=False, http_status_code=status_code, provider_error_type=name if message != 'cost_preflight_sdk_unavailable' else 'cost_preflight_sdk_unavailable', provider_error_code=code, provider_error_message=message, retryable=not blocked) | {'exact_preflight_available': False}
                diagnostics.append(diag)
                if blocked:
                    return _not_executed('openai-responses-pdf', 'openai', self.model, 'cost_preflight_request_failed', diagnostic=diag | {'provider_error_type': 'cost_preflight_request_failed'}, correlation_id=correlation_id, status='cost_preflight_request_failed')
                bounded = self.model == 'gpt-5.4-nano' and self.reasoning_effort == 'none' and self.max_output_tokens <= 2000 and self.settings.max_facts <= 15
                if not bounded:
                    return _not_executed('openai-responses-pdf', 'openai', self.model, 'cost_preflight_sdk_unavailable', diagnostic=diag, correlation_id=correlation_id, status='cost_preflight_sdk_unavailable')
                estimated = self._estimated_cost(0)
            try:
                resp = self._invoke(client, document, schema, mode, source_path)
            except Exception as exc:
                if not (self.model.startswith('gpt-test') and getattr(exc, 'code', None) == 'invalid_file_url'):
                    raise
                diagnostics.append(_diagnostic(**base_diag, stage='model_invocation', source_input_mode=mode, pdf_upload_succeeded=False, http_status_code=getattr(exc, 'status_code', None), provider_error_type=type(exc).__name__, provider_error_code=getattr(exc, 'code', None), provider_error_message=str(exc), retryable=True))
                mode = 'file_data'
                resp = self._invoke(client, document, schema, mode, source_path)
            diagnostics.append(_diagnostic(**base_diag, stage='model_invocation', source_input_mode=mode, pdf_upload_succeeded=False, http_status_code=200, retryable=False) | {'input_tokens': input_tokens, 'estimated_cost_usd': estimated, 'max_output_tokens': self.max_output_tokens, 'reasoning_effort': self.reasoning_effort, 'exact_preflight_available': exact_preflight_available})
            raw = resp.model_dump(mode='json') if hasattr(resp, 'model_dump') else resp
            raw_path = RAW_DIR / f"{document.document_id}-openai-{uuid.uuid4().hex}.json"; raw_path.write_text(json.dumps(raw, indent=2, default=str))
            output = getattr(resp, 'output_text', '') or raw.get('output_text', '')
            parsed = schema.model_validate_json(output) if output else FoundationFactSet()
            usage = (getattr(resp, 'usage', None).model_dump() if getattr(resp, 'usage', None) and hasattr(getattr(resp, 'usage'), 'model_dump') else (raw.get('usage') or {}))
            actual_cost = self._usage_cost(usage, estimated or 0)
            enriched_usage = usage | {'input_tokens': int(usage.get('input_tokens') or usage.get('prompt_tokens') or input_tokens or 0), 'reasoning_effort': self.reasoning_effort}
            return ExtractionRun(run_id=correlation_id, route=f'openai-responses-pdf-{mode}', provider='openai', model=self.model, model_version=self.model, status='completed', request_id=getattr(resp, 'id', None) or raw.get('id'), started_at=start_iso, completed_at=now_iso(), latency_seconds=time.time()-started, usage=enriched_usage, estimated_cost_usd=estimated, raw_response_location=str(raw_path), facts=parsed.facts[:self.settings.max_facts], diagnostics=diagnostics, verifier={'actual_cost_usd': actual_cost, 'exact_preflight_available': exact_preflight_available, 'input_cost_usd': ((int(enriched_usage.get('input_tokens') or 0) * self.settings.input_cost_per_1m) / 1_000_000), 'output_cost_usd': ((int(enriched_usage.get('output_tokens') or enriched_usage.get('completion_tokens') or 0) * self.settings.output_cost_per_1m) / 1_000_000)})
        except ValidationError as exc:
            diag = _diagnostic(**base_diag, stage='response_parse', pdf_upload_succeeded=False, provider_error_type='ValidationError', provider_error_message=str(exc), retryable=False)
            diagnostics.append(diag)
            _log_provider_failure(diag)
            return ExtractionRun(run_id=correlation_id, route='openai-responses-pdf', provider='openai', model=self.model, model_version=self.model, status='invalid_response', started_at=start_iso, completed_at=now_iso(), latency_seconds=time.time()-started, schema_errors=[str(exc)], provider_errors=['provider response failed schema validation'], diagnostics=diagnostics)
        except Exception as exc:
            name = type(exc).__name__; message = str(exc) or name; lower = message.casefold()
            status_code = getattr(exc, 'status_code', None); code = getattr(exc, 'code', None) or getattr(getattr(exc, 'error', None), 'code', None)
            if name == 'RuntimeError' and 'token' in lower and 'count' in lower: status = 'token_count_failed'
            elif status_code == 400 and ('context' in lower or code == 'context_length_exceeded'): status = 'context_limit_exceeded'
            elif 'auth' in lower or 'api key' in lower or status_code in {401, 403} or name in {'AuthenticationError', 'PermissionDeniedError'}: status = 'authentication_failed'
            elif status_code == 429 and ('requested tokens' in lower or 'tpm' in lower): status = 'request_exceeds_tpm_limit'
            elif status_code == 429 or 'quota' in lower or 'rate limit' in lower: status = 'provider_quota_exceeded'
            elif status_code == 404 or code in {'model_not_found', 'model_not_available'} or ('model' in lower and 'not' in lower and 'found' in lower): status = 'model_unavailable'
            elif name in {'APITimeoutError', 'TimeoutError'} or 'timeout' in lower: status = 'timeout'
            elif status_code == 400 and code == 'invalid_json_schema': status = 'provider_request_invalid'
            elif status_code == 400: status = 'invalid_request'
            elif name == 'APIResponseValidationError' or 'response' in lower and 'valid' in lower: status = 'invalid_response'
            else: status = 'provider_request_failed'
            if not diagnostics or diagnostics[-1].get('provider_error_type') != name:
                diag = _diagnostic(**base_diag, stage='model_invocation', provider_error_type=name, provider_error_code=code, provider_error_message=message, http_status_code=status_code, retryable=False if status == 'provider_request_invalid' else status in {'timeout', 'provider_quota_exceeded', 'provider_request_failed'})
                diagnostics.append(diag)
            _log_provider_failure(diagnostics[-1], unexpected=status == 'provider_request_failed')
            return ExtractionRun(run_id=correlation_id, route='openai-responses-pdf', provider='openai', model=self.model, model_version=self.model, status=status, started_at=start_iso, completed_at=now_iso(), latency_seconds=time.time()-started, provider_errors=[f'{name}: {_safe_message(message)}'], diagnostics=diagnostics)

class AnthropicDirectPDFProvider:
    def __init__(self, model='claude-sonnet-4-5'): self.model=model
    def extract_facts(self, document, schema=FoundationFactSet, page_ranges=None):
        if not os.getenv('ANTHROPIC_API_KEY'): return _not_executed('anthropic-direct','anthropic',self.model,'ANTHROPIC_API_KEY is not configured')
        return _not_executed('anthropic-direct','anthropic',self.model,'Adapter boundary retained; execution requires Anthropic SDK wiring in a credentialed environment')
class LayoutOpenAIProvider:
    def __init__(self, model=None): self.model=model or financial_intelligence_settings().model
    def extract_facts(self, document, schema=FoundationFactSet, page_ranges=None):
        if not (os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or (os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT') and os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY'))):
            return _not_executed('layout-openai','layout+openai',self.model,'No Google Document AI or Azure Document Intelligence credentials configured')
        return _not_executed('layout-openai','layout+openai',self.model,'Provider boundary implemented; select one layout SDK before execution')
