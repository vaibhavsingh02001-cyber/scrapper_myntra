from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.models.schemas import JobDetailResponse
from backend.services import job_service

router = APIRouter()

@router.get("/", response_model=List[JobDetailResponse])
def list_all_jobs(db: Session = Depends(get_db)):
    """Lists all submitted jobs ordered by newest first."""
    return job_service.get_all_jobs(db)

@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_detail(job_id: str, db: Session = Depends(get_db)):
    """Retrieves status, metadata, and results for a specific job."""
    return job_service.get_job(db, job_id)

@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Deletes job record and associated results."""
    job_service.delete_job(db, job_id)
    return {"message": f"Job '{job_id}' deleted successfully."}
