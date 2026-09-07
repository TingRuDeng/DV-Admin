"""Cheap guards complement, rather than replace, production image smoke tests."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProductionImageContracts(unittest.TestCase):
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
