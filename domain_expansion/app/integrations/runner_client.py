from __future__ import annotations

import httpx

from domain_expansion.app.settings import settings


class RunnerClient:
    """HTTP client to the runner service.

    V2 contract: control plane triggers runner jobs via outbound HTTP and records ops_jobs.
    """

    def __init__(self) -> None:
        if not settings.runner_url or not settings.runner_token_outbound:
            raise RuntimeError("Runner integration not configured (RUNNER_URL/RUNNER_TOKEN_OUTBOUND).")
        self.base_url = settings.runner_url.rstrip("/")
        self.token = settings.runner_token_outbound

    def _headers(self) -> dict[str, str]:
        return {"X-Runner-Token": self.token}

    async def healthz(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{self.base_url}/healthz", headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def execute_job(self, payload: dict, timeout: float = 10.0) -> dict:
        """Execute a job on the runner.

        V2 contract: Uses short timeout for Vercel safety.
        Runner should accept quickly and process asynchronously.
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                f"{self.base_url}/runner/execute", headers=self._headers(), json=payload
            )
            r.raise_for_status()
            return r.json()

    async def run_job(self, payload: dict) -> dict:
        """Legacy method name — use execute_job instead."""
        return await self.execute_job(payload, timeout=60.0)
