"""启动共享的真实后端 Playwright smoke。"""

from __future__ import annotations

import os
import signal
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
DEFAULT_FRONTEND_PORTS = {
    "Django": 9530,
    "FastAPI": 9531,
}
PLAYWRIGHT_TIMEOUT_SECONDS = 900
PROCESS_TERMINATION_TIMEOUT_SECONDS = 10


def _frontend_port(backend_name: str, environment: dict[str, str]) -> str:
    """为每套后端分配独立端口，同时允许调用方显式覆盖。"""
    configured_port = environment.get("REAL_FRONTEND_PORT")
    if configured_port:
        return configured_port
    try:
        return str(DEFAULT_FRONTEND_PORTS[backend_name])
    except KeyError as exc:
        supported = ", ".join(DEFAULT_FRONTEND_PORTS)
        raise ValueError(
            f"Unsupported backend_name {backend_name!r}; expected one of: {supported}"
        ) from exc


def _terminate_process_group(process: subprocess.Popen[object]) -> None:
    """超时时终止 pnpm、Vite 和 Chromium 所在的整个进程组。"""
    if os.name == "nt":
        process.terminate()
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return

    try:
        process.wait(timeout=PROCESS_TERMINATION_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            process.kill()
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
        process.wait(timeout=PROCESS_TERMINATION_TIMEOUT_SECONDS)


def run_real_backend_playwright(
    *,
    backend_name: str,
    backend_url: str,
    username: str,
    password: str,
    notice_title: str,
    notice_content: str,
    rbac_username: str,
    rbac_password: str,
    rbac_role_id: int,
    rbac_base_permission_ids: list[int],
    rbac_granted_permission_ids: list[int],
    lifecycle_role_name: str,
    lifecycle_dept_name: str,
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
            "REAL_BACKEND_RBAC_USERNAME": rbac_username,
            "REAL_BACKEND_RBAC_PASSWORD": rbac_password,
            "REAL_BACKEND_RBAC_ROLE_ID": str(rbac_role_id),
            "REAL_BACKEND_RBAC_BASE_PERMISSION_IDS": ",".join(
                str(permission_id) for permission_id in rbac_base_permission_ids
            ),
            "REAL_BACKEND_RBAC_GRANTED_PERMISSION_IDS": ",".join(
                str(permission_id) for permission_id in rbac_granted_permission_ids
            ),
            "REAL_BACKEND_LIFECYCLE_ROLE_NAME": lifecycle_role_name,
            "REAL_BACKEND_LIFECYCLE_DEPT_NAME": lifecycle_dept_name,
        }
    )
    env["REAL_FRONTEND_PORT"] = _frontend_port(backend_name, env)
    command = ["pnpm", "run", "test:e2e:real-backend"]
    process = subprocess.Popen(
        command,
        cwd=FRONTEND_ROOT,
        env=env,
        start_new_session=os.name != "nt",
    )
    try:
        return_code = process.wait(timeout=PLAYWRIGHT_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        _terminate_process_group(process)
        raise
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)
