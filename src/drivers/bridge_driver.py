"""
RunZero Remote VM Bridge Driver Client
Proxies VM driver operations (OrbStack, Canonical Multipass, WSL2) to a Host VM Bridge server.
Enables full VM hybrid runner capabilities when the autoscaler runs inside a Docker container.
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from . import RunnerDriver, RunnerInfo

DEFAULT_BRIDGE_URL = "http://host.docker.internal:49504"


class BridgeVMDriver(RunnerDriver):
    """Proxies runner management requests over HTTP to the Host VM Bridge."""

    def __init__(self, target_backend: str, bridge_url: Optional[str] = None):
        """Wrap the given backend name (e.g. "orbstack-vm") behind a bridge at `bridge_url`.

        `bridge_url` falls back to the HOST_VM_BRIDGE_URL env var, then DEFAULT_BRIDGE_URL.
        """
        self.target_backend = target_backend.lower().strip()
        url = bridge_url or os.getenv("HOST_VM_BRIDGE_URL") or DEFAULT_BRIDGE_URL
        self.bridge_url = url.rstrip("/")

    def name(self) -> str:
        """Return the wrapped backend's identifier (e.g. "orbstack-vm"), not "bridge" itself."""
        return self.target_backend

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None, timeout: float = 30.0) -> Dict[str, Any]:
        url = f"{self.bridge_url}{path}"
        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        headers = {"Content-Type": "application/json"} if body_bytes else {}

        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else {}
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ConnectionError) as e:
            return {"error": str(e)}

    def is_available(self) -> bool:
        """Check if bridge server is reachable and reports target_backend as available."""
        res = self._request("GET", "/health", timeout=2.0)
        if res.get("status") == "ok":
            available_vm_drivers = res.get("available_vm_drivers", [])
            all_drivers = res.get("all_drivers", [])
            return self.target_backend in available_vm_drivers or self.target_backend in all_drivers
        return False

    def spawn_runner(
        self,
        repo: Optional[str] = None,
        org: Optional[str] = None,
        arch: str = "arm64",
        labels: Optional[str] = None,
        access_token: Optional[str] = None,
        cache_mounts: Optional[Dict[str, str]] = None,
        proxies_enabled: bool = True,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """POST a spawn request to the bridge's `/api/drivers/{backend}/spawn` endpoint.

        Returns the runner id the bridge reports, or None if the request failed or errored
        (network error, timeout, non-success bridge response).
        """
        payload = {
            "repo": repo,
            "org": org,
            "arch": arch,
            "labels": labels,
            "access_token": access_token,
            "cache_mounts": cache_mounts,
            "proxies_enabled": proxies_enabled,
            "extra_env": extra_env
        }
        res = self._request("POST", f"/api/drivers/{self.target_backend}/spawn", data=payload, timeout=60.0)
        if res.get("status") == "success":
            return res.get("runner_id")
        return None

    def list_runners(self) -> List[RunnerInfo]:
        """GET the bridge's `/api/drivers/{backend}/runners` endpoint and parse the runner list.

        Returns an empty list if the request fails or the bridge returns no runners.
        """
        res = self._request("GET", f"/api/drivers/{self.target_backend}/runners", timeout=10.0)
        runners_data = res.get("runners", [])
        runners: List[RunnerInfo] = []
        for r in runners_data:
            runners.append(RunnerInfo(
                id=r.get("id", ""),
                name=r.get("name", ""),
                status=r.get("status", ""),
                state=r.get("state", ""),
                target_repo=r.get("target_repo", ""),
                target_arch=r.get("target_arch", ""),
                backend=r.get("backend", self.target_backend),
                created_at=r.get("created_at")
            ))
        return runners

    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        """POST `runners` to the bridge's `/prune` endpoint; the bridge's own driver does the filtering.

        Fire-and-forget: the bridge's response (success or error) is not surfaced to the caller.
        """
        payload = {"runners": [r.to_dict() for r in runners]}
        self._request("POST", f"/api/drivers/{self.target_backend}/prune", data=payload, timeout=30.0)

    def destroy_runner(self, runner_id: str) -> bool:
        """POST a destroy request to the bridge's `/destroy` endpoint.

        Returns True only if the bridge reports `destroyed: true`; a request failure, timeout,
        or any other error is treated as False.
        """
        payload = {"runner_id": runner_id}
        res = self._request("POST", f"/api/drivers/{self.target_backend}/destroy", data=payload, timeout=30.0)
        return bool(res.get("destroyed", False))

    def cleanup_all(self) -> None:
        """POST a cleanup-all request to the bridge's `/cleanup` endpoint. Fire-and-forget."""
        self._request("POST", f"/api/drivers/{self.target_backend}/cleanup", timeout=60.0)

    def ensure_base_images_stopped(self) -> None:
        """POST to the bridge's `/ensure-base-stopped` endpoint (VM drivers only). Fire-and-forget.

        The bridge silently no-ops this for a backend whose real driver doesn't implement it
        (e.g. Docker); this proxy has no way to distinguish that from a successful call.
        """
        self._request("POST", f"/api/drivers/{self.target_backend}/ensure-base-stopped", timeout=15.0)

    def build_base_image(self, arch: str = "arm64") -> bool:
        """POST a golden-base-image build request to the bridge's `/build-base` endpoint (VM drivers only).

        Blocks up to 300s (a real build can take 15-25 minutes on the bridge side; this call
        will time out well before a slow build finishes, in which case it returns False even
        though the bridge's own build may still be running). Returns True only if the bridge
        reports `built: true`.
        """
        payload = {"arch": arch}
        res = self._request("POST", f"/api/drivers/{self.target_backend}/build-base", data=payload, timeout=300.0)
        return bool(res.get("built", False))
