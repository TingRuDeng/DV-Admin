"""Both backends must ship the same OIDC policy bytes; behaviour tests live in each backend."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FASTAPI_COPY = ROOT / "fastapi/app/core/oidc_policy.py"
DJANGO_COPY = ROOT / "backend/drf_admin/apps/oauth/oidc_policy.py"


class OidcPolicyContractTests(unittest.TestCase):
    # 只比对字节，不 import：CI 前端 job 的系统 Python 没有安装 PyJWT。
    def test_backend_policy_copies_match(self):
        self.assertEqual(FASTAPI_COPY.read_bytes(), DJANGO_COPY.read_bytes())

    def test_policy_declares_its_parity_rule(self):
        header = FASTAPI_COPY.read_text(encoding="utf-8").splitlines()[0]
        self.assertIn("byte-identical", header)


if __name__ == "__main__":
    unittest.main()
