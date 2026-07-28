"""FastAPI 真实监听端口的共享业务 HTTP smoke。"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest


@pytest.mark.integration
def test_shared_profile_avatar_password_and_notice_flow_over_http(tmp_path: Path):
    """绕过 TestClient，验证真实 Uvicorn HTTP 链路。"""
    port = reserve_tcp_port()
    env = build_server_env(tmp_path)
    log_path = tmp_path / "uvicorn.log"

    with log_path.open("w", encoding="utf-8") as log_file:
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=Path(__file__).resolve().parents[1],
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            base_url = f"http://127.0.0.1:{port}"
            wait_for_server(base_url, server, log_path)
            seed = seed_http_database(env)
            run_http_flow(base_url, seed)
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


def build_server_env(tmp_path: Path) -> dict[str, str]:
    """构造完全隔离的 FastAPI HTTP smoke 环境。"""
    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "development",
            "DATABASE_URL": f"sqlite://{tmp_path / 'http-smoke.sqlite3'}",
            "DEFAULT_PASSWORD": "HttpDefault123!",
            "SECRET_KEY": "http-smoke-secret-key",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "REDIS_URL": "redis://127.0.0.1:1/0",
        }
    )
    return env


def reserve_tcp_port() -> int:
    """向内核申请临时端口，降低并行 CI 冲突概率。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(base_url: str, server: subprocess.Popen, log_path: Path) -> None:
    """等待 Uvicorn 就绪；提前退出时附带日志。"""
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise AssertionError(log_path.read_text(encoding="utf-8"))
        try:
            response = httpx.get(f"{base_url}/health/live", timeout=1)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.1)
    raise AssertionError(f"FastAPI HTTP smoke 启动超时\n{log_path.read_text(encoding='utf-8')}")


def seed_http_database(env: dict[str, str]) -> dict[str, int | str]:
    """通过独立进程写入 smoke 用户、权限和通知。"""
    result = subprocess.run(
        [sys.executable, "tests/live_http_seed.py"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
    )
    return json.loads(result.stdout.strip().splitlines()[-1])


def run_http_flow(base_url: str, seed: dict[str, int | str]) -> None:
    """执行与 Django smoke 相同的共享业务闭环。"""
    with httpx.Client(base_url=base_url, timeout=10) as client:
        login = client.post(
            "/api/v1/oauth/login/",
            json={"username": seed["username"], "password": "httpPass123"},
        )
        token = assert_success(login)["accessToken"]
        client.headers["Authorization"] = f"Bearer {token}"

        profile = assert_success(client.get("/api/v1/information/profile/"))
        assert profile["username"] == seed["username"]

        updated = assert_success(
            client.put(
                "/api/v1/information/profile/",
                json={"name": "FastAPI HTTP 已更新", "gender": 2},
            )
        )
        assert updated["name"] == "FastAPI HTTP 已更新"

        avatar = assert_success(
            client.post(
                "/api/v1/information/change-avatar/",
                files={"file": ("avatar.png", b"\x89PNG\r\n\x1a\nhttp-smoke", "image/png")},
            )
        )
        assert avatar["url"].startswith("/media/avatar/")

        my_page = assert_success(
            client.get(
                "/api/v1/system/notices/my-page/",
                params={"pageNum": 1, "pageSize": 10, "isRead": 0},
            )
        )
        assert seed["notice_id"] in {item["id"] for item in my_page["list"]}

        detail = assert_success(
            client.get(f"/api/v1/system/notices/{seed['notice_id']}/detail")
        )
        assert detail["id"] == seed["notice_id"]

        assert_success(
            client.put(
                "/api/v1/information/password",
                json={
                    "oldPassword": "httpPass123",
                    "newPassword": "httpPass456",
                    "confirmPassword": "httpPass456",
                },
            )
        )
        relogin = assert_success(
            client.post(
                "/api/v1/oauth/login/",
                json={"username": seed["username"], "password": "httpPass456"},
            )
        )
        assert "accessToken" in relogin


def assert_success(response: httpx.Response):
    """断言 FastAPI 真实 HTTP 成功信封并返回 data。"""
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["code"] == 20000, payload
    return payload["data"]
