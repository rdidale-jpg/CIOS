"""Read-only Guest navigation on isolated localhost main, no live services."""
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix='flora-presentation-audit-') as tmp:
        os.environ['FLORA_DATA_DIR'] = str(Path(tmp) / 'isolated-data')
        os.environ['FLORA_ENVIRONMENT'] = 'development'
        os.environ['FLORA_AUTH_PROVIDER'] = 'local'
        os.environ.pop('FLORA_PILOT_DIR', None)
        from cios.applications.flora.web.app import FloraWebHandler

        class Quiet(FloraWebHandler):
            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Quiet)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        config = Path(tmp) / 'config.json'
        config.write_text(json.dumps({'base': f'http://127.0.0.1:{server.server_port}',
                                     'output': str(HERE / 'Browser-Observations.json')}))
        try:
            subprocess.run(['node', str(HERE / 'browser_audit.cjs'), str(config)], check=True)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)


if __name__ == '__main__':
    run()
