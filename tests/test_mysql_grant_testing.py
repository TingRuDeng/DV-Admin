"""Safety guards for the disposable MySQL runner; no database dependency."""

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from scripts import mysql_grant_testing as helper

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mysql_grant_runner", ROOT / "scripts/verify_mysql_grants.py")
runner = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {"mysql_grant_testing": helper}):
    spec.loader.exec_module(runner)


class MySQLGrantTestingTests(unittest.TestCase):
    def test_rejects_remote_hosts_and_existing_database_names(self):
        for host in ("db.example.com", "192.168.0.1"):
            with self.subTest(host=host), patch.dict(os.environ, {"GRANT_MYSQL_HOST": host}):
                with self.assertRaises(ValueError):
                    helper.credentials()
        for name in ("dv_admin", "mysql", "dv_admin_grant_test_existing", "x`; DROP DATABASE mysql"):
            with self.subTest(name=name), patch.dict(os.environ, {"GRANT_MYSQL_DATABASE": name}):
                with self.assertRaises(ValueError):
                    helper.schema_name()

    def test_rejects_unknown_isolation(self):
        with patch.dict(os.environ, {"GRANT_MYSQL_ISOLATION": "READ UNCOMMITTED"}):
            with self.assertRaises(ValueError):
                helper.isolation()

    def test_runner_drops_only_owned_schema_even_on_probe_failure(self):
        for failure in (None, RuntimeError("probe failed"), subprocess.TimeoutExpired("probe", 120)):
            with self.subTest(failure=failure):
                connect = MagicMock()
                cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
                cursor.fetchone.return_value = ("8.0.43",)
                with (
                    patch.dict(sys.modules, {"pymysql": SimpleNamespace(connect=connect)}),
                    patch.dict(os.environ, {"GRANT_MYSQL_PASSWORD": "test-only", "PYTHONOPTIMIZE": ""}),
                    patch.object(runner, "credentials", return_value={}),
                    patch.object(sys, "argv", ["runner", "--backend", "fastapi", "--isolation", "READ COMMITTED"]),
                    patch.object(runner.subprocess, "run", side_effect=failure) as run,
                ):
                    if failure:
                        with self.assertRaises(type(failure)):
                            runner.main()
                    else:
                        runner.main()
                statements = [call.args[0] for call in cursor.execute.call_args_list]
                name = run.call_args.kwargs["env"]["GRANT_MYSQL_DATABASE"]
                self.assertRegex(name, helper.SCHEMA_PATTERN)
                self.assertEqual(statements, [
                    "SELECT VERSION()",
                    f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4",
                    f"DROP DATABASE `{name}`",
                ])
                self.assertTrue(run.call_args.kwargs["check"])
                self.assertEqual(run.call_args.kwargs["timeout"], 120)


if __name__ == "__main__":
    unittest.main()
