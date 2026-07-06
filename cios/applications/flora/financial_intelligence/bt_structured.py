"""BT FY26 governed ESEF/iXBRL ingestion for Flora's structured route."""
from __future__ import annotations
import hashlib,json,os,re,resource,shutil,tempfile,time,zipfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET
from cios.applications.flora.storage import data_path, atomic_write_json
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.live.source_registry import canonical_enterprise_id

CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "flora" / "structured_sources" / "bt-group-plc-fy26.json"
IX_NS="{http://www.xbrl.org/2013/inlineXBRL}"; XBRLI_NS="{http://www.xbrl.org/2003/instance}"; XBRLDI_NS="{http://xbrl.org/2006/xbrldi}"
class OffHostRedirect(Exception): pass
class StructuredIngestionError(Exception):
    def __init__(self, message: str, code: str = "unexpected_runtime_error", stage: str = "unexpected runtime error"):
        super().__init__(message); self.code=code; self.stage=stage
class _NoOffHostRedirect(HTTPRedirectHandler):
    def __init__(self, approved:set[str]): self.approved=approved
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlparse(newurl).scheme != 'https' or urlparse(newurl).hostname not in self.approved: raise StructuredIngestionError(f'off-host redirect rejected: {newurl}', 'redirect_host_rejected', 'official filing retrieval')
        return super().redirect_request(req, fp, code, msg, headers, newurl)
@dataclass(frozen=True)
class RetrievedPackage:
    path:Path; sha256:str; final_url:str; status_code:int; content_type:str|None; size:int

def source_config()->dict[str,Any]:
    path=Path(os.getenv('FLORA_STRUCTURED_SOURCE_CONFIG') or CONFIG_PATH)
    if not path.exists(): raise StructuredIngestionError(f'structured source configuration missing: {path}', 'source_configuration_missing', 'governed source configuration')
    cfg=json.loads(path.read_text())
    if cfg.get('enterprise_id')!='bt-group-plc': raise StructuredIngestionError('BT governed source not selected for canonical enterprise', 'enterprise_identity_mismatch', 'governed source configuration')
    if cfg.get('source_kind') not in {'official_nsm_esef','official_issuer_esef'} or cfg.get('scope')!='group_consolidated': raise StructuredIngestionError('BT governed structured source not selected', 'source_configuration_not_selected', 'governed source configuration')
    if cfg.get('reporting_period')!='FY26' or cfg.get('period_start')!='2025-04-01' or cfg.get('period_end')!='2026-03-31': raise StructuredIngestionError('BT governed source period does not match FY26', 'reporting_period_mismatch', 'governed source configuration')
    artifact_url = cfg.get('artifact_url')
    if not artifact_url: raise StructuredIngestionError('structured artifact URL missing', 'artifact_url_missing', 'governed source configuration')
    parsed_artifact = urlparse(artifact_url)
    if parsed_artifact.fragment or artifact_url.rstrip('/').lower() in {
        'https://data.fca.org.uk',
        'https://data.fca.org.uk/index.html',
        'https://data.fca.org.uk/#/nsm/nationalstoragemechanism',
    } or parsed_artifact.fragment.lower().startswith('/nsm/'):
        raise StructuredIngestionError('The configured source is a search page rather than a filing download.', 'artifact_url_not_downloadable', 'governed source configuration')
    return cfg
def retrieve_package(cfg:dict[str,Any])->RetrievedPackage:
    url=cfg['artifact_url']; parsed=urlparse(url); approved=set(cfg.get('approved_hosts') or ())
    if parsed.scheme!='https' or parsed.hostname not in approved: raise StructuredIngestionError('artifact URL is not approved HTTPS host', 'host_not_allowed', 'official filing retrieval')
    tmp=Path(tempfile.mkdtemp(prefix='flora-bt-esef-'))/'filing.zip'; opener=build_opener(_NoOffHostRedirect(approved)); last=None
    for _ in range(3):
        h=hashlib.sha256(); size=0
        try:
            with opener.open(Request(url,headers={'User-Agent':'Flora structured financial ingestion/1.0'}),timeout=30) as r, tmp.open('wb') as out:
                content_type = r.headers.get('content-type')
                allowed_types = ('zip', 'octet-stream') if cfg.get('artifact_type', 'zip') == 'zip' else ('xhtml', 'html', 'xml', 'octet-stream')
                if content_type and not any(t in content_type.lower() for t in allowed_types): raise StructuredIngestionError(f'content type rejected: {content_type}', 'content_type_rejected', 'official filing retrieval')
                content_length = int(r.headers.get('content-length') or 0)
                while True:
                    chunk=r.read(1024*1024)
                    if not chunk: break
                    size+=len(chunk)
                    if size>int(cfg['compressed_size_limit_bytes']): raise StructuredIngestionError('compressed package size limit exceeded', 'compressed_package_too_large', 'official filing retrieval')
                    h.update(chunk); out.write(chunk)
                if content_length and size != content_length: raise StructuredIngestionError('download incomplete', 'download_incomplete', 'official filing retrieval')
                return RetrievedPackage(tmp,h.hexdigest(),r.geturl(),getattr(r,'status',200),r.headers.get('content-type'),size)
        except HTTPError as exc:
            code='http_403' if exc.code==403 else ('http_404' if exc.code==404 else 'http_error')
            last=StructuredIngestionError(f'HTTP {exc.code}', code, 'official filing retrieval'); time.sleep(.2)
        except URLError as exc:
            reason=str(getattr(exc,'reason',exc)).lower(); code='http_403' if '403' in reason else ('dns_failure' if 'name or service' in reason or 'nodename' in reason else ('tls_failure' if 'ssl' in reason or 'certificate' in reason else 'http_error'))
            last=StructuredIngestionError(str(exc), code, 'official filing retrieval'); time.sleep(.2)
        except Exception as exc: last=exc; time.sleep(.2)
    
    msg=str(last); code=getattr(last,'code',None) or ('download_timeout' if 'timed out' in msg.lower() else 'http_error')
    raise StructuredIngestionError(f'structured source retrieval failed: {last}', code, 'official filing retrieval')
