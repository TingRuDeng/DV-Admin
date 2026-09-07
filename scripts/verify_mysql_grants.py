"""Run real ORM grant races in fresh, disposable MySQL databases."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import uuid
from pathlib import Path

from mysql_grant_testing import ISOLATIONS, credentials

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    import pymysql

    if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
        raise RuntimeError("Assertions must be enabled for this regression gate")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=("django", "fastapi"))
    parser.add_argument("--isolation", choices=ISOLATIONS)
    args = parser.parse_args()
    project = ROOT / ("backend" if args.backend == "django" else "fastapi")
    probe = (
        project / "drf_admin/utils/mysql_grant_probe.py"
        if args.backend == "django" else project / "tests/mysql_grant_probe.py"
    )
    # Each run owns exactly this generated schema; never reset a configured application DB.
    with pymysql.connect(**credentials(), autocommit=True) as admin:
        with admin.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            if not version.startswith("8.") or "MariaDB" in version:
                raise ValueError("This gate requires MySQL 8 with performance_schema enabled")
            for level in (args.isolation,) if args.isolation else ISOLATIONS:
                name = f"dv_admin_grant_test_{uuid.uuid4().hex}"
                cursor.execute(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4")
                env = os.environ | {
                    "GRANT_MYSQL_DATABASE": name,
                    "GRANT_MYSQL_ISOLATION": level,
                    "PYTHONPATH": os.pathsep.join((str(project), str(ROOT))),
                    "APP_ENV": "test",
                    "ENVIRONMENT": "test",
                    "DEBUG": "False",
                    "ALLOWED_HOSTS": "testserver,127.0.0.1,localhost",
                    "EXTRA_INSTALLED_APPS": "",
                    "DATABASE_URL": "sqlite:///:memory:",
                    "REDIS_HOST": "",
                    "SECRET_KEY": "mysql-grant-test-only-key-not-for-production-use-0123456789-abcdef",
                    "PASSWORD_MIN_LENGTH": "15",
                    "PASSWORD_MAX_LENGTH": "128",
                    "DEFAULT_PASSWORD": "MySQL grant test passphrase",
                    "DEFAULT_PWD": "MySQL grant test passphrase",
                }
                try:
                    print(f"{args.backend}: MySQL {version}, {level}, disposable schema", flush=True)
                    subprocess.run([sys.executable, str(probe)], cwd=project, env=env, check=True, timeout=120)
                finally:
                    cursor.execute(f"DROP DATABASE `{name}`")


if __name__ == "__main__":
    main()
