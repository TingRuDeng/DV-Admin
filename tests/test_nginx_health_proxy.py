"""Exercise the production Nginx probe locations using an isolated process."""

import json
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class ProbeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        status = 503 if self.path == "/health/ready" else 200
        self.send_response(status)
        self.end_headers()
        self.wfile.write(json.dumps({"status": status}).encode())

    def log_message(self, *_args):
        pass


@unittest.skipUnless(shutil.which("nginx"), "nginx is required for the production proxy smoke")
class NginxHealthProxyTests(unittest.TestCase):
    def test_proxy_preserves_readiness_failure_and_liveness_success(self):
        source = Path(__file__).resolve().parents[1] / "fastapi/docker/nginx.conf"
        with tempfile.TemporaryDirectory(prefix="dv-nginx-") as directory:
            root = Path(directory)
            upstream = ThreadingHTTPServer(("127.0.0.1", 0), ProbeHandler)
            thread = threading.Thread(target=upstream.serve_forever, daemon=True)
            thread.start()
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            config = source.read_text().replace(
                "server api:8000;", f"server 127.0.0.1:{upstream.server_port};"
            ).replace("listen 80;", f"listen 127.0.0.1:{port};").replace(
                "include /etc/nginx/mime.types;", "types { text/plain txt; }"
            ).replace("/var/log/nginx/", f"{directory}/")
            (root / "nginx.conf").write_text(
                f"daemon off;\npid {root / 'nginx.pid'};\n" + config
            )
            process = subprocess.Popen(
                [shutil.which("nginx"), "-p", directory, "-c", str(root / "nginx.conf")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            try:
                deadline = time.monotonic() + 5
                while True:
                    try:
                        with urlopen(f"http://127.0.0.1:{port}/nginx-health", timeout=0.2) as response:
                            self.assertEqual(response.status, 200)
                        break
                    except URLError:
                        if time.monotonic() > deadline or process.poll() is not None:
                            self.fail("isolated Nginx did not start")
                        time.sleep(0.05)
                with self.assertRaises(HTTPError) as failure:
                    urlopen(f"http://127.0.0.1:{port}/health/ready", timeout=2)
                self.assertEqual(failure.exception.code, 503)
                failure.exception.close()
                with urlopen(f"http://127.0.0.1:{port}/health/live", timeout=2) as response:
                    self.assertEqual(response.status, 200)
            finally:
                process.terminate()
                process.wait(timeout=5)
                upstream.shutdown()
                upstream.server_close()
                thread.join(timeout=5)