SAFETY_FAILURE_CODES={
    'invalid_zip','zip_crc_failure','unsafe_archive_path','archive_entry_limit_exceeded',
    'archive_expanded_size_exceeded','archive_entry_too_large','encrypted_archive_unsupported',
    'unsupported_archive_entry_type'
}
PACKAGE_RECOGNITION_FAILURE_CODES={
    'ixbrl_report_not_found','multiple_ixbrl_reports_ambiguous','report_package_manifest_invalid',
    'unsupported_esef_package_layout','taxonomy_entrypoint_not_found','structured_report_locator_failed'
}
TEXT_EXTENSIONS=('.xhtml','.html','.htm','.xml','.xsd','.json','.txt','.csv')
REPORT_EXTENSIONS=('.xhtml','.html','.htm')
INSTANCE_EXTENSIONS=('.xbrl','.xml')
TAXONOMY_EXTENSIONS=('.xsd','.xml')
NESTED_ARCHIVE_EXTENSIONS=('.zip','.jar','.7z','.tar','.gz','.tgz','.bz2','.xz')


def _is_symlink(info:zipfile.ZipInfo)->bool:
    return ((info.external_attr >> 16) & 0o170000) == 0o120000


def _safe_parts(name:str)->tuple[str,...]:
    return Path(name.replace('\\','/')).parts


def _is_directory_entry(info:zipfile.ZipInfo)->bool:
    return info.filename.replace('\\','/').endswith('/') or ((info.external_attr >> 16) & 0o170000) == 0o040000


def _classify_archive_entry(name:str)->str:
    lower=name.replace('\\','/').lower()
    base=lower.rsplit('/',1)[-1]
    if lower.endswith(REPORT_EXTENSIONS): return 'html_container'
    if base == 'catalog.xml' or lower.endswith('/catalog.xml'): return 'catalog_metadata'
    if base in {'taxonomypackage.xml','taxonomy-package.xml'} or lower.endswith('/taxonomypackage.xml') or lower.endswith('/taxonomy-package.xml'): return 'taxonomy_package_metadata'
    if lower.endswith('.xsd'): return 'extension_schema'
    if lower.endswith(('_pre.xml','-pre.xml','_def.xml','-def.xml','_lab.xml','-lab.xml','_lab-en.xml','-lab-en.xml','_cal.xml','-cal.xml')): return 'linkbase'
    if lower.endswith('.xbrl'): return 'xbrl_instance'
    if lower.endswith('.xml'): return 'xml_metadata_or_support'
    return 'other'


def inspect_archive(path:Path,cfg:dict[str,Any])->dict[str,Any]:
    diag={'central_directory_readable':False,'archive_entry_count':0,'file_entry_count':0,
          'directory_entry_count':0,'total_compressed_size':0,
          'total_expanded_size':0,'maximum_single_entry_size':0,'duplicate_entry_names':[],
          'encrypted_entries':[],'absolute_paths':[],'traversal_paths':[],'symlinks':[],
          'unsupported_entry_types':[],'crc_failures':[],'nested_archives':[],
          'first_failing_safety_rule':None,'top_level_directories':[],'top_level_files':[],
          'candidate_xhtml_html':[],'candidate_html_paths':[],'candidate_xml':[],'candidate_xsd_taxonomy':[],
          'candidate_inline_xbrl_reports':[],'candidate_xbrl_instances':[],'standalone_xbrl_instances':[],
          'extension_schemas':[],'linkbases':[],
          'taxonomy_package_metadata':[],'catalog_metadata':[],'report_package_metadata':[],
          'manifest_files':[],'locator_decision':None,'locator_reason':None,
          'inline_xbrl_marker_results':[],'identity_result':None,'period_result':None,
          'selected_report_path':None,'selection_reason':None}
    try:
        with zipfile.ZipFile(path) as z:
            infos=z.infolist(); diag['central_directory_readable']=True; diag['archive_entry_count']=len(infos)
            seen=set(); dups=[]; top_dirs=set(); top_files=set()
            for info in infos:
                name=info.filename; norm=name.replace('\\','/'); is_dir=_is_directory_entry(info)
                if name in seen: dups.append(name)
                seen.add(name)
                parts=_safe_parts(name)
                if parts and parts[0] not in ('/','..') and not parts[0].endswith(':'):
                    if len(parts)==1 and not is_dir: top_files.add(parts[0])
                    else: top_dirs.add(parts[0].rstrip('/'))
                if is_dir: diag['directory_entry_count']+=1
                else: diag['file_entry_count']+=1
                diag['total_compressed_size']+=info.compress_size; diag['total_expanded_size']+=info.file_size
                diag['maximum_single_entry_size']=max(diag['maximum_single_entry_size'], info.file_size)
                lower=norm.lower(); kind=_classify_archive_entry(norm)
                if info.flag_bits & 0x1: diag['encrypted_entries'].append(name)
                if norm.startswith('/') or (len(parts)>0 and (parts[0]=='/' or parts[0].endswith(':'))): diag['absolute_paths'].append(name)
                if '..' in parts: diag['traversal_paths'].append(name)
                if _is_symlink(info): diag['symlinks'].append(name)
                mode=(info.external_attr >> 16) & 0o170000
                if mode and mode not in (0o100000,0o040000,0): diag['unsupported_entry_types'].append(name)
                if lower.endswith(NESTED_ARCHIVE_EXTENSIONS): diag['nested_archives'].append(name)
                if kind == 'html_container': diag['candidate_xhtml_html'].append(name); diag['candidate_html_paths'].append(name)
                if lower.endswith('.xml'): diag['candidate_xml'].append(name)
                if lower.endswith(TAXONOMY_EXTENSIONS): diag['candidate_xsd_taxonomy'].append(name)
                if kind == 'xbrl_instance': diag['candidate_xbrl_instances'].append(name); diag['standalone_xbrl_instances'].append(name)
                if kind == 'extension_schema': diag['extension_schemas'].append(name)
                if kind == 'linkbase': diag['linkbases'].append(name)
                if kind == 'taxonomy_package_metadata': diag['taxonomy_package_metadata'].append(name)
                if kind == 'catalog_metadata': diag['catalog_metadata'].append(name)
                if 'report-package.json' in lower or 'reports.json' in lower or 'manifest' in lower: diag['manifest_files'].append(name)
                if 'report-package' in lower: diag['report_package_metadata'].append(name)
            diag['duplicate_entry_names']=dups; diag['top_level_directories']=sorted(t for t in top_dirs if t); diag['top_level_files']=sorted(top_files)
            first_bad=z.testzip()
            if first_bad: diag['crc_failures'].append(first_bad)
    except zipfile.BadZipFile:
        diag['first_failing_safety_rule']='invalid_zip'; return diag
    checks=[('zip_crc_failure',diag['crc_failures']),('unsafe_archive_path',diag['absolute_paths'] or diag['traversal_paths']),
            ('encrypted_archive_unsupported',diag['encrypted_entries']),('unsupported_entry_type',diag['symlinks'] or diag['unsupported_entry_types'])]
    if diag['archive_entry_count']>int(cfg['entry_count_limit']): diag['first_failing_safety_rule']='archive_entry_limit_exceeded'
    if diag['total_expanded_size']>int(cfg['expanded_size_limit_bytes']): diag['first_failing_safety_rule']=diag['first_failing_safety_rule'] or 'archive_expanded_size_exceeded'
    if diag['maximum_single_entry_size']>int(cfg.get('single_entry_size_limit_bytes') or cfg['expanded_size_limit_bytes']): diag['first_failing_safety_rule']=diag['first_failing_safety_rule'] or 'archive_entry_too_large'
    for code, present in checks:
        if present and not diag['first_failing_safety_rule']: diag['first_failing_safety_rule']='unsupported_archive_entry_type' if code=='unsupported_entry_type' else code
    return diag

