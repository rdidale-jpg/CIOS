"""Bounded approved-source acquisition, reusing FLORA's HTML/PDF extractor.

Existing live.documents fetches write to the tenant document cache and are not
called here. No raw response is persisted; only a reviewed public excerpt returns.
"""
from datetime import datetime,timezone
import hashlib,re
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlsplit
from ...source_import import extract
from .runtime import network_allowed

HOSTS=frozenset(('www.gov.uk','assets.publishing.service.gov.uk','www.gca.gov.uk','ec.europa.eu','find-and-update.company-information.service.gov.uk'))

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise PermissionError('Source redirect requires explicit registry review')

class ApprovedRetriever:
    def __init__(self,registry):
        self.registry=registry;self.calls=0
    def __call__(self,source_id,role,nonce):
        if self.calls>=12:raise ValueError('Twelve retrieval cap reached')
        if role not in ('researcher','verifier','challenger') or source_id not in self.registry:raise ValueError('Unknown approved research source/role')
        source=self.registry[source_id];u=urlsplit(source['url'])
        if u.scheme!='https' or u.hostname not in HOSTS or u.username or u.password or u.query or u.fragment or u.port not in (None,443):raise ValueError('Source registry URL not approved')
        if source['rights'].get('acquisition')!='allowed' or source['rights'].get('retention')!='allowed':raise PermissionError('Acquisition/selected-excerpt rights unresolved')
        if not network_allowed(u.hostname):raise PermissionError('Official source egress not allowlisted')
        self.calls+=1
        request=Request(source['url'],headers={'User-Agent':'FLORA-Research-Verification/1.0','Accept':'text/html,application/pdf,text/plain','Cache-Control':'no-cache'})
        with build_opener(NoRedirect()).open(request,timeout=15) as response:
            if response.geturl()!=source['url']:raise PermissionError('Unreviewed final source URL')
            kind=response.headers.get('Content-Type','').split(';')[0];raw=response.read(4000001)
            if len(raw)>4000000:raise ValueError('Source byte cap exceeded')
        if kind=='application/pdf':
            import fitz
            with fitz.open(stream=raw,filetype='pdf') as doc:
                if len(doc)>40:raise ValueError('PDF page cap exceeded')
            suffix='.pdf'
        elif kind in ('text/html','application/xhtml+xml'):suffix='.html'
        elif kind=='text/plain':suffix='.txt'
        else:raise ValueError('Unexpected official source MIME type')
        text=extract(raw,suffix);normal=lambda x:re.sub(r'\s+',' ',x).strip()
        fields=source.get('match_fragments',source['text'].split('\n'))
        if not all(normal(f) in normal(text) for f in fields):raise ValueError('Reviewed source passage changed or is not present')
        return {**source,'request_id':nonce,'role':role,'collector_id':'runtime-'+role,'tool_reference':'HTTP-'+nonce,
                'retrieved_at':datetime.now(timezone.utc).isoformat(),'transport_sha256':hashlib.sha256(raw).hexdigest(),
                'sha256':hashlib.sha256(source['text'].encode()).hexdigest(),'visibility':'public_non_personal','raw_response_retained':False}
