"""Durable offline research operations; existing candidate semantics, no canonical writes.

Only an explicitly selected isolated root is used. No web mutation handler, private
retrieval, shell execution, model client, scheduler or Pipeline API lives here.
"""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import secrets
import sqlite3
from ..cycle import digest
from .contracts import Programme, Acquisition, Rights, ROLES
from ...enterprise_intelligence.semantic import CandidateClaim, SourceSegment
from ...enterprise_intelligence.models import EvidencePackageItem
from ...blueprint_import.semantic_twin import SemanticObject, SemanticTwin
from ...blueprint_import.researcher_profile_adapter import adapt_researcher_payload

NOW=lambda:datetime.now(timezone.utc).isoformat()
INJECTION=re.compile(r'ignore.{0,40}instructions|system\s*prompt|api[_ -]?key|execute\s+(?:code|command)|override.{0,20}(?:policy|permissions)',re.I)
SENSITIVE=re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\b(?:password|bearer|confidential|customer[-_ ]secret)\b',re.I)


class Operations:
    def __init__(self,root):
        supplied=Path(root).absolute()
        if any(p.is_symlink() for p in (supplied,*supplied.parents)):raise PermissionError('Operational root cannot traverse symlinks')
        self.root=supplied.resolve()
        import os
        protected=[Path('/var/data').resolve()]
        protected += [Path(os.environ[k]).resolve() for k in ('FLORA_DATA_DIR','FLORA_PILOT_DIR') if os.environ.get(k)]
        if any(self.root==p or self.root.is_relative_to(p) for p in protected):
            raise PermissionError('Research CLI must use an isolated operational root, never production/tenant stores')
        self.root.mkdir(parents=True,exist_ok=True);self.root.chmod(0o700)
        self.path=self.root/'operations.sqlite'
        if self.path.is_symlink() or (self.root/'source_archive').is_symlink():raise PermissionError('Operational storage symlink denied')
        with self.db() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, idem TEXT UNIQUE, programme TEXT, state TEXT, requests INTEGER DEFAULT 0, retained_bytes INTEGER DEFAULT 0, cancel INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, job TEXT, role TEXT, source TEXT, attempt INTEGER, state TEXT, UNIQUE(job,role,source,attempt));
            CREATE TABLE IF NOT EXISTS acquisitions(request TEXT PRIMARY KEY, job TEXT, source TEXT, role TEXT, payload TEXT);
            CREATE TABLE IF NOT EXISTS objects(id TEXT, job TEXT, kind TEXT, payload TEXT, state TEXT, PRIMARY KEY(job,id));
            CREATE TABLE IF NOT EXISTS dependencies(job TEXT,parent TEXT,child TEXT,PRIMARY KEY(job,parent,child));
            CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,job TEXT,event TEXT,at TEXT,payload TEXT);
            CREATE TABLE IF NOT EXISTS releases(id TEXT PRIMARY KEY,job TEXT,version INTEGER,payload TEXT,UNIQUE(job,version));
            ''')
        self.path.chmod(0o600)

    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,timeout=20);db.row_factory=sqlite3.Row
        try:
            db.execute('PRAGMA foreign_keys=ON');db.execute('BEGIN IMMEDIATE');yield db;db.commit()
        except BaseException:db.rollback();raise
        finally:db.close()

    def event(self,db,job,name,payload):
        db.execute('INSERT INTO events(job,event,at,payload) VALUES(?,?,?,?)',(job,name,NOW(),json.dumps(payload,sort_keys=True)))

    def create(self,programme,idempotency_key):
        p=Programme.model_validate(programme.model_dump(mode='json') if isinstance(programme,Programme) else programme)
        raw=p.model_dump(mode='json');encoded=json.dumps(raw,sort_keys=True)
        if not re.fullmatch(r'[A-Za-z0-9._-]{1,120}',idempotency_key):raise ValueError('Finite idempotency key required')
        with self.db() as db:
            old=db.execute('SELECT * FROM jobs WHERE idem=?',(idempotency_key,)).fetchone()
            if old:
                if old['programme']!=encoded:raise ValueError('Idempotency key cannot change research scope')
                return old['id']
            jid='RJ-'+digest([raw,idempotency_key])[:24]
            db.execute('INSERT INTO jobs(id,idem,programme,state) VALUES(?,?,?,?)',(jid,idempotency_key,encoded,'ready' if p.mode=='establish' else 'unsupported_mode'))
            self.event(db,jid,'created',{'mode':p.mode,'audience':p.audience,'implemented':p.mode=='establish'})
            return jid

    def _job(self,db,jid):
        j=db.execute('SELECT * FROM jobs WHERE id=?',(jid,)).fetchone()
        if not j:raise ValueError('Unknown job')
        return j,Programme(**json.loads(j['programme']))

    def status(self,jid):
        with self.db() as db:
            j,p=self._job(db,jid)
            events=[dict(e) for e in db.execute('SELECT * FROM events WHERE job=? ORDER BY seq',(jid,))]
            return {'schema_version':1,'programme_id':p.id,'mode':p.mode,'as_of':p.as_of.isoformat(),'audience':p.audience,'caps':p.caps.model_dump(mode='json'),'id':jid,'state':j['state'],'cancelled':bool(j['cancel']),'logical_source_requests':j['requests'],
                    'retained_excerpt_bytes':j['retained_bytes'],'model_cost':None,'cost_status':'Not measured; no paid client configured',
                    'network_bytes':None,'events':events,'programme_digest':digest(p.model_dump(mode='json'))}

    def cancel(self,jid):
        with self.db() as db:
            self._job(db,jid);db.execute("UPDATE jobs SET cancel=1,state='cancelled' WHERE id=?",(jid,));self.event(db,jid,'cancelled',{})

    def request(self,jid,role,source_id):
        with self.db() as db:
            j,p=self._job(db,jid)
            if j['cancel'] or p.mode!='establish' or j['state']=='exhausted':raise ValueError('Job stopped or mode not implemented')
            if role not in ('researcher','verifier'):raise ValueError('Only acquisition roles issue source requests')
            source=next((s for s in p.sources if s.source_id==source_id),None)
            if not source:raise ValueError('Source outside approved programme')
            source.require('acquisition','deterministic_extraction','retention','quotation')
            if role=='verifier' and not db.execute("SELECT 1 FROM acquisitions WHERE job=? AND source=? AND role='researcher'",(jid,source_id)).fetchone():
                raise ValueError('Verifier acquires after independent research acquisition')
            previous=db.execute('SELECT * FROM requests WHERE job=? AND role=? AND source=? ORDER BY attempt DESC',(jid,role,source_id)).fetchone()
            if previous and previous['state']=='pending':return {'request_id':previous['id'],'source_id':source_id,'url':source.url,'role':role,'collector_id':p.roles[role]}
            if previous and previous['state']=='complete':return None
            attempt=previous['attempt']+1 if previous else 1
            if attempt>p.caps.attempts_per_source or j['requests']>=p.caps.requests:
                db.execute("UPDATE jobs SET state='exhausted' WHERE id=?",(jid,));self.event(db,jid,'gap',{'source_id':source_id,'reason':'Bounded request/retry budget exhausted'});return None
            rid='ACQ-'+secrets.token_hex(16)
            db.execute('INSERT INTO requests VALUES(?,?,?,?,?,?)',(rid,jid,role,source_id,attempt,'pending'))
            db.execute('UPDATE jobs SET requests=requests+1 WHERE id=?',(jid,));self.event(db,jid,'requested',{'request_id':rid,'role':role,'source_id':source_id,'url':source.url})
            return {'request_id':rid,'source_id':source_id,'url':source.url,'role':role,'collector_id':p.roles[role]}

    def fail_request(self,jid,rid,reason):
        with self.db() as db:
            j,p=self._job(db,jid)
            if j['cancel']:raise ValueError('Cancelled job')
            r=db.execute('SELECT * FROM requests WHERE id=? AND job=?',(rid,jid)).fetchone()
            if not r or r['state']!='pending':raise ValueError('Not a pending source request')
            db.execute("UPDATE requests SET state='failed' WHERE id=?",(rid,));self.event(db,jid,'acquisition_failed',{'request_id':rid,'reason_digest':digest(str(reason)),'reason':'Acquisition unsuccessful; bounded retry or retain gap'})

    def ingest(self,jid,record):
        a=Acquisition.model_validate(record.model_dump(mode='json') if isinstance(record,Acquisition) else record)
        raw=a.model_dump(mode='json');encoded=json.dumps(raw,sort_keys=True)
        with self.db() as db:
            j,p=self._job(db,jid)
            if j['cancel'] or j['state'] in ('exhausted','unsupported_mode'):raise ValueError('Job stopped')
            r=db.execute('SELECT * FROM requests WHERE id=? AND job=?',(a.request_id,jid)).fetchone()
            if not r or (r['source'],r['role'])!=(a.source_id,a.role):raise ValueError('Acquisition not issued to this role/source')
            old=db.execute('SELECT payload FROM acquisitions WHERE request=?',(a.request_id,)).fetchone()
            if old:
                if old['payload']!=encoded:raise ValueError('Immutable acquisition changed')
                return a.excerpt_sha256
            if r['state']!='pending':raise ValueError('Closed acquisition request')
            issued=next((e for e in db.execute("SELECT at,payload FROM events WHERE job=? AND event='requested'",(jid,)) if json.loads(e['payload']).get('request_id')==a.request_id),None)
            if not issued or a.retrieved_at<datetime.fromisoformat(issued['at']):raise ValueError('Retrieval predates issued acquisition request')
            source=next(s for s in p.sources if s.source_id==a.source_id)
            source.require('acquisition','deterministic_extraction','retention','quotation')
            if a.url!=source.url or a.collector_id!=p.roles[a.role]:raise ValueError('Collector or URL scope mismatch')
            if a.retrieved_at.astimezone(timezone.utc).date()!=p.as_of:raise ValueError('Acquisition must match reviewed programme cut-off')
            if len(a.excerpt.split())>source.max_quote_words:raise ValueError('Quotation exceeds permitted extent')
            if INJECTION.search(a.excerpt) or SENSITIVE.search(a.excerpt):raise ValueError('Untrusted instructions or sensitive content quarantined')
            size=len(a.excerpt.encode())
            if j['retained_bytes']+size>p.caps.bytes:raise ValueError('Retained-byte budget exceeded')
            # Content-addressed permitted excerpts only; never archive full supplier pages/contact fields.
            folder=self.root/'source_archive';folder.mkdir(exist_ok=True);path=folder/(a.excerpt_sha256+'.txt')
            if path.exists() and path.read_text()!=a.excerpt:raise ValueError('Archive checksum collision')
            if path.is_symlink():raise PermissionError('Archive symlink denied')
            path.write_text(a.excerpt);path.chmod(0o600)
            db.execute('INSERT INTO acquisitions VALUES(?,?,?,?,?)',(a.request_id,jid,a.source_id,a.role,encoded))
            db.execute("UPDATE requests SET state='complete' WHERE id=?",(a.request_id,));db.execute('UPDATE jobs SET retained_bytes=retained_bytes+? WHERE id=?',(size,jid))
            self.event(db,jid,'acquired',{'request_id':a.request_id,'role':a.role,'source_id':a.source_id,'excerpt_sha256':a.excerpt_sha256,'extent':a.extent})
        return a.excerpt_sha256

    def _put(self,db,jid,identifier,kind,payload,state='active',parents=()):
        encoded=json.dumps(payload,sort_keys=True);old=db.execute('SELECT * FROM objects WHERE id=? AND job=?',(identifier,jid)).fetchone()
        if old:
            if old['job']!=jid or old['kind']!=kind or old['payload']!=encoded:raise ValueError('Stable object identity cannot rewrite evidence')
        else:db.execute('INSERT INTO objects VALUES(?,?,?,?,?)',(identifier,jid,kind,encoded,state))
        for parent in parents:db.execute('INSERT OR IGNORE INTO dependencies VALUES(?,?,?)',(jid,parent,identifier))

    def assure(self,jid):
        """Only independently re-acquired exact publisher catalogue entries are releasable.

        This is deterministic source/schema/rights assurance, not model semantic
        verification or proof that the underlying real-world assertion is true.
        """
        with self.db() as db:
            j,p=self._job(db,jid)
            if j['cancel'] or j['state'] in ('exhausted','unsupported_mode'):raise ValueError('Stopped job')
            reports=[]
            for source in p.sources:
                rows={r['role']:Acquisition(**json.loads(r['payload'])) for r in db.execute('SELECT * FROM acquisitions WHERE job=? AND source=?',(jid,source.source_id))}
                reason=''
                if set(rows)!= {'researcher','verifier'}:reason='Independent acquisition incomplete'
                else:
                    research,verification=rows['researcher'],rows['verifier']
                    if research.request_id==verification.request_id or research.collector_id==verification.collector_id or research.tool_reference==verification.tool_reference:
                        reason='Verifier reused researcher acquisition/context'
                    elif (research.publication_date,research.effective_date)!=(verification.publication_date,verification.effective_date):reason='Conflicting source date metadata; reconcile before release'
                    elif research.excerpt!=verification.excerpt or research.locator!=verification.locator:reason='Conflicting passage or location; reconcile before release'
                    elif research.execution_kind!=verification.execution_kind:reason='Fixture/live acquisition mismatch'
                    elif any(a.publication_date and (p.as_of-a.publication_date).days>p.caps.max_publication_age_days for a in rows.values()):reason='Stale publication; historical support only, refresh before current release'
                    elif verification.retrieved_at<research.retrieved_at:reason='Verifier retrieval precedes research'
                    else:
                        try:source.require('retention','quotation','indexing','redistribution')
                        except PermissionError:reason='Publication operation rights unresolved'
                if reason:
                    reports.append({'source_id':source.source_id,'outcome':'withhold_and_investigate','reason':reason});continue
                for acquired in rows.values():
                    archived=self.root/'source_archive'/(acquired.excerpt_sha256+'.txt')
                    if not archived.is_file() or archived.read_text()!=acquired.excerpt:raise ValueError('Source archive changed after acquisition')
                passage=rows['verifier'];segid=source.source_id+'::'+passage.excerpt_sha256[:16]
                segment=SourceSegment(segid,source.source_id,passage.locator,passage.excerpt,passage.excerpt_sha256,
                    source.url,'candidate_intelligence','independently_retrieved_literal')
                # Extract only whole lines that are names, not commands, contacts or free-form claims.
                names=[line.strip() for line in passage.excerpt.splitlines() if re.fullmatch(r'[A-Za-z0-9 &()./-]{2,100}(?:LIMITED|Limited|LTD|Ltd|PLC|SARL|Consortium\))',line.strip())]
                for name in names:
                    cid='RC-'+digest([source.source_id,name,p.as_of.isoformat()])[:24]
                    claim=CandidateClaim(cid,'publisher_reported_catalogue_entry',name,source.source_id,segid,
                        'UK public technology catalogue; no headquartered/market-scale assumption',source.source_id,'lists',name,
                        p.as_of.isoformat(),'named catalogue participant',name,'Literal source support only','candidate_intelligence',
                        'accepted_for_research_publication_not_canonical',[],[])
                    entry={'segment':segment.to_dict(),'candidate':claim.to_dict(),'family_id':source.family_id,
                           'truth_class':'publisher_reported_fact','entity_kind':'catalogue_participant','legal_entity_id':None,
                           'assertion':'GCA lists '+name+' on the referenced catalogue page.',
                           'source_id':source.source_id,'url':source.url,'publication_date':passage.publication_date.isoformat() if passage.publication_date else None,
                           'retrieved_at':passage.retrieved_at.isoformat(),'effective_date':passage.effective_date.isoformat() if passage.effective_date else None,
                           'attribution':source.attribution,'rights_digest':digest(source.model_dump(mode='json')),
                           'limitations':['Government catalogue entry is not a market ranking, legal registry identity, headquartered status, deployment or customer demand.','Fresh acquisition is not independent source-family corroboration.'],
                           'execution_kind':passage.execution_kind,'canonical_promotion':False}
                    self._put(db,jid,cid,'candidate',entry,parents=(source.source_id,))
                    self._put(db,jid,'IDX-'+cid,'derived_index',{'claim_id':cid,'tokens':name.casefold().split()},parents=(cid,))
                    self._put(db,jid,'VIS-'+cid,'visual_projection',{'claim_id':cid,'label':name,'truth_class':'publisher_reported_fact'},parents=(cid,))
                checks={role:{'method':'deterministic','outcome':'pass','basis':
                    'separate request/tool reference, same exact located excerpt' if role=='verifier' else
                    'catalogue name only; legal identity, HQ, jurisdictional applicability not inferred' if role=='entity_checker' else
                    'same publisher family counted once; membership does not prove importance, contract or adoption' if role=='challenger' else
                    'only literal publisher-reported entries; all semantic synthesis withheld' if role=='synthesis_reviewer' else
                    'bounded licensed excerpt, no contacts, sensitive data or private context' if role=='publication_reviewer' else
                    'versioned candidate research release; canonical/Pipeline owners untouched'} for role in ROLES if role!='researcher'}
                reports.append({'source_id':source.source_id,'outcome':'publish_supported_factual_content','names_extracted':names,'checks':checks,'model_semantic_assessment':'not implemented; inferred claims withheld','source_family':source.family_id})
            self.event(db,jid,'assured',{'reports':reports,'guarantee_of_truth':False})
            db.execute("UPDATE jobs SET state='assessed' WHERE id=?",(jid,))
            return reports

    def add_dependent(self,jid,identifier,kind,parents,payload):
        if kind not in ('relationship','hypothesis','visual_projection','derived_index'):raise ValueError('Unsupported dependent object')
        with self.db() as db:
            j,p=self._job(db,jid)
            if j['cancel']:raise ValueError('Cancelled job')
            for parent in parents:
                row=db.execute('SELECT * FROM objects WHERE id=? AND job=?',(parent,jid)).fetchone()
                if not row or row['state']!='active':raise ValueError('Dependent source missing/withdrawn')
            if not parents:raise ValueError('Traceable parents required')
            if kind=='relationship':
                from .contracts import Relationship
                Relationship(**payload)
            if kind=='hypothesis':
                from .contracts import Narrative
                Narrative(**payload)
            if kind in ('relationship','hypothesis'):
                # A dependency graph is operational lineage, never semantic approval.
                payload={**payload,'truth_class':payload.get('truth_class','interpretation'),'publication_state':'withheld_semantic_assurance_required'}
            self._put(db,jid,identifier,kind,payload,parents=parents)

    def withdraw(self,jid,identifier,reason,superseded_by=None):
        if not reason.strip() or SENSITIVE.search(reason) or INJECTION.search(reason):raise ValueError('Public-safe correction rationale required')
        with self.db() as db:
            j,p=self._job(db,jid)
            old=db.execute('SELECT * FROM objects WHERE id=? AND job=?',(identifier,jid)).fetchone()
            if not old or old['kind']!='candidate':raise ValueError('Unknown scoped candidate claim')
            if superseded_by==identifier:raise ValueError('Self supersession denied')
            if superseded_by:
                replacement=db.execute("SELECT * FROM objects WHERE id=? AND job=? AND state='active'",(superseded_by,jid)).fetchone()
                if not replacement or replacement['kind']!='candidate':raise ValueError('Supersession target must exist and be an active candidate')
                if json.loads(old['payload'])['candidate']['statement']!=json.loads(replacement['payload'])['candidate']['statement']:
                    raise ValueError('Supersession cannot silently change entity scope')
            impacted={identifier};front={identifier}
            while front:
                nxt={r['child'] for parent in front for r in db.execute('SELECT child FROM dependencies WHERE job=? AND parent=?',(jid,parent))}-impacted
                impacted|=nxt;front=nxt
            for key in impacted:db.execute("UPDATE objects SET state=? WHERE id=? AND job=?",('superseded' if key==identifier and superseded_by else 'withdrawn' if key==identifier else 'invalidated',key,jid))
            self.event(db,jid,'correction',{'claim_id':identifier,'superseded_by':superseded_by,'reason':reason,'invalidated':sorted(impacted)})
            return sorted(impacted)

    def release(self,jid):
        with self.db() as db:
            j,p=self._job(db,jid)
            if j['cancel'] or j['state'] not in ('assessed','released'):raise ValueError('Assurance required before release')
            # Revalidate permitted archive at release time, not only at assurance.
            for acquired in db.execute('SELECT payload FROM acquisitions WHERE job=?',(jid,)):
                a=Acquisition(**json.loads(acquired['payload']))
                archive=self.root/'source_archive'/(a.excerpt_sha256+'.txt')
                if archive.is_symlink() or not archive.is_file() or archive.read_text()!=a.excerpt:raise ValueError('Release archive/provenance integrity failure')
            active=[json.loads(r['payload']) for r in db.execute("SELECT * FROM objects WHERE job=? AND kind='candidate' AND state='active' ORDER BY id",(jid,))]
            families=sorted({c['family_id'] for c in active})
            gaps=[{'requirement':key,'status':'gap','next_action':'Acquire permitted exact-scope primary evidence and independent assurance; no routine factual owner approval requested.'} for key in p.baseline_requirements]
            payload={'schema_version':1,'programme_id':p.id,'job_id':jid,'as_of':p.as_of.isoformat(),'audience':p.audience,
                     'claims':active,'live_research':bool(active) and all(c['execution_kind']=='live_web_bridge' for c in active),'gaps':gaps,'source_family_count':len(families),'source_families':families,
                     'assurance_kind':'Independent acquisition + deterministic literal/schema/rights validation; not model-based semantic verification',
                     'canonical_mutation':False,'automatic_pipeline_capture':False,'automatic_qualification':False,
                     'limitations':p.publication_limitations,'correction_events':[json.loads(e['payload']) for e in db.execute("SELECT payload FROM events WHERE job=? AND event='correction' ORDER BY seq",(jid,))]}
            latest=db.execute('SELECT * FROM releases WHERE job=? ORDER BY version DESC',(jid,)).fetchone()
            if latest and json.loads(latest['payload'])['content']==payload:
                db.execute("UPDATE jobs SET state='released' WHERE id=?",(jid,))
                return json.loads(latest['payload'])
            version=latest['version']+1 if latest else 1
            result={'id':'REL-'+digest([jid,version,payload])[:24],'version':version,'digest':digest(payload),'content':payload}
            db.execute('INSERT INTO releases VALUES(?,?,?,?)',(result['id'],jid,version,json.dumps(result,sort_keys=True)))
            db.execute("UPDATE jobs SET state='released' WHERE id=?",(jid,));self.event(db,jid,'released',{'release_id':result['id'],'version':version,'claim_count':len(active)})
            return result

    def rebuild(self,jid):
        """Reconstruct derived retrieval/visual state from active evidence, not vice versa."""
        with self.db() as db:
            job,_=self._job(db,jid)
            if job['cancel']:raise ValueError('Cancelled job')
            rows=db.execute("SELECT * FROM objects WHERE job=? AND kind='candidate' AND state='active'",(jid,)).fetchall()
            derived=[r['id'] for r in db.execute("SELECT id FROM objects WHERE job=? AND kind IN ('derived_index','visual_projection')",(jid,))]
            for key in derived:
                db.execute('DELETE FROM dependencies WHERE job=? AND (parent=? OR child=?)',(jid,key,key))
            db.execute("DELETE FROM objects WHERE job=? AND kind IN ('derived_index','visual_projection')",(jid,))
            for row in rows:
                value=json.loads(row['payload']);name=value['candidate']['statement'];cid=row['id']
                self._put(db,jid,'IDX-'+cid,'derived_index',{'claim_id':cid,'tokens':name.casefold().split()},parents=(cid,))
                self._put(db,jid,'VIS-'+cid,'visual_projection',{'claim_id':cid,'label':name,'truth_class':'publisher_reported_fact'},parents=(cid,))
            self.event(db,jid,'projections_rebuilt',{'active_claims':len(rows)})
            return len(rows)

    def semantic_twin(self,release):
        objects=[]
        for row in release['content']['claims']:
            claim=row['candidate'];segment=row['segment']
            evidence=EvidencePackageItem(claim['claim_id'],'Observation',claim['statement'],'Research release only',claim['confidence'],claim['time_scope'],(segment['segment_id'],claim['source_asset_id']),source_location=segment['source_location'])
            canonical_class,payload=adapt_researcher_payload('fact',{'id':claim['claim_id'],'statement':claim['statement'],'source_ids':[claim['source_asset_id']]})
            objects.append(SemanticObject(claim['claim_id'],'Observation',claim['statement'],claim['subject'],(segment['segment_id'],),claim['time_scope'],claim['confidence'],'candidate_intelligence',segment['source_location'],segment['section_heading'],False,'Research publication, not accepted canonical fact',original_id=claim['claim_id'],references=(claim['source_asset_id'],),validation_status='candidate',attributes={'candidate_claim':claim,'evidence_item':evidence.to_dict(),'researcher_adapter':payload,'canonical_class':canonical_class}))
        return SemanticTwin(tuple(objects),())