def validate_archive(path:Path,cfg:dict[str,Any])->list[zipfile.ZipInfo]:
    diag=inspect_archive(path,cfg)
    if not diag['central_directory_readable']: raise StructuredIngestionError('invalid ZIP package', 'invalid_zip', 'structured package validation')
    if diag['first_failing_safety_rule']:
        messages={'zip_crc_failure':'ZIP CRC validation failed','unsafe_archive_path':'unsafe archive path rejected','encrypted_archive_unsupported':'encrypted archive entries are unsupported','unsupported_archive_entry_type':'unsupported archive entry type rejected','archive_entry_limit_exceeded':'archive entry count limit exceeded','archive_expanded_size_exceeded':'expanded archive size limit exceeded','archive_entry_too_large':'archive entry size limit exceeded'}
        raise StructuredIngestionError(messages.get(diag['first_failing_safety_rule'],'archive safety validation failed'), diag['first_failing_safety_rule'], 'structured package validation')
    with zipfile.ZipFile(path) as z: return z.infolist()


def _read_bounded(z:zipfile.ZipFile, name:str, limit:int=2_000_000)->bytes:
    info=z.getinfo(name)
    if info.file_size>limit: return b''
    return z.read(name)


def _local(tag:Any)->str:
    return str(tag).rsplit('}',1)[-1] if '}' in str(tag) else str(tag)


def _mem_kb()->int|None:
    try: return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except Exception: return None

INLINE_NS_RE=re.compile(br'http://www\.xbrl\.org/2013/inlineXBRL|<\s*([A-Za-z_][\w.-]*:)?(header|nonFraction|nonNumeric)\b', re.I)
CONTEXT_RE=re.compile(br'<\s*([A-Za-z_][\w.-]*:)?context\b|http://www\.xbrl\.org/2003/instance', re.I)
SCHEMA_RE=re.compile(br'<\s*([A-Za-z_][\w.-]*:)?schemaRef\b', re.I)
REF_RE=re.compile(br"(?:href|src)\s*=\s*[\"']([^\"']+\.(?:xhtml|html|htm|xml|xbrl|zip))(?:[#?][^\"']*)?[\"']", re.I)
JSON_REF_RE=re.compile(br"[\"']([^\"']+\.(?:xhtml|html|htm|xml|xbrl|zip))[\"']", re.I)

