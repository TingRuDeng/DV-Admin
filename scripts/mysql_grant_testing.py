"""Utilities for disposable MySQL 8 grant-boundary probes, not application code."""

from __future__ import annotations

import os
import re
import time

SCHEMA_PATTERN = re.compile(r"dv_admin_grant_test_[0-9a-f]{32}\Z")
ISOLATIONS = ("READ COMMITTED", "REPEATABLE READ")


def deadlock_count() -> int:
    import pymysql

    with pymysql.connect(**credentials(), autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT FROM information_schema.INNODB_METRICS WHERE NAME='lock_deadlocks'")
            return int(cursor.fetchone()[0])


def mysql_errno(error: BaseException) -> int | None:
    """Unwrap ORM exceptions without parsing translated error messages."""
    seen = set()
    while isinstance(error, BaseException) and id(error) not in seen:
        seen.add(id(error))
        if error.args and isinstance(error.args[0], int):
            return error.args[0]
        nested = next((arg for arg in error.args if isinstance(arg, BaseException)), None)
        error = nested or error.__cause__ or error.__context__
    return None


class WriteFaultBlocker:
    """Hold a test-only row; optionally close a cycle after the real service writes."""

    def __enter__(self):
        import pymysql

        self.connection = pymysql.connect(**credentials(), database=schema_name(), autocommit=True)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS grant_fault_marker (id INT PRIMARY KEY, value INT) ENGINE=InnoDB")
                cursor.executemany("REPLACE INTO grant_fault_marker VALUES (%s, 0)", [(n,) for n in range(100)])
                self.connection.begin()
                # Ensure this transaction outweighs the small service mutation as a victim.
                cursor.execute("UPDATE grant_fault_marker SET value=1")
                cursor.execute("SELECT CONNECTION_ID()")
                self.connection_id = cursor.fetchone()[0]
            return self
        except BaseException:
            self.connection.close()
            raise

    def close_cycle(self, table: str, pk: int):
        if not re.fullmatch(r"[a-z_]+", table):
            raise ValueError("Unexpected model table")
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT id FROM `{table}` WHERE id=%s FOR UPDATE", (pk,))

    def __exit__(self, *exc):
        try:
            self.connection.rollback()
        finally:
            self.connection.close()


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
