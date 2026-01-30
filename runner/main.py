from __future__ import annotations

import asyncio
import json
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from runner.jobs import dispatch_job
from runner.settings import runner_settings


def _normalize_db_url(url: str) -> str:
    # Accept postgres:// and normalize to postgresql://
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


# Database setup (runner connects to same Postgres as control plane)
DATABASE_URL = _normalize_db_url(str(runner_settings.database_url))
if not DATABASE_URL.startswith("postgresql://"):
    raise RuntimeError("V2 runner requires PostgreSQL DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def create_runner_app() -> FastAPI:
    app = FastAPI(title="DOMAIN_EXPANSION Runner", version="2.0.0")

    def require_token(x_runner_token: str | None):
        if not x_runner_token or x_runner_token != runner_settings.runner_token:
            raise HTTPException(status_code=401, detail="invalid_runner_token")

    def _validate_job_type(job_type: str) -> None:
        """Validate job type against allowlist."""
        if runner_settings.runner_allowlist:
            allowed = [j.strip() for j in runner_settings.runner_allowlist.split(",")]
            if job_type not in allowed:
                raise HTTPException(
                    status_code=403, detail=f"Job type '{job_type}' not in allowlist"
                )

    @app.get("/healthz")
    def healthz(x_runner_token: str | None = Header(default=None)):
        require_token(x_runner_token)
        return {"status": "ok", "runner_instance": "default"}

    @app.post("/runner/execute")
    async def runner_execute(
        request: dict, x_runner_token: str | None = Header(default=None)
    ):
        """Execute a job.

        V2 contract:
        1. Validate token
        2. Validate payload includes job_id and job_type
        3. Immediately write status=running to ops_jobs
        4. Dispatch job handler in background
        5. Return quickly (job processes async)
        """
        require_token(x_runner_token)

        job_id = request.get("job_id")
        job_type = request.get("job_type")
        payload = request.get("payload", {})

        if not job_id or not job_type:
            raise HTTPException(
                status_code=400, detail="Missing required fields: job_id, job_type"
            )

        _validate_job_type(job_type)

        # Update ops_jobs to running immediately
        db = SessionLocal()
        try:
            db.execute(
                text(
                    """
                    UPDATE ops_jobs
                    SET status = 'running', updated_at = :now, runner_instance = :instance
                    WHERE id = :job_id::uuid
                    """
                ),
                {
                    "job_id": job_id,
                    "now": datetime.utcnow(),
                    "instance": "default",
                },
            )
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update job status: {str(e)}")
        finally:
            db.close()

        # Dispatch job in background (non-blocking)
        asyncio.create_task(
            _execute_job_async(job_id, job_type, payload)
        )

        return {
            "status": "accepted",
            "job_id": job_id,
            "job_type": job_type,
            "runner_instance": "default",
        }

    async def _execute_job_async(job_id: str, job_type: str, payload: dict) -> None:
        """Execute job asynchronously and update ops_jobs on completion.
        
        V2 contract: Bounded result/error sizes, guaranteed update in finally block.
        """
        db = SessionLocal()
        try:
            result = await dispatch_job(job_type, payload)
            # Bound result size (max 10KB JSON)
            result_json = json.dumps(result) if isinstance(result, dict) else json.dumps({"result": result})
            if len(result_json) > 10000:
                result_json = json.dumps({"error": "Result too large", "truncated": True})
            
            # Update to succeeded
            db.execute(
                text(
                    """
                    UPDATE ops_jobs
                    SET status = 'succeeded', updated_at = :now, result = :result::jsonb
                    WHERE id = :job_id::uuid
                    """
                ),
                {
                    "job_id": job_id,
                    "now": datetime.utcnow(),
                    "result": result_json,
                },
            )
            db.commit()
        except Exception as e:
            # Bound error size (max 500 chars)
            error_msg = str(e)[:500]
            try:
                db.execute(
                    text(
                        """
                        UPDATE ops_jobs
                        SET status = 'failed', updated_at = :now, error = :error
                        WHERE id = :job_id::uuid
                        """
                    ),
                    {
                        "job_id": job_id,
                        "now": datetime.utcnow(),
                        "error": error_msg,
                    },
                )
                db.commit()
            except Exception as update_error:
                # If update fails, log but don't raise (we're in error handler already)
                db.rollback()
        finally:
            db.close()

    # Legacy endpoint (for backward compatibility)
    @app.post("/jobs/run")
    def jobs_run(payload: dict, x_runner_token: str | None = Header(default=None)):
        require_token(x_runner_token)
        return {
            "status": "error",
            "message": "Use /runner/execute endpoint instead",
        }

    return app


app = create_runner_app()
