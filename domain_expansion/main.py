from fastapi import FastAPI

from domain_expansion.app.settings import settings
from domain_expansion.app.routers import ops as ops_router


def create_app() -> FastAPI:
    app = FastAPI(title="DOMAIN_EXPANSION Control Plane", version="2.0.0")

    # Routers
    app.include_router(ops_router.router, prefix="/api/v1")

    @app.get("/health")
    def health():
        """Health check endpoint (always available)."""
        return {"status": "ok", "app_env": settings.app_env}

    @app.get("/healthz")
    def healthz():
        """Health check endpoint (alias for /health)."""
        return {"status": "ok", "app_env": settings.app_env}

    return app


app = create_app()
