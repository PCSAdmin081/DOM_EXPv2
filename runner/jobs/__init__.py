"""Job dispatcher for runner service.

V2 contract: Job handlers are stubs that validate inputs and return structured results.
"""

from __future__ import annotations


async def dispatch_job(job_type: str, payload: dict) -> dict:
    """Dispatch a job to the appropriate handler.

    V2 contract: Returns structured result with "not_implemented": true for stubs.
    """
    if job_type == "nearsight_collect_refresh":
        return await handle_nearsight_collect_refresh(payload)
    elif job_type == "captorator_compose":
        return await handle_captorator_compose(payload)
    elif job_type == "metrics_refresh":
        return await handle_metrics_refresh(payload)
    else:
        raise ValueError(f"Unknown job type: {job_type}")


async def handle_nearsight_collect_refresh(payload: dict) -> dict:
    """Nearsight collect and refresh job (stub).

    V2 contract: Validates inputs, returns structured result.
    """
    # Validate inputs
    if not payload:
        payload = {}
    # Stub implementation
    return {
        "not_implemented": True,
        "job_type": "nearsight_collect_refresh",
        "message": "Job handler not yet implemented",
        "payload": payload,
    }


async def handle_captorator_compose(payload: dict) -> dict:
    """Captorator composition job (stub).

    V2 contract: Validates inputs, returns structured result.
    """
    # Validate inputs
    if not payload:
        payload = {}
    # Stub implementation
    return {
        "not_implemented": True,
        "job_type": "captorator_compose",
        "message": "Job handler not yet implemented",
        "payload": payload,
    }


async def handle_metrics_refresh(payload: dict) -> dict:
    """Metrics refresh job (stub).

    V2 contract: Validates inputs, returns structured result.
    """
    # Validate inputs
    if not payload:
        payload = {}
    # Stub implementation
    return {
        "not_implemented": True,
        "job_type": "metrics_refresh",
        "message": "Job handler not yet implemented",
        "payload": payload,
    }
