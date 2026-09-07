"""Utilities for disposable MySQL 8 grant-boundary probes, not application code."""

from __future__ import annotations

import os
import re
import time

SCHEMA_PATTERN = re.compile(r"dv_admin_grant_test_[0-9a-f]{32}\Z")
ISOLATIONS = ("READ COMMITTED", "REPEATABLE READ")


def credentials() -> dict:
    host = os.environ.get("GRANT_MYSQL_HOST", "127.0.0.1")
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Only a loopback disposable MySQL server is supported")
    return {
        "host": host,
        "port": int(os.environ.get("GRANT_MYSQL_PORT", "3306")),
        "user": os.environ.get("GRANT_MYSQL_USER", "root"),
        "password": os.environ["GRANT_MYSQL_PASSWORD"],
        "charset": "utf8mb4",
    }


def schema_name() -> str:
    name = os.environ["GRANT_MYSQL_DATABASE"]
    if not SCHEMA_PATTERN.fullmatch(name):
        raise ValueError("Refusing a non-disposable database name")
    return name


def isolation() -> str:
    value = os.environ["GRANT_MYSQL_ISOLATION"]
    if value not in ISOLATIONS:
        raise ValueError("Unsupported isolation level")
    return value


def wait_for_lock(waiter: int, blocker: int) -> None:
    """Observe an actual InnoDB wait, rather than infer contention from a sleep."""
    import pymysql

    with pymysql.connect(**credentials(), autocommit=True) as observer:
        deadline = time.monotonic() + 10
        with observer.cursor() as cursor:
            while time.monotonic() < deadline:
                cursor.execute(
                    "SELECT COUNT(*) FROM performance_schema.data_lock_waits w "
                    "JOIN performance_schema.threads r ON r.THREAD_ID=w.REQUESTING_THREAD_ID "
                    "JOIN performance_schema.threads b ON b.THREAD_ID=w.BLOCKING_THREAD_ID "
                    "WHERE r.PROCESSLIST_ID=%s AND b.PROCESSLIST_ID=%s",
                    (waiter, blocker),
                )
                if cursor.fetchone()[0]:
                    return
                time.sleep(0.02)
    raise AssertionError("Expected independent connection to wait on an InnoDB lock")
