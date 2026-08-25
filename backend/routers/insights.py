from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.services.insight_service import InsightService
from backend.services.groq_service import GroqService
from backend.pipeline.artifact_service import ArtifactService
from backend.pipeline.keyword_classifier import THEMES

router = APIRouter()


@router.get("/themes")
def get_themes_overview():
    """Returns full per-theme breakdown: counts, percentages, avg ratings, sample quotes."""
    service = InsightService()
    return service.get_themes_overview()


@router.get("/summary")
def get_summary_stats():
    """Returns high-level dashboard metrics: total reviews, top themes, platform breakdown."""
    service = InsightService()
    return service.get_summary_stats()


@router.get("/quotes")
def get_quotes(
    theme: str = Query("all", description="Theme key or 'all'"),
    limit: int = Query(10, ge=1, le=50),
    platform: Optional[str] = Query(None, description="google_play | app_store | reddit"),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0),
    max_rating: Optional[float] = Query(None, ge=1.0, le=5.0)
):
    """Returns verbatim user quotes for a theme with optional platform and rating filters."""
    service = InsightService()
    return service.get_theme_quotes(
        theme_key=theme,
        limit=limit,
        platform=platform,
        min_rating=min_rating,
        max_rating=max_rating
    )


@router.get("/themes/list")
def list_available_themes():
    """Returns metadata for all 5 dimensions and their sub-labels."""
    taxonomy_list = []
    for dim_key, labels_dict in THEMES.items():
        for label_key, label_data in labels_dict.items():
            taxonomy_list.append({
                "dimension": dim_key,
                "key": label_key,
                "label": label_data["label"]
            })
    return {
        "themes": taxonomy_list
    }


@router.get("/status")
def get_artifact_status():
    """Returns current state of all analysis artifacts."""
    artifact = ArtifactService()
    return artifact.get_artifact_status()


@router.post("/ask")
async def ask_insights_assistant(
    question: str = Query(..., description="Natural language question about the dataset"),
):
    """
    Groq-powered Insights Assistant — answers questions grounded on the analysis artifacts.
    Strictly uses artifacts as its knowledge source (no hallucination).
    """
    insight = InsightService()
    summary = insight.get_themes_overview()

    if summary.get("status") == "no_data":
        return {"answer": "No data available yet. Please run /collect and /analyze/run first."}

    groq = GroqService()

    import json
    context = json.dumps({
        "total_reviews": summary.get("total_reviews_analyzed"),
        "platform_breakdown": summary.get("platform_breakdown"),
        "app_breakdown": summary.get("app_breakdown"),
        "themes": {
            k: {
                "label": v["label"],
                "review_count": v["review_count"],
                "percentage": v["percentage"],
                "avg_rating": v["avg_rating"],
                "sample_quotes": v["verbatim_quotes"][:3]
            }
            for k, v in summary.get("themes", {}).items()
        }
    }, indent=2, default=str)

    answer, _ = await groq.query(context, question)
    return {
        "question": question,
        "answer": answer.get("answer", ""),
        "data_source": "themes_summary.json artifact",
        "total_reviews_used": summary.get("total_reviews_analyzed", 0)
    }