def _scan_ixbrl_markers(z:zipfile.ZipFile,name:str,chunk_size:int=1024*1024,overlap:int=4096)->dict[str,Any]:
    started=time.perf_counter(); before=_mem_kb(); bytes_scanned=0; chunks=0; tail=b''; markers=set(); error=None; eof=False
    try:
        with z.open(name) as fh:
            while True:
                chunk=fh.read(chunk_size)
                if not chunk: eof=True; break
                chunks+=1; bytes_scanned+=len(chunk); window=tail+chunk
                if INLINE_NS_RE.search(window): markers.add('inline_xbrl_namespace_or_fact')
                if re.search(br'<\s*([A-Za-z_][\w.-]*:)?header\b', window, re.I): markers.add('inline_header')
                if re.search(br'<\s*([A-Za-z_][\w.-]*:)?nonFraction\b', window, re.I): markers.add('tagged_numeric_fact')
                if re.search(br'<\s*([A-Za-z_][\w.-]*:)?nonNumeric\b', window, re.I): markers.add('tagged_non_numeric_fact')
                if CONTEXT_RE.search(window): markers.add('xbrl_context')
                if SCHEMA_RE.search(window): markers.add('schema_ref')
                if b'213800LRO7NS5CYQMN21' in window: markers.add('bt_lei')
                if b'2026-03-31' in window: markers.add('fy26_period_end')
                if b'2025-04-01' in window: markers.add('fy26_period_start')
                upper=window.upper()
                if b'BT GROUP' in upper: markers.add('bt_identity_text')
                tail=window[-overlap:]
    except Exception as exc:
        error=f'{type(exc).__name__}: {exc}'
    return {'path':name,'bytes_scanned':bytes_scanned,'chunks_processed':chunks,'end_of_entry_reached':eof,'recognition_duration_seconds':round(time.perf_counter()-started,6),'markers_found':sorted(markers),'scanner_result':'error' if error else ('inline_xbrl_markers_found' if markers else 'no_markers_found'),'scanner_error':error,'memory_before_kb':before,'memory_after_kb':_mem_kb()}

def _read_text_bounded(z:zipfile.ZipFile, name:str, limit:int=2_000_000)->str:
    data=_read_bounded(z,name,limit)
    return data.decode('utf-8','replace') if data else ''

def _metadata_from_xml(text:str)->dict[str,Any]:
    out={'identifier':None,'name':None,'entry_points':[],'schema_refs':[],'lei':None,'period_start':None,'period_end':None,'company_number':None}
    if not text: return out
    try: root=ET.fromstring(text)
    except Exception: return out
    for el in root.iter():
        local=_local(el.tag); val=' '.join(''.join(el.itertext()).split())
        if local in {'identifier','name'} and not out.get(local) and val: out[local]=val
        if local in {'entryPointDocument','schemaRef'}:
            href=el.attrib.get('href') or el.attrib.get('{http://www.w3.org/1999/xlink}href')
            if href: out['entry_points' if local=='entryPointDocument' else 'schema_refs'].append(href)
        if val == '213800LRO7NS5CYQMN21': out['lei']=val
        if val == '2025-04-01': out['period_start']=val
        if val == '2026-03-31': out['period_end']=val
        if '04190816' in val: out['company_number']='04190816'
    return out

def _viewer_references(z:zipfile.ZipFile, name:str)->dict[str,list[str]]:
    refs=[]; embedded=[]
    try:
        with z.open(name) as fh:
            tail=b''
            while True:
                chunk=fh.read(1024*1024)
                if not chunk: break
                win=tail+chunk
                refs += [m.decode('utf-8','replace') for m in REF_RE.findall(win)]
                embedded += [m.decode('utf-8','replace') for m in JSON_REF_RE.findall(win)]
                tail=win[-4096:]
    except Exception: pass
    def uniq(xs):
        out=[]
        for x in xs:
            if x not in out: out.append(x)
        return out
    return {'external_filing_references':uniq(refs),'embedded_filing_locations':uniq(embedded)}

def classify_structured_package(zip_path:Path,cfg:dict[str,Any])->dict[str,Any]:
    diag=inspect_archive(zip_path,cfg)
    metadata={'catalog':{},'taxonomy_package':{},'extension_schemas':{}}
    embedded=[]; external=[]; package_type='unsupported_official_package'; raw_exists=False; raw_path=None
    with zipfile.ZipFile(zip_path) as z:
        for n in diag.get('catalog_metadata',[]): metadata['catalog'][n]=_metadata_from_xml(_read_text_bounded(z,n))
        for n in diag.get('taxonomy_package_metadata',[]):
            md=_metadata_from_xml(_read_text_bounded(z,n)); metadata['taxonomy_package'].update(md)
        for n in diag.get('extension_schemas',[]): metadata['extension_schemas'][n]=_metadata_from_xml(_read_text_bounded(z,n))
        candidates=[]
        for n in [x for x in z.namelist() if x.lower().endswith(REPORT_EXTENSIONS)]:
            info=_inspect_ixbrl_candidate(z,n,cfg); candidates.append(info)
            refs=_viewer_references(z,n); embedded += refs['embedded_filing_locations']; external += refs['external_filing_references']
        inline=[c for c in candidates if c.get('inline_xbrl')]
        if inline:
            raw_path=inline[0]['path']; raw_exists=True
            package_type='viewer_enhanced_inline_xbrl' if any('viewer' in c['path'].lower() for c in inline) else 'raw_inline_xbrl'
        elif embedded:
            package_type='viewer_with_embedded_filing'; raw_exists=True
        elif external:
            package_type='viewer_referencing_external_filing'
        elif candidates:
            package_type='viewer_only_no_structured_report'
    return {'package_type':package_type,'raw_structured_data_exists_in_package':raw_exists,'raw_report_path':raw_path,'source_authority':cfg.get('source_kind'),'issuer_identity_result':'matched' if cfg.get('lei')=='213800LRO7NS5CYQMN21' and cfg.get('company_number')=='04190816' else 'mismatch','period_result':'matched' if cfg.get('period_end')=='2026-03-31' else 'mismatch','consolidated_scope_result':'matched' if cfg.get('scope')=='group_consolidated' else 'mismatch','adapter_handoff_result':'not_attempted','candidate_fact_count':0,'canonical_fact_count':0,'embedded_filing_locations':sorted(set(embedded)),'external_filing_references':sorted(set(external)),'metadata':metadata,'archive_diagnostics':diag}

