"""FastAPI dependencies for authentication and authorization."""

from __future__ import annotations

from fastapi import Header, HTTPException

from domain_expansion.app.settings import settings


def require_ops_api_key(x_ops_key: str | None = Header(default=None, alias="X-Ops-Key")) -> str:
    """Require X-Ops-Key header matching OPS_API_KEY for ops endpoints.
    
    V2 contract: Ops endpoints are server-to-server only.
    """
    # In production, OPS_API_KEY is required
    if settings.app_env in ("prod", "production"):
        if not settings.ops_api_key:
            raise HTTPException(
                status_code=500,
                detail="OPS_API_KEY not configured (required in production)",
            )
        if not x_ops_key or x_ops_key != settings.ops_api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing X-Ops-Key")
        return x_ops_key
    
    # In development, validate if OPS_API_KEY is set
    if settings.ops_api_key:
        if not x_ops_key or x_ops_key != settings.ops_api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing X-Ops-Key")
        return x_ops_key
    
    # Dev mode: allow if OPS_API_KEY not set (for local testing)
    return x_ops_key or "dev-bypass"
