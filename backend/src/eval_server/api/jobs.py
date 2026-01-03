from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..queue import JobState
from .queue_context import queue as _queue


router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCreateResponse(BaseModel):
    job_id: str


@router.post("/", response_model=JobCreateResponse, summary="Create job", description="Create a new job in the execution queue and return its id.")
def create_job() -> JobCreateResponse:
    jid = _queue.add_job()
    return JobCreateResponse(job_id=jid)


@router.get("/{job_id}", summary="Get job", description="Get a job by id, including status and progress.")
def get_job(job_id: str):
    try:
        return _queue.get_job(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="job not found")


@router.get("/", summary="List jobs", description="List jobs in the queue, optionally filtered by state.")
def list_jobs(state: Optional[JobState] = None):
    return _queue.list_jobs(state)


@router.post("/{job_id}/cancel", summary="Cancel job", description="Cancel a running job by id.")
def cancel_job(job_id: str):
    try:
        _queue.cancel_job(job_id, reason="cancelled via API")
        return {"status": "ok"}
    except KeyError:
        raise HTTPException(status_code=404, detail="job not found")
