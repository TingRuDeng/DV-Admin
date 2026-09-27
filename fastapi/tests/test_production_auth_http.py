"""Production authentication with two real API processes and isolated Redis."""

import secrets
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, contextmanager

import httpx
import pytest
from redis import Redis
from test_live_http_contract import (
    build_server_env,
    reserve_tcp_port,
    seed_http_database,
    wait_for_server,
)

from scripts.redis_test_server import RedisTestServer


@contextmanager
def api_process(root, env, name):
    port = reserve_tcp_port()
    log_path = root / f"{name}.log"
    with log_path.open("w") as output:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
             "--port", str(port), "--no-proxy-headers"], env=env, stdout=output, stderr=subprocess.STDOUT,
        )
        try:
            base_url = f"http://127.0.0.1:{port}"
            wait_for_server(base_url, process, log_path)
            yield base_url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.mark.integration
def test_production_revocation_rotation_outage_and_startup_recovery(tmp_path):
    with RedisTestServer() as redis:
        env = build_server_env(tmp_path)
        env.update(APP_ENV="production", DEBUG="false", SECRET_KEY=secrets.token_urlsafe(64),
                   REDIS_URL=redis.url)
        # Migration must work without contacting Redis, even in production mode.
        redis.stop()
        migration = subprocess.run(
            [sys.executable, "-m", "tortoise", "-c", "app.db.migration_config.TORTOISE_ORM", "migrate"],
            env=env, capture_output=True, text=True, timeout=30,
        )
        assert migration.returncode == 0, migration.stderr
        seed = seed_http_database(env)
        with ExitStack() as stack:
            urls = [stack.enter_context(api_process(tmp_path, env, str(index))) for index in range(2)]
            clients = [stack.enter_context(httpx.Client(base_url=url, timeout=10)) for url in urls]
            for client in clients:
                assert client.get("/health/live").status_code == 200
                assert client.get("/health/ready").status_code == 503
            redis.start()
            for client in clients:
                assert client.get("/health/ready").status_code == 200

            first, second = clients
            credentials = {"username": seed["username"], "password": "httpPass123"}
            logged_in = first.post("/api/v1/oauth/login/", json=credentials)
            assert logged_in.status_code == 200
            tokens = logged_in.json()["data"]
            headers = {"Authorization": f"Bearer {tokens['accessToken']}"}
            assert second.get("/api/v1/oauth/info/", headers=headers).status_code == 200
            assert first.post("/api/v1/oauth/logout/", headers=headers).status_code == 200
            assert second.get("/api/v1/oauth/info/", headers=headers).status_code == 401

            tokens = first.post("/api/v1/oauth/login/", json=credentials).json()["data"]

            def refresh(client):
                return client.post("/api/v1/oauth/refresh-token/", json={"refreshToken": tokens["refreshToken"]})

            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(refresh, clients))
            assert sorted(result.status_code for result in results) == [200, 401]
            rotated = next(result.json()["data"] for result in results if result.status_code == 200)
            headers = {"Authorization": f"Bearer {rotated['accessToken']}"}
            redis.stop()
            for client in clients:
                assert client.get("/health/live").status_code == 200
                assert client.get("/health/ready").status_code == 503
                assert client.get("/api/v1/oauth/info/", headers=headers).status_code == 503
                assert client.post("/api/v1/oauth/logout/", headers=headers).status_code == 503
                assert client.post("/api/v1/oauth/refresh-token/", json={"refreshToken": rotated["refreshToken"]}).status_code == 503
                assert client.put("/api/v1/information/password", headers=headers, json={
                    "oldPassword": "httpPass123", "newPassword": " a new HTTP passphrase ",
                    "confirmPassword": " a new HTTP passphrase ",
                }).status_code == 503
            redis.start()
            assert first.post("/api/v1/oauth/login/", json=credentials).status_code == 200
            assert second.get("/api/v1/oauth/info/", headers=headers).status_code == 200
            changed = first.put("/api/v1/information/password", headers=headers, json={
                "oldPassword": "httpPass123", "newPassword": " a new HTTP passphrase ",
                "confirmPassword": " a new HTTP passphrase ",
            })
            assert changed.status_code == 200 and changed.json()["code"] == 20000
            assert second.get("/api/v1/oauth/info/", headers=headers).status_code == 401
            assert second.post("/api/v1/oauth/refresh-token/", json={"refreshToken": rotated["refreshToken"]}).status_code == 401

            with Redis.from_url(redis.url) as counters:
                keys = list(counters.scan_iter("login:*"))
                if keys:
                    counters.delete(*keys)

            def failed_login(index):
                client = clients[index % 2]
                return client.post("/api/v1/oauth/login/", json={
                    "username": f"unknown-{index}", "password": "invalid",
                }, headers={"X-Forwarded-For": f"192.0.2.{index + 1}"})

            with ThreadPoolExecutor(max_workers=8) as pool:
                attempts = list(pool.map(failed_login, range(65)))
            assert sum(response.status_code == 401 for response in attempts) == 60
            assert sum(response.status_code == 429 for response in attempts) == 5
            for response in attempts:
                if response.status_code == 429:
                    assert 1 <= int(response.headers["Retry-After"]) <= 60
