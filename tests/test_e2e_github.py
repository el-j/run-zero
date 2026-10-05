"""
E2E cache canary against real GitHub Actions (el-j/run-zero#74). Gated on secrets.

Dispatches tests/e2e/runzero-cache-canary.yml (copied into a disposable repository RunZero
serves) twice and asserts that the second run hit every cache within budget:

- `actions/setup-node` logs "Found in cache" (tool cache mounted and RUNNER_TOOL_CACHE set),
- pnpm 11 resolves the Verdaccio proxy and downloads nothing (store mounted),
- `playwright install chromium` takes under 10s (browsers cached),
- the whole setup stays under RUNZERO_E2E_SETUP_BUDGET seconds (default 120).

Skips cleanly unless RUNZERO_E2E_REPO (owner/name) and RUNZERO_E2E_TOKEN (a token with
`actions:write` on that repository) are set. Optional: RUNZERO_E2E_RUNS_ON (JSON label list
passed to the workflow), RUNZERO_E2E_REF (default: the repository's default branch).
"""

import calendar
import json
import os
import re
import time
import unittest
import urllib.request
from typing import Any

API = "https://api.github.com"
WORKFLOW = "runzero-cache-canary.yml"
MARKER = re.compile(r"RUNZERO_CANARY (\w+)=(\S*)")
PLAYWRIGHT_BUDGET_SECONDS = 10
RUN_TIMEOUT_SECONDS = 25 * 60


def parse_markers(log: str) -> dict[str, str]:
    """`RUNZERO_CANARY key=value` lines of a job log (the last value of a key wins)."""
    return {m.group(1): m.group(2) for m in MARKER.finditer(log)}


def cache_failures(log: str, setup_budget: int) -> list[str]:
    """Why a warm canary run's log shows a cache miss; [] when every cache hit within budget."""
    markers = parse_markers(log)
    failures = []
    if "Found in cache" not in log:
        failures.append("setup-node did not find Node in the tool cache")
    if ":49501" not in markers.get("registry", ""):
        failures.append(f"pnpm resolved registry {markers.get('registry')!r}, not the Verdaccio proxy")
    if markers.get("pnpm_downloaded", "") not in ("", "0"):
        failures.append(f"pnpm downloaded {markers['pnpm_downloaded']} packages (store not reused)")
    for key, budget in (("playwright_seconds", PLAYWRIGHT_BUDGET_SECONDS), ("setup_seconds", setup_budget)):
        value = markers.get(key)
        if value is None or not value.isdigit():
            failures.append(f"{key} missing from the log")
        elif int(value) >= budget:
            failures.append(f"{key}={value} is over the {budget}s budget")
    return failures


class TestCanaryEvaluation(unittest.TestCase):
    """The log evaluation itself, runnable without secrets."""

    WARM = (
        "Found in cache @ /opt/hostedtoolcache/node/24.1.0/arm64\n"
        "RUNZERO_CANARY registry=http://localhost:49501/\n"
        "RUNZERO_CANARY pnpm_downloaded=0\n"
        "RUNZERO_CANARY playwright_seconds=2\n"
        "RUNZERO_CANARY setup_seconds=41\n"
    )

    def test_warm_run_passes(self):
        self.assertEqual(cache_failures(self.WARM, 120), [])

    def test_every_miss_is_reported(self):
        cold = "RUNZERO_CANARY registry=https://registry.npmjs.org/\nRUNZERO_CANARY pnpm_downloaded=212\nRUNZERO_CANARY playwright_seconds=48\n"
        failures = cache_failures(cold, 120)
        self.assertEqual(len(failures), 5, failures)
        self.assertIn("setup_seconds missing from the log", failures)

    def test_budget_is_configurable(self):
        self.assertEqual(cache_failures(self.WARM, 30), ["setup_seconds=41 is over the 30s budget"])


@unittest.skipUnless(os.getenv("RUNZERO_E2E_REPO") and os.getenv("RUNZERO_E2E_TOKEN"), "set RUNZERO_E2E_REPO and RUNZERO_E2E_TOKEN to run the cache canary")
class TestCacheCanary(unittest.TestCase):
    def setUp(self):
        self.repo = os.environ["RUNZERO_E2E_REPO"]
        self.token = os.environ["RUNZERO_E2E_TOKEN"]
        self.budget = int(os.getenv("RUNZERO_E2E_SETUP_BUDGET", "120"))

    def _api(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        req = urllib.request.Request(
            f"{API}{path}",
            data=json.dumps(body).encode() if body is not None else None,
            method=method,
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
        return json.loads(raw) if raw and resp.headers.get_content_type() == "application/json" else raw.decode("utf-8", "replace")

    def _dispatch_and_wait(self) -> dict[str, Any]:
        ref = os.getenv("RUNZERO_E2E_REF") or self._api("GET", f"/repos/{self.repo}")["default_branch"]
        inputs = {"runs_on": os.getenv("RUNZERO_E2E_RUNS_ON", '["self-hosted", "local"]')}
        started = time.time()
        self._api("POST", f"/repos/{self.repo}/actions/workflows/{WORKFLOW}/dispatches", {"ref": ref, "inputs": inputs})
        deadline = started + RUN_TIMEOUT_SECONDS
        run = None
        while time.time() < deadline:
            time.sleep(10)
            runs = self._api("GET", f"/repos/{self.repo}/actions/workflows/{WORKFLOW}/runs?event=workflow_dispatch&per_page=5")["workflow_runs"]
            fresh = [r for r in runs if calendar.timegm(time.strptime(r["created_at"], "%Y-%m-%dT%H:%M:%SZ")) >= started - 5]
            run = fresh[-1] if fresh else None  # newest first: the earliest run after our dispatch is ours
            if run and run["status"] == "completed":
                return run
        self.fail(f"canary run did not complete within {RUN_TIMEOUT_SECONDS}s (last seen: {run and run['status']})")

    def _job_log(self, run: dict[str, Any]) -> str:
        (job,) = self._api("GET", f"/repos/{self.repo}/actions/runs/{run['id']}/jobs")["jobs"]
        return str(self._api("GET", f"/repos/{self.repo}/actions/jobs/{job['id']}/logs"))

    def test_second_run_hits_every_cache(self):
        first = self._dispatch_and_wait()  # warms the caches; may legitimately miss
        self.assertEqual(first["conclusion"], "success", first["html_url"])
        second = self._dispatch_and_wait()
        self.assertEqual(second["conclusion"], "success", second["html_url"])
        self.assertEqual(cache_failures(self._job_log(second), self.budget), [], second["html_url"])


if __name__ == "__main__":
    unittest.main()
