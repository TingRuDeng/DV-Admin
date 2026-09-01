"""启动共享的真实后端 Playwright smoke。"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"


def run_real_backend_playwright(
    *,
    backend_name: str,
    backend_url: str,
    username: str,
    password: str,
    notice_title: str,
    notice_content: str,
) -> None:
    """让同一份浏览器流程连接指定真实后端，失败时保留 Playwright 原始错误。"""
    env = os.environ.copy()
    env.update(
        {
            "REAL_BACKEND_NAME": backend_name,
            "REAL_BACKEND_URL": backend_url,
            "REAL_BACKEND_USERNAME": username,
            "REAL_BACKEND_PASSWORD": password,
            "REAL_BACKEND_NOTICE_TITLE": notice_title,
            "REAL_BACKEND_NOTICE_CONTENT": notice_content,
        }
    )
    subprocess.run(
        [
            "pnpm",
            "run",
            "test:e2e:real-backend",
        ],
        cwd=FRONTEND_ROOT,
        env=env,
        check=True,
        timeout=300,
    )
