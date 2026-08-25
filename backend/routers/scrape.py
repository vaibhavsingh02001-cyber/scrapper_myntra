from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session
from backend.db.database import get_db, SessionLocal
from backend.models.schemas import ScrapeRequest, JobResponse
from backend.services import job_service, ScraperService, GroqService

router = APIRouter()

async def run_scrape_pipeline(job_id: str, url: str, prompt: str, mode: str):
    """Asynchronous background execution task for end-to-end scraping pipeline."""
    db: Session = SessionLocal()
    try:
        job_service.update_job_status(db, job_id, "running")

        # Step 1: Execute scraping engine
        scraper = ScraperService()
        scrape_output = await scraper.scrape(url, mode)

        # Step 2: Save raw HTML snapshot
        raw_html_path = await scraper.save_raw_html(job_id, scrape_output["raw_html"])

        # Step 3: Run Groq LLM extraction
        groq = GroqService()
        extracted_data, tokens_used = await groq.extract(scrape_output["chunks"], prompt)

        # Step 4: Persist result payload & update job
        job_service.save_result(
            db=db,
            job_id=job_id,
            extracted_data=extracted_data,
            raw_html_path=raw_html_path,
            mode_used=scrape_output["mode_used"],
            model_used=groq.extraction_model,
            token_usage=tokens_used
        )
        job_service.update_job_status(db, job_id, "completed")

    except Exception as e:
        error_msg = str(e)
        status_name = "failed"
        if "403" in error_msg or "blocked" in error_msg.lower():
            status_name = "blocked"
        job_service.update_job_status(db, job_id, status_name, error_message=error_msg)
    finally:
        db.close()

@router.post("/", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submits a new URL scraping & extraction job."""
    job = job_service.create_job(db, request)

    # Queue pipeline execution in background
    background_tasks.add_task(
        run_scrape_pipeline,
        job_id=job.id,
        url=str(request.url),
        prompt=request.prompt,
        mode=request.mode
    )

    return JobResponse(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at
    )