def prepare_raw_report_from_package(source:Path, report_path:str, workdir:Path)->Path:
    """Extract a raw report entry from an official package into a temporary workdir.

    The adapter handoff must receive the selected report document, not a renamed
    copy of the whole ZIP package.  If ``report_path`` is absent, ``source`` is
    already treated as the report file and is copied as-is.
    """
    workdir.mkdir(parents=True,exist_ok=True)
    out=workdir / Path(report_path or source.name).name
    if zipfile.is_zipfile(source) and report_path:
        with zipfile.ZipFile(source) as z, z.open(report_path) as src, out.open('wb') as dst:
            shutil.copyfileobj(src,dst,1024*1024)
        return out
    shutil.copyfile(source,out)
    return out

def _copy_zip_entry_to_temp(z:zipfile.ZipFile,name:str,tmpdir:Path)->Path:
    out=tmpdir / Path(name).name
    with z.open(name) as src, out.open('wb') as dst:
        shutil.copyfileobj(src,dst,1024*1024)
    return out

def _inspect_ixbrl_candidate(z:zipfile.ZipFile,name:str,cfg:dict[str,Any])->dict[str,Any]:
    scan=_scan_ixbrl_markers(z,name)
    info={'path':name,'inline_xbrl':False,'markers_found':list(scan['markers_found']),'marker_scan':scan,'lei_match':False,'legal_name_match':False,
          'period_start_match':False,'period_end_match':False,'schema_ref_found':'schema_ref' in scan['markers_found'],
          'required_metric_matches':0,'fact_count':0,'identity_result':'not_evaluated','period_result':'not_evaluated',
          'recognition_classification':'ordinary_html','parse_error':None,'consolidated_scope_match':True,'parent_or_subsidiary_scope':False}
    if scan.get('scanner_error'):
        info['parse_error']=scan['scanner_error']; info['recognition_classification']='ixbrl_marker_scan_failed'; return info
    tmpdir=Path(tempfile.mkdtemp(prefix='flora-bt-ixbrl-scan-'))
    try:
        path=_copy_zip_entry_to_temp(z,name,tmpdir)
        for event, el in ET.iterparse(path, events=('start','end')):
            local=_local(el.tag)
            if event == 'start' and local == 'header':
                if 'inline_header' not in info['markers_found']: info['markers_found'].append('inline_header')
                if 'ix:header' not in info['markers_found']: info['markers_found'].append('ix:header')
            if event == 'start' and local == 'context':
                if 'xbrl_context' not in info['markers_found']: info['markers_found'].append('xbrl_context')
                if 'xbrli:context' not in info['markers_found']: info['markers_found'].append('xbrli:context')
            if event == 'end' and local in {'explicitMember','typedMember'}:
                member=' '.join(''.join(el.itertext()).split()).lower()
                if 'parent' in member or 'subsidiary' in member or 'company' in member:
                    info['parent_or_subsidiary_scope']=True; info['consolidated_scope_match']=False
            if event == 'start' and local == 'schemaRef':
                info['schema_ref_found']=True
                if 'schemaRef' not in info['markers_found']: info['markers_found'].append('schemaRef')
            if event == 'end' and local in {'nonFraction','nonNumeric'}:
                info['fact_count']+=1
                qn=el.attrib.get('name') or ''
                if qn in cfg.get('required_metrics',{}): info['required_metric_matches']+=1
                compat='ix:nonFraction' if local == 'nonFraction' else 'ix:nonNumeric'
                if compat not in info['markers_found']: info['markers_found'].append(compat)
                txt=' '.join(''.join(el.itertext()).split()).upper()
                if cfg.get('legal_name','').upper() in txt or 'BT GROUP PLC' in txt: info['legal_name_match']=True
                el.clear()
            elif event == 'end' and local == 'identifier':
                if ''.join(el.itertext()).strip() == cfg['lei']: info['lei_match']=True
            elif event == 'end' and local == 'startDate':
                if ''.join(el.itertext()).strip() == cfg['period_start']: info['period_start_match']=True
            elif event == 'end' and local == 'endDate':
                if ''.join(el.itertext()).strip() == cfg['period_end']: info['period_end_match']=True
    except ET.ParseError as exc:
        info['parse_error']=str(exc)
    except Exception as exc:
        info['parse_error']=str(exc)
    finally:
        shutil.rmtree(tmpdir,ignore_errors=True)
    info['inline_xbrl']=bool(info['fact_count'] and 'xbrl_context' in info['markers_found'])
    if info['inline_xbrl']: info['recognition_classification']='viewer_enhanced_inline_xbrl' if 'viewer' in name.lower() else 'inline_xbrl_filing'
    elif scan['markers_found']: info['recognition_classification']='viewer_wrapper_or_partial_inline_xbrl'
    info['identity_result']='matched' if info['lei_match'] else 'mismatch'
    info['period_result']='matched' if info['period_start_match'] and info['period_end_match'] else 'mismatch'
    return info

