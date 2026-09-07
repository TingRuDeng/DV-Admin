"""An isolated Redis process for integration tests, never a user's instance."""

from __future__ import annotations

import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path


class RedisTestServer:
    def __init__(self) -> None:
        self.process: subprocess.Popen | None = None
        self.directory = tempfile.TemporaryDirectory(prefix="dv-admin-redis-")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            self.port = listener.getsockname()[1]
        self.url = f"redis://127.0.0.1:{self.port}/0"

    def start(self) -> None:
        executable = shutil.which("redis-server")
        if executable is None:
            raise RuntimeError("redis-server is required for security integration tests")
        self.process = subprocess.Popen(
            [executable, "--bind", "127.0.0.1", "--port", str(self.port),
             "--dir", str(Path(self.directory.name)), "--save", "",
             "--appendonly", "yes", "--appendfsync", "always"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError("test Redis exited before becoming ready")
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=0.1):
                    return
            except OSError:
                time.sleep(0.02)
        raise RuntimeError("test Redis did not become ready")

    def stop(self) -> None:
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
            self.process = None

    def __enter__(self) -> RedisTestServer:
        try:
            self.start()
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, *_args: object) -> None:
        self.stop()
        self.directory.cleanup()
