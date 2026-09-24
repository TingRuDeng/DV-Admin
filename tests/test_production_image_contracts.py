"""Cheap guards complement, rather than replace, production image smoke tests."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProductionImageContracts(unittest.TestCase):
    def test_django_asgi_channels_entry_is_present_and_explicit(self):
        routing = (ROOT / "backend/drf_admin/routing.py").read_text()
        asgi = (ROOT / "backend/drf_admin/asgi.py").read_text()
        settings = (ROOT / "backend/drf_admin/settings.py").read_text()
        self.assertIn('ASGI_APPLICATION = "drf_admin.routing.application"', settings)
        self.assertIn('"http": django_asgi_app', routing)
        self.assertIn('"websocket": AuthMiddlewareStack(URLRouter([]))', routing)
        self.assertIn("from drf_admin.routing import application", asgi)

    def test_images_install_the_same_frozen_noneditable_runtime(self):
        versions = json.loads((ROOT / "deploy/runtime-versions.json").read_text())
        workflow = (ROOT / ".github/workflows/quality-gates.yml").read_text()
        self.assertIn(f'UV_VERSION: "{versions["uv_version"]}"', workflow)
        for backend in ("backend", "fastapi"):
            with self.subTest(backend=backend):
                dockerfile = (ROOT / backend / "docker/Dockerfile").read_text()
                self.assertIn(versions["python_image"], dockerfile)
                self.assertIn(versions["uv_image"], dockerfile)
                self.assertIn("uv.lock", dockerfile)
                self.assertIn("README.md", dockerfile)
                self.assertIn("uv sync --frozen --no-dev --no-editable", dockerfile)
                self.assertNotIn("pip install", dockerfile)
                self.assertIn("USER 10001:10001", dockerfile)
                self.assertIn("/health/ready", dockerfile)
                ignore = (ROOT / backend / ".dockerignore").read_text()
                self.assertIn(".env*", ignore)
                self.assertIn(".venv", ignore)
        fastapi_dockerfile = (ROOT / "fastapi/docker/Dockerfile").read_text()
        self.assertIn("apt-get install -y --no-install-recommends gcc libc6-dev", fastapi_dockerfile)
        self.assertIn('"asyncmy>=0.2.0"', (ROOT / "fastapi/pyproject.toml").read_text())
