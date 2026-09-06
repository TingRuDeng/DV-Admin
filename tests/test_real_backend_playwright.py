"""真实后端 Playwright runner 的进程生命周期测试。"""

from __future__ import annotations

import os
import signal
import subprocess
import unittest
from unittest.mock import patch

from scripts.real_backend_playwright import (
    PLAYWRIGHT_TIMEOUT_SECONDS,
    run_real_backend_playwright,
)


RUNNER_ARGS = {
    "backend_name": "Django",
    "backend_url": "http://127.0.0.1:8769",
    "username": "admin",
    "password": "password",
    "notice_title": "notice",
    "notice_content": "content",
    "rbac_username": "rbac",
    "rbac_password": "password",
    "rbac_role_id": 1,
    "rbac_base_permission_ids": [1, 2],
    "rbac_granted_permission_ids": [3],
    "lifecycle_role_name": "role",
    "lifecycle_dept_name": "department",
}


class RealBackendPlaywrightRunnerTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.real_backend_playwright.subprocess.Popen")
    def test_sets_backend_specific_frontend_port_and_process_group(self, popen):
        process = popen.return_value
        process.wait.return_value = 0

        run_real_backend_playwright(**RUNNER_ARGS)

        args, kwargs = popen.call_args
        self.assertEqual(args[0], ["pnpm", "run", "test:e2e:real-backend"])
        self.assertEqual(kwargs["env"]["REAL_FRONTEND_PORT"], "9530")
        self.assertTrue(kwargs["start_new_session"])
        process.wait.assert_called_once_with(timeout=PLAYWRIGHT_TIMEOUT_SECONDS)

    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.real_backend_playwright.subprocess.Popen")
    def test_uses_a_different_default_port_for_fastapi(self, popen):
        process = popen.return_value
        process.wait.return_value = 0

        run_real_backend_playwright(**{**RUNNER_ARGS, "backend_name": "FastAPI"})

        self.assertEqual(popen.call_args.kwargs["env"]["REAL_FRONTEND_PORT"], "9531")

    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.real_backend_playwright.os.killpg")
    @patch("scripts.real_backend_playwright.subprocess.Popen")
    def test_timeout_terminates_the_whole_process_group(self, popen, killpg):
        process = popen.return_value
        process.pid = 321
        process.wait.side_effect = [
            subprocess.TimeoutExpired(
                ["pnpm", "run", "test:e2e:real-backend"],
                PLAYWRIGHT_TIMEOUT_SECONDS,
            ),
            None,
        ]

        with self.assertRaises(subprocess.TimeoutExpired):
            run_real_backend_playwright(**RUNNER_ARGS)

        killpg.assert_called_once_with(process.pid, signal.SIGTERM)
        self.assertEqual(process.wait.call_count, 2)

    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.real_backend_playwright.subprocess.Popen")
    def test_nonzero_playwright_exit_is_reported(self, popen):
        process = popen.return_value
        process.wait.return_value = 7

        with self.assertRaises(subprocess.CalledProcessError) as raised:
            run_real_backend_playwright(**RUNNER_ARGS)

        self.assertEqual(raised.exception.returncode, 7)


if __name__ == "__main__":
    unittest.main()
