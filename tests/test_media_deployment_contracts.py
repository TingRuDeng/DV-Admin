import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MediaDeploymentContracts(unittest.TestCase):
    def test_production_paths_and_readonly_proxy_are_explicit(self):
        settings = (ROOT / "backend/drf_admin/settings.py").read_text()
        self.assertIn('env.str("MEDIA_ROOT"', settings)
        for backend, variable in (("backend", "MEDIA_ROOT"), ("fastapi", "UPLOAD_DIR")):
            dockerfile = (ROOT / backend / "docker/Dockerfile").read_text()
            self.assertIn(f"{variable}=/data/media", dockerfile)
            self.assertIn("/data/media", dockerfile)
        compose = (ROOT / "deploy/compose.production.yml").read_text()
        self.assertIn("media:/data/media:ro", compose)
        self.assertIn("media:/data/media", compose)
        nginx = (ROOT / "fastapi/docker/nginx.conf").read_text()
        self.assertIn("location /media/", nginx)
        self.assertIn("alias /data/media/;", nginx)
