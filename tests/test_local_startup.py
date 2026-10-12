"""Regression for the documented local API startup and input-free index route."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_API_KEY = "readme-refresh-not-a-real-key"


class LocalStartupTest(unittest.TestCase):
    def test_root_route_starts_without_calling_a_model(self) -> None:
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]

        with tempfile.TemporaryDirectory(prefix="ai-bootcamp-startup-") as home:
            env = {
                "HOME": home,
                "PATH": os.defpath,
                "OPENAI_API_KEY": TEST_API_KEY,
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            self._assert_index_served(port, env)

    def _assert_index_served(self, port: int, env: dict[str, str]) -> None:
        uvicorn = Path(sys.executable).with_name("uvicorn")
        command = [
            str(uvicorn),
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ]
        process = subprocess.Popen(
            command,
            cwd=REPO_ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        deadline = time.monotonic() + 8
        last_error: Exception | None = None
        try:
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    output, _ = process.communicate()
                    self.fail(
                        f"Uvicorn exited with status {process.returncode} before "
                        f"the root route responded. Output:\n{output}"
                    )
                try:
                    with opener.open(
                        f"http://127.0.0.1:{port}/", timeout=0.25
                    ) as response:
                        self.assertEqual(response.status, 200)
                        payload = json.loads(response.read())
                    self.assertEqual(payload["message"], "AI Agents Bootcamp API")
                    self.assertEqual(payload["docs"], "/docs")
                    self.assertIn("GET /story?topic=", payload["endpoints"])
                    return
                except (urllib.error.URLError, TimeoutError) as exc:
                    last_error = exc
                    time.sleep(0.1)

            process.terminate()
            output, _ = process.communicate(timeout=5)
            self.fail(
                f"Uvicorn did not serve the root route within 8 seconds. "
                f"Last request error: {last_error}. Output:\n{output}"
            )
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=2)


if __name__ == "__main__":
    unittest.main()
