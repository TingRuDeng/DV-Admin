"""Build and exercise the shipped images against disposable services, never host data."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from production_media_probe import assert_media_read, upload_media

ROOT = Path(__file__).resolve().parents[1]


def docker(*args: str, check: bool = True) -> str:
    timeout = 900 if args[0] in {"build", "pull"} else 90
    try:
        result = subprocess.run(
            ["docker", *args], text=True, capture_output=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        if check:
            raise
        return ""
    if check and result.returncode:
        raise RuntimeError(
            f"docker {args[0]} failed: {result.stderr[-5000:]} {result.stdout[-5000:]}"
        )
    return result.stdout.strip()


def wait_status(url: str, expected: int, timeout: int = 60) -> None:
    deadline = time.monotonic() + timeout
    status = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
        except (OSError, TimeoutError):
            status = None
        if status == expected:
            return
        time.sleep(0.5)
    raise AssertionError(f"{url}: expected {expected}, last status {status}")


def verify(backend: str, build: bool) -> None:
    name = "dv-image-test-" + uuid.uuid4().hex[:12]
    image = f"dv-admin-{backend}:audit"
    compose_env = {
        **os.environ,
        "SECRET_KEY": "isolated-config-check-key",
        "DEFAULT_PWD": "Isolated config passphrase",
        "DEFAULT_PASSWORD": "Isolated config passphrase",
        "DATABASE_URL": "mysql://test:test@db/test",
    }
    variant = "django" if backend == "backend" else "fastapi"
    config = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(ROOT / "deploy/compose.production.yml"),
            "-f",
            str(ROOT / f"deploy/compose.{variant}.yml"),
            "config",
            "--format",
            "json",
        ],
        env=compose_env,
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    services = json.loads(config.stdout)["services"]
    assert any(
        m["target"] == "/data/media" and m.get("read_only")
        for m in services["nginx"]["volumes"]
    )
    assert any(
        m["target"] == "/data/media" and not m.get("read_only")
        for m in services["api"]["volumes"]
    )
    assert (
        services["api"]["depends_on"]["migrate"]["condition"]
        == "service_completed_successfully"
    )
    versions = json.loads((ROOT / "deploy/runtime-versions.json").read_text())
    if build:
        print(f"Building {image}", flush=True)
        docker(
            "build",
            "-f",
            str(ROOT / backend / "docker/Dockerfile"),
            "-t",
            image,
            str(ROOT / backend),
        )
    inspect = json.loads(docker("image", "inspect", image))[0]
    assert inspect["Config"]["User"] == "10001:10001"
    package = "app.core" if backend == "fastapi" else "drf_admin.utils"
    distribution = "dv-admin-fastapi" if backend == "fastapi" else "backend"
    probe = (
        "import os,sys,json,importlib.util; from importlib import metadata; "
        "assert os.getuid()==10001; assert sys.version_info[:2]==(3,11); "
        "assert importlib.util.find_spec('pytest') is None; "
        "assert importlib.util.find_spec('ruff') is None; "
        f"d=metadata.distribution('{distribution}'); "
        "assert not json.loads(d.read_text('direct_url.json')).get('dir_info',{}).get('editable'); "
        f"assert d.locate_file('{package.replace('.', '/')}/data/common-passwords.txt').is_file(); "
        f"assert d.locate_file('{package.replace('.', '/')}/data/LICENSE.seclists').is_file(); "
        "print('non-root, Python 3.11, noneditable wheel, no dev tools, packaged password data: OK')"
    )
    try:
        assert (
            docker(
                "run", "--rm", "--name", f"{name}-version", image, "uv", "--version"
            ).split()[1]
            == versions["uv_version"]
        )
        print(
            docker(
                "run",
                "--rm",
                "--name",
                f"{name}-wheel",
                "--workdir",
                "/tmp",
                image,
                "python",
                "-c",
                probe,
            ),
            flush=True,
        )
    finally:
        docker("rm", "-f", f"{name}-version", f"{name}-wheel", check=False)
    env = {
        "SECRET_KEY": "isolated-image-verification-key-not-a-deployment-secret-2026",
        "DATABASE_URL": "sqlite:///data/db/smoke.sqlite3",
        "DEBUG": "False",
    }
    if backend == "fastapi":
        env.update(
            APP_ENV="production",
            DEFAULT_PASSWORD="Isolated image test passphrase",
            REDIS_URL=f"redis://{name}-redis:6379/0",
        )
        migration = [
            "python",
            "-m",
            "tortoise",
            "-c",
            "app.db.migration_config.TORTOISE_ORM",
            "migrate",
        ]
    else:
        env.update(
            DATABASE_URL="sqlite:////data/db/smoke.sqlite3",
            ENVIRONMENT="pro",
            DEFAULT_PWD="Isolated image test passphrase",
            REDIS_HOST=f"{name}-redis",
            REDIS_PORT="6379",
        )
        migration = ["python", "/app/manage.py", "migrate", "--env", "pro", "--noinput"]
    arguments = [
        "--network",
        name,
        "-v",
        f"{name}-db:/data/db",
        "-v",
        f"{name}-media:/data/media",
    ]
    for key, value in env.items():
        arguments.extend(["-e", f"{key}={value}"])
    containers = [f"{name}-nginx", f"{name}-api", f"{name}-migrate", f"{name}-redis"]
    try:
        docker("network", "create", name)
        docker("volume", "create", f"{name}-db")
        docker("volume", "create", f"{name}-media")
        # No Redis exists yet: migration must remain an offline database-only entry point.
        docker(
            "run", "--rm", "--name", f"{name}-migrate", *arguments, image, *migration
        )
        print(f"{backend}: production migration without Redis: OK", flush=True)
        docker(
            "run", "-d", "--name", f"{name}-redis", "--network", name, "redis:7-alpine"
        )
        api_arguments = [
            "run",
            "-d",
            "--name",
            f"{name}-api",
            "--network-alias",
            "api",
            *arguments,
            "-p",
            "127.0.0.1::8000",
            image,
        ]
        docker(*api_arguments)
        info = json.loads(docker("inspect", f"{name}-api"))[0]
        port = info["NetworkSettings"]["Ports"]["8000/tcp"][0]["HostPort"]
        url = f"http://127.0.0.1:{port}"
        wait_status(url + "/health/live", 200)
        wait_status(url + "/health/ready", 200)
        docker(
            "create",
            "--name",
            f"{name}-nginx",
            "--network",
            name,
            "-v",
            f"{name}-media:/data/media:ro",
            "-p",
            "127.0.0.1::80",
            "nginx:alpine",
        )
        # Copy the shipped config to avoid host Desktop file-sharing/TCC dependencies.
        docker(
            "cp",
            str(ROOT / "fastapi/docker/nginx.conf"),
            f"{name}-nginx:/etc/nginx/nginx.conf",
        )
        docker("start", f"{name}-nginx")
        proxy = json.loads(docker("inspect", f"{name}-nginx"))[0]
        proxy_port = proxy["NetworkSettings"]["Ports"]["80/tcp"][0]["HostPort"]
        proxy_url = f"http://127.0.0.1:{proxy_port}"
        wait_status(proxy_url + "/health/ready", 200)
        path, content = upload_media(backend, f"{name}-api", proxy_url, docker)
        assert_media_read(proxy_url, path, content)
        docker(
            "exec",
            f"{name}-nginx",
            "sh",
            "-c",
            "if touch /data/media/should-not-exist; then exit 1; else exit 0; fi",
        )
        health = inspect["Config"]["Healthcheck"]["Test"]
        assert health[0] == "CMD-SHELL"
        docker("exec", f"{name}-api", "sh", "-c", health[1])
        docker("stop", f"{name}-redis")
        wait_status(url + "/health/ready", 503)
        wait_status(proxy_url + "/health/ready", 503)
        wait_status(url + "/health/live", 200)
        docker("start", f"{name}-redis")
        wait_status(url + "/health/ready", 200)
        docker("rm", "-f", f"{name}-api")
        docker(*api_arguments)
        info = json.loads(docker("inspect", f"{name}-api"))[0]
        port = info["NetworkSettings"]["Ports"]["8000/tcp"][0]["HostPort"]
        wait_status(f"http://127.0.0.1:{port}/health/ready", 200)
        assert_media_read(proxy_url, path, content)
        print(
            f"{backend}: Nginx read-only volume and upload survives API container replacement: OK",
            flush=True,
        )
        print(
            f"{backend}: actual workers, Docker probe, Redis outage 503/live 200, recovery: OK; image={inspect['Id']}",
            flush=True,
        )
    except Exception:
        print(docker("logs", "--tail", "60", f"{name}-api", check=False), flush=True)
        raise
    finally:
        for container in containers:
            docker("rm", "-f", container, check=False)
        docker("volume", "rm", f"{name}-db", check=False)
        docker("volume", "rm", f"{name}-media", check=False)
        docker("network", "rm", name, check=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend", choices=("backend", "fastapi", "all"), default="all"
    )
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()
    for project in (
        ("backend", "fastapi") if args.backend == "all" else (args.backend,)
    ):
        verify(project, not args.skip_build)
