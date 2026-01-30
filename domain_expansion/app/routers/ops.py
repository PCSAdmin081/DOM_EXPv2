from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, text
from sqlalchemy.orm import Session

from domain_expansion.app.dependencies import require_ops_api_key
from domain_expansion.app.db.session import get_db
from domain_expansion.app.integrations.runner_client import RunnerClient
from domain_expansion.app.models.ops import JobStatus, OpsJob
from domain_expansion.app.settings import settings

router = APIRouter(
    tags=["ops"],
    dependencies=[Depends(require_ops_api_key)],
)


# Request/Response models
class CreateJobRequest(BaseModel):
    job_type: str
    payload: dict | None = None
    requested_by: str | None = None


class TriggerRunnerRequest(BaseModel):
    job_type: str
    payload: dict | None = None


# Ops Jobs endpoints
@router.post("/ops/jobs", response_model=dict)
def create_job(request: CreateJobRequest, db: Session = Depends(get_db)) -> dict:
    """Create a new ops job record.

    V2 contract: Creates ops_jobs record with status=queued.
    Does not trigger runner — use /ops/trigger_runner for that.
    """
    job = OpsJob(
        job_type=request.job_type,
        status=JobStatus.QUEUED,
        payload=request.payload,
        requested_by=request.requested_by,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": str(job.id), "status": job.status.value}


@router.get("/ops/jobs", response_model=dict)
def list_jobs(
    status: JobStatus | None = None,
    job_type: str | None = None,
    limit: int = 50,
    since: datetime | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """List ops jobs with optional filters.

    V2 contract: Fast DB query only (safe for Vercel).
    """
    # Enforce limits: default 50, hard cap 200, minimum 1
    if limit > 200:
        limit = 200
    if limit < 1:
        limit = 50
    
    query = db.query(OpsJob)
    if status:
        query = query.filter(OpsJob.status == status)
    if job_type:
        query = query.filter(OpsJob.job_type == job_type)
    if since:
        query = query.filter(OpsJob.created_at >= since)
    jobs = query.order_by(desc(OpsJob.created_at)).limit(limit).all()
    return {
        "jobs": [
            {
                "id": str(job.id),
                "job_type": job.job_type,
                "status": job.status.value,
                "requested_by": job.requested_by,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
            }
            for job in jobs
        ],
        "count": len(jobs),
    }


@router.get("/ops/jobs/{job_id}", response_model=dict)
def get_job(job_id: str, db: Session = Depends(get_db)) -> dict:
    """Get a specific ops job by ID."""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")
    job = db.query(OpsJob).filter(OpsJob.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": str(job.id),
        "job_type": job.job_type,
        "status": job.status.value,
        "requested_by": job.requested_by,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "payload": job.payload,
        "result": job.result,
        "error": job.error,
        "runner_instance": job.runner_instance,
    }


@router.post("/ops/jobs/{job_id}/cancel", response_model=dict)
def cancel_job(job_id: str, db: Session = Depends(get_db)) -> dict:
    """Cancel a job (records intent only; runner may honor).

    V2 contract: Only records cancellation intent. Runner may honor or ignore.
    """
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")
    job = db.query(OpsJob).filter(OpsJob.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in (JobStatus.SUCCEEDED, JobStatus.FAILED):
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    # Mark cancellation intent (runner may check this periodically)
    job.error = "Cancellation requested by user"
    db.commit()
    return {"job_id": job_id, "status": "cancel_requested", "message": "Cancellation intent recorded"}


@router.post("/ops/trigger_runner", response_model=dict)
async def trigger_runner(
    request: TriggerRunnerRequest, db: Session = Depends(get_db)
) -> dict:
    """Trigger a runner job.

    V2 contract:
    1. Creates ops_jobs record with status=queued
    2. Calls runner /runner/execute with job_id and payload
    3. If runner returns accepted: updates status to running
    4. If runner call fails: updates status to failed with error
    5. Uses short timeout (5-10 seconds max)
    """
    if not settings.runner_enabled:
        raise HTTPException(status_code=503, detail="Runner integration not enabled")
    if not settings.runner_url or not settings.runner_token_outbound:
        raise HTTPException(
            status_code=503, detail="Runner not configured (RUNNER_URL/RUNNER_TOKEN_OUTBOUND)"
        )

    # Create job record
    job = OpsJob(
        job_type=request.job_type,
        status=JobStatus.QUEUED,
        payload=request.payload,
        requested_by="api",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Call runner
    try:
        client = RunnerClient()
        runner_payload = {
            "job_id": str(job.id),
            "job_type": request.job_type,
            "payload": request.payload or {},
        }
        # Use short timeout for Vercel safety
        result = await client.execute_job(runner_payload, timeout=10.0)
        # Runner accepted — update status to running
        job.status = JobStatus.RUNNING
        job.runner_instance = result.get("runner_instance")
        db.commit()
        return {
            "job_id": str(job.id),
            "status": "running",
            "message": "Job accepted by runner",
        }
    except Exception as e:
        # Runner call failed — mark as failed
        job.status = JobStatus.FAILED
        job.error = str(e)[:500]  # Bound error length
        db.commit()
        raise HTTPException(
            status_code=502,
            detail=f"Runner call failed: {str(e)[:200]}",
        )


# Debug endpoints
@router.get("/ops/debug/env")
def debug_env():
    # No secrets.
    db_url = str(settings.database_url)
    dialect = "postgresql" if db_url.startswith(("postgresql://", "postgres://")) else "unknown"

    return {
        "app_env": settings.app_env,
        "database_url_present": bool(db_url),
        "detected_dialect": dialect,
        "db_schema": settings.db_schema,
        "feature_flags": {
            "NEARSIGHT_ENABLED": settings.nearsight_enabled,
            "CAPTORATOR_ENABLED": settings.captorator_enabled,
            "JOBS_ENABLED": settings.jobs_enabled,
            "NOTION_ENABLED": settings.notion_enabled,
            "RUNNER_ENABLED": settings.runner_enabled,
            "FEATURE_METRICS": settings.metrics_enabled,
        },
    }


@router.get("/ops/debug/db")
def debug_db(db: Session = Depends(get_db)):
    # Minimal sanity: can we SELECT 1
    can_select = False
    current_user = None
    try:
        db.execute(text("SELECT 1"))
        can_select = True
        try:
            current_user = db.execute(text("SELECT current_user")).scalar()
        except Exception:
            current_user = None
    except Exception:
        can_select = False

    return {
        "dialect": db.get_bind().dialect.name,
        "schema": settings.db_schema,
        "can_select": can_select,
        "current_user": current_user,
    }
