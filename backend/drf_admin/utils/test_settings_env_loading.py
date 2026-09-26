"""settings.py 必须在加载 .env 文件之后再读取依赖它的配置。"""

import os
import subprocess
import sys
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
PRINT_PROXY_IPS = (
    "import django, os; os.environ['DJANGO_SETTINGS_MODULE'] = 'drf_admin.settings'; "
    "from django.conf import settings; print(settings.TRUSTED_PROXY_IPS)"
)


def _settings_value_with_env_file(extra_line: str, **env_overrides: str) -> str:
    environment = f"proxycheck{uuid.uuid4().hex[:8]}"
    env_file = BACKEND_DIR / f".env.{environment}"
    env_file.write_text(
        (BACKEND_DIR / ".env.test").read_text(encoding="utf-8") + f"\n{extra_line}\n",
        encoding="utf-8",
    )
    env = {k: v for k, v in os.environ.items() if k != "TRUSTED_PROXY_IPS"}
    env.update({"ENVIRONMENT": environment, **env_overrides})
    try:
        result = subprocess.run(
            [sys.executable, "-c", PRINT_PROXY_IPS],
            cwd=BACKEND_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
    finally:
        env_file.unlink(missing_ok=True)
    return result.stdout.strip().splitlines()[-1]


def test_trusted_proxy_ips_is_read_from_env_file():
    assert _settings_value_with_env_file("TRUSTED_PROXY_IPS=10.0.0.0/8") == "10.0.0.0/8"


def test_process_environment_still_overrides_env_file():
    value = _settings_value_with_env_file(
        "TRUSTED_PROXY_IPS=10.0.0.0/8", TRUSTED_PROXY_IPS="192.168.1.1"
    )
    assert value == "192.168.1.1"