def locate_ixbrl_report(zip_path:Path,cfg:dict[str,Any])->dict[str,Any]:
    diag=inspect_archive(zip_path,cfg); selected=[]; candidates=[]
    with zipfile.ZipFile(zip_path) as z:
        names=[n for n in z.namelist() if n.lower().endswith(REPORT_EXTENSIONS)]
        for name in names:
            info=_inspect_ixbrl_candidate(z,name,cfg)
            if not info['inline_xbrl']:
                candidates.append(info); continue
            candidates.append(info)
            if info['lei_match'] and info['period_start_match'] and info['period_end_match'] and info['required_metric_matches']>0 and not info.get('parent_or_subsidiary_scope'):
                selected.append(info)
    inline=[c for c in candidates if c['inline_xbrl']]
    diag['candidate_inline_xbrl_reports']=[c['path'] for c in inline]
    diag['inline_xbrl_marker_results']=[{'path':c['path'],'markers_found':c['markers_found'],'fact_count':c['fact_count'],'parse_error':c['parse_error'],'marker_scan':c.get('marker_scan'),'recognition_classification':c.get('recognition_classification'),'consolidated_scope_match':c.get('consolidated_scope_match')} for c in candidates]
    diag['identity_result']={c['path']:c['identity_result'] for c in candidates}
    diag['period_result']={c['path']:c['period_result'] for c in candidates}
    diag['recognition_classification']={c['path']:c.get('recognition_classification') for c in candidates}
    if len(selected)==1:
        diag['locator_decision']=selected[0]['path']; diag['selected_report_path']=selected[0]['path']
        diag['locator_reason']=diag['selection_reason']='single inline XBRL report matching BT LEI, FY26 period and required metric markers'
        return {'report_path':selected[0]['path'],'diagnostics':diag,'candidates':candidates,'selected_candidate':selected[0]}
    if not inline:
        diag['locator_reason']='no XHTML/HTML/HTM entry contained validated inline XBRL facts and contexts'
        raise StructuredIngestionError('no inline XBRL report found in package', 'ixbrl_report_not_found', 'structured package recognition')
    if not selected:
        diag['locator_reason']='inline XBRL candidates did not match BT LEI, FY26 period and metric markers'
        raise StructuredIngestionError('structured report locator failed', 'structured_report_locator_failed', 'structured package recognition')
    diag['locator_reason']='multiple inline XBRL reports matched BT LEI, FY26 period and metric markers'
    raise StructuredIngestionError('multiple inline XBRL reports remain ambiguous', 'multiple_ixbrl_reports_ambiguous', 'structured package recognition')
def _contexts(root):
    out={}
    for c in root.iter(XBRLI_NS+'context'):
        cid=c.attrib.get('id'); ident=c.find(f'.//{XBRLI_NS}identifier'); s=c.find(f'.//{XBRLI_NS}startDate'); e=c.find(f'.//{XBRLI_NS}endDate'); inst=c.find(f'.//{XBRLI_NS}instant')
        dims=[ET.tostring(d,encoding='unicode') for d in c.iter() if d.tag in {XBRLDI_NS+'explicitMember',XBRLDI_NS+'typedMember'}]
        if cid: out[cid]={'context_id':cid,'entity_identifier':(ident.text or '').strip() if ident is not None else '', 'period_start':(s.text or '').strip() if s is not None else None, 'period_end':(e.text or '').strip() if e is not None else None, 'instant':(inst.text or '').strip() if inst is not None else None, 'dimensions':dims, 'scope':'group_consolidated' if not dims else 'dimensioned'}
    return out
def extract_candidates(zip_path:Path,cfg:dict[str,Any],receipt:RetrievedPackage):
    
    validate_archive(zip_path,cfg)
    location=locate_ixbrl_report(zip_path,cfg); report_path=location['report_path']
    candidates=[]; quarantine=[]; required=cfg['required_metrics']
    with zipfile.ZipFile(zip_path) as z:
        tmpdir=Path(tempfile.mkdtemp(prefix='flora-bt-adapter-'))
        try:
            report_file=_copy_zip_entry_to_temp(z,report_path,tmpdir)
            root=ET.parse(report_file).getroot()
        finally:
            shutil.rmtree(tmpdir,ignore_errors=True)
    contexts=_contexts(root)
    for el in root.iter():
        qn=el.attrib.get('name') or ''
        if el.tag!=IX_NS+'nonFraction' or qn not in required: continue
        ctx=contexts.get(el.attrib.get('contextRef','')); reason=None
        if not ctx: reason='missing_context'
        elif ctx['entity_identifier']!=cfg['lei']: reason='wrong_entity_identifier'
        elif ctx['period_start']!=cfg['period_start'] or ctx['period_end']!=cfg['period_end']: reason='wrong_period_or_comparator'
        elif ctx['instant']: reason='instant_context_for_duration_metric'
        elif ctx['dimensions']: reason='unsupported_dimension_or_segment'
        if reason: quarantine.append({'qname':qn,'context_ref':el.attrib.get('contextRef'),'reason':reason}); continue
        reported=Decimal(''.join(el.itertext()).strip().replace(',','')); metric=required[qn]
        candidates.append({'metric_id':metric,'qname':qn,'context':ctx,'unit_ref':el.attrib.get('unitRef'),'decimals':el.attrib.get('decimals'),'precision':el.attrib.get('precision'),'reported_amount':str(reported),'reported_scale':'millions','normalised_amount':str(reported*Decimal(1000000)),'source_locator':f"{receipt.final_url}#{report_path}#{qn}:{ctx['context_id']}"})
    return candidates, quarantine
def _statement(metric, amount):
    labels={'revenue':'revenue','operating_profit':'operating profit','profit_before_tax':'profit before tax'}
    return f"BT Group reported FY26 statutory {labels[metric]} of £{Decimal(amount):,}m."
def _snapshot():
    svc=ObservationMemoryService(); ent=canonical_enterprise_id('bt-group-plc') or 'bt-group-plc'; model=svc.models.get(ent); obs=svc.observations.list()
    return {'canonical_enterprise_id':ent,'observations':len(obs),'attributes':len(model.attributes),'active_observation_count':len(obs),'active_enterprise_model_attribute_count':len(model.attributes),'state_existed_before_run':bool(obs or model.attributes)}
