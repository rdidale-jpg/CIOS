from pathlib import Path
import os,sys
from cios.applications.flora.enterprise_intelligence import pipeline
pipeline.run_pipeline.__defaults__=(Path(os.environ['FLORA_DISCOVERY_BROWSER_EVIDENCE']).resolve()/'browser-derived'/sys.argv[1],None,None)
from http.server import ThreadingHTTPServer
from cios.applications.flora.web.app import FloraWebHandler
ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1])),FloraWebHandler).serve_forever()
