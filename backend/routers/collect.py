from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.database import get_db, SessionLocal
from backend.models.scrape_run import ScrapeRun
from backend.scrapers.play_store_scraper import PlayStoreScraper
from backend.scrapers.app_store_scraper import AppStoreScraper
from backend.scrapers.reddit_scraper import RedditScraper
from backend.pipeline.noise_filter import NoiseFilter
from backend.pipeline.artifact_service import ArtifactService

router = APIRouter()

SUPPORTED_PLATFORMS = ["google_play", "app_store", "reddit", "all"]
SUPPORTED_APPS = ["myntra", "all"]


async def run_collection_pipeline(run_id: str, platform: str, app_name: str, max_reviews: int):
    """Background task: collects reviews from the specified platform and saves as artifacts."""
    db: Session = SessionLocal()
    run = db.query(ScrapeRun).filter(ScrapeRun.id == run_id).first()
    artifact = ArtifactService()
    noise_filter = NoiseFilter()
    total_collected = 0
    total_filtered = 0
    total_stored = 0

    try:
        targets = []

        # Build collection targets
        if platform in ("google_play", "all"):
            apps = ["myntra"] if app_name == "all" else [app_name]
            for app in apps:
                targets.append(("google_play", app))

        if platform in ("app_store", "all"):
            apps = ["myntra"] if app_name == "all" else [app_name]
            for app in apps:
                targets.append(("app_store", app))

        if platform in ("reddit", "all"):
            targets.append(("reddit", "myntra"))

        # Execute collection and noise filtering
        for (src_platform, src_app) in targets:
            print(f"[Collect] Starting {src_platform} -> {src_app}")
            raw_reviews = []

            try:
                if src_platform == "google_play":
                    scraper = PlayStoreScraper(max_reviews_per_app=max_reviews)
                    raw_reviews = scraper.collect(src_app)
                elif src_platform == "app_store":
                    scraper = AppStoreScraper(max_reviews_per_app=max_reviews)
                    raw_reviews = scraper.collect(src_app)
                elif src_platform == "reddit":
                    scraper = RedditScraper(max_posts=500)
                    raw_reviews = scraper.collect()
            except Exception as e:
                print(f"[Collect] Error collecting {src_platform}/{src_app}: {e}")
                continue

            total_collected += len(raw_reviews)

            # Filter noise
            accepted, stats = noise_filter.filter_batch(raw_reviews)
            total_filtered += stats["dropped"]
            total_stored += stats["accepted"]

            # Save raw artifacts
            artifact.save_raw_reviews(src_platform, src_app, accepted)
            print(f"[Collect] {src_platform}/{src_app}: {len(raw_reviews)} -> {len(accepted)} after filtering")

        # Update scrape run record
        run.status = "completed"
        run.reviews_collected = total_collected
        run.reviews_filtered = total_filtered
        run.reviews_stored = total_stored
        run.completed_at = datetime.utcnow()
        db.commit()
        print(f"[Collect] Run {run_id} complete. Stored {total_stored} reviews.")

    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)[:500]
        run.completed_at = datetime.utcnow()
        db.commit()
        print(f"[Collect] Run {run_id} failed: {e}")
    finally:
        db.close()


@router.post("/{platform}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_collection(
    platform: str,
    background_tasks: BackgroundTasks,
    app: str = "all",
    max_reviews: int = 10000,
    db: Session = Depends(get_db)
):
    """
    Triggers a review collection run for the specified platform.
    platform: google_play | app_store | reddit | all
    app: myntra | ajio | all
    max_reviews: cap per app (default 10,000)
    """
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform '{platform}'. Choose from: {SUPPORTED_PLATFORMS}"
        )
    if app not in SUPPORTED_APPS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported app '{app}'. Choose from: {SUPPORTED_APPS}"
        )

    run = ScrapeRun(platform=platform, app_name=app, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(
        run_collection_pipeline,
        run_id=run.id,
        platform=platform,
        app_name=app,
        max_reviews=max_reviews
    )

    return {
        "run_id": run.id,
        "platform": platform,
        "app": app,
        "max_reviews_per_app": max_reviews,
        "status": "running",
        "message": f"Collection started for {platform}/{app}. Check /collect/status/{run.id}."
    }


@router.get("/status/{run_id}")
def get_collection_status(run_id: str, db: Session = Depends(get_db)):
    """Returns the current status of a collection run."""
    run = db.query(ScrapeRun).filter(ScrapeRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return {
        "run_id": run.id,
        "platform": run.platform,
        "app_name": run.app_name,
        "status": run.status,
        "reviews_collected": run.reviews_collected,
        "reviews_filtered": run.reviews_filtered,
        "reviews_stored": run.reviews_stored,
        "error_message": run.error_message,
        "started_at": run.started_at,
        "completed_at": run.completed_at
    }