def _reload_ok(obs_ids, attrs):
    svc=ObservationMemoryService(); model=svc.models.get('bt-group-plc')
    return all(svc.observations.get(o) for o in obs_ids) and all(a in model.attributes for a in attrs)
def _diagnostic(run_id,cfg,exc,receipt=None,candidate_count=0,canonical_count=0,adapter=False,archive_diagnostics=None,selected_report_path=None):
    code=getattr(exc,'code','unexpected_runtime_error'); stage=getattr(exc,'stage','unexpected runtime error')
    if not adapter and code == 'no_supported_facts':
        code='ixbrl_report_not_recognised'; stage='structured package recognition'
    url=(cfg or {}).get('artifact_url',''); parsed=urlparse(url) if url else None
    archive_result='passed' if adapter or (receipt and code not in SAFETY_FAILURE_CODES and code not in {'invalid_zip'}) else ('not_attempted' if not receipt else 'failed')
    diag={'support_reference':'FI-'+run_id.removeprefix('fi-'),'enterprise_id':(cfg or {}).get('enterprise_id','bt-group-plc'),'reporting_period':(cfg or {}).get('reporting_period','FY26'),'execution_mode':'structured_standard_financials','source_configuration_status':'loaded' if cfg else 'missing','source_configuration_key':'bt-group-plc-fy26','source_kind':(cfg or {}).get('source_kind'),'artifact_host':parsed.hostname if parsed else None,'artifact_url':url or None,'artifact_resolution_status':'resolved' if url else 'missing','request_attempted': bool(receipt) or code not in {'source_configuration_missing','enterprise_identity_mismatch','reporting_period_mismatch','artifact_url_missing','artifact_url_not_downloadable','host_not_allowed'},'http_status':getattr(receipt,'status_code',None),'redirect_chain':[],'final_host':urlparse(receipt.final_url).hostname if receipt else None,'content_type':getattr(receipt,'content_type',None),'reported_content_length':None,'bytes_downloaded':getattr(receipt,'size',0) if receipt else 0,'compressed_size_limit':int((cfg or {}).get('compressed_size_limit_bytes',0) or 0),'download_result':'succeeded' if receipt else 'failed','package_sha256':getattr(receipt,'sha256',None),'archive_validation_result':archive_result,'selected_report_path':selected_report_path,'package_type':(archive_diagnostics or {}).get('package_type'),'raw_report_path_or_url':selected_report_path or url or None,'source_authority':(cfg or {}).get('source_kind'),'issuer_identity_result':'matched' if (cfg or {}).get('lei')=='213800LRO7NS5CYQMN21' and (cfg or {}).get('company_number')=='04190816' else 'not_evaluated','period_result':'matched' if (cfg or {}).get('period_end')=='2026-03-31' else 'not_evaluated','consolidated_scope_result':'matched' if (cfg or {}).get('scope')=='group_consolidated' else 'not_evaluated','adapter_handoff_attempted':adapter,'adapter_result':'not_attempted' if not adapter else ('completed' if canonical_count else 'failed'),'candidate_fact_count':candidate_count,'canonical_fact_count':canonical_count,'failure_code':code,'failure_stage':stage,'safe_failure_message':('The configured source is a search page rather than a filing download.' if code=='artifact_url_not_downloadable' else 'Structured financial source unavailable'),'timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'deployment_revision':os.getenv('RENDER_GIT_COMMIT') or os.getenv('RENDER_COMMIT') or os.getenv('GIT_COMMIT')}
    if archive_diagnostics: diag['archive_diagnostics']=archive_diagnostics
    return diag
def _safe_diag(run:dict[str,Any])->dict[str,Any]:
    from cios.applications.flora.document_review import attach_financial_run_diagnostic
    attach_financial_run_diagnostic(run)
    return run
def _persist_diag(run_id,diag):
    from cios.applications.flora.document_review import _sanitize_diagnostic_payload
    diag=_sanitize_diagnostic_payload(diag)
    atomic_write_json(data_path('ai_financial_reports','diagnostics',f'{run_id}.json'),diag); print('Flora structured diagnostic '+json.dumps(diag,sort_keys=True),flush=True)
def _failure(run_id,before,exc,cfg=None,receipt=None):
    archive_diag=None
    if cfg and receipt:
        try: archive_diag=inspect_archive(receipt.path,cfg)
        except Exception: archive_diag=None
    diag=_diagnostic(run_id,cfg,exc,receipt,archive_diagnostics=archive_diag); _persist_diag(run_id,diag)
    after=_snapshot(); run={'run_id':run_id,'created_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'structured_source_unavailable','failure_category':'structured_source_unavailable','support_reference':'FI-'+run_id.removeprefix('fi-'),'failure_code':diag['failure_code'],'failure_stage':diag['failure_stage'],'user_message':'Structured financial source unavailable','user_message_display':'Structured financial source unavailable Support reference: FI-'+run_id.removeprefix('fi-')+' Failure stage: '+diag['failure_stage'],'structured_diagnostics':[diag],'provider_diagnostics':[diag],'exceptions':[{'exception_type':type(exc).__name__,'failure_stage':diag['failure_stage'],'failure_code':diag['failure_code'],'support_reference':'FI-'+run_id.removeprefix('fi-'),'user_message':'Structured financial source unavailable','rejection_reason':str(exc)}],'trusted_state_before':before,'trusted_state_after':after,'trusted_twin_changed':before.get('active_observation_count')!=after.get('active_observation_count') or before.get('active_enterprise_model_attribute_count')!=after.get('active_enterprise_model_attribute_count'),'ephemeral_state_absent_before_run':not before.get('state_existed_before_run'),'openai_calls_made':0,'ai_calls_made':0,'pdf_fallback_calls_made':0,'extraction_mode':'structured_standard_financials','provider_status':'not_executed','openai_invoked':False,'prohibited_path_counters':{'provider_calls':0,'pdf_section_selector_calls':0,'pdf_candidate_extractor_calls':0,'pdf_packet_calls':0},'usage':{'openai_calls':0},'collection':{'retrieved':False,'error':str(exc)},'run_status':{'structured_source':'unavailable','ai_calls_made':0,'pdf_fallback_calls_made':0}}
    atomic_write_json(data_path('ai_financial_reports','runs',f'{run_id}.json'),_safe_diag(run)); return run
def ingest_bt_fy26(run_id:str)->dict[str,Any]:
    cfg=None; before=_snapshot(); tmpdir=None; receipt=None
    try:
        cfg=source_config(); receipt=retrieve_package(cfg); tmpdir=receipt.path.parent; candidates,quarantine=extract_candidates(receipt.path,cfg,receipt); by={c['metric_id']:c for c in candidates}
        for m in ('revenue','operating_profit','profit_before_tax'):
            if m not in by: raise StructuredIngestionError(f'required standard fact missing: {m}', 'no_supported_facts', 'structured fact validation')
        svc=ObservationMemoryService(); results=[]; evidence_ids=[]; observation_ids=[]; attrs=[]
        for c in [by['revenue'],by['operating_profit'],by['profit_before_tax']]:
            eid='EV-BT-FY26-'+c['metric_id'].upper().replace('_','-'); attr=f"financial_performance.metrics.{c['metric_id']}.FY26.actual"; stmt=_statement(c['metric_id'],c['reported_amount'])
            evidence={'evidence_id':eid,'enterprise_id':'bt-group-plc','canonical_enterprise_id':'bt-group-plc','legal_name':cfg['legal_name'],'company_number':cfg['company_number'],'lei':cfg['lei'],'filing_title':'BT Group plc Annual Report 2026 ESEF filing','reporting_period':'FY26','source_class':cfg['source_kind'],'discovery_url':cfg['discovery_url'],'artifact_url':cfg['artifact_url'],'source_url':cfg['artifact_url'],'enterprise_scope':'group_consolidated','viewer_url':cfg['viewer_url'],'package_sha256':receipt.sha256,'qname':c['qname'],'context':c['context'],'unit_ref':c['unit_ref'],'currency':'GBP','reported_scale':c['reported_scale'],'decimals':c['decimals'],'precision':c['precision'],'reported_amount':c['reported_amount'],'display_value':f"£{Decimal(c['reported_amount']):,}m",'metric_identity':c['metric_id'],'metric_label':c['metric_id'].replace('_',' '),'normalised_amount':c['normalised_amount'],'original_display_value':f"£{Decimal(c['reported_amount']):,}m",'adapter_name':'StructuredFinancialAdapter','adapter_version':'structured-source-first-v1','collection_timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'acceptance_result':'accepted','source_locator':c['source_locator'],'commercial_condition':'financial_metric_reported','cleaned_observation':stmt,'affected_attribute':attr,'confidence':100,'period':'FY26','state':'actual','accounting_basis':'statutory','evidence_freshness':'current','observation_date':'2026-03-31','publication_date':'2026-05-22','page_range':'structured filing'}
            report=svc.process_evidence(evidence)
            if len(report.results)!=1 or report.rejected_claims: raise StructuredIngestionError(f"canonical validation failed for {c['metric_id']}: {report.rejected_claims}", 'adapter_handoff_failed', 'structured fact validation')
            result=report.results[0]; results.append(result.__dict__); evidence_ids.append(eid); observation_ids.append(result.observation_id); attrs.append(attr)
        after=_snapshot(); status={'structured_source':'available','ai_calls_made':0,'pdf_fallback_calls_made':0,'canonical_facts_accepted':3,'structured_evidence_records':3,'financial_observations':3,'enterprise_model_attributes':3,'trusted_twin_changed':before!=after,'persistent_state_verified_after_restart':_reload_ok(observation_ids,attrs)}
        
        loc=locate_ixbrl_report(receipt.path,cfg)
        diag=_diagnostic(run_id,cfg,StructuredIngestionError('', 'none', 'completed'),receipt,len(candidates),3,True,loc['diagnostics'],loc['report_path']); _persist_diag(run_id,diag)
        run={'run_id':run_id,'status':'completed','support_reference':'FI-'+run_id.removeprefix('fi-'),'structured_diagnostics':[diag],'provider_diagnostics':[diag],'collection':{'retrieved':True,'sha256':receipt.sha256,'final_url':receipt.final_url,'document_size':receipt.size},'claims':candidates,'candidate_exceptions':quarantine,'applied_results':results,'evidence_ids':evidence_ids,'observation_ids':observation_ids,'enterprise_attributes_changed':attrs,'run_status':status,'trusted_state_before':before,'trusted_state_after':after,'trusted_twin_changed':status['trusted_twin_changed'],'openai_calls_made':0,'ai_calls_made':0,'pdf_fallback_calls_made':0,'extraction_mode':'structured_standard_financials','provider_status':'not_executed','openai_invoked':False,'prohibited_path_counters':{'provider_calls':0,'pdf_section_selector_calls':0,'pdf_candidate_extractor_calls':0,'pdf_packet_calls':0}}
        atomic_write_json(data_path('ai_financial_reports','runs',f'{run_id}.json'),_safe_diag(run)); return run
    except Exception as exc: return _failure(run_id,before,exc,cfg,receipt)
    finally:
        if tmpdir and tmpdir.name.startswith('flora-bt-esef-'): shutil.rmtree(tmpdir,ignore_errors=True)
