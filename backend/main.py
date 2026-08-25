import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.db.database import engine, Base
from backend.routers import scrape, jobs, query, export, health
from backend.routers import collect, analyze, insights, research, report


# Ensure DB tables are created on startup
Base.metadata.create_all(bind=engine)

# Ensure storage directories exist
os.makedirs(os.path.join(settings.STORAGE_PATH, "raw"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "exports"), exist_ok=True)

app = FastAPI(
    title="Scapper API",
    description="Intelligent LLM-Powered Web Scraping Platform API",
    version="1.0.0"
)

# CORS Configuration — Unrestricted for local dev & preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Mask API keys if accidentally included in error message string
    err_str = str(exc)
    if "gsk_" in err_str:
        import re
        err_str = re.sub(r"gsk_[a-zA-Z0-9_-]+", "[REDACTED_API_KEY]", err_str)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal System Error",
            "detail": err_str,
            "path": str(request.url)
        }
    )

# Register Routers — Original Generic Scraper API
app.include_router(scrape.router, prefix="/scrape", tags=["Generic Scrape"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(export.router, prefix="/export", tags=["Export"])
app.include_router(health.router, prefix="/health", tags=["Health"])

# Register Routers — Myntra/AJIO Discovery Engine
app.include_router(collect.router, prefix="/collect", tags=["Discovery: Collect"])
app.include_router(analyze.router, prefix="/analyze", tags=["Discovery: Analyze"])
app.include_router(insights.router, prefix="/insights", tags=["Discovery: Insights"])
app.include_router(research.router, prefix="/research", tags=["Discovery: Research"])
app.include_router(report.router, prefix="/report", tags=["Discovery: Report"])

@app.get("/")
def root():
    return {
        "title": "Scapper API Gateway",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }
