"""Explicit offline research collection; never edits Twins, pipeline or authority.

Default: audit the current overlay. --collect downloads unreviewed originals to
new private scratch storage. HTTP success is not evidence/claim acceptance.
Requires approved publisher access in the workspace network policy.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from urllib.request import Request

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cios.applications.flora.research_intelligence.model import load_assessment, freshness

ALLOWED={'www.lloydsbankinggroup.com','www.lloydsbank.com','www.bankofengland.co.uk','www.fca.org.uk','www.gov.uk'}
LIMIT=16*1024*1024


class Text(HTMLParser):
    def __init__(self):
        super().__init__();self.hidden=0;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in {'script','style'}:self.hidden+=1
    def handle_endtag(self,tag):
        if tag in {'script','style'}:self.hidden=max(0,self.hidden-1)
    def handle_data(self,text):
        if not self.hidden and text.strip():self.parts.append(text.strip())


def fetch(source, directory):
    url=source['url'];target=urlsplit(url)
    if target.scheme!='https' or target.hostname not in ALLOWED or target.username or target.password:
        raise ValueError('Only reviewed public-publisher HTTPS URLs are supported')
    # Redirects are checked before following them, not only after receipt.
    from urllib.request import HTTPRedirectHandler, build_opener
    class Redirect(HTTPRedirectHandler):
        def redirect_request(self,request,fp,code,msg,headers,new_url):
            redirected=urlsplit(new_url)
            if redirected.scheme!='https' or redirected.hostname not in ALLOWED:
                raise ValueError('Unapproved redirect destination')
            return super().redirect_request(request,fp,code,msg,headers,new_url)
    opener=build_opener(Redirect())
    with opener.open(Request(url,headers={'User-Agent':'FLORA-Research/1.0 (public-source research)'}),timeout=30) as response:
        content=response.read(LIMIT+1)
        if len(content)>LIMIT:raise ValueError('Source exceeds bounded collection size')
        final=response.geturl();kind=response.headers.get_content_type()
    if content.startswith(b'%PDF'):
        import fitz
        with fitz.open(stream=content,filetype='pdf') as document:
            text='\n'.join(page.get_text() for page in document)
        extension='.pdf'
    elif kind in {'text/html','application/xhtml+xml','text/plain'}:
        decoded=content.decode('utf-8',errors='replace')
        if kind=='text/plain':text=decoded
        else:
            parser=Text();parser.feed(decoded);text='\n'.join(parser.parts)
        extension='.html' if kind!='text/plain' else '.txt'
    else:raise ValueError('Unsupported primary source content type')
    stem=source['id']
    if not re.fullmatch(r'[A-Z0-9-]+',stem):raise ValueError('Unsafe source identity')
    (directory/(stem+extension)).write_bytes(content)
    (directory/(stem+'.text.txt')).write_text(text)
    return dict(source_id=stem,requested_url=url,retrieval_url=final,
                retrieved_at=datetime.now(timezone.utc).isoformat(),publication_date=None,
                primary_content_sha256=hashlib.sha256(content).hexdigest(),
                text_sha256=hashlib.sha256(text.encode()).hexdigest(),reporting_period=source['reporting_period'],
                retrieval_status='downloaded_unreviewed',claim_verification='NOT_ASSESSED',
                instruction='Review the original, publication date, entity/period and exact quotation. Do not import a landing page as proof of claims in a linked PDF. No canonical or commercial acceptance is automatic.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();data=load_assessment()
    if not args.collect:
        print(json.dumps({'status':data['research_status'],'freshness':freshness(data),'claims':len(data['claims']),'candidates':len(data['candidates']),'canonical_mutation':False},indent=2));return 0
    if args.output is None:parser.error('--collect requires a new scratch --output directory')
    from cios.applications.flora.storage import data_root
    directory=args.output.resolve()
    if directory.exists() or directory.is_relative_to(data_root().resolve()) or directory.is_relative_to(Path('/var/data')):
        parser.error('Use a new scratch directory outside application/production data storage')
    directory.mkdir(mode=0o700,parents=True)
    results=[]
    for source in data['sources']:
        try:results.append(fetch(source,directory))
        except Exception as exc:
            results.append({'source_id':source['id'],'requested_url':source['url'],'retrieval_status':'failed',
                            'error_type':type(exc).__name__,'claim_verification':'NOT_ASSESSED'})
    (directory/'collection-manifest.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'downloaded_unreviewed':sum(r['retrieval_status']=='downloaded_unreviewed' for r in results),
                      'failed':sum(r['retrieval_status']=='failed' for r in results),'canonical_mutation':False,'automatic_qualification':False}))
    return 1 if any(r['retrieval_status']=='failed' for r in results) else 0


if __name__=='__main__':raise SystemExit(main())
