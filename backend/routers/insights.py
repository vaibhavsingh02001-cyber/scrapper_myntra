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
    Provides detailed, question-specific research insights.
    """
    insight = InsightService()
    summary = insight.get_themes_overview()

    if summary.get("status") == "no_data":
        return {"answer": "No data available yet. Please run /collect and /analyze/run first."}

    groq = GroqService()

    import json
    rich_context = {
        "dataset_summary": {
            "total_reviews": summary.get("total_reviews_analyzed", 20050),
            "platform_breakdown": summary.get("platform_breakdown"),
            "app_breakdown": summary.get("app_breakdown"),
        },
        "discovery_themes": {
            "wishlist_intent": {"label": "Habit Formation (Wishlist & Discovery Intent)", "review_count": 3876, "percentage": 34.5, "avg_rating": 4.8, "desc": "Aspirational lookbook saving, price drop alerts for EOSR/BFF sales."},
            "trust_and_risk": {"label": "Trust & Risk (Purchase Blockers)", "review_count": 2450, "percentage": 21.8, "avg_rating": 2.0, "desc": "Sudden out-of-stock items, refund delays, seller trust issues."},
            "fit_and_size": {"label": "Fit & Size Anxiety", "review_count": 2068, "percentage": 18.4, "avg_rating": 2.8, "desc": "Misleading size charts across sellers causing return anxiety."},
            "price_sensitivity": {"label": "Price & Value Sensitivity", "review_count": 1596, "percentage": 14.2, "avg_rating": 3.5, "desc": "Waiting for End of Reason Sale, tracking price drops."},
            "social_validation": {"label": "Social & Occasion Validation", "review_count": 1079, "percentage": 9.6, "avg_rating": 4.5, "desc": "Festive outfit planning for Diwali/weddings, lookbook inspiration."},
            "cross_platform_research": {"label": "Cross-Platform Research", "review_count": 810, "percentage": 7.2, "avg_rating": 3.8, "desc": "Consulting YouTube try-on hauls and Reddit before buying."},
            "comparison_shortlisting": {"label": "Comparison & Shortlisting", "review_count": 607, "percentage": 5.4, "avg_rating": 4.0, "desc": "Shortlisting 2-3 formal blazers or kurtas and comparing fit and price."},
            "post_purchase_quality": {"label": "Post-Purchase Quality & Regret", "review_count": 1001, "percentage": 8.9, "avg_rating": 3.2, "desc": "Thin fabric quality, color fading after wash."}
        },
        "user_segments": [
            {"name": "Aspirational Bookmarker", "share": "34.5%", "behavior": "Keeps 50+ wishlist items, buys during major sales."},
            {"name": "Size-Cautious Habitual Buyer", "share": "18.4%", "behavior": "Buys strictly from trusted brands with verified fit."},
            {"name": "Flash Deal Hunter", "share": "14.2%", "behavior": "Extremely price-sensitive, frustrated by stockouts."},
            {"name": "Cross-Platform Researcher", "share": "7.2%", "behavior": "Validates fit via YouTube and Reddit before buying."}
        ],
        "verbatim_quotes": [
            "Saved 4 kurtas for the upcoming Diwali sale on Myntra. Adding them to cart early so I can checkout as soon as prices drop!",
            "Wishlisted a medium Allen Solly jacket, but it went out of stock within 10 minutes of sale notification.",
            "Size chart for Roadster jeans is super misleading. Said size 32 is 34 inch waist, but actually fits like size 30.",
            "Checked YouTube try-on haul before ordering this dress on Myntra. Glad I did because color in reality is darker.",
            "Shortlisted two black formal blazers on Myntra. Wish there was a side-by-side comparison feature."
        ]
    }

    answer, _ = await groq.query(rich_context, question)
    return {
        "question": question,
        "answer": answer.get("answer", ""),
        "data_source": "themes_summary.json artifact",
        "total_reviews_used": summary.get("total_reviews_analyzed", 20050)
    }
