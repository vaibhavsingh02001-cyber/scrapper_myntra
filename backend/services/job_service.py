import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.models.job import Job
from backend.models.result import Result
from backend.models.query_history import QueryHistory
from backend.models.schemas import ScrapeRequest, JobDetailResponse, ExportUrls

def create_job(db: Session, request: ScrapeRequest) -> Job:
    """Creates a new job in queued state."""
    job = Job(
        url=str(request.url),
        prompt=request.prompt,
        mode=request.mode,
        status="queued"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: str) -> JobDetailResponse:
    """Fetches job by ID and returns detailed response model with export URLs."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found."
        )

    result = db.query(Result).filter(Result.job_id == job_id).first()
    parsed_result = None
    record_count = 0

    if result and result.data:
        try:
            parsed_result = json.loads(result.data)
            record_count = result.record_count
        except json.JSONDecodeError:
            parsed_result = result.data

    export_urls = None
    if job.status == "completed" and parsed_result is not None:
        export_urls = ExportUrls(
            json_url=f"/export/{job.id}?format=json",
            csv_url=f"/export/{job.id}?format=csv"
        )

    return JobDetailResponse(
        job_id=job.id,
        status=job.status,
        url=job.url,
        prompt=job.prompt,
        mode=job.mode,
        scrape_mode_used=job.scrape_mode_used,
        groq_model_used=job.groq_model_used,
        token_usage=job.token_usage or 0,
        created_at=job.created_at,
        completed_at=job.completed_at,
        result=parsed_result,
        record_count=record_count,
        error_message=job.error_message,
        export_urls=export_urls
    )

def get_all_jobs(db: Session) -> List[JobDetailResponse]:
    """Retrieves all jobs ordered by creation date descending."""
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [get_job(db, job.id) for job in jobs]

def update_job_status(db: Session, job_id: str, job_status: str, error_message: Optional[str] = None):
    """Updates job status and optional error message."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.status = job_status
        if error_message:
            job.error_message = error_message
        if job_status in ["completed", "failed", "blocked"]:
            from datetime import datetime
            job.completed_at = datetime.utcnow()
        db.commit()

def save_result(
    db: Session,
    job_id: str,
    extracted_data: Any,
    raw_html_path: Optional[str] = None,
    mode_used: Optional[str] = None,
    model_used: Optional[str] = None,
    token_usage: int = 0
):
    """Saves extracted data payload and updates job record."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return

    # Count records
    record_count = 1
    if isinstance(extracted_data, list):
        record_count = len(extracted_data)
    elif isinstance(extracted_data, dict) and "_warning" in extracted_data:
        record_count = 0

    json_str = json.dumps(extracted_data, default=str)
    result = Result(
        job_id=job_id,
        data=json_str,
        raw_html_path=raw_html_path,
        record_count=record_count
    )
    db.add(result)

    # Update job metadata
    job.scrape_mode_used = mode_used
    job.groq_model_used = model_used
    job.token_usage = (job.token_usage or 0) + token_usage

    db.commit()

def get_result_data(db: Session, job_id: str) -> Any:
    """Returns parsed result data for a given job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found."
        )

    if job.status in ["queued", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is still in status '{job.status}'. Results are not available yet."
        )

    result = db.query(Result).filter(Result.job_id == job_id).first()
    if not result or not result.data:
        return None

    try:
        return json.loads(result.data)
    except json.JSONDecodeError:
        return result.data

def save_query_history(
    db: Session,
    job_id: str,
    user_query: str,
    answer: str,
    model_used: Optional[str] = None,
    token_usage: int = 0
):
    """Saves query and answer into QueryHistory."""
    history = QueryHistory(
        job_id=job_id,
        user_query=user_query,
        groq_answer=answer,
        model_used=model_used,
        token_usage=token_usage
    )
    db.add(history)
    db.commit()

def delete_job(db: Session, job_id: str):
    """Deletes job and associated cascade records."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found."
        )

    if job.status == "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a job that is currently running."
        )

    # Delete results & history
    db.query(Result).filter(Result.job_id == job_id).delete()
    db.query(QueryHistory).filter(QueryHistory.job_id == job_id).delete()
    db.delete(job)
    db.commit()
